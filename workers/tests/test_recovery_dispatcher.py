"""Offline orchestration tests; no requests, credentials, or game equivalence claims."""
import importlib.util
import copy
import json
import os
import signal
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import hashlib
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from workers import recovery_dispatcher as d


class DurableDispatcherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.clock = [10000.0]
        self.store = d.Store(self.root, 'a' * 64, lambda: self.clock[0])
        self.addCleanup(lambda: self.store.close())

    def task(self, name='startup', priority=0, kind='startup-preparation', functions=None):
        return {'id': name, 'kind': kind, 'priority': priority,
                'functions': functions or [], 'inputs': {}, 'depends_on': []}

    def test_priority_two_lanes_and_persistent_ownership(self):
        for name, priority in [('background', 50), ('startup', 0), ('branch', 1)]:
            self.store.add(self.task(name, priority))
        self.assertEqual(self.store.claim()['task']['id'], 'startup')
        second = self.store.claim()
        self.assertEqual(second['task']['id'], 'branch')
        self.assertIsNone(self.store.claim())
        self.store.finish(second['job'], {'state': 'complete'})
        self.assertEqual(self.store.claim()['task']['id'], 'background')

    def test_duplicate_function_claim_cannot_mutate_or_add_task(self):
        identity = 'DAOrigins.exe:' + 'b' * 64 + ':rva-004e3024'
        self.store.add(self.task(functions=[identity]))
        with self.assertRaises(d.Refusal):
            self.store.add(self.task('duplicate', functions=[identity]))
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM tasks').fetchone()[0], 1)

    def test_changed_existing_task_or_configuration_refused(self):
        self.store.add(self.task())
        with self.assertRaises(d.Refusal):
            self.store.add(self.task(priority=2))
        with self.assertRaises(d.Refusal):
            d.Store(self.root, 'f' * 64, lambda: self.clock[0])

    def test_opening_debit_and_adjustment_are_exactly_once(self):
        self.store.opening_debit(2, 'setup and review')
        self.store.opening_debit(2, 'setup and review')
        adjustment = {'id': 'repair', 'count': 1, 'evidence': 'explicit director debit'}
        self.store.adjustment(adjustment)
        self.store.adjustment(adjustment)
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM requests').fetchone()[0], 3)
        with self.assertRaises(d.Refusal):
            self.store.opening_debit(0, 'reset forbidden')

    def test_twelve_requests_per_nonoverlapping_cycle_and_restart(self):
        self.store.opening_debit(2, 'setup/review')
        for i in range(5):
            self.assertEqual(len(self.store.reserve('t', ['preparation', 'review'])), 2)
        self.assertIsNone(self.store.reserve('t', ['review']))
        self.store.close()
        self.store = d.Store(self.root, 'a' * 64, lambda: self.clock[0])
        self.assertIsNone(self.store.reserve('t', ['review']))
        self.clock[0] += d.CYCLE
        self.assertEqual(len(self.store.reserve('t', ['review'])), 1)

    def test_deferred_review_also_debits_actual_dispatch_cycle(self):
        first = self.store.reserve('t', ['review'])[0]
        self.clock[0] += d.CYCLE
        self.assertEqual(self.store.request(first, lambda: 'reviewed'), 'reviewed')
        counts = dict(self.store.db.execute('SELECT cycle,count(*) FROM requests GROUP BY cycle').fetchall())
        self.assertEqual(counts, {0: 1, 1: 1})
        with self.assertRaises(d.Refusal):
            self.store.request(first, lambda: self.fail('replayed request'))

    def test_clock_regression_stops_claims_and_dispatch(self):
        request = self.store.reserve('t', ['review'])[0]
        self.clock[0] -= 1
        with self.assertRaises(d.Refusal):
            self.store.request(request, lambda: self.fail('dispatched after clock regression'))

    def test_external_exception_is_ambiguous_and_never_replayed(self):
        request = self.store.reserve('t', ['provider'])[0]
        with self.assertRaises(RuntimeError):
            self.store.request(request, lambda: (_ for _ in ()).throw(RuntimeError('network broke')))
        self.assertEqual(self.store.db.execute('SELECT state FROM requests').fetchone()[0], 'in-flight')
        with self.assertRaises(d.Refusal):
            self.store.request(request, lambda: self.fail('ambiguous external call replayed'))

    def test_restart_consumes_receipt_or_blocks_without_repeating(self):
        self.store.add(self.task())
        claim = self.store.claim()
        self.store.recover()
        self.assertEqual(self.store.summary()['tasks'][0]['state'], 'exception')
        self.assertIsNone(self.store.claim())
        self.store.add(self.task('with-receipt'))
        claim = self.store.claim()
        d.atomic(self.root / 'jobs' / claim['job'] / 'receipt.json', {'state': 'support-approved'})
        self.store.recover()
        self.assertEqual(self.store.db.execute("SELECT state FROM tasks WHERE id='with-receipt'").fetchone()[0], 'support-approved')

    def test_exclusive_lock_and_child_inherits_parent_lease(self):
        directory = self.root / 'lock'
        with d.exclusive(directory) as fd:
            with self.assertRaises(d.Refusal):
                with d.exclusive(directory):
                    pass
            child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(2)'], pass_fds=(fd,))
        try:
            with self.assertRaises(d.Refusal):
                with d.exclusive(directory):
                    pass
        finally:
            child.wait(timeout=5)
        with d.exclusive(directory):
            pass

    def test_request_limit_is_enforced_between_processes(self):
        script = ('from workers.recovery_dispatcher import Store; import sys; '
                  's=Store(sys.argv[1], "a"*64); '
                  'print(s.reserve("t", ["provider","review","review"]) is not None); s.close()')
        # Real wall clock separate ledger avoids fake clock regression.
        shared = self.root / 'process-budget'
        initial = d.Store(shared, 'a' * 64)
        initial.close()
        processes = [subprocess.Popen([sys.executable, '-c', script, str(shared)], cwd=ROOT,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(7)]
        results = [p.communicate(timeout=10) for p in processes]
        self.assertTrue(all(p.returncode == 0 for p in processes), results)
        self.assertEqual(sum(stdout.strip() == b'True' for stdout, _ in results), 4)

    def test_actual_nested_pair_child_retains_lease_after_job_crash(self):
        marker = self.root / 'nested-child.pid'
        job_code = ('import sys; from pathlib import Path; from workers import recovery_dispatcher as d; '
                    'd.LEASE_FDS=(int(sys.argv[1]),); p=d.load_pair(sys.argv[2],"nested_lease_test"); '
                    'p.run_command([sys.executable,"-c",sys.argv[3]],Path(sys.argv[4]),Path(sys.argv[5]),20)')
        child_code = 'import os,time; from pathlib import Path; Path(' + repr(str(marker)) + ').write_text(str(os.getpid())); time.sleep(15)'
        child_pid = None
        job = None
        try:
            with d.exclusive(self.root / 'actual-nested-lock') as fd:
                job = subprocess.Popen([sys.executable, '-c', job_code, str(fd), str(ROOT), child_code,
                                        str(self.root), str(self.root / 'pair-command')],
                                       cwd=ROOT, pass_fds=(fd,), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                deadline = time.monotonic() + 5
                while not marker.exists() and time.monotonic() < deadline:
                    time.sleep(0.02)
                self.assertTrue(marker.is_file(), 'actual nested pair child never started')
                child_pid = int(marker.read_text())
                job.kill()
                job.wait(timeout=5)
            os.kill(child_pid, 0)  # It survived the job and holds the shared lease.
            with self.assertRaises(d.Refusal):
                with d.exclusive(self.root / 'actual-nested-lock'):
                    pass
        finally:
            if job is not None and job.poll() is None:
                job.kill()
                job.wait(timeout=5)
            if child_pid is not None:
                try:
                    os.kill(child_pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass

    def test_protected_paths_and_symlinks_refused(self):
        for name in ['../escape.py', '/tmp/escape.py', 'a/../escape', 'a\\b']:
            with self.assertRaises(d.Refusal):
                d.relative(name)
        source = self.root / 'source'
        source.write_text('source')
        link = self.root / 'link'
        link.symlink_to(source)
        with self.assertRaises(d.Refusal):
            d.bound(link, d.digest(source))

    def test_byte_checked_graph_expansion_adds_discovery_not_implementation(self):
        spec = importlib.util.spec_from_file_location('pe_fixture', ROOT / 'tests/test_pe.py')
        pe = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pe)
        data = pe.image()
        data[480:485] = bytes.fromhex('e805000000')
        binary = self.root / 'original.bin'
        binary.write_bytes(data)
        prefix = 'fixture.exe:' + d.digest(binary) + ':rva-'
        caller, target = prefix + '00001000', prefix + '0000100a'
        task = self.task(functions=[caller])
        task.update(context=[], body_ranges={caller: [[4096, 4100]]}, depth=0)
        self.store.add(task)
        config = {'root': str(ROOT), 'reference': {'path': str(binary), 'module': 'fixture.exe',
                  'sha256': d.digest(binary)}, 'max_depth': 3}
        value = {'observed_edges': [{'caller': caller, 'target': target,
                  'callsite_rva': '00001000', 'instruction_hex': 'e805000000'}]}
        d.expand_observed(config, task, value, self.store, self.root / 'graph')
        child = self.store.db.execute("SELECT kind,state FROM tasks WHERE id='startup-rva-0000100a'").fetchone()
        self.assertEqual(tuple(child), ('startup-preparation', 'queued'))
        self.assertEqual(self.store.summary()['observed_edges'], 1)
        # A made-up target/instruction must not enter the graph.
        value['observed_edges'][0]['instruction_hex'] = 'e806000000'
        with self.assertRaises(d.Refusal):
            d.expand_observed(config, task, value, self.store, self.root / 'bad-graph')
        self.assertEqual(self.store.summary()['observed_edges'], 1)

    def test_invalid_startup_support_never_requests_review_or_executes_it(self):
        task = self.task()
        task.update(context=[], objective='bounded synthetic preparation')
        self.store.add(task)
        claim = self.store.claim()
        response = {'summary': 'Invalid support', 'artifacts': [
                    {'path': 'workers/startup_support/x.py', 'content': 'invalid syntax @'}],
                    'observed_edges': [], 'blockers': [], 'next_action': 'review'}
        with patch.object(d, 'prepare_request', return_value=response), self.assertRaises(SyntaxError):
            d.preparation_job({'root': str(ROOT), 'python': sys.executable}, claim, self.store, self.root / 'job')
        states = [r[0] for r in self.store.db.execute('SELECT state FROM requests ORDER BY kind')]
        self.assertEqual(states, ['complete', 'reserved'])


class PreparationBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name).resolve()

    def proposal(self):
        return {'summary': 'Bounded support proposal',
                'artifacts': [{'path': 'workers/startup_support/capture.py',
                               'content': 'raise RuntimeError("must not be executed by syntax gate")\n'}],
                'observed_edges': [], 'blockers': ['Capture not performed'],
                'next_action': 'Independent review before new adapter execution'}

    def test_syntax_gate_does_not_execute_generated_code(self):
        result = d.check_preparation(self.proposal(), self.directory)
        self.assertTrue(result['passed'])
        self.assertFalse(result['observed_edges_adopted'])

    def test_scope_syntax_and_empty_artifacts_fail(self):
        for name, content in [('tools/run_recovery_pair.py', 'pass'),
                              ('workers/startup_support/x.exe', 'binary'),
                              ('workers/startup_support/x.py', 'this is invalid python @')]:
            with self.subTest(name=name), self.assertRaises((d.Refusal, SyntaxError)):
                value = self.proposal()
                value['artifacts'][0] = {'path': name, 'content': content}
                d.check_preparation(value, self.directory)

    def test_unknown_adapter_and_unowned_promotion_rejected(self):
        with self.assertRaises(d.Refusal):
            d.promote({'root': str(self.directory)}, {}, {}, self.directory, None, 'job')


class ExistingPipelineAdapterTests(unittest.TestCase):
    """Exercise actual existing gate order through the dispatcher's request ledger."""
    def test_gate_failure_never_spends_independent_review(self):
        spec = importlib.util.spec_from_file_location('pair_fixture', ROOT / 'tests/test_recovery_pair.py')
        fixture_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fixture_module)
        for mode in ['pass', 'heldout-fail', 'public-error', 'negative-fail']:
            with self.subTest(mode=mode):
                fixture = fixture_module.RecoveryPairTests()
                fixture.setUp()
                try:
                    with tempfile.TemporaryDirectory() as raw:
                        state = d.Store(Path(raw).resolve(), 'c' * 64)
                        try:
                            ids = state.reserve('synthetic-pair', ['provider', 'review'])
                            state.request(ids[0], lambda: True)
                            proposal = fixture.root / 'response.json'
                            proposal.write_text(json.dumps(fixture.proposal()))
                            if mode == 'heldout-fail': fixture.mode('heldout', 'fail')
                            if mode == 'public-error': fixture.mode('public', 'runner-error')
                            if mode == 'negative-fail': fixture.manifest['commands']['negative'][0]['argv'][2] = 'public'
                            fixture_module.write(fixture.path, fixture.manifest)
                            def reviewer(kind, *args, **kwargs):
                                self.assertEqual(kind, 'review')
                                # Reviewer executes only after exact four-stage pass.
                                status = json.loads((fixture.output / 'status.json').read_text())
                                self.assertEqual([g['stage'] for g in status['attempts'][0]['gates']],
                                                 ['build', 'public', 'heldout', 'negative'])
                                self.assertTrue(all(g['passed'] for g in status['attempts'][0]['gates']))
                                return state.request(ids[1], lambda: fixture.requester(kind, *args, **kwargs))
                            result = fixture_module.run_pair(fixture.path, fixture.output, fixture.root,
                                initial_response=proposal, attempts=1, requester=reviewer)
                            self.assertEqual(result['accepted'], mode == 'pass')
                            review_state = state.db.execute('SELECT state FROM requests WHERE id=?', (ids[1],)).fetchone()[0]
                            self.assertEqual(review_state, 'complete' if mode == 'pass' else 'reserved')
                            self.assertEqual(len(result['attempts']), 1)
                        finally:
                            state.close()
                finally:
                    fixture.doCleanups()


class DeferredCheckpointBindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / 'analysis').mkdir()
        (self.root / 'analysis/functions.json').write_text('synthetic69 registry')
        (self.root / 'source.cpp').write_text('current source')
        self.registry_sha = d.digest(self.root / 'analysis/functions.json')
        self.source = lambda root: {'source.cpp': d.digest(root / 'source.cpp')}
        expected = dict(self.source(self.root), **{'analysis/functions.json': self.registry_sha})
        self.inventory = [(f'function-{i:02}', False) for i in range(69)]
        self.inventory += [(f'function-{i:02}', True) for i in range(48)]
        self.inventory.sort()
        inventory_sha = hashlib.sha256(json.dumps(self.inventory, separators=(',', ':')).encode()).hexdigest()
        self.name = 'analysis/validation/direct-object-fields-ci-001.json'
        self.producer_name = 'reports/checkpoint-direct-object-fields-ci-001/reuse-attestation.json'
        self.task = {'promotion': {'deferred_checkpoint': {'path': self.name,
                     'producer_attestation': self.producer_name, 'registry_sha256': self.registry_sha,
                     'inventory_sha256': inventory_sha}}}
        self.config = {'root': str(self.root)}
        rows = [dict(function_id=identity, negative_control=negative,
                     artifacts_sha256=expected, artifacts_unchanged=True,
                     status='failed' if negative else 'corpus_pass',
                     case_counts={'mismatch' if negative else 'corpus_pass': 1},
                     provenance_kind='fresh_clean_build_and_exact_execution_inputs', repeats_per_side=2)
                for identity, negative in self.inventory]
        self.record = dict(schema_version=2, policy='clean-build-local-groups-003',
                           fresh_clean_build=True, complete_checkpoint=True, proof=False,
                           native_windows_validated=False, records=rows)
        self.seal()
        d.atomic(self.root / self.producer_name, {'status': 'passed', 'complete_checkpoint': True,
                 'usable_for_progress': True, 'source': self.source(self.root),
                 'registry_sha256': self.registry_sha, 'groups': [{'records': rows}]})
        self.addCleanup(patch.stopall)
        gold_rows = copy.deepcopy(rows)
        patch.object(d, 'module', return_value=SimpleNamespace(source_manifest=self.source,
                     publication_document=lambda producer: {'records': gold_rows})).start()

    def seal(self):
        value = dict(self.record)
        value.pop('attestation_sha256', None)
        value['attestation_sha256'] = hashlib.sha256(json.dumps(value, sort_keys=True,
            separators=(',', ':'), allow_nan=False).encode()).hexdigest()
        d.atomic(self.root / self.name, value)

    def test_exact_inventory_source_and_raw_bytes_are_bound(self):
        binding = d.inspect_deferred_checkpoint(self.config, self.task, self.root)
        self.assertEqual(binding['raw_sha256'], d.digest(self.root / self.name))
        self.assertEqual((binding['positive_reports'], binding['negative_reports']), (69, 48))

    def test_complete_marker_without_full_inventory_fails(self):
        self.record['records'].pop()
        self.seal()
        with self.assertRaises(d.Refusal):
            d.inspect_deferred_checkpoint(self.config, self.task, self.root)

    def test_current_source_change_or_wrong_registry_fails(self):
        (self.root / 'source.cpp').write_text('unreviewed change')
        with self.assertRaises(d.Refusal):
            d.inspect_deferred_checkpoint(self.config, self.task, self.root)

    def test_failed_or_changed_semantic_record_cannot_use_passed_producer(self):
        positive = next(r for r in self.record['records'] if not r['negative_control'])
        positive['status'] = 'failed'
        positive['case_counts'] = {'runner_error': 1}
        self.seal()
        with self.assertRaises(d.Refusal):
            d.inspect_deferred_checkpoint(self.config, self.task, self.root)

    def test_control_without_observed_mismatch_or_counts_fails(self):
        negative = next(r for r in self.record['records'] if r['negative_control'])
        negative['case_counts'] = {'corpus_pass': 1}
        self.seal()
        with self.assertRaises(d.Refusal):
            d.inspect_deferred_checkpoint(self.config, self.task, self.root)

    def test_arbitrary_checkpoint_path_is_not_a_deferred_adapter(self):
        self.task['promotion']['deferred_checkpoint']['path'] = 'analysis/validation/arbitrary.json'
        with self.assertRaises(d.Refusal):
            d.inspect_deferred_checkpoint(self.config, self.task, self.root)

    def test_raw_byte_change_after_review_blocks_before_any_shared_write(self):
        binding = d.inspect_deferred_checkpoint(self.config, self.task, self.root)
        directory = self.root / 'job'
        d.atomic(directory / 'integration-approval.json', {'pending_checkpoint_binding': binding})
        path = self.root / self.name
        path.write_bytes(path.read_bytes() + b'\n')  # JSON/domain identity unchanged, raw SHA differs.
        before = (self.root / 'source.cpp').read_bytes()
        with self.assertRaises(d.Refusal):
            d.promote(self.config, self.task, {}, directory, None, 'synthetic')
        self.assertEqual((self.root / 'source.cpp').read_bytes(), before)
        self.assertFalse((directory / 'integration-journal.json').exists())

    def test_missing_named_record_waits_only_promotion_and_has_deadline(self):
        (self.root / self.name).unlink()
        phases = []
        store = SimpleNamespace(phase=lambda job, phase: phases.append(phase))
        with patch.object(d.time, 'monotonic', side_effect=[0, 7201]), self.assertRaises(d.Refusal):
            d.await_deferred_checkpoint(self.config, self.task, self.root / 'job', store, 'synthetic')
        self.assertEqual(phases, ['waiting-existing-checkpoint-before-integration-review'])


if __name__ == '__main__':
    unittest.main()

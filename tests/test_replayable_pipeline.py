"""Durable MCP boundary tests use deliberately invalid open binary inputs.
No proprietary compiler, SharpRetro installation or VM is used in these tests.
"""
import hashlib
import importlib.util
import json
from contextlib import closing
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('replayable_stdio', ROOT / 'tools/decompilation-mcp/tests/test_stdio.py')
stdio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stdio)


def sha(data):
    return hashlib.sha256(data).hexdigest()


@unittest.skipUnless(stdio.DLL.exists(), 'build C# component first')
class PipelineBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.clients = []
        binary = b'open invalid PE, never executable'
        (self.root / 'original.exe').write_bytes(binary)
        (self.root / 'compiler.exe').write_bytes(b'open fake compiler; never executed')
        self.dll = self.root / 'lifter/adapter.dll'
        self.dll.parent.mkdir()
        self.dll.write_bytes(b'open fake adapter; never executed')
        (self.root / 'manifest.json').write_text(json.dumps(dict(revision=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), upstream_tracked_source_sha256={}, assemblies_sha256={'adapter.dll': sha(self.dll.read_bytes())}, runtime_files_sha256={})))
        (self.root / 'lifter.json').write_text(json.dumps(dict(adapter_dll=str(self.dll), build_manifest=str(self.root / 'manifest.json'), sharp_retro_checkout=str(ROOT))))
        functions = [dict(rva=rva, name='fn', body_bytes=1, body_ranges=[dict(start_rva=rva, end_rva_inclusive=rva)], signature_hypothesis='unknown', calling_convention_hypothesis='unknown') for rva in (0x1000, 0x1030, 0x1040, 0x1050)]
        (self.root / 'inventory.json').write_text(json.dumps(dict(module_sha256=sha(binary), image_base=0x400000, functions=functions)))
        project = dict(id='open', module='open-invalid', module_sha256=sha(binary), inventory=str(self.root / 'inventory.json'), original=str(self.root / 'original.exe'), compiler=str(self.root / 'compiler.exe'), compiler_sha256=sha((self.root / 'compiler.exe').read_bytes()), allowed_roots=[str(self.root), str(ROOT)], replayable=dict(lifter_config=str(self.root / 'lifter.json'), vm_build_lock=str(self.root / 'unused.lock'), output_root=str(self.root / 'attempts')))
        self.config = self.root / 'registry.json'
        self.config.write_text(json.dumps(dict(state_root=str(self.root / 'state'), python=__import__('sys').executable, adapter_root=str(ROOT), projects=[project])))
        self.client = self.connect()

    def connect(self):
        client = stdio.Client(self.config)
        self.clients.append(client)
        return client

    def tearDown(self):
        for client in self.clients:
            client.close()
        self.temp.cleanup()

    def submit(self, token, **extra):
        return self.client.call('replayable_run_next', project_id='open', idempotency_key=token, compile=False, **extra)

    def test_failed_first_frontier_remains_active_and_restart_idempotent(self):
        submitted = self.submit('first')
        self.assertEqual(submitted['rva'], 0x1000)
        done = stdio.wait_job(self.client, submitted['job_id'])
        self.assertEqual(done['state'], 'completed')
        self.assertEqual(done['result']['status'], 'inconclusive')
        again = self.connect().call('replayable_run_next', project_id='open', idempotency_key='first', compile=False)
        self.assertEqual(again['job_id'], submitted['job_id'])
        self.assertTrue(again['reused'])
        following = self.submit('retry-exact-frontier')
        self.assertEqual(following['rva'], 0x1000)
        stdio.wait_job(self.client, following['job_id'])
        state = self.client.call('replayable_status', project_id='open')
        self.assertEqual(state['new_pipeline_full_matches'], 0)
        self.assertEqual(state['inventory_identities'], 4)
        self.assertEqual(state['first_unresolved_rva'], 0x1000)

    def test_lifter_artifact_change_invalidates_job_key(self):
        first = self.submit('bound-to-inputs')
        stdio.wait_job(self.client, first['job_id'])
        self.dll.write_bytes(b'changed actual lifter bytes')
        with self.assertRaises(ValueError):
            self.submit('bound-to-inputs')
        second = self.submit('new-inputs')
        self.assertNotEqual(first['pipeline_key'], second['pipeline_key'])
        self.assertEqual(second['rva'], 0x1000)
        stdio.wait_job(self.client, second['job_id'])

    def test_shared_checker_binding_change_creates_new_key_without_credit(self):
        # Isolated source dependency inventory, never a production-module edit.
        adapter_root = self.root / 'adapter-root'
        for component in ('rapid_object', 'rapid_native', 'rapid', 'workers', 'tools/replayable'):
            directory = adapter_root / component
            directory.mkdir(parents=True)
            (directory / 'binding.py').write_text('# open source dependency fixture\n')
        checker = adapter_root / 'rapid_object/constructor_identity.py'
        checker.write_text('# previous exact supported syntax fixture\n')
        config = json.loads(self.config.read_text())
        config['adapter_root'] = str(adapter_root)
        self.config.write_text(json.dumps(config))
        client = self.connect()
        first = client.call('replayable_run_next', project_id='open', idempotency_key='checker-key', compile=False)
        stdio.wait_job(client, first['job_id'])
        request = json.loads((self.root / 'attempts' / first['job_id'] / 'request.json').read_text())
        self.assertEqual(request['inputs'][str(checker)], sha(checker.read_bytes()))
        checker.write_text('# newly supported exact syntax fixture\n')
        with self.assertRaises(ValueError):
            client.call('replayable_run_next', project_id='open', idempotency_key='checker-key', compile=False)
        second = client.call('replayable_run_next', project_id='open', idempotency_key='checker-key-new', compile=False)
        self.assertNotEqual(first['pipeline_key'], second['pipeline_key'])
        self.assertEqual(second['rva'], 0x1000)
        stdio.wait_job(client, second['job_id'])
        state = client.call('replayable_status', project_id='open')
        self.assertEqual(state['new_pipeline_full_matches'], 0)
        self.assertEqual(state['first_unresolved_rva'], 0x1000)

    def test_seeded_receipt_source_object_and_report_integrity_invalidation(self):
        # Controlled persistence-only fixture: no comparison success is claimed.
        import sqlite3
        first = self.submit('receipt-fixture')
        stdio.wait_job(self.client, first['job_id'])
        folder = self.root / 'attempts' / first['job_id']
        (folder / 'build').mkdir()
        paths = {'source_sha256': folder / 'candidate.cpp', 'object_sha256': folder / 'build/candidate.obj', 'comparison_sha256': folder / 'comparison.json', 'callee_lifts_sha256': folder / 'callee-lifts.json', 'eh_evidence_sha256': folder / 'eh-evidence.json'}
        for path in paths.values():
            path.write_bytes(b'controlled persistence fixture')
        receipt = dict(status='full_match', **{key: sha(path.read_bytes()) for key, path in paths.items()})
        (folder / 'result.json').write_text(json.dumps(receipt))
        with closing(sqlite3.connect(self.root / 'state/jobs.sqlite3')) as db, db:
            db.execute("UPDATE replayable_frontier SET status='full_match'")
        self.assertEqual(self.client.call('replayable_status', project_id='open')['new_pipeline_full_matches'], 1)
        for path in paths.values():
            original = path.read_bytes()
            path.write_bytes(b'changed artifact')
            status = self.client.call('replayable_status', project_id='open')
            self.assertEqual(status['new_pipeline_full_matches'], 0)
            self.assertEqual(status['first_unresolved_rva'], 0x1000)
            path.write_bytes(original)
        (folder / 'candidate.cpp').unlink()
        self.assertEqual(self.client.call('replayable_status', project_id='open')['new_pipeline_full_matches'], 0)

    def test_external_unknown_frontier_requires_reconciliation_before_retry(self):
        import sqlite3
        first = self.submit('unknown-control')
        stdio.wait_job(self.client, first['job_id'])
        with closing(sqlite3.connect(self.root / 'state/jobs.sqlite3')) as db, db:
            db.execute("UPDATE replayable_frontier SET status='external_outcome_unknown'")
        with self.assertRaises(ValueError):
            self.submit('must-not-retry-unknown-external-call')

    def assert_cross_key_barrier(self, state):
        import sqlite3
        first = self.submit('cross-key-' + state)
        stdio.wait_job(self.client, first['job_id'])
        database = self.root / 'state/jobs.sqlite3'
        with closing(sqlite3.connect(database)) as db, db:
            db.execute("UPDATE replayable_frontier SET status=?", (state,))
        self.dll.write_bytes(b'changed frontend runtime must not clear external uncertainty')
        changed = self.client.call('replayable_status', project_id='open')
        self.assertNotEqual(changed['pipeline_key'], first['pipeline_key'])
        with self.assertRaises(ValueError):
            self.submit('changed-key-' + state)
        # A compiler/support configuration revision also gets a different key.
        config = json.loads(self.config.read_text())
        config['projects'][0]['compiler_flags'] = ['/open-fixture-revised-compiler-profile']
        self.config.write_text(json.dumps(config))
        other = self.connect()
        revised = other.call('replayable_status', project_id='open')
        self.assertNotEqual(revised['pipeline_key'], changed['pipeline_key'])
        with self.assertRaises(ValueError):
            other.call('replayable_run_next', project_id='open', idempotency_key='revised-compiler-' + state, compile=True)
        with closing(sqlite3.connect(database)) as db, db:
            self.assertEqual(db.execute('SELECT count(*) FROM jobs').fetchone()[0], 1)
            rows = db.execute('SELECT input_key,status,job FROM replayable_frontier').fetchall()
        self.assertEqual(rows, [(first['pipeline_key'], state, first['job_id'])])

    def test_running_frontier_blocks_changed_input_and_compiler_keys(self):
        self.assert_cross_key_barrier('running')

    def test_external_unknown_frontier_blocks_changed_input_and_compiler_keys(self):
        self.assert_cross_key_barrier('external_outcome_unknown')

    def test_unknown_recipe_and_reordered_passes_are_rejected(self):
        recipe = dict(schema_version=1, architecture='x86-bits32-linear-v1', frontend='sharpretro-typed-v1', compiler_profile='vc8-x86-thiscall-stores-v1', steps=['emit-thiscall-stores-v1', 'raise-linear-effects-v1'])
        with self.assertRaises(ValueError):
            self.submit('bad-order', recipe_json=json.dumps(recipe))
        recipe['steps'] = ['invent-semantics']
        with self.assertRaises(ValueError):
            self.submit('bad-step', recipe_json=json.dumps(recipe))

    def regression(self, token, rva=0x1040, **extra):
        function_id = self.client.call('function_query', project_id='open', limit=4)['items'][(0x1000, 0x1030, 0x1040, 0x1050).index(rva)]['function_id']
        return self.client.call('replayable_regression_check', project_id='open', function_id=function_id, idempotency_key=token, compile=False, **extra)

    def test_regression_validates_inventory_identity_and_expected_hash(self):
        for identity in ('', '0x1040', 'unknown', 'f' * 64):
            with self.assertRaises(ValueError):
                self.client.call('replayable_regression_check', project_id='open', function_id=identity, idempotency_key='invalid', compile=False)
        for expected in ('', 'a' * 63, 'g' * 64, 'A' * 64):
            with self.assertRaises(ValueError):
                self.regression('invalid-hash', expected_source_sha256=expected)
        self.assertEqual(self.client.call('replayable_status', project_id='open')['regression_row_count'], 0)

    def test_regression_failure_retained_idempotent_and_explicit_retry(self):
        first = self.regression('regression-failure', expected_source_sha256='a' * 64)
        self.assertFalse(first['ascending_frontier'])
        self.assertEqual(first['purpose'], 'regression')
        done = stdio.wait_job(self.client, first['job_id'])
        self.assertEqual(done['result']['status'], 'inconclusive')
        self.assertEqual(self.regression('regression-failure', expected_source_sha256='a' * 64)['job_id'], first['job_id'])
        for kwargs in (dict(rva=0x1030, expected_source_sha256='a' * 64), dict(expected_source_sha256='b' * 64)):
            with self.assertRaises(ValueError):
                self.regression('regression-failure', **kwargs)
        with self.assertRaises(ValueError):
            self.submit('regression-failure')
        retry = self.regression('regression-explicit-retry')
        stdio.wait_job(self.client, retry['job_id'])
        self.assertNotEqual(retry['job_id'], first['job_id'])
        self.assertEqual(self.client.call('job_get', job_id=first['job_id'])['result'], done['result'])
        self.dll.write_bytes(b'changed actual lifter runtime')
        with self.assertRaises(ValueError):
            self.regression('regression-explicit-retry')
        changed = self.regression('regression-new-key')
        self.assertNotEqual(changed['pipeline_key'], retry['pipeline_key'])
        stdio.wait_job(self.client, changed['job_id'])

    def test_regression_matches_and_tampering_never_advance_recovery(self):
        # Persistence-only fixture: fake receipts test mode separation, not equivalence.
        import sqlite3
        first = self.regression('ahead-regression')
        stdio.wait_job(self.client, first['job_id'])
        folder = self.root / 'attempts' / first['job_id']
        (folder / 'build').mkdir()
        paths = {'source_sha256': folder / 'candidate.cpp', 'object_sha256': folder / 'build/candidate.obj', 'comparison_sha256': folder / 'comparison.json', 'callee_lifts_sha256': folder / 'callee-lifts.json', 'eh_evidence_sha256': folder / 'eh-evidence.json'}
        for path in paths.values():
            path.write_bytes(b'controlled regression receipt fixture')
        (folder / 'retained-comparison.json').write_bytes(b'controlled independent gate fixture')
        (folder / 'result.json').write_text(json.dumps(dict(status='full_match', retained_comparison_sha256=sha((folder / 'retained-comparison.json').read_bytes()), **{key: sha(path.read_bytes()) for key, path in paths.items()})))
        with closing(sqlite3.connect(self.root / 'state/jobs.sqlite3')) as db, db:
            db.execute("UPDATE replayable_frontier SET status='full_match' WHERE input_key LIKE 'regression:%'")
        status = self.client.call('replayable_status', project_id='open')
        self.assertEqual(status['regression_full_matches'], 1)
        self.assertEqual(status['ahead_regression_full_matches'], 1)
        self.assertEqual(status['new_pipeline_full_matches'], 0)
        self.assertEqual(status['first_unresolved_rva'], 0x1000)
        for path in [*paths.values(), folder / 'retained-comparison.json']:
            original = path.read_bytes()
            path.write_bytes(b'changed')
            self.assertEqual(self.client.call('replayable_status', project_id='open')['regression_full_matches'], 0)
            path.write_bytes(original)
        following = self.submit('recovery-after-ahead-regression')
        self.assertEqual(following['rva'], 0x1000)
        stdio.wait_job(self.client, following['job_id'])

    def test_cross_mode_cross_version_running_and_unknown_barriers(self):
        import sqlite3
        for origin in ('recovery', 'regression'):
            for state in ('running', 'external_outcome_unknown'):
                with self.subTest(origin=origin, state=state):
                    first = self.submit('origin-' + origin + state) if origin == 'recovery' else self.regression('origin-' + origin + state)
                    stdio.wait_job(self.client, first['job_id'])
                    table = 'replayable_frontier'
                    with closing(sqlite3.connect(self.root / 'state/jobs.sqlite3')) as db, db:
                        db.execute('UPDATE ' + table + ' SET status=? WHERE job=?', (state, first['job_id']))
                    self.dll.write_bytes(('changed runtime ' + origin + state).encode())
                    with self.assertRaises(ValueError):
                        self.regression('blocked-regression-' + origin + state)
                    with self.assertRaises(ValueError):
                        self.submit('blocked-recovery-' + origin + state)
                    # Remove the deliberately seeded test barrier, never production reconciliation.
                    with closing(sqlite3.connect(self.root / 'state/jobs.sqlite3')) as db, db:
                        self.assertEqual(db.execute('SELECT status FROM ' + table + ' WHERE job=?', (first['job_id'],)).fetchone()[0], state)
                        db.execute('UPDATE ' + table + " SET status='inconclusive' WHERE job=?", (first['job_id'],))

    def test_ahead_regression_never_skips_unresolved_1040(self):
        import sqlite3
        # Controlled receipts establish the selector boundary, not game matches.
        for rva in (0x1000, 0x1030):
            first = self.submit('selector-fixture-' + str(rva))
            self.assertEqual(first['rva'], rva)
            stdio.wait_job(self.client, first['job_id'])
            folder = self.root / 'attempts' / first['job_id']
            (folder / 'build').mkdir()
            paths = {'source_sha256': folder / 'candidate.cpp', 'object_sha256': folder / 'build/candidate.obj', 'comparison_sha256': folder / 'comparison.json', 'callee_lifts_sha256': folder / 'callee-lifts.json', 'eh_evidence_sha256': folder / 'eh-evidence.json'}
            for path in paths.values():
                path.write_bytes(b'controlled selector fixture')
            (folder / 'result.json').write_text(json.dumps(dict(status='full_match', **{key: sha(path.read_bytes()) for key, path in paths.items()})))
            with closing(sqlite3.connect(self.root / 'state/jobs.sqlite3')) as db, db:
                db.execute("UPDATE replayable_frontier SET status='full_match' WHERE job=?", (first['job_id'],))
        ahead = self.regression('ahead-of-1040', rva=0x1050)
        stdio.wait_job(self.client, ahead['job_id'])
        self.assertEqual(self.client.call('replayable_status', project_id='open')['first_unresolved_rva'], 0x1040)
        next_job = self.submit('still-1040')
        self.assertEqual(next_job['rva'], 0x1040)
        stdio.wait_job(self.client, next_job['job_id'])

    def test_legacy_recovery_request_remains_idempotent(self):
        import sqlite3
        first = self.submit('legacy-request')
        stdio.wait_job(self.client, first['job_id'])
        with closing(sqlite3.connect(self.root / 'state/jobs.sqlite3')) as db, db:
            request = json.loads(db.execute('SELECT request FROM jobs WHERE id=?', (first['job_id'],)).fetchone()[0])
            request.pop('purpose')
            request.pop('expected_source_sha256')
            db.execute('UPDATE jobs SET request=? WHERE id=?', (json.dumps(request), first['job_id']))
        self.assertEqual(self.submit('legacy-request')['job_id'], first['job_id'])
        with self.assertRaises(ValueError):
            self.regression('legacy-request', rva=0x1000)

    def test_regression_running_is_visible_to_legacy_project_barrier_query(self):
        import sqlite3
        first = self.regression('legacy-barrier-visibility')
        stdio.wait_job(self.client, first['job_id'])
        with closing(sqlite3.connect(self.root / 'state/jobs.sqlite3')) as db, db:
            db.execute("UPDATE replayable_frontier SET status='external_outcome_unknown' WHERE job=?", (first['job_id'],))
            row = db.execute("SELECT job FROM replayable_frontier WHERE project=? AND status IN ('running','external_outcome_unknown') ORDER BY rva,input_key LIMIT 1", ('open',)).fetchone()
            self.assertEqual(row, (first['job_id'],))
            tracking_key = db.execute('SELECT input_key FROM replayable_frontier WHERE job=?', (first['job_id'],)).fetchone()[0]
            self.assertEqual(tracking_key, 'regression:' + first['pipeline_key'])

    def test_stack_recipe_explicit_key_frontier_and_uncertainty_barrier(self):
        import sqlite3
        recipe=dict(schema_version=1,architecture='x86-bits32-linear-tail-stack-v1',frontend='sharpretro-typed-v1',compiler_profile='vc8-x86-flat32-addressable-stack-v1',steps=['raise-linear-effects-tail-v2','derive-original-normal-return-stack-v1','emit-vc8-composed-stack-v1'])
        baseline=self.client.call('replayable_status',project_id='open')
        selected=self.client.call('replayable_status',project_id='open',recipe_json=json.dumps(recipe))
        self.assertNotEqual(selected['pipeline_key'],baseline['pipeline_key']);self.assertEqual(selected['first_unresolved_rva'],0x1000)
        first=self.submit('stack-selected',recipe_json=json.dumps(recipe));stdio.wait_job(self.client,first['job_id'])
        self.assertEqual(first['rva'],0x1000)
        self.assertEqual(self.submit('stack-selected',recipe_json=json.dumps(recipe))['job_id'],first['job_id'])
        with self.assertRaises(ValueError):self.submit('stack-selected')
        bad=dict(recipe,steps=list(reversed(recipe['steps'])))
        with self.assertRaises(ValueError):self.submit('stack-bad-order',recipe_json=json.dumps(bad))
        for state in ('running','external_outcome_unknown'):
            with closing(sqlite3.connect(self.root/'state/jobs.sqlite3')) as db,db:db.execute('UPDATE replayable_frontier SET status=?',(state,))
            with self.assertRaises(ValueError):self.submit('stack-cross-'+state)
            with self.assertRaises(ValueError):self.regression('stack-regression-cross-'+state,recipe_json=json.dumps(recipe))

    def test_conditional_recipe_is_explicit_and_does_not_skip_or_clear_unknown(self):
        import sqlite3
        recipe=dict(schema_version=1,architecture='x86-bits32-one-forward-conditional-v1',frontend='sharpretro-typed-v1',compiler_profile='vc8-x86-flat32-conditional-calls-v1',steps=['raise-linear-effects-tail-v2','derive-original-normal-return-stack-v1','resolve-pure-forwarding-normal-return-v1','raise-one-forward-conditional-v1','emit-vc8-composed-conditional-v1'])
        baseline=self.client.call('replayable_status',project_id='open');selected=self.client.call('replayable_status',project_id='open',recipe_json=json.dumps(recipe));self.assertNotEqual(selected['pipeline_key'],baseline['pipeline_key']);self.assertEqual(selected['first_unresolved_rva'],0x1000)
        first=self.submit('conditional-selected',recipe_json=json.dumps(recipe));stdio.wait_job(self.client,first['job_id']);self.assertEqual(self.submit('conditional-selected',recipe_json=json.dumps(recipe))['job_id'],first['job_id'])
        with self.assertRaises(ValueError):self.submit('conditional-selected')
        bad=dict(recipe,steps=list(reversed(recipe['steps'])))
        with self.assertRaises(ValueError):self.submit('conditional-bad-order',recipe_json=json.dumps(bad))
        ahead=self.regression('conditional-ahead',recipe_json=json.dumps(recipe));stdio.wait_job(self.client,ahead['job_id']);self.assertEqual(self.client.call('replayable_status',project_id='open',recipe_json=json.dumps(recipe))['first_unresolved_rva'],0x1000)
        with closing(sqlite3.connect(self.root/'state/jobs.sqlite3')) as db,db:db.execute("UPDATE replayable_frontier SET status='external_outcome_unknown' WHERE job=?",(first['job_id'],))
        for extra in ({},{'recipe_json':json.dumps(recipe)}):
            with self.assertRaises(ValueError):self.submit('conditional-unknown-cross-'+str(len(extra)),**extra)

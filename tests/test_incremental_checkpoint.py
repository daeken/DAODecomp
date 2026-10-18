import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools import incremental_checkpoint as cache


class IncrementalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        for name in ['src/a.cpp', 'contracts/a.json', 'analysis/functions.json',
                     'analysis/reference-build.json', 'report.json', 'candidate', 'mutant',
                     'gamedata/bin_ship/DAOrigins.exe', 'build-incremental-fixture/CMakeCache.txt',
                     'build-incremental-fixture/compile_commands.json', 'build-incremental-fixture/dao_leaf_runner', 'build-incremental-fixture/dao_leaf_mutant']:
            p = self.root/name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('{}' if p.suffix == '.json' else 'fixture')
        (self.root/'build-incremental-fixture'/cache.OWNER_FILE).write_text(json.dumps(
            cache.owner_document(self.root, self.root/'build-incremental-fixture')))
        real_output = cache.subprocess.check_output
        def fixture_otool(argv, **kwargs):
            if argv[:2] == ['otool', '-L'] and str(self.root/'build-incremental-fixture') in argv[-1]:
                return argv[-1]+':\n'
            return real_output(argv, **kwargs)
        transport_patch = patch.object(cache.subprocess, 'check_output', side_effect=fixture_otool)
        transport_patch.start(); self.addCleanup(transport_patch.stop)
        self.fixture_case = {'id': 'fixture', 'inputs': {'value': 1}}
        self.case_binding = {'case_id': 'fixture', 'case_sha256': cache.digest(self.fixture_case)}
        self.corpus_binding = {'sha256': cache.digest([self.fixture_case]), 'rows': [self.case_binding]}
        corpus_patch = patch.object(cache, 'actual_corpora', side_effect=lambda group, functions:
            {f['id']: {'positive': self.corpus_binding, 'negative': self.corpus_binding} for f in functions})
        corpus_patch.start(); self.addCleanup(corpus_patch.stop)
        self.function = dict(id='binary+module+rva', name='a', backend='scalar',
                             status='implemented', source='src/a.cpp', contract='contracts/a.json')
        self.registry = {'schema_version': 1, 'functions': [self.function]}
        self.identity = cache.group_identity(self.root, self.root/'build-incremental-fixture', 'scalar',
                                            self.registry, {'src/a.cpp': 'source'},
                                            {'provider': 'macos-full-python-dyld-v1', 'files': {'libunicorn': 'x'}},
                                            {'mode': 'single', 'commands': [{'step':'scalar_all','argv':['scalar_all']},
                                             {'step':'scalar_negative','argv':['scalar_negative']}]})
        artifacts = {n: cache.file_hash(self.root/n) for n in
                     ['src/a.cpp', 'contracts/a.json', 'analysis/functions.json', 'analysis/reference-build.json', 'build-incremental-fixture/dao_leaf_runner', 'build-incremental-fixture/dao_leaf_mutant']}
        self.report = dict(schema_version=1, kind='game', proof=False, native_windows_validated=False,
                           function_id=self.function['id'], artifacts_unchanged=True,
                           repeats=2, status='corpus_pass', cases=[dict(self.case_binding, status='corpus_pass')],
                           corpus_sha256=self.corpus_binding['sha256'],
                           artifacts_sha256=artifacts, contract_sha256=cache.digest({}))
        self.path = self.root/'report.json'
        self.save_report()

    def save_report(self):
        self.path.write_text(json.dumps(self.report))
        record = {'report_sha256': cache.file_hash(self.path), 'negative_control': False,
                  'case_counts': {'corpus_pass': 1}}
        self.entry = dict(schema_version=cache.VERSION, policy=cache.POLICY,
                          identity=self.identity, payload={str(self.path): record})
        self.entry['payload_sha256'] = cache.digest(self.entry['payload'])

    def verify(self):
        return cache.verify_entry(self.root, self.entry, self.identity, {str(self.path): False})

    def test_declared_linked_validation_dependency_is_strict_current_input(self):
        # Synthetic report fixture: tests the role/hash gate, not game execution.
        name = 'tests/test_linked_structures.py'
        dependency = self.root/name
        dependency.parent.mkdir(); dependency.write_text('original test dependency')
        self.identity['group'] = 'linked_structures'
        self.identity['source'][name] = cache.file_hash(dependency)
        self.report['artifacts_sha256'][name] = cache.file_hash(dependency)
        self.save_report()
        self.verify()
        dependency.write_text('changed test dependency')
        with self.assertRaisesRegex(ValueError, 'stale comparison execution artifact'):
            self.verify()
        dependency.unlink()
        with self.assertRaises(FileNotFoundError):
            self.verify()

    def test_exact_hit(self):
        self.assertEqual(len(self.verify()), 1)

    def test_unrelated_registry_addition_keeps_key(self):
        changed = copy.deepcopy(self.registry)
        changed['functions'].append(dict(self.function, id='other', name='other', backend='memory-001'))
        actual = cache.group_identity(self.root, self.root/'build-incremental-fixture', 'scalar', changed,
                                     self.identity['source'], self.identity['runtime'], self.identity['execution'])
        self.assertEqual(actual, self.identity)
        (self.root/'analysis/functions.json').write_text(json.dumps(changed))
        self.verify()

    def test_selected_registry_mutations(self):
        for key, value in [('name', 'b'), ('pilot', 'new'), ('abi', 'changed'), ('backend', 'memory-001')]:
            with self.subTest(key=key):
                changed = copy.deepcopy(self.registry)
                changed['functions'][0][key] = value
                actual = cache.group_identity(self.root, self.root/'build-incremental-fixture', 'scalar', changed,
                                             self.identity['source'], self.identity['runtime'], self.identity['execution'])
                self.assertNotEqual(actual, self.identity)

    def test_source_runtime_contract_corpus_and_dependency_mutation(self):
        for key in ('source', 'runtime', 'executables', 'contracts'):
            with self.subTest(key=key):
                changed = copy.deepcopy(self.identity)
                changed[key]['mutation'] = 'new'
                with self.assertRaises(ValueError):
                    cache.verify_entry(self.root, self.entry, changed, {str(self.path): False})
        for name in ('contracts/a.json', 'build-incremental-fixture/dao_leaf_runner', 'build-incremental-fixture/dao_leaf_mutant', 'analysis/reference-build.json'):
            with self.subTest(artifact=name):
                path = self.root/name
                old = path.read_bytes()
                path.write_bytes(old+b'x')
                with self.assertRaises(ValueError):
                    self.verify()
                path.write_bytes(old)
        # Corpus is a cached immutable report input, never regenerated from claims.
        self.report['artifacts_sha256']['cases.json'] = cache.file_hash(self.path)
        self.save_report()
        with self.assertRaises(FileNotFoundError):
            self.verify()

    def test_missing_tampered_cache_and_reports(self):
        for field, value in [('schema_version', 1), ('policy', 'unknown'), ('payload_sha256', 'tampered')]:
            old = self.entry[field]
            self.entry[field] = value
            with self.assertRaises(ValueError):
                self.verify()
            self.entry[field] = old
        self.path.write_text('{}')
        with self.assertRaises(ValueError):
            self.verify()
        self.path.unlink()
        with self.assertRaises(FileNotFoundError):
            self.verify()

    def test_control_completeness(self):
        with self.assertRaises(ValueError):
            cache.verify_entry(self.root, self.entry, self.identity,
                               {str(self.path): False, str(self.root/'negative.json'): True})
        with self.assertRaises(ValueError):
            cache.verify_entry(self.root, self.entry, self.identity, {str(self.path): True})

    def test_errors_nondeterminism_unknown_never_pass(self):
        for status in ('error', 'unknown', 'nondeterministic', 'mismatch'):
            self.report['cases'] = [{'status': status}]
            self.save_report()
            self.entry['payload'][str(self.path)]['case_counts'] = {status: 1}
            self.entry['payload_sha256'] = cache.digest(self.entry['payload'])
            with self.assertRaises(ValueError):
                self.verify()

    def test_duplicate_and_unknown_registry_provider(self):
        for key in ('id', 'name'):
            changed = {'schema_version': 1, 'functions': [self.function, dict(self.function, id='other', name='other')]}
            changed['functions'][1][key] = self.function[key]
            with self.assertRaises(ValueError):
                cache.selected_entries(changed, 'scalar')
        with self.assertRaises(ValueError):
            cache.selected_entries({'schema_version': 1, 'functions': [dict(self.function, backend='unknown')]}, 'scalar')
        with self.assertRaises(ValueError):
            cache.group_identity(self.root, self.root/'build-incremental-fixture', 'scalar', self.registry, {}, {'provider': 'unknown'})

    def test_runtime_absent_provider_fails_closed(self):
        with patch.object(cache.sys, 'platform', 'unknown'):
            with self.assertRaises(ValueError):
                cache.runtime_manifest()

    def test_source_tree_membership(self):
        (self.root/'CMakeLists.txt').write_text('x')
        (self.root/'requirements-validation.txt').write_text('x')
        before = cache.source_manifest(self.root)
        (self.root/'src/shadow.hpp').write_text('new shadow header')
        self.assertNotEqual(before, cache.source_manifest(self.root))

    def test_publication_keeps_historical_registry_and_current_provenance(self):
        historical = dict(self.entry['payload'][str(self.path)],
                          function_id=self.function['id'], report='report.json',
                          artifacts_sha256=self.report['artifacts_sha256'], status='corpus_pass',
                          artifacts_unchanged=True, repeats_per_side=2)
        result = dict(schema_version=2, policy=cache.POLICY, status='passed',
                      complete_checkpoint=True, usable_for_progress=True,
                      source={'src/a.cpp': cache.file_hash(self.root/'src/a.cpp'),
                              'contracts/a.json': cache.file_hash(self.root/'contracts/a.json'),
                              'analysis/reference-build.json': cache.file_hash(self.root/'analysis/reference-build.json')},
                      registry_sha256='new-registry', groups=[dict(records=[historical],
                      reused=True, identity_sha256=cache.digest(self.identity))])
        with patch.object(cache,'publication_inventory',return_value={(self.function['id'],False)}):
            doc = cache.publication_document(result)
        record = doc['records'][0]
        self.assertEqual(record['artifacts_sha256']['analysis/functions.json'], 'new-registry')
        self.assertEqual(record['historical_comparison']['artifacts_sha256']['analysis/functions.json'],
                         self.report['artifacts_sha256']['analysis/functions.json'])
        from tools.update_progress import Snapshot
        (self.root/'analysis/functions.json').write_text(json.dumps(self.registry))
        target = self.root/'analysis/validation/reused.json'
        target.parent.mkdir()
        target.write_text(json.dumps(doc))
        self.assertEqual(Snapshot(self.root).document('analysis/validation/reused.json'), doc)
        for field, value in [('policy', 'unknown'), ('fresh_clean_build', False),
                             ('complete_checkpoint', False), ('schema_version', 3)]:
            changed = copy.deepcopy(doc)
            changed[field] = value
            unsigned = {k:v for k,v in changed.items() if k != 'attestation_sha256'}
            changed['attestation_sha256'] = cache.digest(unsigned)
            target.write_text(json.dumps(changed))
            with self.assertRaises(ValueError):
                Snapshot(self.root).document('analysis/validation/reused.json')
        result['usable_for_progress'] = False
        with self.assertRaises(ValueError):
            cache.publication_document(result)

    def test_runtime_environment_does_not_store_credentials(self):
        source = Path(cache.__file__).read_text()
        self.assertNotIn("'environment': dict", source)
        self.assertIn("'environment_sha256'", source)

    def test_native_dependency_unknown_fails_closed(self):
        with patch.object(cache.subprocess, 'check_output', return_value='fixture:\n\t@rpath/unknown.dylib (compatibility version 1.0.0)\n'):
            with self.assertRaises(ValueError):
                cache.native_dependencies([self.root/'candidate'])

    def test_cache_lookup_reports_miss_for_incomplete_or_mutated_inputs(self):
        path = self.root/'entry.json'
        path.write_text(json.dumps(self.entry))
        self.assertIsNotNone(cache.lookup_entry(self.root, path, self.identity, {str(self.path): False})[1])
        for field in ('source', 'runtime', 'executables', 'contracts'):
            changed = copy.deepcopy(self.identity)
            changed[field]['changed'] = True
            self.assertEqual(cache.lookup_entry(self.root, path, changed, {str(self.path): False}), (None, None))
        self.assertEqual(cache.lookup_entry(self.root, path, self.identity,
                         {str(self.path): False, str(self.root/'control.json'): True}), (None, None))
        path.write_text('{tampered')
        self.assertEqual(cache.lookup_entry(self.root, path, self.identity, {str(self.path): False}), (None, None))
        path.unlink()
        self.assertEqual(cache.lookup_entry(self.root, path, self.identity, {str(self.path): False}), (None, None))

    def lifecycle(self, fail_boundary=False):
        # Synthetic lifecycle fixture only. Real CMake and original-slice runs
        # are measured separately; these seams exercise cache publication order.
        (self.root/'analysis/functions.json').write_text(json.dumps(self.registry))
        names = ['configure', 'build', 'unittest', 'ctest', 'demo_good', 'demo_mutant']
        names += [g+s for g in cache.LEGACY_GROUPS for s in ('_all', '_negative')]
        executed = []
        def plan(build, output, jobs):
            return [(name, [name], self.root) for name in names]
        def paths(output):
            folder = output/'reports/scalar'
            return [folder/'a-all.json'], [folder/'a-mutant.json']
        def execute(argv, cwd, log):
            executed.append(argv[0])
            if argv[0] == 'build':
                for suffix in ('_runner', '_mutant'):
                    (self.root/'build-incremental-fixture'/('dao_leaf'+suffix)).write_text('fixture')
            if argv[0] in ('scalar_all', 'scalar_negative'):
                report = copy.deepcopy(self.report)
                negative = argv[0] == 'scalar_negative'
                if negative:
                    report['status'] = 'mismatch'
                    report['cases'] = [dict(self.case_binding, status='mismatch')]
                positives, negatives = paths(log.parent)
                path = (negatives if negative else positives)[0]
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(report))
        def record(root, path, function, negative=False):
            report = json.loads(Path(path).read_text())
            return dict(function_id=function['id'], report=str(Path(path).relative_to(root)),
                        report_sha256=cache.file_hash(path), negative_control=negative,
                        artifacts_sha256=report['artifacts_sha256'],
                        case_counts={'mismatch' if negative else 'corpus_pass': 1})
        source = self.identity['source']
        manifests = [source, source, {'changed': 'during-validation'}] if fail_boundary else [source]*3
        with patch.object(cache, 'ROOT', self.root), \
             patch.object(cache.checkpoint, 'build_commands', side_effect=plan), \
             patch.object(cache.checkpoint, 'publication_paths', side_effect=paths), \
             patch.object(cache, 'execute', side_effect=execute), \
             patch.object(cache, 'record_report', side_effect=record), \
             patch.object(cache, 'current_runtime', return_value=self.identity['runtime']), \
             patch.object(cache, 'build_provenance', return_value={'files': {}}), \
             patch.object(cache, 'source_manifest', side_effect=manifests):
            first = cache.run(self.root/'build-incremental-fixture', self.root/'reports/first', self.root/'local/cache', 2, ['scalar'])
        return first, executed

    def test_driver_seed_then_unrelated_registry_reuse(self):
        first, executed = self.lifecycle()
        self.assertFalse(first['groups'][0]['reused'])
        self.assertEqual(executed.count('scalar_all'), 1)
        self.assertEqual(executed.count('scalar_negative'), 1)
        entry = Path(first['groups'][0]['cache'])
        historical_hash = cache.file_hash(entry)
        original_report = self.root/first['groups'][0]['records'][0]['report']
        report_hash = cache.file_hash(original_report)
        changed = copy.deepcopy(self.registry)
        changed['functions'].append(dict(self.function, id='unrelated', name='unrelated',
                                         backend='memory-001', status='inventoried'))
        (self.root/'analysis/functions.json').write_text(json.dumps(changed))
        # Real files remain immutable; fresh infrastructure steps are exercised
        # through the same driver seam while exact saved report bytes are checked.
        names = ['configure', 'build', 'unittest', 'ctest', 'demo_good', 'demo_mutant']
        names += [g+s for g in cache.LEGACY_GROUPS for s in ('_all', '_negative')]
        executed = []
        def paths(output):
            folder = output/'reports/scalar'
            return [folder/'a-all.json'], [folder/'a-mutant.json']
        def execute_second(argv, cwd, log):
            executed.append(argv[0])
            if argv[0] == 'build':
                for suffix in ('_runner', '_mutant'):
                    (self.root/'build-incremental-fixture'/('dao_leaf'+suffix)).write_text('fixture')
        with patch.object(cache, 'ROOT', self.root), \
             patch.object(cache.checkpoint, 'build_commands', return_value=[(n,[n],self.root) for n in names]), \
             patch.object(cache.checkpoint, 'publication_paths', side_effect=paths), \
             patch.object(cache, 'execute', side_effect=execute_second), \
             patch.object(cache, 'current_runtime', return_value=self.identity['runtime']), \
             patch.object(cache, 'build_provenance', return_value={'files': {}}), \
             patch.object(cache, 'source_manifest', return_value=self.identity['source']):
            second = cache.run(self.root/'build-incremental-fixture', self.root/'reports/second', self.root/'local/cache', 2, ['scalar'])
        self.assertTrue(second['groups'][0]['reused'])
        self.assertEqual(executed, names[:6])
        self.assertEqual(historical_hash, cache.file_hash(entry))
        self.assertEqual(report_hash, cache.file_hash(original_report))
        self.assertFalse(second['usable_for_progress'])

    def test_failed_boundary_never_publishes_cache_seed(self):
        with self.assertRaisesRegex(ValueError, 'source changed'):
            self.lifecycle(fail_boundary=True)
        self.assertEqual(list((self.root/'local/cache').glob('*.json')), [])


    def test_invocation_metadata_is_excluded_but_kept_hash_only(self):
        base = {'PATH': '/runtime/bin', 'LIBUNICORN_PATH': '/runtime/unicorn',
                'CODEX_TOOL_CALL_ID': 'invocation-a', 'SHLVL': '1'}
        changed = dict(base, CODEX_TOOL_CALL_ID='invocation-b', SHLVL='2')
        self.assertEqual(cache.environment_identity(base), cache.environment_identity(changed))
        self.assertNotEqual(cache.invocation_environment(base), cache.invocation_environment(changed))
        self.assertNotIn('invocation-a', json.dumps(cache.invocation_environment(base)))
        for name in ('PATH', 'LIBUNICORN_PATH', 'PYTHONPATH', 'DYLD_LIBRARY_PATH', 'LC_ALL'):
            with self.subTest(name=name):
                self.assertNotEqual(cache.environment_identity(base),
                                    cache.environment_identity(dict(base, **{name: 'changed'})))

    def test_identity_only_cannot_execute_or_publish_comparisons(self):
        (self.root/'analysis/functions.json').write_text(json.dumps(self.registry))
        names = ['configure', 'build', 'unittest', 'ctest', 'demo_good', 'demo_mutant']
        names += [g+s for g in cache.LEGACY_GROUPS for s in ('_all', '_negative')]
        calls = []
        def execute(argv, cwd, log):
            calls.append(argv[0])
            if argv[0] == 'build':
                for suffix in ('_runner', '_mutant'):
                    (self.root/'build-incremental-fixture'/('dao_leaf'+suffix)).write_text('fixture')
        with patch.object(cache, 'ROOT', self.root), \
             patch.object(cache.checkpoint, 'build_commands', return_value=[(n,[n],self.root) for n in names]), \
             patch.object(cache.checkpoint, 'publication_paths', return_value=([self.root/'reports/plan/reports/scalar/a-all.json'],[])), \
             patch.object(cache, 'execute', side_effect=execute), \
             patch.object(cache, 'current_runtime', return_value=self.identity['runtime']), \
             patch.object(cache, 'build_provenance', return_value={'files': {}}), \
             patch.object(cache, 'source_manifest', return_value=self.identity['source']):
            result = cache.run(self.root/'build-incremental-fixture', self.root/'reports/plan', self.root/'local/cache', 2, ['scalar'], True)
        self.assertEqual(calls, ['configure', 'build'])
        self.assertEqual(result['status'], 'identity_only')
        self.assertFalse(result['usable_for_progress'])
        self.assertEqual(list((self.root/'local/cache').glob('*.json')), [])
        self.assertFalse((self.root/'reports/plan/current-evidence.json').exists())


    def test_other_group_compiled_source_contract_and_build_metadata_do_not_enter_execution_key(self):
        source = {'src/a.cpp': 'old-cpp', 'include/dao/a.hpp': 'old-header',
                  'contracts/other.json': 'old-other-contract', 'tools/daodecomp/harness.py': 'strict-comparator'}
        first = cache.group_identity(self.root, self.root/'build-incremental-fixture', 'scalar',
                                    self.registry, source, self.identity['runtime'], self.identity['execution'])
        changed = dict(source, **{'src/a.cpp': 'new-cpp', 'include/dao/a.hpp': 'new-header',
                                 'contracts/other.json': 'new-other-contract', 'CMakeLists.txt': 'new-build'})
        second = cache.group_identity(self.root, self.root/'build-incremental-fixture', 'scalar',
                                     self.registry, changed, self.identity['runtime'], self.identity['execution'])
        self.assertEqual(first, second)
        changed['tools/daodecomp/harness.py'] = 'changed-comparator'
        self.assertNotEqual(first, cache.group_identity(self.root, self.root/'build-incremental-fixture', 'scalar',
                            self.registry, changed, self.identity['runtime'], self.identity['execution']))
        (self.root/'src/a.cpp').write_text('current source is separately attested after fresh build')
        self.verify()  # Old source hash stays historical, never relabeled current.

    def test_unowned_or_symlink_build_directory_is_never_cleared(self):
        directory = self.root/'build-incremental-unowned'
        directory.mkdir(); kept = directory/'keep.txt'; kept.write_text('must survive')
        with self.assertRaises(ValueError):
            cache.prepare_build(self.root, directory)
        self.assertEqual(kept.read_text(), 'must survive')
        link = self.root/'build-incremental-link'; link.symlink_to(directory, target_is_directory=True)
        with self.assertRaises(ValueError):
            cache.prepare_build(self.root, link)
        self.assertEqual(kept.read_text(), 'must survive')
        with self.assertRaises(ValueError):
            cache.prepare_build(self.root, self.root/'src')

    def test_owned_build_is_genuinely_empty_and_stale_archives_are_removed(self):
        build = self.root/'build-incremental-fixture'
        stale = build/'old-imported-library.a'; stale.write_text('stale')
        cache.prepare_build(self.root, build)
        self.assertEqual([p.name for p in build.iterdir()], [cache.OWNER_FILE])
        self.assertFalse(stale.exists())

    def test_unknown_historical_artifact_role_and_incomplete_corpus_rows_fail_closed(self):
        unknown = self.root/'unknown-input.bin'; unknown.write_text('unknown closure')
        self.report['artifacts_sha256']['unknown-input.bin'] = cache.file_hash(unknown)
        self.save_report()
        with self.assertRaisesRegex(ValueError, 'unknown historical artifact'):
            self.verify()
        self.report['artifacts_sha256'].pop('unknown-input.bin')
        self.report['cases'][0]['case_sha256'] = 'dropped/replaced actual corpus case'
        self.save_report()
        with self.assertRaisesRegex(ValueError, 'cached corpus differs'):
            self.verify()

    def test_provider_alias_membership_and_resolution_mutations_are_bound(self):
        provider = self.root/'runtime-provider'; provider.mkdir()
        a = provider/'a.py'; b = provider/'b.py'; a.write_text('same bytes'); b.write_text('same bytes')
        alias = provider/'alias.py'; alias.symlink_to(a)
        paths, first = cache.provider_inventory([provider])
        alias.unlink(); alias.symlink_to(b)
        _, second = cache.provider_inventory([provider])
        self.assertNotEqual(first, second)
        self.assertIn(str(alias), first)
        external = self.root/'outside-provider'; external.mkdir()
        shadow = provider/'shadow-package'; shadow.symlink_to(external, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'unknown linked Python provider'):
            cache.provider_inventory([provider])

    def test_execution_mode_and_flags_change_identity(self):
        steps = [('indexed_fields_all', ['python', 'validator', '--report-dir', 'a', '--execution', 'batch', '--batch-size', '64'], self.root),
                 ('indexed_fields_negative', ['python', 'validator', '--expect-mismatch', '--report-dir', 'a', '--execution', 'batch', '--batch-size', '64'], self.root)]
        first = cache.group_execution(steps, 'indexed_fields')
        changed_output = [(n, [v if v != 'a' else 'new-output' for v in argv], cwd) for n,argv,cwd in steps]
        self.assertEqual(first, cache.group_execution(changed_output, 'indexed_fields'))
        changed_flags = [(n, [v if v != '64' else '128' for v in argv], cwd) for n,argv,cwd in steps]
        self.assertNotEqual(first, cache.group_execution(changed_flags, 'indexed_fields'))



if __name__ == '__main__':
    unittest.main()

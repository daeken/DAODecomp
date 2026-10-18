"""Artifact declaration probes use synthetic comparison results, never game evidence."""
import contextlib
import importlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from tools import incremental_checkpoint as cache

ROOT = Path(__file__).resolve().parents[1]
MODULES = {
    'scalar': 'validate_leaves', 'memory': 'validate_memory',
    'object_counters': 'validate_object_counters', 'indexed_stores': 'validate_indexed_stores',
    'indexed_fields': 'validate_indexed_fields', 'linked_structures': 'validate_linked_structures',
    'object_bitfields': 'validate_object_bitfields',
    'direct_object_fields': 'validate_direct_object_fields',
}


class DeclaredArtifactRoleTests(unittest.TestCase):
    @unittest.skipUnless(os.name == 'posix', 'declared batch validators require POSIX')
    def test_all_eight_groups_live_positive_and_negative_declarations_have_roles(self):
        registry = json.loads((ROOT/'analysis/functions.json').read_text())
        source = cache.source_manifest(ROOT)
        by_id = {f['id']: f for f in registry['functions']}
        seen = {}
        # Dummy outputs exist only for validator preflight. compare/compare_batch
        # are intercepted: no emulator, native function, or acceptance comparison runs.
        with tempfile.TemporaryDirectory(prefix='build-incremental-artifact-test-', dir=ROOT) as temp:
            build = Path(temp)
            binary = build/'declaration-only-original.exe'; binary.write_bytes(b'unit fixture')
            for group, (_, prefix) in cache.GROUPS.items():
                for suffix in ('_runner', '_mutant'):
                    (build/(prefix+suffix)).write_bytes(b'unit fixture')
                if group in cache.BATCH_IMAGES:
                    for suffix in ('', '_mutant'):
                        (build/('lib'+cache.BATCH_IMAGES[group]+suffix+'.dylib')).write_bytes(b'unit fixture')
                        (build/('lib'+cache.BATCH_IMAGES[group]+suffix+'.so')).write_bytes(b'unit fixture')
            (build/'CMakeCache.txt').write_text('unit fixture')
            (build/'compile_commands.json').write_text('[]')
            for group, module_name in MODULES.items():
                module = importlib.import_module('validation.'+module_name)
                expected_functions = cache.selected_entries(registry, group)
                mode = 'batch' if group in cache.BATCH_IMAGES else 'single'
                images = cache.execution_images(build, group, {'mode': mode})
                if mode == 'batch' and sys.platform != 'darwin':
                    images = [p.with_suffix('.so') for p in images]
                identity = {'group': group, 'executables': {str(p): 'unit fixture' for p in [binary, *images]},
                            'native_dependencies': {'files': {}},
                            'source': {n: h for n, h in source.items()
                                       if n.startswith(('tools/', 'validation/')) and n.endswith('.py')
                                       or n in {'requirements-validation.txt', 'analysis/reference-build.json'}},
                            'data': {}}
                for name in cache.DECLARED_VALIDATION_DEPENDENCIES.get(group, ()):
                    identity['source'][name] = source[name]
                if group == 'object_bitfields':
                    identity['data'] = {str(ROOT/'validation/object_bitfield_specs.json'): 'unit fixture',
                        **{str(ROOT/f"validation/object_bitfield_corpus/{f['name']}-{suite}.json"): 'unit fixture'
                           for f in expected_functions for suite in ('public', 'heldout')}}
                if group == 'direct_object_fields':
                    identity['data'] = {str(ROOT/'slices.json'):'unit fixture',**{str(ROOT/f"corpus/{f['name']}-{suite}.json"):'unit fixture' for f in expected_functions for suite in ('public','heldout')}}
                for negative in (False, True):
                    captures = []
                    def comparison(contract, cases, oracle, candidate, **kwargs):
                        function = by_id[contract['function_id']]
                        artifacts = list(map(Path, kwargs['artifacts']))
                        case_paths = [p for p in artifacts if p.name.endswith('-cases.json')]
                        self.assertEqual(len(case_paths), 1)
                        report = case_paths[0].with_name(case_paths[0].name.removesuffix('-cases.json')+'.json')
                        for artifact in artifacts:
                            cache.historical_role(ROOT, artifact, function, report, identity)
                        captures.append(function['id'])
                        status = 'mismatch' if negative else 'corpus_pass'
                        return {'status': status, 'artifacts_unchanged': True, 'cases': [{'status': status}]}
                    argv = [module_name, '--binary', str(binary), '--build-dir', str(build),
                            '--report-dir', str(build/group/('negative' if negative else 'positive')), '--jobs', '1']
                    argv += ['--expect-mismatch'] if negative else ['--suite', 'all']
                    if group in cache.BATCH_IMAGES:
                        argv += ['--execution', 'batch']
                    with contextlib.ExitStack() as stack:
                        stack.enter_context(patch.object(sys, 'argv', argv))
                        stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
                        stack.enter_context(patch.object(module, 'version', return_value='declaration-probe'))
                        for name in ('compare', 'compare_batch'):
                            if hasattr(module, name):
                                stack.enter_context(patch.object(module, name, side_effect=comparison))
                        self.assertEqual(module.main(), 0)
                    expected = ({f['id'] for f in expected_functions} if not negative else
                                {fid for fid, corpora in cache.actual_corpora(group, expected_functions).items()
                                 if corpora['negative'] is not None})
                    self.assertEqual(set(captures), expected, (group, negative))
                    self.assertEqual(len(captures), len(expected))
                    seen[group, negative] = len(captures)
                # An existing test file is still unknown: there is no tests/* rule.
                with self.assertRaisesRegex(ValueError, 'unknown historical artifact role'):
                    cache.historical_role(ROOT, ROOT/'tests/test_memory.py', expected_functions[0],
                                          build/'unknown.json', identity)
        self.assertEqual({g for g, negative in seen}, set(cache.GROUPS))
        self.assertEqual(sum(n for (g, negative), n in seen.items() if not negative),
                         len([f for f in registry['functions'] if f['status'] in cache.ACTIVE]))

    def test_only_exact_declared_test_is_keyed_and_changes_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); build = root/'build-incremental-fixture'; build.mkdir()
            function = {'id': 'synthetic', 'name': 'synthetic', 'status': 'implemented',
                        'backend': 'linked-structures-001', 'source': 'src/synthetic.cpp', 'contract': 'contract.json'}
            for relative in ('contract.json', 'analysis/reference-build.json', 'gamedata/bin_ship/DAOrigins.exe',
                             'build-incremental-fixture/dao_linked_structure_runner',
                             'build-incremental-fixture/dao_linked_structure_mutant'):
                path = root/relative; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(b'unit fixture')
            name = 'tests/test_linked_structures.py'
            source = {name: 'original-hash', 'tests/test_memory.py': 'unapproved-test'}
            def identity(values):
                return cache.group_identity(root, build, 'linked_structures',
                    {'schema_version': 1, 'functions': [function]}, values,
                    {'provider': 'macos-full-python-dyld-v1'}, {'mode': 'single'}, {})
            with patch.object(cache, 'native_dependencies', return_value={'files': {}, 'bindings': {}}):
                original = identity(source)
                self.assertEqual(original['source'], {name: 'original-hash'})
                self.assertNotEqual(original, identity({**source, name: 'changed-hash'}))
                with self.assertRaises(KeyError):
                    identity({'tests/test_memory.py': 'not-the-required-test'})
            role = cache.historical_role(root, root/name, function, root/'report.json', original)
            self.assertEqual(role, 'execution_declared_validation_dependency')
            original['source'].pop(name)
            with self.assertRaisesRegex(ValueError, 'not keyed'):
                cache.historical_role(root, root/name, function, root/'report.json', original)

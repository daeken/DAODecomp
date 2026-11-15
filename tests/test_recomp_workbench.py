"""Constructed refactor/build controls, not original-game equivalence evidence."""
import copy
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from tools import recomp, recomp_bulk
from tools import recomp_workbench as w
from tools.recomp_clangd import apply_text_edits, offset
from tools.recomp_bulk_link import manual_guards, registry_sources, step_symbol

PE32_CXX = recomp.ROOT / 'local/tools/recomp/llvm-mingw-20261104-ucrt-macos-universal/bin/i686-w64-mingw32-clang++'


RUNTIME = '''#pragma once
#include <cstdint>
#include <stdexcept>
namespace sharp_retro {
struct State { std::uint64_t pc=0; int result=0; };
struct Memory {};
enum class Exit { returned };
}
'''


def fixture(root, compiler):
    generation = root / 'bulk/runs/1'
    generation.mkdir(parents=True)
    pipeline = 'c' * 64
    backend = root / 'bulk/backends' / pipeline
    backend.mkdir(parents=True)
    (backend / 'CppRuntime.hpp').write_text(RUNTIME)
    (backend / 'IntegerRuntime.hpp').write_text('')
    recomp.atomic_json(backend / 'pipeline.json', {'backend': {
        n: w.sha(backend / n) for n in ('CppRuntime.hpp', 'IntegerRuntime.hpp')}})
    modules, records = {}, []
    for index, role in enumerate(('main', 'umbra')):
        sha = ('a' if index == 0 else 'b') * 64
        prefix = '' if index == 0 else 'm_0123456789abcdef_'
        symbol = prefix + 'fn_00001000'
        context = dict(module=role + '.exe', binary_sha256=sha, module_prefix=prefix)
        directory = generation / role
        directory.mkdir()
        recomp.atomic_json(directory / 'context.json', context)
        selection = dict(rva=4096, size=2, ranges=[dict(rva=4096, size=2)], annotations={}, structures={}, extra_entries=[])
        key = recomp_bulk.function_key(pipeline, context['module'], sha, prefix, selection)
        source = f'''#include "runtime.hpp"
namespace recomp_generated {{
sharp_retro::Exit {symbol}_step(sharp_retro::State& s,sharp_retro::Memory&,std::uint64_t&) {{
  int value = 3;
  {{ int value = 9; (void)value; }}
  const char* text = "value"; // value stays in this comment
  (void)text; s.result=value;
  return sharp_retro::Exit::returned;
}}
sharp_retro::Exit {symbol}(sharp_retro::State& s,sharp_retro::Memory& m,std::uint64_t b) {{ return {symbol}_step(s,m,b); }}
}}
'''
        metadata = dict(name=symbol, rva=4096, size=2,
            instructions=[dict(rva=4096, bytes='90', text='nop'), dict(rva=4097, bytes='c3', text='ret')],
            variables=[dict(name='value', origin='fixture:origin:outer-value', width=32)], abi={'calling_convention': 'unknown'})
        cache = root / 'bulk/cache' / key
        cache.mkdir(parents=True)
        (cache / 'function.cpp').write_text(source)
        (cache / 'function.json.gz').write_bytes(gzip.compress(recomp.encoded(metadata)))
        marker = dict(schema_version=1, artifact_key=key, binary_sha256=sha, rva=4096,
            status='generated_only', behavioral_acceptance=False,
            files={n: w.sha(cache / n) for n in ('function.cpp', 'function.json.gz')})
        recomp.atomic_json(cache / 'complete.json', marker)
        row = dict(id=f'{sha}:{context["module"]}:rva-00001000', rva=4096, module=role,
            artifact_key=key, source_file=symbol + '.cpp', source_sha256=w.sha(cache / 'function.cpp'), inventory_coverage={})
        records.append(row)
        (directory / 'catalog.jsonl').write_text(json.dumps(dict(rva=4096, key=key, selection=selection)) + '\n')
        (directory / 'results.jsonl').write_text(json.dumps(dict(id=row['id'], rva=4096, key=key, status='generated_only', coverage={})) + '\n')
        modules[role] = dict(processed=1, catalog_functions=1, inventory_functions=1, counts={'generated_only': 1})
    report = dict(pipeline=pipeline, modules=modules, status='completed inventory generation attempt; compilation/runtime remain separate')
    recomp.atomic_json(generation / 'report.json', report)
    compilation = root / 'compile/runs/1'
    compilation.mkdir(parents=True)
    inputs = dict(functions=records, generation_run=str(generation),
        generation_report_sha256=w.sha(generation / 'report.json'), runtime_sha256=recomp.digest(RUNTIME.encode()),
        compiler=str(compiler), compiler_sha256=w.sha(compiler),
        target=subprocess.check_output([str(compiler), '--print-target-triple'], text=True).strip())
    recomp.atomic_json(compilation / 'inputs.json', inputs)
    return compilation


class TextEditsTests(unittest.TestCase):
    def test_utf16_positions_and_overlaps_fail_closed(self):
        text = 'a😀b\r\nend\n'
        self.assertEqual(offset(text, dict(line=0, character=3)), 2)
        with self.assertRaisesRegex(ValueError, 'surrogate'):
            offset(text, dict(line=0, character=2))
        edit = dict(range={'start': dict(line=0, character=3), 'end': dict(line=0, character=4)}, newText='B')
        self.assertEqual(apply_text_edits(text, [edit, edit]), 'a😀B\r\nend\n')
        with self.assertRaisesRegex(ValueError, 'overlapping'):
            apply_text_edits(text, [edit, dict(edit, newText='C')])


@unittest.skipUnless(shutil.which('clang++'), 'requires a C++ compiler')
class WorkbenchTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.compilation = fixture(self.root, Path(shutil.which('clang++')).resolve())
        self.work = self.root / 'work'
        w.initialize(self.compilation, self.work)
        self.packet = w.checkout(self.work, 'main', 4096)

    def replacement(self, text, supported=None):
        path = self.root / 'candidate.cpp'
        path.write_text(text)
        return w.plan(self.work, 'main', 4096, dict(view_sha256=self.packet['view_sha256'],
            replacement_file=str(path), supported_rvas=supported or [4096]))

    def test_checkout_does_not_overwrite_and_pins_binary_module_rva(self):
        self.assertEqual(w.checkout(self.work, 'main', 4096), self.packet)
        self.assertIn('a' * 64, self.packet['identity'])
        self.assertEqual(self.packet['contract']['observations']['calling_convention'], 'unknown')
        with self.assertRaisesRegex(ValueError, 'byte budget'):
            w.packet(self.work, 'main', 4096, 10)
        w.checkout(self.work, 'umbra', 4096)
        self.assertEqual(w.packet(self.work, 'main', 4096)['view_sha256'], self.packet['view_sha256'])
        with self.assertRaisesRegex(ValueError, 'must not already'):
            w.initialize(self.compilation, self.work)

    @unittest.skipUnless(shutil.which('clangd'), 'requires clangd')
    def test_semantic_batch_rename_preserves_shadow_comments_strings_and_origin(self):
        found = w.symbols(self.work, 'main', 4096)
        values = [s for s in found['symbols'] if s['name'] == 'value']
        self.assertEqual(len(values), 2)
        request = dict(view_sha256=self.packet['view_sha256'], renames=[
            dict(line=values[0]['line'], column=values[0]['column'], new_name='counter')])
        plan = w.plan(self.work, 'main', 4096, request)
        self.assertIsNone(plan['hypotheses'][0]['origin'])  # Shadowed metadata name is ambiguous.
        self.assertTrue(plan['hypotheses'][0]['symbol_info'])
        w.apply(self.work, Path(plan['plan_file']))
        after = w.packet(self.work, 'main', 4096)['source']
        self.assertIn('int counter = 3;', after)
        self.assertIn('s.result=counter;', after)
        self.assertIn('int value = 9; (void)value;', after)
        self.assertIn('"value"; // value stays in this comment', after)
        self.assertEqual(w.blob(self.work, plan['before_sha256']).decode(), self.packet['source'])
        with self.assertRaisesRegex(ValueError, 'stale'):
            w.apply(self.work, Path(plan['plan_file']))
        with self.assertRaisesRegex(ValueError, 'stale'):
            w.plan(self.work, 'main', 4096, request)

    @unittest.skipUnless(shutil.which('clangd'), 'requires clangd')
    def test_stable_entry_symbol_cannot_be_renamed(self):
        found = w.symbols(self.work, 'main', 4096)
        symbol = next(s for s in found['symbols'] if s['name'] == 'fn_00001000')
        with self.assertRaisesRegex(ValueError, 'stable dispatcher'):
            w.plan(self.work, 'main', 4096, dict(view_sha256=self.packet['view_sha256'],
                renames=[dict(line=symbol['line'], column=symbol['column'], new_name='new_function')]))

    @unittest.skipUnless(shutil.which('clangd'), 'requires clangd')
    def test_rename_merges_portable_and_native_preprocessor_references(self):
        source = self.packet['source'].replace('(void)text; s.result=value;',
            '(void)text;\n#if defined(RECOMP_NATIVE_EXECUTION)\n s.result=value;\n#else\n s.result=value+0;\n#endif')
        replacement = self.replacement(source, [4096, 4097])
        w.apply(self.work, Path(replacement['plan_file']))
        packet = w.packet(self.work, 'main', 4096)
        found = w.symbols(self.work, 'main', 4096)
        value = next(s for s in found['symbols'] if s['name'] == 'value')
        proposal = w.plan(self.work, 'main', 4096, dict(view_sha256=packet['view_sha256'],
            renames=[dict(line=value['line'], column=value['column'], new_name='counter')]))
        self.assertEqual(proposal['hypotheses'][0]['compiler_profiles'], ['portable', 'pinned_native'])
        w.apply(self.work, Path(proposal['plan_file']))
        after = w.packet(self.work, 'main', 4096)['source']
        self.assertIn('s.result=counter;', after)
        self.assertIn('s.result=counter+0;', after)
        self.assertIn('int value = 9; (void)value;', after)

    def test_compile_failure_and_wrong_signature_leave_sources_and_ledger_unchanged(self):
        ledger = (self.work / 'workbench.json').read_bytes()
        for source in ('this is invalid c++', self.packet['source'].replace('std::uint64_t b)', 'std::uint64_t* b)')):
            plan = self.replacement(source)
            with self.assertRaisesRegex(ValueError, 'compiler rejected'):
                w.apply(self.work, Path(plan['plan_file']))
            self.assertEqual((self.work / 'workbench.json').read_bytes(), ledger)
            self.assertEqual(w.packet(self.work, 'main', 4096), self.packet)

    def test_rewrite_requires_explicit_entry_support_and_immutable_plan(self):
        candidate = self.root / 'draft.cpp'
        candidate.write_text(self.packet['source'])
        request = dict(view_sha256=self.packet['view_sha256'], replacement_file=str(candidate))
        with self.assertRaisesRegex(ValueError, 'explicitly declare'):
            w.plan(self.work, 'main', 4096, request)
        for entries in ([4097], [4096, 9000], [True]):
            with self.assertRaisesRegex(ValueError, 'supported_rvas'):
                w.plan(self.work, 'main', 4096, dict(request, supported_rvas=entries))
        plan = self.replacement(self.packet['source'])
        wrong = self.root / 'edited-plan.json'
        recomp.atomic_json(wrong, {k: v for k, v in plan.items() if k not in ('plan_sha256', 'plan_file')})
        with self.assertRaisesRegex(ValueError, 'immutable'):
            w.apply(self.work, wrong)

    def test_editor_adopt_retains_draft_and_exports_are_authenticated(self):
        row = w.select(w.read(self.work), 'main', 4096)
        path = w.inside(self.work, row['source_path'])
        draft = self.packet['source'].replace('int value = 3;', 'int value = 4;')
        path.write_text(draft)
        with self.assertRaisesRegex(ValueError, 'unrecorded'):
            w.packet(self.work, 'main', 4096)
        plan = w.adopt(self.work, 'main', 4096, dict(view_sha256=self.packet['view_sha256'], supported_rvas=[4096]))
        self.assertEqual(path.read_text(), self.packet['source'])
        self.assertEqual(w.blob(self.work, plan['after_sha256']).decode(), draft)
        w.apply(self.work, Path(plan['plan_file']))
        output = self.root / 'export'
        w.export(self.work, output)
        manifest = output / 'manual-overrides.json'
        exported = recomp.load(manifest)
        self.assertIn('types.json', exported['files'])
        self.assertEqual(exported['shared_types']['revision'], 0)
        self.assertEqual(w.sha(output / 'types.json'), exported['files']['types.json'])
        data, rows = w.load_overrides(manifest)
        inputs = recomp.load(self.compilation / 'inputs.json')
        inputs['manual_overrides'] = dict(manifest=str(manifest), manifest_sha256=w.sha(manifest),
            baseline_inputs_sha256=data['baseline_inputs_sha256'])
        record = inputs['functions'][0]
        record['generated_source_sha256'] = record['source_sha256']
        record['source_sha256'] = rows[('main', 4096)]['committed_source_sha256']
        self.assertEqual(w.compilation_overrides(inputs)[1], data['baseline_inputs_sha256'])
        bad = copy.deepcopy(inputs);bad['functions'].pop()
        with self.assertRaisesRegex(ValueError, 'dropped'):
            w.compilation_overrides(bad)
        bad = copy.deepcopy(inputs);bad['functions'][1]['source_sha256'] = 'e' * 64
        with self.assertRaisesRegex(ValueError, 'source identity'):
            w.compilation_overrides(bad)
        (output / rows[('main', 4096)]['source_path']).write_text('changed')
        with self.assertRaisesRegex(ValueError, 'source/header changed'):
            w.load_overrides(manifest)

    def test_shared_header_checks_every_checkout_and_invalidates_old_views(self):
        w.checkout(self.work, 'umbra', 4096)
        state = w.read(self.work)
        replacement = self.root / 'types.hpp'
        replacement.write_text('#pragma once\nstruct GuestNode { std::uint32_t next; };\nstatic_assert(sizeof(GuestNode)==4);\n')
        proposal = w.header_plan(self.work, replacement, state['headers']['include/recovered_types.hpp'])
        result = w.apply(self.work, Path(proposal['plan_file']))
        self.assertEqual(len(result['report']['checks']), 2)
        self.assertNotEqual(w.packet(self.work, 'main', 4096)['view_sha256'], self.packet['view_sha256'])
        self.assertFalse(result['report']['behavioral_acceptance'])

    def test_disjoint_worker_plans_survive_other_commits_and_metadata_plans_cannot_replay(self):
        other = w.checkout(self.work, 'umbra', 4096)
        first = w.plan(self.work, 'main', 4096, dict(view_sha256=self.packet['view_sha256'],
            hypotheses=[dict(kind='naming', name='possible_counter', status='unknown')]))
        second = w.plan(self.work, 'umbra', 4096, dict(view_sha256=other['view_sha256'],
            hypotheses=[dict(kind='type', type='guest32', status='unknown')]))
        w.apply(self.work, Path(first['plan_file']))
        with self.assertRaisesRegex(ValueError, 'stale'):
            w.apply(self.work, Path(first['plan_file']))
        w.apply(self.work, Path(second['plan_file']))
        self.assertEqual(w.packet(self.work, 'umbra', 4096)['hypotheses'][0]['status'], 'unknown')

    def test_paths_and_changed_runtime_fail_closed(self):
        for path in ('../escape', '/tmp/escape'):
            with self.assertRaisesRegex(ValueError, 'relative'):
                w.inside(self.work, path)
        (self.work / 'escape').symlink_to(self.root)
        with self.assertRaisesRegex(ValueError, 'escapes'):
            w.inside(self.work, 'escape/file')
        (self.work / 'include/runtime.hpp').write_text('corrupt')
        with self.assertRaisesRegex(ValueError, 'shared header changed'):
            w.packet(self.work, 'main', 4096)

    def test_regeneration_carries_candidate_as_unapplied_plan_and_refuses_other_binary(self):
        plan = self.replacement(self.packet['source'].replace('int value = 3;', 'int value = 12;'))
        w.apply(self.work, Path(plan['plan_file']))
        from tools import recomp_types
        old_state = w.read(self.work)
        generated = self.work / recomp_types.HEADER
        generated.parent.mkdir(exist_ok=True)
        generated.write_text('#pragma once\n// custom program header\n')
        old_state['headers'][recomp_types.HEADER] = w.sha(generated)
        recomp.atomic_json(self.work / 'workbench.json', old_state)
        old_types = recomp_types.empty(old_state)
        old_types['types'] = {'test.node': dict(id='test.node', kind='struct', name='TestNode',
            fields=[], evidence=[dict(reason='fixture hypothesis')], status='hypothesis')}
        old_types['bindings'] = [dict(function_id=self.packet['identity'], object_origin='fixture:obj',
            type_id='test.node', evidence=[dict(reason='fixture association')])]
        old_types['generated_header_sha256'] = w.sha(generated)
        recomp.atomic_json(self.work / 'types.json', old_types)
        old_state['type_registry_sha256'] = w.sha(self.work / 'types.json')
        recomp.atomic_json(self.work / 'workbench.json', old_state)
        packet = w.packet(self.work, 'main', 4096)
        self.assertEqual(packet['shared_types']['revision'], 0)
        self.assertEqual(packet['shared_types']['bound_types'][0]['id'], 'test.node')
        new_compilation = fixture(self.root / 'new', Path(shutil.which('clang++')).resolve())
        output = self.root / 'rebased'
        report = w.rebase(self.work, new_compilation, output)
        carried = recomp.load(output / 'types.json')
        self.assertIn('test.node', carried['types'])
        self.assertEqual(carried['bindings'], [])
        self.assertEqual(carried['pending_bindings'][0]['status'], 'requires review')
        self.assertEqual(carried['pending_bindings'][0]['old_baseline_inputs_sha256'], old_state['baseline_inputs_sha256'])
        self.assertTrue((output / recomp_types.HEADER).exists())
        self.assertEqual(carried['generated_header_sha256'], w.sha(output / recomp_types.HEADER))
        self.assertIn('proposal only', report['results'][0]['status'])
        self.assertIn('int value = 3;', w.packet(output, 'main', 4096)['source'])
        w.apply(output, Path(report['results'][0]['plan_file']))
        self.assertIn('int value = 12;', w.packet(output, 'main', 4096)['source'])
        context = new_compilation.parent.parent.parent / 'bulk/runs/1/main/context.json'
        metadata = recomp.load(context);metadata['binary_sha256'] = 'f' * 64
        recomp.atomic_json(context, metadata)
        with self.assertRaisesRegex(ValueError, 'binary/module identity'):
            w.rebase(self.work, new_compilation, self.root / 'bad-rebase')
        self.assertFalse((self.root / 'bad-rebase').exists())


    def test_legacy_exports_without_shared_type_files_remain_loadable(self):
        output=self.root/'legacy-export';w.export(self.work,output)
        path=output/'manual-overrides.json';manifest=recomp.load(path)
        manifest.pop('shared_types');manifest['files'].pop('types.json')
        recomp.atomic_json(path,manifest)
        _,rows=w.load_overrides(path)
        self.assertIn(('main',4096),rows)
        manifest['files']['types.json']=w.sha(output/'types.json')
        recomp.atomic_json(path,manifest)
        with self.assertRaisesRegex(ValueError,'registry binding missing'):w.load_overrides(path)


@unittest.skipUnless(shutil.which('clang++'), 'requires C++ compiler')
class ManualDispatchTests(unittest.TestCase):
    def test_constructed_dispatch_guard_executes_candidate_and_refuses_unsupported_resume(self):
        rows = {('main', 4096): dict(symbol='fn_00001000', supported_rvas=[4096])}
        cpp, declarations, aliases = manual_guards(rows, {'main': {'image_base': 0x400000}})
        _, assembly = registry_sources([(0x401000, 'fn_00001000')],
            {0x401000: aliases['fn_00001000'], 0x401001: aliases['fn_00001000']}, [])
        self.assertIn(step_symbol('fn_00001000_manual'), assembly)
        self.assertEqual(assembly.count(step_symbol('fn_00001000_manual')), 2)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'runtime.hpp').write_text(RUNTIME)
            (root / 'functions.hpp').write_text('#pragma once\n#include "runtime.hpp"\nnamespace recomp_generated {\n' +
                'sharp_retro::Exit fn_00001000_step(sharp_retro::State&,sharp_retro::Memory&,std::uint64_t&);\n' + declarations + '}\n')
            (root / 'guards.cpp').write_text(cpp)
            (root / 'test.cpp').write_text('''#include "functions.hpp"
namespace recomp_generated {
sharp_retro::Exit fn_00001000_step(sharp_retro::State& s,sharp_retro::Memory&,std::uint64_t&) { s.result=42; return sharp_retro::Exit::returned; }
}
int main() {
 sharp_retro::State s; sharp_retro::Memory m; std::uint64_t b=10; s.pc=0x401000;
 recomp_generated::fn_00001000_manual_step(s,m,b); if(s.result!=42) return 1;
 s.pc=0x401001; try { recomp_generated::fn_00001000_manual_step(s,m,b); } catch(const std::runtime_error&) { return 0; }
 return 2;
}
''')
            subprocess.run([shutil.which('clang++'), '-std=c++20', str(root / 'guards.cpp'), str(root / 'test.cpp'), '-o', str(root / 'control')], check=True, capture_output=True)
            subprocess.run([str(root / 'control')], check=True, capture_output=True)

    @unittest.skipUnless(PE32_CXX.exists() and shutil.which('ninja'), 'requires local LLVM-MinGW and Ninja')
    def test_constructed_two_module_pe32_build_consumes_export_and_retains_baseline_identity(self):
        from tools.recomp_bulk_build import compile_inventory
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            compilation = fixture(root, PE32_CXX)
            work = root / 'work'
            w.initialize(compilation, work)
            packet = w.checkout(work, 'main', 4096)
            draft = root / 'draft.cpp'
            draft.write_text(packet['source'].replace('int value = 3;', 'int value = 42;'))
            proposal = w.plan(work, 'main', 4096, dict(view_sha256=packet['view_sha256'],
                replacement_file=str(draft), supported_rvas=[4096]))
            w.apply(work, Path(proposal['plan_file']))
            extra = work / 'include/nested/extra.hpp'
            extra.parent.mkdir(parents=True)
            extra.write_text('#pragma once\nstruct ExportedExtra {};\n')
            state = w.read(work)
            state['headers']['include/nested/extra.hpp'] = w.sha(extra)
            recomp.atomic_json(work / 'workbench.json', state)
            w.export(work, root / 'export')
            result = compile_inventory(root / 'bulk/runs/1', root / 'candidate', PE32_CXX, 2,
                root / 'export/manual-overrides.json')
            self.assertEqual(result['status'], 'compiled_all_generated_sources')
            self.assertEqual(len(result['observed_object_artifacts']), 2)
            inputs = recomp.load(Path(result['run_directory']) / 'inputs.json')
            overrides, baseline = w.compilation_overrides(inputs)
            self.assertEqual(len(overrides), 1)
            self.assertEqual(baseline, w.sha(compilation / 'inputs.json'))
            edited = next(r for r in inputs['functions'] if r['module'] == 'main')
            self.assertNotEqual(edited['generated_source_sha256'], edited['source_sha256'])
            self.assertIn('int value = 42;', (root / 'candidate/source/fn_00001000.cpp').read_text())
            self.assertEqual((root / 'candidate/source/nested/extra.hpp').read_text(), extra.read_text())

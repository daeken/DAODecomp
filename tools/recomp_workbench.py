"""Durable, function-scoped C++ recovery workbench (no model invocation).

Compiler checks establish buildability only. Names, types and rewritten bodies
remain hypotheses; this tool never promotes contracts or validation records.
"""
import argparse
import copy
from contextlib import contextmanager
import difflib
import gzip
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from urllib.parse import unquote, urlparse

from tools import recomp, recomp_bulk
from tools.recomp_clangd import Clangd, apply_text_edits, offset


def sha(path):
    return recomp.digest(Path(path).read_bytes())


def inside(root, relative):
    """Manifest paths are relative and must not escape through symlinks."""
    path = Path(relative)
    root = Path(root).resolve()
    if path.is_absolute() or '..' in path.parts or not path.parts:
        raise ValueError('invalid workspace-relative path')
    result = root / path
    if not result.resolve().is_relative_to(root):
        raise ValueError('workspace path escapes its root')
    return result


def put(root, data):
    identity = recomp.digest(data)
    path = root / 'blobs' / identity
    if path.exists():
        if sha(path) != identity:
            raise ValueError('immutable source blob changed')
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return identity


def blob(root, identity):
    if not re.fullmatch('[0-9a-f]{64}', identity):
        raise ValueError('invalid blob identity')
    data = (root / 'blobs' / identity).read_bytes()
    if recomp.digest(data) != identity:
        raise ValueError('immutable source blob changed')
    return data


def read(root):
    state = recomp.load(root / 'workbench.json')
    if state.get('schema_version') != 1:
        raise ValueError('unsupported workbench schema')
    if sha(root / 'baseline/inputs.json') != state['baseline_inputs_sha256']:
        raise ValueError('pinned compilation inputs changed')
    for name, identity in state['headers'].items():
        if sha(inside(root, name)) != identity:
            raise ValueError('shared header changed; coordinator must record a header plan')
    return state


def initialize(compilation, root):
    compilation, root = compilation.resolve(), root.resolve()
    if root.exists():
        raise ValueError('new workbench directory must not already exist')
    inputs = recomp.load(compilation / 'inputs.json')
    generation = Path(inputs['generation_run'])
    if sha(generation / 'report.json') != inputs['generation_report_sha256']:
        raise ValueError('generation report changed')
    report = recomp.load(generation / 'report.json')
    backend = generation.parent.parent / 'backends' / report['pipeline']
    header = (backend / 'CppRuntime.hpp').read_text().replace(
        '#include "IntegerRuntime.hpp"', (backend / 'IntegerRuntime.hpp').read_text()).encode()
    if recomp.digest(header) != inputs['runtime_sha256']:
        raise ValueError('runtime differs from pinned compilation')
    modules = {role: recomp.load(generation / role / 'context.json')
               for role in report['modules']}
    # Initialize in a sibling directory; a failed initialization publishes nothing.
    root.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.workbench-', dir=root.parent) as temporary:
        stage = Path(temporary)
        (stage / 'baseline').mkdir()
        (stage / 'baseline/inputs.json').write_bytes((compilation / 'inputs.json').read_bytes())
        (stage / 'include').mkdir()
        (stage / 'include/runtime.hpp').write_bytes(header)
        (stage / 'include/recovered_types.hpp').write_text(
            '#pragma once\n// Coordinator-owned guest layouts; pointer widths remain explicit.\n')
        for name in ('runtime.hpp', 'recovered_types.hpp'):
            put(stage, (stage / 'include' / name).read_bytes())
        state = dict(schema_version=1, baseline_compilation=str(compilation),
            baseline_inputs_sha256=sha(stage / 'baseline/inputs.json'),
            modules=modules, headers={f'include/{name}': sha(stage / 'include' / name)
                for name in ('runtime.hpp', 'recovered_types.hpp')}, functions={},
            behavioral_acceptance=False, game_acceptance=False)
        recomp.atomic_json(stage / 'workbench.json', state)
        os.rename(stage, root)
    return dict(workspace=str(root), catalog_functions=len(inputs['functions']),
                status='ready; no functions checked out or accepted')


def select(state, module, rva):
    matches = [row for row in state['functions'].values()
               if row['module'] == module and row['rva'] == rva]
    if len(matches) != 1:
        raise ValueError('function is not checked out (select module and RVA)')
    return matches[0]


def checkout(root, module, rva):
    with recomp.locked(root):
        state = read(root)
        inputs = recomp.load(root / 'baseline/inputs.json')
        rows = [r for r in inputs['functions'] if r['module'] == module and r['rva'] == rva]
        if len(rows) != 1:
            raise ValueError('function not present in pinned generated compilation')
        record = rows[0]
        if record['id'] in state['functions']:
            return packet(root, module, rva)
        context = state['modules'][module]
        cache = Path(inputs['generation_run']).parent.parent / 'cache'
        marker = recomp_bulk.load_shard(cache, record['artifact_key'], context['binary_sha256'], rva)
        if marker['files']['function.cpp'] != record['source_sha256']:
            raise ValueError('baseline source identity changed')
        source = (cache / record['artifact_key'] / 'function.cpp').read_bytes()
        metadata = (cache / record['artifact_key'] / 'function.json.gz').read_bytes()
        data = json.loads(gzip.decompress(metadata))
        symbol = Path(record['source_file']).stem
        if (Path(record['source_file']).name != record['source_file'] or
            not re.fullmatch(r'(?:m_[0-9a-f]{16}_)?fn_[0-9a-f]{8}', symbol) or
            data['name'] != symbol or data['rva'] != rva):
            raise ValueError('function identity/symbol mismatch')
        if source.count(b'#include "runtime.hpp"') != 1:
            raise ValueError('generated source runtime include contract changed')
        working = source.replace(b'#include "runtime.hpp"',
            b'#include "runtime.hpp"\n#include "recovered_types.hpp"', 1)
        source_path = 'functions/' + record['source_file']
        inside(root, source_path).parent.mkdir(exist_ok=True)
        if inside(root, source_path).exists():
            raise ValueError('unregistered working file already exists')
        row = dict(record, binary_sha256=context['binary_sha256'],
            binary_module=context['module'], symbol=symbol, source_path=source_path,
            baseline_source_blob=put(root, source), metadata_blob=put(root, metadata),
            committed_source_sha256=put(root, working), hypotheses=[], history=[],
            supported_rvas=sorted({i['rva'] for i in data['instructions']}))
        inside(root, source_path).write_bytes(working)
        state['functions'][row['id']] = row
        recomp.atomic_json(root / 'workbench.json', state)
    return packet(root, module, rva)


def clean_source(root, row):
    data = inside(root, row['source_path']).read_bytes()
    if recomp.digest(data) != row['committed_source_sha256']:
        raise ValueError('unrecorded source edits; submit them with plan --request replacement_file')
    return data


def view(state, row):
    return recomp.digest(recomp.encoded(dict(identity=row['id'],
        source_sha256=row['committed_source_sha256'], headers=state['headers'],
        revision=row.get('revision', 0), header_revision=state.get('header_revision', 0),
        supported_rvas=row['supported_rvas'])))


def packet(root, module, rva, max_bytes=None):
    state = read(root)
    row = select(state, module, rva)
    source = clean_source(root, row).decode()
    metadata = json.loads(gzip.decompress(blob(root, row['metadata_blob'])))
    from tools import recomp_types
    type_context = recomp_types.function_context(root, row['id'], state)
    result = dict(schema_version=1, identity=row['id'], binary_sha256=row['binary_sha256'],
        module=row['binary_module'], rva=rva, symbol=row['symbol'],
        view_sha256=view(state, row), source_sha256=row['committed_source_sha256'],
        owned_files=[row['source_path']], source=source,
        contract=dict(status='unreviewed generated ABI; source signature unknown',
            entry_abi='Exit(State&, Memory&, uint64_t); step uses uint64_t&',
            supported_rvas=row['supported_rvas'], observations=metadata.get('abi', {})),
        provenance=dict(compilation_inputs_sha256=state['baseline_inputs_sha256'],
            artifact_key=row['artifact_key'], baseline_source_sha256=row['source_sha256'],
            metadata_sha256=row['metadata_blob']),
        observations={key: metadata.get(key, []) for key in
            ('instructions', 'variables', 'structures', 'unrecovered_accesses', 'control_flow')},
        hypotheses=row['hypotheses'],
        shared_types=type_context,
        rules=['Submit a plan against this view; positions are 1-based UTF-16 columns.',
            'Only this C++ file is worker-owned. Shared types require a coordinator header plan.',
            'Keep the stable entry/step ABI. Rewrites must declare supported instruction RVAs.',
            'Guest pointers are not host pointers. Unknown calls cannot become successful stubs.',
            'Compiler success is not behavioral equivalence or game acceptance.'],
        behavioral_acceptance=False, game_acceptance=False)
    if max_bytes is not None and len(recomp.encoded(result)) > max_bytes:
        raise ValueError('packet exceeds byte budget; select a smaller function or raise --max-bytes')
    return result


@contextmanager
def staging(root, state, row=None, all_sources=False):
    with tempfile.TemporaryDirectory(prefix='dao-refactor-') as temporary:
        stage = Path(temporary)
        for name in state['headers']:
            target = inside(stage, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(inside(root, name).read_bytes())
        rows = list(state['functions'].values()) if all_sources else [row]
        commands = []
        for item in rows:
            target = inside(stage, item['source_path'])
            target.parent.mkdir(exist_ok=True)
            target.write_bytes(clean_source(root, item))
            commands.append(dict(directory=str(stage), file=str(target), arguments=[
                shutil.which('clang++') or 'clang++', '-std=c++20', '-fno-fast-math',
                '-ffp-contract=off', '-I' + str(stage / 'include'), '-c', str(target)]))
        yield stage, commands


def declarations(server, path, text):
    tokens = server.request('textDocument/semanticTokens/full',
        {'textDocument': {'uri': path.as_uri()}})
    legend = server.capabilities['semanticTokensProvider']['legend']
    line = column = 0
    result = []
    values = tokens['data']
    for i in range(0, len(values), 5):
        delta, start, length, kind, modifiers = values[i:i + 5]
        line += delta
        column = start if delta else column + start
        flags = [name for bit, name in enumerate(legend['tokenModifiers']) if modifiers & (1 << bit)]
        if not set(flags) & {'declaration', 'definition'}:
            continue
        a = offset(text, dict(line=line, character=column))
        b = offset(text, dict(line=line, character=column + length))
        result.append(dict(name=text[a:b], kind=legend['tokenTypes'][kind],
            line=line + 1, column=column + 1, modifiers=flags))
    return result


def symbols(root, module, rva):
    state = read(root)
    row = select(state, module, rva)
    with staging(root, state, row) as (stage, commands), Clangd(stage, commands) as server:
        path = inside(stage, row['source_path'])
        server.open(path)
        result = declarations(server, path, path.read_text())
    return dict(view_sha256=view(state, row), symbols=result)


def compile_check(root, state, stage, rows):
    inputs = recomp.load(root / 'baseline/inputs.json')
    compiler = Path(inputs['compiler'])
    if sha(compiler) != inputs['compiler_sha256']:
        raise ValueError('pinned Windows compiler changed')
    for name, identity in inputs.get('compiler_artifacts', {}).items():
        if sha(Path(name)) != identity:
            raise ValueError('pinned compiler dependency changed')
    compiler_target = subprocess.check_output([str(compiler), '--print-target-triple'], text=True, timeout=15).strip()
    if compiler_target != inputs['target']:
        raise ValueError('compiler target differs from pinned compilation')
    reports = []
    for row in rows:
        target = inside(stage, row['source_path'])
        # Compile a TU that also requires both exact dispatcher signatures.
        probe = stage / 'abi-check.cpp'
        probe.write_text('#include ' + json.dumps(str(target)) + '\n' +
            'using F=sharp_retro::Exit(*)(sharp_retro::State&,sharp_retro::Memory&,std::uint64_t);\n' +
            'using S=sharp_retro::Exit(*)(sharp_retro::State&,sharp_retro::Memory&,std::uint64_t&);\n' +
            f'F verify_entry=&recomp_generated::{row["symbol"]};\n' +
            f'S verify_step=&recomp_generated::{row["symbol"]}_step;\n')
        command = [str(compiler), '-std=c++20', '-DRECOMP_NATIVE_EXECUTION=1',
            '-fno-fast-math', '-ffp-contract=off', '-fsyntax-only', '-I' + str(stage / 'include'), str(probe)]
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, timeout=60)
        except subprocess.TimeoutExpired as error:
            raise ValueError('compiler check timed out; no changes applied') from error
        reports.append(dict(function=row['id'], command=command, exit_code=result.returncode,
                            diagnostics=result.stdout))
        if result.returncode:
            raise ValueError('compiler rejected candidate; no changes applied:\n' + result.stdout[-12000:])
    return dict(status='syntax and dispatcher ABI checked; behavior unvalidated', target=compiler_target,
        host=os.uname().sysname + '/' + os.uname().machine,
        compiler_sha256=inputs['compiler_sha256'], checks=reports,
        behavioral_acceptance=False, game_acceptance=False)


def semantic_renames(root, state, row, renames):
    metadata = json.loads(gzip.decompress(blob(root, row['metadata_blob'])))
    origins = {v['name']: v['origin'] for v in metadata.get('variables', [])}
    for hypothesis in row['hypotheses']:
        if hypothesis.get('origin') and hypothesis.get('new_name'):
            origins[hypothesis['new_name']] = hypothesis['origin']
    if any(h.get('kind') == 'body_replacement' for h in row['hypotheses']):
        origins = {}  # Source-name coincidence after a rewrite is not lineage.
    inputs = recomp.load(root / 'baseline/inputs.json')
    compiler = Path(inputs['compiler'])
    if sha(compiler) != inputs['compiler_sha256']:
        raise ValueError('pinned compiler changed before semantic indexing')
    for name, identity in inputs.get('compiler_artifacts', {}).items():
        if sha(Path(name)) != identity:
            raise ValueError('pinned compiler dependency changed before semantic indexing')
    with staging(root, state, row) as (stage, commands):
        path = inside(stage, row['source_path'])
        source = path.read_text()
        native_commands = []
        for command in commands:
            arguments = list(command['arguments'])
            arguments[0] = str(compiler)
            arguments[1:1] = ['--target=' + inputs['target'], '-DRECOMP_NATIVE_EXECUTION=1']
            native_commands.append(dict(command, arguments=arguments))
        edits, records = [], {}
        # A reference in an inactive preprocessor branch is invisible to an AST.
        # Merge independently resolved edits from portable and actual native
        # target profiles against the SAME source; never text-replace identifiers.
        profiles = [('portable', commands, []), ('pinned_native', native_commands, [compiler])]
        for profile, database, drivers in profiles:
            with Clangd(stage, database, query_drivers=drivers) as server:
                server.open(path)
                names = [s['name'] for s in declarations(server, path, source)]
                for index, rename in enumerate(renames):
                    line, column = rename['line'] - 1, rename['column'] - 1
                    if line < 0 or column < 0 or not re.fullmatch('[A-Za-z_][A-Za-z0-9_]*', rename['new_name']):
                        raise ValueError('invalid rename position/name')
                    try:
                        selection = server.at('textDocument/prepareRename', path, line, column)
                    except ValueError as error:
                        # Only a symbol absent from this configuration may be
                        # skipped. Transport/timeout/other refactor errors fail.
                        if 'no symbol' in str(error).lower():
                            continue
                        raise
                    if not selection:
                        continue
                    extent = selection.get('range', selection)
                    old = source[offset(source, extent['start']):offset(source, extent['end'])]
                    if old in (row['symbol'], row['symbol'] + '_step'):
                        raise ValueError('stable dispatcher symbols cannot be renamed; add a naming hypothesis')
                    info = server.at('textDocument/symbolInfo', path, line, column)
                    change = server.at('textDocument/rename', path, line, column, newName=rename['new_name'])
                    changed = dict(change.get('changes', {}))
                    for document in change.get('documentChanges', []):
                        if 'textDocument' not in document or 'edits' not in document:
                            raise ValueError('file operations are outside function scope')
                        changed.setdefault(document['textDocument']['uri'], []).extend(document['edits'])
                    if not changed or any(Path(unquote(urlparse(uri).path)).resolve() != path for uri in changed):
                        raise ValueError('rename escapes worker-owned function or has no edits')
                    for changes in changed.values():
                        edits.extend(changes)
                    record = dict(kind='semantic_rename', old_name=old, new_name=rename['new_name'],
                        origin=origins.get(old) if names.count(old) == 1 else None,
                        origin_resolution='unambiguous metadata name' if names.count(old) == 1 and old in origins else 'unknown/ambiguous; no origin inferred',
                        symbol_info=info, line=rename['line'], column=rename['column'],
                        based_on_source_sha256=row['committed_source_sha256'], status='hypothesis')
                    if index in records:
                        if records[index]['old_name'] != old or records[index]['origin'] != record['origin']:
                            raise ValueError('selected declaration identity differs between compiler profiles')
                        records[index]['compiler_profiles'].append(profile)
                    else:
                        records[index] = dict(record, compiler_profiles=[profile])
        if len(records) != len(renames):
            raise ValueError('selected position has no renameable symbol in supported profiles')
        return apply_text_edits(source, edits).encode(), list(records.values())


def supported_entries(root, row, values):
    published = {i['rva'] for i in json.loads(gzip.decompress(blob(root, row['metadata_blob'])))['instructions']}
    if (not isinstance(values, list) or not values or any(type(r) is not int for r in values)
        or not set(values) <= published or row['rva'] not in values):
        raise ValueError('supported_rvas must include entry and only original published instructions')
    return sorted(set(values))


def save_plan(root, state, row, request):
    if request.get('view_sha256') != view(state, row):
        raise ValueError('stale function view; refresh packet before planning')
    source = clean_source(root, row)
    kinds = sum(bool(request.get(k)) for k in ('renames', 'replacement_file'))
    if kinds > 1:
        raise ValueError('use separate plans for renames and body replacement')
    hypotheses = request.get('hypotheses', [])
    if not isinstance(hypotheses, list) or any(not isinstance(h, dict) for h in hypotheses):
        raise ValueError('hypotheses must be objects with evidence and explicit uncertainty')
    supported = row['supported_rvas']
    if request.get('renames'):
        candidate, records = semantic_renames(root, state, row, request['renames'])
        hypotheses = records + hypotheses
    elif request.get('replacement_file'):
        candidate = Path(request['replacement_file']).read_bytes()
        if 'supported_rvas' not in request:
            raise ValueError('body replacements must explicitly declare supported_rvas')
        supported = supported_entries(root, row, request['supported_rvas'])
        hypotheses = [dict(kind='body_replacement', status='unvalidated candidate',
            based_on_source_sha256=row['committed_source_sha256'])] + hypotheses
    else:
        candidate = source
    plan = dict(schema_version=1, identity=row['id'], view_sha256=view(state, row),
        baseline_inputs_sha256=state['baseline_inputs_sha256'], headers=state['headers'],
        before_sha256=row['committed_source_sha256'], after_sha256=put(root, candidate),
        supported_rvas=supported, hypotheses=hypotheses,
        diff=''.join(difflib.unified_diff(source.decode().splitlines(keepends=True),
            candidate.decode().splitlines(keepends=True), fromfile=row['source_path'], tofile=row['source_path'])),
        behavioral_acceptance=False, game_acceptance=False)
    identity = recomp.digest(recomp.encoded(plan))
    recomp.atomic_json(root / 'plans' / (identity + '.json'), plan)
    return dict(plan_sha256=identity, plan_file=str(root / 'plans' / (identity + '.json')), **plan)


def plan(root, module, rva, request):
    with recomp.locked(root):
        state = read(root)
        return save_plan(root, state, select(state, module, rva), request)


def cleanup_plan(root, module, rva, formatting=True):
    from tools import recomp_cleanup
    with recomp.locked(root):
        state = read(root)
        row = select(state, module, rva)
        recomp_cleanup.require_runtime((root / 'include/runtime.hpp').read_text())
        before = clean_source(root, row).decode()
        after, stats = recomp_cleanup.simplify(before)
        formatter = None
        if formatting:
            after, executable = recomp_cleanup.format_cpp(after)
            formatter = dict(executable=executable, sha256=sha(executable))
        if after == before:
            return dict(status='already clean', identity=row['id'], statistics=stats)
        stats['after_formatted_bytes'] = len(after.encode())
        with tempfile.TemporaryDirectory(prefix='dao-cleanup-') as temporary:
            draft = Path(temporary) / row['source_file']
            draft.write_text(after)
            return save_plan(root, state, row, dict(view_sha256=view(state, row),
                replacement_file=str(draft), supported_rvas=row['supported_rvas'],
                hypotheses=[dict(kind='expression_cleanup', statistics=stats, formatter=formatter,
                    status='candidate; compiler/equivalence checks remain separate',
                    rules='Unsigned mask composition, low64 literals, constant masks and argument parentheses. No lambda inlining, memory/call/exit/budget/signature changes.')]))


def apply(root, plan_path, check_only=False):
    with recomp.locked(root):
        state = read(root)
        proposal = recomp.load(plan_path)
        plan_sha = recomp.digest(recomp.encoded(proposal))
        if Path(plan_path).resolve() != (root / 'plans' / (plan_sha + '.json')).resolve():
            raise ValueError('plan is not an immutable workbench proposal')
        if proposal.get('kind') == 'shared_header':
            return apply_header(root, state, proposal, plan_sha, check_only)
        row = state['functions'][proposal['identity']]
        if (proposal['baseline_inputs_sha256'] != state['baseline_inputs_sha256'] or
            proposal['view_sha256'] != view(state, row) or proposal['headers'] != state['headers'] or
            proposal['before_sha256'] != row['committed_source_sha256']):
            raise ValueError('stale plan; no changes applied')
        candidate = blob(root, proposal['after_sha256'])
        supported_entries(root, row, proposal['supported_rvas'])
        with staging(root, state, row) as (stage, _):
            inside(stage, row['source_path']).write_bytes(candidate)
            report = compile_check(root, state, stage, [row])
        receipt = dict(plan_sha256=plan_sha, identity=row['id'], report=report,
                       before_sha256=row['committed_source_sha256'], after_sha256=proposal['after_sha256'])
        if check_only:
            return receipt
        # Source first, manifest last: an interrupted transaction is dirty and
        # fails closed. Both versions are retained in the immutable blob store.
        before = clean_source(root, row)
        target = inside(root, row['source_path'])
        temporary = target.with_suffix('.pending')
        temporary.write_bytes(candidate)
        os.replace(temporary, target)
        try:
            row['committed_source_sha256'] = proposal['after_sha256']
            row['supported_rvas'] = proposal['supported_rvas']
            row['hypotheses'].extend(proposal['hypotheses'])
            row['history'].append(receipt)
            row['revision'] = row.get('revision', 0) + 1
            recomp.atomic_json(root / 'workbench.json', state)
        except Exception:
            target.write_bytes(before)
            raise
        recomp.atomic_json(root / 'receipts' / (str(time.time_ns()) + '.json'), receipt)
        return dict(status='applied; behavior unvalidated', **receipt)


def header_plan(root, replacement, expected_sha):
    """Coordinator operation; worker packets never own this shared header."""
    with recomp.locked(root):
        state = read(root)
        name = 'include/recovered_types.hpp'
        if state['headers'][name] != expected_sha:
            raise ValueError('stale shared header')
        before = inside(root, name).read_bytes()
        after = replacement.read_bytes()
        proposal = dict(schema_version=1, kind='shared_header', path=name,
            baseline_inputs_sha256=state['baseline_inputs_sha256'], headers=state['headers'],
            header_revision=state.get('header_revision', 0),
            sources={r['id']: r['committed_source_sha256'] for r in state['functions'].values()},
            before_sha256=expected_sha, after_sha256=put(root, after),
            diff=''.join(difflib.unified_diff(before.decode().splitlines(keepends=True),
                after.decode().splitlines(keepends=True), fromfile=name, tofile=name)),
            behavioral_acceptance=False, game_acceptance=False)
        identity = recomp.digest(recomp.encoded(proposal))
        target = root / 'plans' / (identity + '.json')
        recomp.atomic_json(target, proposal)
        return dict(plan_sha256=identity, plan_file=str(target), **proposal)


def apply_header(root, state, proposal, plan_sha, check_only):
    name = 'include/recovered_types.hpp'
    sources = {r['id']: r['committed_source_sha256'] for r in state['functions'].values()}
    if (proposal['path'] != name or proposal['headers'] != state['headers'] or
        proposal['baseline_inputs_sha256'] != state['baseline_inputs_sha256'] or
        proposal['header_revision'] != state.get('header_revision', 0) or
        proposal['before_sha256'] != state['headers'][name] or proposal['sources'] != sources):
        raise ValueError('stale shared header plan')
    candidate = blob(root, proposal['after_sha256'])
    rows = list(state['functions'].values())
    if not rows:
        raise ValueError('check out functions before editing their shared header')
    with staging(root, state, all_sources=True) as (stage, _):
        inside(stage, name).write_bytes(candidate)
        report = compile_check(root, state, stage, rows)
    receipt = dict(plan_sha256=plan_sha, kind='shared_header', report=report,
                   before_sha256=proposal['before_sha256'], after_sha256=proposal['after_sha256'])
    if check_only:
        return receipt
    before = inside(root, name).read_bytes()
    inside(root, name).write_bytes(candidate)
    try:
        state['headers'][name] = proposal['after_sha256']
        state['header_revision'] = state.get('header_revision', 0) + 1
        state.setdefault('header_history', []).append(receipt)
        recomp.atomic_json(root / 'workbench.json', state)
    except Exception:
        inside(root, name).write_bytes(before)
        raise
    recomp.atomic_json(root / 'receipts' / (str(time.time_ns()) + '.json'), receipt)
    return dict(status='shared header applied; behavior unvalidated', **receipt)


def adopt(root, module, rva, request):
    """Capture editor changes as a plan; restore the last committed working file.

    The draft is retained as a blob even if planning/checking fails. Applying is
    deliberately the same explicit command as applying an agent proposal.
    """
    with recomp.locked(root):
        state = read(root)
        row = select(state, module, rva)
        if request.get('view_sha256') != view(state, row):
            raise ValueError('stale function view')
        supported_entries(root, row, request.get('supported_rvas'))
        path = inside(root, row['source_path'])
        draft = put(root, path.read_bytes())
        original = blob(root, row['committed_source_sha256'])
        request = dict(request, replacement_file=str(root / 'blobs' / draft))
        path.write_bytes(original)
        try:
            return save_plan(root, state, row, request)
        except Exception:
            path.write_bytes(blob(root, draft))
            raise


def export(root, output):
    with recomp.locked(root):
        state = read(root)
        if output.exists():
            raise ValueError('export requires a fresh output directory')
        rows = list(state['functions'].values())
        if not rows:
            raise ValueError('no checked-out functions to export')
        with staging(root, state, all_sources=True) as (stage, _):
            from tools import recomp_types
            type_db = recomp_types.load(root, state)
            registry_bytes = (root / recomp_types.REGISTRY).read_bytes() if (root / recomp_types.REGISTRY).exists() else recomp.encoded(type_db)
            (stage / recomp_types.REGISTRY).write_bytes(registry_bytes)
            report = compile_check(root, state, stage, rows)
            files = {recomp_types.REGISTRY: recomp.digest(registry_bytes)}
            for name in list(state['headers']) + [r['source_path'] for r in rows]:
                files[name] = sha(inside(stage, name))
            manifest = dict(schema_version=1, baseline_inputs_sha256=state['baseline_inputs_sha256'],
                baseline_compilation=state['baseline_compilation'], files=files,
                shared_types=dict(path=recomp_types.REGISTRY, sha256=files[recomp_types.REGISTRY],
                    revision=type_db['revision'], generated_header_sha256=type_db.get('generated_header_sha256')),
                functions=[dict(r) for r in rows], compiler_report=report,
                scope='Manual source candidates; syntax/ABI checked, behavior unvalidated.',
                behavioral_acceptance=False, game_acceptance=False)
            output.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix='.export-', dir=output.parent) as temporary:
                destination = Path(temporary)
                for name in files:
                    target = inside(destination, name)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(inside(stage, name).read_bytes())
                (destination / 'baseline-inputs.json').write_bytes((root / 'baseline/inputs.json').read_bytes())
                recomp.atomic_json(destination / 'manual-overrides.json', manifest)
                os.rename(destination, output)
        return dict(export=str(output / 'manual-overrides.json'), functions=len(rows),
                    behavioral_acceptance=False, game_acceptance=False)


def load_overrides(path, generation=None):
    """Authenticate an immutable export before staging candidate object builds."""
    path = Path(path).resolve()
    data = recomp.load(path)
    baseline = path.parent / 'baseline-inputs.json'
    if (data.get('schema_version') != 1 or data.get('behavioral_acceptance') is not False or
        data.get('game_acceptance') is not False or sha(baseline) != data['baseline_inputs_sha256']):
        raise ValueError('invalid manual export/baseline identity')
    inputs = recomp.load(baseline)
    if generation is not None and Path(inputs['generation_run']).resolve() != Path(generation).resolve():
        raise ValueError('manual export belongs to another generation')
    if sha(Path(inputs['generation_run']) / 'report.json') != inputs['generation_report_sha256']:
        raise ValueError('manual baseline generation changed')
    for name, identity in data['files'].items():
        if sha(inside(path.parent, name)) != identity:
            raise ValueError('manual export source/header changed')
    from tools import recomp_types
    type_meta = data.get('shared_types')
    legacy = (type_meta is None and recomp_types.REGISTRY not in data['files'] and
        recomp_types.HEADER not in data['files'])
    if not legacy:
        if (not isinstance(type_meta, dict) or type_meta.get('path') != recomp_types.REGISTRY or
            type_meta.get('sha256') != data['files'].get(recomp_types.REGISTRY)):
            raise ValueError('manual shared type registry binding missing')
        registry = recomp.load(inside(path.parent, recomp_types.REGISTRY))
        if (registry.get('schema_version') != 1 or
            registry.get('baseline_inputs_sha256') != data['baseline_inputs_sha256'] or
            registry.get('behavioral_acceptance') is not False or registry.get('game_acceptance') is not False or
            registry.get('revision') != type_meta.get('revision') or
            registry.get('generated_header_sha256') != type_meta.get('generated_header_sha256')):
            raise ValueError('manual shared type revision summary changed')
        generated_sha = registry.get('generated_header_sha256')
        if generated_sha is not None and data['files'].get(recomp_types.HEADER) != generated_sha:
            raise ValueError('manual generated type header hash differs from registry')
    if data['files'].get('include/runtime.hpp') != inputs['runtime_sha256']:
        raise ValueError('manual runtime differs from pinned generation')
    originals = {(r['module'], r['rva']): r for r in inputs['functions']}
    rows = {}
    for row in data['functions']:
        key = (row['module'], row['rva'])
        original = originals[key]
        if key in rows or any(row[k] != original[k] for k in
            ('id', 'artifact_key', 'source_file', 'source_sha256')):
            raise ValueError('manual function baseline changed or duplicated')
        if data['files'].get(row['source_path']) != row['committed_source_sha256']:
            raise ValueError('manual function source hash changed')
        context = recomp.load(Path(inputs['generation_run']) / row['module'] / 'context.json')
        if row['binary_sha256'] != context['binary_sha256'] or row['binary_module'] != context['module']:
            raise ValueError('manual binary identity changed')
        cache = Path(inputs['generation_run']).parent.parent / 'cache'
        marker = recomp_bulk.load_shard(cache, row['artifact_key'], context['binary_sha256'], row['rva'])
        if (marker['files']['function.cpp'] != original['source_sha256'] or
            marker['files']['function.json.gz'] != row['metadata_blob']):
            raise ValueError('manual original source/metadata evidence changed')
        metadata = json.loads(gzip.decompress((cache / row['artifact_key'] / 'function.json.gz').read_bytes()))
        if metadata['name'] != row['symbol'] or Path(original['source_file']).stem != row['symbol']:
            raise ValueError('manual dispatcher symbol changed')
        published = {i['rva'] for i in metadata['instructions']}
        supported = row['supported_rvas']
        if (not isinstance(supported, list) or not supported or any(type(pc) is not int for pc in supported)
            or not set(supported) <= published or row['rva'] not in supported):
            raise ValueError('manual supported instruction entries changed')
        rows[key] = row
    return data, rows


def compilation_overrides(inputs):
    """Keep original decoding evidence separate from candidate source identity."""
    binding = inputs.get('manual_overrides')
    if binding is None:
        return {}, None
    path = Path(binding['manifest'])
    if sha(path) != binding['manifest_sha256']:
        raise ValueError('manual export manifest changed')
    data, overrides = load_overrides(path, Path(inputs['generation_run']))
    if binding['baseline_inputs_sha256'] != data['baseline_inputs_sha256']:
        raise ValueError('manual baseline input binding changed')
    baseline = recomp.load(path.parent / 'baseline-inputs.json')
    originals = {(r['module'], r['rva']): r for r in baseline['functions']}
    seen = set()
    for record in inputs['functions']:
        key = (record['module'], record['rva'])
        if key in seen or key not in originals:
            raise ValueError('candidate compilation inventory changed or duplicated')
        seen.add(key)
        original = originals[key]
        if any(record[k] != original[k] for k in ('id', 'artifact_key', 'source_file')):
            raise ValueError('candidate baseline identity changed')
        expected = overrides[key]['committed_source_sha256'] if key in overrides else original['source_sha256']
        if (record['source_sha256'] != expected or
            record.get('generated_source_sha256', original['source_sha256']) != original['source_sha256']):
            raise ValueError('candidate/generated source identity changed')
    if seen != set(originals) or not set(overrides) <= seen or inputs['runtime_sha256'] != baseline['runtime_sha256']:
        raise ValueError('candidate compilation dropped functions or changed runtime')
    return overrides, data['baseline_inputs_sha256']


def catalog(root, module=None, limit=20, max_instructions=None):
    state = read(root)
    inputs = recomp.load(root / 'baseline/inputs.json')
    rows = []
    for record in inputs['functions']:
        if module and record['module'] != module:
            continue
        count = record.get('inventory_coverage', {}).get('instruction_count')
        if max_instructions is not None and (count is None or count > max_instructions):
            continue
        rows.append(dict(identity=record['id'], module=record['module'], rva=record['rva'],
            instructions=count, checked_out=record['id'] in state['functions']))
    rows.sort(key=lambda r: (r['instructions'] is None, r['instructions'] or 0, r['module'], r['rva']))
    return dict(matches=len(rows), functions=rows[:limit], scope='Generated bodies only; no completeness or acceptance claim.')


def rebase(root, compilation, output):
    """Carry handwritten candidates to a new generation as unapplied proposals.

    No textual merge or same-name origin rematching is guessed. Old workspaces
    stay intact; changed binary identities are refused before creating output.
    """
    with recomp.locked(root):
        old = read(root)
        sources = {r['id']: clean_source(root, r) for r in old['functions'].values()}
        inputs = recomp.load(compilation / 'inputs.json')
        generation = Path(inputs['generation_run'])
        for role, context in old['modules'].items():
            new = recomp.load(generation / role / 'context.json')
            if any(context[k] != new[k] for k in ('binary_sha256', 'module')):
                raise ValueError('rebase cannot change pinned binary/module identity')
        initialize(compilation, output)
        state = read(output)
        from tools import recomp_types
        old_types = recomp_types.load(root, old)
        for name, identity in old['headers'].items():
            if name == 'include/runtime.hpp':
                continue
            data = inside(root, name).read_bytes()
            target = inside(output, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            state['headers'][name] = put(output, data)
        new_types = copy.deepcopy(old_types)
        previous_baseline = old['baseline_inputs_sha256']
        pending = []
        for binding in old_types.get('pending_bindings', []):
            pending.append(dict(binding, status='requires review',
                old_baseline_inputs_sha256=binding.get('old_baseline_inputs_sha256', previous_baseline)))
        for binding in old_types.get('bindings', []):
            pending.append(dict(binding, status='requires review', old_baseline_inputs_sha256=previous_baseline))
        new_types.update(baseline_inputs_sha256=state['baseline_inputs_sha256'], bindings=[],
            pending_bindings=pending)
        generated = output / recomp_types.HEADER
        if generated.exists():
            new_types['generated_header_sha256'] = sha(generated)
        else:
            new_types.pop('generated_header_sha256', None)
        recomp.atomic_json(output / recomp_types.REGISTRY, new_types)
        state['type_registry_sha256'] = sha(output / recomp_types.REGISTRY)
        state['rebased_from'] = dict(workspace=str(root), inputs_sha256=old['baseline_inputs_sha256'],
            status='carried header and candidate proposals; no behavioral acceptance')
        recomp.atomic_json(output / 'workbench.json', state)
        available = {r['id'] for r in inputs['functions']}
        results = []
        for row in old['functions'].values():
            draft = output / 'drafts' / row['source_file']
            draft.parent.mkdir(exist_ok=True)
            draft.write_bytes(sources[row['id']])
            if row['id'] not in available:
                results.append(dict(identity=row['id'], status='blocked; identity absent in new compilation', draft=str(draft)))
                continue
            current = checkout(output, row['module'], row['rva'])
            supported = sorted(set(row['supported_rvas']) & set(current['contract']['supported_rvas']))
            if row['rva'] not in supported:
                results.append(dict(identity=row['id'], status='blocked; original entry absent', draft=str(draft)))
                continue
            request = dict(view_sha256=current['view_sha256'], replacement_file=str(draft),
                supported_rvas=supported, hypotheses=row['hypotheses'] + [dict(kind='rebased_candidate',
                    status='requires review against new generation',
                    previous_compilation_inputs_sha256=old['baseline_inputs_sha256'],
                    previous_metadata_sha256=row['metadata_blob'],
                    dropped_supported_rvas=sorted(set(row['supported_rvas']) - set(supported)))])
            proposal = plan(output, row['module'], row['rva'], request)
            results.append(dict(identity=row['id'], status='proposal only; review/check/apply required',
                plan_file=proposal['plan_file'], original_baseline_changed=(
                    current['provenance']['baseline_source_sha256'] != row['source_sha256'])))
        report = dict(workspace=str(output), results=results,
            scope='Candidate sources preserved, not merged or accepted. Unsupported entries remain explicit.',
            behavioral_acceptance=False, game_acceptance=False)
        recomp.atomic_json(output / 'rebase-report.json', report)
        return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, default=recomp.ROOT / 'local/recovery/workbench')
    commands = parser.add_subparsers(dest='command', required=True)
    init = commands.add_parser('init')
    init.add_argument('--compilation', type=Path, required=True)
    listing = commands.add_parser('catalog')
    listing.add_argument('--module', choices=('main', 'umbra'))
    listing.add_argument('--limit', type=int, default=20)
    listing.add_argument('--max-instructions', type=int)
    regenerate = commands.add_parser('rebase')
    regenerate.add_argument('--compilation', type=Path, required=True)
    regenerate.add_argument('--output', type=Path, required=True)
    for name in ('checkout', 'packet', 'symbols', 'plan', 'adopt', 'cleanup'):
        command = commands.add_parser(name)
        command.add_argument('--module', choices=('main', 'umbra'), required=True)
        command.add_argument('--rva', type=lambda x: int(x, 0), required=True)
        if name == 'packet':
            command.add_argument('--max-bytes', type=int, default=128 * 1024)
            command.add_argument('--output', type=Path)
        if name in ('plan', 'adopt'):
            command.add_argument('--request', type=Path, required=True)
        if name == 'cleanup':
            command.add_argument('--no-format', action='store_true')
    header = commands.add_parser('header-plan', help='coordinator-owned shared type edits')
    header.add_argument('--replacement', type=Path, required=True)
    header.add_argument('--expected-sha', required=True)
    for name in ('check', 'apply'):
        commands.add_parser(name).add_argument('--plan', type=Path, required=True)
    commands.add_parser('export').add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    root = args.workspace.resolve()
    try:
        if args.command == 'init':
            result = initialize(args.compilation, root)
        elif args.command == 'catalog':
            if not 1 <= args.limit <= 1000:
                raise ValueError('catalog limit must be 1..1000')
            result = catalog(root, args.module, args.limit, args.max_instructions)
        elif args.command == 'rebase':
            result = rebase(root, args.compilation.resolve(), args.output.resolve())
        elif args.command == 'checkout':
            result = checkout(root, args.module, args.rva)
        elif args.command == 'packet':
            result = packet(root, args.module, args.rva, args.max_bytes)
            if args.output:
                recomp.atomic_json(args.output, result)
                result = dict(packet=str(args.output), view_sha256=result['view_sha256'])
        elif args.command == 'symbols':
            result = symbols(root, args.module, args.rva)
        elif args.command == 'plan':
            result = plan(root, args.module, args.rva, recomp.load(args.request))
        elif args.command == 'cleanup':
            result = cleanup_plan(root, args.module, args.rva, not args.no_format)
        elif args.command == 'adopt':
            result = adopt(root, args.module, args.rva, recomp.load(args.request))
        elif args.command == 'header-plan':
            result = header_plan(root, args.replacement, args.expected_sha)
        elif args.command in ('check', 'apply'):
            result = apply(root, args.plan, args.command == 'check')
        else:
            result = export(root, args.output.resolve())
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as error:
        parser.exit(2, str(error) + '\n')


if __name__ == '__main__':
    raise SystemExit(main())

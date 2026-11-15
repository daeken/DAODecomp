"""Reviewed shared guest layouts and explicit function/object bindings.

Types are hypotheses, not behavioral acceptance. Guest views use the existing
Memory interface; no guessed native layout, host-pointer cast or source ABI.
"""
import argparse
import copy
import json
from pathlib import Path
import re
import time

from tools import recomp, recomp_workbench as w
from tools.recomp_cleanup import Expressions, tokens

HEADER = 'include/program_types.hpp'
REGISTRY = 'types.json'
KEYWORDS = set('class struct union enum template typename auto bool char short int long float double void public private protected virtual static const volatile return new delete operator this sizeof alignof alignas namespace using typedef signed unsigned if else for while switch case default try catch throw concept requires co_await co_return co_yield'.split())
KEYWORDS.update('and and_eq asm bitand bitor break char8_t char16_t char32_t compl consteval constexpr constinit const_cast continue decltype do dynamic_cast explicit export extern false friend goto inline mutable noexcept not not_eq nullptr or or_eq register reinterpret_cast static_assert static_cast thread_local true typeid wchar_t xor xor_eq'.split())
SCALARS = {'u8': (8, 'std::uint8_t'), 'u16': (16, 'std::uint16_t'),
           'u32': (32, 'std::uint32_t'), 'u64': (64, 'std::uint64_t'),
           'i8': (8, 'std::int8_t'), 'i16': (16, 'std::int16_t'),
           'i32': (32, 'std::int32_t'), 'i64': (64, 'std::int64_t'),
           'f32': (32, 'float'), 'f64': (64, 'double'), 'ptr32': (32, None)}


def ident(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,95}', value) or value in KEYWORDS or '__' in value:
        raise ValueError('invalid or reserved C++ identifier')
    return value


def key(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_.:-]{0,95}', value):
        raise ValueError('invalid stable type/field id')
    return value


def evidence(value):
    if not isinstance(value, list) or not value or any(not isinstance(v, dict) or not v.get('reason') for v in value):
        raise ValueError('evidence requires nonempty objects with a reason; uncertainty must be explicit')
    return value


def empty(state):
    return dict(schema_version=1, baseline_inputs_sha256=state['baseline_inputs_sha256'],
        revision=0, types={}, bindings=[], pending_bindings=[], history=[],
        behavioral_acceptance=False, game_acceptance=False)


def load(root, state=None):
    state = state or w.read(root)
    path = root / REGISTRY
    expected = state.get('type_registry_sha256')
    if expected is not None and (not path.exists() or w.sha(path) != expected):
        raise ValueError('shared type registry changed outside a coordinator transaction')
    if path.exists() and expected is None:
        raise ValueError('unregistered shared type registry; coordinator transaction required')
    result = recomp.load(path) if path.exists() else empty(state)
    if (result.get('schema_version') != 1 or result.get('baseline_inputs_sha256') != state['baseline_inputs_sha256'] or
        result.get('behavioral_acceptance') is not False or result.get('game_acceptance') is not False):
        raise ValueError('shared type registry identity/schema changed')
    header_sha = result.get('generated_header_sha256')
    if header_sha is not None and (state['headers'].get(HEADER) != header_sha or w.sha(root / HEADER) != header_sha):
        raise ValueError('shared type header/registry binding changed')
    return result


def validate_definitions(db):
    names = set()
    for type_id, item in db['types'].items():
        key(type_id)
        if item.get('id') != type_id or item.get('kind') not in ('struct', 'class'):
            raise ValueError('type id/kind mismatch')
        name = ident(item['name'])
        if name in ('guest_ptr32', 'unknown_guest_object'):
            raise ValueError('type name collides with shared view support')
        if name in names:
            raise ValueError('duplicate shared C++ type name')
        names.add(name)
        evidence(item.get('evidence'))
        if not isinstance(item.get('fields'), list):
            raise ValueError('type fields must be an explicit list')
        if item.get('status', 'hypothesis') != 'hypothesis':
            raise ValueError('type proposals cannot assert acceptance')
        fields, field_names = {}, set()
        for field in item.get('fields', []):
            fid, fname = key(field['id']), ident(field['name'])
            if fid in fields or fname in field_names:
                raise ValueError('duplicate field id/name')
            fields[fid] = field
            field_names.add(fname)
            if type(field.get('offset')) is not int or not -(2**31) <= field['offset'] < 2**31:
                raise ValueError('field offset must be a signed guest32 byte displacement')
            if field.get('type') not in SCALARS or field.get('width') != SCALARS[field['type']][0]:
                raise ValueError('field type/observed width mismatch')
            if field['type'] == 'ptr32' and field.get('target') not in db['types']:
                raise ValueError('pointer target type is absent')
            evidence(field.get('evidence'))
        size = item.get('size')
        if size is not None and (type(size) is not int or size <= 0 or size >= 2**32 or
            any(f['offset'] >= 0 and f['offset'] + f['width'] // 8 > size for f in fields.values())):
            raise ValueError('claimed size does not contain declared fields')
        base_ids = set()
        for base in item.get('bases', []):
            if base.get('type_id') not in db['types'] or type(base.get('offset')) is not int or not 0 <= base['offset'] < 2**32:
                raise ValueError('invalid explicit guest base-subobject relation')
            if base['type_id'] == type_id:
                raise ValueError('self inheritance is invalid')
            if base['type_id'] in base_ids:
                raise ValueError('duplicate base view needs a distinct explicit type')
            base_ids.add(base['type_id'])
            evidence(base.get('evidence'))
        method_names = set()
        for method in item.get('methods', []):
            name = ident(method['name'])
            if name in method_names:
                raise ValueError('duplicate method association name')
            method_names.add(name)
            if not method.get('function_id'):
                raise ValueError('method association needs a pinned function identity')
            evidence(method.get('evidence'))
    # Views for base subobjects are explicit; cyclic inheritance is never guessed.
    def visit(tid, path):
        if tid in path:
            raise ValueError('cyclic base-subobject relations')
        for base in db['types'][tid].get('bases', []):
            visit(base['type_id'], path | {tid})
    for tid in db['types']:
        visit(tid, set())


def function(root, identity):
    from tools import recomp_queries as q
    with q.open_index(root) as connection:
        row = connection.execute('SELECT module,rva FROM functions WHERE id=?', (identity,)).fetchone()
    if row is None:
        raise ValueError('unknown function identity')
    return q.get_function(root, row['module'], row['rva'])


def validate_bindings(root, db):
    seen = set()
    for binding in db['bindings']:
        pair = (binding['function_id'], binding['object_origin'])
        if pair in seen or binding.get('type_id') not in db['types']:
            raise ValueError('duplicate binding or missing type')
        seen.add(pair)
        evidence(binding.get('evidence'))
        data = function(root, binding['function_id'])
        structures = [s for s in data['metadata'].get('structures', []) if s['origin'] == binding['object_origin']]
        if len(structures) != 1:
            raise ValueError('object origin absent from authenticated function')
        observed = structures[0]
        fields = {f['origin']: f for f in observed['fields']}
        spec = db['types'][binding['type_id']]
        declared = {f['id']: f for f in spec['fields']}
        mapping = binding.get('field_map', {})
        if not mapping or set(mapping) != set(fields):
            raise ValueError('binding must account for every observed field exactly')
        for origin, fid in mapping.items():
            if fid not in declared or any(fields[origin][k] != declared[fid][k] for k in ('offset', 'width')):
                raise ValueError('bound field offset/width conflicts with observation')
        binding['observation_sha256'] = data['function']['metadata_sha256']
        binding['observed_structure'] = observed
        binding['status'] = 'hypothesis'
        if binding.get('lower', True):
            if any(f.get('pointer_targets') for f in observed['fields']):
                raise ValueError('nested follow-view lowering needs separate support; propose explicit lower=false binding')
            binding['view_name'] = ident(binding.get('view_name', 'view_' + observed['name']))
    for item in db['types'].values():
        for method in item.get('methods', []):
            function(root, method['function_id'])
        # RTTI/vtable labels stay hypotheses, but slot words are actual original bytes.
        for table in item.get('vtables', []):
            from tools import recomp_queries as q
            evidence(table.get('evidence'))
            if type(table.get('rva')) is not int or not 0 <= table['rva'] < 2**32:
                raise ValueError('invalid vtable RVA')
            indices = set()
            for slot in table.get('slots', []):
                if type(slot.get('index')) is not int or not 0 <= slot['index'] < 4096:
                    raise ValueError('invalid vtable slot index')
                if slot['index'] in indices:
                    raise ValueError('duplicate vtable slot')
                indices.add(slot['index'])
                raw = q.binary_query(root, 'bytes', table['module'], f"{table['rva'] + 4 * slot['index']:x}", size=4)
                # q's bytes response is checked by its tests; accept explicit hex field only.
                code = raw.get('hex', raw.get('bytes_hex'))
                if not isinstance(code, str):
                    raise ValueError('vtable evidence query lacks original bytes')
                address = int.from_bytes(bytes.fromhex(code), 'little')
                if slot.get('function_id'):
                    target = function(root, slot['function_id'])
                    state = w.read(root)
                    context = state['modules'][target['record']['module']]
                    project = recomp.load(Path(context['project']) / 'project.json')
                    if address != project['image_base'] + target['record']['rva']:
                        raise ValueError('vtable slot differs from associated function')
                elif slot.get('target') != address:
                    raise ValueError('unknown vtable slot needs its exact observed target')


def render(db):
    rows = ['#pragma once', '#include "runtime.hpp"', '#include <bit>',
        '// Shared guest views; class/layout relationships remain recovery hypotheses.',
        'namespace dao_recovered {',
        'template<class T> struct guest_ptr32 { std::uint32_t address; };',
        'struct unknown_guest_object;']
    for item in db['types'].values():
        rows.append(f'{item["kind"]} {item["name"]};')
    compatibility = {}
    for binding in db['bindings'] + db.get('pending_bindings', []):
        if not binding.get('lower', True) or not binding.get('observed_structure'):
            continue
        for field in binding['observed_structure']['fields']:
            fid = binding['field_map'][field['origin']]
            descriptor = (fid, field['width'], field.get('type', 'u' + str(field['width'])), field.get('read', False), field.get('write', False))
            ident(field['name'])
            table = compatibility.setdefault(binding['type_id'], {})
            old = table.get(field['name'])
            if old is not None and old[:3] != descriptor[:3]:
                raise ValueError('legacy field aliases conflict within shared type')
            table[field['name']] = descriptor if old is None else descriptor[:3] + (old[3] or descriptor[3], old[4] or descriptor[4])
    deferred_bases = []
    for tid, item in db['types'].items():
        rows += [f'{item["kind"]} {item["name"]} {{', 'public:',
            '    sharp_retro::Memory& memory;', '    std::uint32_t base;',
            '    // This is a view, not the host layout of the guest allocation.']
        fields = {f['id']: f for f in item['fields']}
        if {f['name'] for f in fields.values()} & set(compatibility.get(tid, {})):
            raise ValueError('semantic field names must differ from legacy field helper names')
        for field in fields.values():
            name, width, offset = field['name'], field['width'], field['offset'] & 0xffffffff
            unsigned = f'std::uint{width}_t'
            raw = f'static_cast<{unsigned}>(memory.load(std::uint32_t(base + 0x{offset:08x}u),{width}))'
            kind = field['type']
            typ = SCALARS[kind][1]
            if kind == 'ptr32':
                typ = 'guest_ptr32<' + db['types'][field['target']]['name'] + '>'
                value = typ + '{' + raw + '}'
                stored = 'value.address'
            elif kind.startswith(('i', 'f')):
                value, stored = f'std::bit_cast<{typ}>({raw})', f'std::bit_cast<{unsigned}>(value)'
            else:
                value, stored = raw, 'value'
            rows += [f'    {typ} read_{name}() const {{ return {value}; }}',
                f'    void write_{name}({typ} value) const {{ memory.store(std::uint32_t(base + 0x{offset:08x}u),{stored},{width}); }}']
        for legacy, (fid, width, old_type, read, write) in compatibility.get(tid, {}).items():
            field = fields[fid]
            offset = field['offset'] & 0xffffffff
            returned = 'sharp_retro::bits' if old_type == 'bits' else f'std::uint{width}_t'
            raw = f'memory.load(std::uint32_t(base + 0x{offset:08x}u),{width})'
            if old_type != 'bits':
                raw = f'static_cast<{returned}>({raw})'
            rows.append(f'    static constexpr std::uint32_t {legacy}_offset=0x{offset:08x}u;')
            if read:
                rows.append(f'    {returned} read_{legacy}() const {{ return {raw}; }}')
            if write:
                rows.append(f'    void write_{legacy}(sharp_retro::bits value) const {{ memory.store(std::uint32_t(base + 0x{offset:08x}u),value,{width}); }}')
        for base in item.get('bases', []):
            target = db['types'][base['type_id']]['name']
            rows.append(f'    {target} as_{target}() const;')
            deferred_bases.append(f'inline {target} {item["name"]}::as_{target}() const {{ return {target}{{memory,std::uint32_t(base+0x{base["offset"]:08x}u)}}; }}')
        rows.append('};')
    rows += deferred_bases + ['} // namespace dao_recovered', '']
    return '\n'.join(rows).encode()


def view_span(source, view_name):
    tree = Expressions(source)
    hits = []
    ts = tree.ts
    for i in range(len(ts) - 2):
        if ts[i].text == 'struct' and ts[i + 1].text == view_name and ts[i + 2].text == '{':
            end = tree.pairs[i + 2] + 1
            if end >= len(ts) or ts[end].text != ';':
                raise ValueError('unrecognized generated view terminator')
            hits.append((ts[i].start, ts[end].end))
    if len(hits) == 1:
        return hits[0]
    if hits:
        raise ValueError('view definition is ambiguous')
    return None


def significant(source):
    return [t.text for t in tokens(source) if not t.text.startswith(('//', '/*'))]


def replace_view(source, view_name, type_name, original, previous_alias=None):
    alias = f'using {view_name} = dao_recovered::{type_name};'
    span = view_span(source, view_name)
    if span is not None:
        frozen = view_span(original, view_name)
        if frozen is None or significant(source[slice(*span)]) != significant(original[slice(*frozen)]):
            raise ValueError('generated view was manually rewritten; refusing to discard its semantics')
        a, b = span
        return source[:a] + alias + source[b:]
    ts = [token for token in tokens(source) if not token.text.startswith(('//', '/*'))]
    matches = []
    for i in range(len(ts) - 6):
        if ([token.text for token in ts[i:i+5]] == ['using', view_name, '=', 'dao_recovered', '::'] and
            ts[i+6].text == ';' and not any(token.opaque for token in ts[i:i+7])):
            matches.append((ts[i].start, ts[i+6].end, ts[i+5].text))
    if len(matches) != 1:
        raise ValueError('bound generated view absent or manually rewritten; use lower=false for proposal only')
    a, b, target = matches[0]
    if previous_alias is None or target != previous_alias:
        raise ValueError('view alias lacks matching prior generated binding; refusing manual alias replacement')
    return source[:a] + alias + source[b:]


def new_row(root, state, identity):
    data = function(root, identity)
    record, metadata = data['record'], data['metadata']
    context = state['modules'][record['module']]
    symbol = metadata['name']
    if Path(record['source_file']).name != record['source_file'] or Path(record['source_file']).stem != symbol:
        raise ValueError('function filename/symbol changed')
    inputs = recomp.load(root / 'baseline/inputs.json')
    cache = Path(inputs['generation_run']).parent.parent / 'cache' / record['artifact_key']
    original = (cache / 'function.cpp').read_bytes()
    if recomp.digest(original) != record['source_sha256'] or original.count(b'#include "runtime.hpp"') != 1:
        raise ValueError('original generated function changed')
    working = original.replace(b'#include "runtime.hpp"', b'#include "runtime.hpp"\n#include "recovered_types.hpp"', 1)
    row = dict(record, binary_sha256=context['binary_sha256'], binary_module=context['module'], symbol=symbol,
        source_path='functions/' + record['source_file'], baseline_source_blob=w.put(root, original),
        metadata_blob=w.put(root, (cache / 'function.json.gz').read_bytes()),
        committed_source_sha256=w.put(root, working), hypotheses=[], history=[],
        supported_rvas=sorted({i['rva'] for i in metadata['instructions']}))
    return row, working


def propose(root, request):
    with recomp.locked(root):
        state = w.read(root)
        db = load(root, state)
        if request.get('expected_revision') != db['revision']:
            raise ValueError('stale shared type revision')
        after = copy.deepcopy(db)
        for item in request.get('types', []):
            tid = key(item['id'])
            after['types'][tid] = copy.deepcopy(dict(item, status='hypothesis'))
        for item in request.get('bindings', []):
            item = copy.deepcopy(item)
            matches = [b for b in after['bindings'] if (b['function_id'], b['object_origin']) == (item['function_id'], item['object_origin'])]
            if matches and matches[0]['type_id'] != item['type_id'] and not item.pop('replace', False):
                raise ValueError('object already bound to another type; explicit replace evidence required')
            after['bindings'] = [b for b in after['bindings'] if b not in matches] + [item]
        validate_definitions(after)
        validate_bindings(root, after)
        after['revision'] += 1
        header = render(after)
        after['generated_header_sha256'] = recomp.digest(header)
        manual = (root / 'include/recovered_types.hpp').read_bytes()
        if b'#include "program_types.hpp"' not in manual:
            manual += b'\n#include "program_types.hpp"\n'
        files = {HEADER: dict(before=state['headers'].get(HEADER), after=w.put(root, header)),
                 'include/recovered_types.hpp': dict(before=state['headers']['include/recovered_types.hpp'], after=w.put(root, manual))}
        rows, originals = {}, {}
        # All live bindings are regenerated so type renames propagate coherently.
        for binding in after['bindings']:
            if not binding.get('lower', True):
                continue
            identity = binding['function_id']
            if identity not in rows:
                if identity in state['functions']:
                    rows[identity] = copy.deepcopy(state['functions'][identity])
                    originals[identity] = w.clean_source(root, rows[identity])
                else:
                    rows[identity], originals[identity] = new_row(root, state, identity)
            row = rows[identity]
            path = row['source_path']
            current = w.blob(root, files[path]['after']) if path in files else originals[identity]
            original = w.blob(root, row['baseline_source_blob']).decode()
            prior = [b for b in db['bindings'] + db.get('pending_bindings', [])
                if (b['function_id'], b['object_origin']) == (identity, binding['object_origin']) and b.get('lower', True)]
            aliases = {db['types'][b['type_id']]['name'] for b in prior}
            previous_alias = next(iter(aliases)) if len(aliases) == 1 else None
            candidate = replace_view(current.decode(), binding['view_name'], after['types'][binding['type_id']]['name'], original, previous_alias).encode()
            files[path] = dict(before=row['committed_source_sha256'] if identity in state['functions'] else None,
                               after=w.put(root, candidate))
        plan = dict(schema_version=1, kind='shared_types', baseline_inputs_sha256=state['baseline_inputs_sha256'],
            before_registry_sha256=recomp.digest(recomp.encoded(db)), after_registry=after,
            headers=state['headers'], header_revision=state.get('header_revision', 0),
            sources={r['id']: r['committed_source_sha256'] for r in state['functions'].values()},
            files=files, rows=rows, behavioral_acceptance=False, game_acceptance=False,
            scope='Shared guest layout/view hypotheses. Compiler checking is not source-type or behavioral acceptance.')
        identity = recomp.digest(recomp.encoded(plan))
        path = root / 'type-plans' / (identity + '.json')
        recomp.atomic_json(path, plan)
        return dict(plan_file=str(path), plan_sha256=identity, types=len(after['types']),
                    bindings=len(after['bindings']), changed_sources=len(rows), revision=after['revision'])


def apply(root, plan_path, check_only=False):
    with recomp.locked(root):
        state = w.read(root)
        db = load(root, state)
        plan = recomp.load(plan_path)
        digest = recomp.digest(recomp.encoded(plan))
        if (Path(plan_path).resolve() != (root / 'type-plans' / (digest + '.json')).resolve() or
            plan['before_registry_sha256'] != recomp.digest(recomp.encoded(db)) or
            plan['baseline_inputs_sha256'] != state['baseline_inputs_sha256'] or
            plan['headers'] != state['headers'] or plan['header_revision'] != state.get('header_revision', 0) or
            plan['sources'] != {r['id']: r['committed_source_sha256'] for r in state['functions'].values()}):
            raise ValueError('stale or changed shared type plan')
        validate_definitions(plan['after_registry'])
        validate_bindings(root, plan['after_registry'])
        staged_rows = dict(state['functions'])
        staged_rows.update(plan['rows'])
        with w.staging(root, state, all_sources=True) as (stage, _):
            for name, versions in plan['files'].items():
                target = w.inside(stage, name)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(w.blob(root, versions['after']))
            checks = list(staged_rows.values())
            if not checks:
                # A declaration-only TU checks the header even before any checkout.
                probe = stage / 'type-header-probe.cpp'
                probe.write_text('#include "recovered_types.hpp"\nnamespace recomp_generated {\n'
                    'sharp_retro::Exit type_header_probe(sharp_retro::State&,sharp_retro::Memory&,std::uint64_t);\n'
                    'sharp_retro::Exit type_header_probe_step(sharp_retro::State&,sharp_retro::Memory&,std::uint64_t&);\n}\n')
                checks = [dict(id='shared-header-declaration-probe', source_path=probe.name, symbol='type_header_probe')]
            report = w.compile_check(root, state, stage, checks)
        receipt = dict(plan_sha256=digest, compiler_report=report, type_revision=plan['after_registry']['revision'],
                       behavioral_acceptance=False, game_acceptance=False)
        if check_only:
            return receipt
        # All checks before writes; manifest last. Interrupted commits fail closed.
        backups = {}
        old_registry = (root / REGISTRY).read_bytes() if (root / REGISTRY).exists() else None
        try:
            for name, versions in plan['files'].items():
                path = w.inside(root, name)
                backups[name] = path.read_bytes() if path.exists() else None
                if versions['before'] is None and path.exists():
                    raise ValueError('unregistered destination already exists')
                if versions['before'] is not None and recomp.digest(path.read_bytes()) != versions['before']:
                    raise ValueError('source/header changed during type check')
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(w.blob(root, versions['after']))
            after = plan['after_registry']
            after['history'].append(receipt)
            recomp.atomic_json(root / REGISTRY, after)
            state['type_registry_sha256'] = w.sha(root / REGISTRY)
            for name, versions in plan['files'].items():
                if name.startswith('include/'):
                    state['headers'][name] = versions['after']
            state['header_revision'] = state.get('header_revision', 0) + 1
            for identity, row in plan['rows'].items():
                row['committed_source_sha256'] = plan['files'][row['source_path']]['after']
                row['revision'] = row.get('revision', 0) + 1
                row['history'].append(receipt)
                row['hypotheses'].append(dict(kind='shared_type_binding', type_revision=after['revision'], status='hypothesis'))
                state['functions'][identity] = row
            recomp.atomic_json(root / 'workbench.json', state)
        except Exception:
            for name, data in backups.items():
                path = w.inside(root, name)
                if data is None:
                    path.unlink(missing_ok=True)
                else:
                    path.write_bytes(data)
            if old_registry is None:
                (root / REGISTRY).unlink(missing_ok=True)
            else:
                (root / REGISTRY).write_bytes(old_registry)
            raise
        recomp.atomic_json(root / 'type-receipts' / (str(time.time_ns()) + '.json'), receipt)
        return dict(status='shared type hypotheses applied and compiler checked', **receipt)


def query(root, kind, type_id=None, function_id=None):
    db = load(root)
    if kind == 'list':
        return dict(revision=db['revision'], types=list(db['types'].values()), bindings=len(db['bindings']))
    if type_id is not None and type_id not in db['types']:
        raise ValueError('unknown shared type')
    if kind == 'show':
        return dict(revision=db['revision'], type=db['types'][type_id],
            bindings=[b for b in db['bindings'] if b['type_id'] == type_id],
            pending_bindings=[b for b in db.get('pending_bindings', []) if b['type_id'] == type_id])
    if kind == 'uses':
        rows = [b for b in db['bindings'] if (type_id is None or b['type_id'] == type_id) and
                (function_id is None or b['function_id'] == function_id)]
        return dict(revision=db['revision'], uses=rows, scope='Explicit reviewed hypothesis bindings; matching offsets are not class identity.')
    if kind == 'methods':
        return dict(revision=db['revision'], methods=db['types'][type_id].get('methods', []))
    raise ValueError('unknown type query')


def function_context(root, identity, state=None):
    db = load(root, state)
    active = [b for b in db['bindings'] if b['function_id'] == identity]
    pending = [b for b in db.get('pending_bindings', []) if b['function_id'] == identity]
    methods = [dict(type_id=tid, **method) for tid, spec in db['types'].items()
        for method in spec.get('methods', []) if method['function_id'] == identity]
    ids = sorted({b['type_id'] for b in active + pending} | {m['type_id'] for m in methods})
    return dict(revision=db['revision'], type_ids=sorted(db['types']),
        bound_types=[db['types'][tid] for tid in ids],
        bindings=active, method_associations=methods, pending_bindings=len(pending))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, default=recomp.ROOT / 'local/recovery/workbench')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('list')
    for name in ('show', 'methods'):
        sub.add_parser(name).add_argument('--type', required=True)
    uses = sub.add_parser('uses')
    uses.add_argument('--type')
    uses.add_argument('--function')
    sub.add_parser('propose').add_argument('--request', type=Path, required=True)
    for name in ('check', 'apply'):
        sub.add_parser(name).add_argument('--plan', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'propose':
            result = propose(args.workspace.resolve(), recomp.load(args.request))
        elif args.command in ('check', 'apply'):
            result = apply(args.workspace.resolve(), args.plan, args.command == 'check')
        else:
            result = query(args.workspace.resolve(), args.command, getattr(args, 'type', None), getattr(args, 'function', None))
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, OSError, KeyError) as error:
        parser.exit(2, str(error) + '\n')


if __name__ == '__main__':
    raise SystemExit(main())

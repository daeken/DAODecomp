"""Bound saved typed lifts. No lifting, compilation, source or acceptance decision."""
import hashlib
import json
from pathlib import Path
from rapid_object.compare import PE
from tools.replayable.range_lift import spans

SCHEMA = 'bound-typed-lift-v1'
LINEAR = 'sharpretro_instruction_lift_v1'
OWNED = 'sharpretro_owned_ranges_v1'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def context(request):
    p = request['project']; inputs = request['inputs']
    def bound(path):
        path = str(path); value = hashlib.sha256(Path(path).read_bytes()).hexdigest()
        need(inputs.get(path) == value, 'typed_cache_input_changed')
        return value
    cfgpath = Path(p['replayable']['lifter_config'])
    cfg = json.loads(cfgpath.read_text())
    def resolve(name):
        path = Path(cfg[name]); return path if path.is_absolute() else cfgpath.parent / path
    manifest_path = resolve('build_manifest'); manifest = json.loads(manifest_path.read_text())
    dll = resolve('adapter_dll'); checkout = resolve('sharp_retro_checkout')
    producer = {'config': bound(cfgpath), 'manifest': bound(manifest_path)}
    for path in sorted(dll.parent.iterdir()):
        if path.suffix in ('.dll', '.json'):producer['assembly/' + path.name] = bound(path)
    need({p.name: producer['assembly/' + p.name] for p in dll.parent.glob('*.dll')} == manifest['assemblies_sha256'], 'typed_cache_assembly_manifest')
    need({p.name: producer['assembly/' + p.name] for p in dll.parent.glob('*.json')} == manifest['runtime_files_sha256'], 'typed_cache_runtime_manifest')
    for name, expected in manifest['upstream_tracked_source_sha256'].items():
        producer['upstream/' + name] = bound(checkout / name)
        need(producer['upstream/' + name] == expected, 'typed_cache_upstream_manifest')
    # Bind the actual extraction bridge/range layer, but not the evolving C#
    # recovery/emission runtime. Replay binds that runtime separately.
    for suffix in ('replayable_adapter.py', 'tools/replayable/range_lift.py', 'tools/replayable/typed_cache.py'):
        matches = [name for name in inputs if name.replace('\\', '/').endswith('/' + suffix)]
        need(len(matches) == 1, 'typed_cache_producer_binding')
        producer[suffix] = bound(matches[0])
    original = Path(p['original']).read_bytes(); need(bound(p['original']) == p['module_sha256'], 'typed_cache_module_pin')
    inventory_hash = bound(p['inventory']); inventory = json.loads(Path(p['inventory']).read_text())
    need(inventory['module_sha256'] == p['module_sha256'], 'typed_cache_inventory_module')
    entries = [e for e in inventory['functions'] if e['rva'] == request['rva']]
    need(len(entries) == 1 and entries[0] == request['entry'], 'typed_cache_inventory_identity')
    ownership = spans(request['entry'], request['rva']); pe = PE(original)
    import struct
    peoff = struct.unpack_from('<I', original, 0x3c)[0]
    image_end = pe.image_base + struct.unpack_from('<I', original, peoff + 24 + 56)[0]
    binding = dict(module=p['module'], module_sha256=p['module_sha256'], rva=request['rva'],
                   ownership=[dict(start_rva=lo, end_rva_inclusive=hi, sha256=hashlib.sha256(pe.read(lo, hi-lo+1)).hexdigest()) for lo, hi in ownership],
                   inventory_sha256=inventory_hash, image_base=pe.image_base, image_end=image_end,
                   lifter_manifest_sha256=producer['manifest'], producer=producer)
    return binding, pe


def inspect_payload(binding, pe, payload):
    if 'error' in payload:
        return 'unknown' if payload.get('status') == 'external_outcome_unknown' else 'failed'
    need(payload['image_base'] == binding['image_base'] and payload['image_end'] == binding['image_end'], 'typed_cache_image_context')
    need(payload['lifter_manifest_sha256'] == binding['lifter_manifest_sha256'], 'typed_cache_payload_lifter')
    lift = payload['lift']; owned = binding['ownership']; base = binding['image_base']; schemas = []
    if len(owned) == 1:
        need(lift.get('schema') == LINEAR, 'typed_cache_lift_schema')
        parts = [lift]
    else:
        need(lift.get('schema') == OWNED and lift['mode'] == 'Bits32' and lift['entry_va'] == base + binding['rva'], 'typed_cache_owned_schema')
        need(len(lift['ranges']) == len(owned), 'typed_cache_owned_count')
        parts = []
        for row, span in zip(lift['ranges'], owned):
            need(row['start_va'] == base + span['start_rva'] and row['end_va_exclusive'] == base + span['end_rva_inclusive'] + 1 and row['slice_sha256'] == span['sha256'], 'typed_cache_owned_range')
            parts.append(row['lift'])
        need(lift['owned_bytes'] == sum(x['end_rva_inclusive'] - x['start_rva'] + 1 for x in owned), 'typed_cache_owned_size')
    complete = True
    for part, span in zip(parts, owned):
        lo, hi = span['start_rva'], span['end_rva_inclusive']; raw = pe.read(lo, hi-lo+1)
        need(part.get('schema') == LINEAR and part['mode'] == 'Bits32', 'typed_cache_lift_schema')
        need(part['id'] == binding['module_sha256'] + ':' + str(lo) and part['pc'] == base + lo and part['byte_length'] == len(raw), 'typed_cache_lift_identity')
        offset = 0
        for ins in part['instructions']:
            data = bytes.fromhex(ins['raw_hex'])
            need(ins['pc'] == base + lo + offset and ins['offset'] == offset and 1 <= ins['length'] <= 15 and len(data) == ins['length'], 'typed_cache_instruction_origin')
            need(data == raw[offset:offset+len(data)] and isinstance(ins['tree'], dict), 'typed_cache_instruction_payload')
            offset += len(data)
            complete &= not ins.get('opaque_markers') and ins.get('lift_error') is None
        need(offset == part['decoded_bytes'] and offset <= len(raw), 'typed_cache_decoded_coverage')
        complete &= part['decode_complete'] is True and offset == len(raw) and part['lift_errors'] == 0 and part['opaque_instructions'] == 0
    slice_hash = owned[0]['sha256'] if len(owned) == 1 else digest(owned)
    need(payload['binary_slice_sha256'] == slice_hash, 'typed_cache_slice_hash')
    return 'complete' if complete else 'incomplete'


def pack(request, payload):
    binding, pe = context(request)
    status = inspect_payload(binding, pe, payload)
    record = dict(schema=SCHEMA, binding=binding, payload=payload, payload_sha256=digest(payload), status=status, proof=False)
    record['record_id'] = digest(record)
    return record


def verify(request, record):
    need(record.get('schema') == SCHEMA, 'typed_cache_record_schema')
    need(record.get('record_id') == digest({k:v for k,v in record.items() if k != 'record_id'}), 'typed_cache_record_hash')
    need(record.get('payload_sha256') == digest(record['payload']), 'typed_cache_payload_hash')
    current, pe = context(request); old = record['binding']
    need(all(old[k] == current[k] for k in ('module', 'module_sha256', 'rva')), 'typed_cache_wrong_identity')
    if old['lifter_manifest_sha256'] != current['lifter_manifest_sha256']:
        return dict(status='legacy_lifter', current=False, proof=False)
    if old != current:
        return dict(status='stale_inputs_or_ranges', current=False, proof=False)
    status = inspect_payload(current, pe, record['payload'])
    need(status == record['status'], 'typed_cache_status_changed')
    return dict(status=status, current=True, payload=record['payload'] if status == 'complete' else None, proof=False)

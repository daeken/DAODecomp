"""Narrow binary/lifter and VC8/complete-comparator bridge. No source synthesis."""
import argparse
import fcntl
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(ok, why):
    if not ok:
        raise ValueError(why)


def resolved(config, name):
    p = Path(name)
    return p if p.is_absolute() else config.parent / p


def lift(request):
    project = request['project']
    config_path = Path(project['replayable']['lifter_config'])
    config = json.loads(config_path.read_text())
    manifest_path = resolved(config_path, config['build_manifest'])
    manifest = json.loads(manifest_path.read_text())
    dll = resolved(config_path, config['adapter_dll'])
    checkout = resolved(config_path, config['sharp_retro_checkout'])
    require(subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=checkout, text=True).strip() == manifest['revision'], 'lifter_revision_changed')
    for name, expected in manifest['upstream_tracked_source_sha256'].items():
        require(sha((checkout / name).read_bytes()) == expected, 'lifter_source_changed')
    require({p.name: sha(p.read_bytes()) for p in dll.parent.glob('*.dll')} == manifest['assemblies_sha256'], 'lifter_assemblies_changed')
    require({p.name: sha(p.read_bytes()) for p in dll.parent.glob('*.json')} == manifest['runtime_files_sha256'], 'lifter_runtime_changed')
    from rapid_object.compare import PE
    original = Path(project['original']).read_bytes()
    require(sha(original) == project['module_sha256'], 'original_pin_changed')
    pe = PE(original)
    entry = request['entry']
    ranges = entry['body_ranges']
    require(len(ranges) == 1 and ranges[0]['start_rva'] == request['rva'], 'discontiguous_or_nonentry_range_unsupported')
    raw = pe.read(request['rva'], ranges[0]['end_rva_inclusive'] - request['rva'] + 1)
    require(len(raw) == entry['body_bytes'], 'inventory_range_length_mismatch')
    payload = dict(hex=raw.hex(), pc=pe.image_base + request['rva'], id=project['module_sha256'] + ':' + str(request['rva']))
    run = subprocess.run([config.get('dotnet', 'dotnet'), str(dll)], input=json.dumps(payload) + '\n', capture_output=True, text=True, timeout=60)
    require(run.returncode == 0, 'lifter_process_failure')
    lifted = json.loads(run.stdout)
    require('adapter_error' not in lifted, 'lifter_adapter_error')
    # Independent decoder checks every instruction boundary; no guessed/dropped bytes.
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoded = list(md.disasm(raw, pe.image_base + request['rva']))
    require([(i.address, i.size, i.bytes.hex()) for i in decoded] == [(i['pc'], i['length'], i['raw_hex']) for i in lifted['instructions']] and sum(i.size for i in decoded) == len(raw), 'independent_decode_disagreement')
    # PE SizeOfImage, never a hardcoded game address bound.
    import struct
    peoff = struct.unpack_from('<I', original, 0x3c)[0]
    image_size = struct.unpack_from('<I', original, peoff + 24 + 56)[0]
    return dict(lift=lifted, image_base=pe.image_base, image_end=pe.image_base + image_size,
                binary_slice_sha256=sha(raw), lifter_manifest_sha256=sha(manifest_path.read_bytes()),
                scope='typed linear lifter output; ABI is a candidate hypothesis, not proven semantics')


def build(request, folder, source):
    from rapid_object.build import compile_object, symbol_bindings
    from rapid_object.compare import PE, compare_bytes
    from rapid_object.symbol_identity import source_identity
    from rapid_object.coff import Coff
    project = request['project']
    source_path = folder / 'candidate.cpp'
    require(source_path.read_text() == source, 'generated_source_changed')
    original = Path(project['original']).read_bytes()
    inventory = json.loads(Path(project['inventory']).read_text())
    require(sha(original) == project['module_sha256'] == inventory['module_sha256'], 'original_inventory_binding')
    build_folder = folder / 'build'
    lock_path = Path(project['replayable']['vm_build_lock'])
    # Registration chooses the existing shared VM lock, never a per-job substitute.
    require(lock_path.is_file(), 'shared_vm_lock_missing')
    with lock_path.open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        receipt = compile_object(source_path, build_folder)
    if not (build_folder / 'build-exit.txt').is_file():
        return dict(status='external_outcome_unknown', blocker='compiler_exit_marker_missing_no_automatic_retry', build=receipt, proof=False)
    compile_exit = int((build_folder / 'build-exit.txt').read_text(encoding='utf-8-sig').strip())
    if compile_exit != 0 or receipt['exit_code'] != 0 or not (build_folder / 'candidate.obj').is_file():
        return dict(status='inconclusive', blocker='compile_failure_with_retained_exit_marker', build=receipt, proof=False)
    require(receipt['compiler']['sha256'] == project['compiler_sha256'] == sha(Path(project['compiler']).read_bytes()), 'actual_compiler_mismatch')
    require(receipt['flags'] == project['compiler_flags'], 'selected_flags_mismatch')
    require(receipt['source_sha256'] == sha(source.encode()) == sha((build_folder / 'candidate.cpp').read_bytes()), 'compiled_source_mismatch')
    require(receipt['module_sha256'] == project['module_sha256'] and receipt['linked'] is False and receipt['original_executed'] is False, 'unsupported_build_receipt')
    require(json.loads((build_folder / 'compiler.json').read_text(encoding='utf-8-sig')) == receipt['compiler'], 'compiler_receipt_changed')
    pe = PE(original)
    entry = request['entry']
    requested = {request['rva']: dict(ranges=entry['body_ranges'], original_va=pe.image_base + request['rva'])}
    registry = {}
    entries = {f['rva'] for f in inventory['functions']}
    obj = (build_folder / 'candidate.obj').read_bytes()
    require(sha(obj) == receipt['object_sha256'], 'compiled_object_changed')
    for symbol in Coff(obj).symbols.values():
        identity = source_identity(symbol.name)
        if identity:
            kind, rva = identity
            require(kind != 'fn' or rva in entries, 'callee_not_in_inventory')
            registry[f'{kind}_{rva:08x}'] = pe.image_base + rva
    bindings = symbol_bindings(build_folder / 'candidate.obj', requested, registry)
    report = compare_bytes(original, obj, requested, bindings, sha(source.encode()), receipt['compiler'], project['module_sha256'])
    (folder / 'comparison.json').write_text(json.dumps(report, sort_keys=True))
    rows = report.get('functions', [])
    status = ('full_match' if not report.get('error') and len(rows) == 1 and rows[0]['rva'] == request['rva'] and rows[0]['status'] == 'exact_object_match' else
              'mismatch' if len(rows) == 1 and rows[0]['status'] == 'nonmatch' else 'inconclusive')
    return dict(status=status, functions=[{k: r[k] for k in ('rva', 'status', 'original_size', 'object_size', 'all_bytes_accounted', 'blockers') if k in r} for r in rows],
                source_sha256=sha(source.encode()), object_sha256=sha(obj), comparison_sha256=sha((folder / 'comparison.json').read_bytes()), build=receipt, proof=False,
                publication='draft_only_pending_independent_machinery_review', provider_calls=0,
                scope='fresh VC8 x86 object and pinned complete original function range; no game execution')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--adapter-root', required=True)
    args = parser.parse_args()
    sys.path.insert(0, args.adapter_root)
    data = json.load(sys.stdin)
    request = data['request']
    try:
        for name, expected in request['inputs'].items():
            require(sha(Path(name).read_bytes()) == expected, 'pipeline_input_changed')
        result = lift(request) if data['action'] == 'lift' else build(request, Path(data['folder']), data['source'])
        for name, expected in request['inputs'].items():
            require(sha(Path(name).read_bytes()) == expected, 'pipeline_input_changed_during_operation')
    except Exception as exc:
        unknown = data['action'] == 'build' and not (Path(data['folder']) / 'build/build-exit.txt').is_file()
        result = dict(status='external_outcome_unknown' if unknown else 'inconclusive', error=type(exc).__name__ + ':' + str(exc), proof=False)
    print(json.dumps(result))


if __name__ == '__main__':
    main()

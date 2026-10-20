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


def direct_call_targets(caller):
    """Original encoding, not propagated register values, selects dependencies."""
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True
    targets = set()
    for row in caller['lift']['instructions']:
        decoded = list(md.disasm(bytes.fromhex(row['raw_hex']), row['pc']))
        require(len(decoded) == 1 and decoded[0].size == row['length'], 'callee_decode_disagreement')
        ins = decoded[0]
        if ins.group(capstone.CS_GRP_CALL):
            require(len(ins.operands) == 1 and ins.operands[0].type == capstone.x86.X86_OP_IMM, 'indirect_caller_call_unsupported')
            targets.add(ins.operands[0].imm)
    return sorted(targets)


def select_callee_entries(request, caller, inventory):
    require(inventory['module_sha256'] == request['project']['module_sha256'], 'callee_inventory_pin_changed')
    entries = {}
    for entry in inventory['functions']:
        require(entry['rva'] not in entries, 'duplicate_inventory_rva')
        entries[entry['rva']] = entry
    selected = []
    for target in direct_call_targets(caller):
        rva = target - caller['image_base']
        require(rva in entries, 'direct_callee_not_in_inventory')
        selected.append((target, entries[rva]))
    return selected


def pure_forwarding_target(derived):
    """Only a complete one-instruction direct near JMP with no typed effects."""
    lifted=derived['lift']
    require(lifted['mode']=='Bits32' and lifted['decode_complete'] and lifted['lift_errors']==0 and lifted['opaque_instructions']==0,'incomplete_forwarding_evidence')
    rows=lifted['instructions']
    if len(rows)!=1:return None
    row=rows[0];body=row['tree'].get('Body',[])
    if len(body)!=1 or body[0].get('type')!='LiftIl.IlBranch' or body[0]['Kind']['name']!='Jmp':return None
    branch=body[0]
    require(branch['Cond'] is None and branch['Target'].get('type')=='LiftIl.IlConst','non_direct_forwarding_thunk')
    import capstone
    md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);md.detail=True;decoded=list(md.disasm(bytes.fromhex(row['raw_hex']),row['pc']))
    require(len(decoded)==1 and decoded[0].mnemonic=='jmp' and len(decoded[0].operands)==1 and decoded[0].operands[0].type==capstone.x86.X86_OP_IMM,'non_direct_forwarding_encoding')
    raw=bytes.fromhex(row['raw_hex']);require((len(raw)==2 and raw[0]==0xeb) or (len(raw)==5 and raw[0]==0xe9),'prefixed_or_far_forwarding_encoding')
    target=int(branch['Target']['Bits']['decimal']);require(target==decoded[0].operands[0].imm,'forwarding_encoding_target_disagrees');return target


def lift_callees(request):
    # Every dependency is original-derived. Full module/inventory/lifter closure
    # are durable request inputs; exact slice and entry evidence are retained too.
    caller=lift(request);inventory=json.loads(Path(request['project']['inventory']).read_text())
    selected=select_callee_entries(request,caller,inventory);entries={e['rva']:e for e in inventory['functions']}
    follow=request.get('recipe',{}).get('compiler_profile')=='vc8-x86-flat32-conditional-calls-v1'
    dependencies={};chains=[]
    for original_target,initial in selected:
        target=original_target;entry=initial;seen=set();chain=[]
        for depth in range(9):
            require(target not in seen,'forwarding_cycle');seen.add(target);chain.append(target)
            if target not in dependencies:
                derived=lift(dict(request,rva=entry['rva'],entry=entry))
                require(derived['image_base']==caller['image_base'] and derived['image_end']==caller['image_end'],'callee_module_boundary_changed')
                dependencies[target]=dict(target=target,rva=entry['rva'],entry=entry,binary_slice_sha256=derived['binary_slice_sha256'],lifter_manifest_sha256=derived['lifter_manifest_sha256'],lift=derived['lift'])
            next_target=pure_forwarding_target(dependencies[target]) if follow else None
            if next_target is None:break
            require(depth<8,'forwarding_depth_exhausted');rva=next_target-caller['image_base'];require(rva in entries,'forwarding_target_not_inventory_entry');target=next_target;entry=entries[rva]
        chains.append(dict(original_target=original_target,chain=chain))
    return dict(caller_slice_sha256=caller['binary_slice_sha256'],callees=list(dependencies.values()),forwarding_chains=chains,
                scope='original-derived normal-return ABI evidence; nested callee effects and termination remain unknown',proof=False)


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
        require(data['action'] in ('lift', 'lift_callees', 'build'), 'unsupported_pipeline_action')
        result = lift(request) if data['action'] == 'lift' else lift_callees(request) if data['action'] == 'lift_callees' else build(request, Path(data['folder']), data['source'])
        for name, expected in request['inputs'].items():
            require(sha(Path(name).read_bytes()) == expected, 'pipeline_input_changed_during_operation')
    except Exception as exc:
        unknown = data['action'] == 'build' and not (Path(data['folder']) / 'build/build-exit.txt').is_file()
        result = dict(status='external_outcome_unknown' if unknown else 'inconclusive', error=type(exc).__name__ + ':' + str(exc), proof=False)
    print(json.dumps(result))


if __name__ == '__main__':
    main()

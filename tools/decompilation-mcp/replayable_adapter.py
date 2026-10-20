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


def effectful_tail_dependency_target(derived):
    """Select a direct terminal edge only. C# must validate all prefix effects/ABI.

    This does not label the body a pure thunk or grant normal-return evidence.
    Complete source slices remain in the derived dependency closure.
    """
    lifted=derived['lift'];rows=lifted['instructions']
    if len(rows)<2:return None
    last=rows[-1];body=last['tree'].get('Body',[])
    if len(body)!=1 or body[0].get('type')!='LiftIl.IlBranch' or body[0]['Kind']['name']!='Jmp':return None
    return pure_forwarding_target(dict(derived,lift=dict(lifted,instructions=[last])))


def lift_callees(request):
    # Every dependency is original-derived. Full module/inventory/lifter closure
    # are durable request inputs; exact slice and entry evidence are retained too.
    caller=lift(request);inventory=json.loads(Path(request['project']['inventory']).read_text())
    selected=select_callee_entries(request,caller,inventory);entries={e['rva']:e for e in inventory['functions']}
    follow=request.get('recipe',{}).get('compiler_profile') in ('vc8-x86-flat32-conditional-calls-v1','vc8-x86-flat32-EH-two-exit-v1','vc8-x86-flat32-call-adapters-v1','vc8-x86-flat32-observed-byvalue-calls-v1','vc8-x86-flat32-ordered-counted-loops-v1','vc8-x86-flat32-ordered-memory-control-v1')
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
            if next_target is None and request.get('recipe',{}).get('compiler_profile') in ('vc8-x86-flat32-call-adapters-v1','vc8-x86-flat32-observed-byvalue-calls-v1','vc8-x86-flat32-ordered-counted-loops-v1','vc8-x86-flat32-ordered-memory-control-v1'):next_target=effectful_tail_dependency_target(dependencies[target])
            if next_target is None:break
            require(depth<8,'forwarding_depth_exhausted');rva=next_target-caller['image_base'];require(rva in entries,'forwarding_target_not_inventory_entry');target=next_target;entry=entries[rva]
        chains.append(dict(original_target=original_target,chain=chain))
    return dict(caller_slice_sha256=caller['binary_slice_sha256'],callees=list(dependencies.values()),forwarding_chains=chains,
                scope='original-derived normal-return ABI evidence; nested callee effects and termination remain unknown',proof=False)


def lift_eh(request):
    """Original-rooted supported EH dependencies, never source-authored placements."""
    from rapid_object import eh_graph as graph
    import struct
    caller=lift(request);original=Path(request['project']['original']).read_bytes();reader=graph.Original(original)
    rows=caller['lift']['instructions'];raw=bytes.fromhex(''.join(r['raw_hex'] for r in rows));main=rows[0]['pc']
    evidence=graph.original_graph(reader,main,raw)
    # LoadConfig fields are original PE metadata, not caller-provided symbols.
    peoff=struct.unpack_from('<I',original,0x3c)[0];opt=peoff+24
    load_rva,load_size=struct.unpack_from('<II',original,opt+96+10*8)
    require(load_rva and load_size>=64,'EH_missing_PE_load_config')
    declared=struct.unpack('<I',reader.read(reader.pe.image_base+load_rva,4))[0]
    require(declared>=72,'EH_missing_complete_declared_load_config')
    load=reader.read(reader.pe.image_base+load_rva,72)
    cookie,table,count=struct.unpack_from('<III',load,60)
    require(0<count<=65536,'EH_safe_handler_table_budget')
    handlers=struct.unpack('<'+'I'*count,reader.read(table,count*4))
    require(evidence['handler']['va']-reader.pe.image_base in handlers,'EH_handler_not_SAFESEH_registered')
    target=evidence['action']['external_target_va'];helper=reader.read(target,5,True)
    require(helper[0]==0xe9,'EH_cleanup_helper_not_pure_direct_forwarder')
    terminal=(target+5+struct.unpack_from('<i',helper,1)[0])&0xffffffff
    code=[]
    for role,node in [(k,evidence[k]) for k in ('handler','action')]+[('cleanup_forwarder',dict(va=target,size=5,bytes_hex=helper.hex()))]:
        rva=node['va']-reader.pe.image_base
        entry=dict(rva=rva,body_bytes=node['size'],body_ranges=[dict(start_rva=rva,end_rva_inclusive=rva+node['size']-1)])
        derived=lift(dict(request,rva=rva,entry=entry))
        code.append(dict(role=role,va=node['va'],size=node['size'],slice_sha256=derived['binary_slice_sha256'],lift=derived['lift'],boundary_basis='original operand-rooted complete supported terminal profile; not an inventory mutation'))
    return dict(caller_slice_sha256=caller['binary_slice_sha256'],image_base=caller['image_base'],image_end=caller['image_end'],graph=evidence,security_cookie_va=cookie,load_config_directory_size=load_size,load_config_declared_size=declared,safe_handler_table_sha256=sha(reader.read(table,count*4)),cleanup_forwarder_va=target,cleanup_terminal_va=terminal,code_dependencies=code,proof=False,scope='bounded original EH graph and actual typed dependencies; common handler, cookie check and cleanup effects remain unknown')


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
        if project['compiler_flags']==['/c','/O2','/Ob1','/Oy','/Gy','/Z7','/Zl','/GS','/GR-','/EHsc']:
            from tools.replayable.vc8_build import compile_object as compile_eh
            receipt=compile_eh(source_path,build_folder,project['compiler_flags'],json.loads(Path(project['replayable']['transport_config']).read_text()))
        else:
            receipt = compile_object(source_path, build_folder)
    return compare_built(request, folder, source, receipt)


def compare_built(request, folder, source, receipt=None):
    from rapid_object.build import symbol_bindings
    from rapid_object.compare import PE, compare_bytes
    from rapid_object.symbol_identity import source_identity
    from rapid_object.coff import Coff
    project=request['project'];build_folder=folder/'build'
    require((folder/'candidate.cpp').read_text()==source,'generated_source_changed')
    original=Path(project['original']).read_bytes();inventory=json.loads(Path(project['inventory']).read_text())
    require(sha(original)==project['module_sha256']==inventory['module_sha256'],'original_inventory_binding')
    if receipt is None:receipt=json.loads((build_folder/'run.json').read_text())
    if 'batch' in receipt:verify_batch_build(request,folder,receipt)
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
    # EH is a separate existing complete-graph backend. A main-only comparison
    # cannot grant credit when original FS registration or generated EH is present.
    from rapid_object import eh_native
    from rapid_object.symbol_identity import generated_identity
    import capstone
    md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);md.detail=True
    obj=(build_folder/'candidate.obj').read_bytes()
    original_rows=request['entry']['body_ranges'];original_body=PE(original).read(request['rva'],original_rows[0]['end_rva_inclusive']-request['rva']+1)
    needs_eh=any(generated_identity(sym.name) is not None for sym in Coff(obj).symbols.values()) or any(op.type==capstone.x86.X86_OP_MEM and op.mem.segment==capstone.x86.X86_REG_FS and op.mem.disp==0 for ins in md.disasm(original_body,PE(original).image_base+request['rva']) for op in ins.operands)
    if needs_eh:
        require(project.get('eh_policy') and project.get('libraries'),'EH_requires_registered_policy_and_libraries')
        report=eh_native.check(original,Path(project['inventory']).read_bytes(),Path(project['compiler']).read_bytes(),{n:Path(path).read_bytes() for n,path in project['libraries'].items()},source.encode(),obj,receipt,json.loads(Path(project['eh_policy']).read_text()))
        (folder/'comparison.json').write_text(json.dumps(report,sort_keys=True));rows=report.get('functions',[])
        status='full_match' if report['status']=='exact_eh_graph_match' and len(rows)==1 and rows[0]['rva']==request['rva'] else 'mismatch' if report['status']=='eh_graph_nonmatch' else 'inconclusive'
        return dict(status=status,backend=report['backend'],functions=[dict(rva=r['rva'],status=r['status'],original_size=r.get('nodes',{}).get('main',{}).get('original_size'),object_size=r.get('nodes',{}).get('main',{}).get('candidate_size'),blockers=r.get('blockers',[])) for r in rows],blockers=report.get('blockers',[]),source_sha256=sha(source.encode()),object_sha256=sha(obj),comparison_sha256=sha((folder/'comparison.json').read_bytes()),build=receipt,proof=False,scope='complete bounded main/EH compiled artifact graph; external runtime semantics unknown')
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
    result = dict(status=status, strict_status=status, match_kind="exact" if status=="full_match" else "none", functions=[{k: r[k] for k in ('rva', 'status', 'original_size', 'object_size', 'all_bytes_accounted', 'blockers') if k in r} for r in rows],
                source_sha256=sha(source.encode()), object_sha256=sha(obj), comparison_sha256=sha((folder / 'comparison.json').read_bytes()), build=receipt, proof=False,
                publication='draft_only_pending_independent_machinery_review', provider_calls=0,
                scope='fresh VC8 x86 object and pinned complete original function range; no game execution')
    if status=='mismatch' and request.get('recipe',{}).get('architecture')=='x86-bits32-composed-memory-encoding-equivalence-v1':
        try:
            from tools.replayable.encoding_check import certify_report
            certificate=certify_report(report,project,request['inputs'])
            proof_bytes=json.dumps(certificate,sort_keys=True,separators=(',',':')).encode()
            (folder/'encoding-equivalence.json').write_bytes(proof_bytes)
            result.update(status='encoding_equivalent',match_kind='encoding_equivalent',encoding_equivalence=certificate,encoding_equivalence_sha256=sha(proof_bytes))
        except (ValueError,KeyError,TypeError,OSError,subprocess.SubprocessError) as exc:
            result['encoding_refusal']=str(exc) if isinstance(exc,ValueError) else type(exc).__name__
    return result



def verify_encoding_cache(request,folder):
    # Fresh host-only validation. Never rewrite retained reports or launch cl.
    from tools.replayable.encoding_check import parse
    import adapter as retained_adapter
    require(request.get('recipe',{}).get('architecture')=='x86-bits32-composed-memory-encoding-equivalence-v1','encoding_cache_recipe')
    result=parse((folder/'result.json').read_bytes());retained=parse((folder/'retained-check-request.json').read_bytes())
    require(result['status'] in ('full_match','encoding_equivalent') and retained['project']==request['project'] and retained['build']['config']['rva']==request['rva'] and retained['build']['config'].get('allow_encoding_equivalence') is True,'encoding_cache_request_binding')
    if result['status']=='encoding_equivalent':
        raw=(folder/'encoding-equivalence.json').read_bytes()
        require(sha(raw)==result['encoding_equivalence_sha256'] and parse(raw)==result['encoding_equivalence'],'encoding_cache_certificate_binding')
    compact,report=retained_adapter.run(retained)
    require(compact['status']==result['status'] and (result['status']!='encoding_equivalent' or compact.get('encoding_equivalence')==result['encoding_equivalence']),'encoding_cache_fresh_certificate_disagreement')
    return dict(status=compact['status'],fresh_comparison=True,compilation_performed=False,proof=False)


def read_batch_dispatch_decision(path):
    # This is a bounded input document with up to16 complete request closures,
    # not a small compiler receipt. Keep receipt limits and strict JSON unchanged.
    from tools.replayable import guest_batch as transport
    require(path.is_file() and not path.is_symlink() and path.stat().st_size <= 16*1024*1024,
            'batch_dispatch_decision_missing_or_size_budget')
    return json.loads(path.read_text(encoding='utf-8-sig'),object_pairs_hook=transport.unique_object)


def batch_build(request, folder, members):
    """Transport only. Durable C# claims/decision and both comparison gates remain external."""
    import shutil
    from tools.replayable import guest_batch as transport
    from rapid_native.pipeline import vm
    project=request['project'];group=request['group_id']
    require(re.fullmatch('[0-9a-f]{32}',group) is not None and folder.name==group,'batch_group_identity')
    decision=read_batch_dispatch_decision(folder/'dispatch-decision.json')
    require(decision['group_id']==group and decision['members']==members,'batch_dispatch_decision_changed')
    require(1<=len(members)<=transport.MAX_ITEMS,'batch_size')
    profile=json.loads(Path(project['replayable']['transport_config']).read_text())
    profile['shared_vm_lock']=project['replayable']['vm_build_lock']
    for path in (Path(transport.__file__),Path(profile['vm_helper'])):
        require(request['inputs'].get(str(path))==sha(path.read_bytes()),'batch_helper_unbound')
    require(profile['vm_helper_sha256']==sha(Path(profile['vm_helper']).read_bytes()),'batch_vm_helper_changed')
    roots={m['job_id']:m for m in request['members']}
    require(len(roots)==len(request['members']),'batch_duplicate_root_identity')
    items=[]
    for member in members:
        child=member['request'];child_folder=Path(member['folder']);identity=child['job_id']
        require(re.fullmatch('[0-9a-f]{32}',identity) is not None and child_folder==Path(project['replayable']['output_root'])/identity,'batch_member_folder')
        require(child['group_parent']==group and child['project']==project and child['inputs']==request['inputs'] and child['recipe']==request['recipe'] and child['pipeline_key']==request['pipeline_key'],'batch_member_binding')
        root=roots.get(identity);require(root is not None and root['rva']==child['rva'] and root.get('expected_source_sha256')==child.get('expected_source_sha256') and root['function_id']==sha((project['module_sha256']+':'+str(child['rva'])).encode()),'batch_member_original_identity_changed')
        require(member['source_sha256']==sha((child_folder/'candidate.cpp').read_bytes()),'batch_member_source_changed')
        items.append(transport.Item('job-'+identity,child_folder/'candidate.cpp',member['source_sha256'],tuple(project['compiler_flags'])))
    lock_path=Path(profile['shared_vm_lock']);require(lock_path.is_file(),'shared_vm_lock_missing')
    with lock_path.open('r+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        for path,digest in request['inputs'].items():require(sha(Path(path).read_bytes())==digest,'batch_input_changed_before_dispatch')
        prepared=transport.prepare(items,folder/'batch',profile,project['compiler_sha256'])
        outcome=transport.execute(prepared,lock_fd=lock.fileno(),authorization=group,run_vm=vm,timeout=300)
        compiler=transport.read_json(prepared.output/'compiler.json');mapped=[]
        require([x['id'] for x in outcome['items']]==[x.id for x in items],'batch_member_order_changed')
        for member,item,result in zip(members,items,outcome['items']):
            child_folder=Path(member['folder']);build_folder=child_folder/'build';build_folder.mkdir(exist_ok=False)
            returned=Path(result['folder']);raw_exit=transport.read_json(returned/'exit.json')
            for name in ('candidate.cpp','candidate.obj','candidate.asm','build.log','start.json','exit.json'):
                if (returned/name).is_file():shutil.copy2(returned/name,build_folder/name)
            (build_folder/'compiler.json').write_text(json.dumps(compiler,sort_keys=True))
            # This compatibility marker comes only from an explicitly confirmed item exit.
            (build_folder/'build-exit.txt').write_text(str(result['exit_code'])+'\n')
            batch=dict(group_id=group,item_id=item.id,nonce=prepared.nonce,manifest_sha256=prepared.manifest_sha256,envelope_sha256=sha((prepared.output/'completed.json').read_bytes()),dispatch_sha256=sha((prepared.output/'dispatch-start.json').read_bytes()),item_exit_sha256=sha((returned/'exit.json').read_bytes()),transport_exit_code=outcome['transport_exit_code'])
            receipt=dict(schema_version=1,source_sha256=item.source_sha256,module_sha256=project['module_sha256'],object_sha256=raw_exit['object_sha256'],compiler=compiler,flags=list(item.flags),linked=False,original_executed=False,vm=prepared.vm_name,vm_workspace=prepared.guest+'\\'+item.id,elapsed_seconds=raw_exit['cl_seconds'],timing_scope='confirmed guest serial compiler time; batch dispatch measured separately',exit_code=result['exit_code'],batch=batch)
            (build_folder/'run.json').write_text(json.dumps(receipt,sort_keys=True));mapped.append(dict(job_id=member['request']['job_id'],receipt=receipt))
    return dict(status='batch_completed',members=mapped,host_dispatch_seconds=outcome['host_dispatch_seconds'],envelope_sha256=sha((prepared.output/'completed.json').read_bytes()),batch_manifest_sha256=prepared.manifest_sha256,proof=False)


def verify_batch_build(request,folder,receipt):
    from tools.replayable import guest_batch as transport
    b=receipt['batch'];group=request['group_parent'];identity=request['job_id'];project=request['project']
    require(re.fullmatch('[0-9a-f]{32}',group) is not None and group==b['group_id'] and b['item_id']=='job-'+identity,'batch_member_identity')
    output=Path(project['replayable']['output_root'])/group/'batch';m=transport.read_json(output/'manifest.json');profile=json.loads(Path(project['replayable']['transport_config']).read_text())
    require(sha((output/'manifest.json').read_bytes())==b['manifest_sha256'] and sha((output/'completed.json').read_bytes())==b['envelope_sha256'] and sha((output/'dispatch-start.json').read_bytes())==b['dispatch_sha256'],'batch_provenance_changed')
    start=transport.read_json(output/'dispatch-start.json');require(start['nonce']==b['nonce'] and start['authorization']==group,'batch_dispatch_binding')
    prepared=transport.PreparedBatch(output,Path(profile['host_transfer_root'])/('coff-batch-'+b['nonce']),b['manifest_sha256'],b['nonce'],m['guest'],m['shared'],m['vm_name'],Path(project['replayable']['vm_build_lock']))
    validated=transport.collect(prepared,b['transport_exit_code']);matched=[x for x in validated['items'] if x['id']==b['item_id']];require(len(matched)==1,'batch_member_missing')
    item=matched[0];raw=transport.read_json(Path(item['folder'])/'exit.json');build=folder/'build'
    require(sha((Path(item['folder'])/'exit.json').read_bytes())==b['item_exit_sha256'] and (Path(item['folder'])/'exit.json').read_bytes()==(build/'exit.json').read_bytes(),'batch_item_exit_changed')
    require(raw['source_sha256']==receipt['source_sha256']==sha((folder/'candidate.cpp').read_bytes()) and raw['flags']==receipt['flags']==project['compiler_flags'] and raw['compiler_sha256']==receipt['compiler']['sha256']==project['compiler_sha256'],'batch_build_binding')
    require(raw['exit_code']==receipt['exit_code'] and raw['object_sha256']==receipt['object_sha256'] and (build/'build-exit.txt').read_text().strip()==str(raw['exit_code']),'batch_build_exit_binding')
    require(receipt['compiler']==transport.read_json(output/'compiler.json') and receipt['elapsed_seconds']==raw['cl_seconds'] and receipt['vm']==m['vm_name'] and receipt['vm_workspace']==m['guest']+'\\'+b['item_id'],'batch_compiler_timing_workspace_binding')
    if item['object'] is not None:require(Path(item['object']).read_bytes()==(build/'candidate.obj').read_bytes(),'batch_build_object_changed')


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
        require(data['action'] in ('lift', 'lift_callees', 'lift_eh', 'build', 'build_batch', 'check_build', 'verify_encoding_cache'), 'unsupported_pipeline_action')
        result = batch_build(request,Path(data['folder']),data['members']) if data['action']=='build_batch' else verify_encoding_cache(request,Path(data['folder'])) if data['action']=='verify_encoding_cache' else compare_built(request,Path(data['folder']),data['source']) if data['action']=='check_build' else lift(request) if data['action'] == 'lift' else lift_callees(request) if data['action'] == 'lift_callees' else lift_eh(request) if data['action']=='lift_eh' else build(request, Path(data['folder']), data['source'])
        for name, expected in request['inputs'].items():
            require(sha(Path(name).read_bytes()) == expected, 'pipeline_input_changed_during_operation')
    except Exception as exc:
        unknown = (data['action']=='build_batch' and (Path(data['folder'])/'batch/dispatch-start.json').exists()) or (data['action'] == 'build' and not (Path(data['folder']) / 'build/build-exit.txt').is_file())
        result = dict(status='external_outcome_unknown' if unknown else 'inconclusive', error=type(exc).__name__ + ':' + str(exc), proof=False)
    print(json.dumps(result))


if __name__ == '__main__':
    main()

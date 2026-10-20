"""Whole-inventory applicability for the bounded conditional-call addition.

Every identity is accounted for. Necessary static checks do not move the durable
ascending frontier. Actual original typed effects and complete thunk dependencies
are passed to the reviewed frontend; generated hypotheses grant no match credit.
"""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
sha=lambda data:hashlib.sha256(data).hexdigest()


def classify(raw,pc,decoder):
    import capstone
    from capstone.x86 import X86_OP_IMM
    rows=list(decoder.disasm(raw,pc))
    if not rows or sum(i.size for i in rows)!=len(raw):return 'incomplete_decode',rows
    if rows[-1].bytes!=b'\xc2\x04\x00':return 'outside_added_return_cleanup',rows
    if len(rows)>128:return 'outside_instruction_budget',rows
    jumps=[i for i in rows if i.group(capstone.CS_GRP_JUMP)]
    if len(jumps)!=1 or jumps[0].mnemonic in ('jmp','ljmp') or len(jumps[0].operands)!=1 or jumps[0].operands[0].type!=X86_OP_IMM:return 'outside_one_direct_conditional',rows
    if any(i.group(capstone.CS_GRP_RET) or i.group(capstone.CS_GRP_IRET) for i in rows[:-1]):return 'outside_single_final_return',rows
    at=rows.index(jumps[0]);join=next((j for j,i in enumerate(rows) if i.address==jumps[0].operands[0].imm),-1)
    if join<=at+1 or join>=len(rows)-1:return 'outside_forward_boundary_join',rows
    if sum(i.group(capstone.CS_GRP_CALL) for i in rows[at+1:join])!=1:return 'outside_single_conditional_call',rows
    if any(i.group(capstone.CS_GRP_CALL) and (len(i.operands)!=1 or i.operands[0].type!=X86_OP_IMM) for i in rows):return 'outside_direct_call_operands',rows
    return 'typed_check_required',rows


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('request','runtime','baseline-runtime','output'):p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args();request=json.loads(args.request.read_text());project=request['project'];inputs=request['inputs']
    def verify():
        for path,digest in inputs.items():
            if sha(Path(path).read_bytes())!=digest:raise ValueError('submitted_input_changed:'+path)
    verify();import capstone
    from rapid_object.compare import PE
    original=Path(project['original']).read_bytes();pe=PE(original);inventory=json.loads(Path(project['inventory']).read_text());entries={f['rva']:f for f in inventory['functions']};assert len(entries)==len(inventory['functions'])
    cfgpath=Path(project['replayable']['lifter_config']);cfg=json.loads(cfgpath.read_text());dll=Path(cfg['adapter_dll']);dll=dll if dll.is_absolute() else cfgpath.parent/dll;dotnet=cfg.get('dotnet','dotnet')
    spec=importlib.util.spec_from_file_location('stack_adapter',ROOT/'tools/decompilation-mcp/replayable_adapter.py');adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
    # Validate the full pinned lifter/source/runtime contract through the same adapter.
    first=adapter.lift(request);image_end=first['image_end'];md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);md.detail=True;cache={};counts=Counter();blocked=Counter();begin=time.monotonic()
    binding=dict(inputs=inputs,runtime_sha256=sha(args.runtime.read_bytes()),baseline_runtime_sha256=sha(args.baseline_runtime.read_bytes()),scan_sha256=sha(Path(__file__).read_bytes()),module_sha256=project['module_sha256'],inventory_sha256=sha(Path(project['inventory']).read_bytes()),capstone_version=capstone.__version__)
    args.output.mkdir(parents=True,exist_ok=False);proc=subprocess.Popen([dotnet,str(dll)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
    def lift(entry):
        rva=entry['rva']
        if rva in cache:return cache[rva]
        ranges=entry['body_ranges']
        if len(ranges)!=1 or ranges[0]['start_rva']!=rva:raise ValueError('unsupported_callee_ranges')
        raw=pe.read(rva,ranges[0]['end_rva_inclusive']-rva+1)
        if len(raw)!=entry['body_bytes']:raise ValueError('inventory_body_length_disagrees')
        proc.stdin.write(json.dumps(dict(hex=raw.hex(),pc=pe.image_base+rva,id=project['module_sha256']+':'+str(rva)))+'\n');proc.stdin.flush();out=json.loads(proc.stdout.readline())
        if 'adapter_error' in out:raise ValueError('lifter_adapter_error')
        decoded=list(md.disasm(raw,pe.image_base+rva))
        if sum(i.size for i in decoded)!=len(raw) or [(i.address,i.size,i.bytes.hex()) for i in decoded]!=[(i['pc'],i['length'],i['raw_hex']) for i in out['instructions']]:raise ValueError('independent_decode_disagreement')
        cache[rva]=dict(lift=out,image_base=pe.image_base,binary_slice_sha256=sha(raw));return cache[rva]
    def dependencies(caller):
        result={};chains=[]
        for original_target,initial in adapter.select_callee_entries(request,caller,inventory):
            target=original_target;entry=initial;seen=set();chain=[]
            for depth in range(9):
                if target in seen:raise ValueError('forwarding_cycle')
                seen.add(target);chain.append(target)
                if target not in result:
                    value=lift(entry);result[target]=dict(target=target,lift=value['lift'],binary_slice_sha256=value['binary_slice_sha256'])
                dest=adapter.pure_forwarding_target(result[target])
                if dest is None:break
                if depth==8:raise ValueError('forwarding_depth_exhausted')
                if dest-pe.image_base not in entries:raise ValueError('forwarding_target_not_inventory_entry')
                target=dest;entry=entries[dest-pe.image_base]
            chains.append(dict(original_target=original_target,chain=chain))
        return list(result.values()),chains
    def frontend(runtime,payload):
        run=subprocess.run([dotnet,str(runtime),'recover-ir'],input=json.dumps(payload),text=True,capture_output=True,timeout=30)
        if run.returncode:raise ValueError('frontend_failed')
        return json.loads(run.stdout)
    try:
        with (args.output/'identities.jsonl').open('x') as output:
            for entry in sorted(entries.values(),key=lambda x:x['rva']):
                rva=entry['rva'];row=dict(rva=rva,status='unsupported_inventory_ranges',compiled=False,matched=False);ranges=entry['body_ranges']
                try:
                    if len(ranges)==1 and ranges[0]['start_rva']==rva:
                        raw=pe.read(rva,ranges[0]['end_rva_inclusive']-rva+1)
                        if len(raw)!=entry['body_bytes']:raise ValueError('inventory_body_length_disagrees')
                        row['status'],_=classify(raw,pe.image_base+rva,md)
                        if row['status']=='typed_check_required':
                            caller=lift(entry);deps,chains=dependencies(caller)
                            payload=dict(lift=caller['lift'],rva=rva,image_base=pe.image_base,image_end=image_end,module=project['module'],stack_arguments=True,conditional_calls=True,callee_lifts=deps)
                            candidate=frontend(args.runtime,payload);row.update(status='typed_unsupported',blocker=candidate.get('blocker'))
                            if candidate['status']=='generated':
                                baseline=frontend(args.baseline_runtime,dict(payload,conditional_calls=False))
                                row.update(status='generated_conditional_hypothesis',source_sha256=sha(candidate['source'].encode()),original_slice_sha256=caller['binary_slice_sha256'],dependencies=[dict(target=d['target'],binary_slice_sha256=d['binary_slice_sha256']) for d in deps],forwarding_chains=chains,baseline_status=baseline['status'],baseline_blocker=baseline.get('blocker'));row.pop('blocker',None)
                except (ValueError,KeyError,OSError,subprocess.TimeoutExpired) as error:row.update(status='analysis_failure',blocker=type(error).__name__+':'+str(error))
                counts[row['status']]+=1
                if row.get('blocker'):blocked[row['blocker']]+=1
                output.write(json.dumps(row,sort_keys=True)+'\n')
                if sum(counts.values())%1000==0:output.flush();print(json.dumps(dict(scanned=sum(counts.values()),counts=dict(counts))),flush=True)
    finally:
        proc.stdin.close();proc.terminate();proc.wait(timeout=10);proc.stdout.close();proc.stderr.close()
    verify();assert sha(args.runtime.read_bytes())==binding['runtime_sha256'] and sha(args.baseline_runtime.read_bytes())==binding['baseline_runtime_sha256']
    summary=dict(schema_version=1,binding=binding,inventory_identities=len(entries),accounted_identities=sum(counts.values()),counts=dict(counts),blockers=dict(blocked),elapsed_seconds=round(time.monotonic()-begin,3),comparisons=0,vm_compiles=0,source_exports=0,proof=False,scope='added conditional-rule applicability only; composed prior domains retained; scan is not equivalence')
    (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True)

if __name__=='__main__':main()

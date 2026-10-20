"""Account every inventory identity for the bounded added EH rule, never acceptance."""
import argparse,collections,hashlib,importlib.util,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
sha=lambda b:hashlib.sha256(b).hexdigest()
def classify(raw,pc,md):
 import capstone
 from capstone.x86 import X86_OP_IMM,X86_OP_MEM,X86_REG_FS
 rows=list(md.disasm(raw,pc))
 if not rows or sum(i.size for i in rows)!=len(raw):return 'incomplete_decode'
 if len(rows)>128:return 'outside_instruction_budget'
 if len([i for i in rows if i.group(capstone.CS_GRP_RET)])!=2 or rows[-1].bytes!=b'\xc3':return 'outside_two_terminal_C3_domain'
 if any(i.group(capstone.CS_GRP_RET) and i.bytes!=b'\xc3' for i in rows):return 'outside_zero_return_cleanup'
 if not any(o.type==X86_OP_MEM and o.mem.segment==X86_REG_FS for i in rows for o in i.operands):return 'outside_FS_registration_domain'
 jumps=[i for i in rows if i.group(capstone.CS_GRP_JUMP)]
 if len(jumps)!=1 or jumps[0].mnemonic in ('jmp','ljmp') or len(jumps[0].operands)!=1 or jumps[0].operands[0].type!=X86_OP_IMM:return 'outside_one_conditional_domain'
 calls=[i for i in rows if i.group(capstone.CS_GRP_CALL)]
 if len(calls)!=2 or any(len(i.operands)!=1 or i.operands[0].type!=X86_OP_IMM for i in calls):return 'outside_two_direct_calls_domain'
 return 'typed_check_required'
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('request','runtime','baseline-runtime','output'):p.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args();request=json.loads(a.request.read_text());project=request['project'];inputs=request['inputs']
 def verify():
  for path,digest in inputs.items():
   if sha(Path(path).read_bytes())!=digest:raise ValueError('submitted_input_changed:'+path)
 verify();import capstone
 from rapid_object.compare import PE
 spec=importlib.util.spec_from_file_location('eh_adapter',ROOT/'tools/decompilation-mcp/replayable_adapter.py');adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
 original=Path(project['original']).read_bytes();pe=PE(original);inv=json.loads(Path(project['inventory']).read_text());entries=sorted(inv['functions'],key=lambda e:e['rva']);assert len({e['rva'] for e in entries})==len(entries)
 cfg=json.loads(Path(project['replayable']['lifter_config']).read_text());dotnet=cfg.get('dotnet','dotnet');md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);md.detail=True
 counts=collections.Counter();blockers=collections.Counter();begin=time.monotonic();binding=dict(inputs=inputs,runtime_sha256=sha(a.runtime.read_bytes()),baseline_runtime_sha256=sha(a.baseline_runtime.read_bytes()),scan_sha256=sha(Path(__file__).read_bytes()),module_sha256=sha(original),inventory_sha256=sha(Path(project['inventory']).read_bytes()),capstone_version=capstone.__version__)
 def frontend(runtime,payload):
  out=subprocess.run([dotnet,str(runtime),'recover-ir'],input=json.dumps(payload),capture_output=True,text=True,timeout=60)
  if out.returncode:raise ValueError('frontend_process_failure')
  return json.loads(out.stdout)
 a.output.mkdir(parents=True,exist_ok=False)
 with (a.output/'identities.jsonl').open('x') as output:
  for entry in entries:
   rva=entry['rva'];row=dict(rva=rva,status='unsupported_inventory_ranges',compiled=False,matched=False)
   try:
    ranges=entry['body_ranges']
    if len(ranges)==1 and ranges[0]['start_rva']==rva:
     raw=pe.read(rva,ranges[0]['end_rva_inclusive']-rva+1)
     if len(raw)!=entry['body_bytes']:raise ValueError('inventory_body_length_disagrees')
     row['status']=classify(raw,pe.image_base+rva,md)
     if row['status']=='typed_check_required':
      req=dict(request,rva=rva,entry=entry);caller=adapter.lift(req);deps=adapter.lift_callees(req);evidence=adapter.lift_eh(req)
      payload=dict(lift=caller['lift'],callee_lifts=deps['callees'],eh_evidence=evidence,rva=rva,image_base=caller['image_base'],image_end=caller['image_end'],module=project['module'],eh_paths=True)
      result=frontend(a.runtime,payload);row.update(status='typed_unsupported',blocker=result.get('blocker'))
      if result['status']=='generated':
       baseline=frontend(a.baseline_runtime,dict(payload,eh_paths=False,conditional_calls=True,stack_arguments=True))
       row.update(status='generated_EH_hypothesis',source_sha256=sha(result['source'].encode()),original_slice_sha256=caller['binary_slice_sha256'],callee_lifts_sha256=sha(json.dumps(deps,sort_keys=True).encode()),eh_evidence_sha256=sha(json.dumps(evidence,sort_keys=True).encode()),baseline_status=baseline['status'],baseline_blocker=baseline.get('blocker'));row.pop('blocker',None)
   except (ValueError,KeyError,OSError,subprocess.TimeoutExpired) as e:row.update(status='analysis_failure',blocker=type(e).__name__+':'+str(e))
   counts[row['status']]+=1
   if row.get('blocker'):blockers[row['blocker']]+=1
   output.write(json.dumps(row,sort_keys=True)+'\n')
 verify();assert sha(a.runtime.read_bytes())==binding['runtime_sha256'] and sha(a.baseline_runtime.read_bytes())==binding['baseline_runtime_sha256']
 summary=dict(schema_version=1,binding=binding,inventory_identities=len(entries),accounted_identities=sum(counts.values()),counts=dict(counts),blockers=dict(blockers),elapsed_seconds=round(time.monotonic()-begin,3),comparisons=0,vm_compiles=0,source_exports=0,proof=False,scope='added EH-rule applicability only; all prior domains composed; scan is not equivalence')
 (a.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
if __name__=='__main__':main()

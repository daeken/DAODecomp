"""Synthetic persistence/attestation fixtures, never native/game match credit."""
from contextlib import closing
import copy,hashlib,importlib.util,inspect,json,shutil,sqlite3,sys,unittest
import test_replayable_pipeline as pipeline
from test_rapid_object_coff import pe,coff
from test_replayable_encoding import recipe as old_recipe
stdio=pipeline.stdio;ROOT=pipeline.ROOT

def sha(raw):return hashlib.sha256(raw).hexdigest()
def recipe():
 x=old_recipe();x['architecture']='x86-bits32-terminal-aware-abi-effects-v1';x['compiler_profile']='vc8-x86-flat32-terminal-aware-memory-control-v1';x['steps']=x['steps'][:-1]+['derive-original-noncontinuable-CRT-exits-v1','raise-terminal-calls-incoming-word-slots-v1','emit-vc8-terminal-aware-memory-control-v1','compare-complete-x86-encoding-equivalence-v1','compare-complete-flat32-ABI-effects-v1'];return x

def mock_effect_lift(raw,pc):
 # Deliberately incomplete OPEN fake frontend for cache tests only. It models
 # onlyCF forADD; actual-pinned frontend/native evidence is tested separately.
 import capstone
 N=lambda k,**kw:dict(type='LiftIl.'+k,**kw)
 T=lambda w:dict(type='LiftIl.IlType+I',Bits=w,Signed=False)
 C=lambda v,w=32:N('IlConst',Ty=T(w),Bits=dict(decimal=str(v)))
 cast=lambda x,w,k='Zext':N('IlCast',Kind=dict(name=k),X=x,Ty=T(w))
 R=lambda i,w=32:cast(N('IlReadReg',Kind=dict(name='X86'),Idx=i,Ty=T(64)),w,'Trunc') if w<64 else N('IlReadReg',Kind=dict(name='X86'),Idx=i,Ty=T(64))
 B=lambda op,a,b,w=32:N('IlBin',Op=dict(name=op),L=a,R=b,Ty=T(w))
 W=lambda i,v:N('IlWriteReg',Kind=dict(name='X86'),Idx=i,Val=cast(v,64))
 md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);md.detail=True;rows=[];regs={n:i for i,n in enumerate(('eax','ecx','edx','ebx','esp','ebp','esi','edi'))}
 for ins in md.disasm(raw,pc):
  def operand(o):
   if o.type==capstone.x86.X86_OP_REG:return R(regs[ins.reg_name(o.reg)])
   m=o.mem;address=B('Add',R(regs[ins.reg_name(m.base)]),C(m.disp))
   if m.index:address=B('Add',address,R(regs[ins.reg_name(m.index)]))
   return N('IlLoad',Addr=cast(address,64),Ty=T(32))
  if ins.mnemonic=='ret':body=[N('IlBranch',Kind=dict(name='Ret'),Target=C(0),Cond=None)]
  elif ins.mnemonic=='mov':body=[W(regs[ins.reg_name(ins.operands[0].reg)],operand(ins.operands[1]))]
  elif ins.mnemonic=='lea':
   m=ins.operands[1].mem;body=[W(regs[ins.reg_name(ins.operands[0].reg)],B('Add',R(regs[ins.reg_name(m.base)]),R(regs[ins.reg_name(m.index)])))]
  elif ins.mnemonic=='add':
   i=regs[ins.reg_name(ins.operands[0].reg)];tmp=N('IlTmp',Id=0,Ty=T(32));body=[N('IlLet',Id=0,Val=B('Add',R(i),operand(ins.operands[1]))),N('IlWriteReg',Kind=dict(name='Eflags'),Idx=0,Val=B('Ult',tmp,R(i),1)),W(i,tmp)]
  else:raise ValueError('unsupported open fixture')
  rows.append(dict(pc=ins.address,offset=ins.address-pc,length=ins.size,raw_hex=ins.bytes.hex(),lift_error=None,opaque_markers=[],tree=N('IlBlock',Body=body)))
 return dict(schema='sharpretro_instruction_lift_v1',mode='Bits32',pc=pc,byte_length=len(raw),decoded_bytes=sum(r['length'] for r in rows),decode_complete=True,unprocessed_hex='',lift_errors=0,opaque_instructions=0,instructions=rows)

@unittest.skipUnless(stdio.DLL.exists() and shutil.which('z3'),'build changed component and existing solver required')
class AbiEffectsPipelineTests(unittest.TestCase):
 setUp=pipeline.PipelineBoundaryTests.setUp
 tearDown=pipeline.PipelineBoundaryTests.tearDown
 connect=pipeline.PipelineBoundaryTests.connect
 def submit(self,token):return self.client.call('replayable_run_next',project_id='open',idempotency_key=token,recipe_json=json.dumps(recipe()),compile=False)
 def status(self):return self.client.call('replayable_status',project_id='open',recipe_json=json.dumps(recipe()))
 def store(self,job,folder,result):
  (folder/'result.json').write_text(json.dumps(result))
  with closing(sqlite3.connect(self.root/'state/jobs.sqlite3')) as db,db:db.execute("UPDATE jobs SET state='completed',result=? WHERE id=?",(json.dumps(result),job));db.execute('UPDATE replayable_frontier SET status=? WHERE job=?',(result['status'],job))
 def seed(self):
  code=bytes.fromhex('8b44240403c303c703d3c3');candidate=bytes.fromhex('8d041f0344240403d3c3');binary=pe(code+b'\0'*256);(self.root/'original.exe').write_bytes(binary);inv=json.loads((self.root/'inventory.json').read_text());inv['module_sha256']=sha(binary);inv['functions'][0].update(body_bytes=len(code),body_ranges=[dict(start_rva=0x1000,end_rva_inclusive=0x1000+len(code)-1)]);(self.root/'inventory.json').write_text(json.dumps(inv))
  self.dll.write_text('import sys,json\n'+inspect.getsource(mock_effect_lift)+'\nfor line in sys.stdin:\n req=json.loads(line);out=mock_effect_lift(bytes.fromhex(req["hex"]),req["pc"]);out["id"]=req["id"];print(json.dumps(out))\n');manifest=self.root/'manifest.json';m=json.loads(manifest.read_text());m['assemblies_sha256']={self.dll.name:sha(self.dll.read_bytes())};manifest.write_text(json.dumps(m));cfg=self.root/'lifter.json';lc=json.loads(cfg.read_text());lc['dotnet']=sys.executable;cfg.write_text(json.dumps(lc))
  solver=__import__('pathlib').Path(shutil.which('z3')).resolve();solver_cfg=self.root/'solver.json';solver_cfg.write_text(json.dumps(dict(schema_version=1,executable=str(solver),sha256=sha(solver.read_bytes()),observation_profile='abi-ordered-fault-events-v1')));config=json.loads(self.config.read_text());p=config['projects'][0];p['module_sha256']=sha(binary);p['compiler_flags']=['/c','/O2','/Ob1','/Oy','/Gy','/Z7','/Zl','/GS','/GR-','/EHsc'];p['allowed_roots'].append(str(solver.parent));p['replayable']['equivalence_solver_config']=str(solver_cfg);self.config.write_text(json.dumps(config));self.client=self.connect();first=self.submit('open-abi-cache');stdio.wait_job(self.client,first['job_id']);folder=self.root/'attempts'/first['job_id'];build=folder/'build';build.mkdir();req=json.loads((folder/'request.json').read_text());source=b'// FUNCTION: open.exe 0x00401000\nextern "C" unsigned int fn_00001000() { return 42u; }\n';(folder/'candidate.cpp').write_bytes(source);(build/'candidate.cpp').write_bytes(source);(build/'candidate.obj').write_bytes(coff(candidate,comdat=True));compiler=dict(sha256=req['project']['compiler_sha256']);(build/'compiler.json').write_text(json.dumps(compiler));receipt=dict(exit_code=0,linked=False,original_executed=False,module_sha256=p['module_sha256'],source_sha256=sha(source),object_sha256=sha((build/'candidate.obj').read_bytes()),compiler=compiler,flags=p['compiler_flags']);(build/'run.json').write_text(json.dumps(receipt));inputs=dict(req['inputs']);inputs.update({str(build/n):sha((build/n).read_bytes()) for n in ('candidate.cpp','candidate.obj','compiler.json','run.json')});retained=dict(project=req['project'],build=dict(config=dict(folder=str(build),rva=0x1000,profile='ordinary',allow_encoding_equivalence=True,allow_abi_effects_equivalence=True),expected_source_sha256=sha(source)),inputs=inputs);(folder/'retained-check-request.json').write_text(json.dumps(retained));spec=importlib.util.spec_from_file_location('abi_retained_adapter',ROOT/'tools/decompilation-mcp/adapter.py');adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter);compact,report=adapter.run(retained);self.assertEqual(compact['status'],'mismatch',report);self.assertFalse(compact['abi_effects_acceptance_enabled'])
  for name in ('comparison.json','retained-comparison.json'):(folder/name).write_text(json.dumps(report))
  cert=compact['abi_effects_diagnostic'];raw=json.dumps(cert,sort_keys=True,separators=(',',':')).encode();(folder/'abi-effects-equivalence.json').write_bytes(raw);result=dict(status='abi_trace_equivalent',strict_status='mismatch',match_kind='abi_trace_equivalent',proof=False,source_sha256=sha(source),object_sha256=receipt['object_sha256'],comparison_sha256=sha((folder/'comparison.json').read_bytes()),retained_comparison_sha256=sha((folder/'retained-comparison.json').read_bytes()),retained_request_sha256=sha((folder/'retained-check-request.json').read_bytes()),abi_effects_equivalence=cert,abi_effects_equivalence_sha256=sha(raw),retained_check=compact);self.store(first['job_id'],folder,result);return first,folder,result,retained
 def test_pending_policy_restart_and_forged_acceptance_mode_refuse(self):
  first,folder,result,retained=self.seed();state=self.status();self.assertEqual((state['new_pipeline_full_matches'],state['new_pipeline_encoding_equivalent_matches'],state['new_pipeline_abi_trace_equivalent_matches'],state['new_pipeline_accepted_matches']),(0,0,0,0));self.assertEqual(state['first_unresolved_rva'],0x1000);self.client=self.connect();self.assertEqual(self.status()['new_pipeline_abi_trace_equivalent_matches'],0)
  for field in ('strict_status','match_kind','proof','retained_check','abi_effects_equivalence','abi_effects_equivalence_sha256'):
   x=copy.deepcopy(result);x.pop(field);self.store(first['job_id'],folder,x);self.assertEqual(self.status()['new_pipeline_accepted_matches'],0,field)
  x=copy.deepcopy(result);x['abi_effects_equivalence']['effect_windows'][0]['status']='sat';x['retained_check']['abi_effects_equivalence']=x['abi_effects_equivalence'];raw=json.dumps(x['abi_effects_equivalence']).encode();(folder/'abi-effects-equivalence.json').write_bytes(raw);x['abi_effects_equivalence_sha256']=sha(raw);self.store(first['job_id'],folder,x);self.assertEqual(self.status()['new_pipeline_accepted_matches'],0)
 def test_tracking_kind_and_regression_counts_never_relabel(self):
  first,folder,result,retained=self.seed();key=self.status()['pipeline_key']
  for wrong in ('full_match','encoding_equivalent'):
   with closing(sqlite3.connect(self.root/'state/jobs.sqlite3')) as db,db:db.execute('UPDATE replayable_frontier SET status=? WHERE job=?',(wrong,first['job_id']))
   self.assertEqual(self.status()['new_pipeline_accepted_matches'],0)
  with closing(sqlite3.connect(self.root/'state/jobs.sqlite3')) as db,db:db.execute('UPDATE replayable_frontier SET input_key=?,status=? WHERE job=?',('regression:'+key,'abi_trace_equivalent',first['job_id']))
  state=self.status();self.assertEqual((state['regression_full_matches'],state['regression_encoding_equivalent_matches'],state['regression_abi_trace_equivalent_matches'],state['regression_accepted_matches']),(0,0,0,0));nxt=self.submit('regression-does-not-advance');self.assertEqual(nxt['rva'],0x1000);stdio.wait_job(self.client,nxt['job_id'])
 def test_solver_binding_or_profile_change_never_transfers_cache_credit(self):
  first,folder,result,retained=self.seed();before=self.status();cfg=self.root/'solver.json';cfg.write_text(cfg.read_text()+'\n');after=self.status();self.assertNotEqual(before['pipeline_key'],after['pipeline_key']);self.assertEqual(after['new_pipeline_accepted_matches'],0);x=json.loads(cfg.read_text());x['observation_profile']='trust-all-IR';cfg.write_text(json.dumps(x))
  with self.assertRaises(ValueError):self.status()
 def test_wrong_rebound_object_never_reuses_a_saved_certificate(self):
  first,folder,result,retained=self.seed();build=folder/'build';(build/'candidate.obj').write_bytes(coff(bytes.fromhex('8d040f0344240403d3c3'),comdat=True));receipt=json.loads((build/'run.json').read_text());receipt['object_sha256']=sha((build/'candidate.obj').read_bytes());(build/'run.json').write_text(json.dumps(receipt));retained['inputs'].update({str(build/n):sha((build/n).read_bytes()) for n in ('candidate.obj','run.json')});(folder/'retained-check-request.json').write_text(json.dumps(retained));result.update(object_sha256=receipt['object_sha256'],retained_request_sha256=sha((folder/'retained-check-request.json').read_bytes()));self.store(first['job_id'],folder,result);self.assertEqual(self.status()['new_pipeline_accepted_matches'],0)
 def test_cross_policy_unknown_barrier_and_idempotency_survive(self):
  first,folder,result,retained=self.seed();self.assertEqual(self.submit('open-abi-cache')['job_id'],first['job_id'])
  for state in ('running','external_outcome_unknown'):
   with closing(sqlite3.connect(self.root/'state/jobs.sqlite3')) as db,db:db.execute('UPDATE replayable_frontier SET status=? WHERE job=?',(state,first['job_id']))
   with self.assertRaises(ValueError):self.client.call('replayable_run_next',project_id='open',idempotency_key='blocked-old-'+state,compile=False)

 def test_diagnostic_status_never_advances_recovery(self):
  first,folder,result,retained=self.seed();result.update(status='mismatch',match_kind='none',abi_effects_acceptance_enabled=False);self.store(first['job_id'],folder,result);state=self.status();self.assertFalse(state['abi_effects_acceptance_enabled']);self.assertEqual(state['new_pipeline_accepted_matches'],0);nxt=self.submit('diagnostic-keeps-frontier');self.assertEqual(nxt['rva'],0x1000);stdio.wait_job(self.client,nxt['job_id'])

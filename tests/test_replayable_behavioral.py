"""Open inherited-registration structure boundaries; no game acceptance fixtures."""
import struct,unittest
from rapid_object.encoding_equivalence import Refusal
from tools.replayable.unregistered_unwind import certify_structure
from test_rapid_object_coff import pe,coff
from rapid_object.encoding_equivalence import decode

class UnregisteredUnwindTests(unittest.TestCase):
 def check(self,a='5303c35bc3',b='538d04035bc3',original=None):
  a=bytes.fromhex(a);b=bytes.fromhex(b);left=[i.address+i.size for i in decode(a,0x401000) if i.mnemonic=='call'];right=[i.address+i.size for i in decode(b,0x401000) if i.mnemonic=='call'];mapping=dict(zip(left,right));return certify_structure(a,b,0x401000,mapping,original or pe(a),coff(b,comdat=True))
 def test_same_unregistered_stack_protocol_preserves_inherited_chain(self):
  x=self.check();self.assertEqual(x['local_registration_frames'],0);self.assertEqual(x['required_fault_registers'],[3,4,5,6,7]);self.assertFalse(x['native_OS_execution'])
 def test_explicit_dynamic_stack_change_refuses(self):
  with self.assertRaisesRegex(Refusal,'dynamic_or_rebased_stack'):self.check('8be003c3c3','8be08d0403c3')
 def test_changed_push_pop_protocol_refuses(self):
  with self.assertRaisesRegex(Refusal,'stack_protocol'):self.check('5303c35bc3','568d04035ec3')
 def test_function_table_metadata_is_not_assumed_unregistered(self):
  raw=bytearray(pe(bytes.fromhex('5303c35bc3')));offset=struct.unpack_from('<I',raw,0x3c)[0]+24;struct.pack_into('<I',raw,offset+92,16);struct.pack_into('<II',raw,offset+96+24,0x2000,12)
  with self.assertRaisesRegex(Refusal,'function_table'):self.check(original=bytes(raw))
 def test_registration_segment_transfer_and_unknown_instruction_refuse(self):
  for a,b in [('64a10000000003c3c3','64a1000000008d0403c3'),('0f31c3','0f31c3'),('ff10c3','ff10c3')]:
   with self.subTest(a=a),self.assertRaises(Refusal):self.check(a,b)
 def test_call_targets_and_mapped_return_continuations_are_explicit(self):
  with self.assertRaisesRegex(Refusal,'changed_return_pc'):self.check('03c3e800010000c3','8d0403e8ff000000c3')
  x=self.check('03c303c7e800010000c3','03c703c3e800010000c3');self.assertEqual(len(x['paired_calls']),1);self.assertEqual(x['paired_calls'][0]['original_return'],x['paired_calls'][0]['candidate_return'])

# Persistence-only synthetic compiler receipt; not native acceptance evidence.
import copy,json,shutil,sqlite3
from contextlib import closing
import test_replayable_abi_effects as abi

from test_replayable_abi_effects import sha,mock_effect_lift,inspect,sys,importlib,pipeline,stdio,ROOT
def behavioral_recipe():
 x=abi.recipe();x['steps']=x['steps'][:-1]+['lower-vc8-packed-observed-receiver-word-fields-v1','compact-captured-instruction-local-unsigned-scalars-v1'];x['architecture']='x86-bits32-scalar-behavioral-events-v1';x['steps'].append('compare-windows-x86-inherited-unwind-ordered-events-v1');return x
@unittest.skipUnless(stdio.DLL.exists() and shutil.which('z3'),'changed component/existing solver needed')
class BehavioralPipelineTests(unittest.TestCase):
 setUp=abi.AbiEffectsPipelineTests.setUp
 tearDown=abi.AbiEffectsPipelineTests.tearDown
 connect=abi.AbiEffectsPipelineTests.connect
 store=abi.AbiEffectsPipelineTests.store
 def submit(self,token):return self.client.call('replayable_run_next',project_id='open',idempotency_key=token,recipe_json=json.dumps(behavioral_recipe()),compile=False)
 def status(self):return self.client.call('replayable_status',project_id='open',recipe_json=json.dumps(behavioral_recipe()))
 def seed(self):
  code=bytes.fromhex('8b44240403c303c703d3c3');candidate=bytes.fromhex('8d041f0344240403d3c3');binary=pe(code+b'\0'*256);(self.root/'original.exe').write_bytes(binary);inv=json.loads((self.root/'inventory.json').read_text());inv['module_sha256']=sha(binary);inv['functions'][0].update(body_bytes=len(code),body_ranges=[dict(start_rva=0x1000,end_rva_inclusive=0x1000+len(code)-1)]);(self.root/'inventory.json').write_text(json.dumps(inv))
  self.dll.write_text('import sys,json\n'+inspect.getsource(mock_effect_lift)+'\nfor line in sys.stdin:\n req=json.loads(line);out=mock_effect_lift(bytes.fromhex(req["hex"]),req["pc"]);out["id"]=req["id"];print(json.dumps(out))\n');manifest=self.root/'manifest.json';m=json.loads(manifest.read_text());m['assemblies_sha256']={self.dll.name:sha(self.dll.read_bytes())};manifest.write_text(json.dumps(m));cfg=self.root/'lifter.json';lc=json.loads(cfg.read_text());lc['dotnet']=sys.executable;cfg.write_text(json.dumps(lc))
  solver=__import__('pathlib').Path(shutil.which('z3')).resolve();solver_cfg=self.root/'solver.json';solver_cfg.write_text(json.dumps(dict(schema_version=1,executable=str(solver),sha256=sha(solver.read_bytes()),observation_profile='windows-x86-inherited-unwind-ordered-events-v1')));config=json.loads(self.config.read_text());p=config['projects'][0];p['module_sha256']=sha(binary);p['compiler_flags']=['/c','/O2','/Ob1','/Oy','/Gy','/Z7','/Zl','/GS','/GR-','/EHsc'];p['allowed_roots'].append(str(solver.parent));p['replayable']['equivalence_solver_config']=str(solver_cfg);self.config.write_text(json.dumps(config));self.client=self.connect();first=self.submit('open-abi-cache');stdio.wait_job(self.client,first['job_id']);folder=self.root/'attempts'/first['job_id'];build=folder/'build';build.mkdir();req=json.loads((folder/'request.json').read_text());source=b'// FUNCTION: open.exe 0x00401000\nextern "C" unsigned int fn_00001000() { return 42u; }\n';(folder/'candidate.cpp').write_bytes(source);(build/'candidate.cpp').write_bytes(source);(build/'candidate.obj').write_bytes(coff(candidate,comdat=True));compiler=dict(sha256=req['project']['compiler_sha256']);(build/'compiler.json').write_text(json.dumps(compiler));receipt=dict(exit_code=0,linked=False,original_executed=False,module_sha256=p['module_sha256'],source_sha256=sha(source),object_sha256=sha((build/'candidate.obj').read_bytes()),compiler=compiler,flags=p['compiler_flags']);(build/'run.json').write_text(json.dumps(receipt));inputs=dict(req['inputs']);inputs.update({str(build/n):sha((build/n).read_bytes()) for n in ('candidate.cpp','candidate.obj','compiler.json','run.json')});retained=dict(project=req['project'],build=dict(config=dict(folder=str(build),rva=0x1000,profile='ordinary',allow_encoding_equivalence=True,allow_behavioral_equivalence=True),expected_source_sha256=sha(source)),inputs=inputs);(folder/'retained-check-request.json').write_text(json.dumps(retained));spec=importlib.util.spec_from_file_location('abi_retained_adapter',ROOT/'tools/decompilation-mcp/adapter.py');adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter);compact,report=adapter.run(retained);self.assertEqual(compact['status'],'behaviorally_equivalent',report)
  for name in ('comparison.json','retained-comparison.json'):(folder/name).write_text(json.dumps(report))
  cert=compact['behavioral_equivalence'];raw=json.dumps(cert,sort_keys=True,separators=(',',':')).encode();(folder/'behavioral-equivalence.json').write_bytes(raw);result=dict(status='behaviorally_equivalent',strict_status='mismatch',match_kind='behaviorally_equivalent',proof=False,source_sha256=sha(source),object_sha256=receipt['object_sha256'],comparison_sha256=sha((folder/'comparison.json').read_bytes()),retained_comparison_sha256=sha((folder/'retained-comparison.json').read_bytes()),retained_request_sha256=sha((folder/'retained-check-request.json').read_bytes()),behavioral_equivalence=cert,behavioral_equivalence_sha256=sha(raw),retained_check=compact);self.store(first['job_id'],folder,result);return first,folder,result,retained
 def test_fresh_bound_result_has_distinct_mode_and_restart_binding(self):
  first,folder,result,retained=self.seed();state=self.status();self.assertEqual(state['new_pipeline_behaviorally_equivalent_matches'],1);self.assertEqual(state['new_pipeline_full_matches'],0);self.assertEqual(state['new_pipeline_encoding_equivalent_matches'],0);self.assertTrue(state['behavioral_acceptance_enabled']);self.client=self.connect();self.assertEqual(self.status()['new_pipeline_behaviorally_equivalent_matches'],1)
  for wrong in ('full_match','encoding_equivalent'):
   with closing(sqlite3.connect(self.root/'state/jobs.sqlite3')) as db,db:db.execute('UPDATE replayable_frontier SET status=? WHERE job=?',(wrong,first['job_id']))
   self.assertEqual(self.status()['new_pipeline_accepted_matches'],0)
 def test_missing_or_forged_structural_certificate_refuses(self):
  first,folder,result,retained=self.seed()
  for field in ('strict_status','match_kind','behavioral_equivalence','behavioral_equivalence_sha256'):
   changed=copy.deepcopy(result);changed.pop(field);self.store(first['job_id'],folder,changed);self.assertEqual(self.status()['new_pipeline_accepted_matches'],0)
  changed=copy.deepcopy(result);changed['behavioral_equivalence']['unwind_relation']['local_registration_frames']=1;raw=json.dumps(changed['behavioral_equivalence']).encode();(folder/'behavioral-equivalence.json').write_bytes(raw);changed['behavioral_equivalence_sha256']=sha(raw);self.store(first['job_id'],folder,changed);self.assertEqual(self.status()['new_pipeline_accepted_matches'],0)
 def test_policy_change_and_unknown_remain_barriers(self):
  first,folder,result,retained=self.seed();before=self.status();cfg=self.root/'solver.json';cfg.write_text(cfg.read_text()+'\n');after=self.status();self.assertNotEqual(before['pipeline_key'],after['pipeline_key']);self.assertEqual(after['new_pipeline_accepted_matches'],0)
  for status in ('running','external_outcome_unknown'):
   with closing(sqlite3.connect(self.root/'state/jobs.sqlite3')) as db,db:db.execute('UPDATE replayable_frontier SET status=? WHERE job=?',(status,first['job_id']))
   with self.assertRaises(ValueError):self.submit('blocked-'+status)

 def test_first_gate_binds_fresh_object_before_retained_request_exists(self):
  first,folder,result,retained=self.seed();(folder/'build/build-exit.txt').write_text('0');request=json.loads((folder/'request.json').read_text());sys.path.insert(0,str(ROOT/'tools/decompilation-mcp'));import replayable_adapter
  fresh=replayable_adapter.compare_built(request,folder,(folder/'candidate.cpp').read_text());self.assertEqual(fresh['status'],'behaviorally_equivalent',fresh)

class BehavioralBoundaryTests(unittest.TestCase):
 def test_nonvolatile_observations_remain_at_changed_block_exit(self):
  from test_replayable_effect_relation import rows,put,const
  from tools.replayable.effect_relation import prove_window
  # EBX may be dead as a normal value before a later restore, but an
  # intervening unchanged fault still observes nonvolatile unwind state.
  a=rows([put(0,const(4))]);b=rows([put(0,const(4)),put(3,const(123))]);solver=shutil.which('z3')
  if not solver:self.skipTest('existing solver unavailable')
  self.assertEqual(prove_window(a,b,[0],solver,fault_context='abi-event-only',fault_live_registers=[3,4,5,6,7])['status'],'unsat')
  self.assertEqual(prove_window(a,b,[0,3,4,5,6,7],solver,fault_context='abi-event-only',fault_live_registers=[3,4,5,6,7])['status'],'sat')

 def test_repeated_reads_do_not_assume_static_external_memory(self):
  from test_replayable_effect_relation import rows,put,load,binary,reg32
  from tools.replayable.effect_relation import prove_window
  a=rows([put(0,load(6))],[put(2,load(6))]);b=rows([put(0,load(6))],[put(2,reg32(0))]);solver=shutil.which('z3')
  if not solver:self.skipTest('existing solver unavailable')
  # Baseline static model proves values equal but cannot authorize this
  # event-count-changing optimization. New mode also keeps reads independent.
  import copy
  b=copy.deepcopy(a);b[-1]['tree']['Body'].append(put(2,reg32(0)))
  self.assertEqual(prove_window(a,b,[0,2,3,4,5,6,7],solver,fault_context='abi-event-only',fault_live_registers=[3,4,5,6,7])['status'],'unsat')
  self.assertEqual(prove_window(a,b,[0,2,3,4,5,6,7],solver,fault_context='abi-event-only',fault_live_registers=[3,4,5,6,7],arbitrary_event_memory=True)['status'],'sat')

class ReturnSlotAliasTests(unittest.TestCase):
 def test_actual_typed_shorter_call_with_ordinary_alias_is_not_certified(self):
  # Same complete call target and all precallGPRs cannot hide CALL's own
  # implicit return-word store through a supplied alias. No game fixture.
  left=bytes.fromhex('8b4600e800010000c3');right=bytes.fromhex('8b06e801010000c3');from tools.replayable.effect_relation import pair_cfg
  _,mapping=pair_cfg(left,right,0x501000,[0,3,4,5,6,7])
  with self.assertRaisesRegex(Refusal,'changed_return_pc'):certify_structure(left,right,0x501000,mapping,pe(left),coff(right,comdat=True))

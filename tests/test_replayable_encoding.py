"""Open protocol/cache controls, never original-game or real-compiler evidence."""
from contextlib import closing
import copy,hashlib,importlib.util,json,sqlite3,unittest
import test_replayable_pipeline as pipeline
from test_rapid_object_coff import pe,coff
stdio=pipeline.stdio
ROOT=pipeline.ROOT

def recipe():
 return dict(schema_version=1,architecture='x86-bits32-composed-memory-encoding-equivalence-v1',frontend='sharpretro-typed-v1',compiler_profile='vc8-x86-flat32-ordered-memory-control-v1',steps=['raise-linear-effects-tail-v2','derive-original-normal-return-stack-v1','resolve-pure-forwarding-normal-return-v1','resolve-transparent-effectful-tail-ABI-v1','raise-one-forward-conditional-v1','raise-bounded-two-exit-effects-v1','derive-original-VC8-EH-frame-v1','raise-initialized-private-subword-copies-v1','observe-outgoing-push-and-private-cleanup-regions-v1','raise-reducible-ordered-memory-graph-v1','raise-guarded-counted-loop-v1','raise-aliasable-forward-memory-effects-v1','emit-vc8-composed-ordered-memory-control-v1','compare-complete-x86-encoding-equivalence-v1'])

def sha(raw):return hashlib.sha256(raw).hexdigest()

@unittest.skipUnless(stdio.DLL.exists(),'build C# component first')
class EncodingPipelineTests(unittest.TestCase):
 setUp=pipeline.PipelineBoundaryTests.setUp
 tearDown=pipeline.PipelineBoundaryTests.tearDown
 connect=pipeline.PipelineBoundaryTests.connect
 def submit(self,token,**kwargs):return self.client.call('replayable_run_next',project_id='open',idempotency_key=token,recipe_json=json.dumps(recipe()),compile=False,**kwargs)
 def status(self):return self.client.call('replayable_status',project_id='open',recipe_json=json.dumps(recipe()))
 def test_explicit_policy_key_and_bad_recipe_refusal(self):
  old=self.client.call('replayable_run_next',project_id='open',idempotency_key='old',compile=False);stdio.wait_job(self.client,old['job_id']);new=self.submit('new');stdio.wait_job(self.client,new['job_id']);self.assertNotEqual(old['pipeline_key'],new['pipeline_key'])
  status=self.status();self.assertEqual((status['new_pipeline_full_matches'],status['new_pipeline_encoding_equivalent_matches'],status['new_pipeline_accepted_matches']),(0,0,0))
  bad=recipe();bad['steps'][-1]='trust-effective-match'
  with self.assertRaises(ValueError):self.client.call('replayable_run_next',project_id='open',idempotency_key='bad',recipe_json=json.dumps(bad),compile=False)
 def test_uncertainty_cannot_be_cleared_by_new_policy(self):
  first=self.client.call('replayable_run_next',project_id='open',idempotency_key='before-policy',compile=False);stdio.wait_job(self.client,first['job_id'])
  for status in ('running','external_outcome_unknown'):
   with closing(sqlite3.connect(self.root/'state/jobs.sqlite3')) as db,db:db.execute('UPDATE replayable_frontier SET status=?',(status,))
   with self.assertRaises(ValueError):self.submit('blocked-'+status)
 def seed_exact_cache(self,synthetic_encoding=False):
  # Valid open PE/COFF and a deliberately synthetic compiler receipt exercise
  # persistence gates. No actual compiler was run and no game credit is claimed.
  code=bytes.fromhex('c644080400c3' if synthetic_encoding else 'b82a000000c3');candidate=bytes.fromhex('c644010400c3') if synthetic_encoding else code
  if synthetic_encoding:
   # Fake typed frontend tests protocol/cache mode handling only. Its complete
   # source and all imported production modules are bound in the open request.
   import inspect,sys
   from test_encoding_equivalence import mock_lift
   text='import sys,json\nsys.path.insert(0,'+repr(str(ROOT))+')\nfrom rapid_object.encoding_equivalence import instruction_fields,decode\n'+inspect.getsource(mock_lift)+'\nfor line in sys.stdin:\n req=json.loads(line);out=mock_lift(bytes.fromhex(req["hex"]),req["pc"]);out["id"]=req["id"];print(json.dumps(out))\n'
   self.dll.write_text(text);manifest=self.root/'manifest.json';m=json.loads(manifest.read_text());m['assemblies_sha256']={self.dll.name:sha(self.dll.read_bytes())};manifest.write_text(json.dumps(m));cfg=self.root/'lifter.json';c=json.loads(cfg.read_text());c['dotnet']=sys.executable;cfg.write_text(json.dumps(c))
  binary=pe(code+b'\0'*256);(self.root/'original.exe').write_bytes(binary);inventory=json.loads((self.root/'inventory.json').read_text());inventory['module_sha256']=sha(binary);inventory['functions'][0].update(body_bytes=len(code),body_ranges=[dict(start_rva=0x1000,end_rva_inclusive=0x1000+len(code)-1)]);(self.root/'inventory.json').write_text(json.dumps(inventory))
  config=json.loads(self.config.read_text());config['projects'][0]['module_sha256']=sha(binary);config['projects'][0]['compiler_flags']=['/c','/O2','/Ob1','/Oy','/Gy','/Z7','/Zl','/GS','/GR-','/EHsc'];self.config.write_text(json.dumps(config));self.client=self.connect()
  first=self.submit('cache');stdio.wait_job(self.client,first['job_id']);folder=self.root/'attempts'/first['job_id'];(folder/'build').mkdir();request=json.loads((folder/'request.json').read_text());project=request['project'];build=folder/'build';source=b'// FUNCTION: open.exe 0x00401000\nextern "C" unsigned int fn_00001000() { return 42u; }\n';(folder/'candidate.cpp').write_bytes(source);(build/'candidate.cpp').write_bytes(source);(build/'candidate.obj').write_bytes(coff(candidate,comdat=True));compiler={'sha256':project['compiler_sha256']};(build/'compiler.json').write_text(json.dumps(compiler));receipt=dict(exit_code=0,linked=False,original_executed=False,module_sha256=project['module_sha256'],source_sha256=sha(source),object_sha256=sha((build/'candidate.obj').read_bytes()),compiler=compiler,flags=project['compiler_flags']);(build/'run.json').write_text(json.dumps(receipt))
  inputs=dict(request['inputs']);inputs.update({str(build/name):sha((build/name).read_bytes()) for name in ('candidate.cpp','candidate.obj','compiler.json','run.json')});retained=dict(project=project,build=dict(config=dict(folder=str(build),rva=0x1000,profile='ordinary',allow_encoding_equivalence=True),expected_source_sha256=sha(source)),inputs=inputs);(folder/'retained-check-request.json').write_text(json.dumps(retained))
  spec=importlib.util.spec_from_file_location('open_retained_adapter',ROOT/'tools/decompilation-mcp/adapter.py');adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter);compact,report=adapter.run(retained);self.assertEqual(compact['status'],'encoding_equivalent' if synthetic_encoding else 'full_match',compact)
  for name in ('comparison.json','retained-comparison.json'):(folder/name).write_text(json.dumps(report))
  result=dict(status='full_match',source_sha256=sha(source),object_sha256=receipt['object_sha256'],comparison_sha256=sha((folder/'comparison.json').read_bytes()),retained_comparison_sha256=sha((folder/'retained-comparison.json').read_bytes()),retained_request_sha256=sha((folder/'retained-check-request.json').read_bytes()))
  if synthetic_encoding:
   cert=compact['encoding_equivalence'];raw=json.dumps(cert,sort_keys=True,separators=(',',':')).encode();(folder/'encoding-equivalence.json').write_bytes(raw);result.update(status='encoding_equivalent',strict_status='mismatch',match_kind='encoding_equivalent',proof=False,encoding_equivalence=cert,encoding_equivalence_sha256=sha(raw),retained_check=compact)
  self.store_result(first['job_id'],folder,result)
  return first,folder,result,retained
 def store_result(self,job,folder,result):
  (folder/'result.json').write_text(json.dumps(result))
  with closing(sqlite3.connect(self.root/'state/jobs.sqlite3')) as db,db:
   db.execute("UPDATE jobs SET state='completed',result=? WHERE id=?",(json.dumps(result),job));db.execute('UPDATE replayable_frontier SET status=? WHERE job=?',(result['status'],job))
 def test_exact_cache_is_freshly_checked_and_file_status_forgery_refuses(self):
  first,folder,result,retained=self.seed_exact_cache();status=self.status();self.assertEqual((status['new_pipeline_full_matches'],status['new_pipeline_encoding_equivalent_matches'],status['new_pipeline_accepted_matches']),(1,0,1));self.assertEqual(status['first_unresolved_rva'],0x1030)
  forged=dict(result,status='encoding_equivalent');(folder/'result.json').write_text(json.dumps(forged));self.assertEqual(self.status()['new_pipeline_accepted_matches'],0)
  self.store_result(first['job_id'],folder,result);(folder/'retained-check-request.json').write_text('{}');self.assertEqual(self.status()['new_pipeline_accepted_matches'],0)
 def test_rebound_wrong_object_cannot_forge_exact_or_equivalent_mode(self):
  first,folder,result,retained=self.seed_exact_cache();build=folder/'build';(build/'candidate.obj').write_bytes(coff(bytes.fromhex('b82b000000c3'),comdat=True));receipt=json.loads((build/'run.json').read_text());receipt['object_sha256']=sha((build/'candidate.obj').read_bytes());(build/'run.json').write_text(json.dumps(receipt));retained['inputs'][str(build/'candidate.obj')]=receipt['object_sha256'];retained['inputs'][str(build/'run.json')]=sha((build/'run.json').read_bytes());(folder/'retained-check-request.json').write_text(json.dumps(retained));result.update(object_sha256=receipt['object_sha256'],retained_request_sha256=sha((folder/'retained-check-request.json').read_bytes()));self.store_result(first['job_id'],folder,result);self.assertEqual(self.status()['new_pipeline_accepted_matches'],0)
  result.update(status='encoding_equivalent',encoding_equivalence={'status':'encoding_equivalent','proof':True});raw=json.dumps(result['encoding_equivalence']).encode();(folder/'encoding-equivalence.json').write_bytes(raw);result['encoding_equivalence_sha256']=sha(raw);self.store_result(first['job_id'],folder,result);self.assertEqual(self.status()['new_pipeline_accepted_matches'],0)

 def test_synthetic_encoding_cache_is_separate_and_never_trusts_proof_files(self):
  first,folder,result,retained=self.seed_exact_cache(synthetic_encoding=True);state=self.status();self.assertEqual((state['new_pipeline_full_matches'],state['new_pipeline_encoding_equivalent_matches'],state['new_pipeline_accepted_matches']),(0,1,1));self.assertEqual(state['first_unresolved_rva'],0x1030)
  self.client=self.connect();self.assertEqual(self.status()['new_pipeline_encoding_equivalent_matches'],1)
  next_job=self.submit('next-after-equivalent');self.assertEqual(next_job['rva'],0x1030);stdio.wait_job(self.client,next_job['job_id']);self.assertEqual(self.submit('next-after-equivalent')['job_id'],next_job['job_id'])
  for field in ('strict_status','match_kind','proof','retained_check','encoding_equivalence','encoding_equivalence_sha256'):
   changed=copy.deepcopy(result);changed.pop(field);self.store_result(first['job_id'],folder,changed);self.assertEqual(self.status()['new_pipeline_accepted_matches'],0,field)
  changed=copy.deepcopy(result);changed['proof']=True;self.store_result(first['job_id'],folder,changed);self.assertEqual(self.status()['new_pipeline_accepted_matches'],0)
  # Even a rebound/forged diagnostic whose hash matches is re-derived from the
  # actual bound instruction bytes and fake frontend; it is not a trust input.
  changed=copy.deepcopy(result);changed['encoding_equivalence']['affine_certificate']['constant']=8;changed['retained_check']['encoding_equivalence']=changed['encoding_equivalence'];raw=json.dumps(changed['encoding_equivalence']).encode();(folder/'encoding-equivalence.json').write_bytes(raw);changed['encoding_equivalence_sha256']=sha(raw);self.store_result(first['job_id'],folder,changed);self.assertEqual(self.status()['new_pipeline_accepted_matches'],0)

 def check_tracking_mode_binding(self,synthetic_encoding):
  first,folder,result,retained=self.seed_exact_cache(synthetic_encoding=synthetic_encoding);expected=result['status'];wrong='full_match' if synthetic_encoding else 'encoding_equivalent';state=self.status();key=state['pipeline_key'];self.assertEqual(state['new_pipeline_accepted_matches'],1)
  with closing(sqlite3.connect(self.root/'state/jobs.sqlite3')) as db,db:db.execute('UPDATE replayable_frontier SET status=? WHERE job=?',(wrong,first['job_id']))
  state=self.status();self.assertEqual((state['new_pipeline_full_matches'],state['new_pipeline_encoding_equivalent_matches'],state['new_pipeline_accepted_matches']),(0,0,0));self.assertEqual(state['first_unresolved_rva'],0x1000)
  with closing(sqlite3.connect(self.root/'state/jobs.sqlite3')) as db,db:db.execute('UPDATE replayable_frontier SET input_key=? WHERE job=?',('regression:'+key,first['job_id']))
  state=self.status();self.assertEqual((state['regression_full_matches'],state['regression_encoding_equivalent_matches'],state['regression_accepted_matches']),(0,0,0))
  with closing(sqlite3.connect(self.root/'state/jobs.sqlite3')) as db,db:db.execute('UPDATE replayable_frontier SET status=? WHERE job=?',(expected,first['job_id']))
  state=self.status();self.assertEqual(state['regression_accepted_matches'],1);self.assertEqual(state['regression_encoding_equivalent_matches'],int(synthetic_encoding));self.assertEqual(state['regression_full_matches'],int(not synthetic_encoding))
  with closing(sqlite3.connect(self.root/'state/jobs.sqlite3')) as db,db:db.execute('UPDATE replayable_frontier SET input_key=?,status=? WHERE job=?',(key,wrong,first['job_id']))
  next_job=self.submit('tracking-kind-mismatch-remains-frontier');self.assertEqual(next_job['rva'],0x1000);stdio.wait_job(self.client,next_job['job_id'])
 def test_encoding_tracking_row_cannot_claim_exact_kind(self):self.check_tracking_mode_binding(True)
 def test_exact_tracking_row_cannot_claim_encoding_kind(self):self.check_tracking_mode_binding(False)

 def test_encoding_input_binding_change_starts_without_old_credit(self):
  first,folder,result,retained=self.seed_exact_cache(synthetic_encoding=True);before=self.status();self.assertEqual(before['new_pipeline_encoding_equivalent_matches'],1)
  self.dll.write_bytes(b'changed actual open frontend runtime')
  after=self.status();self.assertNotEqual(before['pipeline_key'],after['pipeline_key']);self.assertEqual(after['new_pipeline_accepted_matches'],0);self.assertEqual(after['first_unresolved_rva'],0x1000)

class EncodingBridgeTests(unittest.TestCase):
 setUp=pipeline.PipelineBoundaryTests.setUp
 tearDown=pipeline.PipelineBoundaryTests.tearDown
 connect=pipeline.PipelineBoundaryTests.connect
 def bound(self):
  from tools.replayable.encoding_check import attested_lifter
  project=json.loads(self.config.read_text())['projects'][0];paths=[self.root/'lifter.json',self.root/'manifest.json',self.dll];inputs={str(p):sha(p.read_bytes()) for p in paths};return attested_lifter,project,inputs
 def test_exact_runtime_attestation_and_missing_binding_refusal(self):
  from rapid_object.encoding_equivalence import Refusal
  attest,project,inputs=self.bound();callback,bindings=attest(project,inputs);self.assertTrue(callable(callback));self.assertEqual(bindings['adapter_sha256'],sha(self.dll.read_bytes()))
  for path in inputs:
   reduced=dict(inputs);reduced.pop(path)
   with self.subTest(path=path),self.assertRaisesRegex(Refusal,'unbound'):attest(project,reduced)
 def test_unexpected_runtime_file_or_wrong_revision_refuses(self):
  from rapid_object.encoding_equivalence import Refusal
  attest,project,inputs=self.bound();extra=self.dll.parent/'extra.dll';extra.write_bytes(b'unknown runtime');inputs[str(extra)]=sha(extra.read_bytes())
  with self.assertRaisesRegex(Refusal,'runtime_changed'):attest(project,inputs)
  extra.unlink();inputs.pop(str(extra));manifest=self.root/'manifest.json';value=json.loads(manifest.read_text());value['revision']='0'*40;manifest.write_text(json.dumps(value));inputs[str(manifest)]=sha(manifest.read_bytes())
  with self.assertRaisesRegex(Refusal,'revision_changed'):attest(project,inputs)
 def test_duplicate_stale_missing_or_failed_process_response_refuses(self):
  from rapid_object.encoding_equivalence import Refusal
  from unittest.mock import patch
  import subprocess
  attest,project,inputs=self.bound();callback,_=attest(project,inputs)
  payloads=[(0,''),(0,'{"id":"original"}\n'),(0,'{"id":"candidate"}\n{"id":"original"}\n'),(0,'{"id":"wrong","id":"original"}\n{"id":"candidate"}\n'),(1,'')]
  for code,text in payloads:
   with self.subTest(text=text),patch('tools.replayable.encoding_check.subprocess.run',return_value=subprocess.CompletedProcess([],code,text,'')),self.assertRaises(ValueError):callback(b'\x90',b'\x90',0x1000)

"""Open synthetic compiler receipts test publication plumbing, not native evidence."""
from contextlib import closing
import copy,hashlib,importlib.util,json,sqlite3,sys,unittest
from pathlib import Path
import test_replayable_pipeline as pipeline
from test_replayable_encoding import recipe
from test_replayable_ir import node,ty,reg,const,write,tmp,binary
from test_rapid_object_coff import pe,coff
stdio=pipeline.stdio;ROOT=pipeline.ROOT

def sha(raw):return hashlib.sha256(raw).hexdigest()
def template():
 bodies=[[node('IlStore',Addr=reg(1),Val=const(0x01020304))],[write(0,reg(1))],[node('IlLet',Id=0,Val=node('IlLoad',Addr=reg(4),Ty=ty(32))),write(4,binary('Add',reg(4),const(4,64))),node('IlBranch',Kind=dict(name='Ret'),Target=tmp(0,32),Cond=None)]]
 rows=[];pc=0
 for raw,body in zip(('c70104030201','8bc1','c3'),bodies):rows.append(dict(pc=pc,length=len(bytes.fromhex(raw)),raw_hex=raw,decoded=dict(P=dict(Lock=False,Rep=False,RepNz=False)),tree=node('IlBlock',Body=body)));pc+=len(bytes.fromhex(raw))
 return dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=rows)

@unittest.skipUnless(stdio.DLL.exists(),'build changed component first')
class SourceExportTests(unittest.TestCase):
 setUp=pipeline.PipelineBoundaryTests.setUp
 tearDown=pipeline.PipelineBoundaryTests.tearDown
 connect=pipeline.PipelineBoundaryTests.connect
 def seed(self):
  raw=bytes.fromhex('c701040302018bc1c3');binary=pe(raw+b'\0'*256);(self.root/'original.exe').write_bytes(binary);inv=json.loads((self.root/'inventory.json').read_text());inv['module_sha256']=sha(binary);inv['functions'][0].update(body_bytes=len(raw),body_ranges=[dict(start_rva=0x1000,end_rva_inclusive=0x1000+len(raw)-1)]);(self.root/'inventory.json').write_text(json.dumps(inv))
  script='import sys,json,copy\ntemplate='+repr(template())+'\nfor line in sys.stdin:\n req=json.loads(line);out=copy.deepcopy(template)\n for row in out["instructions"]:row["pc"]+=req["pc"]\n out["id"]=req["id"];print(json.dumps(out))\n';self.dll.write_text(script);m=json.loads((self.root/'manifest.json').read_text());m['assemblies_sha256']={self.dll.name:sha(self.dll.read_bytes())};(self.root/'manifest.json').write_text(json.dumps(m));cfg=json.loads((self.root/'lifter.json').read_text());cfg['dotnet']=sys.executable;(self.root/'lifter.json').write_text(json.dumps(cfg));registry=json.loads(self.config.read_text());p=registry['projects'][0];p.update(module_sha256=sha(binary),source_export_root=str(self.root/'publication'),compiler_flags=['/c','/O2','/Ob1','/Oy','/Gy','/Z7','/Zl','/GS','/GR-','/EHsc']);self.config.write_text(json.dumps(registry));self.client=self.connect();job=self.client.call('replayable_run_next',project_id='open',idempotency_key='open-generated-export-source',recipe_json=json.dumps(recipe()),compile=False);generated=stdio.wait_job(self.client,job['job_id']);self.assertEqual(generated['result']['status'],'generated',generated);folder=self.root/'attempts'/job['job_id'];request=json.loads((folder/'request.json').read_text());request['compile']=True;(folder/'request.json').write_text(json.dumps(request));source=(folder/'candidate.cpp').read_bytes();build=folder/'build';build.mkdir();(build/'candidate.cpp').write_bytes(source);(build/'candidate.obj').write_bytes(coff(raw,comdat=True));compiler=dict(sha256=p['compiler_sha256']);(build/'compiler.json').write_text(json.dumps(compiler));receipt=dict(exit_code=0,linked=False,original_executed=False,module_sha256=p['module_sha256'],source_sha256=sha(source),object_sha256=sha((build/'candidate.obj').read_bytes()),compiler=compiler,flags=p['compiler_flags']);(build/'run.json').write_text(json.dumps(receipt));(build/'build-exit.txt').write_text('0\n');sys.path.insert(0,str(ROOT/'tools/decompilation-mcp'));import replayable_adapter as adapter
  first=adapter.compare_built(request,folder,source.decode());inputs=dict(request['inputs']);inputs.update({str(build/n):sha((build/n).read_bytes()) for n in ('candidate.cpp','candidate.obj','compiler.json','run.json')});retained=dict(project=request['project'],build=dict(config=dict(folder=str(build),rva=0x1000,profile='ordinary',allow_encoding_equivalence=True),expected_source_sha256=sha(source)),inputs=inputs);(folder/'retained-check-request.json').write_text(json.dumps(retained));import adapter as independent
  second,report=independent.run(retained);self.assertEqual(second['status'],'full_match');(folder/'retained-comparison.json').write_text(json.dumps(report));result=dict(first,retained_check=second,retained_request_sha256=sha((folder/'retained-check-request.json').read_bytes()),retained_comparison_sha256=sha((folder/'retained-comparison.json').read_bytes()));self.store(job['job_id'],folder,request,result);return job['job_id'],folder,request,result
 def store(self,job,folder,request,result):
  (folder/'request.json').write_text(json.dumps(request));(folder/'result.json').write_text(json.dumps(result))
  with closing(sqlite3.connect(self.root/'state/jobs.sqlite3')) as db,db:db.execute("UPDATE jobs SET request=?,state='completed',result=? WHERE id=?",(json.dumps(request),json.dumps(result),job));db.execute('UPDATE replayable_frontier SET status=? WHERE job=?',(result['status'],job))
 def submit(self,jobs,token='export',revision=None,publication=None):
  info=self.client.call('project_open',project_id='open');return self.client.call('source_export',project_id='open',job_ids=jobs,expected_revision=revision or info['revision'],expected_publication_revision=publication or info['source_export']['revision'],idempotency_key=token)
 def test_exact_source_export_is_byte_equal_allowlisted_and_restart_idempotent(self):
  job,folder,req,result=self.seed();info=self.client.call('project_open',project_id='open');submitted=self.submit([job]);done=stdio.wait_job(self.client,submitted['job_id']);self.assertEqual(done['result']['status'],'source_exported',done);index=json.loads((self.root/'publication/index.json').read_text());row=index['functions'][0];self.assertEqual((self.root/'publication'/row['source']).read_bytes(),(folder/'candidate.cpp').read_bytes());self.assertEqual(row['accepted_kind'],'full_match');self.assertFalse(row['linked']);public=json.dumps(index);self.assertNotIn(str(self.root),public);self.assertNotIn('original_bytes',public);self.assertNotIn('instructions',public);self.assertEqual({p.suffix for p in (self.root/'publication').rglob('*') if p.is_file()},{'.cpp','.json','.md'});self.client=self.connect();again=self.client.call('source_export',project_id='open',job_ids=[job],expected_revision=info['revision'],expected_publication_revision='empty',idempotency_key='export');self.assertEqual(again['job_id'],submitted['job_id']);self.assertTrue(again['reused'])
 def test_rejects_stale_revisions_bad_ids_nonmatching_and_unknown_jobs(self):
  job,folder,req,result=self.seed()
  for args in (([job],dict(revision='0'*64)),([job],dict(publication='0'*64)),([job,job],{}),(['../escape'],{}),(['f'*32],{})):
   with self.subTest(args=args),self.assertRaises(ValueError):self.submit(args[0],token='bad'+str(args),**args[1])
  for status in ('mismatch','inconclusive','external_outcome_unknown','abi_trace_equivalent'):
   changed=dict(result,status=status);self.store(job,folder,req,changed)
   with self.assertRaises(ValueError):self.submit([job],token=status)
 def test_source_object_receipt_and_report_tampering_never_publishes(self):
  job,folder,req,result=self.seed()
  for name in ('candidate.cpp','build/candidate.obj','build/run.json','comparison.json','retained-comparison.json','retained-check-request.json'):
   path=folder/name;raw=path.read_bytes();path.write_bytes(raw+b' ');submitted=self.submit([job],token='tamper-'+name);done=stdio.wait_job(self.client,submitted['job_id']);self.assertEqual(done['result']['status'],'inconclusive',done);self.assertFalse((self.root/'publication/index.json').exists());path.write_bytes(raw)
 def test_rebound_wrong_object_cannot_use_a_saved_full_match(self):
  job,folder,req,result=self.seed();obj=coff(bytes.fromhex('c701050302018bc1c3'),comdat=True);(folder/'build/candidate.obj').write_bytes(obj);receipt=json.loads((folder/'build/run.json').read_text());receipt['object_sha256']=sha(obj);(folder/'build/run.json').write_text(json.dumps(receipt));saved=json.loads((folder/'retained-check-request.json').read_text());saved['inputs'].update({str(folder/'build'/n):sha((folder/'build'/n).read_bytes()) for n in ('candidate.obj','run.json')});(folder/'retained-check-request.json').write_text(json.dumps(saved));changed=dict(result,object_sha256=sha(obj),build=receipt,retained_request_sha256=sha((folder/'retained-check-request.json').read_bytes()));self.store(job,folder,req,changed);done=stdio.wait_job(self.client,self.submit([job])['job_id']);self.assertEqual(done['result']['status'],'inconclusive');self.assertFalse((self.root/'publication/index.json').exists())
 def test_batch_classification_is_durable_even_without_optional_result_metadata(self):
  job,folder,req,result=self.seed();parent='a'*32;req.update(group_parent=parent,job_id=job);self.store(job,folder,req,result);member=dict(job_id=job,rva=0x1000,function_id=sha((req['project']['module_sha256']+':4096').encode()));parent_req=dict(operation='replayable_batch',group_id=parent,project=req['project'],recipe=req['recipe'],inputs=req['inputs'],members=[member]);parent_result=dict(status='batch_completed',members=[dict(member,status='full_match')])
  with closing(sqlite3.connect(self.root/'state/jobs.sqlite3')) as db,db:db.execute("INSERT INTO jobs(id,project,token,request,state,created,result) VALUES(?,?,?,?,'completed','2026-01-01T00:00:00Z',?)",(parent,'open','open-parent',json.dumps(parent_req),json.dumps(parent_result)))
  done=stdio.wait_job(self.client,self.submit([job])['job_id']);self.assertEqual(done['result']['status'],'inconclusive');self.assertFalse((self.root/'publication/index.json').exists())
  with closing(sqlite3.connect(self.root/'state/jobs.sqlite3')) as db,db:db.execute("UPDATE jobs SET state='interrupted_unknown' WHERE id=?",(parent,))
  with self.assertRaises(ValueError):self.submit([job],token='unknown-parent')
 def test_concurrent_same_token_reuses_one_durable_export(self):
  from concurrent.futures import ThreadPoolExecutor
  job,folder,req,result=self.seed();other=self.connect();info=self.client.call('project_open',project_id='open');kwargs=dict(project_id='open',job_ids=[job],expected_revision=info['revision'],expected_publication_revision='empty',idempotency_key='concurrent')
  with ThreadPoolExecutor(2) as pool:answers=list(pool.map(lambda c:c.call('source_export',**kwargs),(self.client,other)))
  self.assertEqual(answers[0]['job_id'],answers[1]['job_id']);done=stdio.wait_job(self.client,answers[0]['job_id']);self.assertEqual(done['result']['status'],'source_exported',done)
 def test_false_boolean_exit_receipt_and_proof_claim_are_not_accepted(self):
  job,folder,req,result=self.seed();receipt=json.loads((folder/'build/run.json').read_text());receipt['exit_code']=False;(folder/'build/run.json').write_text(json.dumps(receipt));saved=json.loads((folder/'retained-check-request.json').read_text());saved['inputs'][str(folder/'build/run.json')]=sha((folder/'build/run.json').read_bytes());(folder/'retained-check-request.json').write_text(json.dumps(saved));changed=dict(result,build=receipt,retained_request_sha256=sha((folder/'retained-check-request.json').read_bytes()));self.store(job,folder,req,changed);done=stdio.wait_job(self.client,self.submit([job])['job_id']);self.assertEqual(done['result']['status'],'inconclusive');self.assertFalse((self.root/'publication/index.json').exists())
  receipt['exit_code']=0;(folder/'build/run.json').write_text(json.dumps(receipt));saved['inputs'][str(folder/'build/run.json')]=sha((folder/'build/run.json').read_bytes());(folder/'retained-check-request.json').write_text(json.dumps(saved));changed.update(build=receipt,proof=True,retained_request_sha256=sha((folder/'retained-check-request.json').read_bytes()));self.store(job,folder,req,changed);again=stdio.wait_job(self.client,self.submit([job],token='false-proof-claim')['job_id']);self.assertEqual(again['result']['status'],'inconclusive')
 def test_compiled_source_binding_cannot_be_replaced_by_arbitrary_source(self):
  job,folder,req,result=self.seed();source=(folder/'candidate.cpp').read_bytes()+b'\n// changed source\n';(folder/'candidate.cpp').write_bytes(source);(folder/'build/candidate.cpp').write_bytes(source);changed=dict(result,source_sha256=sha(source));self.store(job,folder,req,changed);submitted=self.submit([job]);done=stdio.wait_job(self.client,submitted['job_id']);self.assertEqual(done['result']['status'],'inconclusive');self.assertFalse((self.root/'publication/index.json').exists())
 def test_unknown_barrier_survives_new_export_mode(self):
  job,folder,req,result=self.seed()
  for state in ('running','external_outcome_unknown'):
   with closing(sqlite3.connect(self.root/'state/jobs.sqlite3')) as db,db:db.execute('UPDATE replayable_frontier SET status=?',(state,))
   with self.assertRaises(ValueError):self.submit([job],token='barrier-'+state)
 def test_registered_historical_source_tree_cannot_contain_export_namespace(self):
  job,folder,req,result=self.seed();historical=self.root/'historical';historical.mkdir();index=historical/'index.json';raw=json.dumps(dict(module_sha256=req['project']['module_sha256'],functions=[]));index.write_text(raw);config=json.loads(self.config.read_text());config['projects'][0].update(published_index=str(index),source_export_root=str(historical/'nested'));self.config.write_text(json.dumps(config));self.client=self.connect()
  with self.assertRaises(ValueError):self.client.call('project_open',project_id='open')
  self.assertEqual(index.read_text(),raw);self.assertFalse((historical/'nested').exists())
 def test_symlink_output_and_historical_namespace_are_not_overwritten(self):
  job,folder,req,result=self.seed();target=self.root/'other';target.mkdir();(self.root/'publication').symlink_to(target,target_is_directory=True)
  with self.assertRaises(ValueError):self.submit([job])
  (self.root/'publication').unlink();(self.root/'publication').mkdir();(self.root/'publication/index.json').write_text(json.dumps(dict(schema='old-historical-export',module_sha256=req['project']['module_sha256'])))
  with self.assertRaises(ValueError):self.submit([job])
 def test_published_mode_is_bound_to_durable_export_revision(self):
  job,folder,req,result=self.seed();out=stdio.wait_job(self.client,self.submit([job])['job_id']);self.assertEqual(out['result']['status'],'source_exported');path=self.root/'publication/index.json';index=json.loads(path.read_text());index['functions'][0]['accepted_kind']='encoding_equivalent';index['counts']={'encoding_equivalent':1};path.write_text(json.dumps(index))
  with self.assertRaises(ValueError):self.client.call('project_open',project_id='open')
 def test_interrupted_publication_state_cannot_be_reconciled_by_read_or_restart(self):
  job,folder,req,result=self.seed();out=stdio.wait_job(self.client,self.submit([job])['job_id']);self.assertEqual(out['result']['status'],'source_exported')
  with closing(sqlite3.connect(self.root/'state/jobs.sqlite3')) as db,db:db.execute("UPDATE jobs SET state='interrupted_unknown' WHERE id=?",(out['job_id'],))
  self.client=self.connect()
  with self.assertRaises(ValueError):self.client.call('project_open',project_id='open')
 def test_worker_refuses_changed_executor_registration(self):
  import uuid,subprocess
  job,folder,req,result=self.seed();out=stdio.wait_job(self.client,self.submit([job])['job_id']);self.assertEqual(out['result']['status'],'source_exported');index=(self.root/'publication/index.json').read_bytes();new_id=uuid.uuid4().hex
  with closing(sqlite3.connect(self.root/'state/jobs.sqlite3')) as db,db:
   original=db.execute('SELECT request FROM jobs WHERE id=?',(out['job_id'],)).fetchone()[0];db.execute("INSERT INTO jobs(id,project,token,request,state,created) VALUES(?,?,?,?,'queued','2026-01-01T00:00:00Z')",(new_id,'open','open-executor-tamper',original))
  changed=json.loads(self.config.read_text());changed['adapter_root']=str(self.root/'different-executor');config=self.root/'changed-executor.json';config.write_text(json.dumps(changed));subprocess.run(['/usr/local/share/dotnet/dotnet',str(stdio.DLL),'worker','--config',str(config),'--job',new_id],check=True,capture_output=True);done=self.client.call('job_get',job_id=new_id);self.assertEqual(done['result']['blocker'],'source_export_executor_changed');self.assertEqual((self.root/'publication/index.json').read_bytes(),index)
 def test_explicit_snapshot_and_public_source_integrity(self):
  job,folder,req,result=self.seed();out=stdio.wait_job(self.client,self.submit([job])['job_id']);self.assertEqual(out['result']['status'],'source_exported',out);index=json.loads((self.root/'publication/index.json').read_text());path=self.root/'publication'/index['functions'][0]['source'];path.write_bytes(path.read_bytes()+b'\nchanged')
  with self.assertRaises(ValueError):self.client.call('project_open',project_id='open')

class SourceExportProgressTests(unittest.TestCase):
 def test_historical_input_dot_components_cannot_escape_registered_read_root(self):
  import tempfile
  from tools.replayable.source_export import read
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp).resolve();allowed=root/'allowed';allowed.mkdir();outside=root/'outside';outside.write_text('open fixture only');inside=allowed/'inside';inside.write_text('inside');project=dict(allowed_roots=[str(allowed)])
   with self.assertRaisesRegex(ValueError,'outside_roots'):read(project,allowed/'..'/'outside')
   self.assertEqual(read(project,allowed/'.'/'inside'),b'inside')
 def fixture(self):
  from tools import update_progress
  raw=b'// Open synthetic source snapshot\n';module='a'*64;job='b'*32;source=f'exports/{job}/units/00001000-{sha(raw)[:16]}.cpp';row=dict(rva=0x1000,function_id=sha((module+':4096').encode()),source=source,source_sha256=sha(raw),accepted_kind='full_match',linked=False,proof=False,game_execution=False,complete_required_ranges=True);index=dict(schema='replayable-source-publication-v1',module_sha256=module,export_job_id=job,proof=False,counts={'full_match':1},functions=[row]);data={'src/native/replayable/index.json':json.dumps(index).encode(),'src/native/replayable/'+source:raw}
  class Snapshot:
   def exists(self,name):return name in data
   def read(self,name):return data[name]
  return update_progress,Snapshot(),data,index,module
 def test_separate_export_counts_check_source_hash_and_identity(self):
  updater,snapshot,data,index,module=self.fixture();self.assertEqual(updater.replayable_exports(snapshot,module),{'full_match':1,'encoding_equivalent':0});data.clear();self.assertIsNone(updater.replayable_exports(snapshot,module))
 def test_tampered_publication_cannot_inflate_progress(self):
  for mutation in ('mode','module','counts','traversal','duplicate','rva_bool','function_id','linked','hash','job'):
   updater,snapshot,data,index,module=self.fixture();row=index['functions'][0]
   if mutation=='mode':row['accepted_kind']='abi_trace_equivalent'
   elif mutation=='module':index['module_sha256']='c'*64
   elif mutation=='counts':index['counts']['full_match']=True
   elif mutation=='traversal':row['source']='../private.cpp'
   elif mutation=='duplicate':index['functions'].append(copy.deepcopy(row))
   elif mutation=='rva_bool':row['rva']=True
   elif mutation=='function_id':row['function_id']='f'*64
   elif mutation=='linked':row['linked']=True
   elif mutation=='hash':data['src/native/replayable/'+row['source']]+=b'changed'
   else:index['export_job_id']='c'*32
   data['src/native/replayable/index.json']=json.dumps(index).encode()
   with self.subTest(mutation=mutation),self.assertRaises(ValueError):updater.replayable_exports(snapshot,module)

 def test_behavioral_progress_requires_separate_policy_and_certificate_hash(self):
  updater,snapshot,data,index,module=self.fixture();row=index['functions'][0];row.update(accepted_kind='behaviorally_equivalent',observation_policy='windows-x86-inherited-unwind-ordered-events-v1',behavioral_certificate_sha256='e'*64);index['counts']={'behaviorally_equivalent':1};data['src/native/replayable/index.json']=json.dumps(index).encode();self.assertEqual(updater.replayable_exports(snapshot,module),{'full_match':0,'encoding_equivalent':0,'behaviorally_equivalent':1})
  for key in ('observation_policy','behavioral_certificate_sha256'):
   changed=copy.deepcopy(index);changed['functions'][0].pop(key);data['src/native/replayable/index.json']=json.dumps(changed).encode()
   with self.assertRaises(ValueError):updater.replayable_exports(snapshot,module)

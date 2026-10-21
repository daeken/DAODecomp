"""Saved-analysis plumbing with open synthetic typed input; no compiler or VM."""
from contextlib import closing
import copy,hashlib,json,sqlite3,sys,unittest
from pathlib import Path
import test_replayable_pipeline as pipeline
from test_replayable_bare_return import fixture
from test_rapid_object_coff import pe
from tools.replayable import typed_cache as cache
stdio=pipeline.stdio; ROOT=pipeline.ROOT
sha=lambda b:hashlib.sha256(b).hexdigest()

@unittest.skipUnless(stdio.DLL.exists(),'build changed component first')
class TypedAnalysisTests(unittest.TestCase):
 setUp=pipeline.PipelineBoundaryTests.setUp
 tearDown=pipeline.PipelineBoundaryTests.tearDown
 connect=pipeline.PipelineBoundaryTests.connect
 def seed(self):
  binary=pe(b'\xc3'+b'\0'*256);(self.root/'original.exe').write_bytes(binary);inv=json.loads((self.root/'inventory.json').read_text());inv['module_sha256']=sha(binary);(self.root/'inventory.json').write_text(json.dumps(inv))
  lift=fixture()['lift'];lift.update(schema=cache.LINEAR,byte_length=1,decoded_bytes=1,pc=0);lift['instructions'][0].update(pc=0,offset=0,opaque_markers=[],lift_error=None)
  marker=self.root/'lift-calls.txt';script='import sys,json,copy\nfrom pathlib import Path\ntemplate='+repr(lift)+'\nfor line in sys.stdin:\n req=json.loads(line);out=copy.deepcopy(template);out["pc"]=req["pc"];out["id"]=req["id"];out["instructions"][0]["pc"]=req["pc"]\n with Path('+repr(str(marker))+').open("a") as f:f.write("lift\\n")\n print(json.dumps(out))\n';self.dll.write_text(script)
  m=json.loads((self.root/'manifest.json').read_text());m['assemblies_sha256']={self.dll.name:sha(self.dll.read_bytes())};(self.root/'manifest.json').write_text(json.dumps(m));cfg=json.loads((self.root/'lifter.json').read_text());cfg['dotnet']=sys.executable;(self.root/'lifter.json').write_text(json.dumps(cfg));reg=json.loads(self.config.read_text());reg['projects'][0]['module_sha256']=sha(binary);self.config.write_text(json.dumps(reg));self.client=self.connect();self.fid=sha((sha(binary)+':4096').encode())
  job=self.client.call('replayable_regression_check',project_id='open',function_id=self.fid,idempotency_key='populate',compile=False);done=stdio.wait_job(self.client,job['job_id']);self.assertEqual(done['result']['status'],'generated',done);folder=self.root/'attempts'/job['job_id'];receipt=json.loads((folder/'typed-analysis-index.json').read_text());self.assertEqual(receipt['status'],'indexed',receipt);self.request=json.loads((folder/'request.json').read_text());self.folder=folder
  with closing(sqlite3.connect(self.root/'state/jobs.sqlite3')) as db:self.record=json.loads(db.execute('SELECT record FROM replayable_typed_lifts').fetchone()[0])
 def replay(self):return self.client.call('replayable_analysis_replay',project_id='open',function_ids=[self.fid])
 def replace(self,record,rehash=True):
  if rehash:record['record_id']=cache.digest({k:v for k,v in record.items() if k!='record_id'})
  with closing(sqlite3.connect(self.root/'state/jobs.sqlite3')) as db,db:db.execute('UPDATE replayable_typed_lifts SET record=?',(json.dumps(record),))
 def test_population_and_replay_persist_without_lift_compiler_or_credit(self):
  self.seed();before=(self.root/'lift-calls.txt').read_bytes();self.client=self.connect();out=self.replay();self.assertEqual(out['records'][0]['status'],'source_proposal',out);self.assertFalse(out['acceptance_credit']);self.assertEqual(out['new_lifts'],0);self.assertEqual(out['compiler_invocations'],0);self.assertEqual(out['acceptance_checks'],0);self.assertEqual((self.root/'lift-calls.txt').read_bytes(),before);self.assertFalse(list(self.root.rglob('candidate.obj')));self.assertEqual(self.client.call('replayable_status',project_id='open')['new_pipeline_full_matches'],0)
  report=self.root/'attempts/analysis-replay'/out['report_id']/'report.json';self.assertEqual(sha(report.read_bytes()),out['report_sha256']);self.assertEqual(json.loads(report.read_text())['records'][0]['proposal']['ir']['return'],dict(kind='register_input',index=0))
  again=self.client.call('replayable_regression_check',project_id='open',function_id=self.fid,idempotency_key='populate-again',compile=False);stdio.wait_job(self.client,again['job_id'])
  with closing(sqlite3.connect(self.root/'state/jobs.sqlite3')) as db:self.assertEqual(db.execute('SELECT count(*) FROM replayable_typed_lifts').fetchone()[0],1)
 def test_missing_and_explicit_identity_bounds(self):
  self.seed();missing=sha((self.record['binding']['module_sha256']+':4144').encode());out=self.client.call('replayable_analysis_replay',project_id='open',function_ids=[missing]);self.assertEqual(out['records'][0]['status'],'missing')
  for ids in ([],[self.fid]*2,['x'],[self.fid]*17):
   with self.assertRaises(ValueError):self.client.call('replayable_analysis_replay',project_id='open',function_ids=ids)
 def test_record_and_payload_hash_tampering_refuse(self):
  self.seed()
  for mode in ('record','payload'):
   x=copy.deepcopy(self.record)
   if mode=='record':x['status']='invented'
   else:x['payload']['lift']['instructions'][0]['tree']['extra']='changed'
   self.replace(x,rehash=mode=='payload');out=self.replay();self.assertEqual(out['records'][0]['versions'][0]['status'],'invalid',out);self.assertNotEqual(out['records'][0]['status'],'source_proposal')
 def test_rebound_wrong_identity_schema_bytes_and_origins_refuse(self):
  self.seed()
  for mode in ('identity','schema','bytes','origin','record_schema'):
   x=copy.deepcopy(self.record);p=x['payload']['lift']
   if mode=='identity':p['id']='wrong:4096'
   elif mode=='schema':p['schema']='future'
   elif mode=='bytes':p['instructions'][0]['raw_hex']='90'
   elif mode=='origin':p['instructions'][0]['pc']+=1
   else:x['schema']='future'
   x['payload_sha256']=cache.digest(x['payload']);self.replace(x);out=self.replay();self.assertEqual(out['records'][0]['versions'][0]['status'],'invalid',out)
 def test_stale_ranges_producer_and_legacy_lifter_are_not_replayed(self):
  self.seed()
  for mode in ('ranges','producer','lifter'):
   x=copy.deepcopy(self.record)
   if mode=='ranges':x['binding']['ownership'][0]['end_rva_inclusive']+=1
   elif mode=='producer':x['binding']['producer']['config']='0'*64
   else:x['binding']['lifter_manifest_sha256']='0'*64
   self.replace(x);out=self.replay();self.assertEqual(out['records'][0]['versions'][0]['status'],'legacy_lifter' if mode=='lifter' else 'stale_inputs_or_ranges');self.assertNotEqual(out['records'][0]['status'],'source_proposal')
 def test_incomplete_failed_unknown_records_remain_explicit(self):
  self.seed()
  for status in ('incomplete','failed','unknown'):
   payload=copy.deepcopy(self.record['payload'])
   if status=='incomplete':payload['lift']['opaque_instructions']=1
   else:payload=dict(error='synthetic failure',status='external_outcome_unknown' if status=='unknown' else 'inconclusive')
   x=cache.pack(self.request,payload);self.replace(x);out=self.replay();self.assertEqual(out['records'][0]['versions'][0]['status'],status);self.assertNotEqual(out['records'][0]['status'],'source_proposal')
 def test_valid_cache_unsupported_typed_effect_is_not_dropped(self):
  self.seed();x=copy.deepcopy(self.record);x['payload']['lift']['instructions'][0]['tree']['Body'][-1]['Target']={'type':'LiftIl.IlConst','Bits':{'decimal':'0'},'Ty':{'type':'LiftIl.IlType+I','Bits':32,'Signed':False}};x['payload_sha256']=cache.digest(x['payload']);self.replace(x);out=self.replay();self.assertEqual(out['records'][0]['status'],'unsupported',out)
 def test_multiple_current_payloads_refuse_ambiguous_replay(self):
  self.seed();x=copy.deepcopy(self.record);x['payload']['scope']='second retained payload';x['payload_sha256']=cache.digest(x['payload']);x['record_id']=cache.digest({k:v for k,v in x.items()if k!='record_id'})
  with closing(sqlite3.connect(self.root/'state/jobs.sqlite3')) as db,db:db.execute("INSERT INTO replayable_typed_lifts SELECT project,module_sha256,rva,?, ?,first_origin,created FROM replayable_typed_lifts",(x['record_id'],json.dumps(x)))
  self.assertEqual(self.replay()['records'][0]['status'],'ambiguous_current_records')

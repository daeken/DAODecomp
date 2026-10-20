"""Durable batch claims on open invalid binaries; no compiler or game acceptance."""
import concurrent.futures
from contextlib import closing
import hashlib,json,sqlite3,time,unittest
import test_replayable_pipeline as pipeline
stdio=pipeline.stdio

@unittest.skipUnless(stdio.DLL.exists(),'build C# component first')
class BatchPipelineTests(unittest.TestCase):
 setUp=pipeline.PipelineBoundaryTests.setUp
 tearDown=pipeline.PipelineBoundaryTests.tearDown
 connect=pipeline.PipelineBoundaryTests.connect
 def ids(self,*rvas):return [hashlib.sha256((json.loads((self.root/'inventory.json').read_text())['module_sha256']+':'+str(r)).encode()).hexdigest() for r in (rvas or (0x1000,0x1030))]
 def configure_transport(self):
  p=json.loads(self.config.read_text());profile=self.root/'transport.json';profile.write_text(json.dumps({'protocol':'prlctl-sync-copy-v1'}));p['projects'][0]['compiler_flags']=['/c','/O2','/Ob1','/Oy','/Gy','/Z7','/Zl','/GS','/GR-','/EHsc'];p['projects'][0]['replayable']['transport_config']=str(profile);self.config.write_text(json.dumps(p));self.client=self.connect()
 def submit(self,token='batch',ids=None,**kw):
  return self.client.call('replayable_regression_batch',project_id='open',function_ids=self.ids() if ids is None else ids,idempotency_key=token,**kw)
 def db(self):return closing(sqlite3.connect(self.root/'state/jobs.sqlite3'))
 def test_invalid_identity_size_duplicates_and_expected_bindings_refuse(self):
  self.configure_transport()
  for ids in ([],self.ids()*9,[self.ids()[0]]*2,['unknown']):
   with self.assertRaises(ValueError):self.submit(ids=ids)
  for expected in ('[]','{"unknown":"'+'a'*64+'"}','{"'+self.ids()[0]+'":"ABC"}'):
   with self.assertRaises(ValueError):self.submit(expected_sources_json=expected)
 def test_generation_failures_retained_and_recovery_selector_not_advanced(self):
  self.configure_transport();j=self.submit();out=stdio.wait_job(self.client,j['job_id']);self.assertEqual(out['result']['status'],'batch_completed',out);self.assertEqual(out['result']['outcomes'],{'inconclusive':2})
  self.assertFalse(j['ascending_frontier'])
  for child in j['members']:
   c=self.client.call('job_get',job_id=child['job_id']);self.assertEqual(c['state'],'completed');self.assertEqual(c['result']['status'],'inconclusive');self.assertFalse(c['result']['compiler_dispatched'])
  status=self.client.call('replayable_status',project_id='open');self.assertEqual((status['first_unresolved_rva'],status['new_pipeline_full_matches'],status['regression_full_matches']),(0x1000,0,0))
 def test_idempotency_survives_restart_and_changed_request_refuses(self):
  self.configure_transport();first=self.submit();stdio.wait_job(self.client,first['job_id']);self.client=self.connect();self.assertEqual(self.submit()['job_id'],first['job_id'])
  for extra in (dict(ids=list(reversed(self.ids()))),dict(expected_sources_json=json.dumps({self.ids()[0]:'a'*64}))):
   with self.assertRaises(ValueError):self.submit(**extra)
  self.dll.write_bytes(b'changed lifter input binding')
  with self.assertRaises(ValueError):self.submit()
  changed=self.submit('changed-key');self.assertNotEqual(changed['job_id'],first['job_id']);stdio.wait_job(self.client,changed['job_id'])
 def test_concurrent_same_token_claims_one_parent_and_member_set(self):
  self.configure_transport();other=self.connect()
  def call(c):return c.call('replayable_regression_batch',project_id='open',function_ids=self.ids(),idempotency_key='simultaneous')
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(call,(self.client,other)))
  self.assertEqual(results[0]['job_id'],results[1]['job_id']);stdio.wait_job(self.client,results[0]['job_id'])
  with self.db() as d:self.assertEqual(d.execute('select count(*) from jobs').fetchone()[0],3)
 def test_cross_version_and_mode_uncertainty_barriers(self):
  self.configure_transport()
  for state in ('running','external_outcome_unknown'):
   with self.db() as d:
    d.execute('CREATE TABLE IF NOT EXISTS replayable_frontier(project TEXT,input_key TEXT,rva INTEGER,status TEXT,job TEXT,PRIMARY KEY(project,input_key,rva))');d.execute('INSERT OR REPLACE INTO replayable_frontier VALUES(?,?,?,?,?)',('open','foreign-runtime-key',0x1000,state,'f'*32));d.commit()
   self.dll.write_bytes(('different-key-'+state).encode())
   with self.assertRaises(ValueError):self.submit('blocked-'+state)
   with self.assertRaises(ValueError):self.client.call('replayable_run_next',project_id='open',idempotency_key='single-'+state,compile=False)
   with self.db() as d:d.execute('DELETE FROM replayable_frontier WHERE input_key=?',('foreign-runtime-key',));d.commit()
 def test_batch_cache_requires_member_and_whole_envelope_provenance(self):
  # Controlled persistence-only fixture, never an original object comparison.
  self.configure_transport();j=self.submit('cache-fixture');stdio.wait_job(self.client,j['job_id']);child=j['members'][0];folder=self.root/'attempts'/child['job_id'];(folder/'build').mkdir();batch=self.root/'attempts'/j['job_id']/'batch';batch.mkdir()
  sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
  paths={'source_sha256':folder/'candidate.cpp','object_sha256':folder/'build/candidate.obj','comparison_sha256':folder/'comparison.json'}
  for path in paths.values():path.write_bytes(b'open cache fixture')
  provenance={}
  for name in ('run.json','compiler.json','start.json','exit.json','build-exit.txt'):
   path=folder/'build'/name;path.write_text('{}');provenance['build/'+name]=sha(path)
  binding={'group_id':j['job_id']}
  for name,key in (('manifest.json','manifest_sha256'),('completed.json','envelope_sha256'),('dispatch-start.json','dispatch_sha256')):
   path=batch/name;path.write_text('{}');binding[key]=sha(path)
  result=dict(status='full_match',group_job_id=j['job_id'],batch_provenance=provenance,build={'batch':binding},**{key:sha(path) for key,path in paths.items()})
  (folder/'result.json').write_text(json.dumps(result))
  with self.db() as d:d.execute("UPDATE replayable_frontier SET status='full_match' WHERE job=?",(child['job_id'],));d.commit()
  self.assertEqual(self.client.call('replayable_status',project_id='open')['regression_full_matches'],1)
  for path in [folder/name for name in provenance]+list(batch.iterdir()):
   original=path.read_bytes();path.write_bytes(b'changed');self.assertEqual(self.client.call('replayable_status',project_id='open')['regression_full_matches'],0);path.write_bytes(original)
  for key in ('batch_provenance','group_job_id','build'):
   saved=result.pop(key);(folder/'result.json').write_text(json.dumps(result));self.assertEqual(self.client.call('replayable_status',project_id='open')['regression_full_matches'],0);result[key]=saved
  saved=result['build'].pop('batch');(folder/'result.json').write_text(json.dumps(result));self.assertEqual(self.client.call('replayable_status',project_id='open')['regression_full_matches'],0);result['build']['batch']=saved
  saved=result.pop('batch_provenance');original=(batch/'completed.json').read_bytes();(batch/'completed.json').write_text('corrupted parent envelope');(folder/'result.json').write_text(json.dumps(result));self.assertEqual(self.client.call('replayable_status',project_id='open')['regression_full_matches'],0);(batch/'completed.json').write_bytes(original);result['batch_provenance']=saved
  result['group_job_id']='0'*32;(folder/'result.json').write_text(json.dumps(result));self.assertEqual(self.client.call('replayable_status',project_id='open')['regression_full_matches'],0)
 def inject_orphan(self,job,terminal_parent=False):
  # Open-fixture fault injection: emulate a dead parent before any VM dispatch.
  with self.db() as d:
   d.execute('UPDATE jobs SET state=?,result=? WHERE id=?',('interrupted_unknown' if terminal_parent else 'running',json.dumps({'status':'inconclusive','reason':'legacy interrupted parent'}),job['job_id']))
   d.execute("UPDATE replayable_batches SET phase='dispatching' WHERE job=?",(job['job_id'],))
   for child in job['members']:
    d.execute("UPDATE jobs SET state='group_member',result=NULL WHERE id=?",(child['job_id'],));d.execute("UPDATE replayable_frontier SET status='running' WHERE job=?",(child['job_id'],))
   d.commit()
 def test_orphan_parent_preserves_unknown_members_and_cannot_replay(self):
  self.configure_transport();j=self.submit();stdio.wait_job(self.client,j['job_id']);self.inject_orphan(j);out=self.client.call('job_get',job_id=j['job_id']);self.assertEqual(out['state'],'interrupted_unknown',out)
  for child in j['members']:
   c=self.client.call('job_get',job_id=child['job_id']);self.assertEqual(c['result']['status'],'external_outcome_unknown');self.assertFalse(c['result']['automatic_retry'])
  self.client=self.connect();self.assertEqual(self.submit()['job_id'],j['job_id'])
  with self.assertRaises(ValueError):self.submit('not-a-retry')
  with self.assertRaises(ValueError):self.client.call('replayable_run_next',project_id='open',idempotency_key='no-skip',compile=False)
 def test_legacy_terminal_parent_cannot_release_unfinished_members(self):
  self.configure_transport();j=self.submit();stdio.wait_job(self.client,j['job_id']);self.inject_orphan(j,True);out=self.client.call('job_get',job_id=j['job_id']);self.assertEqual(out['result'],{'status':'inconclusive','reason':'legacy interrupted parent'})
  with self.db() as d:self.assertEqual(d.execute("SELECT count(*) FROM replayable_frontier WHERE status='external_outcome_unknown'").fetchone()[0],2)
  with self.assertRaises(ValueError):self.submit('changed-token')

class BatchDispatchTests(unittest.TestCase):
 setUp=BatchPipelineTests.setUp
 connect=BatchPipelineTests.connect
 ids=BatchPipelineTests.ids
 configure_transport=BatchPipelineTests.configure_transport
 submit=BatchPipelineTests.submit
 db=BatchPipelineTests.db
 """Isolated fake bridge exercises state only; it never reports a full match."""
 def install_bridge(self,mode):
  import shutil
  from test_replayable_ir import fixture
  self.configure_transport();runtime=self.root/'isolated-runtime';shutil.copytree(stdio.DLL.parent,runtime);self.saved_dll=stdio.DLL;stdio.DLL=runtime/'Decompilation.Mcp.dll'
  payload=json.dumps(dict(lift=fixture()['lift'],image_base=0x500000,image_end=0x510000,binary_slice_sha256='open-fixture'))
  script='''import json,sys,time,shutil
from pathlib import Path
d=json.load(sys.stdin);a=d['action'];mode=MODE
if a=='lift':result=PAYLOAD
elif a=='build_batch':
 p=Path(d['folder']);(p/'mock-dispatched').write_text('one dispatch')
 if mode=='hold':time.sleep(1)
 if mode=='crash':raise SystemExit(7)
 if mode=='partial':
  first=Path(d['members'][0]['folder'])/'build';first.mkdir();(first/'candidate.obj').write_bytes(b'object alone cannot pass');result={'status':'external_outcome_unknown','error':'partial envelope'}
 else:
  members=[]
  for m in d['members']:
   b=Path(m['folder'])/'build';b.mkdir();shutil.copy2(Path(m['folder'])/'candidate.cpp',b/'candidate.cpp')
   for name in ('compiler.json','run.json','start.json','exit.json'):(b/name).write_text('{}')
   (b/'build-exit.txt').write_text('2');(b/'candidate.obj').write_bytes(b'invalid open object, never accepted');members.append({'job_id':m['request']['job_id']})
  result={'status':'batch_completed','members':members if mode!='wrong-members' else list(reversed(members))}
elif a=='check_build':result={'status':'inconclusive','blocker':'confirmed compiler failure; object alone is not success','proof':False}
else:result={'status':'inconclusive','error':'unexpected mock action'}
print(json.dumps(result))
'''.replace('MODE',repr(mode)).replace('PAYLOAD',repr(json.loads(payload)))
  (runtime/'replayable_adapter.py').write_text(script);self.client=self.connect()
 def tearDown(self):
  try:BatchPipelineTests.tearDown(self)
  finally:
   if hasattr(self,'saved_dll'):stdio.DLL=self.saved_dll
 def test_partial_envelope_keeps_all_members_unknown_despite_object(self):
  self.install_bridge('partial');j=self.submit('partial');out=stdio.wait_job(self.client,j['job_id']);self.assertEqual(out['result']['status'],'external_outcome_unknown',out)
  for child in j['members']:self.assertEqual(self.client.call('job_get',job_id=child['job_id'])['result']['status'],'external_outcome_unknown')
  with self.assertRaises(ValueError):self.submit('cannot-replay-partial')
 def test_confirmed_failures_stay_failures_and_clear_only_known_group(self):
  self.install_bridge('known-failure');j=self.submit('failure');out=stdio.wait_job(self.client,j['job_id']);self.assertEqual(out['result']['outcomes'],{'inconclusive':2});self.assertEqual(out['result']['status'],'batch_completed')
  for child in j['members']:
   result=self.client.call('job_get',job_id=child['job_id'])['result'];self.assertEqual(result['status'],'inconclusive');self.assertIn('compiler failure',result['blocker'])
 def test_crashed_dispatch_cannot_replay(self):
  self.install_bridge('crash');j=self.submit('dispatch-crash');out=stdio.wait_job(self.client,j['job_id']);self.assertEqual(out['state'],'interrupted_unknown',out)
  with self.assertRaises(ValueError):self.submit('new-crash')
 def test_wrong_item_bindings_cannot_be_accepted_or_replayed(self):
  self.install_bridge('wrong-members');j=self.submit('dispatch-wrong');out=stdio.wait_job(self.client,j['job_id']);self.assertEqual(out['state'],'interrupted_unknown',out)
  with self.assertRaises(ValueError):self.submit('new-wrong')
 def test_active_child_is_owned_by_parent_lock(self):
  self.install_bridge('hold');j=self.submit('locks');target=self.root/'attempts'/j['job_id']/'mock-dispatched'
  for _ in range(100):
   if target.exists():break
   time.sleep(.02)
  self.assertTrue(target.exists())
  for child in j['members']:self.assertEqual(self.client.call('job_get',job_id=child['job_id'])['state'],'running')
  stdio.wait_job(self.client,j['job_id'])

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

BASE=Path(__file__).resolve().parents[1]
CODE=BASE/('code' if (BASE/'code').is_dir() else 'continuation')
def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
c=module(CODE/'continuation.py','tested_continuation')
d=c.d
# This immutable root implementation creates the historical fixture, without successor tables.
ROOT=BASE.parents[1] if (BASE/'code').is_dir() else BASE.parent
old=module(ROOT/'workers/recovery_dispatcher.py','old_continuation_fixture')

class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve();self.lineage=self.root/'old';self.runtime=self.root/'successor'
        self.runtime.mkdir();self.doc=self.root/'doc';self.doc.write_text('current evidence')
        self.original='a'*64
        s=old.Store(self.lineage,self.original,now=lambda:1800)
        s.opening_debit(2,'historical setup')
        self.identity='test.exe:'+('b'*64)+':rva-00000010'
        self.task={'id':'old-task','kind':'startup-preparation','priority':1,'functions':[self.identity],
            'inputs':{str(self.doc):d.digest(self.doc)},'depends_on':[]}
        s.add(self.task);s.close()
        self.config={'lineage_state':str(self.lineage),'root':str(self.root),'ledger':str(self.root/'ledger'),
            'tasks':[dict(self.task,id='next-task')],'trusted_code':{},'runtime_code':{}}
        self.configpath=self.runtime/'config.json';d.atomic(self.configpath,self.config)
        db=sqlite3.connect(self.lineage/'state.sqlite3');db.row_factory=sqlite3.Row
        self.before=c.history(db);row=dict(db.execute('SELECT payload,state,job FROM tasks').fetchone());db.close()
        self.plan={'id':'migration-1','config':str(self.configpath),'runtime':str(self.runtime),
            'config_sha256':d.digest(self.configpath),'original_config_sha256':self.original,
            'fixed_inputs':{str(self.doc):d.digest(self.doc)},'request_dispositions':{},
            'anchor':'1800','historical_meta':dict(self.before['meta']),
            'supersessions':{'old-task':{'successor':'next-task','reason':'new measured input','predecessor_sha256':c.value_sha(row)}}}
        self.planpath=self.root/'plan.json';self.approval=self.root/'approval.json';self.release=self.root/'release.json'
        self.freeze()
    def freeze(self):
        d.atomic(self.planpath,self.plan)
        d.atomic(self.approval,{'decision':'approve','plan_sha256':d.digest(self.planpath),'runtime_code':{},
            'scope':'same-lineage-migration-external-adoption-and-bounded-startup-preparation','blocking_issues':[]})
        d.atomic(self.release,{'released':True,'plan_sha256':d.digest(self.planpath),'head':'head'})
    def install(self):
        with patch.object(d,'output',side_effect=lambda argv,root:'' if argv[1]=='status' else 'head'),\
             patch.object(d,'verify_controller'),patch.object(c,'external_adoption',return_value={'accepted_increment':24}):
            c.install(self.planpath,self.approval,self.release)
    def db(self):
        db=sqlite3.connect(self.lineage/'state.sqlite3');self.addCleanup(db.close);return db
    def test_history_same_database_anchor_requests_and_claims_preserved(self):
        self.install()
        with self.db() as db: after=c.history(db)
        self.assertEqual([r for r in after['meta'] if r[0]!='successor-config'],self.before['meta'])
        for table in c.HISTORICAL:
            if table!='meta':self.assertEqual(after[table],self.before[table])
        s=d.Store(self.runtime,d.digest(self.configpath),now=lambda:1800)
        self.addCleanup(s.close);s.add(self.config['tasks'][0])
        self.assertEqual(s.db.execute('SELECT * FROM ownership').fetchall()[0][1],'old-task')
        self.assertEqual(s.db.execute('SELECT successor FROM ownership_successors').fetchone()[0],'next-task')
        claim=s.claim();self.assertEqual(claim['task']['id'],'next-task')
        self.assertEqual(len(claim['requests']),2)
        self.assertEqual(s.db.execute('SELECT value FROM meta WHERE key="anchor"').fetchone()[0],'1800')
        self.assertEqual(s.db.execute('SELECT state FROM tasks WHERE id="old-task"').fetchone()[0],'queued')
        self.assertFalse((self.runtime/'state.sqlite3').exists())
    def test_duplicate_install_and_changed_review_refuse(self):
        self.install()
        with self.assertRaisesRegex(d.Refusal,'already installed'):self.install()
        x=d.load(self.approval);x['decision']='reject';d.atomic(self.approval,x)
        with self.assertRaisesRegex(d.Refusal,'approval missing'):self.install()
    def test_active_worker_refuses_without_schema_mutation(self):
        with self.db() as db:db.execute("INSERT INTO jobs VALUES('active','old-task','running','x',NULL)")
        with self.assertRaisesRegex(d.Refusal,'active'):self.install()
        with self.db() as db:self.assertFalse(db.execute("SELECT 1 FROM sqlite_master WHERE name='migrations'").fetchone())
    def test_active_publisher_lock_refuses(self):
        with d.exclusive(self.root/'local/providers/recovery-integration'):
            with self.assertRaisesRegex(d.Refusal,'another controller'):self.install()
    def test_unresolved_request_refuses(self):
        with self.db() as db:db.execute("INSERT INTO requests VALUES('unknown',0,'other','review','in-flight')")
        with self.assertRaisesRegex(d.Refusal,'ambiguous external'):self.install()
    def test_stale_docs_and_changed_predecessor_refuse(self):
        self.doc.write_text('changed')
        with self.assertRaisesRegex(d.Refusal,'binding changed'):self.install()
        self.doc.write_text('current evidence')
        with self.db() as db:db.execute("UPDATE tasks SET reason='not part of payload'")
        # Reason is retained but not a predecessor scheduling input. State/job/payload are exact.
        with self.db() as db:db.execute("UPDATE tasks SET state='exception'")
        with self.assertRaisesRegex(d.Refusal,'predecessor changed'):self.install()
    def test_pre_reservation_stale_inputs_no_debit_and_other_queue_progress(self):
        self.install();s=d.Store(self.runtime,d.digest(self.configpath),now=lambda:1800);self.addCleanup(s.close)
        s.add(self.config['tasks'][0]);self.doc.write_text('stale')
        before=s.db.execute('SELECT count(*) FROM requests').fetchone()[0]
        self.assertIsNone(s.claim());self.assertEqual(s.db.execute('SELECT count(*) FROM requests').fetchone()[0],before)
        other=dict(self.task,id='other-task',functions=[],inputs={},priority=2)
        s.add(other);self.assertEqual(s.claim()['task']['id'],'other-task')
        self.assertEqual(s.db.execute('SELECT id FROM input_blocks').fetchone()[0],'next-task')
    def test_cycle_limit_not_reset_by_migration(self):
        with self.db() as db:
            db.executemany('INSERT INTO requests VALUES(?,0,?,?,?)',[(str(i),'prior','review','reserved') for i in range(10)])
        self.install();s=d.Store(self.runtime,d.digest(self.configpath),now=lambda:1800);self.addCleanup(s.close)
        s.add(self.config['tasks'][0]);self.assertIsNone(s.claim())
        self.assertEqual(s.db.execute('SELECT count(*) FROM requests').fetchone()[0],12)
    def test_static_adapter_zero_requests_dependency_then_model_task(self):
        self.install();s=d.Store(self.runtime,d.digest(self.configpath),now=lambda:1800);self.addCleanup(s.close)
        task=dict(self.task,id='static-packet',kind='startup-static-packet',functions=[],inputs={},priority=0)
        s.add(task)
        next_task=dict(self.config['tasks'][0],depends_on=['static-packet']);s.add(next_task)
        claim=s.claim();self.assertEqual(claim['task']['id'],'static-packet');self.assertEqual(claim['requests'],[])
        s.finish(claim['job'],{'state':'complete','stage':'preparation'})
        self.assertEqual(s.claim()['task']['id'],'next-task')
    def test_failed_external_adoption_transaction_no_install(self):
        with patch.object(d,'output',side_effect=lambda argv,root:'' if argv[1]=='status' else 'head'),\
             patch.object(c,'external_adoption',side_effect=d.Refusal('incomplete external publication')):
            with self.assertRaisesRegex(d.Refusal,'incomplete'):c.install(self.planpath,self.approval,self.release)
        with self.db() as db:self.assertEqual(c.history(db),self.before)

class CheckpointTests(unittest.TestCase):
    def fixture(self):
        rows=[{'function_id':'f'+str(i),'negative_control':False,'case_counts':{'corpus_pass':1},'status':'corpus_pass'} for i in range(93)]
        rows += [{'function_id':'n'+str(i),'negative_control':True,'case_counts':{'mismatch':1},'status':'failed'} for i in range(72)]
        x={'schema_version':2,'policy':'clean-build-local-groups-003','fresh_clean_build':True,'native_windows_validated':False,
           'complete_checkpoint':True,'proof':False,'records':rows}
        return self.sign(x)
    def sign(self,x):
        x.pop('attestation_sha256',None)
        x['attestation_sha256']=hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest();return x
    def test_exact_inventory_and_controls(self):c.check_checkpoint(self.fixture())
    def test_incomplete_duplicate_and_false_control_refused(self):
        for mutation in (lambda x:x.update(complete_checkpoint=False),lambda x:x['records'].pop(),
                         lambda x:x['records'].__setitem__(1,x['records'][0]),
                         lambda x:x['records'][-1].update(case_counts={'runner_error':1})):
            x=self.fixture();mutation(x)
            with self.assertRaises(d.Refusal):c.check_checkpoint(self.sign(x))
    def test_self_binding_refuses(self):
        x=self.fixture();x['records'][0]['case_counts']['corpus_pass']=2
        with self.assertRaisesRegex(d.Refusal,'self-binding'):c.check_checkpoint(x)

class ExternalAdoptionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name).resolve()
        self.package=self.root/'pair/accepted/package.json';source=self.root/'src/candidate.cpp';source.parent.mkdir();source.write_text('candidate')
        d.atomic(self.package,{'candidate_target':'src/candidate.cpp','source_sha256':d.digest(source),
            'functions':['f'+str(i) for i in range(46)],'proof':False,'native_windows_validated':False})
        descriptor=self.root/'descriptor.json';d.atomic(descriptor,{'package_sha256':d.digest(self.package),
            'pair':str(self.package.parents[1]),'state':'accepted-for-integration'})
        registry=self.root/'analysis/functions.json';d.atomic(registry,{})
        self.source={'source':'hash'};expected=dict(self.source,**{'analysis/functions.json':d.digest(registry)})
        self.record=CheckpointTests().fixture()
        for r in self.record['records']:r.update(artifacts_sha256=expected,artifacts_unchanged=True,
            provenance_kind='fresh_clean_build_and_exact_execution_inputs',repeats_per_side=2)
        CheckpointTests().sign(self.record)
        self.recordpath=self.root/'analysis/validation/current.json';d.atomic(self.recordpath,self.record)
        producer=self.root/'reports/dispatcher-19527cacd0bd4f18a248d7e8a9296480/reuse-attestation.json'
        d.atomic(producer,{'status':'passed','complete_checkpoint':True,'usable_for_progress':True,'source':self.source,
            'registry_sha256':d.digest(registry)})
        self.published=self.root/'published.json';self.receipt=self.root/'receipt.json'
        self.runs=[{'databaseId':1,'headSha':'head','status':'completed','conclusion':'success'}]
        d.atomic(self.published,{'commit':'head','ci_runs':self.runs,'record':str(self.recordpath.relative_to(self.root))})
        self.external={'fixed_inputs':{str(descriptor):d.digest(descriptor)},'descriptor':str(descriptor),
            'package_sha256':d.digest(self.package),'receipt':str(self.receipt),'published':str(self.published),
            'review_packet_sha256':'a'*64,'approval_sha256':'b'*64}
        d.atomic(self.receipt,{'state':'complete','result':{'state':'complete','commit':'head'},
            'review_packet_raw_sha256':'a'*64,'approval_raw_sha256':'b'*64,'published_raw_sha256':d.digest(self.published)})
        self.ci={'headSha':'head','status':'completed','conclusion':'success',
            'jobs':[{'name':'synthetic ('+host+')','conclusion':'success'} for host in ('ubuntu-latest','macos-latest','windows-latest')]}
    def adopt(self):
        cache=SimpleNamespace(source_manifest=lambda root:self.source,publication_document=lambda producer:self.record)
        with patch.object(d,'output',return_value=json.dumps(self.ci)),patch.object(d,'module',return_value=cache):
            return c.external_adoption({'root':str(self.root)},{'external_adoption':self.external})
    def test_exact_accepted_candidate_checkpoint_and_three_host_ci(self):
        result=self.adopt();self.assertEqual(result['accepted_increment'],24);self.assertFalse(result['native_windows_validated'])
    def test_failed_incomplete_and_partial_publication_refuse(self):
        original=d.load(self.receipt)
        for change in ({'state':'exception'},{'published_raw_sha256':'0'*64},{'approval_raw_sha256':'0'*64}):
            d.atomic(self.receipt,dict(original,**change))
            with self.assertRaises(d.Refusal):self.adopt()
    def test_missing_host_and_stale_current_evidence_refuse(self):
        self.ci['jobs'].pop()
        with self.assertRaisesRegex(d.Refusal,'three-host'):self.adopt()
        self.ci['jobs'].append({'name':'synthetic (windows-latest)','conclusion':'success'})
        self.record['records'][0]['artifacts_sha256']={'stale':'hash'}
        CheckpointTests().sign(self.record);d.atomic(self.recordpath,self.record)
        with self.assertRaisesRegex(d.Refusal,'current inputs stale'):self.adopt()
    def test_accepted_source_substitution_refused(self):
        (self.root/'src/candidate.cpp').write_text('different')
        with self.assertRaisesRegex(d.Refusal,'binding changed'):self.adopt()

class StaticPreparationTests(unittest.TestCase):
    def fixture(self, root):
        binary=bytearray(0x500000)
        edges=[]
        for callsite,target in ((0x16b13,0xc2480),(0x16b28,0x4e19e0),(0x16b63,0x4e2d29),(0x16b7c,0x4e2da2),(0x16c00,0x13660)):
            code=b'\xe8'+((target-callsite-5)&0xffffffff).to_bytes(4,'little')
            binary[callsite:callsite+5]=code
            edges.append({'callsite_rva':f'{callsite:08x}','target_rva':f'{target:08x}','kind':'call','bytes':code.hex()})
        image=root/'synthetic.exe';image.write_bytes(binary)
        identity=d.digest(image)
        metadata=root/'observation.json';frontier=root/'frontier.json'
        d.atomic(metadata,{'identity':{'sha256':identity},'observed_control_flow':{'target_rva':'0x00016ad0','target_body_executed':False},
            'termination':{'approval_permanently_consumed':True},'bindings':{}})
        d.atomic(frontier,{'units_in_priority_order':[{'id':'application-envelope','functions':[{'id':'synthetic:'+identity+':rva-00016ad0'}],
            'observed_edges':edges}]+[{'id':'dependency','functions':[{'rva':f'{rva:08x}',
                'body_ranges_hypothesis':[{'start_rva':rva,'end_rva_inclusive':rva+31}],
                'concatenated_body_ranges_sha256':hashlib.sha256(binary[rva:rva+32]).hexdigest()}]}
                for rva in (0xc2480,0x4e19e0,0x4e2d29,0x4e2da2)]})
        task={'observation':str(metadata),'frontier':str(frontier),'inputs':{str(metadata):d.digest(metadata),str(frontier):d.digest(frontier)}}
        config={'root':str(root),'reference':{'path':str(image),'module':'synthetic.exe','sha256':identity}}
        return config,task,{'sections':[{'rva':0,'file_size':len(binary),'file_offset':0}]}
    def test_synthetic_packet_feeds_four_dependencies_without_acceptance(self):
        with tempfile.TemporaryDirectory() as temp:
            config,task,pe=self.fixture(Path(temp).resolve())
            with patch('tools.daodecomp.pe.fingerprint',return_value=pe):result=c.prepare_static(config,task)
            self.assertEqual(len(result['dependency_queue']),4)
            self.assertFalse(result['contract']['implementation_eligible'])
            self.assertFalse(result['windows_milestone']['execute_permitted'])
            self.assertEqual(result['accepted_functions'],0)
    def test_synthetic_edge_tamper_and_stale_evidence_refuse(self):
        with tempfile.TemporaryDirectory() as temp:
            config,task,pe=self.fixture(Path(temp).resolve())
            frontier=d.load(task['frontier']);frontier['units_in_priority_order'][0]['observed_edges'][0]['bytes']='e800000000'
            d.atomic(task['frontier'],frontier)
            with patch('tools.daodecomp.pe.fingerprint',return_value=pe):
                with self.assertRaisesRegex(d.Refusal,'binding changed'):c.prepare_static(config,task)
                task['inputs'][task['frontier']]=d.digest(task['frontier'])
                with self.assertRaisesRegex(d.Refusal,'instruction changed'):c.prepare_static(config,task)
    def test_mapping_never_guesses_ambiguous_or_unbacked_ranges(self):
        for sections in ([],[{'rva':0,'file_size':16,'file_offset':0}]*2):
            with self.assertRaisesRegex(d.Refusal,'unmapped/ambiguous'):c.read_rva(bytes(16),sections,0,4)

class CodecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.pair=module(CODE/'run_recovery_pair.py','compact_continuation_pair')
    def test_lossless_codec_and_invalid_index(self):
        p=self.pair
        rows=[{'stage':'heldout','reports':[{'execution_artifacts_raw_sha256':{'long'+str(i):p.digest(i) for i in range(40)}} for _ in range(10)]}]
        original=p.deduplicate_prompt_provenance(rows,mode='reviewer');compact=p.compact_review_provenance(original)
        self.assertEqual(p.expand_review_provenance(compact),original)
        broken=copy.deepcopy(compact);broken['value']['report_provenance'][0]['binding_indices']=[True]
        with self.assertRaises(p.PairError):p.expand_review_provenance(broken)
    def test_size_refuses_before_request(self):
        p=self.pair
        with tempfile.TemporaryDirectory() as temp,patch.object(p,'run_command',side_effect=AssertionError('no model')):
            target=Path(temp)/'review'
            with self.assertRaises(p.PairError):p.request_model('review','x'*(p.REVIEW_INPUT_LIMIT+1),target,'gpt-6.1-sol',Path(temp),Path('unused'),'python')
            self.assertFalse(target.exists())

if __name__=='__main__':unittest.main()

"""Common object queue controls; no game/VM/compiler dependency."""
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from workers.deepseek_packet import atomic,sha
from rapid.packets import PIN
from rapid_object.catalog import open_store,pages,assign_groups,read_native_attestations
from rapid_object.queue import decision,split_batch,next_packet,process_batch,reconcile,best_results


class ObjectQueueTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name).resolve();self.store=open_store(self.root)
    def tearDown(self):self.store.close();self.temp.cleanup()
    def function(self,rva,paged=False):
        f={'rva':rva,'name':f'fn_{rva:08x}','original_va':0x400000+rva,'ranges':[{'start_rva':rva,'end_rva_inclusive':rva}],'bytes_sha256':sha(b'\xc3'),'signature_hypothesis':{'status':'unknown'},'direct_calls':[],'address_references':[],'context_pages':[[{'bytes':'c3','instruction':'ret'}]]*(2 if paged else 1)}
        self.store.db.execute('INSERT INTO catalog VALUES(?,?,?,?,?,?,?)',(rva,str(rva),'queued',None,'{}',json.dumps(f),None));self.store.db.commit();return f
    def batch(self,rvas,paged=False):
        for r in rvas:self.function(r,paged)
        self.store.add('group',rvas);folder=self.root/'batches/group';folder.mkdir(parents=True);atomic(folder/'selection.json',{'module_sha256':PIN,'rvas':rvas});return folder
    def test_all_catalogued_and_resume_group_assignment(self):
        functions={r:self.function(r,paged=r==3) for r in range(1,5)}
        functions[1]['observations']={'indirect_calls':['unknown'],'floating_point':True};functions[2]['ranges']*=2
        self.assertGreater(assign_groups(self.store,functions,{},1,2),0)
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM identities').fetchone()[0],4)
        self.assertEqual(assign_groups(self.store,functions,{},1,2),0)
    def test_page_bytes_not_lost(self):
        units=[{'bytes':str(i)*10} for i in range(100)]
        self.assertEqual([u for page in pages(units,100) for u in page],units)
    def test_context_page_does_not_compile_or_credit(self):
        folder=self.batch([1],True);value,attempt=next_packet(self.store,'group')
        def request(where,*args):
            where.mkdir();atomic(where/'packet.json',value);(where/'candidate.cpp').write_text('// provisional');r={'outcome':'success','charged_nanodollars':1};atomic(where/'result.json',r);return r
        with patch('rapid_object.queue.request_packet',side_effect=request),patch('rapid_object.queue.build_and_compare') as build:
            process_batch(self.root,'group','id',value,attempt,'vc','ledger','global')
            build.assert_not_called()
        result=json.loads((folder/'result.json').read_text());self.assertEqual(result['context_page'],1);self.assertTrue(result['needs_work']);self.assertEqual(result['functions'],[])
        value,attempt=next_packet(self.store,'group');self.assertEqual(attempt,2);self.assertTrue(value['context_complete']);self.assertIn('prior_context_source',value)
    def test_compiler_repair_gets_exact_failed_source(self):
        folder=self.batch([1]);where=folder/'attempt-1';where.mkdir();source=where/'candidate.cpp';source.write_text('invalid __thiscall source')
        atomic(where/'result.json',{'outcome':'success','charged_nanodollars':1})
        atomic(folder/'result.json',{'needs_work':True,'repairs':1,'latest_source':str(source),'compiler_feedback':{'error':'C3865'}})
        value,attempt=next_packet(self.store,'group');self.assertEqual(attempt,2)
        feedback=value['repair_feedback'];self.assertIn(source.read_text(),feedback['best_sources'].values())
        self.assertEqual(feedback['function_feedback'][-1]['latest_failed_source_sha256'],sha(source.read_bytes()))

    def test_six_repairs_and_attempt_three(self):
        value={'context_complete':True,'functions':[{'rva':1}]};previous={}
        for attempt in range(1,8):
            previous=decision(previous,value,{'outcome':'success','charged_nanodollars':1},[{'rva':1,'status':'nonmatch','score':attempt/10}],6,3)
            self.assertEqual(previous['needs_work'],attempt<7)
        self.assertEqual(previous['stop_reason'],'repair_limit');self.assertEqual(previous['repairs'],6)
    def test_stagnation_and_unknown_stop(self):
        value={'context_complete':True,'functions':[{'rva':1}]};previous={}
        for _ in range(4):previous=decision(previous,value,{'outcome':'success','charged_nanodollars':1},[])
        self.assertEqual(previous['stop_reason'],'stagnation')
        self.assertFalse(decision({},value,{'outcome':'timeout','charged_nanodollars':1},[])['needs_work'])
    def test_split_preserves_history_matches_and_consumed_repairs(self):
        folder=self.batch([1,2,3]);(folder/'candidate.cpp').write_text('retained')
        with self.store.db:self.store.db.execute("UPDATE catalog SET state='exact_object_match' WHERE rva=1")
        children=split_batch(self.store,'group',[2,3],'known_complete',{'repairs':5})
        self.assertEqual(len(children),2);self.assertEqual((folder/'candidate.cpp').read_text(),'retained')
        self.assertEqual(self.store.db.execute('SELECT batch FROM identities WHERE rva=1').fetchone()[0],'group')
        for child in children:
            result=json.loads((self.root/'batches'/child/'result.json').read_text());self.assertEqual(result['repairs'],5)
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM identities').fetchone()[0],3)
    def test_known_invalid_splits_but_unknown_does_not(self):
        folder=self.batch([1,2]);value,attempt=next_packet(self.store,'group')
        def request(where,*args):
            where.mkdir();(where/'raw-response.json').write_text('{}');r={'outcome':'invalid_response','http_status':200,'charged_nanodollars':1};atomic(where/'result.json',r);return r
        with patch('rapid_object.queue.request_packet',side_effect=request):process_batch(self.root,'group','id',value,attempt,'vc','ledger','global')
        result=json.loads((folder/'result.json').read_text());self.assertEqual(len(result['split_children']),2)
        for child in result['split_children']:self.assertEqual(json.loads((self.root/'batches'/child/'result.json').read_text())['repairs'],1)
    def test_pause_and_unknown_reconcile(self):
        self.batch([1]);self.store.pause(True);self.assertIsNone(self.store.next());self.store.pause(False);self.assertEqual(self.store.next(),'group');reconcile(self.store)
        self.assertEqual(self.store.db.execute('SELECT state FROM batches').fetchone()[0],'interrupted_unknown')
    def test_unknown_paid_attempt_never_replayed(self):
        folder=self.batch([1]);where=folder/'attempt-1';where.mkdir();atomic(where/'result.json',{'outcome':'timeout','charged_nanodollars':1});atomic(folder/'result.json',{'needs_work':True})
        with self.assertRaisesRegex(ValueError,'unknown_paid_outcome'):next_packet(self.store,'group')
    def test_stale_or_extra_summary_never_credited(self):
        folder=self.batch([1]);where=folder/'attempt-1';build=where/'build';build.mkdir(parents=True);source=where/'candidate.cpp';source.write_text('x');obj=build/'candidate.obj';obj.write_bytes(b'obj')
        value={'context_complete':True,'functions':[json.loads(self.store.db.execute('SELECT details_json FROM catalog').fetchone()[0])]};atomic(where/'packet.json',value)
        report={'module_sha256':PIN,'source_sha256':sha(source.read_bytes()),'object_sha256':sha(obj.read_bytes()),'implementation_sha256':{n:sha((Path('rapid_object')/n).read_bytes()) for n in ('coff.py','compare.py')},'requested':{'1':{'ranges':value['functions'][0]['ranges']}},'functions':[{'rva':2,'status':'exact_object_match'}]};atomic(build/'summary.json',report)
        self.assertEqual(best_results(folder),[])
        report['functions']=[{'rva':1,'status':'exact_object_match','original_bytes_sha256':value['functions'][0]['bytes_sha256']}];report['implementation_sha256']={};atomic(build/'summary.json',report);self.assertEqual(best_results(folder),[])
    def test_imported_native_bindings_and_completeness(self):
        native=self.root/'native';native.mkdir();source=native/'candidate.cpp';source.write_text('s');dll=native/'candidate.dll';dll.write_bytes(b'dll');report=native/'summary.json'
        r={'module_sha256':PIN,'source_sha256':sha(source.read_bytes()),'recompiled_sha256':sha(dll.read_bytes()),'functions':[{'rva':1,'status':'reccmp_matched','score':1.0,'complete_range_compared':True,'unknowns':[]}]};atomic(report,r)
        path=native/'queue.sqlite3';db=sqlite3.connect(path);db.execute('CREATE TABLE native_functions(rva,status,source,summary)');db.execute('INSERT INTO native_functions VALUES(?,?,?,?)',(1,'reccmp_matched',str(source),str(report)));db.commit();db.close()
        self.assertEqual(len(read_native_attestations(path)),1);r['functions'][0]['complete_range_compared']=False;atomic(report,r);self.assertEqual(read_native_attestations(path),{})
        r['functions'][0]['complete_range_compared']=True;atomic(report,r);dll.write_bytes(b'mutated');self.assertEqual(read_native_attestations(path),{})

if __name__=='__main__':unittest.main()

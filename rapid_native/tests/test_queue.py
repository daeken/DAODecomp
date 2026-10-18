"""Synthetic common queue controls; no game/VM/compiler/provider needed."""
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from rapid_native.queue import native_store,reconcile,best_functions,ingest,next_packet,process_batch,status
from rapid.store import reserve_global
from workers.deepseek_packet import atomic,encode,sha

class NativeQueueTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name).resolve();self.store=native_store(self.root)
    def tearDown(self):self.store.close();self.tmp.cleanup()
    def add(self,ident='example'):
        folder=self.root/'batches'/ident;folder.mkdir(parents=True);self.store.add(ident,[1]);return folder
    def test_pause_dedup_claim(self):
        self.add();self.assertFalse(self.store.add('duplicate',[1]));self.store.pause();self.assertIsNone(self.store.next());self.store.pause(False);self.assertEqual(self.store.next(),'example');self.assertIsNone(self.store.next())
    def test_interrupted_claim_is_never_replayed(self):
        folder=self.add();self.store.next();atomic(folder/'result.json',{'final_record':False,'dispatching':True});reconcile(self.store)
        self.assertEqual(self.store.status()['batches'],{'interrupted_unknown':1});self.assertIsNone(self.store.next())
    def test_completed_response_reconciles_without_provider(self):
        folder=self.add();self.store.next();atomic(folder/'result.json',{'final_record':True,'outcome':'success','needs_repair':False,'functions':[]});reconcile(self.store)
        self.assertEqual(self.store.status()['batches'],{'complete':1})
    def test_exact_best_source_survives_worse_repair(self):
        original={'functions':[{'rva':1,'score':1.0,'status':'reccmp_matched'}]};repair={'functions':[{'rva':1,'score':.9,'status':'retained_unmatched'}]}
        best=best_functions([('old.cpp','old.json',original),('new.cpp','new.json',repair)])
        self.assertEqual(best[0]['source'],'old.cpp');ingest(self.store,'x',best);ingest(self.store,'y',[{**best[0],'status':'retained_unmatched','score':.9}]);self.assertEqual(status(self.root)['reccmp_matched'],1)
    def test_authoritative_budget_exhaustion_and_rollover(self):
        path=self.root/'global.sqlite3';db=sqlite3.connect(path);db.executescript('CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT);CREATE TABLE requests(id TEXT PRIMARY KEY,cycle INTEGER,task TEXT,kind TEXT,state TEXT);');db.execute("INSERT INTO meta VALUES('anchor','1000')");db.commit();db.close()
        for n in range(12):self.assertIsNotNone(reserve_global(path,str(n),1001)[0])
        self.assertIsNone(reserve_global(path,'blocked',2799)[0]);self.assertIsNotNone(reserve_global(path,'next',2800)[0])
    def test_wrong_output_domain_cannot_match(self):
        value={'module':'test','module_sha256':'0'*64,'functions':[{'name':'example','rva':1}]};ident=sha(encode(value));folder=self.add(ident);atomic(folder/'packet.json',value);self.store.next()
        output=folder/'attempt-1/build-1';output.mkdir(parents=True);summary={'functions':[{'rva':2,'score':1.0,'status':'reccmp_matched'}]};atomic(output/'summary.json',summary)
        with patch('rapid_native.queue.request_packet',return_value={'outcome':'success'}),patch('rapid_native.queue.evaluate',return_value=((folder/'attempt-1/candidate.cpp',output/'summary.json',summary),None)):
            process_batch(self.root,ident,'reserved',value,1,'unused','unused','unused')
        result=json.loads((folder/'result.json').read_text());self.assertEqual(result['outcome'],'error')
        # Unexpected identities must never enter the coordinator's matched index.
        self.assertEqual(result['functions'],[])
if __name__=='__main__':unittest.main()

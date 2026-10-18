import concurrent.futures
import json
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from workers import deepseek_packet as provider
from rapid.factory import REPO,build_request,execute
from rapid.packets import PIN
from rapid.store import Store,reserve_global

class RapidTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name).resolve()
    def tearDown(self): self.tmp.cleanup()
    def global_db(self):
        p=self.root/'global.sqlite3'
        with sqlite3.connect(p) as db:
            db.executescript('CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT); CREATE TABLE requests(id TEXT PRIMARY KEY,cycle INTEGER,task TEXT,kind TEXT,state TEXT);')
            db.execute('INSERT INTO meta VALUES(?,?)',('anchor','1000'))
        db.close()
        return p
    def packet(self):
        return {'schema_version':1,'module':'DAOrigins.exe','module_sha256':PIN,'abi_sha256':provider.sha((REPO/'rapid/context.hpp').read_bytes()),'functions':[{'name':'fn_00001000','rva':4096}]}
    def test_dedup_claim_pause_resume(self):
        store=Store(self.root/'queue'); self.assertTrue(store.add('a',[1,2])); self.assertFalse(store.add('b',[2,3]))
        self.assertEqual(store.next(),'a'); self.assertIsNone(store.next())
        store.add('c',[4]); store.pause(); self.assertIsNone(store.next()); store.pause(False); self.assertEqual(store.next(),'c')
        store.reconcile(); self.assertEqual(store.status()['batches'],{'interrupted_unknown':2})
        self.assertEqual(store.status()['functions_verified'],0)
    def test_concurrent_claim_and_budget(self):
        queue=self.root/'queue'; Store(queue).add('a',[1]); db=self.global_db()
        def claim(_): return Store(queue).next()
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            self.assertEqual(list(pool.map(claim,range(8))).count('a'),1)
            reservations=list(pool.map(lambda i:reserve_global(db,str(i),1001),range(24)))
        self.assertEqual(sum(r[0] is not None for r in reservations),12)
        self.assertIsNone(reserve_global(db,'later',2799)[0]); self.assertIsNotNone(reserve_global(db,'next',2800)[0])
    def test_packet_identity_and_domain(self):
        packet=self.packet(); body,bindings,maximum,names,_=build_request(packet)
        self.assertEqual(bindings['packet_sha256'],provider.sha(provider.encode(packet)))
        self.assertEqual(bindings['request_sha256'],provider.sha(body)); self.assertGreater(maximum,0)
        with self.assertRaises(provider.Refusal): provider.source_response({'source':'x','functions':[{'name':'wrong','suggested_name':'x','explanation':'x'}],'uncertainties':[]},names)
    def test_output_bindings_and_retention(self):
        root=self.root/'queue'; store=Store(root); db=self.global_db(); ident,_=reserve_global(db,'test',1001)
        packet=self.packet(); batch=provider.sha(provider.encode(packet)); folder=root/'batches'/batch; folder.mkdir(parents=True)
        provider.atomic(folder/'packet.json',packet); store.add(batch,[4096]); self.assertEqual(store.next(),batch)
        ledger=self.root/'ledger'; provider.Ledger.initialize(ledger,0,[])
        response={'source':'#include "rapid/context.hpp"\nvoid fn_00001000(rapid::Context& c) { c.tick(); c.ret(); }','functions':[{'name':'fn_00001000','suggested_name':'ret','explanation':'Observed return'}],'uncertainties':[]}
        raw=provider.encode({'choices':[{'finish_reason':'stop','message':{'content':json.dumps(response)}}],'usage':{'prompt_tokens':12,'completion_tokens':34}})
        original=provider.read_regular
        def read(path,*args): return b'test-key' if Path(path).name=='.deepseek.key' else original(path,*args)
        with patch.object(provider,'read_regular',side_effect=read),patch.object(provider,'transport',return_value=('success',raw,200)):
            execute(root,batch,ledger,db,ident)
        value=json.loads((folder/'result.json').read_text())
        self.assertEqual(value['outcome'],'success'); self.assertTrue(value['compile_ready']); self.assertEqual(value['validation_status'],'unvalidated')
        self.assertEqual(value['source_sha256'],provider.sha((folder/'source.cpp').read_bytes()))
        self.assertEqual((folder/'raw-response.json').read_bytes(),raw)
        self.assertEqual(Path(value['abi_header']).read_bytes(),(REPO/'rapid/context.hpp').read_bytes())
        self.assertEqual(store.status()['batches'],{'complete':1})
    def test_interrupted_partial_record_is_unknown(self):
        store=Store(self.root/'queue'); store.add('partial',[9]); store.next()
        folder=self.root/'queue/batches/partial'; folder.mkdir(parents=True)
        (folder/'result.json').write_text(json.dumps({'outcome':'error','final_record':False}))
        store.reconcile(); self.assertEqual(store.status()['batches'],{'interrupted_unknown':1})
        self.assertIsNone(store.next())
    def test_packet_tamper_cannot_dispatch(self):
        root=self.root/'queue'; store=Store(root); db=self.global_db(); ident,_=reserve_global(db,'test',1001)
        packet=self.packet(); batch=provider.sha(provider.encode(packet)); folder=root/'batches'/batch; folder.mkdir(parents=True)
        packet['functions'][0]['rva']=123; provider.atomic(folder/'packet.json',packet)
        store.add(batch,[4096]); store.next()
        with patch.object(provider,'transport') as transport:
            execute(root,batch,self.root/'unused-ledger',db,ident)
            transport.assert_not_called()
        value=json.loads((folder/'result.json').read_text()); self.assertEqual(value['outcome'],'error')
        self.assertEqual(value['validation_status'],'unvalidated'); self.assertFalse(value['compile_ready'])
    def test_malformed_paid_response_retained_without_retry(self):
        root=self.root/'queue'; store=Store(root); db=self.global_db(); ident,_=reserve_global(db,'test',1001)
        packet=self.packet(); batch=provider.sha(provider.encode(packet)); folder=root/'batches'/batch; folder.mkdir(parents=True)
        provider.atomic(folder/'packet.json',packet); store.add(batch,[4096]); store.next()
        ledger=self.root/'ledger'; provider.Ledger.initialize(ledger,0,[])
        raw=provider.encode({'choices':[{'finish_reason':'length','message':{'content':'partial source'}}],'usage':{'prompt_tokens':12,'completion_tokens':34}})
        original=provider.read_regular
        def read(path,*args): return b'test-key' if Path(path).name=='.deepseek.key' else original(path,*args)
        with patch.object(provider,'read_regular',side_effect=read),patch.object(provider,'transport',return_value=('success',raw,200)) as sender:
            execute(root,batch,ledger,db,ident); sender.assert_called_once()
        self.assertEqual((folder/'raw-response.json').read_bytes(),raw)
        result=json.loads((folder/'result.json').read_text()); self.assertEqual(result['outcome'],'invalid_response')
        self.assertFalse(result['compile_ready']); self.assertIsNone(store.next())
    def test_unsupported_and_guest_wrap(self):
        source=self.root/'test.cpp'; executable=self.root/'test'
        source.write_text('''#include "rapid/context.hpp"
#include <map>
int main(){ rapid::Context c; try { c.call_rva(1,2); return 1; } catch(const rapid::Unsupported&) {}
std::map<uint32_t,uint8_t> m; c.memory_read=[&](uint32_t a){return m[a];}; c.memory_write=[&](uint32_t a,uint8_t v){m[a]=v;};
c.write32(0xffffffffu,0x12345678u); if(c.read32(0xffffffffu)!=0x12345678u)return 2;
c.esp=4; c.push32(99); c.ret(8); if(!c.returned || c.esp!=12 || c.return_address!=99)return 3;
c.step_budget=c.steps; try {c.tick();return 4;}catch(const rapid::Unsupported&){} return 0;}''')
        subprocess.run(['c++','-std=c++20','-I',str(REPO),str(source),'-o',str(executable)],check=True,capture_output=True)
        subprocess.run([str(executable)],check=True)
if __name__=='__main__': unittest.main()

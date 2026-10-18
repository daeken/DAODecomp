"""Generic scaling/operand/repair controls, independent of the game and VM."""
from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from rapid_native.operands import instruction_keys
from rapid_native.repairs import attempt_numbers,progress_decision
from rapid_native.queue import native_store,claim_native,next_packet
from rapid.store import reserve_global
from workers.deepseek_packet import atomic

class OperandGuards(unittest.TestCase):
    def test_every_memory_operand_field_is_preserved(self):
        value=[{'mnemonic':'mov','prefixes':[0,0,0,0],'address_size':4,'operands':[{'type':'mem','width':4,'segment':None,'base':'ecx','index':'eax','scale':4,'displacement':16}]}]
        for field,replacement in [('width',1),('segment','fs'),('base','edx'),('index','edi'),('scale',8),('displacement',20)]:
            changed=deepcopy(value);changed[0]['operands'][0][field]=replacement
            with self.subTest(field=field):self.assertNotEqual(instruction_keys(value),instruction_keys(changed))
        changed=deepcopy(value);changed[0]['prefixes']=[0,0x66,0,0];self.assertNotEqual(instruction_keys(value),instruction_keys(changed))
    def test_real_memory_scope_and_raw_displacement_controls(self):
        try:
            from capstone import Cs,CS_ARCH_X86,CS_MODE_32
        except ImportError:self.skipTest('optional Capstone runtime unavailable')
        from rapid_native.operands import scope_reason,strict_operand_match
        md=Cs(CS_ARCH_X86,CS_MODE_32);md.detail=True
        decode=lambda value:list(md.disasm(bytes.fromhex(value),0x401000))
        self.assertIsNone(scope_reason(decode('8b4104c3'),0x401000,4))
        self.assertIsNone(scope_reason(decode('89448810c3'),0x401000,5))
        for value in ('a100204000c3','64a100000000c3','ff20','e800000000c3'):
            with self.subTest(value=value):self.assertIsNotNone(scope_reason(decode(value),0x401000,len(bytes.fromhex(value))))
        self.assertFalse(strict_operand_match(decode('8b4104c3'),decode('8b4108c3')))
        self.assertFalse(strict_operand_match(decode('8b4104c3'),decode('8a4104c3')))

class RepairScaling(unittest.TestCase):
    def test_attempt_three_and_seven_ceiling(self):
        best=[{'status':'retained_unmatched','score':.7}]
        value=progress_decision(3,best,1,{'quality':[0,.6]},6,3)
        self.assertTrue(value['needs_repair'])
        value=progress_decision(7,best,1,{'quality':[0,.6]},6,3)
        self.assertFalse(value['needs_repair']);self.assertEqual(value['stop_reason'],'repair_limit')
        self.assertFalse(progress_decision(2,[{'status':'reccmp_matched','score':1.0}],1,{},6,3)['needs_repair'])
    def test_three_stagnant_repairs_stop(self):
        best=[{'status':'retained_unmatched','score':.7}];state={'quality':[0,.7]}
        for attempt in (2,3,4):state=progress_decision(attempt,best,1,state,6,3)
        self.assertFalse(state['needs_repair']);self.assertEqual(state['stagnation'],3)
    def test_numeric_attempts_and_no_directory_reuse(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name).resolve();folder=root/'batches/example';folder.mkdir(parents=True)
            atomic(folder/'packet.json',{'functions':[{'rva':1}]});atomic(folder/'result.json',{'needs_repair':True})
            for n in (1,2):
                p=folder/f'attempt-{n}';p.mkdir();atomic(p/'result.json',{'outcome':'success','charged_nanodollars':1})
            self.assertEqual(attempt_numbers(folder),[1,2])
            with patch('rapid_native.queue.retained_evaluations',return_value=[]),patch('rapid_native.queue.feedback_for',return_value={}):
                _,number=next_packet(root,'example');self.assertEqual(number,3)
            (folder/'attempt-4').mkdir()
            with self.assertRaises(ValueError):attempt_numbers(folder)
    def test_fresh_and_repair_preference(self):
        with tempfile.TemporaryDirectory() as name:
            store=native_store(Path(name));store.add('repair',[1]);store.finish('repair','pending','repair_pending');store.add('fresh',[2])
            self.assertEqual(claim_native(store,False),'fresh');self.assertEqual(claim_native(store,True),'repair');store.close()
    def test_configurable_global_limit_preserves_old_default(self):
        with tempfile.TemporaryDirectory() as name:
            p=Path(name)/'global.sqlite3';db=sqlite3.connect(p);db.executescript('CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT);CREATE TABLE requests(id TEXT PRIMARY KEY,cycle INTEGER,task TEXT,kind TEXT,state TEXT);');db.execute("INSERT INTO meta VALUES('anchor','1000')");db.commit();db.close()
            for n in range(12):self.assertIsNotNone(reserve_global(p,str(n),1001)[0])
            self.assertIsNone(reserve_global(p,'old-default',1001)[0])
            for n in range(12,120):self.assertIsNotNone(reserve_global(p,str(n),1001,ceiling=120)[0])
            self.assertIsNone(reserve_global(p,'native-full',1001,ceiling=120)[0]);self.assertIsNotNone(reserve_global(p,'rollover',2800,ceiling=120)[0])
            with self.assertRaises(ValueError):reserve_global(p,'invalid',1001,ceiling=True)
if __name__=='__main__':unittest.main()

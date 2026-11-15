"""Exception metadata cannot silently widen ownership or accept unwinding."""
from pathlib import Path
import struct
import tempfile
import unittest
from tests.test_recomp_pointer_discovery import fixture
from tools.recomp_native import PE32
from tools.recomp_seh_discovery import PROLOG_MIDDLE,PROLOG_END,discover,internal_roots


class SehDiscoveryTests(unittest.TestCase):
    def image(self,mutate=None):
        data=fixture();data[0x400:0x1400]=b'\xcc'*0x1000;data[0x1400:0x1600]=bytes(0x200)
        def put(rva,raw):data[0x400+rva-0x1000:0x400+rva-0x1000+len(raw)]=raw
        prolog=b'\x68'+struct.pack('<I',0x401300)+PROLOG_MIDDLE+b'\xa1'+struct.pack('<I',0x404000)+PROLOG_END
        self.assertEqual(len(prolog),69);put(0x1100,prolog)
        put(0x1000,b'\x68'+struct.pack('<I',0x403000)+b'\xe8'+struct.pack('<i',0x1100-0x100a))
        put(0x1200,bytes.fromhex('b801000000c3'));put(0x1210,b'\xc3');put(0x1300,b'\xc3')
        struct.pack_into('<iiii',data,0x1400,-2,0,-32,0)
        struct.pack_into('<iII',data,0x1410,-2,0x401200,0x401210)
        # Two original relocation blocks, including source, prolog and record.
        struct.pack_into('<IIHHHH',data,0x1a00,0x1000,16,0x3001,0x3101,0x311e,0)
        struct.pack_into('<IIHHHH',data,0x1a10,0x3000,16,0x3014,0x3018,0,0)
        if mutate:mutate(data)
        temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup)
        path=Path(temporary.name)/'seh.exe';path.write_bytes(data);return PE32(path)

    def catalog(self):return [dict(rva=0x1000,selection=dict(ranges=[dict(rva=0x1000,size=0x300)]))]

    def test_filter_and_handler_are_internal_hypotheses_with_relocated_origins(self):
        pe=self.image();found=discover(pe,{0x1000,0x1005});self.assertEqual(len(found['tables']),1)
        row=found['tables'][0];self.assertEqual(row['records'][0]['filter_rva'],0x1200)
        self.assertIsNotNone(row['trailing_unknown'])
        proposals,unknown=internal_roots(pe,self.catalog(),{0x1000,0x1005},found)
        self.assertFalse(unknown);self.assertEqual([r['rva'] for r in proposals],[0x1200,0x1210])
        self.assertTrue(all(r['owner_rvas']==[0x1000] and 'unknown' in r['contract_status'] for r in proposals))
        self.assertEqual(proposals[0]['origins'][0]['pointer_rva'],0x3014)

    def test_unregistered_source_boundaries_do_not_create_tables(self):
        found=discover(self.image(),{0x1000});self.assertFalse(found['tables'])
        self.assertIn('boundaries',found['rejected'][0]['reason'])

    def test_missing_handler_relocation_and_bad_enclosing_level_stay_rejected(self):
        for mutate in [lambda d:struct.pack_into('<H',d,0x1a1a,0),lambda d:struct.pack_into('<i',d,0x1410,1)]:
            with self.subTest(mutate=mutate):
                found=discover(self.image(mutate),{0x1000,0x1005});self.assertFalse(found['tables']);self.assertTrue(found['rejected'])

    def test_executable_scope_table_and_unbacked_table_stay_rejected(self):
        for target in [0x401200,0x407000,0x405000]:
            found=discover(self.image(lambda d:struct.pack_into('<I',d,0x401,target)),{0x1000,0x1005})
            self.assertFalse(found['tables']);self.assertIn('ordinary data',found['rejected'][0]['reason'])

    def test_instruction_interiors_and_unowned_targets_do_not_widen_ranges(self):
        pe=self.image();found=discover(pe,{0x1000,0x1005})
        proposals,unknown=internal_roots(pe,[],{0x1000,0x1005},found)
        self.assertFalse(proposals);self.assertEqual(len(unknown),2)
        found['tables'][0]['records'][0]['filter_rva']=0x1201
        proposals,unknown=internal_roots(pe,self.catalog(),{0x1000,0x1005,0x1200},found)
        self.assertEqual([r['rva'] for r in proposals],[0x1210]);self.assertIn('interior',unknown[0]['reason'])

    def test_record_budget_cannot_claim_completed_discovery(self):
        with self.assertRaisesRegex(ValueError,'budget exhausted'):
            discover(self.image(),{0x1000,0x1005},record_limit=1)

if __name__=='__main__':unittest.main()

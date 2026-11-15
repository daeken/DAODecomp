"""Original guarded remaps and shared case tails must not become data/padding."""
import copy
from pathlib import Path
import struct
import tempfile
import unittest
import capstone
from tools.recomp_native import PE32
from tools.recomp_pointer_discovery import highlow_sites
from tools.recomp_switch_case_recovery import cfg_tables, recover_owner
from tests.test_recomp_pointer_discovery import fixture


def compressed_fixture():
    image = fixture()
    image[0x440:0x45b] = bytes.fromhex('83f902568bf07728eb038d49000fb68920114000ff248d00114000')
    image[0x45b:0x460] = b'\xcc'*5
    image[0x460:0x465] = bytes.fromhex('83c001eb06')
    image[0x465:0x468] = b'\xcc'*3
    image[0x468:0x474] = bytes.fromhex('83c00283c003eb0233c05ec3')
    struct.pack_into('<II',image,0x500,0x401060,0x401068)
    image[0x520:0x523] = bytes([0,1,0])
    struct.pack_into('<IIHHHH',image,0x1a00,0x1000,16,0x3050,0x3057,0x3100,0x3104)
    struct.pack_into('<I',image,0x98+96+5*8+4,16)
    return image


class SwitchCaseRecoveryTests(unittest.TestCase):
    def setup_image(self,image=None):
        temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup)
        path=Path(temporary.name)/'remap.exe';path.write_bytes(image if image is not None else compressed_fixture())
        pe=PE32(path);decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
        selection=dict(rva=0x1040,size=0x34,ranges=[dict(rva=0x1040,size=10),dict(rva=0x104d,size=14),dict(rva=0x1070,size=4)],
                       extra_entries=[],annotations={'retained_name':'same'},structures={'retained_type':'same'})
        rows=[]
        for span in selection['ranges']:
            rows.extend(dict(rva=i.address-0x400000,bytes=i.bytes.hex()) for i in decoder.disasm(pe.read(span['rva'],span['size']),0x400000+span['rva']))
        return pe,selection,rows

    def test_cfg_guard_crosses_preserving_push_and_direct_branch_skip(self):
        pe,selection,rows=self.setup_image()
        tables,rejected=cfg_tables(pe,rows,highlow_sites(pe))
        self.assertFalse(rejected);self.assertEqual(len(tables),1)
        table=tables[0];self.assertEqual(table['remap']['bytes'],'000100')
        self.assertEqual(table['guard_witness']['unsigned_bound'],2)
        self.assertEqual([t['rva'] for t in table['targets']],[0x1060,0x1068])
        self.assertIn(0x1048,table['guard_witness']['path_rvas'])

    def test_shared_tail_recovery_adds_only_instructions_and_preserves_annotations(self):
        pe,selection,rows=self.setup_image();before=copy.deepcopy(selection)
        tables,_=cfg_tables(pe,rows,highlow_sites(pe));catalog=[dict(rva=selection['rva'],selection=selection)]
        revised,evidence=recover_owner(pe,selection,rows,tables,catalog)
        self.assertEqual(selection,before)
        self.assertEqual(revised['ranges'],[dict(rva=0x1040,size=10),dict(rva=0x104d,size=14),dict(rva=0x1060,size=5),dict(rva=0x1068,size=12)])
        self.assertEqual([i['rva'] for i in evidence['added_instructions']],[0x1060,0x1063,0x1068,0x106b,0x106e])
        self.assertEqual(revised['annotations'],before['annotations']);self.assertEqual(revised['structures'],before['structures'])
        self.assertFalse(evidence['behavioral_acceptance'])
        self.assertNotIn(0x104a,revised['extra_entries'])  # skipped alignment
        self.assertNotIn(0x1100,revised['extra_entries'])  # literal target words

    def test_malformed_map_or_wrong_guard_cannot_propose_cases(self):
        for mutation in ('map_relocation','target_relocation','index_write','signed_guard','oversized_map','noncode_target'):
            image=compressed_fixture()
            if mutation=='map_relocation':struct.pack_into('<H',image,0x1a08,0)
            elif mutation=='target_relocation':struct.pack_into('<H',image,0x1a0c,0)
            elif mutation=='index_write':image[0x444:0x446]=bytes.fromhex('8bc8') # MOV ECX,EAX
            elif mutation=='signed_guard':image[0x446]=0x7f
            elif mutation=='oversized_map':image[0x442]=0x7f
            else:struct.pack_into('<I',image,0x500,0x403000)
            with self.subTest(mutation=mutation):
                pe,_,rows=self.setup_image(image);tables,rejected=cfg_tables(pe,rows,highlow_sites(pe),max_entries=32)
                self.assertFalse(tables);self.assertTrue(rejected)

    def test_guard_and_case_budgets_refuse_without_partial_success(self):
        pe,selection,rows=self.setup_image();sites=highlow_sites(pe)
        tables,rejected=cfg_tables(pe,rows,sites,guard_budget=1)
        self.assertFalse(tables);self.assertTrue(rejected)
        tables,_=cfg_tables(pe,rows,sites)
        with self.assertRaisesRegex(ValueError,'budget exhausted'):
            recover_owner(pe,selection,rows,tables,[dict(rva=selection['rva'],selection=selection)],instruction_limit=1)

    def test_instruction_interiors_tables_and_protected_contracts_refuse(self):
        pe,selection,rows=self.setup_image();tables,_=cfg_tables(pe,rows,highlow_sites(pe));catalog=[dict(rva=selection['rva'],selection=selection)]
        with self.assertRaisesRegex(ValueError,'separate bounds review'):
            recover_owner(pe,selection,rows,tables,catalog,protected=True)
        changed=copy.deepcopy(tables);changed[0]['targets'][0]['rva']=0x1041
        with self.assertRaisesRegex(ValueError,'instruction interior'):
            recover_owner(pe,selection,rows,changed,catalog)
        with self.assertRaisesRegex(ValueError,'table data'):
            recover_owner(pe,selection,rows,tables,catalog,forbidden_data=[(0x1060,0x1065)])

    def test_other_compiled_owner_is_an_explicit_continuation(self):
        pe,selection,rows=self.setup_image();tables,_=cfg_tables(pe,rows,highlow_sites(pe))
        catalog=[dict(rva=selection['rva'],selection=selection),dict(rva=0x106b,selection=dict(ranges=[dict(rva=0x106b,size=5)]))]
        revised,evidence=recover_owner(pe,selection,rows,tables,catalog)
        self.assertIn(0x106b,evidence['external_transfers'])
        self.assertTrue(all(not (s['rva']<0x1070 and 0x106b<s['rva']+s['size']) for s in revised['ranges']))

    def test_tampered_guard_bytes_are_rejected_as_evidence(self):
        pe,_,rows=self.setup_image();rows[0]['bytes']='83f903'
        tables,rejected=cfg_tables(pe,rows,highlow_sites(pe))
        self.assertFalse(tables);self.assertTrue(rejected)

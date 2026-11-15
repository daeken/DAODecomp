"""Direct-edge evidence must not invent fallthroughs, targets or callable ABIs."""
from pathlib import Path
import struct
import tempfile
import unittest
from tools import recomp
from tools.recomp_native import PE32
from tools.recomp_direct_transfer_discovery import DirectTransferScanner, published_origin, prepare
from tools.recomp_instruction_pointer_discovery import discover_closure, ClosureBudgetError
from tests.test_recomp_pointer_discovery import fixture
from tests.test_recomp_switch_case_recovery import compressed_fixture
import copy


class DirectTransferDiscoveryTests(unittest.TestCase):
    def setup_image(self):
        image=fixture();forms={
            0x1000:'0f85fa000000', # conditional to1100, fallthrough1006 omitted
            0x1006:'c3',0x1020:'ebde', # short backwards jump1000
            0x1030:'e8cb000000',0x1035:'c3', # call1100 / return continuation
            0x1040:'b801000000',0x1045:'c3', # ordinary missing fallthrough
            0x1050:'ffe0',0x1060:'ffd0',0x1062:'c3', # indirect JMP/CALL
            0x1070:'66e90100', # unsupported operand-size near transfer
            0x1080:'e97b1f0000', # jump to nonexecutable3000
            0x1090:'f4',0x1100:'e9fb000000',0x1180:'c3',0x1200:'c3'}
        for rva,raw in forms.items():
            data=bytes.fromhex(raw);offset=0x400+rva-0x1000;image[offset:offset+len(data)]=data
        temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup)
        path=Path(temporary.name)/'edges.exe';path.write_bytes(image)
        scanner=DirectTransferScanner(PE32(path))
        return scanner,{rva:dict(rva=rva,bytes=raw) for rva,raw in forms.items()}

    def test_near_edges_and_missing_continuations_are_distinct(self):
        scanner,rows=self.setup_image()
        expected={0x1000:{(0x1100,'direct_conditional'),(0x1006,'conditional_fallthrough')},
                  0x1020:{(0x1000,'direct_jump')},
                  0x1030:{(0x1100,'direct_call'),(0x1035,'return_continuation')},
                  0x1040:{(0x1045,'fallthrough')}}
        for source,wanted in expected.items():
            found,rejected=scanner.scan([rows[source]])
            self.assertFalse(rejected);self.assertEqual({(p['rva'],p['kind']) for p in found},wanted)
            self.assertTrue(all(not p['behavioral_acceptance'] for p in found))
            for row in found:self.assertNotIn('source_pointer_rva',published_origin(row))

    def test_indirect_jumps_and_terminals_never_gain_fake_fallthroughs(self):
        scanner,rows=self.setup_image()
        for source in [0x1050,0x1090,0x1006]:
            found,_=scanner.scan([rows[source]]);self.assertFalse(found)
        found,rejected=scanner.scan([rows[0x1060]])
        self.assertEqual([(p['rva'],p['kind']) for p in found],[(0x1062,'return_continuation')])
        self.assertTrue(rejected)

    def test_byte_mismatch_unsupported_width_and_noncode_target_refuse(self):
        scanner,rows=self.setup_image()
        for row in [dict(rva=0x1000,bytes='0f85fb000000'),rows[0x1070],rows[0x1080]]:
            found,rejected=scanner.scan([row]);self.assertFalse(found);self.assertTrue(rejected)

    def test_generated_instruction_interiors_are_not_new_roots(self):
        scanner,rows=self.setup_image();scanner.record_generated([rows[0x1000]])
        scanner.record_generated([rows[0x1000]]) # identical shared instruction metadata is harmless
        with self.assertRaisesRegex(ValueError,'interiors overlap'):
            scanner.record_generated([dict(rva=0x1001,bytes='85fa000000')])
        self.assertEqual(scanner.known_bytes[0x1000],1);self.assertEqual(scanner.known_bytes[0x1002],2)

    def test_closure_follows_outgoing_targets_beyond_another_owner(self):
        scanner,rows=self.setup_image();found,_=scanner.scan([rows[0x1000]])
        catalog=[dict(rva=0x1000,selection=dict(ranges=[dict(rva=0x1000,size=6)])),
                 dict(rva=0x1180,selection=dict(ranges=[dict(rva=0x1180,size=1)]))]
        result=discover_closure(scanner,[(0x1000,found)],catalog)
        self.assertEqual({p['rva'] for p in result['proposals']},{0x1006,0x1100,0x1200})
        self.assertEqual(result['closure_rounds'],2)
        with self.assertRaises(ClosureBudgetError):discover_closure(scanner,[(0x1000,found)],catalog,max_rounds=1)

    def test_resource_storage_cannot_masquerade_as_an_instruction_source(self):
        scanner,rows=self.setup_image()
        found,rejected=scanner.scan([dict(rva=0x5000,bytes=rows[0x1000]['bytes'])])
        self.assertFalse(found);self.assertTrue(rejected)

    def test_changed_base_overlay_refuses_before_publishing_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);generation=root/'generation';overlay=root/'overlay';generation.mkdir();overlay.mkdir()
            module=dict(inventory_functions=100,catalog_functions=102,processed=102,counts=dict(generated_only=102))
            recomp.atomic_json(generation/'report.json',dict(status='completed inventory generation attempt; compilation/runtime remain separate',
                modules=dict(main=module,umbra=module),entry_overlay=str(overlay),entry_overlay_sha256='0'*64))
            recomp.atomic_json(overlay/'overlay.json',dict(files={}))
            with self.assertRaisesRegex(ValueError,'overlay identity changed'):prepare(generation,root/'output')
            self.assertFalse((root/'output').exists())

    def switch_scanner(self, image=None):
        temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup)
        path=Path(temporary.name)/'switch.exe';path.write_bytes(image if image is not None else compressed_fixture())
        scanner=DirectTransferScanner(PE32(path),include_switches=True)
        rows=[]
        for rva,size in [(0x1040,10),(0x104d,14),(0x1070,4)]:
            rows.extend(dict(rva=i.address-0x400000,bytes=i.bytes.hex())
                for i in scanner.decoder.disasm(scanner.pe.read(rva,size),0x400000+rva))
        scanner.record_generated(rows)
        return scanner,rows

    def test_external_compressed_cases_and_direct_edges_close_without_widening_owner(self):
        scanner,rows=self.switch_scanner();found,rejected=scanner.scan(rows)
        self.assertTrue(any(r['kind']=='guarded_switch_case' for r in found))
        selection=dict(rva=0x1040,size=0x1b,ranges=[dict(rva=0x1040,size=10),dict(rva=0x104d,size=14)],annotations={'name':'retained'})
        catalog=[dict(rva=0x1040,selection=selection),dict(rva=0x1070,selection=dict(ranges=[dict(rva=0x1070,size=4)]))]
        before=copy.deepcopy(catalog);result=discover_closure(scanner,[(0x1040,found)],catalog)
        self.assertEqual(catalog,before)
        self.assertEqual({p['rva'] for p in result['proposals']},{0x1060,0x106b})
        self.assertTrue(any(r['rva']==0x1068 and 'fallthrough' in r['reason'] for r in result['rejected_bounds']))
        scanner.validate_table_separation(result['proposals'])
        origin=next(r for r in found if r['kind']=='guarded_switch_case')
        self.assertEqual(published_origin(origin)['table_entry_rva'],0x1100)
        self.assertNotIn('relative_operand_rva',published_origin(origin))

    def test_switch_literal_overlap_refuses_the_overlay(self):
        scanner,rows=self.switch_scanner();scanner.scan(rows)
        for rva in [0x1100,0x1120]:
            with self.assertRaisesRegex(ValueError,'switch data'):
                scanner.validate_table_separation([dict(ranges=[dict(rva=rva,size=1)])])
        scanner.known_bytes[0x1100]=1
        with self.assertRaisesRegex(ValueError,'switch data'):
            scanner.validate_table_separation([])

    def test_unrelocated_case_and_tampered_guard_do_not_become_switch_roots(self):
        image=compressed_fixture();struct.pack_into('<H',image,0x1a0c,0)
        scanner,rows=self.switch_scanner(image);found,rejected=scanner.scan(rows)
        self.assertFalse(any(r['kind']=='guarded_switch_case' for r in found));self.assertTrue(rejected)
        scanner,rows=self.switch_scanner();rows[0]['bytes']='83f903'
        found,rejected=scanner.scan(rows)
        self.assertFalse(any(r['kind']=='guarded_switch_case' for r in found));self.assertTrue(rejected)

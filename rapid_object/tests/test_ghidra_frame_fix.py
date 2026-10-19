"""Synthetic byte-backed cookie/address controls; no game/VM required."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from rapid.packets import PIN
from workers.deepseek_packet import atomic,sha
from rapid_object import ghidra_frame_fix as frame


# Four fixed pushes precede a 32-bit cookie XOR with entryESP-16.
PREFIX=bytes.fromhex('6aff680020400064a1000000005056a100304000')
SUFFIX=bytes.fromhex('64a30000000064a300000000c3')
DATA=PREFIX+bytes.fromhex('33c4')+SUFFIX
class PE:
    def __init__(self,data):self.data=data
    def get_data(self,rva,size):return self.data[rva-0x1000:rva-0x1000+size]


def record(data=DATA):
    return {'rva':0x1000,'original_va':0x401000,'image_base':0x400000,'module_sha256':PIN,'status':'decompiled','ranges':[{'start_rva':0x1000,'end_rva_inclusive':0x1000+len(data)-1}],'bytes_sha256':sha(data),'draft':'uint FUN_00401000(void) {\n int *unaff_FS_OFFSET;\n int old;\n uint temp;\n old = *unaff_FS_OFFSET;\n temp = DAT_00403000 ^ (uint)&stack0xfffffff0;\n *unaff_FS_OFFSET = (int)&old;\n *unaff_FS_OFFSET = old;\n return temp;\n}', 'type_declarations_hypothesis':'typedef unsigned int uint;','symbols':[{'kind':'function','token':'FUN_00401000','name':'FUN_00401000','rva':0x1000,'original_va':0x401000},{'kind':'global','token':'DAT_00403000','original_va':0x403000,'type_hypothesis':'uint'}]}


class FrameTests(unittest.TestCase):
    def test_fixed_push_prologue_proves_actual_negative_delta(self):
        proof=frame.frame_evidence(record(),PE(DATA));self.assertEqual(proof['original_delta'],-16);self.assertEqual(proof['cookie_va'],0x403000);self.assertEqual(proof['matched_site']['delta'],-16)
    def test_lowering_uses_real_entry_address_and_unsigned_wrap_not_local_storage(self):
        raw=record();proof=frame.frame_evidence(raw,PE(DATA));out,change=frame.lower_frame(raw,proof)
        self.assertIn('DAT_00403000 ^ ((unsigned int)_AddressOfReturnAddress() + 0xfffffff0u)',out['draft']);self.assertIn('_AddressOfReturnAddress',out['type_declarations_hypothesis']);self.assertIn('&stack0xfffffff0',raw['draft']);self.assertFalse(change['native_seh_frame_reconstructed'])
        self.assertEqual(((0x80000008+0xfffffff0)&0xffffffff),0x7ffffff8)
    def test_wrong_delta_or_wrong_cookie_target_refused(self):
        raw=record();raw['draft']=raw['draft'].replace('fffffff0','ffffffec')
        with self.assertRaisesRegex(ValueError,'delta_mismatch'):frame.frame_evidence(raw,PE(DATA))
        wrong=PREFIX[:-4]+bytes.fromhex('04304000')+bytes.fromhex('33c4')+SUFFIX
        with self.assertRaisesRegex(ValueError,'no_matching|nonlinear'):frame.frame_evidence(record(wrong),PE(wrong))
    def test_two_cookie_sites_select_only_unique_expected_delta(self):
        # First GS cookie at entrySP-16; second SEH cookie after two saved registers.
        data=PREFIX+bytes.fromhex('33c45056a10030400033c4')+SUFFIX
        raw=record(data);raw['draft']=raw['draft'].replace('fffffff0','ffffffe8');proof=frame.frame_evidence(raw,PE(data));self.assertEqual([x['delta'] for x in proof['cookie_sites']],[-16,-24]);self.assertEqual(proof['matched_site']['delta'],-24)
    def test_two_matching_sites_are_ambiguous_and_later_call_or_branch_not_crossed(self):
        data=PREFIX+bytes.fromhex('33c4a10030400033c4')+SUFFIX
        with self.assertRaisesRegex(ValueError,'ambiguous_cookie_delta_sites'):frame.frame_evidence(record(data),PE(data))
        for boundary in (bytes.fromhex('e800000000'),bytes.fromhex('eb00'),bytes.fromhex('83e4f0')):
            data=PREFIX+bytes.fromhex('33c4')+boundary+bytes.fromhex('5056a10030400033c4')+SUFFIX;raw=record(data);raw['draft']=raw['draft'].replace('fffffff0','ffffffe8')
            with self.assertRaisesRegex(ValueError,'delta_mismatch|unknown_dynamic|nonlinear'):frame.frame_evidence(raw,PE(data))

    def test_dynamic_stack_alignment_call_and_branch_before_cookie_refused(self):
        for extra in (bytes.fromhex('83e4f0'),bytes.fromhex('e800000000'),bytes.fromhex('eb00')):
            data=PREFIX+extra+bytes.fromhex('33c4')+SUFFIX
            with self.assertRaisesRegex(ValueError,'unknown_dynamic|nonlinear'):frame.frame_evidence(record(data),PE(data))
    def test_register_cookie_copy_cannot_hide_second_matching_site(self):
        data=PREFIX+bytes.fromhex('33c4a1003040008bc833cc')+SUFFIX
        with self.assertRaisesRegex(ValueError,'ambiguous_cookie_delta_sites'):frame.frame_evidence(record(data),PE(data))

    def test_traps_interrupts_system_transfers_cannot_reach_later_cookie(self):
        for encoded in ('cc','0f0b','ce','cf','f4','f1','cd80','0f34','0f35','0f05','0f07','c7f800000000','c6f800','6200'):
            with self.subTest(encoded=encoded):
                data=PREFIX+bytes.fromhex(encoded+'33c4')+SUFFIX
                with self.assertRaisesRegex(ValueError,'nonlinear_or_callee_modified_frame'):frame.frame_evidence(record(data),PE(data))

    def test_partial_register_write_invalidates_loaded_cookie(self):
        data=PREFIX+bytes.fromhex('b00133c4')+SUFFIX
        with self.assertRaisesRegex(ValueError,'no_matching|nonlinear'):frame.frame_evidence(record(data),PE(data))
    def test_fixed_sub_and_saved_entry_relative_register_are_supported(self):
        data=PREFIX+bytes.fromhex('83ec088bec33c5')+SUFFIX;raw=record(data);raw['draft']=raw['draft'].replace('fffffff0','ffffffe8');proof=frame.frame_evidence(raw,PE(data));self.assertEqual(proof['original_delta'],-24)
    def test_any_local_storage_dereference_address_alias_or_second_reference_refused(self):
        for text in ('temp = stack0xfffffff0;','temp = *(uint *)&stack0xfffffff0;','char *p = (char *)&stack0xfffffff0;'):
            raw=record();raw['draft']=raw['draft'].replace('return temp;',text+'\n return temp;')
            with self.assertRaisesRegex(ValueError,'not_single_cookie'):frame.cookie_expression(raw)
    def test_positive_or_return_address_token_is_not_cookie_local_frame(self):
        for token in ('00000004','00000000'):
            raw=record();raw['draft']=raw['draft'].replace('fffffff0',token)
            with self.assertRaisesRegex(ValueError,'not_negative'):frame.cookie_expression(raw)
    def test_alias_width_requires_unique_real_type_not_comment(self):
        for types in ('// typedef unsigned int uint;\ntypedef unsigned short uint;','typedef unsigned int uint; typedef unsigned short uint;','typedef unsigned short uint;'):
            raw=record();raw['type_declarations_hypothesis']=types
            with self.assertRaisesRegex(ValueError,'not_proven_u32'):frame.cookie_expression(raw)
    def test_inline_or_naked_entry_cannot_rebind_return_slot_to_caller(self):
        for qualifier in ('inline ','_inline ','__inline ','_forceinline ','__forceinline ','__declspec(naked) '):
            raw=record();raw['draft']=qualifier+raw['draft']
            with self.assertRaisesRegex(ValueError,'entry_boundary_not_out_of_line'):frame.cookie_expression(raw)

    def test_full_original_bytes_and_identity_pinned(self):
        raw=record();raw['bytes_sha256']='wrong'
        with self.assertRaisesRegex(ValueError,'original_range_hash'):frame.frame_evidence(raw,PE(DATA))
        raw=record();raw['original_va']+=1
        with self.assertRaisesRegex(ValueError,'original_entry_identity'):frame.frame_evidence(raw,PE(DATA))
    def test_only_address_expression_changes_cookie_load_and_body_remain(self):
        raw=record();out,_=frame.lower_frame(raw,frame.frame_evidence(raw,PE(DATA)));before=raw['draft'].split('(uint)&stack0xfffffff0');after=out['draft'].split('((unsigned int)_AddressOfReturnAddress() + 0xfffffff0u)');self.assertEqual(before,after)
    def test_source_recipe_change_refuses_retained_derived_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();raw=root/'raw.json';atomic(raw,record());case={'rva':0x1000,'raw_export':str(raw),'raw_export_sha256':sha(raw.read_bytes()),'category':'frame'};folder=root/'00001000';folder.mkdir();(folder/'frame-export.json').write_bytes(b'changed')
            with patch.object(frame,'frame_evidence',return_value=frame.frame_evidence(record(),PE(DATA))):
                with self.assertRaisesRegex(ValueError,'recipe_changed'):frame.evaluate(case,root)


if __name__=='__main__':unittest.main()

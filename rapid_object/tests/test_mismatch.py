"""Synthetic diagnostics controls, never game-equivalence evidence."""
import copy
import hashlib
import unittest
from unittest.mock import patch
from rapid_object.mismatch import classify_function, classify_report


def entry(original, candidate):
    return {'rva':0x1000,'original_va':0x401000,'status':'nonmatch','diagnostics':['full_function_bytes_differ'],
            'original_bytes_hex':original.hex(),'relocated_bytes_hex':candidate.hex(),
            'original_bytes_sha256':hashlib.sha256(original).hexdigest(),
            'relocated_bytes_sha256':hashlib.sha256(candidate).hexdigest()}


class MismatchTests(unittest.TestCase):
    def classify(self,a,b): return classify_function(entry(bytes.fromhex(a),bytes.fromhex(b)))
    def test_register_only(self):
        r=self.classify('8bc1c3','8bc2c3');self.assertEqual(r['primary'],'register');self.assertEqual(r['labels'],['register'])
        self.assertTrue(r['same_instruction_shapes']);self.assertEqual(r['examples'][0]['original']['offset'],0)
    def test_memory_displacement_is_not_register(self):
        r=self.classify('8b4104c3','8b4108c3');self.assertEqual(r['primary'],'memory_displacement');self.assertNotIn('register',r['labels'])
    def test_stack_displacement(self):self.assertEqual(self.classify('8b442404c3','8b442408c3')['primary'],'stack_displacement')
    def test_memory_base(self):self.assertEqual(self.classify('8b0100c3','8b0200c3')['primary'],'memory_addressing')
    def test_branch_condition(self):
        r=self.classify('760090c3','740090c3');self.assertEqual(r['primary'],'branch_condition');self.assertIn('control_flow_shape',r['labels'])
    def test_branch_target(self):self.assertEqual(self.classify('750090c3','750190c3')['primary'],'control_flow_shape')
    def test_direct_call_target(self):self.assertEqual(self.classify('e800000000c3','e801000000c3')['primary'],'call_target')
    def test_indirect_call_target(self):self.assertEqual(self.classify('ff1500104000c3','ff1504104000c3')['primary'],'call_target')
    def test_register_indirect_call(self):self.assertEqual(self.classify('ffd0c3','ffd1c3')['primary'],'call_target')
    def test_return_cleanup(self):
        r=self.classify('c20400','c20800');self.assertEqual(r['primary'],'stack_cleanup');self.assertIn('prologue_epilogue',r['labels'])
    def test_stack_adjustment(self):self.assertEqual(self.classify('83c404c3','83c408c3')['primary'],'stack_cleanup')
    def test_immediate(self):self.assertEqual(self.classify('b801000000c3','b802000000c3')['primary'],'immediate')
    def test_width(self):self.assertEqual(self.classify('8b01c3','668b01c3')['primary'],'operand_width')
    def test_instruction_selection(self):self.assertEqual(self.classify('01c8c3','29c8c3')['primary'],'instruction_selection')
    def test_structural(self):self.assertIn('larger_structural_difference',self.classify('c3','9090c3')['labels'])
    def test_incomplete_decode(self):self.assertEqual(self.classify('c3','0f')['primary'],'unsupported_decode')
    def test_bad_hex(self):
        e=entry(b'\xc3',b'\x90');e['relocated_bytes_hex']='zz';self.assertEqual(classify_function(e)['primary'],'unsupported_decode')
    def test_wrong_byte_hash(self):
        e=entry(b'\xc3',b'\x90');e['original_bytes_sha256']='0'*64;self.assertEqual(classify_function(e)['decode_error'],'comparison_byte_hash_mismatch')
    def test_missing_relocated_data(self):
        e=entry(b'\xc3',b'\x90');del e['relocated_bytes_hex'];self.assertEqual(classify_function(e)['primary'],'unsupported_decode')
    def test_unresolved_never_decode_partial_bytes(self):
        e=entry(b'\xc3',b'\x90');e.update(status='inconclusive',diagnostics=['unresolved_symbol:_bad']);r=classify_function(e);self.assertEqual(r['primary'],'relocation_resolution');self.assertNotIn('original_instruction_count',r)
    def test_boundary(self):self.assertEqual(classify_function({'status':'inconclusive','diagnostics':['unsupported_noncontiguous_or_missing_original_ranges']})['primary'],'boundary_or_range')
    def test_unsupported(self):self.assertEqual(classify_function({'status':'inconclusive','diagnostics':['unsupported_thing']})['primary'],'unsupported_comparison')
    def test_unknown(self):self.assertEqual(classify_function({'status':'inconclusive','diagnostics':['other']})['primary'],'unknown')
    def test_exact_retains_status_without_rediagnosis(self):self.assertEqual(classify_function({'status':'exact_object_match'})['primary'],'existing_exact_report')
    def test_no_acceptance_or_input_mutation(self):
        e=entry(b'\xc3',b'\x90');before=copy.deepcopy(e);r=classify_report({'functions':[e]});self.assertEqual(e,before);self.assertFalse(r['functions'][0]['acceptance_changed']);self.assertTrue(r['diagnostic_only'])
    def test_example_bound_and_repeatability(self):
        e=entry(bytes.fromhex('b801000000c3'),bytes.fromhex('b802000000c3'));self.assertEqual(classify_function(e,0)['examples'],[]);self.assertEqual(classify_function(e),classify_function(e))
    def test_identical_relative_call_encoding_at_shifted_offset(self):
        r=self.classify('e800000000c3','90e800000000c3');self.assertIn('call_target',r['labels']);self.assertIn('larger_structural_difference',r['labels'])
    def test_byte_budget(self):
        with patch('rapid_object.mismatch.MAX_BYTES',1):
            self.assertEqual(self.classify('90c3','91c3')['primary'],'unsupported_decode')
    def test_alignment_budget(self):
        with patch('rapid_object.mismatch.MAX_ALIGNMENT_PRODUCT',0):
            r=self.classify('c3','90c3');self.assertEqual(r['alignment'],'diagnostic_alignment_budget_exceeded');self.assertIn('larger_structural_difference',r['labels'])
    def test_invalid_limit(self):
        with self.assertRaises(ValueError):classify_function({},33)

if __name__=='__main__':unittest.main()

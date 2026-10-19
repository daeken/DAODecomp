"""Synthetic generic source/byte fixtures test binding, never establish game behavior."""
from pathlib import Path
import sys,tempfile,unittest,copy
sys.path.insert(0,str(Path(__file__).resolve().parents[2]));sys.path.insert(0,str(Path(__file__).resolve().parent))
from rapid_object import ast_match as m
if (Path(__file__).resolve().parent/'proposal.py').is_file():
 import proposal as p
else:
 from rapid_object import indirect_receiver_fix as p
BASE='typedef unsigned int code(...);\nvoid __fastcall fn_00001000(int p) { (**(code **)(**(unsigned int **)(p+12)+16))(); }\n'
HEX='8b490c8b018b5010ffe2'

def report(hex=HEX):return {'functions':[{'rva':0x1000,'original_va':0x401000,'original_bytes_hex':hex}],'symbol_addresses':{}}

class Rules(unittest.TestCase):
 def setUp(self):self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.folder=Path(self.temp.name)
 def run_rule(self,source=BASE,hex=HEX,rep=None):
  ast=m.parse(source,self.folder);return p.rewrite(source,ast,rep or report(hex))
 def test_parameter_receiver_and_target_are_bound_to_ast(self):
  source,meta=self.run_rule();self.assertIn('__thiscall',source);self.assertEqual(meta['receiver_source'],'*(unsigned int **)(p+12)');self.assertEqual(meta['original_edge']['slot'],16);self.assertEqual(meta['original_edge']['edge_kind'],'jmp');self.assertFalse(meta['semantic_preservation_claim']);m.parse(source,self.folder,'changed')
 def test_observed_global_receiver(self):
  src='typedef unsigned int code(...); extern "C" unsigned int *g_00000020; void fn_00001000(){(**(code **)(*g_00000020+16))();}'
  r=report('8b0d200040008b018b5010ffe2');r['symbol_addresses']={'_g_00000020':0x400020}
  changed,meta=self.run_rule(src,rep=r);self.assertEqual(meta['receiver_source'],'g_00000020');m.parse(changed,self.folder,'changed')
 def test_global_address_disagreement(self):
  src='typedef unsigned int code(...); extern "C" unsigned int *g_00000024; void fn_00001000(){(**(code **)(*g_00000024+16))();}'
  r=report('8b0d200040008b018b5010ffe2');r['symbol_addresses']={'_g_00000024':0x400024}
  with self.assertRaises(p.Unsupported):self.run_rule(src,rep=r)
 def test_slot_mutation_rejected(self):
  with self.assertRaises(p.Unsupported):self.run_rule(hex=HEX.replace('5010','5014'))
 def test_receiver_displacement_mutation_rejected(self):
  with self.assertRaises(p.Unsupported):self.run_rule(hex=HEX.replace('490c','4910'))
 def test_lost_ecx_input_is_not_invented(self):
  with self.assertRaises(p.Unsupported):self.run_rule(hex='8b410c8b008b5010ffe2')
 def test_multiple_edges_rejected(self):
  with self.assertRaises(p.Unsupported):self.run_rule(hex=HEX+'ffe0')
 def test_earlier_call_rejected(self):
  with self.assertRaises(p.Unsupported):self.run_rule(hex='e800000000'+HEX)
 def test_branch_prefix_rejected(self):
  with self.assertRaises(p.Unsupported):self.run_rule(hex='7400'+HEX)
 def test_memory_write_prefix_rejected(self):
  with self.assertRaises(p.Unsupported):self.run_rule(hex='c70100000000'+HEX)
 def test_partial_register_prefix_rejected(self):
  with self.assertRaises(p.Unsupported):self.run_rule(hex='b100'+HEX)
 def test_stack_receiver_rejected(self):
  with self.assertRaises(p.Unsupported):self.run_rule(hex='8b4c24048b018b5010ffe2')
 def test_indexed_receiver_rejected(self):
  with self.assertRaises(p.Unsupported):self.run_rule(hex='8b4c810c8b018b5010ffe2')
 def test_segmented_receiver_rejected(self):
  with self.assertRaises(p.Unsupported):self.run_rule(hex='648b490c8b018b5010ffe2')
 def test_unbound_cdecl_entry_rejected(self):
  with self.assertRaises(p.Unsupported):self.run_rule(BASE.replace('__fastcall ',''))
 def test_two_parameters_rejected(self):
  with self.assertRaises(p.Unsupported):self.run_rule(BASE.replace('int p)','int p, int q)'))
 def test_wide_parameter_rejected(self):
  with self.assertRaises(p.Unsupported):self.run_rule(BASE.replace('int p)','__int64 p)'))
 def test_explicit_argument_rejected(self):
  with self.assertRaises(p.Unsupported):self.run_rule(BASE.replace('))();','))(7);'))
 def test_existing_return_hypothesis_is_not_invented(self):
  with self.assertRaises(p.Unsupported):self.run_rule(BASE.replace('typedef unsigned int code','typedef float code'))
 def test_side_effectful_receiver_rejected(self):
  with self.assertRaises(p.Unsupported):self.run_rule(BASE.replace('(p+12)','(p+++12)'))
 def test_macro_spelling_rejected(self):
  src='#define DISPATCH(p) (**(code **)(**(unsigned int **)(p+12)+16))()\n'+'typedef unsigned int code(...); void __fastcall fn_00001000(int p){DISPATCH(p);}'
  with self.assertRaises(p.Unsupported):self.run_rule(src)
 def test_nonword_pointer_stride_rejected(self):
  with self.assertRaises(p.Unsupported):self.run_rule(BASE.replace('(p+12)','((char *)p+12)'))
 def test_incomplete_instruction_range_rejected(self):
  with self.assertRaises(p.Unsupported):self.run_rule(hex=HEX+'0f')
 def test_direct_call_not_rewritten(self):
  with self.assertRaises(p.Unsupported):self.run_rule('extern "C" unsigned int direct();void __fastcall fn_00001000(int p){direct();}')

 def test_volatile_receiver_is_rejected(self):
  with self.assertRaises(p.Unsupported):self.run_rule(BASE.replace('unsigned int **','unsigned int * volatile *'))
 def test_non_ascii_source_rejected(self):
  with self.assertRaises(p.Unsupported):self.run_rule('// é\n'+BASE)
 def test_function_identity_is_stable(self):
  r=report();r['functions'][0]['rva']=0x2000
  with self.assertRaises(p.Unsupported):self.run_rule(rep=r)
 def test_duplicate_function_definitions_rejected(self):
  source=BASE+'void __fastcall fn_00001000(unsigned int p) { (**(code **)(**(unsigned int **)(p+12)+16))(); }'
  with self.assertRaises(p.Unsupported):self.run_rule(source)

if __name__=='__main__':unittest.main()

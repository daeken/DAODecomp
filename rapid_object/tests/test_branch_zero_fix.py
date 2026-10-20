"""Synthetic integer predicate/source-binding controls, not proof of the game."""
from pathlib import Path
import sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]));sys.path.insert(0,str(Path(__file__).resolve().parent))
from rapid_object import ast_match as m
try:from rapid_object import branch_zero_fix as p
except ImportError:import branch_zero_fix as p
BASE='int fn_00001000(int x){return -1 < x;}\n'
def report(hex='85c07c00c3'):return {'functions':[{'rva':0x1000,'original_va':0x401000,'original_bytes_hex':hex}]}
class Rules(unittest.TestCase):
 def setUp(self):self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.folder=Path(self.t.name)
 def run_rule(self,source=BASE,r=None):return p.rewrite(source,m.parse(source,self.folder),r or report())
 def test_negative_one_left(self):
  s,meta=self.run_rule();self.assertIn('(x) >= 0',s);self.assertEqual(len(meta['sites']),1);self.assertFalse(meta['whole_function_semantic_proof']);m.parse(s,self.folder,'candidate')
 def test_negative_one_right(self):self.assertIn('(x) >= 0',self.run_rule(BASE.replace('-1 < x','x > -1'))[0])
 def test_negative_threshold_left(self):self.assertIn('(x) < 0',self.run_rule(BASE.replace('-1 < x','-1 >= x'))[0])
 def test_negative_threshold_right(self):self.assertIn('(x) < 0',self.run_rule(BASE.replace('-1 < x','x <= -1'))[0])
 def test_plain_memory_read_retained_once(self):
  s,_=self.run_rule('int fn_00001000(int *x){return -1 < x[1];}');self.assertEqual(s.count('x[1]'),1)
 def test_multiple_sites(self):
  s,meta=self.run_rule('int fn_00001000(int x,int y){return (-1 < x) && (y <= -1);}');self.assertEqual(len(meta['sites']),2);m.parse(s,self.folder,'candidate')
 def test_signed_boundaries(self):
  for x in (-2147483648,-2147483647,-2,-1,0,1,2147483646,2147483647):self.assertEqual(-1<x,x>=0);self.assertEqual(x<=-1,x<0)
 def test_unsigned_comparison_refused(self):
  with self.assertRaises(p.Unsupported):self.run_rule(BASE.replace('int x','unsigned int x'))
 def test_float_comparison_refused(self):
  with self.assertRaises(p.Unsupported):self.run_rule(BASE.replace('int x','float x'))
 def test_wide_integer_refused(self):
  with self.assertRaises(p.Unsupported):self.run_rule(BASE.replace('int x','long long x'))
 def test_volatile_read_refused(self):
  with self.assertRaises(p.Unsupported):self.run_rule('int fn_00001000(volatile int *x){return -1 < *x;}')
 def test_call_refused(self):
  with self.assertRaises(p.Unsupported):self.run_rule('int effect();int fn_00001000(){return -1 < effect();}')
 def test_increment_refused(self):
  with self.assertRaises(p.Unsupported):self.run_rule(BASE.replace('-1 < x','-1 < x++'))
 def test_assignment_refused(self):
  with self.assertRaises(p.Unsupported):self.run_rule(BASE.replace('-1 < x','-1 < (x=2)'))
 def test_zero_canonical_not_replayed(self):
  with self.assertRaises(p.Unsupported):self.run_rule(BASE.replace('-1 < x','x >= 0'))
 def test_other_threshold_not_guessed(self):
  with self.assertRaises(p.Unsupported):self.run_rule(BASE.replace('-1 < x','-2 < x'))
 def test_unrelated_direction_not_changed(self):
  with self.assertRaises(p.Unsupported):self.run_rule(BASE.replace('-1 < x','-1 > x'))
 def test_original_sign_branch_required(self):
  with self.assertRaises(p.Unsupported):self.run_rule(r=report('85c07400c3'))
 def test_original_cmp_memory_zero_supported(self):self.run_rule(r=report('8338007c00c3'))
 def test_sub_copy_sign_observed(self):
  _,meta=self.run_rule(r=report('2bd78bf27200c3'.replace('72','78')));self.assertIn('wrapped32',meta['original_zero_sign_branches'][0]['evidence'])
 def test_sub_copy_non_sign_branches_refused(self):
  for branch in ['7c','7d','74','75']:
   with self.subTest(branch=branch),self.assertRaises(p.Unsupported):self.run_rule(r=report('2bd78bf2'+branch+'00c3'))
 def test_sub_copy_partial_width_refused(self):
  with self.assertRaises(p.Unsupported):self.run_rule(r=report('2bd7668bf27800c3'))
 def test_sub_copy_wrong_source_refused(self):
  with self.assertRaises(p.Unsupported):self.run_rule(r=report('2bd78bf17800c3'))
 def test_sub_copy_flag_clobber_refused(self):
  with self.assertRaises(p.Unsupported):self.run_rule(r=report('2bd78bf283c2017800c3'))
 def test_incomplete_original_refused(self):
  with self.assertRaises(p.Unsupported):self.run_rule(r=report('85c07c00c30f'))
 def test_wrong_function_identity(self):
  with self.assertRaises(p.Unsupported):self.run_rule(BASE.replace('fn_00001000','fn_00001004'))
 def test_stale_constant_span(self):
  ast=m.parse(BASE,self.folder)
  with self.assertRaises(p.Unsupported):p.rewrite(BASE.replace('-1','-2'),ast,report())
 def test_stale_operator_span(self):
  ast=m.parse(BASE,self.folder)
  with self.assertRaises(p.Unsupported):p.rewrite(BASE.replace('<','>'),ast,report())
 def test_macro_refused(self):
  with self.assertRaises(p.Unsupported):self.run_rule('#define NEG -1\nint fn_00001000(int x){return NEG < x;}')
 def test_alias_signed_int(self):self.run_rule('typedef int signedword;int fn_00001000(signedword x){return -1 < x;}')
if __name__=='__main__':unittest.main()

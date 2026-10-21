"""Bounded forward-region paths, including crossing edges; no game evidence."""
import itertools,json,re,subprocess,unittest
from test_replayable_ir import DOTNET,DLL

@unittest.skipUnless(DLL.exists(),'build changed component first')
class ForwardRegionsTests(unittest.TestCase):
 def structure(self,lines):return json.loads(subprocess.check_output([DOTNET,str(DLL),'recover-ir'],input=json.dumps(dict(forward_cpp_regions=lines)).encode()))
 def original(self,lines,values):
  labels={s[:-2]:i for i,s in enumerate(lines)if s.endswith(':;')};i=0;trace=[]
  while i<len(lines):
   line=lines[i];m=re.fullmatch(r'(?:if \((\w+)\) )?goto (\w+);',line)
   if m and (not m[1]or values[m[1]]):i=labels[m[2]];continue
   if line.startswith('effect_'):trace.append(line)
   i+=1
  return trace
 def structured(self,lines,values):
  trace=[];active=[True];conditions=[]
  for line in map(str.strip,lines):
   m=re.fullmatch(r'if \(!\((\w+)\)\) \{',line)
   if m:conditions.append(not values[m[1]]);active.append(active[-1]and conditions[-1])
   elif line=='} else {':active[-1]=active[-2]and not conditions[-1]
   elif line=='}':active.pop();conditions.pop()
   elif line.startswith('effect_')and active[-1]:trace.append(line)
  self.assertEqual(active,[True]);return trace
 def assert_paths(self,lines):
  r=self.structure(lines);self.assertEqual(r['status'],'structured',r);self.assertFalse(any('goto 'in x for x in r['lines']))
  for bits in itertools.product([False,True],repeat=3):
   values=dict(zip('abc',bits));self.assertEqual(self.original(lines,values),self.structured(r['lines'],values),(values,r))
 def test_nested_diamond_and_shared_forward_join_preserve_all_paths(self):
  self.assert_paths(['effect_start;','if (a) goto L_main_10;','effect_fall;','goto L_main_30;','L_main_10:;','if (b) goto L_main_30;','effect_b;','if (c) goto L_main_30;','effect_c;','L_main_30:;','effect_end;'])
 def test_nested_selection_and_ordered_effects(self):
  self.assert_paths(['if (a) goto L_main_40;','effect_load;','if (b) goto L_main_20;','effect_call_a;','goto L_main_30;','L_main_20:;','effect_call_b;','L_main_30:;','effect_store;','L_main_40:;','effect_final;'])
 def test_redundant_forward_jump_to_next_label(self):
  self.assert_paths(['effect_start;','if (a) goto L_main_10;','L_main_10:;','effect_end;'])
 def test_backward_and_missing_targets_refuse(self):
  for lines in [['L_main_10:;','goto L_main_10;'],['goto L_main_10;']]:self.assertEqual(self.structure(lines)['status'],'unsupported')
 def test_cross_entry_at_exact_arm_start_refuses(self):
  # The first jump must not enter the following conditional's fallthrough arm.
  lines=['if (a) goto L_main_20;','if (b) goto L_main_30;','L_main_20:;','effect_x;','L_main_30:;','effect_y;']
  self.assertEqual(self.structure(lines)['status'],'unsupported')
 def test_cross_exit_refuses(self):
  lines=['if (a) goto L_main_30;','if (b) goto L_main_40;','effect_x;','L_main_30:;','effect_y;','L_main_40:;']
  self.assertEqual(self.structure(lines)['status'],'unsupported')

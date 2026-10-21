"""Lexical ownership from EH tables is separate from residual machine states."""
import copy,json,subprocess,unittest
from test_replayable_ir import DOTNET,DLL
from test_replayable_ebp_source import fixture

@unittest.skipUnless(DLL.exists(),'build changed component first')
class LexicalRegionsTests(unittest.TestCase):
 def recover(self,graph):return json.loads(subprocess.check_output([DOTNET,str(DLL),'recover-ir'],input=json.dumps(dict(ebp_lexical_topology=graph)).encode()))
 def graph(self,triples=((0,0,3),(2,2,3)),unwind=(-1,-1,1,1)):
  g=fixture()['eh']['graph'];g['try_map']['entries']=[dict(try_low=a,try_high=b,catch_high=c)for a,b,c in triples];g['unwind_map']['transitions']=[dict(to_state=i,action_va=0)for i in unwind];g['FuncInfo']['states']=len(unwind);return g
 def test_nested_retry_belongs_to_catch_not_enclosing_try(self):
  r=self.recover(self.graph());self.assertEqual(r['status'],'recovered',r);a,b=r['topology']['scopes'];self.assertEqual((a['parent_region'],a['parent_state']),('function',-1));self.assertEqual((b['parent_try_low'],b['parent_region'],b['parent_state']),(0,'catch',1));self.assertFalse(r['topology']['proof'])
 def test_enclosing_try_is_distinct_despite_same_state_count(self):
  r=self.recover(self.graph(((1,1,2),(0,2,3)),(-1,0,0,-1)));self.assertEqual(r['status'],'recovered',r);a,b=r['topology']['scopes'];self.assertEqual((b['parent_try_low'],b['parent_region'],b['parent_state']),(0,'try',0))
 def test_input_table_order_does_not_change_ownership(self):
  g=self.graph();a=self.recover(g);g['try_map']['entries'].reverse();self.assertEqual(self.recover(g),a)
 def test_unwind_chain_must_correspond_to_scope_parent(self):
  for unwind in [(-1,-1,0,1),(-1,-1,1,0),(-1,0,1,1)]:self.assertEqual(self.recover(self.graph(unwind=unwind))['blocker'],'EBP_lexical_scope_exit_disagrees_with_unwind')
 def test_crossing_intervals_cannot_be_called_nested(self):
  r=self.recover(self.graph(((0,0,2),(1,1,3)),(-1,-1,0,0)));self.assertEqual(r['blocker'],'EBP_lexical_crossing_intervals')
 def test_duplicate_invalid_intervals_actions_and_missing_states_refuse(self):
  variants=[self.graph(((0,0,3),(0,0,3))),self.graph(((0,1,1),)),self.graph(unwind=(-1,-1,2,1))]
  g=self.graph();g['unwind_map']['transitions'][2]['action_va']=123;variants.append(g)
  g=self.graph();g['FuncInfo']['states']=5;variants.append(g)
  for g in variants:self.assertEqual(self.recover(g)['status'],'unsupported')
 def test_sibling_scopes_do_not_acquire_catch_ownership(self):
  r=self.recover(self.graph(((0,0,1),(2,2,3)),(-1,-1,-1,-1)));self.assertEqual(r['status'],'recovered',r);self.assertTrue(all(x['parent_region']=='function'for x in r['topology']['scopes']))

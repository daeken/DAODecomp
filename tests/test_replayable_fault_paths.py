"""Explicit architectural exits remain separate from normal ABI evidence."""
import copy,json,subprocess,unittest
from test_replayable_ir import DLL,DOTNET,node,ty,reg,const,write,tmp
from test_replayable_frame_flow import payload
from test_replayable_conditional import op
from test_replayable_stackargs import row,ret
from test_replayable_terminal_calls import fixture as terminal

def guard(condition):
 return node('IlIf',Cond=condition,Then=[node('IlFault',Architecture='x86',Vector=0)],Else=[])

def guarded():
 return payload([[node('IlLet',Id=0,Val=reg(1)),guard(op('Eq',tmp(0,64),const(0,64),1)),node('IlLet',Id=1,Val=op('UDiv',const(0xffffffff,64),tmp(0,64),64)),guard(op('Ugt',tmp(1,64),const(0xffffffff,64),1)),write(0,node('IlCast',Kind=dict(name='Trunc'),X=tmp(1,64),Ty=ty(32)))],ret(0)],explicit_architectural_faults=True)

@unittest.skipUnless(DLL.exists(),'build changed component first')
class FaultPathsTests(unittest.TestCase):
 def recover(self,p):return json.loads(subprocess.check_output([DOTNET,str(DLL),'recover-ir'],input=json.dumps(p).encode()))
 def test_ordered_fault_exits_and_normal_continuation(self):
  r=self.recover(guarded());self.assertEqual(r['status'],'recovered',r);ir=r['ir'];self.assertEqual(len(ir['normal_paths']),1);faults=ir['fault_paths'];self.assertEqual(len(faults),2)
  self.assertEqual([p['taken'] for p in faults[0]['predicates']],[True]);self.assertEqual([p['taken'] for p in faults[1]['predicates']],[False,True]);self.assertEqual([p['taken'] for p in ir['normal_paths'][0]['predicates']],[False,False])
  for f in faults:self.assertEqual(f['effects'],[]);self.assertEqual(f['registers']['0'],dict(kind='register_input',index=0));self.assertTrue(f['handler_semantics_unknown']);self.assertEqual(f['vector'],0)
 def test_fault_read_precedes_fault_and_is_not_repeated(self):
  p=guarded();p['lift']['instructions'][0]['tree']['Body'][0]['Val']=node('IlLoad',Addr=reg(1),Ty=ty(64));r=self.recover(p);self.assertEqual(r['status'],'recovered',r)
  for path in r['ir']['fault_paths']+r['ir']['normal_paths']:self.assertEqual(sum(e['kind']=='memory_read' for e in path['effects']),1)
 def test_fault_snapshot_invalidates_aliasable_stack_and_retains_store_order(self):
  self.check_fault_stack_freshness(False)
 def test_fault_snapshot_preserves_only_selectively_fresh_words(self):
  self.check_fault_stack_freshness(True)
 def check_fault_stack_freshness(self,fresh_push):
  from test_replayable_frame_flow import push
  from test_replayable_flow_eh import store
  from test_replayable_ir import binary
  effects=[push(const(11)),[store(reg(1),const(99))]]
  if fresh_push:effects.append(push(const(22)))
  effects.extend([[guard(op('Eq',reg(2),const(0,64),1))],[write(4,binary('Add',reg(4),const(8 if fresh_push else 4,64)))],ret(0)])
  r=self.recover(payload(effects,aliasable_memory_stores=True,track_fresh_stack_words=True,explicit_architectural_faults=True));self.assertEqual(r['status'],'recovered',r)
  f=r['ir']['fault_paths'][0];self.assertTrue(f['stack_memory_may_have_changed']);self.assertEqual(f['fresh_stack_words'],[-8] if fresh_push else [])
  self.assertEqual(f['stack']['-4'],dict(kind='unknown',reason='aliased_stack_word'));self.assertEqual(f['stack']['0'],dict(kind='unknown',reason='aliased_stack_word'))
  stores=[e for e in f['effects'] if e['kind'] in ('stack_store','memory_store')];self.assertEqual([e['value']['value'] for e in stores],[11,99,22] if fresh_push else [11,99])
  if fresh_push:self.assertEqual(f['stack']['-8'],dict(kind='constant',value=22,bits=32))
 def test_default_consumers_refuse_and_budget_counts_fault_paths(self):
  p=guarded();p['flow_contract']['explicit_architectural_faults']=False;self.assertEqual(self.recover(p)['blocker'],'flow_architectural_fault_support_required')
  p=guarded();p['flow_contract']['maximum_paths']=2;self.assertEqual(self.recover(p)['blocker'],'flow_path_budget')
 def test_unknown_vectors_or_nonterminal_guard_arms_refuse(self):
  for mode in ('vector','architecture','else','then','width'):
   p=guarded();g=p['lift']['instructions'][0]['tree']['Body'][1]
   if mode=='vector':g['Then'][0]['Vector']=3
   elif mode=='architecture':g['Then'][0]['Architecture']='other'
   elif mode=='else':g['Else']=[write(0,const(1))]
   elif mode=='then':g['Then'].append(write(0,const(1)))
   else:g['Cond']['Ty']=ty(32)
   self.assertEqual(self.recover(p)['status'],'unsupported',mode)
 def test_normal_only_cleanup_retains_complete_fault_prefixes(self):
  p=guarded();p=dict(normal_return_evidence=True,target=p['lift']['instructions'][0]['pc'],lift=p['lift']);r=self.recover(p);self.assertEqual(r['status'],'recovered',r);ir=r['ir'];self.assertEqual(ir['cleanup_bytes'],0);self.assertEqual(len(ir['architectural_faults']),2)
  self.assertEqual(len(ir['architectural_faults'][1]['preceding_effects']),3);self.assertEqual(ir['architectural_faults'][1]['preceding_effects'][1]['type'],'LiftIl.IlIf');self.assertFalse(ir['proof'])
 def test_terminal_walker_cannot_drop_a_fault_path(self):
  p=terminal();p['lift']['instructions'][0]['tree']['Body']=[guard(const(1,1))];self.assertEqual(self.recover(p)['blocker'],'terminal_architectural_fault_path_unproven')
 def test_mixed_return_throw_requires_exact_bound_terminal(self):
  p=terminal();base=p['target'];p['normal_return_evidence']=True;p.pop('terminal_callee');p['lift']['instructions'][0]['tree']['Body']=[node('IlBranch',Kind=dict(name='CondJmp'),Cond=const(1,1),Target=const(base+6,32))];p['lift']['instructions'].append(row(base+6,ret(0),'c3'))
  r=self.recover(p);self.assertEqual(r['status'],'recovered',r);self.assertEqual(r['ir']['exceptional_call_sites'],[base+1]);self.assertEqual(r['ir']['return_sites'],1)
  p.pop('runtime_terminal_evidence');r=self.recover(p);self.assertEqual(r['status'],'recovered',r);self.assertEqual(r['ir']['exceptional_call_sites'],[]) # ordinary call now really falls through to the RET
  p['lift']['instructions'][-1]=row(base+6,[]);self.assertEqual(self.recover(p)['blocker'],'callee_falls_out_of_range')
 def test_normal_cleanup_rejects_unconditional_or_nested_fault(self):
  p=guarded();p=dict(normal_return_evidence=True,target=p['lift']['instructions'][0]['pc'],lift=p['lift'])
  p['lift']['instructions'][0]['tree']['Body']=[node('IlFault',Architecture='x86',Vector=0)];self.assertEqual(self.recover(p)['status'],'unsupported')
  p['lift']['instructions'][0]['tree']['Body']=[node('IlLet',Id=0,Val=node('IlFault',Architecture='x86',Vector=0))];self.assertEqual(self.recover(p)['blocker'],'nested_architectural_control_effect')
 def test_constant_guard_selects_only_actual_effects_and_symbolic_guard_refuses(self):
  p=payload([[node('IlIf',Cond=const(1,1),Then=[write(0,const(7))],Else=[node('IlUndefined',Reason='not executed',Ty=ty(32))])],ret(0)],constant_condition_effects=True)
  r=self.recover(p);self.assertEqual(r['status'],'recovered',r);self.assertEqual(r['ir']['normal_paths'][0]['exit']['return']['value'],7)
  p['lift']['instructions'][0]['tree']['Body'][0]['Cond']=op('Eq',reg(1),const(0,64),1);self.assertEqual(self.recover(p)['blocker'],'flow_symbolic_effect_condition_unsupported')
 def test_unsupported_wide_fault_guard_refuses(self):
  p=guarded();p['lift']['instructions'][0]['tree']['Body'][0]['Val']=const(1,128);self.assertEqual(self.recover(p)['blocker'],'flow_unsupported_width')
 def test_effect_comparator_refuses_conditional_architectural_exits(self):
  from tools.replayable.effect_relation import State,Terms
  from rapid_object.encoding_equivalence import Refusal
  with self.assertRaisesRegex(Refusal,'effect_unsupported_statement:IlIf'):
   State(Terms()).run([dict(tree=dict(Body=[guard(const(1,1))]),effect_segments=dict(read='DS',write='DS'))])
 def test_owned_range_graph_preserves_fault_edge_and_guard_evidence(self):
  from test_replayable_owned_ranges import envelope
  p=envelope();p['ranges'][0]['lift']['instructions'][0]['tree']['Body'].insert(0,guard(const(1,1)))
  r=self.recover(dict(owned_ranges=True,lift=p));self.assertEqual(r['status'],'inspected',r);self.assertEqual(r['ir']['edges'][0]['kind'],'architectural_fault');self.assertEqual(len(r['ir']['architectural_faults']),1);self.assertTrue(r['ir']['architectural_faults'][0]['handler_semantics_unknown'])

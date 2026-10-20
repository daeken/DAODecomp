"""Open bitvector/effect boundaries; no original-function acceptance fixtures."""
import copy,shutil,unittest
from tools.replayable.effect_relation import prove_window,Refusal
from test_replayable_ir import node,const,reg,write,ty
from test_replayable_loops import binary,reg32

def cast(x,bits,kind='Zext'):return node('IlCast',Kind=dict(name=kind),X=x,Ty=ty(bits))
def address(base,offset=0):return cast(binary('Add',reg32(base),const(offset)),64)
def load(base,offset=0):return node('IlLoad',Addr=address(base,offset),Ty=ty(32))
def put(index,value):return write(index,cast(value,64))
def flag(index,value):return node('IlWriteReg',Kind=dict(name='Eflags'),Idx=index,Val=value)
def rows(*bodies):return [dict(pc=0x500000+i,effect_segments=dict(read='DS',write='DS'),tree=dict(Body=body)) for i,body in enumerate(bodies)]
def add(index,value):
 result=binary('Add',reg32(index),value);return [node('IlLet',Id=0,Val=result),flag(0,binary('Ult',node('IlTmp',Id=0,Ty=ty(32)),reg32(index),1)),put(index,node('IlTmp',Id=0,Ty=ty(32)))]
def sum_pair(final_flags=True):
 a=rows([put(0,load(4,4))],add(0,reg32(3)),add(0,reg32(7)));b=rows([put(0,binary('Add',reg32(3),reg32(7)))],add(0,load(4,4)))
 if final_flags:a+=rows(add(2,reg32(3)));b+=rows(add(2,reg32(3)))
 return a,b

@unittest.skipUnless(shutil.which('z3'),'existing solver unavailable; no install')
class EffectRelationTests(unittest.TestCase):
 def prove(self,a,b,live=range(8),context='abi-event-only'):return prove_window(a,b,live,shutil.which('z3'),fault_context=context,fault_live_registers=[3,5,6,7])
 def test_narrow_fault_profile_requires_explicit_register_contract(self):
  a,b=sum_pair()
  with self.assertRaisesRegex(Refusal,'explicit_fault_register_contract'):
   prove_window(a,b,range(8),shutil.which('z3'),fault_context='abi-event-only')
 def test_wrapping_sum_and_dead_intermediate_flags(self):
  a,b=sum_pair();x=self.prove(a,b);self.assertEqual(x['status'],'unsat');self.assertEqual(x['ordered_memory_events'],1);self.assertFalse(x['whole_function_equivalence_proven']);self.assertFalse(x['full_fault_register_context_checked'])
 def test_live_carry_difference_not_erased(self):
  a,b=sum_pair(False);self.assertEqual(self.prove(a,b)['status'],'sat')
 def test_wrong_incoming_register_is_not_equivalent(self):
  a,b=sum_pair();b[0]['tree']['Body'][0]=put(0,binary('Add',reg32(1),reg32(7)));self.assertEqual(self.prove(a,b)['status'],'sat')
 def test_fault_context_difference_remains_observable_in_strict_model(self):
  a,b=sum_pair();self.assertEqual(self.prove(a,b,context='full-registers')['status'],'sat')
 def test_memory_read_order_is_not_commutative(self):
  a=rows([put(0,load(6))],[put(1,load(7))]);b=rows([put(1,load(7))],[put(0,load(6))]);self.assertEqual(self.prove(a,b)['status'],'sat')
 def test_nonvolatile_fault_registers_are_preserved_even_in_abi_event_profile(self):
  a=rows([put(0,load(6))],add(3,const(1)));b=rows(add(3,const(1)),[put(0,load(6))]);self.assertEqual(self.prove(a,b)['status'],'sat')
 def test_may_alias_read_write_order_refuses(self):
  store=node('IlStore',Addr=address(7),Val=reg32(0));a=rows([put(0,load(6))],[store]);b=rows([store],[put(0,load(6))])
  with self.assertRaisesRegex(Refusal,'memory_event_order'):self.prove(a,b)
 def test_call_clobbers_and_undefined_values_refuse(self):
  for body in ([node('IlBranch',Kind=dict(name='Call'),Target=const(0x502000),Cond=None)],[put(0,node('IlUndefined',Reason='same reason is not a value',Ty=ty(32)))]):
   with self.subTest(body=body),self.assertRaises(Refusal):self.prove(rows(body),rows(body))
 def test_unwrapped_address_and_unbounded_shift_refuse(self):
  for value in (node('IlLoad',Addr=reg(6),Ty=ty(32)),binary('Shr',reg32(0),reg32(1))):
   with self.assertRaises(Refusal):self.prove(rows([put(0,value)]),rows([put(0,value)]))
 def test_register_liveness_is_explicit_not_universal(self):
  a=rows([put(0,const(2))]);b=rows([put(0,const(2)),put(1,const(19))]);self.assertEqual(self.prove(a,b,live=[0,2,3,4,5,6,7])['status'],'unsat');self.assertEqual(self.prove(a,b)['status'],'sat')
 def test_equal_address_with_different_default_segments_refuses(self):
  a=rows([put(0,load(6))]);b=copy.deepcopy(a);b[0]['effect_segments']['read']='SS'
  with self.assertRaisesRegex(Refusal,'memory_segment_difference'):self.prove(a,b)
 def test_same_ordered_aliases_need_no_nonalias_assumption(self):
  a=rows([put(0,load(6))],[node('IlStore',Addr=address(7),Val=reg32(0))],[put(2,load(6))]);self.assertEqual(self.prove(a,copy.deepcopy(a))['status'],'unsat')

class EffectCfgTests(unittest.TestCase):
 def pair(self,a,b):
  from tools.replayable.effect_relation import pair_cfg
  return pair_cfg(bytes.fromhex(a),bytes.fromhex(b),0x500000,[0,3,4,5,6,7])
 def test_unequal_length_direct_control_graph_pairs_without_byte_normalization(self):
  pairs,mapping=self.pair('8b44240403c303c703d3c3','8d041f0344240403d3c3');self.assertEqual(len(pairs),1);self.assertFalse(pairs[0]['unchanged']);self.assertIn(0,pairs[0]['live_registers']);self.assertEqual(mapping,{0x500000:0x500000})
 def test_unknown_call_requires_every_gpr_at_boundary(self):
  pairs,_=self.pair('8b44240403c303c703d3e800010000c3','8d041f0344240403d3e801010000c3');changed=next(p for p in pairs if not p['unchanged']);self.assertEqual(changed['live_registers'],list(range(8)))
 def test_changed_call_target_not_hidden_by_control_relocation(self):
  with self.assertRaisesRegex(Refusal,'call_target'):self.pair('03c3e800010000c3','03c7e800020000c3')
 def test_interior_target_indirect_call_and_prefix_return_refuse(self):
  for a,b in (('ebff','ebff'),('ff10c3','ff10c3'),('66c3','c3')):
   with self.subTest(a=a),self.assertRaises(Refusal):self.pair(a,b)
 def test_unreachable_tail_and_unsupported_external_observer_refuse(self):
  for a,b in (('c3c3','c3c3'),('ccc3','ccc3')):
   with self.subTest(a=a),self.assertRaises(Refusal):self.pair(a,b)

@unittest.skipUnless(shutil.which('z3'),'existing solver unavailable')
class EffectCertificateBoundaryTests(unittest.TestCase):
 def fixture(self):
  from test_replayable_abi_effects import mock_effect_lift
  a=bytes.fromhex('8b44240403c303c703d3c3');b=bytes.fromhex('8d041f0344240403d3c3');return a,b,[mock_effect_lift(a,0x500000),mock_effect_lift(b,0x500000)]
 def certify(self,lifts):
  from tools.replayable.effect_relation import certify_typed_effects
  a,b,_=self.fixture();return certify_typed_effects(a,b,pc=0x500000,lifts=lifts,solver=shutil.which('z3'),exit_live_registers=[0,3,4,5,6,7],fault_context='abi-event-only',fault_live_registers=[3,5,6,7])
 def test_missing_bad_stale_or_opaque_lift_never_certifies(self):
  a,b,lifts=self.fixture()
  for mode in ('missing','mode','raw','pc','opaque','undefined'):
   x=copy.deepcopy(lifts)
   if mode=='missing':x=[]
   elif mode=='mode':x[1]['mode']='Bits64'
   elif mode=='raw':x[1]['instructions'][0]['raw_hex']='00'
   elif mode=='pc':x[1]['pc']+=1
   elif mode=='opaque':x[1]['opaque_instructions']=1
   else:x[1]['instructions'][0]['tree']['Body'][0]['Val']=node('IlUndefined',Reason='unknown',Ty=ty(64))
   with self.subTest(mode=mode),self.assertRaises(Refusal):self.certify(x)
 def test_solver_unknown_timeout_and_json_roundtrip(self):
  import json,subprocess
  from unittest.mock import patch
  _,_,lifts=self.fixture();certificate=self.certify(lifts);self.assertEqual(certificate,json.loads(json.dumps(certificate)))
  with patch('tools.replayable.effect_relation.subprocess.run',return_value=subprocess.CompletedProcess([],0,'unknown\n','')),self.assertRaisesRegex(Refusal,'not_proved:unknown'):self.certify(lifts)
  with patch('tools.replayable.effect_relation.subprocess.run',side_effect=subprocess.TimeoutExpired('solver',6)),self.assertRaises(subprocess.TimeoutExpired):self.certify(lifts)

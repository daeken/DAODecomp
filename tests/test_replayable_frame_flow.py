"""Bounded architecture frame-flow cases, not EH/source acceptance evidence."""
import copy,json,subprocess,unittest
from test_replayable_ir import DLL,DOTNET,node,ty,reg,const,binary,write,tmp
from test_replayable_stackargs import row,ret,callee
from test_replayable_conditional import call,flag,fw,op
from test_replayable_flow_eh import load,store,push,simple
from tools.replayable.range_lift import combine


def contract(**options):
 return dict(abi=dict(id='open-frame-v1',return_register=0,argument_registers=[1],volatile_registers=[0,1,2],preserved_registers=[3,5,6,7]),flat_data_and_stack_segments=True,normal_return_abi_selected=True,**options)
def payload(bodies,**options):
 p=simple(bodies);p.update(flow_paths=True,callee_lifts=[],flow_contract=contract(**options));return p

def pop(i):
 return [node('IlLet',Id=0,Val=load(reg(4))),write(4,binary('Add',reg(4),const(4,64))),write(i,tmp(0,32))]

@unittest.skipUnless(DLL.exists(),'build changed component first')
class FrameFlowTests(unittest.TestCase):
 def recover(self,p):
  return json.loads(subprocess.check_output([DOTNET,str(DLL),'recover-ir'],input=json.dumps(p).encode()))
 def test_ebp_alias_and_signed_displacement_preserve_local_and_saved_register(self):
  for bits in (32,64):
   address=binary('Add',reg(5),const((1<<bits)-4,bits))
   p=payload([push(reg(5)),[write(5,reg(4))],[write(4,binary('Sub',reg(4),const(4,64)))],[store(address,const(42))],[write(0,load(address))],[write(4,reg(5))],pop(5),ret(0)],signed_frame_displacements=True)
   r=self.recover(p);self.assertEqual(r['status'],'recovered',r);self.assertEqual(r['ir']['normal_paths'][0]['exit']['return']['value'],42);self.assertTrue(r['ir']['exceptional_semantics_unknown'])
   p['flow_contract']['signed_frame_displacements']=False;self.assertEqual(self.recover(p)['blocker'],'flow_stack_adjustment_budget')
 def test_displacement_budget_and_partial_unknown_local_refuse(self):
  for off in (-4097,4097):
   p=payload([push(reg(5)),[write(5,reg(4))],[write(0,binary('Add',reg(5),const(off&0xffffffff,32)))],[write(4,reg(5))],pop(5),ret(0)],signed_frame_displacements=True)
   self.assertEqual(self.recover(p)['blocker'],'flow_stack_adjustment_budget')
 def test_range_jump_skips_gap_without_invented_fallthrough(self):
  # Jump lands beyond the beginning of the second range. Its first instruction
  # is reached on the other branch; physical previous row is NOT the executed edge.
  rows=[row(0x1000,[node('IlBranch',Kind=dict(name='CondJmp'),Cond=const(1,1),Target=const(0x1010,64))],'740e'),row(0x1002,[node('IlBranch',Kind=dict(name='Jmp'),Cond=None,Target=const(0x1011,64))],'eb0d'),row(0x1010,[write(0,const(1))]),row(0x1011,ret(0),'c3')]
  def part(rs):return dict(mode='Bits32',pc=rs[0]['pc'],byte_length=sum(r['length']for r in rs),decoded_bytes=sum(r['length']for r in rs),decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=rs)
  p=dict(flow_paths=True,callee_lifts=[],flow_contract=contract(explicit_owned_ranges=True),lift=combine([part(rows[:2]),part(rows[2:])],[(0x1000,0x1003),(0x1010,0x1011)],0))
  r=self.recover(p);self.assertEqual(r['status'],'recovered',r);self.assertEqual(len(r['ir']['normal_paths']),2)
  p['lift']['ranges'][0]['lift']['instructions'][1]['tree']['Body']=[write(0,const(1))]
  self.assertEqual(self.recover(p)['blocker'],'flow_fallthrough_across_unowned_gap')
 def test_multiply_wrap_and_dead_undefined_flag_preserved(self):
  undefined=node('IlUndefined',Reason='unsigned multiply undefined ZF',Ty=ty(1))
  p=payload([[write(0,op('Mul',const(0xffffffff),const(3),32)),fw(6,undefined)],ret(0)],deferred_undefined_flags=True)
  r=self.recover(p);self.assertEqual(r['status'],'recovered',r);self.assertEqual(r['ir']['normal_paths'][0]['exit']['return']['value'],0xfffffffd);self.assertEqual(r['ir']['normal_paths'][0]['exit']['flags']['6']['kind'],'unknown')
  p['flow_contract']['deferred_undefined_flags']=False;self.assertIn('flow_undefined_architectural_value',self.recover(p)['blocker'])
 def test_undefined_flag_use_refuses_but_later_defined_write_replaces_it(self):
  first=[fw(6,node('IlUndefined',Reason='undefined',Ty=ty(1)))];last=[write(0,node('IlCast',Kind=dict(name='Zext'),X=flag(6),Ty=ty(32)))]
  p=payload([first,last,ret(0)],deferred_undefined_flags=True);self.assertEqual(self.recover(p)['blocker'],'flow_undefined_flag_observed')
  p=payload([first,[fw(6,const(1,1))],last,ret(0)],deferred_undefined_flags=True);self.assertEqual(self.recover(p)['ir']['normal_paths'][0]['exit']['return']['value'],1)
 def test_alias_store_fresh_push_call_does_not_restore_old_saved_stack(self):
  p=payload([[store(reg(1),const(7))],push(const(12)),call(0x502002,0x503000),[write(4,binary('Add',reg(4),const(4,64)))],ret(0)],aliasable_memory_stores=True,track_fresh_stack_words=True)
  # simple() uses one-byte fixture rows; CALL's actual encoded length is five.
  rs=p['lift']['instructions'];rs[2]=row(0x502002,call(0x502002,0x503000),'e800000000');rs[3]['pc']=0x502007;rs[4]['pc']=0x502008
  p['callee_lifts']=[dict(target=0x503000,lift=callee(0))]
  r=self.recover(p);self.assertEqual(r['status'],'recovered',r);path=r['ir']['normal_paths'][0];self.assertEqual(next(e for e in path['effects']if e['kind']=='external_call')['call']['arguments'][0]['value'],12);self.assertTrue(path['exit']['stack_memory_may_have_changed']);self.assertEqual(path['exit']['return_target']['kind'],'memory_read')
  p['flow_contract']['track_fresh_stack_words']=False;self.assertEqual(self.recover(p)['blocker'],'flow_call_after_aliasable_store_requires_fresh_argument_state')
 def test_alias_store_after_push_does_not_reuse_stale_argument(self):
  p=payload([push(const(12)),[store(reg(1),const(7))],call(0x502002,0x503000),[write(4,binary('Add',reg(4),const(4,64)))],ret(0)],aliasable_memory_stores=True,track_fresh_stack_words=True)
  rs=p['lift']['instructions'];rs[2]=row(0x502002,call(0x502002,0x503000),'e800000000');rs[3]['pc']=0x502007;rs[4]['pc']=0x502008;p['callee_lifts']=[dict(target=0x503000,lift=callee(0))]
  self.assertEqual(self.recover(p)['blocker'],'flow_outgoing_argument_alias_unknown')
 def test_opaque_callee_cannot_be_a_successful_normal_return(self):
  p=payload([call(0x502000,0x503000),ret(0)]);p['lift']['instructions'][0]=row(0x502000,call(0x502000,0x503000),'e800000000');p['lift']['instructions'][1]['pc']=0x502005
  c=callee(0);c['opaque_instructions']=1;p['callee_lifts']=[dict(target=0x503000,lift=c)];self.assertEqual(self.recover(p)['blocker'],'incomplete_forwarding_evidence')

class RangeCalleeInspectionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  import importlib.util
  from pathlib import Path
  spec=importlib.util.spec_from_file_location('range_callee_adapter',Path(__file__).resolve().parents[1]/'tools/decompilation-mcp/replayable_adapter.py');cls.adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.adapter)
 def test_split_range_direct_targets_do_not_flatten_the_gap(self):
  caller=dict(lift=dict(schema='sharpretro_owned_ranges_v1',ranges=[dict(lift=dict(instructions=[row(0x501000,[],'e8fb1f0000')])),dict(lift=dict(instructions=[row(0x501010,[],'e8eb2f0000')]))]))
  self.assertEqual(self.adapter.direct_call_targets(caller),[0x503000,0x504000])
 def test_inspection_retains_opaque_dependency_but_production_still_refuses(self):
  import tempfile
  from pathlib import Path
  from unittest.mock import patch
  caller=dict(lift=dict(instructions=[row(0x501000,[],'e8fb1f0000')]),image_base=0x500000,image_end=0x510000,binary_slice_sha256='b'*64)
  c=callee(0);c['opaque_instructions']=1;derived=dict(lift=c,image_base=0x500000,image_end=0x510000,binary_slice_sha256='c'*64,lifter_manifest_sha256='d'*64)
  def lift(request):return caller if request['rva']==0x1000 else derived
  with tempfile.TemporaryDirectory()as t:
   p=Path(t)/'inventory.json';p.write_text(json.dumps(dict(module_sha256='a'*64,functions=[dict(rva=0x3000)])));request=dict(rva=0x1000,project=dict(module_sha256='a'*64,inventory=str(p)),recipe=dict(compiler_profile='vc8-x86-flat32-EH-two-exit-v1'))
   with patch.object(self.adapter,'lift',side_effect=lift):
    with self.assertRaisesRegex(ValueError,'incomplete_forwarding_evidence'):self.adapter.lift_callees(request)
    r=self.adapter.lift_callees(request,inspection=True)
   self.assertTrue(r['inspection_only']);self.assertEqual(r['callees'][0]['lift']['opaque_instructions'],1);self.assertEqual(r['blockers'][0]['target'],0x503000);self.assertFalse(r['proof'])

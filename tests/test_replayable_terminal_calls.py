"""Open terminal-edge/identity boundaries; no original-game/compiler credit."""
import copy,json,struct,subprocess,unittest
from test_replayable_ir import DLL,DOTNET,node,const
from test_replayable_stackargs import row,ret
from test_replayable_conditional import call

def fixture():
 base=0x504000;target=0x507000;pc=base+1;raw=(b'\xe8'+struct.pack('<i',target-pc-5)).hex()
 lift=dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=[row(base,[]),row(pc,call(pc,target),raw)])
 runtime=dict(target=target,profile='vc8-CxxThrowException-noncontinuable-v1',bytes_sha256='1'*64,complete_bytes_compared=True,normal_return_supported=False,library_sha256='2'*64,object_sha256='3'*64,assumptions=['open synthetic profile evidence, not a real runtime identity'],effects='unknown exceptional effects',proof=False)
 return dict(terminal_callee=True,target=base,lift=lift,runtime_terminal_evidence=runtime)

@unittest.skipUnless(DLL.exists(),'build changed component first')
class TerminalCallTests(unittest.TestCase):
 def recover(self,p):return json.loads(subprocess.check_output([DOTNET,str(DLL),'recover-ir'],input=json.dumps(p).encode()))
 def test_complete_call_terminal_has_no_fabricated_cleanup_or_value(self):
  x=self.recover(fixture());self.assertEqual(x['status'],'recovered',x);ir=x['ir'];self.assertEqual(ir['terminal_call_sites'],[0x504001]);self.assertTrue(ir['memory_effects_unknown']);self.assertTrue(ir['exceptional_destinations_unknown']);self.assertNotIn('cleanup_bytes',ir);self.assertNotIn('return_value',ir);self.assertFalse(ir['proof'])
 def test_name_or_no_RET_does_not_make_unknown_call_terminal(self):
  p=fixture();p['runtime_terminal_evidence']['target']+=16;self.assertEqual(self.recover(p)['blocker'],'terminal_unproven_fallthrough')
  p=fixture();p['lift']['instructions'][-1]=row(0x504001,ret(0),'c3');self.assertEqual(self.recover(p)['blocker'],'terminal_normal_return_or_unknown_exit')
 def test_indirect_propagated_wrong_target_and_prefix_refuse(self):
  for mode in ('typed','raw','prefix','far'):
   p=fixture();r=p['lift']['instructions'][-1]
   if mode=='typed':r['tree']['Body'][0]['Val']=const(0x507004)
   elif mode=='raw':r['raw_hex']='e801000000'
   elif mode=='prefix':r['decoded']['P']['Rep']=True
   else:r['raw_hex']='ff10000000'
   self.assertEqual(self.recover(p)['status'],'unsupported',mode)
 def test_unreachable_extra_bytes_and_uncertainty_refuse(self):
  for mode in ('extra','opaque','partial','unbound','proof','normal','profile'):
   p=fixture()
   if mode=='extra':p['lift']['instructions'].append(row(0x504006,[]))
   elif mode=='opaque':p['lift']['opaque_instructions']=1
   elif mode=='partial':p['lift']['decode_complete']=False
   elif mode=='unbound':p['runtime_terminal_evidence']['library_sha256']=''
   elif mode=='proof':p['runtime_terminal_evidence']['proof']=True
   elif mode=='normal':p['runtime_terminal_evidence']['normal_return_supported']=True
   else:p['runtime_terminal_evidence']['profile']='guess-from-name'
   self.assertEqual(self.recover(p)['status'],'unsupported',mode)
 def test_all_paths_must_reach_certified_terminal_no_loop_shortcut(self):
  p=fixture();base=p['target'];p['lift']['instructions'][0]['tree']['Body']=[node('IlBranch',Kind=dict(name='CondJmp'),Target=const(base+6,32),Cond=const(1,1))];p['lift']['instructions'].append(row(base+6,ret(0),'c3'));self.assertEqual(self.recover(p)['blocker'],'terminal_normal_return_or_unknown_exit')
  p=fixture();p['lift']['instructions'][0]['tree']['Body']=[node('IlBranch',Kind=dict(name='Jmp'),Target=const(p['target'],32),Cond=None)];self.assertEqual(self.recover(p)['blocker'],'terminal_backedge_not_proven')

class RuntimeBindingTests(unittest.TestCase):
 def setup_case(self):
  from types import SimpleNamespace
  from tools.replayable.terminal_calls import bind_complete_function
  code=b'\xb8'+b'\0'*4+b'\xc3';ref=b'\xb8'+struct.pack('<I',0x604000)+b'\xc3';reader=SimpleNamespace(pe=SimpleNamespace(image_base=0x500000),read=lambda address,length,executable:ref)
  definition=dict(bytes_hex=code.hex(),relocations=[dict(symbol='open-data',kind=6,addend_u32=0,offset=1)],library_sha256='a'*64,object_sha256='b'*64,symbol='open-function');entry=lambda r:dict(body_ranges=[dict(start_rva=r,end_rva_inclusive=r+5)])
  return bind_complete_function,definition,reader,{0x2000:entry(0x2000)}, {'open-data':0x604000},entry
 def test_unique_complete_match_not_target_selection(self):
  bind,d,r,entries,symbols,entry=self.setup_case();x=bind(d,r,entries,symbols);self.assertEqual(x['target'],0x502000);self.assertTrue(x['complete_bytes_compared']);entries[0x3000]=entry(0x3000)
  with self.assertRaisesRegex(ValueError,'nonunique'):bind(d,r,entries,symbols)
 def test_wrong_dependency_partial_range_and_relocation_refuse(self):
  bind,d,r,entries,symbols,entry=self.setup_case()
  for mode in ('target','missing','range','kind','addend'):
   dx=copy.deepcopy(d);ex=copy.deepcopy(entries);sx=dict(symbols)
   if mode=='target':sx['open-data']+=4
   elif mode=='missing':sx={}
   elif mode=='range':ex[0x2000]['body_ranges'][0]['end_rva_inclusive']-=1
   elif mode=='kind':dx['relocations'][0]['kind']=20
   else:dx['relocations'][0]['addend_u32']=1
   with self.subTest(mode=mode),self.assertRaises(ValueError):bind(dx,r,ex,sx)

def mutable_fixture():
 from test_replayable_ir import reg,write,ty
 from test_replayable_loops import binary,reg32
 from test_replayable_byvalue import load,push
 from test_replayable_conditional import fw,flag
 base=0x508000;target=0x509800;rows=[]
 def add(body,raw='90'):
  pc=base+sum(r['length'] for r in rows);rows.append(row(pc,body,raw));return pc
 add(push(reg32(6)),'56');add([write(6,reg(1))],'8bf1');add([write(0,load(binary('Add',reg(4),const(8,64))))],'8b442408')
 add([fw(0,const(0,1)),fw(6,binary('Eq',reg32(0),const(0),1))],'85c0');branch=len(rows);add([node('IlBranch',Kind=dict(name='CondJmp'),Cond=flag(6),Target=const(0,32))],'7400')
 add(push(load(binary('Add',reg(4),const(12,64)))),'ff74240c');pc=base+sum(r['length'] for r in rows);add(call(pc,target),(b'\xe8'+struct.pack('<i',target-pc-5)).hex());add([write(0,const(17))],'b811000000');cleanup=add([write(4,binary('Add',reg(4),const(4,64)))],'83c404');join=add([write(2,binary('Add',reg(6),const(4,64)))],'8d5604');rows[branch]['tree']['Body'][0]['Target']=const(join,32)
 add([node('IlStore',Addr=binary('Add',reg(4),const(8,64)),Val=reg32(2))],'89542408');add([write(2,load(binary('Add',reg(4),const(8,64))))],'8b542408');add([node('IlStore',Addr=binary('Add',reg(6),const(12,64)),Val=reg32(0))],'89460c');add([write(0,reg32(6))],'8bc6');add([node('IlLet',Id=0,Val=load(reg(4))),write(4,binary('Add',reg(4),const(4,64))),write(6,node('IlTmp',Id=0,Ty=ty(32)))],'5e');add(ret(8),'c20800')
 runtime=fixture()['runtime_terminal_evidence'];p=dict(structured_memory=True,rva=0x8000,image_base=0x500000,image_end=0x510000,module='open.exe',runtime_terminal_evidence=runtime,lift=dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=rows),callee_lifts=[dict(target=target,lift=dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=[row(target,ret(0),'c3')]))]);return p,cleanup


def mixed_width_fixture(bits):
 from test_replayable_ir import ty,write,reg
 from test_replayable_loops import binary,reg32
 from test_replayable_byvalue import load
 p,_=mutable_fixture();rows=p['lift']['instructions'];rows[12]['tree']['Body'][0]['Val']=reg32(2)
 # Observe the complete second incoming word on both edges, without guessing
 # that RET8 alone established any input extent.
 oldtarget=int(rows[4]['tree']['Body'][0]['Target']['Bits']['decimal']);rows.insert(3,row(rows[3]['pc'],[write(2,load(binary('Add',reg(4),const(12,64))))],'8b54240c'))
 for rr in rows[4:]:rr['pc']+=4
 shift=4
 if bits==8:
  first=rows[2]['tree']['Body'][0]['Val'];first['Ty']=ty(8);rows[2]['tree']['Body'][0]['Val']=node('IlCast',Kind=dict(name='Zext'),X=first,Ty=ty(32));rows[2]['raw_hex']='0fb6442408';rows[2]['length']=5
  for rr in rows[3:]:rr['pc']+=1
  shift+=1
 branch=rows[5];branch['tree']['Body'][0]['Target']=const(oldtarget+shift,32);branch['raw_hex']=(b'\x74'+struct.pack('b',oldtarget+shift-branch['pc']-2)).hex()
 for rr in rows:
  if rr['raw_hex'].startswith('e8'):
   rr['raw_hex']=(b'\xe8'+struct.pack('<i',0x509800-rr['pc']-5)).hex()
   for n in rr['tree']['Body']:
    if n['type']=='LiftIl.IlStore':n['Val']=const(rr['pc']+rr['length'],32)
 return p


def terminal_width_fixture(bits):
 from test_replayable_ir import write,reg
 from test_replayable_loops import binary,reg32
 from test_replayable_byvalue import load,push
 from test_replayable_conditional import fw,flag
 p=mixed_width_fixture(bits);rows=p['lift']['instructions']
 for rr in rows:
  if rr['raw_hex'] in ('89542408','8b542408'):rr['tree']['Body']=[write(2,const(0))];rr['raw_hex']='ba00000000';rr['length']=5
 rows[4:4]=[row(0xdead0000,[fw(6,binary('Eq',reg32(2),const(0),1))],'85d2'),row(0xdead0002,[node('IlBranch',Kind=dict(name='CondJmp'),Cond=flag(6),Target=const(0xdead0100,32))],'7400')]
 rows.extend([row(0xdead0100,[node('IlStore',Addr=binary('Add',reg(4),const(8,64)),Val=const(0x12345678))],'c744240878563412'),row(0xdead0110,[write(2,load(binary('Add',reg(4),const(8,64))))],'8b542408'),row(0xdead0120,push(reg32(2)),'52'),row(0xdead0130,call(0xdead0130,0x509900),'e800000000'),row(0xdead0140,[write(4,binary('Add',reg(4),const(4,64)))],'83c404'),row(0xdead0150,call(0xdead0150,0x504000),'e800000000')])
 mapping={};pc=0x508000
 for rr in rows:mapping[rr['pc']]=pc;pc+=rr['length']
 for rr in rows:
  rr['pc']=mapping[rr['pc']]
  for n in rr['tree']['Body']:
   if n['type']=='LiftIl.IlBranch':
    kind=n['Kind']['name']
    if kind in ('Jmp','CondJmp'):
     target=mapping[int(n['Target']['Bits']['decimal'])];n['Target']=const(target,32);rr['raw_hex']=(b'\x74'+struct.pack('b',target-rr['pc']-2)).hex()
    elif kind=='Call':
     target=int(rr['tree']['Body'][0]['Val']['Bits']['decimal']);rr['raw_hex']=(b'\xe8'+struct.pack('<i',target-rr['pc']-5)).hex()
     for x in rr['tree']['Body']:
      if x['type']=='LiftIl.IlStore':x['Val']=const(rr['pc']+5,32)
 p['callee_lifts'].append(dict(target=0x504000,lift=fixture()['lift']));p['callee_lifts'].append(dict(target=0x509900,lift=dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=[row(0x509900,ret(0),'c3')])));return p

@unittest.skipUnless(DLL.exists(),'build changed component first')
class MutableFlowTests(unittest.TestCase):
 def recover(self,p):return json.loads(subprocess.check_output([DOTNET,str(DLL),'recover-ir'],input=json.dumps(p).encode()))
 def test_delayed_cleanup_incoming_word_and_shared_join(self):
  p,cleanup=mutable_fixture();x=self.recover(p);self.assertEqual(x['status'],'generated',x);f=x['ir']['flow'];self.assertEqual(len(f['normal_paths']),2);call_=next(e['call'] for path in f['normal_paths'] for e in path['effects'] if e['kind']=='external_call');self.assertEqual((call_['callee_cleanup'],call_['caller_cleanup'],call_['caller_cleanup_pc'],len(call_['arguments'])),(0,4,cleanup,1));self.assertTrue(call_['memory_effects_unknown']);self.assertFalse(call_['formal_arity_known']);self.assertEqual(x['source'].count('fn_00009800('),2);self.assertEqual(x['source'].count('write_word('),2);self.assertNotIn('= 0; // unknown',x['source']);self.assertIn('arg_0 =',x['source'])
  self.assertTrue(any(e['kind']=='incoming_store' for path in f['normal_paths'] for e in path['effects']));self.assertTrue(any(e['kind']=='incoming_slot_read' for path in f['normal_paths'] for e in path['effects']))
 def test_unsigned_zero_form_requires_same_instruction_false_carry_and_captured_word(self):
  from test_replayable_ir import ty
  from test_replayable_loops import binary,reg32
  from test_replayable_conditional import fw,flag
  for carry,expected in ((0,True),(1,False)):
   p,_=mutable_fixture();test=p['lift']['instructions'][3];tmp=node('IlTmp',Id=7,Ty=ty(32));test['tree']['Body']=[node('IlLet',Id=7,Val=reg32(0)),fw(0,const(carry,1)),fw(6,binary('Eq',tmp,const(0),1))];p['lift']['instructions'][4]['tree']['Body'][0]['Cond']=binary('Or',flag(0),flag(6),1);x=self.recover(p);self.assertEqual(x['status'],'generated',x);self.assertEqual(any(form in x['source'] for form in (' <= 0u)',' > 0u)')),expected)
 def test_fullword_slot_mutation_refuses_initial_byte_parameter(self):
  for bits in (8,32):
   x=self.recover(mixed_width_fixture(bits))
   if bits==8:self.assertEqual((x['status'],x['blocker']),('unsupported','mutable_mixed_width_incoming_store'))
   else:self.assertEqual(x['status'],'generated',x);self.assertIn('unsigned int arg_0',x['source'])
 def test_terminal_path_uses_same_slot_width_guard_and_call_declarations(self):
  for bits in (8,32):
   x=self.recover(terminal_width_fixture(bits))
   if bits==8:self.assertEqual((x['status'],x['blocker']),('unsupported','mutable_mixed_width_incoming_store'))
   else:self.assertEqual(x['status'],'generated',x);self.assertIn('extern "C" void __cdecl fn_00009900(unsigned int);',x['source']);self.assertIn('arg_0 = static_cast<unsigned int>(305419896u)',x['source'])
 def test_incoming_extent_alignment_partial_and_return_word_refuse(self):
  from test_replayable_ir import reg
  from test_replayable_loops import binary,reg32
  for offset,bits in ((16,32),(9,32),(8,16),(4,32)):
   p,_=mutable_fixture();store=next(n for row_ in p['lift']['instructions'] for n in row_['tree']['Body'] if n['type']=='LiftIl.IlStore' and row_['raw_hex']=='89542408');store['Addr']=binary('Add',reg(4),const(offset,64));store['Val']=const(2,bits);x=self.recover(p);self.assertEqual(x['status'],'unsupported',(offset,bits,x))
 def test_stack_pointer_escape_and_unknown_register_are_not_stubbed(self):
  from test_replayable_ir import reg
  from test_replayable_loops import reg32
  for mode in ('escape','unknown'):
   p,_=mutable_fixture()
   if mode=='escape':next(n for row_ in p['lift']['instructions'] if row_['raw_hex']=='89542408' for n in row_['tree']['Body'])['Val']=reg32(4)
   else:p['lift']['instructions'][2]['tree']['Body'][0]['Val']=reg(2)
   self.assertEqual(self.recover(p)['status'],'unsupported',mode)
 def test_unused_memory_observation_is_refused_not_dropped(self):
  from test_replayable_ir import reg,ty
  from test_replayable_loops import binary
  from test_replayable_byvalue import load
  p,_=mutable_fixture();p['lift']['instructions'][1]['tree']['Body'].insert(0,node('IlLet',Id=8,Val=load(binary('Add',reg(1),const(16,64)))));x=self.recover(p);self.assertEqual(x['status'],'unsupported',x);self.assertEqual(x['blocker'],'mutable_unused_memory_effect_requires_observable_read')
 def test_no_cleanup_crosses_intervening_call_or_branch(self):
  p,cleanup=mutable_fixture();rows=p['lift']['instructions'];at=next(i for i,r in enumerate(rows) if r['pc']==cleanup);rows[at-1]['tree']['Body']=[node('IlBranch',Kind=dict(name='Jmp'),Cond=None,Target=const(cleanup,32))];x=self.recover(p);self.assertEqual(x['status'],'unsupported',x)

@unittest.skipUnless(DLL.exists(),'build changed component first')
class ReceiverLayoutTests(unittest.TestCase):
 def recover(self,p):return json.loads(subprocess.check_output([DOTNET,str(DLL),'recover-ir'],input=json.dumps(p).encode()))
 def test_observed_access_slots_are_not_declared_field_or_object_sizes(self):
  p,_=mutable_fixture();x=self.recover(p);self.assertEqual(x['status'],'generated',x);layout=x['ir']['receiver_layout'];slot=next(s for s in layout['slots'] if s['offset']==12);self.assertEqual((slot['observed_bytes'],slot['access_widths']),(4,[32]));self.assertFalse(slot['declared_field_size_known']);self.assertEqual(slot['declared_type'],'unknown');self.assertFalse(layout['allocated_object_extent_known']);self.assertFalse(layout['cross_method_type_merge']);self.assertEqual(layout['minimum_fixed_access_span'],16);self.assertTrue(slot['origins']);self.assertTrue(layout['accesses'][0]['path_guards']);self.assertIn('checked_receiver_access_view',x['source']);self.assertIn('receiver_access_000c',x['source']);self.assertIn('actual field types, sizes and object extent remain unknown',x['source'])
 def test_overlapping_widths_keep_union_ambiguity_and_do_not_get_disjoint_views(self):
  from test_replayable_ordered_memory import fixture as ordinary
  p=ordinary();p.update(recover_only=True,layout_only=True);x=self.recover(p);self.assertEqual(x['status'],'recovered',x);slots=x['ir']['slots'];self.assertTrue(next(s for s in slots if s['offset']==12)['overlap_ambiguous']);self.assertTrue(next(s for s in slots if s['offset']==13)['overlap_ambiguous']);self.assertFalse(x['ir']['allocated_object_extent_known'])
 def test_indexed_access_retains_unknown_bound_and_possible_slot_alias(self):
  from test_replayable_ordered_memory import fixture as ordinary
  from test_replayable_ir import reg
  from test_replayable_loops import binary,reg32
  p=ordinary();store=p['lift']['instructions'][7]['tree']['Body'][0];store['Addr']=binary('Add',reg(6),binary('Add',const(13),reg32(0)));p.update(recover_only=True,layout_only=True);x=self.recover(p);self.assertEqual(x['status'],'recovered',x);self.assertTrue(any(a['index'] is not None for a in x['ir']['accesses']));self.assertTrue(all(s['indexed_overlap_possible'] for s in x['ir']['slots']));self.assertFalse(x['ir']['allocated_object_extent_known'])

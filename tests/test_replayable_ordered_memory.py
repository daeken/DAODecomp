"""Open forward effects; unknown callees and stack aliases stay explicit."""
import copy,json,subprocess,unittest
from test_replayable_ir import DLL,DOTNET,node,ty,reg,const,write
from test_replayable_loops import binary,reg32
from test_replayable_byvalue import load,push
from test_replayable_stackargs import row,ret
from test_replayable_conditional import call

def fixture():
 b=0x502000;target=0x503000
 def branch(offset,cond):return node('IlBranch',Kind=dict(name='CondJmp'),Target=const(b+offset,64),Cond=cond)
 # Distinct open layout and one arbitrary external call. The two paths join
 # ordered overlapping stores and RET reads its target from memory afterward.
 rows=[row(b,[write(6,reg(1)),write(0,load(binary('Add',reg(4),const(4,64)),8)),branch(8,binary('Eq',reg32(0),const(0),1))]),row(b+1,push(reg32(6))),row(b+2,push(load(binary('Add',reg(4),const(12,64))))) ,row(b+3,call(b+3,target),'e800000000')]
 # Five-byte CALL makes the continuation b+8; target skip is the common store.
 rows +=[row(b+8,[write(4,binary('Add',reg(4),const(4,64)))]),row(b+9,[node('IlLet',Id=0,Val=load(reg(4))),write(4,binary('Add',reg(4),const(4,64))),write(6,node('IlTmp',Id=0,Ty=ty(32)))]),row(b+10,[node('IlStore',Addr=binary('Add',reg(1),const(12,64)),Val=const(7))]),row(b+11,[node('IlStore',Addr=binary('Add',reg(1),const(13,64)),Val=const(9,8))]),row(b+12,ret(8),'c20800')]
 # Branch skips both pushed words and their cleanup, directly to the stores.
 rows[0]['tree']['Body'][-1]['Target']=const(b+10,64)
 # External cdecl may clobber ECX; preserve this in ESI on all paths, and use
 # an ordinary spill for its entry value. Easier open fixture uses EBX as an
 # unmodified receiver backup; introduce the save before the branch instead.
 rows[0]['tree']['Body']=[*push(reg32(6)),write(6,reg(1)),write(0,load(binary('Add',reg(4),const(8,64)),8)),branch(10,binary('Eq',reg32(0),const(0),1))]
 rows[1]['tree']['Body']=[] # now only the shared receiver save exists
 for r in rows[6:8]:r['tree']['Body'][0]['Addr']['L']=reg(6)
 # Restore only after all stores; shared stack slot may now be aliased.
 rows[5]['tree']['Body']=[]
 rows.insert(-1,row(b+12,[node('IlLet',Id=0,Val=load(reg(4))),write(4,binary('Add',reg(4),const(4,64))),write(6,node('IlTmp',Id=0,Ty=ty(32)))]))
 rows[-1]['pc']=b+13
 return dict(lift=dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=rows),callee_lifts=[dict(target=target,lift=dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=[row(target,ret(0),'c3')]))],structured_memory=True,rva=0x2000,image_base=0x500000,image_end=0x510000,module='open.exe')

@unittest.skipUnless(DLL.exists(),'build changed component first')
class OrderedMemoryTests(unittest.TestCase):
 def recover(self,p):return json.loads(subprocess.check_output([DOTNET,str(DLL),'recover-ir'],input=json.dumps(p).encode()))
 def test_join_keeps_ordered_overlap_and_unknown_return_target(self):
  r=self.recover(fixture());self.assertEqual(r['status'],'generated',r);f=r['ir']['flow'];self.assertEqual(len(f['normal_paths']),2)
  for path in f['normal_paths']:
   self.assertTrue(path['exit']['stack_memory_may_have_changed']);self.assertEqual(path['exit']['return_target']['kind'],'memory_read');self.assertEqual([e['bits'] for e in path['effects'] if e['kind']=='memory_store'],[32,8])
  calls=[e['call'] for p in f['normal_paths'] for e in p['effects'] if e['kind']=='external_call'];self.assertEqual(len(calls),1);self.assertTrue(calls[0]['memory_effects_unknown']);self.assertTrue(calls[0]['termination_unknown']);self.assertFalse(calls[0]['formal_arity_known']);self.assertEqual(r['source'].count('write_word('),2);self.assertIn('unsigned char arg_0',r['source'])
 def test_pointer_escape_and_call_after_alias_store_refuse(self):
  p=fixture();p['lift']['instructions'][6]['tree']['Body'][0]['Val']=reg32(4);self.assertEqual(self.recover(p)['status'],'unsupported')
  p=fixture();p['lift']['instructions'][1]['tree']['Body']=[node('IlStore',Addr=binary('Add',reg(6),const(20)),Val=const(1))];r=self.recover(p);self.assertEqual(r['status'],'unsupported');self.assertEqual(r['blocker'],'structured_memory_precall_incoming_extent')
 def test_unknown_callee_and_indirect_target_refuse(self):
  p=fixture();p['callee_lifts']=[];self.assertEqual(self.recover(p)['status'],'unsupported')
  p=fixture();p['lift']['instructions'][3]['tree']['Body'][0]['Val']=reg(0);self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_unsupported_width_and_segment_do_not_disappear(self):
  for edit in ('width','segment'):
   p=fixture();s=p['lift']['instructions'][6]['tree']['Body'][0]
   if edit=='width':s['Val']=const(1,16)
   else:s['Addr']=binary('Add',node('IlReadReg',Kind=dict(name='X86Seg'),Idx=4,Ty=ty(64)),s['Addr'],64)
   self.assertEqual(self.recover(p)['status'],'unsupported')

 def test_halfword_incoming_observation_cannot_be_emitted_as_full_word(self):
  p=fixture();p['lift']['instructions'][0]['tree']['Body'][4]['Val']['Ty']['Bits']=16;r=self.recover(p);self.assertEqual(r['status'],'unsupported',r);self.assertEqual(r['blocker'],'structured_memory_incoming_byte_or_word_slots_only')
  # 0x10000 has a zero low halfword but is nonzero as a full word; the old
  # untruncated uint parameter comparison therefore changed the condition.
  self.assertEqual(0x10000&0xffff,0);self.assertNotEqual(0x10000,0)
 def test_supported_byte_and_word_input_boundaries_still_generate(self):
  for bits in (8,32):
   p=fixture();p['lift']['instructions'][0]['tree']['Body'][4]['Val']['Ty']['Bits']=bits;r=self.recover(p);self.assertEqual(r['status'],'generated',r);self.assertIn(('unsigned char' if bits==8 else 'unsigned int')+' arg_0',r['source'])

 def test_zero_cleanup_without_incoming_reads_generates_empty_parameters(self):
  p=fixture();rows=p['lift']['instructions']
  # A distinct memory-controlled diamond, with no observed incoming arguments.
  rows[0]['tree']['Body'][4]['Val']=load(binary('Add',reg(6),const(24,64)),32)
  rows[2]['tree']['Body']=push(reg32(6))
  rows[-1]=row(rows[-1]['pc'],ret(0),'c3')
  r=self.recover(p);self.assertEqual(r['status'],'generated',r)
  self.assertIn('fn_00002000()',r['source']);self.assertNotIn('arg_0',r['source'])
  self.assertEqual(r['ir']['flow']['incoming']['required_read_bytes'],0)
  for path in r['ir']['flow']['normal_paths']:
   self.assertEqual(path['exit']['return_target']['kind'],'memory_read')
  calls=[e['call'] for path in r['ir']['flow']['normal_paths'] for e in path['effects'] if e['kind']=='external_call']
  self.assertTrue(all(c['memory_effects_unknown'] and c['throw_behavior_unknown'] and not c['formal_arity_known'] for c in calls))

 def test_zero_cleanup_does_not_hide_observed_incoming_reads(self):
  p=fixture();rows=p['lift']['instructions'];rows[-1]=row(rows[-1]['pc'],ret(0),'c3')
  r=self.recover(p);self.assertEqual(r['status'],'unsupported',r)
  self.assertEqual(r['blocker'],'structured_memory_precall_incoming_extent')

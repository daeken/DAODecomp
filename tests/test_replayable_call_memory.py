"""Open typed call/memory cases; no game or native equivalence claim."""
import copy,json,struct,subprocess,unittest
from test_replayable_ir import DLL,DOTNET,node,reg,const,binary,write,tmp
from test_replayable_frame_flow import contract,pop
from test_replayable_flow_eh import load,store,push
from test_replayable_stackargs import row,ret,callee
from test_replayable_conditional import call

TARGET=0x503000

def incoming(off=8):return binary('Add',reg(4),const(off,64))
def fixture(after=None):
 # Capture incoming value before overwriting its memory word, then invoke an
 # opaque normal-ABI call. Each synthetic row has explicit typed effects.
 bodies=[push(reg(3)),[write(3,load(incoming()))],[store(incoming(),const(17))],push(const(0)),None,[write(4,binary('Add',reg(4),const(4,64)))]]
 bodies+=after if after is not None else [[write(0,load(incoming()))]]
 bodies += [pop(3),ret(4)];rows=[];pc=0x502000
 for b in bodies:
  raw='e8'+struct.pack('<i',TARGET-pc-5).hex() if b is None else 'c20400' if b==bodies[-1] else '90'
  rows.append(row(pc,call(pc,TARGET) if b is None else b,raw));pc+=len(raw)//2
 return dict(flow_paths=True,lift=dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=rows),flow_contract=contract(incoming_word_stores=True,aliasable_memory_stores=True,private_subword_stack=True),callee_lifts=[dict(target=TARGET,lift=callee(0))])

def effects(result):return result['ir']['normal_paths'][0]['effects']
def low(v):
 while v.get('kind')=='bit_operation' and v['operation']in('Zext','Trunc'):v=v['operands'][0]
 return v

@unittest.skipUnless(DLL.exists(),'build changed component first')
class CallMemoryTests(unittest.TestCase):
 def recover(self,p):return json.loads(subprocess.check_output([DOTNET,str(DLL),'recover-ir'],input=json.dumps(p).encode()))
 def checked(self,p):
  r=self.recover(p);self.assertEqual(r['status'],'recovered',r);self.assertEqual(r['ir']['memory_model'],'opaque-call-caller-memory-havoc-v2');return r
 def test_incoming_reload_has_postcall_memory_identity_not_cached_store(self):
  r=self.checked(fixture());e=next(e for e in effects(r)if e['kind']=='incoming_slot_read');self.assertEqual(e['value']['kind'],'memory_read');self.assertEqual(e['value']['pc'],e['pc']);self.assertEqual(e['value']['bits'],32);self.assertGreater(e['value']['epoch'],0);self.assertNotEqual(e['value'],dict(kind='constant',value=17,bits=32))
  self.assertEqual(r['ir']['normal_paths'][0]['exit']['return_target']['kind'],'memory_read')
 def test_preserved_capture_and_memory_reload_are_distinct_under_mutation(self):
  r=self.checked(fixture([[write(1,reg(3))],[write(0,load(incoming()))]]));out=r['ir']['normal_paths'][0]['exit'];captured=low(out['registers']['1']);reload=low(out['return']);self.assertEqual(captured['kind'],'incoming_stack_read');self.assertEqual(captured['memory_epoch'],0);self.assertEqual(reload['kind'],'memory_read')
  # Executable distinguishing valuations, not an assumed actual callback.
  for before,after in [(7,99),(0xffffffff,0),(0,0x80000000)]:
   memory=bytearray(struct.pack('<I',before));snapshot=struct.unpack('<I',memory)[0];struct.pack_into('<I',memory,0,after);self.assertNotEqual(snapshot,struct.unpack('<I',memory)[0])
 def test_call_entry_is_precall_and_later_snapshots_mask_stale_words(self):
  r=self.checked(fixture([push(const(0)),None,[write(4,binary('Add',reg(4),const(4,64)))],[write(0,load(incoming()))]]));calls=[e['call']for e in effects(r)if e['kind']=='external_call'];self.assertEqual(calls[0]['entry_stack']['4']['value'],17);self.assertEqual(calls[1]['entry_stack']['4']['kind'],'unknown');self.assertEqual(calls[1]['entry_stack']['-4']['kind'],'unknown');self.assertEqual(calls[1]['arguments'][0]['value'],0)
  self.assertEqual(low(calls[0]['entry_registers']['3']),low(calls[1]['entry_registers']['3']))
 def test_full_word_refresh_only_restores_written_slot(self):
  r=self.checked(fixture([[store(incoming(),const(99))],[write(0,load(incoming()))]]));out=r['ir']['normal_paths'][0]['exit'];self.assertEqual(low(out['return'])['value'],99);self.assertEqual(out['return_target']['kind'],'memory_read');self.assertTrue(out['stack_memory_may_have_changed'])
 def test_second_call_invalidates_refreshed_word_again(self):
  r=self.checked(fixture([[store(incoming(),const(99))],push(const(0)),None,[write(4,binary('Add',reg(4),const(4,64)))],[write(0,load(incoming()))]]));self.assertEqual(r['ir']['normal_paths'][0]['exit']['return']['kind'],'memory_read')
 def test_partial_and_overlapping_incoming_writes_do_not_refresh_word(self):
  for offset,bits in [(8,8),(9,32),(10,16)]:
   r=self.recover(fixture([[store(incoming(offset),const(9,bits))],[write(0,load(incoming()))]]));self.assertEqual(r['status'],'unsupported');self.assertEqual(r['blocker'],'flow_incoming_store_outside_observed_word')
 def test_partial_saved_word_after_call_cannot_resurrect_old_high_bytes(self):
  r=self.recover(fixture([[store(reg(4),const(1,8))],[write(0,load(incoming()))]]));self.assertEqual(r['blocker'],'flow_private_subword_without_initialized_word')
 def test_explicit_full_refresh_then_partial_merge_is_known(self):
  r=self.checked(fixture([[store(reg(4),const(0x12345678))],[store(binary('Add',reg(4),const(1,64)),const(0xff,8))],[write(0,load(reg(4)))]]));v=r['ir']['normal_paths'][0]['exit']['return'];self.assertEqual(v['kind'],'bit_operation');self.assertEqual(v['operation'],'Or');self.assertIn('305419896',json.dumps(v));self.assertEqual(r['ir']['normal_paths'][0]['exit']['return_target']['kind'],'memory_read')
 def test_legacy_contract_does_not_silently_select_new_normal_ABI(self):
  p=fixture();p['flow_contract']['caller_frame_retained_on_normal_return']=p['flow_contract'].pop('normal_return_abi_selected');r=self.recover(p);self.assertEqual(r['blocker'],'flow_requires_explicit_normal_ABI_contract')
 def test_explicitly_disabled_fresh_tracking_stays_unsupported(self):
  p=fixture([[store(incoming(),const(9))]]);p['flow_contract']['track_fresh_stack_words']=False;self.assertEqual(self.recover(p)['blocker'],'flow_incoming_store_outside_observed_word')

 def test_fault_snapshot_after_call_keeps_only_explicit_refresh(self):
  from test_replayable_fault_paths import guard
  from test_replayable_conditional import op
  p=fixture([[store(incoming(),const(99))],[guard(op('Eq',reg(3),const(0,64),1))],[write(0,load(incoming()))]]);p['flow_contract']['explicit_architectural_faults']=True
  r=self.checked(p);f=r['ir']['fault_paths'][0];self.assertEqual(f['fresh_stack_words'],[4]);self.assertEqual(f['stack']['4']['value'],99);self.assertEqual(f['stack']['-4']['kind'],'unknown');self.assertEqual(f['stack']['0']['kind'],'unknown');self.assertEqual(sum(e['kind']=='external_call'for e in f['effects']),1)
 def test_join_preserves_only_path_local_refresh(self):
  from test_replayable_conditional import op
  p=fixture([[node('IlBranch',Kind=dict(name='CondJmp'),Cond=op('Eq',reg(3),const(0,64),1),Target=const(0,64))],[store(incoming(),const(99))],[write(0,load(incoming()))]])
  rows=p['lift']['instructions'];rows[6]['tree']['Body'][0]['Target']=const(rows[8]['pc'],64);r=self.checked(p);self.assertEqual(len(r['ir']['normal_paths']),2)
  vals=[low(q['exit']['return'])for q in r['ir']['normal_paths']];self.assertEqual({v['kind']for v in vals},{'constant','memory_read'});self.assertEqual(next(v['value']for v in vals if v['kind']=='constant'),99)

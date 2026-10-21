"""Saved location provenance is not saved content equality or game proof."""
import copy,json,struct,subprocess,unittest
from test_replayable_ir import DLL,DOTNET,node,ty,reg,const,binary,write,tmp
from test_replayable_flow_eh import eh_fixture,load,store,addr

def fixture():
 p=eh_fixture();p['callee_lifts']=p.pop('callees');p['eh_evidence']=p.pop('evidence');p.pop('eh');p['eh_paths']=True;return p

def restore_rows(p):
 return [r for r in p['lift']['instructions']if any(n['type']=='LiftIl.IlStore'and n['Addr']==addr(4,0)and n['Val'].get('type')=='LiftIl.IlLoad'for n in r['tree']['Body'])]

@unittest.skipUnless(DLL.exists(),'build changed component first')
class SavedFrameTests(unittest.TestCase):
 def recover(self,p):return json.loads(subprocess.check_output([DOTNET,str(DLL),'recover-ir'],input=json.dumps(p).encode()))
 def check(self,p):
  x=self.recover(p);self.assertEqual(x['status'],'generated',x);self.assertEqual(x['ir']['function']['memory_model'],'opaque-call-caller-memory-havoc-v2');self.assertFalse(x['proof']);return x
 def test_same_location_has_current_unknown_value_on_both_exits(self):
  x=self.check(fixture());plans=x['ir']['saved_frame_reloads'];self.assertEqual(len(plans),2)
  for path,p in zip(x['ir']['function']['normal_paths'],plans):
   self.assertEqual((p['entry_stack_offset'],p['width_bits']),(-12,32));self.assertFalse(p['restored_entry_value_proven']);self.assertFalse(p['frame_disjointness_proven']);self.assertEqual(p['saved_entry_value']['address']['segment']['index'],4);self.assertEqual(p['current_value']['address']['offset'],-12);self.assertEqual(p['current_value']['pc'],p['reload_pc']);self.assertGreater(p['current_value']['epoch'],p['saved_entry_value']['epoch']);self.assertNotEqual(p['current_value'],p['saved_entry_value']);self.assertEqual(path['exit']['return_target']['kind'],'memory_read');self.assertTrue(path['exit']['stack_memory_may_have_changed']);self.assertEqual(path['exit']['stack']['-12']['kind'],'unknown')
  self.assertEqual(sorted(len(p['intervening_calls'])for p in plans),[1,2])
 def test_executable_mutation_distinguishes_same_location_from_original_value(self):
  p=self.check(fixture())['ir']['saved_frame_reloads'][0];self.assertFalse(p['restored_entry_value_proven'])
  for entry,changed in ((0x11223344,0xaabbccdd),(0,0xffffffff),(0x80000000,1)):
   frame=bytearray(32);struct.pack_into('<I',frame,12,entry);captured=struct.unpack_from('<I',frame,12)[0];struct.pack_into('<I',frame,12,changed);restored=struct.unpack_from('<I',frame,12)[0];self.assertEqual(restored,changed);self.assertNotEqual(restored,captured)
 def test_wrong_saved_word_and_return_target_word_refuse_actual_role_guard(self):
  for offset in (4,12,20):
   p=fixture();restore_rows(p)[0]['tree']['Body'][0]['Val']['Addr']=binary('Add',reg(4),const(offset,64));x=self.recover(p);self.assertEqual(x['blocker'],'EH_saved_FS_reload_required')
 def test_missing_reload_on_only_one_path_refuses(self):
  p=fixture();restore_rows(p)[1]['tree']['Body'][0]['Val']=const(0);self.assertEqual(self.recover(p)['blocker'],'EH_saved_FS_reload_required')
 def test_second_saved_word_definition_refuses(self):
  p=fixture();p['lift']['instructions'][10]['tree']['Body'].append(store(binary('Add',reg(4),const(8,64)),const(123)));self.assertEqual(self.recover(p)['blocker'],'EH_unique_saved_FS_word_required')
 def test_partial_or_misaligned_reload_does_not_supply_complete_word(self):
  for mode in ('partial','overlap'):
   p=fixture();value=restore_rows(p)[0]['tree']['Body'][0]['Val']
   if mode=='partial':value['Ty']=ty(16)
   else:value['Addr']=binary('Add',reg(4),const(9,64))
   self.assertEqual(self.recover(p)['blocker'],'flow_unknown_or_overlapping_stack_read')
 def test_narrowed_reloaded_value_cannot_be_restored_as_complete_FS_word(self):
  p=fixture();st=restore_rows(p)[0]['tree']['Body'][0];st['Val']=node('IlCast',Kind=dict(name='Zext'),Ty=ty(32),X=node('IlCast',Kind=dict(name='Trunc'),Ty=ty(8),X=st['Val']));self.assertEqual(self.recover(p)['blocker'],'EH_saved_FS_word_width_required')
 def test_different_segment_or_adjusted_FS_destination_refuses(self):
  p=fixture();st=restore_rows(p)[0]['tree']['Body'][0];st['Val']['Addr']=binary('Add',addr(3,0),binary('Add',reg(4),const(8,64)));self.assertEqual(self.recover(p)['blocker'],'EH_unmodeled_external_read')
  p=fixture();restore_rows(p)[0]['tree']['Body'][0]['Addr']=addr(4,4);self.assertEqual(self.recover(p)['blocker'],'flow_unknown_store_frame_alias')
 def test_direct_known_entry_value_does_not_substitute_for_reload(self):
  p=fixture();st=restore_rows(p)[0]['tree']['Body'][0];st['Val']=load(addr(4,0));self.assertEqual(self.recover(p)['blocker'],'EH_unmodeled_external_read')
 def test_duplicate_reload_and_reordered_global_effect_refuse(self):
  p=fixture();r=restore_rows(p)[0];r['tree']['Body'].insert(0,write(2,copy.deepcopy(r['tree']['Body'][0]['Val'])));self.assertEqual(self.recover(p)['blocker'],'EH_saved_FS_reload_required')
  p=fixture();rows=p['lift']['instructions'];r=restore_rows(p)[0];i=rows.index(r);global_store=rows[i-1]['tree']['Body'][0];rows[i-1]['tree']['Body']=[write(2,const(0))];r['tree']['Body']=[node('IlLet',Id=7,Val=r['tree']['Body'][0]['Val']),global_store,store(addr(4,0),tmp(7,32))];self.assertEqual(self.recover(p)['blocker'],'EH_saved_FS_effect_order_required')
 def test_partial_saved_word_write_and_extra_alias_store_stay_unsupported(self):
  p=fixture();p['lift']['instructions'][10]['tree']['Body'].append(store(binary('Add',reg(4),const(9,64)),const(1,8)));self.assertEqual(self.recover(p)['blocker'],'flow_stack_store_outside_allocated_word')
  p=fixture();restore_rows(p)[0]['tree']['Body'].insert(0,store(addr(3,0x509100),const(7)));self.assertEqual(self.recover(p)['blocker'],'EH_extra_or_partial_memory_effect')

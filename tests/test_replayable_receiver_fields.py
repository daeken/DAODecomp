"""Open receiver-slot emission boundaries; no original type/array assertions."""
import json,subprocess,unittest
from test_replayable_ir import DLL,DOTNET,const,node,reg
from test_replayable_loops import binary,reg32
from test_replayable_terminal_calls import mutable_fixture

@unittest.skipUnless(DLL.exists(),'build changed component first')
class TypedReceiverTests(unittest.TestCase):
 def recover(self,p):return json.loads(subprocess.check_output([DOTNET,str(DLL),'recover-ir'],input=json.dumps(p).encode()))
 def test_fixed_word_slot_is_real_member_with_checked_offset_and_neutral_padding(self):
  p,_=mutable_fixture();old=self.recover(p);p['typed_receiver']=True;x=self.recover(p);self.assertEqual(x['status'],'generated',x);source=x['source'];self.assertIn('unsigned int field_000c;',source);self.assertIn('this->field_000c =',source);self.assertIn('DAO_ACCESS_OFFSETOF(Recovered, field_000c) == 12u',source);self.assertIn('#pragma pack(push, 1)',source);self.assertIn('unsigned char unknown_0000[12];',source);self.assertNotIn('this->field_',old['source']);self.assertEqual(x['ir'],old['ir']);self.assertFalse(x['ir']['receiver_layout']['allocated_object_extent_known'])
 def test_unaligned_relative_slot_keeps_memcpy_fallback(self):
  p,_=mutable_fixture();p['typed_receiver']=True;p['lift']['instructions'][12]['tree']['Body'][0]['Addr']=binary('Add',reg(6),const(13,64));x=self.recover(p);self.assertEqual(x['status'],'generated',x);self.assertNotIn('unsigned int field_',x['source']);self.assertIn('write_word(',x['source'])
 def test_overlapping_observed_widths_keep_raw_aliasing_fallback(self):
  p,_=mutable_fixture();p['typed_receiver']=True;p['lift']['instructions'][12]['tree']['Body'].append(node('IlStore',Addr=binary('Add',reg(6),const(13,64)),Val=const(7,8)));x=self.recover(p);self.assertEqual(x['status'],'generated',x);self.assertNotIn('unsigned int field_',x['source']);self.assertTrue(all(s['overlap_ambiguous'] for s in x['ir']['receiver_layout']['slots']))
 def test_dynamic_index_is_not_declared_array_or_bound(self):
  p,_=mutable_fixture();p['typed_receiver']=True;p['lift']['instructions'][12]['tree']['Body'][0]['Addr']=binary('Add',reg(6),binary('Add',const(12),reg32(0)));x=self.recover(p);self.assertEqual(x['status'],'generated',x);self.assertNotIn('unsigned int field_',x['source']);self.assertFalse(x['ir']['receiver_layout']['allocated_object_extent_known']);self.assertTrue(any(a['index'] is not None for a in x['ir']['receiver_layout']['accesses']))

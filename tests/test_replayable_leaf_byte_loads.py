"""Byte load proposals keep upper EAX and the exact one-read snapshot."""
import json,subprocess,unittest
from test_replayable_ir import DLL,DOTNET,node,ty,reg,const,write,binary
from test_replayable_leaf_receivers import receiver

def byte_load(offset=40,base=1,width=8):
 p=receiver(offset,base=base,width=width);w=p['lift']['instructions'][0]['tree']['Body'][0];w['Val']=binary('Or',binary('And',reg(0),const(0xffffffffffffff00,64)),w['Val']);return p

@unittest.skipUnless(DLL.exists(),'build component first')
class LeafByteLoadTests(unittest.TestCase):
 def recover(self,p):return json.loads(subprocess.check_output([DOTNET,str(DLL),'recover-ir'],input=json.dumps(p).encode()))
 def test_byte_load_retains_upper_eax_read_identity_and_width(self):
  x=self.recover(byte_load());self.assertEqual(x['status'],'generated',x);self.assertEqual(x['ir']['receiver_operation'],'load_byte');self.assertEqual(x['ir']['return_type'],'unsigned char');p=x['ir']['flow']['normal_paths'][0];self.assertEqual(p['effects'][0]['bits'],8);self.assertEqual(p['exit']['return']['kind'],'bit_operation');self.assertIn('unsigned char*',x['source']);self.assertFalse(x['proof'])
 def test_word_width_or_other_receiver_does_not_fit_byte_rule(self):
  for p in (byte_load(width=16),byte_load(width=32),byte_load(base=2),byte_load(4097)):
   self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_full_eax_byte_read_and_wrong_upper_mask_refuse(self):
  self.assertEqual(self.recover(receiver(40,width=8))['status'],'unsupported')
  p=byte_load();p['lift']['instructions'][0]['tree']['Body'][0]['Val']['L']['R']=const(0xffffffffffff0000,64);self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_read_flags_or_second_snapshot_cannot_be_dropped(self):
  for e in (node('IlWriteReg',Kind=dict(name='Eflags'),Idx=6,Val=const(1,1)),node('IlLet',Id=9,Val=node('IlLoad',Addr=reg(1),Ty=ty(8))),node('IlStore',Addr=reg(1),Val=const(1,8))):
   p=byte_load();p['lift']['instructions'][0]['tree']['Body'].append(e);self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_truncated_byte_merge_or_replaced_return_target_refuses(self):
  p=byte_load();p['lift']['instructions'][0]['tree']['Body'][0]['Val']['R']['Kind']['name']='Trunc';self.assertEqual(self.recover(p)['status'],'unsupported')
  p=byte_load();p['lift']['instructions'][-1]['tree']['Body'][-1]['Target']=const(0x500010);self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_routine_stack_fallback_emits_same_source(self):
  p=byte_load();a=self.recover(p);del p['leaf_returns'];p.update(stack_arguments=True,callee_lifts=[]);b=self.recover(p);self.assertEqual(b['status'],'generated',b);self.assertEqual(a['source'],b['source'])

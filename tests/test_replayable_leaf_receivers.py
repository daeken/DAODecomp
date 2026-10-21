"""Receiver lineage/width guards; compiled artifacts remain the acceptance gate."""
import json,subprocess,unittest
from test_replayable_ir import DLL,DOTNET,node,ty,reg,const,write,binary
from test_replayable_leaf_returns import fixture

def cast(v,bits,kind):return node('IlCast',Kind=dict(name=kind),Ty=ty(bits),X=v)
def receiver(offset=0,load=True,base=1,width=32):
 p=fixture();addr=reg(base) if offset==0 else cast(cast(binary('Add',reg(base),const(offset,64)),32,'Trunc'),64,'Zext')
 value=cast(node('IlLoad',Addr=addr,Ty=ty(width)),64,'Zext') if load else addr
 p['lift']['instructions'][0]['tree']['Body']=[write(0,value)];return p

@unittest.skipUnless(DLL.exists(),'build component first')
class LeafReceiverTests(unittest.TestCase):
 def recover(self,p):return json.loads(subprocess.check_output([DOTNET,str(DLL),'recover-ir'],input=json.dumps(p).encode()))
 def test_word_loads_retain_address_width_origin_and_snapshot(self):
  for offset in (0,16,4096):
   x=self.recover(receiver(offset));self.assertEqual(x['status'],'generated',x);self.assertEqual(x['ir']['receiver_operation'],'load_word');self.assertEqual(x['ir']['receiver_offset'],offset);e=x['ir']['flow']['normal_paths'][0]['effects'][0];self.assertEqual(e['kind'],'memory_read');self.assertEqual(e['bits'],32);self.assertEqual(e['value']['epoch'],0);self.assertIn('reinterpret_cast<unsigned int*>',x['source']);self.assertFalse(x['proof'])
 def test_address_arithmetic_uses_unsigned_bits_without_object_extent(self):
  x=self.recover(receiver(12,False));self.assertEqual(x['status'],'generated',x);self.assertEqual(x['ir']['receiver_operation'],'address');self.assertIn('reinterpret_cast<unsigned int>(this) + 12u',x['source']);self.assertNotIn('char*',x['source']);self.assertFalse(any(e['kind']=='memory_read'for e in x['ir']['flow']['normal_paths'][0]['effects']))
 def test_receiver_and_extent_are_not_inferred_from_word_width(self):
  for p in (receiver(base=2),receiver(4097),receiver(width=8),receiver(width=16)):
   self.assertEqual(self.recover(p)['status'],'unsupported',p)
 def test_extra_read_write_flags_or_call_cannot_disappear(self):
  extras=[node('IlLet',Id=2,Val=node('IlLoad',Addr=reg(1),Ty=ty(32))),node('IlStore',Addr=reg(1),Val=const(0)),write(1,const(0)),node('IlWriteReg',Kind=dict(name='Eflags'),Idx=6,Val=const(1,1)),node('IlBranch',Kind=dict(name='Call'),Cond=None,Target=reg(0))]
  for extra in extras:
   p=receiver();p['lift']['instructions'][0]['tree']['Body'].append(extra);self.assertEqual(self.recover(p)['status'],'unsupported',extra)
 def test_partial_return_of_read_refuses(self):
  p=receiver();p['lift']['instructions'][0]['tree']['Body'][0]['Val']=cast(node('IlLoad',Addr=reg(1),Ty=ty(32)),8,'Trunc');self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_low_byte_zero_retains_constant_flags(self):
  p=fixture(0,low=True);p['lift']['instructions'][0]['tree']['Body'].append(node('IlWriteReg',Kind=dict(name='Eflags'),Idx=6,Val=const(1,1)));x=self.recover(p);self.assertEqual(x['status'],'generated',x);self.assertIn('unsigned char',x['source']);self.assertEqual(x['ir']['flow']['normal_paths'][0]['exit']['return']['kind'],'bit_operation');self.assertTrue(any(e['kind']=='flag_write'for e in x['ir']['flow']['normal_paths'][0]['effects']))
 def test_entry_eax_arithmetic_remains_unsupported(self):
  p=fixture();p['lift']['instructions'][0]['tree']['Body']=[write(0,binary('Add',reg(0),reg(0)))];self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_routine_stack_fallback_reaches_receiver_rule(self):
  p=receiver(16);del p['leaf_returns'];p.update(stack_arguments=True,callee_lifts=[]);x=self.recover(p);self.assertEqual(x['status'],'generated',x);self.assertEqual(x['ir']['receiver_operation'],'load_word')

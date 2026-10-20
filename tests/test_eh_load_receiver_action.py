"""Synthetic fixed-profile EH action controls; no game byte fixtures."""
import copy,struct,unittest
from test_eh_native import fixture,changed_world,sha
from test_eh_graph import coff,H
from rapid_object.eh_native import check,terminal_profile
from rapid_object.eh_graph import action_shape,Unsupported

def load_fixture(opcode=0x8b):
 kw,s,y=fixture();o=bytearray(kw['original']);action=bytes([opcode,0x4d,0xf0,0xe9])+struct.pack('<i',0x401400-0x401308);o[0x500:0x508]=action;changed_world(kw,bytes(o))
 old=s[1];body=bytes([opcode,0x4d,0xf0,0xe9])+bytes(4)+old[1][11:];rels=[(4,n,k) if a==5 else (a-3,n,k) for a,n,k in old[2]];s[1]=(old[0],body,rels,old[3]);y=[(n,8 if n==H else v,c,t,st,size) for n,v,c,t,st,size in y];kw['object_bytes']=coff(s,y);kw['build']['object_sha256']=sha(kw['object_bytes']);return kw,s,y

class LoadReceiverActionTests(unittest.TestCase):
 def test_complete_load_profile(self):
  kw,_,_=load_fixture();r=check(**kw);self.assertEqual(r['status'],'exact_eh_graph_match',r);a=r['functions'][0]['nodes']['action'];self.assertEqual(a['original_size'],8);self.assertEqual(a['candidate_size'],8);self.assertEqual(a['counts'],{'equal':8});self.assertEqual(a['original_span']['instructions'][-1]['mnemonic'],'jmp')
 def test_existing_lea_profile_reads_eight(self):
  kw,_,_=load_fixture(0x8d);self.assertEqual(check(**kw)['status'],'exact_eh_graph_match')
 def test_each_action_byte_mutation_refuses(self):
  for offset in range(8):
   kw,s,y=load_fixture();sec=s[1];b=bytearray(sec[1]);b[offset]^=1;s[1]=(sec[0],bytes(b),sec[2],sec[3]);kw['object_bytes']=coff(s,y);kw['build']['object_sha256']=sha(kw['object_bytes'])
   with self.subTest(offset=offset):self.assertNotEqual(check(**kw)['status'],'exact_eh_graph_match')
 def test_unknown_external_action_target_refuses(self):
  kw,s,y=load_fixture();sec=s[1];s[1]=(sec[0],sec[1],[(a,'_fn_00001450' if a==4 else n,k) for a,n,k in sec[2]],sec[3]);kw['object_bytes']=coff(s,y);kw['build']['object_sha256']=sha(kw['object_bytes']);self.assertNotEqual(check(**kw)['status'],'exact_eh_graph_match')
 def test_wrong_tail_target_refuses(self):
  kw,s,y=load_fixture();sec=s[3];b=bytearray(sec[1]);b[1]=1;s[3]=(sec[0],bytes(b),sec[2],sec[3]);kw['object_bytes']=coff(s,y);kw['build']['object_sha256']=sha(kw['object_bytes']);self.assertNotEqual(check(**kw)['status'],'exact_eh_graph_match')
 def test_complete_length_and_terminal_transfer_required(self):
  valid=bytes.fromhex('8b4df0e900000000')
  for bad in [valid[:-1],valid+b'\x90',valid[:3]+b'\xe8'+valid[4:],b'\x8b\x45'+valid[2:]]:
   with self.subTest(bad=bad),self.assertRaises(Unsupported):action_shape(bad)
 def test_profile_keeps_signed_offset_and_relocation(self):
  p=action_shape(bytes.fromhex('8b4df0e900000000'));self.assertEqual(p['parent_ebp_offset'],-16);self.assertEqual((p['target_field'],p['target_kind']),(4,20))
if __name__=='__main__':unittest.main()

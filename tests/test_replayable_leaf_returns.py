"""Leaf source proposals retain complete FlowIR; no fixture is game proof."""
import copy,json,subprocess,unittest
from test_replayable_ir import DLL,DOTNET,node,ty,reg,const,write,tmp,binary
from test_replayable_stackargs import row,ret

def fixture(value=0,cleanup=0,low=False):
 p=dict(rva=0x7200,image_base=0x500000,image_end=0x510000,module='open.exe',leaf_returns=True)
 rows=[]
 if value is not None:
  v=binary('Or',binary('And',reg(0),const(0xffffffffffffff00,64)),const(value,64)) if low else const(value,32)
  rows=[row(0x507200,[write(0,v)],'b02a' if low else'33c0')]
 raw='c3' if cleanup==0 else 'c2'+cleanup.to_bytes(2,'little').hex()
 rows.append(row(0x507200+(2 if rows else 0),ret(cleanup),raw));p['lift']=dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=rows);return p

@unittest.skipUnless(DLL.exists(),'build component first')
class LeafReturnTests(unittest.TestCase):
 def recover(self,p):return json.loads(subprocess.check_output([DOTNET,str(DLL),'recover-ir'],input=json.dumps(p).encode()))
 def test_constant_and_flags_are_retained(self):
  p=fixture();p['lift']['instructions'][0]['tree']['Body'].append(node('IlWriteReg',Kind=dict(name='Eflags'),Idx=6,Val=const(1,1)))
  x=self.recover(p);self.assertEqual(x['status'],'generated',x);self.assertIn('unsigned int Recovered::',x['source']);self.assertIn('return 0u;',x['source']);self.assertTrue(any(e['kind']=='flag_write' for e in x['ir']['flow']['normal_paths'][0]['effects']));self.assertFalse(x['proof'])
 def test_low_byte_retains_upper_register_expression(self):
  x=self.recover(fixture(42,low=True));self.assertEqual(x['status'],'generated',x);self.assertIn('unsigned char Recovered::',x['source']);self.assertEqual(x['ir']['flow']['normal_paths'][0]['exit']['return']['kind'],'bit_operation');self.assertIn('return 42u;',x['source'])
 def test_cleanup_span_is_proposed_parameters_not_exact_arity(self):
  for n in (4,20,32):
   x=self.recover(fixture(None,n));self.assertEqual(x['status'],'generated',x);self.assertEqual(x['ir']['proposed_word_parameters'],n//4);self.assertFalse(x['ir']['flow']['incoming']['exact_arity_known']);self.assertEqual(x['ir']['flow']['normal_paths'][0]['exit']['return'],dict(kind='register_input',index=0))
 def test_zero_oversized_unaligned_or_conflicting_cleanup_refuses(self):
  for n in (0,2,36,68):self.assertEqual(self.recover(fixture(None,n))['status'],'unsupported',n)
  p=fixture(None,4);p['lift']['instructions'][0]['tree']['Body']=ret(8);self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_extra_volatile_flag_unknown_and_memory_effects_refuse(self):
  extras=[write(1,const(7)),node('IlStore',Addr=reg(1),Val=const(7)),node('IlWriteReg',Kind=dict(name='Eflags'),Idx=6,Val=node('IlReadReg',Kind=dict(name='Eflags'),Idx=0,Ty=ty(1))),write(0,node('IlLoad',Addr=reg(1),Ty=ty(32)))]
  for extra in extras:
   p=fixture();p['lift']['instructions'][0]['tree']['Body'].insert(0,extra);self.assertEqual(self.recover(p)['status'],'unsupported',extra)
 def test_partial_register_mask_and_extra_flags_refuse(self):
  p=fixture(1,low=True);p['lift']['instructions'][0]['tree']['Body'][0]['Val']['L']['R']=const(0xffffffffffff0000,64);self.assertEqual(self.recover(p)['status'],'unsupported')
  p=fixture(1,low=True);p['lift']['instructions'][0]['tree']['Body'].append(node('IlWriteReg',Kind=dict(name='Eflags'),Idx=6,Val=const(1,1)));self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_return_target_fault_prefix_and_extra_instructions_refuse(self):
  for mode in ('target','fault','prefix','extra','opaque'):
   p=fixture();rows=p['lift']['instructions']
   if mode=='target':rows[-1]['tree']['Body'][-1]['Target']=const(0x501000)
   elif mode=='fault':rows[0]['tree']['Body'].append(node('IlFault',Architecture='x86',Vector=3))
   elif mode=='prefix':rows[0]['decoded']['P']['Rep']=True
   elif mode=='extra':rows.append(row(0x507203,[]))
   else:p['lift']['opaque_instructions']=1
   self.assertEqual(self.recover(p)['status'],'unsupported',mode)
 def test_routine_stack_fallback_reaches_same_rule(self):
  p=fixture(None,20);del p['leaf_returns'];p.update(stack_arguments=True,callee_lifts=[]);x=self.recover(p);self.assertEqual(x['status'],'generated',x);self.assertEqual(x['ir']['proposed_word_parameters'],5)

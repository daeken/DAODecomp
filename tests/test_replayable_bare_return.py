"""Complete typed bare-return recognition; void remains a compiler proposal."""
import copy,json,subprocess,unittest
from test_replayable_ir import DLL,DOTNET,node,ty,reg,const,write,tmp,binary
from test_replayable_stackargs import row,ret

def fixture():
 return dict(rva=0x6200,image_base=0x500000,image_end=0x510000,module='open.exe',lift=dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=[row(0x506200,ret(0),'c3')]))

@unittest.skipUnless(DLL.exists(),'build component first')
class BareReturnTests(unittest.TestCase):
 def recover(self,p):return json.loads(subprocess.check_output([DOTNET,str(DLL),'recover-ir'],input=json.dumps(p).encode()))
 def test_single_near_return_keeps_entry_eax_and_no_fabricated_value(self):
  x=self.recover(fixture());self.assertEqual(x['status'],'generated',x);self.assertTrue(x['ir']['bare_near_return']);self.assertEqual(x['ir']['return'],dict(kind='register_input',index=0));self.assertEqual(x['ir']['effects'],[]);self.assertEqual(x['ir']['stack_effects'],[]);self.assertIn('void Recovered::fn_00006200()',x['source']);self.assertNotIn('return this',x['source']);self.assertNotIn('return 0',x['source']);self.assertFalse(x['proof'])
 def test_segmented_stack_and_target_capture_alias_supported(self):
  p=fixture();body=p['lift']['instructions'][0]['tree']['Body'];body[0]['Val']['Addr']=binary('Add',node('IlReadReg',Kind=dict(name='X86Seg'),Idx=2,Ty=ty(64)),reg(4));body.insert(2,node('IlLet',Id=1,Val=tmp(0,32)));body[-1]['Target']=tmp(1,32);x=self.recover(p);self.assertEqual(x['status'],'generated',x);self.assertTrue(x['ir']['bare_near_return'])
 def test_empty_effect_list_does_not_qualify_extra_register_write(self):
  p=fixture();r=p['lift']['instructions'][0];r['tree']['Body'].insert(1,write(1,const(7)));x=self.recover(p);self.assertEqual(x['status'],'unsupported',x)
  p=fixture();p['lift']['instructions'].insert(0,row(0x5061ff,[write(1,const(7))]));x=self.recover(p);self.assertEqual(x['status'],'unsupported',x)
 def test_one_byte_trap_or_wrong_encoding_never_becomes_empty_body(self):
  for raw,body in [('cc',[node('IlFault',Architecture='x86',Vector=3)]),('90',ret(0)),('cb',ret(0))]:
   p=fixture();p['lift']['instructions'][0]=row(0x506200,body,raw);self.assertEqual(self.recover(p)['status'],'unsupported',raw)
 def test_cleanup_and_operand_prefix_not_bare_near_return(self):
  for raw,cleanup in [('c20400',4),('66c3',0),('c20000',0)]:
   p=fixture();p['lift']['instructions'][0]=row(0x506200,ret(cleanup),raw);self.assertEqual(self.recover(p)['status'],'unsupported',raw)
 def test_wrong_stack_width_target_delta_or_segment_refuses(self):
  for mode in ('width','target','delta','segment','flags'):
   p=fixture();b=p['lift']['instructions'][0]['tree']['Body']
   if mode=='width':b[0]['Val']['Ty']['Bits']=16
   elif mode=='target':b[-1]['Target']=const(0x501000)
   elif mode=='delta':b[1]['Val']['R']=const(8,64)
   elif mode=='segment':b[0]['Val']['Addr']=binary('Add',node('IlReadReg',Kind=dict(name='X86Seg'),Idx=4,Ty=ty(64)),reg(4))
   else:b.insert(1,node('IlWriteReg',Kind=dict(name='Eflags'),Idx=6,Val=const(0,1)))
   self.assertEqual(self.recover(p)['status'],'unsupported',mode)
 def test_partial_opaque_and_prefix_evidence_refuses(self):
  for mode in ('decode','opaque','prefix','extra'):
   p=fixture()
   if mode=='decode':p['lift']['decode_complete']=False
   elif mode=='opaque':p['lift']['opaque_instructions']=1
   elif mode=='prefix':p['lift']['instructions'][0]['decoded']['P']['Rep']=True
   else:p['lift']['instructions'].append(row(0x506201,[]))
   self.assertEqual(self.recover(p)['status'],'unsupported',mode)

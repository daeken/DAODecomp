"""Narrow void source hypotheses; typed effects are not artifact acceptance."""
import copy,json,struct,subprocess,unittest
from test_replayable_ir import DLL,DOTNET,node,ty,reg,const,write,binary
from test_replayable_stackargs import row,ret
from test_replayable_conditional import call
from test_replayable_byvalue import push

def stores():
 b=0x506000
 return dict(rva=0x6000,image_base=0x500000,image_end=0x510000,module='open.exe',lift=dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=[row(b,[node('IlStore',Addr=binary('Add',reg(1),const(28,64)),Val=const(0x509020))],'c7411c20905000'),row(b+7,ret(0),'c3')]))

def member(values=(17,29)):
 p=stores();b=0x506000;target=0x507000;rows=[]
 for value in reversed(values):
  pc=b+sum(r['length']for r in rows);rows.append(row(pc,push(const(value)),'68'+struct.pack('<I',value).hex()))
 pc=b+sum(r['length']for r in rows);rows.append(row(pc,call(pc,target),(b'\xe8'+struct.pack('<i',target-pc-5)).hex()));rows.append(row(pc+5,ret(0),'c3'))
 p.update(stack_arguments=True,callee_lifts=[dict(target=target,lift=dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=[row(target,ret(len(values)*4),'c2'+struct.pack('<H',len(values)*4).hex())]))]);p['lift']['instructions']=rows;return p

@unittest.skipUnless(DLL.exists(),'build component first')
class VoidProposalTests(unittest.TestCase):
 def recover(self,p):return json.loads(subprocess.check_output([DOTNET,str(DLL),'recover-ir'],input=json.dumps(p).encode()))
 def test_store_only_preserves_observed_entry_return_register_in_ir(self):
  x=self.recover(stores());self.assertEqual(x['status'],'generated',x);self.assertEqual(x['ir']['return'],dict(kind='register_input',index=0));self.assertEqual(x['ir']['effects'][0]['bits'],32);self.assertEqual(x['ir']['effects'][0]['address']['offset'],28);self.assertIn('void Recovered::fn_00006000()',x['source']);self.assertNotIn('return this',x['source']);self.assertFalse(x['proof'])
 def test_store_proposal_rejects_other_return_and_nonreceiver_address(self):
  for mode in ('return','address','width'):
   p=stores();body=p['lift']['instructions'][0]['tree']['Body']
   if mode=='return':body.append(write(0,reg(2)))
   elif mode=='address':body[0]['Addr']=reg(2)
   else:body[0]['Val']=const(3,64)
   self.assertEqual(self.recover(p)['status'],'unsupported',mode)
 def test_constant_member_argument_order_and_unknown_boundary(self):
  x=self.recover(member());self.assertEqual(x['status'],'generated',x);ir=x['ir'];self.assertEqual([v['value']for v in ir['calls'][0]['arguments']],[17,29]);self.assertEqual([v['value']['value']for v in ir['function']['stack_effects']],[29,17]);self.assertEqual(ir['calls'][0]['evidence']['cleanup_bytes'],8);self.assertFalse(ir['calls'][0]['evidence']['proof']);self.assertEqual(ir['function']['return']['kind'],'unknown');self.assertIn('fn_00007000(17u, 29u);',x['source']);self.assertNotIn('extern "C"',x['source']);self.assertNotIn('noexcept',x['source']);self.assertFalse(x['proof'])
 def test_one_and_four_words_supported_five_refuses(self):
  for count in (1,4,5):
   x=self.recover(member(tuple(range(count))));self.assertEqual(x['status'],'generated'if count<=4 else'unsupported',x)
 def test_extra_observable_effect_receiver_change_and_nonconstant_refuse(self):
  for mode in ('store','receiver','argument','narrow'):
   p=member();rows=p['lift']['instructions']
   if mode=='store':rows[0]['tree']['Body'].insert(0,node('IlStore',Addr=reg(1),Val=const(7)))
   elif mode=='receiver':rows[0]['tree']['Body'].insert(0,write(1,reg(2)))
   else:rows[0]['tree']['Body'][0]['Val']=reg(0)if mode=='argument'else const(7,16)
   self.assertEqual(self.recover(p)['status'],'unsupported',mode)
 def test_callee_cleanup_disagreement_incomplete_or_missing_evidence_refuses(self):
  for mode in ('cleanup','partial','missing'):
   p=member()
   if mode=='missing':p['callee_lifts']=[]
   elif mode=='partial':p['callee_lifts'][0]['lift']['decode_complete']=False
   else:p['callee_lifts'][0]['lift']['instructions'][0]['tree']['Body']=ret(4)
   self.assertEqual(self.recover(p)['status'],'unsupported',mode)
 def test_incoming_value_cannot_become_constant_word(self):
  p=member();p['lift']['instructions'][0]['tree']['Body'][0]['Val']=node('IlLoad',Addr=binary('Add',reg(4),const(4,64)),Ty=ty(32));self.assertEqual(self.recover(p)['status'],'unsupported')

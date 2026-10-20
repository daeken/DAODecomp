"""Open capture/def-use boundaries; no instruction scheduling promises."""
import json,subprocess,unittest,struct
from test_replayable_ir import DLL,DOTNET,node,const,reg,write,ty
from test_replayable_loops import binary,reg32
from test_replayable_byvalue import load
from test_replayable_terminal_calls import mutable_fixture

def temporary(i):return node('IlTmp',Id=i,Ty=ty(32))
def let(i,v):return node('IlLet',Id=i,Val=v)
def payload(body):
 p,_=mutable_fixture();p.update(typed_receiver=True,compact_scalars=True);p['lift']['instructions'][12]['tree']['Body']=body+[node('IlStore',Addr=binary('Add',reg(6),const(12,64)),Val=temporary(1))];return p

def deferred_predicate_fixture(overwrite=True):
 from test_replayable_conditional import fw,flag
 from test_replayable_stackargs import row
 p,_=mutable_fixture();rows=p['lift']['instructions'];captured=node('IlTmp',Id=7,Ty=ty(32));rows[3]['tree']['Body']=[let(7,reg32(0)),fw(0,const(0,1)),fw(6,binary('Eq',captured,const(0),1))];rows[4]['tree']['Body'][0]['Cond']=binary('Or',flag(0),flag(6),1);rows[4]['raw_hex']='7600'
 if overwrite:rows.insert(4,row(0xdead0000,[write(0,const(17))],'b811000000'))
 mapping={};pc=0x508000
 for rr in rows:mapping[rr['pc']]=pc;pc+=rr['length']
 for rr in rows:
  rr['pc']=mapping[rr['pc']]
  for n in rr['tree']['Body']:
   if n['type']=='LiftIl.IlBranch':
    if n['Kind']['name']=='CondJmp':
     dest=mapping[int(n['Target']['Bits']['decimal'])];n['Target']=const(dest,32);rr['raw_hex']=(b'\x76'+struct.pack('b',dest-rr['pc']-2)).hex()
    elif n['Kind']['name']=='Call':
     dest=int(rr['tree']['Body'][0]['Val']['Bits']['decimal']);rr['raw_hex']=(b'\xe8'+struct.pack('<i',dest-rr['pc']-5)).hex()
     for effect in rr['tree']['Body']:
      if effect['type']=='LiftIl.IlStore':effect['Val']=const(rr['pc']+5,32)
 p.update(typed_receiver=True,compact_scalars=True);return p,rows[3]['pc']

@unittest.skipUnless(DLL.exists(),'build changed component first')
class ScalarSourceTests(unittest.TestCase):
 def recover(self,p):return json.loads(subprocess.check_output([DOTNET,str(DLL),'recover-ir'],input=json.dumps(p).encode()))
 def test_deferred_test_predicate_retains_capture_after_register_overwrite(self):
  p,pc=deferred_predicate_fixture();x=self.recover(p);self.assertEqual(x['status'],'generated',x);p['compact_scalars']=False;old=self.recover(p);self.assertEqual(x['ir'],old['ir']);name=f't_{pc:x}_7';self.assertIn(f'{name} =',x['source']);self.assertIn(f'if (({name} > 0u))',x['source']);self.assertNotIn('if ((r_0 > 0u))',x['source']);self.assertLess(x['source'].index(f'{name} ='),x['source'].index('r_0 = 17u;'))
 def test_deferred_test_predicate_keeps_stable_spelling_without_overwrite(self):
  p,pc=deferred_predicate_fixture(False);x=self.recover(p);self.assertEqual(x['status'],'generated',x);self.assertIn(f'if ((t_{pc:x}_7 > 0u))',x['source'])
 def test_single_use_pure_word_chain_inlines_without_changing_shared_ir(self):
  p=payload([let(0,reg32(0)),let(1,binary('Add',temporary(0),const(0xffffffff)))]);x=self.recover(p);self.assertEqual(x['status'],'generated',x);p['compact_scalars']=False;old=self.recover(p);self.assertEqual(x['ir'],old['ir']);pc=p['lift']['instructions'][12]['pc'];self.assertNotIn(f't_{pc:x}_0',x['source']);self.assertNotIn(f't_{pc:x}_1',x['source']);self.assertIn('4294967295u',x['source']);self.assertIn('r_0 + 4294967295u',x['source']);self.assertIn(f't_{pc:x}_0',old['source'])
 def test_register_overwrite_keeps_original_capture_and_transitive_capture(self):
  p=payload([let(0,reg32(0)),let(1,binary('Add',temporary(0),const(1))),write(0,const(99))]);x=self.recover(p);self.assertEqual(x['status'],'generated',x);pc=p['lift']['instructions'][12]['pc'];self.assertIn(f't_{pc:x}_0',x['source']);self.assertIn(f't_{pc:x}_1',x['source']);self.assertLess(x['source'].index(f't_{pc:x}_0 ='),x['source'].index('r_0 = 99u;'))
 def test_intervening_memory_store_is_a_capture_fence(self):
  p=payload([let(0,reg32(0)),node('IlStore',Addr=binary('Add',reg(6),const(16,64)),Val=const(1)),let(1,binary('Add',temporary(0),const(1)))]);x=self.recover(p);self.assertEqual(x['status'],'generated',x);pc=p['lift']['instructions'][12]['pc'];self.assertIn(f't_{pc:x}_0 =',x['source'])
 def test_flag_overwrite_keeps_captured_flag_value(self):
  flag=lambda v:node('IlWriteReg',Kind=dict(name='Eflags'),Idx=0,Val=const(v,1))
  value=node('IlReadReg',Kind=dict(name='Eflags'),Idx=0,Ty=ty(1));captured=node('IlTmp',Id=0,Ty=ty(1))
  p=payload([flag(1),let(0,value),flag(0),let(1,node('IlCast',Kind=dict(name='Zext'),X=captured,Ty=ty(32)))]);x=self.recover(p);self.assertEqual(x['status'],'generated',x);pc=p['lift']['instructions'][12]['pc'];self.assertIn(f't_{pc:x}_0 =',x['source']);self.assertLess(x['source'].index(f't_{pc:x}_0 ='),x['source'].index('f_0 = 0u;',x['source'].index(f't_{pc:x}_0 =')))
 def test_memory_read_stays_captured_and_is_not_duplicated(self):
  p=payload([let(0,load(binary('Add',reg(6),const(8,64)))),let(1,binary('Add',temporary(0),const(1)))]);x=self.recover(p);self.assertEqual(x['status'],'generated',x);pc=p['lift']['instructions'][12]['pc'];self.assertIn(f't_{pc:x}_0 =',x['source']);self.assertEqual(x['source'].count(f't_{pc:x}_0 ='),1)
 def test_multiple_uses_keep_capture_instead_of_expanding_expression_tree(self):
  p=payload([let(0,binary('Add',reg32(0),const(1))),let(1,binary('Add',temporary(0),temporary(0)))]);x=self.recover(p);self.assertEqual(x['status'],'generated',x);pc=p['lift']['instructions'][12]['pc'];self.assertIn(f't_{pc:x}_0 =',x['source'])
 def test_source_changes_are_opt_in_and_unsigned_views_keep_low32_width(self):
  p,_=mutable_fixture();old=self.recover(p);p.update(typed_receiver=True,compact_scalars=True);x=self.recover(p);self.assertEqual(x['status'],'generated',x);self.assertEqual(x['ir'],old['ir']);self.assertNotIn('volatile',x['source']);self.assertNotIn('__asm',x['source']);self.assertLess(x['source'].count('static_cast'),old['source'].count('static_cast'));self.assertIn('this->field_000c',x['source'])

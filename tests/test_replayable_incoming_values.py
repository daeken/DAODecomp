"""Open incoming-storage/value separation; generated source alone grants no credit."""
import copy,json,subprocess,unittest
from test_replayable_ir import DLL,DOTNET,node,const,reg
from test_replayable_loops import binary,reg32
from test_replayable_terminal_calls import mutable_fixture,mixed_width_fixture,terminal_width_fixture
from test_replayable_scalar_source import deferred_predicate_fixture

@unittest.skipUnless(DLL.exists(),'build changed component first')
class IncomingValueIdentityTests(unittest.TestCase):
 def recover(self,p):return json.loads(subprocess.check_output([DOTNET,str(DLL),'recover-ir'],input=json.dumps(p).encode()))
 def payload(self):
  p,_=mutable_fixture();p.update(typed_receiver=True,compact_scalars=True,incoming_value_identities=True);return p
 def test_initial_capture_and_architectural_effects_survive_separate_carrier(self):
  p=self.payload();x=self.recover(p);self.assertEqual(x['status'],'generated',x);p['incoming_value_identities']=False;old=self.recover(p);self.assertEqual(x['ir'],old['ir']);source=x['source'];self.assertIn('unsigned int slot_value_0004;',source);self.assertIn('slot_value_0004 = r_2;',source);self.assertNotIn('arg_0 =',source);self.assertIn('r_0 = arg_0;',source);self.assertIn('r_2 = slot_value_0004;',source)
  effects=[e for path in x['ir']['flow']['normal_paths']for e in path['effects']];self.assertTrue(any(e['kind']=='incoming_store'for e in effects));self.assertTrue(any(e['kind']=='incoming_slot_read'for e in effects));self.assertTrue(any(e['kind']=='external_call'and e['call']['memory_effects_unknown']for e in effects))
 def test_multiple_fullword_definitions_keep_order_and_same_slot_identity(self):
  p=self.payload();row=p['lift']['instructions'][10];row['tree']['Body'].insert(0,node('IlStore',Addr=binary('Add',reg(4),const(8,64)),Val=const(0xffffffff)));x=self.recover(p);self.assertEqual(x['status'],'generated',x);self.assertIn('slot_value_0004 = 4294967295u;\n',x['source']);self.assertLess(x['source'].index('slot_value_0004 = 4294967295u;'),x['source'].index('slot_value_0004 = r_2;'))
 def test_partial_and_overlapping_incoming_storage_refuse(self):
  for mode in ('byte','overlap'):
   p=self.payload();store=p['lift']['instructions'][10]['tree']['Body'][0]
   if mode=='byte':store['Val']=const(1,8)
   else:store['Addr']=binary('Add',reg(4),const(9,64))
   self.assertEqual(self.recover(p)['status'],'unsupported',mode)
 def test_unknown_alias_between_word_store_and_read_refuses(self):
  p=self.payload();p['lift']['instructions'][10]['tree']['Body'].append(node('IlStore',Addr=binary('Add',reg(6),const(16,64)),Val=const(9)));x=self.recover(p);self.assertEqual(x['status'],'unsupported',x);self.assertIn('unknown_incoming_slot_read',x['blocker'])
 def test_escaped_stack_value_is_not_a_private_slot_assumption(self):
  p=self.payload();p['lift']['instructions'][10]['tree']['Body'][0]['Val']=reg32(4);x=self.recover(p);self.assertEqual(x['status'],'unsupported',x)
 def test_byte_declared_argument_cannot_hold_fullword_carrier(self):
  p=mixed_width_fixture(8);p.update(incoming_value_identities=True);x=self.recover(p);self.assertEqual(x['status'],'unsupported',x);self.assertIn('mixed_width',x['blocker'])
 def test_live_deferred_flag_capture_stays_stable(self):
  p,pc=deferred_predicate_fixture();p['incoming_value_identities']=True;x=self.recover(p);self.assertEqual(x['status'],'generated',x);self.assertIn(f'if ((t_{pc:x}_7 > 0u))',x['source']);p['incoming_value_identities']=False;self.assertEqual(x['ir'],self.recover(p)['ir'])
 def test_opt_in_does_not_introduce_volatile_or_assembly(self):
  x=self.recover(self.payload());self.assertNotIn('__asm',x['source']);self.assertNotIn('volatile',x['source']);self.assertIn('unsigned int arg_0',x['source'])

 def test_terminal_effects_use_the_same_fullword_guard(self):
  for bits in (8,32):
   p=terminal_width_fixture(bits);p.update(incoming_value_identities=True);x=self.recover(p)
   if bits==8:self.assertEqual(x['status'],'unsupported',x)
   else:self.assertEqual(x['status'],'generated',x);self.assertIn('slot_value_0004',x['source'])
 def test_joined_values_keep_their_source_paths_and_initial_argument(self):
  p=self.payload();p['lift']['instructions'][10]['tree']['Body'][0]['Val']=reg32(0);p['lift']['instructions'][12]['tree']['Body'][0]['Val']=reg32(2);x=self.recover(p);self.assertEqual(x['status'],'generated',x);self.assertIn('slot_value_0004 = r_0;',x['source']);self.assertIn('r_0 = arg_0;',x['source']);p['incoming_value_identities']=False;self.assertEqual(x['ir'],self.recover(p)['ir'])

# Open persistence-only compiler receipts, not original/native acceptance evidence.
from test_replayable_behavioral import BehavioralPipelineTests,behavioral_recipe

def incoming_recipe():
 x=behavioral_recipe();x['architecture']='x86-bits32-incoming-slot-value-identities-v1';x['steps'].insert(-1,'emit-vc8-incoming-word-value-identities-v1');return x
class IncomingValuePipelineTests(BehavioralPipelineTests):
 def submit(self,token):return self.client.call('replayable_run_next',project_id='open',idempotency_key=token,recipe_json=json.dumps(incoming_recipe()),compile=False)
 def status(self):return self.client.call('replayable_status',project_id='open',recipe_json=json.dumps(incoming_recipe()))

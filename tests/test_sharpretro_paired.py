"""Generic synthetic machinery/mutation tests, never game evidence."""
import copy,json,sys,unittest,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
if (Path(__file__).resolve().parent/'paired.py').is_file():
 import paired as p
else:
 from tools.sharpretro import paired as p
CONFIG_PATH=os.environ.get('SHARPRETRO_CONFIG')
if CONFIG_PATH:p.configure(CONFIG_PATH)

def lift(h):return p.lift_raw(bytes.fromhex(h))
def pair(a,b):return p.diagnose(lift(a),lift(b))
def nodes(value):
 if isinstance(value,dict):
  yield value
  for v in value.values():yield from nodes(v)
 elif isinstance(value,list):
  for v in value:yield from nodes(v)

@unittest.skipUnless(CONFIG_PATH, 'Set SHARPRETRO_CONFIG to an explicit pinned adapter config')
class LiftTests(unittest.TestCase):
 def test_deterministic_complete_typed_roundtrip(self):
  a=lift('83c001c3');b=lift('83c001c3');self.assertEqual(p.diagnose(a,b)['state'],'exact_lift_tree_agreement')
  self.assertTrue(a['complete_supported']);self.assertEqual(a['decoded_bytes'],4)
  self.assertEqual(json.loads(json.dumps(a))['instructions'],a['instructions'])
  ns=list(nodes(a['instructions'][0]['tree']))
  self.assertTrue(any(x.get('type')=='LiftIl.IlType+I' and x.get('Bits')==32 and x.get('Signed') is False for x in ns))
  self.assertTrue(any(x.get('type')=='LiftIl.IlWriteReg' and x['Kind']['name']=='Eflags' for x in ns))
 def test_immediate_mutation(self):self.assertEqual(pair('83c001c3','83c002c3')['state'],'differing_supported_il')
 def test_register_livein_mutation(self):self.assertEqual(pair('8bc1c3','8bc2c3')['state'],'differing_supported_il')
 def test_memory_address_mutation(self):self.assertEqual(pair('8b4104c3','8b4108c3')['state'],'differing_supported_il')
 def test_flags_not_discarded(self):self.assertEqual(pair('83c001c3','40c3')['state'],'differing_supported_il')
 def test_width_preserved(self):self.assertEqual(pair('6683c001c3','83c001c3')['state'],'differing_supported_il')
 def test_signed_branch_condition(self):self.assertEqual(pair('720090c3','7c0090c3')['state'],'differing_supported_il')
 def test_call_target_preserved(self):self.assertEqual(pair('e800000000c3','e801000000c3')['state'],'differing_supported_il')
 def test_indirect_call_livein(self):self.assertEqual(pair('ffd0c3','ffd1c3')['state'],'differing_supported_il')
 def test_ret_cleanup(self):self.assertEqual(pair('c20400','c20800')['state'],'differing_supported_il')
 def test_truncated_instruction_is_not_skipped(self):
  x=lift('900f');self.assertFalse(x['decode_complete']);self.assertEqual(x['unprocessed_hex'],'0f');self.assertEqual(p.diagnose(x,x)['state'],'incomplete_lift')
 def test_opaque_x87_retained(self):
  x=lift('d9e8c3');self.assertGreater(x['opaque_instructions'],0);self.assertEqual(p.diagnose(x,x)['state'],'opaque_or_unsupported')
 def test_internal_nonboundary_branch(self):
  x=lift('ebff');self.assertTrue(x['nonboundary_internal_edges']);self.assertEqual(p.diagnose(x,x)['state'],'incomplete_lift')
 def test_decoder_disagreement_fails_closed(self):
  x=lift('90c3');x['decoder_boundaries_agree']=False;self.assertEqual(p.diagnose(x,x)['state'],'incomplete_lift')
 def test_lock_is_not_silent(self):
  x=lift('f0830001c3');self.assertTrue(x['architectural_context_markers']);self.assertEqual(p.diagnose(x,x)['state'],'opaque_or_unsupported')
 def test_distinct_encoding_measured(self):
  # ADD EAX,1 short signed immediate vs full immediate. No byte or NOP erasure.
  x=pair('83c001','0501000000');self.assertEqual(x['state'],'exact_lift_tree_agreement')
 def test_no_nop_dropping(self):self.assertEqual(pair('c3','90c3')['state'],'differing_supported_il')
 def test_no_address_normalization(self):
  a=lift('e800000000c3');b=p.lift_raw(bytes.fromhex('e800000000c3'),pc=0x402000)
  self.assertEqual(p.diagnose(a,b)['state'],'differing_supported_il')
 def test_serialized_unknown_nodes_are_not_faked(self):
  x=lift('0f0bc3');self.assertFalse(x['complete_supported'])


@unittest.skipUnless(CONFIG_PATH and os.environ.get('SHARPRETRO_TEST_SUMMARY'), 'Set SHARPRETRO_TEST_SUMMARY for retained attestation negatives')
class BindingTests(unittest.TestCase):
 def setUp(self):
  import tempfile,shutil
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
  source=Path(os.environ['SHARPRETRO_TEST_SUMMARY']).resolve().parent
  for name in ('summary.json','candidate.cpp','candidate.obj','run.json','compiler.json','identities.json'):shutil.copy2(source/name,self.root/name)
  self.summary=self.root/'summary.json';self.report=json.loads(self.summary.read_text());self.rva=self.report['functions'][0]['rva']
 def save(self):self.summary.write_text(json.dumps(self.report))
 def test_source_mutation_rejected(self):
  with (self.root/'candidate.cpp').open('ab') as f:f.write(b'\n')
  with self.assertRaisesRegex(ValueError,'source_hash'):p.bound_function(self.summary,self.rva)
 def test_object_mutation_rejected(self):
  with (self.root/'candidate.obj').open('ab') as f:f.write(b'\0')
  with self.assertRaisesRegex(ValueError,'object_hash'):p.bound_function(self.summary,self.rva)
 def test_flags_even_consistently_rebound_rejected(self):
  build=json.loads((self.root/'run.json').read_text());build['flags']=['/Od'];(self.root/'run.json').write_text(json.dumps(build));self.report['build']=build;self.save()
  with self.assertRaisesRegex(ValueError,'compiler_flags'):p.bound_function(self.summary,self.rva)
 def test_compiler_even_consistently_rebound_rejected(self):
  build=json.loads((self.root/'run.json').read_text());compiler=build['compiler'];compiler['sha256']='0'*64
  (self.root/'compiler.json').write_text(json.dumps(compiler));(self.root/'run.json').write_text(json.dumps(build));self.report['compiler']=compiler;self.report['build']=build;self.save()
  with self.assertRaisesRegex(ValueError,'compiler_identity'):p.bound_function(self.summary,self.rva)
 def test_symbol_identity_rejected(self):
  ids=json.loads((self.root/'identities.json').read_text());key=next(iter(ids['symbols']));ids['symbols'][key]+=4
  self.report['symbol_addresses']=ids['symbols'];(self.root/'identities.json').write_text(json.dumps(ids));self.save()
  with self.assertRaisesRegex(ValueError,'stable_symbol_identity'):p.bound_function(self.summary,self.rva)
 def test_stale_comparator_rejected(self):
  self.report['implementation_sha256']['compare.py']='0'*64;self.save()
  with self.assertRaisesRegex(ValueError,'comparator_binding'):p.bound_function(self.summary,self.rva)
 def test_forged_comparison_result_rejected(self):
  self.report['functions'][0]['original_size']+=1;self.save()
  with self.assertRaisesRegex(ValueError,'fresh_comparator_replay'):p.bound_function(self.summary,self.rva)

if __name__=='__main__':unittest.main()

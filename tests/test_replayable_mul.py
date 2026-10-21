"""Open unsigned-MUL wire boundaries; no original-game fixture or acceptance."""
import json,os,subprocess,unittest
from pathlib import Path
from rapid_object.encoding_equivalence import Refusal
from tools.replayable.effect_relation import State,Terms
from test_replayable_ir import node,ty

def nodes(x):
 if isinstance(x,dict):
  yield x
  for value in x.values():yield from nodes(value)
 elif isinstance(x,list):
  for value in x:yield from nodes(value)

class MulConsumerTests(unittest.TestCase):
 def test_scalar_effect_consumer_refuses_unknown_flags_and_wide_products(self):
  for value,reason in ((node('IlUndefined',Ty=ty(1),Reason='MUL undefined flag'),'effect_unsupported_value'),(node('IlConst',Ty=ty(128),Bits=dict(decimal='0')),'effect_integer_width')):
   with self.subTest(value=value),self.assertRaises(Refusal):State(Terms()).value(value)
 def test_registered_unsigned_adapter_keeps_explicit_undefined_flags(self):
  config=os.environ.get('DECOMPILATION_REPLAYABLE_TEST_LIFTER_CONFIG')
  if not config:self.skipTest('separate reviewed unsigned-MUL lifter build not supplied')
  cfg=json.loads(Path(config).read_text())
  for raw in ('f6e6','66f7e6','f7e6','f72424'):
   with self.subTest(raw=raw):
    req=dict(hex=raw,pc=0x502000,id='open-unsigned-mul')
    result=json.loads(subprocess.check_output([cfg['dotnet'],cfg['adapter_dll']],input=(json.dumps(req)+'\n').encode()))
    self.assertTrue(result['decode_complete']);self.assertEqual(result['lift_errors'],0);self.assertEqual(result['opaque_instructions'],0)
    all_nodes=list(nodes(result));undefined=[x for x in all_nodes if x.get('type')=='LiftIl.IlUndefined'];self.assertEqual(len(undefined),4)
    self.assertTrue(all(x['Ty']['Bits']==1 and x['Reason'] for x in undefined))
    writers=[x for x in all_nodes if x.get('type')=='LiftIl.IlWriteReg' and x.get('Val',{}).get('type')=='LiftIl.IlUndefined'];self.assertEqual({x['Idx'] for x in writers},{2,4,6,7})
    self.assertTrue(any(x.get('type')=='LiftIl.IlBin' and x.get('Op',{}).get('name')=='Mul' for x in all_nodes))

"""Open typed stack/call fixtures; source hypotheses earn no native match credit."""
import copy,json,subprocess,unittest
from pathlib import Path
from test_replayable_ir import ROOT,DLL,DOTNET,node,ty,reg,const,binary,write,tmp,fixture as ordinary
from test_replayable_stackargs import row,ret
from test_replayable_conditional import call

def load(a,bits=32):return node('IlLoad',Addr=a,Ty=ty(bits))
def push(v):return [node('IlLet',Id=0,Val=v),write(4,binary('Sub',reg(4),const(4,64))),node('IlStore',Addr=reg(4),Val=tmp(0,32))]
def fixture():
 rows=[];base=0x502000
 def add(body,raw='90'):
  pc=base+sum(r['length'] for r in rows);rows.append(row(pc,body,raw));return pc
 add(push(reg(1)))
 add([node('IlStore',Addr=reg(4),Val=const(0,8))])
 add([write(0,load(reg(4)))])
 add(push(reg(0)))
 for _ in range(3):add(push(load(binary('Add',reg(4),const(20,64)))))
 pc=base+sum(r['length'] for r in rows);add(call(pc,0x503000),'e800000000')
 add([write(4,binary('Add',reg(4),const(20,64)))])
 add(ret(0),'c3')
 callee=dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=[row(0x503000,ret(0),'c3')])
 return dict(lift=dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=rows),callee_lifts=[dict(target=0x503000,lift=callee)],by_value_calls=True,rva=0x2000,image_base=0x500000,image_end=0x510000,module='open.exe')

@unittest.skipUnless(DLL.exists(),'build changed component first')
class ByValueTests(unittest.TestCase):
 def recover(self,p):return json.loads(subprocess.check_output([DOTNET,str(DLL),'recover-ir'],input=json.dumps(p).encode()))
 def test_private_byte_copy_outgoing_extent_and_unknown_return(self):
  r=self.recover(fixture());self.assertEqual(r['status'],'generated',r);ir=r['ir'];call_=ir['call'];self.assertEqual((len(call_['arguments']),call_['caller_cleanup'],call_['caller_private_cleanup_bytes']),(4,20,4));self.assertEqual(ir['function']['incoming']['required_read_bytes'],12);self.assertFalse(ir['function']['incoming']['exact_arity_known']);self.assertFalse(call_['formal_arity_known']);self.assertTrue(call_['memory_effects_unknown']);self.assertTrue(call_['throw_behavior_unknown']);self.assertEqual(ir['function']['normal_paths'][0]['exit']['return']['kind'],'external_register');self.assertIn('return fn_00003000(arg_0, arg_1, arg_2, local_3)',r['source']);self.assertEqual(ir['carriers'][0]['preserved_upper_bits']['operands'][1]['value'],0xffffff00);self.assertEqual(ir['carriers'][0]['preserved_upper_bits']['operands'][0],dict(kind='register_input',index=1));self.assertIn('padding unspecified',ir['carriers'][0]['basis']);self.assertNotIn('unsigned int local_',r['source'])
 def test_distinct_repeated_incoming_reads_are_preserved_in_source_profile(self):
  p=fixture();p['lift']['instructions'][4]['tree']['Body'][0]['Val']['Addr']=binary('Add',reg(4),const(16,64));r=self.recover(p);self.assertEqual(r['status'],'generated',r);self.assertIn('volatile unsigned int arg_1',r['source']);reads=[e for e in r['ir']['function']['normal_paths'][0]['effects'] if e['kind']=='incoming_read' and e['value']['offset']==8];self.assertEqual(len(reads),2);self.assertNotEqual(reads[0]['pc'],reads[1]['pc'])
 def test_return_slot_overlap_and_private_extent_refuse(self):
  for offset in (4,3,-1):
   p=fixture();p['lift']['instructions'][1]['tree']['Body'][0]['Addr']=binary('Add',reg(4),const(offset if offset>=0 else (1<<64)+offset,64));self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_partial_word_requires_complete_prior_initialization(self):
  p=fixture();p['lift']['instructions'][0]['tree']['Body']=[write(4,binary('Sub',reg(4),const(4,64)))];self.assertEqual(self.recover(p)['blocker'],'flow_private_subword_without_initialized_word')
 def test_nonlow_byte_and_word_carriers_are_not_invented(self):
  for bits,offset in ((16,0),(8,1)):
   p=fixture();store=p['lift']['instructions'][1]['tree']['Body'][0];store['Val']=const(0,bits);store['Addr']=binary('Add',reg(4),const(offset,64));self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_cleanup_cannot_swallow_unclassified_frame_or_return_address(self):
  for amount in (16,24,68):
   p=fixture();p['lift']['instructions'][-2]['tree']['Body'][0]['Val']=binary('Add',reg(4),const(amount,64));self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_call_target_form_not_constant_propagation_decides_directness(self):
  p=fixture();c=p['lift']['instructions'][-3]['tree']['Body'];c[0]['Val']=reg(1);self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_undefined_values_refuse_in_all_symbolic_recovery_paths(self):
  undefined=node('IlUndefined',Ty=ty(32),Reason='open undefined architectural value')
  p=fixture();p['lift']['instructions'][0]['tree']['Body'][0]['Val']=undefined;r=self.recover(p);self.assertEqual(r['status'],'unsupported');self.assertIn('undefined_architectural_value',r['blocker'])
  for flag in ({},{'flow_paths':True}):
   p=ordinary();p['lift']['instructions'][0]['raw_hex']='90';p['lift']['instructions'][0]['tree']['Body']=[write(0,undefined)]
   for row_ in p['lift']['instructions']:row_.setdefault('raw_hex','90')
   p.update(flag,callee_lifts=[]);r=self.recover(p);self.assertEqual(r['status'],'unsupported');self.assertIn('undefined_architectural_value',r['blocker'])
  from test_replayable_conditional import fixture as conditional_fixture
  p=conditional_fixture();p['callee_lifts']=p.pop('callees');p['conditional_calls']=True;p['lift']['instructions'][0]['tree']['Body'][0]['Val']=undefined;r=self.recover(p);self.assertEqual(r['status'],'unsupported');self.assertIn('undefined_architectural_value',r['blocker'])
 def test_complete_callee_normal_return_evidence_keeps_undefined_effects_unknown(self):
  p=fixture();callee=p['callee_lifts'][0]['lift'];callee['instructions']=[row(0x503000,[node('IlWriteReg',Kind=dict(name='Eflags'),Idx=2,Val=node('IlUndefined',Ty=ty(1),Reason='undefined flag'))],'90'),row(0x503001,ret(0),'c3')]
  r=self.recover(p);self.assertEqual(r['status'],'generated',r);self.assertTrue(r['ir']['call']['memory_effects_unknown']);self.assertFalse(r['ir']['call']['evidence']['normal_return']['proof'])

class UndefinedWireTests(unittest.TestCase):
 def test_registered_private_adapter_preserves_typed_undefined_flags(self):
  import os
  config=os.environ.get('DECOMPILATION_REPLAYABLE_TEST_LIFTER_CONFIG')
  if not config:self.skipTest('separate reviewed lifter build not supplied')
  cfg=json.loads(Path(config).read_text());dll=Path(cfg['adapter_dll'])
  def nodes(x):
   if isinstance(x,dict):
    yield x
    for v in x.values():yield from nodes(v)
   elif isinstance(x,list):
    for v in x:yield from nodes(v)
  for raw in ('f6ebc3','66f7eac3','f7eac3'):
   result=json.loads(subprocess.check_output([cfg.get('dotnet',DOTNET),str(dll)],input=(json.dumps(dict(hex=raw,pc=0x502000,id='open-imul'))+'\n').encode()));self.assertTrue(result['decode_complete']);self.assertEqual(result['opaque_instructions'],0)
   undefined=[n for n in nodes(result) if n.get('type')=='LiftIl.IlUndefined'];self.assertEqual(len(undefined),4)
   writers=[n for n in nodes(result) if n.get('type')=='LiftIl.IlWriteReg' and n.get('Val',{}).get('type')=='LiftIl.IlUndefined'];self.assertEqual({n['Idx'] for n in writers},{2,4,6,7});self.assertTrue(all(n['Kind']['name']=='Eflags' for n in writers))
   for n in undefined:self.assertEqual(n['Ty']['Bits'],1);self.assertTrue(n['Reason'])


class BatchDecisionDocumentTests(unittest.TestCase):
 def test_large_input_decision_is_distinct_from_small_receipt_budget(self):
  import importlib.util,tempfile
  from tools.replayable import guest_batch
  spec=importlib.util.spec_from_file_location('byvalue_adapter',ROOT/'tools/decompilation-mcp/replayable_adapter.py');adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'dispatch-decision.json';value=dict(group_id='a'*32,members=[dict(job_id=str(i),inputs={'original_source_closure':'b'*100000}) for i in range(16)]);path.write_text(json.dumps(value));self.assertGreater(path.stat().st_size,1024*1024);self.assertEqual(adapter.read_batch_dispatch_decision(path),value)
   with self.assertRaises(ValueError):guest_batch.read_json(path)
   for content in ('{"group_id":"a","group_id":"b"}','[invalid', ' '* (16*1024*1024+1)):
    path.write_text(content)
    with self.assertRaises(ValueError):adapter.read_batch_dispatch_decision(path)
   path.unlink()
   with self.assertRaises(ValueError):adapter.read_batch_dispatch_decision(path)
   if __import__('os').name=='posix':
    target=Path(folder)/'real.json';target.write_text('{}');path.symlink_to(target)
    with self.assertRaises(ValueError):adapter.read_batch_dispatch_decision(path)

"""Open typed x86 effects; no game fixtures, compiler or acceptance in unit tests."""
import copy
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest
from test_replayable_ir import node,ty,reg,const,binary,write,tmp
from test_replayable_stackargs import row,ret
ROOT=Path(__file__).resolve().parents[1]
DOTNET=shutil.which('dotnet')
def flag(i):return node('IlReadReg',Kind=dict(name='Eflags'),Idx=i,Ty=ty(1))
def fw(i,v):return node('IlWriteReg',Kind=dict(name='Eflags'),Idx=i,Val=v)
def op(name,l,r,bits):return node('IlBin',Op=dict(name=name),L=l,R=r,Ty=ty(bits))
def push():return [node('IlLet',Id=0,Val=reg(6)),write(4,binary('Sub',reg(4),const(4,64))),node('IlStore',Addr=reg(4),Val=tmp(0,32))]
def call(pc,target):return [node('IlLet',Id=0,Val=const(target)),node('IlLet',Id=1,Val=const(pc+5)),write(4,binary('Sub',reg(4),const(4,64))),node('IlStore',Addr=reg(4),Val=tmp(1,32)),node('IlBranch',Kind=dict(name='Call'),Cond=None,Target=tmp(0,32))]
def fixture():
 base=0x502000;rows=[]
 def add(body,raw):
  pc=base+sum(r['length'] for r in rows);rows.append(row(pc,body,raw));return pc
 add(push(),'56');add([write(6,reg(1))],'8bf1');add([node('IlStore',Addr=reg(6),Val=const(0x500900))],'c70600095000')
 pc=base+sum(r['length'] for r in rows);add(call(pc,0x503100),(b'\xe8'+struct.pack('<i',0x503100-pc-5)).hex())
 value=op('And',node('IlLoad',Addr=binary('Add',reg(4),const(8,64)),Ty=ty(8)),const(1,8),8)
 add([node('IlLet',Id=0,Val=value),fw(0,const(0,1)),fw(11,const(0,1)),fw(7,node('IlCast',Kind=dict(name='Trunc'),Ty=ty(1),X=op('Shr',tmp(0,8),const(7,8),8))),fw(2,op('Eq',tmp(0,8),const(0,8),1)),fw(6,op('Eq',tmp(0,8),const(0,8),1))],'f644240801')
 branch_index=len(rows);add([node('IlBranch',Kind=dict(name='CondJmp'),Cond=flag(6),Target=const(0,64))],'7409')
 add(push(),'56');pc=base+sum(r['length'] for r in rows);add(call(pc,0x503000),(b'\xe8'+struct.pack('<i',0x503000-pc-5)).hex())
 add([write(4,binary('Add',reg(4),const(4,64))),fw(6,op('Eq',reg(4),const(0,64),1))],'83c404')
 join=base+sum(r['length'] for r in rows);rows[branch_index]['tree']['Body'][0]['Target']=const(join,64)
 add([write(0,reg(6))],'8bc6');add([node('IlLet',Id=0,Val=node('IlLoad',Addr=reg(4),Ty=ty(32))),write(4,binary('Add',reg(4),const(4,64))),write(6,tmp(0,32))],'5e');add(ret(4),'c20400')
 def normal(pc):return dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=[row(pc,ret(0),'c3')])
 thunk=dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=[row(0x503000,[node('IlBranch',Kind=dict(name='Jmp'),Cond=None,Target=const(0x504000,64))],(b'\xe9'+struct.pack('<i',0x504000-0x503005)).hex())])
 return dict(lift=dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=rows),callees=[dict(target=0x503100,lift=normal(0x503100)),dict(target=0x503000,lift=thunk),dict(target=0x504000,lift=normal(0x504000))],rva=0x2000,image_base=0x500000,image_end=0x510000)

@unittest.skipUnless(DOTNET,'dotnet unavailable')
class ConditionalTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory(prefix='dao-conditional-');d=Path(cls.temp.name)
  for name in ('ReplayableIr.cs','ConditionalIr.cs'):shutil.copy2(ROOT/'tools/decompilation-mcp'/name,d/name)
  (d/'Probe.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup></Project>')
  (d/'Program.cs').write_text('''using System.Text.Json;using Decompilation;var options=new JsonSerializerOptions{PropertyNamingPolicy=JsonNamingPolicy.SnakeCaseLower};try{using var doc=JsonDocument.Parse(Console.In.ReadToEnd());var p=doc.RootElement;var callees=p.GetProperty("callees").EnumerateArray().Select(c=>new CalleeStackLift(c.GetProperty("target").GetUInt64(),c.GetProperty("lift"))).ToArray();if(p.TryGetProperty("resolve",out var target)){var evidence=NormalReturnResolver.Resolve(target.GetUInt64(),callees,p.TryGetProperty("budget",out var budget)?budget.GetInt32():8);Console.Write(JsonSerializer.Serialize(new{status="resolved",evidence},options));}else{var ir=X86ConditionalRecovery.Raise(p.GetProperty("lift"),Vc8ConditionalCallsProfile.Abi,callees,!p.TryGetProperty("flat",out var flat)||flat.GetBoolean());var source=Vc8ConditionalCallsProfile.Emit(ir,p.GetProperty("rva").GetUInt32(),p.GetProperty("image_base").GetUInt32(),p.GetProperty("image_end").GetUInt32(),"open.exe");Console.Write(JsonSerializer.Serialize(new{status="generated",ir,source},options));}}catch(Exception e){Console.Write(JsonSerializer.Serialize(new{status="unsupported",blocker=e.Message},options));}''')
  subprocess.run([DOTNET,'build',str(d/'Probe.csproj'),'-o',str(d/'out'),'--nologo'],check=True,text=True,capture_output=True);cls.dll=d/'out/Probe.dll'
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def recover(self,p):return json.loads(subprocess.run([DOTNET,str(self.dll)],input=json.dumps(p),text=True,capture_output=True,check=True).stdout)
 def test_structured_join_original_target_byte_read_and_caller_cleanup(self):
  result=self.recover(fixture());self.assertEqual(result['status'],'generated',result);ir=result['ir'];self.assertEqual(ir['conditional']['join']['sp'],-4);self.assertEqual(ir['exit']['sp'],8)
  call=next(e['call'] for e in ir['conditional']['fallthrough_effects'] if e['kind']=='call');self.assertEqual(call['original_target'],0x503000);self.assertEqual((call['callee_cleanup_bytes'],call['caller_cleanup_bytes']),(0,4));self.assertEqual(call['arguments'],[dict(kind='register_input',index=1)])
  self.assertEqual(call['entry_state']['sp'],-12);self.assertEqual(call['entry_state']['stack']['-8'],dict(kind='register_input',index=1));self.assertTrue(any(e['kind']=='stack_store' for e in ir['conditional']['fallthrough_effects']));self.assertTrue(call['memory_effects_unknown']);self.assertFalse(call['evidence']['proof']);self.assertEqual([n['target'] for n in call['evidence']['chain']],[0x503000,0x504000]);self.assertIn('fn_00003000(this)',result['source']);self.assertNotIn('fn_00004000',result['source']);self.assertIn('arg_0 & 1u',result['source']);self.assertEqual(call['receiver']['kind'],'unknown')
  self.assertEqual(ir['conditional']['taken_condition']['operands'][0]['operands'][0]['kind'],'incoming_stack_read');self.assertEqual(ir['conditional']['taken_condition']['operands'][0]['operands'][0]['bits'],8);self.assertGreater(ir['conditional']['taken_condition']['operands'][0]['operands'][0]['memory_epoch'],0)
  self.assertEqual(ir['conditional']['join']['flags']['6']['kind'],'unknown');self.assertEqual(ir['exit']['registers']['6'],dict(kind='register_input',index=6))
 def test_cleanup_zero_does_not_imply_no_arguments(self):
  r=self.recover(fixture());self.assertEqual(r['status'],'generated',r);calls=[e['call'] for e in r['ir']['prefix'] if e['kind']=='call'];calls+= [e['call'] for e in r['ir']['conditional']['fallthrough_effects'] if e['kind']=='call'];self.assertEqual([len(c['arguments']) for c in calls],[0,1]);self.assertEqual([c['callee_cleanup_bytes'] for c in calls],[0,0])
 def test_missing_duplicate_and_nonentry_dependencies_refuse(self):
  for edit in [lambda p:p['callees'].pop(),lambda p:p['callees'].append(copy.deepcopy(p['callees'][0])),lambda p:p['callees'][-1]['lift']['instructions'][0].update(pc=0x504001)]:
   p=fixture();edit(p);self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_thunk_cycles_and_finite_budget_refuse(self):
  p=fixture();p['resolve']=0x503000;p['budget']=0;self.assertEqual(self.recover(p)['status'],'unsupported')
  p=fixture();p['resolve']=0x503000;r=p['callees'][1]['lift']['instructions'][0];r['tree']['Body'][0]['Target']=const(0x503000,64);r['raw_hex']='e9fbffffff';self.assertEqual(self.recover(p)['blocker'],'forwarding_cycle')
 def test_thunk_side_effect_indirect_prefix_and_encoding_disagreement_refuse(self):
  edits=[lambda r:r['tree']['Body'].insert(0,write(0,const(1))),lambda r:r['tree']['Body'][0].update(Target=reg(0)),lambda r:r.update(raw_hex='66e90000',length=4),lambda r:r['tree']['Body'][0].update(Target=const(0x504001,64))]
  for edit in edits:
   p=fixture();p['resolve']=0x503000;edit(p['callees'][1]['lift']['instructions'][0]);self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_live_stack_or_preserved_register_join_must_agree(self):
  p=fixture();p['lift']['instructions'][8]['tree']['Body'][0]['Val']['R']=const(8,64);self.assertEqual(self.recover(p)['status'],'unsupported')
  p=fixture();p['lift']['instructions'][8]['tree']['Body'].append(write(7,const(3)));self.assertEqual(self.recover(p)['blocker'],'ambiguous_caller_cleanup')
  p=fixture();p['lift']['instructions'][6]['tree']['Body'].append(write(7,const(3)));self.assertEqual(self.recover(p)['blocker'],'incompatible_preserved_register_join')
 def test_unknown_flag_nonboundary_backward_or_second_branch_refuse(self):
  for edit in [lambda p:p['lift']['instructions'][5]['tree']['Body'][0].update(Cond=flag(3)),lambda p:p['lift']['instructions'][5]['tree']['Body'][0].update(Target=const(0x502001,64)),lambda p:p['lift']['instructions'][5]['tree']['Body'][0].update(Target=const(0x502000,64)),lambda p:p['lift']['instructions'][8]['tree']['Body'].append(copy.deepcopy(p['lift']['instructions'][5]['tree']['Body'][0]))]:
   p=fixture();edit(p);self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_unjustified_flat_relation_or_external_input_load_refuses(self):
  p=fixture();p['flat']=False;self.assertEqual(self.recover(p)['status'],'unsupported')
  p=fixture();p['lift']['instructions'][4]['tree']['Body'][0]['Val']['L']['Addr']=reg(1);self.assertEqual(self.recover(p)['blocker'],'unsupported_conditional_memory_load')
 def test_incoming_extent_and_subword_boundary_refuse(self):
  for offset in (3,12):
   p=fixture();p['lift']['instructions'][4]['tree']['Body'][0]['Val']['L']['Addr']['R']=const(offset,64);self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_actual_call_target_cannot_come_from_propagated_register(self):
  p=fixture();p['lift']['instructions'][7]['tree']['Body'][0]['Val']=reg(6);self.assertEqual(self.recover(p)['blocker'],'indirect_conditional_call')
 def test_call_stack_width_and_return_address_refuse(self):
  p=fixture();p['lift']['instructions'][7]['tree']['Body'][2]['Val']['R']=const(8,64);self.assertEqual(self.recover(p)['blocker'],'incorrect_Bits32_call_stack_width')
  p=fixture();p['lift']['instructions'][7]['tree']['Body'][1]['Val']=const(1);self.assertEqual(self.recover(p)['blocker'],'conditional_call_return_address_mismatch')

 def test_valid_finite_depth_boundary_and_multinode_cycle(self):
  p=fixture();p['resolve']=0x503000;p['budget']=1;self.assertEqual(self.recover(p)['status'],'resolved')
  terminal=copy.deepcopy(p['callees'][-1]);terminal['target']=0x505000;terminal['lift']['instructions'][0]['pc']=0x505000
  row=p['callees'][-1]['lift']['instructions'][0];row.update(length=5,raw_hex=(b'\xe9'+struct.pack('<i',0x505000-0x504005)).hex());row['tree']['Body']=[node('IlBranch',Kind=dict(name='Jmp'),Cond=None,Target=const(0x505000,64))];p['callees'].append(terminal)
  self.assertEqual(self.recover(p)['blocker'],'forwarding_depth_exhausted');p['budget']=2;self.assertEqual(self.recover(p)['status'],'resolved')
  row['raw_hex']=(b'\xe9'+struct.pack('<i',0x503000-0x504005)).hex();row['tree']['Body'][0]['Target']=const(0x503000,64);p['budget']=8;self.assertEqual(self.recover(p)['blocker'],'forwarding_cycle')
 def test_duplicate_call_temporary_is_not_constant_target_evidence(self):
  p=fixture();p['lift']['instructions'][7]['tree']['Body'][1]['Id']=0
  self.assertEqual(self.recover(p)['blocker'],'duplicate_conditional_call_temporary')

 def test_known_private_frame_address_cannot_escape_unknown_call(self):
  p=fixture();p['lift']['instructions'][6]['tree']['Body'][0]['Val']=reg(4)
  self.assertEqual(self.recover(p)['blocker'],'conditional_stack_address_escape')

 def test_private_word_store_requires_complete_aligned_allocated_extent(self):
  # Open MOV DWORD PTR [ESP+3],123 after PUSH ESI overlaps entry[-1,+2].
  # Refuse every partial/unaligned word, including overlap with a saved word.
  for displacement in (1,2,3,4,5,-4):
   p=fixture();body=p['lift']['instructions'][0]['tree']['Body']
   body.append(node('IlStore',Addr=binary('Add',reg(4),const(displacement,64)) if displacement>=0 else binary('Sub',reg(4),const(-displacement,64)),Val=const(123)))
   self.assertEqual(self.recover(p)['blocker'],'unsupported_conditional_stack_store')
  # The complete aligned private word at entry[-4,0) is permitted.
  p=fixture();p['lift']['instructions'][0]['tree']['Body'].append(node('IlStore',Addr=reg(4),Val=tmp(0,32)))
  self.assertEqual(self.recover(p)['status'],'generated')
 def test_private_stack_adjustment_stays_word_aligned_and_below_return(self):
  for amount in (1,2,3):
   p=fixture();p['lift']['instructions'][0]['tree']['Body'][1]['Val']['R']=const(amount,64)
   self.assertEqual(self.recover(p)['blocker'],'unsupported_conditional_SP')
  p=fixture();p['lift']['instructions'][8]['tree']['Body'][0]['Val']['R']=const(12,64)
  self.assertEqual(self.recover(p)['blocker'],'unsupported_conditional_SP')

try:
 import capstone
except ImportError:
 capstone=None

@unittest.skipUnless(capstone is not None and __import__('os').name=='posix','host original dependency decoder unavailable')
class ConditionalDependencyTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  import importlib.util
  spec=importlib.util.spec_from_file_location('conditional_adapter',ROOT/'tools/decompilation-mcp/replayable_adapter.py');cls.adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.adapter)
 def test_pure_direct_only_not_constant_propagated_or_side_effecting(self):
  p=fixture();derived=dict(lift=p['callees'][1]['lift']);self.assertEqual(self.adapter.pure_forwarding_target(derived),0x504000)
  altered=copy.deepcopy(derived);altered['lift']['instructions'][0]['tree']['Body'][0]['Target']=reg(0)
  with self.assertRaises(ValueError):self.adapter.pure_forwarding_target(altered)
  altered=copy.deepcopy(derived);altered['lift']['instructions'][0]['tree']['Body'].insert(0,write(1,const(2)));self.assertIsNone(self.adapter.pure_forwarding_target(altered))
 def run_closure(self,edit=None,profile='vc8-x86-flat32-conditional-calls-v1'):
  from unittest.mock import patch
  p=fixture();image=0x500000;values={0x2000:p['lift'],**{c['target']-image:c['lift'] for c in p['callees']}}
  if edit:edit(values)
  functions=[dict(rva=rva) for rva in values];inventory=dict(module_sha256='open-pinned',functions=functions)
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'inventory.json';path.write_text(json.dumps(inventory));request=dict(rva=0x2000,entry=functions[0],project=dict(module_sha256='open-pinned',inventory=str(path)),recipe=dict(compiler_profile=profile))
   def lift(request):return dict(lift=values[request['rva']],image_base=image,image_end=image+0x10000,binary_slice_sha256='open-slice-'+str(request['rva']),lifter_manifest_sha256='open-lifter')
   with patch.object(self.adapter,'lift',side_effect=lift):return self.adapter.lift_callees(request)
 def test_original_call_roots_keep_complete_chain_and_old_recipe_remains_available(self):
  result=self.run_closure();self.assertEqual({c['target'] for c in result['callees']},{0x503000,0x503100,0x504000});chain=next(c for c in result['forwarding_chains'] if c['original_target']==0x503000);self.assertEqual(chain['chain'],[0x503000,0x504000]);self.assertFalse(result['proof'])
  old=self.run_closure(profile='vc8-x86-flat32-addressable-stack-v1');self.assertEqual({c['target'] for c in old['callees']},{0x503000,0x503100})
 def test_missing_exact_entry_cycle_and_bounded_chain_refuse(self):
  def missing(values):
   r=values[0x3000]['instructions'][0];r['raw_hex']=(b'\xe9'+struct.pack('<i',0x505000-0x503005)).hex();r['tree']['Body'][0]['Target']=const(0x505000,64)
  with self.assertRaisesRegex(ValueError,'forwarding_target_not_inventory_entry'):self.run_closure(missing)
  def cycle(values):
   r=values[0x3000]['instructions'][0];r['raw_hex']='e9fbffffff';r['tree']['Body'][0]['Target']=const(0x503000,64)
  with self.assertRaisesRegex(ValueError,'forwarding_cycle'):self.run_closure(cycle)
  def chain(values):
   for n in range(9):
    address=0x503000+n*0x1000;dest=address+0x1000;values[address-0x500000]=dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=[row(address,[node('IlBranch',Kind=dict(name='Jmp'),Cond=None,Target=const(dest,64))],(b'\xe9'+struct.pack('<i',dest-address-5)).hex())])
   values[0xc000]=dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=[row(0x50c000,ret(0),'c3')])
  with self.assertRaisesRegex(ValueError,'forwarding_depth_exhausted'):self.run_closure(chain)
 def test_scan_necessary_boundaries_are_not_match_credit(self):
  import importlib.util
  spec=importlib.util.spec_from_file_location('conditional_scan',ROOT/'tools/replayable/scan_conditional_calls.py');scan=importlib.util.module_from_spec(spec);spec.loader.exec_module(scan);p=fixture();raw=bytes.fromhex(''.join(r['raw_hex'] for r in p['lift']['instructions']));md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);md.detail=True
  self.assertEqual(scan.classify(raw,0x502000,md)[0],'typed_check_required')
  for edited in (raw[:-1],raw[:-3]+b'\xc3',raw[:19]+b'\x74\xeb'+raw[21:]):self.assertNotEqual(scan.classify(edited,0x502000,md)[0],'typed_check_required')

class ConditionalIntegrationTests(unittest.TestCase):
 def test_composed_cli_preserves_prior_sources(self):
  from test_replayable_ir import DLL,DOTNET,fixture as old_fixture,tail_fixture
  from test_replayable_stackargs import stack_fixture
  if not DLL.exists():self.skipTest('build C# component first')
  for payload in (old_fixture(),old_fixture(4),tail_fixture(),stack_fixture()):
   if 'callees' in payload:payload['stack_arguments']=True;payload['callee_lifts']=payload.pop('callees')
   old=json.loads(subprocess.run([DOTNET,str(DLL),'recover-ir'],input=json.dumps(payload),text=True,capture_output=True,check=True).stdout);self.assertEqual(old['status'],'generated',old)
   payload['conditional_calls']=True;payload.setdefault('callee_lifts',[]);new=json.loads(subprocess.run([DOTNET,str(DLL),'recover-ir'],input=json.dumps(payload),text=True,capture_output=True,check=True).stdout);self.assertEqual(new['status'],'generated',new);self.assertEqual(new['source'],old['source'])

"""Open tail-adapter ABI hypotheses; original external calls are never inlined."""
import copy,json,shutil,struct,subprocess,tempfile,unittest
from pathlib import Path
from test_replayable_ir import node,reg,const,write
from test_replayable_stackargs import row,ret
from test_replayable_conditional import fixture as conditional_fixture
ROOT=Path(__file__).resolve().parents[1];DOTNET=shutil.which('dotnet')
def adapter(target=0x503100,destination=0x505000,receiver=1):
 raw='c7'+('01' if receiver==1 else '03')+'00705000'
 return dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=[row(target,[node('IlStore',Addr=reg(receiver),Val=const(0x507000))],raw),row(target+6,[node('IlBranch',Kind=dict(name='Jmp'),Cond=None,Target=const(destination,64))],(b'\xe9'+struct.pack('<i',destination-target-11)).hex())])
def fixture():
 p=conditional_fixture();p['callees'][0]['lift']=adapter();p['callees'].append(dict(target=0x505000,lift=dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=[row(0x505000,ret(0),'c3')])));p['adapters']=True;return p
@unittest.skipUnless(DOTNET,'dotnet unavailable')
class TailAdapterTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory(prefix='dao-tail-adapter-');d=Path(cls.temp.name)
  for n in ('ReplayableIr.cs','ConditionalIr.cs','FlowIr.cs','EhProfile.cs'):shutil.copy2(ROOT/'tools/decompilation-mcp'/n,d/n)
  (d/'Probe.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup></Project>')
  (d/'Program.cs').write_text('''using System.Text.Json;using Decompilation;var o=new JsonSerializerOptions{PropertyNamingPolicy=JsonNamingPolicy.SnakeCaseLower};try{using var doc=JsonDocument.Parse(Console.In.ReadToEnd());var p=doc.RootElement;var deps=p.GetProperty("callees").EnumerateArray().Select(c=>new CalleeStackLift(c.GetProperty("target").GetUInt64(),c.GetProperty("lift"))).ToArray();bool adapters=p.TryGetProperty("adapters",out var a)&&a.GetBoolean();var abi=Vc8CallAdaptersProfile.Abi;if(p.TryGetProperty("receiver",out var receiver))abi=abi with{ArgumentRegisters=[receiver.GetInt32()]};if(p.TryGetProperty("frame_probe",out _))Console.Write(JsonSerializer.Serialize(new{status="marker_only",possible=Vc8EhProfile.MayHaveFrame(p.GetProperty("lift")),proof=false},o));else if(p.TryGetProperty("resolve",out var target)){var evidence=NormalReturnResolver.Resolve(target.GetUInt64(),deps,p.TryGetProperty("budget",out var budget)?budget.GetInt32():8,adapters?abi:null);Console.Write(JsonSerializer.Serialize(new{status="resolved",evidence},o));}else{var ir=X86ConditionalRecovery.Raise(p.GetProperty("lift"),abi,deps,true,adapters);Console.Write(JsonSerializer.Serialize(new{status="generated",ir,source=Vc8CallAdaptersProfile.Emit(ir,p.GetProperty("rva").GetUInt32(),p.GetProperty("image_base").GetUInt32(),p.GetProperty("image_end").GetUInt32(),"open.exe")},o));}}catch(Exception e){Console.Write(JsonSerializer.Serialize(new{status="unsupported",blocker=e.Message},o));}''')
  subprocess.run([DOTNET,'build',str(d/'Probe.csproj'),'-o',str(d/'out'),'--nologo'],check=True,capture_output=True,text=True);cls.dll=d/'out/Probe.dll'
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def recover(self,p):return json.loads(subprocess.run([DOTNET,str(self.dll)],input=json.dumps(p),capture_output=True,text=True,check=True).stdout)
 def test_prefix_effects_and_original_call_target_remain_external(self):
  r=self.recover(fixture());self.assertEqual(r['status'],'generated',r);call=next(e['call'] for e in r['ir']['prefix'] if e['kind']=='call');self.assertEqual(call['original_target'],0x503100);self.assertTrue(call['memory_effects_unknown']);self.assertEqual(call['evidence']['normal_return']['target'],0x505000);self.assertFalse(call['evidence']['proof'])
  edge=call['evidence']['chain'][0]['tail_adapter'];self.assertEqual([e['kind'] for e in edge['function']['effects']],['store','tail_call']);self.assertEqual(edge['function']['effects'][0]['value']['value'],0x507000);self.assertEqual(edge['stack_pointer_delta'],0);self.assertTrue(edge['memory_effects_unknown'] and edge['throw_behavior_unknown'] and edge['termination_unknown']);self.assertFalse(edge['object_frame_disjointness_proven']);self.assertIn('fn_00003100()',r['source']);self.assertNotIn('fn_00005000',r['source'])
 def test_old_resolver_does_not_silently_expand(self):
  p=fixture();p['adapters']=False;self.assertEqual(self.recover(p)['blocker'],'external_or_misaligned_callee_exit')
 def test_explicit_ABI_controls_receiver_mapping(self):
  p=fixture();p['resolve']=0x503100;p['receiver']=3;p['callees'][0]['lift']=adapter(receiver=3);r=self.recover(p);self.assertEqual(r['status'],'resolved',r);self.assertEqual(r['evidence']['chain'][0]['tail_adapter']['argument_map'],[dict(kind='register_input',index=3)])
  p['receiver']=1;self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_changed_register_stack_flags_or_unknown_load_refuses(self):
  from test_replayable_ir import ty
  for extra in (write(4,const(0)),write(1,const(0)),write(6,const(0)),node('IlWriteReg',Kind=dict(name='Eflags'),Idx=6,Val=const(0,1)),node('IlLet',Id=9,Val=node('IlLoad',Addr=reg(1),Ty=ty(32)))):
   p=fixture();p['callees'][0]['lift']['instructions'][0]['tree']['Body'].insert(0,extra);self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_return_slot_and_unknown_receiver_stores_refuse(self):
  for address in (reg(4),reg(0)):
   p=fixture();p['callees'][0]['lift']['instructions'][0]['tree']['Body'][0]['Addr']=address;self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_prefix_call_conditional_and_nonconstant_store_refuse(self):
  for extra in (node('IlBranch',Kind=dict(name='Call'),Cond=None,Target=const(0x505000,64)),node('IlBranch',Kind=dict(name='CondJmp'),Cond=const(1,1),Target=const(0x503106,64))):
   p=fixture();p['callees'][0]['lift']['instructions'][0]['tree']['Body'].insert(0,extra);self.assertEqual(self.recover(p)['status'],'unsupported')
  p=fixture();p['callees'][0]['lift']['instructions'][0]['tree']['Body'][0]['Val']=reg(0);self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_indirect_tail_is_checked_before_constant_propagation(self):
  p=fixture();p['callees'][0]['lift']['instructions'][0]['tree']['Body'].insert(0,write(0,const(0x505000)));p['callees'][0]['lift']['instructions'][-1]['tree']['Body'][0]['Target']=reg(0);self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_missing_duplicate_cycle_depth_and_misaligned_dependencies_refuse(self):
  edits=[lambda p:p['callees'].pop(),lambda p:p['callees'].append(copy.deepcopy(p['callees'][0])),lambda p:p['callees'][0].update(lift=adapter(destination=0x503100)),lambda p:p.update(budget=0),lambda p:p['callees'][0]['lift']['instructions'][-1].update(pc=0x503107)]
  for edit in edits:
   p=fixture();p['resolve']=0x503100;edit(p);self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_prefix_lock_and_target_encoding_disagreement_refuse(self):
  for index,edit in ((0,lambda r:r['decoded']['P'].update(Lock=True)),(-1,lambda r:r['tree']['Body'][0].update(Target=const(0x505001,64)))):
   p=fixture();edit(p['callees'][0]['lift']['instructions'][index]);self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_normal_return_cleanup_is_not_formal_arity_or_success(self):
  p=fixture();p['resolve']=0x503100;r=self.recover(p);self.assertEqual(r['status'],'resolved',r);e=r['evidence'];self.assertEqual(e['normal_return']['cleanup_bytes'],0);self.assertIn('normal-return-ABI-hypothesis',e['normal_return']['basis']);self.assertFalse(e['proof'])
 def test_nonEH_caller_has_no_EH_applicability_marker(self):
  p=fixture();p['frame_probe']=True;self.assertEqual(self.recover(p),dict(status='marker_only',possible=False,proof=False))

@unittest.skipUnless(__import__('os').name=='posix','host dependency adapter is POSIX-only')
class TailAdapterDependencyTests(unittest.TestCase):
 def test_dependency_selection_retains_prefix_and_checks_actual_direct_exit(self):
  import importlib.util
  spec=importlib.util.spec_from_file_location('tail_adapter',ROOT/'tools/decompilation-mcp/replayable_adapter.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
  try:import capstone
  except ImportError:self.skipTest('dependency decoder unavailable')
  derived=dict(lift=adapter());before=copy.deepcopy(derived)
  self.assertIsNone(a.pure_forwarding_target(derived));self.assertEqual(a.effectful_tail_dependency_target(derived),0x505000);self.assertEqual(derived,before)
  derived['lift']['instructions'][-1]['tree']['Body'][0]['Target']=reg(0)
  with self.assertRaisesRegex(ValueError,'non_direct_forwarding_thunk'):a.effectful_tail_dependency_target(derived)
 def test_complete_pinned_dependency_chain_and_old_recipe_separation(self):
  from unittest.mock import patch
  import importlib.util
  spec=importlib.util.spec_from_file_location('tail_adapter',ROOT/'tools/decompilation-mcp/replayable_adapter.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
  try:import capstone
  except ImportError:self.skipTest('dependency decoder unavailable')
  p=fixture();values={0x2000:p['lift'],**{c['target']-0x500000:c['lift'] for c in p['callees']}}
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'inventory.json';path.write_text(json.dumps(dict(module_sha256='open',functions=[dict(rva=r) for r in values])))
   request=dict(rva=0x2000,entry=dict(rva=0x2000),project=dict(module_sha256='open',inventory=str(path)),recipe=dict(compiler_profile='vc8-x86-flat32-call-adapters-v1'))
   def lift(r):return dict(lift=values[r['rva']],image_base=0x500000,image_end=0x510000,binary_slice_sha256='open-'+str(r['rva']),lifter_manifest_sha256='open')
   with patch.object(a,'lift',side_effect=lift):
    result=a.lift_callees(request);chain=next(c for c in result['forwarding_chains'] if c['original_target']==0x503100);self.assertEqual(chain['chain'],[0x503100,0x505000]);self.assertFalse(result['proof'])
    request['recipe']['compiler_profile']='vc8-x86-flat32-observed-byvalue-calls-v1';composed=a.lift_callees(request);self.assertEqual(composed,result)
    request['recipe']['compiler_profile']='vc8-x86-flat32-conditional-calls-v1';old=a.lift_callees(request);self.assertNotIn(0x505000,[c['target'] for c in old['callees']])
    request['recipe']['compiler_profile']='vc8-x86-flat32-call-adapters-v1';path.write_text(json.dumps(dict(module_sha256='open',functions=[dict(rva=r) for r in values if r!=0x5000])))
    with self.assertRaisesRegex(ValueError,'forwarding_target_not_inventory_entry'):a.lift_callees(request)

class TailAdapterIntegrationTests(unittest.TestCase):
 def test_new_composition_preserves_prior_open_sources_and_original_target(self):
  from test_replayable_ir import DLL,DOTNET,fixture as old_fixture,tail_fixture
  from test_replayable_stackargs import stack_fixture
  if not DLL.exists():self.skipTest('build C# component first')
  for payload in (old_fixture(),tail_fixture(),stack_fixture(),conditional_fixture()):
   if 'callees' in payload:payload['callee_lifts']=payload.pop('callees')
   payload.update(stack_arguments=True,conditional_calls=True)
   def run(p):return json.loads(subprocess.run([DOTNET,str(DLL),'recover-ir'],input=json.dumps(p),text=True,capture_output=True,check=True).stdout)
   old=run(payload);new=run(dict(payload,call_adapters=True));self.assertEqual(old['status'],'generated',old);self.assertEqual(new['status'],'generated',new);self.assertEqual(old['source'],new['source'])
  payload=fixture();payload['callee_lifts']=payload.pop('callees');payload['call_adapters']=True
  result=run(payload);self.assertEqual(result['status'],'generated',result);self.assertIn('fn_00003100()',result['source']);self.assertNotIn('fn_00005000',result['source'])

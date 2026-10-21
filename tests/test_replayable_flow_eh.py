"""Open typed-effects fixtures; synthetic compiler-profile evidence is not acceptance."""
import copy,hashlib,json,shutil,subprocess,tempfile,unittest
from pathlib import Path
from test_replayable_ir import node,ty,reg,const,binary,write,tmp,fixture as linear_fixture
from test_replayable_stackargs import row,ret
from test_replayable_conditional import flag,fw,op,call
ROOT=Path(__file__).resolve().parents[1]
DOTNET=shutil.which('dotnet')
def load(a,bits=32):return node('IlLoad',Addr=a,Ty=ty(bits))
def seg(i):return node('IlReadReg',Kind=dict(name='X86Seg'),Idx=i,Ty=ty(64))
def addr(i,n):return binary('Add',seg(i),const(n,64))
def store(a,v):
 if v.get('Ty',{}).get('Bits')==64:v=node('IlCast',Kind=dict(name='Trunc'),Ty=ty(32),X=v)
 return node('IlStore',Addr=a,Val=v)
def push(v):return [node('IlLet',Id=0,Val=v),write(4,binary('Sub',reg(4),const(4,64))),store(reg(4),tmp(0,32))]
def simple(bodies):
 rows=[];pc=0x502000
 for b in bodies:
  raw='c3' if b[-1].get('Kind',{}).get('name')=='Ret' else '90'
  rows.append(row(pc,b,raw));pc+=1
 return dict(lift=dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=rows),callees=[])
def eh_fixture():
 base=0x502000;handler=0x506000;cookie=0x509000;global_=0x509100;rows=[]
 def add(b,raw='90'):
  pc=base+sum(r['length'] for r in rows);rows.append(row(pc,b,raw));return pc
 for v in (const(0xffffffff),const(handler),load(addr(4,0)),reg(1),op('Xor',load(addr(3,cookie)),reg(4),32)):add(push(v))
 add([store(addr(4,0),binary('Add',reg(4),const(8,64)))])
 add(push(const(20)));pc=base+sum(r['length'] for r in rows);add(call(pc,0x503000),'e800000000')
 add([write(4,binary('Add',reg(4),const(4,64)))])
 add([store(binary('Add',reg(4),const(4,64)),reg(0))])
 add([fw(6,op('Eq',op('And',reg(0),reg(0),32),const(0),1))])
 add([store(binary('Add',reg(4),const(16,64)),const(0))])
 branch=len(rows);add([node('IlBranch',Kind=dict(name='CondJmp'),Cond=flag(6),Target=const(0,64))])
 add([write(1,reg(0))]);pc=base+sum(r['length'] for r in rows);add(call(pc,0x504000),'e800000000')
 def finish():
  add([store(addr(3,global_),reg(0))]);add([store(addr(4,0),load(binary('Add',reg(4),const(8,64))))]);add([write(4,binary('Add',reg(4),const(20,64)))]);add(ret(0),'c3')
 finish();rows[branch]['tree']['Body'][0]['Target']=const(base+sum(r['length'] for r in rows),64)
 add([write(0,const(0))]);finish()
 def normal(pc,receiver=False):
  rs=[row(pc,[write(0,reg(1))])] if receiver else []
  rs.append(row(pc+len(rs),ret(0),'c3'))
  return dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=rs)
 # Complete open dependency ranges with independently bound raw bytes.
 deps=[]
 for role,va,raw in [('handler',handler,'90'),('action',0x506100,'90'),('cleanup_forwarder',0x506200,'e9fb000000')]:
  body=[node('IlBranch',Kind=dict(name='Jmp'),Cond=None,Target=const(0x506300,64))] if role=='cleanup_forwarder' else [write(0,const(1))]
  lift=dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,decoded_bytes=len(raw)//2,instructions=[row(va,body,raw)])
  deps.append(dict(role=role,va=va,size=len(raw)//2,slice_sha256=hashlib.sha256(bytes.fromhex(raw)).hexdigest(),lift=lift))
 evidence=dict(image_base=0x500000,image_end=0x510000,security_cookie_va=cookie,cleanup_forwarder_va=0x506200,cleanup_terminal_va=0x506300,code_dependencies=deps,graph=dict(handler=dict(va=handler,bytes_hex='90',profile=dict(cookie_checked=True)),action=dict(va=0x506100,bytes_hex='90',profile=dict(kind='load_word_push_call_pop_ret',parent_ebp_offset=-16)),FuncInfo=dict(fields=dict(states=1))))
 return dict(lift=dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=rows),callees=[dict(target=0x503000,lift=normal(0x503000)),dict(target=0x504000,lift=normal(0x504000,True))],eh=True,evidence=evidence,rva=0x2000,image_base=0x500000,image_end=0x510000)

@unittest.skipUnless(DOTNET,'dotnet unavailable')
class FlowEhTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory(prefix='dao-flow-');d=Path(cls.temp.name)
  for name in ('ReplayableIr.cs','ConditionalIr.cs','FlowIr.cs','OwnedRanges.cs','EhProfile.cs','TerminalCalls.cs'):shutil.copy2(ROOT/'tools/decompilation-mcp'/name,d/name)
  (d/'Probe.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup></Project>')
  (d/'Program.cs').write_text('''using System.Text.Json;using Decompilation;var o=new JsonSerializerOptions{PropertyNamingPolicy=JsonNamingPolicy.SnakeCaseLower};try{using var doc=JsonDocument.Parse(Console.In.ReadToEnd());var p=doc.RootElement;var deps=p.GetProperty("callees").EnumerateArray().Select(c=>new CalleeStackLift(c.GetProperty("target").GetUInt64(),c.GetProperty("lift"))).ToArray();if(p.TryGetProperty("eh",out var eh)&&eh.GetBoolean()){var ir=Vc8EhProfile.Raise(p.GetProperty("lift"),deps,p.GetProperty("evidence"));Console.Write(JsonSerializer.Serialize(new{status="generated",ir,source=Vc8EhProfile.Emit(ir,p.GetProperty("rva").GetUInt32(),p.GetProperty("image_base").GetUInt32(),p.GetProperty("image_end").GetUInt32(),"open.exe")},o));}else{var ir=X86FlowRecovery.Raise(p.GetProperty("lift"),new(Vc8EhProfile.Abi,true,!p.TryGetProperty("frame",out var f)||f.GetBoolean()),deps);Console.Write(JsonSerializer.Serialize(new{status="recovered",ir},o));}}catch(Exception e){Console.Write(JsonSerializer.Serialize(new{status="unsupported",blocker=e.Message},o));}''')
  subprocess.run([DOTNET,'build',str(d/'Probe.csproj'),'-o',str(d/'out'),'--nologo'],capture_output=True,text=True,check=True);cls.dll=d/'out/Probe.dll'
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def recover(self,p):return json.loads(subprocess.run([DOTNET,str(self.dll)],input=json.dumps(p),capture_output=True,text=True,check=True).stdout)
 def test_C3_and_incoming_extent_are_independent(self):
  p=simple([[write(0,load(binary('Add',reg(4),const(4,64))))],ret(0)])
  r=self.recover(p);self.assertEqual(r['status'],'recovered',r);self.assertEqual(r['ir']['incoming']['required_read_bytes'],4);self.assertFalse(r['ir']['incoming']['exact_arity_known']);self.assertEqual(r['ir']['return_cleanup_bytes'],[0])
 def test_unknown_store_may_alias_return_or_private_frame_and_refuses(self):
  for address in (reg(1),addr(3,0x509000),addr(4,0)):
   p=simple([[store(address,const(1))],ret(0)])
   self.assertEqual(self.recover(p)['blocker'],'flow_unknown_store_frame_alias')
 def test_reads_remain_ordered_even_when_value_cancels(self):
  p=simple([[node('IlLet',Id=0,Val=load(addr(3,0x509000))),write(0,op('Xor',tmp(0,32),tmp(0,32),32))],ret(0)])
  r=self.recover(p);self.assertEqual(r['status'],'recovered',r);effects=r['ir']['normal_paths'][0]['effects'];self.assertEqual(effects[0]['kind'],'memory_read');self.assertEqual(r['ir']['normal_paths'][0]['exit']['return']['value'],0)
 def test_distinct_external_reads_do_not_cancel(self):
  p=simple([[write(0,op('Xor',load(addr(3,0x509000)),load(addr(3,0x509000)),32))],ret(0)])
  r=self.recover(p);self.assertEqual(r['status'],'recovered',r);self.assertEqual(r['ir']['normal_paths'][0]['exit']['return']['kind'],'bit_operation');self.assertEqual(len([e for e in r['ir']['normal_paths'][0]['effects'] if e['kind']=='memory_read']),2)
 def test_private_word_full_extent_and_alignment(self):
  for off in (1,2,3,4,8):
   p=simple([push(reg(6)),[store(binary('Add',reg(4),const(off,64)),const(123))],[write(4,binary('Add',reg(4),const(4,64)))],ret(0)])
   self.assertEqual(self.recover(p)['blocker'],'flow_stack_store_outside_allocated_word')
 def test_complete_two_exit_EH_refuses_unproved_postcall_FS_restoration(self):
  r=self.recover(eh_fixture());self.assertEqual(r['status'],'unsupported',r);self.assertEqual(r['blocker'],'EH_registration_and_exact_restoration_required')
 def test_EH_evidence_wrong_cookie_handler_state_and_dependency_reject(self):
  edits=[lambda p:p['evidence'].update(security_cookie_va=0x509004),lambda p:p['evidence']['graph']['handler'].update(va=0x506001),lambda p:p['evidence']['graph']['FuncInfo']['fields'].update(states=2),lambda p:p['evidence']['code_dependencies'].pop(),lambda p:p['evidence']['code_dependencies'][0].update(slice_sha256='0'*64),lambda p:p['evidence']['code_dependencies'][0]['lift'].update(opaque_instructions=1),lambda p:p['evidence']['code_dependencies'][0].update(va=0x506001)]
  for edit in edits:
   p=eh_fixture();edit(p);self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_unknown_receiver_return_is_not_invented(self):
  p=eh_fixture();p['callees'][1]['lift']['instructions'][0]['tree']['Body']=[write(0,const(1))];self.assertEqual(self.recover(p)['blocker'],'EH_missing_original_receiver_return_relation')
 def test_actual_direct_call_required_before_propagation(self):
  p=eh_fixture();r=next(r for r in p['lift']['instructions'] if r['tree']['Body'][-1].get('Kind',{}).get('name')=='Call');r['tree']['Body'][0]['Val']=reg(0);self.assertEqual(self.recover(p)['blocker'],'flow_direct_call_required')
 def test_no_implicit_normal_frame_contract(self):
  p=simple([ret(0)]);p['frame']=False;self.assertEqual(self.recover(p)['blocker'],'flow_requires_explicit_normal_ABI_contract')
 def test_unregistered_frame_escape_prevents_unknown_call(self):
  p=eh_fixture();p['eh']=False;self.assertEqual(self.recover(p)['blocker'],'flow_unknown_store_frame_alias')
 def test_misaligned_backward_partial_and_unreached_control_refuse(self):
  for edit in (lambda p:p['lift'].update(decode_complete=False),lambda p:p['lift']['instructions'][0]['decoded']['P'].update(Lock=True),lambda p:p['lift']['instructions'][12]['tree']['Body'][0].update(Target=const(0x502000,64)),lambda p:p['lift']['instructions'][-1].update(pc=0x507000)):
   p=eh_fixture();edit(p);self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_extra_memory_effect_cannot_be_emission_noise(self):
  p=eh_fixture();p['lift']['instructions'][0]['tree']['Body'].insert(0,store(addr(3,0x509200),const(1)));self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_source_identity_cannot_bypass_unknown_saved_FS(self):
  p=eh_fixture();p['rva']=0x2100;r=self.recover(p);self.assertEqual(r['blocker'],'EH_registration_and_exact_restoration_required')
 def test_wrong_call_RA_width_and_outgoing_frame_alias_refuse(self):
  edits=[lambda r:r['tree']['Body'][1].update(Val=const(1)),lambda r:r['tree']['Body'][2]['Val'].update(R=const(8,64)),lambda r:r['tree']['Body'][0].update(Val=reg(1))]
  for edit in edits:
   p=eh_fixture();r=next(r for r in p['lift']['instructions'] if r['tree']['Body'][-1].get('Kind',{}).get('name')=='Call');edit(r);self.assertEqual(self.recover(p)['status'],'unsupported')
 def test_EH_restore_and_global_order_are_required_effects(self):
  for kind in ('restore','global','state','cookie'):
   p=eh_fixture();rows=p['lift']['instructions']
   if kind=='restore':rows[16]['tree']['Body'][0]['Val']=const(0)
   elif kind=='global':rows[15]['tree']['Body'][0]['Val']=const(0)
   elif kind=='state':rows[11]['tree']['Body'][0]['Val']=const(1)
   else:rows[4]['tree']['Body'][0]['Val']=const(123)
   with self.subTest(kind=kind):self.assertEqual(self.recover(p)['status'],'unsupported')

try:
 import capstone
except ImportError:capstone=None
@unittest.skipUnless(capstone is not None,'decoder unavailable')
class EhScanTests(unittest.TestCase):
 def test_necessary_filter_is_not_validation_and_keeps_effect_domains(self):
  import importlib.util
  spec=importlib.util.spec_from_file_location('eh_scan',ROOT/'tools/replayable/scan_eh_flow.py');scan=importlib.util.module_from_spec(spec);spec.loader.exec_module(scan)
  md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);md.detail=True
  # Open bytes: FS read, two calls, one branch, two C3. Typed/profile checks still required.
  raw=bytes.fromhex('64a100000000e8000000007406e800000000c3c3')
  self.assertEqual(scan.classify(raw,0x501000,md),'typed_check_required')
  for bad in (raw[:-1],raw.replace(bytes.fromhex('64a100000000'),bytes.fromhex('a100000000')),raw.replace(bytes.fromhex('e800000000'),bytes.fromhex('ffd0909090'),1),b'\xc3'):
   self.assertNotEqual(scan.classify(bad,0x501000,md),'typed_check_required')

@unittest.skipUnless(capstone is not None and __import__('os').name=='posix','host dependency bridge unavailable')
class EhDependencyTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  import importlib.util
  spec=importlib.util.spec_from_file_location('flow_eh_adapter',ROOT/'tools/decompilation-mcp/replayable_adapter.py');cls.adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.adapter)
 def evidence(self,mutation=None):
  import struct
  from unittest.mock import patch
  from rapid_object import eh_graph
  raw=bytearray(512);struct.pack_into('<I',raw,0x3c,0x80);opt=0x80+24;struct.pack_into('<II',raw,opt+96+80,0x7000,64)
  load=bytearray(72);struct.pack_into('<I',load,0,72);struct.pack_into('<III',load,60,0x509000,0x508000,1)
  memory={0x507000:bytes(load),0x508000:(0x6000).to_bytes(4,'little'),0x506200:bytes.fromhex('e9fb000000')}
  if mutation:mutation(raw,memory)
  observed=[]
  class Reader:
   pe=type('PE',(),dict(image_base=0x500000))()
   def __init__(self,original):pass
   def read(self,va,size,*args):return memory[va][:size]
  def lift(request):
   observed.append(request)
   return dict(lift=dict(instructions=[dict(pc=0x502000,raw_hex='90')]),image_base=0x500000,image_end=0x510000,binary_slice_sha256='a'*64)
  graph=dict(handler=dict(va=0x506000,size=1,bytes_hex='90'),action=dict(va=0x506100,size=1,bytes_hex='90',external_target_va=0x506200))
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'open.exe';p.write_bytes(raw);request=dict(project=dict(original=str(p)),rva=0x2000,entry={})
   with patch.object(self.adapter,'lift',side_effect=lift),patch.object(eh_graph,'Original',Reader),patch.object(eh_graph,'original_graph',return_value=graph):result=self.adapter.lift_eh(request)
  return result,observed
 def test_derive_all_complete_code_dependencies_and_PE_cookie(self):
  result,calls=self.evidence();self.assertEqual(result['security_cookie_va'],0x509000);self.assertEqual(result['cleanup_terminal_va'],0x506300);self.assertEqual([d['role'] for d in result['code_dependencies']],['handler','action','cleanup_forwarder']);self.assertEqual([c['rva'] for c in calls[1:]],[0x6000,0x6100,0x6200]);self.assertFalse(result['proof'])
  for c in calls[1:]:self.assertEqual(c['entry']['body_ranges'][0]['end_rva_inclusive']-c['rva']+1,c['entry']['body_bytes'])
 def test_PE_registration_bounds_and_exact_cleanup_forwarder_required(self):
  import struct
  edits=[lambda r,m:struct.pack_into('<I',r,0x80+24+96+80+4,63),lambda r,m:m.update({0x507000:(71).to_bytes(4,'little')+m[0x507000][4:]}),lambda r,m:m.update({0x508000:(0x6001).to_bytes(4,'little')}),lambda r,m:m.update({0x507000:m[0x507000][:68]+bytes(4)}),lambda r,m:m.update({0x506200:b'\xc3'+bytes(4)})]
  for edit in edits:
   with self.subTest(edit=edit),self.assertRaises(ValueError):self.evidence(edit)

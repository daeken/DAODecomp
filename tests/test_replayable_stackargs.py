"""Generic opt-in addressable stack argument recovery. No game acceptance."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from test_replayable_ir import node, ty, reg, const, binary, write, tmp, fixture, tail_fixture

ROOT = Path(__file__).resolve().parents[1]
DOTNET = shutil.which('dotnet')


def ret(cleanup):
    body = [node('IlLet', Id=0, Val=node('IlLoad', Addr=reg(4), Ty=ty(32))), write(4, binary('Add', reg(4), const(4,64)))]
    if cleanup: body += [write(4, binary('Add', reg(4), const(cleanup,16)))]
    return body + [node('IlBranch', Kind=dict(name='Ret'), Cond=None, Target=tmp(0,32))]


def row(pc, body, raw='90'):
    return dict(pc=pc,length=len(raw)//2,raw_hex=raw,decoded=dict(P=dict(Lock=False,Rep=False,RepNz=False)),tree=node('IlBlock',Body=body))


def callee(cleanup=4):
    raw='c20400' if cleanup==4 else ('c3' if cleanup==0 else 'c20800')
    return dict(mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=[row(0x503000,ret(cleanup),raw)])


def stack_fixture():
    p=fixture(4)
    rows=p['lift']['instructions']
    rows.insert(2,row(0,[write(0,binary('Add',reg(4),const(8,64)))]))
    rows.insert(3,row(0,[node('IlLet',Id=0,Val=reg(0)),write(4,binary('Sub',reg(4),const(4,64))),node('IlStore',Addr=reg(4),Val=tmp(0,32))]))
    for i,r in enumerate(rows): r['pc']=0x502000+i;r['raw_hex']='90'
    for r in rows:
        b=r['tree']['Body']
        if b[-1].get('Kind',{}).get('name')=='Call':b[0]['Val']['Bits']['decimal']=str(r['pc']+1)
    rows[-1]['tree']['Body']=ret(4);rows[-1]['raw_hex']='c20400';rows[-1]['length']=3
    p['callees']=[dict(target=0x503000,lift=callee())]
    return p


@unittest.skipUnless(DOTNET,'dotnet unavailable')
class StackArgumentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='dao-stackargs-');d=Path(cls.temp.name)
        shutil.copy2(ROOT/'tools/decompilation-mcp/ReplayableIr.cs',d/'ReplayableIr.cs')
        (d/'Probe.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup></Project>')
        (d/'Program.cs').write_text('''using System.Text.Json;using Decompilation;
var options=new JsonSerializerOptions{PropertyNamingPolicy=JsonNamingPolicy.SnakeCaseLower};
try{using var doc=JsonDocument.Parse(Console.In.ReadToEnd());var p=doc.RootElement;var lift=p.GetProperty("lift");
if(p.TryGetProperty("old",out var old)&&old.GetBoolean()){var ir=X86Recovery.Raise(lift,Vc8Profile.Abi);Console.Write(JsonSerializer.Serialize(new{status="generated",source=Vc8Profile.Emit(ir,p.GetProperty("rva").GetUInt32(),p.GetProperty("image_base").GetUInt32(),p.GetProperty("image_end").GetUInt32(),"open.exe")},options));}
else{var callees=p.GetProperty("callees").EnumerateArray().Select(c=>new CalleeStackLift(c.GetProperty("target").GetUInt64(),c.GetProperty("lift"))).ToArray();var ir=Vc8StackArgsProfile.Raise(lift,callees);var source=Vc8StackArgsProfile.Emit(ir,p.GetProperty("rva").GetUInt32(),p.GetProperty("image_base").GetUInt32(),p.GetProperty("image_end").GetUInt32(),"open.exe");Console.Write(JsonSerializer.Serialize(new{status="generated",ir,source},options));}}
catch(Exception e){Console.Write(JsonSerializer.Serialize(new{status="unsupported",blocker=e.Message},options));}''')
        subprocess.run([DOTNET,'build',str(d/'Probe.csproj'),'-o',str(d/'out'),'--nologo'],check=True,capture_output=True,text=True)
        cls.dll=d/'out/Probe.dll'
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def recover(self,p):return json.loads(subprocess.run([DOTNET,str(self.dll)],input=json.dumps(p),text=True,capture_output=True,check=True).stdout)
    def test_address_slot_outgoing_pointer_and_separate_cleanups(self):
        r=self.recover(stack_fixture());self.assertEqual(r['status'],'generated',r)
        self.assertEqual(r['ir']['return_cleanup_bytes'],4)
        self.assertEqual(r['ir']['calls'][0]['arguments'],[dict(kind='incoming_stack_address',offset=4,bits=32)])
        self.assertEqual(r['ir']['calls'][0]['evidence']['cleanup_bytes'],4)
        self.assertFalse(r['ir']['calls'][0]['evidence']['proof'])
        self.assertIn('unsigned int arg_0',r['source']);self.assertIn('fn_00003000(&arg_0)',r['source'])
    def test_unrepresentable_symbolic_offset_is_unsupported_not_process_failure(self):
        p=stack_fixture();p['lift']['instructions'][2]['tree']['Body'][0]['Val']['R']=const((1<<64)-1,64)
        result=self.recover(p);self.assertEqual(result['status'],'unsupported');self.assertEqual(result['blocker'],'symbolic_offset_out_of_supported_range')
    def test_missing_duplicate_and_wrong_cleanup_fail(self):
        for edit in [lambda p:p.update(callees=[]),lambda p:p['callees'].append(copy.deepcopy(p['callees'][0])),lambda p:p['callees'][0].update(lift=callee(0))]:
            p=stack_fixture();edit(p);self.assertEqual(self.recover(p)['status'],'unsupported')
    def test_invalid_input_addresses_fail(self):
        for delta in [4,9,12]:
            p=stack_fixture();p['lift']['instructions'][2]['tree']['Body'][0]['Val']['R']=const(delta,64)
            self.assertEqual(self.recover(p)['status'],'unsupported')
    def test_wrong_return_cleanup_does_not_relax_balance(self):
        p=stack_fixture();p['lift']['instructions'][-1]['tree']['Body']=ret(0);p['lift']['instructions'][-1]['raw_hex']='c3';p['lift']['instructions'][-1]['length']=1
        self.assertEqual(self.recover(p)['status'],'unsupported')
    def test_conflicting_and_ambiguous_callee_cfg_fail(self):
        for target in [reg(0),const(0x503002,64),const(0x503100,64)]:
            p=stack_fixture();c=p['callees'][0]['lift'];c['instructions'].insert(0,row(0x503000,[node('IlBranch',Kind=dict(name='Jmp'),Cond=None,Target=target)]));c['instructions'][1]['pc']=0x503001
            self.assertEqual(self.recover(p)['status'],'unsupported')
        p=stack_fixture();c=p['callees'][0]['lift'];c['instructions']=[row(0x503000,[node('IlBranch',Kind=dict(name='CondJmp'),Cond=const(1,8),Target=const(0x503004,64))]),row(0x503001,ret(4),'c20400'),row(0x503004,ret(0),'c3')]
        self.assertEqual(self.recover(p)['blocker'],'conflicting_callee_cleanup')
    def test_missing_encoding_or_partial_lift_fail(self):
        for edit in [lambda c:c.update(decode_complete=False),lambda c:c['instructions'][0].pop('raw_hex'),lambda c:c['instructions'][0].update(raw_hex='66c3')]:
            p=stack_fixture();edit(p['callees'][0]['lift']);self.assertEqual(self.recover(p)['status'],'unsupported')
    def test_return_target_capture_alias_preserves_origin(self):
        p=stack_fixture()
        for r in [p['lift']['instructions'][-1],p['callees'][0]['lift']['instructions'][0]]:
            r['tree']['Body'].insert(2,node('IlLet',Id=1,Val=tmp(0,32)))
            r['tree']['Body'][-1]['Target']=tmp(1,32)
        self.assertEqual(self.recover(p)['status'],'generated')
        p['callees'][0]['lift']['instructions'][0]['tree']['Body'][2]['Val']=const(0x1234)
        self.assertEqual(self.recover(p)['status'],'unsupported')
    def test_callee_return_encoding_and_typed_effect_must_agree(self):
        p=stack_fixture();p['callees'][0]['lift']['instructions'][0]['tree']['Body']=ret(0)
        self.assertEqual(self.recover(p)['blocker'],'conflicting_return_encoding_and_effects')
    def test_unreachable_callee_bytes_or_fallthrough_are_not_clean_evidence(self):
        p=stack_fixture();p['callees'][0]['lift']['instructions'].append(row(0x503003,ret(4),'c20400'))
        self.assertEqual(self.recover(p)['blocker'],'unreachable_callee_range_bytes')
        p=stack_fixture();p['callees'][0]['lift']['instructions']=[row(0x503000,[])]
        self.assertEqual(self.recover(p)['blocker'],'callee_falls_out_of_range')
    def test_old_profiles_keep_generic_store_call_and_tail_source(self):
        for p in [fixture(),fixture(4),tail_fixture()]:
            p['old']=True;r=self.recover(p);self.assertEqual(r['status'],'generated',r)
            self.assertNotIn('arg_0',r['source'])
    def test_unknown_call_value_cannot_become_success(self):
        p=stack_fixture();rows=p['lift']['instructions'];rows[-3]['tree']['Body']=[write(0,reg(2))]
        self.assertEqual(self.recover(p)['status'],'unsupported')

class StackIntegrationTests(unittest.TestCase):
    def test_composed_recipe_and_diagnostic_keep_prior_sources(self):
        from test_replayable_ir import DLL, DOTNET
        if not DLL.exists(): self.skipTest('build C# component first')
        for p in (fixture(),fixture(4),tail_fixture()):
            old=json.loads(subprocess.run([DOTNET,str(DLL),'recover-ir'],input=json.dumps(p),text=True,capture_output=True,check=True).stdout)
            p['stack_arguments']=True;p['callee_lifts']=[]
            new=json.loads(subprocess.run([DOTNET,str(DLL),'recover-ir'],input=json.dumps(p),text=True,capture_output=True,check=True).stdout)
            self.assertEqual(new['source'],old['source'])
        p=stack_fixture();p['stack_arguments']=True;p['callee_lifts']=p.pop('callees')
        out=json.loads(subprocess.run([DOTNET,str(DLL),'recover-ir'],input=json.dumps(p),text=True,capture_output=True,check=True).stdout)
        self.assertEqual(out['status'],'generated',out);self.assertEqual(out['ir']['calls'][0]['evidence']['cleanup_bytes'],4)


try:
    import capstone
except ImportError:
    capstone=None

@unittest.skipUnless(capstone is not None and __import__('os').name=='posix','host dependency decoder unavailable')
class StackDependencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import importlib.util
        spec=importlib.util.spec_from_file_location('stack_adapter',ROOT/'tools/decompilation-mcp/replayable_adapter.py');cls.adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.adapter)
    def caller(self,raw):
        return dict(image_base=0x400000,lift=dict(instructions=[dict(pc=0x401000,length=len(raw),raw_hex=raw.hex())]))
    def test_actual_direct_operand_only_not_known_register_indirect(self):
        import struct
        direct=self.caller(b'\xe8'+struct.pack('<i',0x403000-0x401005))
        self.assertEqual(self.adapter.direct_call_targets(direct),[0x403000])
        for raw in (b'\xff\xd0',b'\xff\x14\x24'):
            with self.assertRaisesRegex(ValueError,'indirect_caller_call'):self.adapter.direct_call_targets(self.caller(raw))
    def test_exact_inventory_identity_module_and_duplicates_required(self):
        import struct
        caller=self.caller(b'\xe8'+struct.pack('<i',0x403000-0x401005));request=dict(project=dict(module_sha256='pinned'));entry=dict(rva=0x3000)
        inventory=dict(module_sha256='pinned',functions=[entry]);self.assertEqual(self.adapter.select_callee_entries(request,caller,inventory),[(0x403000,entry)])
        for bad in [dict(module_sha256='other',functions=[entry]),dict(module_sha256='pinned',functions=[]),dict(module_sha256='pinned',functions=[entry,entry])]:
            with self.assertRaises(ValueError):self.adapter.select_callee_entries(request,caller,bad)
    def test_added_rule_scan_does_not_skip_required_control_flow_checks(self):
        import importlib.util,struct
        spec=importlib.util.spec_from_file_location('stack_scan',ROOT/'tools/replayable/scan_stackargs.py');scan=importlib.util.module_from_spec(spec);spec.loader.exec_module(scan)
        md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);md.detail=True
        call=b'\xe8'+struct.pack('<i',0x403000-0x401005)
        self.assertEqual(scan.classify(call+b'\xc2\x04\x00',0x401000,md)[0],'typed_check_required')
        for raw in (call+b'\xc3',b'\x75\x00'+call+b'\xc2\x04\x00',b'\xff\xd0\xc2\x04\x00',b'\xc2\x04'):
            self.assertNotEqual(scan.classify(raw,0x401000,md)[0],'typed_check_required')

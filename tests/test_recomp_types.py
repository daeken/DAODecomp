"""Shared guest-view controls; these synthetic programs do not prove game behavior."""
import copy
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

from tools import recomp, recomp_queries as q, recomp_types as t, recomp_workbench as w
from tests.test_recomp_workbench import fixture

E = [{'reason': 'Constructed explicit object-flow fixture, not an original-game claim.'}]
RUNTIME = """#pragma once
#include <cstdint>
#include <map>
namespace sharp_retro {
using bits = std::uint64_t;
struct State { std::uint64_t pc=0; int result=0; };
struct Memory {
 std::map<std::uint32_t,std::uint8_t> bytes;
 bits load(std::uint32_t a,unsigned n) { bits x=0; for(unsigned i=0;i<n/8;++i) x |= bits(bytes[std::uint32_t(a+i)])<<(i*8); return x; }
 void store(std::uint32_t a,bits x,unsigned n) { for(unsigned i=0;i<n/8;++i) bytes[std::uint32_t(a+i)]=std::uint8_t(x>>(i*8)); }
};
enum class Exit { returned };
}
"""


def view():
    return """struct view_object_0 {
sharp_retro::Memory& memory; std::uint32_t base;
static constexpr std::uint32_t field_00000003_u32_offset=0x00000003u;
std::uint32_t read_field_00000003_u32() const { return static_cast<std::uint32_t>(memory.load(static_cast<std::uint32_t>(base+field_00000003_u32_offset),32)); }
void write_field_00000003_u32(sharp_retro::bits value) const { auto field_address=static_cast<std::uint32_t>(base+field_00000003_u32_offset); memory.store(field_address,value,32); }
static constexpr std::uint32_t field_00000004_u16_offset=0x00000004u;
std::uint16_t read_field_00000004_u16() const { return static_cast<std::uint16_t>(memory.load(static_cast<std::uint32_t>(base+field_00000004_u16_offset),16)); }
void write_field_00000004_u16(sharp_retro::bits value) const { auto field_address=static_cast<std::uint32_t>(base+field_00000004_u16_offset); memory.store(field_address,value,16); }
};"""


@unittest.skipUnless(shutil.which('clang++'), 'requires C++ compiler')
class SharedTypeTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.root=Path(temp.name);self.compiler=Path(shutil.which('clang++')).resolve()
        compilation=fixture(self.root,self.compiler)
        inputs=recomp.load(compilation/'inputs.json'); generation=Path(inputs['generation_run'])
        backend=generation.parent.parent/'backends'/('c'*64)
        (backend/'CppRuntime.hpp').write_text(RUNTIME)
        recomp.atomic_json(backend/'pipeline.json',{'backend':{n:w.sha(backend/n) for n in ('CppRuntime.hpp','IntegerRuntime.hpp')}})
        inputs['runtime_sha256']=recomp.digest(RUNTIME.encode())
        self.ids=[]
        for row in inputs['functions']:
            self.ids.append(row['id']); shard=generation.parent.parent/'cache'/row['artifact_key']
            symbol=Path(row['source_file']).stem
            source=(shard/'function.cpp').read_text().replace('namespace recomp_generated {', 'namespace recomp_generated::'+symbol+'_detail {\n'+view()+'\n}\nnamespace recomp_generated {',1)
            (shard/'function.cpp').write_text(source);row['source_sha256']=w.sha(shard/'function.cpp')
            metadata=json.loads(gzip.decompress((shard/'function.json.gz').read_bytes()))
            metadata['structures']=[{'origin':'object:'+row['module'],'name':'object_0','fields':[
                {'origin':'field:'+row['module']+':3','name':'field_00000003_u32','offset':3,'width':32,'type':'u32','read':True,'write':True,'sites':[{'instruction_rva':4096,'mode':'read'}]},
                {'origin':'field:'+row['module']+':4','name':'field_00000004_u16','offset':4,'width':16,'type':'u16','read':True,'write':True,'sites':[{'instruction_rva':4097,'mode':'write'}]}]}]
            (shard/'function.json.gz').write_bytes(gzip.compress(recomp.encoded(metadata)))
            marker=recomp.load(shard/'complete.json');marker['files']={n:w.sha(shard/n) for n in ('function.cpp','function.json.gz')}
            recomp.atomic_json(shard/'complete.json',marker)
        recomp.atomic_json(compilation/'inputs.json',inputs)
        self.work=self.root/'work';w.initialize(compilation,self.work)
        modules={role:dict(context={'binary_sha256':('a' if role=='main' else 'b')*64,'module':role+'.exe'},state={'image_base':0x400000 if role=='main' else 0x10000000}) for role in ('main','umbra')}
        with mock.patch.object(q,'_module_sources',return_value=modules):q.build(self.work)

    def request(self, both=True):
        typ=dict(id='fixture.buffer',name='BufferState',kind='class',size=None,evidence=E,fields=[
            dict(id='word',name='stateWord',offset=3,width=32,type='u32',evidence=E),
            dict(id='half',name='overlappingHalf',offset=4,width=16,type='u16',evidence=E)])
        bindings=[dict(function_id=self.ids[i],object_origin='object:'+role,type_id=typ['id'],evidence=E,
            field_map={'field:'+role+':3':'word','field:'+role+':4':'half'}) for i,role in enumerate(('main','umbra')) if both or i==0]
        return dict(expected_revision=t.load(self.work)['revision'],types=[typ],bindings=bindings)

    def apply_request(self, request):
        proposal=t.propose(self.work,request)
        return t.apply(self.work,Path(proposal['plan_file']))

    def test_two_functions_share_explicit_class_and_rename_propagates(self):
        report=self.apply_request(self.request())
        self.assertEqual(len(report['compiler_report']['checks']),2)
        self.assertEqual(len(t.query(self.work,'uses',type_id='fixture.buffer')['uses']),2)
        state=w.read(self.work)
        for row in state['functions'].values():self.assertIn('dao_recovered::BufferState',w.clean_source(self.work,row).decode())
        current=q.get_function(self.work,'main',4096)['workspace_source']
        self.assertIn('dao_recovered::BufferState',Path(current['committed_blob']).read_text())
        req=self.request();req['types'][0]['name']='RenamedBuffer';self.apply_request(req)
        for row in w.read(self.work)['functions'].values():self.assertIn('dao_recovered::RenamedBuffer',w.clean_source(self.work,row).decode())
        self.assertFalse(t.load(self.work)['behavioral_acceptance'])

    def test_guest_accessors_preserve_overlap_unaligned_and_wrap(self):
        self.apply_request(self.request())
        probe=self.root/'probe.cpp';exe=self.root/'probe'
        probe.write_text('#include "program_types.hpp"\n#include <cassert>\nint main(){ sharp_retro::Memory m; dao_recovered::BufferState b{m,0xfffffffdu}; b.write_stateWord(0x12345678u); assert(m.load(0,32)==0x12345678u); assert(b.read_overlappingHalf()==0x3456u); b.write_overlappingHalf(0xabcd); assert(b.read_field_00000003_u32()==0x12abcd78u); b.write_field_00000003_u32(0xfedcba98u); assert(b.read_stateWord()==0xfedcba98u); }')
        subprocess.run([str(self.compiler),'-std=c++20','-I'+str(self.work/'include'),str(probe),'-o',str(exe)],check=True,capture_output=True)
        subprocess.run([str(exe)],check=True,capture_output=True)

    def test_matching_offsets_do_not_implicitly_bind_other_function(self):
        self.apply_request(self.request(False))
        self.assertEqual(len(t.query(self.work,'uses')['uses']),1)
        self.assertEqual(len(w.read(self.work)['functions']),1)

    def test_bad_origins_width_and_conflicts_do_not_write(self):
        for change in ('origin','width','field'):
            req=self.request()
            if change=='origin':req['bindings'][0]['object_origin']='invented'
            elif change=='width':req['types'][0]['fields'][0]['offset']=2
            else:req['bindings'][0]['field_map']['field:main:3']='absent'
            with self.assertRaises(ValueError):t.propose(self.work,req)
            self.assertFalse((self.work/'types.json').exists())
            self.assertFalse((self.work/'functions').exists())

    def test_stale_plans_and_header_corruption_fail_closed(self):
        proposal=t.propose(self.work,self.request());plan=Path(proposal['plan_file'])
        self.apply_request(self.request(False))
        with self.assertRaisesRegex(ValueError,'stale'):t.apply(self.work,plan)
        (self.work/t.HEADER).write_text('//corrupt')
        with self.assertRaisesRegex(ValueError,'header changed|binding changed'):t.query(self.work,'list')

    def test_manually_rewritten_view_is_not_discarded(self):
        packet=w.checkout(self.work,'main',4096);state=w.read(self.work);row=state['functions'][self.ids[0]]
        changed=w.clean_source(self.work,row).decode().replace('memory.load(', 'memory.load(1+',1)
        # Check the replacement primitive directly: arbitrary body edits are refused.
        original=w.blob(self.work,row['baseline_source_blob']).decode()
        with self.assertRaisesRegex(ValueError,'manually rewritten'):t.replace_view(changed,'view_object_0','BufferState',original)
        commented=original.replace('Memory& memory','Memory& /*spacing*/ memory')
        self.assertIn('dao_recovered::BufferState',t.replace_view(commented,'view_object_0','BufferState',original))
        alias='using view_object_0 = dao_recovered::ManualBehavior;'
        with self.assertRaisesRegex(ValueError,'prior generated binding'):
            t.replace_view(alias,'view_object_0','BufferState',original)
        with self.assertRaisesRegex(ValueError,'prior generated binding'):
            t.replace_view(alias,'view_object_0','BufferState',original,'ExpectedOldType')
        with self.assertRaisesRegex(ValueError,'absent'):
            t.replace_view('// '+alias,'view_object_0','BufferState',original,'ManualBehavior')

    def test_cycles_host_pointer_and_legacy_name_collision_are_rejected(self):
        req=self.request();req['types'][0]['fields'][0]['type']='BufferState*'
        with self.assertRaises(ValueError):t.propose(self.work,req)
        req=self.request();req['types'][0]['bases']=[dict(type_id='fixture.buffer',offset=0,evidence=E)]
        with self.assertRaises(ValueError):t.propose(self.work,req)
        req=self.request();req['types'][0]['fields'][0]['name']='field_00000003_u32'
        with self.assertRaisesRegex(ValueError,'legacy'):t.propose(self.work,req)

    def test_compile_failure_rolls_back_all_files(self):
        proposal=t.propose(self.work,self.request())
        before=(self.work/'workbench.json').read_bytes()
        with mock.patch.object(w,'compile_check',side_effect=ValueError('compiler rejected')):
            with self.assertRaisesRegex(ValueError,'compiler rejected'):t.apply(self.work,Path(proposal['plan_file']))
        self.assertEqual((self.work/'workbench.json').read_bytes(),before)
        self.assertFalse((self.work/'types.json').exists());self.assertFalse((self.work/t.HEADER).exists())

    def test_pointer_fields_return_guest_address_and_bases_are_explicit_views(self):
        req=self.request();typ=req['types'][0];typ['fields'][0].update(type='ptr32',target=typ['id'])
        req['types'].append(dict(id='fixture.base',name='BaseView',kind='struct',fields=[],evidence=E))
        typ['bases']=[dict(type_id='fixture.base',offset=5,evidence=E)]
        self.apply_request(req)
        header=(self.work/t.HEADER).read_text()
        self.assertIn('guest_ptr32<BufferState>',header);self.assertIn('as_BaseView()',header)
        self.assertNotIn('reinterpret_cast',header)

    def test_unbound_type_header_is_compiled_and_registry_is_authenticated(self):
        req=self.request();req['bindings']=[]
        req['types'][0]['methods']=[dict(name='initialize',function_id=self.ids[0],evidence=E)]
        report=self.apply_request(req)
        self.assertEqual(report['compiler_report']['checks'][0]['function'],'shared-header-declaration-probe')
        self.assertFalse(w.read(self.work)['functions'])
        context=q.get_function(self.work,'main',4096)['shared_types']
        self.assertEqual(context['bound_types'][0]['id'],'fixture.buffer')
        self.assertEqual(context['method_associations'][0]['name'],'initialize')
        path=self.work/'types.json';path.write_bytes(path.read_bytes()+b' ')
        with self.assertRaisesRegex(ValueError,'registry changed'):t.load(self.work)


if __name__=='__main__':unittest.main()

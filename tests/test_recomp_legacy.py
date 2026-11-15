"""Special-instruction transport and explicit unsupported-host boundaries."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from tools import recomp
from recompiler.experiments.call_fixture import make_fixture


class LegacyTests(unittest.TestCase):
    def test_xlat_wraps_addresses_transports_unknowns_and_faults_before_commit(self):
        if not shutil.which('dotnet') or not shutil.which('clang++'):
            self.skipTest('requires SharpRetro and Clang')
        with tempfile.TemporaryDirectory() as temporary:
            project=Path(temporary);image=bytearray(make_fixture()[0]);image[0x200:0x202]=bytes.fromhex('d7c3');image[0x210:0x213]=bytes.fromhex('0f31c3')
            binary=project/'special.exe';binary.write_bytes(image)
            recomp.atomic_json(project/'project.json',dict(schema_version=1,revision=0,binary=str(binary),module=binary.name,
                binary_sha256=recomp.digest(image),image_base=0x400000,sharp_retro=str(recomp.ROOT.parent/'SharpRetro'),
                functions=[dict(rva=0x1000,size=2,annotations={}),dict(rva=0x1010,size=3,annotations={})]))
            generated=recomp.generate(project);view,_=recomp.read_view(project,generated['view']);driver=project/'control.cpp'
            driver.write_text(r'''
#include "functions.hpp"
#include "image_memory.hpp"
using namespace sharp_retro;
int main(){
 recomp_generated::ImageMemory memory;memory.map_bytes("ram",0x8000,4096,true,true);memory.seal();memory.store(0x8800,0x12345678,32);
 State s;s.gpr[0]=0xabcdef0112345602ULL;s.gpr[3]=0xffffffffu;s.gpr[4]=0x8800;s.segments[3]=0x8000;s.defined_flags=0;invalidate_gprs(s,9);s.partial_gpr[0]=255;s.partial_gpr[3]=0xffffffffu;
 Scalar32 byte{0xa5,0xfffffff0u,{}};for(unsigned i=0;i<4;++i)byte.origins[i]=100+i;memory.store_scalar8(0x8001,byte);auto before=s;std::uint64_t budget=10;
 if(recomp_generated::execute_guest(0x401000,0x12345678,s,memory,budget)!=Exit::returned||budget!=8)return 1;
 if(s.gpr[0]!=0xabcdef01123456a5ULL||(s.defined_gpr&1)||s.partial_gpr[0]!=0xf0u||s.flags!=before.flags||s.defined_flags)return 2;
 for(unsigned i=0;i<4;++i)if(s.gpr_origins[0][i]!=100+i)return 3;
 s=before;s.segments[3]=0xdead0000;before=s;budget=10;bool fault=false;
 try{(void)recomp_generated::execute_guest(0x401000,0x12345678,s,memory,budget);}catch(const std::runtime_error&){fault=true;}
 if(!fault||std::memcmp(s.gpr,before.gpr,sizeof(s.gpr))||s.defined_gpr!=before.defined_gpr||s.partial_gpr[0]!=before.partial_gpr[0]||s.flags!=before.flags)return 4;
 s=State{};s.gpr[4]=0x8800;before=s;budget=10;bool refused=false;
 try{(void)recomp_generated::execute_guest(0x401010,0x12345678,s,memory,budget);}catch(const std::runtime_error&){refused=true;}
 if(!refused||std::memcmp(s.gpr,before.gpr,sizeof(s.gpr))||s.flags!=before.flags)return 5;
}
''')
            executable=project/'control';built=subprocess.run(['clang++','-std=c++20','-O2','-fsanitize=address,undefined',
                '-fno-sanitize-recover=all','-I',str(view),'-I',str(recomp.RUNTIME),str(driver),*map(str,view.glob('*.cpp')),'-o',str(executable)],
                capture_output=True,text=True,timeout=90)
            self.assertEqual(built.returncode,0,built.stderr)
            result=subprocess.run([str(executable)],capture_output=True,text=True,timeout=15)
            self.assertEqual(result.returncode,0,result.stderr)

"""Debug the reached CRT FP controls, including the lifter's former MXCSR stubs."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from tools import recomp
from recompiler.experiments.call_fixture import make_fixture


class FloatingControlTests(unittest.TestCase):
    def test_generated_controls_observe_state_and_refuse_unknowns(self):
        if not shutil.which('dotnet') or not shutil.which('clang++'):
            self.skipTest('requires SharpRetro and Clang')
        with tempfile.TemporaryDirectory() as temporary:
            project=Path(temporary); binary=project/'fp.exe'; image,_,_=make_fixture(); image=bytearray(image)
            codes=['dbe3d938dd3a0fae19c3', 'd928d93ac3', '0fae100fae1ac3', 'dbe2dfe0c3', '9bc3']
            functions=[]
            for i,code in enumerate(codes):
                data=bytes.fromhex(code); offset=0x200+i*32; image[offset:offset+len(data)]=data
                functions.append(dict(rva=0x1000+i*32,size=len(data),annotations={}))
            binary.write_bytes(image)
            recomp.atomic_json(project/'project.json',dict(schema_version=1,revision=0,binary=str(binary),module=binary.name,
                binary_sha256=recomp.digest(image),image_base=0x400000,sharp_retro=str(recomp.ROOT.parent/'SharpRetro'),functions=functions))
            generated=recomp.generate(project); view,_=recomp.read_view(project,generated['view'])
            driver=project/'driver.cpp'
            driver.write_text(r'''
#include "functions.hpp"
#include "image_memory.hpp"
int main() {
 for(unsigned kind=0;kind<9;kind++) {
  recomp_generated::ImageMemory memory; memory.map_bytes("ram",0x8000,0x2000,true,true); memory.seal();
  sharp_retro::State s; s.gpr[4]=0x8800; s.gpr[0]=0x9000; s.gpr[1]=0x9020; s.gpr[2]=0x9010;
  s.mxcsr_mask=0xffff; s.mxcsr=0x3fa0; s.mxcsr_defined=0xffffffff;
  memory.store(0x8800,0x12345678,32); memory.store(0x9000,kind==2 ? 0x5f80 : kind==5 ? 0x10000 : 0xffff,32);
  memory.store(0x9010,0xaabbccdd,32); std::uint64_t budget=100;
  if(kind==1) { s.x87_control=0x37f; s.x87_control_defined=0xffff; s.x87_status=0; s.x87_status_defined=0xffff; }
  if(kind==3) { s.x87_status=0xffff; s.x87_status_defined=0xffff; sharp_retro::invalidate_gprs(s,1); }
  if(kind==7 || kind==8) { s.x87_control=kind==7 ? 0x37f : 0x37e; s.x87_control_defined=0xffff; s.x87_status=1; s.x87_status_defined=0xffff; }
  unsigned function=kind<4 ? kind : kind==5 ? 2 : kind==6 ? 3 : 4;
  try {
   auto result=recomp_generated::execute_guest(0x401000+function*32,0x12345678,s,memory,budget);
   if(kind==4 || kind==5 || kind==6 || kind==8 || result!=sharp_retro::Exit::returned) return 1;
   if(kind==0 && (memory.load(0x9000,16)!=0x37f || memory.load(0x9010,16)!=0 || memory.load(0x9020,32)!=0x3fa0 || s.x87_tag!=0xffff)) return 2;
   if(kind==1 && (s.x87_control!=0x1f7f || memory.load(0x9010,16)!=0x1f7f)) return 3;
   if(kind==2 && (s.mxcsr!=0x5f80 || memory.load(0x9010,32)!=0x5f80)) return 4;
   if(kind==3 && (sharp_retro::read_gpr_mask(s,0,0xffff)!=0x7f00 || (s.defined_gpr&1))) return 5;
  } catch(const sharp_retro::GuestCpuFault& fault) {
   if(kind==5) { if(fault.vector!=13 || fault.pc!=0x401040 || s.mxcsr!=0x3fa0 || memory.load(0x9010,32)!=0xaabbccdd) return 6; }
   else if(kind==8) { if(fault.vector!=16 || fault.pc!=0x401080) return 7; }
   else return 8;
   if(s.gpr[4]!=0x8800) return 9;
  } catch(const std::runtime_error&) { if(kind!=4 && kind!=6) return 10; }
 }
}
''')
            executable=project/'driver'
            built=subprocess.run(['clang++','-std=c++20','-O2','-fsanitize=address,undefined','-fno-sanitize-recover=all',
                '-I',str(view),'-I',str(recomp.RUNTIME),str(driver),*map(str,view.glob('*.cpp')),'-o',str(executable)],capture_output=True,text=True,timeout=90)
            self.assertEqual(built.returncode,0,built.stderr)
            result=subprocess.run([str(executable)],capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)


if __name__=='__main__': unittest.main()

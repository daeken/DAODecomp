"""Regression for the CRT's PUSH-volatile allocation after a native call."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from tools import recomp
from recompiler.experiments.call_fixture import make_fixture


class NativeScratchTests(unittest.TestCase):
    def test_unknown_spill_can_be_overwritten_but_cannot_be_observed(self):
        if not shutil.which('dotnet') or not shutil.which('clang++'):
            self.skipTest('requires SharpRetro and Clang')
        with tempfile.TemporaryDirectory() as temporary:
            project=Path(temporary); binary=project/'scratch.exe'; image,_,_=make_fixture(); image=bytearray(image)
            cases=[bytes.fromhex('51c704244433221158c3'),bytes.fromhex('5158c3'),bytes.fromhex('51c604247f58c3'),bytes.fromhex('54c3'),bytes.fromhex('31c989c8c3'),bytes.fromhex('f7f1c3'),bytes.fromhex('5131c95931c0c3'),bytes.fromhex('f3c3'),bytes.fromhex('b25a0fb6c2c3'),bytes.fromhex('b65a0fb6c6c3'),bytes.fromhex('66ba34120fb7c2c3'),bytes.fromhex('b25a89d0c3'),bytes.fromhex('b25ab63489d0c3'),bytes.fromhex('b25ab6340fb7c2c3'),bytes.fromhex('e81bffffff'),bytes.fromhex('5589e5c9c3'),bytes.fromhex('5589e5c989e8c3'),bytes.fromhex('896c24fc8b5424fc31c0c3'),bytes.fromhex('896c24fc8b4424fcc3')]
            functions=[]
            for i,code in enumerate(cases):
                offset=0x200+i*32; image[offset:offset+len(code)]=code
                functions.append(dict(rva=0x1000+i*32,size=len(code),annotations={}))
            binary.write_bytes(image)
            recomp.atomic_json(project/'project.json',dict(schema_version=1,revision=0,binary=str(binary),module=binary.name,
                binary_sha256=recomp.digest(image),image_base=0x400000,sharp_retro=str(recomp.ROOT.parent/'SharpRetro'),functions=functions))
            generated=recomp.generate(project); view,manifest=recomp.read_view(project,generated['view'])
            self.assertEqual(next(f for f in manifest['functions'] if f['rva']==0x11c0)['unselected_call_continuations'],[0x11c5])
            driver=project/'driver.cpp'
            driver.write_text(r'''
#include "functions.hpp"
#include "image_memory.hpp"
#include <string>
int main() {
 for(unsigned i=0;i<5;i++) {
  recomp_generated::ImageMemory memory; memory.map_bytes("stack",0x8000,0x1000,true,true); memory.seal();
  sharp_retro::State state; state.gpr[4]=0x8800; state.gpr[1]=0xdeadbeef;
  state.defined_gpr &= ~(1u<<(i==3 ? 4 : 1));
  memory.store(0x8800,0x12345678,32); std::uint64_t budget=100;
  try {
   auto result=recomp_generated::execute_guest(0x401000+i*32,0x12345678,state,memory,budget);
   if(i==1 || i==2) (void)sharp_retro::read_gpr(state,0);
   if((i!=0 && i!=4) || result!=sharp_retro::Exit::returned || state.gpr[0]!=(i==0 ? 0x11223344u : 0u) || state.gpr[4]!=0x8804) return 1;
   if(i==0 && (state.defined_gpr&(1u<<1))) return 2;
   if(i==4 && (!(state.defined_gpr&(1u<<1)) || (state.flags&0x8c5)!=0x44 || (state.defined_flags&0x8c5)!=0x8c5 || (state.defined_flags&0x10))) return 6;
  } catch(const std::runtime_error& e) {
   if(i==0 || i==4) return 3;
   std::string reason=e.what();
   if(i<3 && reason.find("undefined guest register")==std::string::npos) return 4;
   if(i==3 && reason.find("undefined guest register")==std::string::npos) return 5;
  }
 }
 {
  recomp_generated::ImageMemory memory; memory.map_bytes("stack",0x8000,0x1000,true,true); memory.seal();
  sharp_retro::State state; state.gpr[4]=0x8800; state.defined_gpr&=~(1u<<1);
  memory.store(0x8800,0x12345678,32); std::uint64_t budget=100;
  auto result=recomp_generated::execute_guest(0x4010c0,0x12345678,state,memory,budget);
  if(result!=sharp_retro::Exit::returned || state.gpr[0]!=0 || state.gpr[4]!=0x8804 || (state.defined_gpr&(1u<<1))) return 9;
  try { (void)sharp_retro::read_gpr(state,1); return 10; } catch(const std::runtime_error&) {}
 }

 for(unsigned kind=0;kind<4;kind++) {
  recomp_generated::ImageMemory memory; memory.map_bytes("stack",0x8000,0x1000,true,true); memory.seal();
  sharp_retro::State state; state.gpr[4]=0x8800; sharp_retro::invalidate_gprs(state,1u<<5);
  auto incoming=sharp_retro::scalar_gpr32(state,5);
  memory.store(0x8800,0x12345678,32); std::uint64_t budget=100;
  auto result=recomp_generated::execute_guest(0x4011e0+kind*32,0x12345678,state,memory,budget);
  if(result!=sharp_retro::Exit::returned || state.gpr[4]!=0x8804 || (state.defined_gpr&(1u<<5)) || state.gpr_origins[5]!=incoming.origins) return 15;
  if(kind>=2 && state.gpr_origins[kind==2 ? 2 : 0]!=incoming.origins) return 17;
  if(kind==1 || kind==3) {
   try { (void)sharp_retro::read_gpr(state,0); return 16; } catch(const std::runtime_error&) {}
  }
 }
 for(unsigned counter : {0u,4u,0xffffffffu}) {
  recomp_generated::ImageMemory memory; memory.map_bytes("stack",0x8000,0x1000,true,true); memory.seal();
  sharp_retro::State state; state.gpr[4]=0x8800; state.gpr[1]=counter; state.flags=0x647;
  memory.store(0x8800,0x12345678,32); std::uint64_t budget=100;
  auto result=recomp_generated::execute_guest(0x4010e0,0x12345678,state,memory,budget);
  if(result!=sharp_retro::Exit::returned || state.gpr[4]!=0x8804 || state.gpr[1]!=counter || state.flags!=0x647 || budget!=99) return 11;
 }
 for(unsigned kind=8;kind<14;kind++) {
  recomp_generated::ImageMemory memory; memory.map_bytes("stack",0x8000,0x1000,true,true); memory.seal();
  sharp_retro::State state; state.gpr[4]=0x8800; state.gpr[2]=0xaabbccdd; sharp_retro::invalidate_gprs(state,1u<<2);
  memory.store(0x8800,0x12345678,32); std::uint64_t budget=100;
  try {
   auto result=recomp_generated::execute_guest(0x401000+kind*32,0x12345678,state,memory,budget);
   // MOV may carry a partial value; observing the full return must still fail.
   (void)sharp_retro::read_gpr(state,0);
   auto expected=kind==10 ? 0x1234u : kind==13 ? 0x345au : 0x5au;
   if(kind==11 || kind==12 || result!=sharp_retro::Exit::returned || state.gpr[0]!=expected || (state.defined_gpr&(1u<<2)) || !(state.defined_gpr&1)) return 12;
  } catch(const std::runtime_error&) { if(kind!=11 && kind!=12) return 13; }
 }
 {
  recomp_generated::ImageMemory memory; memory.map_bytes("stack",0x8000,0x1000,true,true); memory.seal();
  sharp_retro::State state; state.gpr[4]=0x8800;
  memory.store(0x8800,0x12345678,32); std::uint64_t budget=100; bool failed=false;
  try { (void)recomp_generated::execute_guest(0x4011c0,0x12345678,state,memory,budget); }
  catch(const std::runtime_error& e) { failed=std::string(e.what()).find("untranslated guest code/import target")!=std::string::npos; }
  if(!failed || state.pc!=0x4011c5) return 14;
 }
 for(unsigned kind=0;kind<3;kind++) {
  recomp_generated::ImageMemory memory; memory.map_bytes("stack",0x8000,0x1000,true,true); memory.seal();
  sharp_retro::State state; state.gpr[4]=0x8800; state.gpr[0]=256; state.gpr[1]=kind==1 ? 0 : kind==2 ? 1 : 3;
  state.gpr[2]=kind==2 ? 1 : 0; auto before=state;
  memory.store(0x8800,0x12345678,32); std::uint64_t budget=100;
  try {
   auto result=recomp_generated::execute_guest(0x4010a0,0x12345678,state,memory,budget);
   if(kind || result!=sharp_retro::Exit::returned || state.gpr[0]!=85 || state.gpr[2]!=1 || state.gpr[4]!=0x8804 || (state.defined_flags&0x8d5)) return 7;
  } catch(const sharp_retro::GuestCpuFault& fault) {
   if(!kind || fault.architecture!="x86" || fault.vector!=0 || fault.pc!=0x4010a0 || state.pc!=fault.pc ||
      state.gpr[0]!=before.gpr[0] || state.gpr[2]!=before.gpr[2] || state.gpr[4]!=before.gpr[4]) return 8;
  }
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

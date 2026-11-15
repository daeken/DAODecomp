"""Debug the original feature probe's mixed 16/32-bit stack operations."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from tools import recomp
from recompiler.experiments.call_fixture import make_fixture


class WordStackTests(unittest.TestCase):
    def test_mixed_word_flags_registers_and_partial_memory(self):
        if not shutil.which('dotnet') or not shutil.which('clang++'):
            self.skipTest('requires SharpRetro and Clang')
        with tempfile.TemporaryDirectory() as temporary:
            project=Path(temporary); binary=project/'word.exe'; image,_,_=make_fixture(); image=bytearray(image)
            # The reached mixed-width probe, preserving the result through ECX.
            probe=bytes.fromhex('53669c588bd8350000200050669d669c5833c389c153669d5b89c8c3')
            registers=bytearray.fromhex('6660')
            for reg in (0,1,2,3,5,6,7): registers+=bytes([0xb8+reg])+(0xa1000011+reg*0x01010001).to_bytes(4,'little')
            # Poison the saved SP slot. POPA must skip it.
            registers+=bytes.fromhex('66c7442406adde6661c3')
            dwords=bytearray.fromhex('60')
            for reg in (0,1,2,3,5,6,7): dwords+=bytes([0xb8+reg])+(0xa1000011+reg*0x01010001).to_bytes(4,'little')
            dwords+=bytes.fromhex('c744240cefbeadde61c3')
            functions=[]
            address_copies=bytes.fromhex('8d49008d118d5a00c3')
            for i,code in enumerate((probe,registers,dwords,address_copies,bytes.fromhex('832000c3'))):
                offset=0x200+i*128; image[offset:offset+len(code)]=code
                functions.append(dict(rva=0x1000+i*128,size=len(code),annotations={}))
            binary.write_bytes(image)
            recomp.atomic_json(project/'project.json',dict(schema_version=1,revision=0,binary=str(binary),module=binary.name,
                binary_sha256=recomp.digest(image),image_base=0x400000,sharp_retro=str(recomp.ROOT.parent/'SharpRetro'),functions=functions))
            generated=recomp.generate(project); view,_=recomp.read_view(project,generated['view'])
            driver=project/'driver.cpp'
            driver.write_text(r'''
#include "functions.hpp"
#include "image_memory.hpp"
int main() {
 for(unsigned kind=0;kind<4;kind++) {
  recomp_generated::ImageMemory memory; memory.map_bytes("stack",0x50000000,4096,true,true); memory.seal();
  sharp_retro::State s; s.gpr[4]=0x50000800; s.gpr[3]=0xa55a69c3; s.flags=kind&1 ? 0x200202 : 0x202;
  s.defined_flags=1u<<10; if(kind>=2) sharp_retro::invalidate_gprs(s,1u<<3);
  auto incoming=sharp_retro::scalar_gpr32(s,3);
  memory.store(s.gpr[4],0x12345678,32); std::uint64_t budget=100;
  auto result=recomp_generated::execute_guest(0x401000,0x12345678,s,memory,budget);
  if(result!=sharp_retro::Exit::returned || s.gpr[4]!=0x50000804 || sharp_retro::read_gpr(s,0)!=0x200000) return 1;
  auto restored=sharp_retro::scalar_gpr32(s,3);
  if(restored.value!=incoming.value || restored.known!=incoming.known || (kind>=2 && restored.origins!=incoming.origins)) return 2;
  if(s.flags&(1u<<10) || !(s.defined_flags&(1u<<10)) || (s.defined_flags&0x10)) return 3;
 }
 {
  recomp_generated::ImageMemory memory; memory.map_bytes("stack",0x50000000,4096,true,true); memory.seal();
  sharp_retro::State s; s.gpr[4]=0x50000800; s.gpr[1]=0x13579bdf; s.flags=0x202; s.defined_flags=0x400;
  sharp_retro::invalidate_gprs(s,1u<<1); auto before=sharp_retro::scalar_gpr32(s,1);
  memory.store(s.gpr[4],0x12345678,32); std::uint64_t budget=100;
  auto result=recomp_generated::execute_guest(0x401180,0x12345678,s,memory,budget);
  if(result!=sharp_retro::Exit::returned || s.flags!=0x202 || s.defined_flags!=0x400) return 15;
  for(unsigned reg:{1u,2u,3u}) {
   auto after=sharp_retro::scalar_gpr32(s,reg);
   if(after.value!=before.value || after.known!=before.known || after.origins!=before.origins) return 16;
   try { (void)sharp_retro::read_gpr(s,reg); return 17; } catch(const std::runtime_error&) {}
  }
 }
 for(unsigned kind=0;kind<3;kind++) {
  recomp_generated::ImageMemory memory; memory.map_bytes("ram",0x8000,4096,true,kind!=1); memory.map_bytes("stack",0x50000000,4096,true,true);
  memory.store_unknown(0x8000,0x89abcdef,32); memory.seal();
  sharp_retro::State s; s.gpr[4]=0x50000800; s.gpr[0]=kind==2 ? 0x7000 : 0x8000; s.flags=0x202; s.defined_flags=0xffff;
  memory.store(s.gpr[4],0x12345678,32); std::uint64_t budget=100;
  try {
   auto result=recomp_generated::execute_guest(0x401200,0x12345678,s,memory,budget);
   if(kind || result!=sharp_retro::Exit::returned || memory.load(0x8000,32)!=0 || (s.defined_flags&0x10) || (s.flags&0x8c5)!=0x44) return 18;
  } catch(const std::runtime_error&) {
   if(!kind || s.flags!=0x202 || s.defined_flags!=0xffff) return 19;
   try { (void)memory.load(0x8000,32); return 20; } catch(const sharp_retro::UnknownMemoryRead&) {}
  }
 }
 for(unsigned unknown=0;unknown<2;unknown++) {
  recomp_generated::ImageMemory memory; memory.map_bytes("stack",0x50000000,4096,true,true); memory.seal();
  sharp_retro::State s; s.gpr[4]=0x50000800;
  for(unsigned reg=0;reg<8;reg++) if(reg!=4) s.gpr[reg]=0x123469c3+reg*0x01010101;
  if(unknown) sharp_retro::invalidate_gprs(s,0xef);
  sharp_retro::Scalar32 before[8]; for(unsigned reg=0;reg<8;reg++) before[reg]=sharp_retro::scalar_gpr32(s,reg);
  memory.store(s.gpr[4],0x12345678,32); std::uint64_t budget=100;
  auto result=recomp_generated::execute_guest(0x401080,0x12345678,s,memory,budget);
  if(result!=sharp_retro::Exit::returned || s.gpr[4]!=0x50000804) return 4;
  for(unsigned reg=0;reg<8;reg++) if(reg!=4) {
   auto after=sharp_retro::scalar_gpr32(s,reg); auto high=(0xa1000011u+reg*0x01010001u)&0xffff0000u;
   if((after.known&0xffff0000u)!=0xffff0000u || (after.value&0xffff0000u)!=high || (after.value&0xffffu)!=(before[reg].value&0xffffu)) return 5;
   if(unknown) {
    if(after.known&0xffffu) return 6;
    for(unsigned bit=0;bit<16;bit++) if(after.origins[bit]!=before[reg].origins[bit]) return 7;
   } else if(after.known!=0xffffffffu) return 8;
  }
 }

 for(unsigned unknown=0;unknown<2;unknown++) {
  recomp_generated::ImageMemory memory; memory.map_bytes("stack",0x50000000,4096,true,true); memory.seal();
  sharp_retro::State s; s.gpr[4]=0x50000800;
  for(unsigned reg=0;reg<8;reg++) if(reg!=4) s.gpr[reg]=0x123469c3+reg*0x01010101;
  if(unknown) sharp_retro::invalidate_gprs(s,0xef);
  sharp_retro::Scalar32 before[8]; for(unsigned reg=0;reg<8;reg++) before[reg]=sharp_retro::scalar_gpr32(s,reg);
  memory.store(s.gpr[4],0x12345678,32); std::uint64_t budget=100;
  auto result=recomp_generated::execute_guest(0x401100,0x12345678,s,memory,budget);
  if(result!=sharp_retro::Exit::returned || s.gpr[4]!=0x50000804) return 13;
  for(unsigned reg=0;reg<8;reg++) if(reg!=4) {
   auto after=sharp_retro::scalar_gpr32(s,reg);
   if(after.value!=before[reg].value || after.known!=before[reg].known || (unknown && after.origins!=before[reg].origins)) return 14;
  }
 }
 {
  recomp_generated::ImageMemory memory; memory.map_bytes("ram",0x8000,32,true,true); memory.seal();
  sharp_retro::Scalar32 a{0x11223344,0xff00ff00,{}},b{0x55667788,0xff00,{} };
  for(unsigned i=0;i<32;i++) { a.origins[i]=sharp_retro::fresh_unknown_origin(); b.origins[i]=sharp_retro::fresh_unknown_origin(); }
  memory.store_scalar32(0x8000,a); memory.store_scalar16(0x8001,b);
  auto value=memory.load_scalar32(0x8000);
  if(value.value!=0x11778844 || value.known!=0xffff0000) return 9;
  for(unsigned bit=0;bit<8;bit++) if(value.origins[bit]!=a.origins[bit] || value.origins[8+bit]!=b.origins[bit]) return 10;
  memory.store(0x8002,0xab,8); value=memory.load_scalar32(0x8000);
  if(value.value!=0x11ab8844 || value.known!=0xffff0000) return 11;
  try { (void)memory.load(0x8000,32); return 12; } catch(const sharp_retro::UnknownMemoryRead&) {}
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

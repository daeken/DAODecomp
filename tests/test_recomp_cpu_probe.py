"""Debug the reached CPU probe without inventing the saved undefined flag bits."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from tools import recomp
from recompiler.experiments.call_fixture import make_fixture


class CpuProbeTests(unittest.TestCase):
    def test_symbolic_flag_copies_and_cpuid_inputs(self):
        if not shutil.which('dotnet') or not shutil.which('clang++'):
            self.skipTest('requires SharpRetro and Clang')
        with tempfile.TemporaryDirectory() as temporary:
            project=Path(temporary); binary=project/'cpu.exe'; image,_,_=make_fixture(); image=bytearray(image)
            # The reached ID-toggle sequence, with a visible branch result.
            codes=['9c588bc83500002000509d9c5a2bd17407519db801000000c331c0c3', '0fa2c3', '660f28c1c3', '660fefc0660f7f00c3', '660f7f00c3', '1bd2c3', '19ffc3', '1bd1c3', '0f28100f2911c3', '83caffc3', '81ca00ff0000c3', '0dffffffffc3']
            functions=[]
            for i,code in enumerate(codes):
                data=bytes.fromhex(code); offset=0x200+i*64; image[offset:offset+len(data)]=data
                functions.append(dict(rva=0x1000+i*64,size=len(data),annotations={}))
            binary.write_bytes(image)
            recomp.atomic_json(project/'project.json',dict(schema_version=1,revision=0,binary=str(binary),module=binary.name,
                binary_sha256=recomp.digest(image),image_base=0x400000,sharp_retro=str(recomp.ROOT.parent/'SharpRetro'),functions=functions))
            generated=recomp.generate(project); view,_=recomp.read_view(project,generated['view'])
            driver=project/'driver.cpp'
            driver.write_text(r'''
#include "functions.hpp"
#include "image_memory.hpp"
struct Memory : recomp_generated::ImageMemory {
 unsigned calls=0;
 std::array<std::uint32_t,4> cpuid(std::uint32_t leaf,std::uint32_t subleaf) override {
  ++calls; return {leaf+1,0x2222,subleaf,0x4444};
 }
};
int main() {
 for(unsigned kind=0;kind<4;kind++) {
  Memory memory; memory.map_bytes("ram",0x8000,0x2000,true,true); memory.seal();
  sharp_retro::State s; s.gpr[4]=0x8800; s.flags=0x200ad7;
  unsigned reg=kind==3 ? 0 : 2;
  sharp_retro::Scalar32 input{0x12345678u,kind==1 ? 0xffff00ffu : kind==2 ? 0xffff00f7u : 0u,{}};
  sharp_retro::scalar_gpr32(s,reg,input);
  memory.store(0x8800,0x12345678,32); std::uint64_t budget=100;
  try {
   auto result=recomp_generated::execute_guest(kind==0 ? 0x401240 : kind==3 ? 0x4012c0 : 0x401280,0x12345678,s,memory,budget);
   if(kind==2 || result!=sharp_retro::Exit::returned || sharp_retro::read_gpr(s,reg)!=(kind==1 ? 0x1234ff78u : 0xffffffffu) ||
      (s.flags&0x8c5)!=(kind==1 ? 4u : 0x84u) || (s.defined_flags&0x8c5)!=0x8c5 || (s.defined_flags&16)) return 31;
   bool refused=false; try { (void)sharp_retro::read_flags(s,4); } catch(const std::runtime_error&) { refused=true; }
   if(!refused) return 32;
  } catch(const std::runtime_error&) { if(kind!=2 || s.pc!=0x401280 || s.gpr[4]!=0x8800) return 33; }
 }
 for(unsigned kind=0;kind<7;kind++) {
  Memory memory; memory.map_bytes("ram",0x8000,0x2000,true,true);
  if(kind==5) memory.map_bytes("no read",0xb000,16,false,true);
  if(kind==6) memory.map_bytes("readonly",0xb000,16,true,false);
  memory.seal();
  auto pattern=(sharp_retro::bits(0x7f800001ff800000ULL)<<64)|0x8000000000000001ULL;
  memory.store(0x9000,pattern,128); memory.store(0x9100,~sharp_retro::bits(0),128);
  if(kind==3) memory.store_unknown(0x9000,pattern,128);
  sharp_retro::State s; s.gpr[0]=(kind==4 || kind==5) ? 0xb000 : kind==1 ? 0x9001 : 0x9000;
  s.gpr[1]=kind==6 ? 0xb000 : kind==2 ? 0x9101 : 0x9100; s.gpr[4]=0x8800;
  s.xmm[2]=~sharp_retro::bits(0); s.defined_xmm=4; s.flags=0x200ad7; s.mxcsr=0x1fa0;
  memory.store(0x8800,0x12345678,32); std::uint64_t budget=100;
  bool faulted=false;
  try {
   auto result=recomp_generated::execute_guest(0x401200,0x12345678,s,memory,budget);
   if((kind!=0 && kind!=3) || result!=sharp_retro::Exit::returned) return 22;
  } catch(const sharp_retro::GuestCpuFault& fault) {
   if((kind!=1 && kind!=2) || fault.vector!=13 || fault.pc!=(kind==1 ? 0x401200u : 0x401203u) || s.gpr[4]!=0x8800) return 23;
   faulted=true;
  } catch(const std::runtime_error&) {
   if(kind<4 || s.pc!=(kind==6 ? 0x401203u : 0x401200u) || s.gpr[4]!=0x8800) return 24;
   faulted=true;
  }
  if(s.flags!=0x200ad7 || s.mxcsr!=0x1fa0) return 25;
  if(kind==0 && (s.xmm[2]!=pattern || !(s.defined_xmm&4) || memory.load(0x9100,128)!=pattern)) return 26;
  if(kind==3) {
   if(s.defined_xmm&4) return 27;
   bool unknown=false; try { memory.load(0x9100,128); } catch(const sharp_retro::UnknownMemoryRead&) { unknown=true; }
   if(!unknown) return 28;
  }
  if(faulted && memory.load(0x9100,128)!=~sharp_retro::bits(0)) return 29;
  if((kind==1 || kind==4 || kind==5) && (s.xmm[2]!=~sharp_retro::bits(0) || !(s.defined_xmm&4))) return 30;
 }
 for(unsigned function=0;function<2;function++) for(unsigned carry=0;carry<2;carry++) {
  Memory memory; memory.map_bytes("stack",0x8000,0x2000,true,true); memory.seal();
  sharp_retro::State s; s.gpr[4]=0x8800; sharp_retro::invalidate_gprs(s,0xef);
  s.flags=0x200ad6u|carry; s.defined_flags=1; auto before=s.flags;
  memory.store(0x8800,0x12345678,32); std::uint64_t budget=100;
  auto result=recomp_generated::execute_guest(0x401140+64*function,0x12345678,s,memory,budget);
  unsigned reg=function ? 7 : 2;
  if(result!=sharp_retro::Exit::returned || sharp_retro::read_gpr(s,reg)!=(carry ? 0xffffffffu : 0u) ||
     (s.flags&0x8d5)!=(carry ? 0x95u : 0x44u) || (s.defined_flags&0x8d5)!=0x8d5 ||
     (s.flags&~0x8d5ULL)!=(before&~0x8d5ULL)) return 20;
 }
 for(unsigned function:{0u,2u}) {
  Memory memory; memory.map_bytes("stack",0x8000,0x2000,true,true); memory.seal();
  sharp_retro::State s; s.gpr[4]=0x8800; sharp_retro::invalidate_gprs(s,7); s.defined_flags=function ? 1 : 0;
  memory.store(0x8800,0x12345678,32); std::uint64_t budget=100; bool refused=false;
  try { recomp_generated::execute_guest(0x401140+64*function,0x12345678,s,memory,budget); }
  catch(const std::runtime_error&) { refused=true; }
  if(!refused || s.gpr[4]!=0x8800 || (s.defined_gpr&4)) return 21;
 }
 for(unsigned known=0;known<2;known++) {
  Memory memory; memory.map_bytes("stack",0x8000,0x2000,true,true); memory.seal();
  sharp_retro::State s; s.gpr[4]=0x8800; s.xmm[1]=(sharp_retro::bits(0x0123456789abcdefULL)<<64)|0xfedcba9876543210ULL;
  s.defined_xmm=known ? 2 : 0; s.flags=0x8d7;
  memory.store(0x8800,0x12345678,32); std::uint64_t budget=100;
  auto result=recomp_generated::execute_guest(0x401080,0x12345678,s,memory,budget);
  if(result!=sharp_retro::Exit::returned || s.xmm[0]!=s.xmm[1] || s.flags!=0x8d7 || bool(s.defined_xmm&1)!=bool(known)) return 11;
  try { (void)sharp_retro::read_xmm128(s,0); if(!known) return 12; } catch(const std::runtime_error&) { if(known) return 13; }
 }

 for(unsigned kind=0;kind<3;kind++) {
  Memory memory; memory.map_bytes("ram",0x8000,0x2000,true,true); memory.seal();
  sharp_retro::State s; s.gpr[4]=0x8800; s.gpr[0]=kind==1 ? 0x9001 : 0x9000; s.flags=0x8d7; s.mxcsr=0x1fa0;
  s.xmm[0]=~sharp_retro::bits(0); s.defined_xmm=0; memory.store(0x9000,~sharp_retro::bits(0),128);
  memory.store(0x8800,0x12345678,32); std::uint64_t budget=100;
  try {
   auto result=recomp_generated::execute_guest(kind==2 ? 0x401100 : 0x4010c0,0x12345678,s,memory,budget);
   if(kind==1 || result!=sharp_retro::Exit::returned || s.flags!=0x8d7 || s.mxcsr!=0x1fa0) return 14;
   if(kind==0 && (!(s.defined_xmm&1) || s.xmm[0]!=0 || memory.load(0x9000,128)!=0)) return 15;
   if(kind==2) {
    if(s.defined_xmm&1) return 16;
    try { (void)memory.load(0x9000,128); return 17; } catch(const sharp_retro::UnknownMemoryRead&) {}
   }
  } catch(const sharp_retro::GuestCpuFault& fault) {
   if(kind!=1 || fault.vector!=13 || fault.pc!=0x4010c4 || s.pc!=fault.pc || s.gpr[4]!=0x8800 || memory.load(0x9000,128)!=~sharp_retro::bits(0)) return 18;
  }
 }
 for(unsigned initial : {0u,0x200202u,0xffffffffu}) {
  Memory memory; memory.map_bytes("stack",0x8000,0x2000,true,true); memory.seal();
  sharp_retro::State s; s.gpr[4]=0x8800; s.flags=initial; s.defined_flags=1u<<10;
  memory.store(0x8800,0x12345678,32); std::uint64_t budget=100;
  auto result=recomp_generated::execute_guest(0x401000,0x12345678,s,memory,budget);
  if(result!=sharp_retro::Exit::returned || sharp_retro::read_gpr(s,0)!=1 || s.gpr[4]!=0x8804 || (s.defined_gpr&2)) return 1;
  try { (void)sharp_retro::read_gpr(s,1); return 2; } catch(const std::runtime_error&) {}
 }
 for(unsigned leaf : {0u,1u,7u}) {
  Memory memory; memory.map_bytes("stack",0x8000,0x2000,true,true); memory.seal();
  sharp_retro::State s; s.gpr[4]=0x8800; s.gpr[0]=leaf; sharp_retro::invalidate_gprs(s,0xe);
  memory.store(0x8800,0x12345678,32); std::uint64_t budget=100;
  try {
   auto result=recomp_generated::execute_guest(0x401040,0x12345678,s,memory,budget);
   if(leaf==7 || result!=sharp_retro::Exit::returned || s.gpr[0]!=leaf+1 || s.gpr[3]!=0x2222 || s.gpr[1]!=0 || s.gpr[2]!=0x4444 || (s.defined_gpr&15)!=15 || memory.calls!=1) return 3;
  } catch(const std::runtime_error&) { if(leaf!=7 || memory.calls) return 4; }
 }
 // All single-bit differences and both signs, including the sign-bit case.
 for(unsigned bit=0;bit<32;bit++) for(unsigned sign=0;sign<2;sign++) for(unsigned fixed=0;fixed<2;fixed++) {
  auto delta=std::uint32_t(1u<<bit),a=std::uint32_t(0xa55a69c3u),b=std::uint32_t(a^delta),actual=std::uint32_t(a-b);
  if(sign) { std::swap(a,b); actual=std::uint32_t(a-b); }
  sharp_retro::State s; sharp_retro::Scalar32 left{a,fixed ? delta : 0u,{}},right{b,left.known,{}};
  for(unsigned i=0;i<32;i++) left.origins[i]=right.origins[i]=sharp_retro::fresh_unknown_origin();
  sharp_retro::scalar_gpr32(s,0,left); sharp_retro::scalar_gpr32(s,1,right);
  if(!sharp_retro::subtract_correlated32(s,0,1)) return 5;
  auto output=sharp_retro::scalar_gpr32(s,0);
  if((output.value&output.known)!=(actual&output.known)) return 6;
  auto flags=std::uint32_t((a<b ? 1u : 0u)|((std::popcount(actual&255u)%2==0) ? 4u : 0u)|((a^b^actual)&16u)|
      (actual==0 ? 64u : 0u)|((actual>>24)&128u)|(((a^b)&(a^actual)&0x80000000u) ? 0x800u : 0u));
  if(((s.flags^flags)&s.defined_flags&0x8d5)!=0 || !(s.defined_flags&64) || (s.flags&64)) return 7;
 }
 {
  sharp_retro::State s; sharp_retro::invalidate_gprs(s,3);
  if(sharp_retro::subtract_correlated32(s,0,1)) return 8;
  Memory memory; memory.map_bytes("ram",0x8000,16,true,true); memory.seal();
  auto value=sharp_retro::scalar_gpr32(s,0); memory.store_scalar32(0x8000,value);
  memory.store(0x8001,0x12,8); auto loaded=memory.load_scalar32(0x8000);
  if((loaded.known&0xff00u)!=0xff00u || ((loaded.value>>8)&255)!=0x12) return 9;
  for(unsigned bit=0;bit<32;bit++) if(bit<8 || bit>=16) { if(loaded.origins[bit]!=value.origins[bit]) return 19; }
  // An overlapping byte write replaces that byte while retaining untouched identities.
  try { (void)memory.load(0x8000,32); return 10; } catch(const sharp_retro::UnknownMemoryRead&) {}
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

"""Debugging regression for the CRT's observed REP moves and byte/word/dword stores."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from tools import recomp
from recompiler.experiments.call_fixture import make_fixture


class RepCopyTests(unittest.TestCase):
    def test_comparisons_preserve_zero_count_unknowns_and_completed_fault_prefix(self):
        upstream=recomp.ROOT.parent/'SharpRetro/Decompiler'
        if not shutil.which('clang++'):self.skipTest('requires Clang')
        with tempfile.TemporaryDirectory() as temporary:
            out=Path(temporary);(out/'runtime.hpp').write_bytes((upstream/'CppRuntime.hpp').read_bytes())
            driver=out/'compare.cpp';driver.write_text(r'''
#include "image_memory.hpp"
#include "StringRuntime.hpp"
using namespace sharp_retro;
int main(){
 for(unsigned width:{8u,16u,32u})for(bool scan:{false,true})for(bool ne:{false,true}){
  auto descriptor=width|(scan?0x100u:0u)|0x200u|(ne?0x400u:0u);std::uint64_t budget=0;
  recomp_generated::ImageMemory empty;empty.seal();State zero;zero.gpr[1]=0;
  invalidate_gprs(zero,(1u<<0)|(1u<<6)|(1u<<7));zero.defined_flags&=~(1u<<10);auto before=zero;
  if(!string_compare32(zero,empty,descriptor,budget)||budget||zero.defined_gpr!=before.defined_gpr||zero.defined_flags!=before.defined_flags||zero.flags!=before.flags)return 1;
  for(unsigned i=0;i<16;++i)if(zero.gpr[i]!=before.gpr[i])return 2;
  recomp_generated::ImageMemory memory;memory.map_bytes("data",0x8000,0x2000,true,true);memory.seal();auto step=width/8;
  for(unsigned i=0;i<5;++i)memory.store(0x8020+i*step,0xa5,width);
  for(unsigned i=0;i<2;++i)memory.store(0xa000-(2-i)*step,ne?0xa4:0xa5,width);
  State state;state.segments[3]=0x8000;state.segments[0]=0x9000;state.gpr[0]=0xa5;state.gpr[1]=4;state.gpr[6]=0x20;state.gpr[7]=0x1000-2*step;state.flags=0x202;
  budget=2;if(string_compare32(state,memory,descriptor,budget)||budget||state.gpr[1]!=2||state.gpr[7]!=0x1000||state.gpr[6]!=(scan?0x20:0x20+2*step))return 3;
  before=state;budget=5;bool fault=false;
  try{(void)string_compare32(state,memory,descriptor,budget);}catch(const std::runtime_error&){fault=true;}
  if(!fault||state.flags!=before.flags||state.defined_flags!=before.defined_flags||state.defined_gpr!=before.defined_gpr)return 4;
  for(unsigned i=0;i<16;++i)if(state.gpr[i]!=before.gpr[i])return 5;
 }
 for(unsigned width:{8u,16u,32u})for(bool scan:{false,true})for(bool down:{false,true}){
  recomp_generated::ImageMemory memory;memory.map_bytes("data",0x8000,0x2000,true,true);memory.seal();memory.store(0x8020,0,width);memory.store(0x9040,1,width);
  State state;state.segments[3]=0x8000;state.segments[0]=0x9000;state.gpr[0]=0;state.gpr[6]=0x20;state.gpr[7]=0x40;state.gpr[1]=0xa5a5;
  invalidate_gprs(state,1u<<1);state.flags=down?0x602:0x202;state.defined_flags&=~0x8d5u;auto count=scalar_gpr32(state,1);std::uint64_t budget=0;
  if(!string_compare32(state,memory,width|(scan?0x100u:0u),budget)||state.flags!=(down?0x697u:0x297u)||(state.defined_flags&0x8d5u)!=0x8d5u)return 6;
  auto after=scalar_gpr32(state,1);if(after.value!=count.value||after.known!=count.known||after.origins!=count.origins)return 7;
  auto step=down?0u-width/8:width/8;if(state.gpr[7]!=std::uint32_t(0x40+step)||state.gpr[6]!=(scan?0x20:std::uint32_t(0x20+step)))return 8;
 }
}
''')
            executable=out/'compare'
            built=subprocess.run(['clang++','-std=c++20','-O2','-fsanitize=address,undefined','-fno-sanitize-recover=all',
                '-I',str(out),'-I',str(upstream),'-I',str(recomp.RUNTIME),str(driver),'-o',str(executable)],capture_output=True,text=True,timeout=90)
            self.assertEqual(built.returncode,0,built.stderr)
            result=subprocess.run([str(executable)],capture_output=True,text=True,timeout=20)
            self.assertEqual(result.returncode,0,result.stderr)

    def test_rep_copy_transports_partial_known_bits_without_consuming_them(self):
        upstream = recomp.ROOT.parent / 'SharpRetro' / 'Decompiler'
        if not shutil.which('clang++') or not (upstream / 'CppRuntime.hpp').is_file():
            self.skipTest('requires SharpRetro and Clang')
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            (project / 'runtime.hpp').write_bytes((upstream / 'CppRuntime.hpp').read_bytes())
            (project / 'StringRuntime.hpp').write_bytes((upstream / 'StringRuntime.hpp').read_bytes())
            driver = project / 'driver.cpp'
            driver.write_text(r'''
#include "image_memory.hpp"
#include "StringRuntime.hpp"
#include <cstdio>
using namespace sharp_retro;
bool equal(Scalar32 a,Scalar32 b){return a.value==b.value && a.known==b.known && a.origins==b.origins;}
int main(){
 for(bool down:{false,true})for(bool overlap:{false,true}){
  recomp_generated::ImageMemory memory;memory.map_bytes("data",0x8000,4096,true,true);memory.seal();
  std::array<Scalar32,4> initial;
  for(unsigned i=0;i<4;i++){
   auto& value=initial[i];value.value=0x13579bdfu+i*0x1010101u;value.known=0x00ffff0fu;
   for(unsigned bit=0;bit<32;bit++)if(!(value.known&(1u<<bit)))value.origins[bit]=1000+i*32+bit;
   memory.store_scalar32(0x8020+i*4,value);
  }
  auto source=down ? 0x802cu:0x8020u;
  auto destination=overlap ? source+(down ? -4u:4u) : (down ? 0x808cu:0x8080u);
  State s;s.gpr[1]=4;s.gpr[6]=source;s.gpr[7]=destination;s.flags=down ? 0x602:0x202;
  auto flags=s.flags,defined=s.defined_flags;std::uint64_t budget=2;
  if(rep_movsd32(s,memory,budget) || budget || s.gpr[1]!=2)return 1;
  budget=2;if(!rep_movsd32(s,memory,budget) || budget || s.gpr[1] || s.flags!=flags || s.defined_flags!=defined)return 2;
  for(unsigned i=0;i<4;i++){
   auto expected=initial[overlap ? (down ? 3:0) : (down ? 3-i:i)];
   auto address=destination+(down ? -4u*i:4u*i);
   if(!equal(memory.load_scalar32(address),expected))return 3;
   bool unknown=false;try{(void)memory.load(address,32);}catch(const UnknownMemoryRead&){unknown=true;}
   if(!unknown)return 4;
  }
 }
 {
  recomp_generated::ImageMemory memory;memory.map_bytes("data",0x8000,4096,true,true);memory.seal();
  memory.store_unknown(0x8020,0xa5c33c5a,32);State s;s.gpr[1]=1;s.gpr[6]=0x8020;s.gpr[7]=0x8080;std::uint64_t budget=1;
  if(!rep_movsd32(s,memory,budget) || memory.load_scalar32(0x8080).known || memory.load_scalar32(0x8080).value!=0xa5c33c5a)return 5;
  // Faulting stores retain the completed prefix and the current iteration's
  // addresses/count, even when the source carries unknown bits.
  s.gpr[1]=2;s.gpr[6]=0x8020;s.gpr[7]=0x8ffc;budget=3;
  bool fault=false;try{(void)rep_movsd32(s,memory,budget);}catch(const std::runtime_error&){fault=true;}
  if(!fault || s.gpr[1]!=1 || s.gpr[6]!=0x8024 || s.gpr[7]!=0x9000 || !equal(memory.load_scalar32(0x8ffc),memory.load_scalar32(0x8020)))return 6;
 }
 for(unsigned width:{8u,16u})for(bool down:{false,true})for(bool overlap:{false,true}){
  recomp_generated::ImageMemory memory;memory.map_bytes("small",0x8000,4096,true,true);memory.seal();
  std::array<Scalar32,4> initial;
  for(unsigned i=0;i<4;i++){
   auto& value=initial[i];value.value=0x9573u+i*0x101u;value.known=width==8?0xfffffff0u:0xffffff0fu;
   for(unsigned bit=0;bit<width;bit++)if(!(value.known&(1u<<bit)))value.origins[bit]=4000+i*32+bit;
   if(width==8)memory.store_scalar8(0x8020+i,value);else memory.store_scalar16(0x8020+i*2,value);
  }
  auto step=width/8,source=0x8020u+(down?3*step:0);
  auto destination=overlap?source+(down?0u-step:step):0x8080u+(down?3*step:0);
  State s;s.gpr[1]=4;s.gpr[6]=source;s.gpr[7]=destination;s.flags=down?0x602:0x202;
  auto flags=s.flags,known=s.defined_flags;std::uint64_t budget=2;
  if(rep_movs_extra32(s,memory,width,budget)||budget||s.gpr[1]!=2)return 9;
  budget=2;if(!rep_movs_extra32(s,memory,width,budget)||budget||s.gpr[1]||s.flags!=flags||s.defined_flags!=known)return 10;
  for(unsigned i=0;i<4;i++){
   auto address=destination+(down?0u-step*i:step*i);
   auto expected=initial[overlap?(down?3:0):(down?3-i:i)];
   expected.value&=width==8?0xffu:0xffffu;
   auto actual=width==8?memory.load_scalar8(address):memory.load_scalar16(address);
   // Only the element's bits belong to the scalar transfer contract.
   auto mask=width==8?0xffu:0xffffu;
   if(actual.value!=expected.value||(actual.known&mask)!=(expected.known&mask))return 11;
   for(unsigned bit=0;bit<width;bit++)if(!(actual.known&(1u<<bit))&&actual.origins[bit]!=expected.origins[bit])return 12;
  }
 }

 for(unsigned width:{16u,32u})for(bool down:{false,true}) {
  recomp_generated::ImageMemory memory;memory.map_bytes("data",0x8000,4096,true,true);memory.seal();
  Scalar32 input{0x13579bdfu,0x00ff0ff0u,{}};
  for(unsigned bit=0;bit<32;bit++)if(!(input.known&(1u<<bit)))input.origins[bit]=2000+bit;
  if(width==16)memory.store_scalar16(0x8020,input);else memory.store_scalar32(0x8020,input);
  auto expected=width==16 ? memory.load_scalar16(0x8020):memory.load_scalar32(0x8020);
  State s;s.segments[3]=s.segments[0]=0x8000;s.gpr[6]=0x20;s.gpr[7]=0x21;s.gpr[1]=0x76543210;
  invalidate_gprs(s,1u<<1);s.flags=down ? 0x602:0x202;s.defined_flags&=~(1u<<6);
  auto flags=s.flags,defined=s.defined_flags;auto count=scalar_gpr32(s,1);
  movs32(s,memory,width);
  auto copied=width==16 ? memory.load_scalar16(0x8021):memory.load_scalar32(0x8021);
  unsigned step=down ? 0u-width/8:width/8;
  if(!equal(expected,copied) || !equal(count,scalar_gpr32(s,1)) || s.flags!=flags || s.defined_flags!=defined ||
     s.gpr[6]!=std::uint32_t(0x20+step) || s.gpr[7]!=std::uint32_t(0x21+step))return 7;
  for(bool read_fault:{false,true}) {
   s.gpr[6]=read_fault ? 0xfffu:0x20u;s.gpr[7]=read_fault ? 0x80u:0xfffu;auto before=s;
   bool fault=false;try{movs32(s,memory,width);}catch(const std::runtime_error&){fault=true;}
   bool same_registers=true;for(unsigned i=0;i<16;++i)if(s.gpr[i]!=before.gpr[i])same_registers=false;
   if(!fault || !same_registers || s.defined_gpr!=before.defined_gpr || s.flags!=before.flags || s.defined_flags!=before.defined_flags){
    std::fprintf(stderr,"MOVS fault width=%u down=%u read=%u fault=%u SI=%llx/%llx DI=%llx/%llx GPR=%02x/%02x flags=%llx/%llx known=%llx/%llx\n",width,unsigned(down),unsigned(read_fault),unsigned(fault),
     (unsigned long long)s.gpr[6],(unsigned long long)before.gpr[6],(unsigned long long)s.gpr[7],(unsigned long long)before.gpr[7],s.defined_gpr,before.defined_gpr,
     (unsigned long long)s.flags,(unsigned long long)before.flags,(unsigned long long)s.defined_flags,(unsigned long long)before.defined_flags);return 8;}
  }
 }
}
''')
            executable = project / 'driver'
            built = subprocess.run(['clang++', '-std=c++20', '-O2', '-fsanitize=address,undefined',
                '-fno-sanitize-recover=all', '-I', str(project), '-I', str(upstream), '-I', str(recomp.RUNTIME),
                str(driver), '-o', str(executable)], capture_output=True, text=True, timeout=90)
            self.assertEqual(built.returncode, 0, built.stderr)
            result = subprocess.run([str(executable)], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_crt_string_instructions_match_execution_and_retain_partial_progress(self):
        try:
            from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UcError
            from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_ECX, UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_EFLAGS, UC_X86_REG_EIP
        except ImportError:
            self.skipTest('requires pinned Unicorn')
        if not shutil.which('dotnet') or not shutil.which('clang++'):
            self.skipTest('requires SharpRetro and Clang')
        with tempfile.TemporaryDirectory() as temporary:
            project=Path(temporary); binary=project/'rep.exe'; image,_,_=make_fixture(); image=bytearray(image)
            image[0x200:0x203]=bytes.fromhex('f3a5c3'); image[0x220:0x222]=bytes.fromhex('abc3'); image[0x240:0x243]=bytes.fromhex('f3abc3'); image[0x260:0x263]=bytes.fromhex('f3aac3'); image[0x280:0x284]=bytes.fromhex('66f3abc3'); image[0x2a0:0x2a2]=bytes.fromhex('a5c3'); image[0x2c0:0x2c3]=bytes.fromhex('66a5c3'); image[0x2e0:0x2e3]=bytes.fromhex('f3a4c3'); image[0x300:0x304]=bytes.fromhex('66f3a5c3'); image[0x320:0x324]=bytes.fromhex('f366a5c3'); image[0x340:0x342]=bytes.fromhex('a4c3'); binary.write_bytes(image)
            recomp.atomic_json(project/'project.json',dict(schema_version=1,revision=0,binary=str(binary),module=binary.name,
                binary_sha256=recomp.digest(image),image_base=0x400000,sharp_retro=str(recomp.ROOT.parent/'SharpRetro'),
                functions=[dict(rva=0x1000,size=3,annotations={}),dict(rva=0x1020,size=2,annotations={}),dict(rva=0x1040,size=3,annotations={}),dict(rva=0x1060,size=3,annotations={}),dict(rva=0x1080,size=4,annotations={}),dict(rva=0x10a0,size=2,annotations={}),dict(rva=0x10c0,size=3,annotations={}),dict(rva=0x10e0,size=3,annotations={}),dict(rva=0x1100,size=4,annotations={}),dict(rva=0x1120,size=4,annotations={}),dict(rva=0x1140,size=2,annotations={})]))
            generated=recomp.generate(project); view,_=recomp.read_view(project,generated['view'])
            driver=project/'driver.cpp'
            driver.write_text(r'''
#include "functions.hpp"
#include "image_memory.hpp"
#include <iostream>
int main() {
 unsigned count,source,destination,flags,unknown,operation; std::uint64_t budget;
 std::cin>>count>>source>>destination>>flags>>budget>>unknown>>operation;
 recomp_generated::ImageMemory memory;
 memory.map_bytes("data",0x8000,0x1000,true,true); memory.map_bytes("stack",0xa000,0x1000,true,true);
 memory.map_bytes("low wrap",0,0x1000,true,true); memory.map_bytes("high wrap",0xfffff000ULL,0x1000,true,true); memory.seal();
 for(unsigned i=0;i<4096;i++) { memory.store(0x8000+i,(i*17+3)&255,8); memory.store(i,(i*7+5)&255,8); memory.store(0xfffff000ULL+i,(i*11+9)&255,8); }
 sharp_retro::State state; state.gpr[0]=0xa5c33c5a; state.gpr[1]=count; state.gpr[6]=source; state.gpr[7]=destination; state.gpr[4]=0xa800; state.flags=flags;
 if(unknown==1) { state.defined_gpr&=~((1u<<6)|(1u<<7)); state.defined_flags&=~(1u<<10); }
 if(unknown==2) { sharp_retro::invalidate_gprs(state,1); sharp_retro::write_gpr_slice(state,0,0x5a,0xff); }
 if(unknown==3) { sharp_retro::invalidate_gprs(state,1); sharp_retro::write_gpr_slice(state,0,0x3c5a,0xffff); }
 if(unknown==4) { sharp_retro::invalidate_gprs(state,1u<<1); state.defined_flags&=~(1u<<6); }
 memory.store(0xa800,0x12345678,32); std::string status;
 try { auto result=recomp_generated::execute_guest(0x401000+operation*0x20,0x12345678,state,memory,budget);
       status=result==sharp_retro::Exit::returned ? "returned" : result==sharp_retro::Exit::budget_exhausted ? "budget" : "bad"; }
 catch(const std::runtime_error&) { status="fault"; }
 if(unknown==4 && ((state.defined_gpr&(1u<<1)) || (state.defined_flags&(1u<<6)))) return 2;
 std::cout<<status<<' '<<state.pc<<' '<<state.gpr[1]<<' '<<state.gpr[6]<<' '<<state.gpr[7]<<' '<<state.flags<<' '<<budget;
 for(unsigned i=0;i<128;i++) std::cout<<' '<<unsigned(memory.load(0x8000+i,8));
 std::cout<<'\n';
}
''')
            executable=project/'driver'
            built=subprocess.run(['clang++','-std=c++20','-O2','-fsanitize=address,undefined','-fno-sanitize-recover=all',
                '-I',str(view),'-I',str(recomp.RUNTIME),str(driver),*map(str,view.glob('*.cpp')),'-o',str(executable)],capture_output=True,text=True,timeout=90)
            self.assertEqual(built.returncode,0,built.stderr)
            cases=[(8,0x8020,0x8080,0x202,100,0),(8,0x803c,0x809c,0x602,100,0),
                   (8,0x8020,0x8024,0x202,100,0),(8,0x803c,0x8038,0x602,100,0),
                   (0,0xffffffff,0xffffffff,0x202,100,1),(2,0xfffffffc,0x8040,0x202,100,0),
                   (8,0x8020,0x8080,0x202,3,0),(3,0x8ff8,0x8020,0x202,100,0)]
            cases=[(*case,0) for case in cases]+[(8,0x8020,0x8040,flags,100,0,1) for flags in (0x202,0x602)]+[(8,0x8020,0x803c,flags,100,0,2) for flags in (0x202,0x602)]+[(0,0xffffffff,0xffffffff,0x202,100,1,2),(8,0x8020,0x8040,0x202,3,0,2),(3,0x8020,0x8ff8,0x202,100,0,2)]
            cases += [(8,0xdeadbeef,0x8040,flags,100,0,3) for flags in (0x202,0x602)]
            cases += [(0,0xffffffff,0xffffffff,0x202,100,1,3),(8,0,0x8040,0x202,3,0,3),(3,0,0x8fff,0x202,100,0,3),(3,0,0xffffffff,0x202,100,0,3)]
            cases += [(8,0,0x8040,0x202,100,2,3)]
            cases += [(8,0,0x8040,flags,100,0,4) for flags in (0x202,0x602)]
            cases += [(0,0xffffffff,0xffffffff,0x202,100,1,4),(8,0,0x8040,0x202,3,0,4),(3,0,0x8ffe,0x202,100,0,4),(3,0,0xfffffffe,0x202,100,0,4),(8,0,0x8040,0x202,100,3,4)]
            for operation,width in ((5,4),(6,2),(10,1)):
                cases += [(count,0x8020,destination,flags,100,unknown,operation)
                          for count in (0,1,7) for destination in (0x8020,0x8021,0x8080)
                          for flags in (0x202,0x602) for unknown in (0,4)]
                cases += [(0,source,destination,flags,100,0,operation) for source,destination,flags in
                          ((0x100000000-width,0x8040,0x202),(0,0x8040,0x602),
                           (0x8020,0x100000000-width,0x202),(0x8fff,0x8040,0x202),
                           (0x8020,0x8fff,0x202),(0xdeadbeef,0x8040,0x202))]
            for operation,width in ((7,1),(8,2),(9,2)):
                cases += [(count,source,destination,flags,budget,unknown,operation)
                          for count in (0,1,7) for source,destination in ((0x8020,0x8060),(0x8040,0x8040),(0x8020,0x8021),(0x8030,0x802f))
                          for flags in (0x202,0x602) for budget in (3,100) for unknown in (0,) if budget==100 or count>2]
                cases += [(0,0xffffffff,0xffffffff,0x202,100,1,operation),
                          (3,0x9000-width,0x8020,0x202,100,0,operation),
                          (3,0x8020,0x9000-width,0x202,100,0,operation),
                          (3,0x100000000-width,0x8040,0x202,100,0,operation),
                          (3,0,0x8040,0x602,100,0,operation)]
            for count,source,destination,flags,budget,unknown,operation in cases:
                with self.subTest(count=count,source=source,destination=destination,flags=flags,budget=budget):
                    uc=Uc(UC_ARCH_X86,UC_MODE_32)
                    for base in (0,0x8000,0xfffff000,0x401000): uc.mem_map(base,4096)
                    instruction=bytes.fromhex(('f3a5','ab','f3ab','f3aa','66f3ab','a5','66a5','f3a4','66f3a5','f366a5','a4')[operation]); entry=0x401000+operation*0x20
                    uc.mem_write(entry,instruction); uc.reg_write(UC_X86_REG_EAX,0xa5c33c5a)
                    for base,multiplier,add in ((0x8000,17,3),(0,7,5),(0xfffff000,11,9)):
                        uc.mem_write(base,bytes((i*multiplier+add)&255 for i in range(4096)))
                    for register,value in ((UC_X86_REG_ECX,count),(UC_X86_REG_ESI,source),(UC_X86_REG_EDI,destination),(UC_X86_REG_EFLAGS,flags)):
                        uc.reg_write(register,value)
                    fault=False
                    try: uc.emu_start(entry,entry+len(instruction),count=2 if budget==3 else 10000)
                    except UcError: fault=True
                    expected_status='fault' if fault else 'budget' if budget==3 else 'returned'
                    result=subprocess.run([str(executable)],input=f'{count} {source} {destination} {flags} {budget} {unknown} {operation}\n',capture_output=True,text=True,timeout=10)
                    self.assertEqual(result.returncode,0,result.stderr)
                    actual=result.stdout.split(); self.assertEqual(actual[0],expected_status)
                    values=list(map(int,actual[1:])); pc,cx,si,di,observed_flags,remaining=values[:6]
                    self.assertEqual((cx,si,di,observed_flags),tuple(uc.reg_read(r) for r in (UC_X86_REG_ECX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EFLAGS)))
                    self.assertEqual(pc,0x12345678 if expected_status=='returned' else uc.reg_read(UC_X86_REG_EIP))
                    self.assertEqual(bytes(values[6:]),bytes(uc.mem_read(0x8000,128)))
                    if expected_status=='budget': self.assertEqual(remaining,0)


if __name__=='__main__': unittest.main()

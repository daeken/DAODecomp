#include "functions.hpp"
#include "native_execution.hpp"
#include "shift_cases.inc"
#include <cstdio>
extern "C" unsigned char shift_reference_code[];
using namespace recomp_generated;
struct TracedMemory : NativeX86Memory {
 bool tracing=false;unsigned reads=0,writes=0,width=0;std::uint32_t operand=0;
 sharp_retro::bits load(std::uint64_t a,unsigned w) override {if(tracing&&a==operand){++reads;width=w;}return NativeX86Memory::load(a,w);}
 void store(std::uint64_t a,sharp_retro::bits v,unsigned w) override {if(tracing&&a==operand){++writes;width=w;}NativeX86Memory::store(a,v,w);}
};
int main(){try{
 TracedMemory memory;memory.reserve_image(0x31000000,0x10000);memory.map_bytes("stack",0x50000000,0x10000,true,true);memory.map_bytes("data",0x50010000,4096,true,true);memory.seal();memory.add_native_stack(0x50000000,0x50010000);
 constexpr unsigned n=sizeof(shift_cases)/sizeof(shift_cases[0]);sharp_retro::State host;capture_native_context(host);host.gpr[4]=0x5000f000;memory.store(host.gpr[4],0x12345678,32);
 if(!invoke_native_abi_address(std::uint32_t(reinterpret_cast<std::uintptr_t>(shift_reference_code+n*32)),host,memory))return 4;capture_native_context(host);
 const std::uint32_t patterns[]={0,1,0xffffffffu,0x80000000u,0x7fffffffu,0x8000u,0x7fffu,0xaa557f01u};unsigned cases=0,mismatches=0;
 for(unsigned form=0;form<n;++form)for(unsigned count=0;count<(shift_cases[form].cl?256u:1u);++count)for(unsigned pattern=0;pattern<8;++pattern)for(unsigned seed=0;seed<4;++seed){
  auto& fixture=shift_cases[form];auto expected=host;for(unsigned i=0;i<8;++i)expected.gpr[i]=0x11000000u+i*0x1010101u;
  expected.flags=0x202u|(seed&1?0x8d5u:0u)|(seed&2?0x200000u:0u);expected.defined_flags=0xffffffffu;expected.defined_gpr=0xffff;
  expected.gpr[0]=patterns[pattern];expected.gpr[2]=patterns[(pattern+3)%8];expected.gpr[1]=0x12340000u|count;expected.gpr[4]=0x5000f000;
  auto operand=0x50010083u;expected.gpr[6]=operand;if(fixture.ea==5)operand=0x5000f004;
  if(fixture.ea==6)expected.gpr[5]=operand+8;
  if(fixture.ea==7){expected.gpr[1]=0x40000000u|count;expected.gpr[0]=operand+16u-count*4u;}
  sharp_retro::bits initial=(sharp_retro::bits(0x5a5a5a5a5a5a5a5aULL)<<64)|0xa5a5a5a500000000ULL|patterns[pattern];memory.store(operand,initial,128);memory.store(expected.gpr[4],0x12345678,32);auto candidate=expected;
  if(!invoke_native_abi_address(std::uint32_t(reinterpret_cast<std::uintptr_t>(shift_reference_code+form*32)),expected,memory))return 5;
  auto output=memory.load(operand,128);memory.store(operand,initial,128);memory.store(candidate.gpr[4],0x12345678,32);
  memory.operand=operand;memory.reads=memory.writes=0;memory.tracing=true;std::uint64_t budget=10;auto result=execute_guest(0x31001000+form*32,0x12345678,candidate,memory,budget);memory.tracing=false;
  bool registers=true;for(unsigned i=0;i<8;++i)if(candidate.gpr[i]!=expected.gpr[i])registers=false;
  bool footprint=fixture.ea<4?(!memory.reads&&!memory.writes):(memory.reads==1&&memory.writes==1&&memory.width==fixture.width);
  bool match=result==sharp_retro::Exit::returned&&registers&&candidate.flags==expected.flags&&candidate.defined_flags==expected.defined_flags&&memory.load(operand,128)==output&&footprint&&candidate.mxcsr==expected.mxcsr&&candidate.x87_status==expected.x87_status&&candidate.x87_st==expected.x87_st;
  ++cases;if(!match){++mismatches;if(mismatches<8)std::fprintf(stderr,"shift form=%u ea=%u width=%u right=%u count=%u pattern=%u seed=%u regs=%u flags=%llx/%llx footprint=%u rw=%u/%u\n",form,fixture.ea,fixture.width,unsigned(fixture.right),fixture.cl?count:fixture.count,pattern,seed,unsigned(registers),(unsigned long long)candidate.flags,(unsigned long long)expected.flags,unsigned(footprint),memory.reads,memory.writes);}
 }
 std::printf("{\"native_double_shift_encodings\":%u,\"physical_comparisons\":%u,\"mismatches\":%u,\"game_acceptance\":false}\n",n,cases,mismatches);return mismatches?1:0;
}catch(const std::exception& e){std::fprintf(stderr,"double shift control failed: %s\n",e.what());return 10;}}

#include "functions.hpp"
#include "native_execution.hpp"
#include "special_cases.inc"
#include <cstdio>
extern "C" unsigned char shift_reference_code[];
using namespace recomp_generated;
static std::uint64_t ticks(){std::uint32_t a,d;asm volatile("rdtsc":"=a"(a),"=d"(d)::"memory");return (std::uint64_t(d)<<32)|a;}
int main(){try{
 NativeX86Memory memory;memory.reserve_image(0x31000000,0x10000);memory.map_bytes("stack",0x50000000,0x10000,true,true);memory.map_bytes("data",0x50010000,4096,true,true);memory.seal();memory.add_native_stack(0x50000000,0x50010000);
 constexpr unsigned n=sizeof(special_kinds)/sizeof(special_kinds[0]);sharp_retro::State host;capture_native_context(host);host.gpr[4]=0x5000f000;memory.store(host.gpr[4],0x12345678,32);
 if(!invoke_native_abi_address(std::uint32_t(reinterpret_cast<std::uintptr_t>(shift_reference_code+n*32)),host,memory))return 4;capture_native_context(host);
 unsigned cases=0,mismatches=0;
 for(unsigned form=0;form<n;++form)for(unsigned index=0;index<256;++index)for(unsigned seed=0;seed<2;++seed){
  auto kind=special_kinds[form];auto expected=host;for(unsigned i=0;i<8;++i)expected.gpr[i]=0xa5a50000u+i*0x101u;
  expected.flags=seed?0x200a97u:0x202u;expected.defined_flags=0xffffffffu;expected.defined_gpr=0xffff;expected.gpr[4]=0x5000f000;
  auto operand=0x50010083u;expected.gpr[6]=operand;expected.gpr[0]=0x12340000u|index;expected.gpr[3]=std::uint32_t(operand-index);
  sharp_retro::bits initial=(sharp_retro::bits(0x5a5a5a5a5a5a5a5aULL)<<64)|0xa5a5a5a500000000ULL|(index^0xa5u);memory.store(operand,initial,128);memory.store(expected.gpr[4],0x12345678,32);auto candidate=expected;
  if(!invoke_native_abi_address(std::uint32_t(reinterpret_cast<std::uintptr_t>(shift_reference_code+form*32)),expected,memory))return 5;
  auto output=memory.load(operand,128);memory.store(operand,initial,128);memory.store(candidate.gpr[4],0x12345678,32);
  auto low=ticks();std::uint64_t budget=10;auto result=execute_guest(0x31001000+form*32,0x12345678,candidate,memory,budget);auto high=ticks();
  bool registers=true;for(unsigned i=0;i<8;++i)if(!(kind==3&&(i==0||i==2))&&candidate.gpr[i]!=expected.gpr[i])registers=false;
  auto clock=(candidate.gpr[2]<<32)|candidate.gpr[0];bool interval=kind!=3||(clock>=low&&clock<=high);
  bool match=result==sharp_retro::Exit::returned&&registers&&interval&&candidate.flags==expected.flags&&memory.load(operand,128)==output&&candidate.mxcsr==expected.mxcsr&&candidate.x87_status==expected.x87_status&&candidate.x87_st==expected.x87_st;
  ++cases;if(!match){++mismatches;if(mismatches<8)std::fprintf(stderr,"legacy form=%u kind=%u index=%u regs=%u interval=%u flags=%llx/%llx\n",form,kind,index,unsigned(registers),unsigned(interval),(unsigned long long)candidate.flags,(unsigned long long)expected.flags);}
 }
 std::printf("{\"native_legacy_encodings\":%u,\"physical_comparisons\":%u,\"mismatches\":%u,\"game_acceptance\":false}\n",n,cases,mismatches);return mismatches?1:0;
}catch(const std::exception& e){std::fprintf(stderr,"legacy control failed: %s\n",e.what());return 10;}}

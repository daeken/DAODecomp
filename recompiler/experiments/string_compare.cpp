// Independent physical CMPS/SCAS instructions versus generated C++.
#include "functions.hpp"
#include "native_execution.hpp"
#include "string_cases.inc"
#include <cstdio>
extern "C" unsigned char string_reference_code[];
extern "C" {volatile std::uint32_t string_reference_flags=0;}
using namespace recomp_generated;
struct TracedMemory : NativeX86Memory {
 bool tracing=false;unsigned reads=0,writes=0;
 sharp_retro::bits load(std::uint64_t a,unsigned w) override {if(tracing&&a>=0x50010000&&a<0x50011000)++reads;return NativeX86Memory::load(a,w);}
 void store(std::uint64_t a,sharp_retro::bits v,unsigned w) override {if(tracing&&a>=0x50010000&&a<0x50011000)++writes;NativeX86Memory::store(a,v,w);}
};
int main(){try{
 TracedMemory memory;memory.reserve_image(0x31000000,0x10000);memory.map_bytes("stack",0x50000000,0x10000,true,true);memory.map_bytes("data",0x50010000,4096,true,true);memory.seal();memory.add_native_stack(0x50000000,0x50010000);
 constexpr unsigned n=sizeof(string_cases)/sizeof(string_cases[0]);
 sharp_retro::State host;capture_native_context(host);host.gpr[4]=0x5000f000;memory.store(host.gpr[4],0x12345678,32);
 if(!invoke_native_abi_address(std::uint32_t(reinterpret_cast<std::uintptr_t>(string_reference_code+n*64)),host,memory))return 4;
 capture_native_context(host);unsigned cases=0,mismatches=0;
 for(unsigned form=0;form<n;++form)for(bool down:{false,true})for(unsigned count:{0u,1u,2u,3u,7u,16u,31u})for(unsigned pattern=0;pattern<8;++pattern)for(unsigned stop:{0u,1u,2u,3u,7u,15u,30u,31u}){
  auto& fixture=string_cases[form];auto selected=fixture.width==32?0xffffffffu:(1u<<fixture.width)-1u;auto step=fixture.width/8;
  std::uint32_t source=0x50010100,destination=0x50010400,accumulator=(0x80ff7f01u+pattern*0x2173u)&selected;
  for(unsigned i=0;i<32;++i){auto left=fixture.scan?accumulator:(0x80ff7f01u+pattern*0x2173u+i*0x317u)&selected;auto right=fixture.not_equal?(left^1u):left;if(i==stop)right^=1u;memory.store(source+i*step,left,fixture.width);memory.store(destination+i*step,right,fixture.width);}
  // Traverse both directions; the reference supplies the completed count.
  if(down){source+=31*step;destination+=31*step;}
  auto expected=host;expected.flags=0x202u|((pattern&1)?0x8d5u:0u);expected.defined_flags=0xffffffffu;expected.defined_gpr=0xffff;
  for(unsigned i=0;i<8;++i)expected.gpr[i]=0x11000000u+i*0x1010101u;
  expected.gpr[0]=accumulator;expected.gpr[1]=count;expected.gpr[4]=0x5000f000;expected.gpr[6]=source;expected.gpr[7]=destination;memory.store(expected.gpr[4],0x12345678,32);auto candidate=expected;candidate.flags|=down?0x400u:0u;
  if(!invoke_native_abi_address(std::uint32_t(reinterpret_cast<std::uintptr_t>(string_reference_code+(form*2+unsigned(down))*32)),expected,memory))return 5;
  expected.flags=string_reference_flags;
  memory.store(candidate.gpr[4],0x12345678,32);memory.reads=memory.writes=0;memory.tracing=true;std::uint64_t budget=100;
  auto result=execute_guest(0x31001000+form*32,0x12345678,candidate,memory,budget);memory.tracing=false;
  bool registers=true;for(unsigned i=0;i<8;++i)if(candidate.gpr[i]!=expected.gpr[i])registers=false;
  auto iterations=fixture.repeat?count-std::uint32_t(expected.gpr[1]):1u;
  bool match=result==sharp_retro::Exit::returned&&registers&&candidate.flags==expected.flags&&candidate.defined_flags==expected.defined_flags&&candidate.defined_gpr==expected.defined_gpr&&!memory.writes&&memory.reads==iterations*(fixture.scan?1u:2u)&&candidate.mxcsr==expected.mxcsr&&candidate.x87_control==expected.x87_control&&candidate.x87_status==expected.x87_status&&candidate.x87_tag==expected.x87_tag&&candidate.x87_st==expected.x87_st;
  ++cases;if(!match){++mismatches;if(mismatches<8)std::fprintf(stderr,"string form=%u width=%u DF=%u count=%u pattern=%u stop=%u registers=%u flags=%llx/%llx reads=%u/%u\n",form,fixture.width,unsigned(down),count,pattern,stop,unsigned(registers),(unsigned long long)candidate.flags,(unsigned long long)expected.flags,memory.reads,iterations*(fixture.scan?1u:2u));}
 }
 std::printf("{\"native_string_compare_encodings\":%u,\"physical_comparisons\":%u,\"mismatches\":%u,\"game_acceptance\":false}\n",n,cases,mismatches);return mismatches?1:0;
}catch(const std::exception& e){std::fprintf(stderr,"string compare control failed: %s\n",e.what());return 10;}}

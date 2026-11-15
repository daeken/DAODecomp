#include "functions.hpp"
#include "native_execution.hpp"
#include "mmx_cases.inc"
#include <cstdio>
extern "C" unsigned char shift_reference_code[];
using namespace recomp_generated;
static bool fp_same(const sharp_retro::State& a,const sharp_retro::State& b){return a.x87_control==b.x87_control&&a.x87_status==b.x87_status&&a.x87_tag==b.x87_tag&&a.mxcsr==b.mxcsr&&a.x87_st==b.x87_st&&a.x87_ip==b.x87_ip&&a.x87_dp==b.x87_dp&&a.x87_opcode==b.x87_opcode;}
int main(){try{
 NativeX86Memory memory;memory.reserve_image(0x31000000,0x10000);memory.map_bytes("stack",0x50000000,0x10000,true,true);memory.map_bytes("data",0x50010000,4096,true,true);memory.seal();memory.add_native_stack(0x50000000,0x50010000);
 constexpr unsigned n=sizeof(mmx_cases)/sizeof(mmx_cases[0]);sharp_retro::State host;capture_native_context(host);host.gpr[4]=0x5000f000;memory.store(host.gpr[4],0x12345678,32);
 if(!invoke_native_abi_address(std::uint32_t(reinterpret_cast<std::uintptr_t>(shift_reference_code+n*32)),host,memory))return 4;capture_native_context(host);
 const std::uint64_t patterns[]={0,1,0xffffffffffffffffULL,0x800000007fffffffULL,0x7fffffff80000000ULL,0x0000800000007fffULL,0x7fff0000ffff0001ULL,0xaa557f01ffeeddccULL};unsigned cases=0,mismatches=0;
 for(unsigned form=0;form<n;++form)for(unsigned top=0;top<8;++top)for(unsigned tags:{0u,0xffffu,0xaaaau})for(unsigned pattern=0;pattern<8;++pattern)for(unsigned rounding=0;rounding<4;++rounding){
  auto& fixture=mmx_cases[form];auto expected=host;for(unsigned i=0;i<8;++i)expected.gpr[i]=0x11000000u+i*0x1010101u;
  expected.flags=0x200a97u;expected.defined_flags=0xffffffffu;expected.defined_gpr=0xffff;expected.mxcsr=0x1f80u|(rounding<<13);expected.x87_control=0x37f;expected.x87_status=0x4700u|(top<<11);expected.x87_tag=tags;expected.defined_x87_st=0xff;
  for(unsigned i=0;i<8;++i){auto fraction=patterns[(i+pattern)%8];std::uint16_t exponent=0x3fff+i;std::memcpy(expected.x87_st[i].data(),&fraction,8);std::memcpy(expected.x87_st[i].data()+8,&exponent,2);expected.xmm[i]=(sharp_retro::bits(patterns[(i+pattern)%8])<<64)|patterns[(i+pattern+3)%8];}expected.defined_xmm=0xffff;for(unsigned i=0;i<8;++i)expected.native_mmx[i]=patterns[(i+pattern+2)%8];expected.defined_native_mmx=0xff;
  expected.gpr[0]=std::uint32_t(patterns[pattern]);expected.gpr[2]=std::uint32_t(patterns[(pattern+3)%8]);expected.gpr[4]=0x5000f000;
  auto operand=0x50010083u;expected.gpr[6]=operand;
  sharp_retro::bits initial=(sharp_retro::bits(0x5a5a5a5a5a5a5a5aULL)<<64)|patterns[pattern];memory.store(operand,initial,128);memory.store(expected.gpr[4],0x12345678,32);auto candidate=expected;
  if(!invoke_native_abi_address(std::uint32_t(reinterpret_cast<std::uintptr_t>(shift_reference_code+form*32)),expected,memory))return 5;
  auto output=memory.load(operand,128);memory.store(operand,initial,128);memory.store(candidate.gpr[4],0x12345678,32);
  std::uint64_t budget=10;auto result=execute_guest(0x31001000+form*32,0x12345678,candidate,memory,budget);
  bool registers=true;for(unsigned i=0;i<8;++i)if(candidate.gpr[i]!=expected.gpr[i]||candidate.xmm[i]!=expected.xmm[i])registers=false;
  bool match=result==sharp_retro::Exit::returned&&registers&&candidate.flags==expected.flags&&memory.load(operand,128)==output&&fp_same(candidate,expected)&&(!native_mmx_is_split()||candidate.native_mmx==expected.native_mmx)&&candidate.defined_x87_st==0xff;
  ++cases;if(!match){++mismatches;if(mismatches<8)std::fprintf(stderr,"mmx form=%u op=%x mem=%u top=%u tags=%x pattern=%u rc=%u regs=%u fp=%u SW=%x/%x TAG=%x/%x\n",form,fixture.opcode,unsigned(fixture.mem),top,tags,pattern,rounding,unsigned(registers),unsigned(fp_same(candidate,expected)),candidate.x87_status,expected.x87_status,candidate.x87_tag,expected.x87_tag);if(mismatches<2)for(unsigned i=0;i<8;++i){if(candidate.gpr[i]!=expected.gpr[i])std::fprintf(stderr,"GPR%u=%llx/%llx\n",i,(unsigned long long)candidate.gpr[i],(unsigned long long)expected.gpr[i]);if(candidate.xmm[i]!=expected.xmm[i])std::fprintf(stderr,"XMM%u=%llx:%llx/%llx:%llx\n",i,(unsigned long long)(candidate.xmm[i]>>64),(unsigned long long)candidate.xmm[i],(unsigned long long)(expected.xmm[i]>>64),(unsigned long long)expected.xmm[i]);}}
 }
 sharp_retro::State after;capture_native_context(after);bool restored=fp_same(host,after)&&(!native_mmx_is_split()||host.native_mmx==after.native_mmx);
 std::printf("{\"native_mmx_encodings\":%u,\"physical_comparisons\":%u,\"mismatches\":%u,\"host_fp_restored\":%s,\"game_acceptance\":false}\n",n,cases,mismatches,restored?"true":"false");return mismatches||!restored?1:0;
}catch(const std::exception& e){std::fprintf(stderr,"MMX control failed: %s\n",e.what());return 10;}}

// Unknown physical slots must survive MMX aliasing without becoming zero facts.
#include "functions.hpp"
#include "image_memory.hpp"
#include "native_floating.hpp"
#include <cstdio>
namespace sharp_retro {void native_legacy(Memory&,State&,std::uint64_t,unsigned,std::uint32_t,std::uint32_t);}
int main(){try{
 recomp_generated::ImageMemory memory;memory.map_bytes("ram",0x8000,4096,true,true);memory.seal();memory.store(0x8001,0x800000017fffffffULL,64);
 sharp_retro::State host;recomp_generated::capture_native_fp(host);unsigned cases=0,guards=0;bool split=recomp_generated::native_mmx_is_split();
 for(unsigned top=0;top<8;++top){
  auto s=host;s.x87_control=0x37f;s.x87_status=top<<11;s.x87_tag=0xffff;s.defined_x87_st=0;
  for(unsigned i=0;i<8;++i){std::uint64_t f=0xabcdef0000000000ULL+i;std::memcpy(s.x87_st[i].data(),&f,8);}
  auto invoke=[&](unsigned opcode,unsigned reg=0,unsigned rm=0,bool mem=false){sharp_retro::native_legacy(memory,s,0x31001000,0,opcode|(reg<<8)|(rm<<11)|(mem?0x4000u:0u),0x8001);};
  for(unsigned opcode:{0xefu,0xfau,0x76u}){
   s.defined_x87_st=0;s.defined_native_mmx=0;invoke(opcode,3,3);auto logical=(3+8-((s.x87_status>>11)&7))&7;
   std::uint64_t value;if(split)value=s.native_mmx[3];else std::memcpy(&value,s.x87_st[logical].data(),8);
   if((split?s.defined_native_mmx!=(1u<<3):s.defined_x87_st!=(1u<<logical))||value!=(opcode==0x76?~std::uint64_t(0):0))return 1;++cases;
  }
  invoke(0x6f,5,6,true);auto logical=(5+8-((s.x87_status>>11)&7))&7;
  if(!(split?s.defined_native_mmx&(1u<<5):s.defined_x87_st&(1u<<logical)))return 2;
  invoke(0x7e,5,0);if(s.gpr[0]!=0x7fffffffu)return 3;++cases;
  auto before=s;bool refused=false;
  try{invoke(0xdb,5,1);}catch(const std::runtime_error&){refused=true;}
  if(!refused||s.x87_st!=before.x87_st||s.native_mmx!=before.native_mmx||s.defined_native_mmx!=before.defined_native_mmx||s.defined_x87_st!=before.defined_x87_st||s.x87_status!=before.x87_status||s.x87_tag!=before.x87_tag)return 4;++guards;
  s.defined_xmm|=1;s.xmm[0]=sharp_retro::bits(0xabcdef0123456789ULL)<<64;
  invoke(0x2a,0,6,true);if(std::uint64_t(s.xmm[0]>>64)!=0xabcdef0123456789ULL)return 5;++cases;
  auto tags=s.x87_tag;invoke(0x77);if(s.x87_tag!=(split?tags:0xffffu))return 6;++cases;
 }
 std::printf("{\"mmx_unknown_cases\":%u,\"refusal_guards\":%u,\"game_acceptance\":false}\n",cases,guards);return cases==48&&guards==8?0:7;
}catch(const std::exception& e){std::fprintf(stderr,"MMX unknown control failed: %s\n",e.what());return 10;}}

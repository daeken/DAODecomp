#include "functions.hpp"
#include "image_memory.hpp"
#include "native_x87.hpp"
#include <cstdio>
#include <cstring>
using namespace recomp_generated;
struct DebugMemory : ImageMemory {
 bool tracing=false;unsigned reads=0,writes=0,checks=0;
 sharp_retro::bits load(std::uint64_t a,unsigned w)override{if(tracing&&a>=0x9001&&a<0x9081){++reads;if(w!=8)throw std::runtime_error("wrong environment load width");}return ImageMemory::load(a,w);}
 void store(std::uint64_t a,sharp_retro::bits v,unsigned w)override{if(tracing&&a>=0x9001&&a<0x9081){++writes;if(w!=8)throw std::runtime_error("wrong environment store width");}ImageMemory::store(a,v,w);}
 void validate_store(std::uint64_t a,unsigned w)override{if(tracing){++checks;if(a<0x9001||a>=0x906d||w!=8)throw std::runtime_error("wrong environment store range");}ImageMemory::validate_store(a,w);}
 void execute_x87(sharp_retro::X87Op op,sharp_retro::State& s,std::uint64_t pc,std::uint32_t address,std::uint16_t opcode)override{execute_native_x87(*this,op,s,pc,address,opcode);}
};
static bool same(const sharp_retro::State& a,const sharp_retro::State& b){return a.x87_control==b.x87_control&&a.x87_status==b.x87_status&&a.x87_tag==b.x87_tag&&a.mxcsr==b.mxcsr&&a.x87_st==b.x87_st&&a.x87_ip==b.x87_ip&&a.x87_dp==b.x87_dp&&a.x87_cs==b.x87_cs&&a.x87_ds==b.x87_ds&&a.x87_opcode==b.x87_opcode;}
static void reference(unsigned form,NativeX87Image& image){switch(form){
#define REF(N,A,B) case N:asm volatile(".byte " #A "," #B::"a"(image.data()):"memory");break;
 REF(0,0xd9,0x20) REF(1,0xd9,0x30) REF(2,0xdd,0x20) REF(3,0xdd,0x30)
#undef REF
}}
static void fill(sharp_retro::State& s,unsigned top,unsigned tags,unsigned rc,unsigned salt){s.x87_control=0x37f|(rc<<10);s.x87_status=0x4700|(top<<11);s.x87_tag=tags;s.defined_x87_st=0xff;s.x87_ip=0x12340000+salt;s.x87_dp=0x98760000+salt;s.x87_opcode=0x321;s.x87_cs=0x23;s.x87_ds=0x2b;
 for(unsigned i=0;i<8;++i){std::uint64_t f=0x8000000000000000ULL|(std::uint64_t(salt+i)<<48);std::uint16_t e=0x3fff+i;std::memcpy(s.x87_st[i].data(),&f,8);std::memcpy(s.x87_st[i].data()+8,&e,2);}}
int main(){try{
 DebugMemory memory;memory.map_bytes("ram",0x8000,0x2000,true,true);memory.seal();memory.store(0x8800,0x12345678,32);
 sharp_retro::State host;capture_native_fp(host);unsigned cases=0,mismatches=0;
 for(unsigned form=0;form<4;++form)for(unsigned top=0;top<8;++top)for(unsigned loadedTop=0;loadedTop<8;++loadedTop)for(unsigned tags:{0u,0xffffu,0xaaaau})for(unsigned rounding=0;rounding<4;++rounding){
  auto expected=host;fill(expected,top,tags,rounding,0x12);auto input=host;fill(input,loadedTop,0x5a5a,3-rounding,0x56);auto image=native_fp_image(input,false);auto initial=image;
  auto candidate=expected;{NativeFloatingScope fp(expected,false);reference(form,image);fp.finish();}
  memory.store(0x9000,0x5a,8);for(unsigned i=0;i<108;++i)memory.store(0x9001+i,initial[i],8);memory.store(0x906d,0xa5,8);
  candidate.gpr[0]=0x9001;candidate.gpr[4]=0x8800;auto before=candidate;memory.reads=memory.writes=memory.checks=0;memory.tracing=true;
  std::uint64_t budget=10;auto exit=execute_guest(0x401000+form*16,0x12345678,candidate,memory,budget);memory.tracing=false;
  bool content=memory.load(0x9000,8)==0x5a&&memory.load(0x906d,8)==0xa5;for(unsigned i=0;i<108;++i)if(memory.load(0x9001+i,8)!=image[i])content=false;
  bool registers=true;for(unsigned i=0;i<16;++i)if(candidate.gpr[i]!=(i==4?before.gpr[i]+4:before.gpr[i]))registers=false;
  unsigned size=form>=2?108:28;bool footprint=memory.reads==(form%2==0?size:0)&&memory.writes==(form%2?size:0)&&memory.checks==(form%2?size:0);
  bool match=exit==sharp_retro::Exit::returned&&budget==8&&registers&&content&&footprint&&same(candidate,expected)&&candidate.defined_x87_st==0xff&&candidate.flags==before.flags;
  ++cases;if(!match){++mismatches;if(mismatches<8)std::fprintf(stderr,"environment form=%u TOP=%u loadedTOP=%u tags=%x rc=%u registers=%u content=%u footprint=%u fp=%u TOPs=%x/%x\n",form,top,loadedTop,tags,rounding,unsigned(registers),unsigned(content),unsigned(footprint),unsigned(same(candidate,expected)),candidate.x87_status,expected.x87_status);}
 }
 sharp_retro::State after;capture_native_fp(after);bool restored=same(host,after);
 std::printf("{\"native_environment_cases\":%u,\"mismatches\":%u,\"host_fp_restored\":%s,\"game_acceptance\":false}\n",cases,mismatches,restored?"true":"false");return mismatches||!restored?1:0;
}catch(const std::exception& e){std::fprintf(stderr,"environment control failed: %s\n",e.what());return 10;}}

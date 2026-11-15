// Exact signed-qword load needed by main 0x004cb18f; infrastructure debugging.
#include "x87_pop_control.inc"
static void integer64_reference(std::uint64_t value){asm volatile(".byte 0xdf,0x28"::"a"(&value):"memory");}
int main(){
 if(auto result=pop_control())return result;
 CompareMemory memory;memory.map_bytes("ram",0x8000,0x2000,true,true);memory.seal();memory.store(0x8800,0x12345678,32);
 sharp_retro::State host;recomp_generated::capture_native_fp(host);unsigned cases=0,mismatches=0,guards=0;
 const std::uint64_t values[]={0,1,0xffffffffffffffffULL,0x7fffffffffffffffULL,0x8000000000000000ULL,0x8000000000000001ULL,0x1000001,0x1ffffff,0x20000000000001ULL,0xffffffff00000001ULL,0x7fffffff00000000ULL};
 for(unsigned top=0;top<8;++top)for(unsigned precision:{0u,2u,3u})for(unsigned rounding=0;rounding<4;++rounding)for(unsigned mode=0;mode<3;++mode)for(auto value:values){
  auto expected=host;expected.x87_control=std::uint16_t(0x7f|(precision<<8)|(rounding<<10));expected.x87_status=std::uint16_t(0x4700|(top<<11));expected.x87_tag=0;expected.defined_x87_st=0xff;
  for(unsigned i=0;i<8;++i)raw(expected,i,0x8000000000000000ULL|(std::uint64_t(i)<<59),0x3fff);
  if(mode==1)expected.x87_tag=0xffff;
  if(mode==2)expected.x87_tag|=std::uint16_t(3u<<(((top+7)&7)*2));
  auto candidate=expected;{recomp_generated::NativeFloatingScope scope(expected,false);integer64_reference(value);scope.finish();}
  memory.store(0x9001,value,64);candidate.gpr[0]=0x9001;candidate.gpr[4]=0x8800;auto before=candidate;
  memory.reads=memory.writes=0;memory.tracing=true;std::uint64_t budget=10;
  auto result=recomp_generated::execute_guest(0x401700,0x12345678,candidate,memory,budget);memory.tracing=false;
  bool registers=true;for(unsigned i=0;i<16;++i)if(candidate.gpr[i]!=(i==4 ? before.gpr[i]+4:before.gpr[i]))registers=false;
  bool match=result==sharp_retro::Exit::returned&&registers&&candidate.flags==before.flags&&candidate.defined_flags==before.defined_flags&&candidate.defined_x87_st==0xff&&same(expected,candidate)&&memory.reads==1&&memory.last_width==64&&!memory.writes;
  ++cases;if(!match){++mismatches;if(mismatches<5)std::fprintf(stderr,"integer64 top=%u mode=%u value=%llx SW=%x/%x TAG=%x/%x\n",top,mode,(unsigned long long)value,expected.x87_status,candidate.x87_status,expected.x87_tag,candidate.x87_tag);}
 }
 {sharp_retro::State check;recomp_generated::capture_native_fp(check);if(!same(host,check))std::fprintf(stderr,"integer64 host changed before refusal fixtures\n");}
 for(unsigned mode=0;mode<4;++mode){
  auto state=host;state.x87_control=mode==0 ? 0x37e:0x37f;state.x87_status=0;state.x87_tag=0xfffc;state.defined_x87_st=mode==1 ? 0xfe:0xff;raw(state,0,0x8000000000000000ULL,0x3fff);auto before=state;
  // Unknown-byte fixture insertion can rehash a C++ unordered_set, changing
  // host FP status. Isolate that setup exactly as in the memory-compare control;
  // the provider call below must still preserve its incoming host state.
  {auto fixture_state=host;recomp_generated::NativeFloatingScope fixture(fixture_state,false);
   memory.forget_unknown_range(0x9001,8);memory.store(0x9001,0,64);if(mode==2)memory.store_unknown(0x9001,0,64);}
  memory.writes=0;memory.tracing=true;
  sharp_retro::State setup;recomp_generated::capture_native_fp(setup);if(!same(host,setup))std::fprintf(stderr,"integer64 fixture changed host before mode %u\n",mode);
  try{recomp_generated::execute_native_x87(memory,recomp_generated::native_encoded_x87,state,0x401700,mode==3 ? 0x9ffc:0x9001,0x728);}
  catch(const std::runtime_error&){if(same(state,before)&&state.defined_x87_st==before.defined_x87_st&&!memory.writes)++guards;}memory.tracing=false;
  sharp_retro::State finished;recomp_generated::capture_native_fp(finished);if(!same(setup,finished))std::fprintf(stderr,"integer64 provider changed host in mode %u\n",mode);
 }
 for(unsigned opcode:{0x8728u,0x7e8u,0x720u}){auto state=host;auto before=state;try{recomp_generated::execute_native_x87(memory,recomp_generated::native_encoded_x87,state,0x401700,0x9001,opcode);}catch(const std::runtime_error&){if(same(state,before))++guards;}}
 sharp_retro::State after;recomp_generated::capture_native_fp(after);bool restored=same(host,after);
 if(!restored){std::fprintf(stderr,"integer64 host CW=%x/%x SW=%x/%x TAG=%x/%x MXCSR=%x/%x values_equal=%u\n",host.x87_control,after.x87_control,host.x87_status,after.x87_status,host.x87_tag,after.x87_tag,host.mxcsr,after.mxcsr,unsigned(host.x87_st==after.x87_st));}
 std::printf("{\"native_signed_integer64_load_cases\":%u,\"mismatches\":%u,\"failure_guards\":%u,\"host_fp_restored\":%s}\n",cases,mismatches,guards,restored?"true":"false");return mismatches||guards!=7||!restored ? 1:0;
}

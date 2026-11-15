#include "native_callback_entry.hpp"
#include <cstdio>
using namespace recomp_generated;
extern "C" unsigned char mmx_callback_reference[];
using Callback=unsigned(__cdecl*)(unsigned,unsigned);
static unsigned entries=0;
static LONG CALLBACK observe(EXCEPTION_POINTERS* event){
 if(event->ContextRecord->Eip!=0x31001160||!native_callback::is_execute_fault(event))return EXCEPTION_CONTINUE_SEARCH;
 try{if(native_callback::schedule(event)){++entries;return EXCEPTION_CONTINUE_EXECUTION;}}catch(const std::exception& e){std::fprintf(stderr,"MMX callback: %s\n",e.what());}
 TerminateProcess(GetCurrentProcess(),11);return EXCEPTION_CONTINUE_SEARCH;
}
extern "C" __declspec(noinline) unsigned __stdcall mmx_add(unsigned a,unsigned b,unsigned c){return a+b+c;}
extern "C" unsigned mmx_callback_control(Callback,const std::uint64_t*,std::uint64_t*);
asm(".text\n.globl _mmx_callback_control\n_mmx_callback_control:\n"
 "pushl %esi; pushl %edi; movl 12(%esp),%eax; movl 16(%esp),%esi; movl 20(%esp),%edi;"
 "movq 0(%esi),%mm0; movq 8(%esi),%mm1; movq 16(%esi),%mm2; movq 24(%esi),%mm3;"
 "movq 32(%esi),%mm4; movq 40(%esi),%mm5; movq 48(%esi),%mm6; movq 56(%esi),%mm7;"
 "pushl $9; pushl $12; call *%eax; addl $8,%esp;"
 "movq %mm0,0(%edi); movq %mm1,8(%edi); movq %mm2,16(%edi); movq %mm3,24(%edi);"
 "movq %mm4,32(%edi); movq %mm5,40(%edi); movq %mm6,48(%edi); movq %mm7,56(%edi);"
 "popl %edi; popl %esi; ret;\n");
int main(){try{
 if(!SetProcessDEPPolicy(PROCESS_DEP_ENABLE|PROCESS_DEP_DISABLE_ATL_THUNK_EMULATION))return 2;native_callback::initialize();
 NativeX86Memory memory;memory.reserve_image(0x31000000,0x3000);memory.map_bytes("NX code",0x31001000,4096,true,false);memory.map_bytes("IAT",0x31002000,4096,true,true);
 auto* tib=reinterpret_cast<NT_TIB*>(NtCurrentTeb());memory.add_native_stack(reinterpret_cast<std::uintptr_t>(tib->StackLimit),reinterpret_cast<std::uintptr_t>(tib->StackBase));memory.store(0x31002050,reinterpret_cast<std::uintptr_t>(&mmx_add),32);
 const unsigned char code[]={0x0f,0xdb,0xd9,0x6a,3,0xff,0x74,0x24,0x0c,0xff,0x74,0x24,0x0c,0xff,0x15,0x50,0x20,0,0x31,0x0f,0xeb,0xd4,0xc3};
 // The code page is deliberately NX; these bytes are identification evidence.
 for(unsigned i=0;i<sizeof(code);++i)memory.store(0x31001160+i,code[i],8);
 memory.seal();native_callback::adopt_images=[](NativeX86Memory& m){m.ProcessMemory::reserve_image(0x31000000,0x3000);};auto handler=AddVectoredExceptionHandler(1,observe);if(!handler)return 3;
 sharp_retro::State host;capture_native_context(host);std::uint64_t budget=10000;unsigned cases=0,mismatches=0;
 for(unsigned pattern=0;pattern<32;++pattern){
  NativeMmxImage input{},expected{},candidate{};for(unsigned i=0;i<8;++i)input[i]=(0x123456789abcdef0ULL>>(pattern%16))^(std::uint64_t(i+pattern)<<37);
  unsigned a=0,b=0;{auto working=host;NativeFloatingScope fp(working,false);a=mmx_callback_control(reinterpret_cast<Callback>(mmx_callback_reference),input.data(),expected.data());fp.finish();}
  {auto working=host;NativeFloatingScope fp(working,false);native_callback::Binding binding(memory,budget);b=mmx_callback_control(reinterpret_cast<Callback>(0x31001160),input.data(),candidate.data());fp.finish();}
  ++cases;if(a!=24||b!=a||candidate!=expected){++mismatches;if(mismatches<4)std::fprintf(stderr,"callback MMX mismatch pattern=%u result=%u/%u\n",pattern,b,a);}
 }
 RemoveVectoredExceptionHandler(handler);std::printf("{\"callback_mmx_cases\":%u,\"entries\":%u,\"mismatches\":%u,\"game_acceptance\":false}\n",cases,entries,mismatches);return mismatches||entries!=32?1:0;
}catch(const std::exception& e){std::fprintf(stderr,"callback MMX control failed: %s\n",e.what());return 10;}}

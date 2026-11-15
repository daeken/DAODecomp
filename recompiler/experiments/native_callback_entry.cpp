// Constructed native -> compiled x86 -> native calls. No game acceptance.
#include "native_callback_entry.hpp"
#include <cstdio>
using namespace recomp_generated;
#define CHECK(x) do{if(!(x))throw std::runtime_error(std::string("line ")+std::to_string(__LINE__)+": "+#x);}while(false)
using Callback=unsigned(__cdecl*)(unsigned,unsigned);
static Callback callback=reinterpret_cast<Callback>(0x31001160);
static unsigned entries=0;
static CONTEXT last_context{};
static LONG CALLBACK observe(EXCEPTION_POINTERS* event){
 auto error=GetLastError();
 if(event->ContextRecord->Eip!=0x31001160||!native_callback::is_execute_fault(event)){SetLastError(error);return EXCEPTION_CONTINUE_SEARCH;}
 last_context=*event->ContextRecord;
 std::uint16_t incoming_status=0;std::memcpy(&incoming_status,last_context.ExtendedRegisters+2,2);
 std::fprintf(stderr,"callback input FP: legacy=%lx/%lx/%lx extended=%x/%x context=%lx\n",last_context.FloatSave.ControlWord,last_context.FloatSave.StatusWord,last_context.FloatSave.TagWord,incoming_status,unsigned(last_context.ExtendedRegisters[4]),last_context.ContextFlags);
 try{SetLastError(error);if(native_callback::schedule(event)){++entries;return EXCEPTION_CONTINUE_EXECUTION;}}catch(const std::exception& e){std::fprintf(stderr,"callback control: %s\n",e.what());}
 TerminateProcess(GetCurrentProcess(),11);return EXCEPTION_CONTINUE_SEARCH;
}
static thread_local unsigned depth=0;
extern "C" __declspec(noinline) unsigned __stdcall nested(unsigned a,unsigned b,unsigned c){
 if(depth)return a+b+c;++depth;auto result=callback(a,b);--depth;SetLastError(0x13572468);return result+100;
}
extern "C" __declspec(noinline) unsigned __stdcall add(unsigned a,unsigned b,unsigned c){return a+b+c;}
static DWORD WINAPI thread(void*){return callback(7,6);}
extern "C" unsigned __cdecl callback_xmm_control(Callback,const unsigned char*,unsigned char*);
asm(".text\n.globl _callback_xmm_control\n_callback_xmm_control:\n"
 "pushl %esi\npushl %edi\nmovl 12(%esp),%eax\nmovl 16(%esp),%esi\nmovl 20(%esp),%edi\n"
 "movups 0(%esi),%xmm0\nmovups 16(%esi),%xmm1\nmovups 32(%esi),%xmm2\nmovups 48(%esi),%xmm3\n"
 "movups 64(%esi),%xmm4\nmovups 80(%esi),%xmm5\nmovups 96(%esi),%xmm6\nmovups 112(%esi),%xmm7\n"
 "pushl $9\npushl $12\ncall *%eax\naddl $8,%esp\n"
 "movups %xmm0,0(%edi)\nmovups %xmm1,16(%edi)\nmovups %xmm2,32(%edi)\nmovups %xmm3,48(%edi)\n"
 "movups %xmm4,64(%edi)\nmovups %xmm5,80(%edi)\nmovups %xmm6,96(%edi)\nmovups %xmm7,112(%edi)\n"
 "popl %edi\npopl %esi\nret\n");
int main(){try{
 CHECK(SetProcessDEPPolicy(PROCESS_DEP_ENABLE|PROCESS_DEP_DISABLE_ATL_THUNK_EMULATION));native_callback::initialize();
 NativeX86Memory memory;memory.reserve_image(0x31000000,0x3000);memory.map_bytes("constructed NX code",0x31001000,4096,true,false);
 unsigned char bytes[]={0x6a,3,0xff,0x74,0x24,0x0c,0xff,0x74,0x24,0x0c,0xff,0x15,0x50,0x20,0,0x31,0xc3};
 for(unsigned i=0;i<sizeof(bytes);++i)memory.store(0x31001160+i,bytes[i],8);
 memory.map_bytes("native IAT",0x31002000,4096,true,true);memory.seal();
 auto* tib=reinterpret_cast<NT_TIB*>(NtCurrentTeb());memory.add_native_stack(reinterpret_cast<std::uintptr_t>(tib->StackLimit),reinterpret_cast<std::uintptr_t>(tib->StackBase));
 native_callback::adopt_images=[](NativeX86Memory& m){m.ProcessMemory::reserve_image(0x31000000,0x3000);};
 auto handler=AddVectoredExceptionHandler(1,observe);CHECK(handler);
 auto muldiv=GetProcAddress(GetModuleHandleW(L"kernel32.dll"),"MulDiv");CHECK(muldiv);memory.store(0x31002050,reinterpret_cast<std::uintptr_t>(muldiv),32);
 std::uint64_t budget=1000;unsigned direct=0,nested_result=0;
 {native_callback::Binding binding(memory,budget);SetLastError(0x24681357);direct=callback(12,9);CHECK(direct==36);CHECK(GetLastError()==0x24681357);
  memory.store(0x31002050,reinterpret_cast<std::uintptr_t>(&nested),32);nested_result=callback(12,9);CHECK(nested_result==124);CHECK(GetLastError()==0x13572468);}
 memory.store(0x31002050,reinterpret_cast<std::uintptr_t>(muldiv),32);
 auto worker=CreateThread(nullptr,0,thread,nullptr,0,nullptr);CHECK(worker);CHECK(WaitForSingleObject(worker,10000)==WAIT_OBJECT_0);DWORD exit=0;CHECK(GetExitCodeThread(worker,&exit)&&exit==14);CloseHandle(worker);
 memory.store(0x31002050,reinterpret_cast<std::uintptr_t>(&add),32);
 alignas(16) NativeX87Image before{},after{};
 {native_callback::Binding binding(memory,budget);asm volatile("fld1\n\tfnsave %0\n\tfrstor %0":"=m"(before)::"memory");
  auto live=callback(12,9);asm volatile("fnsave %0\n\tfninit":"=m"(after)::"memory");CHECK(live==24);}
 std::fprintf(stderr,"live x87 before=%x/%x/%x after=%x/%x/%x\n",fp_word(before,0),fp_word(before,4),fp_word(before,8),fp_word(after,0),fp_word(after,4),fp_word(after,8));
 CHECK(fp_word(before,0)==fp_word(after,0)&&fp_word(before,4)==fp_word(after,4)&&fp_word(before,8)==fp_word(after,8));
 CHECK(std::memcmp(before.data()+28,after.data()+28,10)==0);
 unsigned fp_cases=1;static const double values[]={1,2,4,8,16,32,64,128};
 for(unsigned top=0;top<8;++top){native_callback::Binding binding(memory,budget);
  asm volatile("fninit\n\tfldl 0(%0)\n\tfldl 8(%0)\n\tfldl 16(%0)\n\tfldl 24(%0)\n\tfldl 32(%0)\n\tfldl 40(%0)\n\tfldl 48(%0)\n\tfldl 56(%0)"::"r"(values):"memory");
  for(unsigned i=0;i<top;++i)asm volatile("fincstp":::"memory");
  asm volatile("fnsave %0\n\tfrstor %0":"=m"(before)::"memory");auto result=callback(12,9);asm volatile("fnsave %0\n\tfninit":"=m"(after)::"memory");CHECK(result==24);
  CHECK(fp_word(before,0)==fp_word(after,0)&&fp_word(before,4)==fp_word(after,4)&&fp_word(before,8)==fp_word(after,8));CHECK(std::memcmp(before.data()+28,after.data()+28,80)==0);++fp_cases;}
 const std::uint64_t specials[]={0x8000000000000000ULL,0x7ff0000000000000ULL,0x7ff8000000001234ULL};
 for(auto raw:specials){native_callback::Binding binding(memory,budget);asm volatile("fldl %1\n\tfnsave %0\n\tfrstor %0":"=m"(before):"m"(raw):"memory");
  auto result=callback(12,9);asm volatile("fnsave %0\n\tfninit":"=m"(after)::"memory");CHECK(result==24);
  CHECK(fp_word(before,0)==fp_word(after,0)&&fp_word(before,4)==fp_word(after,4)&&fp_word(before,8)==fp_word(after,8));CHECK(std::memcmp(before.data()+28,after.data()+28,10)==0);++fp_cases;}
 alignas(16) unsigned char xmm_input[128],xmm_output[128]{};
 for(unsigned i=0;i<128;++i)xmm_input[i]=static_cast<unsigned char>(i*37+19);
 {native_callback::Binding binding(memory,budget);CHECK(callback_xmm_control(callback,xmm_input,xmm_output)==24);}
 CHECK(std::memcmp(xmm_input,xmm_output,sizeof(xmm_input))==0);
 unsigned guards=0;CONTEXT context=last_context;sharp_retro::State captured;native_callback::context_state(context,captured);
 auto incomplete=context;incomplete.ContextFlags=CONTEXT_FULL;
 try{sharp_retro::State s;native_callback::context_state(incomplete,s);}catch(const std::runtime_error&){++guards;}
 auto flags=captured;flags.defined_flags&=~16ULL;
 try{native_callback::state_context(flags,context);}catch(const std::runtime_error&){++guards;}
 auto invalid=context;std::uint32_t invalid_mxcsr=0x80000000;std::memcpy(invalid.ExtendedRegisters+24,&invalid_mxcsr,4);
 try{sharp_retro::State s;native_callback::context_state(invalid,s);}catch(const std::runtime_error&){++guards;}
 auto pending=captured;pending.x87_status|=0x80;
 try{native_callback::state_context(pending,context);}catch(const std::runtime_error&){++guards;}
 for(unsigned flag:{0x100u,0x4000u,0x40000u}){
  auto input=last_context;input.EFlags|=flag;try{sharp_retro::State s;native_callback::context_state(input,s);}catch(const std::runtime_error&){++guards;}
  auto output=captured;output.flags|=flag;try{native_callback::state_context(output,context);}catch(const std::runtime_error&){++guards;}}
 unsigned fault_guards=0;EXCEPTION_RECORD refusal{};CONTEXT refusal_context=last_context;
 EXCEPTION_POINTERS refusal_event{&refusal,&refusal_context};
 refusal.ExceptionCode=EXCEPTION_ILLEGAL_INSTRUCTION;refusal_context.Eip=reinterpret_cast<std::uintptr_t>(&add);
 if(!native_callback::is_execute_fault(&refusal_event))++fault_guards;
 refusal.ExceptionCode=EXCEPTION_ACCESS_VIOLATION;refusal.NumberParameters=2;refusal.ExceptionInformation[0]=0;
 refusal_context.Eip=0x31001160;refusal.ExceptionInformation[1]=refusal_context.Eip;
 if(!native_callback::is_execute_fault(&refusal_event))++fault_guards;
 refusal.ExceptionInformation[0]=8;refusal.ExceptionInformation[1]=0x31001161;
 if(!native_callback::is_execute_fault(&refusal_event))++fault_guards;
 auto* inaccessible=VirtualAlloc(nullptr,4096,MEM_RESERVE|MEM_COMMIT,PAGE_NOACCESS);CHECK(inaccessible);
 refusal.ExceptionCode=native_callback::execute_fault_code;refusal.NumberParameters=refusal.ExceptionCode==EXCEPTION_ACCESS_VIOLATION?2:0;
 refusal_context.Eip=reinterpret_cast<std::uintptr_t>(inaccessible);refusal.ExceptionInformation[0]=8;refusal.ExceptionInformation[1]=refusal_context.Eip;
 if(!native_callback::is_execute_fault(&refusal_event))++fault_guards;
 VirtualFree(inaccessible,0,MEM_RELEASE);
 CHECK(guards==10&&entries==17&&fp_cases==12&&fault_guards==4);RemoveVectoredExceptionHandler(handler);
 std::printf("{\"direct_result\":%u,\"nested_result\":%u,\"new_thread_result\":%lu,\"compiled_callback_entries\":%u,\"live_x87_preserved\":true,\"live_fp_cases\":%u,\"live_xmm_cases\":1,\"live_xmm_bytes\":128,\"live_xmm_preserved\":true,\"last_error_preserved\":true,\"refusal_guards\":%u,\"execute_fault_refusal_guards\":%u,\"execute_fault_code\":%lu,\"remaining_parent_budget\":%llu,\"game_acceptance\":false}\n",direct,nested_result,exit,entries,fp_cases,guards,fault_guards,native_callback::execute_fault_code,(unsigned long long)budget);return 0;
 }catch(const std::exception& error){std::fprintf(stderr,"native callback control: %s\n",error.what());return 10;}}

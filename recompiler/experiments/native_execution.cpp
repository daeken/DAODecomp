// Translate a real constructed x86 caller, then use native pointers/ABI directly.
#include "functions.hpp"
#include "native_execution.hpp"
#include "native_imports.hpp"
#include <cstdio>
using namespace recomp_generated;
#define CHECK(x) do {if(!(x)) throw std::runtime_error(std::string("line ")+std::to_string(__LINE__)+": "+#x);} while(false)
extern "C" __declspec(noinline) unsigned __stdcall native_vtable(unsigned a,unsigned b,unsigned c) {return a+b+c;}
extern "C" __declspec(noinline) double __cdecl native_float(double a,double b) {return a+b;}
extern "C" __declspec(noinline) unsigned __cdecl native_id_flag() {unsigned flags;asm volatile("pushfl; popl %0":"=r"(flags));return flags&0x200000u;}
int main(){try {
    NativeX86Memory memory;memory.reserve_image(0x31000000,0x3000);
    memory.map_bytes("native IAT",0x31002000,4096,true,true);
    memory.map_bytes("native stack",0x50000000,65536,true,true);
    memory.map_bytes("native data",0x50010000,4096,true,true);memory.seal();memory.add_native_stack(0x50000000,0x50010000);
    auto state=[&] {sharp_retro::State s;capture_native_context(s);s.gpr[4]=0x5000f000;memory.store(s.gpr[4],0x12345678,32);return s;};
    auto prepare=[&](std::initializer_list<std::uint32_t> args) {auto s=state();unsigned i=1;for(auto arg:args) memory.store(s.gpr[4]+4*i++,arg,32);return s;};
    auto direct_teb=state();
    memory.store(direct_teb.segments[4]+0x34,0x13572468u,32);
    invoke_native_import({0,"kernel32.dll","GetLastError",false},direct_teb,memory);
    CHECK(direct_teb.gpr[0]==0x13572468u && ::GetLastError()==0x13572468u);
    auto raw_teb=state();memory.store(raw_teb.segments[4]+0x34,0x24681357u,32);
    auto get_error=::GetProcAddress(::GetModuleHandleW(L"kernel32.dll"),"GetLastError");CHECK(get_error);
    ::SetLastError(0x24681357u);
    CHECK(invoke_native_abi_address(std::uint32_t(reinterpret_cast<std::uintptr_t>(get_error)),raw_teb,memory));
    CHECK(raw_teb.gpr[0]==0x24681357u && ::GetLastError()==0x24681357u);
    for(unsigned id:{0u,0x200000u}) {
        auto s=state();s.flags=(s.flags&~0x200000ULL)|id;
        CHECK(invoke_native_abi_address(std::uint32_t(reinterpret_cast<std::uintptr_t>(&native_id_flag)),s,memory));
        CHECK(s.gpr[0]==id && (s.flags&0x200000u)==id);
    }
    auto pattern=(sharp_retro::bits(0x12345678)<<96)|(sharp_retro::bits(0x89abcdef)<<64)|0x9876543210abcdefULL;
    for(unsigned width:{8u,16u,32u,64u,128u}) {
        memory.store(0x50010002,0x5a,8);memory.store(0x50010003+width/8,0xa5,8);
        memory.store(0x50010003,pattern,width);
        auto mask=width==128 ? ~sharp_retro::bits(0):(sharp_retro::bits(1)<<width)-1;
        CHECK(memory.load(0x50010003,width)==(pattern&mask));
        CHECK(memory.load(0x50010002,8)==0x5a && memory.load(0x50010003+width/8,8)==0xa5);
    }
    memory.store(0x31002050,0x31002050,32);
    auto first=prepare({12,9});std::uint64_t budget=100;
    CHECK(execute_guest(0x31001160,0x12345678,first,memory,budget)==sharp_retro::Exit::returned && first.gpr[0]==36 && first.gpr[4]==0x5000f004);
    // A native GetProcAddress result needs no symbol/variable marshalling entry.
    auto target=::GetProcAddress(::GetModuleHandleW(L"kernel32.dll"),"MulDiv");CHECK(target);
    memory.store(0x31002050,reinterpret_cast<std::uintptr_t>(target),32);auto dynamic=prepare({12,9});budget=100;
    CHECK(execute_guest(0x31001160,0x12345678,dynamic,memory,budget)==sharp_retro::Exit::returned && dynamic.gpr[0]==36);
    // Same transport for an ordinary native vtable-style function address.
    memory.store(0x31002050,reinterpret_cast<std::uintptr_t>(&native_vtable),32);auto indirect=prepare({12,9});budget=100;
    CHECK(execute_guest(0x31001160,0x12345678,indirect,memory,budget)==sharp_retro::Exit::returned && indirect.gpr[0]==24);
    auto heap_state=prepare({});invoke_native_import({0,"kernel32.dll","GetProcessHeap",false},heap_state,memory);
    auto heap=std::uint32_t(heap_state.gpr[0]);auto allocated=prepare({heap,HEAP_ZERO_MEMORY,64});
    invoke_native_import({0,"kernel32.dll","HeapAlloc",false},allocated,memory);auto pointer=std::uint32_t(allocated.gpr[0]);CHECK(pointer);
    CHECK(memory.load(pointer,32)==0);memory.store(pointer+17,0x12345678,32);CHECK(memory.load(pointer+17,32)==0x12345678);
    // Native production does not include the strict ownership-wrapper headers.
    auto freed=prepare({heap,0,pointer});invoke_native_import({0,"kernel32.dll","HeapFree",false},freed,memory);CHECK(freed.gpr[0]);
    double a=1.25,b=2.5;std::uint64_t x,y;std::memcpy(&x,&a,8);std::memcpy(&y,&b,8);
    auto floating=prepare({std::uint32_t(x),std::uint32_t(x>>32),std::uint32_t(y),std::uint32_t(y>>32)});
    CHECK(invoke_native_abi_address(std::uint32_t(reinterpret_cast<std::uintptr_t>(&native_float)),floating,memory));
    CHECK(floating.defined_x87_st&1);
    memory.execute_x87(sharp_retro::X87Op::fstp64,floating,0x31001000,0x50010000,0);
    double result;auto raw=std::uint64_t(memory.load(0x50010000,64));std::memcpy(&result,&raw,8);CHECK(result==3.75);
    unsigned guards=0;
    try {memory.store_unknown(0x50010000,0,32);}catch(const std::runtime_error&){++guards;}
    auto unknown=prepare({12,9,3});sharp_retro::invalidate_gprs(unknown,2);
    try {invoke_native_import({0,"kernel32.dll","MulDiv",false},unknown,memory);}catch(const std::runtime_error&){++guards;}
    try {auto s=state();invoke_native_import({0,"umbra.dll","anything",true},s,memory);}catch(const std::runtime_error&){++guards;}
    auto unknown_flags=prepare({12,9,3});unknown_flags.defined_flags&=~16ULL;
    try {invoke_native_import({0,"kernel32.dll","MulDiv",false},unknown_flags,memory);}catch(const std::runtime_error&){++guards;}
    for(unsigned flag:{8u,14u,18u}) {
        auto s=prepare({12,9,3});s.flags|=1u<<flag;
        try {invoke_native_import({0,"kernel32.dll","MulDiv",false},s,memory);}catch(const std::runtime_error&){++guards;}
    }
    auto before=memory.load(0x50010000,32);
    try {memory.store_scalar8(0x50010000,{1,0xfffffffeu,{}});}catch(const std::runtime_error&){++guards;}
    try {memory.store_scalar16(0x50010000,{1,0xfffffffeu,{}});}catch(const std::runtime_error&){++guards;}
    CHECK(guards==9 && memory.load(0x50010000,32)==before);
    std::puts("{\"translated_x86_caller\":true,\"native_static_import\":true,\"raw_GetProcAddress_target\":true,\"native_vtable_target\":true,\"unregistered_native_heap_pointer\":true,\"unaligned_native_memory\":true,\"native_x87_return_consumed\":true,\"ID_flag_preserved\":true,\"direct_TEB_last_error_preserved\":true,\"per_api_ownership_wrappers\":0,\"unknown_and_fallback_guards\":9,\"game_acceptance\":false}");return 0;
}catch(const std::exception& e){std::fprintf(stderr,"native execution: %s\n",e.what());return 10;}}

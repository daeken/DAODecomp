// Native semaphore creation/count/ownership transport, not guest-thread support.
#include "native_imports.hpp"
#include "win32_memory.hpp"
#include <cstdio>
using namespace recomp_generated;
int main(){try{
    Win32ProcessMemory memory;memory.map_bytes("stack",0x50000000,4096,true,true);memory.map_bytes("input",0x50010000,4096,true,true);memory.seal();
    auto invoke=[&](const char* symbol,std::initializer_list<std::uint32_t> args){
        sharp_retro::State s;s.gpr[4]=0x50000800;for(unsigned reg:{3u,5u,6u,7u})s.gpr[reg]=0x12340000u+reg;
        memory.store(0x50000800,0x12345678,32);unsigned i=1;for(auto v:args)memory.store(0x50000800+i++*4,v,32);
        invoke_native_import({0,"KERNEL32.dll",symbol,false},s,memory);
        if(s.pc!=0x12345678 || s.gpr[4]!=0x50000800+i*4 || !(s.defined_gpr&1) || (s.defined_gpr&6) || s.gpr[3]!=0x12340003 || s.gpr[5]!=0x12340005 || s.gpr[6]!=0x12340006 || s.gpr[7]!=0x12340007)throw std::runtime_error("semaphore ABI mismatch");return std::uint32_t(s.gpr[0]);
    };
    auto handle=[](std::uint32_t token){return reinterpret_cast<HANDLE>(std::uintptr_t(token));};unsigned cases=0,failures=0;
    for(auto counts:std::array<std::array<std::uint32_t,2>,8>{{{0,1},{1,1},{2,3},{0,0},{2,1},{0xffffffffu,3},{0,0x80000000u},{0x7fffffffu,0x7fffffffu}}}){
        ::SetLastError(0x13579);auto expected=::CreateSemaphoreW(nullptr,std::bit_cast<LONG>(counts[0]),std::bit_cast<LONG>(counts[1]),nullptr);auto error=::GetLastError();native_error_context.value=0x13579;
        auto token=invoke("CreateSemaphoreW",{0,counts[0],counts[1],0});if(bool(token)!=bool(expected) || native_error_context.value!=error)return 1;
        if(token){
            if(native_kernel_handles.at(token)!=NativeKernelHandleKind::semaphore)return 2;
            for(unsigned j=0;j<3;j++){::SetLastError(0x13579);auto result=::WaitForSingleObjectEx(expected,0,FALSE);error=::GetLastError();native_error_context.value=0x13579;if(invoke("WaitForSingleObjectEx",{token,0,0})!=result || native_error_context.value!=error)return 3;}
            if(!::CloseHandle(expected) || !invoke("CloseHandle",{token}) || native_kernel_handles.contains(token))return 4;
        }else ++failures;++cases;
    }
    auto put=[&](std::uint32_t address,const std::wstring& text){for(unsigned i=0;i<=text.size();i++)memory.store(address+i*2,std::uint16_t(text.c_str()[i]),16);};
    auto name=L"Local\\DAODecomp_semaphore_"+std::to_wstring(::GetCurrentProcessId());put(0x50010000,name);
    auto first=invoke("CreateSemaphoreW",{0,2,3,0x50010000});auto second=invoke("CreateSemaphoreW",{0,0,1,0x50010000});
    if(!first || !second || first==second || native_error_context.value!=ERROR_ALREADY_EXISTS || invoke("WaitForSingleObjectEx",{first,0,0})!=WAIT_OBJECT_0 || invoke("WaitForSingleObjectEx",{second,0,0})!=WAIT_OBJECT_0 || invoke("WaitForSingleObjectEx",{first,0,0})!=WAIT_TIMEOUT)return 5;
    if(!invoke("CloseHandle",{first}) || !invoke("CloseHandle",{second}))return 6;
    auto collision=name+L"_event";put(0x50010200,collision);auto event=::CreateEventW(nullptr,FALSE,FALSE,collision.c_str());if(!event)return 7;
    ::SetLastError(0x13579);auto expected=::CreateSemaphoreW(nullptr,0,1,collision.c_str());auto error=::GetLastError();native_error_context.value=0x13579;
    if(expected || invoke("CreateSemaphoreW",{0,0,1,0x50010200}) || native_error_context.value!=error || !::CloseHandle(event))return 8;
    memory.store(0x50010400,12,32);memory.store(0x50010404,0,32);memory.store(0x50010408,1,32);auto inherited=invoke("CreateSemaphoreW",{0x50010400,0,1,0});DWORD flags=0;
    if(!inherited || !::GetHandleInformation(handle(inherited),&flags) || !(flags&HANDLE_FLAG_INHERIT) || !invoke("CloseHandle",{inherited}))return 9;
    memory.store(0x50010404,0x50010500,32);unsigned refused=0;
    try{(void)invoke("CreateSemaphoreW",{0x50010400,0,1,0});}catch(const std::runtime_error&){++refused;}
    try{(void)invoke("CreateSemaphoreW",{0,0,1,0x12340});}catch(const std::runtime_error&){++refused;}
    if(!native_kernel_handles.empty())return 10;
    std::printf("{\"native_semaphore_count_cases\":%u,\"native_count_failures\":%u,\"named_count_preserved\":true,\"native_name_collision_failure\":true,\"inheritance_preserved\":true,\"refusal_guards\":%u}\n",cases,failures,refused);return cases!=8 || !failures || refused!=2 ? 11 : 0;
}catch(const std::exception& e){std::fprintf(stderr,"semaphore debug: %s\n",e.what());return 12;}}

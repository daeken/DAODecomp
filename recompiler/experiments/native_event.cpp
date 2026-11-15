// Event creation, native reset/state transitions and owned-handle transport.
#include "native_imports.hpp"
#include "win32_memory.hpp"
#include <cstdio>
using namespace recomp_generated;
int main() {
 try {
    Win32ProcessMemory memory;memory.map_bytes("stack",0x50000000,4096,true,true);memory.map_bytes("input",0x50010000,4096,true,true);memory.seal();
    auto invoke=[&](const char* symbol,std::initializer_list<std::uint32_t> args) {
        sharp_retro::State s;s.gpr[4]=0x50000800;
        for(unsigned reg:{3u,5u,6u,7u})s.gpr[reg]=0x12340000u+reg;
        memory.store(0x50000800,0x12345678,32);unsigned i=1;for(auto value:args)memory.store(0x50000800+i++*4,value,32);
        invoke_native_import({0,"KERNEL32.dll",symbol,false},s,memory);
        if(s.pc!=0x12345678 || s.gpr[4]!=0x50000800+i*4 || !(s.defined_gpr&1) || (s.defined_gpr&6) ||
           s.gpr[3]!=0x12340003 || s.gpr[5]!=0x12340005 || s.gpr[6]!=0x12340006 || s.gpr[7]!=0x12340007)throw std::runtime_error("event ABI mismatch");
        return std::uint32_t(s.gpr[0]);
    };
    auto handle=[](std::uint32_t v){return reinterpret_cast<HANDLE>(std::uintptr_t(v));};unsigned cases=0;
    for(std::uint32_t manual:{0u,1u,2u,0x80000000u})for(std::uint32_t initial:{0u,1u,2u,0x80000000u}) {
        ::SetLastError(0x13579);auto expected=::CreateEventW(nullptr,std::bit_cast<BOOL>(manual),std::bit_cast<BOOL>(initial),nullptr);auto error=::GetLastError();native_error_context.value=0x13579;
        auto token=invoke("CreateEventW",{0,manual,initial,0});if(!expected || !token || native_error_context.value!=error || native_kernel_handles.at(token)!=NativeKernelHandleKind::event)return 1;
        for(unsigned phase=0;phase<3;phase++) {
            if(phase==1 && (!::SetEvent(expected) || !::SetEvent(handle(token))))return 2;
            if(phase==2 && (!::ResetEvent(expected) || !::ResetEvent(handle(token))))return 3;
            for(unsigned repeat=0;repeat<2;repeat++) {
                ::SetLastError(0x13579);auto observed=::WaitForSingleObjectEx(expected,0,FALSE);error=::GetLastError();native_error_context.value=0x13579;
                if(invoke("WaitForSingleObjectEx",{token,0,0})!=observed || native_error_context.value!=error)return 4;
            }
        }
        if(!::CloseHandle(expected) || !invoke("CloseHandle",{token}) || native_kernel_handles.contains(token))return 5;++cases;
    }
    auto put=[&](std::uint32_t address,const std::wstring& value){for(unsigned i=0;i<=value.size();i++)memory.store(address+i*2,std::uint16_t(value.c_str()[i]),16);};
    auto name=L"Local\\DAODecomp_event_"+std::to_wstring(::GetCurrentProcessId());put(0x50010000,name);
    auto first=invoke("CreateEventW",{0,1,1,0x50010000});auto second=invoke("CreateEventW",{0,0,0,0x50010000});
    if(!first || !second || first==second || native_error_context.value!=ERROR_ALREADY_EXISTS ||
       invoke("WaitForSingleObjectEx",{first,0,0})!=WAIT_OBJECT_0 || invoke("WaitForSingleObjectEx",{second,0,0})!=WAIT_OBJECT_0)return 6;
    if(!invoke("CloseHandle",{first}) || !invoke("CloseHandle",{second}))return 7;
    auto collision=name+L"_mutex";put(0x50010200,collision);auto mutex=::CreateMutexW(nullptr,FALSE,collision.c_str());if(!mutex)return 8;
    ::SetLastError(0x13579);auto expected=::CreateEventW(nullptr,FALSE,FALSE,collision.c_str());auto error=::GetLastError();native_error_context.value=0x13579;
    if(expected || invoke("CreateEventW",{0,0,0,0x50010200}) || native_error_context.value!=error || !::CloseHandle(mutex))return 9;
    memory.store(0x50010400,12,32);memory.store(0x50010404,0,32);memory.store(0x50010408,1,32);
    auto inherited=invoke("CreateEventW",{0x50010400,0,0,0});DWORD flags=0;if(!inherited || !::GetHandleInformation(handle(inherited),&flags) || !(flags&HANDLE_FLAG_INHERIT) || !invoke("CloseHandle",{inherited}))return 10;
    unsigned refused=0;memory.store(0x50010404,0x50010500,32);
    try{(void)invoke("CreateEventW",{0x50010400,0,0,0});}catch(const std::runtime_error&){++refused;}
    try{(void)invoke("CreateEventW",{0,0,0,0x12340});}catch(const std::runtime_error&){++refused;}
    if(!native_kernel_handles.empty())return 11;
    std::printf("{\"native_event_state_cases\":%u,\"named_existing_state_preserved\":true,\"native_name_collision_failure\":true,\"inheritance_preserved\":true,\"refusal_guards\":%u}\n",cases,refused);return cases!=16 || refused!=2 ? 12 : 0;
 }catch(const std::exception& e){std::fprintf(stderr,"event debug: %s\n",e.what());return 13;}
}

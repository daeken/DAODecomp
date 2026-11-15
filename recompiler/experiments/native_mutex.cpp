// Actual kernel-object boundaries needed by the reached CreateMutexW import.
#include "native_imports.hpp"
#include "win32_memory.hpp"
#include <cstdio>
#include <cwchar>
using namespace recomp_generated;
struct Probe { HANDLE mutex; DWORD result=WAIT_FAILED; };
static DWORD WINAPI probe_thread(void* data) {
    auto& probe=*static_cast<Probe*>(data); probe.result=::WaitForSingleObject(probe.mutex,0);
    if(probe.result==WAIT_OBJECT_0 && !::ReleaseMutex(probe.mutex)) probe.result=WAIT_FAILED;
    return 0;
}
static DWORD probe(HANDLE mutex) {
    Probe data{mutex}; auto thread=::CreateThread(nullptr,0,probe_thread,&data,0,nullptr);
    if(!thread || ::WaitForSingleObject(thread,10000)!=WAIT_OBJECT_0 || !::CloseHandle(thread))
        throw std::runtime_error("native mutex probe thread failed");
    return data.result;
}
int main() {
 try {
    Win32ProcessMemory memory;
    memory.map_bytes("stack",0x50000000,4096,true,true);
    memory.map_bytes("names",0x50010000,4096,true,true);
    memory.map_bytes("attributes",0x50020000,64,true,true);
    auto put=[&](std::uint32_t address,const wchar_t* value) {
        unsigned i=0; do { memory.store(address+2*i,std::uint16_t(value[i]),16); } while(value[i++]);
    };
    wchar_t name[128],collision[128];
    std::swprintf(name,128,L"Local\\DAODecomp_mutex_%lu",::GetCurrentProcessId());
    std::swprintf(collision,128,L"Local\\DAODecomp_mutex_collision_%lu",::GetCurrentProcessId());
    put(0x50010000,name); put(0x50010200,collision);
    memory.store(0x50020000,12,32); memory.store(0x50020004,0,32); memory.store(0x50020008,1,32);
    memory.seal();
    auto invoke=[&](const char* symbol,std::initializer_list<std::uint32_t> args) {
        sharp_retro::State s; s.gpr[4]=0x50000800;
        for(unsigned reg:{3u,5u,6u,7u}) s.gpr[reg]=0x13570000u+reg;
        memory.store(s.gpr[4],0x12345678,32); unsigned index=1;
        for(auto value:args) memory.store(s.gpr[4]+4u*index++,value,32);
        invoke_native_import({0,"KERNEL32.dll",symbol,false},s,memory);
        if(s.pc!=0x12345678 || s.gpr[4]!=0x50000800+4u*index || !(s.defined_gpr&1) || (s.defined_gpr&6) ||
           s.gpr[3]!=0x13570003 || s.gpr[5]!=0x13570005 || s.gpr[6]!=0x13570006 || s.gpr[7]!=0x13570007)
            throw std::runtime_error("kernel-object ABI mismatch");
        return std::uint32_t(s.gpr[0]);
    };
    auto token=invoke("CreateMutexW",{0,1,0x50010000});
    if(!token || !native_kernel_handles.contains(token)) return 1;
    auto native=reinterpret_cast<HANDLE>(std::uintptr_t(token));
    if(probe(native)!=WAIT_TIMEOUT || invoke("WaitForSingleObject",{token,0})!=WAIT_OBJECT_0 ||
       !invoke("ReleaseMutex",{token}) || probe(native)!=WAIT_TIMEOUT || !invoke("ReleaseMutex",{token}) ||
       probe(native)!=WAIT_OBJECT_0) return 2;
    auto duplicate=invoke("CreateMutexW",{0,1,0x50010000});
    if(!duplicate || duplicate==token || native_error_context.value!=ERROR_ALREADY_EXISTS ||
       probe(native)!=WAIT_OBJECT_0) return 3; // Existing-object initial ownership is ignored.
    if(!invoke("CloseHandle",{duplicate}) || !invoke("CloseHandle",{token}) || !native_kernel_handles.empty()) return 4;
    bool closed_refused=false;
    try { (void)invoke("WaitForSingleObject",{token,0}); } catch(const std::runtime_error&) { closed_refused=true; }
    if(!closed_refused) return 5;
    auto inherited=invoke("CreateMutexW",{0x50020000,0,0}); DWORD flags=0;
    if(!inherited || !::GetHandleInformation(reinterpret_cast<HANDLE>(std::uintptr_t(inherited)),&flags) || !(flags&HANDLE_FLAG_INHERIT)) return 6;
    ::SetLastError(0x13579); auto expected=::ReleaseMutex(reinterpret_cast<HANDLE>(std::uintptr_t(inherited))); auto expected_error=::GetLastError();
    native_error_context.value=0x13579;
    if(invoke("ReleaseMutex",{inherited})!=std::uint32_t(expected) || expected || native_error_context.value!=expected_error) return 7;
    if(!invoke("CloseHandle",{inherited})) return 8;
    auto event=::CreateEventW(nullptr,FALSE,FALSE,collision);
    if(!event) return 9;
    ::SetLastError(0x2468); auto expected_mutex=::CreateMutexW(nullptr,FALSE,collision); expected_error=::GetLastError();
    native_error_context.value=0x2468;
    auto failed=invoke("CreateMutexW",{0,0,0x50010200});
    if(expected_mutex || failed || native_error_context.value!=expected_error || !native_kernel_handles.empty() || !::CloseHandle(event)) return 10;
    unsigned invalid_inputs=0;
    memory.store(0x50020004,0x50020100,32); // Nonnull descriptors remain unsupported.
    const std::array<std::uint32_t,3> bad_arguments[]={{0x50020000,0,0},{0x50030000,0,0},{0,0,0x50030000}};
    for(auto args:bad_arguments) {
        try { (void)invoke("CreateMutexW",{args[0],args[1],args[2]}); }
        catch(const std::runtime_error&) { ++invalid_inputs; }
    }
    if(invalid_inputs!=3 || !native_kernel_handles.empty()) return 11;
    std::printf("{\"recursive_ownership\":true,\"cross_thread_timeout_and_acquire\":true,\"existing_name_error\":%u,\"default_security_inheritance\":true,\"native_failed_create_error\":%u,\"release_error_matches_native\":true,\"closed_handle_refused\":true,\"invalid_inputs_refused\":%u}\n",unsigned(ERROR_ALREADY_EXISTS),unsigned(expected_error),invalid_inputs);
 } catch(const std::exception& e) { std::fprintf(stderr,"%s\n",e.what()); return 20; }
}

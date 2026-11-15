// Existing-key/absent-key native registry boundary debugging; creates no keys.
#include "native_imports.hpp"
#include "win32_memory.hpp"
#include <cstdio>
using namespace recomp_generated;
int main() {
 try {
    Win32ProcessMemory memory;
    memory.map_bytes("stack",0x50000000,4096,true,true);
    memory.map_bytes("names",0x50010000,4096,true,true);
    memory.map_bytes("output",0x50020000,64,true,true);
    memory.map_bytes("readonly",0x50030000,4,true,false);
    auto put=[&](std::uint32_t address,const wchar_t* name) {
        unsigned i=0; do { memory.store(address+2*i,std::uint16_t(name[i]),16); } while(name[i++]);
    };
    wchar_t missing[128]; std::swprintf(missing,128,L"Software\\__DAODecomp_missing_%lu",::GetCurrentProcessId());
    put(0x50010000,L"Software"); put(0x50010040,L""); put(0x50010100,missing); memory.seal();
    auto invoke=[&](const char* symbol,std::initializer_list<std::uint32_t> args) {
        sharp_retro::State state; state.gpr[4]=0x50000800;
        for(unsigned reg:{3u,5u,6u,7u}) state.gpr[reg]=0x12345000u+reg;
        memory.store(state.gpr[4],0x12345678,32); unsigned index=1;
        for(auto argument:args) memory.store(state.gpr[4]+4u*index++,argument,32);
        invoke_native_import({0,"ADVAPI32.dll",symbol,false},state,memory);
        if(state.pc!=0x12345678 || state.gpr[4]!=0x50000800+4u*index || !(state.defined_gpr&1) ||
           (state.defined_gpr&6) || state.gpr[3]!=0x12345003 || state.gpr[5]!=0x12345005 ||
           state.gpr[6]!=0x12345006 || state.gpr[7]!=0x12345007) throw std::runtime_error("registry ABI mismatch");
        return std::uint32_t(state.gpr[0]);
    };
    constexpr std::uint32_t root=0x80000001u,output=0x50020000u;
    HKEY expected=nullptr;
    auto native_status=::RegOpenKeyExW(HKEY_CURRENT_USER,L"Software",0,KEY_READ,&expected);
    memory.store_unknown(output,0,64);
    auto status=invoke("RegOpenKeyExW",{root,0x50010000,0,KEY_READ,output});
    if(native_status!=ERROR_SUCCESS || status!=std::uint32_t(native_status)) return 1;
    auto key=std::uint32_t(memory.load(output,32));
    if(!native_open_registry_keys.contains(key) || ::RegCloseKey(expected)!=ERROR_SUCCESS || invoke("RegCloseKey",{key})!=ERROR_SUCCESS ||
       native_open_registry_keys.contains(key)) return 2;
    bool closed_refused=false;
    try { (void)invoke("RegCloseKey",{key}); } catch(const std::runtime_error&) { closed_refused=true; }
    if(!closed_refused) return 3;
    for(auto name:{0u,0x50010040u}) {
        expected=nullptr; native_status=::RegOpenKeyExW(HKEY_CURRENT_USER,name ? L"" : nullptr,0,KEY_READ,&expected);
        status=invoke("RegOpenKeyExW",{root,name,0,KEY_READ,output});
        if(status!=std::uint32_t(native_status) || status!=ERROR_SUCCESS || memory.load(output,32)!=reinterpret_cast<std::uintptr_t>(expected) ||
           memory.load(output,32)!=root || !native_open_registry_keys.empty()) return 4;
        if(invoke("RegCloseKey",{root})!=std::uint32_t(::RegCloseKey(expected))) return 5;
    }
    ::SetLastError(0x13579); expected=reinterpret_cast<HKEY>(std::uintptr_t(0x12345678));
    native_status=::RegOpenKeyExW(HKEY_CURRENT_USER,missing,0,KEY_READ,&expected); auto expected_error=::GetLastError();
    native_error_context.value=0x13579;
    status=invoke("RegOpenKeyExW",{root,0x50010100,0,KEY_READ,output});
    if(status!=std::uint32_t(native_status) || status==ERROR_SUCCESS || !native_open_registry_keys.empty() || native_error_context.value!=expected_error) return 6;
    bool unknown=false,tail_unknown=false;
    try { (void)memory.load(output,32); } catch(const sharp_retro::UnknownMemoryRead&) { unknown=true; }
    try { (void)memory.load(output+4,32); } catch(const sharp_retro::UnknownMemoryRead&) { tail_unknown=true; }
    if(!unknown || !tail_unknown) return 7;
    unsigned bad_outputs=0;
    for(auto address:{0x50030000u,0x50040000u}) {
        try { (void)invoke("RegOpenKeyExW",{root,0x50010000,0,KEY_READ,address}); }
        catch(const std::runtime_error&) { ++bad_outputs; }
    }
    if(bad_outputs!=2 || !native_open_registry_keys.empty()) return 8;
    std::printf("{\"successful_open_close\":true,\"predefined_alias_cases\":2,\"missing_key_status\":%u,\"failed_output_unknown\":true,\"output_tail_unknown\":true,\"closed_handle_refused\":true,\"invalid_outputs_refused\":%u,\"last_error_matches_native\":true}\n",status,bad_outputs);
 } catch(const std::exception& error) { std::fprintf(stderr,"%s\n",error.what()); return 20; }
}

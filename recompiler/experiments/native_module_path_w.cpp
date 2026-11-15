// Measured Windows x86 UTF16 module-path boundary; no game scenario acceptance.
#include "native_imports.hpp"
#include "win32_memory.hpp"
#include <cstdio>
#include <vector>
using namespace recomp_generated;
int main() {
 try {
    Win32ProcessMemory memory;memory.map_bytes("stack",0x50000000,4096,true,true);memory.map_bytes("output",0x50010000,2048,true,true);
    memory.map_bytes("readonly",0x50020000,4096,true,false);memory.seal();
    std::vector<wchar_t> actual(32768);auto count=::GetModuleFileNameW(nullptr,actual.data(),DWORD(actual.size()));
    if(!count || count>=actual.size())return 1;logical_main_module_path_w.assign(actual.data(),count);
    auto invoke=[&](std::uint32_t module,std::uint32_t destination,std::uint32_t capacity) {
        sharp_retro::State s;s.gpr[4]=0x50000800;
        for(unsigned reg:{3u,5u,6u,7u})s.gpr[reg]=0x12340000u+reg;
        memory.store(0x50000800,0x12345678,32);memory.store(0x50000804,module,32);memory.store(0x50000808,destination,32);memory.store(0x5000080c,capacity,32);
        invoke_native_import({0,"KERNEL32.dll","GetModuleFileNameW",false},s,memory);
        if(s.pc!=0x12345678 || s.gpr[4]!=0x50000810 || !(s.defined_gpr&1) || (s.defined_gpr&6) ||
           s.gpr[3]!=0x12340003 || s.gpr[5]!=0x12340005 || s.gpr[6]!=0x12340006 || s.gpr[7]!=0x12340007)
            throw std::runtime_error("UTF16 module path ABI mismatch");
        return std::uint32_t(s.gpr[0]);
    };
    auto kernel=::GetModuleHandleW(L"kernel32.dll");register_native_module(std::uint32_t(reinterpret_cast<std::uintptr_t>(kernel)),"kernel32.dll");
    unsigned cases=0;
    for(unsigned kind=0;kind<3;kind++)for(DWORD capacity:std::array<DWORD,6>{0,1,count-1,count,count+1,512}) {
        std::vector<wchar_t> expected(520,wchar_t(0x5a5a));for(unsigned i=0;i<520;i++)memory.store(0x50010000+i*2,0x5a5a,16);
        auto native=kind==2 ? kernel : nullptr;auto token=kind==2 ? std::uint32_t(reinterpret_cast<std::uintptr_t>(kernel)) : kind==1 ? 0x400000u : 0u;
        ::SetLastError(0x13579);auto expected_result=::GetModuleFileNameW(native,expected.data(),capacity);auto expected_error=::GetLastError();native_error_context.value=0x13579;
        auto result=invoke(token,0x50010000,capacity);
        if(result!=expected_result || native_error_context.value!=expected_error)throw std::runtime_error("UTF16 path native return/error mismatch");
        for(unsigned i=0;i<520;i++)if(memory.load(0x50010000+i*2,16)!=std::uint16_t(expected[i]))throw std::runtime_error("UTF16 path bytes/tail differ from native");
        ++cases;
    }
    logical_main_module_path_w=L"Z:\\Ω\\\U0001f409\\DAOrigins.exe";
    if(invoke(0,0x50010000,512)!=logical_main_module_path_w.size())return 2;
    for(unsigned i=0;i<=logical_main_module_path_w.size();i++)if(memory.load(0x50010000+i*2,16)!=std::uint16_t(logical_main_module_path_w.c_str()[i]))return 3;
    // The capacity counts UTF16 code units, including an incomplete surrogate
    // pair at truncation. Determine only this host's termination convention.
    wchar_t probe[7];std::fill(std::begin(probe),std::end(probe),wchar_t(0x5a5a));(void)::GetModuleFileNameW(nullptr,probe,7);bool terminates=probe[6]==0;
    if(invoke(0,0x50010000,7)!=7)return 4;
    const std::uint16_t truncated[]={0x5a,0x3a,0x5c,0x3a9,0x5c,0xd83d,0xdc09};
    for(unsigned i=0;i<7;i++)if(memory.load(0x50010000+i*2,16)!=(terminates && i==6 ? 0 : truncated[i]))return 5;
    unsigned refused=0;
    for(auto arguments:std::array<std::array<std::uint32_t,3>,3>{{{0,0x50020000,1},{0x12340,0x50010000,512},{0,0x50010000,0x80000001}}}) {
        try{(void)invoke(arguments[0],arguments[1],arguments[2]);}catch(const std::runtime_error&){++refused;}
    }
    std::printf("{\"native_UTF16_path_cases\":%u,\"unicode_full_path\":true,\"surrogate_truncation\":true,\"refusal_guards\":%u}\n",cases,refused);return refused==3 ? 0 : 6;
 }catch(const std::exception& e){std::fprintf(stderr,"UTF16 module path: %s\n",e.what());return 7;}
}

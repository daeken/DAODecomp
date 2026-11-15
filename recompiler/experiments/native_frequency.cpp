// Actual native frequency transport, not a deterministic game timing fixture.
#include "native_imports.hpp"
#include "win32_memory.hpp"
#include <cstdio>
using namespace recomp_generated;
int main(){try{
    Win32ProcessMemory memory;memory.map_bytes("stack",0x50000000,4096,true,true);memory.map_bytes("output",0x50010000,4096,true,true);memory.seal();
    auto invoke=[&](std::uint32_t destination){
        sharp_retro::State s;s.gpr[4]=0x50000800;for(unsigned reg:{3u,5u,6u,7u})s.gpr[reg]=0x12340000u+reg;
        memory.store(0x50000800,0x12345678,32);memory.store(0x50000804,destination,32);
        invoke_native_import({0,"KERNEL32.dll","QueryPerformanceFrequency",false},s,memory);
        if(s.pc!=0x12345678 || s.gpr[4]!=0x50000808 || !(s.defined_gpr&1) || (s.defined_gpr&6) || s.gpr[3]!=0x12340003 || s.gpr[5]!=0x12340005 || s.gpr[6]!=0x12340006 || s.gpr[7]!=0x12340007)throw std::runtime_error("frequency ABI mismatch");return std::uint32_t(s.gpr[0]);
    };
    LARGE_INTEGER expected;::SetLastError(0x13579);auto direct=::QueryPerformanceFrequency(&expected);auto error=::GetLastError();
    memory.store_unknown(0x50010000,0x5151515151515151ULL,64);memory.store(0x50010008,0x12345678,32);native_error_context.value=0x13579;
    if(invoke(0x50010000)!=std::uint32_t(direct) || native_error_context.value!=error || !direct || memory.load(0x50010000,64)!=std::uint64_t(expected.QuadPart) || memory.load(0x50010008,32)!=0x12345678)return 1;
    unsigned refused=0;for(auto pointer:{0u,0x50010ffcu})try{(void)invoke(pointer);}catch(const std::runtime_error&){++refused;}
    std::printf("{\"native_frequency_cases\":1,\"frequency\":%lld,\"output_known\":true,\"neighbor_preserved\":true,\"refusal_guards\":%u}\n",static_cast<long long>(expected.QuadPart),refused);return refused!=2 ? 2:0;
}catch(const std::exception& e){std::fprintf(stderr,"frequency debug: %s\n",e.what());return 3;}}

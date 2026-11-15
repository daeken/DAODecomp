// Debug transport for the actually reached WINMM!timeGetTime boundary.
#include "native_imports.hpp"
#include "image_memory.hpp"
#include <cstdio>
using namespace recomp_generated;
static bool same_fp(const sharp_retro::State& a,const sharp_retro::State& b) {
    return a.x87_control==b.x87_control && a.x87_status==b.x87_status && a.x87_tag==b.x87_tag && a.x87_st==b.x87_st && a.mxcsr==b.mxcsr;
}
int main() {
 try {
    ImageMemory memory;memory.map_bytes("stack",0x8000,0x1000,true,true);memory.seal();memory.store(0x8800,0x12345678,32);
    sharp_retro::State host;capture_native_fp(host);native_floating_bridge_enabled=true;
    unsigned cases=0;
    for(unsigned i=0;i<32;i++) {
        auto state=host;state.gpr[4]=0x8800;
        for(unsigned reg:{3u,5u,6u,7u}) state.gpr[reg]=0x12340000u+reg;
        auto before=::timeGetTime();::SetLastError(0x13570000u+i);(void)::timeGetTime();auto error=::GetLastError();
        native_error_context.value=0x13570000u+i;
        invoke_native_import({0,"WINMM.dll","timeGetTime",false},state,memory);
        auto actual_error=native_error_context.value;auto after=::timeGetTime();
        auto value=std::uint32_t(state.gpr[0]);
        if(std::uint32_t(value-before)>std::uint32_t(after-before) || actual_error!=error || state.pc!=0x12345678 || state.gpr[4]!=0x8804 ||
           !(state.defined_gpr&1) || (state.defined_gpr&6) || state.defined_flags!=(std::uint64_t(1)<<10) ||
           state.gpr[3]!=0x12340003 || state.gpr[5]!=0x12340005 || state.gpr[6]!=0x12340006 || state.gpr[7]!=0x12340007 ||
           memory.load(0x8800,32)!=0x12345678) throw std::runtime_error("timer result/ABI/error transport mismatch");
        ++cases;
    }
    unsigned refused=0;
    for(unsigned mode=0;mode<2;mode++) {
        auto state=host;state.gpr[4]=0x8800;if(mode==0)state.defined_flags=0;
        try { invoke_native_import({0,"WINMM.dll",mode ? "GetTickCount" : "timeGetTime",false},state,memory); }
        catch(const std::runtime_error&) { if(state.gpr[4]==0x8800 && state.pc==host.pc)++refused; }
    }
    sharp_retro::State after;capture_native_fp(after);bool restored=same_fp(host,after);
    std::printf("{\"native_clock_bracket_cases\":%u,\"refusal_guards\":%u,\"host_fp_restored\":%s}\n",cases,refused,restored ? "true" : "false");
    return cases!=32 || refused!=2 || !restored ? 1 : 0;
 } catch(const std::exception& e) { std::fprintf(stderr,"timer debug: %s\n",e.what());return 2; }
}

// Bounded bit-copy debugging against actual x86 MOVAPS; no game-equivalence claim.
#include "functions.hpp"
#include "image_memory.hpp"
#include <array>
#include <cstdio>
#include <cstring>
int main() {
    const std::array<std::array<std::uint32_t,4>,4> patterns{{
        {{0,0,0,0}},{{0xffffffffu,0xffffffffu,0xffffffffu,0xffffffffu}},
        {{1,0x80000000u,0x7f800001u,0xffc00001u}},{{0x13579bdfu,0x2468ace0u,0xdeadbeefu,0xcafebabeu}}
    }};
    unsigned cases=0;
    for(const auto& pattern:patterns) for(unsigned rotation=0;rotation<4;rotation++) {
        alignas(16) std::uint32_t source[4],destination[4]{};
        for(unsigned i=0;i<4;i++) source[i]=pattern[(i+rotation)%4];
        std::uint32_t before,after,mx_before,mx_after;
        asm volatile("pushfl\n\tpopl %[before]\n\tstmxcsr %[mx_before]\n\tmovaps (%[source]),%%xmm2\n\tmovaps %%xmm2,(%[destination])\n\tstmxcsr %[mx_after]\n\tpushfl\n\tpopl %[after]"
                     : [before] "=m" (before), [after] "=m" (after), [mx_before] "=m" (mx_before), [mx_after] "=m" (mx_after)
                     : [source] "r" (source), [destination] "r" (destination) : "xmm2","memory");
        if(before!=after || mx_before!=mx_after || std::memcmp(source,destination,16)) return 1;
        recomp_generated::ImageMemory memory; memory.map_bytes("ram",0x8000,4096,true,true); memory.seal();
        for(unsigned i=0;i<4;i++) memory.store(0x8000+i*4,source[i],32);
        memory.store(0x8800,0x12345678,32);
        sharp_retro::State state; state.gpr[0]=0x8000; state.gpr[1]=0x8100; state.gpr[4]=0x8800;
        state.flags=0x200ad7; state.mxcsr=0x1fa0;
        std::uint64_t budget=100;
        if(recomp_generated::execute_guest(0x401000,0x12345678,state,memory,budget)!=sharp_retro::Exit::returned ||
           !(state.defined_xmm&4) || state.flags!=0x200ad7 || state.mxcsr!=0x1fa0 || state.gpr[4]!=0x8804) return 2;
        for(unsigned i=0;i<4;i++) if(memory.load(0x8100+i*4,32)!=destination[i]) return 3;
        ++cases;
    }
    std::printf("{\"native_movaps_copy_cases\":%u,\"mismatches\":0,\"native_flags_preserved\":true,\"native_mxcsr_preserved\":true,\"candidate_flags_preserved\":true,\"candidate_mxcsr_preserved\":true}\n",cases);
}

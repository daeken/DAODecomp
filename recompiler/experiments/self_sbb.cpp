// Compare the reached SBB EDX,EDX idiom with compiled native x86 instructions.
#include "CppRuntime.hpp"
#include <cstdio>
#include <cstdint>
int main() {
    unsigned cases=0;
    for(auto input:{0u,1u,15u,16u,127u,128u,255u,256u,0x7fffffffu,0x80000000u,0xfffffffeu,0xffffffffu})
    for(unsigned carry=0;carry<2;carry++) for(unsigned known=0;known<2;known++) {
        std::uint32_t expected,flags;
        asm volatile("movl %[input],%%edx\n\tbtl $0,%[carry]\n\tsbbl %%edx,%%edx\n\tmovl %%edx,%[result]\n\tpushfl\n\tpopl %[flags]"
                     : [result] "=&r" (expected), [flags] "=&r" (flags)
                     : [input] "r" (input), [carry] "r" (carry) : "edx","cc");
        sharp_retro::State state; state.gpr[2]=input; state.flags=0x200ad6u|carry; state.defined_flags=1;
        if(!known) sharp_retro::invalidate_gprs(state,4);
        sharp_retro::sbb_self32(state,2);
        if(sharp_retro::read_gpr(state,2)!=expected || (state.flags&0x8d5)!=(flags&0x8d5) ||
           (state.defined_flags&0x8d5)!=0x8d5 || (state.flags&~0x8d5ULL)!=(0x200ad6u&~0x8d5ULL)) return 1;
        ++cases;
    }
    sharp_retro::State unknown; sharp_retro::invalidate_gprs(unknown,4); unknown.defined_flags=0;
    bool refused=false;
    try { sharp_retro::sbb_self32(unknown,2); } catch(const std::runtime_error&) { refused=true; }
    if(!refused || (unknown.defined_gpr&4)) return 2;
    std::printf("{\"native_instruction_cases\":%u,\"mismatches\":0,\"unknown_input_register_supported\":true,\"unknown_carry_refused\":true}\n",cases);
}

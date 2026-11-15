// Bounded OR-immediate knownness/flag debugging, not game-equivalence evidence.
#include "functions.hpp"
#include "image_memory.hpp"
#include <cstdio>
int main() {
    unsigned cases=0;
    for(auto input:{0u,1u,0x7fffffffu,0x80000000u,0xffffffffu,0xdeadbeefu,0x55555555u,0xaaaaaaaau})
    for(unsigned kind=0;kind<3;kind++) {
        std::uint32_t expected,flags;
        if(kind==1) asm volatile("movl %[input],%%edx\n\torl $0xff00,%%edx\n\tmovl %%edx,%[result]\n\tpushfl\n\tpopl %[flags]"
                                : [result] "=&r" (expected), [flags] "=&r" (flags) : [input] "r" (input) : "edx","cc");
        else asm volatile("movl %[input],%%edx\n\torl $-1,%%edx\n\tmovl %%edx,%[result]\n\tpushfl\n\tpopl %[flags]"
                          : [result] "=&r" (expected), [flags] "=&r" (flags) : [input] "r" (input) : "edx","cc");
        recomp_generated::ImageMemory memory; memory.map_bytes("stack",0x8000,4096,true,true); memory.seal();
        memory.store(0x8800,0x12345678,32);
        sharp_retro::State state; state.gpr[4]=0x8800; state.flags=0x200ad7;
        unsigned reg=kind==2 ? 0 : 2;
        sharp_retro::scalar_gpr32(state,reg,{input,kind==1 ? 0xffff00ffu : 0u,{}});
        std::uint64_t budget=100;
        if(recomp_generated::execute_guest(0x401000+kind*64,0x12345678,state,memory,budget)!=sharp_retro::Exit::returned ||
           sharp_retro::read_gpr(state,reg)!=expected || (state.flags&0x8c5)!=(flags&0x8c5) ||
           (state.defined_flags&0x8c5)!=0x8c5 || (state.defined_flags&16) || state.gpr[4]!=0x8804) return 1;
        ++cases;
    }
    std::printf("{\"native_or_immediate_cases\":%u,\"mismatches\":0,\"forced_unknown_bits_supported\":true,\"defined_arithmetic_flags_match\":true,\"auxiliary_flag_unknown\":true}\n",cases);
}

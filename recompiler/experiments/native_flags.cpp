// Debug the native Umbra CPU probe: compare concrete XOR flag transport with
// actual x86 XOR/PUSHFD observations. This is not whole-function acceptance.
#include "runtime.hpp"
#include <array>
#include <cstdio>
#include <stdexcept>
using namespace sharp_retro;
#define REFERENCE(name,operation,suffix,operands) \
extern "C" __attribute__((naked)) unsigned name(unsigned,unsigned,unsigned) { \
    asm volatile("pushfl; movl 8(%esp),%eax; movl 12(%esp),%edx; pushl 16(%esp); popfl; " operation suffix " " operands "; pushfl; popl %eax; popfl; ret"); \
}
#define REFERENCES(name,operation) \
REFERENCE(name##8,operation,"b","%dl,%al") \
REFERENCE(name##16,operation,"w","%dx,%ax") \
REFERENCE(name##32,operation,"l","%edx,%eax")
REFERENCES(and_ref,"and")
REFERENCES(or_ref,"or")
REFERENCES(xor_ref,"xor")
REFERENCES(test_ref,"test")
REFERENCE(imul_ref16,"imul","w","%dx,%ax")
REFERENCE(imul_ref32,"imul","l","%edx,%eax")
REFERENCE(imul_imm_ref16,"imul","w","$56,%ax,%ax")
REFERENCE(imul_imm_ref32,"imul","l","$56,%eax,%eax")
REFERENCE(mul_ref8,"mul","b","%dl")
REFERENCE(mul_ref16,"mul","w","%dx")
REFERENCE(mul_ref32,"mul","l","%edx")
REFERENCE(imul_one_ref8,"imul","b","%dl")
REFERENCE(imul_one_ref16,"imul","w","%dx")
REFERENCE(imul_one_ref32,"imul","l","%edx")
#define SHIFT_REFERENCE(name,operation,suffix,operand) \
extern "C" __attribute__((naked)) unsigned name(unsigned,unsigned,unsigned) { \
    asm volatile("pushfl; movl 8(%esp),%eax; movl 12(%esp),%ecx; pushl 16(%esp); popfl; " operation suffix " %cl," operand "; pushfl; popl %eax; popfl; ret"); \
}
#define SHIFT_REFERENCES(name,operation) \
SHIFT_REFERENCE(name##8,operation,"b","%al") \
SHIFT_REFERENCE(name##16,operation,"w","%ax") \
SHIFT_REFERENCE(name##32,operation,"l","%eax")
SHIFT_REFERENCES(shl_ref,"shl")
SHIFT_REFERENCES(shr_ref,"shr")
SHIFT_REFERENCES(sar_ref,"sar")
#define DIVIDE_REFERENCE(name,operation,suffix,high,operand) \
extern "C" __attribute__((naked)) unsigned name(std::uint64_t,unsigned,unsigned) { \
    asm volatile("pushfl; movl 8(%esp),%eax; " high "; movl 16(%esp),%ecx; pushl 20(%esp); popfl; " operation suffix " " operand "; pushfl; popl %eax; popfl; ret"); \
}
DIVIDE_REFERENCE(div_ref8,"div","b","nop","%cl")
DIVIDE_REFERENCE(div_ref16,"div","w","movl %eax,%edx; shrl $16,%edx","%cx")
DIVIDE_REFERENCE(div_ref32,"div","l","movl 12(%esp),%edx","%ecx")
DIVIDE_REFERENCE(idiv_ref8,"idiv","b","nop","%cl")
DIVIDE_REFERENCE(idiv_ref16,"idiv","w","movl %eax,%edx; shrl $16,%edx","%cx")
DIVIDE_REFERENCE(idiv_ref32,"idiv","l","movl 12(%esp),%edx","%ecx")
#undef DIVIDE_REFERENCE
#undef SHIFT_REFERENCES
#undef SHIFT_REFERENCE
#undef REFERENCES
#undef REFERENCE
int main() {
    unsigned cases=0;
    for(auto left:std::array<unsigned,8>{0,1,15,16,255,0x7fffffff,0x80000000,0xffffffff})
    for(auto right:std::array<unsigned,8>{0,1,15,16,255,0x7fffffff,0x80000000,0xffffffff}) {
        unsigned actual,flags;
        asm volatile("movl %2,%0; xorl %3,%0; pushfl; popl %1" : "=&r"(actual),"=r"(flags) : "r"(left),"r"(right) : "cc","memory");
        for(unsigned kind=0;kind<2;++kind) {
            State state;state.flags=0x200ad7;state.defined_flags=0xffffffffu;
            state.gpr[0]=left;state.gpr[1]=right;
            if(kind) xor_scalar32(state,0,right); else xor_gprs32(state,0,1);
            if(state.gpr[0]!=actual || (state.flags&0x8d5)!=(flags&0x8d5) ||
               (state.defined_flags&0x8d5)!=0x8d5 || (state.flags&~0x8d5ULL)!=(0x200ad7&~0x8d5ULL)) return 1;
            ++cases;
        }
    }
    State symbolic;invalidate_gprs(symbolic,3);xor_gprs32(symbolic,0,1);
    if(symbolic.defined_flags&16) return 2;
    using Reference=unsigned(*)(unsigned,unsigned,unsigned);
    const Reference reference[4][3]={{and_ref8,and_ref16,and_ref32},{or_ref8,or_ref16,or_ref32},
                                   {xor_ref8,xor_ref16,xor_ref32},{test_ref8,test_ref16,test_ref32}};
    unsigned logical_cases=0;
    for(unsigned operation=0;operation<4;++operation) for(unsigned size=0;size<3;++size)
    for(unsigned initial:{0x202u,0x246u,0xad7u,0x8d7u})
    for(auto left:std::array<unsigned,8>{0,1,15,16,255,0x7fffffff,0x80000000,0xffffffff})
    for(auto right:std::array<unsigned,8>{0,1,15,16,255,0x7fffffff,0x80000000,0xffffffff}) {
        State state;state.flags=initial;state.defined_flags=0xffffffffu;
        native_logic_flags(state,operation,8u<<size,left,right);
        auto expected=reference[operation][size](left,right,(initial&0x8d5u)|0x202u);
        if((state.flags&0x8d5)!=(expected&0x8d5) || (state.defined_flags&0x8d5)!=0x8d5 ||
           (state.flags&~0x8d5ULL)!=(initial&~0x8d5ULL)) return 3;
        ++logical_cases;
    }
    const Reference shifts[3][3]={{shl_ref8,shl_ref16,shl_ref32},{shr_ref8,shr_ref16,shr_ref32},{sar_ref8,sar_ref16,sar_ref32}};
    unsigned shift_cases=0;
    for(unsigned operation=0;operation<3;++operation) for(unsigned size=0;size<3;++size)
    for(unsigned initial:{0x202u,0x246u,0xad7u,0x8d7u})
    for(auto left:std::array<unsigned,8>{0,1,15,16,255,0x7fffffff,0x80000000,0xffffffff})
    for(unsigned count:{0u,1u,2u,7u,8u,15u,16u,31u,32u,33u,63u,255u}) {
        State state;state.flags=initial;state.defined_flags=0xffffffffu;
        native_logic_flags(state,operation+4,8u<<size,left,count);
        auto expected=shifts[operation][size](left,count,(initial&0x8d5u)|0x202u);
        if((state.flags&0x8d5)!=(expected&0x8d5) || (state.defined_flags&0x8d5)!=0x8d5 ||
           (state.flags&~0x8d5ULL)!=(initial&~0x8d5ULL)) return 4;
        ++shift_cases;
    }
    const Reference multiply[2]={imul_ref16,imul_ref32},immediate[2]={imul_imm_ref16,imul_imm_ref32};
    unsigned multiply_cases=0;
    for(unsigned size=0;size<2;++size) for(unsigned initial:{0x202u,0x246u,0xad7u,0x8d7u})
    for(unsigned left:{0u,1u,0x7fffu,0x8000u,0xffffu,0x7fffffffu,0x80000000u,0xffffffffu}) {
        for(unsigned right:{0u,1u,2u,56u,0x8000u,0xffffu,0x80000000u,0xffffffffu}) {
            State state;state.flags=initial;state.defined_flags=0xffffffffu;
            native_logic_flags(state,7,16u<<size,left,right);
            auto expected=multiply[size](left,right,(initial&0x8d5u)|0x202u);
            if((state.flags&0x8d5)!=(expected&0x8d5) || (state.defined_flags&0x8d5)!=0x8d5 ||
               (state.flags&~0x8d5ULL)!=(initial&~0x8d5ULL)) return 5;
            ++multiply_cases;
        }
        State state;state.flags=initial;state.defined_flags=0xffffffffu;
        native_logic_flags(state,7,16u<<size,left,56);
        auto expected=immediate[size](left,56,(initial&0x8d5u)|0x202u);
        if((state.flags&0x8d5)!=(expected&0x8d5)) return 6;
        ++multiply_cases;
    }
    unsigned error,after;asm volatile("movl %%fs:0x34,%0":"=r"(error));
    unsigned marker=0x12345678;asm volatile("movl %0,%%fs:0x34"::"r"(marker):"memory");
    State trace;trace.pc=0x1234;trace.flag_origins[4]=fresh_unknown_flag_origin(trace,4);
    auto producer=native_undefined_flag_pc(trace,4);asm volatile("movl %%fs:0x34,%0":"=r"(after));
    asm volatile("movl %0,%%fs:0x34"::"r"(error):"memory");
    if(after!=marker || producer!=trace.pc) return 7;
    const Reference implicit[2][3]={{mul_ref8,mul_ref16,mul_ref32},{imul_one_ref8,imul_one_ref16,imul_one_ref32}};
    unsigned implicit_cases=0;
    for(unsigned operation=0;operation<2;++operation) for(unsigned size=0;size<3;++size)
    for(unsigned initial:{0x202u,0x246u,0xad7u,0x8d7u})
    for(unsigned left:{0u,1u,0x7fu,0x80u,0x7fffu,0x8000u,0x7fffffffu,0x80000000u,0xaaaaaaabu,0xffffffffu})
    for(unsigned right:{0u,1u,2u,0x7fu,0x80u,0x7fffu,0x8000u,0x7fffffffu,0x80000000u,0xffffffffu}) {
        State state;state.flags=initial;state.defined_flags=0xffffffffu;
        native_logic_flags(state,operation+8,8u<<size,left,right);
        auto expected=implicit[operation][size](left,right,(initial&0x8d5u)|0x202u);
        if((state.flags&0x8d5)!=(expected&0x8d5) || (state.defined_flags&0x8d5)!=0x8d5 ||
           (state.flags&~0x8d5ULL)!=(initial&~0x8d5ULL)) return 8;
        ++implicit_cases;
    }
    using DivideReference=unsigned(*)(std::uint64_t,unsigned,unsigned);
    const DivideReference divide[3]={div_ref8,div_ref16,div_ref32},signed_divide[3]={idiv_ref8,idiv_ref16,idiv_ref32};
    unsigned divide_cases=0,divide_guards=0;
    for(unsigned size=0;size<3;++size) {
        unsigned width=8u<<size;auto mask=(std::uint64_t(1)<<width)-1;
        for(unsigned initial:{0x202u,0x246u,0xad7u,0x8d7u}) {
            for(auto divisor:{1ULL,2ULL,3ULL,7ULL,(unsigned long long)(mask/2),(unsigned long long)mask})
            for(auto quotient:{0ULL,1ULL,2ULL,(unsigned long long)(mask/2),(unsigned long long)mask})
            for(auto remainder:{0ULL,divisor-1}) {
                auto numerator=quotient*divisor+remainder;
                State state;state.flags=initial;state.defined_flags=0xffffffffu;
                native_logic_flags(state,10,width,numerator,divisor);
                auto expected=divide[size](numerator,unsigned(divisor),(initial&0x8d5u)|0x202u);
                if((state.flags&0x8d5)!=(expected&0x8d5) || (state.defined_flags&0x8d5)!=0x8d5) return 9;
                ++divide_cases;
            }
            auto limit=std::int64_t(1)<<(width-1);
            for(auto divisor:std::array<std::int64_t,6>{1,-1,2,-2,limit-1,-limit})
            for(auto quotient:std::array<std::int64_t,5>{0,1,-1,limit-1,-limit}) {
                auto numerator=std::bit_cast<std::uint64_t>(quotient*divisor);
                State state;state.flags=initial;state.defined_flags=0xffffffffu;
                native_logic_flags(state,11,width,numerator,std::uint64_t(divisor));
                auto expected=signed_divide[size](numerator,unsigned(divisor),(initial&0x8d5u)|0x202u);
                if((state.flags&0x8d5)!=(expected&0x8d5) || (state.defined_flags&0x8d5)!=0x8d5) return 10;
                ++divide_cases;
            }
        }
        for(unsigned guard=0;guard<5;++guard) {
            State state;
            auto numerator=guard==2 ? std::uint64_t(1)<<width:guard==3 ? std::uint64_t(1)<<(width-1):std::uint64_t(1)<<(width*2-1);
            auto divisor=guard<2 ? 0ULL:guard==4 ? ~0ULL:1ULL;
            try {native_logic_flags(state,guard==1 || guard>=3 ? 11:10,width,numerator,divisor);}
            catch(const std::runtime_error&) {++divide_guards;}
        }
    }
    if(divide_guards!=15) return 11;
    std::printf("{\"concrete_native_xor_cases\":%u,\"logical_width_cases\":%u,\"shift_width_cases\":%u,\"signed_multiply_cases\":%u,\"implicit_multiply_cases\":%u,\"divide_cases\":%u,\"divide_guards\":%u,\"producer_trace_preserves_last_error\":true,\"symbolic_AF_still_unknown\":true,\"game_acceptance\":false}\n",cases,logical_cases,shift_cases,multiply_cases,implicit_cases,divide_cases,divide_guards);
}

#pragma once
#include "native_floating.hpp"

namespace recomp_generated {
// Extended forms are identified by the original, emitter-checked FOP. Enum
// class has fixed int representation; this reserved tag carries no guessed op.
inline constexpr auto native_encoded_x87=static_cast<sharp_retro::X87Op>(0x7fff);
// Block environment formats exceed the scalar Memory width. Keep exact byte
// access and unknown empty payloads; never turn unobserved FSAVE slots into zero.
inline void execute_native_x87_environment(sharp_retro::Memory& memory,sharp_retro::State& state,std::uint32_t address,std::uint16_t opcode) {
#if defined(_WIN32) && defined(__i386__)
    auto form=opcode&0x738u;
    bool save=form==0x530 || form==0x130;
    bool full=form==0x530 || form==0x520;
    if(form!=0x130 && form!=0x120 && form!=0x530 && form!=0x520 || (opcode&0xc0)==0xc0)throw std::runtime_error("invalid x87 environment form");
    unsigned size=full?108:28;
    if(size>0x100000000ULL-address)throw std::runtime_error("wrapping x87 environment span");
    auto working=state;
    // Nonwaiting stores do not consume pending exceptions, but delivery of an
    // already-pending native exception is not yet modeled by this FP boundary.
    validate_native_fp(working,false);
    alignas(16) NativeX87Image image{};
    if(save)for(unsigned i=0;i<size;++i)memory.validate_store(std::uint64_t(address)+i,8);
    else for(unsigned i=0;i<size;++i)image[i]=std::uint8_t(memory.load(std::uint64_t(address)+i,8));
    auto old_known=state.defined_x87_st;auto old_top=(state.x87_status>>11)&7;
    {
        NativeFloatingScope fp(working,false);
        switch(form){
        case 0x130:asm volatile("fnstenv %0":"=m"(image)::"memory");break;
        case 0x530:asm volatile("fnsave %0":"=m"(image)::"memory");break;
        case 0x120:asm volatile("fldenv %0"::"m"(image):"memory");break;
        case 0x520:asm volatile("frstor %0"::"m"(image):"memory");break;
        }
        fp.finish();
    }
    auto new_top=(working.x87_status>>11)&7;unsigned known=0;
    for(unsigned physical=0;physical<8;++physical)if(old_known&(1u<<((physical+8-old_top)&7)))known|=1u<<((physical+8-new_top)&7);
    if(!save && full)known=0xff;
    // FNSAVE initializes control/status/tags, retaining the physical payloads.
    working.defined_x87_st=std::uint8_t(known);
    if(save)for(unsigned i=0;i<size;++i) {
        bool payload_unknown=full && i>=28 && !(old_known&(1u<<((i-28)/10)));
        if(payload_unknown)memory.store_scalar8(std::uint64_t(address)+i,{image[i],0xffffff00u,{}});
        else memory.store(std::uint64_t(address)+i,image[i],8);
    }
    state=working;
#else
    (void)memory;(void)state;(void)address;(void)opcode;
    throw std::runtime_error("x87 environment execution requires Windows x86");
#endif
}
// Controlled, compiled x87 operations for the Windows x86 execution backend.
// Original instruction pages never execute. No host double conversion is used.
inline void execute_native_x87(sharp_retro::Memory& memory,sharp_retro::X87Op op,sharp_retro::State& state,
                               std::uint64_t pc,std::uint32_t address,std::uint16_t opcode) {
#if defined(_WIN32) && defined(__i386__)
    using sharp_retro::X87Op;
    bool encoded=op==native_encoded_x87;
    if(encoded && (opcode&0xc0)!=0xc0 && ((opcode&0x738)==0x130 || (opcode&0x738)==0x120 || (opcode&0x738)==0x530 || (opcode&0x738)==0x520)) {
        execute_native_x87_environment(memory,state,address,opcode);return;
    }
    bool conditional=encoded && ((opcode&0x7e0)==0x2c0 || (opcode&0x7e0)==0x3c0);
    bool compare_integer=encoded && ((opcode&0x7f8)==0x3e8 || (opcode&0x7f8)==0x3f0 || (opcode&0x7f8)==0x7e8 || (opcode&0x7f8)==0x7f0);
    bool unordered=encoded && (opcode&0x7f8)==0x5e0;
    bool unordered_pop=encoded && (opcode&0x7f8)==0x5e8;
    bool compare_twice=encoded && (opcode==0x2e9 || opcode==0x6d9);
    bool divide_pop=encoded && (opcode&0x7f8)==0x6f8;
    bool reverse_divide_pop=encoded && (opcode&0x7f8)==0x6f0;
    unsigned register_group=opcode&0x7f8;
    bool reverse_subtract_pop=encoded && register_group==0x6e0;
    bool encoded_add_sub=encoded && (register_group==0xc0 || register_group==0xe0 || register_group==0xe8 ||
        register_group==0x4c0 || register_group==0x4e0 || register_group==0x4e8);
    bool absolute=encoded && opcode==0x1e1;
    bool constant_load=encoded && opcode>=0x1e9 && opcode<=0x1ed;
    bool math_pop=encoded && (opcode==0x1f1 || opcode==0x1f3 || opcode==0x1f9);
    bool tangent=encoded && opcode==0x1f2;
    bool status_only=encoded && (opcode==0x1e5 || opcode==0x1e4);
    bool math_unary=encoded && (opcode==0x1f0 || opcode==0x1f5 || opcode==0x1f8 || opcode==0x1fc || opcode==0x1fd || opcode==0x1fe || opcode==0x1ff);
    bool encoded_register_store=encoded && (opcode&0x7f8)==0x5d0;
    bool encoded_register_pop=encoded && (opcode&0x7f8)==0x5d8;
    bool integer64_load=encoded && (opcode&0x738)==0x728 && (opcode&0xc0)!=0xc0;
    unsigned memory_arithmetic_opcode=opcode&0x738;
    unsigned integer_arithmetic_group=memory_arithmetic_opcode&0x338;
    bool integer_arithmetic=encoded && (opcode&0xc0)!=0xc0 &&
        (memory_arithmetic_opcode&0x200)!=0 && (memory_arithmetic_opcode&0x100)==0 &&
        (integer_arithmetic_group==0x200 || integer_arithmetic_group==0x208 || integer_arithmetic_group==0x220 ||
         integer_arithmetic_group==0x228 || integer_arithmetic_group==0x230 || integer_arithmetic_group==0x238);
    bool extended_store=encoded && memory_arithmetic_opcode==0x338 && (opcode&0xc0)!=0xc0;
    bool encoded_memory_arithmetic=encoded && (opcode&0xc0)!=0xc0 &&
        (memory_arithmetic_opcode==0 || memory_arithmetic_opcode==0x20 || memory_arithmetic_opcode==0x28 ||
         memory_arithmetic_opcode==0x428 || memory_arithmetic_opcode==0x30 || memory_arithmetic_opcode==0x38);
    bool integer_store=encoded && (opcode&0xc0)!=0xc0 &&
        (memory_arithmetic_opcode==0x710 || memory_arithmetic_opcode==0x310 || memory_arithmetic_opcode==0x718 ||
         memory_arithmetic_opcode==0x318 || memory_arithmetic_opcode==0x738);
    bool integer_store_pop=integer_store && memory_arithmetic_opcode!=0x710 && memory_arithmetic_opcode!=0x310;
    if(encoded && (opcode>0x7ff || (!conditional && !compare_integer && !unordered && !unordered_pop && !compare_twice && !divide_pop && !reverse_divide_pop && !reverse_subtract_pop && !encoded_add_sub && !integer64_load && !encoded_memory_arithmetic && !integer_arithmetic && !extended_store && !integer_store && !absolute && !constant_load && !math_pop && !tangent && !status_only && !math_unary && !encoded_register_store && !encoded_register_pop)))
        throw std::runtime_error("unimplemented encoded native x87 operation");
    sharp_retro::x87_wait(state,pc);
    validate_native_fp(state,false);
    if((state.x87_control&0x3f)!=0x3f)
        throw std::runtime_error("native x87 operation with unmasked exceptions requires delivery modeling");
    bool store=op==X87Op::fst32 || op==X87Op::fst64 || op==X87Op::fstp32 || op==X87Op::fstp64 || integer_store || extended_store;
    bool register_pop=op==X87Op::fstp0 || op==X87Op::fstp1 || encoded_register_pop;
    bool register_store=register_pop || encoded_register_store;
    unsigned register_store_index=encoded_register_store || encoded_register_pop ? opcode&7u : op==X87Op::fstp1 ? 1u:0u;
    bool register_swap=op>=X87Op::fxch0 && op<=X87Op::fxch7;
    unsigned swap_index=unsigned(op)-unsigned(X87Op::fxch0);
    bool pop=op==X87Op::fstp32 || op==X87Op::fstp64 || integer_store_pop || extended_store;
    bool register_arithmetic=op>=X87Op::fmul_st0_0 && op<=X87Op::fmul_sti_7;
    unsigned arithmetic_destination=register_arithmetic && op>=X87Op::fmul_sti_0 ? unsigned(op)-unsigned(X87Op::fmul_sti_0) : 0u;
    bool register_divide=op>=X87Op::fdiv_sti_0 && op<=X87Op::fdiv_sti_7;
    if(register_divide) {register_arithmetic=true;arithmetic_destination=unsigned(op)-unsigned(X87Op::fdiv_sti_0);}
    bool divide_st0=op>=X87Op::fdiv_st0_0 && op<=X87Op::fdiv_st0_7;
    bool reverse_st0=op>=X87Op::fdivr_st0_0 && op<=X87Op::fdivr_st0_7;
    bool reverse_sti=op>=X87Op::fdivr_sti_0 && op<=X87Op::fdivr_sti_7;
    if(divide_st0 || reverse_st0 || reverse_sti) {
        register_arithmetic=true;
        arithmetic_destination=reverse_sti ? unsigned(op)-unsigned(X87Op::fdivr_sti_0) : 0u;
    }
    if(encoded_add_sub) {
        register_arithmetic=true;
        arithmetic_destination=register_group>=0x400 ? opcode&7u : 0u;
    }
    bool memory_compare=op==X87Op::fcom32 || op==X87Op::fcom64 || op==X87Op::fcomp32 || op==X87Op::fcomp64;
    bool compare=(op>=X87Op::fcom_st0 && op<=X87Op::fcomp_st7) || memory_compare || compare_integer || unordered || unordered_pop || compare_twice;
    bool compare_pop=(op>=X87Op::fcomp_st0 && op<=X87Op::fcomp_st7) || op==X87Op::fcomp32 || op==X87Op::fcomp64;
    unsigned compare_pops=compare_twice ? 2u : (compare_pop || unordered_pop || (compare_integer && opcode>=0x700) ? 1u : 0u);
    bool register_load=op>=X87Op::fld_st0 && op<=X87Op::fld_st7;
    bool multiply_pop=op>=X87Op::fmulp_st0 && op<=X87Op::fmulp_st7;
    bool add_pop=op>=X87Op::faddp_st0 && op<=X87Op::faddp_st7;
    bool subtract_pop=op>=X87Op::fsubp_st0 && op<=X87Op::fsubp_st7;
    bool arithmetic_pop=multiply_pop || add_pop || subtract_pop || divide_pop || reverse_divide_pop || reverse_subtract_pop || math_pop;
    unsigned pop_destination=multiply_pop ? unsigned(op)-unsigned(X87Op::fmulp_st0) :
        add_pop ? unsigned(op)-unsigned(X87Op::faddp_st0) : subtract_pop ? unsigned(op)-unsigned(X87Op::fsubp_st0) : math_pop ? 1u : (divide_pop || reverse_divide_pop || reverse_subtract_pop) ? opcode&7u:0u;
    bool two_results=op==X87Op::fsincos || tangent;
    bool arithmetic64=op==X87Op::fsub64 || op==X87Op::fmul64 || op==X87Op::fdiv64 || op==X87Op::fdivr64 || op==X87Op::fadd64 ||
        (encoded_memory_arithmetic && memory_arithmetic_opcode==0x428);
    bool arithmetic=arithmetic64 || op==X87Op::fmul32 || encoded_memory_arithmetic || integer_arithmetic;
    bool unary_arithmetic=op==X87Op::fsqrt || op==X87Op::fchs || absolute || math_unary;
    bool load=op==X87Op::fld32 || op==X87Op::fld64 || op==X87Op::fld80 || op==X87Op::fild32 || integer64_load || arithmetic || memory_compare;
    unsigned width=(integer_arithmetic && (memory_arithmetic_opcode&0x400)) || (integer_store && (memory_arithmetic_opcode==0x710 || memory_arithmetic_opcode==0x718)) ? 16 :
        op==X87Op::fld80 || extended_store ? 80 : op==X87Op::fld64 || op==X87Op::fst64 || op==X87Op::fstp64 || arithmetic64 || integer64_load ||
        (integer_store && memory_arithmetic_opcode==0x738) || op==X87Op::fcom64 || op==X87Op::fcomp64 ? 64 : 32;
    if(store) memory.validate_store(address,width);
    else if(!load && !register_store && !register_swap && !register_arithmetic && !compare && !register_load && !arithmetic_pop && !two_results && !unary_arithmetic && !conditional && !status_only && !constant_load && op!=X87Op::fld1 && op!=X87Op::fldz) throw std::runtime_error("unimplemented native x87 operation");
    auto input=load ? memory.load(address,width) : sharp_retro::bits(0);
    std::uint64_t input64=std::uint64_t(input),output64=0;
    std::array<std::uint8_t,10> input80{},output80{};
    if(op==X87Op::fld80) for(unsigned i=0;i<input80.size();i++) input80[i]=std::uint8_t(input>>(i*8));
    std::uint32_t input32=std::uint32_t(input64),output32=0;
    std::uint16_t output16=0;
    auto working=state;
    auto old_top=(state.x87_status>>11)&7;
    auto known=state.defined_x87_st;
    std::uint32_t executed_ip=0,integer_flags=0,seed=0x202;
    if(conditional) {
        unsigned condition=(opcode>>3)&3;
        unsigned needed=condition==0?1u:condition==1?0x40u:condition==2?0x41u:4u;
        for(unsigned bit=0;bit<7;++bit)if(needed&(1u<<bit)) (void)sharp_retro::read_flags(state,bit);
        seed|=std::uint32_t(state.flags)&needed;
    }
    {
        NativeFloatingScope floating(working,false);
        if(integer_store) switch(memory_arithmetic_opcode) {
        case 0x710:asm volatile("leal 1f,%0\n\t1: fists %1" : "=&r"(executed_ip),"=m"(output16) : : "memory");break;
        case 0x310:asm volatile("leal 1f,%0\n\t1: fistl %1" : "=&r"(executed_ip),"=m"(output32) : : "memory");break;
        case 0x718:asm volatile("leal 1f,%0\n\t1: fistps %1" : "=&r"(executed_ip),"=m"(output16) : : "memory");break;
        case 0x318:asm volatile("leal 1f,%0\n\t1: fistpl %1" : "=&r"(executed_ip),"=m"(output32) : : "memory");break;
        case 0x738:asm volatile("leal 1f,%0\n\t1: fistpll %1" : "=&r"(executed_ip),"=m"(output64) : : "memory");break;
        } else if(extended_store) {
            asm volatile("leal 1f,%0\n\t1: fstpt %1" : "=&r"(executed_ip),"=m"(output80) : : "memory");
        } else if(integer_arithmetic) switch(memory_arithmetic_opcode) {
        case 0x200:asm volatile("leal 1f,%0\n\t1: fiaddl %1" : "=&r"(executed_ip) : "m"(input32) : "memory");break;
        case 0x208:asm volatile("leal 1f,%0\n\t1: fimull %1" : "=&r"(executed_ip) : "m"(input32) : "memory");break;
        case 0x220:asm volatile("leal 1f,%0\n\t1: fisubl %1" : "=&r"(executed_ip) : "m"(input32) : "memory");break;
        case 0x228:asm volatile("leal 1f,%0\n\t1: fisubrl %1" : "=&r"(executed_ip) : "m"(input32) : "memory");break;
        case 0x230:asm volatile("leal 1f,%0\n\t1: fidivl %1" : "=&r"(executed_ip) : "m"(input32) : "memory");break;
        case 0x238:asm volatile("leal 1f,%0\n\t1: fidivrl %1" : "=&r"(executed_ip) : "m"(input32) : "memory");break;
        case 0x600:asm volatile("leal 1f,%0\n\t1: fiadds %1" : "=&r"(executed_ip) : "m"(input32) : "memory");break;
        case 0x608:asm volatile("leal 1f,%0\n\t1: fimuls %1" : "=&r"(executed_ip) : "m"(input32) : "memory");break;
        case 0x620:asm volatile("leal 1f,%0\n\t1: fisubs %1" : "=&r"(executed_ip) : "m"(input32) : "memory");break;
        case 0x628:asm volatile("leal 1f,%0\n\t1: fisubrs %1" : "=&r"(executed_ip) : "m"(input32) : "memory");break;
        case 0x630:asm volatile("leal 1f,%0\n\t1: fidivs %1" : "=&r"(executed_ip) : "m"(input32) : "memory");break;
        case 0x638:asm volatile("leal 1f,%0\n\t1: fidivrs %1" : "=&r"(executed_ip) : "m"(input32) : "memory");break;
        } else if(encoded_memory_arithmetic) switch(memory_arithmetic_opcode) {
        case 0:asm volatile("leal 1f,%0\n\t1: fadds %1" : "=&r"(executed_ip) : "m"(input32) : "memory");break;
        case 0x20:asm volatile("leal 1f,%0\n\t1: fsubs %1" : "=&r"(executed_ip) : "m"(input32) : "memory");break;
        case 0x28:asm volatile("leal 1f,%0\n\t1: fsubrs %1" : "=&r"(executed_ip) : "m"(input32) : "memory");break;
        case 0x428:asm volatile("leal 1f,%0\n\t1: fsubrl %1" : "=&r"(executed_ip) : "m"(input64) : "memory");break;
        case 0x30:asm volatile("leal 1f,%0\n\t1: fdivs %1" : "=&r"(executed_ip) : "m"(input32) : "memory");break;
        case 0x38:asm volatile("leal 1f,%0\n\t1: fdivrs %1" : "=&r"(executed_ip) : "m"(input32) : "memory");break;
        } else if(integer64_load) {
            asm volatile("leal 1f,%0\n\t1: fildll %1" : "=&r"(executed_ip) : "m"(input64) : "memory");
        } else if(encoded) switch(opcode) {
#define RECOMP_X87_FLAGS(I) \
        case 0x3e8+I:asm volatile("leal 1f,%0; pushfl; 1: fucomi %%st(" #I "),%%st; pushfl; popl %1; popfl" : "=&r"(executed_ip),"=r"(integer_flags) : : "memory","cc");break; \
        case 0x3f0+I:asm volatile("leal 1f,%0; pushfl; 1: fcomi %%st(" #I "),%%st; pushfl; popl %1; popfl" : "=&r"(executed_ip),"=r"(integer_flags) : : "memory","cc");break; \
        case 0x7e8+I:asm volatile("leal 1f,%0; pushfl; 1: fucomip %%st(" #I "),%%st; pushfl; popl %1; popfl" : "=&r"(executed_ip),"=r"(integer_flags) : : "memory","cc");break; \
        case 0x7f0+I:asm volatile("leal 1f,%0; pushfl; 1: fcomip %%st(" #I "),%%st; pushfl; popl %1; popfl" : "=&r"(executed_ip),"=r"(integer_flags) : : "memory","cc");break;
        RECOMP_X87_FLAGS(0) RECOMP_X87_FLAGS(1) RECOMP_X87_FLAGS(2) RECOMP_X87_FLAGS(3)
        RECOMP_X87_FLAGS(4) RECOMP_X87_FLAGS(5) RECOMP_X87_FLAGS(6) RECOMP_X87_FLAGS(7)
#undef RECOMP_X87_FLAGS
#define RECOMP_X87_CONDITION(OP,CODE,I) \
        case CODE+I:asm volatile("leal 1f,%0; pushfl; pushl %1; popfl; 1: " #OP " %%st(" #I "),%%st; popfl" : "=&r"(executed_ip) : "r"(seed) : "memory","cc");break;
#define RECOMP_X87_CONDITIONS(I) \
        RECOMP_X87_CONDITION(fcmovb,0x2c0,I) RECOMP_X87_CONDITION(fcmove,0x2c8,I) RECOMP_X87_CONDITION(fcmovbe,0x2d0,I) RECOMP_X87_CONDITION(fcmovu,0x2d8,I) \
        RECOMP_X87_CONDITION(fcmovnb,0x3c0,I) RECOMP_X87_CONDITION(fcmovne,0x3c8,I) RECOMP_X87_CONDITION(fcmovnbe,0x3d0,I) RECOMP_X87_CONDITION(fcmovnu,0x3d8,I)
        RECOMP_X87_CONDITIONS(0) RECOMP_X87_CONDITIONS(1) RECOMP_X87_CONDITIONS(2) RECOMP_X87_CONDITIONS(3)
        RECOMP_X87_CONDITIONS(4) RECOMP_X87_CONDITIONS(5) RECOMP_X87_CONDITIONS(6) RECOMP_X87_CONDITIONS(7)
#undef RECOMP_X87_CONDITIONS
#undef RECOMP_X87_CONDITION
        case 0x1f0:asm volatile("leal 1f,%0\n\t1: f2xm1" : "=&r"(executed_ip) : : "memory");break;
        case 0x1f1:asm volatile("leal 1f,%0\n\t1: fyl2x" : "=&r"(executed_ip) : : "memory");break;
        case 0x1f2:asm volatile("leal 1f,%0\n\t1: fptan" : "=&r"(executed_ip) : : "memory");break;
        case 0x1f3:asm volatile("leal 1f,%0\n\t1: fpatan" : "=&r"(executed_ip) : : "memory");break;
        case 0x1e4:asm volatile("leal 1f,%0\n\t1: ftst" : "=&r"(executed_ip) : : "memory");break;
        case 0x1e5:asm volatile("leal 1f,%0\n\t1: fxam" : "=&r"(executed_ip) : : "memory");break;
        case 0x1f5:asm volatile("leal 1f,%0\n\t1: fprem1" : "=&r"(executed_ip) : : "memory");break;
        case 0x1f8:asm volatile("leal 1f,%0\n\t1: fprem" : "=&r"(executed_ip) : : "memory");break;
        case 0x1f9:asm volatile("leal 1f,%0\n\t1: fyl2xp1" : "=&r"(executed_ip) : : "memory");break;
        case 0x1fc:asm volatile("leal 1f,%0\n\t1: frndint" : "=&r"(executed_ip) : : "memory");break;
        case 0x1fd:asm volatile("leal 1f,%0\n\t1: fscale" : "=&r"(executed_ip) : : "memory");break;
        case 0x1fe:asm volatile("leal 1f,%0\n\t1: fsin" : "=&r"(executed_ip) : : "memory");break;
        case 0x1ff:asm volatile("leal 1f,%0\n\t1: fcos" : "=&r"(executed_ip) : : "memory");break;
        // Native constants obey RC without substituting host-double literals.
        // FNSAVE/FRSTOR preserve the complete extended values, tags and status.
        case 0x1e9:asm volatile("leal 1f,%0\n\t1: fldl2t" : "=&r"(executed_ip) : : "memory");break;
        case 0x1ea:asm volatile("leal 1f,%0\n\t1: fldl2e" : "=&r"(executed_ip) : : "memory");break;
        case 0x1eb:asm volatile("leal 1f,%0\n\t1: fldpi" : "=&r"(executed_ip) : : "memory");break;
        case 0x1ec:asm volatile("leal 1f,%0\n\t1: fldlg2" : "=&r"(executed_ip) : : "memory");break;
        case 0x1ed:asm volatile("leal 1f,%0\n\t1: fldln2" : "=&r"(executed_ip) : : "memory");break;
#define RECOMP_X87_ADD_SUB(I) \
        case 0xc0+I:asm volatile("leal 1f,%0\n\t1: .intel_syntax noprefix\n\tfadd st(0),st(" #I ")\n\t.att_syntax prefix" : "=&r"(executed_ip) : : "memory");break; \
        case 0xe0+I:asm volatile("leal 1f,%0\n\t1: .intel_syntax noprefix\n\tfsub st(0),st(" #I ")\n\t.att_syntax prefix" : "=&r"(executed_ip) : : "memory");break; \
        case 0xe8+I:asm volatile("leal 1f,%0\n\t1: .intel_syntax noprefix\n\tfsubr st(0),st(" #I ")\n\t.att_syntax prefix" : "=&r"(executed_ip) : : "memory");break; \
        case 0x4c0+I:asm volatile("leal 1f,%0\n\t1: .intel_syntax noprefix\n\tfadd st(" #I "),st(0)\n\t.att_syntax prefix" : "=&r"(executed_ip) : : "memory");break; \
        case 0x4e8+I:asm volatile("leal 1f,%0\n\t1: .intel_syntax noprefix\n\tfsub st(" #I "),st(0)\n\t.att_syntax prefix" : "=&r"(executed_ip) : : "memory");break; \
        case 0x4e0+I:asm volatile("leal 1f,%0\n\t1: .intel_syntax noprefix\n\tfsubr st(" #I "),st(0)\n\t.att_syntax prefix" : "=&r"(executed_ip) : : "memory");break; \
        case 0x6e0+I:asm volatile("leal 1f,%0\n\t1: .intel_syntax noprefix\n\tfsubrp st(" #I "),st(0)\n\t.att_syntax prefix" : "=&r"(executed_ip) : : "memory");break;
        RECOMP_X87_ADD_SUB(0) RECOMP_X87_ADD_SUB(1) RECOMP_X87_ADD_SUB(2) RECOMP_X87_ADD_SUB(3)
        RECOMP_X87_ADD_SUB(4) RECOMP_X87_ADD_SUB(5) RECOMP_X87_ADD_SUB(6) RECOMP_X87_ADD_SUB(7)
#undef RECOMP_X87_ADD_SUB
#define RECOMP_X87_REGISTER_STORE(I) \
        case 0x5d0+I:asm volatile("leal 1f,%0\n\t1: fst %%st(" #I ")" : "=&r"(executed_ip) : : "memory");break; \
        case 0x5d8+I:asm volatile("leal 1f,%0\n\t1: fstp %%st(" #I ")" : "=&r"(executed_ip) : : "memory");break;
        RECOMP_X87_REGISTER_STORE(0) RECOMP_X87_REGISTER_STORE(1) RECOMP_X87_REGISTER_STORE(2) RECOMP_X87_REGISTER_STORE(3)
        RECOMP_X87_REGISTER_STORE(4) RECOMP_X87_REGISTER_STORE(5) RECOMP_X87_REGISTER_STORE(6) RECOMP_X87_REGISTER_STORE(7)
#undef RECOMP_X87_REGISTER_STORE
        case 0x1e1:asm volatile("leal 1f,%0\n\t1: fabs" : "=&r"(executed_ip) : : "memory");break;
#define RECOMP_X87_UNORDERED(I) \
        case 0x5e0+I: \
            asm volatile("leal 1f,%0\n\t1: fucom %%st(" #I ")" : "=&r"(executed_ip) : : "memory"); break; \
        case 0x5e8+I: \
            asm volatile("leal 1f,%0\n\t1: fucomp %%st(" #I ")" : "=&r"(executed_ip) : : "memory"); break; \
        case 0x6f0+I: \
            asm volatile("leal 1f,%0\n\t1: .intel_syntax noprefix\n\tfdivrp st(" #I "),st(0)\n\t.att_syntax prefix" : "=&r"(executed_ip) : : "memory"); break; \
        case 0x6f8+I: \
            asm volatile("leal 1f,%0\n\t1: .intel_syntax noprefix\n\tfdivp st(" #I "),st(0)\n\t.att_syntax prefix" : "=&r"(executed_ip) : : "memory"); break;
        RECOMP_X87_UNORDERED(0) RECOMP_X87_UNORDERED(1) RECOMP_X87_UNORDERED(2) RECOMP_X87_UNORDERED(3)
        RECOMP_X87_UNORDERED(4) RECOMP_X87_UNORDERED(5) RECOMP_X87_UNORDERED(6) RECOMP_X87_UNORDERED(7)
#undef RECOMP_X87_UNORDERED
        case 0x2e9:
            asm volatile("leal 1f,%0\n\t1: fucompp" : "=&r"(executed_ip) : : "memory"); break;
        case 0x6d9:
            asm volatile("leal 1f,%0\n\t1: fcompp" : "=&r"(executed_ip) : : "memory"); break;
        }
        else switch(op) {
        case X87Op::fld1:
            asm volatile("leal 1f,%0\n\t1: fld1" : "=&r"(executed_ip) : : "memory"); break;
        case X87Op::fldz:
            asm volatile("leal 1f,%0\n\t1: fldz" : "=&r"(executed_ip) : : "memory"); break;
        case X87Op::fld32:
            asm volatile("leal 1f,%0\n\t1: flds %1" : "=&r"(executed_ip) : "m"(input32) : "memory"); break;
        case X87Op::fld64:
            asm volatile("leal 1f,%0\n\t1: fldl %1" : "=&r"(executed_ip) : "m"(input64) : "memory"); break;
        case X87Op::fld80:
            asm volatile("leal 1f,%0\n\t1: fldt %1" : "=&r"(executed_ip) : "m"(input80) : "memory"); break;
        case X87Op::fild32:
            asm volatile("leal 1f,%0\n\t1: fildl %1" : "=&r"(executed_ip) : "m"(input32) : "memory"); break;
        case X87Op::fsub64:
            asm volatile("leal 1f,%0\n\t1: fsubl %1" : "=&r"(executed_ip) : "m"(input64) : "memory"); break;
        case X87Op::fmul64:
            asm volatile("leal 1f,%0\n\t1: fmull %1" : "=&r"(executed_ip) : "m"(input64) : "memory"); break;
        case X87Op::fmul32:
            asm volatile("leal 1f,%0\n\t1: fmuls %1" : "=&r"(executed_ip) : "m"(input32) : "memory"); break;
#define RECOMP_X87_MULTIPLY(I) \
        case X87Op::fmul_st0_##I: \
            asm volatile("leal 1f,%0\n\t1: fmul %%st(" #I "),%%st(0)" : "=&r"(executed_ip) : : "memory"); break; \
        case X87Op::fmul_sti_##I: \
            asm volatile("leal 1f,%0\n\t1: fmul %%st(0),%%st(" #I ")" : "=&r"(executed_ip) : : "memory"); break;
        RECOMP_X87_MULTIPLY(0) RECOMP_X87_MULTIPLY(1) RECOMP_X87_MULTIPLY(2) RECOMP_X87_MULTIPLY(3)
        RECOMP_X87_MULTIPLY(4) RECOMP_X87_MULTIPLY(5) RECOMP_X87_MULTIPLY(6) RECOMP_X87_MULTIPLY(7)
#undef RECOMP_X87_MULTIPLY
#define RECOMP_X87_COMPARE_DIVIDE(I) \
        case X87Op::fcom_st##I: \
            asm volatile("leal 1f,%0\n\t1: fcom %%st(" #I ")" : "=&r"(executed_ip) : : "memory"); break; \
        case X87Op::fcomp_st##I: \
            asm volatile("leal 1f,%0\n\t1: fcomp %%st(" #I ")" : "=&r"(executed_ip) : : "memory"); break; \
        case X87Op::fdiv_sti_##I: \
            asm volatile("leal 1f,%0\n\t1: .intel_syntax noprefix\n\tfdiv st(" #I "),st(0)\n\t.att_syntax prefix" : "=&r"(executed_ip) : : "memory"); break; \
        case X87Op::fdiv_st0_##I: \
            asm volatile("leal 1f,%0\n\t1: .intel_syntax noprefix\n\tfdiv st(0),st(" #I ")\n\t.att_syntax prefix" : "=&r"(executed_ip) : : "memory"); break; \
        case X87Op::fdivr_st0_##I: \
            asm volatile("leal 1f,%0\n\t1: .intel_syntax noprefix\n\tfdivr st(0),st(" #I ")\n\t.att_syntax prefix" : "=&r"(executed_ip) : : "memory"); break; \
        case X87Op::fdivr_sti_##I: \
            asm volatile("leal 1f,%0\n\t1: .intel_syntax noprefix\n\tfdivr st(" #I "),st(0)\n\t.att_syntax prefix" : "=&r"(executed_ip) : : "memory"); break;
        RECOMP_X87_COMPARE_DIVIDE(0) RECOMP_X87_COMPARE_DIVIDE(1) RECOMP_X87_COMPARE_DIVIDE(2) RECOMP_X87_COMPARE_DIVIDE(3)
        RECOMP_X87_COMPARE_DIVIDE(4) RECOMP_X87_COMPARE_DIVIDE(5) RECOMP_X87_COMPARE_DIVIDE(6) RECOMP_X87_COMPARE_DIVIDE(7)
#undef RECOMP_X87_COMPARE_DIVIDE
        case X87Op::fchs:
            asm volatile("leal 1f,%0\n\t1: fchs" : "=&r"(executed_ip) : : "memory"); break;
        case X87Op::fdiv64:
            asm volatile("leal 1f,%0\n\t1: fdivl %1" : "=&r"(executed_ip) : "m"(input64) : "memory"); break;
        case X87Op::fdivr64:
            asm volatile("leal 1f,%0\n\t1: fdivrl %1" : "=&r"(executed_ip) : "m"(input64) : "memory"); break;
        case X87Op::fadd64:
            asm volatile("leal 1f,%0\n\t1: faddl %1" : "=&r"(executed_ip) : "m"(input64) : "memory"); break;
        case X87Op::fcom32:
            asm volatile("leal 1f,%0\n\t1: fcoms %1" : "=&r"(executed_ip) : "m"(input32) : "memory"); break;
        case X87Op::fcom64:
            asm volatile("leal 1f,%0\n\t1: fcoml %1" : "=&r"(executed_ip) : "m"(input64) : "memory"); break;
        case X87Op::fcomp32:
            asm volatile("leal 1f,%0\n\t1: fcomps %1" : "=&r"(executed_ip) : "m"(input32) : "memory"); break;
        case X87Op::fcomp64:
            asm volatile("leal 1f,%0\n\t1: fcompl %1" : "=&r"(executed_ip) : "m"(input64) : "memory"); break;
        case X87Op::fsqrt:
            asm volatile("leal 1f,%0\n\t1: fsqrt" : "=&r"(executed_ip) : : "memory"); break;
        case X87Op::fsincos:
            asm volatile("leal 1f,%0\n\t1: fsincos" : "=&r"(executed_ip) : : "memory"); break;
#define RECOMP_X87_STACK(I) \
        case X87Op::fld_st##I: \
            asm volatile("leal 1f,%0\n\t1: fld %%st(" #I ")" : "=&r"(executed_ip) : : "memory"); break; \
        case X87Op::fmulp_st##I: \
            asm volatile("leal 1f,%0\n\t1: fmulp %%st(0),%%st(" #I ")" : "=&r"(executed_ip) : : "memory"); break;
        RECOMP_X87_STACK(0) RECOMP_X87_STACK(1) RECOMP_X87_STACK(2) RECOMP_X87_STACK(3)
        RECOMP_X87_STACK(4) RECOMP_X87_STACK(5) RECOMP_X87_STACK(6) RECOMP_X87_STACK(7)
#undef RECOMP_X87_STACK
#define RECOMP_X87_ADD_SUB_POP(I) \
        case X87Op::faddp_st##I: \
            asm volatile("leal 1f,%0\n\t1: faddp %%st(0),%%st(" #I ")" : "=&r"(executed_ip) : : "memory"); break; \
        case X87Op::fsubp_st##I: \
            asm volatile("leal 1f,%0\n\t1: .intel_syntax noprefix\n\tfsubp st(" #I "),st(0)\n\t.att_syntax prefix" : "=&r"(executed_ip) : : "memory"); break;
        RECOMP_X87_ADD_SUB_POP(0) RECOMP_X87_ADD_SUB_POP(1) RECOMP_X87_ADD_SUB_POP(2) RECOMP_X87_ADD_SUB_POP(3)
        RECOMP_X87_ADD_SUB_POP(4) RECOMP_X87_ADD_SUB_POP(5) RECOMP_X87_ADD_SUB_POP(6) RECOMP_X87_ADD_SUB_POP(7)
#undef RECOMP_X87_ADD_SUB_POP
        case X87Op::fstp0:
            asm volatile("leal 1f,%0\n\t1: fstp %%st(0)" : "=&r"(executed_ip) : : "memory"); break;
        case X87Op::fstp1:
            asm volatile("leal 1f,%0\n\t1: fstp %%st(1)" : "=&r"(executed_ip) : : "memory"); break;
        case X87Op::fxch0:
            asm volatile("leal 1f,%0\n\t1: fxch %%st(0)" : "=&r"(executed_ip) : : "memory"); break;
        case X87Op::fxch1:
            asm volatile("leal 1f,%0\n\t1: fxch %%st(1)" : "=&r"(executed_ip) : : "memory"); break;
        case X87Op::fxch2:
            asm volatile("leal 1f,%0\n\t1: fxch %%st(2)" : "=&r"(executed_ip) : : "memory"); break;
        case X87Op::fxch3:
            asm volatile("leal 1f,%0\n\t1: fxch %%st(3)" : "=&r"(executed_ip) : : "memory"); break;
        case X87Op::fxch4:
            asm volatile("leal 1f,%0\n\t1: fxch %%st(4)" : "=&r"(executed_ip) : : "memory"); break;
        case X87Op::fxch5:
            asm volatile("leal 1f,%0\n\t1: fxch %%st(5)" : "=&r"(executed_ip) : : "memory"); break;
        case X87Op::fxch6:
            asm volatile("leal 1f,%0\n\t1: fxch %%st(6)" : "=&r"(executed_ip) : : "memory"); break;
        case X87Op::fxch7:
            asm volatile("leal 1f,%0\n\t1: fxch %%st(7)" : "=&r"(executed_ip) : : "memory"); break;
        case X87Op::fst32:
            asm volatile("leal 1f,%0\n\t1: fsts %1" : "=&r"(executed_ip),"=m"(output32) : : "memory"); break;
        case X87Op::fst64:
            asm volatile("leal 1f,%0\n\t1: fstl %1" : "=&r"(executed_ip),"=m"(output64) : : "memory"); break;
        case X87Op::fstp32:
            asm volatile("leal 1f,%0\n\t1: fstps %1" : "=&r"(executed_ip),"=m"(output32) : : "memory"); break;
        case X87Op::fstp64:
            asm volatile("leal 1f,%0\n\t1: fstpl %1" : "=&r"(executed_ip),"=m"(output64) : : "memory"); break;
        }
        floating.finish();
    }
    // Translate recorded native instruction/data addresses if this CPU actually
    // records them. Wine's translated x87 currently leaves these fields at zero;
    // preserving the observed fields avoids inventing guest pointers there.
    if(working.x87_ip==executed_ip) {
        working.x87_ip=std::uint32_t(pc); working.x87_opcode=opcode;
    } else if(working.x87_opcode!=state.x87_opcode) {
        throw std::runtime_error("unrecognized native x87 opcode/IP recording behavior");
    }
    const void* operand=store ? (width==80 ? static_cast<void*>(output80.data()) : width==16 ? static_cast<void*>(&output16) : width==64 ? static_cast<void*>(&output64) : &output32) :
        (width==80 ? static_cast<void*>(input80.data()) : width==64 ? static_cast<void*>(&input64) : &input32);
    auto native_operand=std::uint32_t(reinterpret_cast<std::uintptr_t>(operand));
    if((store || load) && working.x87_dp==native_operand) working.x87_dp=address;
    else if(working.x87_dp!=state.x87_dp) throw std::runtime_error("unrecognized native x87 data-pointer recording behavior");
    auto new_top=(working.x87_status>>11)&7;
    bool unmasked=(working.x87_status&0x3f)&~working.x87_control;
    if(conditional) {
        if(new_top!=old_top)throw std::runtime_error("unexpected x87 conditional move stack transition");
        if(((working.x87_tag>>(new_top*2))&3)!=3)known|=1u;
    } else if(status_only) {
        if(new_top!=old_top)throw std::runtime_error("unexpected x87 classification stack transition");
    } else if(compare) {
        if(new_top!=((old_top+compare_pops)&7)) throw std::runtime_error("unexpected x87 comparison stack transition");
        if(compare_pops) known=std::uint8_t((known>>compare_pops)|(known<<(8-compare_pops)));
    } else if(two_results) {
        if(new_top==((old_top+7)&7)) known=std::uint8_t((known<<1)|3u);
        else if(new_top!=old_top || !(working.x87_status&0x400)) throw std::runtime_error("unexpected x87 sincos stack transition");
        // C2=1 leaves an out-of-range input and TOP unchanged.
    } else if(arithmetic_pop) {
        if(new_top!=((old_top+1)&7)) throw std::runtime_error("unexpected x87 arithmetic-pop transition");
        known|=std::uint8_t(1u<<pop_destination);
        known=std::uint8_t((known>>1)|(known<<7));
    } else if(register_swap) {
        if(new_top!=old_top) throw std::runtime_error("unexpected x87 register exchange stack transition");
        auto low=(known&1u),other=(known>>swap_index)&1u;
        known=std::uint8_t((known&~(1u|(1u<<swap_index)))|other|(low<<swap_index));
        // Live operands were required known. Masked empty-stack results that
        // become live are defined by the native instruction, not empty payload.
        for(auto index:{0u,swap_index})
            if(((working.x87_tag>>(((new_top+index)&7)*2))&3)!=3) known|=std::uint8_t(1u<<index);
    } else if(register_arithmetic) {
        if(new_top!=old_top) throw std::runtime_error("unexpected x87 register arithmetic stack transition");
        known|=std::uint8_t(1u<<arithmetic_destination);
    } else if(arithmetic || unary_arithmetic) {
        if(new_top!=old_top) throw std::runtime_error("unexpected x87 arithmetic stack transition");
        known|=1u;
    } else if(register_store) {
        if(new_top!=((old_top+unsigned(register_pop))&7)) throw std::runtime_error("unexpected x87 register-store transition");
        // A live destination receives ST(0), or the masked-underflow indefinite
        // value. Retain conservative knowledge for a popped ST(0) slot.
        if(!register_pop || register_store_index) known|=std::uint8_t(1u<<register_store_index);
        if(register_pop) known=std::uint8_t((known>>1)|(known<<7));
    } else if(!store) {
        if(new_top==((old_top+7)&7)) known=std::uint8_t((known<<1)|1u);
        else if(new_top!=old_top || !unmasked) throw std::runtime_error("unexpected x87 push stack transition");
    } else {
        if(!pop) {
            if(new_top!=old_top) throw std::runtime_error("unexpected x87 non-popping store stack transition");
        } else {
            if(new_top==((old_top+1)&7)) known=std::uint8_t((known>>1)|(known<<7));
            else if(new_top!=old_top || !unmasked) throw std::runtime_error("unexpected x87 pop stack transition");
        }
        // An unmasked x87 exception suppresses the write and pop. Commit the
        // pending state; the next waiting instruction performs guest delivery.
        if(!unmasked) {
            sharp_retro::bits output=width==16 ? output16 : width==64 ? output64 : output32;
            if(width==80) {output=0;for(unsigned i=0;i<output80.size();++i) output|=sharp_retro::bits(output80[i])<<(i*8);}
            memory.store(address,output,width);
        }
    }
    if(compare_integer) {
        working.flags=(working.flags&~std::uint64_t(0x8d5u))|(integer_flags&0x8d5u);
        working.defined_flags|=0x8d5u;
        for(unsigned bit=0;bit<32;++bit)if(0x8d5u&(1u<<bit))working.flag_origins[bit]=0;
    }
    working.defined_x87_st=known;
    state=working;
#else
    (void)memory; (void)op; (void)state; (void)pc; (void)address; (void)opcode;
    throw std::runtime_error("x87 value backend requires Windows x86");
#endif
}
}

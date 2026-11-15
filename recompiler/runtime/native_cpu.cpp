#include "runtime.hpp"
#include "native_floating.hpp"
#if defined(_WIN32) && defined(__i386__) && defined(RECOMP_NATIVE_EXECUTION)
namespace sharp_retro {
// Execute against the physical x87 register file, retaining its aliasing with
// MMX. Unknown unconsumed registers carry representative bits, never evidence.
void native_legacy(Memory& memory,State& state,std::uint64_t pc,unsigned family,std::uint32_t descriptor,std::uint32_t address) {
    if(family==2) {
        if(descriptor || address)throw std::runtime_error("invalid RDTSC descriptor");
        std::uint32_t low,high;asm volatile("rdtsc":"=a"(low),"=d"(high)::"memory");
        scalar_gpr32(state,0,{low,0xffffffffu,{}});scalar_gpr32(state,2,{high,0xffffffffu,{}});return;
    }
    if(family==1) {
        if(descriptor&~0xffu || (descriptor&7)>5)throw std::runtime_error("invalid segment-store descriptor");
        std::uint32_t selector=0;
        switch(descriptor&7){
#define SELECTOR(N,NAME) case N:asm volatile("movl %%" #NAME ",%0":"=r"(selector));break;
        SELECTOR(0,es) SELECTOR(1,cs) SELECTOR(2,ss) SELECTOR(3,ds) SELECTOR(4,fs) SELECTOR(5,gs)
#undef SELECTOR
        }
        if(descriptor&0x80u)memory.store(address,selector,16);
        else if(descriptor&0x40u)write_gpr_slice(state,(descriptor>>3)&7,selector,0xffffu);
        else scalar_gpr32(state,(descriptor>>3)&7,{selector,0xffffffffu,{}});
        return;
    }
    if(family!=0 || descriptor&~0x7fffu)throw std::runtime_error("invalid legacy family/descriptor");
    unsigned opcode=descriptor&255,reg=(descriptor>>8)&7,rm=(descriptor>>11)&7;bool mem=descriptor&0x4000;
    if(opcode!=0x77 && opcode!=0x6e && opcode!=0x7e && opcode!=0x6f && opcode!=0x7f && opcode!=0xdb && opcode!=0x76 && opcode!=0xeb && opcode!=0xfa && opcode!=0x62 && opcode!=0x61 && opcode!=0xef && opcode!=0x2a)throw std::runtime_error("unsupported MMX opcode");
    if(opcode==0x77 && descriptor!=0x77)throw std::runtime_error("invalid EMMS descriptor");
    x87_wait(state,pc);
    auto working=state;auto old_top=(state.x87_status>>11)&7;auto old_known=state.defined_x87_st;bool split=recomp_generated::native_mmx_is_split();
    working.defined_x87_st=0xff;recomp_generated::validate_native_fp(working,false);
    if((working.x87_control&0x3f)!=0x3f)throw std::runtime_error("unmasked MMX x87 exceptions require delivery modeling");
    if(opcode==0x2a && (working.mxcsr&0x1f80u)!=0x1f80u)throw std::runtime_error("unmasked MMX conversion exceptions require delivery modeling");
    auto require_mmx=[&](unsigned physical) {if(!(split?state.defined_native_mmx&(1u<<physical):old_known&(1u<<((physical+8-old_top)&7))))throw std::runtime_error("read of unknown aliased MMX value");};
    bool store=opcode==0x7e || opcode==0x7f;
    bool load=mem && !store;unsigned width=(opcode==0x6e || opcode==0x7e)?32:64;
    std::uint64_t input=0,output=0;
    if(load)input=std::uint64_t(memory.load(address,width));
    if(mem && store)memory.validate_store(address,width);
    if(opcode==0x6e && !mem)input=std::uint32_t(read_gpr_mask(state,rm,0xffffffffu));
    if(store)require_mmx(reg);
    bool binary=opcode==0xdb || opcode==0x76 || opcode==0xeb || opcode==0xfa || opcode==0x62 || opcode==0x61 || opcode==0xef;
    bool zero=binary && !mem && reg==rm && (opcode==0xef || opcode==0xfa || opcode==0x76);
    // Zero idioms still execute natively, but do not consume their old payload.
    if(opcode!=0x77 && opcode!=0x6e && !mem && !zero)require_mmx(store?reg:rm);
    if(binary && !zero)require_mmx(reg);
    auto xmm_bits=opcode==0x2a?read_xmm128(state,reg):bits(0);std::array<std::uint64_t,2> xmm{};std::memcpy(xmm.data(),&xmm_bits,16);
    {
        recomp_generated::NativeFloatingScope fp(working,false);
        if(opcode==0x77)asm volatile("emms":::"memory");
        else if(mem || opcode==0x6e || opcode==0x7e) {
            switch(reg) {
#define MMX_MEMORY(I) case I: switch(opcode){ \
            case 0x6e:asm volatile("movd %0,%%mm" #I::"m"(input):"memory");break; \
            case 0x7e:asm volatile("movd %%mm" #I ",%0":"=m"(output)::"memory");break; \
            case 0x6f:asm volatile("movq %0,%%mm" #I::"m"(input):"memory");break; \
            case 0x7f:asm volatile("movq %%mm" #I ",%0":"=m"(output)::"memory");break; \
            case 0xdb:asm volatile("pand %0,%%mm" #I::"m"(input):"memory");break; \
            case 0x76:asm volatile("pcmpeqd %0,%%mm" #I::"m"(input):"memory");break; \
            case 0xeb:asm volatile("por %0,%%mm" #I::"m"(input):"memory");break; \
            case 0xfa:asm volatile("psubd %0,%%mm" #I::"m"(input):"memory");break; \
            case 0x62:asm volatile("punpckldq %0,%%mm" #I::"m"(input):"memory");break; \
            case 0x61:asm volatile("punpcklwd %0,%%mm" #I::"m"(input):"memory");break; \
            case 0xef:asm volatile("pxor %0,%%mm" #I::"m"(input):"memory");break; \
            }break;
            MMX_MEMORY(0) MMX_MEMORY(1) MMX_MEMORY(2) MMX_MEMORY(3)
            MMX_MEMORY(4) MMX_MEMORY(5) MMX_MEMORY(6) MMX_MEMORY(7)
#undef MMX_MEMORY
            }
            if(opcode==0x2a)asm volatile("movdqu %1,%%xmm0; cvtpi2ps %2,%%xmm0; movdqu %%xmm0,%0":"=m"(xmm):"m"(xmm),"m"(input):"xmm0","memory");
        } else switch((reg<<3)|rm) {
#define MMX_PAIR(D,S) case ((D)<<3)|(S):switch(opcode){ \
            case 0x6f:asm volatile("movq %%mm" #S ",%%mm" #D:::"memory");break; \
            case 0x7f:asm volatile("movq %%mm" #D ",%%mm" #S:::"memory");break; \
            case 0xdb:asm volatile("pand %%mm" #S ",%%mm" #D:::"memory");break; \
            case 0x76:asm volatile("pcmpeqd %%mm" #S ",%%mm" #D:::"memory");break; \
            case 0xeb:asm volatile("por %%mm" #S ",%%mm" #D:::"memory");break; \
            case 0xfa:asm volatile("psubd %%mm" #S ",%%mm" #D:::"memory");break; \
            case 0x62:asm volatile("punpckldq %%mm" #S ",%%mm" #D:::"memory");break; \
            case 0x61:asm volatile("punpcklwd %%mm" #S ",%%mm" #D:::"memory");break; \
            case 0xef:asm volatile("pxor %%mm" #S ",%%mm" #D:::"memory");break; \
            case 0x2a:asm volatile("movdqu %1,%%xmm0; cvtpi2ps %%mm" #S ",%%xmm0; movdqu %%xmm0,%0":"=m"(xmm):"m"(xmm):"xmm0","memory");break; \
            }break;
#define MMX_ROW(D) MMX_PAIR(D,0) MMX_PAIR(D,1) MMX_PAIR(D,2) MMX_PAIR(D,3) MMX_PAIR(D,4) MMX_PAIR(D,5) MMX_PAIR(D,6) MMX_PAIR(D,7)
            MMX_ROW(0) MMX_ROW(1) MMX_ROW(2) MMX_ROW(3) MMX_ROW(4) MMX_ROW(5) MMX_ROW(6) MMX_ROW(7)
#undef MMX_ROW
#undef MMX_PAIR
        }
        fp.finish();
    }
    auto new_top=(working.x87_status>>11)&7;unsigned known=0;
    for(unsigned physical=0;physical<8;++physical)if(old_known&(1u<<((physical+8-old_top)&7)))known|=1u<<((physical+8-new_top)&7);
    bool mmx_write=opcode!=0x77 && opcode!=0x7e && opcode!=0x2a && !(opcode==0x7f && mem);
    if(mmx_write) {
        unsigned physical=opcode==0x7f?rm:reg;
        if(split)working.defined_native_mmx|=std::uint8_t(1u<<physical);
        else known|=1u<<((physical+8-new_top)&7);
    }
    working.defined_x87_st=std::uint8_t(known);
    if(opcode==0x2a){std::memcpy(&working.xmm[reg],xmm.data(),16);working.defined_xmm|=std::uint16_t(1u<<reg);}
    if(store){if(mem)memory.store(address,output,width);else if(opcode==0x7e)scalar_gpr32(working,rm,{std::uint32_t(output),0xffffffffu,{}});}
    state=working;
}

std::uint32_t native_double_shift_bits(bool right,unsigned width,std::uint32_t left,std::uint32_t source,unsigned count,std::uint32_t seed,std::uint32_t& flags) {
#define DOUBLE_SHIFT(OP,SUFFIX,L,S) asm volatile("pushfl; pushl %4; popfl; " OP SUFFIX " %%cl,%2,%0; pushfl; popl %1; popfl" \
    : "+&r"(L),"=r"(flags) : "r"(S),"c"(count),"r"(seed) : "memory","cc")
    if(width==16) {auto a=std::uint16_t(left),b=std::uint16_t(source);if(right){DOUBLE_SHIFT("shrd","w",a,b);}else{DOUBLE_SHIFT("shld","w",a,b);}return a;}
    if(width!=32)throw std::runtime_error("invalid native double-shift width");
    if(right){DOUBLE_SHIFT("shrd","l",left,source);}else{DOUBLE_SHIFT("shld","l",left,source);}return left;
#undef DOUBLE_SHIFT
}
namespace {thread_local std::array<std::pair<std::uint64_t,std::uint64_t>,32> flag_producers{};}
void native_record_flag_origin(std::uint64_t origin,unsigned bit,std::uint64_t pc) {
    std::uint32_t error;asm volatile("movl %%fs:0x34,%0":"=r"(error)::"memory");
    if(bit<32) flag_producers[bit]={origin,pc};
    asm volatile("movl %0,%%fs:0x34"::"r"(error):"memory");
}
std::uint64_t native_flag_origin_pc(std::uint64_t origin,unsigned bit) {
    std::uint32_t error;asm volatile("movl %%fs:0x34,%0":"=r"(error)::"memory");
    auto pc=bit<32 && flag_producers[bit].first==origin ? flag_producers[bit].second:0;
    asm volatile("movl %0,%%fs:0x34"::"r"(error):"memory");
    return pc;
}
void native_require_observed_alu_flags(const State& s) {
    if((s.defined_flags&0x8d5u)!=0x8d5u) {
        std::string message="native ALU input flags have no concrete CPU observation";
        for(unsigned bit=0;bit<32;++bit) if((0x8d5u&(1u<<bit)) && !(s.defined_flags&(1u<<bit)))
            message+="; bit "+std::to_string(bit)+" producer "+std::to_string(native_undefined_flag_pc(s,bit));
        throw std::runtime_error(message);
    }
}
std::uint32_t native_alu_flag_bits(unsigned operation,unsigned width,std::uint64_t input_left,std::uint64_t input_right,std::uint32_t seed) {
    auto left=std::uint32_t(input_left),right=std::uint32_t(input_right);
    std::uint32_t flags;
#define SHARP_NATIVE_LOGIC(instruction,suffix,l,r,constraint) \
    asm volatile("pushfl; pushl %3; popfl; " instruction suffix " %2,%0; pushfl; popl %1; popfl" \
        : "+" constraint(l),"=r"(flags) : constraint(r),"r"(seed) : "cc","memory")
#define SHARP_NATIVE_LOGIC_WIDTH(instruction) \
    if(width==8) {auto a=std::uint8_t(left),b=std::uint8_t(right);SHARP_NATIVE_LOGIC(instruction,"b",a,b,"q");} \
    else if(width==16) {auto a=std::uint16_t(left),b=std::uint16_t(right);SHARP_NATIVE_LOGIC(instruction,"w",a,b,"r");} \
    else if(width==32) {SHARP_NATIVE_LOGIC(instruction,"l",left,right,"r");} \
    else throw std::runtime_error("invalid native logical operand width")
#define SHARP_NATIVE_SHIFT(instruction,suffix,l,constraint) \
    asm volatile("pushfl; pushl %3; popfl; " instruction suffix " %%cl,%0; pushfl; popl %1; popfl" \
        : "+" constraint(l),"=r"(flags) : "c"(right),"r"(seed) : "cc","memory")
#define SHARP_NATIVE_SHIFT_WIDTH(instruction) \
    if(width==8) {auto a=std::uint8_t(left);SHARP_NATIVE_SHIFT(instruction,"b",a,"q");} \
    else if(width==16) {auto a=std::uint16_t(left);SHARP_NATIVE_SHIFT(instruction,"w",a,"r");} \
    else if(width==32) {SHARP_NATIVE_SHIFT(instruction,"l",left,"r");} \
    else throw std::runtime_error("invalid native shift operand width")
    if(operation==0) {SHARP_NATIVE_LOGIC_WIDTH("and");}
    else if(operation==1) {SHARP_NATIVE_LOGIC_WIDTH("or");}
    else if(operation==2) {SHARP_NATIVE_LOGIC_WIDTH("xor");}
    else if(operation==3) {SHARP_NATIVE_LOGIC_WIDTH("test");}
    else if(operation==4) {SHARP_NATIVE_SHIFT_WIDTH("shl");}
    else if(operation==5) {SHARP_NATIVE_SHIFT_WIDTH("shr");}
    else if(operation==6) {SHARP_NATIVE_SHIFT_WIDTH("sar");}
    else if(operation==7) {
        if(width==16) {auto a=std::uint16_t(left),b=std::uint16_t(right);SHARP_NATIVE_LOGIC("imul","w",a,b,"r");}
        else if(width==32) {SHARP_NATIVE_LOGIC("imul","l",left,right,"r");}
        else throw std::runtime_error("invalid native signed multiply operand width");
    }
    else if(operation==8 || operation==9) {
#define SHARP_NATIVE_IMPLICIT(instruction) \
        if(width==8) {std::uint16_t a=std::uint8_t(left);auto b=std::uint8_t(right); \
            asm volatile("pushfl; pushl %3; popfl; " instruction "b %2; pushfl; popl %1; popfl" \
                : "+a"(a),"=r"(flags) : "q"(b),"r"(seed) : "cc","memory");} \
        else if(width==16) {auto a=std::uint16_t(left),b=std::uint16_t(right);std::uint16_t high; \
            asm volatile("pushfl; pushl %4; popfl; " instruction "w %3; pushfl; popl %2; popfl" \
                : "+a"(a),"=d"(high),"=r"(flags) : "r"(b),"r"(seed) : "cc","memory");} \
        else if(width==32) {auto a=left,b=right;std::uint32_t high; \
            asm volatile("pushfl; pushl %4; popfl; " instruction "l %3; pushfl; popl %2; popfl" \
                : "+a"(a),"=d"(high),"=r"(flags) : "r"(b),"r"(seed) : "cc","memory");} \
        else throw std::runtime_error("invalid native implicit multiply operand width")
        if(operation==8) {SHARP_NATIVE_IMPLICIT("mul");} else {SHARP_NATIVE_IMPLICIT("imul");}
#undef SHARP_NATIVE_IMPLICIT
    }
    else if(operation==10 || operation==11) {
        // The generated IR has already rejected zero divisors and quotient
        // overflow before this observation; exception delivery stays separate.
        if(width!=8 && width!=16 && width!=32) throw std::runtime_error("invalid native divide operand width");
        auto mask=(std::uint64_t(1)<<width)-1;
        auto numerator=width==32 ? input_left:input_left&((std::uint64_t(1)<<(width*2))-1);
        auto divisor=input_right&mask;
        if(!divisor) throw std::runtime_error("native divide flag observation requires a nonzero divisor");
        if(operation==10) {
            if(numerator/divisor>mask) throw std::runtime_error("native divide flag observation refuses quotient overflow");
        } else {
            auto signed_numerator=width==32 ? std::bit_cast<std::int64_t>(numerator):
                width==16 ? std::int64_t(std::bit_cast<std::int32_t>(std::uint32_t(numerator))):
                            std::int64_t(std::bit_cast<std::int16_t>(std::uint16_t(numerator)));
            auto signed_divisor=width==32 ? std::int64_t(std::bit_cast<std::int32_t>(std::uint32_t(divisor))):
                width==16 ? std::int64_t(std::bit_cast<std::int16_t>(std::uint16_t(divisor))):
                            std::int64_t(std::bit_cast<std::int8_t>(std::uint8_t(divisor)));
            if(signed_numerator==std::numeric_limits<std::int64_t>::min() && signed_divisor==-1)
                throw std::runtime_error("native divide flag observation refuses signed overflow");
            auto quotient=signed_numerator/signed_divisor,limit=std::int64_t(1)<<(width-1);
            if(quotient < -limit || quotient>=limit) throw std::runtime_error("native divide flag observation refuses signed quotient overflow");
        }
#define SHARP_NATIVE_DIVIDE(instruction) \
        if(width==8) {auto a=std::uint16_t(input_left);auto b=std::uint8_t(right); \
            asm volatile("pushfl; pushl %3; popfl; " instruction "b %2; pushfl; popl %1; popfl" \
                : "+a"(a),"=r"(flags) : "q"(b),"r"(seed) : "cc","memory");} \
        else if(width==16) {auto a=std::uint16_t(input_left),high=std::uint16_t(input_left>>16),b=std::uint16_t(right); \
            asm volatile("pushfl; pushl %4; popfl; " instruction "w %3; pushfl; popl %2; popfl" \
                : "+a"(a),"+d"(high),"=r"(flags) : "r"(b),"r"(seed) : "cc","memory");} \
        else if(width==32) {auto a=std::uint32_t(input_left),high=std::uint32_t(input_left>>32),b=right; \
            asm volatile("pushfl; pushl %4; popfl; " instruction "l %3; pushfl; popl %2; popfl" \
                : "+a"(a),"+d"(high),"=r"(flags) : "r"(b),"r"(seed) : "cc","memory");} \
        else throw std::runtime_error("invalid native divide operand width")
        if(operation==10) {SHARP_NATIVE_DIVIDE("div");} else {SHARP_NATIVE_DIVIDE("idiv");}
#undef SHARP_NATIVE_DIVIDE
    }
    else throw std::runtime_error("invalid native ALU operation");
#undef SHARP_NATIVE_SHIFT_WIDTH
#undef SHARP_NATIVE_SHIFT
#undef SHARP_NATIVE_LOGIC_WIDTH
#undef SHARP_NATIVE_LOGIC
    return flags;
}
} // namespace sharp_retro
#endif

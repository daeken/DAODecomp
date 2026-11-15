#include "runtime.hpp"
#if defined(_WIN32) && defined(__i386__) && defined(RECOMP_NATIVE_EXECUTION)
namespace sharp_retro {
namespace {
unsigned simd_width(unsigned op){
    if(op==1||op==2||op==3||op==4||(op>=10&&op<=13)||op==33||op==34||op==39||(op>=60&&op<=62)||op==70||op==71||op==85||op==89||op==90||(op>=93&&op<=98))return 64;
    if(op==23)return 16;if(op==24||op==25||op==48||op==49||op==50||op==51||op==56||op==57||op==63||op==72||op==73||op==74||op==75||op==86||op==91||op==92)return 32;return 128;
}
bits simd_fp(State& state,unsigned op,bits left,bits right,unsigned immediate=0) {
    if(state.mxcsr_defined!=0xffffffffu||!state.mxcsr_mask||(state.mxcsr&~state.mxcsr_mask))
        throw std::runtime_error("unknown or invalid MXCSR in native SIMD operation");
    if((state.mxcsr&0x1f80u)!=0x1f80u)
        throw std::runtime_error("unmasked SIMD exceptions require delivery modeling");
    // Distinct members prevent the compiler from overlapping saved/input/output
    // storage. All physical FP work and host restoration occur in one asm block.
    struct alignas(16) Frame {std::array<std::uint64_t,2> left,right,result;std::uint32_t guest,host,after;} frame{};
    frame.guest=state.mxcsr;std::memcpy(frame.left.data(),&left,16);std::memcpy(frame.right.data(),&right,16);
#define SIMD_FP(INSTRUCTION) asm volatile( \
    "stmxcsr %0; ldmxcsr %3; movdqu %4,%%xmm0; movdqu %5,%%xmm1; " INSTRUCTION "; movdqu %%xmm0,%1; stmxcsr %2; ldmxcsr %0" \
    : "=m"(frame.host),"=m"(frame.result),"=m"(frame.after) \
    : "m"(frame.guest),"m"(frame.left),"m"(frame.right) : "xmm0","xmm1","eax","memory","cc")
    switch(op){
    case 10:SIMD_FP("mulsd %%xmm1,%%xmm0");break;
    case 11:SIMD_FP("addsd %%xmm1,%%xmm0");break;
    case 12:SIMD_FP("subsd %%xmm1,%%xmm0");break;
    case 13:SIMD_FP("divsd %%xmm1,%%xmm0");break;
    case 14:SIMD_FP("mulpd %%xmm1,%%xmm0");break;
    case 15:SIMD_FP("addpd %%xmm1,%%xmm0");break;
    case 16:SIMD_FP("subpd %%xmm1,%%xmm0");break;
    case 17:SIMD_FP("divpd %%xmm1,%%xmm0");break;
    case 33:SIMD_FP("cvtdq2pd %%xmm1,%%xmm0");break;
    case 34:SIMD_FP("cvtsd2si %%xmm1,%%eax; movd %%eax,%%xmm0");break;
    case 35:SIMD_FP("addps %%xmm1,%%xmm0");break;
    case 36:SIMD_FP("subps %%xmm1,%%xmm0");break;
    case 37:SIMD_FP("mulps %%xmm1,%%xmm0");break;
    case 38:SIMD_FP("divps %%xmm1,%%xmm0");break;
    case 39:SIMD_FP("cvttsd2si %%xmm1,%%eax; movd %%eax,%%xmm0");break;
    case 48:SIMD_FP("cvttss2si %%xmm1,%%eax; movd %%eax,%%xmm0");break;
    case 49:SIMD_FP("cvtss2si %%xmm1,%%eax; movd %%eax,%%xmm0");break;
    case 50:SIMD_FP("rcpss %%xmm1,%%xmm0");break;
    case 51:SIMD_FP("rsqrtss %%xmm1,%%xmm0");break;
    case 52:SIMD_FP("rcpps %%xmm1,%%xmm0");break;
    case 53:SIMD_FP("rsqrtps %%xmm1,%%xmm0");break;
    case 54:SIMD_FP("minps %%xmm1,%%xmm0");break;
    case 55:SIMD_FP("maxps %%xmm1,%%xmm0");break;
    case 56:SIMD_FP("minss %%xmm1,%%xmm0");break;
    case 57:SIMD_FP("maxss %%xmm1,%%xmm0");break;
    case 58:SIMD_FP("minpd %%xmm1,%%xmm0");break;
    case 59:SIMD_FP("maxpd %%xmm1,%%xmm0");break;
    case 60:SIMD_FP("minsd %%xmm1,%%xmm0");break;
    case 61:SIMD_FP("maxsd %%xmm1,%%xmm0");break;
    case 62:SIMD_FP("sqrtsd %%xmm1,%%xmm0");break;
    case 63:SIMD_FP("sqrtss %%xmm1,%%xmm0");break;
    case 64:SIMD_FP("sqrtpd %%xmm1,%%xmm0");break;
    case 65:SIMD_FP("sqrtps %%xmm1,%%xmm0");break;
    case 72:SIMD_FP("movd %%xmm1,%%eax; cvtsi2sd %%eax,%%xmm0");break;
    case 73:SIMD_FP("movd %%xmm1,%%eax; cvtsi2ss %%eax,%%xmm0");break;
    case 89:SIMD_FP("ucomisd %%xmm1,%%xmm0; pushfl; popl %%eax; movd %%eax,%%xmm0");break;
    case 90:SIMD_FP("comisd %%xmm1,%%xmm0; pushfl; popl %%eax; movd %%eax,%%xmm0");break;
    case 91:SIMD_FP("ucomiss %%xmm1,%%xmm0; pushfl; popl %%eax; movd %%eax,%%xmm0");break;
    case 92:SIMD_FP("comiss %%xmm1,%%xmm0; pushfl; popl %%eax; movd %%eax,%%xmm0");break;
    case 85:case 86:case 87:case 88:
        // Only the eight defined legacy predicates are admitted. The physical
        // instruction owns NaNs, signaling and sticky MXCSR flags.
#define SIMD_CMP(P) case P: if(op==85){SIMD_FP("cmpsd $" #P ",%%xmm1,%%xmm0");} \
        else if(op==86){SIMD_FP("cmpss $" #P ",%%xmm1,%%xmm0");} \
        else if(op==87){SIMD_FP("cmppd $" #P ",%%xmm1,%%xmm0");} \
        else {SIMD_FP("cmpps $" #P ",%%xmm1,%%xmm0");} break;
        switch(immediate){SIMD_CMP(0) SIMD_CMP(1) SIMD_CMP(2) SIMD_CMP(3) SIMD_CMP(4) SIMD_CMP(5) SIMD_CMP(6) SIMD_CMP(7)}
#undef SIMD_CMP
        break;
    default:throw std::runtime_error("unknown native SIMD floating operation");
    }
#undef SIMD_FP
    state.mxcsr=frame.after;bits result;std::memcpy(&result,frame.result.data(),16);return result;
}
}
void native_simd(Memory& memory,State& state,std::uint64_t pc,std::uint32_t descriptor,std::uint32_t address){
    unsigned op=descriptor&255,reg=(descriptor>>8)&7,rm=(descriptor>>11)&7,immediate=(descriptor>>16)&255;
    bool mem=(descriptor&0x4000)!=0;
    if((descriptor&0xff008000u)||!op||op>100||op==42||op==43||
       (immediate&&op!=18&&op!=19&&op!=22&&op!=23&&op!=26&&op!=69&&op!=85&&op!=86&&op!=87&&op!=88&&op!=100)||
       ((op==1||op==2)&&!mem)||((op==18||op==19||op==22||op==32)&&mem)||
       (op==18&&reg!=2)||(op==19&&reg!=6)||(op>=85&&op<=88&&immediate>7)||
       ((op==93||op==94)&&mem)||((op==95||op==96||op==97||op==98)&&!mem))throw std::runtime_error("unsupported native SIMD descriptor");
    unsigned width=simd_width(op);
    if(mem&&width==128&&op!=40&&op!=41&&op!=44&&op!=45&&(address&15u))throw GuestCpuFault("x86",13,pc);
    auto xmm=[&](unsigned index){return read_xmm128(state,index);};
    auto write_xmm=[&](unsigned index,bits value){state.xmm[index]=value;state.defined_xmm|=std::uint16_t(1u<<index);};
    auto write_gpr=[&](unsigned index,std::uint32_t value){state.gpr[index]=value;state.defined_gpr|=std::uint16_t(1u<<index);state.partial_gpr[index]=0;};
    auto source=[&](){return mem?memory.load(address,width):xmm(rm);};
    constexpr bits low64=(bits(1)<<64)-1;
    constexpr bits low32=0xffffffffu;
    if(op==1){auto right=source();auto left=xmm(reg);write_xmm(reg,(left&~low64)|(right&low64));return;}
    if(op==2){auto value=xmm(reg);memory.validate_store(address,64);memory.store(address,value,64);return;}
    if(op==3){auto right=source();auto left=mem?bits(0):xmm(reg);write_xmm(reg,(left&~low64)|(right&low64));return;}
    if(op==4){auto right=xmm(reg);if(mem){memory.validate_store(address,64);memory.store(address,right,64);}else write_xmm(rm,(xmm(rm)&~low64)|(right&low64));return;}
    if(op==70){write_xmm(reg,source()&low64);return;}
    if(op==71){auto right=xmm(reg)&low64;if(mem){memory.validate_store(address,64);memory.store(address,right,64);}else write_xmm(rm,right);return;}
    if(op==74){auto right=source();auto left=mem?bits(0):xmm(reg);write_xmm(reg,(left&~low32)|(right&low32));return;}
    if(op==75){auto right=xmm(reg);if(mem){memory.validate_store(address,32);memory.store(address,right,32);}else write_xmm(rm,(xmm(rm)&~low32)|(right&low32));return;}
    if(op==93){auto left=xmm(reg),right=xmm(rm);write_xmm(reg,(left&~low64)|(right>>64));return;}
    if(op==94||op==97){auto left=xmm(reg),right=source();write_xmm(reg,(left&low64)|(right<<64));return;}
    if(op==95){auto right=source();write_xmm(reg,(xmm(reg)&~low64)|(right&low64));return;}
    if(op==96||op==98){auto value=xmm(reg);memory.validate_store(address,64);memory.store(address,op==96?value:value>>64,64);return;}
    if(op==5||op==40||op==44||op==46){auto value=source();write_xmm(reg,value);return;}
    if(op==6||op==41||op==45||op==47){auto value=xmm(reg);if(mem){memory.validate_store(address,128);memory.store(address,value,128);}else write_xmm(rm,value);return;}
    if(op==22){write_gpr(reg,std::uint32_t(xmm(rm)>>(16*(immediate&7)))&0xffffu);return;}
    if(op==23){auto right=mem?memory.load(address,16):bits(read_gpr_mask(state,rm,0xffff));auto left=xmm(reg);unsigned shift=16*(immediate&7);write_xmm(reg,(left&~(bits(0xffff)<<shift))|((right&0xffff)<<shift));return;}
    if(op==24){auto value=mem?memory.load(address,32):bits(read_gpr_mask(state,rm,0xffffffffu));write_xmm(reg,value&0xffffffffu);return;}
    if(op==25){auto value=std::uint32_t(xmm(reg));if(mem){memory.validate_store(address,32);memory.store(address,value,32);}else write_gpr(rm,value);return;}
    if(op==32){auto value=xmm(rm);std::uint32_t mask=0;for(unsigned i=0;i<16;++i)mask|=std::uint32_t((value>>(8*i+7))&1)<<i;write_gpr(reg,mask);return;}
    if(op==26){auto value=source();bits result=0;for(unsigned i=0;i<4;++i)result|=bits(std::uint32_t(value>>(32*((immediate>>(i*2))&3))))<<(32*i);write_xmm(reg,result);return;}
    if(op==72||op==73){auto right=mem?memory.load(address,32):bits(read_gpr_mask(state,rm,0xffffffffu));auto left=xmm(reg);write_xmm(reg,simd_fp(state,op,left,right));return;}
    if(op==18||op==19){auto value=xmm(rm);bits result=0;for(unsigned i=0;i<2;++i){auto lane=std::uint64_t(value>>(64*i));auto shifted=immediate>=64?0:op==18?lane>>immediate:lane<<immediate;result|=bits(shifted)<<(64*i);}write_xmm(rm,result);return;}
    if(!mem&&reg==rm&&(op==9||op==30||op==81||op==84)){write_xmm(reg,op==30?~bits(0):bits(0));return;}
    auto right=source();
    if(op==33||op==34||op==39||op==48||op==49){auto result=simd_fp(state,op,0,right);if(op==33)write_xmm(reg,result);else write_gpr(reg,std::uint32_t(result));return;}
    auto left=xmm(reg);bits result=0;
    if(op>=89&&op<=92){auto flags=std::uint32_t(simd_fp(state,op,left,right));state.flags=(state.flags&~std::uint64_t(0x8d5u))|(flags&0x8d5u);state.defined_flags|=0x8d5u;for(unsigned bit=0;bit<32;++bit)if(0x8d5u&(1u<<bit))state.flag_origins[bit]=0;return;}
    if((op>=10&&op<=17) || (op>=35&&op<=38) || (op>=50&&op<=65) || (op>=85&&op<=88)){write_xmm(reg,simd_fp(state,op,left,right,immediate));return;}
    switch(op){
    case 7:result=left&right;break;case 8:result=left|right;break;case 9:result=left^right;break;
    case 20:case 21:{auto count=std::uint64_t(right);for(unsigned i=0;i<2;++i){auto lane=std::uint64_t(left>>(64*i));auto shifted=count>=64?0:op==20?lane>>count:lane<<count;result|=bits(shifted)<<(64*i);}break;}
    case 27:result=(left&low64)|(right<<64);break;
    case 28:for(unsigned i=0;i<2;++i)result|=bits(std::uint64_t(left>>(64*i))-std::uint64_t(right>>(64*i)))<<(64*i);break;
    case 29:for(unsigned i=0;i<4;++i)result|=bits(std::uint32_t(std::uint32_t(left>>(32*i))-std::uint32_t(right>>(32*i))))<<(32*i);break;
    case 30:for(unsigned i=0;i<4;++i)if(std::uint32_t(left>>(32*i))==std::uint32_t(right>>(32*i)))result|=bits(0xffffffffu)<<(32*i);break;
    case 31:for(unsigned i=0;i<8;++i){auto a=std::uint16_t(left>>(16*i)),b=std::uint16_t(right>>(16*i));result|=bits((a^0x8000u)>(b^0x8000u)?a:b)<<(16*i);}break;
    case 66:result=(left>>64)|(right&~low64);break;
    case 67:case 68:for(unsigned i=0;i<2;++i){unsigned lane=i+(op==68?2u:0u);result|=bits(std::uint32_t(left>>(32*lane)))<<(64*i);result|=bits(std::uint32_t(right>>(32*lane)))<<(64*i+32);}break;
    case 69:for(unsigned i=0;i<4;++i){auto value=i<2?left:right;result|=bits(std::uint32_t(value>>(32*((immediate>>(2*i))&3))))<<(32*i);}break;
    case 76:case 77:case 79:result=(~left)&right;break;
    case 78:case 82:result=left&right;break;
    case 80:case 83:result=left|right;break;
    case 81:case 84:result=left^right;break;
    case 99:for(unsigned i=0;i<2;++i)result|=bits(std::uint64_t(left>>(64*i))+std::uint64_t(right>>(64*i)))<<(64*i);break;
    case 100:result=((left>>(64*(immediate&1u)))&low64)|((right>>(64*((immediate>>1)&1u)))<<64);break;
    default:throw std::runtime_error("unimplemented native SIMD operation");
    }
    write_xmm(reg,result);
}
}
#endif

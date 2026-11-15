// Literal-byte division-pop references for the instruction reached at main 0x4cb1b0.
#include "x87_unordered_control.inc"
static void divide_pop_reference(unsigned form,unsigned index) {
#define RAW_DIV_POP(I) case I: if(form==0) asm volatile(".byte 0xde,0xf8+" #I : : : "memory"); \
    else asm volatile(".byte 0xde,0xf0+" #I : : : "memory");break;
    switch(index){RAW_DIV_POP(0) RAW_DIV_POP(1) RAW_DIV_POP(2) RAW_DIV_POP(3) RAW_DIV_POP(4) RAW_DIV_POP(5) RAW_DIV_POP(6) RAW_DIV_POP(7)}
#undef RAW_DIV_POP
}
int main() {
    if(auto result=unordered_control())return result;
    DebugMemory memory;memory.map_bytes("stack",0x8000,0x1000,true,true);memory.seal();memory.store(0x8800,0x12345678,32);
    sharp_retro::State host;recomp_generated::capture_native_fp(host);unsigned cases=0,mismatches=0,guards=0;
    for(unsigned form=0;form<16;++form)for(unsigned top:{0u,3u,7u})for(unsigned pattern=0;pattern<9;++pattern)
    for(unsigned mode=0;mode<4;++mode)for(unsigned rounding=0;rounding<4;++rounding) for(unsigned precision:{0u,2u,3u}) {
        unsigned index=form&7;
        auto expected=host;expected.x87_control=std::uint16_t(0x7f|(precision<<8)|(rounding<<10));expected.x87_status=std::uint16_t(0x4700|(top<<11));expected.x87_tag=0;expected.defined_x87_st=0xff;
        for(unsigned i=0;i<8;++i)raw(expected,i,0x8000000000000000ULL|(std::uint64_t(i)<<59),std::uint16_t(0x3fff|((i&1)<<15)));
        if(pattern==1)raw(expected,0,0,0);
        if(pattern==2)raw(expected,0,0,0x8000);
        if(pattern==3)raw(expected,0,0x8000000000000000ULL,0x7fff);
        if(pattern==4)raw(expected,0,0xc000000000001234ULL,0x7fff);
        if(pattern==5)raw(expected,0,0x8000000000001234ULL,0x7fff);
        if(pattern==6)raw(expected,0,1,0);
        if(pattern==7)raw(expected,0,0x8000000000000000ULL,0xbfff);
        if(pattern==8)raw(expected,index,0xc000000000001234ULL,0x7fff);
        for(unsigned i=0;i<8;++i){std::uint64_t frac;std::uint16_t exp;std::memcpy(&frac,expected.x87_st[i].data(),8);std::memcpy(&exp,expected.x87_st[i].data()+8,2);
            unsigned value=!(exp&0x7fff) ? (frac ? 2u:1u) : (exp&0x7fff)==0x7fff ? 2u:0u;expected.x87_tag|=std::uint16_t(value<<(((top+i)&7)*2));}
        if(mode&1)expected.x87_tag|=std::uint16_t(3u<<(top*2));
        if(mode&2)expected.x87_tag|=std::uint16_t(3u<<(((top+index)&7)*2));
        auto candidate=expected;{recomp_generated::NativeFloatingScope scope(expected,false);divide_pop_reference(form/8,index);scope.finish();}
        candidate.gpr[4]=0x8800;auto flags=candidate.flags;auto known=candidate.defined_flags;std::uint64_t budget=10;
        auto result=recomp_generated::execute_guest(0x401600+form*16,0x12345678,candidate,memory,budget);
        bool match=result==sharp_retro::Exit::returned && candidate.gpr[4]==0x8804 && candidate.flags==flags && candidate.defined_flags==known && candidate.defined_x87_st==0xff && same(expected,candidate);
        ++cases;if(!match){++mismatches;if(mismatches<5)std::fprintf(stderr,"divide-pop form=%u top=%u pattern=%u mode=%u SW=%04x/%04x TAG=%04x/%04x\n",form,top,pattern,mode,expected.x87_status,candidate.x87_status,expected.x87_tag,candidate.x87_tag);}
    }
    for(unsigned form=0;form<16;++form)for(unsigned mode=0;mode<2;++mode){
        auto state=host;state.x87_control=mode ? 0x37f:0x37e;state.x87_status=0;state.x87_tag=0;state.defined_x87_st=mode ? 0xfe:0xff;
        for(unsigned i=0;i<8;++i)raw(state,i,0x8000000000000000ULL,0x3fff);auto before=state;
        auto opcode=std::uint16_t(form<8 ? 0x6f8+form : 0x6f0+(form&7));
        try{recomp_generated::execute_native_x87(memory,recomp_generated::native_encoded_x87,state,0x401600,0,opcode);}
        catch(const std::runtime_error&){if(same(state,before) && state.defined_x87_st==before.defined_x87_st)++guards;}
    }
    for(unsigned opcode:{0x86f0u,0x86f8u,0x6e0u,0u,0x7fffu}) {
        auto state=host;auto before=state;
        try{recomp_generated::execute_native_x87(memory,recomp_generated::native_encoded_x87,state,0x401600,0,std::uint16_t(opcode));}
        catch(const std::runtime_error&){if(same(state,before) && state.defined_x87_st==before.defined_x87_st)++guards;}
    }
    {auto state=host;auto before=state;
     try{recomp_generated::execute_native_x87(memory,static_cast<sharp_retro::X87Op>(0x7ffe),state,0x401600,0,0);}
     catch(const std::runtime_error&){if(same(state,before) && state.defined_x87_st==before.defined_x87_st)++guards;}}
    sharp_retro::State after;recomp_generated::capture_native_fp(after);bool restored=same(host,after);
    std::printf("{\"native_division_pop_cases\":%u,\"mismatches\":%u,\"failure_guards\":%u,\"host_fp_restored\":%s}\n",cases,mismatches,guards,restored ? "true":"false");
    return mismatches || guards!=38 || !restored ? 1:0;
}

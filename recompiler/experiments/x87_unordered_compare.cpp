// Independently encoded x87 status comparisons needed by main 0x5ddbcc.
#include "x87_memory_control.inc"
static void unordered_reference(unsigned form,unsigned index) {
    if(form==16){asm volatile(".byte 0xde,0xd9" : : : "memory");return;}
    if(form==17){asm volatile(".byte 0xda,0xe9" : : : "memory");return;}
#define RAW_UNORDERED(I) case I: if(form<8) asm volatile(".byte 0xdd,0xe0+" #I : : : "memory"); \
    else asm volatile(".byte 0xdd,0xe8+" #I : : : "memory");break;
    switch(index){RAW_UNORDERED(0) RAW_UNORDERED(1) RAW_UNORDERED(2) RAW_UNORDERED(3) RAW_UNORDERED(4) RAW_UNORDERED(5) RAW_UNORDERED(6) RAW_UNORDERED(7)}
#undef RAW_UNORDERED
}
int main() {
    if(auto result=memory_control())return result;
    DebugMemory memory;memory.map_bytes("stack",0x8000,0x1000,true,true);memory.seal();memory.store(0x8800,0x12345678,32);
    sharp_retro::State host;recomp_generated::capture_native_fp(host);unsigned cases=0,mismatches=0,guards=0;
    for(unsigned form=0;form<18;++form)for(unsigned top:{0u,3u,7u})for(unsigned pattern=0;pattern<9;++pattern)
    for(unsigned mode=0;mode<4;++mode)for(unsigned rounding=0;rounding<4;++rounding) {
        unsigned index=form<16 ? form&7 : 1u;
        auto expected=host;expected.x87_control=std::uint16_t(0x37f|(rounding<<10));expected.x87_status=std::uint16_t(0x4700|(top<<11));expected.x87_tag=0;expected.defined_x87_st=0xff;
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
        auto candidate=expected;{recomp_generated::NativeFloatingScope scope(expected,false);unordered_reference(form,index);scope.finish();}
        candidate.gpr[4]=0x8800;auto flags=candidate.flags;auto known=candidate.defined_flags;std::uint64_t budget=10;
        auto result=recomp_generated::execute_guest(0x401400+form*16,0x12345678,candidate,memory,budget);
        bool match=result==sharp_retro::Exit::returned && candidate.gpr[4]==0x8804 && candidate.flags==flags && candidate.defined_flags==known && candidate.defined_x87_st==0xff && same(expected,candidate);
        ++cases;if(!match){++mismatches;if(mismatches<5)std::fprintf(stderr,"unordered form=%u top=%u pattern=%u mode=%u SW=%04x/%04x TAG=%04x/%04x\n",form,top,pattern,mode,expected.x87_status,candidate.x87_status,expected.x87_tag,candidate.x87_tag);}
    }
    for(unsigned form=0;form<18;++form)for(unsigned mode=0;mode<2;++mode){
        auto state=host;state.x87_control=mode ? 0x37f:0x37e;state.x87_status=0;state.x87_tag=0;state.defined_x87_st=mode ? 0xfe:0xff;
        for(unsigned i=0;i<8;++i)raw(state,i,0x8000000000000000ULL,0x3fff);auto before=state;
        auto opcode=std::uint16_t(form<8 ? 0x5e0+form : form<16 ? 0x5e8+(form&7) : form==16 ? 0x6d9:0x2e9);
        try{recomp_generated::execute_native_x87(memory,recomp_generated::native_encoded_x87,state,0x401400,0,opcode);}
        catch(const std::runtime_error&){if(same(state,before) && state.defined_x87_st==before.defined_x87_st)++guards;}
    }
    for(unsigned opcode:{0x85e0u,0x85e8u,0x5f0u,0u,0x7fffu}) {
        auto state=host;auto before=state;
        try{recomp_generated::execute_native_x87(memory,recomp_generated::native_encoded_x87,state,0x401400,0,std::uint16_t(opcode));}
        catch(const std::runtime_error&){if(same(state,before) && state.defined_x87_st==before.defined_x87_st)++guards;}
    }
    {auto state=host;auto before=state;
     try{recomp_generated::execute_native_x87(memory,static_cast<sharp_retro::X87Op>(0x7ffe),state,0x401400,0,0);}
     catch(const std::runtime_error&){if(same(state,before) && state.defined_x87_st==before.defined_x87_st)++guards;}}
    sharp_retro::State after;recomp_generated::capture_native_fp(after);bool restored=same(host,after);
    std::printf("{\"native_unordered_and_double_pop_cases\":%u,\"mismatches\":%u,\"failure_guards\":%u,\"host_fp_restored\":%s}\n",cases,mismatches,guards,restored ? "true":"false");
    return mismatches || guards!=42 || !restored ? 1:0;
}

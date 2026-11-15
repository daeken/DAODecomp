// Memory arithmetic needed by main 0xa3cfe6 and related operand forms.
// Independent reference bytes, exact memory width and full raw FP state.
#include "x87_clock_control.inc"
static void arithmetic_memory_reference(unsigned form,std::uint32_t word,std::uint64_t quad) {
    switch(form) {
    case 0:asm volatile(".byte 0xd8,0x00" : : "a"(&word) : "memory");break;
    case 1:asm volatile(".byte 0xd8,0x20" : : "a"(&word) : "memory");break;
    case 2:asm volatile(".byte 0xd8,0x28" : : "a"(&word) : "memory");break;
    case 3:asm volatile(".byte 0xdc,0x28" : : "a"(&quad) : "memory");break;
    case 4:asm volatile(".byte 0xd8,0x30" : : "a"(&word) : "memory");break;
    case 5:asm volatile(".byte 0xd8,0x38" : : "a"(&word) : "memory");break;
    }
}
int main() {
    if(auto result=clock_control()) return result;
    CompareMemory memory;memory.map_bytes("ram",0x8000,0x2000,true,true);memory.seal();memory.store(0x8800,0x12345678,32);
    sharp_retro::State host;recomp_generated::capture_native_fp(host);
    const std::uint32_t words[]={0,0x80000000u,0x3f800000u,0xbf800000u,0x40000000u,0x7f800000u,0x7fc01234u,0x7f801234u,1};
    const std::uint64_t quads[]={0,0x8000000000000000ULL,0x3ff0000000000000ULL,0xbff0000000000000ULL,0x4000000000000000ULL,0x7ff0000000000000ULL,0x7ff8000000001234ULL,0x7ff0000000001234ULL,1};
    unsigned cases=0,mismatches=0,guards=0;
    for(unsigned form=0;form<6;++form) for(unsigned top=0;top<8;++top) for(unsigned precision:{0u,2u,3u})
    for(unsigned rounding=0;rounding<4;++rounding) for(unsigned pattern=0;pattern<9;++pattern)
    for(unsigned operand=0;operand<9;++operand) for(bool empty:{false,true}) {
        auto expected=host;expected.x87_control=std::uint16_t(0x7f|(precision<<8)|(rounding<<10));
        expected.x87_status=std::uint16_t(0x4700|(top<<11));expected.x87_tag=0;expected.defined_x87_st=0xff;
        for(unsigned i=0;i<8;++i) raw(expected,i,0x8000000000000000ULL|(std::uint64_t(i)<<59),std::uint16_t(0x3fff|((i&1)<<15)));
        if(pattern==1)raw(expected,0,0,0);
        if(pattern==2)raw(expected,0,0,0x8000);
        if(pattern==3)raw(expected,0,0x8000000000000000ULL,0x7fff);
        if(pattern==4)raw(expected,0,0xc000000000001234ULL,0x7fff);
        if(pattern==5)raw(expected,0,0x8000000000001234ULL,0x7fff);
        if(pattern==6)raw(expected,0,1,0);
        if(pattern==7)raw(expected,0,0x8000000000000000ULL,0xbfff);
        unsigned tag=pattern==1 || pattern==2 ? 1u : pattern>=3 && pattern<=6 ? 2u : 0u;
        expected.x87_tag|=std::uint16_t((empty ? 3u:tag)<<(top*2));
        auto candidate=expected;
        {recomp_generated::NativeFloatingScope scope(expected,false);arithmetic_memory_reference(form,words[operand],quads[operand]);scope.finish();}
        auto payload=form==3 ? quads[operand] : 0x5a5a5a5a00000000ULL|words[operand];memory.store(0x9001,payload,64);
        candidate.gpr[0]=0x9001;candidate.gpr[4]=0x8800;auto before=candidate;
        memory.reads=memory.writes=0;memory.tracing=true;std::uint64_t budget=10;
        auto result=recomp_generated::execute_guest(0x401710+form*16,0x12345678,candidate,memory,budget);memory.tracing=false;
        bool registers=true;for(unsigned i=0;i<16;++i)if(candidate.gpr[i]!=(i==4 ? before.gpr[i]+4:before.gpr[i]))registers=false;
        bool match=result==sharp_retro::Exit::returned && registers && candidate.flags==before.flags && candidate.defined_flags==before.defined_flags &&
            candidate.defined_x87_st==0xff && same(expected,candidate) && memory.reads==1 && memory.last_width==(form==3 ? 64u:32u) && !memory.writes && memory.load(0x9001,64)==payload;
        ++cases;if(!match){++mismatches;if(mismatches<5)std::fprintf(stderr,"memory arithmetic form=%u top=%u pattern=%u operand=%u empty=%u SW=%04x/%04x TAG=%04x/%04x\n",form,top,pattern,operand,unsigned(empty),expected.x87_status,candidate.x87_status,expected.x87_tag,candidate.x87_tag);}
    }
    for(unsigned form=0;form<6;++form) for(unsigned mode=0;mode<4;++mode) {
        auto state=host;state.x87_control=mode==0 ? 0x37e:0x37f;state.x87_status=0;state.x87_tag=0xfffc;state.defined_x87_st=mode==1 ? 0xfe:0xff;
        raw(state,0,0x8000000000000000ULL,0x4000);auto before=state;
        {auto setup=host;recomp_generated::NativeFloatingScope fixture(setup,false);memory.forget_unknown_range(0x9001,8);memory.store(0x9001,0,64);if(mode==2)memory.store_unknown(0x9001,0,64);}
        const std::uint16_t opcodes[]={0,0x20,0x28,0x428,0x30,0x38};
        memory.writes=0;memory.tracing=true;
        try {recomp_generated::execute_native_x87(memory,recomp_generated::native_encoded_x87,state,0x401710,mode==3 ? 0xdeadbeef:0x9001,opcodes[form]);}
        catch(const std::runtime_error&){if(same(before,state) && before.defined_x87_st==state.defined_x87_st && !memory.writes)++guards;}
        memory.tracing=false;
    }
    for(unsigned opcode:{0x8000u,0xc0u,0x100u,0x420u,0x380u}) {
        auto state=host;auto before=state;
        try{recomp_generated::execute_native_x87(memory,recomp_generated::native_encoded_x87,state,0x401710,0x9001,std::uint16_t(opcode));}
        catch(const std::runtime_error&){if(same(state,before)&&state.defined_x87_st==before.defined_x87_st)++guards;}
    }
    sharp_retro::State after;recomp_generated::capture_native_fp(after);bool restored=same(host,after);
    std::printf("{\"native_memory_arithmetic_cases\":%u,\"mismatches\":%u,\"failure_guards\":%u,\"host_fp_restored\":%s}\n",cases,mismatches,guards,restored ? "true":"false");
    return mismatches || guards!=29 || !restored ? 1:0;
}

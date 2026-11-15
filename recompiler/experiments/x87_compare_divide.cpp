// Debug the exact register operations reached at main 0x411650.
#include "functions.hpp"
#include "image_memory.hpp"
#include "native_x87.hpp"
#include <cstdio>
#include <cstring>
struct DebugMemory : recomp_generated::ImageMemory {
    void execute_x87(sharp_retro::X87Op op,sharp_retro::State& s,std::uint64_t pc,std::uint32_t address,std::uint16_t opcode) override {
        recomp_generated::execute_native_x87(*this,op,s,pc,address,opcode);
    }
};
static bool same(const sharp_retro::State& a,const sharp_retro::State& b) {
    return a.x87_control==b.x87_control && a.x87_status==b.x87_status && a.x87_tag==b.x87_tag && a.mxcsr==b.mxcsr && a.x87_st==b.x87_st;
}
static void raw(sharp_retro::State& s,unsigned i,std::uint64_t fraction,std::uint16_t exponent) {
    std::memcpy(s.x87_st[i].data(),&fraction,8);std::memcpy(s.x87_st[i].data()+8,&exponent,2);
}
static void reference(unsigned family,unsigned index) {
#define RAW(I) case I: if(family==0) asm volatile(".byte 0xd8,0xd0+" #I : : : "memory"); \
    else if(family==1) asm volatile(".byte 0xd8,0xd8+" #I : : : "memory"); \
    else asm volatile(".byte 0xdc,0xf8+" #I : : : "memory"); break;
    if(family==3) {asm volatile(".byte 0xd9,0xe0" : : : "memory");return;}
    switch(index) {RAW(0) RAW(1) RAW(2) RAW(3) RAW(4) RAW(5) RAW(6) RAW(7)}
#undef RAW
}
int main() {
    DebugMemory memory;memory.map_bytes("stack",0x8000,0x1000,true,true);memory.seal();memory.store(0x8800,0x12345678,32);
    sharp_retro::State host;recomp_generated::capture_native_fp(host);
    unsigned cases=0,mismatches=0,guards=0;
    for(unsigned family=0;family<4;++family) for(unsigned index=0;index<(family==3 ? 1u:8u);++index)
    for(unsigned top:{0u,3u,7u}) for(unsigned pattern=0;pattern<9;++pattern)
    for(unsigned mode=0;mode<4;++mode) for(unsigned rounding=0;rounding<4;++rounding) {
        auto expected=host;expected.x87_control=std::uint16_t(0x37f|(rounding<<10));expected.x87_status=std::uint16_t(0x4700|(top<<11));
        expected.x87_tag=0;expected.defined_x87_st=0xff;
        for(unsigned i=0;i<8;++i) raw(expected,i,0x8000000000000000ULL|(std::uint64_t(i)<<59),std::uint16_t(0x3fff|((i&1)<<15)));
        // Unequal finite values expose reversed register-division operands.
        raw(expected,0,0x8000000000000000ULL,0x4000);
        if(pattern==1) raw(expected,0,0,0);
        if(pattern==2) raw(expected,0,0,0x8000);
        if(pattern==3) raw(expected,0,0x8000000000000000ULL,0x7fff);
        if(pattern==4) raw(expected,0,0xc000000000001234ULL,0x7fff);
        if(pattern==5) raw(expected,0,0x8000000000001234ULL,0x7fff);
        if(pattern==6) raw(expected,0,1,0);
        if(pattern==7) raw(expected,0,0x8000000000000000ULL,0xbfff);
        if(pattern==8) raw(expected,index,0x8000000000000000ULL,0x4000);
        // Supply explicit initial value classes for FRSTOR; empty classes below
        // are deliberate masked-underflow cases with retained raw payloads.
        for(unsigned i=0;i<8;++i) {
            std::uint64_t frac;std::uint16_t exp;std::memcpy(&frac,expected.x87_st[i].data(),8);std::memcpy(&exp,expected.x87_st[i].data()+8,2);
            unsigned value=!(exp&0x7fff) ? (frac ? 2u:1u) : (exp&0x7fff)==0x7fff ? 2u:0u;
            expected.x87_tag|=std::uint16_t(value<<((((top+i)&7)*2)));
        }
        if(mode&1) expected.x87_tag|=std::uint16_t(3u<<((top&7)*2));
        if(mode&2) expected.x87_tag|=std::uint16_t(3u<<(((top+index)&7)*2));
        auto candidate=expected;
        {recomp_generated::NativeFloatingScope scope(expected,false);reference(family,index);scope.finish();}
        candidate.gpr[4]=0x8800;auto flags=candidate.flags;auto defined=candidate.defined_flags;std::uint64_t budget=10;
        auto result=recomp_generated::execute_guest(0x401000+(family*8+index)*16,0x12345678,candidate,memory,budget);
        bool match=result==sharp_retro::Exit::returned && candidate.gpr[4]==0x8804 && candidate.defined_x87_st==0xff &&
            candidate.flags==flags && candidate.defined_flags==defined && same(expected,candidate);
        ++cases;if(!match) {++mismatches;if(mismatches<5) std::fprintf(stderr,"family=%u index=%u top=%u pattern=%u mode=%u SW=%04x/%04x TAG=%04x/%04x\n",family,index,top,pattern,mode,expected.x87_status,candidate.x87_status,expected.x87_tag,candidate.x87_tag);}
    }
    for(unsigned family=0;family<4;++family) for(unsigned mode=0;mode<2;++mode) {
        auto state=host;state.x87_control=mode ? 0x37f:0x37e;state.x87_status=0;state.x87_tag=0xfff0;state.defined_x87_st=mode ? 0xfe:0xff;
        raw(state,0,0x8000000000000000ULL,0x4000);raw(state,1,0x8000000000000000ULL,0x4001);auto before=state;
        auto op=family==0 ? sharp_retro::X87Op::fcom_st1 : family==1 ? sharp_retro::X87Op::fcomp_st1 : family==2 ? sharp_retro::X87Op::fdiv_sti_1 : sharp_retro::X87Op::fchs;
        try {recomp_generated::execute_native_x87(memory,op,state,0x401100,0,0);}
        catch(const std::runtime_error&) {if(same(before,state) && before.defined_x87_st==state.defined_x87_st) ++guards;}
    }
    sharp_retro::State after;recomp_generated::capture_native_fp(after);bool restored=same(host,after);
    std::printf("{\"native_compare_divide_sign_cases\":%u,\"mismatches\":%u,\"failure_guards\":%u,\"host_fp_restored\":%s}\n",cases,mismatches,guards,restored ? "true":"false");
    return mismatches || guards!=8 || !restored ? 1:0;
}

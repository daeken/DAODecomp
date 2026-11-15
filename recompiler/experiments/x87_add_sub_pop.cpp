// Debug reached FADDP/FSUBP register destinations using compiled native
// controls. Constructed instruction observations, not game-function acceptance.
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
static void raw(sharp_retro::State& s,unsigned i,std::uint64_t fraction,std::uint16_t exponent) {
    std::memcpy(s.x87_st[i].data(),&fraction,8); std::memcpy(s.x87_st[i].data()+8,&exponent,2);
}
static void tag(sharp_retro::State& s,unsigned i,unsigned value) {
    auto shift=((((s.x87_status>>11)&7)+i)&7)*2;
    s.x87_tag=std::uint16_t((s.x87_tag&~(3u<<shift))|(value<<shift));
}
static bool same(const sharp_retro::State& a,const sharp_retro::State& b,unsigned known=0xff) {
    if(a.x87_control!=b.x87_control || a.x87_status!=b.x87_status || a.x87_tag!=b.x87_tag || a.mxcsr!=b.mxcsr) return false;
    for(unsigned i=0;i<8;i++) if((known&(1u<<i)) && a.x87_st[i]!=b.x87_st[i]) return false;
    return true;
}
static void reference(sharp_retro::State& s,unsigned form,unsigned index,std::uint32_t input) {
    recomp_generated::NativeFloatingScope fp(s,false);
    (void)input;
    switch(index) {
// Original constructed opcode bytes supply the independent control. In
// particular, no shared AT&T operand spelling chooses the destination here.
#define REF(I) case I: if(form==0) asm volatile(".byte 0xde,0xc0+" #I : : : "memory"); \
                else asm volatile(".byte 0xde,0xe8+" #I : : : "memory"); break;
    REF(0) REF(1) REF(2) REF(3) REF(4) REF(5) REF(6) REF(7)
#undef REF
    }
    fp.finish();
}
int main() {
    sharp_retro::State host; recomp_generated::capture_native_fp(host);
    struct Value { std::uint64_t fraction; std::uint16_t exponent; std::uint32_t memory; unsigned tag; };
    const Value values[]={
      {0x8000000000000000ULL,0x4000,0x40400000,0}, // 2 * 3
      {0xaaaaaaaaaaaaaaabULL,0xbfff,0x3eaaaaab,0},
      {0,0,0x40400000,1},{0,0x8000,0xc0400000,1},
      {0x8000000000000000ULL,0x7fff,0,2},
      {0x8000000000000000ULL,0xffff,0xbf800000,2},
      {0xc000000000001234ULL,0x7fff,0x7fc05678,2},
      {0x8000000000001234ULL,0x7fff,0x7f805678,2},
      {1,0,1,2},
      {0xffffffffffffffffULL,0x7ffe,0x7f7fffff,0}
    };
    unsigned cases=0,unknown_cases=0,mismatches=0;
    for(unsigned form=0;form<2;form++) for(unsigned index=0;index<8;index++)
    for(unsigned top:{0u,3u,7u}) for(unsigned precision:{0u,2u,3u})
    for(unsigned rounding=0;rounding<4;rounding++) for(auto value:values) {
        auto expected=host;
        expected.x87_control=std::uint16_t(0x7f|(precision<<8)|(rounding<<10));
        expected.x87_status=std::uint16_t(0x4500|(top<<11)); expected.x87_tag=0;
        for(unsigned i=0;i<8;i++) raw(expected,i,0x8000000000000000ULL|(std::uint64_t(i)<<58),std::uint16_t(0x4000|((i&1)<<15)));
        raw(expected,0,value.fraction,value.exponent); tag(expected,0,value.tag);
        if(index) { raw(expected,index,0xc000000000005678ULL,0x4000); tag(expected,index,0); }
        expected.defined_x87_st=0xff; auto candidate=expected;
        reference(expected,form,index,value.memory);
        DebugMemory memory;
        { auto setup=host; recomp_generated::NativeFloatingScope scope(setup,false);
          memory.map_bytes("stack",0x8000,0x1000,true,true); memory.map_bytes("exact m32 operand",0x9000,4,true,false,
              {reinterpret_cast<const std::uint8_t*>(&value.memory),4}); memory.seal(); memory.store(0x8800,0x12345678,32); }
        candidate.gpr[0]=0x9000; candidate.gpr[4]=0x8800;
        auto flags=candidate.flags,known_flags=candidate.defined_flags; std::uint64_t budget=10;
        auto exit=recomp_generated::execute_guest(0x401000+form*0x100+index*0x10,0x12345678,candidate,memory,budget);
        bool match=exit==sharp_retro::Exit::returned && budget==8 && candidate.gpr[4]==0x8804 && candidate.flags==flags &&
            candidate.defined_flags==known_flags && candidate.defined_x87_st==0xff && same(expected,candidate);
        ++cases;
        if(!match) { ++mismatches; if(mismatches<5) std::fprintf(stderr,"add/sub-pop mismatch form=%u index=%u TOP=%u PC=%u RC=%u SW=%04x/%04x TAG=%04x/%04x\n",form,index,top,precision,rounding,expected.x87_status,candidate.x87_status,expected.x87_tag,candidate.x87_tag); }
    }
    // Empty source/destination tags ignore their unknown raw payload. Untouched
    // empty slots retain unknownness; only the native-written destination is known.
    for(unsigned form=0;form<2;form++) for(unsigned index:{0u,1u,3u,7u})
    for(unsigned top:{0u,3u,7u}) for(unsigned empty=1;empty<4;empty++) {
        auto expected=host; expected.x87_control=0x37f; expected.x87_status=std::uint16_t(top<<11);expected.x87_tag=0; expected.defined_x87_st=0xff;
        for(unsigned i=0;i<8;i++) raw(expected,i,0x8000000000001234ULL,0x4000);
        if(empty&1) tag(expected,0,3);
        if(empty&2) tag(expected,index,3);
        auto candidate=expected;unsigned known=0xff;
        if(empty&1) known&=~1u;
        if(empty&2) known&=~(1u<<index);
        candidate.defined_x87_st=std::uint8_t(known); known|=1u<<index; known=((known>>1)|(known<<7))&0xff;
        reference(expected,form,index,0);
        DebugMemory memory;
        { auto setup=host; recomp_generated::NativeFloatingScope scope(setup,false); memory.map_bytes("stack",0x8000,0x1000,true,true);memory.seal();memory.store(0x8800,0x12345678,32); }
        candidate.gpr[4]=0x8800;std::uint64_t budget=10;
        auto exit=recomp_generated::execute_guest(0x401000+form*0x100+index*0x10,0x12345678,candidate,memory,budget);
        ++unknown_cases;
        if(exit!=sharp_retro::Exit::returned || candidate.defined_x87_st!=known || !same(expected,candidate,known)) ++mismatches;
    }
    unsigned refused=0;
    for(unsigned mode=0;mode<4;mode++) {
        auto s=host;s.x87_control=mode==0 ? 0x37b : 0x37f;s.x87_status=0;s.x87_tag=0;s.defined_x87_st=0xff;
        for(unsigned i=0;i<8;i++) raw(s,i,0x8000000000000000ULL,0x4000);
        if(mode==1) s.defined_x87_st&=~1u;
        if(mode==2) s.defined_x87_st&=~8u;
        if(mode==3) s.x87_control_defined=0xfffe;
        auto before=s;DebugMemory memory;
        { auto setup=host;recomp_generated::NativeFloatingScope scope(setup,false);memory.map_bytes("operand",0x8000,4,true,true);memory.seal();memory.store(0x8000,0x40000000,32);if(mode==3)memory.store_unknown(0x8000,0,32); }
        try { recomp_generated::execute_native_x87(memory,sharp_retro::X87Op::fsubp_st3,s,0x401000,0x8000,0x6eb); }
        catch(const std::runtime_error&) { if(same(before,s) && before.defined_x87_st==s.defined_x87_st) ++refused; }
    }
    sharp_retro::State after;recomp_generated::capture_native_fp(after);bool restored=same(host,after);
    std::printf("{\"native_add_sub_pop_cases\":%u,\"unknown_empty_cases\":%u,\"mismatches\":%u,\"failure_guards\":%u,\"host_fp_restored\":%s}\n",cases,unknown_cases,mismatches,refused,restored ? "true" : "false");
    return mismatches || refused!=4 || !restored ? 1 : 0;
}

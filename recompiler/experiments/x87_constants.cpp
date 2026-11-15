// Constructed controls isolate constant precision/rounding and masked overflow.
// Reference uses opcode bytes; generated candidates use assembler mnemonics.
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
static bool same(const sharp_retro::State& a,const sharp_retro::State& b,unsigned known=0xff) {
    if(a.x87_control!=b.x87_control || a.x87_status!=b.x87_status || a.x87_tag!=b.x87_tag || a.mxcsr!=b.mxcsr) return false;
    for(unsigned i=0;i<8;i++) if((known&(1u<<i)) && a.x87_st[i]!=b.x87_st[i]) return false;
    return true;
}
static void reference(sharp_retro::State& s,unsigned index) {
    recomp_generated::NativeFloatingScope fp(s,false);
    switch(index) {
#define REF(I) case I:asm volatile(".byte 0xd9,0xe8+" #I : : : "memory");break;
    REF(0) REF(1) REF(2) REF(3) REF(4) REF(5) REF(6)
#undef REF
    }
    fp.finish();
}
int main() {
    sharp_retro::State host;recomp_generated::capture_native_fp(host);
    DebugMemory memory;
    { auto setup=host;recomp_generated::NativeFloatingScope scope(setup,false);
      memory.map_bytes("stack",0x8000,0x1000,true,true);memory.seal();memory.store(0x8800,0x12345678,32); }
    unsigned cases=0,mismatches=0;
    for(unsigned index=0;index<7;index++) for(unsigned top=0;top<8;top++)
    for(unsigned precision:{0u,2u,3u}) for(unsigned rounding=0;rounding<4;rounding++)
    for(unsigned stack:{0u,1u,8u}) for(unsigned sticky:{0u,0x21u}) {
        auto expected=host;
        expected.x87_control=std::uint16_t(0x7f|(precision<<8)|(rounding<<10));
        expected.x87_status=std::uint16_t(0x4500|(top<<11)|sticky);expected.x87_tag=0xffff;
        for(unsigned i=0;i<8;i++) {
            std::uint64_t fraction=0x8000000000000000ULL|(std::uint64_t(i)<<58);std::uint16_t exponent=0x4000;
            std::memcpy(expected.x87_st[i].data(),&fraction,8);std::memcpy(expected.x87_st[i].data()+8,&exponent,2);
            if(i<stack) expected.x87_tag&=std::uint16_t(~(3u<<(((top+i)&7)*2)));
        }
        expected.defined_x87_st=0xff;auto candidate=expected;
        reference(expected,index);
        candidate.gpr[4]=0x8800;auto flags=candidate.flags,defined_flags=candidate.defined_flags;
        std::uint64_t budget=10;
        auto exit=recomp_generated::execute_guest(0x401000+index*8,0x12345678,candidate,memory,budget);
        // Empty physical payloads are unobservable; compare every live value.
        unsigned live=0;
        for(unsigned i=0;i<8;i++) if(((expected.x87_tag>>(((((expected.x87_status>>11)&7)+i)&7)*2))&3)!=3) live|=1u<<i;
        bool match=exit==sharp_retro::Exit::returned && budget==8 && candidate.gpr[4]==0x8804 &&
            candidate.flags==flags && candidate.defined_flags==defined_flags && candidate.defined_x87_st==0xff && same(expected,candidate,live);
        ++cases;
        if(!match) {++mismatches;if(mismatches<5)std::fprintf(stderr,"constant mismatch op=%u TOP=%u PC=%u RC=%u stack=%u sticky=%x SW=%04x/%04x TAG=%04x/%04x\n",index,top,precision,rounding,stack,sticky,expected.x87_status,candidate.x87_status,expected.x87_tag,candidate.x87_tag);}
    }
    unsigned refused=0;
    for(unsigned mode=0;mode<4;mode++) {
        auto s=host;s.x87_control=0x37f;s.x87_status=0;s.x87_tag=0xffff;s.defined_x87_st=0xff;
        if(mode==0)s.x87_control&=~1u;
        if(mode==1)s.x87_status=0x80;
        if(mode==2)s.x87_control_defined=0xfffe;
        auto before=s;
        try {recomp_generated::execute_native_x87(memory,recomp_generated::native_encoded_x87,s,0x401018,0,mode==3 ? 0x1ef : 0x1eb);}
        catch(const std::exception&) {if(same(before,s) && s.defined_x87_st==before.defined_x87_st)++refused;}
    }
    sharp_retro::State after;recomp_generated::capture_native_fp(after);bool restored=same(host,after);
    std::printf("{\"native_constant_cases\":%u,\"mismatches\":%u,\"failure_guards\":%u,\"host_fp_restored\":%s}\n",cases,mismatches,refused,restored ? "true" : "false");
    return mismatches || refused!=4 || !restored ? 1 : 0;
}

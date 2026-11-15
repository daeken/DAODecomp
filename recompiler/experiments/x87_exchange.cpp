// Native instruction debugging for the FXCH family needed by main VA 0x53ff80.
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
    return a.x87_control==b.x87_control && a.x87_status==b.x87_status &&
        a.x87_tag==b.x87_tag && a.mxcsr==b.mxcsr && a.x87_st==b.x87_st;
}
static void tag(sharp_retro::State& s,unsigned i,unsigned value) {
    auto shift=((((s.x87_status>>11)&7)+i)&7)*2;
    s.x87_tag=std::uint16_t((s.x87_tag&~(3u<<shift))|(value<<shift));
}
static void raw(sharp_retro::State& s,unsigned i,std::uint64_t fraction,std::uint16_t exponent) {
    std::memcpy(s.x87_st[i].data(),&fraction,8); std::memcpy(s.x87_st[i].data()+8,&exponent,2);
}
int main() {
    sharp_retro::State host; recomp_generated::capture_native_fp(host);
    unsigned cases=0,unknown_cases=0,mismatches=0;
    for(unsigned index=0;index<8;index++) for(unsigned top:{0u,3u,7u})
    for(unsigned pattern=0;pattern<2;pattern++) for(unsigned c1=0;c1<2;c1++)
    for(unsigned mode=0;mode<4;mode++) for(unsigned unknown=0;unknown<2;unknown++) {
        if(unknown && mode!=3) continue;
        auto expected=host; expected.x87_control=0x37f; expected.x87_status=std::uint16_t(0x4500|(c1<<9)|(top<<11));
        expected.x87_tag=0; expected.defined_x87_st=0xff;
        for(unsigned i=0;i<8;i++) raw(expected,i,0x8000000000000000ULL|(std::uint64_t(i)<<59),std::uint16_t(0x3fff|((i&1)<<15)));
        if(pattern) {
            raw(expected,0,0,0x8000); tag(expected,0,1);
            if(index) { raw(expected,index,0xc000000000001234ULL,0x7fff); tag(expected,index,2); }
        }
        if(mode&1) tag(expected,0,3);
        if(mode&2) tag(expected,index,3);
        auto candidate=expected;
        if(unknown) { candidate.defined_x87_st&=std::uint8_t(~(1u|(1u<<index))); ++unknown_cases; }
        {
            recomp_generated::NativeFloatingScope floating(expected,false);
            switch(index) {
            case 0: asm volatile("fxch %%st(0)" : : : "memory"); break;
            case 1: asm volatile("fxch %%st(1)" : : : "memory"); break;
            case 2: asm volatile("fxch %%st(2)" : : : "memory"); break;
            case 3: asm volatile("fxch %%st(3)" : : : "memory"); break;
            case 4: asm volatile("fxch %%st(4)" : : : "memory"); break;
            case 5: asm volatile("fxch %%st(5)" : : : "memory"); break;
            case 6: asm volatile("fxch %%st(6)" : : : "memory"); break;
            case 7: asm volatile("fxch %%st(7)" : : : "memory"); break;
            }
            floating.finish();
        }
        DebugMemory memory; memory.map_bytes("stack",0x8000,0x1000,true,true); memory.seal();
        candidate.gpr[4]=0x8800; memory.store(0x8800,0x12345678,32); auto flags=candidate.flags; auto known_flags=candidate.defined_flags;
        std::uint64_t budget=10; auto exit=recomp_generated::execute_guest(0x401000+index*32,0x12345678,candidate,memory,budget);
        bool match=exit==sharp_retro::Exit::returned && candidate.gpr[4]==0x8804 &&
            candidate.flags==flags && candidate.defined_flags==known_flags &&
            candidate.defined_x87_st==0xff && same(expected,candidate);
        ++cases;
        if(!match) { ++mismatches; if(mismatches<5) std::fprintf(stderr,"FXCH mismatch index=%u TOP=%u mode=%u unknown=%u TAG=%04x/%04x known=%02x\n",index,top,mode,unknown,expected.x87_tag,candidate.x87_tag,candidate.defined_x87_st); }
    }
    unsigned refused=0;
    for(unsigned mode=0;mode<2;mode++) {
        auto s=host; s.x87_control=mode ? 0x37f : 0x37b; s.x87_status=0; s.x87_tag=0xfff0; s.defined_x87_st=mode ? 0xfd : 0xff;
        raw(s,0,0x8000000000000000ULL,0x3fff); raw(s,1,0x8000000000000000ULL,0x4000);
        auto before=s; DebugMemory memory;
        try { recomp_generated::execute_native_x87(memory,sharp_retro::X87Op::fxch1,s,0x401100,0,0x1c9); }
        catch(const std::runtime_error&) { if(same(before,s) && before.defined_x87_st==s.defined_x87_st) ++refused; }
    }
    sharp_retro::State after; recomp_generated::capture_native_fp(after); bool restored=same(host,after);
    std::printf("{\"native_exchange_cases\":%u,\"unknown_empty_cases\":%u,\"mismatches\":%u,\"failure_guards\":%u,\"host_fp_restored\":%s}\n",cases,unknown_cases,mismatches,refused,restored ? "true" : "false");
    return mismatches || refused!=2 || !restored ? 1 : 0;
}

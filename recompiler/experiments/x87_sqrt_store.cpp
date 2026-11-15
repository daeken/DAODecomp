// Debug the FST m64 wrapper and sqrt helper selected by actual startup.
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
struct Value { std::uint64_t significand; std::uint16_t exponent; };
int main() {
    sharp_retro::State host; recomp_generated::capture_native_fp(host);
    const Value values[]={{0,0},{0,0x8000},{0x8000000000000000ULL,0x3fff},{0x8000000000000000ULL,0x4000},
        {0x8000000000000000ULL,0xbfff},{0x8000000000000000ULL,0x7fff},{0x8000000000000000ULL,0xffff},
        {0xc000000000001234ULL,0x7fff},{0x8000000000001234ULL,0x7fff},{1,0},
        {0x8000000000000001ULL,0x3fff},{0xffffffffffffffffULL,0x7ffe}};
    unsigned cases=0,mismatches=0;
    for(auto value:values) for(unsigned top:{0u,3u,7u}) for(unsigned precision:{0u,2u,3u})
    for(unsigned rounding=0;rounding<4;rounding++) for(unsigned form=0;form<3;form++) {
        std::array<std::uint8_t,10> raw{}; std::memcpy(raw.data(),&value.significand,8); std::memcpy(raw.data()+8,&value.exponent,2);
        auto expected=host; expected.x87_control=std::uint16_t(0x7f|(precision<<8)|(rounding<<10));
        expected.x87_status=std::uint16_t(0x120|(top<<11)); expected.x87_tag=0xffff; expected.defined_x87_st=0xff;
        for(auto& slot:expected.x87_st) { slot.fill(0); slot[7]=0x80; slot[8]=0xff; slot[9]=0x3f; }
        if(form==2) {
            expected.x87_st[0]=raw;
            auto exponent=value.exponent&0x7fff; unsigned tag=exponent==0 && !value.significand ? 1u : exponent==0 || exponent==0x7fff ? 2u : 0u;
            expected.x87_tag=std::uint16_t((expected.x87_tag&~(3u<<(top*2)))|(tag<<(top*2)));
        }
        auto candidate=expected; std::uint64_t output=0;
        {
            recomp_generated::NativeFloatingScope floating(expected,false);
            if(form==0) asm volatile("fldt %1\n\tfstl %0" : "=m"(output) : "m"(raw) : "memory");
            else if(form==1) asm volatile("fldt %1\n\tfsqrt\n\tfstl %0" : "=m"(output) : "m"(raw) : "memory");
            else asm volatile("fstl %0" : "=m"(output) : : "memory");
            floating.finish();
        }
        DebugMemory memory; memory.map_bytes("ram",0x8000,0x2000,true,true); memory.seal();
        for(unsigned i=0;i<raw.size();i++) memory.store(0x9000+i,raw[i],8);
        candidate.gpr[0]=0x9000; candidate.gpr[2]=0x9040; candidate.gpr[4]=0x8800;
        memory.store(0x8800,0x12345678,32); std::uint64_t budget=100;
        auto result=recomp_generated::execute_guest(0x401000+form*64,0x12345678,candidate,memory,budget);
        bool match=result==sharp_retro::Exit::returned && candidate.gpr[4]==0x8804 && candidate.defined_x87_st==0xff && same(expected,candidate) && memory.load(0x9040,64)==output;
        ++cases; if(!match) { ++mismatches; if(mismatches<4) std::fprintf(stderr,"sqrt/store mismatch form=%u TOP=%u PC=%u RC=%u SW=%04x/%04x\n",form,top,precision,rounding,expected.x87_status,candidate.x87_status); }
    }
    unsigned empty=0,refused=0;
    for(unsigned top:{0u,7u}) {
        auto expected=host; expected.x87_control=0x37f; expected.x87_status=std::uint16_t(top<<11); expected.x87_tag=0xffff; expected.defined_x87_st=0;
        auto candidate=expected; std::uint64_t output=0;
        { recomp_generated::NativeFloatingScope scope(expected,false); asm volatile("fstl %0" : "=m"(output) : : "memory"); scope.finish(); }
        DebugMemory memory; memory.map_bytes("output",0x8000,8,true,true); memory.seal();
        memory.execute_x87(sharp_retro::X87Op::fst64,candidate,0x401100,0x8000,0x512);
        if(!same(expected,candidate) || candidate.defined_x87_st || memory.load(0x8000,64)!=output) ++mismatches;
        ++empty;
    }
    for(unsigned mode=0;mode<4;mode++) {
        auto s=host; s.x87_control=0x37f; s.x87_status=0; s.x87_tag=0xfffc; s.defined_x87_st=mode==1 ? 0xfe : 0xff;
        s.x87_st[0].fill(0); s.x87_st[0][7]=0x80; s.x87_st[0][8]=0xff; s.x87_st[0][9]=0x3f;
        auto before=s; DebugMemory memory;
        { auto setup=host; recomp_generated::NativeFloatingScope fixture(setup,false);
          memory.map_bytes("operand",0x8000,mode==2 ? 8 : 16,true,mode!=0); memory.seal();
          if(mode==3) memory.store_unknown(0x8000,0,80); }
        try { memory.execute_x87(mode<2 ? sharp_retro::X87Op::fst64 : sharp_retro::X87Op::fld80,s,0x401100,0x8000,mode<2 ? 0x512 : 0x328); }
        catch(const std::runtime_error&) { if(same(before,s) && s.defined_x87_st==before.defined_x87_st) ++refused; }
    }
    sharp_retro::State after; recomp_generated::capture_native_fp(after); bool restored=same(host,after);
    std::printf("{\"native_load80_sqrt_store64_cases\":%u,\"empty_store_cases\":%u,\"mismatches\":%u,\"failure_guards\":%u,\"host_fp_restored\":%s}\n",cases,empty,mismatches,refused,restored ? "true" : "false");
    return mismatches || refused!=4 || !restored ? 1 : 0;
}

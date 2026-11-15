// Bounded check of the x87 integer/arithmetic sequence reached in Umbra startup.
#include "functions.hpp"
#include "image_memory.hpp"
#include "native_x87.hpp"
#include <cstdio>
struct DebugMemory : recomp_generated::ImageMemory {
    void execute_x87(sharp_retro::X87Op op,sharp_retro::State& state,std::uint64_t pc,std::uint32_t address,std::uint16_t opcode) override {
        recomp_generated::execute_native_x87(*this,op,state,pc,address,opcode);
    }
};
static bool same(const sharp_retro::State& a,const sharp_retro::State& b) {
    // Instructions execute at different addresses. Compare numeric data, tags,
    // status/control and MXCSR; opcode/instruction/data pointers are excluded.
    return a.x87_control==b.x87_control && a.x87_status==b.x87_status && a.x87_tag==b.x87_tag && a.mxcsr==b.mxcsr && a.x87_st==b.x87_st;
}
int main() {
    unsigned cases=0,mismatches=0;
    sharp_retro::State host; recomp_generated::capture_native_fp(host);
    const std::uint64_t subtract=0x3ff8000000000000ULL,multiply=0x4000000000000000ULL,divide=0x4008000000000000ULL,add=0x3fd0000000000000ULL;
    for(auto integer:{0u,1u,0xffffffffu,0x80000000u,0x7fffffffu,0x01000001u,0xfeffffffu,3u})
    for(unsigned top:{0u,3u,7u}) for(unsigned precision:{0u,2u,3u}) for(unsigned rounding=0;rounding<4;rounding++) for(unsigned width:{32u,64u}) {
        auto expected=host;
        expected.x87_control=std::uint16_t(0x7f|(precision<<8)|(rounding<<10)); expected.x87_status=std::uint16_t(0x120|(top<<11)); expected.x87_tag=0xffff;
        expected.defined_x87_st=0xff;
        for(unsigned i=0;i<8;i++) { expected.x87_st[i].fill(0); expected.x87_st[i][7]=0x80; expected.x87_st[i][8]=0xff; expected.x87_st[i][9]=0x3f; }
        auto candidate=expected; std::uint32_t output32=0; std::uint64_t output64=0;
        {
            recomp_generated::NativeFloatingScope floating(expected,false);
            if(width==32) asm volatile("fildl %1\n\tfsubl %2\n\tfmull %3\n\tfdivl %4\n\tfaddl %5\n\tfstps %0" : "=m"(output32) : "m"(integer),"m"(subtract),"m"(multiply),"m"(divide),"m"(add) : "memory");
            else asm volatile("fildl %1\n\tfsubl %2\n\tfmull %3\n\tfdivl %4\n\tfaddl %5\n\tfstpl %0" : "=m"(output64) : "m"(integer),"m"(subtract),"m"(multiply),"m"(divide),"m"(add) : "memory");
            floating.finish();
        }
        DebugMemory memory; memory.map_bytes("ram",0x8000,0x2000,true,true); memory.seal();
        memory.store(0x9000,integer,32); memory.store(0x9008,subtract,64); memory.store(0x9010,multiply,64); memory.store(0x9018,divide,64); memory.store(0x9020,add,64);
        candidate.gpr[0]=0x9000; candidate.gpr[2]=0x9040; candidate.gpr[4]=0x8800;
        memory.store(0x8800,0x12345678,32); std::uint64_t budget=100;
        auto result=recomp_generated::execute_guest(width==32 ? 0x401000 : 0x401080,0x12345678,candidate,memory,budget);
        bool match=result==sharp_retro::Exit::returned && candidate.gpr[4]==0x8804 && candidate.defined_x87_st==0xff && same(expected,candidate) && memory.load(0x9040,width)==(width==32 ? output32 : output64);
        ++cases; if(!match) { ++mismatches; if(mismatches<4) std::fprintf(stderr,"mismatch integer=%08x TOP=%u PC=%u RC=%u width=%u SW=%04x/%04x\n",integer,top,precision,rounding,width,expected.x87_status,candidate.x87_status); }
    }
    sharp_retro::State after; recomp_generated::capture_native_fp(after);
    bool restored=same(host,after);
    std::printf("{\"synthetic_arithmetic_cases\":%u,\"mismatches\":%u,\"host_fp_restored\":%s}\n",cases,mismatches,restored ? "true" : "false");
    return mismatches || !restored ? 1 : 0;
}

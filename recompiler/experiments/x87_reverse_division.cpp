// Debug the FDIVR m64 operation reached at original main VA 0x0054e842.
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
    // Different native instruction/operand addresses: those fields are excluded.
    return a.x87_control==b.x87_control && a.x87_status==b.x87_status &&
        a.x87_tag==b.x87_tag && a.mxcsr==b.mxcsr && a.x87_st==b.x87_st;
}
int main(int argc,char**) {
    sharp_retro::State host; recomp_generated::capture_native_fp(host);
    if(argc>1) {
        DebugMemory memory; memory.map_bytes("native shadow-memory control",0x8000,16,true,true); memory.seal();
        memory.store_unknown(0x8000,0,64);
        sharp_retro::State after; recomp_generated::capture_native_fp(after);
        std::printf("{\"shadow_memory_preparation_control\":true,\"mxcsr_before\":%u,\"mxcsr_after\":%u,\"raw_x87_preserved\":%s,\"host_fp_preserved\":%s}\n",host.mxcsr,after.mxcsr,host.x87_st==after.x87_st ? "true" : "false",same(host,after) ? "true" : "false");
        return 0;
    }
    bool traced=false;
    auto trace=[&](const char* stage) {
        if(traced) return;
        sharp_retro::State current; recomp_generated::capture_native_fp(current);
        if(!same(host,current)) { traced=true; std::fprintf(stderr,"first host FP change: %s\n",stage); }
    };
    struct Pair { std::uint64_t stack,memory; };
    const Pair pairs[]={
        {0x4000000000000000ULL,0x4020000000000000ULL}, // 8 / 2, not 2 / 8.
        {0xc000000000000000ULL,0x4020000000000000ULL},
        {0x4008000000000000ULL,0x3ff0000000000000ULL},
        {0,0x3ff0000000000000ULL},{0x8000000000000000ULL,0x3ff0000000000000ULL},
        {0,0},{0x7ff0000000000000ULL,0x4000000000000000ULL},
        {0x4000000000000000ULL,0x7ff0000000000000ULL},
        {0x7ff0000000000000ULL,0x7ff0000000000000ULL},
        {0x7ff8000000001234ULL,0x4000000000000000ULL},
        {0x7ff0000000001234ULL,0x4000000000000000ULL},
        {1,0x4000000000000000ULL}
    };
    unsigned cases=0,mismatches=0;
    for(auto operands:pairs) for(unsigned top:{0u,3u,7u})
    for(unsigned precision:{0u,2u,3u}) for(unsigned rounding=0;rounding<4;rounding++)
    for(unsigned form=0;form<3;form++) {
        trace("case entry");
        auto expected=host;
        expected.x87_control=std::uint16_t(0x7f|(precision<<8)|(rounding<<10));
        expected.x87_status=std::uint16_t(0x120|(top<<11)); expected.x87_tag=0xffff;
        expected.defined_x87_st=0xff;
        for(auto& value:expected.x87_st) { value.fill(0); value[7]=0x80; value[8]=0xff; value[9]=0x3f; }
        auto candidate=expected; std::uint32_t output32=0; std::uint64_t output64=0;
        {
            recomp_generated::NativeFloatingScope floating(expected,false);
            if(form==0) asm volatile("fldl %0\n\tfdivrl %1" : : "m"(operands.stack),"m"(operands.memory) : "memory");
            else if(form==1) asm volatile("fldl %1\n\tfdivrl %2\n\tfstps %0" : "=m"(output32) : "m"(operands.stack),"m"(operands.memory) : "memory");
            else asm volatile("fldl %1\n\tfdivrl %2\n\tfstpl %0" : "=m"(output64) : "m"(operands.stack),"m"(operands.memory) : "memory");
            floating.finish();
        }
        trace("direct native reference");
        DebugMemory memory; memory.map_bytes("ram",0x8000,0x2000,true,true); memory.seal();
        trace("memory preparation");
        memory.store(0x9000,operands.stack,64); memory.store(0x9008,operands.memory,64);
        candidate.gpr[0]=0x9000; candidate.gpr[2]=0x9040; candidate.gpr[4]=0x8800;
        memory.store(0x8800,0x12345678,32); std::uint64_t budget=100;
        auto result=recomp_generated::execute_guest(0x401000+form*64,0x12345678,candidate,memory,budget);
        trace("generated execution");
        bool match=result==sharp_retro::Exit::returned && candidate.gpr[4]==0x8804 &&
            candidate.defined_x87_st==0xff && same(expected,candidate) &&
            (!form || memory.load(0x9040,form==1 ? 32 : 64)==(form==1 ? output32 : output64));
        if(operands.stack==0x4000000000000000ULL && operands.memory==0x4020000000000000ULL)
            match=match && (form==0 || (form==1 ? output32==0x40800000u : output64==0x4010000000000000ULL));
        ++cases;
        if(!match) { ++mismatches; if(mismatches<4) std::fprintf(stderr,"FDIVR mismatch TOP=%u PC=%u RC=%u form=%u SW=%04x/%04x\n",top,precision,rounding,form,expected.x87_status,candidate.x87_status); }
    }
    unsigned refused=0;
    for(unsigned mode=0;mode<3;mode++) {
        trace("guard entry");
        auto state=host; state.x87_control=mode==0 ? 0x37b : 0x37f;
        state.x87_status=0; state.x87_tag=0xfffc; state.defined_x87_st=mode==1 ? 0xfe : 0xff;
        state.x87_st[0].fill(0); state.x87_st[0][7]=0x80; state.x87_st[0][8]=0xff; state.x87_st[0][9]=0x3f;
        auto before=state; DebugMemory memory;
        {
            // The host's hash-container growth uses FP during shadow-memory
            // setup. Insulate fixture preparation, retaining the full host-state
            // comparator around the actual operation and its refusal paths.
            auto setup=host; recomp_generated::NativeFloatingScope fixture(setup,false);
            memory.map_bytes("operand",0x8000,16,true,true); memory.seal();
            memory.store(0x8000,0x3ff0000000000000ULL,64);
            if(mode==2) memory.store_unknown(0x8000,0,64);
        }
        trace(mode==2 ? "unknown-memory fixture preparation" : "other guard preparation");
        try { recomp_generated::execute_native_x87(memory,sharp_retro::X87Op::fdivr64,state,0x401100,0x8000,0x478); }
        catch(const std::runtime_error&) { if(same(before,state) && state.defined_x87_st==before.defined_x87_st) ++refused; }
        trace("guard refusal");
    }
    sharp_retro::State after; recomp_generated::capture_native_fp(after); bool restored=same(host,after);
    if(!restored) {
        std::fprintf(stderr,"host FP CW=%04x/%04x SW=%04x/%04x TAG=%04x/%04x MXCSR=%08x/%08x\n",host.x87_control,after.x87_control,host.x87_status,after.x87_status,host.x87_tag,after.x87_tag,host.mxcsr,after.mxcsr);
        for(unsigned i=0;i<8;i++) if(host.x87_st[i]!=after.x87_st[i]) std::fprintf(stderr,"host raw logical ST(%u) changed\n",i);
    }
    std::printf("{\"native_reverse_division_cases\":%u,\"mismatches\":%u,\"failure_guards\":%u,\"host_fp_restored\":%s}\n",cases,mismatches,refused,restored ? "true" : "false");
    return mismatches || refused!=3 || !restored ? 1 : 0;
}

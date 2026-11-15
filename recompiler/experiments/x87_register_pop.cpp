// Bounded x87 register-store/pop debugging; no game-equivalence claim.
#include "native_x87.hpp"
#include "image_memory.hpp"
#include <cstdio>
struct DebugMemory : recomp_generated::ImageMemory {
    void execute_x87(sharp_retro::X87Op op,sharp_retro::State& state,std::uint64_t pc,std::uint32_t address,std::uint16_t opcode) override {
        recomp_generated::execute_native_x87(*this,op,state,pc,address,opcode);
    }
};
static sharp_retro::State input(unsigned top,unsigned precision,unsigned rounding) {
    sharp_retro::State state;
    state.x87_control=std::uint16_t(0x7f|(precision<<8)|(rounding<<10));
    state.x87_status=std::uint16_t(0x120|(top<<11)); state.x87_tag=0xffff;
    state.x87_control_defined=state.x87_status_defined=state.x87_tag_defined=0xffff;
    state.x87_environment_defined=true; state.mxcsr=0x1fa0; state.mxcsr_defined=0xffffffffu;
    state.mxcsr_mask=recomp_generated::native_mxcsr_mask(); state.defined_x87_st=0xff;
    for(unsigned i=0;i<8;i++) { state.x87_st[i][7]=0x80; state.x87_st[i][8]=0xff; state.x87_st[i][9]=0x3f; }
    return state;
}
static bool same(const sharp_retro::State& a,const sharp_retro::State& b) {
    return a.x87_control==b.x87_control && a.x87_status==b.x87_status && a.x87_tag==b.x87_tag &&
           a.mxcsr==b.mxcsr && a.x87_st==b.x87_st;
}
int main() {
 try {
    unsigned cases=0; sharp_retro::State host_before; recomp_generated::capture_native_fp(host_before);
    for(unsigned top:{0u,7u}) for(unsigned destination=0;destination<2;destination++) for(unsigned setup=0;setup<3;setup++) {
        auto expected=input(top,2,0); expected.defined_x87_st=0; auto candidate=expected;
        {
            recomp_generated::NativeFloatingScope scope(expected,false);
            if(setup<2) asm volatile("fld1" : : : "memory");
            if(setup==0) asm volatile("fldz" : : : "memory");
            if(destination) asm volatile("fstp %%st(1)" : : : "memory");
            else asm volatile("fstp %%st(0)" : : : "memory");
            scope.finish();
        }
        DebugMemory memory;
        if(setup<2) memory.execute_x87(sharp_retro::X87Op::fld1,candidate,0x445560,0,0x1e8);
        if(setup==0) memory.execute_x87(sharp_retro::X87Op::fldz,candidate,0x445562,0,0x1ee);
        memory.execute_x87(destination ? sharp_retro::X87Op::fstp1 : sharp_retro::X87Op::fstp0,candidate,0x445564,0,std::uint16_t(0x5d8+destination));
        if(!same(expected,candidate)) {
            std::fprintf(stderr,"TOP=%u destination=%u setup=%u SW=%04x/%04x TW=%04x/%04x data=%d known=%02x\n",top,destination,setup,expected.x87_status,candidate.x87_status,expected.x87_tag,candidate.x87_tag,int(expected.x87_st==candidate.x87_st),candidate.defined_x87_st); return 1;
        }
        auto new_top=(candidate.x87_status>>11)&7;
        for(unsigned i=0;i<8;i++) if(((candidate.x87_tag>>(((new_top+i)&7)*2))&3)!=3 && !(candidate.defined_x87_st&(1u<<i))) return 2;
        ++cases;
    }
    auto unknown=input(0,2,0); DebugMemory memory;
    memory.execute_x87(sharp_retro::X87Op::fld1,unknown,0x445560,0,0x1e8); unknown.defined_x87_st=0; auto before=unknown;
    bool refused=false;
    try { memory.execute_x87(sharp_retro::X87Op::fstp1,unknown,0x445562,0,0x5d9); }
    catch(const std::runtime_error&) { refused=same(before,unknown) && !unknown.defined_x87_st; }
    sharp_retro::State host_after; recomp_generated::capture_native_fp(host_after);
    if(!refused || !same(host_before,host_after)) return 3;
    std::printf("{\"native_register_pop_cases\":%u,\"mismatches\":0,\"live_results_known\":true,\"unknown_live_values_refused\":true,\"host_fp_restored\":true}\n",cases);
 } catch(const std::exception& error) { std::fprintf(stderr,"%s\n",error.what()); return 20; }
}

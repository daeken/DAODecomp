// Bounded x87 non-popping-store debugging; no game-equivalence claim.
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
    for(auto bits:{0x3ff0000000000000ULL,0x3ff199999999999aULL})
    for(unsigned top:{0u,7u}) for(unsigned precision:{0u,2u,3u}) for(unsigned rounding=0;rounding<4;rounding++) {
        auto expected=input(top,precision,rounding),candidate=expected;
        std::uint32_t a=0,b=0,c=0;
        {
            recomp_generated::NativeFloatingScope scope(expected,false);
            asm volatile("fldl %3\n\tfsts %0\n\tfsts %1\n\tfstps %2" : "=m"(a),"=m"(b),"=m"(c) : "m"(bits) : "memory"); scope.finish();
        }
        DebugMemory memory; memory.map_bytes("data",0x8000,32,true,true); memory.seal(); memory.store(0x8000,bits,64);
        memory.execute_x87(sharp_retro::X87Op::fld64,candidate,0x445560,0x8000,0x500);
        auto before=candidate;
        memory.execute_x87(sharp_retro::X87Op::fst32,candidate,0x445562,0x8010,0x110);
        if(((candidate.x87_status^before.x87_status)&0x3800) || candidate.x87_tag!=before.x87_tag ||
           candidate.x87_st!=before.x87_st || candidate.defined_x87_st!=before.defined_x87_st) return 1;
        memory.execute_x87(sharp_retro::X87Op::fst32,candidate,0x445564,0x8014,0x110);
        memory.execute_x87(sharp_retro::X87Op::fstp32,candidate,0x445566,0x8018,0x118);
        if(!same(expected,candidate) || memory.load(0x8010,32)!=a || memory.load(0x8014,32)!=b || memory.load(0x8018,32)!=c) return 2;
        ++cases;
    }
    unsigned empty_cases=0;
    for(unsigned top:{0u,7u}) {
        auto expected=input(top,2,0); expected.defined_x87_st=0; auto candidate=expected;
        std::uint32_t output=0;
        { recomp_generated::NativeFloatingScope scope(expected,false); asm volatile("fsts %0" : "=m"(output) : : "memory"); scope.finish(); }
        DebugMemory memory; memory.map_bytes("data",0x8000,4,true,true); memory.seal();
        memory.execute_x87(sharp_retro::X87Op::fst32,candidate,0x445568,0x8000,0x110);
        if(!same(expected,candidate) || memory.load(0x8000,32)!=output || candidate.defined_x87_st) return 3;
        ++empty_cases;
    }
    bool readonly_refused=false,unknown_refused=false;
    {
        auto state=input(0,2,0); DebugMemory memory; memory.map_bytes("readonly",0x8000,4,true,false); memory.map_bytes("writeable",0x8010,4,true,true); memory.seal();
        memory.execute_x87(sharp_retro::X87Op::fld1,state,0x445560,0,0x1e8); auto before=state;
        try { memory.execute_x87(sharp_retro::X87Op::fst32,state,0x445562,0x8000,0x110); }
        catch(const std::runtime_error&) { readonly_refused=same(before,state) && before.defined_x87_st==state.defined_x87_st; }
        state.defined_x87_st=0; before=state;
        try { memory.execute_x87(sharp_retro::X87Op::fst32,state,0x445562,0x8010,0x110); }
        catch(const std::runtime_error&) { unknown_refused=same(before,state) && !state.defined_x87_st; }
    }
    sharp_retro::State host_after; recomp_generated::capture_native_fp(host_after); bool restored=same(host_before,host_after);
    if(!readonly_refused || !unknown_refused || !restored) return 4;
    std::printf("{\"native_nonpop_sequences\":%u,\"empty_stack_cases\":%u,\"mismatches\":0,\"top_tags_data_retained\":true,\"readonly_store_preserves_state\":true,\"unknown_live_value_refused\":true,\"host_fp_restored\":true}\n",cases,empty_cases);
 } catch(const std::exception& error) { std::fprintf(stderr,"%s\n",error.what()); return 20; }
}

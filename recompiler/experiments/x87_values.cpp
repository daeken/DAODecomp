// Bounded debugging of the reached Umbra matrix initializer and x87 transport.
// Native original execution is confined to this reference experiment.
#include "functions.hpp"
#include "image_memory.hpp"
#include "native_x87.hpp"
#include <windows.h>
#include <cstdio>
#ifndef RECOMP_MATRIX_FUNCTION
#error "Bind the generated candidate for pinned Umbra RVA 0xf5000"
#endif
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
    state.x87_environment_defined=true;
    state.mxcsr=0x1fa0; state.mxcsr_defined=0xffffffffu; state.mxcsr_mask=recomp_generated::native_mxcsr_mask();
    state.defined_x87_st=0xff;
    for(unsigned i=0;i<8;i++) {
        auto value=std::uint64_t(0x8000000000000000ULL)|(std::uint64_t(i)<<56);
        std::memcpy(state.x87_st[i].data(),&value,8); state.x87_st[i][8]=0xff; state.x87_st[i][9]=0x3f;
    }
    return state;
}
static bool same_fp(const sharp_retro::State& a,const sharp_retro::State& b,bool pointers=true) {
    return a.x87_control==b.x87_control && a.x87_status==b.x87_status && a.x87_tag==b.x87_tag && a.mxcsr==b.mxcsr && a.x87_st==b.x87_st &&
        (!pointers || (a.x87_ip==b.x87_ip && a.x87_dp==b.x87_dp && a.x87_cs==b.x87_cs && a.x87_ds==b.x87_ds && a.x87_opcode==b.x87_opcode));
}
int main(int argc,char** argv) {
    if(argc!=2 || sizeof(void*)!=4) return 2;
    auto module=::LoadLibraryA(argv[1]);
    if(!module) { std::fprintf(stderr,"LoadLibrary failed: %lu\n",::GetLastError()); return 3; }
    auto base=reinterpret_cast<std::uintptr_t>(module);
    auto original=reinterpret_cast<void(*)()>(base+0xf5000);
    unsigned cases=0,mismatches=0;
    sharp_retro::State host_before; recomp_generated::capture_native_fp(host_before);
    for(unsigned top=0;top<8;top++) for(unsigned precision:{0u,2u,3u}) for(unsigned rounding=0;rounding<4;rounding++) {
        auto expected=input(top,precision,rounding),candidate=expected;
        {
            recomp_generated::NativeFloatingScope floating(expected,false);
            original(); floating.finish();
        }
        // Normalize only pointers into the relocated original DLL.
        if(expected.x87_ip>=base && expected.x87_ip-base<0x120000) expected.x87_ip=0x10000000u+std::uint32_t(expected.x87_ip-base);
        if(expected.x87_dp>=base && expected.x87_dp-base<0x120000) expected.x87_dp=0x10000000u+std::uint32_t(expected.x87_dp-base);
        DebugMemory memory; memory.map_bytes("matrix",0x1010a6f0,64,true,true); memory.map_bytes("stack",0x50000000,4096,true,true); memory.seal();
        candidate.gpr[4]=0x50000800; candidate.gpr[5]=0xaabbccdd; candidate.pc=0x100f5000;
        memory.store(candidate.gpr[4],0x12345678,32);
        auto outcome=recomp_generated::RECOMP_MATRIX_FUNCTION(candidate,memory,1000);
        bool match=outcome==sharp_retro::Exit::returned && candidate.pc==0x12345678 && candidate.gpr[4]==0x50000804 && candidate.gpr[5]==0xaabbccdd &&
            candidate.defined_x87_st==0xff && same_fp(expected,candidate);
        for(unsigned i=0;i<16;i++) {
            std::uint32_t actual; std::memcpy(&actual,reinterpret_cast<void*>(base+0x10a6f0+i*4),4);
            match&=actual==std::uint32_t(memory.load(0x1010a6f0+i*4,32));
        }
        ++cases; if(!match) { ++mismatches; std::fprintf(stderr,"matrix mismatch TOP=%u PC=%u RC=%u; SW=%04x/%04x TW=%04x/%04x IP=%08x/%08x OP=%03x/%03x DP=%08x/%08x\n",top,precision,rounding,expected.x87_status,candidate.x87_status,expected.x87_tag,candidate.x87_tag,expected.x87_ip,candidate.x87_ip,expected.x87_opcode,candidate.x87_opcode,expected.x87_dp,candidate.x87_dp); }
    }
    unsigned pair_cases=0,pair_mismatches=0;
    struct Pair { unsigned width; std::uint64_t bits; };
    for(auto item : {Pair{32,0},Pair{32,0x80000000},Pair{32,0x3f800000},Pair{32,0x7f7fffff},Pair{32,1},Pair{32,0x7f800000},Pair{32,0xff800000},Pair{32,0x7fc12345},Pair{32,0x7f812345},
                     Pair{64,0},Pair{64,0x8000000000000000ULL},Pair{64,0x3ff0000000000000ULL},Pair{64,0x7fefffffffffffffULL},Pair{64,1},Pair{64,0x7ff0000000000000ULL},Pair{64,0xfff0000000000000ULL},Pair{64,0x7ff8123456789abcULL},Pair{64,0x7ff0123456789abcULL}})
    for(unsigned top:{0u,3u,7u}) for(unsigned rounding=0;rounding<4;rounding++) {
        auto expected=input(top,2,rounding),candidate=expected;
        std::uint32_t source32=std::uint32_t(item.bits),out32=0; std::uint64_t source64=item.bits,out64=0;
        {
            recomp_generated::NativeFloatingScope floating(expected,false);
            if(item.width==32) asm volatile("flds %1\n\tfstps %0" : "=m"(out32) : "m"(source32) : "memory");
            else asm volatile("fldl %1\n\tfstpl %0" : "=m"(out64) : "m"(source64) : "memory");
            floating.finish();
        }
        DebugMemory memory; memory.map_bytes("data",0x8000,32,true,true); memory.seal(); memory.store(0x8000,item.bits,item.width);
        auto load=item.width==32 ? sharp_retro::X87Op::fld32 : sharp_retro::X87Op::fld64;
        auto store=item.width==32 ? sharp_retro::X87Op::fstp32 : sharp_retro::X87Op::fstp64;
        memory.execute_x87(load,candidate,0x445560,0x8000,item.width==32 ? 0x100 : 0x500);
        memory.execute_x87(store,candidate,0x445562,0x8010,item.width==32 ? 0x118 : 0x518);
        bool match=same_fp(expected,candidate,false) && memory.load(0x8010,item.width)==(item.width==32 ? out32 : out64);
        ++pair_cases; if(!match) ++pair_mismatches;
    }
    bool unknown_refused=false,unmasked_refused=false,store_fault_preserved=false;
    unsigned init_mismatches=0;
    for(unsigned top=0;top<8;top++) {
        auto expected=input(top,2,0),candidate=expected;
        {
            recomp_generated::NativeFloatingScope floating(expected,false);
            asm volatile("fninit" : : : "memory"); floating.finish();
        }
        sharp_retro::x87_fninit(candidate);
        if(candidate.defined_x87_st!=0xff || !same_fp(expected,candidate)) ++init_mismatches;
    }
    {
        auto state=input(0,2,0); state.x87_tag=0; state.defined_x87_st=0;
        DebugMemory memory;
        try { memory.execute_x87(sharp_retro::X87Op::fld1,state,0x445566,0,0x1e8); }
        catch(const std::runtime_error&) { unknown_refused=state.x87_tag==0 && state.x87_status==0x120; }
        state=input(0,2,0); state.x87_control&=~1u;
        try { memory.execute_x87(sharp_retro::X87Op::fld1,state,0x445566,0,0x1e8); }
        catch(const std::runtime_error&) { unmasked_refused=state.x87_tag==0xffff && state.x87_status==0x120; }
        state=input(0,2,0); memory.map_bytes("readonly",0x8000,4,true,false); memory.seal();
        memory.execute_x87(sharp_retro::X87Op::fld1,state,0x445566,0,0x1e8); auto before=state;
        try { memory.execute_x87(sharp_retro::X87Op::fstp32,state,0x445568,0x8000,0x118); }
        catch(const std::runtime_error&) { store_fault_preserved=same_fp(before,state) && before.defined_x87_st==state.defined_x87_st; }
    }
    sharp_retro::State host_after; recomp_generated::capture_native_fp(host_after);
    bool host_restored=same_fp(host_before,host_after);
    std::printf("{\"original_matrix_cases\":%u,\"mismatches\":%u,\"load_store_cases\":%u,\"load_store_mismatches\":%u,\"fninit_top_cases\":8,\"fninit_data_mismatches\":%u,\"unknown_live_value_refused\":%s,\"unmasked_control_refused\":%s,\"store_fault_preserved_state\":%s,\"host_fp_restored\":%s}\n",cases,mismatches,pair_cases,pair_mismatches,init_mismatches,unknown_refused ? "true" : "false",unmasked_refused ? "true" : "false",store_fault_preserved ? "true" : "false",host_restored ? "true" : "false");
    return mismatches || pair_mismatches || init_mismatches || !unknown_refused || !unmasked_refused || !store_fault_preserved || !host_restored ? 1 : 0;
}

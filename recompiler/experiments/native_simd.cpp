// Independent physical execution of constructed SSE encodings versus emitted C++.
#include "functions.hpp"
#include "native_execution.hpp"
#include "image_memory.hpp"
#include "simd_cases.inc"
#include <cstdio>
namespace sharp_retro {void native_simd(Memory&,State&,std::uint64_t,std::uint32_t,std::uint32_t);}
extern "C" unsigned char simd_reference_code[];
using namespace recomp_generated;
struct SimdMemory : NativeX86Memory {
    bool tracing=false;unsigned reads=0,writes=0,last_width=0;std::uint32_t operand=0;
    sharp_retro::bits load(std::uint64_t a,unsigned width) override {if(tracing&&a==operand){++reads;last_width=width;}return NativeX86Memory::load(a,width);}
    void store(std::uint64_t a,sharp_retro::bits v,unsigned width) override {if(tracing&&a==operand){++writes;last_width=width;}NativeX86Memory::store(a,v,width);}
};
static bool fp_same(const sharp_retro::State& a,const sharp_retro::State& b){return
    a.x87_control==b.x87_control&&a.x87_status==b.x87_status&&a.x87_tag==b.x87_tag&&a.x87_st==b.x87_st&&
    a.x87_control_defined==b.x87_control_defined&&a.x87_status_defined==b.x87_status_defined&&a.x87_tag_defined==b.x87_tag_defined&&
    a.defined_x87_st==b.defined_x87_st&&a.x87_environment_defined==b.x87_environment_defined&&
    a.x87_ip==b.x87_ip&&a.x87_dp==b.x87_dp&&a.x87_cs==b.x87_cs&&a.x87_ds==b.x87_ds&&a.x87_opcode==b.x87_opcode&&
    a.mxcsr==b.mxcsr&&a.mxcsr_defined==b.mxcsr_defined&&a.mxcsr_mask==b.mxcsr_mask;}

int main(){try{
    SimdMemory memory;memory.reserve_image(0x31000000,0x10000);
    memory.map_bytes("stack",0x50000000,0x10000,true,true);memory.map_bytes("operands",0x50010000,4096,true,true);memory.seal();memory.add_native_stack(0x50000000,0x50010000);
    constexpr unsigned n=sizeof(simd_cases)/sizeof(simd_cases[0]);
    auto* code=simd_reference_code;
    sharp_retro::State warm;capture_native_context(warm);warm.gpr[4]=0x5000f000;memory.store(warm.gpr[4],0x12345678,32);
    if(!invoke_native_abi_address(std::uint32_t(reinterpret_cast<std::uintptr_t>(code+n*32)),warm,memory))return 4;
    sharp_retro::State host;capture_native_context(host);
    using sharp_retro::bits;
    const bits patterns[]={
      (bits(0xc000000000000000ULL)<<64)|0x3ff0000000000000ULL,(bits(0x7ff0000000001234ULL)<<64)|0x7ff8000000001234ULL,
      (bits(0xfff0000000000000ULL)<<64)|0x7ff0000000000000ULL,(bits(0x8000000000000000ULL)<<64),
      (bits(0x000fffffffffffffULL)<<64)|1,(bits(0xffefffffffffffffULL)<<64)|0x7fefffffffffffffULL,
      (bits(0xffffffff80000000ULL)<<64)|0x7fffffff80000001ULL,(bits(0xbff8000000000000ULL)<<64)|0x4004000000000000ULL,
      (bits(0x7f800001ff800000ULL)<<64)|0x3f800000bf800000ULL,(bits(0x80000001007fffffULL)<<64)|0x0080000000000001ULL,
      ~bits(0),(bits(0x0123456789abcdefULL)<<64)|0xfedcba9876543210ULL};
    unsigned cases=0,mismatches=0,guards=0;
    for(unsigned index=0;index<n;++index)for(unsigned pattern=0;pattern<12;++pattern)for(unsigned rounding=0;rounding<4;++rounding)for(unsigned denorm=0;denorm<4;++denorm){
        auto expected=host;expected.flags=0x202u|((pattern&1)?0x8d5u:0);expected.defined_flags=0xffffffffu;
        expected.mxcsr=0x1f80u|(rounding<<13)|((denorm&1)?0x40u:0)|((denorm&2)?0x8000u:0)|((pattern&1)?0x21u:0);expected.mxcsr_defined=0xffffffffu;
        expected.gpr[4]=0x5000f000;for(unsigned i=0;i<8;++i)if(i!=4)expected.gpr[i]=0x11000000u+i*0x1010101u;expected.defined_gpr=0xffff;
        auto& fixture=simd_cases[index];auto operand=0x50010080u+(fixture.unaligned?3u:0u);if(fixture.ea==1)operand=std::uint32_t(expected.gpr[4])+4;
        expected.gpr[6]=operand;
        if(fixture.ea==2)expected.gpr[5]=operand+8;
        if(fixture.ea==3){expected.gpr[0]=operand+4;expected.gpr[1]=3;}
        if(fixture.ea==4){expected.gpr[0]=operand+16;expected.gpr[1]=0x40000000u;}
        if(fixture.ea==5)expected.gpr[1]=2;
        if(fixture.ea==7)expected.gpr[1]=4;
        if(fixture.ea==8)expected.gpr[5]=2;
        if(fixture.size>=8 && fixture.code[3]==0xb8)expected.gpr[0]=operand+16;
        expected.defined_xmm=0xffff;for(unsigned i=0;i<8;++i)expected.xmm[i]=patterns[(pattern+i)%12];
        // A full live x87 stack exposes accidental damage to unrelated FP state.
        expected.x87_control=0x37f;expected.x87_status=0;expected.x87_tag=0;expected.defined_x87_st=0xff;
        for(unsigned i=0;i<8;++i){std::uint64_t fraction=0x8000000000000000ULL|(std::uint64_t(i)<<59);std::uint16_t exponent=0x3fff;std::memcpy(expected.x87_st[i].data(),&fraction,8);std::memcpy(expected.x87_st[i].data()+8,&exponent,2);}
        auto candidate=expected;auto input=patterns[(pattern+5)%12];memory.store(operand,input,128);memory.store(expected.gpr[4],0x12345678,32);
        ::SetLastError(0x24681357u);
        if(!invoke_native_abi_address(std::uint32_t(reinterpret_cast<std::uintptr_t>(code+index*32)),expected,memory))return 5;
        auto output=memory.load(operand,128);memory.store(operand,input,128);memory.store(candidate.gpr[4],0x12345678,32);
        memory.operand=operand;memory.reads=memory.writes=0;memory.tracing=true;std::uint64_t budget=10;
        auto exit=execute_guest(0x31001000+index*32,0x12345678,candidate,memory,budget);memory.tracing=false;
        bool registers=true;for(unsigned i=0;i<8;++i)if(candidate.gpr[i]!=expected.gpr[i]||candidate.xmm[i]!=expected.xmm[i])registers=false;
        bool footprint=memory.reads==(fixture.width&&!fixture.store?1u:0u)&&memory.writes==(fixture.store?1u:0u)&&(!fixture.width||memory.last_width==fixture.width);
        bool match=exit==sharp_retro::Exit::returned&&registers&&candidate.flags==expected.flags&&candidate.defined_flags==expected.defined_flags&&candidate.defined_gpr==expected.defined_gpr&&candidate.defined_xmm==expected.defined_xmm&&fp_same(candidate,expected)&&memory.load(operand,128)==output&&footprint&&::GetLastError()==0x24681357u;
        ++cases;if(!match){++mismatches;if(mismatches<8)std::fprintf(stderr,"SIMD case=%u pattern=%u rounding=%u denorm=%u registers=%u flags=%llx/%llx csr=%x/%x fp=%u footprint=%u rw=%u/%u width=%u\n",index,pattern,rounding,denorm,unsigned(registers),(unsigned long long)candidate.flags,(unsigned long long)expected.flags,candidate.mxcsr,expected.mxcsr,unsigned(fp_same(candidate,expected)),unsigned(footprint),memory.reads,memory.writes,memory.last_width);}
    }
    ImageMemory checked;checked.map_bytes("guard",0x9000,0x100,true,true);checked.map_bytes("readonly",0xa000,0x100,true,false);checked.seal();checked.store(0x9000,0,128);
    for(unsigned mode=0;mode<17;++mode){
        auto state=host;state.defined_xmm=0xffff;state.mxcsr=0x1f80;state.mxcsr_defined=0xffffffffu;state.gpr[1]=7;state.defined_gpr=0xffff;
        std::uint32_t descriptor=11u|(1u<<11),address=0x9000;
        if(mode==0)state.defined_xmm&=~2u;
        if(mode==1){descriptor=24u|(1u<<11);state.defined_gpr&=~2u;state.partial_gpr[1]=0;}
        if(mode==2)state.mxcsr_defined=0;
        if(mode==3)state.mxcsr&=~0x80u;
        if(mode==4)state.mxcsr|=0x80000000u;
        if(mode==5){descriptor=15|0x4000;address=0x9001;}
        if(mode==6){descriptor=11|0x4000;auto setup=host;NativeFloatingScope scope(setup,false);checked.store_unknown(0x9000,0,64);}
        if(mode==7){descriptor=11|0x4000;address=0xdeadbeef;}
        if(mode==8){descriptor=2|0x4000;address=0xa000;}
        if(mode==9)descriptor|=0x80000000u;
        if(mode==10)descriptor=42;
        if(mode==11)descriptor|=1u<<16;
        if(mode==12)descriptor=18;
        if(mode==13)descriptor=1;
        if(mode==14)descriptor=32|0x4000;
        if(mode==15){descriptor=1|0x4000;state.defined_xmm&=~1u;checked.forget_unknown_range(0x9000,8);checked.store(0x9000,0,64);}
        if(mode==16)state.mxcsr_mask=0;
        auto before=state;
        try{sharp_retro::native_simd(checked,state,0x31001000,descriptor,address);}
        catch(const std::runtime_error&){if(fp_same(state,before)&&state.defined_xmm==before.defined_xmm&&state.xmm[0]==before.xmm[0]&&state.gpr[0]==before.gpr[0]&&state.defined_gpr==before.defined_gpr)++guards;}
    }
    sharp_retro::State after;capture_native_fp(after);bool restored=fp_same(host,after);
    std::printf("{\"compiled_simd_encoding_cases\":%u,\"physical_comparisons\":%u,\"mismatches\":%u,\"refusal_guards\":%u,\"host_fp_restored\":%s,\"game_acceptance\":false}\n",n,cases,mismatches,guards,restored?"true":"false");
    return mismatches||guards!=17||!restored?1:0;
}catch(const std::exception& e){std::fprintf(stderr,"SIMD debug error: %s\n",e.what());return 10;}}

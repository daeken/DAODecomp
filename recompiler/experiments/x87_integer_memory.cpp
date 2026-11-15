// Constructed controls for integer memory arithmetic and extended stores.
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
static std::uint32_t reference(unsigned form,void* pointer) {
    std::uint32_t ip=0;
#define REF(N,FIRST,SECOND) case N: asm volatile("leal 1f,%0\n\t1: .byte " #FIRST "," #SECOND : "=&r"(ip) : "a"(pointer) : "memory");break;
    switch(form) {
    REF(0,0xda,0x00) REF(1,0xda,0x08) REF(2,0xda,0x20) REF(3,0xda,0x28) REF(4,0xda,0x30) REF(5,0xda,0x38)
    REF(6,0xde,0x00) REF(7,0xde,0x08) REF(8,0xde,0x20) REF(9,0xde,0x28) REF(10,0xde,0x30) REF(11,0xde,0x38)
    REF(12,0xdb,0x38)
    }
#undef REF
    return ip;
}
static bool environment_same(const sharp_retro::State& a,const sharp_retro::State& b) {
    return a.x87_ip==b.x87_ip && a.x87_dp==b.x87_dp && a.x87_cs==b.x87_cs && a.x87_ds==b.x87_ds && a.x87_opcode==b.x87_opcode;
}
struct TracedMemory : DebugMemory {
    bool tracing=false;unsigned reads=0,writes=0,width=0;
    sharp_retro::bits load(std::uint64_t a,unsigned w) override {if(tracing&&a==0x9001){++reads;width=w;}return ImageMemory::load(a,w);}
    void store(std::uint64_t a,sharp_retro::bits v,unsigned w) override {if(tracing){++writes;width=w;}ImageMemory::store(a,v,w);}
};
int main() {try {
    TracedMemory memory;memory.map_bytes("ram",0x8000,0x2000,true,true);memory.seal();memory.store(0x8800,0x12345678,32);
    sharp_retro::State host;recomp_generated::capture_native_fp(host);
    const std::uint32_t values[]={0,1,0xffffffffu,0x7fffffffu,0x80000000u,0x7fffu,0x8000u,0xffffu,3};
    const unsigned codes[]={0x200,0x208,0x220,0x228,0x230,0x238,0x600,0x608,0x620,0x628,0x630,0x638,0x338};
    unsigned cases=0,mismatches=0,guards=0;
    for(unsigned form=0;form<13;++form)for(unsigned top=0;top<8;++top)for(unsigned precision:{0u,2u,3u})
    for(unsigned rounding=0;rounding<4;++rounding)for(unsigned pattern=0;pattern<9;++pattern)for(unsigned operand=0;operand<9;++operand)for(bool empty:{false,true}) {
        auto expected=host;expected.x87_control=std::uint16_t(0x7f|(precision<<8)|(rounding<<10));expected.x87_status=std::uint16_t(0x4700|(top<<11));expected.x87_tag=0;expected.defined_x87_st=0xff;
        for(unsigned i=0;i<8;++i)raw(expected,i,0x8000000000000000ULL|(std::uint64_t(i)<<59),std::uint16_t(0x3fff|((i&1)<<15)));
        if(pattern==1)raw(expected,0,0,0);if(pattern==2)raw(expected,0,0,0x8000);
        if(pattern==3)raw(expected,0,0x8000000000000000ULL,0x7fff);if(pattern==4)raw(expected,0,0xc000000000001234ULL,0x7fff);
        if(pattern==5)raw(expected,0,0x8000000000001234ULL,0x7fff);if(pattern==6)raw(expected,0,1,0);
        if(pattern==7)raw(expected,0,0x8000000000000000ULL,0xbfff);
        tag(expected,0,empty?3u:pattern==1||pattern==2?1u:pattern>=3&&pattern<=6?2u:0u);
        auto candidate=expected;std::array<std::uint8_t,16> output;output.fill(0x5a);auto input=values[operand];
        auto pointer=form==12?static_cast<void*>(output.data()):static_cast<void*>(&input);std::uint32_t ip=0;
        {recomp_generated::NativeFloatingScope fp(expected,false);ip=reference(form,pointer);fp.finish();}
        auto pc=0x401000u+form*16;if(expected.x87_ip==ip)expected.x87_ip=pc;
        if(expected.x87_dp==std::uint32_t(reinterpret_cast<std::uintptr_t>(pointer)))expected.x87_dp=0x9001;
        sharp_retro::bits payload=0;if(form==12)std::memset(&payload,0x5a,16);else payload=0x5a5a5a5a00000000ULL|values[operand];
        memory.store(0x9001,payload,128);candidate.gpr[0]=0x9001;candidate.gpr[4]=0x8800;candidate.defined_gpr=0xffff;auto before=candidate;
        memory.reads=memory.writes=0;memory.tracing=true;std::uint64_t budget=10;
        auto exit=recomp_generated::execute_guest(pc,0x12345678,candidate,memory,budget);memory.tracing=false;
        bool registers=true;for(unsigned i=0;i<16;++i)if(candidate.gpr[i]!=(i==4?before.gpr[i]+4:before.gpr[i]))registers=false;
        sharp_retro::bits wanted=payload;if(form==12)std::memcpy(&wanted,output.data(),16);
        bool footprint=memory.width==(form==12?80u:form<6?32u:16u)&&memory.reads==(form==12?0u:1u)&&memory.writes==(form==12?1u:0u);
        bool match=exit==sharp_retro::Exit::returned&&registers&&same(expected,candidate)&&environment_same(expected,candidate)&&candidate.flags==before.flags&&candidate.defined_flags==before.defined_flags&&candidate.defined_x87_st==0xff&&footprint&&memory.load(0x9001,128)==wanted;
        ++cases;if(!match){++mismatches;if(mismatches<8)std::fprintf(stderr,"integer memory form=%u top=%u pc=%u rc=%u pattern=%u operand=%u empty=%u fp=%u env=%u footprint=%u SW=%x/%x OP=%x/%x IP=%x/%x DP=%x/%x\n",form,top,precision,rounding,pattern,operand,unsigned(empty),unsigned(same(expected,candidate)),unsigned(environment_same(expected,candidate)),unsigned(footprint),expected.x87_status,candidate.x87_status,expected.x87_opcode,candidate.x87_opcode,expected.x87_ip,candidate.x87_ip,expected.x87_dp,candidate.x87_dp);}
    }
    for(unsigned form=0;form<13;++form)for(unsigned mode=0;mode<4;++mode) {
        auto state=host;state.x87_control=mode==0?0x37e:0x37f;state.x87_status=0;state.x87_tag=0xfffc;state.defined_x87_st=mode==1?0xfe:0xff;raw(state,0,0x8000000000000000ULL,0x3fff);auto before=state;
        // Fixture hash-table allocation/rehashing can use host FP arithmetic.
        // Keep preparation outside the measured instruction's host-state scope.
        {auto setup=host;recomp_generated::NativeFloatingScope fixture(setup,false);
         memory.forget_unknown_range(0x9001,16);memory.store(0x9001,0,128);
         if(mode==3&&form!=12)memory.store_unknown(0x9001,0,form<6?32:16);fixture.finish();}
        auto address=mode==2?0xdeadbeefu:mode==3&&form==12?0x9fffu:0x9001u;
        sharp_retro::State guard_before;recomp_generated::capture_native_fp(guard_before);
        try{recomp_generated::execute_native_x87(memory,recomp_generated::native_encoded_x87,state,0x401000,address,codes[form]);}
        catch(const std::runtime_error&){if(same(before,state)&&environment_same(before,state)&&state.defined_x87_st==before.defined_x87_st)++guards;}
        sharp_retro::State guard_after;recomp_generated::capture_native_fp(guard_after);
        if(!same(guard_before,guard_after))std::fprintf(stderr,"guard physical state changed form=%u mode=%u MXCSR=%x/%x\n",form,mode,guard_before.mxcsr,guard_after.mxcsr);
    }
    sharp_retro::State after;recomp_generated::capture_native_fp(after);bool restored=same(host,after)&&environment_same(host,after);
    if(!restored){std::fprintf(stderr,"host restoration fp=%u env=%u CW=%x/%x SW=%x/%x TAG=%x/%x MXCSR=%x/%x IP=%x/%x DP=%x/%x OP=%x/%x CS=%x/%x DS=%x/%x\n",unsigned(same(host,after)),unsigned(environment_same(host,after)),host.x87_control,after.x87_control,host.x87_status,after.x87_status,host.x87_tag,after.x87_tag,host.mxcsr,after.mxcsr,host.x87_ip,after.x87_ip,host.x87_dp,after.x87_dp,host.x87_opcode,after.x87_opcode,host.x87_cs,after.x87_cs,host.x87_ds,after.x87_ds);for(unsigned i=0;i<8;++i)if(host.x87_st[i]!=after.x87_st[i])std::fprintf(stderr,"host ST%u differs\n",i);}
    std::printf("{\"native_integer_memory_cases\":%u,\"mismatches\":%u,\"refusal_guards\":%u,\"host_fp_restored\":%s,\"game_acceptance\":false}\n",cases,mismatches,guards,restored?"true":"false");
    return mismatches||guards!=52||!restored?1:0;
}catch(const std::exception& e){std::fprintf(stderr,"integer memory control failed: %s\n",e.what());return 10;}}

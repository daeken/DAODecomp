// Constructed PUSH r/m32 controls, separate from whole-function acceptance.
#include "functions.hpp"
#include "image_memory.hpp"
#include <cstdio>
using namespace sharp_retro;
using recomp_generated::ImageMemory;
static constexpr unsigned sizes[]={3,3,4,4,3,6};
static std::uint32_t source(unsigned form,std::uint32_t sp){return form==1 ? sp:form==2 ? sp-4u:form==3 ? sp+4u:0x8800u;}
static void setup(ImageMemory& m,State& s,bool writable=true){
    m.map_bytes("data",0x8000,4096,true,true);m.map_bytes("stack",0xa000,4096,true,writable);
    s.gpr[4]=0xa800;s.gpr[5]=0x8870;s.gpr[0]=0x87fd;s.gpr[6]=3;
    m.store(0xa800,0x12345678,32);m.store(0xa7fc,0xabcdef00,32);
}
static void step(State& s,Memory& m,unsigned form){std::uint64_t budget=1;
    if(recomp_generated::execute_guest(0x401000u+form*16,0x12345678,s,m,budget)!=Exit::budget_exhausted || budget || s.pc!=0x401000u+form*16+sizes[form])throw std::runtime_error("PUSH step/budget mismatch");
}
#if defined(_WIN32) && defined(__i386__)
static std::uint32_t native(std::uint32_t input,std::uint32_t flags,std::uint32_t& observed){
    std::uint32_t value;
    asm volatile("pushfl\n\tpushl %[before]\n\tpopfl\n\tpushl (%[cell])\n\tpopl %[value]\n\tpushfl\n\tpopl %[after]\n\tpopfl"
        :[value]"=&r"(value),[after]"=&r"(observed):[cell]"r"(&input),[before]"r"(flags):"cc","memory");
    return value;
}
#endif
int main(){try{
    unsigned known_cases=0,native_cases=0,partial_cases=0,guards=0;
    for(unsigned form=0;form<6;form++)for(auto input:{0u,1u,0x7fffffffu,0x80000000u,0xffffffffu,0x12345678u,0xa5c33c5au,0xdeadbeefu})for(auto flags:{0xad7u,0x6d7u}){
        if(form==1 && input!=0x12345678u)continue;
        ImageMemory m;State s;setup(m,s);s.flags=flags;m.store(source(form,0xa800),input,32);m.seal();auto before=s;step(s,m,form);
        std::uint32_t expected=input,observed=flags;
#if defined(_WIN32) && defined(__i386__)
        expected=native(input,flags,observed);++native_cases;
#endif
        if(s.gpr[4]!=0xa7fc || m.load(0xa7fc,32)!=expected || s.flags!=observed || s.defined_flags!=before.defined_flags)return 1;
        for(unsigned reg=0;reg<16;reg++)if(reg!=4 && s.gpr[reg]!=before.gpr[reg])return 2;
        std::uint64_t budget=100;if(recomp_generated::resume_guest(0x12345678,s,m,budget)!=Exit::returned || s.gpr[4]!=0xa804)return 3;++known_cases;
    }
    for(unsigned form=0;form<6;form++)for(auto known:{0u,0xff00ff00u,0xffffffffu}){
        ImageMemory m;State s;setup(m,s);s.flags=0xad7;s.defined_flags=1u<<10;
        Scalar32 value{form==1 ? 0x12345678u:0xa5c33c5au,known,{}};for(unsigned bit=0;bit<32;bit++)if(!(known&(1u<<bit)))value.origins[bit]=1000+bit;
        m.store_scalar32(source(form,0xa800),value);m.seal();auto before=s;step(s,m,form);auto actual=m.load_scalar32(0xa7fc);
        if(s.gpr[4]!=0xa7fc || actual.value!=value.value || actual.known!=value.known || actual.origins!=value.origins || s.flags!=before.flags || s.defined_flags!=before.defined_flags || s.flag_origins!=before.flag_origins)return 4;
        if(known!=0xffffffffu){bool unknown=false;try{(void)m.load(0xa7fc,32);}catch(const UnknownMemoryRead&){unknown=true;}if(!unknown)return 5;}++partial_cases;
    }
    for(bool write_fault:{false,true}){
        ImageMemory m;State s;setup(m,s,!write_fault);s.flags=0xad7;s.defined_flags=0x400;
        if(!write_fault)s.gpr[5]=0x7070;else m.store_unknown(0x8800,0xa5c33c5a,32);
        m.seal();auto before=s;bool fault=false;try{step(s,m,0);}catch(const std::runtime_error&){fault=true;}
        if(!fault || s.pc!=0x401000 || s.gpr[4]!=before.gpr[4] || s.flags!=before.flags || s.defined_flags!=before.defined_flags || m.load(0xa7fc,32)!=0xabcdef00)return 6;++guards;
    }
    {
        ImageMemory m;State s;m.map_bytes("data",0x8000,4096,true,true);m.map_bytes("low stack",0,4096,true,true);m.map_bytes("high stack",0xfffff000u,4096,true,true);m.seal();
        s.gpr[4]=0;m.store(0,0x12345678,32);m.store(0x8800,0xa5c33c5a,32);auto flags=s.flags;step(s,m,5);
        if(s.gpr[4]!=0xfffffffcu || m.load(0xfffffffcu,32)!=0xa5c33c5a || s.flags!=flags)return 7;
    }
    std::printf("{\"known_cases\":%u,\"native_cases\":%u,\"partial_cases\":%u,\"fault_guards\":%u,\"wraparound_cases\":1}\n",known_cases,native_cases,partial_cases,guards);return 0;
}catch(const std::exception& e){std::fprintf(stderr,"memory PUSH: %s\n",e.what());return 8;}}

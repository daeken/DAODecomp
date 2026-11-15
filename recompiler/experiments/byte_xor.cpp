// Constructed instruction controls, not function/game acceptance.
#include "functions.hpp"
#include "image_memory.hpp"
#include <cstdio>
using namespace sharp_retro;
using recomp_generated::ImageMemory;
static std::uint32_t flags_for(unsigned value){return (value&0x80u) | (!value ? 0x40u:0u) | (std::popcount(value)%2==0 ? 4u:0u);}
static void run(State& s,Memory& memory,unsigned form){
    s.gpr[4]=0xa800;memory.store(0xa800,0x12345678,32);auto before=s;std::uint64_t budget=100;
    auto entry=form==8 ? 0x401100u:0x401000u+form*16;
    if(recomp_generated::execute_guest(entry,0x12345678,s,memory,budget)!=Exit::returned || s.pc!=0x12345678 || s.gpr[4]!=0xa804)throw std::runtime_error("byte XOR return mismatch");
    for(unsigned reg=0;reg<16;reg++)if(reg!=4 && (s.gpr[reg]!=before.gpr[reg] || s.partial_gpr[reg]!=before.partial_gpr[reg]))throw std::runtime_error("byte XOR modified GPR");
}
#if defined(_WIN32) && defined(__i386__)
static std::uint32_t native(unsigned char* cell,unsigned source,std::uint32_t flags,bool high){
    std::uint32_t observed;
    if(high)asm volatile("pushfl\n\tpushl %[before]\n\tpopfl\n\t.byte 0x30,0x27\n\tpushfl\n\tpopl %[after]\n\tpopfl"
        :[after]"=&d"(observed),[cell]"+m"(*cell):"a"(source),"D"(cell),[before]"r"(flags):"cc","memory");
    else asm volatile("pushfl\n\tpushl %[before]\n\tpopfl\n\t.byte 0x30,0x0c,0x30\n\tpushfl\n\tpopl %[after]\n\tpopfl"
        :[after]"=&d"(observed),[cell]"+m"(*cell):"a"(std::uintptr_t(cell)-3u),"S"(3u),"c"(source),[before]"r"(flags):"cc","memory");
    return observed;
}
#endif
int main(){try{
    ImageMemory memory;memory.map_bytes("data",0x8000,4096,true,true);memory.map_bytes("stack",0xa000,4096,true,true);memory.seal();
    unsigned native_cases=0,abstract_cases=0,guards=0;
#if defined(_WIN32) && defined(__i386__)
    for(bool high:{false,true})for(unsigned a:{0u,1u,0x7fu,0x80u,0x96u,0xa5u,0xfeu,0xffu})for(unsigned b:{0u,1u,0x7fu,0x80u,0x96u,0xa5u,0xfeu,0xffu}){
        State s;s.flags=0x202u|0x8d5u;s.gpr[7]=0x8080;s.gpr[0]=high ? b<<8:0x807d;s.gpr[6]=3;s.gpr[1]=b;
        memory.store(0x807f,0xab,8);memory.store(0x8080,a,8);memory.store(0x8081,0xcd,8);unsigned char expected=static_cast<unsigned char>(a);
        auto flags=native(&expected,high ? b<<8:b,std::uint32_t(s.flags),high);run(s,memory,high ? 4:8);
        if(memory.load(0x8080,8)!=expected || ((s.flags^flags)&~std::uint64_t(0x10)) || (s.defined_flags&0x8d5)!=0x8c5 || memory.load(0x807f,8)!=0xab || memory.load(0x8081,8)!=0xcd)return 1;++native_cases;
    }
#endif
    for(unsigned form=0;form<9;form++)for(unsigned known:{0u,0xf0u,0x7fu,0xffu}){
        auto source=form==8 ? 1u:form,reg=source&3u,shift=source<4 ? 0u:8u;
        State s;s.flags=0x202u|0x8d5u;s.gpr[7]=0x8080;if(form==8){s.gpr[0]=0x807d;s.gpr[6]=3;}
        s.gpr[reg]=(s.gpr[reg]&~(0xffu<<shift))|(0x5au<<shift);
        Scalar32 value{0xa5u,0xffffff00u|known,{}};for(unsigned bit=0;bit<8;bit++)if(!(known&(1u<<bit)))value.origins[bit]=100+bit;
        memory.store_scalar8(0x8080,value);run(s,memory,form);auto output=memory.load_scalar8(0x8080);
        if(output.value!=0xffu || (output.known&0xffu)!=known)return 2;
        for(unsigned bit=0;bit<8;bit++)if(!(known&(1u<<bit)) && output.origins[bit]!=value.origins[bit])return 3;
        unsigned all_one=0xc4u,all_zero=0xc4u;
        for(unsigned candidate=0;candidate<256;candidate++)if((candidate&known)==(0xa5u&known)){auto f=flags_for(candidate^0x5a);all_one&=f;all_zero&=~f;}
        auto expected_known=all_one|all_zero;
        if((s.defined_flags&0x8d5u)!=(expected_known|0x801u) || ((s.flags^all_one)&expected_known) || (s.flags&0x801u))return 4;
        ++abstract_cases;
    }
    for(unsigned form=0;form<8;form++)for(bool correlate:{false,true}){
        auto reg=form&3u,shift=form<4 ? 0u:8u;State s;s.flags=0x202;s.gpr[7]=0x8080;
        Scalar32 a{0x69,0xffffff00u,{}},b{0x96u<<shift,~(0xffu<<shift),{}};
        for(unsigned bit=0;bit<8;bit++){a.origins[bit]=100+bit;b.origins[bit+shift]=(correlate ? 100:200)+bit;}
        memory.store_scalar8(0x8080,a);scalar_gpr32(s,reg,b);run(s,memory,form);auto output=memory.load_scalar8(0x8080);
        if(correlate){if(memory.load(0x8080,8)!=0xff || (s.defined_flags&0x8d5u)!=0x8c5u)return 5;}
        else {if(output.known&0xffu)return 6;for(unsigned bit=0;bit<8;bit++)if(!output.origins[bit] || output.origins[bit]==100+bit || output.origins[bit]==200+bit)return 7;}
        ++abstract_cases;
    }
    for(bool unmapped:{false,true}){
        ImageMemory read_only;read_only.map_bytes("input",0x8000,4096,true,false);read_only.map_bytes("stack",0xa000,4096,true,true);read_only.store_unknown(0x8080,0x69,8);read_only.seal();
        State s;s.flags=0xad7;s.gpr[7]=unmapped ? 0x7000:0x8080;s.gpr[1]=0x96;auto before=s;bool refused=false;
        try{run(s,read_only,1);}catch(const std::runtime_error&){refused=true;}
        if(!refused || s.flags!=before.flags || s.defined_flags!=before.defined_flags || s.pc!=0x401010)return 8;++guards;
    }
    std::printf("{\"native_cases\":%u,\"abstract_cases\":%u,\"fault_guards\":%u}\n",native_cases,abstract_cases,guards);return 0;
}catch(const std::exception& e){std::fprintf(stderr,"byte XOR: %s\n",e.what());return 9;}}

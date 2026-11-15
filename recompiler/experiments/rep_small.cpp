// Constructed native REP/MOVS debugging, not game-function acceptance.
#include "functions.hpp"
#include "native_execution.hpp"
#include "StringRuntime.hpp"
#include <cstdio>
#if defined(_WIN32) && defined(__i386__)
using namespace recomp_generated;
static void cpu_copy(unsigned operation,unsigned char*& source,unsigned char*& destination,unsigned& count,unsigned seed,unsigned& flags){
#define COPY_BYTES(BYTES) asm volatile("pushfl; pushl %4; popfl; " BYTES "; pushfl; popl %3; popfl" : "+S"(source),"+D"(destination),"+c"(count),"=r"(flags):"r"(seed):"cc","memory")
    switch(operation){case 0:COPY_BYTES(".byte 0xf3,0xa4");break;case 1:COPY_BYTES(".byte 0x66,0xf3,0xa5");break;case 2:COPY_BYTES(".byte 0xf3,0x66,0xa5");break;case 3:COPY_BYTES(".byte 0xa4");break;}
#undef COPY_BYTES
}
int main(){try{
    NativeX86Memory memory;unsigned cases=0,guards=0,mismatches=0;
    sharp_retro::State host;capture_native_fp(host);
    for(unsigned operation=0;operation<4;++operation)for(unsigned count:{0u,1u,2u,7u,16u})for(bool down:{false,true})for(unsigned alias=0;alias<4;++alias)for(bool arithmetic:{false,true})for(bool resume:{false,true}){
        if(resume&&(operation==3||count!=7))continue;
        unsigned char original[256],candidate[256];for(unsigned i=0;i<256;++i)original[i]=candidate[i]=std::uint8_t(i*17+3);
        unsigned width=operation==1||operation==2?2:1,source_offset=down?80:32;
        unsigned destination_offset=alias==0?160:alias==1?source_offset:alias==2?source_offset+1:source_offset-1;
        auto* source=original+source_offset;auto* destination=original+destination_offset;auto remaining=count;
        unsigned seed=0x202u|(down?0x400u:0)|(arithmetic?0x8d5u:0),observed=0;
        cpu_copy(operation,source,destination,remaining,seed,observed);
        sharp_retro::State state;state.gpr[1]=count;state.gpr[6]=reinterpret_cast<std::uintptr_t>(candidate+source_offset);state.gpr[7]=reinterpret_cast<std::uintptr_t>(candidate+destination_offset);state.flags=seed;
        std::uint32_t stop=0x12345678;state.gpr[4]=reinterpret_cast<std::uintptr_t>(&stop);auto initial_sp=state.gpr[4];std::uint64_t budget=resume?3:1000;
        auto exit=execute_guest(0x401000+operation*32,0x12345678,state,memory,budget);
        bool partial=true;
        if(resume){partial=exit==sharp_retro::Exit::budget_exhausted&&!budget&&state.gpr[1]==5&&state.pc==0x401000+operation*32&&state.gpr[4]==initial_sp&&state.flags==seed;budget=1000;exit=execute_guest(0x401000+operation*32,0x12345678,state,memory,budget);}
        auto source_result=std::uint32_t(state.gpr[6])-std::uint32_t(reinterpret_cast<std::uintptr_t>(candidate));
        auto destination_result=std::uint32_t(state.gpr[7])-std::uint32_t(reinterpret_cast<std::uintptr_t>(candidate));
        bool match=partial&&exit==sharp_retro::Exit::returned&&state.gpr[4]==initial_sp+4&&state.gpr[1]==remaining&&source_result==unsigned(source-original)&&destination_result==unsigned(destination-original)&&state.flags==observed&&state.defined_flags==~std::uint64_t(0)&&std::memcmp(original,candidate,256)==0;
        ++cases;if(!match){++mismatches;if(mismatches<6)std::fprintf(stderr,"copy op=%u width=%u count=%u down=%u alias=%u resume=%u CX=%u/%u SI=%u/%u DI=%u/%u flags=%llx/%x\n",operation,width,count,unsigned(down),alias,unsigned(resume),unsigned(state.gpr[1]),remaining,source_result,unsigned(source-original),destination_result,unsigned(destination-original),(unsigned long long)state.flags,observed);}
    }
    for(unsigned operation=0;operation<3;++operation){
        sharp_retro::State state;state.gpr[1]=0;state.gpr[6]=state.gpr[7]=0xdeadbeef;state.defined_gpr&=~((1u<<6)|(1u<<7));state.defined_flags&=~(1u<<10);
        std::uint32_t stop=0x12345678;state.gpr[4]=reinterpret_cast<std::uintptr_t>(&stop);std::uint64_t budget=10;auto before=state;
        if(execute_guest(0x401000+operation*32,0x12345678,state,memory,budget)==sharp_retro::Exit::returned&&state.gpr[6]==before.gpr[6]&&state.gpr[7]==before.gpr[7]&&state.defined_gpr==before.defined_gpr&&state.defined_flags==before.defined_flags)++guards;
    }
    for(unsigned operation=0;operation<3;++operation)for(unsigned mode=0;mode<2;++mode){
        unsigned char data[8]={};sharp_retro::State state;state.gpr[1]=1;state.gpr[6]=state.gpr[7]=reinterpret_cast<std::uintptr_t>(data);if(mode==0)state.defined_flags&=~(1u<<10);else state.defined_gpr&=~(1u<<6);
        std::uint32_t stop=0x12345678;state.gpr[4]=reinterpret_cast<std::uintptr_t>(&stop);std::uint64_t budget=10;auto before=state;
        try{execute_guest(0x401000+operation*32,0x12345678,state,memory,budget);}
        catch(const std::runtime_error&){if(state.gpr[1]==before.gpr[1]&&state.gpr[6]==before.gpr[6]&&state.gpr[7]==before.gpr[7]&&state.defined_gpr==before.defined_gpr&&state.flags==before.flags&&state.defined_flags==before.defined_flags)++guards;}
    }
    sharp_retro::State after;capture_native_fp(after);bool restored=host.x87_control==after.x87_control&&host.x87_status==after.x87_status&&host.x87_tag==after.x87_tag&&host.x87_st==after.x87_st&&host.mxcsr==after.mxcsr;
    std::printf("{\"native_copy_cases\":%u,\"mismatches\":%u,\"zero_count_and_unknown_guards\":%u,\"host_fp_restored\":%s,\"game_acceptance\":false}\n",cases,mismatches,guards,restored?"true":"false");return mismatches||cases!=368||guards!=9||!restored?1:0;
}catch(const std::exception& e){std::fprintf(stderr,"small MOVS: %s\n",e.what());return 10;}}
#endif

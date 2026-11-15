#include "functions.hpp"
#include "image_memory.hpp"
#include "umbra_fixture.h"
#include "umbra_contract.hpp"
#include <array>
#include <cstdio>
#ifdef _WIN32
#include <windows.h>
#endif
struct CheckedMemory : recomp_generated::ImageMemory {
    bool active=false;
    void store(std::uint64_t a,sharp_retro::bits value,unsigned width) override {
        if(active && !((a>=0x30000000 && a+width/8<=0x30000400) || (a>=0x50000780 && a+width/8<=0x50000810)))
            throw std::runtime_error("write outside contracted arena/stack frame");
        ImageMemory::store(a,value,width);
    }
};
int main(int argc,char** argv) { try {
    if(argc!=2) return 2;
#ifdef _WIN32
    if(GetModuleHandleA("umbra.dll")) return 3;
#endif
    CheckedMemory memory;
    memory.map_bytes("arena",0x30000000,1024,true,true); memory.map_bytes("stack",0x50000000,4096,true,true);
    recomp_generated::initialize_linked_images(memory,argv[1]);
    unsigned kind,object,inner,nested,mode,word,first,second,seed;
    while(std::scanf("%u %u %u %u %u %u %u %u %u",&kind,&object,&inner,&nested,&mode,&word,&first,&second,&seed)==9) {
        if(kind>=umbra_function_count || object>960 || inner>960 || nested>960) return 4;
        std::array<unsigned char,1024> arena;
        prepare_arena(arena.data(),object,inner,nested,word,seed,umbra_function_rvas[kind]); memory.active=false;
        for(unsigned i=0;i<1024;i++) memory.store(0x30000000+i,arena[i],8);
        for(unsigned i=0;i<4096;i++) memory.store(0x50000000+i,0xa5,8);
        memory.store(0x1010fb10,mode,32);
        sharp_retro::State state; state.flags=0x202;
        state.gpr[0]=0x12344321; state.gpr[1]=0x30000000+object; state.gpr[2]=0x87655678;
        state.gpr[3]=0xaabbccdd; state.gpr[4]=0x50000800; state.gpr[5]=0x33445566;
        state.gpr[6]=0x778899aa; state.gpr[7]=0xbbccddee;
        memory.store(0x50000800,0x12345678,32); memory.store(0x50000804,first,32); memory.store(0x50000808,second,32);
        std::uint64_t budget=1000; memory.active=true;
        if(recomp_generated::execute_guest(0x10000000+umbra_function_rvas[kind],0x12345678,state,memory,budget)!=sharp_retro::Exit::returned ||
           state.pc!=0x12345678 || state.gpr[4]!=0x50000804+umbra_cleanups[kind] ||
           state.gpr[3]!=0xaabbccdd || state.gpr[5]!=0x33445566 || state.gpr[6]!=0x778899aa || state.gpr[7]!=0xbbccddee ||
           (state.defined_gpr&255)!=255 || (state.defined_flags&0x8c5)!=0x8c5) return 5;
        for(unsigned i=0;i<8;i++) std::printf("%u ",unsigned(state.gpr[i]));
        std::printf("%u %u ",unsigned(state.flags&0x8c5),unsigned(memory.load(0x1010fb10,32)));
        for(unsigned i=0;i<1024;i++) std::printf("%02x",unsigned(memory.load(0x30000000+i,8)));
        std::putchar('\n');
    }
    return std::feof(stdin) ? 0 : 6;
} catch(const std::exception& e) { std::fprintf(stderr,"umbra candidate: %s\n",e.what()); return 7; } }

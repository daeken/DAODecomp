// Synthetic cross-module execution with data loaded from immutable view artifacts.
#include "functions.hpp"
#include "image_memory.hpp"
#include "fixture_addresses.hpp"
#include <cstdio>
#ifdef _WIN32
#include <windows.h>
#endif
int main(int argc,char** argv) { try {
    if(argc!=2) return 2;
#ifdef _WIN32
    if(GetModuleHandleA("fixture_provider.dll")) return 3;
#endif
    unsigned first,second,count;
    while(std::scanf("%u %u %u",&first,&second,&count)==3) {
        if(count<1 || count>2) return 4;
        recomp_generated::ImageMemory memory;
        memory.map_bytes("stack",0x50000000,0x1000,true,true);
        recomp_generated::initialize_linked_images(memory,argv[1]);
        if(memory.load(fixture_counter,32)!=0 || memory.load(fixture_bias,32)!=11 ||
           memory.load(fixture_slot,32)!=fixture_target) return 5;
        unsigned result=0;
        for(unsigned i=0;i<count;i++) {
            sharp_retro::State state;
            state.gpr[4]=0x50000800;
            state.gpr[3]=0x11223344; state.gpr[5]=0xaabbccdd;
            state.gpr[6]=0x778899aa; state.gpr[7]=0x55667788;
            memory.store(0x50000800,0x12345678,32);
            memory.store(0x50000804,first,32); memory.store(0x50000808,second,32);
            std::uint64_t budget=100;
            if(recomp_generated::execute_guest(fixture_entry,0x12345678,state,memory,budget)!=sharp_retro::Exit::returned ||
               state.pc!=0x12345678 || state.gpr[4]!=0x50000804 ||
               state.gpr[3]!=0x11223344 || state.gpr[5]!=0xaabbccdd ||
               state.gpr[6]!=0x778899aa || state.gpr[7]!=0x55667788) return 6;
            result=unsigned(state.gpr[0]);
        }
        std::printf("%u %u\n",result,unsigned(memory.load(fixture_counter,32)));
    }
    return std::ferror(stdin) ? 7 : 0;
} catch(const std::exception& e) { std::fprintf(stderr,"candidate: %s\n",e.what()); return 8; } }

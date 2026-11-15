#include "functions.hpp"
#include <array>
#include <cstdio>
#ifndef FIXTURE_BASE
#define FIXTURE_BASE 0x30000000u
#endif

struct Memory : sharp_retro::Memory {
    static constexpr std::uint64_t base=0x100000;
    std::array<std::uint8_t,65536> bytes{};
    std::uint32_t target=FIXTURE_BASE+0x2050;
    void check(std::uint64_t address,unsigned width) {
        if(width!=32 || address<base || address-base>bytes.size() || width/8>bytes.size()-(address-base))
            throw std::runtime_error("guest stack bounds");
    }
    sharp_retro::bits load(std::uint64_t address,unsigned width) override {
        if(address==FIXTURE_BASE+0x2050 && width==32) return target;
        if(address==FIXTURE_BASE+0x3000 && width==32) return FIXTURE_BASE+0x1040;
        check(address,width); sharp_retro::bits value=0;
        for(unsigned i=0;i<4;i++) value|=sharp_retro::bits(bytes[address-base+i])<<(i*8); return value;
    }
    void store(std::uint64_t address,sharp_retro::bits value,unsigned width) override {
        check(address,width); for(unsigned i=0;i<4;i++) bytes[address-base+i]=std::uint8_t(value>>(i*8));
    }
};
int main() {
    try {
        const std::uint32_t offsets[]={0x1000,0x1080,0x10a0,0x10c0,0x10e0,0x1160,0x11a0,0x1160};
        unsigned kind,first,second;
        while(std::scanf("%u %u %u",&kind,&first,&second)==3) {
            if(kind>=8 || (kind==4 && first>8)) return 2;
            Memory memory; memory.target=FIXTURE_BASE+(kind==7 ? 0x11e0 : 0x2050);
            sharp_retro::State state;
            state.gpr[1]=FIXTURE_BASE+0x3000; state.gpr[4]=Memory::base+0x8000;
            state.gpr[3]=0xaabbccdd; state.gpr[5]=0x33445566; state.gpr[6]=0x778899aa; state.gpr[7]=0xbbccddee;
            memory.store(state.gpr[4],0x12345678,32); memory.store(state.gpr[4]+4,first,32); memory.store(state.gpr[4]+8,second,32);
            std::uint64_t budget=1000;
            auto result=recomp_generated::execute_guest(FIXTURE_BASE+offsets[kind],0x12345678,state,memory,budget);
            if(result!=sharp_retro::Exit::returned || state.pc!=0x12345678 || state.gpr[4]!=Memory::base+0x8004 ||
               state.gpr[3]!=0xaabbccdd || state.gpr[5]!=0x33445566 || state.gpr[6]!=0x778899aa || state.gpr[7]!=0xbbccddee) return 3;
            std::printf("%u\n",unsigned(state.gpr[0]));
        }
        return std::feof(stdin) ? 0 : 4;
    } catch(const std::exception& error) { std::fprintf(stderr,"candidate: %s\n",error.what()); return 5; }
}

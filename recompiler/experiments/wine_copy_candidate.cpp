#include "functions.hpp"
#include <array>
#include <cstdio>

struct Arena : sharp_retro::Memory {
    static constexpr std::uint64_t base=0x100000;
    std::array<std::uint8_t,1024> bytes{};
    void check(std::uint64_t address,unsigned width) {
        if(width==0 || width>128 || width%8 || address<base) throw std::runtime_error("guest bounds");
        auto offset=address-base;
        bool object=offset<=512 && width/8<=512-offset;
        bool stack=offset>=800 && offset<=808 && width/8<=808-offset;
        if(!object && !stack) throw std::runtime_error("undeclared memory access");
    }
    sharp_retro::bits load(std::uint64_t address,unsigned width) override {
        check(address,width); sharp_retro::bits value=0;
        for(unsigned i=0;i<width/8;i++) value|=sharp_retro::bits(bytes[address-base+i])<<(i*8);
        return value;
    }
    void store(std::uint64_t address,sharp_retro::bits value,unsigned width) override {
        check(address,width);
        for(unsigned i=0;i<width/8;i++) bytes[address-base+i]=std::uint8_t(value>>(i*8));
    }
};
int main() {
    try {
        unsigned object,source,seed;
        while(std::scanf("%u %u %u",&object,&source,&seed)==3) {
            if(object>476 || source>476) return 2;
            Arena memory; std::uint32_t random=seed;
            for(unsigned i=0;i<512;i++) { random^=random<<13; random^=random>>17; random^=random<<5; memory.bytes[i]=std::uint8_t(random); }
            sharp_retro::State state;
            state.pc=0x92ab70; state.gpr[1]=Arena::base+object; state.gpr[4]=Arena::base+800;
            state.gpr[3]=0xaabbccdd; state.gpr[5]=0x33445566; state.gpr[6]=0x778899aa; state.gpr[7]=0xbbccddee;
            memory.store(state.gpr[4],0x12345678,32); memory.store(state.gpr[4]+4,Arena::base+source,32);
            auto outcome=recomp_generated::fn_0052ab70(state,memory,1000);
            if(outcome!=sharp_retro::Exit::returned || state.pc!=0x12345678 || state.gpr[4]!=Arena::base+808 ||
               state.gpr[3]!=0xaabbccdd || state.gpr[5]!=0x33445566 || state.gpr[6]!=0x778899aa || state.gpr[7]!=0xbbccddee) return 3;
            std::printf("%u %u ",unsigned(state.gpr[0]-Arena::base),unsigned(state.gpr[1]));
            for(unsigned i=0;i<512;i++) std::printf("%02x",memory.bytes[i]);
            std::putchar('\n');
        }
        return std::feof(stdin) ? 0 : 4;
    } catch(const std::exception& error) { std::fprintf(stderr,"candidate: %s\n",error.what()); return 5; }
}

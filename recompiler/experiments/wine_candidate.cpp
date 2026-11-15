#include "functions.hpp"
#include <array>
#include <cstdio>
#include <cstring>

struct Arena final : sharp_retro::Memory {
    static constexpr std::uint64_t base=0x100000;
    std::array<std::uint8_t,1024> bytes{};
    void check(std::uint64_t address,unsigned width) {
        if(width==0 || width>128 || width%8 || address<base || address-base>bytes.size() ||
           width/8>bytes.size()-(address-base)) throw std::runtime_error("guest memory bounds");
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

int main(int argc,char** argv) {
    if(argc!=2 || (std::strcmp(argv[1],"0") && std::strcmp(argv[1],"1"))) return 2;
    try {
        unsigned object,value,seed;
        while(std::scanf("%u %u %u",&object,&value,&seed)==3) {
            if(object>400) return 3;
            Arena memory;
            std::uint32_t random=seed;
            for(unsigned i=0;i<512;i++) { random^=random<<13; random^=random>>17; random^=random<<5; memory.bytes[i]=std::uint8_t(random); }
            sharp_retro::State state;
            state.gpr[1]=Arena::base+object;
            state.gpr[3]=0xaabbccdd; state.gpr[5]=0x33445566;
            state.gpr[6]=0x778899aa; state.gpr[7]=0xbbccddee;
            state.gpr[4]=Arena::base+800;
            memory.store(state.gpr[4],0x12345678,32);
            memory.store(state.gpr[4]+4,value,32);
            bool setter=argv[1][0]=='1';
            state.pc=setter ? 0x424030 : 0x418760;
            auto outcome=setter ? recomp_generated::fn_00024030(state,memory,1000)
                                : recomp_generated::fn_00018760(state,memory,1000);
            if(outcome!=sharp_retro::Exit::returned || state.pc!=0x12345678 ||
               state.gpr[4]!=Arena::base+800+(setter ? 8 : 4) ||
               state.gpr[3]!=0xaabbccdd || state.gpr[5]!=0x33445566 ||
               state.gpr[6]!=0x778899aa || state.gpr[7]!=0xbbccddee) return 4;
            std::printf("%u %u ",unsigned(state.gpr[0]),unsigned(state.gpr[1]-Arena::base));
            for(unsigned i=0;i<512;i++) std::printf("%02x",memory.bytes[i]);
            std::putchar('\n');
        }
        return std::feof(stdin) ? 0 : 5;
    } catch(const std::exception& error) {
        std::fprintf(stderr,"candidate: %s\n",error.what()); return 6;
    }
}

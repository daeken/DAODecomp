// Bounded native/translated instruction debugging, not game validation.
#include "functions.hpp"
#include "image_memory.hpp"
#include <cstdio>
extern "C" {
std::uint32_t word_inputs[8]{},word_outputs[8]{},word_sp=0;
std::uint16_t word_frame[8]{};
std::uint32_t dword_frame[8]{};
std::uint32_t native_word_probe(std::uint32_t);
void native_word_regs();
void native_dword_regs();
}
int main() {
    unsigned probe_cases=0,register_cases=0,dword_cases=0,mismatches=0; std::uint32_t value=0x6d2b79f5;
    for(unsigned iteration=0;iteration<32;iteration++) {
        value=value*1664525u+1013904223u;
        auto expected=native_word_probe(value);
        recomp_generated::ImageMemory memory; memory.map_bytes("stack",0x50000000,4096,true,true); memory.seal();
        sharp_retro::State state; state.gpr[4]=0x50000800; state.gpr[3]=value; state.flags=0x202; state.defined_flags=1u<<10;
        memory.store(state.gpr[4],0x12345678,32); std::uint64_t budget=100;
        auto result=recomp_generated::execute_guest(0x401000,0x12345678,state,memory,budget);
        ++probe_cases;
        if(expected!=0x200000 || result!=sharp_retro::Exit::returned || sharp_retro::read_gpr(state,0)!=expected || state.gpr[3]!=value || state.gpr[4]!=0x50000804) ++mismatches;
        sharp_retro::State initial;
        for(unsigned reg=0;reg<8;reg++) { value=value*1664525u+1013904223u; word_inputs[reg]=value; initial.gpr[reg]=value; }
        initial.gpr[4]=0x50000800; native_word_regs();
        memory.store(initial.gpr[4],0x12345678,32); budget=100;
        result=recomp_generated::execute_guest(0x401080,0x12345678,initial,memory,budget);
        bool match=result==sharp_retro::Exit::returned && initial.gpr[4]==0x50000804 && word_outputs[4]==word_sp && word_frame[3]==std::uint16_t(word_sp);
        const unsigned saved_order[]={7,6,5,4,3,2,1,0};
        for(unsigned reg=0;reg<8;reg++) if(reg!=4) match&=initial.gpr[reg]==word_outputs[reg];
        for(unsigned slot=0;slot<8;slot++) if(slot!=3) match&=word_frame[slot]==std::uint16_t(memory.load(0x500007f0+slot*2,16)) && word_frame[slot]==std::uint16_t(word_inputs[saved_order[slot]]);
        match&=memory.load(0x500007f6,16)==0xdead;
        ++register_cases; if(!match) ++mismatches;
        for(unsigned reg=0;reg<8;reg++) initial.gpr[reg]=word_inputs[reg];
        initial.gpr[4]=0x50000800; native_dword_regs();
        memory.store(initial.gpr[4],0x12345678,32); budget=100;
        result=recomp_generated::execute_guest(0x401100,0x12345678,initial,memory,budget);
        match=result==sharp_retro::Exit::returned && initial.gpr[4]==0x50000804 && word_outputs[4]==word_sp && dword_frame[3]==word_sp;
        for(unsigned reg=0;reg<8;reg++) if(reg!=4) match&=initial.gpr[reg]==word_outputs[reg] && word_outputs[reg]==word_inputs[reg];
        for(unsigned slot=0;slot<8;slot++) if(slot!=3) match&=dword_frame[slot]==memory.load(0x500007e0+slot*4,32);
        match&=memory.load(0x500007ec,32)==0xdeadbeef;
        ++dword_cases; if(!match) ++mismatches;
    }
    std::printf("{\"mixed_flag_probe_cases\":%u,\"word_register_cases\":%u,\"dword_register_cases\":%u,\"mismatches\":%u}\n",probe_cases,register_cases,dword_cases,mismatches);
    return mismatches ? 1 : 0;
}

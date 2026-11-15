// Bounded native-boundary debugging; not game-function validation.
#include "native_imports.hpp"
#include "win32_memory.hpp"
#include <cstdio>
using namespace recomp_generated;
int main() {
 try {
    Win32ProcessMemory memory;
    memory.map_bytes("stack",0x50000000,4096,true,true);
    memory.map_bytes("output",0x50010000,48,true,true);
    memory.map_bytes("readonly",0x50020000,36,true,false);
    memory.seal();
    memory.store_unknown(0x50010000,0,128);
    memory.store_unknown(0x50010010,0,128);
    memory.store_unknown(0x50010020,0,128);
    auto state_for=[&](std::uint32_t output) {
        sharp_retro::State state;
        for(unsigned i=0;i<8;i++) state.gpr[i]=0x12345000u+i;
        state.gpr[4]=0x50000800;
        memory.store(state.gpr[4],0x12345678,32);
        memory.store(state.gpr[4]+4,output,32);
        return state;
    };
    SYSTEM_INFO expected{};
    ::SetLastError(0x13579); ::GetSystemInfo(&expected); auto expected_error=::GetLastError();
    native_error_context.value=0x13579;
    auto state=state_for(0x50010000);
    invoke_native_import({0,"KERNEL32.dll","GetSystemInfo",false},state,memory);
    if(state.pc!=0x12345678 || state.gpr[4]!=0x50000808 || (state.defined_gpr&7) ||
       state.gpr[3]!=0x12345003 || state.gpr[5]!=0x12345005 || state.gpr[6]!=0x12345006 || state.gpr[7]!=0x12345007 ||
       native_error_context.value!=expected_error) return 1;
    const auto* bytes=reinterpret_cast<const std::uint8_t*>(&expected);
    unsigned compared=0;
    for(unsigned offset=0;offset<48;offset++) {
        bool should_be_known=offset<36 && offset!=2 && offset!=3;
        bool known=true;
        try { memory.check_known(0x50010000+offset,8); } catch(const sharp_retro::UnknownMemoryRead&) { known=false; }
        if(known!=should_be_known) return 2;
        if(known) { if(memory.load(0x50010000+offset,8)!=bytes[offset]) return 3; ++compared; }
    }
    for(auto output:{0x50020000u,0x50010020u,0x50030000u}) {
        auto invalid=state_for(output); bool refused=false;
        try { invoke_native_import({0,"KERNEL32.dll","GetSystemInfo",false},invalid,memory); }
        catch(const std::runtime_error&) { refused=true; }
        if(!refused || invalid.pc!=0) return 4;
    }
    std::printf("{\"documented_bytes_match_native\":%u,\"reserved_word_unknown\":true,\"output_tail_unknown\":true,\"void_abi_preserved\":true,\"last_error_matches_native\":true,\"invalid_outputs_refused\":3,\"logical_processors\":%u,\"page_size\":%u}\n",
                compared,unsigned(expected.dwNumberOfProcessors),unsigned(expected.dwPageSize));
    return 0;
 } catch(const std::exception& error) { std::fprintf(stderr,"%s\n",error.what()); return 20; }
}

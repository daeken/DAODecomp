// Focused native profile-folder transport; no game scenario acceptance.
#include "native_imports.hpp"
#include "win32_memory.hpp"
#include <cstdio>
using namespace recomp_generated;
int main(){try{
    Win32ProcessMemory memory;memory.map_bytes("stack",0x50000000,4096,true,true);memory.map_bytes("output",0x50010000,4096,true,true);memory.seal();
    auto invoke=[&](std::uint32_t owner,std::uint32_t csidl,std::uint32_t token,std::uint32_t flags,std::uint32_t destination){
        sharp_retro::State s;s.gpr[4]=0x50000800;for(unsigned reg:{3u,5u,6u,7u})s.gpr[reg]=0x12340000u+reg;
        memory.store(0x50000800,0x12345678,32);unsigned i=1;for(auto v:{owner,csidl,token,flags,destination})memory.store(0x50000800+i++*4,v,32);
        invoke_native_import({0,"SHELL32.dll","SHGetFolderPathW",false},s,memory);
        if(s.pc!=0x12345678 || s.gpr[4]!=0x50000818 || !(s.defined_gpr&1) || (s.defined_gpr&6) || s.gpr[3]!=0x12340003 || s.gpr[5]!=0x12340005 || s.gpr[6]!=0x12340006 || s.gpr[7]!=0x12340007)throw std::runtime_error("folder-path ABI mismatch");return std::uint32_t(s.gpr[0]);
    };
    unsigned cases=0,failures=0,refused=0;
    for(auto input:std::array<std::array<std::uint32_t,3>,7>{{{CSIDL_PERSONAL,0,SHGFP_TYPE_CURRENT},{CSIDL_APPDATA,0,SHGFP_TYPE_DEFAULT},{CSIDL_WINDOWS,0,0},{CSIDL_SYSTEM,0,0},{CSIDL_PERSONAL,0xffffffffu,0},{0x7fffffffu,0,0},{CSIDL_PERSONAL,0,0xffffffffu}}}){
        std::array<wchar_t,MAX_PATH> expected;expected.fill(wchar_t(0x5151));
        for(unsigned i=0;i<MAX_PATH;i++)memory.store_unknown(0x50010000+i*2,0x5151,16);
        ::SetLastError(0x13579);auto direct=::SHGetFolderPathW(nullptr,std::bit_cast<int>(input[0]),reinterpret_cast<HANDLE>(std::uintptr_t(input[1])),input[2],expected.data());auto error=::GetLastError();
        native_error_context.value=0x13579;auto result=invoke(0,input[0],input[1],input[2],0x50010000);
        if(result!=std::uint32_t(direct) || native_error_context.value!=error)return 1;
        auto* actual=static_cast<wchar_t*>(memory.native_pointer(0x50010000,MAX_PATH*2,false,false));
        if(std::memcmp(actual,expected.data(),MAX_PATH*2))return 2;
        unsigned length=0;while(length<MAX_PATH && expected[length])++length;
        for(unsigned i=0;i<=length;i++)if(memory.load(0x50010000+i*2,16)!=std::uint16_t(expected[i]))return 3;
        if(length+1<MAX_PATH){bool unknown=false;try{(void)memory.load(0x50010000+(length+1)*2,16);}catch(const std::runtime_error&){unknown=true;}if(!unknown)return 4;}
        ++cases;if(direct!=S_OK)++failures;
    }
    for(auto input:std::array<std::array<std::uint32_t,3>,3>{{{1,0,0x50010000},{0,123,0x50010000},{0,0,0x50010f00}}}){
        try{(void)invoke(input[0],CSIDL_PERSONAL,input[1],0,input[2]);}catch(const std::runtime_error&){++refused;}
    }
    std::printf("{\"native_folder_cases\":%u,\"native_failures\":%u,\"full_buffer_matches\":true,\"unwritten_tail_unknown\":true,\"refusal_guards\":%u}\n",cases,failures,refused);
    return cases!=7 || !failures || refused!=3 ? 5:0;
}catch(const std::exception& e){std::fprintf(stderr,"folder debug: %s\n",e.what());return 6;}}

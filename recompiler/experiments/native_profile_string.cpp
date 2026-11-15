// Focused native INI read transport; the fixture is not a game configuration.
#include "native_imports.hpp"
#include "win32_memory.hpp"
#include <cstdio>
using namespace recomp_generated;
int main(){try{
    Win32ProcessMemory memory;memory.map_bytes("stack",0x50000000,4096,true,true);memory.map_bytes("data",0x50010000,8192,true,true);memory.seal();
    auto put=[&](std::uint32_t address,const std::wstring& text){for(unsigned i=0;i<=text.size();i++)memory.store(address+i*2,std::uint16_t(text.c_str()[i]),16);};
    wchar_t temp[MAX_PATH];if(!::GetTempPathW(MAX_PATH,temp))return 1;auto file=std::wstring(temp)+L"DAODecomp_profile_"+std::to_wstring(::GetCurrentProcessId())+L".ini";
    if(!::WritePrivateProfileStringW(L"Settings",L"Name",L"quoted value",file.c_str()))return 2;
    put(0x50010000,L"sEtTiNgS");put(0x50010200,L"Name");put(0x50010400,L"fallback  ");put(0x50010600,file);
    auto invoke=[&](std::uint32_t section,std::uint32_t key,std::uint32_t fallback,std::uint32_t capacity,std::uint32_t filename,std::uint32_t destination=0x50011000){
        sharp_retro::State s;s.gpr[4]=0x50000800;for(unsigned reg:{3u,5u,6u,7u})s.gpr[reg]=0x12340000u+reg;
        memory.store(0x50000800,0x12345678,32);unsigned i=1;for(auto v:{section,key,fallback,destination,capacity,filename})memory.store(0x50000800+i++*4,v,32);
        invoke_native_import({0,"KERNEL32.dll","GetPrivateProfileStringW",false},s,memory);
        if(s.pc!=0x12345678 || s.gpr[4]!=0x5000081c || !(s.defined_gpr&1) || (s.defined_gpr&6) || s.gpr[3]!=0x12340003 || s.gpr[5]!=0x12340005 || s.gpr[6]!=0x12340006 || s.gpr[7]!=0x12340007)throw std::runtime_error("profile-string ABI mismatch");return std::uint32_t(s.gpr[0]);
    };
    unsigned cases=0,refused=0;
    for(unsigned mode=0;mode<3;mode++)for(unsigned capacity:{0u,1u,2u,6u,64u}){
        auto key=mode==1 ? L"missing":L"Name";auto filename=mode==2 ? file+L".missing":file;put(0x50010200,key);put(0x50010600,filename);
        std::array<wchar_t,64> expected;expected.fill(wchar_t(0x5151));for(unsigned i=0;i<64;i++)memory.store_unknown(0x50011000+i*2,0x5151,16);
        ::SetLastError(0x13579);auto direct=::GetPrivateProfileStringW(L"sEtTiNgS",key,L"fallback  ",capacity ? expected.data():nullptr,capacity,filename.c_str());auto error=::GetLastError();
        native_error_context.value=0x13579;auto result=invoke(0x50010000,0x50010200,0x50010400,capacity,0x50010600);
        if(result!=direct || native_error_context.value!=error)return 3;
        auto* actual=static_cast<wchar_t*>(memory.native_pointer(0x50011000,128,false,false));if(std::memcmp(actual,expected.data(),128))return 4;
        if(capacity){for(unsigned i=0;i<=result;i++)if(memory.load(0x50011000+i*2,16)!=std::uint16_t(expected[i]))return 5;}
        unsigned tail=capacity ? result+1:0;if(tail<64){bool unknown=false;try{(void)memory.load(0x50011000+tail*2,16);}catch(const std::runtime_error&){unknown=true;}if(!unknown)return 6;}++cases;
    }
    for(auto args:std::array<std::array<std::uint32_t,3>,4>{{{0,0x50010200,0x50011000},{0x50010000,0,0x50011000},{0x12340,0x50010200,0x50011000},{0x50010000,0x50010200,0x50011ff0}}})try{(void)invoke(args[0],args[1],0,64,0x50010600,args[2]);}catch(const std::runtime_error&){++refused;}
    if(!::DeleteFileW(file.c_str()))return 7;
    std::printf("{\"native_profile_cases\":%u,\"full_buffer_matches\":true,\"unwritten_tail_unknown\":true,\"refusal_guards\":%u}\n",cases,refused);return cases!=15 || refused!=4 ? 8:0;
}catch(const std::exception& e){std::fprintf(stderr,"profile debug: %s\n",e.what());return 9;}}

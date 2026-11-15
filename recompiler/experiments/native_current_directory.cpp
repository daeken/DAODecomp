// Actual process-directory effects and errors for reached SetCurrentDirectoryW.
#include "native_imports.hpp"
#include "image_memory.hpp"
#include <cstdio>
#include <vector>
using namespace recomp_generated;
static std::wstring cwd() {
    std::vector<wchar_t> text(32768);auto n=::GetCurrentDirectoryW(DWORD(text.size()),text.data());
    if(!n || n>=text.size())throw std::runtime_error("native directory read failed");return {text.data(),n};
}
int main() {
    auto original=cwd();unsigned cases=0;
    try {
        ImageMemory memory;memory.map_bytes("stack",0x8000,4096,true,true);memory.map_bytes("path",0x9000,65536,true,true);memory.seal();
        auto missing=original+L"\\DAODecomp_nonexistent_directory_"+std::to_wstring(::GetCurrentProcessId());
        if(::GetFileAttributesW(missing.c_str())!=INVALID_FILE_ATTRIBUTES)throw std::runtime_error("failure fixture path unexpectedly exists");
        for(auto path:std::vector<std::wstring>{L".",L"..",original,L"C:\\windows",missing,L""}) {
            if(!::SetCurrentDirectoryW(original.c_str()))return 1;
            ::SetLastError(0x13579);auto expected=::SetCurrentDirectoryW(path.c_str());auto error=::GetLastError();auto expected_directory=cwd();
            if(!::SetCurrentDirectoryW(original.c_str()))return 2;
            for(unsigned i=0;i<=path.size();i++)memory.store(0x9000+i*2,std::uint16_t(path.c_str()[i]),16);
            memory.store(0x8800,0x12345678,32);memory.store(0x8804,0x9000,32);
            sharp_retro::State state;state.gpr[4]=0x8800;
            for(unsigned reg:{3u,5u,6u,7u})state.gpr[reg]=0x12340000u+reg;
            native_error_context.value=0x13579;invoke_native_import({0,"KERNEL32.dll","SetCurrentDirectoryW",false},state,memory);
            if(std::uint32_t(state.gpr[0])!=std::uint32_t(expected) || native_error_context.value!=error || cwd()!=expected_directory ||
               state.pc!=0x12345678 || state.gpr[4]!=0x8808 || !(state.defined_gpr&1) || (state.defined_gpr&6) ||
               state.gpr[3]!=0x12340003 || state.gpr[5]!=0x12340005 || state.gpr[6]!=0x12340006 || state.gpr[7]!=0x12340007)
                throw std::runtime_error("directory effect/error/ABI transport mismatch");
            ++cases;
        }
        if(!::SetCurrentDirectoryW(original.c_str()))return 3;
        sharp_retro::State state;state.gpr[4]=0x8800;memory.store(0x8804,0x2000,32);bool refused=false;
        try{invoke_native_import({0,"KERNEL32.dll","SetCurrentDirectoryW",false},state,memory);}catch(const std::runtime_error&){refused=state.gpr[4]==0x8800 && cwd()==original;}
        std::printf("{\"native_directory_effect_cases\":%u,\"invalid_pointer_refused\":%s,\"original_directory_restored\":true}\n",cases,refused ? "true" : "false");return cases!=6 || !refused ? 4 : 0;
    }catch(const std::exception& e){(void)::SetCurrentDirectoryW(original.c_str());std::fprintf(stderr,"directory debug: %s\n",e.what());return 5;}
}

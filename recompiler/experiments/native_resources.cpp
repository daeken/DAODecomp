// Compare checked translated resource data with read-only original resource
// data. LOAD_LIBRARY_AS_DATAFILE never runs the original module's entry/code.
#include "runtime_api.hpp"
#include "win32_memory.hpp"
#include "image_tls.hpp"
#include "native_imports.hpp"
#include <cstdio>
#include <vector>
#include <cstring>
extern "C" __declspec(dllimport) unsigned char recomp_guestspace_marker;
using namespace recomp_generated;
static std::vector<std::uint8_t> bitmap(HBITMAP handle) {
    if(!handle)return {};
    BITMAP shape{};if(!::GetObjectW(handle,sizeof shape,&shape) || shape.bmWidth<=0 || shape.bmHeight<=0 || shape.bmWidth>1024 || shape.bmHeight>2048)throw std::runtime_error("invalid control bitmap");
    BITMAPINFO info{};info.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);info.bmiHeader.biWidth=shape.bmWidth;info.bmiHeader.biHeight=shape.bmHeight;info.bmiHeader.biPlanes=1;info.bmiHeader.biBitCount=32;info.bmiHeader.biCompression=BI_RGB;
    std::vector<std::uint8_t> data(8+std::size_t(shape.bmWidth)*shape.bmHeight*4);std::memcpy(data.data(),&shape.bmWidth,4);std::memcpy(data.data()+4,&shape.bmHeight,4);
    auto dc=::GetDC(nullptr);auto rows=::GetDIBits(dc,handle,0,UINT(shape.bmHeight),data.data()+8,&info,DIB_RGB_COLORS);::ReleaseDC(nullptr,dc);
    if(rows!=shape.bmHeight)throw std::runtime_error("native bitmap read failed");return data;
}
static std::vector<std::uint8_t> icon_pixels(HICON icon) {
    ICONINFO info{};if(!icon || !::GetIconInfo(icon,&info))throw std::runtime_error("native icon info failed");
    auto color=bitmap(info.hbmColor);auto mask=bitmap(info.hbmMask);if(info.hbmColor)::DeleteObject(info.hbmColor);if(info.hbmMask)::DeleteObject(info.hbmMask);
    color.insert(color.end(),mask.begin(),mask.end());return color;
}
int main(int argc,char** argv) {
 try {
    if(argc!=3 || reinterpret_cast<std::uintptr_t>(::GetModuleHandleA("recomp_guestspace.dll"))!=0x400000)return 1;
    volatile auto marker=&recomp_guestspace_marker;(void)marker;
    Win32ProcessMemory memory;reserve_linked_images(memory);memory.map_bytes("stack",0x50000000,4096,true,true);memory.map_bytes("thread",0x60000000,4096,true,true);
    ThreadTlsLayout tls{0x60000000,0x60010000,0x60020000};initialize_linked_images(memory,argv[1],&tls);
    auto reference=::LoadLibraryExA(argv[2],nullptr,LOAD_LIBRARY_AS_DATAFILE);if(!reference)throw std::runtime_error("read-only original resource load failed");
    auto invoke=[&](const char* symbol,std::uint32_t module,std::uint32_t name) {
        sharp_retro::State state;state.gpr[4]=0x50000800;
        for(unsigned reg:{3u,5u,6u,7u})state.gpr[reg]=0x12340000u+reg;
        memory.store(0x50000800,0x12345678,32);memory.store(0x50000804,module,32);memory.store(0x50000808,name,32);
        invoke_native_import({0,"USER32.dll",symbol,false},state,memory);
        if(state.pc!=0x12345678 || state.gpr[4]!=0x5000080c || !(state.defined_gpr&1) || (state.defined_gpr&6) ||
           state.gpr[3]!=0x12340003 || state.gpr[5]!=0x12340005 || state.gpr[6]!=0x12340006 || state.gpr[7]!=0x12340007)throw std::runtime_error("USER resource ABI mismatch");
        return std::uint32_t(state.gpr[0]);
    };
    auto resource_module=checked_resource_module(memory,memory,0x400000);
    auto original_icon=::LoadIconW(reference,MAKEINTRESOURCEW(106));auto original_error=::GetLastError();
    auto value=invoke("LoadIconW",0x400000,106);auto candidate_error=native_error_context.value;
    if(!original_icon || !value || !native_shared_icons.contains(value) || icon_pixels(original_icon)!=icon_pixels(reinterpret_cast<HICON>(std::uintptr_t(value))))throw std::runtime_error("original/translated resource icon differs");
    unsigned native_cases=0;
    for(unsigned kind=0;kind<2;kind++)for(unsigned valid=0;valid<2;valid++) {
        auto id=valid ? (kind ? 32512u : 32512u) : 0x7ffeu;
        ::SetLastError(0x13579);auto expected=kind ? std::uintptr_t(::LoadCursorW(nullptr,MAKEINTRESOURCEW(id))) : std::uintptr_t(::LoadIconW(nullptr,MAKEINTRESOURCEW(id)));auto error=::GetLastError();
        native_error_context.value=0x13579;auto actual=invoke(kind ? "LoadCursorW" : "LoadIconW",0,id);
        if(actual!=expected || native_error_context.value!=error)throw std::runtime_error("system resource result/error differs");++native_cases;
    }
    ::SetLastError(0x13579);auto expected=::LoadIconW(resource_module,MAKEINTRESOURCEW(0x7ffe));auto error=::GetLastError();native_error_context.value=0x13579;
    if(invoke("LoadIconW",0x400000,0x7ffe)!=std::uintptr_t(expected) || native_error_context.value!=error)return 2;
    unsigned refused=0;for(auto module:{0x400004u,0x12340u})try{(void)invoke("LoadIconW",module,106);}catch(const std::runtime_error&){++refused;}
    if(!::FreeLibrary(reference))return 3;
    std::printf("{\"original_icon_pixels_match\":true,\"system_resource_cases\":%u,\"missing_resource_native_failure\":true,\"invalid_module_guards\":%u,\"original_datafile_last_error_observed\":%u,\"translated_module_last_error_observed\":%u,\"original_module_code_executed\":false}\n",native_cases,refused,unsigned(original_error),unsigned(candidate_error));return refused==2 ? 0 : 4;
 }catch(const std::exception& e){std::fprintf(stderr,"resource debug: %s\n",e.what());return 5;}
}

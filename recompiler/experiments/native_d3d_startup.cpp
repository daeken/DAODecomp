// Diagnose the real startup fault on Wine+Rosetta. No game/API stubs.
#include "native_execution.hpp"
#include <d3d9.h>
#include <cstdio>
#include <cstring>
static void stop_marker() {}
__declspec(noinline) static IDirect3D9* call_on_os_stack(FARPROC target) {
    alignas(16) unsigned char storage[256*1024];
    auto* tib=reinterpret_cast<NT_TIB*>(::NtCurrentTeb());
    recomp_generated::NativeX86Memory memory;
    memory.add_native_stack(reinterpret_cast<std::uintptr_t>(tib->StackLimit),reinterpret_cast<std::uintptr_t>(tib->StackBase));
    sharp_retro::State state;recomp_generated::capture_native_context(state);
    state.gpr[4]=reinterpret_cast<std::uintptr_t>(storage)+sizeof(storage)-4096;
    memory.store(state.gpr[4],reinterpret_cast<std::uintptr_t>(&stop_marker),32);
    memory.store(state.gpr[4]+4,D3D_SDK_VERSION,32);
    if(!recomp_generated::invoke_native_abi_address(reinterpret_cast<std::uintptr_t>(target),state,memory))throw std::runtime_error("native call not admitted");
    if(state.pc!=reinterpret_cast<std::uintptr_t>(&stop_marker))throw std::runtime_error("native return differs");
    return reinterpret_cast<IDirect3D9*>(std::uintptr_t(state.gpr[0]));
}
int main(int argc,char** argv) {
    try {
        bool bridge=argc>1 && std::strncmp(argv[1],"bridge",6)==0;
        if(argc>2) {
            auto module=::LoadLibraryA(argv[2]);
            if(!module) {std::fprintf(stderr,"load runtime failed: %lu\n",::GetLastError());return 2;}
        }
        auto module=::LoadLibraryW(L"d3d9.dll");
        auto target=module ? ::GetProcAddress(module,"Direct3DCreate9") : nullptr;
        if(!target){std::fprintf(stderr,"load D3D9 failed: %lu\n",::GetLastError());return 3;}
        std::fprintf(stderr,"calling Direct3DCreate9 sdk=%u bridge=%u\n",D3D_SDK_VERSION,unsigned(bridge));std::fflush(stderr);
        IDirect3D9* object=nullptr;
        if(!bridge) object=reinterpret_cast<IDirect3D9*(WINAPI*)(UINT)>(target)(D3D_SDK_VERSION);
        else if(std::strcmp(argv[1],"bridge-os")==0) object=call_on_os_stack(target);
        else {
            void* stack=::VirtualAlloc(nullptr,16*1024*1024,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);
            if(!stack){std::fprintf(stderr,"guest stack failed: %lu\n",::GetLastError());return 4;}
            auto low=std::uint32_t(reinterpret_cast<std::uintptr_t>(stack));
            recomp_generated::NativeX86Memory memory;memory.add_native_stack(low,low+16*1024*1024);
            sharp_retro::State state;recomp_generated::capture_native_context(state);
            state.gpr[4]=low+16*1024*1024-4096;
            memory.store(state.gpr[4],reinterpret_cast<std::uintptr_t>(&stop_marker),32);
            memory.store(state.gpr[4]+4,D3D_SDK_VERSION,32);
            if(!recomp_generated::invoke_native_abi_address(reinterpret_cast<std::uintptr_t>(target),state,memory))return 5;
            if(state.pc!=reinterpret_cast<std::uintptr_t>(&stop_marker))return 6;
            object=reinterpret_cast<IDirect3D9*>(std::uintptr_t(state.gpr[0]));
            ::VirtualFree(stack,0,MEM_RELEASE);
        }
        std::printf("{\"direct3d_object_nonnull\":%s,\"bridge\":%s,\"runtime_loaded\":%s,\"game_acceptance\":false}\n",
            object ? "true":"false",bridge ? "true":"false",argc>2 ? "true":"false");
        std::fflush(stdout);
        if(object)object->Release();
        return object ? 0:7;
    }catch(const std::exception& error){std::fprintf(stderr,"control refused: %s\n",error.what());return 8;}
}

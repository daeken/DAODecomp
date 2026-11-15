#pragma once
#include "native_access.hpp"
#include "native_registry.hpp"
#include <set>
#ifdef _WIN32
namespace recomp_generated {
// Shared USER resources have their own token namespace/lifecycle; they are not
// kernel HANDLEs and are never retired through CloseHandle.
inline std::set<std::uint32_t> native_shared_icons,native_shared_cursors;
inline HINSTANCE checked_resource_module(sharp_retro::Memory& memory,NativeAccess& access,std::uint32_t module) {
    if(!module) return nullptr;
    auto extent=access.guest_module_extent(module);
    if(!extent) {
        if(access.guest_image_address(module)) throw std::runtime_error("resource module requires its exact image base");
        (void)registered_native_module(module);
        return reinterpret_cast<HINSTANCE>(std::uintptr_t(module));
    }
    if(extent<64) throw std::runtime_error("resource module image is too small");
    // Only a provider's checked, known, readable flat data backing can become a
    // native HINSTANCE. Original executable sections stay inaccessible.
    auto* header=access.native_pointer(module,64,false);
    if(reinterpret_cast<std::uintptr_t>(header)!=module || memory.load(module,16)!=0x5a4d)
        throw std::runtime_error("resource module requires a checked flat PE image");
    auto nt=std::uint32_t(memory.load(std::uint64_t(module)+0x3c,32));
    if(nt>extent || extent-nt<24+0xe0 || memory.load(std::uint64_t(module)+nt,32)!=0x4550 ||
       memory.load(std::uint64_t(module)+nt+4,16)!=0x14c || memory.load(std::uint64_t(module)+nt+24,16)!=0x10b)
        throw std::runtime_error("resource module is not a bounded PE32 x86 image");
    auto optional=std::uint64_t(module)+nt+24;
    auto headers=std::uint32_t(memory.load(optional+60,32));
    if(headers<nt+24+0xe0 || headers>extent || memory.load(optional+92,32)<3)
        throw std::runtime_error("resource module headers/directories are incomplete");
    (void)access.native_pointer(module,headers,false);
    auto rva=std::uint32_t(memory.load(optional+112,32));
    auto size=std::uint32_t(memory.load(optional+116,32));
    if(rva || size) {
        if(!rva || !size || rva>extent || size>extent-rva) throw std::runtime_error("resource directory exceeds its image");
        (void)access.native_pointer(std::uint32_t(std::uint64_t(module)+rva),size,false);
    }
    return static_cast<HINSTANCE>(header);
}
}
#endif

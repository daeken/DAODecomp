#pragma once
#include "image_memory.hpp"
#ifdef _WIN32
namespace recomp_generated {
// Output-write evidence for this exact Wine 11 x86 provider. Generic Windows
// documentation reserves the WORD; unreviewed providers keep it unknown.
// Review: local/recomp/startup/discovery/system-info-contract-review.json.
inline bool system_info_provider_file(HMODULE module,const char* expected) {
    std::array<wchar_t,32768> path{};
    auto length=::GetModuleFileNameW(module,path.data(),DWORD(path.size()));
    if(!length || length>=path.size()) return false;
    std::ifstream file(std::filesystem::path(path.data()),std::ios::binary|std::ios::ate);
    if(!file) return false;
    auto size=file.tellg(); if(size<=0 || size>32*1024*1024) return false;
    std::vector<std::uint8_t> bytes(static_cast<std::size_t>(size));file.seekg(0);
    if(!file.read(reinterpret_cast<char*>(bytes.data()),static_cast<std::streamsize>(size)) || file.peek()!=std::char_traits<char>::eof()) return false;
    return image_sha256(bytes)==expected;
}
inline bool reviewed_system_info_reserved_writer() {
    static const bool reviewed=[] {
        struct ErrorRestore { DWORD error=::GetLastError(); ~ErrorRestore(){::SetLastError(error);} } restore;
        auto kernel=::GetModuleHandleW(L"kernel32.dll"),base=::GetModuleHandleW(L"kernelbase.dll");
        if(!kernel || !base) return false;
        auto thunk=::GetProcAddress(kernel,"GetSystemInfo"),implementation=::GetProcAddress(base,"GetSystemInfo");
        if(reinterpret_cast<std::uintptr_t>(thunk)-reinterpret_cast<std::uintptr_t>(kernel)!=0xd854u ||
           reinterpret_cast<std::uintptr_t>(implementation)-reinterpret_cast<std::uintptr_t>(base)!=0x2cb50u) return false;
        if(!system_info_provider_file(kernel,"c4b1f1f1210e85acc9f82a898664b1c79b6e83e0485cb59e2e6251885cde9418") ||
           !system_info_provider_file(base,"4fae98d80c69cf36fbfc669acbe87676f0ad06dcebb85cff7b4abee13912a6f6")) return false;
        // These are owned native module addresses from the loader, never guest
        // data/code tokens. The pinned kernel32 thunk jumps through this slot.
        auto target=*reinterpret_cast<const FARPROC*>(reinterpret_cast<std::uintptr_t>(kernel)+0x4f424u);
        return target==implementation;
    }();
    return reviewed;
}
}
#endif

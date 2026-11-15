#pragma once
#include "runtime_api.hpp"
#include <set>
#include <string>
namespace recomp_generated {
#ifdef _WIN32
// Registry handles are opaque values, with a namespace separate from module,
// heap, synchronization and guest-memory identities. Initial guest thread only.
inline std::set<std::uint32_t> native_open_registry_keys;
inline bool predefined_registry_key(std::uint32_t token) {
    return token==0x80000000u || token==0x80000001u || token==0x80000002u ||
           token==0x80000003u || token==0x80000005u;
}
inline HKEY checked_registry_key(std::uint32_t token) {
    if(!predefined_registry_key(token) && !native_open_registry_keys.contains(token))
        throw std::runtime_error("registry API requires a supported predefined or live owned key");
    return reinterpret_cast<HKEY>(std::uintptr_t(token));
}
#endif
}

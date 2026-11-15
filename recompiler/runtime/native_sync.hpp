#pragma once
#include "runtime_api.hpp"
#include "native_access.hpp"
#include <bit>
#include <map>
#include <mutex>
#include <stdexcept>
#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
namespace recomp_generated {
enum class NativeKernelHandleKind { mutex,event,semaphore,file };
inline std::map<std::uint32_t,NativeKernelHandleKind> native_kernel_handles;
inline std::mutex native_kernel_handle_mutex;
inline void register_native_kernel_handle(std::uint32_t token,NativeKernelHandleKind kind) {
    std::lock_guard guard(native_kernel_handle_mutex);
    if(!token || !native_kernel_handles.emplace(token,kind).second)
        throw std::runtime_error("invalid or duplicate live native kernel handle");
}
inline HANDLE checked_native_kernel_handle(std::uint32_t token) {
    std::lock_guard guard(native_kernel_handle_mutex);
    if(!native_kernel_handles.contains(token))
        throw std::runtime_error("kernel object API requires a live owned handle");
    return reinterpret_cast<HANDLE>(std::uintptr_t(token));
}
inline SECURITY_ATTRIBUTES read_native_security_attributes(sharp_retro::Memory& memory,NativeAccess& access,std::uint32_t address) {
    static_assert(sizeof(SECURITY_ATTRIBUTES)==12 && sizeof(BOOL)==4);
    (void)access.native_pointer(address,12,false);
    SECURITY_ATTRIBUTES value{};
    value.nLength=std::uint32_t(memory.load(address,32));
    if(memory.load(std::uint64_t(address)+4,32))
        throw std::runtime_error("non-default native security descriptor requires a typed adapter");
    value.bInheritHandle=std::bit_cast<BOOL>(std::uint32_t(memory.load(std::uint64_t(address)+8,32)));
    return value;
}
}
#endif

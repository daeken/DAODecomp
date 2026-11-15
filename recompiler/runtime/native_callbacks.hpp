#pragma once
#include "native_registry.hpp"
#include <array>
#include <exception>
#include <set>
#include <atomic>
#ifdef _WIN32
namespace recomp_generated {
// The exploration host owns the callback execution context until it explicitly
// terminates an incomplete process. No exception may cross a Windows callback ABI.
inline void (*native_fls_runner)(std::uint32_t,std::uint32_t)=nullptr;
inline std::array<std::uint32_t,64> fls_callback_targets{};
inline std::deque<std::pair<DWORD,int>> guest_fls_slots;
inline std::set<DWORD> guest_tls_slots;
// Registration is real; reaching this native callback remains an explicit
// frontier until EXCEPTION_POINTERS/CONTEXT and guest exception delivery exist.
inline void (*native_unhandled_frontier)(std::uint32_t,EXCEPTION_POINTERS*) noexcept=nullptr;
inline std::atomic<std::uint32_t> guest_unhandled_target{0};
inline std::set<std::uint32_t> returned_native_filters;
inline LONG WINAPI native_unhandled_trampoline(EXCEPTION_POINTERS* pointers) noexcept {
    auto target=guest_unhandled_target.load(std::memory_order_acquire);
    if(native_unhandled_frontier) native_unhandled_frontier(target,pointers);
    std::terminate();
}
inline std::uint32_t install_guest_unhandled_filter(std::uint32_t target,bool translated) {
    auto error=::GetLastError();
    if(translated && !native_unhandled_frontier) throw std::runtime_error("exception-filter registration requires an explicit callback frontier");
    std::uint32_t result;
    {
        std::lock_guard guard(native_registry_mutex);
        if(target && !translated && !returned_native_filters.contains(target))
            throw std::runtime_error("unregistered native exception-filter pointer");
        auto old_guest=guest_unhandled_target.exchange(translated ? target : 0,std::memory_order_acq_rel);
        auto callback=translated ? native_unhandled_trampoline : reinterpret_cast<LPTOP_LEVEL_EXCEPTION_FILTER>(std::uintptr_t(target));
        ::SetLastError(error);
        auto previous=::SetUnhandledExceptionFilter(callback); error=::GetLastError();
        result=previous==native_unhandled_trampoline ? old_guest : std::uint32_t(reinterpret_cast<std::uintptr_t>(previous));
        if(previous && previous!=native_unhandled_trampoline) returned_native_filters.insert(result);
    }
    ::SetLastError(error); return result;
}
template<std::size_t Index> void WINAPI native_fls_trampoline(PVOID value) noexcept {
    auto error=::GetLastError();
    std::uint32_t target;
    { std::lock_guard guard(native_registry_mutex); target=fls_callback_targets[Index]; }
    if(!target || !native_fls_runner) std::terminate();
    ::SetLastError(error);
    try { native_fls_runner(target,std::uint32_t(reinterpret_cast<std::uintptr_t>(value))); }
    catch(...) { std::terminate(); }
}
template<std::size_t... Index> constexpr auto fls_trampoline_table(std::index_sequence<Index...>) {
    return std::array<PFLS_CALLBACK_FUNCTION,sizeof...(Index)>{native_fls_trampoline<Index>...};
}
inline constexpr auto native_fls_trampolines=fls_trampoline_table(std::make_index_sequence<64>{});
inline DWORD allocate_guest_fls(std::uint32_t target) {
    auto initial_error=::GetLastError();
    int callback=-1;
    if(target) {
        if(!native_fls_runner) throw std::runtime_error("translated FLS callbacks require an execution context");
        std::lock_guard guard(native_registry_mutex);
        for(unsigned i=0;i<fls_callback_targets.size();i++) if(!fls_callback_targets[i]) { callback=int(i); break; }
        if(callback<0) throw std::runtime_error("native callback thunk capacity exhausted");
        fls_callback_targets[callback]=target;
    }
    ::SetLastError(initial_error);
    auto index=::FlsAlloc(callback<0 ? nullptr : native_fls_trampolines[callback]);
    auto error=::GetLastError();
    { std::lock_guard guard(native_registry_mutex);
      if(index==FLS_OUT_OF_INDEXES) { if(callback>=0) fls_callback_targets[callback]=0; }
      else guest_fls_slots.emplace_back(index,callback); }
    ::SetLastError(error); return index;
}
inline void require_guest_slot(DWORD index,bool fls) {
    std::lock_guard guard(native_registry_mutex);
    if(fls) { for(auto slot:guest_fls_slots) if(slot.first==index) return; }
    else if(guest_tls_slots.contains(index)) return;
    throw std::runtime_error("unregistered native TLS/FLS index");
}
inline BOOL free_guest_fls(DWORD index) {
    auto initial_error=::GetLastError();
    require_guest_slot(index,true);
    // FlsFree can synchronously call the translated callback. Do not hold the
    // registry lock, clear the target, or replace its context before it returns.
    ::SetLastError(initial_error);
    auto result=::FlsFree(index); auto error=::GetLastError();
    if(result) {
        std::lock_guard guard(native_registry_mutex);
        std::erase_if(guest_fls_slots,[&](auto slot) {
            if(slot.first!=index) return false;
            if(slot.second>=0) fls_callback_targets[slot.second]=0;
            return true;
        });
    }
    ::SetLastError(error); return result;
}
}
#endif

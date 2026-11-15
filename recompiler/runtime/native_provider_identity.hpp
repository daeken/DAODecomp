#pragma once
#include <windows.h>
#include <atomic>
#include <cstdint>
#include <limits>
#include <map>
#include <mutex>
#include <stdexcept>
#include <string>

namespace recomp_generated {
namespace native_provider_identity_detail {
// Loader notifications run before dynamic linking. This callback must neither
// allocate nor call into another module. A saturated epoch disables reuse.
static_assert(std::atomic<std::uint32_t>::is_always_lock_free);
inline std::atomic<std::uint32_t> epoch{1};
inline std::atomic<std::uint32_t> queries{0};
inline std::once_flag initialization;
inline bool notifications_available=false;
inline void* notification_cookie=nullptr;
inline void CALLBACK changed(ULONG reason,const void*,void*) noexcept {
    if(reason!=1 && reason!=2) return;
    auto value=epoch.load(std::memory_order_relaxed);
    while(value!=std::numeric_limits<std::uint32_t>::max() &&
          !epoch.compare_exchange_weak(value,value+1,std::memory_order_release,std::memory_order_relaxed)) {}
}
inline void initialize() {
    std::call_once(initialization,[]{
#if !defined(RECOMP_NATIVE_PROVIDER_CACHE_DISABLED)
        using Register=LONG (NTAPI*)(ULONG,void (CALLBACK*)(ULONG,const void*,void*),void*,void**);
        auto module=::GetModuleHandleW(L"ntdll.dll");
        auto function=module ? reinterpret_cast<Register>(::GetProcAddress(module,"LdrRegisterDllNotification")) : nullptr;
        if(function && function(0,changed,nullptr,&notification_cookie)==0 && notification_cookie)
            notifications_available=true;
#endif
    });
}
inline std::string query(HMODULE module) {
    char filename[32768];
    auto count=::GetModuleFileNameA(module,filename,sizeof(filename));
    if(!count || count>=sizeof(filename)) throw std::runtime_error("native code provider identity unavailable");
    queries.fetch_add(1,std::memory_order_relaxed);
    std::string name(filename,count);
    for(auto& c:name) if(c>='A' && c<='Z') c+=32;
    return name.substr(name.find_last_of("\\/")+1);
}
struct Cache {
    std::uint32_t epoch=0;
    std::map<HMODULE,std::string> names;
};
inline thread_local Cache cache;
}

// Cache the basename only. Callers still obtain the actual module from the
// target address and check executable-page permissions on every native call.
// No DLL reference is retained. Any load/unload invalidates all cached names;
// absent notifications or epoch saturation uses the original query path.
inline std::string native_provider_identity(HMODULE module) {
    using namespace native_provider_identity_detail;
    initialize();
    auto before=epoch.load(std::memory_order_acquire);
    bool reusable=notifications_available && before!=std::numeric_limits<std::uint32_t>::max();
    if(reusable) {
        if(cache.epoch!=before) {cache.names.clear();cache.epoch=before;}
        auto found=cache.names.find(module);
        if(found!=cache.names.end() && epoch.load(std::memory_order_acquire)==before)
            return found->second;
    }
    auto name=query(module);
    if(reusable && epoch.load(std::memory_order_acquire)==before) {
        if(cache.names.size()>=128) cache.names.clear();
        cache.names[module]=name;
    }
    return name;
}
}

#pragma once
#ifdef _WIN32
#include <map>
#include <set>
#include <vector>
namespace recomp_generated {
inline std::set<std::uint32_t> native_owned_heaps,native_process_heaps;
inline HANDLE checked_native_heap(std::uint32_t heap) {
    if(!native_owned_heaps.contains(heap) && !native_process_heaps.contains(heap))
        throw std::runtime_error("heap API requires a registered heap handle");
    return reinterpret_cast<HANDLE>(std::uintptr_t(heap));
}
template<class A> void native_bridge_HeapDestroy(NativeBatchArguments<A>& a,std::uint32_t& result) {
    auto token=a.argument(0);auto heap=checked_native_heap(token);
    if(!native_owned_heaps.contains(token)) throw std::runtime_error("cannot destroy the process heap");
    result=std::uint32_t(call_native([&]{return ::HeapDestroy(heap);}));
    if(result) {a.access().forget_heap(token);native_owned_heaps.erase(token);}
}
template<class A> void native_bridge_HeapLock(NativeBatchArguments<A>& a,std::uint32_t& result) {
    auto heap=checked_native_heap(a.argument(0));result=std::uint32_t(call_native([&]{return ::HeapLock(heap);}));
}
template<class A> void native_bridge_HeapUnlock(NativeBatchArguments<A>& a,std::uint32_t& result) {
    auto heap=checked_native_heap(a.argument(0));result=std::uint32_t(call_native([&]{return ::HeapUnlock(heap);}));
}
template<class A> void native_bridge_HeapReAlloc(NativeBatchArguments<A>& a,std::uint32_t& result) {
    auto token=a.argument(0),flags=a.argument(1),address=a.argument(2),size=a.argument(3);auto heap=checked_native_heap(token);
    if(flags&HEAP_GENERATE_EXCEPTIONS) throw std::runtime_error("native heap exceptions require exception dispatch");
    auto* pointer=a.access().heap_pointer(address,token);
    auto* resized=call_native([&]{return ::HeapReAlloc(heap,flags,pointer,size);});
    result=std::uint32_t(reinterpret_cast<std::uintptr_t>(resized));
    if(resized) {
        auto actual=::HeapSize(heap,0,resized);
        if(actual==SIZE_T(-1) || actual<size) throw std::runtime_error("native resized allocation size unknown");
        result=a.access().replace_heap(address,token,resized,actual ? actual:1,size);
    }
}

struct NativeVirtualRun {std::uint64_t begin,end;bool readable,writable;};
struct NativeVirtualAllocation {std::uint32_t base;std::uint64_t size;NativeAccess* owner;std::vector<NativeVirtualRun> runs;};
inline std::map<std::uint32_t,NativeVirtualAllocation> native_virtual_allocations;
inline std::vector<NativeVirtualRun> inspect_native_virtual(std::uint32_t base,std::uint64_t& size) {
    std::vector<NativeVirtualRun> runs;std::uint64_t cursor=base;
    while(cursor<0x100000000ULL) {
        MEMORY_BASIC_INFORMATION info{};
        if(!::VirtualQuery(reinterpret_cast<const void*>(std::uintptr_t(cursor)),&info,sizeof(info)) || !info.RegionSize)
            throw std::runtime_error("cannot inspect owned virtual allocation");
        if(reinterpret_cast<std::uintptr_t>(info.AllocationBase)!=base) break;
        auto begin=reinterpret_cast<std::uintptr_t>(info.BaseAddress);auto end=std::uint64_t(begin)+info.RegionSize;
        if(begin!=cursor || end<=cursor || end>0x100000000ULL) throw std::runtime_error("invalid native virtual query interval");
        if(info.State==MEM_COMMIT) {
            bool read=info.Protect==PAGE_READONLY || info.Protect==PAGE_READWRITE,write=info.Protect==PAGE_READWRITE;
            if(!read && info.Protect!=PAGE_NOACCESS) throw std::runtime_error("virtual page protection outside reviewed data contract");
            runs.push_back({cursor,end,read,write});
        } else if(info.State!=MEM_RESERVE) throw std::runtime_error("owned virtual allocation has unexpected page state");
        cursor=end;
    }
    size=cursor-base;
    if(!size) throw std::runtime_error("owned virtual allocation no longer exists");
    return runs;
}
inline void synchronize_native_virtual(NativeVirtualAllocation& allocation,std::vector<NativeVirtualRun> next) {
    std::set<std::uint64_t> boundaries;
    for(const auto& run:allocation.runs) {boundaries.insert(run.begin);boundaries.insert(run.end);}
    for(const auto& run:next) {boundaries.insert(run.begin);boundaries.insert(run.end);}
    std::vector<std::uint64_t> points(boundaries.begin(),boundaries.end());
    auto at=[](const auto& runs,std::uint64_t address)->const NativeVirtualRun* {
        for(const auto& run:runs) if(run.begin<=address && address<run.end) return &run;return nullptr;
    };
    for(std::size_t i=1;i<points.size();++i) {
        auto begin=points[i-1],size=points[i]-begin;
        auto* old=at(allocation.runs,begin);auto* now=at(next,begin);
        if(old && !now) allocation.owner->forget_native_range(std::uint32_t(begin),size);
        else if(!old && now) allocation.owner->register_native(reinterpret_cast<void*>(std::uintptr_t(begin)),size,now->readable,now->writable);
        else if(old && now && (old->readable!=now->readable || old->writable!=now->writable))
            allocation.owner->native_permissions(std::uint32_t(begin),size,now->readable,now->writable);
    }
    allocation.runs=std::move(next);
}
inline NativeVirtualAllocation* owned_native_virtual(NativeAccess& access,std::uint32_t address,std::uint64_t size) {
    for(auto& [base,allocation]:native_virtual_allocations)
        if(address>=base && std::uint64_t(address)-base<allocation.size && size<=allocation.size-(std::uint64_t(address)-base)) {
            if(allocation.owner!=&access) throw std::runtime_error("virtual allocation belongs to another guest memory instance");
            return &allocation;
        }
    return nullptr;
}
template<class A> void native_bridge_VirtualAlloc(NativeBatchArguments<A>& a,std::uint32_t& result) {
    auto address=a.argument(0),size=a.argument(1),flags=a.argument(2),protection=a.argument(3);auto& access=a.access();
    if((flags&~DWORD(MEM_RESERVE|MEM_COMMIT|MEM_TOP_DOWN)) || !(flags&(MEM_RESERVE|MEM_COMMIT)) ||
       (protection!=PAGE_READWRITE && protection!=PAGE_READONLY && protection!=PAGE_NOACCESS))
        throw std::runtime_error("VirtualAlloc flags/protection require a separate data/code/state contract");
    if(std::uint64_t(address)+size>0x100000000ULL || (address && access.guest_storage_overlap(address,size ? size:1)))
        throw std::runtime_error("VirtualAlloc overlaps guest namespace or wraps");
    auto* existing=address ? owned_native_virtual(access,address,size):nullptr;
    if(address && !(flags&MEM_RESERVE) && !existing)
        throw std::runtime_error("VirtualAlloc commit requires an owned reservation");
    auto* pointer=call_native([&]{return ::VirtualAlloc(reinterpret_cast<void*>(std::uintptr_t(address)),size,flags,protection);});
    result=std::uint32_t(reinterpret_cast<std::uintptr_t>(pointer));
    if(!pointer) return;
    MEMORY_BASIC_INFORMATION info{};
    if(!::VirtualQuery(pointer,&info,sizeof(info))) throw std::runtime_error("VirtualAlloc result extent is unknown");
    auto base=std::uint32_t(reinterpret_cast<std::uintptr_t>(info.AllocationBase));std::uint64_t actual_size=0;
    auto runs=inspect_native_virtual(base,actual_size);
    auto found=native_virtual_allocations.find(base);
    if(found==native_virtual_allocations.end()) {
        if(access.guest_storage_overlap(base,actual_size)) {
            ::VirtualFree(reinterpret_cast<void*>(std::uintptr_t(base)),0,MEM_RELEASE);
            throw std::runtime_error("native virtual allocation collides with guest storage");
        }
        found=native_virtual_allocations.emplace(base,NativeVirtualAllocation{base,actual_size,&access,{}}).first;
    } else if(found->second.owner!=&access || found->second.size!=actual_size)
        throw std::runtime_error("native virtual reservation identity changed");
    synchronize_native_virtual(found->second,std::move(runs));
}
template<class A> void native_bridge_VirtualFree(NativeBatchArguments<A>& a,std::uint32_t& result) {
    auto address=a.argument(0),size=a.argument(1),flags=a.argument(2);auto& access=a.access();
    if(flags!=MEM_RELEASE && flags!=MEM_DECOMMIT) throw std::runtime_error("unmodeled virtual free flags");
    auto* allocation=owned_native_virtual(access,address,size);
    if(!allocation) throw std::runtime_error("VirtualFree requires owned reservation storage");
    auto base=allocation->base;
    result=std::uint32_t(call_native([&]{return ::VirtualFree(reinterpret_cast<void*>(std::uintptr_t(address)),size,flags);}));
    if(!result) return;
    if(flags==MEM_RELEASE) {synchronize_native_virtual(*allocation,{});native_virtual_allocations.erase(base);}
    else {
        std::uint64_t actual_size=0;auto runs=inspect_native_virtual(base,actual_size);
        if(actual_size!=allocation->size) throw std::runtime_error("decommit changed virtual reservation extent");
        synchronize_native_virtual(*allocation,std::move(runs));
    }
}
} // namespace recomp_generated
#endif

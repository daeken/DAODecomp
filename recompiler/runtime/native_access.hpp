#pragma once
#include <cstddef>
#include <cstdint>
#include <stdexcept>
namespace recomp_generated {
// Only explicit native API adapters can register native-owned storage. Guest
// values are opaque until checked against a live registered range.
struct NativeAccess {
    virtual std::uint32_t register_native(void*,std::uint64_t,bool,bool)=0;
    virtual void* native_pointer(std::uint32_t,std::uint64_t,bool,bool require_defined=true)=0;
    virtual void complete_native_write(std::uint32_t,std::uint64_t)=0;
    virtual void forget_native(void*)=0;
    virtual std::uint32_t register_heap(void*,std::uint64_t,std::uint32_t,std::uint64_t)=0;
    virtual void* heap_pointer(std::uint32_t,std::uint32_t)=0;
    virtual std::uint32_t replace_heap(std::uint32_t,std::uint32_t,void*,std::uint64_t,std::uint64_t)=0;
    virtual bool guest_image_address(std::uint64_t) const=0;
    virtual void forget_heap(std::uint32_t) { throw std::runtime_error("heap-wide lifetime transport unavailable"); }
    virtual bool guest_storage_overlap(std::uint64_t,std::uint64_t) const { throw std::runtime_error("guest storage inventory unavailable"); }
    virtual void native_permissions(std::uint32_t,std::uint64_t,bool,bool) { throw std::runtime_error("native range permissions unavailable"); }
    virtual void forget_native_range(std::uint32_t,std::uint64_t) { throw std::runtime_error("native range lifetime transport unavailable"); }
    virtual std::uint64_t guest_module_extent(std::uint32_t) const { return 0; }
    virtual ~NativeAccess()=default;
};
}

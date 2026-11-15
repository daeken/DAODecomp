#pragma once
#include "image_memory.hpp"
#include "native_access.hpp"
#include <cstring>
namespace recomp_generated {
// Transitional process backing: original data is still a guest image; native
// allocations and OS-owned strings have checked native backing and lifetimes.
// Passing original image/stack storage directly to a native API remains refused.
class ProcessMemory : public ImageMemory,public NativeAccess {
    struct NativeRegion { std::uint32_t address; std::uint64_t size; void* pointer; bool readable,writable; };
    std::vector<NativeRegion> native_regions;
    struct HeapOwner { std::uint32_t heap; std::uint64_t requested; };
    std::unordered_map<std::uint32_t,HeapOwner> heap_owners;
    std::vector<std::pair<std::uint64_t,std::uint64_t>> guest_images;
protected:
    std::uint64_t readable_native_prefix(std::uint64_t address) const {
        for(const auto& region:native_regions)
            if(address>=region.address && address-region.address<region.size) {
                if(!region.readable) throw std::runtime_error("native-backed memory permission violation");
                return region.size-(address-region.address);
            }
        return 0;
    }
private:
    NativeRegion* find(std::uint64_t address,unsigned width,bool write) {
        if(!width || width>128 || width%8 || address>0xffffffffULL || width/8>0x100000000ULL-address)
            throw std::runtime_error("invalid native-backed guest32 access");
        for(auto& region:native_regions)
            if(address>=region.address && address-region.address<region.size && width/8<=region.size-(address-region.address)) {
                if(write ? !region.writable : !region.readable) throw std::runtime_error("native-backed memory permission violation");
                return &region;
            }
        return nullptr;
    }
public:
    bool guest_storage_overlap(std::uint64_t address,std::uint64_t size) const override {
        if(overlaps_mapping(address,size)) return true;
        for(const auto& image:guest_images)
            if(address<image.first+image.second && image.first<address+size) return true;
        return false;
    }
    void forget_heap(std::uint32_t heap) override {
        std::vector<std::uint32_t> retired;
        for(const auto& [address,owner]:heap_owners) if(owner.heap==heap) retired.push_back(address);
        for(auto address:retired) forget_native(reinterpret_cast<void*>(std::uintptr_t(address)));
    }
    // Split only metadata. The underlying virtual allocation remains owned by
    // Windows; surviving bytes and their scalar origins are never copied/reset.
    void change_native_range(std::uint32_t address,std::uint64_t size,bool remove,bool readable,bool writable) {
        if(!size || size>0x100000000ULL-address || guest_storage_overlap(address,size))
            throw std::runtime_error("invalid native range transition");
        std::vector<NativeRegion> next; std::uint64_t covered=0,end=std::uint64_t(address)+size;
        for(const auto& region:native_regions) {
            auto start=std::max<std::uint64_t>(address,region.address),stop=std::min(end,region.address+region.size);
            if(start>=stop) { next.push_back(region); continue; }
            if(heap_owners.contains(region.address)) throw std::runtime_error("virtual range transition overlaps a heap block");
            covered+=stop-start;
            auto piece=[&](std::uint64_t begin,std::uint64_t finish,bool r,bool w) {
                if(begin<finish) next.push_back({std::uint32_t(begin),finish-begin,
                    static_cast<std::uint8_t*>(region.pointer)+(begin-region.address),r,w});
            };
            piece(region.address,start,region.readable,region.writable);
            if(!remove) piece(start,stop,readable,writable);
            piece(stop,region.address+region.size,region.readable,region.writable);
        }
        if(covered!=size) throw std::runtime_error("native range transition has unmapped gaps");
        native_regions=std::move(next);
        if(remove) forget_unknown_range(address,size);
    }
    void native_permissions(std::uint32_t address,std::uint64_t size,bool readable,bool writable) override {
        change_native_range(address,size,false,readable,writable);
    }
    void forget_native_range(std::uint32_t address,std::uint64_t size) override {
        change_native_range(address,size,true,false,false);
    }
    void validate_store(std::uint64_t address,unsigned width) override {
        if(!find(address,width,true)) ImageMemory::validate_store(address,width);
    }
    bool guest_image_address(std::uint64_t address) const override {
        for(const auto& image:guest_images) if(address>=image.first && address-image.first<image.second) return true;
        return false;
    }
    std::uint64_t guest_module_extent(std::uint32_t base) const override {
        for(const auto& image:guest_images) if(image.first==base) return image.second;
        return 0;
    }
    void reserve_image(std::uint64_t address,std::uint64_t size) override {
        if(!size || address>0xffffffffULL || size>0x100000000ULL-address) throw std::runtime_error("invalid guest image range");
        for(const auto& image:guest_images) if(image.first==address && image.second==size) return;
        for(const auto& region:native_regions)
            if(address<region.address+region.size && region.address<address+size) throw std::runtime_error("native allocation overlaps guest image namespace");
        guest_images.emplace_back(address,size);
    }
    std::uint32_t register_native(void* pointer,std::uint64_t size,bool readable,bool writable) override {
        auto address=reinterpret_cast<std::uintptr_t>(pointer);
        if(!pointer) return 0;
        // Native adapters register storage already allocated by Windows. This
        // records its extent; it neither copies nor allocates that many host
        // bytes. The game's startup arenas exceed the old 256 MiB prototype cap.
        if(sizeof(void*)!=4 || !size || address>0xffffffffULL || size>0x100000000ULL-address)
            throw std::runtime_error("unsupported native allocation/address width");
        // An original image/stack mapping must never silently change backing.
        if(overlaps_mapping(address,size)) throw std::runtime_error("native storage overlaps guest-owned memory");
        for(const auto& image:guest_images)
            if(address<image.first+image.second && image.first<address+size) throw std::runtime_error("native allocation overlaps guest image namespace; flat address reservation needed");
        for(auto& region:native_regions) {
            if(address>=region.address && address-region.address<=region.size && size<=region.size-(address-region.address)) {
                if((readable && !region.readable) || (writable && !region.writable)) throw std::runtime_error("native permission upgrade refused");
                return std::uint32_t(address);
            }
            if(address<region.address+region.size && region.address<address+size)
                throw std::runtime_error("ambiguous overlapping native allocations");
        }
        native_regions.push_back({std::uint32_t(address),size,pointer,readable,writable});
        return std::uint32_t(address);
    }
    void* native_pointer(std::uint32_t address,std::uint64_t size,bool write,bool require_defined=true) override {
        if(!address && !size) return nullptr;
        for(auto& region:native_regions)
            if(address>=region.address && std::uint64_t(address)-region.address<=region.size && size<=region.size-(std::uint64_t(address)-region.address)) {
                if(write ? !region.writable : !region.readable) throw std::runtime_error("native pointer permission violation");
                if(require_defined) for(std::uint64_t i=0;i<size;i+=8) check_known(address+i,unsigned(std::min<std::uint64_t>(8,size-i)*8));
                if(write) discard_scalar_images(address,size);
                return static_cast<std::uint8_t*>(region.pointer)+(address-region.address);
            }
        throw std::runtime_error("guest pointer has no registered native backing");
    }
    void complete_native_write(std::uint32_t address,std::uint64_t size) override {
        if(!size) return;
        (void)native_pointer(address,size,true,false);
        for(std::uint64_t i=0;i<size;i+=8) mark_known(address+i,unsigned(std::min<std::uint64_t>(8,size-i)*8));
    }
    void forget_native(void* pointer) override {
        auto before=native_regions.size();
        for(const auto& region:native_regions) if(region.pointer==pointer) {
            forget_unknown_range(region.address,region.size); heap_owners.erase(region.address);
        }
        std::erase_if(native_regions,[&](const auto& region){ return region.pointer==pointer; });
        if(native_regions.size()==before) throw std::runtime_error("free of unregistered native backing");
    }
    std::uint32_t register_heap(void* pointer,std::uint64_t size,std::uint32_t heap,std::uint64_t requested) override {
        if(!pointer || requested>size) throw std::runtime_error("invalid heap allocation registration");
        auto address=register_native(pointer,size,true,true);
        if(!heap_owners.emplace(address,HeapOwner{heap,requested}).second) throw std::runtime_error("duplicate live heap allocation");
        return address;
    }
    void* heap_pointer(std::uint32_t address,std::uint32_t heap) override {
        auto found=heap_owners.find(address);
        if(found==heap_owners.end() || found->second.heap!=heap) throw std::runtime_error("heap pointer requires its live allocation base and owner");
        // Allocator metadata operations do not consume the guest's payload.
        return native_pointer(address,1,false,false);
    }
    std::uint32_t replace_heap(std::uint32_t old_address,std::uint32_t heap,void* pointer,std::uint64_t size,std::uint64_t requested) override {
        (void)heap_pointer(old_address,heap);
        auto owner=heap_owners.at(old_address);
        auto found=std::find_if(native_regions.begin(),native_regions.end(),[&](const auto& region){ return region.address==old_address; });
        if(found==native_regions.end()) throw std::runtime_error("missing heap region");
        auto old_size=found->size;
        // No reads of old backing here: successful HeapReAlloc may have moved it.
        native_regions.erase(found); heap_owners.erase(old_address);
        auto address=register_heap(pointer,size,heap,requested);
        relocate_unknown_range(old_address,old_size,address,size,std::min(owner.requested,requested));
        return address;
    }
    sharp_retro::bits load(std::uint64_t address,unsigned width) override {
        if(auto region=find(address,width,false)) {
            auto bytes=static_cast<const std::uint8_t*>(region->pointer)+(address-region->address);
            sharp_retro::bits value=0;
            for(unsigned i=0;i<width/8;i++) value|=sharp_retro::bits(bytes[i])<<(i*8);
            check_known(address,width,value);
            return value;
        }
        return ImageMemory::load(address,width);
    }
    void store(std::uint64_t address,sharp_retro::bits value,unsigned width) override {
        if(auto region=find(address,width,true)) {
            mark_known(address,width);
            auto bytes=static_cast<std::uint8_t*>(region->pointer)+(address-region->address);
            for(unsigned i=0;i<width/8;i++) bytes[i]=std::uint8_t(value>>(i*8));
            return;
        }
        ImageMemory::store(address,value,width);
    }
};
}

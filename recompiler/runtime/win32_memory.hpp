#pragma once
#include "process_memory.hpp"
#include "native_x87.hpp"
#include <cstdio>
#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#if defined(__i386__)
#include <cpuid.h>
#endif
namespace recomp_generated {
inline void (*native_tail_read_trace)(std::uint32_t,unsigned,std::uint64_t)=nullptr;
// Reserve guest image namespaces before native heaps can occupy them. Original
// instruction pages stay uncommitted/PAGE_NOACCESS. Only declared data, stack and
// thread regions receive backing, and every guest->native conversion is checked.
class Win32ProcessMemory : public ProcessMemory {
    struct Reservation { std::uint64_t address,size; void* pointer; bool owned; };
    struct Backing { std::uint64_t address,size; std::uint8_t* pointer; bool readable,writable; };
    std::vector<Reservation> reservations;
    std::vector<Backing> backing;
    void reserve(std::uint64_t address,std::uint64_t size) {
        if(sizeof(void*)!=4 || !size || address>0xffffffffULL || size>0x100000000ULL-address)
            throw std::runtime_error("flat memory requires nonwrapping Windows x86 ranges");
        for(const auto& range:reservations) {
            if(address>=range.address && address-range.address<=range.size && size<=range.size-(address-range.address)) return;
            if(address<range.address+range.size && range.address<address+size) throw std::runtime_error("overlapping physical reservations");
        }
        // A tiny import DLL reserves the original EXE address range before the
        // host CRT creates heaps. It contains BSS and no entry point/game code.
        auto placeholder=::GetModuleHandleA("recomp_guestspace.dll");
        if(placeholder && reinterpret_cast<std::uintptr_t>(placeholder)==address) {
            auto* dos=reinterpret_cast<const IMAGE_DOS_HEADER*>(placeholder);
            auto* pe=reinterpret_cast<const IMAGE_NT_HEADERS*>(reinterpret_cast<const std::uint8_t*>(placeholder)+dos->e_lfanew);
            if(dos->e_magic!=IMAGE_DOS_SIGNATURE || pe->Signature!=IMAGE_NT_SIGNATURE || pe->OptionalHeader.SizeOfImage<size)
                throw std::runtime_error("reservation DLL has invalid image bounds");
            DWORD old;
            if(!::VirtualProtect(placeholder,SIZE_T(size),PAGE_NOACCESS,&old)) throw std::runtime_error("cannot protect reserved placeholder");
            reservations.push_back({address,size,placeholder,false}); return;
        }
        auto* pointer=::VirtualAlloc(reinterpret_cast<void*>(std::uintptr_t(address)),SIZE_T(size),MEM_RESERVE,PAGE_NOACCESS);
        if(!pointer || reinterpret_cast<std::uintptr_t>(pointer)!=address) {
            auto error=::GetLastError(); if(pointer) ::VirtualFree(pointer,0,MEM_RELEASE);
            for(auto cursor=address;cursor<address+size;) {
                MEMORY_BASIC_INFORMATION information{};
                if(!::VirtualQuery(reinterpret_cast<void*>(std::uintptr_t(cursor)),&information,sizeof information) || !information.RegionSize) break;
                if(information.State!=MEM_FREE)
                    std::printf("{\"event\":\"reservation_conflict\",\"address\":%u,\"allocation_base\":%u,\"region_base\":%u,\"region_size\":%llu,\"state\":%u,\"type\":%u}\n",
                                unsigned(cursor),unsigned(reinterpret_cast<std::uintptr_t>(information.AllocationBase)),
                                unsigned(reinterpret_cast<std::uintptr_t>(information.BaseAddress)),(unsigned long long)information.RegionSize,
                                unsigned(information.State),unsigned(information.Type));
                auto next=reinterpret_cast<std::uintptr_t>(information.BaseAddress)+std::uint64_t(information.RegionSize);
                if(next<=cursor) break; cursor=next;
            }
            throw std::runtime_error("cannot reserve guest namespace at "+std::to_string(address)+"; Windows error "+std::to_string(error));
        }
        reservations.push_back({address,size,pointer,true});
    }
    Backing* find(std::uint64_t address,std::uint64_t size,bool write) {
        if(!size || address>0xffffffffULL || size>0x100000000ULL-address) throw std::runtime_error("invalid flat guest access");
        for(auto& item:backing)
            if(address>=item.address && address-item.address<item.size && size<=item.size-(address-item.address)) {
                if(is_sealed() && (write ? !item.writable : !item.readable)) throw std::runtime_error("flat guest memory permission violation");
                return &item;
            }
        return nullptr;
    }
public:
    void validate_store(std::uint64_t address,unsigned width) override {
        if(!width || width>128 || width%8) throw std::runtime_error("invalid flat store width");
        if(!find(address,width/8,true)) ProcessMemory::validate_store(address,width);
    }
    void execute_x87(sharp_retro::X87Op op,sharp_retro::State& state,std::uint64_t pc,std::uint32_t address,std::uint16_t opcode) override {
        execute_native_x87(*this,op,state,pc,address,opcode);
    }
    std::array<std::uint32_t,4> cpuid(std::uint32_t leaf,std::uint32_t subleaf) override {
#if defined(__i386__)
        std::array<std::uint32_t,4> result{};
        __cpuid_count(leaf,subleaf,result[0],result[1],result[2],result[3]);
        std::printf("{\"event\":\"native_cpuid\",\"leaf\":%u,\"subleaf\":%u,\"eax\":%u,\"ebx\":%u,\"ecx\":%u,\"edx\":%u}\n",
                    leaf,subleaf,result[0],result[1],result[2],result[3]);
        return result;
#else
        return ProcessMemory::cpuid(leaf,subleaf);
#endif
    }
    Win32ProcessMemory()=default;
    Win32ProcessMemory(const Win32ProcessMemory&)=delete;
    Win32ProcessMemory& operator=(const Win32ProcessMemory&)=delete;
    ~Win32ProcessMemory() override { for(auto& range:reservations) if(range.owned) ::VirtualFree(range.pointer,0,MEM_RELEASE); }
    void reserve_image(std::uint64_t address,std::uint64_t size) override {
        reserve(address,size); ProcessMemory::reserve_image(address,size);
    }
    void map_bytes(std::string name,std::uint64_t address,std::uint64_t size,bool readable,bool writable,
                   std::span<const std::uint8_t> bytes={}) override {
        if(is_sealed()) throw std::runtime_error("flat image is already sealed");
        reserve(address,size);
        ImageMemory::map_bytes(std::move(name),address,size,readable,writable,bytes);
        void* pointer=nullptr;
        for(const auto& range:reservations)
            if(!range.owned && address>=range.address && address-range.address<=range.size && size<=range.size-(address-range.address)) {
                pointer=static_cast<std::uint8_t*>(range.pointer)+(address-range.address); DWORD old;
                if(!::VirtualProtect(pointer,SIZE_T(size),PAGE_READWRITE,&old))
                    throw std::runtime_error("cannot commit placeholder data backing at "+std::to_string(address)+"; Windows error "+std::to_string(::GetLastError()));
                break;
            }
        if(!pointer) pointer=::VirtualAlloc(reinterpret_cast<void*>(std::uintptr_t(address)),SIZE_T(size),MEM_COMMIT,PAGE_READWRITE);
        if(!pointer || reinterpret_cast<std::uintptr_t>(pointer)!=address) throw std::runtime_error("failed to commit guest backing");
        std::memset(pointer,0,std::size_t(size)); if(!bytes.empty()) std::memcpy(pointer,bytes.data(),bytes.size());
        backing.push_back({address,size,static_cast<std::uint8_t*>(pointer),readable,writable});
    }
    void seal() override {
        for(auto& region:backing) {
            DWORD old=0,permission=region.writable ? PAGE_READWRITE : region.readable ? PAGE_READONLY : PAGE_NOACCESS;
            if(!::VirtualProtect(region.pointer,SIZE_T(region.size),permission,&old)) throw std::runtime_error("failed to protect guest backing");
        }
        ImageMemory::seal();
    }
    sharp_retro::bits load(std::uint64_t address,unsigned width) override {
        if(!width || width>128 || width%8) throw std::runtime_error("invalid flat load width");
        if(auto* item=find(address,width/8,false)) {
            sharp_retro::bits value=0;
            for(unsigned i=0;i<width/8;i++) value|=sharp_retro::bits(item->pointer[address-item->address+i])<<(i*8);
            check_known(address,width,value);
            return value;
        }
        auto prefix=readable_native_prefix(address);
        if(prefix && prefix<width/8) {
            // MSVC strlen reads aligned words containing a terminator even at
            // a logical HeapSize boundary. Allocation ownership and virtual
            // memory accessibility are different. Observe the actual bytes via
            // Windows, without C++ out-of-allocation pointer arithmetic or an
            // invented padding value. Native pointer conversions stay bounded.
            auto tail=address+prefix,extra=width/8-prefix;
            if(overlaps_mapping(tail,extra) || guest_image_address(tail))
                throw std::runtime_error("native tail read crosses guest-owned storage");
            std::array<std::uint8_t,16> bytes{}; SIZE_T transferred=0;
            auto error=::GetLastError();
            auto success=::ReadProcessMemory(::GetCurrentProcess(),reinterpret_cast<LPCVOID>(std::uintptr_t(address)),bytes.data(),width/8,&transferred);
            auto read_error=::GetLastError(); ::SetLastError(error);
            if(!success || transferred!=width/8)
                throw std::runtime_error("native allocation-tail read is inaccessible; Windows error "+std::to_string(read_error));
            if(native_tail_read_trace) native_tail_read_trace(std::uint32_t(address),width,prefix);
            sharp_retro::bits value=0;
            for(unsigned i=0;i<width/8;i++) value|=sharp_retro::bits(bytes[i])<<(i*8);
            check_known(address,width,value);
            return value;
        }
        return ProcessMemory::load(address,width);
    }
    void store(std::uint64_t address,sharp_retro::bits value,unsigned width) override {
        if(!width || width>128 || width%8) throw std::runtime_error("invalid flat store width");
        if(auto* item=find(address,width/8,true)) {
            mark_known(address,width);
            for(unsigned i=0;i<width/8;i++) item->pointer[address-item->address+i]=std::uint8_t(value>>(i*8));
            return;
        }
        ProcessMemory::store(address,value,width);
    }
    void* native_pointer(std::uint32_t address,std::uint64_t size,bool write,bool require_defined=true) override {
        if(size) if(auto* item=find(address,size,write)) {
            if(require_defined) for(std::uint64_t i=0;i<size;i+=8) check_known(address+i,unsigned(std::min<std::uint64_t>(8,size-i)*8));
            if(write) discard_scalar_images(address,size);
            return item->pointer+(address-item->address);
        }
        return ProcessMemory::native_pointer(address,size,write,require_defined);
    }
};
}
#endif

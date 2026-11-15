#pragma once
#include "native_abi.hpp"
#include "win32_memory.hpp"
#if defined(_WIN32) && defined(__i386__)
namespace recomp_generated {
// Addresses in this execution profile designate the actual Windows x86 virtual
// address space. Scalar accesses are native machine reads/writes, not shadow
// allocations. The strict ImageMemory/ProcessMemory profiles remain separate.
class NativeX86Memory : public Win32ProcessMemory,public NativeExecution {
    std::vector<std::pair<std::uint32_t,std::uint32_t>> stacks;
    static void address_width(std::uint64_t address,unsigned width) {
        if(!width || width>128 || width%8 || address>0xffffffffULL || width/8>0x100000000ULL-address)
            throw std::runtime_error("invalid native x86 memory operand");
    }
public:
    std::array<std::uint32_t,4> cpuid(std::uint32_t leaf,std::uint32_t subleaf) override {
        std::array<std::uint32_t,4> result{};
        __cpuid_count(leaf,subleaf,result[0],result[1],result[2],result[3]);
        return result;
    }
    // Adopt an image already mapped by the Windows loader. This records only
    // the translated address namespace; it neither reserves over the module
    // nor copies/protects its headers, TLS, IAT, resources or native sections.
    void adopt_native_image(std::uint32_t base,std::uint32_t extent) {
        auto module=reinterpret_cast<const std::uint8_t*>(std::uintptr_t(base));
        MEMORY_BASIC_INFORMATION info{};
        if(!extent || !::VirtualQuery(module,&info,sizeof(info)) || info.AllocationBase!=module || info.Type!=MEM_IMAGE)
            throw std::runtime_error("native image is not mapped at its pinned base");
        auto* dos=reinterpret_cast<const IMAGE_DOS_HEADER*>(module);
        if(dos->e_magic!=IMAGE_DOS_SIGNATURE || dos->e_lfanew<0 || std::uint32_t(dos->e_lfanew)>4096u-sizeof(IMAGE_NT_HEADERS32))
            throw std::runtime_error("invalid native image DOS header");
        auto* pe=reinterpret_cast<const IMAGE_NT_HEADERS32*>(module+dos->e_lfanew);
        if(pe->Signature!=IMAGE_NT_SIGNATURE || pe->FileHeader.Machine!=IMAGE_FILE_MACHINE_I386 ||
           pe->OptionalHeader.Magic!=IMAGE_NT_OPTIONAL_HDR32_MAGIC || pe->OptionalHeader.ImageBase!=base ||
           pe->OptionalHeader.SizeOfImage<extent)
            throw std::runtime_error("native image differs from its address contract");
        auto* sections=IMAGE_FIRST_SECTION(pe);
        for(unsigned i=0;i<pe->FileHeader.NumberOfSections;++i)
            if(sections[i].VirtualAddress<extent && (sections[i].Characteristics&IMAGE_SCN_MEM_EXECUTE))
                throw std::runtime_error("original code namespace contains executable native pages");
        ProcessMemory::reserve_image(base,extent);
    }
    void add_native_stack(std::uint32_t low,std::uint32_t high) {
        if(low>=high) throw std::runtime_error("invalid native stack bounds");
        stacks.emplace_back(low,high);
    }
    std::pair<std::uint32_t,std::uint32_t> native_stack(std::uint32_t sp) override {
        // A native thread entry can legitimately be close to StackBase. Only
        // the return word must be in range here; the CPU observes real argument
        // accesses and the callee's actual stack cleanup.
        for(const auto& bounds:stacks) if(sp>bounds.first+4096 && sp<=bounds.second-4) return bounds;
        throw std::runtime_error("native call stack has no declared live physical bounds");
    }
    sharp_retro::bits load(std::uint64_t address,unsigned width) override {
        address_width(address,width);auto pointer=std::uint32_t(address);
        if(width==8) {std::uint8_t v;asm volatile("movb (%1),%0":"=q"(v):"r"(pointer):"memory");return v;}
        if(width==16) {std::uint16_t v;asm volatile("movw (%1),%0":"=r"(v):"r"(pointer):"memory");return v;}
        if(width==32) {std::uint32_t v;asm volatile("movl (%1),%0":"=r"(v):"r"(pointer):"memory");return v;}
        if(width==64) {std::uint64_t v;asm volatile("movq (%1),%%xmm0; movq %%xmm0,%0":"=m"(v):"r"(pointer):"xmm0","memory");return v;}
        if(width==128) {
            std::array<std::uint8_t,16> bytes;asm volatile("movdqu (%1),%%xmm0; movdqu %%xmm0,%0":"=m"(bytes):"r"(pointer):"xmm0","memory");
            sharp_retro::bits v;std::memcpy(&v,bytes.data(),16);return v;
        }
        sharp_retro::bits value=0;
        // Opaque assembly observes physical bytes, including native allocator
        // storage. It does not evaluate an indeterminate C++ object or cast a
        // portable guest token into an unverified host address domain.
        for(unsigned i=0;i<width/8;++i) {
            unsigned char byte;auto cursor=std::uint32_t(address+i);
            asm volatile("movb (%1),%0" : "=q"(byte) : "r"(cursor) : "memory");
            value|=sharp_retro::bits(byte)<<(i*8);
        }
        return value;
    }
    void store(std::uint64_t address,sharp_retro::bits value,unsigned width) override {
        address_width(address,width);auto pointer=std::uint32_t(address);
        if(width==8) {auto v=std::uint8_t(value);asm volatile("movb %1,(%0)"::"r"(pointer),"q"(v):"memory");return;}
        if(width==16) {auto v=std::uint16_t(value);asm volatile("movw %1,(%0)"::"r"(pointer),"r"(v):"memory");return;}
        if(width==32) {auto v=std::uint32_t(value);asm volatile("movl %1,(%0)"::"r"(pointer),"r"(v):"memory");return;}
        if(width==64) {auto v=std::uint64_t(value);asm volatile("movq %1,%%xmm0; movq %%xmm0,(%0)"::"r"(pointer),"m"(v):"xmm0","memory");return;}
        if(width==128) {
            std::array<std::uint8_t,16> bytes;std::memcpy(bytes.data(),&value,16);
            asm volatile("movdqu %1,%%xmm0; movdqu %%xmm0,(%0)"::"r"(pointer),"m"(bytes):"xmm0","memory");return;
        }
        for(unsigned i=0;i<width/8;++i) {
            auto byte=std::uint8_t(value>>(i*8));auto cursor=std::uint32_t(address+i);
            asm volatile("movb %1,(%0)" : : "r"(cursor),"q"(byte) : "memory");
        }
    }
    void validate_store(std::uint64_t address,unsigned width) override {address_width(address,width);}
    sharp_retro::Scalar32 load_scalar32(std::uint64_t address) override {return {std::uint32_t(load(address,32)),0xffffffffu,{}};}
    void store_scalar32(std::uint64_t address,sharp_retro::Scalar32 value) override {
        if(value.known!=0xffffffffu) throw std::runtime_error("native execution refuses unresolved symbolic scalar input");
        store(address,value.value,32);
    }
    void store_scalar8(std::uint64_t address,sharp_retro::Scalar32 value) override {
        if((value.known&0xffu)!=0xffu) throw std::runtime_error("native execution refuses unresolved symbolic byte input");
        store(address,value.value,8);
    }
    void store_scalar16(std::uint64_t address,sharp_retro::Scalar32 value) override {
        if((value.known&0xffffu)!=0xffffu) throw std::runtime_error("native execution refuses unresolved symbolic word input");
        store(address,value.value,16);
    }
    void store_unknown(std::uint64_t,sharp_retro::bits,unsigned) override {
        throw std::runtime_error("native execution refuses fabricated unknown-memory payloads");
    }
    void* native_pointer(std::uint32_t address,std::uint64_t size,bool write,bool=true) override {
        if(!address && !size) return nullptr;
        if(size>0x100000000ULL-address) throw std::runtime_error("wrapping native pointer span");
        auto end=std::uint64_t(address)+std::max<std::uint64_t>(size,1),cursor=std::uint64_t(address);
        while(cursor<end) {
            MEMORY_BASIC_INFORMATION info{};
            if(!::VirtualQuery(reinterpret_cast<const void*>(std::uintptr_t(cursor)),&info,sizeof(info)) || !info.RegionSize ||
               info.State!=MEM_COMMIT || (info.Protect&(PAGE_NOACCESS|PAGE_GUARD))) throw std::runtime_error("inaccessible native pointer span");
            auto protection=info.Protect&0xffu;
            bool readable=protection==PAGE_READONLY || protection==PAGE_READWRITE || protection==PAGE_WRITECOPY ||
                protection==PAGE_EXECUTE_READ || protection==PAGE_EXECUTE_READWRITE || protection==PAGE_EXECUTE_WRITECOPY;
            bool writable=protection==PAGE_READWRITE || protection==PAGE_WRITECOPY || protection==PAGE_EXECUTE_READWRITE || protection==PAGE_EXECUTE_WRITECOPY;
            if(!readable || (write && !writable)) throw std::runtime_error("native pointer span permission violation");
            auto next=std::uint64_t(reinterpret_cast<std::uintptr_t>(info.BaseAddress))+info.RegionSize;
            if(next<=cursor) throw std::runtime_error("invalid native pointer page interval");cursor=next;
        }
        return reinterpret_cast<void*>(std::uintptr_t(address));
    }
};
}
#endif

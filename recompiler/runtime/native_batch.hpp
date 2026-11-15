#pragma once
// Included after call_native by native_imports.hpp. No unchecked native fallback.
#ifdef _WIN32
namespace recomp_generated {
inline bool native_library_is(const char* actual,const char* lower) {
    while(*actual && *lower) {
        auto c=static_cast<unsigned char>(*actual++);
        if(c>='A' && c<='Z') c+=('a'-'A');
        if(c!=static_cast<unsigned char>(*lower++)) return false;
    }
    return *actual==*lower;
}

template<class Arguments> struct NativeBatchArguments {
    sharp_retro::Memory& memory;
    Arguments& argument;
    NativeAccess& access() {
        auto* bridge=dynamic_cast<NativeAccess*>(&memory);
        if(!bridge || sizeof(void*)!=4) throw std::runtime_error("generated native binding requires checked x86 backing");
        return *bridge;
    }
    template<class T> T scalar(unsigned index) {
        static_assert(std::is_integral_v<T> && sizeof(T)==4);
        return std::bit_cast<T>(argument(index));
    }
    template<class Char> const Char* text(unsigned index,bool nullable,int count) {
        static_assert(sizeof(Char)==1 || sizeof(Char)==2);
        auto address=argument(index);
        if(!address) {
            if(nullable || count==0) return nullptr;
            throw std::runtime_error("null string outside generated native contract");
        }
        std::uint64_t units=0;
        if(count<0) {
            constexpr unsigned limit=65536/sizeof(Char);
            for(;units<limit;++units) {
                auto cursor=std::uint64_t(address)+units*sizeof(Char);
                if(cursor+sizeof(Char)>0x100000000ULL) throw std::runtime_error("wrapping generated native string");
                if(memory.load(cursor,sizeof(Char)*8)==0) break;
            }
            if(units==limit) throw std::runtime_error("generated native string exceeds supported bound");
            ++units; // Include the observed terminator in the checked backing.
        } else units=unsigned(count);
        if(std::uint64_t(address)+units*sizeof(Char)>0x100000000ULL)
            throw std::runtime_error("wrapping generated native input span");
        // Preserve the original backing and aliases, rather than copying strings.
        return static_cast<const Char*>(access().native_pointer(address,units*sizeof(Char),false,true));
    }
    template<class T,bool Output> auto record(unsigned index) {
        auto address=argument(index);
        if(!address) throw std::runtime_error("null record outside generated native contract");
        if constexpr(Output) return static_cast<T*>(access().native_pointer(address,sizeof(T),true,false));
        else return static_cast<const T*>(access().native_pointer(address,sizeof(T),false,true));
    }
    void finish_output(std::uint32_t address,std::uint64_t size,bool defined) {
        if(defined) access().complete_native_write(address,size);
        else {
            // Failure grants no knowledge of an unspecified output. Retain real
            // returned bytes, but do not let stale input knownness certify them.
            auto* bytes=static_cast<const unsigned char*>(access().native_pointer(address,size,true,false));
            for(std::uint64_t i=0;i<size;++i) memory.store_unknown(address+i,bytes[i],8);
        }
    }
};

} // namespace recomp_generated
#include "native_files.hpp"
#include "native_memory.hpp"
namespace recomp_generated {

template<class Arguments> bool invoke_batch_native_import(const ImportEntry& import,sharp_retro::Memory& memory,
        Arguments& argument,std::uint32_t& result,unsigned& cleanup,bool& returns_eax) {
    NativeBatchArguments<Arguments> args{memory,argument};
#include "native_bindings.generated.inc"
}
} // namespace recomp_generated
#endif

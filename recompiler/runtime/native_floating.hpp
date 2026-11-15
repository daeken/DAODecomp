#pragma once
#include "runtime_api.hpp"
#include <array>
#include <cstring>
#ifdef _WIN32
namespace recomp_generated {
// Enabled only by launchers with a declared FP entry-state contract. Scalar
// experiments without that contract retain unknown volatile FP status.
inline bool native_floating_bridge_enabled=false;
inline thread_local sharp_retro::State* native_floating_state=nullptr;
struct NativeFloatingBinding {
    sharp_retro::State* previous=native_floating_state;
    explicit NativeFloatingBinding(sharp_retro::State& state) { if(native_floating_bridge_enabled) native_floating_state=&state; }
    ~NativeFloatingBinding() { native_floating_state=previous; }
};
#if defined(__i386__)
using NativeX87Image=std::array<std::uint8_t,108>;
inline std::uint16_t fp_word(const NativeX87Image& bytes,unsigned offset) {
    return std::uint16_t(bytes[offset])|(std::uint16_t(bytes[offset+1])<<8);
}
inline std::uint32_t fp_dword(const NativeX87Image& bytes,unsigned offset) {
    std::uint32_t value; std::memcpy(&value,bytes.data()+offset,4); return value;
}
inline void fp_word(NativeX87Image& bytes,unsigned offset,std::uint16_t value) {
    bytes[offset]=std::uint8_t(value); bytes[offset+1]=std::uint8_t(value>>8);
}
inline void fp_dword(NativeX87Image& bytes,unsigned offset,std::uint32_t value) {
    std::memcpy(bytes.data()+offset,&value,4);
}
using NativeMmxImage=std::array<std::uint64_t,8>;
inline void capture_mmx_bits(NativeMmxImage& values) {
    asm volatile("movq %%mm0,0(%0); movq %%mm1,8(%0); movq %%mm2,16(%0); movq %%mm3,24(%0); movq %%mm4,32(%0); movq %%mm5,40(%0); movq %%mm6,48(%0); movq %%mm7,56(%0)"::"r"(values.data()):"memory");
}
inline void install_mmx_bits(const NativeMmxImage& values) {
    asm volatile("movq 0(%0),%%mm0; movq 8(%0),%%mm1; movq 16(%0),%%mm2; movq 24(%0),%%mm3; movq 32(%0),%%mm4; movq 40(%0),%%mm5; movq 48(%0),%%mm6; movq 56(%0),%%mm7"::"r"(values.data()):"memory");
}
inline bool native_mmx_is_split() {
    static const bool split=[] {
        alignas(16) NativeX87Image host{},seed{},after{};NativeMmxImage mmx{};
        fp_word(seed,0,0x37f);fp_word(seed,8,0xffff);
        asm volatile("fnsave %0":"=m"(host)::"memory");capture_mmx_bits(mmx);
        std::uint64_t marker=0x123456789abcdef0ULL,actual=0;
        asm volatile("frstor %2; movq %3,%%mm0; movq %%mm0,%1; fnsave %0":"=m"(after),"=m"(actual):"m"(seed),"m"(marker):"memory");
        std::uint64_t observed=0;std::memcpy(&observed,after.data()+28,8);
        bool separated=observed!=marker;
        asm volatile("frstor %0"::"m"(host):"memory");
        if(separated)install_mmx_bits(mmx);
        if(actual!=marker || (observed!=marker && observed!=0))throw std::runtime_error("unrecognized native MMX/x87 save-image relationship");
        return separated;
    }();return split;
}
inline std::uint32_t native_mxcsr_mask() {
    alignas(16) std::array<std::uint8_t,512> image{};
    asm volatile("fxsave %0" : "=m"(image) : : "memory");
    std::uint32_t mask; std::memcpy(&mask,image.data()+28,4);
    return mask ? mask : 0xffbf; // SDM fallback for a zero FXSAVE MXCSR_MASK.
}
inline void validate_native_fp(const sharp_retro::State& state,bool require_empty=true) {
    if(state.x87_control_defined!=0xffff || state.x87_status_defined!=0xffff || state.x87_tag_defined!=0xffff ||
       !state.x87_environment_defined || state.mxcsr_defined!=0xffffffffu || !state.mxcsr_mask)
        throw std::runtime_error("native FP boundary requires declared control/status/environment state");
    if(require_empty && state.x87_tag!=0xffff) throw std::runtime_error("native scalar FP boundary requires an empty x87 stack; native value ABI is unimplemented");
    auto top=(state.x87_status>>11)&7;
    for(unsigned i=0;i<8;i++) if(((state.x87_tag>>(((top+i)&7)*2))&3)!=3 && !(state.defined_x87_st&(1u<<i)))
        throw std::runtime_error("unknown live x87 value at native FP boundary");
    if((state.x87_status&0x80) || ((state.x87_status&0x3f)&~state.x87_control))
        throw std::runtime_error("native boundary with a pending x87 exception requires delivery modeling");
    if(state.mxcsr&~state.mxcsr_mask) throw std::runtime_error("invalid MXCSR at native FP boundary");
}
inline NativeX87Image native_fp_image(const sharp_retro::State& state,bool require_empty=true) {
    validate_native_fp(state,require_empty); NativeX87Image image{};
    fp_word(image,0,state.x87_control); fp_word(image,4,state.x87_status); fp_word(image,8,state.x87_tag);
    fp_dword(image,12,state.x87_ip); fp_word(image,16,state.x87_cs); fp_word(image,18,state.x87_opcode);
    fp_dword(image,20,state.x87_dp); fp_word(image,24,state.x87_ds);
    for(unsigned i=0;i<8;i++) if(state.defined_x87_st&(1u<<i))
        std::memcpy(image.data()+28+i*10,state.x87_st[i].data(),10);
    return image;
}
inline void read_native_fp_image(sharp_retro::State& state,const NativeX87Image& image,std::uint32_t mxcsr,bool require_empty=true) {
    state.x87_control=fp_word(image,0); state.x87_status=fp_word(image,4); state.x87_tag=fp_word(image,8);
    state.x87_control_defined=state.x87_status_defined=state.x87_tag_defined=0xffff;
    state.x87_ip=fp_dword(image,12); state.x87_cs=fp_word(image,16); state.x87_opcode=fp_word(image,18)&0x7ff;
    state.x87_dp=fp_dword(image,20); state.x87_ds=fp_word(image,24); state.x87_environment_defined=true;
    state.mxcsr=mxcsr; state.mxcsr_defined=0xffffffffu;
    for(unsigned i=0;i<8;i++) std::memcpy(state.x87_st[i].data(),image.data()+28+i*10,10);
    // An opaque scalar API may have overwritten any empty physical register.
    // Instruction adapters separately establish which logical values are known.
    state.defined_x87_st=0;
    if(require_empty && state.x87_tag!=0xffff) throw std::runtime_error("native scalar call left a nonempty x87 stack; native value ABI is unimplemented");
}
inline void capture_native_fp(sharp_retro::State& state) {
    alignas(16) NativeX87Image image{}; std::uint32_t mxcsr;
    asm volatile("fnsave %0\n\tstmxcsr %1\n\tfrstor %0" : "=m"(image),"=m"(mxcsr) : : "memory");
    state.mxcsr_mask=native_mxcsr_mask(); read_native_fp_image(state,image,mxcsr);
    if(native_mmx_is_split()){capture_mmx_bits(state.native_mmx);state.defined_native_mmx=0xff;}
}
inline void install_native_fp(const sharp_retro::State& state) {
    auto image=native_fp_image(state); auto mxcsr=state.mxcsr;
    bool split=native_mmx_is_split();if(split && state.defined_native_mmx!=0xff)throw std::runtime_error("native FP install requires observed MMX state");
    // FNSAVE clears any host pending exception before restoring the guest image.
    alignas(16) NativeX87Image discarded{};
    asm volatile("fnsave %0\n\tfrstor %1\n\tldmxcsr %2" : "=m"(discarded) : "m"(image),"m"(mxcsr) : "memory");
    if(split)install_mmx_bits(state.native_mmx);
}
class NativeFloatingScope {
    sharp_retro::State* state=nullptr;
    alignas(16) NativeX87Image host{};
    NativeMmxImage host_mmx{};
    bool split_mmx=false;
    std::uint32_t host_mxcsr=0;
    bool require_empty=true;
    void restore() noexcept {
        if(!state) return;
        alignas(16) NativeX87Image discarded{};
        asm volatile("fnsave %0\n\tfrstor %1\n\tldmxcsr %2" : "=m"(discarded) : "m"(host),"m"(host_mxcsr) : "memory");
        if(split_mmx)install_mmx_bits(host_mmx);
        state=nullptr;
    }
public:
    NativeFloatingScope() : NativeFloatingScope(native_floating_bridge_enabled ? native_floating_state : nullptr,true) {}
    explicit NativeFloatingScope(sharp_retro::State& input,bool require_empty) : NativeFloatingScope(&input,require_empty) {}
    NativeFloatingScope(sharp_retro::State* input,bool require_empty) : require_empty(require_empty) {
        if(!input) return;
        split_mmx=native_mmx_is_split();
        auto guest=native_fp_image(*input,require_empty); auto mxcsr=input->mxcsr;
        if(split_mmx)capture_mmx_bits(host_mmx);
        state=input;
        asm volatile("fnsave %0\n\tstmxcsr %1\n\tfrstor %2\n\tldmxcsr %3" : "=m"(host),"=m"(host_mxcsr) : "m"(guest),"m"(mxcsr) : "memory");
        if(split_mmx)install_mmx_bits(input->native_mmx);
    }
    ~NativeFloatingScope() { restore(); }
    void finish() {
        if(!state) return;
        alignas(16) NativeX87Image guest{}; std::uint32_t mxcsr;NativeMmxImage mmx{};
        if(split_mmx)capture_mmx_bits(mmx);
        asm volatile("fnsave %0\n\tstmxcsr %1" : "=m"(guest),"=m"(mxcsr) : : "memory");
        auto* completed=state; restore(); read_native_fp_image(*completed,guest,mxcsr,require_empty);
        if(split_mmx)completed->native_mmx=mmx;
    }
};
#else
inline std::uint32_t native_mxcsr_mask() { throw std::runtime_error("native FP bridge requires Windows x86"); }
inline void capture_native_fp(sharp_retro::State&) { throw std::runtime_error("native FP callback requires Windows x86"); }
inline void install_native_fp(const sharp_retro::State&) { throw std::runtime_error("native FP callback requires Windows x86"); }
struct NativeFloatingScope {
    NativeFloatingScope() { if(native_floating_bridge_enabled) throw std::runtime_error("native FP bridge requires Windows x86"); }
    void finish() {}
};
#endif
}
#endif

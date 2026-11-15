// Reached x87 control debugging under Windows x86. Not game validation.
#include "native_imports.hpp"
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>
static std::uint16_t word(const std::array<std::uint8_t,28>& bytes,unsigned offset) {
    return std::uint16_t(bytes[offset])|(std::uint16_t(bytes[offset+1])<<8);
}
static void word(std::array<std::uint8_t,28>& bytes,unsigned offset,std::uint16_t value) {
    bytes[offset]=std::uint8_t(value); bytes[offset+1]=std::uint8_t(value>>8);
}
int main() {
#if defined(__i386__)
    std::array<std::uint8_t,28> saved{},incoming{},observed{};
    asm volatile("fnstenv %0" : "=m"(saved));
    unsigned clear_mismatches=0,control_mismatches=0;
    for(unsigned value=0;value<65536;value++) {
        incoming=saved; word(incoming,0,0x037f); word(incoming,4,std::uint16_t(value)); word(incoming,8,0xa55a);
        asm volatile("fninit\n\tfldenv %1\n\tfnclex\n\tfnstenv %0" : "=m"(observed) : "m"(incoming) : "memory");
        sharp_retro::State state; state.x87_control=0x037f; state.x87_tag=0xa55a;
        state.x87_status=std::uint16_t(value); state.x87_status_defined=0xffff;
        sharp_retro::x87_fnclex(state);
        if(state.x87_status!=word(observed,4) || state.x87_control!=word(observed,0) || state.x87_tag!=word(observed,8) || state.x87_status_defined!=0xffff) ++clear_mismatches;
        std::uint16_t control=std::uint16_t(value),actual;
        asm volatile("fninit\n\tfldcw %1\n\tfnstcw %0" : "=m"(actual) : "m"(control) : "memory");
        sharp_retro::x87_fldcw(state,control);
        if(actual!=state.x87_control || state.x87_control_defined!=0xffff) ++control_mismatches;
    }
    sharp_retro::State unknown; sharp_retro::x87_fnclex(unknown);
    bool definedness=unknown.x87_status_defined==0x80ff && unknown.x87_control_defined==0 && unknown.x87_tag_defined==0;
    std::array<std::uint16_t,6> after_unmask{};
    for(unsigned bit=0;bit<6;bit++) {
        incoming=saved; word(incoming,0,0x037f); word(incoming,4,std::uint16_t(1u<<bit)); word(incoming,8,0xffff);
        auto control=std::uint16_t(0x037f&~(1u<<bit));
        asm volatile("fninit\n\tfldenv %1\n\tfldcw %2\n\tfnstsw %0" : "=m"(after_unmask[bit]) : "m"(incoming),"m"(control) : "memory");
    }
    asm volatile("fninit\n\tfldenv %0" : : "m"(saved) : "memory");
    sharp_retro::State before; recomp_generated::capture_native_fp(before);
    auto guest=before; guest.x87_control=0x027f; guest.x87_status=0x0120; guest.mxcsr=0x1fa0;
    std::uint16_t entered_control=0; std::uint32_t entered_mxcsr=0;
    recomp_generated::native_floating_bridge_enabled=true;
    {
        recomp_generated::NativeFloatingBinding binding(guest);
        recomp_generated::call_native([&] { asm volatile("fnstcw %0\n\tstmxcsr %1\n\tfnclex" : "=m"(entered_control),"=m"(entered_mxcsr) : : "memory"); });
    }
    sharp_retro::State after; recomp_generated::capture_native_fp(after);
    bool bridge=entered_control==0x027f && entered_mxcsr==0x1fa0 && guest.x87_status==0x0100 &&
        before.x87_control==after.x87_control && before.x87_status==after.x87_status && before.x87_tag==after.x87_tag && before.mxcsr==after.mxcsr;
    {
        recomp_generated::NativeFloatingBinding binding(guest);
        try { recomp_generated::call_native([&] { asm volatile("fnclex" : : : "memory"); throw std::runtime_error("debugging unwind"); }); }
        catch(const std::runtime_error&) {}
    }
    recomp_generated::capture_native_fp(after);
    bool unwind=before.x87_control==after.x87_control && before.x87_status==after.x87_status && before.x87_tag==after.x87_tag && before.mxcsr==after.mxcsr;
    recomp_generated::native_floating_bridge_enabled=false;
    bool unknown_refused=false;
    try { sharp_retro::State unknown; sharp_retro::x87_wait(unknown,0x401000); }
    catch(const std::runtime_error&) { unknown_refused=true; }
    auto pending=guest; pending.x87_control=0x037e; pending.x87_status=1; bool faulted=false;
    try { sharp_retro::x87_wait(pending,0x401000); }
    catch(const sharp_retro::GuestCpuFault& fault) { faulted=fault.vector==16 && fault.pc==0x401000; }
    std::printf("{\"status_inputs\":65536,\"fnclex_mismatches\":%u,\"definedness_preserved\":%s,\"control_inputs\":65536,\"fldcw_normalization_mismatches\":%u,\"native_bridge_restored_host\":%s,\"unwind_restored_host\":%s,\"unknown_wait_refused\":%s,\"pending_wait_faulted\":%s,\"status_after_unmask\":[",clear_mismatches,definedness ? "true" : "false",control_mismatches,bridge ? "true" : "false",unwind ? "true" : "false",unknown_refused ? "true" : "false",faulted ? "true" : "false");
    for(unsigned i=0;i<6;i++) std::printf("%s%u",i ? "," : "",unsigned(after_unmask[i]));
    std::puts("]}");
    return clear_mismatches || !definedness || control_mismatches || !bridge || !unwind || !unknown_refused || !faulted ? 1 : 0;
#else
    std::fputs("This experiment requires Windows x86 instruction execution.\n",stderr); return 2;
#endif
}

#pragma once
#include <cstdint>
#include <functional>
#include <stdexcept>
#include <string>
namespace rapid {
struct Unsupported : std::runtime_error { using std::runtime_error::runtime_error; };
struct Context {
  uint32_t eax=0, ebx=0, ecx=0, edx=0, esi=0, edi=0, ebp=0, esp=0, eflags=2;
  uint32_t image_base=0x400000, return_address=0;
  bool returned=false;
  uint64_t steps=0, step_budget=100000;
  std::function<uint8_t(uint32_t)> memory_read;
  std::function<void(uint32_t,uint8_t)> memory_write;
  std::function<void(Context&,uint32_t)> resolver;
  [[noreturn]] void unsupported(const std::string& why) const { throw Unsupported(why); }
  void tick(uint64_t n=1) { if(n>step_budget || steps>step_budget-n) unsupported("step_budget"); steps+=n; }
  uint8_t read8(uint32_t a) { if(!memory_read) unsupported("memory_read"); return memory_read(a); }
  uint16_t read16(uint32_t a) { return uint16_t(uint16_t(read8(a)) | uint16_t(uint16_t(read8(a+1u))<<8)); }
  uint32_t read32(uint32_t a) { return uint32_t(read16(a)) | (uint32_t(read16(a+2u))<<16); }
  void write8(uint32_t a,uint8_t v) { if(!memory_write) unsupported("memory_write"); memory_write(a,v); }
  void write16(uint32_t a,uint16_t v) { write8(a,uint8_t(v)); write8(a+1u,uint8_t(v>>8)); }
  void write32(uint32_t a,uint32_t v) { write16(a,uint16_t(v)); write16(a+2u,uint16_t(v>>16)); }
  void push32(uint32_t v) { esp-=4u; write32(esp,v); }
  uint32_t pop32() { auto v=read32(esp); esp+=4u; return v; }
  void ret(uint32_t cleanup=0) { return_address=pop32(); esp+=cleanup; returned=true; }
  // Caller pushes the actual guest continuation VA before dispatch. Resolver executes
  // the callee through its RET; this method consumes its return marker, not its stack.
  void call_rva(uint32_t rva,uint32_t continuation_va) {
    tick(); if(!resolver) unsupported("unresolved_call"); push32(continuation_va);
    returned=false; resolver(*this,rva);
    if(!returned || return_address!=continuation_va) unsupported("callee_return"); returned=false;
  }
  void call_va(uint32_t va,uint32_t continuation_va) { call_rva(va-image_base,continuation_va); }
};
using Function=void(*)(Context&);
inline int64_t signed32(uint32_t v) { return v<0x80000000u ? int64_t(v) : int64_t(v)-0x100000000LL; }
inline uint32_t sar32(uint32_t v,uint32_t n) { n&=31u; return n==0 ? v : (v>>n) | ((v&0x80000000u) ? (~uint32_t(0)<<(32u-n)) : 0u); }
}

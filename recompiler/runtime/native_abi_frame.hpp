#pragma once
#if defined(_WIN32) && defined(__i386__)
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <array>
#include <cstddef>
#include <cstdint>
extern "C" {extern DWORD recomp_native_abi_tls_slot;}
namespace recomp_generated {
struct alignas(16) NativeAbiFrame {
    std::uint32_t target,gpr[8],flags,host_sp,call_sp,return_pc,last_error;
    std::uint32_t stack_low,stack_high,host_stack_low,host_stack_high;
    alignas(16) std::array<unsigned char,512> input_fx,output_fx,host_fx;
    std::array<unsigned char,108> output_x87;
    alignas(16) std::array<unsigned char,108> input_x87;
    std::array<std::uint64_t,8> input_mmx,output_mmx,host_mmx;
    std::uint32_t split_mmx;
};
static_assert(sizeof(void*)==4 && offsetof(NativeAbiFrame,gpr)==4 && offsetof(NativeAbiFrame,flags)==36 &&
    offsetof(NativeAbiFrame,stack_low)==56 && offsetof(NativeAbiFrame,host_stack_high)==68 &&
    offsetof(NativeAbiFrame,input_fx)==80 && offsetof(NativeAbiFrame,output_fx)==592 && offsetof(NativeAbiFrame,host_fx)==1104 &&
    offsetof(NativeAbiFrame,output_x87)==1616 && offsetof(NativeAbiFrame,input_x87)==1728 && offsetof(NativeAbiFrame,input_mmx)==1840 && offsetof(NativeAbiFrame,output_mmx)==1904 && offsetof(NativeAbiFrame,host_mmx)==1968 && offsetof(NativeAbiFrame,split_mmx)==2032 && offsetof(NT_TIB,StackBase)==4 && offsetof(NT_TIB,StackLimit)==8);
extern "C" void recomp_native_abi_call(NativeAbiFrame*);
extern "C" void recomp_native_abi_capture(NativeAbiFrame*);
}
#endif

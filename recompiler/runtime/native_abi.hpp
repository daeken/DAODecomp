#pragma once
#include "runtime_api.hpp"
#include <utility>
#if defined(_WIN32) && defined(__i386__)
namespace recomp_generated {
// Native execution is a separate address/state contract from symbolic checking.
// Merely using Windows backing does not opt a strict fixture into this path.
struct NativeExecution {
    virtual std::pair<std::uint32_t,std::uint32_t> native_stack(std::uint32_t)=0;
    virtual ~NativeExecution()=default;
};
bool uses_native_execution(sharp_retro::Memory&);
void capture_native_context(sharp_retro::State&);
void invoke_native_abi_import(const ImportEntry&,sharp_retro::State&,sharp_retro::Memory&);
bool invoke_native_abi_address(std::uint32_t,sharp_retro::State&,sharp_retro::Memory&);
}
#endif

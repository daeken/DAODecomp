#pragma once
#include "runtime_api.hpp"
#include <cstddef>
namespace recomp_generated {
// Private exploration ABI. The source digest additionally pins complete headers,
// compiler/flags and backend identity; sizes/offsets catch accidental ABI mixing.
using OriginFactory=std::uint64_t(*)();
struct CandidateDescriptor {
    std::uint32_t version,state_size,state_align,memory_size,bits_size,pc_offset,x87_offset;
    const char* abi_sha256;
    const char* manifest_sha256;
    const char* module_sha256;
    std::uint32_t image_base;
    const CodeEntry* code;
    std::uint32_t code_count;
    const FunctionEntry* functions;
    std::uint32_t function_count;
    void(*bind_origin)(OriginFactory);
};
using CandidateEntry=const CandidateDescriptor*(*)();
inline bool candidate_layout_matches(const CandidateDescriptor& d) {
    return d.version==1 && d.state_size==sizeof(sharp_retro::State) && d.state_align==alignof(sharp_retro::State) &&
        d.memory_size==sizeof(sharp_retro::Memory) && d.bits_size==sizeof(sharp_retro::bits) &&
        d.pc_offset==offsetof(sharp_retro::State,pc) && d.x87_offset==offsetof(sharp_retro::State,x87_st);
}
}

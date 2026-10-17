#pragma once
#include <cstdint>

namespace dao {
// Descriptive names; original names and subsystem ownership are unknown.
// DAOrigins.exe RVA 0x4a3f0. See analysis/functions.json for binary identity.
std::uint32_t byte_swap_u32(std::uint32_t value) noexcept;

// DAOrigins.exe RVA 0x518a0. 0xffffffff means all bits; other indices wrap mod 32.
std::uint32_t bit_mask_or_all(std::uint32_t index) noexcept;
}

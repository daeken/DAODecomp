#include "dao/primitives.hpp"
#include <limits>

namespace dao {
std::uint32_t byte_swap_u32(std::uint32_t value) noexcept {
    return (value >> 24) | ((value >> 8) & 0x0000ff00u) |
           ((value << 8) & 0x00ff0000u) | (value << 24);
}

std::uint32_t bit_mask_or_all(std::uint32_t index) noexcept {
    if (index == std::numeric_limits<std::uint32_t>::max()) {
        return index;
    }
    // x86 masks a 32-bit shift count. An unmasked C++ shift would be undefined.
    return std::uint32_t{1} << (index & 31u);
}
}

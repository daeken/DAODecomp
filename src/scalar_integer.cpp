#include "dao/scalar_pilot.hpp"

#include <cstdint>

namespace dao {

std::uint32_t fn_00184920(std::uint32_t value) noexcept {
    return (value + std::uint32_t{1}) & 0xffu;
}

std::uint32_t fn_0052aad0(std::uint32_t value) noexcept {
    // High 32 bits of 0xCCCCCCCD * value, then shift right by four.
    const std::uint64_t product = std::uint64_t{0xcccccccdu} * value;
    return static_cast<std::uint32_t>(product >> 36);
}

std::uint32_t fn_005851a0(std::uint32_t value) noexcept {
    const std::int64_t signed_value = static_cast<std::int32_t>(value);
    const std::int64_t product = signed_value * std::int64_t{0x66666667};
    const std::int32_t high = static_cast<std::int32_t>(product >> 32);
    const std::int32_t quotient = high >> 3;
    const std::int32_t adjusted = quotient + static_cast<std::int32_t>(static_cast<std::uint32_t>(quotient) >> 31);
    return static_cast<std::uint32_t>(adjusted);
}

std::uint32_t fn_005c0c00(std::uint32_t value) noexcept {
    const std::int64_t signed_value = value <= 0x7fffffffu
        ? static_cast<std::int64_t>(value)
        : static_cast<std::int64_t>(value) - 4294967296LL;
    return (signed_value % 4 == 0 &&
            (signed_value % 100 != 0 || signed_value % 400 == 0))
        ? 1u : 0u;
}

} // namespace dao

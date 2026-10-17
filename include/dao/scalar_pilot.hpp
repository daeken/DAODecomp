#pragma once
#include <cstdint>

namespace dao {
// Stable RVA names for the first low-cost-model pilot. All parameters and returns
// are unsigned bit patterns; byte-return functions normalize their result to u32.
std::uint32_t fn_00184920(std::uint32_t value) noexcept;
std::uint32_t fn_0052aad0(std::uint32_t value) noexcept;
std::uint32_t fn_005851a0(std::uint32_t value) noexcept;
std::uint32_t fn_005c0c00(std::uint32_t value) noexcept;
std::uint32_t fn_004d79c0(std::uint32_t value) noexcept;
std::uint32_t fn_004b6e70(std::uint32_t value) noexcept;
std::uint32_t fn_004b65b0(std::uint32_t value) noexcept;
std::uint32_t fn_004b64d0(std::uint32_t value) noexcept;
}

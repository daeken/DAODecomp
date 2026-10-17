#include "dao/scalar_pilot.hpp"

namespace dao {

std::uint32_t fn_004d79c0(std::uint32_t value) noexcept {
    const auto byte = static_cast<std::uint8_t>(value);
    const auto lower = (byte >= 0x41u && byte <= 0x5Au)
        ? static_cast<std::uint8_t>(byte + 0x20u)
        : byte;
    return lower;
}

std::uint32_t fn_004b6e70(std::uint32_t value) noexcept {
    const auto byte = static_cast<std::uint8_t>(value);
    return (byte >= 0x41u && byte <= 0x5Au) ? 1u : 0u;
}

std::uint32_t fn_004b65b0(std::uint32_t value) noexcept {
    const auto byte = static_cast<std::uint8_t>(value);
    const bool digit = byte >= 0x30u && byte <= 0x39u;
    const bool lowercase_hex = byte >= 0x61u && byte <= 0x66u;
    const bool uppercase_hex = byte >= 0x41u && byte <= 0x46u;
    return (digit || lowercase_hex || uppercase_hex) ? 1u : 0u;
}

std::uint32_t fn_004b64d0(std::uint32_t value) noexcept {
    const auto byte = static_cast<std::uint8_t>(value);
    const bool in_range = byte >= 0x20u && byte <= 0x7Du;
    const bool excluded_punctuation = byte == 0x25u || byte == 0x22u || byte == 0x27u;
    return (!in_range || excluded_punctuation) ? 1u : 0u;
}

} // namespace dao

#include "dao/indexed_stores.hpp"

#include <array>
#include <cstdint>
#include <exception>
#include <iostream>
#include <span>
#include <string>
#include <string_view>

namespace {
constexpr std::size_t kArenaSize = 512;
constexpr std::uint32_t kMaxObjectOffset = 128;
constexpr std::string_view kHexDigits = "0123456789abcdef";

bool decode_hex(std::string_view text, std::array<std::uint8_t, kArenaSize>& bytes) {
    if (text.size() != bytes.size() * 2) return false;
    for (std::size_t i = 0; i < bytes.size(); ++i) {
        const auto hi = kHexDigits.find(text[2 * i]);
        const auto lo = kHexDigits.find(text[2 * i + 1]);
        if (hi == kHexDigits.npos || lo == kHexDigits.npos) return false;
        bytes[i] = static_cast<std::uint8_t>((hi << 4) | lo);
    }
    return true;
}
} // namespace

int main(int argc, char** argv) {
    if (argc != 2) return 2;
    std::string arena_hex, extra;
    std::uint64_t raw_object = 0, raw_index = 0, raw_value = 0, raw_eax = 0;
    if (!(std::cin >> arena_hex >> raw_object >> raw_index >> raw_value >> raw_eax)
            || std::cin >> extra || raw_object > kMaxObjectOffset
            || raw_index > 0xffffffffULL || raw_value > 0xffffffffULL || raw_eax > 0xffffffffULL)
        return 2;
    std::array<std::uint8_t, kArenaSize> bytes{};
    if (!decode_hex(arena_hex, bytes)) return 2;
    const auto object = static_cast<std::uint32_t>(raw_object);
    const auto index = static_cast<std::uint32_t>(raw_index);
    const auto value = static_cast<std::uint32_t>(raw_value);
    const auto entry_eax = static_cast<std::uint32_t>(raw_eax);
    const std::string_view name{argv[1]};
    std::uint32_t field = 0;
    std::uint32_t width = 0;
    if (name == "fn_00347d10") { field = 0x12a; width = 2; }
    else if (name == "fn_00347d50") { field = 0x138; width = 1; }
    else return 2;

    const auto low = index & 0xff;
    const bool accepted = low < 7;
    const auto offset = object + field + width * low;
    if (accepted && offset + width > bytes.size()) return 2;
    dao::MemoryRange range{offset, width};
    dao::GuestMemory memory{bytes, std::span<const dao::MemoryRange>{},
                            accepted ? std::span{&range, 1} : std::span<const dao::MemoryRange>{}};
    std::uint32_t result = 0;
    try {
        if (name == "fn_00347d10") result = dao::fn_00347d10(memory, object, index, value, entry_eax);
        else result = dao::fn_00347d50(memory, object, index, value, entry_eax);
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 3;
    }
#ifdef DAO_INDEXED_STORE_MUTANT
    // Corrupt the rejected path's upper EAX bits after the real candidate call.
    if (name == "fn_00347d10" && !accepted) result &= 0xff;
#endif
    std::cout << result << '\n';
    for (const auto byte : bytes)
        std::cout << kHexDigits[byte >> 4] << kHexDigits[byte & 0x0f];
    std::cout << '\n';
}

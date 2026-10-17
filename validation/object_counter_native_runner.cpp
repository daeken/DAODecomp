#include "dao/object_counters.hpp"

#include <array>
#include <cstdint>
#include <exception>
#include <iostream>
#include <limits>
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

#ifdef DAO_OBJECT_COUNTER_MUTANT
std::uint32_t read_u32(const std::array<std::uint8_t, kArenaSize>& bytes, std::uint32_t offset) {
    return std::uint32_t{bytes[offset]} | (std::uint32_t{bytes[offset + 1]} << 8)
         | (std::uint32_t{bytes[offset + 2]} << 16) | (std::uint32_t{bytes[offset + 3]} << 24);
}
#endif
} // namespace

int main(int argc, char** argv) {
    if (argc != 2) return 2;
    std::string arena_hex, extra;
    std::uint64_t raw_object = 0;
    if (!(std::cin >> arena_hex >> raw_object) || std::cin >> extra
            || raw_object > kMaxObjectOffset) return 2;
    std::array<std::uint8_t, kArenaSize> bytes{};
    if (!decode_hex(arena_hex, bytes)) return 2;

    const auto object = static_cast<std::uint32_t>(raw_object);
    const std::string_view name{argv[1]};
    std::uint32_t field_offset = 0;
    if (name == "fn_00061f40") field_offset = 0xd0;
    else if (name == "fn_00061f60") field_offset = 0xd4;
    else if (name == "fn_00061f80") field_offset = 0xd8;
    else return 2;
    const auto offset = object + field_offset;
    if (offset + 4 > bytes.size()) return 2;
    const dao::MemoryRange range{offset, 4};
    dao::GuestMemory memory{bytes, std::span{&range, 1}, std::span{&range, 1}};
#ifdef DAO_OBJECT_COUNTER_MUTANT
    const auto old = read_u32(bytes, offset);
#endif
    std::uint32_t result = 0;
    try {
        if (name == "fn_00061f40") result = dao::fn_00061f40(memory, object);
        else if (name == "fn_00061f60") result = dao::fn_00061f60(memory, object);
        else result = dao::fn_00061f80(memory, object);
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 3;
    }
#ifdef DAO_OBJECT_COUNTER_MUTANT
    // Preserve the real D0 store, then mutate only its sentinel return value.
    if (name == "fn_00061f40" && old == std::numeric_limits<std::uint32_t>::max()) result = 1;
#endif
    std::cout << result << '\n';
    for (const auto byte : bytes)
        std::cout << kHexDigits[byte >> 4] << kHexDigits[byte & 0x0f];
    std::cout << '\n';
}

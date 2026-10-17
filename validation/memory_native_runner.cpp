#include "dao/memory_primitives.hpp"
#include <array>
#include <exception>
#include <iostream>
#include <limits>
#include <string>
#include <string_view>

int main(int argc, char** argv) {
    if (argc != 2) return 2;
    std::string hex, extra;
    std::array<std::uint64_t, 4> raw{};
    if (!(std::cin >> hex >> raw[0] >> raw[1] >> raw[2] >> raw[3]) || std::cin >> extra || hex.size() != 256)
        return 2;
    for (const auto v : raw) if (v > std::numeric_limits<std::uint32_t>::max()) return 2;
    std::array<std::uint8_t, 128> bytes{};
    constexpr std::string_view digits = "0123456789abcdef";
    for (std::size_t i = 0; i < bytes.size(); ++i) {
        auto hi = digits.find(hex[2 * i]), lo = digits.find(hex[2 * i + 1]);
        if (hi == digits.npos || lo == digits.npos) return 2;
        bytes[i] = static_cast<std::uint8_t>(hi * 16 + lo);
    }
    const auto destination = static_cast<std::uint32_t>(raw[0]);
    const auto source = static_cast<std::uint32_t>(raw[1]);
    const auto index = static_cast<std::uint32_t>(raw[2]);
    const auto enabled = static_cast<std::uint32_t>(raw[3]);
    const std::string_view name{argv[1]};
    dao::MemoryRange readable{}, writable{};
    if (name == "fn_00061fa0" || name == "fn_0013af20") {
        const std::uint32_t size = name == "fn_00061fa0" ? 16 : 24;
        if (raw[0] + size > bytes.size() || raw[1] + size > bytes.size()) return 2;
        readable = {source, size};
        writable = {destination, size};
    } else if (name == "fn_0035bc40") {
        const auto offset = raw[0] + 4 * (raw[2] >> 5);
        if (offset + 4 > bytes.size()) return 2;
        readable = writable = {static_cast<std::uint32_t>(offset), 4};
    } else return 2;
    dao::GuestMemory memory{bytes, std::span{&readable, 1}, std::span{&writable, 1}};
    std::uint32_t result;
    try {
        if (name == "fn_00061fa0") {
#ifdef DAO_MEMORY_MUTANT
            // Deliberately wrong snapshot copy: loses sequential overlap effects.
            std::array<std::uint32_t, 4> saved{};
            for (std::uint32_t i = 0; i < 4; ++i) saved[i] = memory.read_u32(source + 4 * i);
            for (std::uint32_t i = 0; i < 4; ++i) memory.write_u32(destination + 4 * i, saved[i]);
            result = destination;
#else
            result = dao::fn_00061fa0(memory, destination, source);
#endif
        } else if (name == "fn_0013af20") result = dao::fn_0013af20(memory, destination, source);
        else result = dao::fn_0035bc40(memory, destination, index, enabled);
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 3;
    }
    std::cout << result << '\n';
    for (const auto byte : bytes) std::cout << digits[byte >> 4] << digits[byte & 15];
    std::cout << '\n';
}

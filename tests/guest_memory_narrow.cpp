#include "dao/guest_memory.hpp"
#include <array>
#include <cstdint>
#include <stdexcept>

int main() {
    std::array<std::uint8_t, 16> bytes{};
    for (std::uint32_t i = 0; i < bytes.size(); ++i) bytes[i] = static_cast<std::uint8_t>(i + 0x80);
    const std::array<dao::MemoryRange, 2> ranges{{{3, 2}, {15, 1}}};
    const dao::GuestMemory memory{bytes, ranges, {}};
    if (memory.read_u8(3) != 0x83 || memory.read_u8(4) != 0x84 || memory.read_u8(15) != 0x8f) return 1;
    if (memory.read_u16(3) != 0x8483) return 2;
    for (const auto offset : {2u, 5u, 16u, 0xffffffffu}) {
        try { (void)memory.read_u8(offset); return 3; } catch (const std::out_of_range&) {}
    }
    for (const auto offset : {2u, 4u, 15u, 16u, 0xffffffffu}) {
        try { (void)memory.read_u16(offset); return 4; } catch (const std::out_of_range&) {}
    }
    const dao::GuestMemory denied{bytes, {}, ranges};
    try { (void)denied.read_u8(3); return 5; } catch (const std::out_of_range&) {}
    try { (void)denied.read_u16(3); return 6; } catch (const std::out_of_range&) {}
    const std::array<dao::MemoryRange, 1> too_long{{{15, 2}}};
    const dao::GuestMemory bounded{bytes, too_long, {}};
    try { (void)bounded.read_u16(15); return 7; } catch (const std::out_of_range&) {}
    return 0;
}

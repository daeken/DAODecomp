#include "dao/guest_memory.hpp"
#include <array>
#include <cstdint>
#include <stdexcept>

int main() {
    std::array<std::uint8_t, 16> bytes{};
    bytes.fill(0x55);
    const std::array<dao::MemoryRange, 1> ranges{{{3, 4}}};
    dao::GuestMemory memory{bytes, ranges, ranges};
    memory.write_u32(3, 0x89abcdefu);
    if (memory.read_u32(3) != 0x89abcdefu || bytes[3] != 0xef || bytes[6] != 0x89) return 1;
    for (std::size_t i = 0; i < bytes.size(); ++i)
        if ((i < 3 || i > 6) && bytes[i] != 0x55) return 2;
    for (const auto offset : {2u, 4u, 0xfffffffdu}) {
        try { memory.write_u32(offset, 0); return 3; } catch (const std::out_of_range&) {}
        try { (void)memory.read_u32(offset); return 4; } catch (const std::out_of_range&) {}
    }
    bytes.fill(0x55);
    const std::array<dao::MemoryRange, 2> narrow_ranges{{{3, 2}, {15, 1}}};
    dao::GuestMemory narrow{bytes, {}, narrow_ranges};
    narrow.write_u16(3, 0xabcd);
    narrow.write_u8(15, 0xef);
    if (bytes[3] != 0xcd || bytes[4] != 0xab || bytes[15] != 0xef) return 5;
    for (std::size_t i = 0; i < bytes.size(); ++i)
        if (i != 3 && i != 4 && i != 15 && bytes[i] != 0x55) return 6;
    const auto before = bytes;
    for (const auto offset : {2u, 4u, 15u, 0xffffffffu}) {
        try { narrow.write_u16(offset, 0); return 7; } catch (const std::out_of_range&) {}
        try { narrow.write_u32(offset, 0); return 8; } catch (const std::out_of_range&) {}
    }
    for (const auto offset : {2u, 5u, 16u, 0xffffffffu}) {
        try { narrow.write_u8(offset, 0); return 9; } catch (const std::out_of_range&) {}
    }
    try { (void)narrow.read_u32(3); return 10; } catch (const std::out_of_range&) {}
    if (bytes != before) return 11;
    return 0;
}

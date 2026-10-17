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
    return 0;
}

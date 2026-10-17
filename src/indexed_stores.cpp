#include "dao/indexed_stores.hpp"

namespace dao {

std::uint32_t fn_00347d10(GuestMemory memory, std::uint32_t object, std::uint32_t index,
                          std::uint32_t value, std::uint32_t entry_eax) {
    const auto k = static_cast<std::uint8_t>(index);
    if (k < 7) {
        memory.write_u16(object + 0x12a + 2u * k, static_cast<std::uint16_t>(value));
        return k;
    }
    return (entry_eax & 0xffffff00u) | k;
}

std::uint32_t fn_00347d50(GuestMemory memory, std::uint32_t object, std::uint32_t index,
                          std::uint32_t value, std::uint32_t entry_eax) {
    const auto k = static_cast<std::uint8_t>(index);
    if (k < 7) {
        memory.write_u8(object + 0x138 + k, static_cast<std::uint8_t>(value));
        return k;
    }
    return (entry_eax & 0xffffff00u) | k;
}

} // namespace dao
#include "dao/startup_string.hpp"

namespace dao {

std::uint32_t fn_004e2d29(GuestMemory& memory, std::uint32_t string_pointer,
                          std::uint32_t search) {
    if (string_pointer == 0) {
        return 0;
    }

    const std::uint32_t start = string_pointer - kStartupStringArenaBase;
    const std::uint16_t wanted = static_cast<std::uint16_t>(search);

    std::uint32_t cursor = start;
    while (memory.read_u16(cursor) != 0) {
        cursor += 2;
    }

    for (;;) {
        if (memory.read_u16(cursor) == wanted) {
            return kStartupStringArenaBase + cursor;
        }
        if (cursor == start) {
            break;
        }
        cursor -= 2;
    }

    return 0;
}

} // namespace dao

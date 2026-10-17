#include "dao/object_counters.hpp"

namespace dao {

std::uint32_t fn_00061f40(GuestMemory memory, std::uint32_t object) {
    std::uint32_t value = memory.read_u32(object + 0xd0u);
    if (value == 0xffffffffu) {
        memory.write_u32(object + 0xd0u, 1u);
        return value;
    }
    value += 1u;
    memory.write_u32(object + 0xd0u, value);
    return value;
}

std::uint32_t fn_00061f60(GuestMemory memory, std::uint32_t object) {
    std::uint32_t value = memory.read_u32(object + 0xd4u);
    value += 1u;
    if (value == 0xffffffffu) {
        value = 1u;
    }
    memory.write_u32(object + 0xd4u, value);
    return value;
}

std::uint32_t fn_00061f80(GuestMemory memory, std::uint32_t object) {
    std::uint32_t value = memory.read_u32(object + 0xd8u);
    value += 1u;
    if (value == 0xffffffffu) {
        value = 1u;
    }
    memory.write_u32(object + 0xd8u, value);
    return value;
}

} // namespace dao

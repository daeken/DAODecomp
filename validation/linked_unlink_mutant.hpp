#pragma once
#include <cstdint>
namespace dao {
inline std::uint32_t linked_unlink_mutant_ecx(std::uint32_t list_offset, std::uint32_t) {
    return 0x02000000u + list_offset;
}
}

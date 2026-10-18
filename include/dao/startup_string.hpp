#pragma once
#include "dao/guest_memory.hpp"
namespace dao {
inline constexpr std::uint32_t kStartupStringArenaBase = 0x02000000;
// Raw guest address, never a host pointer. Zero means absent; arena offset zero is valid.
std::uint32_t fn_004e2d29(GuestMemory& memory, std::uint32_t string_pointer,
                          std::uint32_t search);
}

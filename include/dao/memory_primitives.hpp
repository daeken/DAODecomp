#pragma once
#include "dao/guest_memory.hpp"

namespace dao {
std::uint32_t fn_00061fa0(GuestMemory memory, std::uint32_t destination, std::uint32_t source);
std::uint32_t fn_0013af20(GuestMemory memory, std::uint32_t destination, std::uint32_t source);
std::uint32_t fn_0035bc40(GuestMemory memory, std::uint32_t base, std::uint32_t index, std::uint32_t enabled);
} // namespace dao

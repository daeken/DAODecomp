#pragma once
#include "dao/guest_memory.hpp"

namespace dao {
std::uint32_t fn_00347d10(GuestMemory memory, std::uint32_t object, std::uint32_t index,
                        std::uint32_t value, std::uint32_t entry_eax);
std::uint32_t fn_00347d50(GuestMemory memory, std::uint32_t object, std::uint32_t index,
                        std::uint32_t value, std::uint32_t entry_eax);
} // namespace dao

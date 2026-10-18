#pragma once
#include "dao/guest_memory.hpp"

namespace dao {
std::uint32_t fn_00347cf0(GuestMemory memory, std::uint32_t object, std::uint32_t index, std::uint32_t entry_eax);
std::uint32_t fn_00347d30(GuestMemory memory, std::uint32_t object, std::uint32_t index, std::uint32_t entry_eax);
std::uint32_t fn_00347d70(GuestMemory memory, std::uint32_t object, std::uint32_t index, std::uint32_t entry_eax);
std::uint32_t fn_00347d90(GuestMemory memory, std::uint32_t object, std::uint32_t index, std::uint32_t value, std::uint32_t entry_eax);
std::uint32_t fn_00347db0(GuestMemory memory, std::uint32_t object, std::uint32_t index, std::uint32_t entry_eax);
std::uint32_t fn_00347dd0(GuestMemory memory, std::uint32_t object, std::uint32_t index, std::uint32_t value, std::uint32_t entry_eax);
std::uint32_t fn_00347df0(GuestMemory memory, std::uint32_t object, std::uint32_t index, std::uint32_t entry_eax);
std::uint32_t fn_00347e10(GuestMemory memory, std::uint32_t object, std::uint32_t index, std::uint32_t value, std::uint32_t entry_eax);
std::uint32_t fn_00347e70(GuestMemory memory, std::uint32_t object, std::uint32_t index, std::uint32_t entry_eax);
std::uint32_t fn_00347e90(GuestMemory memory, std::uint32_t object, std::uint32_t index, std::uint32_t entry_eax);
std::uint32_t fn_00347eb0(GuestMemory memory, std::uint32_t object, std::uint32_t index, std::uint32_t value, std::uint32_t entry_eax);
} // namespace dao

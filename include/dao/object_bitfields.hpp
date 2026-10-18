#pragma once
#include "dao/guest_memory.hpp"
namespace dao {
// High-level observation interface; source/object are arena offsets.
// The fixed guest arena base is0x02000000; stored pointers and exit_ecx stay raw guest32 bits.
// exit_ecx must contain the raw guest32 exit register; copy return is destination offset.
std::uint32_t fn_0052a680(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t source, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_0052a820(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t source, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_0052a840(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t source, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_0052a860(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t source, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_0052a950(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t source, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_0052a9d0(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t source, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_0052a9f0(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t source, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_0052aa10(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t source, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_0052aa30(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t source, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_0052aa50(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t source, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_0052aa70(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t source, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_0052aa90(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t source, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_0052ab30(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t source, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_0052ab70(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t source, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_0052abe0(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t source, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
}

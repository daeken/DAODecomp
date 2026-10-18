#pragma once
#include "dao/guest_memory.hpp"
namespace dao {
// High-level observation interface, not a claim about original source signatures.
// object is an arena offset; exit_ecx stores raw guest32 bits, base 0x02000000.
std::uint32_t fn_00319290(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_00342080(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_00342090(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_00347b40(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_00347b50(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_00347b70(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_00347b80(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_00347b90(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_003480b0(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_003480c0(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_003b51e0(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_003cd030(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_003cd040(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_003cd0d0(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_003cd140(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_003cd350(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_003edbc0(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_00515af0(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_00515b00(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_00515b10(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_0054f6e0(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
std::uint32_t fn_0054fa40(GuestMemory&, std::uint32_t object, std::uint32_t value, std::uint32_t entry_eax, std::uint32_t& exit_ecx);
}

#pragma once
#include "dao/guest_memory.hpp"

namespace dao {
// Fixed raw guest-address base for this group's bounded arena mapping. Zero is
// null; offset zero denotes the non-null address kLinkedArenaBase.
inline constexpr std::uint32_t kLinkedArenaBase = 0x02000000u;

std::uint32_t fn_00018390(GuestMemory memory, std::uint32_t list, std::uint32_t node);
std::uint32_t fn_000183d0(GuestMemory memory, std::uint32_t list);
// Candidate-facing mapping: .eax is the full raw EAX return; .ecx_exit is the
// separately observed volatile-register value, serialized by the adapter.
struct UnlinkObservation { std::uint32_t eax; std::uint32_t ecx_exit; };
UnlinkObservation fn_00018400(GuestMemory memory, std::uint32_t list, std::uint32_t node);
} // namespace dao

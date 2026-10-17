#include "dao/linked_structures.hpp"

namespace dao {
// Original: DAOrigins.exe SHA-256
// 2346caee611002d4dff6ecef68eb315b63a37004dd98b39c11a9c26c0b45bfb3,
// RVA 0x00018400. Translation of the supplied instruction slice for the
// frozen canonical, disjoint arena domain; preserves arena access order.
UnlinkObservation fn_00018400(GuestMemory memory, std::uint32_t list, std::uint32_t node) {
    const std::uint32_t list_va = kLinkedArenaBase + list;
    const std::uint32_t target_va = kLinkedArenaBase + node;
    std::uint32_t eax = memory.read_u32(list + 0x18u);
    std::uint32_t ecx = list_va;

    if (eax == 0)
        return {eax, ecx};

    while (eax != target_va) {
        eax = memory.read_u32((eax - kLinkedArenaBase) + 4u);
        if (eax == 0)
            return {eax, ecx};
    }

    eax = memory.read_u32(node + 8u);
    if (eax != 0) {
        const std::uint32_t next = memory.read_u32(node + 4u);
        memory.write_u32((eax - kLinkedArenaBase) + 4u, next);
    } else {
        eax = memory.read_u32(node + 4u);
        memory.write_u32(list + 0x18u, eax);
    }

    eax = memory.read_u32(node + 4u);
    if (eax != 0) {
        ecx = memory.read_u32(node + 8u);
        memory.write_u32((eax - kLinkedArenaBase) + 8u, ecx);
        return {eax, ecx};
    }

    const std::uint32_t prev = memory.read_u32(node + 8u);
    memory.write_u32(list + 0x1cu, prev);
    return {eax, ecx};
}
} // namespace dao

#include "dao/linked_structures.hpp"

namespace dao {

std::uint32_t fn_00018390(GuestMemory memory, std::uint32_t list, std::uint32_t node) {
    const std::uint32_t list_tail = list + 0x1c;
    const std::uint32_t appended = kLinkedArenaBase + node;

    const std::uint32_t old_tail = memory.read_u32(list_tail);
    if (old_tail != 0) {
        memory.write_u32(node + 8, old_tail);
        const std::uint32_t reloaded_tail = memory.read_u32(list_tail);
        const std::uint32_t old_tail_offset = reloaded_tail - kLinkedArenaBase;
        memory.write_u32(old_tail_offset + 4, appended);
        memory.write_u32(node + 4, 0);
        memory.write_u32(list_tail, appended);
    } else {
        memory.write_u32(node + 8, 0);
        memory.write_u32(node + 4, 0);
        memory.write_u32(list + 0x18, appended);
        memory.write_u32(list_tail, appended);
    }

    return appended;
}

std::uint32_t fn_000183d0(GuestMemory memory, std::uint32_t list) {
    const std::uint32_t list_head = list + 0x18;
    const std::uint32_t old_head = memory.read_u32(list_head);
    if (old_head == 0)
        return 0;

    const std::uint32_t old_head_offset = old_head - kLinkedArenaBase;
    const std::uint32_t first_next = memory.read_u32(old_head_offset + 4);
    if (first_next != 0) {
        const std::uint32_t reloaded_next = memory.read_u32(old_head_offset + 4);
        const std::uint32_t successor_offset = reloaded_next - kLinkedArenaBase;
        memory.write_u32(list_head, reloaded_next);
        memory.write_u32(successor_offset + 8, 0);
    } else {
        memory.write_u32(list_head, 0);
        memory.write_u32(list + 0x1c, 0);
    }

    return old_head;
}

} // namespace dao
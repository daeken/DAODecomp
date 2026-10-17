#include "dao/memory_primitives.hpp"

namespace dao {

std::uint32_t fn_00061fa0(GuestMemory memory, std::uint32_t destination, std::uint32_t source) {
    const std::uint32_t result = destination;
    if (destination != source) {
        const std::uint32_t word0 = memory.read_u32(source);
        memory.write_u32(destination, word0);
        const std::uint32_t word1 = memory.read_u32(source + 4u);
        memory.write_u32(destination + 4u, word1);
        const std::uint32_t word2 = memory.read_u32(source + 8u);
        memory.write_u32(destination + 8u, word2);
        const std::uint32_t word3 = memory.read_u32(source + 12u);
        memory.write_u32(destination + 12u, word3);
    }
    return result;
}

std::uint32_t fn_0013af20(GuestMemory memory, std::uint32_t destination, std::uint32_t source) {
    const std::uint32_t result = destination;
    if (destination != source) {
        const std::uint32_t word0 = memory.read_u32(source);
        memory.write_u32(destination, word0);
        const std::uint32_t word1 = memory.read_u32(source + 4u);
        memory.write_u32(destination + 4u, word1);
        const std::uint32_t word2 = memory.read_u32(source + 8u);
        memory.write_u32(destination + 8u, word2);
        const std::uint32_t word3 = memory.read_u32(source + 12u);
        memory.write_u32(destination + 12u, word3);
        const std::uint32_t word4 = memory.read_u32(source + 16u);
        memory.write_u32(destination + 16u, word4);
        const std::uint32_t word5 = memory.read_u32(source + 20u);
        memory.write_u32(destination + 20u, word5);
    }
    return result;
}

std::uint32_t fn_0035bc40(GuestMemory memory, std::uint32_t base, std::uint32_t index, std::uint32_t enabled) {
    const std::uint32_t bit = std::uint32_t{1} << (index & 31u);
    const std::uint32_t word_offset = base + ((index >> 5u) * 4u);
    const std::uint32_t old_value = memory.read_u32(word_offset);
    const std::uint32_t value = (enabled & 0xffu) != 0u
        ? (old_value | bit)
        : (old_value & ~bit);
    memory.write_u32(word_offset, value);
    // SHR EAX, 5 leaves the word index in EAX on both return paths.
    return index >> 5u;
}

} // namespace dao

#include "dao/linked_structures.hpp"
#include "linked_unlink_mutant.hpp"

#include <algorithm>
#include <array>
#include <cstdint>
#include <exception>
#include <iostream>
#include <span>
#include <string>
#include <string_view>

namespace {
constexpr std::size_t kArenaSize = 512;
constexpr std::uint32_t kListSize = 32;
constexpr std::uint32_t kNodeSize = 12;
constexpr std::uint32_t kListLimit = kArenaSize - kListSize;
constexpr std::uint32_t kNodeLimit = kArenaSize - kNodeSize;
constexpr std::string_view kHexDigits = "0123456789abcdef";

bool decode_hex(std::string_view text, std::span<std::uint8_t> bytes) {
    if (text.size() != bytes.size() * 2) return false;
    for (std::size_t i = 0; i < bytes.size(); ++i) {
        const auto hi = kHexDigits.find(text[2 * i]);
        const auto lo = kHexDigits.find(text[2 * i + 1]);
        if (hi == kHexDigits.npos || lo == kHexDigits.npos) return false;
        bytes[i] = static_cast<std::uint8_t>((hi << 4) | lo);
    }
    return true;
}

std::uint32_t read_u32(const std::array<std::uint8_t, kArenaSize>& bytes, std::uint32_t offset) {
    return std::uint32_t{bytes[offset]} | (std::uint32_t{bytes[offset + 1]} << 8)
         | (std::uint32_t{bytes[offset + 2]} << 16) | (std::uint32_t{bytes[offset + 3]} << 24);
}

#ifdef DAO_LINKED_STRUCTURE_MUTANT
void write_u32(std::array<std::uint8_t, kArenaSize>& bytes, std::uint32_t offset, std::uint32_t value) {
    for (std::uint32_t i = 0; i < 4; ++i)
        bytes[offset + i] = static_cast<std::uint8_t>(value >> (8 * i));
}
#endif

std::uint32_t pointer(std::uint32_t offset) { return dao::kLinkedArenaBase + offset; }

bool interval_valid(std::uint32_t start, std::uint32_t size, std::uint32_t limit) {
    return start <= limit && std::uint64_t{start} + size <= kArenaSize;
}

bool overlaps(std::uint32_t a, std::uint32_t as, std::uint32_t b, std::uint32_t bs) {
    return std::uint64_t{a} < std::uint64_t{b} + bs && std::uint64_t{b} < std::uint64_t{a} + as;
}

struct Graph {
    std::array<std::uint32_t, 4> nodes{};
    std::array<std::uint32_t, 4> active{};
    std::size_t active_count = 0;
    std::uint32_t head = 0;
    std::uint32_t tail = 0;
};

Graph validate_graph(const std::array<std::uint8_t, kArenaSize>& bytes,
                     std::uint32_t list, std::string_view node_hex) {
    Graph graph;
    if (!interval_valid(list, kListSize, kListLimit)) throw std::runtime_error("invalid list interval");
    std::array<std::uint8_t, 16> encoded{};
    if (!decode_hex(node_hex, encoded)) throw std::runtime_error("invalid node metadata hex");
    for (std::size_t i = 0; i < graph.nodes.size(); ++i) {
        const auto base = 4 * i;
        graph.nodes[i] = std::uint32_t{encoded[base]} | (std::uint32_t{encoded[base + 1]} << 8)
                       | (std::uint32_t{encoded[base + 2]} << 16) | (std::uint32_t{encoded[base + 3]} << 24);
        if (!interval_valid(graph.nodes[i], kNodeSize, kNodeLimit))
            throw std::runtime_error("invalid node interval");
        if (std::find(graph.nodes.begin(), graph.nodes.begin() + static_cast<std::ptrdiff_t>(i), graph.nodes[i])
                != graph.nodes.begin() + static_cast<std::ptrdiff_t>(i))
            throw std::runtime_error("duplicate node offset");
        if (overlaps(list, kListSize, graph.nodes[i], kNodeSize))
            throw std::runtime_error("node overlaps list");
        for (std::size_t j = 0; j < i; ++j)
            if (overlaps(graph.nodes[i], kNodeSize, graph.nodes[j], kNodeSize))
                throw std::runtime_error("node intervals overlap");
    }
    graph.head = read_u32(bytes, list + 0x18);
    graph.tail = read_u32(bytes, list + 0x1c);
    if (graph.head == 0 || graph.tail == 0) {
        if (graph.head != 0 || graph.tail != 0) throw std::runtime_error("inconsistent empty endpoints");
        return graph;
    }
    std::uint32_t current = graph.head;
    std::uint32_t previous = 0;
    while (current != 0) {
        const auto found = std::find_if(graph.nodes.begin(), graph.nodes.end(),
            [current](std::uint32_t offset) { return pointer(offset) == current; });
        if (found == graph.nodes.end()) throw std::runtime_error("active pointer is outside node pool");
        const auto offset = *found;
        if (std::find(graph.active.begin(), graph.active.begin() + static_cast<std::ptrdiff_t>(graph.active_count), offset)
                != graph.active.begin() + static_cast<std::ptrdiff_t>(graph.active_count))
            throw std::runtime_error("active chain contains a cycle");
        if (read_u32(bytes, offset + 8) != previous) throw std::runtime_error("nonreciprocal previous link");
        graph.active[graph.active_count++] = offset;
        const auto next = read_u32(bytes, offset + 4);
        if (next != 0 && std::none_of(graph.nodes.begin(), graph.nodes.end(),
                [next](std::uint32_t member) { return pointer(member) == next; }))
            throw std::runtime_error("active next pointer is outside node pool");
        previous = current;
        current = next;
    }
    if (graph.active_count == 0 || pointer(graph.active[graph.active_count - 1]) != graph.tail)
        throw std::runtime_error("tail does not match active chain");
    if (read_u32(bytes, graph.active[graph.active_count - 1] + 4) != 0)
        throw std::runtime_error("tail next link is not null");
    return graph;
}

} // namespace

int main(int argc, char** argv) {
    if (argc != 2) return 2;
    const std::string_view name{argv[1]};
    const bool append = name == "fn_00018390";
    const bool pop = name == "fn_000183d0";
    const bool unlink = name == "fn_00018400";
    if (!append && !pop && !unlink) return 2;
    std::string arena_hex, node_hex, extra;
    std::uint64_t raw_list = 0, raw_node = 0;
    if (!(std::cin >> arena_hex >> raw_list >> node_hex)) return 2;
    if ((append || unlink) && !(std::cin >> raw_node)) return 2;
    if (std::cin >> extra || raw_list > kListLimit || ((append || unlink) && raw_node > kNodeLimit)) return 2;
    std::array<std::uint8_t, kArenaSize> bytes{};
    if (!decode_hex(arena_hex, bytes)) return 2;
    const auto list = static_cast<std::uint32_t>(raw_list);
    Graph graph;
    try {
        graph = validate_graph(bytes, list, node_hex);
        if (append || unlink) {
            const auto node = static_cast<std::uint32_t>(raw_node);
            if (std::find(graph.nodes.begin(), graph.nodes.end(), node) == graph.nodes.end()
                    || (append && std::find(graph.active.begin(), graph.active.begin() + static_cast<std::ptrdiff_t>(graph.active_count), node)
                       != graph.active.begin() + static_cast<std::ptrdiff_t>(graph.active_count))
                    || (append && graph.active_count > 3))
                throw std::runtime_error("target is outside the allowed pool/domain");
        }
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 2;
    }

    std::array<dao::MemoryRange, 16> readable{};
    std::size_t readable_count = 0;
    std::array<dao::MemoryRange, 5> writable{};
    std::size_t writable_count = 0;
    if (append) {
        const auto node = static_cast<std::uint32_t>(raw_node);
        readable[readable_count++] = {list + 0x1c, 4};
        writable[writable_count++] = {node + 8, 4};
        writable[writable_count++] = {node + 4, 4};
        writable[writable_count++] = {list + 0x1c, 4};
        if (graph.active_count == 0) writable[writable_count++] = {list + 0x18, 4};
        else writable[writable_count++] = {graph.active[graph.active_count - 1] + 4, 4};
    } else if (pop) {
        readable[readable_count++] = {list + 0x18, 4};
        if (graph.active_count != 0) {
            readable[readable_count++] = {graph.active[0] + 4, 4};
            if (graph.active_count == 1) {
                writable[writable_count++] = {list + 0x18, 4};
                writable[writable_count++] = {list + 0x1c, 4};
            } else {
                writable[writable_count++] = {list + 0x18, 4};
                writable[writable_count++] = {graph.active[1] + 8, 4};
            }
        }
    } else {
        readable[readable_count++] = {list + 0x18, 4};
        for (std::size_t i = 0; i < graph.active_count; ++i) {
            const auto current = graph.active[i];
            if (current != static_cast<std::uint32_t>(raw_node))
                readable[readable_count++] = {current + 4, 4};
            else {
                readable[readable_count++] = {current + 8, 4};
                readable[readable_count++] = {current + 4, 4};
                const auto prev = read_u32(bytes, current + 8);
                const auto next = read_u32(bytes, current + 4);
                if (next) readable[readable_count++] = {current + 8, 4};
                if (prev) writable[writable_count++] = {prev - dao::kLinkedArenaBase + 4, 4};
                else writable[writable_count++] = {list + 0x18, 4};
                if (next) writable[writable_count++] = {next - dao::kLinkedArenaBase + 8, 4};
                else writable[writable_count++] = {list + 0x1c, 4};
                break;
            }
        }
    }
    dao::GuestMemory memory{bytes,
        std::span<const dao::MemoryRange>{readable.data(), readable_count},
        std::span<const dao::MemoryRange>{writable.data(), writable_count}};
    std::uint32_t result = 0;
    std::uint32_t ecx_exit = 0;
#ifdef DAO_LINKED_STRUCTURE_MUTANT
    const auto initial_head = graph.head;
#endif
    try {
        if (append) result = dao::fn_00018390(memory, list, static_cast<std::uint32_t>(raw_node));
        else if (pop) result = dao::fn_000183d0(memory, list);
        else {
            const auto observation = dao::fn_00018400(memory, list, static_cast<std::uint32_t>(raw_node));
            result = observation.eax;
            ecx_exit = observation.ecx_exit;
        }
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 3;
    }
#ifdef DAO_LINKED_STRUCTURE_MUTANT
    if (append) {
        result = 0;
    } else if (unlink) {
        ecx_exit = dao::linked_unlink_mutant_ecx(list, ecx_exit);
    } else if (initial_head != 0) {
        const auto old_offset = initial_head - dao::kLinkedArenaBase;
        // Deliberately clear the popped node's forward link after the correct
        // candidate returns. This mutation exists only in the named mutant.
        write_u32(bytes, old_offset + 4, 0);
    }
#endif
    std::cout << result << '\n';
    for (const auto byte : bytes)
        std::cout << kHexDigits[byte >> 4] << kHexDigits[byte & 0x0f];
    std::cout << '\n';
    if (unlink) std::cout << ecx_exit << '\n';
}

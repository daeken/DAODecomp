// Constructed cache correctness/workload control, not game evidence.
#include "static_code_lookup.hpp"
#include <chrono>
#include <cstdio>
#include <string_view>
#include <vector>
using Step = void(*)();
struct Entry { std::uint32_t address; Step step; };
static void first() {}
static void second() {}
int main(int argc, char** argv) {
    using recomp_generated::StaticCodeLookup;
    const std::array<Entry, 6> entries{{{0, first}, {8, second}, {16, nullptr},
        {32, first}, {32, second}, {0xffffffffu, second}}};
    StaticCodeLookup<Entry, 1> collision_cache{entries};
    for(unsigned repeat = 0; repeat < 100; ++repeat) {
        for(auto address : {0u, 8u, 16u, 32u, 0xffffffffu, 1u, 33u, 0xfffffffeu}) {
            auto expected = std::lower_bound(entries.begin(), entries.end(), address,
                [](const auto& e, auto key) { return e.address < key; });
            const Entry* pointer = expected != entries.end() && expected->address == address ? &*expected : nullptr;
            if(collision_cache.find(address) != pointer) return 1;
        }
    }
    const std::array<Entry, 1> other{{{8, first}}};
    StaticCodeLookup<Entry, 1> other_cache{other};
    StaticCodeLookup<Entry, 1> empty_cache{std::span<const Entry>{}};
    if(other_cache.find(8) != &other[0] || empty_cache.find(0) || empty_cache.find(8)) return 2;
    if(argc == 1) { std::puts("constructed cache controls passed"); return 0; }
    if(argc != 2 || std::string_view(argv[1]) != "--benchmark") return 64;
    std::vector<Entry> table;
    table.reserve(2422520);
    for(std::uint32_t i = 0; i < 2422520; ++i) table.push_back({0x400000u + 8u * i, first});
    StaticCodeLookup<Entry> cache{table};
    std::array<std::uint32_t, 128> hot{};
    for(unsigned i = 0; i < hot.size(); ++i) hot[i] = table[17001u * i].address;
    for(bool cached : {false, true}) {
        std::uint64_t checksum = 0;
        const auto start = std::chrono::steady_clock::now();
        for(unsigned i = 0; i < 2000000; ++i) {
            const auto address = hot[(i * 37u) & 127u];
            const Entry* found;
            if(cached) found = cache.find(address);
            else {
                auto it = std::lower_bound(table.begin(), table.end(), address,
                    [](const auto& e, auto key) { return e.address < key; });
                found = it != table.end() && it->address == address ? &*it : nullptr;
            }
            if(!found || found->address != address || found->step != first) return 3;
            checksum += found->address;
        }
        auto ns = std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now() - start).count();
        std::printf("{\"cached\":%s,\"lookups\":2000000,\"nanoseconds\":%lld,\"checksum\":%llu,\"game_acceptance\":false}\n",
            cached ? "true" : "false", static_cast<long long>(ns), static_cast<unsigned long long>(checksum));
    }
}

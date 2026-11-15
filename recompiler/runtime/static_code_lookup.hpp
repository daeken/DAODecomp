#pragma once
#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

namespace recomp_generated {
// The backing table and its function pointers must remain immutable and live
// for this object's lifetime. Never put unloadable candidate/import bindings
// in this cache. Each dispatcher thread owns a separate instance.
template<class Entry, std::size_t Slots = 1024>
class StaticCodeLookup {
    static_assert(Slots && (Slots & (Slots - 1)) == 0);
    struct Slot { std::uint32_t address = 0; const Entry* entry = nullptr; };
    std::span<const Entry> table_;
    std::array<Slot, Slots> slots_{};
public:
    explicit StaticCodeLookup(std::span<const Entry> table) : table_(table) {}
    const Entry* find(std::uint32_t address) {
        auto& slot = slots_[(address ^ (address >> 12)) & (Slots - 1)];
        if(slot.entry && slot.address == address) return slot.entry;
        auto found = std::lower_bound(table_.begin(), table_.end(), address,
            [](const auto& entry, auto key) { return entry.address < key; });
        if(found == table_.end() || found->address != address) return nullptr;
        // A miss, including a dynamic candidate, is never remembered. Recursive
        // guest entry may replace a slot; callers retain only the copied pointer.
        slot = {address, &*found};
        return slot.entry;
    }
};
}

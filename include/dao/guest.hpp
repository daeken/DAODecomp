#pragma once
#include <cstdint>

namespace dao {
// Guest addresses are serialized integers, never host pointers. Confirm the
// actual PE architecture at intake before using this in a game ABI adapter.
struct GuestAddress32 {
    std::uint32_t value;
};
static_assert(sizeof(GuestAddress32) == 4);
}  // namespace dao


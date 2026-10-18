#pragma once
#include <cstdint>
#include <string_view>

// Test-only mutation after the recovered function; never supplies missing semantics.
inline std::uint32_t indexed_field_mutated_return(std::string_view name, bool accepted,
                                                 std::uint32_t result) {
    if (accepted) return result;
    if (name == "fn_00347cf0") return result & 0xffffu;
    if (name == "fn_00347d70" || name == "fn_00347eb0") return result & 0xffu;
    if (name == "fn_00347db0") return 0;
    return result;
}

#include "../validation/indexed_field_mutant.hpp"
#include <cstdint>
#include <initializer_list>

int main() {
    // Synthetic post-call values test only the exact mutation used by the native runner.
    for (const auto name : {"fn_00347cf0", "fn_00347d70", "fn_00347db0", "fn_00347eb0"})
        if (indexed_field_mutated_return(name, true, 0xa5b6c7d8u) != 0xa5b6c7d8u) return 1;
    if (indexed_field_mutated_return("fn_00347cf0", false, 0xa5b6ffffu) != 0xffffu) return 2;
    if (indexed_field_mutated_return("fn_00347d70", false, 0xa5b6c7ffu) != 0xffu) return 3;
    if (indexed_field_mutated_return("fn_00347db0", false, 255u) != 0u) return 4;
    if (indexed_field_mutated_return("fn_00347eb0", false, 0xa5b6c7ffu) != 0xffu) return 5;
    if (indexed_field_mutated_return("unknown", false, 0x12345678u) != 0x12345678u) return 6;
    return 0;
}

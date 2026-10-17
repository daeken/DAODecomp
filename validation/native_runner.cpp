#include "dao/primitives.hpp"
#include "dao/scalar_pilot.hpp"
#include <cstdint>
#include <iostream>
#include <limits>
#include <string_view>

int main(int argc, char** argv) {
    std::uint64_t raw{};
    if (argc != 2 || !(std::cin >> raw) || raw > std::numeric_limits<std::uint32_t>::max()) {
        return 2;
    }
    const auto value = static_cast<std::uint32_t>(raw);
    std::uint32_t result{};
    if (std::string_view{argv[1]} == "byte_swap_u32") {
        result = dao::byte_swap_u32(value);
    } else if (std::string_view{argv[1]} == "bit_mask_or_all") {
#ifdef DAO_LEAF_MUTANT
        // Negative control only: deliberately discard the all-bits sentinel.
        result = std::uint32_t{1} << (value & 31u);
#else
        result = dao::bit_mask_or_all(value);
#endif
    } else if (std::string_view{argv[1]} == "fn_00184920") {
        result = dao::fn_00184920(value);
    } else if (std::string_view{argv[1]} == "fn_0052aad0") {
        result = dao::fn_0052aad0(value);
    } else if (std::string_view{argv[1]} == "fn_005851a0") {
        result = dao::fn_005851a0(value);
    } else if (std::string_view{argv[1]} == "fn_005c0c00") {
        result = dao::fn_005c0c00(value);
    } else if (std::string_view{argv[1]} == "fn_004d79c0") {
        result = dao::fn_004d79c0(value);
    } else if (std::string_view{argv[1]} == "fn_004b6e70") {
        result = dao::fn_004b6e70(value);
    } else if (std::string_view{argv[1]} == "fn_004b65b0") {
        result = dao::fn_004b65b0(value);
    } else if (std::string_view{argv[1]} == "fn_004b64d0") {
        result = dao::fn_004b64d0(value);
    } else {
        return 2;
    }
    std::cout << result << '\n';
}

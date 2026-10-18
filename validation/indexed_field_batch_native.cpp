// Fresh-child C ABI adapter for the unchanged indexed-fields-002 bodies.
// No case is executed by the preloading supervisor. Not a game ABI bridge.
#include "dao/indexed_fields.hpp"
#include "indexed_field_mutant.hpp"
#include <algorithm>
#include <array>
#include <cstdint>
#include <exception>
#include <span>
#include <string_view>

extern "C" int dao_indexed_field_case(const char* raw_name, const std::uint8_t* before,
        std::uint32_t object, std::uint32_t index, std::uint32_t value,
        std::uint32_t entry_eax, std::uint32_t* returned, std::uint8_t* after) {
    if (raw_name == nullptr || before == nullptr || returned == nullptr || after == nullptr || object > 64) return 2;
    const std::string_view name{raw_name};
    std::array<std::uint8_t, 512> bytes{};
    std::copy_n(before, bytes.size(), bytes.begin());
    std::uint32_t field = 0, width = 0, limit = 0;
    bool getter = false;
    if (name == "fn_00347cf0") { field = 0x12a; width = 2; limit = 7; getter = true; }
    else if (name == "fn_00347d30") { field = 0x138; width = 1; limit = 7; getter = true; }
    else if (name == "fn_00347d70") { field = 0x13f; width = 1; limit = 7; getter = true; }
    else if (name == "fn_00347d90") { field = 0x13f; width = 1; limit = 7; getter = false; }
    else if (name == "fn_00347db0") { field = 0x148; width = 4; limit = 7; getter = true; }
    else if (name == "fn_00347dd0") { field = 0x148; width = 4; limit = 7; getter = false; }
    else if (name == "fn_00347df0") { field = 0x164; width = 4; limit = 7; getter = true; }
    else if (name == "fn_00347e10") { field = 0x164; width = 4; limit = 7; getter = false; }
    else if (name == "fn_00347e70") { field = 0x19c; width = 2; limit = 6; getter = true; }
    else if (name == "fn_00347e90") { field = 0x1a8; width = 1; limit = 6; getter = true; }
    else if (name == "fn_00347eb0") { field = 0x1a8; width = 1; limit = 6; getter = false; }
    else return 2;

    const auto low = index & 0xff;
    const bool accepted = low < limit;
    const auto offset = object + field + width * low;
    if (accepted && offset + width > bytes.size()) return 2;
    dao::MemoryRange range{offset, width};
    const auto access = accepted ? std::span<const dao::MemoryRange>{&range, 1} : std::span<const dao::MemoryRange>{};
    dao::GuestMemory memory{bytes, getter ? access : std::span<const dao::MemoryRange>{},
                            getter ? std::span<const dao::MemoryRange>{} : access};
    std::uint32_t result = 0;
    try {
        if (name == "fn_00347cf0") result = dao::fn_00347cf0(memory, object, index, entry_eax);
        else if (name == "fn_00347d30") result = dao::fn_00347d30(memory, object, index, entry_eax);
        else if (name == "fn_00347d70") result = dao::fn_00347d70(memory, object, index, entry_eax);
        else if (name == "fn_00347d90") result = dao::fn_00347d90(memory, object, index, value, entry_eax);
        else if (name == "fn_00347db0") result = dao::fn_00347db0(memory, object, index, entry_eax);
        else if (name == "fn_00347dd0") result = dao::fn_00347dd0(memory, object, index, value, entry_eax);
        else if (name == "fn_00347df0") result = dao::fn_00347df0(memory, object, index, entry_eax);
        else if (name == "fn_00347e10") result = dao::fn_00347e10(memory, object, index, value, entry_eax);
        else if (name == "fn_00347e70") result = dao::fn_00347e70(memory, object, index, entry_eax);
        else if (name == "fn_00347e90") result = dao::fn_00347e90(memory, object, index, entry_eax);
        else if (name == "fn_00347eb0") result = dao::fn_00347eb0(memory, object, index, value, entry_eax);
    } catch (const std::exception& error) {
        (void)error;
        return 3;
    }
#ifdef DAO_INDEXED_FIELD_MUTANT
    result = indexed_field_mutated_return(name, accepted, result);
#endif
    *returned = result;
    std::copy(bytes.begin(), bytes.end(), after);
    return 0;
}

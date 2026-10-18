#include "dao/direct_object_fields.hpp"

namespace dao {

// Supplied instruction provenance: DAOrigins.exe
// SHA-256: 2346caee611002d4dff6ecef68eb315b63a37004dd98b39c11a9c26c0b45bfb3
// Each function name identifies its original RVA.
// Contract: only the supplied ordinary RAM observation interface is modeled.

std::uint32_t fn_00319290(GuestMemory& memory, std::uint32_t object,
                         std::uint32_t, std::uint32_t entry_eax,
                         std::uint32_t& exit_ecx) {
    memory.write_u8(object + 0x86U, std::uint8_t{1});
    exit_ecx = 0x02000000U + object;
    return entry_eax;
}

std::uint32_t fn_00342080(GuestMemory& memory, std::uint32_t object,
                         std::uint32_t value, std::uint32_t entry_eax,
                         std::uint32_t& exit_ecx) {
    memory.write_u16(object, static_cast<std::uint16_t>(value));
    exit_ecx = 0x02000000U + object;
    return (entry_eax & 0xffff0000U) | (value & 0x0000ffffU);
}

std::uint32_t fn_00342090(GuestMemory& memory, std::uint32_t object,
                         std::uint32_t value, std::uint32_t entry_eax,
                         std::uint32_t& exit_ecx) {
    memory.write_u8(object + 0x02U, static_cast<std::uint8_t>(value));
    exit_ecx = 0x02000000U + object;
    return (entry_eax & 0xffffff00U) | (value & 0x000000ffU);
}

std::uint32_t fn_00347b40(GuestMemory& memory, std::uint32_t object,
                         std::uint32_t value, std::uint32_t entry_eax,
                         std::uint32_t& exit_ecx) {
    memory.write_u16(object + 0x5aU, static_cast<std::uint16_t>(value));
    exit_ecx = 0x02000000U + object;
    return (entry_eax & 0xffff0000U) | (value & 0x0000ffffU);
}

std::uint32_t fn_00347b50(GuestMemory& memory, std::uint32_t object,
                         std::uint32_t value, std::uint32_t entry_eax,
                         std::uint32_t& exit_ecx) {
    const std::uint32_t al = value & 0xffU;
    const std::uint32_t dl = (al - 1U) & 0xffU;
    memory.write_u8(object + 0x50U,
                    static_cast<std::uint8_t>(dl <= 2U ? al : 1U));
    exit_ecx = 0x02000000U + object;
    return (entry_eax & 0xffffff00U) | al;
}

std::uint32_t fn_00347b70(GuestMemory& memory, std::uint32_t object,
                         std::uint32_t value, std::uint32_t,
                         std::uint32_t& exit_ecx) {
    memory.write_u32(object + 0x20U, value);
    exit_ecx = 0x02000000U + object;
    return value;
}

std::uint32_t fn_00347b80(GuestMemory& memory, std::uint32_t object,
                         std::uint32_t value, std::uint32_t entry_eax,
                         std::uint32_t& exit_ecx) {
    memory.write_u8(object + 0x18U, static_cast<std::uint8_t>(value));
    exit_ecx = 0x02000000U + object;
    return (entry_eax & 0xffffff00U) | (value & 0x000000ffU);
}

std::uint32_t fn_00347b90(GuestMemory& memory, std::uint32_t object,
                         std::uint32_t value, std::uint32_t,
                         std::uint32_t& exit_ecx) {
    memory.write_u32(object + 0x30U, value);
    exit_ecx = 0x02000000U + object;
    return value;
}

std::uint32_t fn_003480b0(GuestMemory& memory, std::uint32_t object,
                         std::uint32_t, std::uint32_t,
                         std::uint32_t& exit_ecx) {
    const std::uint32_t field = memory.read_u16(object + 0x12aU);
    exit_ecx = 0x02000000U + object;
    return field == 0x26U ? 1U : 0U;
}

std::uint32_t fn_003480c0(GuestMemory& memory, std::uint32_t object,
                         std::uint32_t, std::uint32_t,
                         std::uint32_t& exit_ecx) {
    const std::uint32_t field = memory.read_u16(object + 0x12aU);
    exit_ecx = 0x02000000U + object;
    return field == 0x16U ? 1U : 0U;
}

std::uint32_t fn_003b51e0(GuestMemory& memory, std::uint32_t object,
                         std::uint32_t, std::uint32_t,
                         std::uint32_t& exit_ecx) {
    const std::uint32_t field = memory.read_u32(object + 0x08U);
    exit_ecx = 0x02000000U + object;
    return field;
}

std::uint32_t fn_003cd030(GuestMemory& memory, std::uint32_t object,
                         std::uint32_t value, std::uint32_t entry_eax,
                         std::uint32_t& exit_ecx) {
    memory.write_u8(object + 0x11dU, static_cast<std::uint8_t>(value));
    exit_ecx = 0x02000000U + object;
    return (entry_eax & 0xffffff00U) | (value & 0x000000ffU);
}

std::uint32_t fn_003cd040(GuestMemory& memory, std::uint32_t object,
                         std::uint32_t value, std::uint32_t,
                         std::uint32_t& exit_ecx) {
    memory.write_u32(object + 0x120U, value);
    exit_ecx = 0x02000000U + object;
    return value;
}

std::uint32_t fn_003cd0d0(GuestMemory& memory, std::uint32_t object,
                         std::uint32_t, std::uint32_t,
                         std::uint32_t& exit_ecx) {
    const std::uint32_t flags = memory.read_u8(object + 0x99U);
    memory.write_u8(object + 0x99U,
                    static_cast<std::uint8_t>(flags | 2U));
    const std::uint32_t field = memory.read_u32(object + 0x94U);
    memory.write_u8(object + 0x119U, std::uint8_t{0});
    exit_ecx = 0x02000000U + object;
    return field == 2U ? 1U : 0U;
}

std::uint32_t fn_003cd140(GuestMemory& memory, std::uint32_t object,
                         std::uint32_t value, std::uint32_t,
                         std::uint32_t& exit_ecx) {
    memory.write_u32(object + 0x1c0U, value);
    memory.write_u8(object + 0x1b9U, std::uint8_t{1});
    exit_ecx = 0x02000000U + object;
    return value;
}

std::uint32_t fn_003cd350(GuestMemory& memory, std::uint32_t object,
                         std::uint32_t, std::uint32_t entry_eax,
                         std::uint32_t& exit_ecx) {
    memory.write_u8(object + 0x84U, std::uint8_t{0});
    exit_ecx = 0x02000000U + object;
    return entry_eax;
}

std::uint32_t fn_003edbc0(GuestMemory& memory, std::uint32_t object,
                         std::uint32_t, std::uint32_t entry_eax,
                         std::uint32_t& exit_ecx) {
    memory.write_u32(object + 0x44U, std::uint32_t{0});
    exit_ecx = 0x02000000U + object;
    return entry_eax;
}

std::uint32_t fn_00515af0(GuestMemory& memory, std::uint32_t object,
                         std::uint32_t, std::uint32_t,
                         std::uint32_t& exit_ecx) {
    const std::uint32_t field = memory.read_u32(object + 0x0cU);
    exit_ecx = 0x02000000U + object;
    return field & 1U;
}

std::uint32_t fn_00515b00(GuestMemory& memory, std::uint32_t object,
                         std::uint32_t, std::uint32_t,
                         std::uint32_t& exit_ecx) {
    const std::uint32_t field = memory.read_u32(object + 0x0cU);
    exit_ecx = 0x02000000U + object;
    return (field >> 4U) & 1U;
}

std::uint32_t fn_00515b10(GuestMemory& memory, std::uint32_t object,
                         std::uint32_t, std::uint32_t,
                         std::uint32_t& exit_ecx) {
    const std::uint32_t field = memory.read_u32(object + 0x0cU);
    exit_ecx = 0x02000000U + object;
    return (field >> 1U) & 1U;
}

std::uint32_t fn_0054f6e0(GuestMemory& memory, std::uint32_t object,
                         std::uint32_t, std::uint32_t,
                         std::uint32_t& exit_ecx) {
    const std::uint32_t field = memory.read_u32(object + 0x30U);
    exit_ecx = field;
    return field == 1U ? 1U : 0U;
}

std::uint32_t fn_0054fa40(GuestMemory& memory, std::uint32_t object,
                         std::uint32_t, std::uint32_t,
                         std::uint32_t& exit_ecx) {
    const std::uint32_t field = memory.read_u32(object + 0x28U);
    exit_ecx = field;
    return field == 1U ? 1U : 0U;
}

} // namespace dao

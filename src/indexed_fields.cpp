#include "dao/indexed_fields.hpp"

namespace dao {

// Provenance: supplied original instruction slices from DAOrigins.exe.
// Binary SHA-256:
// 2346caee611002d4dff6ecef68eb315b63a37004dd98b39c11a9c26c0b45bfb3
// Scope: supplied isolated RAM contracts; no native x86 ABI bridge asserted.
// Validation: source inspection only; no compilation or execution performed.

// RVA 00347cf0; slice SHA-256:
// fe5ec2d090f480c799f7975af981c904e4a06fe8ab12806e5bf57bccbcaeff58
std::uint32_t fn_00347cf0(GuestMemory memory, std::uint32_t object,
                          std::uint32_t index, std::uint32_t entry_eax) {
    const std::uint32_t k = index & 0xffu;
    if (k >= 7u)
        return (entry_eax & 0xffff0000u) | 0xffffu;
    return memory.read_u16(object + 0x12au + 2u * k);
}

// RVA 00347d30; slice SHA-256:
// 68e657fa6835e2096d5105c54e65b7fd9240014f3326aaaa6bd9950f4fcf3cae
std::uint32_t fn_00347d30(GuestMemory memory, std::uint32_t object,
                          std::uint32_t index, std::uint32_t entry_eax) {
    const std::uint32_t k = index & 0xffu;
    if (k >= 7u)
        return (entry_eax & 0xffffff00u) | 0xffu;
    return memory.read_u8(object + 0x138u + k);
}

// RVA 00347d70; slice SHA-256:
// 8d7af58d4df9b6db552a21aba6db12d89212d05d9f25e73bf7f94a09f7f9b06c
std::uint32_t fn_00347d70(GuestMemory memory, std::uint32_t object,
                          std::uint32_t index, std::uint32_t entry_eax) {
    const std::uint32_t k = index & 0xffu;
    if (k >= 7u)
        return (entry_eax & 0xffffff00u) | 0xffu;
    return memory.read_u8(object + 0x13fu + k);
}

// RVA 00347d90; slice SHA-256:
// d088edecee9d5e3c4e3d2231b7b2e81a700d6a03dc888d8f2363545e2427d46e
std::uint32_t fn_00347d90(GuestMemory memory, std::uint32_t object,
                          std::uint32_t index, std::uint32_t value,
                          std::uint32_t entry_eax) {
    const std::uint32_t k = index & 0xffu;
    if (k >= 7u)
        return (entry_eax & 0xffffff00u) | k;
    memory.write_u8(object + 0x13fu + k, static_cast<std::uint8_t>(value));
    return k;
}

// RVA 00347db0; slice SHA-256:
// d7da1ba66dc89b021c957d6af4981e820f71af15e0477b757cb0764b7734a1e1
std::uint32_t fn_00347db0(GuestMemory memory, std::uint32_t object,
                          std::uint32_t index, std::uint32_t /*entry_eax*/) {
    const std::uint32_t k = index & 0xffu;
    if (k >= 7u)
        return 0xffu;
    return memory.read_u32(object + 0x148u + 4u * k);
}

// RVA 00347dd0; slice SHA-256:
// d990b020ac73148d3c9e312d190047435c3d4cf7e7f0c3028c2dc67c00ab2d2f
std::uint32_t fn_00347dd0(GuestMemory memory, std::uint32_t object,
                          std::uint32_t index, std::uint32_t value,
                          std::uint32_t entry_eax) {
    const std::uint32_t k = index & 0xffu;
    if (k >= 7u)
        return (entry_eax & 0xffffff00u) | k;
    memory.write_u32(object + 0x148u + 4u * k, value);
    return k;
}

// RVA 00347df0; slice SHA-256:
// d65079a7af0abcd6b2f0681f045f4f2d64d8624d8710c129bb6b50afe754a5e2
std::uint32_t fn_00347df0(GuestMemory memory, std::uint32_t object,
                          std::uint32_t index, std::uint32_t /*entry_eax*/) {
    const std::uint32_t k = index & 0xffu;
    if (k >= 7u)
        return 0u;
    return memory.read_u32(object + 0x164u + 4u * k);
}

// RVA 00347e10; slice SHA-256:
// b8f7bcbbbc9c5c26a0f0e08a06cdbc4a0c03515e5e215fef0bab84f1b529031d
std::uint32_t fn_00347e10(GuestMemory memory, std::uint32_t object,
                          std::uint32_t index, std::uint32_t value,
                          std::uint32_t entry_eax) {
    const std::uint32_t k = index & 0xffu;
    if (k >= 7u)
        return (entry_eax & 0xffffff00u) | k;
    memory.write_u32(object + 0x164u + 4u * k, value);
    return k;
}

// RVA 00347e70; slice SHA-256:
// 07c6a1c8150d5d11e2ba977aec4d9d0770027c6056ceb9b140c5ebe4d640287e
std::uint32_t fn_00347e70(GuestMemory memory, std::uint32_t object,
                          std::uint32_t index, std::uint32_t entry_eax) {
    const std::uint32_t k = index & 0xffu;
    if (k >= 6u)
        return (entry_eax & 0xffff0000u) | 0xffffu;
    return memory.read_u16(object + 0x19cu + 2u * k);
}

// RVA 00347e90; slice SHA-256:
// 16ce21f6bda3cdf011abb2c0e1aa52650dfe09295f844f6a3fc7d961e75ba902
std::uint32_t fn_00347e90(GuestMemory memory, std::uint32_t object,
                          std::uint32_t index, std::uint32_t entry_eax) {
    const std::uint32_t k = index & 0xffu;
    if (k >= 6u)
        return (entry_eax & 0xffffff00u) | 0xffu;
    return memory.read_u8(object + 0x1a8u + k);
}

// RVA 00347eb0; slice SHA-256:
// 97aef0e563139d6bd1812ab3e708eab0bd2afa6c89864994ca09ae289b0b1789
std::uint32_t fn_00347eb0(GuestMemory memory, std::uint32_t object,
                          std::uint32_t index, std::uint32_t value,
                          std::uint32_t entry_eax) {
    const std::uint32_t k = index & 0xffu;
    if (k >= 6u)
        return (entry_eax & 0xffffff00u) | k;
    memory.write_u8(object + 0x1a8u + k, static_cast<std::uint8_t>(value));
    return k;
}

} // namespace dao

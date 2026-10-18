#include "dao/object_bitfields.hpp"

namespace dao {
namespace {
constexpr std::uint32_t arena_base = 0x02000000u;

// Compute the x86 effective address with guest32 wraparound, then check
// before subtracting the arena base. GuestMemory checks the declared spans.
std::uint32_t offset_at(std::uint32_t raw, std::uint32_t displacement,
                        std::uint32_t width) {
    const std::uint32_t address = raw + displacement;
    const std::uint64_t widened = address;
    if (widened < std::uint64_t{arena_base} ||
        widened + width > 0x100000000ull)
        throw std::out_of_range("guest address outside arena address space");
    return static_cast<std::uint32_t>(widened - std::uint64_t{arena_base});
}
} // namespace

// Provenance for all fifteen functions:
// DAOrigins.exe SHA-256:
// 2346caee611002d4dff6ecef68eb315b63a37004dd98b39c11a9c26c0b45bfb3
// Function suffixes identify the supplied pinned RVAs. Slice SHA-256 values
// appear below. Implementation follows the supplied instruction slices;
// no independent execution or validation report has been produced here.
// Contract: object/source are arena offsets; pointer fields and exit_ecx are
// raw guest32 bits. Only GuestMemory performs memory accesses. Invalid memory
// accesses throw rather than supplying missing semantics as zero.

// Flag contracts: exact-width read/modify/write, unchanged EAX and ECX.
// Predicate is low byte(value) != 0 unless explicitly specified otherwise.
#define DAO_FLAG16(NAME, DISP, MASK) \
std::uint32_t NAME(GuestMemory& memory, std::uint32_t object, \
                   std::uint32_t value, std::uint32_t, \
                   std::uint32_t entry_eax, std::uint32_t& exit_ecx) { \
    const std::uint32_t raw = arena_base + object; \
    const auto offset = offset_at(raw, DISP, 2u); \
    const std::uint32_t old = memory.read_u16(offset); \
    const std::uint32_t updated = (value & 0xffu) != 0u \
        ? (old | MASK) : (old & ~std::uint32_t{MASK}); \
    memory.write_u16(offset, static_cast<std::uint16_t>(updated)); \
    exit_ecx = raw; \
    return entry_eax; \
}

#define DAO_FLAG8(NAME, MASK, PREDICATE) \
std::uint32_t NAME(GuestMemory& memory, std::uint32_t object, \
                   std::uint32_t value, std::uint32_t, \
                   std::uint32_t entry_eax, std::uint32_t& exit_ecx) { \
    const std::uint32_t raw = arena_base + object; \
    const auto offset = offset_at(raw, 0x133u, 1u); \
    const std::uint32_t old = memory.read_u8(offset); \
    const std::uint32_t updated = (PREDICATE) \
        ? (old | MASK) : (old & ~std::uint32_t{MASK}); \
    memory.write_u8(offset, static_cast<std::uint8_t>(updated)); \
    exit_ecx = raw; \
    return entry_eax; \
}

// RVA 0x0052a680; slice SHA-256:
// a134ad0d00e8dd6ffb3afe30e77a3d36a6482e29752060273266b6eaed41f7eb
DAO_FLAG16(fn_0052a680, 0x8cu, 0x0800u)

// RVA 0x0052a820; slice SHA-256:
// 96511a802899cb0a033bd7580d9d83545d946fe3fca22ed68bac360ca66d8deb
DAO_FLAG8(fn_0052a820, 0x20u, (value & 0xffu) != 0u)

// RVA 0x0052a840; slice SHA-256:
// 10234a4c1801d861c1165fd87735916f4792f0f6d9f1dbb324415107bc077d6e
DAO_FLAG8(fn_0052a840, 0x40u, (value & 0xffu) != 0u)

// RVA 0x0052a860; slice SHA-256:
// 289803a7e103ac622becf7bd63b8e17220ad6d39d67c9d3933525fe6c36746d1
// Predicate compares the complete unsigned value against one.
DAO_FLAG8(fn_0052a860, 0x80u, value > 1u)

// RVA 0x0052a950; slice SHA-256:
// bc7ebfcedf1e080741f2bae8c8e799a58115e4e87a7605f560038f2a76dd72cc
// Contract: first set byte +0x14e bit 0, then update +0x14c bits 2..3.
// Return AL is the XOR delta, with the entry EAX upper 24 bits retained.
std::uint32_t fn_0052a950(GuestMemory& memory, std::uint32_t object,
                          std::uint32_t value, std::uint32_t,
                          std::uint32_t entry_eax, std::uint32_t& exit_ecx) {
    const std::uint32_t raw = arena_base + object;
    std::uint32_t al = value & 0xffu;
    const auto dirty = offset_at(raw, 0x14eu, 1u);
    memory.write_u8(dirty, static_cast<std::uint8_t>(
        std::uint32_t{memory.read_u8(dirty)} | 1u));
    al = (al + al) & 0xffu;
    al = (al + al) & 0xffu;
    const auto field = offset_at(raw, 0x14cu, 1u);
    al ^= memory.read_u8(field);
    al &= 0x0cu;
    const std::uint32_t old = memory.read_u8(field);
    memory.write_u8(field, static_cast<std::uint8_t>(old ^ al));
    exit_ecx = raw;
    return (entry_eax & 0xffffff00u) | al;
}

// RVA 0x0052a9d0; slice SHA-256:
// 95252ffee21a98610a87579f9ae0af6bc714b5973d658444237037f06e2f4788
DAO_FLAG16(fn_0052a9d0, 0xc4u, 0x0010u)

// RVA 0x0052a9f0; slice SHA-256:
// b1c9fe13f412cdaa758aa83a180d0366bce88e6577d5b184eb577b0af5dd441f
DAO_FLAG16(fn_0052a9f0, 0xc4u, 0x0020u)

// RVA 0x0052aa10; slice SHA-256:
// af336b7876d4626203c42c04a09ae324b7faa8f96451e654e4b6ce6bc9ee4b58
DAO_FLAG16(fn_0052aa10, 0xc4u, 0x0008u)

// RVA 0x0052aa30; slice SHA-256:
// 0d5e390e32bbc55e8e7c36344b865c26181c97b6721e790293c590a04358c6b9
DAO_FLAG16(fn_0052aa30, 0xc4u, 0x0100u)

// RVA 0x0052aa50; slice SHA-256:
// 5a3a642023570e4af888ddfe96576b6a319259b27e31f625499015ce6fb9ad2d
DAO_FLAG16(fn_0052aa50, 0xc4u, 0x0200u)

// RVA 0x0052aa70; slice SHA-256:
// 8008322066c5e06aab82092c347ba63d457c92c6550ba3dac1078dc6d0399152
DAO_FLAG16(fn_0052aa70, 0xc4u, 0x0400u)

// RVA 0x0052aa90; slice SHA-256:
// 72e54a4027df1aa690e42af920e8c0dc3372b494b5acb6bd9334c210d953744f
DAO_FLAG16(fn_0052aa90, 0xc4u, 0x0800u)

#undef DAO_FLAG8
#undef DAO_FLAG16

// RVA 0x0052ab30; slice SHA-256:
// c98b1d8660dcaa3dd6fb409c9420577d36d1d5e623f6e4f4c40e539da4bab070
// Contract: merge byte +0x137 into EAX bits 24..31 and value bits 0..23;
// store that exact dword at +0x140 and return it. Preserve raw ECX.
std::uint32_t fn_0052ab30(GuestMemory& memory, std::uint32_t object,
                          std::uint32_t value, std::uint32_t,
                          std::uint32_t, std::uint32_t& exit_ecx) {
    const std::uint32_t raw = arena_base + object;
    const std::uint32_t high = memory.read_u8(offset_at(raw, 0x137u, 1u));
    const std::uint32_t eax = (high << 24u) | (value & 0x00ffffffu);
    memory.write_u32(offset_at(raw, 0x140u, 4u), eax);
    exit_ecx = raw;
    return eax;
}

// RVA 0x0052ab70; slice SHA-256:
// 519f2703b79dbe90b39143fd25563eac6b9b300d71d82bfa2d6c165b82c2c4de
// Contract: eight sequential byte copies, then four sequential word copies,
// then one dword copy. Each read precedes its corresponding write; later
// reads see earlier writes under overlap. Exit ECX is the final dword read.
// Return is the destination offset per the observation mapping.
std::uint32_t fn_0052ab70(GuestMemory& memory, std::uint32_t object,
                          std::uint32_t, std::uint32_t source,
                          std::uint32_t, std::uint32_t& exit_ecx) {
    const std::uint32_t destination_raw = arena_base + object;
    const std::uint32_t source_raw = arena_base + source;
    exit_ecx = source_raw;
    for (std::uint32_t displacement = 0x10u; displacement < 0x18u;
         ++displacement) {
        const auto data = memory.read_u8(offset_at(source_raw, displacement, 1u));
        memory.write_u8(offset_at(destination_raw, displacement, 1u), data);
    }
    for (std::uint32_t displacement = 0x18u; displacement < 0x20u;
         displacement += 2u) {
        const auto data = memory.read_u16(offset_at(source_raw, displacement, 2u));
        memory.write_u16(offset_at(destination_raw, displacement, 2u), data);
    }
    const std::uint32_t data = memory.read_u32(offset_at(source_raw, 0x20u, 4u));
    exit_ecx = data;
    memory.write_u32(offset_at(destination_raw, 0x20u, 4u), data);
    return object;
}

// RVA 0x0052abe0; slice SHA-256:
// 7e2b18c600938fb0440d6711757627c83d96e1358be8e9b0eb779b9c19de2df4
// Contract: follow raw pointer at +0x9c, then raw pointer at +0x11c.
// Nonzero: retain its upper 24 EAX bits, replace AL with byte +0x64 bit 1,
// and preserve entry ECX. Zero: load ECX from object +0x98 and return its
// byte +0x50 bit 5 with zero upper EAX bits. No initial-pointer null guard
// exists in the supplied instructions.
std::uint32_t fn_0052abe0(GuestMemory& memory, std::uint32_t object,
                          std::uint32_t, std::uint32_t,
                          std::uint32_t, std::uint32_t& exit_ecx) {
    const std::uint32_t raw = arena_base + object;
    exit_ecx = raw;
    std::uint32_t eax = memory.read_u32(offset_at(raw, 0x9cu, 4u));
    eax = memory.read_u32(offset_at(eax, 0x11cu, 4u));
    if (eax != 0u) {
        const std::uint32_t byte = memory.read_u8(offset_at(eax, 0x64u, 1u));
        return (eax & 0xffffff00u) | ((byte >> 1u) & 1u);
    }
    exit_ecx = memory.read_u32(offset_at(raw, 0x98u, 4u));
    const std::uint32_t byte = memory.read_u8(offset_at(exit_ecx, 0x50u, 1u));
    return (byte >> 5u) & 1u;
}

} // namespace dao

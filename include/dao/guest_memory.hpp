#pragma once
#include <cstdint>
#include <span>
#include <stdexcept>

namespace dao {
struct MemoryRange {
    std::uint32_t offset;
    std::uint32_t size;
};

// Offsets refer to one guest allocation, never to host pointer values. Byte-wise
// little-endian access permits unaligned and overlapping guest objects without
// C++ alignment, effective-type or pointer-aliasing assumptions.
class GuestMemory {
public:
    GuestMemory(std::span<std::uint8_t> bytes, std::span<const MemoryRange> readable,
                std::span<const MemoryRange> writable)
        : bytes_(bytes), readable_(readable), writable_(writable) {}

    std::uint32_t read_u32(std::uint32_t offset) const {
        check(offset, readable_);
        std::uint32_t value = 0;
        for (std::uint32_t i = 0; i < 4; ++i)
            value |= std::uint32_t{bytes_[offset + i]} << (i * 8);
        return value;
    }

    std::uint8_t read_u8(std::uint32_t offset) const {
        check(offset, readable_, 1);
        return bytes_[offset];
    }

    std::uint16_t read_u16(std::uint32_t offset) const {
        check(offset, readable_, 2);
        return static_cast<std::uint16_t>(std::uint16_t{bytes_[offset]} |
                                         (std::uint16_t{bytes_[offset + 1]} << 8));
    }

    void write_u32(std::uint32_t offset, std::uint32_t value) {
        check(offset, writable_);
        for (std::uint32_t i = 0; i < 4; ++i)
            bytes_[offset + i] = static_cast<std::uint8_t>(value >> (i * 8));
    }

    void write_u8(std::uint32_t offset, std::uint8_t value) {
        check(offset, writable_, 1);
        bytes_[offset] = value;
    }

    void write_u16(std::uint32_t offset, std::uint16_t value) {
        check(offset, writable_, 2);
        bytes_[offset] = static_cast<std::uint8_t>(value);
        bytes_[offset + 1] = static_cast<std::uint8_t>(value >> 8);
    }

private:
    void check(std::uint32_t offset, std::span<const MemoryRange> ranges,
               std::uint32_t width = 4) const {
        const auto end = std::uint64_t{offset} + width;
        if (end <= bytes_.size()) {
            for (const auto range : ranges)
                if (offset >= range.offset && end <= std::uint64_t{range.offset} + range.size)
                    return;
        }
        throw std::out_of_range("guest memory access outside declared footprint");
    }
    std::span<std::uint8_t> bytes_;
    std::span<const MemoryRange> readable_;
    std::span<const MemoryRange> writable_;
};
} // namespace dao

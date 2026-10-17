"""Read-only PE header inventory. Does not load or execute the image."""
import struct
from pathlib import Path
from .harness import file_hash


def fingerprint(path):
    path = Path(path)
    size = path.stat().st_size
    with path.open("rb") as stream:
        def read(offset, length):
            if offset < 0 or offset + length > size:
                raise ValueError("truncated PE file")
            stream.seek(offset)
            data = stream.read(length)
            if len(data) != length:
                raise ValueError("file changed during intake")
            return data

        if read(0, 2) != b"MZ":
            raise ValueError("not a DOS/PE image")
        pe_offset = struct.unpack("<I", read(0x3C, 4))[0]
        if read(pe_offset, 4) != b"PE\0\0":
            raise ValueError("missing PE signature")
        machine, count, timestamp, _, _, optional_size, flags = struct.unpack("<HHIIIHH", read(pe_offset + 4, 20))
        optional = pe_offset + 24
        magic = struct.unpack("<H", read(optional, 2))[0]
        minimum = {0x10B: 96, 0x20B: 112}.get(magic)
        if minimum is None or optional_size < minimum:
            raise ValueError("invalid or unsupported optional header")
        read(optional, optional_size)
        image_base = struct.unpack("<I" if magic == 0x10B else "<Q", read(optional + (28 if magic == 0x10B else 24), 4 if magic == 0x10B else 8))[0]
        entry = struct.unpack("<I", read(optional + 16, 4))[0]
        sections = []
        for index in range(count):
            raw = read(optional + optional_size + index * 40, 40)
            name, virtual_size, rva, raw_size, offset = struct.unpack("<8sIIII", raw[:24])
            if raw_size and offset + raw_size > size:
                raise ValueError("section data extends beyond file")
            sections.append({"name": name.rstrip(b"\0").decode("ascii", errors="replace"),
                             "rva": rva, "virtual_size": virtual_size,
                             "file_offset": offset, "file_size": raw_size})
    return {"schema_version": 1, "filename": path.name, "size": size, "sha256": file_hash(path),
            "format": "PE32" if magic == 0x10B else "PE32+", "machine": machine,
            "architecture": {0x14C: "x86", 0x8664: "x86_64", 0xAA64: "arm64"}.get(machine, "unknown"),
            "image_base": image_base, "entry_rva": entry, "coff_timestamp": timestamp,
            "characteristics": flags, "sections": sections}


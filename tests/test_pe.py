from pathlib import Path
import struct
import tempfile
import unittest
from tools.daodecomp.pe import fingerprint


def image(plus=False):
    data = bytearray(512)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 0x3C, 0x80)
    data[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<HHIIIHH", data, 0x84, 0x8664 if plus else 0x14C, 1, 0, 0, 0, 112 if plus else 96, 2)
    optional = 0x98
    struct.pack_into("<H", data, optional, 0x20B if plus else 0x10B)
    struct.pack_into("<I", data, optional + 16, 0x1000)
    struct.pack_into("<Q" if plus else "<I", data, optional + (24 if plus else 28), 0x140000000 if plus else 0x400000)
    struct.pack_into("<8sIIII", data, optional + (112 if plus else 96), b".text", 16, 0x1000, 16, 480)
    return data


class PETests(unittest.TestCase):
    def inspect(self, data):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "fixture.exe"
            path.write_bytes(data)
            result = fingerprint(path)
            self.assertEqual(path.read_bytes(), data)
            return result

    def test_x86(self):
        result = self.inspect(image())
        self.assertEqual(result["architecture"], "x86")
        self.assertEqual(result["image_base"], 0x400000)
        self.assertEqual(result["sections"][0]["rva"], 0x1000)
        self.assertEqual(len(result["sha256"]), 64)

    def test_pe32_plus(self):
        result = self.inspect(image(True))
        self.assertEqual(result["architecture"], "x86_64")
        self.assertEqual(result["image_base"], 0x140000000)

    def test_rejects_invalid_and_truncated_files(self):
        for data in (b"not an exe", image()[:200], image()[:490]):
            with self.subTest(size=len(data)), self.assertRaises(ValueError):
                self.inspect(data)


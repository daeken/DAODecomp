import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

from test_pe import image
from tools.daodecomp.leaf import execute_leaf, load_slice


class SliceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "fixture.exe"
        self.data = image()
        self.data[480:485] = bytes.fromhex("8b442404c3")  # Hand-authored identity function.
        self.path.write_bytes(self.data)
        self.digest = hashlib.sha256(self.data).hexdigest()
        self.code_digest = hashlib.sha256(self.data[480:485]).hexdigest()

    def test_valid_slice(self):
        address, code = load_slice(self.path, self.digest, 0x1000, 5, self.code_digest)
        self.assertEqual(address, 0x401000)
        self.assertEqual(code, self.data[480:485])

    def test_wrong_reference_rejected(self):
        with self.assertRaisesRegex(ValueError, "module hash"):
            load_slice(self.path, "0" * 64, 0x1000, 5, self.code_digest)

    def test_wrong_code_rejected(self):
        with self.assertRaisesRegex(ValueError, "slice hash"):
            load_slice(self.path, self.digest, 0x1000, 5, "0" * 64)

    def test_unbacked_ranges_rejected(self):
        for rva, size in [(0, 5), (0x100f, 5), (0x1010, 5), (0x1000, 0), (-1, 5)]:
            with self.subTest(rva=rva, size=size), self.assertRaises(ValueError):
                load_slice(self.path, self.digest, rva, size, self.code_digest)

    def test_x64_rejected(self):
        self.path.write_bytes(image(True))
        digest = hashlib.sha256(self.path.read_bytes()).hexdigest()
        with self.assertRaisesRegex(ValueError, "PE32 x86"):
            load_slice(self.path, digest, 0x1000, 5, self.code_digest)


@unittest.skipUnless(importlib.util.find_spec("unicorn"), "optional Unicorn backend is not installed")
class LeafGuardTests(unittest.TestCase):
    def run_code(self, hex_code):
        return execute_leaf(0x401000, bytes.fromhex(hex_code), 0x12345678)

    def test_identity_returns(self):
        self.assertEqual(self.run_code("8b442404 c3"), 0x12345678)

    def test_write_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "memory write"):
            self.run_code("89442404 c3")

    def test_extra_stack_read_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "read outside"):
            self.run_code("8b442408 c3")

    def test_register_corruption_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "nonvolatile"):
            self.run_code("bb01000000 c3")

    def test_wrong_stack_cleanup_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "stack balance"):
            self.run_code("c20400")

    def test_out_of_slice_execution_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "escaped"):
            self.run_code("eb01")

    def test_budget_exhaustion_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "within budget"):
            self.run_code("ebfe")

    def test_direction_flag_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "direction flag"):
            self.run_code("fd c3")

    def test_register_argument_and_partial_return(self):
        # Hand-authored mov al, cl; ret, with unknown high return bits.
        result = execute_leaf(0x401000, bytes.fromhex("88c8 c3"), 0xdeadbeef,
                              argument="ecx", return_bits=8)
        self.assertEqual(result, 0xef)

    def test_declared_stack_cleanup(self):
        self.assertEqual(execute_leaf(0x401000, bytes.fromhex("8b442404 c20400"),
                                      77, stack_cleanup=4), 77)

    def test_register_abi_cannot_read_stack_argument(self):
        with self.assertRaisesRegex(RuntimeError, "read outside"):
            execute_leaf(0x401000, bytes.fromhex("8b442404 c3"), 77, argument="eax")

    def test_custom_preserved_register_checked(self):
        with self.assertRaisesRegex(RuntimeError, "nonvolatile"):
            execute_leaf(0x401000, bytes.fromhex("31c9 c3"), 77,
                         argument="ecx", preserved_registers=["ecx"])

    def test_unknown_abi_rejected(self):
        for abi in [{"argument": "edx"}, {"return_bits": 16}, {"stack_cleanup": 8},
                    {"argument": "ecx", "stack_cleanup": 4}]:
            with self.subTest(abi=abi), self.assertRaisesRegex(ValueError, "scalar ABI"):
                execute_leaf(0x401000, b"\xc3", 77, **abi)

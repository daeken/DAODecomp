"""Open x86 snippets test applicability classification, never acceptance."""
import importlib.util
from pathlib import Path
import struct
import unittest

try:
    import capstone
except ImportError:
    capstone = None

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('tailcall_scan', ROOT / 'tools/replayable/scan_tailcalls.py')
scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan)


@unittest.skipUnless(capstone is not None, 'capstone unavailable')
class TailApplicabilityTests(unittest.TestCase):
    def classify(self, data):
        md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        md.detail = True
        return scan.classify(data, 0x10000, md)[0]

    def test_direct_external_terminal_jump_needs_actual_typed_check(self):
        self.assertEqual(self.classify(b'\x90\xe9' + struct.pack('<i', 0x20000 - 0x10006)), 'typed_check_required')

    def test_internal_jump_is_outside_linear_tail_domain(self):
        self.assertEqual(self.classify(b'\xeb\xfe'), 'internal_terminal_jump')

    def test_conditional_prefix_is_not_treated_as_linear(self):
        self.assertEqual(self.classify(b'\x75\x00\xe9' + struct.pack('<i', 0x20000 - 0x10007)), 'nonlinear_terminal_jump')

    def test_indirect_return_and_incomplete_ranges_are_not_candidates(self):
        self.assertEqual(self.classify(b'\xff\xe0'), 'no_terminal_direct_jump')
        self.assertEqual(self.classify(b'\xc3'), 'no_terminal_direct_jump')
        self.assertEqual(self.classify(b'\xe9'), 'incomplete_disassembly')

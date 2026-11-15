"""Separate real relocation words from code operands and resource pixels."""
import struct
import tempfile
from pathlib import Path
import unittest
import capstone
from tools.recomp_native import PE32
from tools.recomp_literal_pointer_discovery import ExecutableLiteralScanner
from tools.recomp_pointer_discovery import highlow_sites
import test_recomp_pointer_discovery as pointer_cases


class ExecutableLiteralTests(unittest.TestCase):
    def scanner(self, image):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / 'literals.exe'
        path.write_bytes(image)
        pe = PE32(path)
        scanner = ExecutableLiteralScanner(pe)
        decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        rows = [dict(rva=i.address - 0x400000, bytes=i.bytes.hex())
                for rva, size in ((0x1000, 16), (0x1040, 17))
                for i in decoder.disasm(pe.read(rva, size), 0x400000 + rva)]
        scanner.record_emitted(rows)
        self.addCleanup(lambda: self.assertEqual(path.read_bytes(), image))
        return scanner, rows

    def test_executable_literals_survive_without_inventing_guard_bounds(self):
        image = pointer_cases.SwitchDiscoveryTests.switch_fixture()
        image[0x447] = 0x7f  # A signed guard is not accepted by the switch recognizer.
        scanner, _ = self.scanner(image)
        found = scanner.scan()
        self.assertEqual(found['targets'], {0x1060: [0x1100], 0x1070: [0x1104]})
        self.assertFalse(found['refused'])
        self.assertIn(dict(source_pointer_rva=0x104c, reason='relocation overlaps emitted instruction bytes'),
                      found['excluded_sources'])
        self.assertTrue(all(not r['behavioral_acceptance'] for r in found['origins']))
        self.assertTrue(all('unsigned_bound' not in r for r in found['origins']))

    def test_unrelocated_words_and_resource_relocations_do_not_create_roots(self):
        image = pointer_cases.SwitchDiscoveryTests.switch_fixture()
        struct.pack_into('<H', image, 0x1a0a, 0)  # Remove only the first literal relocation.
        # Include the fixture's second relocation block in the actual PE directory.
        # Its pixel word points at otherwise unowned code, so neither ownership nor
        # an instruction-interior check can accidentally conceal a bad source filter.
        struct.pack_into('<I', image, 0x98 + 96 + 5 * 8 + 4, 32)
        struct.pack_into('<I', image, 0x1800, 0x401080)
        scanner, _ = self.scanner(image)
        self.assertIn(0x5000, highlow_sites(scanner.pe))
        found = scanner.scan()
        self.assertEqual(found['targets'], {0x1070: [0x1104]})
        self.assertNotIn(0x1007, found['targets'])

    def test_targets_in_literal_data_or_instruction_interiors_stay_refused(self):
        for target in (0x401104, 0x401007):
            image = pointer_cases.SwitchDiscoveryTests.switch_fixture()
            struct.pack_into('<I', image, 0x500, target)
            with self.subTest(target=target):
                scanner, _ = self.scanner(image)
                found = scanner.scan()
                self.assertEqual(found['targets'], {0x1070: [0x1104]})
                self.assertEqual([r['rva'] for r in found['refused']], [target - 0x400000])

    def test_wrong_bytes_or_conflicting_code_masks_cannot_publish_roots(self):
        scanner, rows = self.scanner(pointer_cases.SwitchDiscoveryTests.switch_fixture())
        scanner.record_emitted(rows)  # Identical shared owners are legitimate.
        with self.assertRaisesRegex(ValueError, 'pinned original'):
            scanner.record_emitted([dict(rva=0x1000, bytes='85c1')])
        with self.assertRaisesRegex(ValueError, 'boundaries'):
            scanner.record_emitted([dict(rva=0x1001, bytes=scanner.pe.read(0x1001, 2).hex())])


if __name__ == '__main__':
    unittest.main()

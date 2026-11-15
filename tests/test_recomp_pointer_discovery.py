"""Resource pixels must not become function roots or cut real instruction bytes."""
from pathlib import Path
import struct
import tempfile
import unittest
from tools.recomp_pointer_discovery import highlow_sites, pointer_runs, propose_bounds, unowned_targets
from tools.recomp_switch_discovery import guarded_tables, prepare
import capstone


def fixture():
    image = bytearray(0x1c00)
    image[:2] = b'MZ'
    struct.pack_into('<I', image, 0x3c, 0x80)
    image[0x80:0x84] = b'PE\0\0'
    struct.pack_into('<HHIIIHH', image, 0x84, 0x14c, 5, 0, 0, 0, 224, 0x102)
    optional = 0x98
    struct.pack_into('<H', image, optional, 0x10b)
    struct.pack_into('<I', image, optional + 28, 0x400000)
    struct.pack_into('<I', image, optional + 32, 4096)
    struct.pack_into('<I', image, optional + 92, 16)
    struct.pack_into('<II', image, optional + 96 + 5 * 8, 0x6000, 32)
    sections = [(b'.text', 0x1000, 0x1000, 0x400, 0x60000020),
                (b'.rdata', 0x3000, 0x200, 0x1400, 0x40000040),
                (b'.data', 0x4000, 0x200, 0x1600, 0xc0000040),
                (b'.rsrc', 0x5000, 0x200, 0x1800, 0x40000040),
                (b'.reloc', 0x6000, 0x200, 0x1a00, 0x42000040)]
    for index, (name, rva, size, offset, flags) in enumerate(sections):
        struct.pack_into('<8sIIIIIIHHI', image, optional + 224 + index * 40,
                         name, size, rva, size, offset, 0, 0, 0, 0, flags)
    # TEST/JZ followed by two distinct MOV/RET paths. RVA1007 is inside an
    # immediate, never a function root despite appearing in resource pixels.
    image[0x400:0x410] = bytes.fromhex('85c07406b801000000c3b802000000c3')
    image[0x410] = image[0x420] = 0xc3
    struct.pack_into('<III', image, 0x1400, 0x401000, 0x401010, 0x401020)
    struct.pack_into('<III', image, 0x1600, 0x401007, 0x40100b, 0x40100d)
    struct.pack_into('<III', image, 0x1800, 0x401007, 0x401008, 0x401009)
    struct.pack_into('<IIHHHH', image, 0x1a00, 0x3000, 16, 0x3000, 0x3004, 0x3008, 0)
    # Even relocation-looking evidence in a resource section is not a vtable.
    struct.pack_into('<IIHHHH', image, 0x1a10, 0x5000, 16, 0x3000, 0x3004, 0x3008, 0)
    return image


class PointerDiscoveryTests(unittest.TestCase):
    def run_scan(self, image):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / 'pointers.exe'
        path.write_bytes(image)
        result = pointer_runs(path)
        self.assertEqual(path.read_bytes(), image)
        return result

    def test_pixels_and_unrelocated_numeric_words_do_not_cut_real_code(self):
        pe, targets, stats = self.run_scan(fixture())
        self.assertEqual(targets, {0x1000: [0x3000], 0x1010: [0x3004], 0x1020: [0x3008]})
        self.assertEqual(stats['pointer_runs'], 1)
        candidates, rejected = propose_bounds(pe, targets, [])
        self.assertFalse(rejected)
        first = next(row for row in candidates if row['rva'] == 0x1000)
        self.assertEqual(first['ranges'], [dict(rva=0x1000, size=16)])
        self.assertEqual(first['extra_entries'], [0x1000, 0x1002, 0x1004, 0x1009, 0x100a, 0x100f])
        self.assertFalse(first['behavioral_acceptance'])

    def test_missing_relocation_breaks_a_pointer_run(self):
        image = fixture()
        struct.pack_into('<H', image, 0x1a0a, 0)  # Middle source has no relocation.
        _, targets, stats = self.run_scan(image)
        self.assertEqual(targets, {})
        self.assertEqual(stats['pointer_runs'], 0)

    def test_linked_rtti_recovers_short_tables_without_weakening_pixel_filter(self):
        for count in (1, 2):
            image = self.rtti_fixture(count)
            pe, targets, stats = self.run_scan(image)
            self.assertEqual(targets, {0x1000 + i * 16: [0x3010 + i * 4] for i in range(count)})
            self.assertEqual(stats['rtti_short_tables'], 1)
            origin = stats['rtti_tables'][0]
            self.assertEqual(origin['mangled_type_name'], '.?AVTexture@@')
            self.assertEqual(origin['subobject_offset'], 4)
            self.assertEqual(origin['type_descriptor_rva'], 0x4000)
            self.assertNotIn(0x1007, targets)

    @staticmethod
    def rtti_fixture(count=2):
        image = fixture()
        image[0x1400:0x1600] = bytes(0x200)
        image[0x1600:0x1800] = bytes(0x200)
        struct.pack_into('<I', image, 0x140c, 0x403040)
        for index in range(count):
            struct.pack_into('<I', image, 0x1410 + index * 4, 0x401000 + index * 16)
        struct.pack_into('<IiIII', image, 0x1440, 0, 4, 0, 0x404000, 0x403080)
        struct.pack_into('<IIII', image, 0x1480, 0, 1, 1, 0x4030a0)
        struct.pack_into('<I', image, 0x14a0, 0x4030c0)
        struct.pack_into('<IIIIII', image, 0x14c0, 0x404000, 0, 0, 0xffffffff, 0, 64)
        image[0x1608:0x1616] = b'.?AVTexture@@\0'
        offsets = [0xc, *[0x10 + i * 4 for i in range(count)], 0x4c, 0x50, 0x8c, 0xa0, 0xc0]
        words = [0x3000 + offset for offset in offsets]
        if len(words) % 2:
            words.append(0)
        length = 8 + len(words) * 2
        struct.pack_into('<II', image, 0x1a00, 0x3000, length)
        struct.pack_into('<' + 'H' * len(words), image, 0x1a08, *words)
        struct.pack_into('<I', image, 0x98 + 96 + 5 * 8 + 4, length)
        return image

    def test_broken_rtti_chain_cannot_promote_an_isolated_code_pointer(self):
        for mutation in ('unrelocated_locator', 'mismatched_class', 'invalid_name', 'exhausted_budget'):
            image = self.rtti_fixture()
            if mutation == 'unrelocated_locator':
                struct.pack_into('<H', image, 0x1a08, 0)
            elif mutation == 'mismatched_class':
                struct.pack_into('<I', image, 0x14c0, 0x404020)
            elif mutation == 'invalid_name':
                image[0x1608] = 0
            else:
                struct.pack_into('<I', image, 0x1488, 4097)
            with self.subTest(mutation=mutation):
                _, targets, stats = self.run_scan(image)
                self.assertEqual(targets, {})
                self.assertEqual(stats['rtti_short_tables'], 0)

    def test_malformed_or_unsupported_relocation_cannot_publish_roots(self):
        for mutation in ('truncated', 'odd', 'highadj', 'duplicate'):
            image = fixture()
            if mutation == 'truncated':
                struct.pack_into('<I', image, 0x98 + 96 + 5 * 8 + 4, 31)
            elif mutation == 'odd':
                struct.pack_into('<I', image, 0x1a04, 15)
            elif mutation == 'highadj':
                struct.pack_into('<H', image, 0x1a08, 0x4000)
            else:
                struct.pack_into('<H', image, 0x1a0a, 0x3000)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.run_scan(image)

    def test_ownership_and_exhausted_decode_budget_remain_explicit(self):
        pe, targets, _ = self.run_scan(fixture())
        catalog = [dict(rva=0x1000, selection=dict(ranges=[dict(rva=0x1000, size=16)])),
                   dict(rva=0x1010)]  # Refused selection remains a known root.
        unowned, occupied = unowned_targets(targets, catalog)
        self.assertEqual(unowned, {0x1020: [0x3008]})
        self.assertIn((0x1010, 0x1010), occupied)
        candidates, rejected = propose_bounds(pe, targets, [], instruction_limit=1)
        self.assertNotIn(0x1000, [row['rva'] for row in candidates])
        self.assertIn('budget exhausted', next(row['reason'] for row in rejected if row['rva'] == 0x1000))


class SwitchDiscoveryTests(unittest.TestCase):
    @staticmethod
    def switch_fixture():
        image = fixture()
        # CMP EAX,1 / unrelated MOV / JA default / JMP [EAX*4+table].
        # The table is in executable .text, which ordinary pointer runs ignore.
        image[0x440:0x451] = bytes.fromhex('83f801894c24047707ff248500114000c3')
        image[0x460:0x466] = bytes.fromhex('b801000000c3')
        image[0x470:0x476] = bytes.fromhex('b802000000c3')
        struct.pack_into('<II', image, 0x500, 0x401060, 0x401070)
        struct.pack_into('<IIHHHH', image, 0x1a00, 0x1000, 16, 0x304c, 0x3100, 0x3104, 0)
        struct.pack_into('<I', image, 0x98 + 96 + 5 * 8 + 4, 16)
        return image

    def prepare(self, image):
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / 'switch.exe'; path.write_bytes(image)
        pe, ordinary, _ = pointer_runs(path)
        self.assertEqual(ordinary, {})
        instructions = [dict(rva=i.address - 0x400000, bytes=i.bytes.hex())
                        for i in capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32).disasm(pe.read(0x1040, 17), 0x401040)]
        return pe, instructions, highlow_sites(pe)

    def test_guarded_executable_table_recovers_unowned_case_without_widening_owner(self):
        pe, instructions, sites = self.prepare(self.switch_fixture())
        tables, rejected = guarded_tables(pe, instructions, sites)
        self.assertFalse(rejected); self.assertEqual(len(tables), 1)
        self.assertEqual([row['rva'] for row in tables[0]['targets']], [0x1060, 0x1070])
        self.assertEqual(tables[0]['unsigned_bound'], 1)
        targets = {row['rva']: [row['source_pointer_rva']] for row in tables[0]['targets']}
        catalog = [dict(rva=0x1040, selection=dict(ranges=[dict(rva=0x1040, size=17)])),
                   dict(rva=0x1070, selection=dict(ranges=[dict(rva=0x1070, size=6)]))]
        unowned, occupied = unowned_targets(targets, catalog)
        proposals, rejected = propose_bounds(pe, unowned, occupied)
        self.assertFalse(rejected); self.assertEqual(proposals[0]['ranges'], [dict(rva=0x1060, size=6)])
        self.assertFalse(tables[0]['behavioral_acceptance'])
        self.assertEqual(catalog[0]['selection']['ranges'], [dict(rva=0x1040, size=17)])

    def test_untrusted_guards_or_pointer_words_cannot_create_case_roots(self):
        for mutation in ('signed_guard', 'other_index', 'changed_flags', 'index_alias', 'self_guard',
                         'unrelocated_operand', 'unrelocated_target', 'data_target'):
            image = self.switch_fixture()
            if mutation == 'signed_guard': image[0x447] = 0x7f
            elif mutation == 'other_index': image[0x441] = 0xf9
            elif mutation == 'changed_flags': image[0x443:0x447] = bytes.fromhex('83c00090')
            elif mutation == 'index_alias': image[0x443:0x447] = bytes.fromhex('6689c890')
            elif mutation == 'self_guard': image[0x448] = 0xf9
            elif mutation == 'unrelocated_operand': struct.pack_into('<H', image, 0x1a08, 0)
            elif mutation == 'unrelocated_target': struct.pack_into('<H', image, 0x1a0a, 0)
            else: struct.pack_into('<I', image, 0x500, 0x403000)
            with self.subTest(mutation=mutation):
                pe, instructions, sites = self.prepare(image)
                tables, rejected = guarded_tables(pe, instructions, sites)
                self.assertFalse(tables); self.assertTrue(rejected)

    def test_tampered_metadata_and_missing_guard_remain_explicit(self):
        for mutation in ('tampered', 'missing', 'ambiguous'):
            pe, instructions, sites = self.prepare(self.switch_fixture())
            if mutation == 'tampered': instructions[0]['bytes'] = '83f802'
            elif mutation == 'missing': instructions = instructions[1:]
            else: instructions.append(dict(instructions[1]))
            tables, rejected = guarded_tables(pe, instructions, sites)
            self.assertFalse(tables); self.assertTrue(rejected)

    def test_table_and_guard_budgets_do_not_publish_partial_success(self):
        pe, instructions, sites = self.prepare(self.switch_fixture())
        for arguments in (dict(max_entries=1), dict(lookbehind=2)):
            tables, rejected = guarded_tables(pe, instructions, sites, **arguments)
            self.assertFalse(tables); self.assertTrue(rejected)
        with self.assertRaises(ValueError): guarded_tables(pe, instructions, sites, lookbehind=1)

    def test_preparation_refuses_an_overlay_that_would_drop_prior_selections(self):
        from tools import recomp
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); generation = root / 'generation'; overlay = root / 'overlay'
            generation.mkdir(); overlay.mkdir()
            module = dict(inventory_functions=100, catalog_functions=102, processed=102,
                          counts=dict(generated_only=102))
            recomp.atomic_json(generation / 'report.json', dict(
                status='completed inventory generation attempt; compilation/runtime remain separate',
                modules=dict(main=module, umbra=module), entry_overlay_sha256='0' * 64))
            recomp.atomic_json(overlay / 'overlay.json', dict(files={}))
            with self.assertRaisesRegex(ValueError, 'base discovery overlay differs'):
                prepare(generation, overlay, root / 'output')
            self.assertFalse((root / 'output').exists())

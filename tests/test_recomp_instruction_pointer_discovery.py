"""Materialized code addresses require original instruction/relocation origins."""
import struct
import tempfile
import unittest
from pathlib import Path
import capstone
from tools import recomp
from tools.recomp_native import PE32
from tools.recomp_instruction_pointer_discovery import (
    InstructionPointerScanner, ClosureBudgetError, discover_closure, prepare)
from tests.test_recomp_pointer_discovery import fixture


def materialization_fixture():
    image = fixture()
    forms = {
        0x1000: bytes.fromhex('b800114000c3'),       # MOV EAX, callback
        0x1010: bytes.fromhex('c70120114000c3'),     # MOV [ECX], callback
        0x1020: bytes.fromhex('6840114000c3'),       # PUSH callback
        0x1030: bytes.fromhex('8d0560114000c3'),     # LEA EAX,[absolute callback]
        0x1040: bytes.fromhex('a180114000c3'),       # Dereference code, not its address
        0x1050: bytes.fromhex('05a0114000c3'),       # Relative arithmetic, not an origin
        0x1060: bytes.fromhex('b800304000c3'),       # Data address, not code
        0x1080: bytes.fromhex('c705c0114000e0114000c3'),  # Code destination != immediate value
        0x1090: bytes.fromhex('8d8000124000c3'),     # Indexed/base-relative LEA
        0x10a0: bytes.fromhex('ff1520124000c3'),     # Indirect memory CALL
        0x1100: bytes.fromhex('b840124000c3'),       # Discovered callback materializes another
    }
    for rva, code in forms.items():
        image[0x400 + rva - 0x1000:0x400 + rva - 0x1000 + len(code)] = code
    for rva in [0x1120,0x1140,0x1160,0x1180,0x11a0,0x11c0,0x11e0,0x1200,0x1220,0x1240]:
        image[0x400 + rva - 0x1000] = 0xc3
    sources = [0x1001,0x1012,0x1021,0x1032,0x1041,0x1051,0x1061,0x1082,0x1086,0x1092,0x10a2,0x1101]
    words = [0x3000 | (rva - 0x1000) for rva in sources]
    size = 8 + len(words) * 2
    struct.pack_into('<II', image, 0x1a00, 0x1000, size)
    struct.pack_into('<' + 'H' * len(words), image, 0x1a08, *words)
    struct.pack_into('<I', image, 0x98 + 96 + 5 * 8 + 4, size)
    return image, forms


class InstructionPointerDiscoveryTests(unittest.TestCase):
    def prepare_fixture(self, image=None):
        original, forms = materialization_fixture()
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / 'callbacks.exe'; path.write_bytes(image or original)
        scanner = InstructionPointerScanner(PE32(path))
        rows = []
        for rva, code in forms.items():
            if rva == 0x1100: continue  # Only reached through closure discovery.
            raw = scanner.pe.read(rva, len(code))
            rows.extend(dict(rva=i.address-0x400000, bytes=i.bytes.hex())
                        for i in capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32).disasm(raw,0x400000+rva))
        return scanner, rows

    def test_recovers_only_actual_full_width_materializations(self):
        scanner, rows = self.prepare_fixture()
        found, rejected = scanner.scan(rows)
        self.assertEqual({p['rva'] for p in found}, {0x1100,0x1120,0x1140,0x1160,0x11e0})
        self.assertEqual({p['kind'] for p in found}, {'mov_immediate','push_immediate','lea_absolute'})
        self.assertNotIn(0x11c0, {p['rva'] for p in found})  # MOV's destination displacement.
        self.assertEqual(len(rejected), 5)
        self.assertTrue(all(p['behavioral_acceptance'] is False for p in found))

    def test_missing_relocation_or_nonexecutable_source_cannot_create_roots(self):
        image, _ = materialization_fixture()
        struct.pack_into('<H', image, 0x1a08, 0)
        scanner, rows = self.prepare_fixture(image)
        found, _ = scanner.scan(rows)
        self.assertNotIn(0x1100, {p['rva'] for p in found})
        self.assertFalse(scanner.intersects([dict(rva=0x3000,size=32)]))

    def test_tampered_and_split_instruction_bytes_remain_refusals(self):
        for raw in ['b820114000','b80011']:
            scanner, _ = self.prepare_fixture()
            found, rejected = scanner.scan([dict(rva=0x1000, bytes=raw)])
            self.assertFalse(found); self.assertTrue(rejected)

    def test_closure_discovers_callbacks_materialized_by_new_bodies(self):
        scanner, rows = self.prepare_fixture()
        found, _ = scanner.scan([r for r in rows if r['rva']==0x1000])
        catalog = [dict(rva=0x1000,selection=dict(ranges=[dict(rva=0x1000,size=6)]))]
        result = discover_closure(scanner, [(0x1000,found)], catalog)
        self.assertEqual(result['closure_rounds'],2)
        self.assertEqual({p['rva'] for p in result['proposals']},{0x1100,0x1240})
        self.assertFalse(result['rejected_bounds'])
        self.assertEqual(result['origins'][0x1240][0]['source_kind'],'bounded_original_body_hypothesis')
        self.assertEqual(catalog[0]['selection']['ranges'],[dict(rva=0x1000,size=6)])

    def test_exhausted_closure_never_returns_a_partial_success(self):
        scanner, rows = self.prepare_fixture()
        found, _ = scanner.scan([r for r in rows if r['rva']==0x1000])
        catalog = [dict(rva=0x1000,selection=dict(ranges=[dict(rva=0x1000,size=6)]))]
        with self.assertRaises(ClosureBudgetError) as caught:
            discover_closure(scanner, [(0x1000,found)], catalog, max_rounds=1)
        self.assertEqual(caught.exception.targets,[0x1100,0x1240])
        with self.assertRaises(ValueError):discover_closure(scanner,[],catalog,max_rounds=0)

    def test_wrong_base_overlay_refuses_before_any_output_is_published(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);generation=root/'generation';overlay=root/'overlay'
            generation.mkdir();overlay.mkdir()
            module=dict(inventory_functions=100,catalog_functions=102,processed=102,counts=dict(generated_only=102))
            recomp.atomic_json(generation/'report.json',dict(status='completed inventory generation attempt; compilation/runtime remain separate',
                modules=dict(main=module,umbra=module),entry_overlay=str(overlay),entry_overlay_sha256='0'*64))
            recomp.atomic_json(overlay/'overlay.json',dict(files={}))
            with self.assertRaisesRegex(ValueError,'base discovery overlay differs'):
                prepare(generation,root/'output')
            self.assertFalse((root/'output').exists())

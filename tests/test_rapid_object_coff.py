"""Generated tiny COFF/PE controls for the object comparator, not game evidence."""
import hashlib
import struct
import unittest
from rapid_object.coff import Coff, CoffError
from rapid_object.compare import compare_bytes


def pe(code):
    data = bytearray(0x200 + len(code))
    data[:2] = b'MZ'
    struct.pack_into('<I', data, 0x3c, 0x80)
    data[0x80:0x84] = b'PE\0\0'
    struct.pack_into('<HHIIIHH', data, 0x84, 0x14c, 1, 0, 0, 0, 224, 0)
    struct.pack_into('<H', data, 0x98, 0x10b)
    struct.pack_into('<I', data, 0x98 + 28, 0x400000)
    struct.pack_into('<8sIIIIIIHHI', data, 0x178, b'.text', len(code), 0x1000, len(code), 0x200, 0, 0, 0, 0, 0x60000020)
    data[0x200:] = code
    return bytes(data)


def coff(code, rels=(), targets=(), aux_size=None, comdat=False):
    """Return a valid standard COFF with long names and optional function aux."""
    strings = bytearray(b'\0' * 4)
    symbols = bytearray()
    indexes = {}

    def symbol(name, value, section, typ, storage, aux=()):
        idx = len(symbols) // 18
        indexes[name] = idx
        raw = name.encode()
        if len(raw) > 8:
            offset = len(strings)
            strings.extend(raw + b'\0')
            raw = struct.pack('<II', 0, offset)
        symbols.extend(struct.pack('<8sIhHBB', raw, value, section, typ, storage, len(aux)))
        for item in aux:
            symbols.extend(item)
        return idx

    if comdat:
        aux = bytearray(18)
        struct.pack_into('<IHH', aux, 0, len(code), len(rels), 0)
        aux[14] = 2
        symbol('.text', 0, 1, 0, 3, [aux])
    fnaux = []
    if aux_size is not None:
        aux = bytearray(18)
        struct.pack_into('<I', aux, 4, aux_size)
        fnaux = [aux]
    symbol('_fn_00001000', 0, 1, 0x20, 2, fnaux)
    for name, value, sec in targets:
        symbol(name, value, sec, 0, 2 if sec == 0 else 3)
    relocation_data = b''.join(struct.pack('<IIH', off, indexes[name], kind) for off, name, kind in rels)
    ptr = 60
    relocptr = ptr + len(code)
    symptr = relocptr + len(relocation_data)
    header = struct.pack('<HHIIIHH', 0x14c, 1, 0, symptr, len(symbols) // 18, 0, 0)
    section = struct.pack('<8sIIIIIIHHI', b'.text', 0, 0, len(code), ptr, relocptr if rels else 0, 0, len(rels), 0, 0x60000020 | (0x1000 if comdat else 0))
    struct.pack_into('<I', strings, 0, len(strings))
    return header + section + code + relocation_data + symbols + strings


class ObjectComparisonTests(unittest.TestCase):
    def compare(self, original, obj, symbols=None, requested=None):
        return compare_bytes(pe(original), obj, requested or {0x1000: {'ranges': [{'start_rva': 0x1000, 'end_rva_inclusive': 0x1000 + len(original) - 1}], 'bytes_sha256': hashlib.sha256(original).hexdigest()}}, symbols)

    def status(self, report):
        self.assertNotIn('error', report, report)
        return report['functions'][0]['status']

    def test_unsupported_relocation_before_function_is_not_skipped(self):
        obj = bytearray(coff(b'\0\0\xc3\0', [(0, '_g', 7)], [('_g', 0, 0)], aux_size=1))
        symptr, = struct.unpack_from('<I', obj, 8)
        struct.pack_into('<I', obj, symptr + 8, 2)
        self.assertEqual(self.status(self.compare(b'\xc3', obj, {'_g': 0x403000})), 'inconclusive')

    def test_absolute_symbol_cannot_be_overridden(self):
        original = b'\xa1' + struct.pack('<I', 0x403000) + b'\xc3'
        obj = coff(b'\xa1\0\0\0\0\xc3', [(1, '_g', 6)], [('_g', 0x41234567, -1)], aux_size=6)
        self.assertEqual(self.status(self.compare(original, obj, {'_g': 0x403000})), 'inconclusive')

    def test_local_addend_cannot_reach_unexamined_data(self):
        original = b'\xa1' + struct.pack('<I', 0x401006) + b'\xc3'
        obj = coff(b'\xa1' + struct.pack('<I', 6) + b'\xc3\x11', [(1, '$section', 6)], [('$section', 0, 1)], aux_size=6)
        self.assertEqual(self.status(self.compare(original, obj)), 'inconclusive')

    def test_ret_full_aux_and_comdat(self):
        for options in ({'aux_size': 1}, {'comdat': True}):
            result = self.compare(b'\xc3', coff(b'\xc3', **options))
            self.assertEqual(self.status(result), 'exact_object_match')
            self.assertFalse(result['proof'])
            self.assertFalse(result['reccmp_used'])

    def test_call_target_resolved_not_wildcarded(self):
        original = b'\xe8' + struct.pack('<I', 0x402000 - 0x401005) + b'\xc3'
        obj = coff(b'\xe8\0\0\0\0\xc3', [(1, '_callee', 0x14)], [('_callee', 0, 0)], aux_size=6)
        self.assertEqual(self.status(self.compare(original, obj, {'_callee': 0x402000})), 'exact_object_match')
        self.assertEqual(self.status(self.compare(original, obj, {'_callee': 0x402001})), 'nonmatch')
        self.assertEqual(self.status(self.compare(original, obj)), 'inconclusive')

    def test_global_addend_and_width(self):
        original = b'\xa1' + struct.pack('<I', 0x403004) + b'\xc3'
        for addend, expected in ((4, 'exact_object_match'), (8, 'nonmatch')):
            obj = coff(b'\xa1' + struct.pack('<I', addend) + b'\xc3', [(1, '_global', 6)], [('_global', 0, 0)], aux_size=6)
            self.assertEqual(self.status(self.compare(original, obj, {'_global': 0x403000})), expected)
        wrong_width = coff(b'\x66\xa1\0\0\0\0\xc3', [(2, '_global', 6)], [('_global', 0, 0)], aux_size=7)
        self.assertEqual(self.status(self.compare(original, wrong_width, {'_global': 0x403004})), 'nonmatch')

    def test_internal_label_relocation(self):
        original = b'\xe9\0\0\0\0\xc3'
        obj = coff(original, [(1, '$label', 0x14)], [('$label', 5, 1)], aux_size=6)
        self.assertEqual(self.status(self.compare(original, obj)), 'exact_object_match')

    def test_negative_addend_preserved(self):
        original = b'\xa1' + struct.pack('<I', 0x402ffc) + b'\xc3'
        obj = coff(b'\xa1\xfc\xff\xff\xff\xc3', [(1, '_global', 6)], [('_global', 0, 0)], aux_size=6)
        self.assertEqual(self.status(self.compare(original, obj, {'_global': 0x403000})), 'exact_object_match')

    def test_unknown_kind_and_helper(self):
        for kind in (7, 0xb):
            obj = coff(b'\xa1\0\0\0\0\xc3', [(1, '__helper', kind)], [('__helper', 0, 0)], aux_size=6)
            self.assertEqual(self.status(self.compare(b'\xa1\0\0\0\0\xc3', obj, {'__helper': 0x403000})), 'inconclusive')
        obj = coff(b'\xe8\0\0\0\0\xc3', [(1, '__helper', 0x14)], [('__helper', 0, 0)], aux_size=6)
        self.assertEqual(self.status(self.compare(b'\xe8\0\0\0\0\xc3', obj)), 'inconclusive')

    def test_missing_relocation_not_ignored(self):
        original = b'\xa1' + struct.pack('<I', 0x403000) + b'\xc3'
        self.assertEqual(self.status(self.compare(original, coff(b'\xa1\0\0\0\0\xc3', aux_size=6))), 'nonmatch')

    def test_partial_range_and_padding_never_prefix_match(self):
        self.assertEqual(self.status(self.compare(b'\xc3\x90', coff(b'\xc3', aux_size=1))), 'nonmatch')
        self.assertEqual(self.status(self.compare(b'\xc3', coff(b'\xc3\xcc', comdat=True))), 'nonmatch')
        req = {0x1000: {'ranges': [{'start_rva': 0x1000, 'end_rva_inclusive': 0x1000}, {'start_rva': 0x1002, 'end_rva_inclusive': 0x1002}]}}
        self.assertEqual(self.status(self.compare(b'\xc3\x90\xc3', coff(b'\xc3', aux_size=1), requested=req)), 'inconclusive')

    def test_unknown_boundary_no_inferred_prefix(self):
        self.assertEqual(self.status(self.compare(b'\xc3', coff(b'\xc3'))), 'inconclusive')

    def test_out_of_bounds_and_overlapping_relocations(self):
        for rels in ([(3, '_g', 6)], [(0, '_g', 6), (1, '_g', 6)]):
            obj = coff(b'\0' * 6, rels, [('_g', 0, 0)], aux_size=6)
            with self.assertRaises(CoffError):
                Coff(obj)
            result = self.compare(b'\0' * 6, obj)
            self.assertEqual(result['counts']['exact_object_match'], 0)

    def test_auxiliary_and_symbol_tables_malformed(self):
        base = coff(b'\xc3', aux_size=1)
        symptr = struct.unpack_from('<I', base, 8)[0]
        for mutate in ('aux', 'string', 'section', 'truncated'):
            data = bytearray(base)
            if mutate == 'aux': data[symptr + 17] = 255
            elif mutate == 'string': struct.pack_into('<I', data, symptr + 4, 0xffffffff)
            elif mutate == 'section': struct.pack_into('<h', data, symptr + 12, 2)
            else: data = data[:-8]
            with self.assertRaises((CoffError, UnicodeError)):
                Coff(data)

    def test_relocation_into_auxiliary_rejected(self):
        data = bytearray(coff(b'\0' * 4, [(0, '_g', 6)], [('_g', 0, 0)], aux_size=4))
        struct.pack_into('<I', data, 60 + 4 + 4, 1)
        with self.assertRaises(CoffError): Coff(data)

    def test_hash_identity_and_empty_input_fail_closed(self):
        obj = coff(b'\xc3', aux_size=1)
        req = {0x1000: {'ranges': [{'start_rva': 0x1000, 'end_rva_inclusive': 0x1000}], 'bytes_sha256': '0' * 64}}
        self.assertEqual(self.status(self.compare(b'\xc3', obj, requested=req)), 'inconclusive')
        result = compare_bytes(pe(b'\xc3'), obj, {})
        self.assertEqual(result['error'], 'empty_requested_functions')
        result = compare_bytes(pe(b'\xc3'), obj, {0x1000: {}}, module_sha256='0' * 64)
        self.assertEqual(result['error'], 'module_sha256_mismatch')

    def test_explicit_decorated_identity(self):
        obj = coff(b'\xc3', aux_size=1)
        result = self.compare(b'\xc3', obj, {'_fn_00001000': 0x402000})
        self.assertEqual(result['error'], 'symbol_identity_conflict')

    def test_defined_target_beyond_compared_span_refused(self):
        original = b'\xe9' + struct.pack('<I', 0) + b'\xc3'
        obj = coff(b'\xe9\0\0\0\0\xc3\x11', [(1, '$data', 0x14)], [('$data', 6, 1)], aux_size=6)
        result = self.compare(original, obj, {'$data': 0x401006})
        self.assertEqual(self.status(result), 'inconclusive')
        self.assertIn('unexamined_defined_target', result['functions'][0]['diagnostics'][0])

    def test_object_structural_regions_must_not_alias(self):
        data = bytearray(coff(b'\xc3', aux_size=1))
        struct.pack_into('<I', data, 20 + 20, 1)
        with self.assertRaises(CoffError): Coff(data)

    def test_weak_symbol_is_not_resolved_as_ordinary_external(self):
        obj = bytearray(coff(b'\xe8\0\0\0\0\xc3', [(1, '_g', 0x14)], [('_g', 0, 0)], aux_size=6))
        symptr = struct.unpack_from('<I', obj, 8)[0]
        obj[symptr + 36 + 16] = 105
        self.assertEqual(self.status(self.compare(b'\xe8\0\0\0\0\xc3', obj, {'_g': 0x401005})), 'inconclusive')

    def test_function_aux_size_outside_section(self):
        self.assertEqual(self.status(self.compare(b'\xc3', coff(b'\xc3', aux_size=2))), 'inconclusive')


if __name__ == '__main__':
    unittest.main()

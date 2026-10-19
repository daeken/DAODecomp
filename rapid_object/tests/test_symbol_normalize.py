import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from rapid_object.symbol_normalize import normalize_identifiers, propose_file


class SymbolNormalizeTests(unittest.TestCase):
    def test_consistent_identifiers_only(self):
        source = 'extern int fn_00401234(); int g_00405678;\nfn_00401234(); g_00405678 = fn_00401234();'
        result, changes = normalize_identifiers(source, {'fn_00001234': 0x401234, 'g_00005678': {'original_va': 0x405678}}, 0x400000)
        self.assertEqual(result, source.replace('fn_00401234', 'fn_00001234').replace('g_00405678', 'g_00005678'))
        self.assertEqual([c['occurrences'] for c in changes], [3, 2])

    def test_known_rva_and_ambiguous_unchanged(self):
        source = 'fn_00401234(); fn_00001234();'
        self.assertEqual(normalize_identifiers(source, {'fn_00401234': 0x801234, 'fn_00001234': 0x401234}, 0x400000), (source, []))

    def test_known_rva_hex_case_wins(self):
        source = 'fn_0040ABCD(); g_0040AbCd;'
        registry = {'fn_0040abcd': 0x80abcd, 'fn_0000abcd': 0x40abcd,
                    'g_0040abcd': 0x80abcd, 'g_0000abcd': 0x40abcd}
        self.assertEqual(normalize_identifiers(source, registry, 0x400000), (source, []))

    def test_missing_or_wrong_target_unchanged(self):
        for registry in ({}, {'fn_00001234': 0x401235}):
            self.assertEqual(normalize_identifiers('fn_00401234();', registry, 0x400000), ('fn_00401234();', []))

    def test_boundaries_comments_literals(self):
        source = '''// fn_00401234
/* fn_00401234 */ "fn_00401234\\\"" 'x'
prefix_fn_00401234 fn_00401234_suffix fn_004012345 1fn_00401234 $fn_00401234 fn_00401234$ éfn_00401234
fn_00401234();'''
        result, changes = normalize_identifiers(source, {'fn_00001234': 0x401234}, 0x400000)
        self.assertEqual(result, source[:-len('fn_00401234();')] + 'fn_00001234();')
        self.assertEqual(changes[0]['occurrences'], 1)

    def test_line_comment_continuation(self):
        source = '// fn_00401234 \\\n+fn_00401234\nfn_00401234();'
        result, changes = normalize_identifiers(source, {'fn_00001234': 0x401234}, 0x400000)
        self.assertEqual(result, source.rsplit('fn_00401234', 1)[0] + 'fn_00001234();')
        self.assertEqual(changes[0]['occurrences'], 1)

    def test_hash_bindings_and_preservation(self):
        sha = lambda value: hashlib.sha256(value).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = b'int fn_00401234();'
            (root / 'original.cpp').write_bytes(source)
            (root / 'candidate.obj').write_bytes(b'object')
            report = json.dumps({'source_sha256': sha(source), 'object_sha256': sha(b'object')}).encode()
            (root / 'report.json').write_bytes(report)
            args = (root / 'original.cpp', root / 'report.json', root / 'proposal', {'fn_00001234': 0x401234}, 0x400000)
            with self.assertRaisesRegex(ValueError, 'retained_artifact_hash_mismatch'):
                propose_file(*args, '0' * 64, sha(report))
            provenance = propose_file(*args, sha(source), sha(report))
            self.assertEqual((root / 'original.cpp').read_bytes(), source)
            self.assertEqual((root / 'proposal/candidate.cpp').read_text(), 'int fn_00001234();')
            self.assertEqual(provenance['status'], 'unvalidated_source_proposal')

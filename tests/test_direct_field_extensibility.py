"""Data/domain rejection tests; extended domains below are synthetic, not recovered functions."""
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools import freeze_direct_object_fields_pair as freeze
from tools.daodecomp.harness import file_hash, load_json
from validation import direct_object_field_cases as fields, validate_direct_object_fields as validator

ROOT = Path(__file__).resolve().parents[1]
ROWS = load_json(ROOT/'slices.json')
REGISTRY = load_json(ROOT/'analysis/functions.json')['functions']


class DirectFieldExtensibilityTests(unittest.TestCase):
    def test_external_map_exactly_matches_all_current_raw_corpora(self):
        values = fields.corpus_hashes()
        self.assertEqual(values, {f'{name}-{suite}.json': file_hash(ROOT/f'corpus/{name}-{suite}.json')
                                  for name in fields.NAMES for suite in ('public', 'heldout')})
        self.assertEqual(set(fields.NAMES), {r['name'] for r in ROWS})
        self.assertIn(fields.HASH_MAP, freeze.support_files())
        for row in ROWS:
            for suite in ('public', 'heldout'):
                self.assertEqual(fields.cases(row['name'], suite), load_json(ROOT/f"corpus/{row['name']}-{suite}.json"))
            self.assertEqual(fields.negative_cases(row['name']), fields.cases(row['name'], 'public'))

    def test_hash_map_rejects_missing_malformed_duplicate_and_inexact_domains(self):
        original = fields.corpus_hashes()
        name = next(iter(original))
        bad = [[], None, {}, {**original, 'unknown-public.json': '0'*64},
               {k: v for k, v in original.items() if k != name},
               {**original, name: 0}, {**original, name: True},
               {**original, name: 'F'*64}, {**original, name: 'a'*63}]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'hashes.json'
            with self.assertRaises(ValueError): fields.corpus_hashes(path)
            for value in bad:
                path.write_text(json.dumps(value))
                with self.subTest(value=type(value).__name__), self.assertRaises(ValueError):
                    fields.corpus_hashes(path)
            for text in ('{', '{"x": "a", "x": "b"}', 'NaN'):
                path.write_text(text)
                with self.assertRaises(ValueError): fields.corpus_hashes(path)
            target = Path(temp)/'target.json'; target.write_text(json.dumps(original))
            path.unlink(); path.symlink_to(target)
            with self.assertRaises(ValueError): fields.corpus_hashes(path)

    def test_current_process_reloads_map_and_rejects_changed_map_or_corpus(self):
        name = fields.NAMES[0]; relative = f'corpus/{name}-public.json'
        original = fields.corpus_hashes()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); corpus = root/relative; corpus.parent.mkdir()
            corpus.write_bytes((ROOT/relative).read_bytes())
            path = root/fields.HASH_MAP; path.parent.mkdir(); path.write_text(json.dumps(original))
            with patch.object(fields, 'ROOT', root):
                self.assertEqual(fields.cases(name), load_json(corpus))
                changed = dict(original); changed[corpus.name] = '0'*64; path.write_text(json.dumps(changed))
                with self.assertRaisesRegex(ValueError, 'corpus changed'): fields.cases(name)
                path.write_text(json.dumps(original)); before = corpus.read_bytes(); corpus.write_bytes(before+b' ')
                with self.assertRaisesRegex(ValueError, 'corpus changed'): fields.cases(name)
                corpus.write_bytes(before); path.unlink()
                with self.assertRaises(ValueError): fields.cases(name)

    def test_domain_equality_rejects_duplicates_missing_extra_and_binding_changes(self):
        fields.registry_domain(ROWS, REGISTRY)
        for rows in ([], {}, [None], ROWS+[ROWS[0]], [dict(ROWS[0], name=True)],
                     [dict(ROWS[0], id=True)], [dict(ROWS[0], name='../escape')]):
            with self.subTest(rows_type=type(rows).__name__), self.assertRaises(ValueError):
                fields.descriptor_domain(rows)
        for key, value in [('id', 'other'), ('name', 'fn_ffffffff'), ('rva', 1), ('size', 1),
                           ('code_sha256', '0'*64), ('module_sha256', '0'*64),
                           ('contract', 'contracts/wrong.json'), ('source', 'src/wrong.cpp'),
                           ('status', 'contracted'), ('backend', 'wrong'), ('recovery_group', 'wrong')]:
            changed = copy.deepcopy(REGISTRY)
            next(f for f in changed if f['id'] == ROWS[0]['id'])[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): fields.registry_domain(ROWS, changed)
        direct = [f for f in REGISTRY if f.get('backend') == fields.GROUP]
        for changed in (REGISTRY+[copy.deepcopy(direct[0])],
                        [f for f in REGISTRY if f['id'] != direct[0]['id']]):
            with self.assertRaises(ValueError): fields.registry_domain(ROWS, changed)
        duplicate_names = copy.deepcopy(ROWS); duplicate_names[-1]['name'] = duplicate_names[0]['name']
        duplicate_ids = copy.deepcopy(ROWS); duplicate_ids[-1]['id'] = duplicate_ids[0]['id']
        for rows in (duplicate_names, duplicate_ids):
            with self.assertRaises(ValueError): fields.descriptor_domain(rows)

    def synthetic_extended_domain(self):
        # Structural extension only. No new contract, corpus, implementation or game evidence.
        row = dict(ROWS[0], name='fn_00ffffff', id='synthetic-extension-only', rva=0xffffff)
        registry = copy.deepcopy(REGISTRY)
        entry = dict(next(f for f in registry if f['id'] == ROWS[0]['id']),
                     name=row['name'], id=row['id'], rva=row['rva'], contract=f"contracts/{row['name']}.json")
        return [*ROWS, row], [*registry, entry]

    def test_validator_and_freezer_accept_exact_extended_domain_without_count_literals(self):
        rows, registry = self.synthetic_extended_domain()
        hashes = {**fields.corpus_hashes(), **{f"{rows[-1]['name']}-{s}.json": '0'*64 for s in ('public', 'heldout')}}
        fields.registry_domain(rows, registry)
        for stage in ('public', 'heldout', 'negative'):
            self.assertEqual(len(freeze.commands([f['name'] for f in rows])[stage][0]['reports']), len(rows))
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root/'analysis').mkdir(); (root/'validation').mkdir()
            (root/'slices.json').write_text(json.dumps(rows)); (root/'analysis/functions.json').write_text(json.dumps({'functions': registry}))
            (root/fields.HASH_MAP).write_text(json.dumps(hashes))
            args = ['validator', '--binary', str(root/'reference'), '--build-dir', str(root/'build'),
                    '--report-dir', str(root/'reports'), '--function', rows[-1]['name']]
            with patch.object(validator, 'ROOT', root), patch.object(validator, 'SPECS', {f['name']: f for f in rows}), \
                 patch('sys.argv', args), patch.object(validator, 'validate_function', return_value=True) as execution:
                self.assertEqual(validator.main(), 0); self.assertEqual(execution.call_count, 1)
                # Full-domain equality still runs before --function filtering.
                (root/'analysis/functions.json').write_text(json.dumps({'functions': registry[:-1]}))
                execution.reset_mock()
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit): validator.main()
                execution.assert_not_called()
            (root/'analysis/functions.json').write_text(json.dumps({'functions': registry}))
            args = ['freezer', '--binary', str(root/'reference')]
            with patch.object(freeze, 'ROOT', root), patch.object(freeze, 'SPECS', {f['name']: f for f in rows}), \
                 patch('sys.argv', args), patch.object(freeze, 'preload_slices') as slices, \
                 patch.object(freeze, 'required_review', return_value={'review-required': 'synthetic'}), \
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(freeze.main(), 0); slices.assert_called_once_with(root/'reference', rows)
                (root/'slices.json').write_text(json.dumps(rows[:-1])); slices.reset_mock()
                with self.assertRaisesRegex(ValueError, 'frozen descriptor domain changed'): freeze.main()
                slices.assert_not_called()

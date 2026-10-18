import json
import hashlib
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
from tempfile import TemporaryDirectory
from validation import indexed_field_cases as fields, indexed_field_runner as runner
from tools import freeze_indexed_fields_pair as freeze, validate_checkpoint as checkpoint
from tools.daodecomp.memory import ARENA_BASE, execute_memory

ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / 'gamedata/bin_ship/DAOrigins.exe'
ROWS = [f for f in json.loads((ROOT/'analysis/functions.json').read_text())['functions'] if f.get('recovery_group') == 'indexed-fields-002']

class IndexedFieldAcceptanceTests(unittest.TestCase):
    def test_exact_corpora_determinism_separation_and_count(self):
        total = 0
        for name in fields.FIELD_SPECS:
            ids = []
            for suite in ('public', 'heldout'):
                generated = fields.cases(name, suite)
                saved = ROOT/freeze.EVIDENCE/f'{name}-{suite}-cases.json'
                raw = (json.dumps(generated, separators=(',', ':'))+'\n').encode()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), fields.CHARACTERIZED_CASE_HASHES[saved.name])
                if saved.is_file(): self.assertEqual(generated, json.loads(saved.read_text()))
                self.assertEqual(generated, fields.cases(name, suite))
                ids.append({c['id'] for c in generated});total += len(generated)
            self.assertFalse(ids[0] & ids[1])
        self.assertEqual(total, 15632)

    def test_strict_inputs_and_exact_six_seven_slot_footprints(self):
        for name, (kind, offset, width, limit) in fields.FIELD_SPECS.items():
            original = fields.cases(name)[0]['inputs']
            for changes in ({'index': True}, {'object': True}, {'object': 65}, {'object': -1}, {'entry_eax': 1<<32}, {'arena': 'A'*1024}, {'extra': 1}):
                with self.subTest(name=name, changes=changes), self.assertRaises(ValueError):
                    fields.fixture(name, {**original, **changes})
            if kind == 'get':
                with self.assertRaises(ValueError):fields.fixture(name, {**original, 'value': 1})
            else:
                with self.assertRaises(ValueError):fields.fixture(name, {**original, 'value': -1})
            for low in (0, limit-1, limit, 255):
                arena, reads, writes = fields.fixture(name, {**original, 'object': 64, 'index': 0xa5b60000|low})
                expected = [(64+offset+width*low, width)] if low<limit else []
                self.assertEqual(len(arena), 512)
                self.assertEqual(reads, expected if kind=='get' else [])
                self.assertEqual(writes, expected if kind=='set' else [])

    def test_dispatch_exact_abi_and_footprints(self):
        for row in ROWS:
            name=row['name'];kind=fields.FIELD_SPECS[name][0];inputs=fields.cases(name)[1]['inputs'];observed={}
            def execute(address, code, arena, **kwargs):observed.update(kwargs);return 0xa5b6c7d8, arena
            with patch.object(runner,'load_slice',return_value=(0x747cf0,b'code')), patch.object(runner,'execute_memory',side_effect=execute):
                runner.dispatch_original(row,inputs,BINARY)
            _, reads, writes=fields.fixture(name,inputs)
            self.assertEqual(observed['registers'],dict(eax=inputs['entry_eax'],ecx=ARENA_BASE+inputs['object']))
            self.assertEqual(observed['stack_arguments'],[inputs['index']]+([inputs['value']] if kind=='set' else []))
            self.assertEqual(observed['stack_cleanup'],8 if kind=='set' else 4)
            self.assertEqual((observed['readable'],observed['writable']),(reads,writes))
            self.assertEqual(observed['preserved_registers'],('ecx',))

    def test_candidate_parser_fail_closed(self):
        inputs=fields.cases('fn_00347d70')[0]['inputs']
        for output in ('1\n00\n','-1\n'+'00'*512+'\n','4294967296\n'+'00'*512+'\n','1\n'+'A'*1024+'\n'):
            with patch.object(runner.subprocess,'run',return_value=subprocess.CompletedProcess([],0,output,'')):
                with self.assertRaises(RuntimeError):runner.dispatch_candidate(dict(name='fn_00347d70'),inputs,Path('synthetic-input'))

    def test_existing_guard_rejects_denied_narrow_access_synthetic_code(self):
        for code in (bytes.fromhex('0fb601c3'),bytes.fromhex('668901c3')):
            with self.assertRaises(RuntimeError):
                execute_memory(0x401000,code,bytes(512),registers=dict(ecx=ARENA_BASE),stack_arguments=[],readable=[],writable=[],stack_cleanup=0)

    def test_negative_cases_are_exact_public_control_set(self):
        for name in fields.FIELD_SPECS:
            if name in fields.NEGATIVE_NAMES:self.assertEqual(fields.negative_cases(name),fields.cases(name))
            else:
                with self.assertRaises(ValueError):fields.negative_cases(name)

    def test_checkpoint_exact_batch_and_four_negative_reports(self):
        proposed=json.loads((ROOT/'analysis/functions.json').read_text())
        with patch.object(checkpoint.json,'loads',return_value=proposed):
            for f in proposed['functions']:
                if f.get('recovery_group')=='indexed-fields-002':f['status']='contracted'
            before=checkpoint.publication_paths(Path('/synthetic-output'))
            for f in proposed['functions']:
                if f.get('recovery_group')=='indexed-fields-002':f['status']='implemented' # Synthetic in-memory state only.
            positive,negative=checkpoint.publication_paths(Path('/synthetic-output'))
            self.assertEqual(len(positive),len(before[0])+11);self.assertEqual(len(negative),len(before[1])+4)
            next(f for f in proposed['functions'] if f.get('recovery_group')=='indexed-fields-002')['status']='contracted'
            with self.assertRaises(ValueError):checkpoint.publication_paths(Path('/synthetic-output'))

    def test_freeze_closure_and_public_packet_separation(self):
        support=set(freeze.required_files(ROOT));self.assertNotIn(freeze.CANDIDATE,support)
        for path in ('tests/test_indexed_fields.py','tests/test_linked_structures.py','validation/indexed_field_mutant.hpp'):
            self.assertIn(path,support)
        for path in support:
            if not path.startswith('local/'): self.assertTrue((ROOT/path).is_file(),path)
        if not (ROOT/freeze.EVIDENCE/'slices.txt').is_file():
            return # Private original instruction evidence is required only for freeze/packet generation.
        packet=freeze.packet_text(ROOT,ROWS)
        for name in fields.FIELD_SPECS:
            self.assertIn(name,packet)
            for c in fields.cases(name,'heldout')[:2]:self.assertNotIn(c['inputs']['arena'],packet)
        self.assertNotIn('heldout-0000',packet);self.assertIn('include dao/indexed_fields.hpp',packet)

    def test_review_prompt_keeps_full_hash_coverage_without_raw_corpora(self):
        corpus_paths = {f'{freeze.EVIDENCE}/{name}-{suite}-cases.json'
                        for name in fields.FIELD_SPECS for suite in ('public', 'heldout')}
        self.assertEqual(len(corpus_paths), 22)
        self.assertTrue(corpus_paths <= freeze.REVIEW_REQUIRED)
        self.assertTrue(corpus_paths <= set(freeze.required_files(ROOT)))
        evidence = set(freeze.prompt_evidence('local/real-independent-review.json'))
        self.assertFalse(corpus_paths & evidence)
        self.assertIn('local/real-independent-review.json', evidence)
        self.assertIn(freeze.CORPUS_SUMMARY, evidence)
        if not (ROOT/freeze.CORPUS_SUMMARY).is_file():
            return  # Private corpus summary is generated for review/freeze, not required in CI.
        freeze.verify_corpus_summary(ROOT)
        summary = freeze.corpus_summary(ROOT)
        self.assertEqual(summary['total_cases'], {'public': 14224, 'heldout': 1408})
        rows = {f['name']: f for f in summary['functions']}
        self.assertEqual(rows['fn_00347e70']['suites']['heldout']['accepted_indexes_missing'], [1, 3])
        self.assertEqual(rows['fn_00347e90']['suites']['heldout']['accepted_indexes_missing'], [1, 3, 5])
        self.assertEqual(rows['fn_00347eb0']['suites']['heldout']['accepted_indexes_missing'], [1, 3, 5])
        encoded = json.dumps(summary)
        for name in fields.FIELD_SPECS:
            self.assertEqual(rows[name]['suites']['public']['accepted_indexes_missing'], [])
            for suite in ('public', 'heldout'):
                self.assertNotIn(fields.cases(name, suite)[0]['inputs']['arena'], encoded)
        with patch.object(freeze, 'corpus_summary', return_value={'tampered': True}):
            with self.assertRaises(ValueError): freeze.verify_corpus_summary(ROOT)

    def test_freeze_refuses_unapproved_or_unbound_review(self):
        with TemporaryDirectory() as temp:
            path=Path(temp)/'review.json'
            for report in (dict(decision='needs-evidence'),dict(decision='approve',reviewed_artifacts_sha256={})):
                path.write_text(json.dumps(report))
                with self.assertRaises(ValueError):freeze.approved_review(ROOT,path)

    @unittest.skipUnless(BINARY.is_file(),'private pinned original unavailable')
    def test_original_slice_hashes_and_freeze_corpus_equality(self):
        self.assertEqual(len(freeze.verify_inputs(ROOT,BINARY)),11)

    @unittest.skipUnless(BINARY.is_file(),'private pinned original unavailable')
    def test_original_protocol_fresh_process_repeats(self):
        # 11 functions x 2 paths x 2 processes =44 original-only process invocations.
        for row in ROWS:
            limit=fields.FIELD_SPECS[row['name']][3];saved=fields.cases(row['name'])
            for i in (0,limit):
                case=saved[i];request=json.dumps(dict(schema_version=1,function_id=row['id'],case=case));results=[]
                for repeat in range(2):
                    process=subprocess.run([sys.executable,str(ROOT/'validation/indexed_field_runner.py'),'original',str(BINARY)],input=request,text=True,capture_output=True,check=True,timeout=10)
                    results.append(json.loads(process.stdout))
                self.assertEqual(results[0],results[1]);expected,after=runner.dispatch_original(row,case['inputs'],BINARY)
                self.assertEqual(results[0]['return'],expected);self.assertEqual(results[0]['memory'],dict(arena=after.hex()));self.assertEqual(results[0]['calls'],[])

if __name__=='__main__':unittest.main()

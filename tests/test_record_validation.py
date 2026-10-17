import json
from pathlib import Path
import tempfile
import unittest

from tools.daodecomp.harness import digest, file_hash
from tools.record_validation import record_report


class RecordingTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.function = {"id": "fixture:1", "source": "src/test.cpp", "contract": "contracts/test.json"}
        contract = {"function_id": "fixture:1"}
        self.artifacts = {}
        for name in ["src/test.cpp", "contracts/test.json", "analysis/functions.json", "analysis/reference-build.json"]:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(contract) if name == self.function['contract'] else '{}')
            self.artifacts[str(path)] = file_hash(path)
        self.path = self.root / 'report.json'
        self.report = {"schema_version": 1, "kind": "game", "function_id": "fixture:1", "proof": False,
                       "status": "corpus_pass", "cases": [{"status": "corpus_pass"}], "repeats": 2,
                       "artifacts_unchanged": True, "artifacts_sha256": self.artifacts.copy(),
                       "contract_sha256": digest(contract), "corpus_sha256": "fixture-corpus",
                       "native_windows_validated": False, "host": {"platform": "test"}}

    def record(self, **kwargs):
        self.path.write_text(json.dumps(self.report))
        return record_report(self.root, self.path, self.function, **kwargs)

    def test_passing_report_preserves_evidence(self):
        record = self.record()
        self.assertEqual(record['case_counts'], {'corpus_pass': 1})
        self.assertEqual(record['report_sha256'], file_hash(self.path))
        self.assertIn(self.function['source'], record['artifacts_sha256'])

    def test_stale_source_rejected(self):
        (self.root / self.function['source']).write_text('changed')
        with self.assertRaisesRegex(ValueError, 'stale artifact'): self.record()

    def test_error_cannot_be_recorded_as_positive_or_negative(self):
        self.report['cases'] = [{'status': 'runner_error'}, {'status': 'mismatch'}]
        for negative in [False, True]:
            with self.assertRaisesRegex(ValueError, 'not acceptable'): self.record(negative=negative)

    def test_negative_control_must_be_explicit(self):
        self.report['status'] = 'failed'
        self.report['cases'] = [{'status': 'mismatch'}]
        with self.assertRaises(ValueError): self.record()
        self.assertTrue(self.record(negative=True)['negative_control'])

    def test_missing_artifacts_and_wrong_contract_rejected(self):
        del self.report['artifacts_sha256'][str(self.root / self.function['source'])]
        with self.assertRaisesRegex(ValueError, 'missing required'): self.record()
        self.report['artifacts_sha256'] = self.artifacts.copy()
        self.report['contract_sha256'] = 'incorrect'
        with self.assertRaisesRegex(ValueError, 'canonical hash'): self.record()

    def test_proof_or_native_claim_rejected(self):
        for key in ['proof', 'native_windows_validated']:
            self.report[key] = True
            with self.assertRaisesRegex(ValueError, 'not acceptable'): self.record()
            self.report[key] = False

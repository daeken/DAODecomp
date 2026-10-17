from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest

from tools.daodecomp.harness import compare, differing_paths, parse_json

CONTRACT = {"schema_version": 1, "function_id": "synthetic:test", "kind": "synthetic",
            "inputs": {"value": "u32"}, "return_type": "u32", "memory": {"state": 4},
            "calls": ["log"], "preconditions": "All uint32 values."}
CASES = [{"id": "one", "inputs": {"value": 1}}]


def runner(mode, *args):
    return [sys.executable, str(Path(__file__).with_name("runner_fixture.py")), mode, *map(str, args)]


class HarnessTests(unittest.TestCase):
    def test_equal_results_are_corpus_evidence_only(self):
        result = compare(CONTRACT, CASES, runner("ok"), runner("ok"))
        self.assertEqual(result["status"], "corpus_pass")
        self.assertFalse(result["proof"])
        self.assertEqual(len(result["cases"][0]["observation_sha256"]), 64)

    def test_changes_to_each_observation_are_detected(self):
        for mode, path in (("return_mismatch", "$.return"), ("memory_mismatch", "$.memory.state"), ("call_mismatch", "$.calls")):
            with self.subTest(mode=mode):
                report = compare(CONTRACT, CASES, runner("ok"), runner(mode))
                self.assertEqual(report["status"], "failed")
                self.assertEqual(report["cases"][0]["differing_paths"], [path])
                self.assertEqual(report["cases"][0]["case"], CASES[0])

    def test_matching_crashes_do_not_pass(self):
        report = compare(CONTRACT, CASES, runner("crash"), runner("crash"))
        self.assertEqual(report["cases"][0]["status"], "runner_error")

    def test_malformed_or_incomplete_observations_do_not_pass(self):
        for mode in ("malformed", "missing_memory", "bool_return"):
            with self.subTest(mode=mode):
                report = compare(CONTRACT, CASES, runner(mode), runner(mode))
                self.assertEqual(report["cases"][0]["status"], "runner_error")

    def test_timeouts_do_not_pass(self):
        report = compare(CONTRACT, CASES, runner("hang"), runner("hang"), timeout=0.05)
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["cases"][0]["oracle"][0]["error"], "timeout")

    def test_nondeterminism_is_reported_on_either_side(self):
        for side in ("oracle", "candidate"):
            with self.subTest(side=side), tempfile.TemporaryDirectory() as temp:
                variable = runner("nondeterministic", Path(temp) / "counter")
                commands = [variable, runner("ok")] if side == "oracle" else [runner("ok"), variable]
                result = compare(CONTRACT, CASES, *commands)
                self.assertEqual(result["cases"][0]["status"], side + "_nondeterministic")

    def test_empty_duplicate_and_invalid_input_corpora_rejected(self):
        for cases in ([], CASES * 2, [{"id": "bad", "inputs": {"value": -1}}], [{"id": "bad", "inputs": {"value": True}}]):
            with self.subTest(cases=cases), self.assertRaises(ValueError):
                compare(CONTRACT, cases, runner("ok"), runner("ok"))

    def test_no_single_execution_acceptance(self):
        with self.assertRaises(ValueError):
            compare(CONTRACT, CASES, runner("ok"), runner("ok"), repeats=1)

    def test_unknown_contract_fields_rejected(self):
        bad = deepcopy(CONTRACT)
        bad["ignore_memory"] = True
        with self.assertRaises(ValueError):
            compare(bad, CASES, runner("ok"), runner("ok"))

    def test_duplicate_keys_and_float_encodings_rejected(self):
        for text in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":1.5}', '{"x":Infinity}'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_json(text)

    def test_exact_comparison_preserves_types_and_order(self):
        self.assertEqual(differing_paths(True, 1), ["$"])
        self.assertEqual(differing_paths([1, 2], [2, 1]), ["$[0]", "$[1]"])

    def test_artifact_hashes_recorded(self):
        report = compare(CONTRACT, CASES, runner("ok"), runner("ok"), artifacts=[__file__])
        self.assertTrue(report["artifacts_unchanged"])
        self.assertEqual(len(report["artifacts_sha256"][__file__]), 64)


import copy
import unittest

from tools.run_recovery_pair import (
    ARTIFACT_BINDING_HASH_DOMAIN,
    ARTIFACT_MAP_HASH_DOMAIN,
    EXECUTION_HASH_DOMAIN,
    PairError,
    canonical,
    deduplicate_prompt_provenance,
    digest,
    repair_prompt,
)


def restore_for(envelope, mode):
    # Reconstruction mode is explicit because structural coordinates have distinct layouts.
    result = copy.deepcopy(envelope["evidence"])
    bindings = {}
    for item in envelope["shared_artifact_bindings"]:
        binding = {"path": item["path"], "raw_file_sha256": item["raw_file_sha256"]}
        if digest(binding) != item["binding_sha256"]:
            raise ValueError("binding digest mismatch")
        bindings[item["binding_sha256"]] = binding
    executions = {item["provenance_sha256"]: item["value"]
                  for item in envelope["shared_execution_provenance"]}
    for row in envelope["report_provenance"]:
        report = (result[row["location"][0]]["reports"][row["location"][1]]
                  if mode == "reviewer" else result[row["location"][0]])
        if row["artifacts_present"]:
            artifact_map = {}
            for key in row["binding_refs"]:
                binding = bindings[key]
                if binding["path"] in artifact_map:
                    raise ValueError("duplicate path")
                artifact_map[binding["path"]] = binding["raw_file_sha256"]
            if digest(artifact_map) != row["artifact_map_sha256"]:
                raise ValueError("artifact map digest mismatch")
            report["execution_artifacts_raw_sha256"] = artifact_map
        if row["execution_present"]:
            value = executions[row["execution_sha256"]]
            if digest(value) != row["execution_sha256"]:
                raise ValueError("execution digest mismatch")
            report["execution"] = value
    return result


def report(inputs):
    return {
        "report": "/reports/public.json",
        "sha256": "c" * 64,
        "function": "fn_demo",
        "passed": False,
        "contract_canonical_json_sha256": "d" * 64,
        "contract_raw_file_sha256": "e" * 64,
        "corpus_canonical_json_sha256": "f" * 64,
        "corpus_raw_file_sha256": "1" * 64,
        "source_raw_file_sha256": "2" * 64,
        "execution": {"host": "runner", "compiler": "clang", "abi": {"stack": 8}},
        "execution_artifacts_raw_sha256": {"/src/runner.py": "a" * 64},
        "counterexample": {"case": {"id": "public-1", "inputs": inputs,
                                    "oracle": {"return": 9},
                                    "candidate": {"return": 10}}},
    }


class PromptDedupV2Tests(unittest.TestCase):
    def test_all_review_counterexamples_round_trip_exactly_and_inputs_are_unchanged(self):
        arbitrary_inputs = [
            {"execution": 7},
            {"execution": {"meaning": "input"},
             "execution_provenance_ref": {"original_fact": "KEEP-ME"}},
            {"execution_artifacts_raw_sha256": {"p": "b" * 64},
             "execution_artifacts_ref": {"original_fact": "KEEP-ME"}},
            {"execution_provenance_ref": {"original_fact": "ONLY-REF"}},
        ]
        original = [{"stage": "public", "passed": False,
                     "reports": [report(inputs) for inputs in arbitrary_inputs]}]
        before = canonical(original)
        envelope = deduplicate_prompt_provenance(original, mode="reviewer")
        self.assertEqual(canonical(restore_for(envelope, "reviewer")), before)
        self.assertEqual(canonical(original), before)
        self.assertEqual(len(envelope["report_provenance"]), 4)
        for index, original_report in enumerate(original[0]["reports"]):
            packed_report = envelope["evidence"][0]["reports"][index]
            self.assertEqual(packed_report["counterexample"], original_report["counterexample"])
            self.assertEqual(packed_report["report"], original_report["report"])
            self.assertEqual(packed_report["sha256"], original_report["sha256"])
        self.assertEqual(envelope["hash_domains"], {
            "artifact_binding": ARTIFACT_BINDING_HASH_DOMAIN,
            "artifact_map": ARTIFACT_MAP_HASH_DOMAIN,
            "execution_provenance": EXECUTION_HASH_DOMAIN,
        })
        self.assertIn("ensure_ascii=True", ARTIFACT_MAP_HASH_DOMAIN)
        self.assertIn("separators=(',', ':')", ARTIFACT_MAP_HASH_DOMAIN)
        self.assertIn("allow_nan=False", ARTIFACT_MAP_HASH_DOMAIN)
        self.assertIn("encode('utf-8')", ARTIFACT_MAP_HASH_DOMAIN)

    def test_report_metadata_is_only_extracted_at_known_report_locations(self):
        case = report({"execution": 7, "execution_provenance_ref": {"keep": True}})
        original = [{"stage": "public", "reports": [case]},
                    {"stage": "build", "reports": [
                        {"counterexample": {"execution": 3,
                                            "execution_artifacts_ref": {"keep": True}}}]}]
        envelope = deduplicate_prompt_provenance(original, mode="reviewer")
        self.assertEqual(canonical(restore_for(envelope, "reviewer")), canonical(original))
        self.assertEqual(len(envelope["report_provenance"]), 1)
        self.assertEqual(envelope["evidence"][1]["reports"][0], original[1]["reports"][0])

    def test_repair_preserves_execution_named_inputs_and_only_packs_public_report_rows(self):
        public = report({"execution": {"ordinary": "data"},
                         "execution_provenance_ref": {"keep": 1},
                         "execution_artifacts_ref": {"keep": 2}})
        feedback = [public, {"stage": "build", "exit_code": 1},
                    {"stage": "public", "opaque": {"execution": 7}}]
        before = canonical(feedback)
        envelope = deduplicate_prompt_provenance(feedback, mode="repair")
        self.assertEqual(canonical(restore_for(envelope, "repair")), before)
        self.assertEqual(canonical(feedback), before)
        self.assertEqual([x["location"] for x in envelope["report_provenance"]], [[0]])

    def test_same_path_different_hash_and_distinct_path_same_hash_are_distinct_bindings(self):
        rows = [{"stage": "public", "reports": [
            {"execution_artifacts_raw_sha256": {"/same": "a" * 64}},
            {"execution_artifacts_raw_sha256": {"/same": "b" * 64}},
            {"execution_artifacts_raw_sha256": {"/other": "a" * 64}},
        ]}]
        envelope = deduplicate_prompt_provenance(rows, mode="reviewer")
        self.assertEqual(len(envelope["shared_artifact_bindings"]), 3)
        self.assertEqual(canonical(restore_for(envelope, "reviewer")), canonical(rows))

    def test_tampered_or_missing_sidecar_rows_rejected(self):
        envelope = deduplicate_prompt_provenance(
            [{"stage": "public", "reports": [report({"execution": 7})]}], mode="reviewer")
        bad = copy.deepcopy(envelope)
        bad["shared_execution_provenance"][0]["value"]["host"] = "tampered"
        with self.assertRaisesRegex(ValueError, "execution digest mismatch"):
            restore_for(bad, "reviewer")
        bad = copy.deepcopy(envelope)
        bad["shared_artifact_bindings"].clear()
        with self.assertRaises((KeyError, ValueError)):
            restore_for(bad, "reviewer")
        bad = copy.deepcopy(envelope)
        bad["report_provenance"][0]["execution_sha256"] = "0" * 64
        with self.assertRaises((KeyError, ValueError)):
            restore_for(bad, "reviewer")

    def test_public_repair_wording_and_filtering_remain_public_only(self):
        public = {"stage": "public", "reports": [report({"execution": 7})]}
        heldout = {"stage": "heldout", "reports": [{"secret": "HELDOUT-MUST-NOT-APPEAR"}]}
        negative = {"stage": "negative", "reports": [{"secret": "NEGATIVE-MUST-NOT-APPEAR"}]}
        text = repair_prompt("packet", "complete source", [public, heldout, negative])
        self.assertIn("Preserve every already-passing function implementation unchanged", text)
        self.assertIn("public-1", text)
        self.assertNotIn("HELDOUT-MUST-NOT-APPEAR", text)
        self.assertNotIn("NEGATIVE-MUST-NOT-APPEAR", text)


if __name__ == "__main__":
    unittest.main()

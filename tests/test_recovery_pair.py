"""Pipeline safety tests use a fake deterministic adapter, never claim game evidence."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

from tools.run_recovery_pair import (PairError, check_manifest, digest, load, review_response,
                                     run_command, run_pair, sha, source_response, write)


# This fixture exercises command/report handling; game validation uses the existing comparator.
GATE = '''import sys, json, hashlib
from pathlib import Path
def digest(v):
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",", ":")).encode()).hexdigest()
stage, destination, mode, binary = sys.argv[1:]
if mode == "infrastructure":
    print("CMake Error: Cannot find source file: protected.cpp", file=sys.stderr)
    raise SystemExit(1)
if mode == "mutate":
    Path("oracle.py").write_text("changed")
if stage == "build":
    raise SystemExit(0)
suite = "heldout" if stage == "heldout" else "public"
corpus = json.loads(Path(suite+".json").read_text())
contract = json.loads(Path("contract.json").read_text())
status = "mismatch" if stage == "negative" or mode == "fail" else "corpus_pass"
if mode == "runner-error":
    status = "runner_error"
if mode == "oracle-unstable":
    status = "oracle_nondeterministic"
rows = [{"case_id": c["id"], "case_sha256": digest(c), "status": status,
         "case": c, "oracle": [{"observation": {"return": 1}}],
         "candidate": [{"observation": {"return": 2}}]} for c in corpus]
report = {"schema_version": 1, "function_id": contract["function_id"], "proof": False,
          "artifacts_unchanged": True, "repeats": 2, "cases": rows,
          "contract_sha256": digest(contract), "corpus_sha256": digest(corpus),
          "artifacts_sha256": {str(p.resolve()): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in (Path("src/candidate.cpp"), Path("contract.json"), Path(binary))},
          "status": "corpus_pass" if status == "corpus_pass" else "failed"}
if mode == "empty":
    report["cases"] = []
if mode == "stale-source":
    report["artifacts_sha256"][str(Path("src/candidate.cpp").resolve())] = "0" * 64
Path(destination).parent.mkdir(parents=True,exist_ok=True)
Path(destination).write_text(json.dumps(report))
raise SystemExit(1 if mode == "fail" else 0)
'''


class RecoveryPairTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.output = self.root / "local/pairs/run"
        files = {"packet.txt": "Evidence. Do not call tools.", "tools/run_model_packet.py": "# launcher",
                 "oracle.py": "# frozen oracle", "gate.py": GATE,
                 "contract.json": json.dumps({"function_id": "module:sha:rva-1"}),
                 "public.json": json.dumps([{"id": "public-1", "inputs": {"x": 1}}]),
                 "heldout.json": json.dumps([{"id": "heldout-1", "inputs": {"x": 2}}])}
        for name, text in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        binary = self.root / "original.bin"
        binary.write_bytes(b"fake reference; not game evidence")
        self.manifest = {"schema_version": 1, "group": "fixture", "packet": "packet.txt",
                         "candidate": "src/candidate.cpp",
                         "snapshot": {name: sha(self.root / name) for name in files},
                         "reference": {"path": str(binary), "sha256": sha(binary)},
                         "functions": [{"name": "f", "id": "module:sha:rva-1", "contract": "contract.json",
                                        "corpora": {"public": "public.json", "heldout": "heldout.json"}}],
                         "review_evidence": ["oracle.py"], "commands": {}}
        for stage in ("build", "public", "heldout", "negative"):
            self.manifest["commands"][stage] = [{
                "argv": ["{python}", "{tree}/gate.py", stage, "{report_dir}/" + stage + ".json", "pass", "{binary}"],
                "timeout_seconds": 5,
                "reports": [] if stage == "build" else [{"path": stage + ".json", "function": "f",
                    "corpus": "heldout" if stage == "heldout" else "public",
                    "expect": "mismatch" if stage == "negative" else "pass"}]}]
        self.path = self.root / "manifest.json"
        self.calls = []
        self.decision = "approve"

    def proposal(self, source="// candidate"):
        return {"source": source, "functions": [{"name": "f", "suggested_name": "f", "explanation": "fixture"}],
                "uncertainties": []}

    def requester(self, kind, prompt, directory, model, *args):
        self.calls.append((kind, prompt, model))
        if kind == "implementation":
            return self.proposal(), {"kind": kind, "requested_model": model, "reused": False}
        return {"decision": self.decision, "summary": "Scoped fixture review", "issues": [],
                "limitations": ["Synthetic pipeline test only"]}, {
                    "kind": kind, "requested_model": model, "reused": False}

    def run_pair(self, **kwargs):
        write(self.path, self.manifest)
        return run_pair(self.path, self.output, self.root, requester=self.requester, **kwargs)

    def mode(self, stage, value):
        self.manifest["commands"][stage][0]["argv"][-2] = value

    def test_gate_order_and_acceptance_package(self):
        result = self.run_pair()
        self.assertEqual(result["status"], "accepted-for-integration")
        self.assertTrue((self.output / "accepted/candidate.cpp").is_file())
        self.assertFalse((self.root / "src/candidate.cpp").exists())
        self.assertEqual([g["stage"] for g in result["attempts"][0]["gates"]],
                         ["build", "public", "heldout", "negative"])
        self.assertEqual([c[0] for c in self.calls], ["implementation", "review"])
        self.assertEqual(self.calls[-1][2], "gpt-6.1-sol")
        self.assertIn("ABI", self.calls[-1][1])
        self.assertIn("contract_canonical_json_sha256", self.calls[-1][1])
        self.assertIn("source_raw_file_sha256", self.calls[-1][1])
        self.assertIn("Compiler/build evidence", self.calls[-1][1])
        self.assertFalse(list(self.output.glob("attempt-*/tree-*")))

    def test_public_failure_suppresses_review_and_has_bounded_model_order(self):
        self.mode("public", "fail")
        result = self.run_pair()
        self.assertEqual(result["status"], "implementation-exhausted")
        self.assertEqual([c[2] for c in self.calls], ["gpt-6-luna", "gpt-6-luna", "gpt-6.1-sol"])
        self.assertNotIn("review", [c[0] for c in self.calls])
        self.assertIn('"return":1', self.calls[1][1])
        self.assertFalse((self.output / "accepted").exists())

    def test_public_setup_and_execution_errors_do_not_trigger_source_repair(self):
        for mode in ("infrastructure", "runner-error", "oracle-unstable"):
            with self.subTest(mode=mode):
                self.output = self.root / "local/pairs" / mode
                self.calls = []
                self.mode("public", mode)
                result = self.run_pair()
                self.assertEqual(result["status"], "needs-evidence")
                self.assertEqual(len(self.calls), 1)

    def test_compiler_repair_receives_diagnostics_from_failed_build_command(self):
        build = self.manifest["commands"]["build"]
        build.append({"argv": ["{python}", "-c", "import sys; print('candidate compile error', file=sys.stderr); sys.exit(1)"],
                      "timeout_seconds": 5, "reports": []})
        result = self.run_pair(attempts=2)
        self.assertEqual(result["status"], "implementation-exhausted")
        self.assertIn("candidate compile error", self.calls[1][1])

    def test_heldout_failure_no_retry_no_reviewer(self):
        self.mode("heldout", "fail")
        result = self.run_pair()
        self.assertEqual(result["status"], "needs-evidence")
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(result["attempts"][0]["status"], "heldout-failed")
        self.assertFalse((self.output / "attempt-1/negative.json").exists())

    def test_negative_control_failure_suppresses_review(self):
        # Producing a normal pass is not a successful negative control.
        command = self.manifest["commands"]["negative"][0]
        command["argv"][2] = "public"
        result = self.run_pair()
        self.assertEqual(result["status"], "needs-evidence")
        self.assertEqual(len(self.calls), 1)

    def test_mutating_frozen_oracle_rejected_even_when_gate_exits_zero(self):
        self.mode("build", "mutate")
        result = self.run_pair()
        self.assertEqual(result["status"], "needs-evidence")
        self.assertIn("frozen snapshot changed: oracle.py", result["reason"])
        self.assertEqual(len(self.calls), 1)
        self.assertEqual((self.root / "oracle.py").read_text(), "# frozen oracle")

    def test_empty_report_cannot_pass(self):
        self.mode("public", "empty")
        result = self.run_pair()
        self.assertEqual(result["status"], "needs-evidence")
        self.assertIn("invalid/incomplete", result["reason"])
        self.assertEqual(len(self.calls), 1)

    def test_report_must_bind_the_actually_tested_source(self):
        self.mode("public", "stale-source")
        result = self.run_pair()
        self.assertEqual(result["status"], "needs-evidence")
        self.assertIn("bind tested source", result["reason"])
        self.assertEqual(len(self.calls), 1)

    def test_missing_build_support_stops_without_model_repair(self):
        self.mode("build", "infrastructure")
        result = self.run_pair()
        self.assertEqual(result["status"], "infrastructure-error")
        self.assertEqual(len(self.calls), 1)
        self.assertFalse((self.output / "accepted").exists())

    @unittest.skipUnless(shutil.which("cmake"), "CMake configuration preflight")
    def test_cmake_missing_support_fails_before_spending_any_model_request(self):
        cmake = self.root / "CMakeLists.txt"
        cmake.write_text('cmake_minimum_required(VERSION 3.20)\nproject(Fixture LANGUAGES NONE)\n'
                         'add_executable(fixture protected-missing.cpp src/candidate.cpp)\n')
        self.manifest["snapshot"]["CMakeLists.txt"] = sha(cmake)
        self.manifest["commands"]["build"].insert(0, {
            "argv": ["cmake", "-S", "{tree}", "-B", "{build}"],
            "timeout_seconds": 10, "reports": []})
        result = self.run_pair()
        self.assertEqual(result["status"], "infrastructure-error")
        self.assertEqual(self.calls, [])
        self.assertEqual(result["new_model_request_count"], 0)

    def test_review_refusal_suppresses_accepted_package(self):
        self.decision = "needs-evidence"
        result = self.run_pair()
        self.assertEqual(result["status"], "review-needs-evidence")
        self.assertFalse(result["accepted"])
        self.assertFalse((self.output / "accepted").exists())

    def test_initial_response_reused_without_first_model_request(self):
        response = self.root / "response.json"
        write(response, self.proposal())
        result = self.run_pair(initial_response=response)
        self.assertTrue(result["accepted"])
        self.assertEqual([c[0] for c in self.calls], ["review"])
        self.assertTrue(result["model_requests"][0]["reused"])
        self.assertEqual(result["new_model_request_count"], 1)

    def test_reused_source_preserves_actual_sol_origin_and_luna_slot_separately(self):
        response = self.root / "response.json"
        write(response, self.proposal())
        write(self.root / "run.json", {"requested_model": "gpt-6.1-sol", "tool_items": []})
        result = self.run_pair(initial_response=response)
        self.assertEqual(result["model_requests"][0]["requested_model"], "gpt-6.1-sol")
        self.assertEqual(result["model_requests"][0]["attempt_slot_model"], "gpt-6-luna")

    def test_wrong_contract_and_source_schema_fail_closed(self):
        with self.assertRaises(PairError):
            source_response({**self.proposal(), "extra": True}, ["f"])
        with self.assertRaises(PairError):
            source_response(self.proposal(), ["other"])
        with self.assertRaises(PairError):
            review_response({"decision": "approve", "summary": "x", "limitations": [],
                "issues": [{"severity": "evidence", "function": "f", "detail": "unknown"}]}, ["f"])
        self.manifest["snapshot"]["oracle.py"] = "0" * 64
        with self.assertRaisesRegex(PairError, "hash mismatch"):
            check_manifest(self.manifest, self.root)

    def test_traversal_and_missing_coverage_rejected(self):
        self.manifest["candidate"] = "src/../../oracle.py"
        with self.assertRaises(PairError):
            check_manifest(self.manifest, self.root)
        self.manifest["candidate"] = "src/candidate.cpp"
        self.manifest["commands"]["heldout"][0]["reports"] = []
        with self.assertRaises(PairError):
            check_manifest(self.manifest, self.root)

    def test_timeout_is_failure_and_has_durable_metrics(self):
        result = run_command([sys.executable, "-c", "import time; time.sleep(10)"],
                             self.root, self.root / "timeout", 0.03)
        self.assertTrue(result["timed_out"])
        self.assertNotEqual(result["exit_code"], 0)
        self.assertEqual(load(self.root / "timeout/run.json"), result)

    def test_manifest_shell_strings_not_accepted(self):
        self.manifest["commands"]["build"][0]["argv"] = "true; echo yes"
        with self.assertRaises(PairError):
            check_manifest(self.manifest, self.root)


if __name__ == "__main__":
    unittest.main()

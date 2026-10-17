import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from validation import object_counter_cases as counter_cases
from validation import object_counter_runner as runner

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_object_counters", ROOT / "validation/validate_object_counters.py")
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class ObjectCounterFixtureTests(unittest.TestCase):
    def test_corpora_are_deterministic_disjoint_and_match_characterization_counts(self):
        for name in counter_cases.FIELD_OFFSETS:
            public = counter_cases.cases(name, "public")
            heldout = counter_cases.cases(name, "heldout")
            self.assertEqual((len(public), len(heldout)), (340, 128))
            self.assertEqual(public, counter_cases.cases(name, "public"))
            self.assertEqual(heldout, counter_cases.cases(name, "heldout"))
            self.assertFalse({case["id"] for case in public} & {case["id"] for case in heldout})
            for case in public + heldout:
                arena, readable, writable = counter_cases.fixture(name, case["inputs"])
                offset = case["inputs"]["object"] + counter_cases.FIELD_OFFSETS[name]
                self.assertEqual(len(arena), 512)
                self.assertEqual(readable, [(offset, 4)])
                self.assertEqual(writable, [(offset, 4)])

    def test_matches_saved_independent_characterization_when_available(self):
        local_packet = ROOT / "local/pilots/object-fields-001"
        if not local_packet.is_dir():
            self.skipTest("ignored original characterization is absent in a fresh clone")
        for name in counter_cases.FIELD_OFFSETS:
            for suite in ("public", "heldout"):
                saved = json.loads((local_packet / f"{name}-{suite}-proposed.json").read_text())
                self.assertEqual(counter_cases.cases(name, suite), saved)

    def test_rejects_bad_inputs_strictly(self):
        valid = counter_cases.cases("fn_00061f40")[0]["inputs"]
        invalid = [
            {**valid, "object": True},
            {**valid, "object": 129},
            {**valid, "object": -1},
            {**valid, "extra": 1},
            {**valid, "arena": valid["arena"].upper()},
            {**valid, "arena": valid["arena"][:-2]},
            {"arena": "z" * 1024, "object": 0},
        ]
        for inputs in invalid:
            with self.subTest(inputs=list(inputs)):
                with self.assertRaises(ValueError):
                    counter_cases.fixture("fn_00061f40", inputs)
        with self.assertRaises(ValueError):
            counter_cases.fixture("fn_unknown", valid)

    def test_full_public_corpus_is_negative_control_and_only_d0_supported(self):
        negative = counter_cases.negative_cases("fn_00061f40")
        self.assertEqual(negative, counter_cases.cases("fn_00061f40", "public"))
        self.assertEqual(len(negative), 340)
        with self.assertRaises(ValueError):
            counter_cases.negative_cases("fn_00061f60")


class ObjectCounterAdapterTests(unittest.TestCase):
    def test_original_dispatch_uses_ecx_object_and_exact_field_footprint(self):
        function = {"name": "fn_00061f60", "module_sha256": "a" * 64,
                    "rva": 0x61f60, "size": 26, "code_sha256": "b" * 64}
        case = counter_cases.cases(function["name"])[17]
        observed = {}

        def execute(address, code, arena, **kwargs):
            observed.update(kwargs)
            return 123, arena

        with patch.object(runner, "load_slice", return_value=(0x406000, b"code")), \
             patch.object(runner, "execute_memory", side_effect=execute):
            result, after = runner.dispatch_original(function, case["inputs"], Path("reference.exe"))
        obj = case["inputs"]["object"]
        offset = obj + 0xd4
        self.assertEqual(result, 123)
        self.assertEqual(len(after), 512)
        self.assertEqual(observed["registers"], {"ecx": 0x02000000 + obj})
        self.assertEqual(observed["stack_arguments"], [])
        self.assertEqual(observed["stack_cleanup"], 0)
        self.assertEqual(observed["readable"], [(offset, 4)])
        self.assertEqual(observed["writable"], [(offset, 4)])

    def test_protocol_rejects_registry_function_on_another_backend(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / "analysis").mkdir()
        registry = {"functions": [{"id": "id", "name": "fn_00061f40", "backend": "memory-001"}]}
        (root / "analysis/functions.json").write_text(json.dumps(registry))
        request = {"schema_version": 1, "function_id": "id",
                   "case": {"id": "public-0000", "inputs": counter_cases.cases("fn_00061f40")[0]["inputs"]}}
        with patch.object(runner, "ROOT", root), patch("sys.argv", ["runner", "candidate", "unused"]), \
             patch("sys.stdin") as stdin:
            stdin.read.return_value = json.dumps(request)
            # main uses json.load(sys.stdin), so provide a text stream-like object.
            from io import StringIO
            stdin.__enter__.return_value = StringIO(json.dumps(request))
            with self.assertRaisesRegex(ValueError, "not registered"):
                runner.main()

    def test_candidate_parser_rejects_malformed_observation(self):
        inputs = counter_cases.cases("fn_00061f40")[0]["inputs"]
        with patch.object(runner.subprocess, "run", return_value=subprocess.CompletedProcess(
                ["candidate"], 0, stdout="1\n00\n", stderr="")):
            with self.assertRaisesRegex(RuntimeError, "512-byte"):
                runner.dispatch_candidate({"name": "fn_00061f40"}, inputs, Path("candidate"))


class ObjectCounterValidatorTests(unittest.TestCase):
    def test_negative_validation_binds_full_public_corpus_and_mutant_binary(self):
        function = {"name": "fn_00061f40", "id": "id", "contract": "contracts/counter.json"}
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            built = {}

            def fake_compare(contract, cases, oracle, candidate, **kwargs):
                built["cases"] = cases
                built["candidate"] = candidate
                rows = [{"case_id": case["id"], "status": "corpus_pass"} for case in cases]
                for row in rows:
                    if row["case_id"] in {"public-0067", "public-0135"}:
                        row["status"] = "mismatch"
                return {"status": "failed", "cases": rows, "artifacts_unchanged": True,
                        "proof": False, "function_id": "id", "kind": "game", "repeats": 2,
                        "artifacts_sha256": {}}

            with patch.object(validator, "ROOT", directory), patch.object(validator, "compare", side_effect=fake_compare), \
                 patch.object(validator, "load_json", return_value={"schema_version": 1, "function_id": "id"}), \
                 patch.object(validator, "version", return_value="test"):
                (directory / "validation").mkdir()
                (directory / "analysis").mkdir()
                (directory / "contracts").mkdir()
                (directory / "contracts/counter.json").write_text("{}")
                for rel in ("tools/daodecomp/harness.py", "tools/daodecomp/leaf.py", "tools/daodecomp/memory.py", "tools/daodecomp/pe.py",
                            "analysis/functions.json", "analysis/reference-build.json", "CMakeLists.txt", "requirements-validation.txt",
                            "validation/object_counter_runner.py", "validation/object_counter_cases.py", "validation/object_counter_native_runner.cpp"):
                    path = directory / rel
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("placeholder")
                result = validator.validate_function(function, binary=directory / "game.exe",
                    executable=directory / "dao_object_counter_mutant", build_dir=directory,
                    report_dir=directory / "reports", suite="public", expect_mismatch=True)
            self.assertTrue(result)
            self.assertEqual(built["cases"], counter_cases.cases("fn_00061f40", "public"))
            self.assertIn("dao_object_counter_mutant", built["candidate"][-1])


if __name__ == "__main__":
    unittest.main()

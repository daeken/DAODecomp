import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from validation import indexed_store_cases as store_cases
from validation import indexed_store_runner as runner

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_indexed_stores", ROOT / "validation/validate_indexed_stores.py")
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class IndexedStoreCaseTests(unittest.TestCase):
    def test_deterministic_disjoint_characterized_sizes_and_snapshots(self):
        local = ROOT / "local/pilots/object-fields-001"
        for name in store_cases.STORE_WIDTHS:
            public, heldout = store_cases.cases(name, "public"), store_cases.cases(name, "heldout")
            self.assertEqual((len(public), len(heldout)), (1304, 128))
            self.assertEqual(public, store_cases.cases(name, "public"))
            self.assertEqual(heldout, store_cases.cases(name, "heldout"))
            self.assertFalse({c["id"] for c in public} & {c["id"] for c in heldout})
            if local.is_dir():
                for suite, generated in (("public", public), ("heldout", heldout)):
                    saved = json.loads((local / f"{name}-{suite}-proposed.json").read_text())
                    self.assertEqual(generated, saved)

    def test_strict_inputs_and_conditional_exact_width(self):
        original = store_cases.cases("fn_00347d10")[0]["inputs"]
        for patch_values in ({"index": True}, {"value": -1}, {"entry_eax": 1 << 32},
                             {"object": True}, {"object": 129}, {"arena": "A" * 1024},
                             {"extra": 1}):
            bad = {**original, **patch_values}
            with self.subTest(patch_values=patch_values), self.assertRaises(ValueError):
                store_cases.fixture("fn_00347d10", bad)
        for name, (field, width) in store_cases.STORE_WIDTHS.items():
            for low in (0, 6):
                inputs = {**original, "index": 0x12340000 | low, "object": 128}
                _, readable, writable = store_cases.fixture(name, inputs)
                self.assertEqual(readable, [])
                self.assertEqual(writable, [(128 + field + low * width, width)])
            for low in (7, 255):
                _, readable, writable = store_cases.fixture(name, {**original, "index": 0x12340000 | low})
                self.assertEqual((readable, writable), ([], []))

    def test_negative_control_is_full_public_fn_d10_only(self):
        negative = store_cases.negative_cases("fn_00347d10")
        self.assertEqual(negative, store_cases.cases("fn_00347d10", "public"))
        self.assertEqual(len(negative), 1304)
        with self.assertRaises(ValueError):
            store_cases.negative_cases("fn_00347d50")


class IndexedStoreAdapterTests(unittest.TestCase):
    def test_original_dispatch_supplies_entry_registers_stack_and_preservation(self):
        function = {"name": "fn_00347d10", "module_sha256": "a" * 64,
                    "rva": 0x347d10, "size": 30, "code_sha256": "b" * 64}
        inputs = store_cases.cases(function["name"])[23]["inputs"]
        observed = {}

        def execute(address, code, arena, **kwargs):
            observed.update(kwargs)
            return 0x12345678, arena

        with patch.object(runner, "load_slice", return_value=(0x406000, b"code")), \
             patch.object(runner, "execute_memory", side_effect=execute):
            result, after = runner.dispatch_original(function, inputs, Path("reference.exe"))
        obj, low = inputs["object"], inputs["index"] & 0xff
        self.assertEqual(result, 0x12345678)
        self.assertEqual(len(after), 512)
        self.assertEqual(observed["registers"], {"eax": inputs["entry_eax"], "ecx": 0x02000000 + obj})
        self.assertEqual(observed["stack_arguments"], [inputs["index"], inputs["value"]])
        self.assertEqual(observed["stack_cleanup"], 8)
        self.assertEqual(observed["readable"], [])
        self.assertEqual(observed["writable"], [(obj + 0x12a + 2 * low, 2)] if low < 7 else [])
        self.assertEqual(observed["preserved_registers"], ("ecx",))

    def test_candidate_parser_requires_full_lowercase_arena(self):
        inputs = store_cases.cases("fn_00347d50")[0]["inputs"]
        for output in ("1\n00\n", "1\n" + "A" * 1024 + "\n", "4294967296\n" + "00" * 512 + "\n"):
            with patch.object(runner.subprocess, "run", return_value=subprocess.CompletedProcess(
                    ["candidate"], 0, stdout=output, stderr="")):
                with self.assertRaises(RuntimeError):
                    runner.dispatch_candidate({"name": "fn_00347d50"}, inputs, Path("candidate"))


class IndexedStoreValidatorTests(unittest.TestCase):
    def test_negative_gate_uses_full_public_corpus_and_mutant(self):
        function = {"name": "fn_00347d10", "id": "id", "contract": "contracts/store.json"}
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            captured = {}

            def fake_compare(contract, cases, oracle, candidate, **kwargs):
                captured.update(cases=cases, candidate=candidate)
                rows = [{"case_id": c["id"],
                         "status": ("mismatch" if c["id"] == "public-0007" else "corpus_pass")}
                        for c in cases]
                return {"status": "failed", "cases": rows, "artifacts_unchanged": True,
                        "proof": False, "function_id": "id", "kind": "game", "repeats": 2,
                        "artifacts_sha256": {}}

            with patch.object(validator, "ROOT", root), patch.object(validator, "compare", side_effect=fake_compare), \
                 patch.object(validator, "load_json", return_value={"schema_version": 1, "function_id": "id"}), \
                 patch.object(validator, "version", return_value="test"):
                (root / "validation").mkdir()
                (root / "analysis").mkdir()
                (root / "contracts").mkdir()
                (root / "contracts/store.json").write_text("{}")
                paths = ("tools/daodecomp/harness.py", "tools/daodecomp/leaf.py", "tools/daodecomp/memory.py",
                         "tools/daodecomp/pe.py", "analysis/functions.json", "analysis/reference-build.json",
                         "CMakeLists.txt", "requirements-validation.txt", "validation/indexed_store_runner.py",
                         "validation/indexed_store_cases.py", "validation/indexed_store_native_runner.cpp")
                for rel in paths:
                    path = root / rel
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("placeholder")
                result = validator.validate_function(function, binary=root / "game.exe",
                    executable=root / "dao_indexed_store_mutant", build_dir=root, report_dir=root / "reports",
                    suite="public", expect_mismatch=True)
            self.assertTrue(result)
            self.assertEqual(captured["cases"], store_cases.cases("fn_00347d10", "public"))
            self.assertIn("dao_indexed_store_mutant", captured["candidate"][-1])


if __name__ == "__main__":
    unittest.main()

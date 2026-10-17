import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SOURCE_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_checkpoint", SOURCE_ROOT / "tools/validate_checkpoint.py")
checkpoint = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checkpoint)


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for path in ("reports", "analysis/validation", "analysis"):
            (self.root / path).mkdir(parents=True, exist_ok=True)
        self.readme = self.root / "README.md"
        self.readme.write_bytes(b"before\n")
        functions = [
            {"name": "bit_mask_or_all", "status": "implemented", "backend": "scalar"},
            {"name": "scalar_other", "status": "implemented", "backend": "scalar"},
            {"name": "fn_00061fa0", "status": "implemented", "backend": "memory-001"},
            {"name": "fn_00061f40", "status": "implemented", "backend": "object-counters-001"},
            {"name": "fn_00061f60", "status": "implemented", "backend": "object-counters-001"},
            {"name": "fn_00061f80", "status": "implemented", "backend": "object-counters-001"},
        ]
        (self.root / "analysis/functions.json").write_text(json.dumps({"functions": functions}))
        self.patcher = patch.object(checkpoint, "ROOT", self.root)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.platform_patcher = patch.object(checkpoint, "is_windows_platform", return_value=False)
        self.platform_patcher.start()
        self.addCleanup(self.platform_patcher.stop)
        self.output = self.root / "reports/checkpoint-run"
        self.record = self.root / "analysis/validation/new.json"

    def test_output_directory_must_be_new_path_under_reports(self):
        for path in (self.root / "other/out", self.root / "reports"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                checkpoint.validate_output_path(path)
        self.assertEqual(checkpoint.validate_output_path(self.output), self.output.resolve())
        self.output.mkdir()
        with self.assertRaises(FileExistsError):
            checkpoint.run_checkpoint("build", self.output, self.record, 1, runner=lambda *a, **k: self.fail("ran"))

    def test_record_path_rejects_input_and_existing_file(self):
        existing = self.root / "analysis/validation/existing.json"
        existing.write_text("{}")
        with self.assertRaises(ValueError):
            checkpoint.validate_record_path(self.root / "analysis/functions.json")
        with self.assertRaises(ValueError):
            checkpoint.validate_record_path(existing)
        self.assertEqual(checkpoint.validate_record_path(self.record), self.record.resolve())

    def test_implemented_function_with_unknown_backend_blocks_publication(self):
        registry_path = self.root / "analysis/functions.json"
        registry = json.loads(registry_path.read_text())
        registry["functions"].append({"name": "future_impl", "status": "implemented", "backend": "unknown"})
        registry_path.write_text(json.dumps(registry))
        with self.assertRaisesRegex(ValueError, "unsupported validation backend.*future_impl"):
            checkpoint.publication_paths(self.output)

    def test_object_counter_backend_has_full_and_negative_checkpoint_paths(self):
        positives, negatives = checkpoint.publication_paths(self.output)
        self.assertEqual([path.name for path in positives if "object-counters" in str(path)], [
            "fn_00061f40-all.json", "fn_00061f60-all.json", "fn_00061f80-all.json"])
        self.assertIn("fn_00061f40-mutant.json", [path.name for path in negatives])

    def test_contracted_object_counter_functions_do_not_require_publication_yet(self):
        path = self.root / "analysis/functions.json"
        registry = json.loads(path.read_text())
        for function in registry["functions"]:
            if function.get("backend") == "object-counters-001":
                function["status"] = "contracted"
        path.write_text(json.dumps(registry))
        positives, negatives = checkpoint.publication_paths(self.output)
        self.assertFalse(any("object-counters" in str(report) for report in positives))
        self.assertEqual(len(negatives), 2)

    def test_argv_construction_caps_parallelism_and_rejects_windows(self):
        steps = checkpoint.build_commands(self.root / "build", self.output, 3, windows=False)
        by_name = {name: argv for name, argv, _ in steps}
        self.assertIsInstance(by_name["scalar_all"], list)
        self.assertEqual(by_name["scalar_all"][by_name["scalar_all"].index("--jobs") + 1], "3")
        self.assertIn("object_counters_all", by_name)
        self.assertIn("object_counters_negative", by_name)
        self.assertIn("--suite", by_name["object_counters_all"])
        self.assertEqual(by_name["object_counters_all"][by_name["object_counters_all"].index("--suite") + 1], "all")
        with self.assertRaisesRegex(ValueError, "unavailable on Windows"):
            checkpoint.build_commands(self.root / "build", self.output, 2, windows=True)

    def test_run_checkpoint_rejects_windows_explicitly(self):
        with patch.object(checkpoint, "is_windows_platform", return_value=True):
            with self.assertRaisesRegex(ValueError, "unavailable on Windows"):
                checkpoint.run_checkpoint("build", self.output, self.record, 1, runner=lambda *a, **k: self.fail("ran"))

    def test_missing_readme_fails_durably_after_validation_steps(self):
        self.readme.unlink()
        with patch.object(checkpoint, "build_commands", return_value=[]):
            result = checkpoint.run_checkpoint("build", self.output, self.record, 1)
        state = json.loads((self.output / "checkpoint.json").read_text())
        self.assertEqual((result, state["status"], state["failed_step"]), (1, "failed", "record_validation"))

    def test_success_publishes_after_progress_and_captures_statuses(self):
        def runner(argv, **kwargs):
            if "record_validation.py" in argv[1]:
                target = Path(argv[argv.index("--output") + 1])
                target.write_text(json.dumps({"records": [
                    {"function_id": "scalar-id", "status": "corpus_pass", "negative_control": False},
                    {"function_id": "mutant-id", "status": "mismatch", "negative_control": True},
                ]}))
            else:
                self.readme.write_text("updated\n")
            return subprocess.CompletedProcess(argv, 0, stdout="ok\n")

        with patch.object(checkpoint, "build_commands", return_value=[]):
            result = checkpoint.run_checkpoint("build", self.output, self.record, 2, runner=runner)
        self.assertEqual(result, 0)
        state = json.loads((self.output / "checkpoint.json").read_text())
        self.assertEqual(state["status"], "passed")
        self.assertTrue(state["artifacts_unchanged"])
        self.assertEqual(state["evidence_records"][0]["status"], "corpus_pass")
        self.assertTrue(self.record.exists())
        self.assertEqual(self.readme.read_text(), "updated\n")
        self.assertFalse(list((self.root / "analysis/validation").glob(".*checkpoint-tmp.json")))

    def test_publication_failure_cleans_record_restores_readme_and_is_durable(self):
        calls = []

        def runner(argv, **kwargs):
            calls.append(argv)
            if "record_validation.py" in argv[1]:
                target = Path(argv[argv.index("--output") + 1])
                target.write_text(json.dumps({"records": []}))
                return subprocess.CompletedProcess(argv, 0, stdout="recorded")
            self.readme.write_text("partially changed\n")
            return subprocess.CompletedProcess(argv, 2, stdout="progress failed")

        with patch.object(checkpoint, "build_commands", return_value=[]):
            result = checkpoint.run_checkpoint("build", self.output, self.record, 2, runner=runner)
        self.assertEqual(result, 1)
        state = json.loads((self.output / "checkpoint.json").read_text())
        self.assertEqual((state["status"], state["failed_step"]), ("failed", "update_progress"))
        self.assertFalse(self.record.exists())
        self.assertFalse(list((self.root / "analysis/validation").glob(".*checkpoint-tmp.json")))
        self.assertEqual(self.readme.read_bytes(), b"before\n")

    def test_publication_parse_error_does_not_leave_running_checkpoint_or_temp(self):
        def runner(argv, **kwargs):
            if "record_validation.py" in argv[1]:
                Path(argv[argv.index("--output") + 1]).write_text("not json")
                return subprocess.CompletedProcess(argv, 0, stdout="done")
            self.fail("progress must not run after invalid recorder output")

        with patch.object(checkpoint, "build_commands", return_value=[]):
            result = checkpoint.run_checkpoint("build", self.output, self.record, 2, runner=runner)
        self.assertEqual(result, 1)
        state = json.loads((self.output / "checkpoint.json").read_text())
        self.assertEqual((state["status"], state["failed_step"]), ("failed", "record_validation"))
        self.assertFalse(self.record.exists())
        self.assertFalse(list((self.root / "analysis/validation").glob(".*checkpoint-tmp.json")))

    def test_timeout_is_passed_to_each_step_and_saved_as_failure(self):
        output = self.root / "reports/timeout"

        def runner(argv, **kwargs):
            self.assertEqual(kwargs["timeout"], 7)
            raise subprocess.TimeoutExpired(argv, 7, output=b"partial")

        with patch.object(checkpoint, "build_commands", return_value=[("slow", ["slow"], self.root)]):
            result = checkpoint.run_checkpoint("build", output, self.record, 1, timeout=7, runner=runner)
        state = json.loads((output / "checkpoint.json").read_text())
        self.assertEqual((result, state["failed_step"], state["steps"][0]["exit_code"]), (1, "slow", 124))
        self.assertIn("partial", (output / "logs/slow.log").read_text())


if __name__ == "__main__":
    unittest.main()

import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from tools.update_progress import END, START, Snapshot, git, progress, replace_block, update

ROOT = Path(__file__).resolve().parents[1]


class ProgressTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="dao progress ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        git(self.root, "init", "-q")
        for key, value in {"user.name": "Progress Test", "user.email": "test@example.invalid",
                           "commit.gpgsign": "false", "core.autocrlf": "false",
                           "core.hooksPath": ".githooks"}.items():
            git(self.root, "config", key, value)
        self.write("README.md", f"# Fixture\n\n{START}\nold\n{END}\n\nShared notes.\n")
        self.write("src/leaf.cpp", "unsigned leaf(unsigned value) { return value; }\n")
        self.function = {"id": "test:leaf", "status": "implemented", "source": "src/leaf.cpp",
                         "contract": "contracts/leaf.json"}
        self.document("analysis/functions.json", {"functions": [self.function]})
        self.document("analysis/reference-build.json", {"module": {"sha256": "a" * 64}})
        self.document("analysis/static-summary.json", {"module_sha256": "a" * 64, "function_hypotheses": 12})
        self.document("contracts/leaf.json", {"function_id": "test:leaf", "kind": "game"})
        self.record = {
            "function_id": "test:leaf", "status": "corpus_pass", "negative_control": False,
            "artifacts_unchanged": True, "repeats_per_side": 2, "case_counts": {"corpus_pass": 7},
            "artifacts_sha256": {p: hashlib.sha256((self.root / p).read_bytes()).hexdigest()
                                 for p in ["src/leaf.cpp", "contracts/leaf.json",
                                           "analysis/functions.json", "analysis/reference-build.json"]}}
        # Private artifacts must not be required on a fresh clone.
        self.record["artifacts_sha256"]["gamedata/bin_ship/game.exe"] = "b" * 64
        self.validation([self.record])
        for name in ["tools/update_progress.py", ".githooks/pre-commit"]:
            destination = self.root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, destination)
        (self.root / ".githooks/pre-commit").chmod(0o755)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="")

    def document(self, name, content):
        self.write(name, json.dumps({"schema_version": 1, **content}) + "\n")

    def validation(self, records):
        self.document("analysis/validation/run.json", {"evidence_level": "emulator_corpus_agreement",
                                                      "native_windows_validated": False, "records": records})

    def test_counts_unique_functions_and_ignores_negative_control(self):
        self.validation([self.record, self.record, {**self.record, "negative_control": True,
                                                   "case_counts": {"corpus_pass": 500}}])
        result = progress(Snapshot(self.root))
        self.assertIn("| C++ implementations | 1 |", result)
        self.assertIn("| Implementations with current emulator corpus evidence | 1 |", result)
        self.assertIn("| Input cases across those functions (excluding repeat runs) | 7 |", result)
        self.assertIn("| Implementations with current native Windows corpus evidence | 0 |", result)

    def test_changed_or_deleted_inputs_invalidate_evidence(self):
        for change in ["edit", "delete"]:
            with self.subTest(change=change):
                if change == "edit":
                    self.write("src/leaf.cpp", "changed source\n")
                else:
                    (self.root / "src/leaf.cpp").unlink()
                if change == "edit":
                    self.assertIn("| Implementations with current emulator corpus evidence | 0 |",
                                  progress(Snapshot(self.root)))
                else:
                    with self.assertRaisesRegex(ValueError, "missing"):
                        progress(Snapshot(self.root))

    def test_failed_empty_or_incomplete_evidence_never_counts(self):
        mutations = [{"status": "failed"}, {"case_counts": {"corpus_pass": 0}},
                     {"case_counts": {"corpus_pass": 7, "mismatch": 1}},
                     {"artifacts_unchanged": False}, {"repeats_per_side": 1},
                     {"artifacts_sha256": {}}, {"function_id": "synthetic:other"}]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                self.validation([{**self.record, **mutation}])
                self.assertIn("| Implementations with current emulator corpus evidence | 0 |",
                              progress(Snapshot(self.root)))

    def test_duplicate_function_ids_rejected(self):
        self.document("analysis/functions.json", {"functions": [self.function, self.function]})
        with self.assertRaisesRegex(ValueError, "duplicate function"):
            progress(Snapshot(self.root))

    def test_check_is_read_only_and_update_is_idempotent(self):
        before = (self.root / "README.md").read_bytes()
        with self.assertRaisesRegex(ValueError, "stale"):
            update(self.root, check=True)
        self.assertEqual((self.root / "README.md").read_bytes(), before)
        self.assertTrue(update(self.root))
        self.assertFalse(update(self.root))
        self.assertFalse(update(self.root, check=True))

    def test_markers_and_line_endings(self):
        for text in ["missing", START + END + END, END + START]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                replace_block(text, "body")
        text = f"intro\r\n{START}\r\nold\r\n{END}\r\nnotes\r\n"
        self.assertEqual(replace_block(text, "new\nbody"),
                         f"intro\r\n{START}\r\nnew\r\nbody\r\n{END}\r\nnotes\r\n")

    def test_real_hook_preserves_partial_staging_and_uses_index(self):
        self.write("README.md", (self.root / "README.md").read_text() + "Staged note.\n")
        git(self.root, "add", ".")
        self.write("README.md", (self.root / "README.md").read_text() + "Unstaged note.\n")
        # Neither this source edit nor this registry entry belongs in the commit.
        self.write("src/leaf.cpp", "unstaged source edit\n")
        self.document("analysis/functions.json", {"functions": [self.function,
                                                                {"id": "test:future", "status": "discovered"}]})
        git(self.root, "commit", "-qm", "Exercise the actual pre-commit hook")
        committed = git(self.root, "show", "HEAD:README.md").decode()
        working = (self.root / "README.md").read_text()
        self.assertIn("Staged note.", committed)
        self.assertNotIn("Unstaged note.", committed)
        self.assertIn("Unstaged note.", working)
        self.assertIn("| Functions in the recovery registry | 1 |", committed)
        self.assertIn("| Implementations with current emulator corpus evidence | 1 |", committed)
        self.assertIn("| Implementations with current emulator corpus evidence | 1 |", working)
        self.assertNotIn(b"unstaged source edit", git(self.root, "show", "HEAD:src/leaf.cpp"))
        self.assertIn("unstaged source edit", (self.root / "src/leaf.cpp").read_text())
        self.assertFalse(update(self.root, staged=True, check=True))

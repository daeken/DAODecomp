"""Synthetic PE/COFF adapter refusal tests; no game behavior claim."""
import copy
import json
from pathlib import Path
import unittest
from tests import test_native_source_export as fixtures
from tools import export_ast_matches as adapter


class AstExportTests(unittest.TestCase):
    write = fixtures.RetainedFreeExportTests.write
    mutate_json = fixtures.RetainedFreeExportTests.mutate_json

    def setUp(self):
        fixtures.RetainedFreeExportTests.setUp(self)
        self.record = {"rva": 4096, "status": "exact_object_match", "accepted_source": str(self.source),
                       "accepted_source_sha256": self.build["source_sha256"],
                       "baseline": {"rva": 4096, "source": str(self.source), "source_sha256": self.build["source_sha256"]},
                       "attempts": [{"source_sha256": self.build["source_sha256"], "bound": True,
                                     "status": "exact_object_match", "summary": str(self.folder / "summary.json")}]}
        for name in ("summary.json", "identities.json"):
            self.mutate_json(name, lambda r: r["requested"]["4096"].update(rva=4096, module_sha256=self.pin))
        path = self.root / "conversion.json"
        conversion = json.loads(path.read_text())
        conversion.update(rva=4096, module_sha256=self.pin, raw_export=str(self.root / "raw.json"))
        self.write(path, conversion)
        self.output_number = 0

    def run_bridge(self, records=None):
        self.output_number += 1
        return adapter.bridge(records if records is not None else [self.record], self.root / f"stage{self.output_number}", self.original)

    def test_bridge_uses_existing_exporter_and_preserves_source(self):
        summary_before = (self.folder / "summary.json").read_bytes()
        report = self.run_bridge()
        row = report["records"][0]
        index, files, audit = self.exporter.extend_snapshot(self.index, {}, [Path(row["measurement"]["summary"]).parent.parent / "report.json"], self.original_path)
        self.assertEqual(audit["added"], 1)
        self.assertEqual(audit["rejected"], [])
        self.assertEqual(list(files.values()), [self.source.read_bytes()])
        self.assertEqual((self.folder / "summary.json").read_bytes(), summary_before)
        self.assertNotIn("rva", adapter.exporter.read_json(row["measurement"]["summary"])["requested"]["4096"])
        self.assertEqual(row["ast_origin"]["summary_sha256"], adapter.exporter.digest(summary_before))

    def test_result_provenance_route_and_ambiguity_refusal(self):
        conversion = json.loads((self.root / "conversion.json").read_text())
        result = {"rva": 4096, "source": str(self.source), "source_sha256": self.build["source_sha256"],
                  "baseline": {"rva": 4096, "raw_export": conversion["raw_export"], "raw_export_sha256": conversion["export_sha256"]}}
        self.write(self.root / "result.json", result)
        with self.assertRaisesRegex(ValueError, "ambiguous AST baseline provenance"):
            self.run_bridge()
        (self.root / "conversion.json").unlink()
        self.assertEqual(len(self.run_bridge()["records"]), 1)
        result["baseline"]["raw_export_sha256"] = "stale"
        self.write(self.root / "result.json", result)
        with self.assertRaisesRegex(ValueError, "raw export binding"):
            self.run_bridge()

    def test_claimed_exact_cannot_promote_inconclusive_attempt(self):
        self.record["attempts"][0]["status"] = "inconclusive"
        with self.assertRaisesRegex(ValueError, "attempt not exact"):
            self.run_bridge()

    def test_stale_artifacts_and_wrong_identity_range_compiler_rejected(self):
        changes = [
            ("summary.json", lambda r: r.update(source_sha256="stale")),
            ("summary.json", lambda r: r.update(object_sha256="stale")),
            ("summary.json", lambda r: r["requested"]["4096"].update(rva=True)),
            ("summary.json", lambda r: r["requested"]["4096"]["ranges"][0].update(end_rva_inclusive=4097)),
            ("summary.json", lambda r: r["functions"][0].update(status="nonmatch")),
            ("summary.json", lambda r: r["functions"][0].update(object_size=True)),
            ("compiler.json", lambda r: r.update(sha256="wrong")),
        ]
        for name, change in changes:
            path = self.folder / name
            saved = path.read_bytes()
            self.mutate_json(name, change)
            with self.subTest(name=name, change=change), self.assertRaises(ValueError):
                self.run_bridge()
            path.write_bytes(saved)
        for path in (self.source, self.folder / "candidate.obj"):
            saved = path.read_bytes()
            path.write_bytes(b"stale")
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.run_bridge()
            path.write_bytes(saved)

    def test_nonmatches_and_inconclusive_are_skipped(self):
        rows = [{"status": s} for s in ("nonmatch", "inconclusive", "rejected")]
        report = self.run_bridge(rows)
        self.assertEqual(report["records"], [])
        self.assertEqual(report["skipped"], {s: 1 for s in ("nonmatch", "inconclusive", "rejected")})

    def test_duplicate_and_ambiguous_candidate_refused(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.run_bridge([self.record, self.record])
        self.record["attempts"].append(copy.deepcopy(self.record["attempts"][0]))
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            self.run_bridge()

    def test_unbound_attempt_and_wrong_candidate_path_refused(self):
        self.record["attempts"][0]["bound"] = 1
        with self.assertRaisesRegex(ValueError, "attempt not exact"):
            self.run_bridge()
        self.record["attempts"][0]["bound"] = True
        alternate = self.root / "elsewhere.cpp"
        alternate.write_bytes(self.source.read_bytes())
        self.record["accepted_source"] = str(alternate)
        with self.assertRaisesRegex(ValueError, "candidate path"):
            self.run_bridge()


if __name__ == "__main__":
    unittest.main()

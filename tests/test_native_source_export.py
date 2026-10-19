import json
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest

from tools.export_native_sources import MODULE_SHA256, digest, publish, snapshot


class NativeSourceExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.native = self.root / "native"
        self.object = self.root / "object"
        self.sources = []
        self.reports = []
        for root, table, status, rva in (
            (self.native, "native_functions", "reccmp_matched", 0x1000),
            (self.object, "object_results", "exact_object_match", 0x2000),
        ):
            root.mkdir()
            source = root / "candidate.cpp"
            source.write_bytes(f"// FUNCTION: DAO 0x{0x400000+rva:x}\r\nvoid f() {{}}\r\n".encode())
            self.sources.append(source)
            native = root == self.native
            binary = root / ("candidate.dll" if native else "candidate.obj")
            binary.write_bytes(b"synthetic compiler artifact")
            (root / "candidate.pdb").write_bytes(b"synthetic pdb")
            report = {
                "module_sha256": MODULE_SHA256, "source_sha256": digest(source.read_bytes()),
                ("recompiled_sha256" if native else "object_sha256"): digest(binary.read_bytes()),
                "functions": [{"rva": rva, "status": status, "score": 1.0,
                               "complete_range_compared": True, "unknowns": [],
                               "original_bytes_hex": "PRIVATE_BYTES_MUST_NOT_EXPORT"}],
                "reccmp_version": "fixture", "pdb_sha256": digest(b"synthetic pdb"),
                "operand_guard_sha256": "fixture", "tool_module_sha256": {},
                "implementation_sha256": {}, "compiler": {"file_version": "fixture", "sha256": "fixture"},
                "build": {"flags": ["/c"]}, "private_path": "/private/example",
            }
            report_path = root / "summary.json"
            report_path.write_text(json.dumps(report))
            self.reports.append(report_path)
            with closing(sqlite3.connect(root / "queue.sqlite3")) as db, db:
                db.execute(f"CREATE TABLE {table}(rva INTEGER,source TEXT,summary TEXT,status TEXT)")
                db.execute(f"INSERT INTO {table} VALUES(?,?,?,?)", (rva, str(source), str(report_path), status))

    def test_exact_sources_and_sanitized_index(self):
        index, files = snapshot(self.native, self.object)
        self.assertEqual(index["matched_functions"], 2)
        self.assertEqual(set(files.values()), {p.read_bytes() for p in self.sources})
        self.assertTrue(all(f["annotation_line"] == 1 for f in index["functions"]))
        output = self.root / "published"
        publish(index, files, output)
        self.assertEqual({(output / p).read_bytes() for p in files}, set(files.values()))
        serialized = (output / "index.json").read_text()
        self.assertNotIn("PRIVATE_BYTES", serialized)
        self.assertNotIn("/private/", serialized)
        self.assertNotIn(str(self.root), serialized)

    def test_modified_source_refused(self):
        self.sources[0].write_text("changed source")
        with self.assertRaisesRegex(ValueError, "source/module binding"):
            snapshot(self.native, self.object)

    def test_modified_object_refused(self):
        (self.object / "candidate.obj").write_bytes(b"changed object")
        with self.assertRaisesRegex(ValueError, "compiled artifact binding"):
            snapshot(self.native, self.object)

    def test_incomplete_report_refused(self):
        report = json.loads(self.reports[0].read_text())
        report["functions"][0]["complete_range_compared"] = False
        self.reports[0].write_text(json.dumps(report))
        with self.assertRaisesRegex(ValueError, "incomplete native comparison"):
            snapshot(self.native, self.object)

    def test_unmatched_rows_are_not_published(self):
        with closing(sqlite3.connect(self.object / "queue.sqlite3")) as db, db:
            db.execute("UPDATE object_results SET status='nonmatch'")
        index, files = snapshot(self.native, self.object)
        self.assertEqual(index["matched_functions"], 1)
        self.assertEqual(len(files), 1)


class RetainedFreeExportTests(unittest.TestCase):
    """Synthetic tiny PE/COFF controls; no game behavior claim."""

    def setUp(self):
        from unittest.mock import patch
        from tests.test_rapid_object_coff import pe, coff
        from rapid_object.compare import compare_bytes
        from tools import export_native_sources as exporter
        self.exporter = exporter
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.folder = self.root / "build"
        self.folder.mkdir()
        self.original = pe(b"\xc3")
        self.original_path = self.root / "original.exe"
        self.original_path.write_bytes(self.original)
        self.pin = digest(self.original)
        self.patch = patch.object(exporter, "MODULE_SHA256", self.pin)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.source = self.root / "candidate.cpp"
        self.source.write_bytes(b"// FUNCTION: DAO 0x00401000\nvoid fn_00001000() {}\n")
        (self.folder / "candidate.cpp").write_bytes(self.source.read_bytes())
        obj = coff(b"\xc3", aux_size=1)
        (self.folder / "candidate.obj").write_bytes(obj)
        compiler = {"sha256": exporter.SELECTED_COMPILER_SHA256, "file_version": "synthetic selected identity"}
        self.build = {"exit_code": 0, "compiler": compiler, "source_sha256": digest(self.source.read_bytes()),
                      "object_sha256": digest(obj), "module_sha256": self.pin, "flags": exporter.SELECTED_FLAGS}
        self.raw = {"module_sha256": self.pin, "rva": 0x1000, "original_va": 0x401000,
                    "ranges": [{"start_rva": 0x1000, "end_rva_inclusive": 0x1000}],
                    "bytes_sha256": digest(b"\xc3"), "symbols": []}
        self.write(self.root / "raw.json", self.raw)
        self.write(self.root / "conversion.json", {"export_sha256": digest((self.root / "raw.json").read_bytes()), "source_sha256": self.build["source_sha256"]})
        requested = {0x1000: {k: self.raw[k] for k in ("original_va", "ranges", "bytes_sha256")}}
        requested[0x1000]["symbol"] = "_fn_00001000"
        symbols = {"_fn_00001000": 0x401000}
        report = compare_bytes(self.original, obj, requested, symbols, self.build["source_sha256"], compiler, self.pin)
        report["build"] = self.build
        self.write(self.folder / "summary.json", report)
        self.write(self.folder / "run.json", self.build)
        self.write(self.folder / "compiler.json", compiler)
        self.write(self.folder / "identities.json", {"requested": requested, "symbols": symbols, "module_sha256": self.pin})
        self.row = {"rva": 0x1000, "source": str(self.source), "raw_export": str(self.root / "raw.json"),
                    "measurement": {"status": "exact_object_match", "summary": str(self.folder / "summary.json"), "build": self.build}}
        self.index = {"functions": [], "translation_units": [], "counts": {}, "matched_functions": 0}

    def write(self, path, value):
        path.write_text(json.dumps(value))

    def run_export(self, rows=None):
        report = self.root / "sample-report.json"
        self.write(report, {"records": rows or [self.row]})
        return self.exporter.extend_snapshot(self.index, {}, [report], self.original_path)

    def mutate_json(self, filename, change):
        path = self.folder / filename
        value = json.loads(path.read_text())
        change(value)
        self.write(path, value)

    def test_verified_match_and_sanitized_metadata(self):
        index, files, audit = self.run_export()
        self.assertEqual(audit["added"], 1)
        self.assertEqual(audit["rejected"], [])
        self.assertEqual(list(files.values()), [self.source.read_bytes()])
        public = json.dumps(index)
        self.assertNotIn(str(self.root), public)
        self.assertNotIn("bytes_hex", public)
        self.assertEqual(index["functions"][0]["original_bytes_sha256"], digest(b"\xc3"))

    def test_duplicates_preserve_existing_evidence(self):
        index, files, audit = self.run_export([self.row, self.row])
        self.assertEqual((audit["verified_matches"], audit["added"], audit["duplicates_preserved"]), (2, 1, 1))
        self.index = index
        _, _, audit = self.run_export()
        self.assertEqual((audit["added"], audit["duplicates_preserved"]), (0, 1))

    def test_missing_artifacts_are_explicit_rejections(self):
        for filename in ("candidate.obj", "candidate.cpp", "run.json", "compiler.json", "identities.json", "summary.json"):
            path = self.folder / filename
            saved = path.read_bytes()
            path.unlink()
            with self.subTest(filename=filename):
                _, _, audit = self.run_export()
                self.assertEqual(audit["added"], 0)
                self.assertEqual(len(audit["rejected"]), 1)
            path.write_bytes(saved)

    def test_mutation_controls_fail_closed(self):
        mutations = [
            ("summary.json", lambda r: r.update(source_sha256="changed")),
            ("summary.json", lambda r: r.update(object_sha256="changed")),
            ("summary.json", lambda r: r.update(module_sha256="changed")),
            ("summary.json", lambda r: r.update(implementation_sha256={})),
            ("summary.json", lambda r: r["requested"]["4096"]["ranges"][0].update(end_rva_inclusive=4097)),
            ("summary.json", lambda r: r["symbol_addresses"].update(_fn_00001000=0x401001)),
            ("summary.json", lambda r: r["functions"][0].update(status="nonmatch")),
            ("summary.json", lambda r: r["functions"][0].update(object_size=0)),
            ("compiler.json", lambda r: r.update(sha256="other compiler")),
            ("run.json", lambda r: r.update(flags=["/c"])),
        ]
        for filename, change in mutations:
            path = self.folder / filename
            saved = path.read_bytes()
            self.mutate_json(filename, change)
            with self.subTest(filename=filename, change=change):
                _, _, audit = self.run_export()
                self.assertEqual(audit["added"], 0)
                self.assertEqual(len(audit["rejected"]), 1)
            path.write_bytes(saved)

    def test_forged_report_does_not_override_actual_object(self):
        (self.folder / "candidate.obj").write_bytes(b"corrupt")
        _, _, audit = self.run_export()
        self.assertEqual(audit["rejected_reasons"], {"object_binding": 1})

    def test_other_statuses_cannot_be_accepted(self):
        for status in ("nonmatch", "inconclusive", "rounded_match", "comparison_missing"):
            self.row["measurement"]["status"] = status
            _, _, audit = self.run_export()
            self.assertEqual(audit["added"], 0)
            self.assertEqual(audit["not_reported_match"], {status: 1})


    def test_coordinated_object_hash_mutation_still_recompares(self):
        from tests.test_rapid_object_coff import coff
        obj = coff(b"\x90", aux_size=1)
        (self.folder / "candidate.obj").write_bytes(obj)
        self.build["object_sha256"] = digest(obj)
        self.write(self.folder / "run.json", self.build)
        self.mutate_json("summary.json", lambda r: r.update(build=self.build, object_sha256=digest(obj)))
        _, _, audit = self.run_export()
        self.assertEqual(audit["rejected_reasons"], {"recomparison_binding": 1})


if __name__ == "__main__":
    unittest.main()

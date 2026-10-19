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


if __name__ == "__main__":
    unittest.main()

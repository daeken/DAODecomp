import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from test_pe import image


class CLITests(unittest.TestCase):
    def test_intake_writes_manifest_without_changing_binary(self):
        with tempfile.TemporaryDirectory() as temp:
            original = Path(temp) / "original.exe"
            report = Path(temp) / "manifest.json"
            original.write_bytes(image())
            result = subprocess.run([sys.executable, "-m", "tools.daodecomp", "fingerprint",
                                     str(original), "--output", str(report)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(original.read_bytes(), image())
            self.assertEqual(json.loads(report.read_text())["architecture"], "x86")

    def test_output_cannot_replace_reference_binary(self):
        with tempfile.TemporaryDirectory() as temp:
            original = Path(temp) / "original.exe"
            original.write_bytes(image())
            result = subprocess.run([sys.executable, "-m", "tools.daodecomp", "fingerprint",
                                     str(original), "--output", str(original)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must not overwrite", result.stderr)
            self.assertEqual(original.read_bytes(), image())

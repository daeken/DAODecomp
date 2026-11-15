"""Immutable-table collision/identity controls, separate from game validation."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from tools import recomp


class StaticCodeLookupTests(unittest.TestCase):
    def test_collisions_zero_max_empty_null_steps_and_table_identity(self):
        compiler = shutil.which('clang++')
        if not compiler:
            self.skipTest('requires clang++')
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / 'lookup'
            result = subprocess.run([compiler, '-std=c++20', '-O2',
                '-fsanitize=address,undefined', '-fno-sanitize-recover=all',
                '-I', str(recomp.RUNTIME),
                str(recomp.ROOT / 'recompiler/experiments/static_code_lookup.cpp'),
                '-o', str(executable)], capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stderr)
            result = subprocess.run([str(executable)], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)

"""Instruction debugging for the formatter's PUSH r/m32, not game validation."""
from pathlib import Path
import json
import shutil
import subprocess
import tempfile
import unittest
from tools import recomp
from recompiler.experiments.call_fixture import make_fixture

PUSHES = ('ff7590', 'ff3424', 'ff7424fc', 'ff742404', 'ff3406', 'ff3500880000')


def fixture(project):
    image, _, _ = make_fixture()
    image = bytearray(image)
    functions = []
    for i, text in enumerate(PUSHES):
        code = bytes.fromhex(text + '83c404c3')
        image[0x200+i*16:0x200+i*16+len(code)] = code
        functions.append(dict(rva=0x1000+i*16, size=len(code), annotations={}))
    binary = project / 'memory-push.exe'
    binary.write_bytes(image)
    recomp.atomic_json(project/'project.json', dict(schema_version=1, revision=0, binary=str(binary),
        module=binary.name, binary_sha256=recomp.digest(image), image_base=0x400000,
        sharp_retro=str(recomp.ROOT.parent/'SharpRetro'), functions=functions))


class MemoryPushTests(unittest.TestCase):
    def test_generated_push_carries_unknowns_and_uses_incoming_esp(self):
        if not shutil.which('dotnet') or not shutil.which('clang++'):
            self.skipTest('requires SharpRetro and Clang')
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            fixture(project)
            generated = recomp.generate(project)
            view, _ = recomp.read_view(project, generated['view'])
            self.assertIn('push_scalar32(s,memory,push_value)', (view/'fn_00001000.cpp').read_text())
            executable = project / 'driver'
            built = subprocess.run(['clang++', '-std=c++20', '-O2', '-fsanitize=address,undefined',
                '-fno-sanitize-recover=all', '-I', str(view), '-I', str(recomp.RUNTIME),
                str(recomp.ROOT/'recompiler/experiments/memory_push.cpp'), *map(str, view.glob('*.cpp')),
                '-o', str(executable)], capture_output=True, text=True, timeout=90)
            self.assertEqual(built.returncode, 0, built.stderr)
            result = subprocess.run([str(executable)], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), dict(known_cases=82, native_cases=0,
                partial_cases=18, fault_guards=2, wraparound_cases=1))


if __name__ == '__main__':
    unittest.main()

"""Debug the reached byte XOR's unknown-bit transport; not game validation."""
from pathlib import Path
import json
import shutil
import subprocess
import tempfile
import unittest
from tools import recomp
from recompiler.experiments.call_fixture import make_fixture


def fixture(project):
    image, _, _ = make_fixture()
    image = bytearray(image)
    functions = []
    for register in range(8):
        image[0x200+register*16:0x203+register*16] = bytes([0x30, register*8+7, 0xc3])
        functions.append(dict(rva=0x1000+register*16, size=3, annotations={}))
    image[0x300:0x304] = bytes.fromhex('300c30c3')
    functions.append(dict(rva=0x1100, size=4, annotations={}))
    binary = project / 'byte-xor.exe'
    binary.write_bytes(image)
    recomp.atomic_json(project/'project.json', dict(schema_version=1, revision=0, binary=str(binary),
        module=binary.name, binary_sha256=recomp.digest(image), image_base=0x400000,
        sharp_retro=str(recomp.ROOT.parent/'SharpRetro'), functions=functions))


class ByteXorTests(unittest.TestCase):
    def test_generated_byte_xor_preserves_unknowns_flags_aliases_and_faults(self):
        if not shutil.which('dotnet') or not shutil.which('clang++'):
            self.skipTest('requires SharpRetro and Clang')
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            fixture(project)
            generated = recomp.generate(project)
            view, _ = recomp.read_view(project, generated['view'])
            self.assertIn('xor_memory_gpr8(s,memory,address,1)', (view/'fn_00001100.cpp').read_text())
            executable = project / 'driver'
            result = subprocess.run(['clang++', '-std=c++20', '-O2', '-fsanitize=address,undefined',
                '-fno-sanitize-recover=all', '-I', str(view), '-I', str(recomp.RUNTIME),
                str(recomp.ROOT/'recompiler/experiments/byte_xor.cpp'), *map(str, view.glob('*.cpp')),
                '-o', str(executable)], capture_output=True, text=True, timeout=90)
            self.assertEqual(result.returncode, 0, result.stderr)
            result = subprocess.run([str(executable)], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), dict(native_cases=0, abstract_cases=52, fault_guards=2))


if __name__ == '__main__':
    unittest.main()

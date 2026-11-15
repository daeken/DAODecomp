"""Require byte-checked lowering, independently of native arithmetic observations."""
from pathlib import Path
import shutil
import tempfile
import unittest
from tools import recomp
from recompiler.experiments.x87_register_add_sub import project_at, FORMS
from recompiler.experiments import x87_constants, x87_integer_memory


class X87RegisterArithmeticTests(unittest.TestCase):
    def test_integer_memory_families_preserve_ten_byte_stores_and_narrow_reads(self):
        if not shutil.which('dotnet'):self.skipTest('requires SharpRetro and .NET')
        with tempfile.TemporaryDirectory() as temporary:
            project=Path(temporary);x87_integer_memory.project_at(project)
            generated=recomp.generate(project);view,manifest=recomp.read_view(project,generated['view'])
            self.assertEqual(len(manifest['functions']),13)
            for index,function in enumerate(manifest['functions']):
                access=[a for a in function['unrecovered_accesses'] if a['instruction_rva']==function['rva']]
                expected=(80,'write') if index==12 else (32 if index<6 else 16,'read')
                self.assertEqual([(a['width'],a['mode']) for a in access],[expected])

    def test_constant_load_family_lowers_from_original_bytes(self):
        if not shutil.which('dotnet'):self.skipTest('requires SharpRetro and .NET')
        with tempfile.TemporaryDirectory() as temporary:
            project=Path(temporary);x87_constants.project_at(project)
            generated=recomp.generate(project);view,manifest=recomp.read_view(project,generated['view'])
            self.assertEqual(len(manifest['functions']),7)
            for index,name in enumerate(x87_constants.CONSTANTS):
                rva=0x1000+index*8
                function=next(f for f in manifest['functions'] if f['rva']==rva)
                self.assertEqual(function['instructions'][0]['bytes'],bytes([0xd9,0xe8+index]).hex())
                source=(view/(function['name']+'.cpp')).read_text()
                tag=f'X87Op::{name}' if name in ('fld1','fldz') else 'static_cast<X87Op>(0x7fff)'
                self.assertIn(f'memory.execute_x87({tag},s,0x{0x400000+rva:x}ULL,0,0x{0x1e8+index:x});',source)

    def test_all_register_families_lower_to_original_checked_opcodes(self):
        if not shutil.which('dotnet'):self.skipTest('requires SharpRetro and .NET')
        with tempfile.TemporaryDirectory() as temporary:
            project=Path(temporary);project_at(project)
            generated=recomp.generate(project);view,manifest=recomp.read_view(project,generated['view'])
            self.assertEqual(len(manifest['functions']),56)
            for form,(first,second) in enumerate(FORMS):
                for index in range(8):
                    rva=0x1000+form*0x40+index*8
                    function=next(f for f in manifest['functions'] if f['rva']==rva)
                    self.assertEqual(function['instructions'][0]['bytes'],bytes([first,second+index]).hex())
                    source=(view/(function['name']+'.cpp')).read_text()
                    opcode=((first&7)<<8)|(second+index)
                    self.assertIn(f'memory.execute_x87(static_cast<X87Op>(0x7fff),s,0x{0x400000+rva:x}ULL,0,0x{opcode:x});',source)


if __name__=='__main__':unittest.main()

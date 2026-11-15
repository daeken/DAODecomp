"""Keep recovered memory provenance consistent with actual SSE load/store roles."""
from pathlib import Path
import shutil
import tempfile
import unittest
from tools import recomp
from recompiler.experiments.call_fixture import make_fixture

class SimdMemoryProvenanceTests(unittest.TestCase):
    def test_extended_simd_families_keep_original_operand_widths_and_directions(self):
        if not shutil.which('dotnet'):
            self.skipTest('requires SharpRetro')
        with tempfile.TemporaryDirectory() as temporary:
            image,_,_=make_fixture();image=bytearray(image);functions=[]
            forms=[('f30f2c44242cc3',32,'read'),('f30f2d3ec3',32,'read'),('f20f2c06c3',64,'read'),('f20f2d06c3',64,'read'),
                   ('f30f5306c3',32,'read'),('f20f5106c3',64,'read'),('f30f7e06c3',64,'read'),('660fd606c3',64,'write'),
                   ('f20f2a06c3',32,'read'),('f30f2a06c3',32,'read'),('0fc606e4c3',128,'read')]
            for index,(code,width,direction) in enumerate(forms):
                body=bytes.fromhex(code);rva=0x1000+index*32
                image[0x200+index*32:0x200+index*32+len(body)]=body
                functions.append(dict(rva=rva,size=len(body),annotations={}))
            binary=Path(temporary)/'scalar-conversions.exe';binary.write_bytes(image)
            result=recomp.export(dict(binary=str(binary),binary_sha256=recomp.digest(image),module=binary.name,image_base=0x400000,
                sharp_retro=str(recomp.ROOT.parent/'SharpRetro'),functions=functions))
            for function,(_,width,direction) in zip(result['functions'],forms,strict=True):
                access=[a for a in function['unrecovered_accesses'] if a['instruction_rva']==function['rva']]
                self.assertEqual([(a['width'],a['mode']) for a in access],[(width,direction)])

    def test_movd_load_and_store_have_distinct_access_directions(self):
        if not shutil.which('dotnet'):
            self.skipTest('requires SharpRetro')
        with tempfile.TemporaryDirectory() as temporary:
            image,_,_=make_fixture();image=bytearray(image);functions=[]
            for index,code in enumerate(['660f6e06c3','660f7e06c3']):
                body=bytes.fromhex(code);rva=0x1000+index*32
                image[0x200+index*32:0x200+index*32+len(body)]=body
                functions.append(dict(rva=rva,size=len(body),annotations={}))
            binary=Path(temporary)/'simd.exe';binary.write_bytes(image)
            result=recomp.export(dict(binary=str(binary),binary_sha256=recomp.digest(image),module=binary.name,image_base=0x400000,
                sharp_retro=str(recomp.ROOT.parent/'SharpRetro'),functions=functions))
            for function,direction in zip(result['functions'],['read','write'],strict=True):
                access=[a for a in function['unrecovered_accesses'] if a['instruction_rva']==function['rva']]
                self.assertEqual([(a['width'],a['mode']) for a in access],[(32,direction)])

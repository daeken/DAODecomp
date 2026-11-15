"""Candidate ownership/provenance guards on constructed PE32; not game evidence."""
import copy
from pathlib import Path
import tempfile
import unittest
from tools import recomp
from tools.recomp_live import abi_identity, checked_selection, choose_selection
from recompiler.experiments.call_fixture import make_fixture


class LiveCandidateTests(unittest.TestCase):
    def setUp(self):
        temporary=tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        self.root=Path(temporary.name); binary=self.root/'fixture.exe'
        image,functions,_=make_fixture(); binary.write_bytes(image)
        self.state=dict(binary=str(binary),binary_sha256=recomp.digest(image),image_base=0x400000)
        f=functions['callee']; self.selection=dict(f,slice_sha256=recomp.digest(image[0x240:0x240+f['size']]))
        self.inventory=self.root/'inventory.json'
        recomp.atomic_json(self.inventory,dict(module_sha256=self.state['binary_sha256'],functions=[dict(rva=f['rva'],name='constructed',
            body_ranges=[dict(start_rva=f['rva'],end_rva_inclusive=f['rva']+f['size']-1)])]))

    def test_byte_pin_range_ownership_and_executable_section_are_required(self):
        self.assertEqual(checked_selection(self.state,self.selection,[]),self.selection)
        with self.assertRaisesRegex(ValueError,'overlap'): checked_selection(self.state,self.selection,[self.selection])
        with self.assertRaisesRegex(ValueError,'bytes changed'): checked_selection(self.state,dict(self.selection,slice_sha256='0'*64),[])
        with self.assertRaisesRegex(ValueError,'envelope'): checked_selection(self.state,dict(self.selection,ranges=[dict(rva=0x103f,size=1)]),[])
        with self.assertRaisesRegex(ValueError,'executable'): checked_selection(self.state,dict(self.selection,rva=0x2000),[])
        binary=Path(self.state['binary']); binary.write_bytes(binary.read_bytes()+b'changed')
        with self.assertRaisesRegex(ValueError,'binary hash changed'): checked_selection(self.state,self.selection,[])

    def test_inventory_or_explicit_review_required_without_guessing_bounds(self):
        selected=choose_selection(self.state,self.inventory,0x1040,[],[])
        self.assertIn('observed',selected['purpose'])
        with self.assertRaisesRegex(ValueError,'reviewed discovery'): choose_selection(self.state,self.inventory,0x1060,[],[])
        review=dict(binary_sha256=self.state['binary_sha256'],selection=self.selection)
        self.assertEqual(choose_selection(self.state,self.inventory,0x1040,[review],[])['size'],self.selection['size'])
        with self.assertRaisesRegex(ValueError,'ambiguous'): choose_selection(self.state,self.inventory,0x1040,[review,review],[])

    def test_runtime_backend_and_compiler_bytes_change_abi_identity(self):
        compiler=self.root/'compiler'; compiler.write_bytes(b'constructed compiler identity')
        manifest=dict(files={n:'a'*64 for n in ('runtime.hpp','runtime_api.hpp','candidate_api.hpp')},backend_artifacts={'backend.dll':'b'*64})
        initial=abi_identity(manifest,compiler)
        for name in manifest['files']:
            changed=copy.deepcopy(manifest); changed['files'][name]='c'*64
            self.assertNotEqual(initial,abi_identity(changed,compiler))
        changed=copy.deepcopy(manifest); changed['backend_artifacts']['backend.dll']='d'*64
        self.assertNotEqual(initial,abi_identity(changed,compiler))
        driver=self.root/'clang'; driver.write_bytes(b'underlying compiler')
        with_driver=abi_identity(manifest,compiler)
        self.assertNotEqual(initial,with_driver)
        driver.write_bytes(b'changed underlying compiler')
        self.assertNotEqual(with_driver,abi_identity(manifest,compiler))
        compiler.write_bytes(b'different compiler'); self.assertNotEqual(initial,abi_identity(manifest,compiler))

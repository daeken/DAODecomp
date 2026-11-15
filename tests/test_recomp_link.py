"""Synthetic module linkage/data tests. Not game-function validation."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from tools import recomp
from tools.recomp_link import resolve_bindings, reviewed_data_sections
from recompiler.experiments.link_fixture import make_pair,CALLER_BASE,PROVIDER_BASE,RVA,BIAS,COUNTER,TABLE


class InlineDataBoundsTests(unittest.TestCase):
    def test_only_pinned_noninstruction_bytes_are_exposed(self):
        image, _, _, _ = make_pair()
        with tempfile.TemporaryDirectory() as directory:
            binary=Path(directory) / "fixture.exe"; binary.write_bytes(image)
            # Explicit pool in executable storage. Adjacent instruction bytes
            # must remain unmapped even when the OS backing shares a page.
            rva=0x1100; size=4; content=image[0x300:0x304]
            region=dict(rva=rva,size=size,sha256=recomp.digest(content),purpose="synthetic pool",
                        provenance=dict(module_sha256=recomp.digest(image)))
            state=dict(binary=str(binary),binary_sha256=recomp.digest(image),data_regions=[region])
            result=dict(image_base=CALLER_BASE,pe_image_size=0x4000,data_sections=[],
                        functions=[dict(instructions=[dict(rva=rva-1,bytes="90")])])
            sections=reviewed_data_sections(state,result)
            self.assertEqual((sections[0]["address"],sections[0]["size"],sections[0]["writable"]),
                             (CALLER_BASE+rva,4,False))
            for change, message in ((dict(rva=rva-1),"overlaps"),
                                    (dict(sha256="0"*64),"bytes changed"),
                                    (dict(provenance=dict(module_sha256="0"*64)),"invalid"),
                                    (dict(size=0),"invalid"), (dict(rva=0x3800),"file-backed")):
                state["data_regions"]=[dict(region,**change)]
                with self.assertRaisesRegex(ValueError,message): reviewed_data_sections(state,result)
            state["data_regions"]=[region,region]
            with self.assertRaisesRegex(ValueError,"overlaps"): reviewed_data_sections(state,result)


class Pe32LinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("dotnet") or not (recomp.ROOT.parent / "SharpRetro/Decompiler/Pe32AbiFacts.cs").exists():
            raise unittest.SkipTest("requires SharpRetro PE32 support")
        cls.temporary=tempfile.TemporaryDirectory(); cls.addClassCleanup(cls.temporary.cleanup)
        cls.root=Path(cls.temporary.name)
        caller,caller_fn,provider,provider_fn=make_pair()
        cls.projects=[]
        for name,image,base,function in (("caller.exe",caller,CALLER_BASE,caller_fn),
                                         ("fixture_provider.dll",provider,PROVIDER_BASE,provider_fn)):
            binary=cls.root / name; binary.write_bytes(image); project=cls.root / (name+"-project")
            recomp.atomic_json(project / "project.json",dict(schema_version=1,revision=0,binary=str(binary),module=name,
                binary_sha256=recomp.digest(image),image_base=base,sharp_retro=str(recomp.ROOT.parent / "SharpRetro"),functions=[function]))
            cls.projects.append(project)
        generated=recomp.generate(cls.projects[0],linked_modules=[cls.projects[1]],require_translated_code=True)
        cls.view=generated["view"]; cls.directory,cls.manifest=recomp.read_view(cls.projects[0],cls.view)

    def test_module_identity_same_rva_and_name_or_ordinal_resolution(self):
        self.assertEqual([f["rva"] for f in self.manifest["functions"]],[RVA,RVA])
        self.assertEqual(len({f["name"] for f in self.manifest["functions"]}),2)
        self.assertEqual(len({f["id"] for f in self.manifest["functions"]}),2)
        for symbol in ("transform","@ordinal:7","bias","counter","vtable"):
            bindings=resolve_bindings(self.manifest["modules"],self.manifest["functions"],
                [dict(library="FIXTURE_PROVIDER.DLL",symbol=symbol,address=CALLER_BASE+0x2050,policy="native")])
            row=bindings[0]
            self.assertTrue(row["symbol_resolved"])
            self.assertEqual(row["status"],"translated_code" if symbol in ("transform","@ordinal:7") else "translated_data")
        with self.assertRaisesRegex(ValueError,"ambiguous"):
            recomp.select_function(self.manifest,RVA)
        function=recomp.select_function(self.manifest,RVA,"fixture_provider.dll")
        with self.assertRaisesRegex(ValueError,"owning project"):
            recomp.owned_function(self.manifest,recomp.state(self.projects[0]),self.projects[0],RVA,"fixture_provider.dll")
        self.assertTrue(function["name"].startswith("m_"))

    def test_missing_code_symbols_and_forwarders_do_not_become_native(self):
        for symbol,expected in (("transform","untranslated_code"),("absent","missing_export"),("@ordinal:99","missing_export")):
            imports=[dict(library="fixture_provider.dll",symbol=symbol,address=CALLER_BASE+0x2050,policy="native")]
            row=resolve_bindings(self.manifest["modules"],[],imports)[0]
            self.assertEqual(row["status"],expected); self.assertEqual(imports[0]["policy"],"translate")
            self.assertFalse(row["code_ready"])
        provider=dict(self.manifest["modules"][1],exports=[dict(name="forward",forwarder="other.target")])
        row=resolve_bindings([provider],[],[dict(library="fixture_provider.dll",symbol="forward",address=1,policy="native")])[0]
        self.assertEqual(row["status"],"unsupported_forwarder"); self.assertFalse(row["symbol_resolved"])
        # Strict generation must not replace the prior valid immutable view.
        project=self.root / "empty-provider"
        state=dict(recomp.state(self.projects[1]),functions=[])
        recomp.atomic_json(project / "project.json",state)
        before=(self.projects[0] / "current.json").read_bytes()
        recipe=(self.projects[0] / "link.json").read_bytes()
        with self.assertRaisesRegex(ValueError,"lack executable code"):
            recomp.generate(self.projects[0],linked_modules=[project],require_translated_code=True)
        self.assertEqual((self.projects[0] / "current.json").read_bytes(),before)
        self.assertEqual((self.projects[0] / "link.json").read_bytes(),recipe)
        with self.assertRaisesRegex(ValueError,"duplicate module"):
            recomp.generate(self.projects[0],linked_modules=[self.projects[1],project])

    def test_compiled_cross_module_data_vtable_return_budget_and_integrity(self):
        if not shutil.which("clang++"): self.skipTest("requires clang++")
        driver=self.root / "linked.cpp"
        driver.write_text(r'''
#include "functions.hpp"
#include "image_memory.hpp"
#include <cstdio>
#include <string>
template<class F> bool rejects(F f) { try { f(); return false; } catch(const std::exception&) { return true; } }
int main(int argc,char** argv) {
 if(argc!=2) return 99;
 using recomp_generated::ImageMemory;
 for(unsigned size:{0u,1u,55u,56u,63u,64u,65u,10001u}) {
  std::vector<std::uint8_t> input(size); for(unsigned i=0;i<size;i++) input[i]=std::uint8_t(i*17+3);
  std::puts(recomp_generated::image_sha256(input).c_str());
 }
 ImageMemory memory; memory.map_bytes("stack",0x8000,0x1000,true,true);
 recomp_generated::initialize_linked_images(memory,argv[1]);
 if(!memory.is_sealed() || memory.load(0x402050,32)!=0x30001160 || memory.load(0x30002250,32)!=0 ||
    memory.load(0x300020d0,32)!=0x30001160 || memory.load(0x300020c0,32)!=11) return 1;
 for(unsigned i=0;i<2;i++) {
  sharp_retro::State state; state.gpr[4]=0x8800;
  memory.store(0x8800,0x12345678,32); memory.store(0x8804,12,32); memory.store(0x8808,9,32);
  std::uint64_t budget=1;
  if(recomp_generated::execute_guest(0x401160,0x12345678,state,memory,budget)!=sharp_retro::Exit::budget_exhausted || budget!=0) return 2;
  budget=100;
  if(recomp_generated::resume_guest(0x12345678,state,memory,budget)!=sharp_retro::Exit::returned ||
     state.gpr[0]!=57+2*i || state.gpr[4]!=0x8804 || memory.load(0x30002250,32)!=2*(i+1)) return 3;
 }
 // Existing vtable pointers resolve via the same translated-function registry.
 if(!recomp_generated::resolve_guest(unsigned(memory.load(0x300020d0,32)))) return 4;
 if(!rejects([&]{ memory.store(0x30003000,0,8); }) ||
    !rejects([&]{ memory.load(0x30002300,8); }) ||
    !rejects([&]{ memory.load(0xffffffff,16); }) ||
    !rejects([&]{ memory.map_bytes("late",0x10000,16,true,true); })) return 5;
 memory.store(0x402050,0x30001161,32);
 sharp_retro::State unknown; unknown.gpr[4]=0x8800; std::uint64_t remaining=100;
 if(!rejects([&]{ recomp_generated::execute_guest(0x401160,0x12345678,unknown,memory,remaining); })) return 8;
 ImageMemory other; other.map_bytes("a",0xfffffffc,4,false,true);
 if(!rejects([&]{ other.map_bytes("overlap",0xfffffffe,2,true,true); }) ||
    !rejects([&]{ other.map_bytes("wrap",0xffffffff,2,true,true); })) return 6;
 other.store(0xfffffffc,0xabcdef01,32); other.seal();
 if(!rejects([&]{ other.load(0xfffffffc,32); })) return 7;
 return 0;
}
''')
        executable=self.root / "linked"
        built=subprocess.run(["clang++","-std=c++20","-O2","-fsanitize=address,undefined","-fno-sanitize-recover=all",
                              "-I",str(self.directory),str(driver),*map(str,self.directory.glob("*.cpp")),"-o",str(executable)],
                             capture_output=True,text=True,timeout=90)
        self.assertEqual(built.returncode,0,built.stderr)
        run=subprocess.run([str(executable),str(self.directory)],capture_output=True,text=True,timeout=10)
        self.assertEqual(run.returncode,0,run.stderr)
        expected=[recomp.digest(bytes((i*17+3)&255 for i in range(size))) for size in (0,1,55,56,63,64,65,10001)]
        self.assertEqual(run.stdout.splitlines(),expected)
        # Loader integrity is independent of the Python manifest check.
        copied=self.root / "changed-data"; shutil.copytree(self.directory,copied)
        data=copied / self.manifest["modules"][1]["data_sections"][0]["file"]
        content=data.read_bytes(); data.write_bytes(bytes([content[0]^1])+content[1:])
        run=subprocess.run([str(executable),str(copied)],capture_output=True,text=True,timeout=10)
        self.assertNotEqual(run.returncode,0)
        self.assertIn("changed/truncated",run.stderr)


if __name__=="__main__": unittest.main()

"""Synthetic guest32 structure analysis and lowering checks, not game proofs."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from tools import recomp
from test_recomp import pe32


SCENARIOS = {
    "fields": "89ca8b421889421c0fb64220c3",
    "overlap": "8b01668b4102884101c3",
    "negative": "8b41fc894108c3",
    "nested": "8b51048b4208c3",
    "conflict": "85c0740489caeb0289da8b4204c3",
    "join": "85c0740489caeb0289ca8b4204c3",
    "indexed": "8b449108c3",
    "segment": "648b4108c3",
    "stack": "8b442404c3",
    "loop_changed": "83c1044a75fa8b4108c3",
    "read_write": "8b410840894108c3",
    "narrow_root": "88ca0fb6d28b4208c3",
    "lea": "8d51048b4208c3",
    "changed_entry": "89ca83c10c8b4208c3",
    "alias": "8b4104408942088b4104c3",
    "stack_pointer": "8b5424048b4208c3",
}


class StructureRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("dotnet") or not (recomp.ROOT.parent / "SharpRetro/Decompiler/Pe32ObjectRecovery.cs").exists():
            raise unittest.SkipTest("requires local SharpRetro guest32 structure recovery and .NET 10")
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.root = Path(cls.temporary.name)
        cls.binary = cls.root / "fixture.exe"
        code = bytearray()
        selections = []
        cls.rvas = {}
        for name, hexcode in SCENARIOS.items():
            cls.rvas[name] = 0x1000 + len(code)
            data = bytes.fromhex(hexcode)
            selections.append({"rva": cls.rvas[name], "size": len(data), "annotations": {}})
            code.extend(data)
            code.extend(b"\xcc" * ((-len(code)) % 16))
        cls.binary.write_bytes(pe32(code))
        cls.state = {"schema_version": 1, "revision": 0, "binary": str(cls.binary), "module": cls.binary.name,
                     "binary_sha256": recomp.digest(cls.binary.read_bytes()), "image_base": 0x400000,
                     "sharp_retro": str(recomp.ROOT.parent / "SharpRetro"), "functions": selections}
        cls.typed = recomp.export(cls.state)
        cls.raw = recomp.export(cls.state, raw_memory=True)
        cls.functions = {name: next(f for f in cls.typed["functions"] if f["rva"] == rva)
                         for name, rva in cls.rvas.items()}

    def test_fields_offsets_aliases_overlaps_and_nested_pointer_relationships(self):
        structure, = self.functions["fields"]["structures"]
        self.assertEqual(structure["entry_register"], 1)
        self.assertEqual([(f["offset"], f["width"], f["read"], f["write"]) for f in structure["fields"]],
                         [(0x18, 32, True, False), (0x1c, 32, False, True), (0x20, 8, True, False)])
        overlap, = self.functions["overlap"]["structures"]
        self.assertEqual([(f["offset"], f["width"]) for f in overlap["fields"]], [(0, 32), (1, 8), (2, 16)])
        self.assertTrue(all(f["overlapping"] for f in overlap["fields"]))
        negative, = self.functions["negative"]["structures"]
        self.assertEqual({f["offset"] for f in negative["fields"]}, {-4, 8})
        parent, child = self.functions["nested"]["structures"]
        self.assertEqual(parent["fields"][0]["pointer_targets"], [child["origin"]])
        self.assertEqual(child["source_field_origin"], parent["fields"][0]["origin"])
        lea, = self.functions["lea"]["structures"]
        self.assertEqual(lea["fields"][0]["offset"], 12)
        read_write, = self.functions["read_write"]["structures"]
        self.assertTrue(read_write["fields"][0]["read"] and read_write["fields"][0]["write"])
        pointer, = self.functions["stack_pointer"]["structures"]
        self.assertIsNone(pointer["entry_register"])
        self.assertIsNone(pointer["source_field_origin"])
        self.assertEqual(pointer["fields"][0]["offset"], 8)

    def test_joins_dynamic_segments_stack_and_narrowed_values_stay_conservative(self):
        joined, = self.functions["join"]["structures"]
        self.assertEqual(joined["entry_register"], 1)
        for name in ("conflict", "indexed", "segment", "stack", "loop_changed", "narrow_root"):
            with self.subTest(name=name):
                self.assertEqual(self.functions[name]["structures"], [])
                self.assertTrue(self.functions[name]["unrecovered_accesses"])
        # Equal ECX usage in different functions is not a shared class identity.
        self.assertNotEqual(self.functions["fields"]["structures"][0]["origin"], joined["origin"])

    def test_compiled_views_preserve_complete_bounded_state_and_ordered_memory_traces(self):
        if not shutil.which("clang++"):
            self.skipTest("requires clang++")
        directory = self.root / "compiled"
        directory.mkdir()
        (directory / "runtime.hpp").write_text(self.typed["runtime"])
        header = '#pragma once\n#include "runtime.hpp"\n'
        sources = []
        for result, namespace in ((self.typed, "recomp_generated"), (self.raw, "baseline_generated")):
            header += f"namespace {namespace} {{\n"
            for function in result["functions"]:
                header += f"sharp_retro::Exit {function['name']}(sharp_retro::State&,sharp_retro::Memory&,std::uint64_t);\n"
                path = directory / (namespace + function["name"] + ".cpp")
                path.write_text(function["source"].replace("recomp_generated", namespace))
                sources.append(path)
            header += "}\n"
        (directory / "functions.hpp").write_text(header)
        rows = ",\n".join(f"{{0x{0x400000+rva:x},recomp_generated::fn_{rva:08x},baseline_generated::fn_{rva:08x}}}"
                           for rva in self.rvas.values())
        driver = r'''
#include "functions.hpp"
#include <array>
#include <map>
#include <string>
#include <vector>
using sharp_retro::bits;
struct Effect { bool write; std::uint64_t address; unsigned width; bits value; bool operator==(const Effect&) const = default; };
struct Arena : sharp_retro::Memory {
 std::map<std::uint64_t,std::uint8_t> bytes;
 std::vector<Effect> effects;
 std::uint8_t byte(std::uint64_t address) { return bytes.contains(address) ? bytes.at(address) : std::uint8_t(address*37+13); }
 bits load(std::uint64_t address,unsigned width) override {
  bits value=0; for(unsigned i=0;i<width/8;i++) value|=bits(byte(address+i))<<(i*8);
  effects.push_back({false,address,width,value}); return value;
 }
 void store(std::uint64_t address,bits value,unsigned width) override {
  effects.push_back({true,address,width,value});
  for(unsigned i=0;i<width/8;i++) bytes[address+i]=std::uint8_t(value>>(i*8));
 }
};
using Function=sharp_retro::Exit(*)(sharp_retro::State&,sharp_retro::Memory&,std::uint64_t);
struct Fixture { std::uint64_t entry; Function typed,raw; };
Fixture fixtures[] = { ROWS };
bool equal(const sharp_retro::State& a,const sharp_retro::State& b) {
 if(a.pc!=b.pc || a.flags!=b.flags || a.defined_flags!=b.defined_flags) return false;
 for(int i=0;i<16;i++) if(a.gpr[i]!=b.gpr[i]) return false;
 for(int i=0;i<6;i++) if(a.segments[i]!=b.segments[i]) return false;
 return true;
}
int execute(Function function,sharp_retro::State& state,Arena& memory,unsigned budget,std::string& error) {
 try { return int(function(state,memory,budget)); }
 catch(const std::exception& exception) { error=exception.what(); return -1; }
}
int main() {
 std::uint32_t bases[]={0,1,0x100001,0xfffffff0,0xffffffff};
 for(auto fixture:fixtures) for(auto base:bases) for(unsigned budget=0;budget<=24;budget++) {
  sharp_retro::State a;
  for(unsigned i=0;i<16;i++) a.gpr[i]=0xaabbccdd00000000ULL+base+i*19;
  a.pc=fixture.entry; a.gpr[1]=0xaabbccdd00000000ULL+base; a.gpr[2]=2; a.gpr[4]=0x100000;
  if(fixture.entry==ALIAS) a.gpr[2]=std::uint32_t(base-4);
  a.segments[2]=0x200000000ULL; a.segments[4]=0x300000000ULL;
  auto b=a; Arena left,right;
  left.store(a.segments[2]+a.gpr[4],0xcafebabe,32); left.effects.clear(); right=left;
  std::string le,re;
  auto lo=execute(fixture.typed,a,left,budget,le),ro=execute(fixture.raw,b,right,budget,re);
  if(lo!=ro || le!=re || !equal(a,b) || left.bytes!=right.bytes || left.effects!=right.effects) return 1;
  // Resume at each interrupted PC with live registers, not entry snapshots.
  for(unsigned step=0;step<24 && lo==int(sharp_retro::Exit::budget_exhausted);step++) {
   lo=execute(fixture.typed,a,left,1,le); ro=execute(fixture.raw,b,right,1,re);
   if(lo!=ro || le!=re || !equal(a,b) || left.bytes!=right.bytes || left.effects!=right.effects) return 2;
  }
 }
}
'''.replace("ROWS", rows).replace("ALIAS", f"0x{0x400000+self.rvas['alias']:x}ULL")
        (directory / "driver.cpp").write_text(driver)
        executable = directory / "driver"
        result = subprocess.run(["clang++", "-std=c++20", "-O2", "-fstrict-aliasing",
                                 "-fsanitize=address,undefined", "-fno-sanitize-recover=all", "-I", str(directory),
                                 str(directory / "driver.cpp"), *map(str, sources), "-o", str(executable)],
                                capture_output=True, text=True, timeout=90)
        self.assertEqual(result.returncode, 0, result.stderr)
        run = subprocess.run([str(executable)], capture_output=True, text=True, timeout=30)
        self.assertEqual(run.returncode, 0, run.stderr)
        # Change one recovered field's actual accessor displacement. Its inverse
        # address materialization remains fixed, so the trace oracle must notice.
        target = directory / f"recomp_generatedfn_{self.rvas['read_write']:08x}.cpp"
        needle = "field_00000008_u32_offset = 0x00000008u;"
        self.assertEqual(target.read_text().count(needle), 1)
        target.write_text(target.read_text().replace(needle, "field_00000008_u32_offset = 0x0000000cu;"))
        rebuilt = subprocess.run(["clang++", "-std=c++20", "-O2", "-I", str(directory),
                                  str(directory / "driver.cpp"), *map(str, sources), "-o", str(executable)],
                                 capture_output=True, text=True, timeout=90)
        self.assertEqual(rebuilt.returncode, 0, rebuilt.stderr)
        # Exit 1 reports a direct trace/state disagreement; exit 2 reports one
        # after single-instruction resumption. Crashes/other errors do not count.
        self.assertIn(subprocess.run([str(executable)], timeout=30).returncode, (1, 2))

    def test_structure_and_field_names_persist_and_bad_edits_are_atomic(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            initial = recomp.json.loads(recomp.json.dumps(self.state))
            initial["functions"] = [f for f in initial["functions"] if f["rva"] == self.rvas["fields"]]
            recomp.atomic_json(project / "project.json", initial)
            first = recomp.generate(project)
            structure = self.functions["fields"]["structures"][0]
            recomp.annotate_structure(project, first["view"], self.rvas["fields"], structure["name"], "ObservedRecord")
            second = recomp.generate(project, dispatch=True)
            recomp.annotate_structure(project, second["view"], self.rvas["fields"], "ObservedRecord", "flags",
                                      structure["fields"][0]["name"], "u32")
            final = recomp.generate(project)
            directory, manifest = recomp.read_view(project, final["view"])
            renamed = manifest["functions"][0]["structures"][0]
            self.assertEqual(renamed["origin"], structure["origin"])
            self.assertEqual((renamed["name"], renamed["fields"][0]["name"]), ("ObservedRecord", "flags"))
            source = (directory / f"fn_{self.rvas['fields']:08x}.cpp").read_text()
            self.assertIn("struct view_ObservedRecord", source)
            self.assertIn(".read_flags()", source)
            before = (project / "project.json").read_bytes()
            for name, field, kind in (("return", None, None), ("bad;name", None, None),
                                      (None, "flags", "u16"), (None, "missing", "u32")):
                with self.assertRaises((ValueError, StopIteration)):
                    recomp.annotate_structure(project, final["view"], self.rvas["fields"], "ObservedRecord", name, field, kind)
                self.assertEqual((project / "project.json").read_bytes(), before)
            # The raw baseline still reports/validates structure annotations.
            raw = recomp.generate(project, raw_memory=True)
            directory, manifest = recomp.read_view(project, raw["view"])
            self.assertEqual(manifest["functions"][0]["structures"][0]["name"], "ObservedRecord")
            self.assertNotIn("struct view_ObservedRecord", (directory / f"fn_{self.rvas['fields']:08x}.cpp").read_text())


if __name__ == "__main__":
    unittest.main()

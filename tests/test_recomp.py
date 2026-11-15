"""Synthetic controller/provenance tests; not evidence of game equivalence."""
import contextlib
import io
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest
from tools import recomp


def pe32(code):
    data = bytearray(0x200 + len(code))
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 0x3c, 0x80)
    data[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<HHIIIHH", data, 0x84, 0x14c, 1, 0, 0, 0, 0xe0, 2)
    struct.pack_into("<H", data, 0x98, 0x10b)
    struct.pack_into("<I", data, 0x98 + 28, 0x400000)
    section = 0x98 + 0xe0
    struct.pack_into("<8sIIII", data, section, b".text", len(code), 0x1000, len(code), 0x200)
    struct.pack_into("<I", data, section + 36, 0x60000020)
    data[0x200:] = code
    return data


class RecompTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("dotnet") or not (recomp.ROOT.parent / "SharpRetro/Decompiler/CppVariableOrigins.cs").exists():
            raise unittest.SkipTest("requires the local SharpRetro provenance API and .NET 10")

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.project = self.root / "project"
        self.binary = self.root / "fixture.exe"
        # Two call-free functions using 32-bit wraparound and actual RET.
        self.binary.write_bytes(pe32(bytes.fromhex("8b44240483c001c3" "8b442404d1e8c3")))
        self.command("new", str(self.binary))
        self.command("add", "--rva", "0x1000", "--size", "8")
        self.command("add", "--rva", "0x1008", "--size", "7")

    def command(self, *args, expected=0):
        output, error = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            status = recomp.main(["--project", str(self.project), *args])
        self.assertEqual(status, expected, error.getvalue())
        return recomp.json.loads(output.getvalue()) if status == 0 else error.getvalue()

    def test_annotation_survives_emission_change_and_units_link(self):
        first = self.command("generate")
        directory, manifest = recomp.read_view(self.project, first["view"])
        function = manifest["functions"][0]
        variable = next(v for v in function["variables"] if v["width"] == 32)
        origin = variable["origin"]
        self.command("annotate", "--view", first["view"], "--rva", "0x1000",
                     "--variable", variable["name"], "--name", "input_word", "--type", "u32")
        second = self.command("generate", "--dispatch")
        directory, manifest = recomp.read_view(self.project, second["view"])
        rebound = next(v for v in manifest["functions"][0]["variables"] if v["origin"] == origin)
        self.assertEqual((rebound["name"], rebound["type"]), ("input_word", "u32"))
        self.assertIn("std::uint32_t input_word;", (directory / "fn_00001000.cpp").read_text())
        if not shutil.which("clang++"):
            self.skipTest("source checks passed; linked execution requires clang++")
        driver = self.root / "driver.cpp"
        driver.write_text('''#include "functions.hpp"
struct Memory : sharp_retro::Memory {
 sharp_retro::bits load(std::uint64_t a,unsigned w) override {
  if(w!=32) throw std::runtime_error("width");
  if(a==0x100) return 0x1234;
  if(a==0x104) return 0xffffffff;
  throw std::runtime_error("address");
 }
 void store(std::uint64_t,sharp_retro::bits,unsigned) override { throw std::runtime_error("write"); }
};
int main() {
 Memory m; sharp_retro::State a,b;
 a.pc=0x401000; a.gpr[4]=0x100; b=a; b.pc=0x401008;
 if(recomp_generated::fn_00001000(a,m,100)!=sharp_retro::Exit::returned || a.gpr[0]!=0 || a.gpr[4]!=0x104 || a.pc!=0x1234) return 1;
 if(recomp_generated::fn_00001008(b,m,100)!=sharp_retro::Exit::returned || b.gpr[0]!=0x7fffffff) return 2;
 a.pc=0x401000;
 if(recomp_generated::fn_00001000(a,m,0)!=sharp_retro::Exit::budget_exhausted) return 3;
 // Guest vtable entries remain 32-bit address tokens, never host function pointers.
 std::uint32_t vtable[]={0x401000,0x401008};
 if(recomp_generated::resolve_guest(vtable[1])!=recomp_generated::fn_00001008) return 4;
 a={}; a.gpr[4]=0x100;
 if(recomp_generated::invoke_guest(vtable[0],a,m,100)!=sharp_retro::Exit::returned || a.gpr[0]!=0) return 5;
 auto before=a.pc;
 try { recomp_generated::invoke_guest(0x401fff,a,m,100); return 6; }
 catch(const std::runtime_error&) { if(a.pc!=before) return 7; }
}
''')
        executable = self.root / "driver"
        compiled = subprocess.run(["clang++", "-std=c++20", "-O2", "-fsanitize=address,undefined",
                                   "-fno-sanitize-recover=all", "-I", str(directory), str(driver),
                                   *map(str, directory.glob("*.cpp")), "-o", str(executable)],
                                  capture_output=True, text=True, timeout=60)
        self.assertEqual(compiled.returncode, 0, compiled.stderr)
        executed = subprocess.run([str(executable)], capture_output=True, text=True, timeout=10)
        self.assertEqual(executed.returncode, 0, executed.stderr)

    def test_bad_edits_are_atomic_and_stale_views_refuse(self):
        generated = self.command("generate")
        _, manifest = recomp.read_view(self.project, generated["view"])
        variable = manifest["functions"][0]["variables"][0]
        before = (self.project / "project.json").read_bytes()
        for arguments in (("--name", "return"), ("--name", "s"), ("--name", "x;bad"),
                          ("--type", "bool")):
            self.command("annotate", "--view", generated["view"], "--rva", "0x1000",
                         "--variable", variable["name"], *arguments, expected=1)
            self.assertEqual(before, (self.project / "project.json").read_bytes())
        self.command("annotate", "--view", generated["view"], "--rva", "0x1000",
                     "--variable", variable["name"], "--name", "saved_word")
        error = self.command("annotate", "--view", generated["view"], "--rva", "0x1000",
                             "--variable", variable["name"], "--name", "later_word", expected=1)
        self.assertIn("stale view", error)

    def test_reviewed_indirect_entries_preserve_bounds_and_unknown_origins(self):
        # JMP EAX cannot statically discover this second code island. Its ECX
        # input has no incoming affine fact from the primary function entry.
        image=pe32(bytes.fromhex("ffe0")+bytes(14)+bytes.fromhex("8b01c3"))
        binary=self.root / "indirect.exe"; binary.write_bytes(image)
        function=dict(rva=0x1000,size=19,ranges=[dict(rva=0x1000,size=2),dict(rva=0x1010,size=3)],
                      extra_entries=[0x1010],annotations={})
        state=dict(recomp.state(self.project),binary=str(binary),binary_sha256=recomp.digest(image),functions=[function])
        result=recomp.export(state)
        recovered=result["functions"][0]
        self.assertEqual([i["rva"] for i in recovered["instructions"]],[0x1000,0x1010,0x1012])
        self.assertEqual(recovered["structures"],[])
        self.assertTrue(any(a["instruction_rva"]==0x1010 for a in recovered["unrecovered_accesses"]))
        for entries,message in (([0x1008],"outside selected"),([0x1010,0x1011],"Overlapping")):
            function["extra_entries"]=entries
            with self.assertRaisesRegex(ValueError,message): recomp.export(state)

    def test_tampered_views_and_changed_binary_refuse(self):
        generated = self.command("generate")
        directory, _ = recomp.read_view(self.project, generated["view"])
        (directory / "fn_00001000.cpp").write_text("changed")
        with self.assertRaisesRegex(ValueError, "view changed"):
            recomp.read_view(self.project, generated["view"])
        with self.binary.open("ab") as stream:
            stream.write(b"changed")
        self.assertIn("hash changed", self.command("generate", expected=1))

    def test_unmatched_origins_and_untranslated_boundaries_refuse(self):
        original = recomp.state(self.project)
        original["functions"][0]["annotations"]["missing-origin"] = {"name": "missing", "type": None}
        with self.assertRaisesRegex(ValueError, "Unmatched variable"):
            recomp.export(original)
        original["functions"][0]["annotations"] = {}
        original["functions"][0]["size"] = 7  # RET excluded from selected range.
        with self.assertRaisesRegex(ValueError, "untranslated boundary"):
            recomp.export(original)

    def test_duplicate_names_refuse(self):
        generated = self.command("generate")
        _, manifest = recomp.read_view(self.project, generated["view"])
        variables = manifest["functions"][0]["variables"]
        self.command("annotate", "--view", generated["view"], "--rva", "0x1000",
                     "--variable", variables[0]["name"], "--name", variables[1]["name"], expected=1)


if __name__ == "__main__":
    unittest.main()

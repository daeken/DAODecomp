"""Call/ABI/import transport tests on constructed PE32, not game validation."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from tools import recomp
from recompiler.experiments.call_fixture import make_fixture,BASE,IAT,STOP


class Pe32CallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("dotnet") or not (recomp.ROOT.parent / "SharpRetro/Decompiler/Pe32AbiFacts.cs").exists():
            raise unittest.SkipTest("requires SharpRetro PE32 call/ABI support")
        cls.temporary=tempfile.TemporaryDirectory(); cls.addClassCleanup(cls.temporary.cleanup)
        cls.root=Path(cls.temporary.name); cls.binary=cls.root / "calls.exe"
        image,cls.functions,_=make_fixture(); cls.binary.write_bytes(image)
        cls.project=cls.root / "project"
        cls.initial={"schema_version":1,"revision":0,"binary":str(cls.binary),"module":cls.binary.name,
                     "binary_sha256":recomp.digest(image),"image_base":BASE,
                     "sharp_retro":str(recomp.ROOT.parent / "SharpRetro"),"functions":list(cls.functions.values())}
        recomp.atomic_json(cls.project / "project.json",cls.initial)
        generated=recomp.generate(cls.project)
        cls.directory,cls.manifest=recomp.read_view(cls.project,generated["view"])

    def test_abi_observations_and_import_identity_do_not_guess_source_types(self):
        callee=next(f for f in self.manifest["functions"] if f["rva"]==self.functions["callee"]["rva"])
        self.assertEqual(callee["abi"]["callee_cleanup_bytes"],[0])
        reads={(a["offset"],a["width"]) for a in callee["abi"]["stack_accesses"] if not a["write"]}
        self.assertTrue({(4,32),(8,32)}<=reads)
        stdcall=next(f for f in self.manifest["functions"] if f["rva"]==self.functions["stdcall"]["rva"])
        self.assertEqual(stdcall["abi"]["callee_cleanup_bytes"],[8])
        self.assertIn("unknown",stdcall["abi"]["calling_convention"])
        imported=next(f for f in self.manifest["functions"] if f["rva"]==self.functions["import"]["rva"])
        self.assertEqual(imported["abi"]["transfers"][0]["import_slot"],IAT)
        self.assertEqual(self.manifest["imports"][0]["symbol"],"MulDiv")
        self.assertEqual(self.manifest["imports"][0]["policy"],"native")
        self.assertEqual(self.manifest["module_policy"]["modules"]["umbra.dll"]["policy"],"translate")

    def test_compiled_calls_returns_recursion_live_iat_budget_and_unknowns(self):
        if not shutil.which("clang++"): self.skipTest("requires clang++")
        driver=self.root / "driver.cpp"
        driver.write_text(r'''
#include "functions.hpp"
#include <array>
#include <string>
struct Memory : sharp_retro::Memory {
 std::array<std::uint8_t,0x10000> bytes{};
 std::uint32_t target=0x402050;
 sharp_retro::bits load(std::uint64_t address,unsigned width) override {
  if(address==0x402050 && width==32) return target;
  if(address==0x403000 && width==32) return 0x401040;
  if(address>bytes.size() || width/8>bytes.size()-address) throw std::runtime_error("bounds");
  sharp_retro::bits value=0; for(unsigned i=0;i<width/8;i++) value|=sharp_retro::bits(bytes[address+i])<<(i*8); return value;
 }
 void store(std::uint64_t address,sharp_retro::bits value,unsigned width) override {
  if(address>bytes.size() || width/8>bytes.size()-address) throw std::runtime_error("bounds");
  for(unsigned i=0;i<width/8;i++) bytes[address+i]=std::uint8_t(value>>(i*8));
 }
};
void setup(sharp_retro::State& s,Memory& m,unsigned first=12) {
 s={}; s.gpr[1]=0x403000; s.gpr[4]=0x8000;
 s.gpr[3]=0x11223344; s.gpr[5]=0xaabbccdd; s.gpr[6]=0x778899aa; s.gpr[7]=0x55667788;
 m.store(0x8000,0x12345678,32); m.store(0x8004,first,32); m.store(0x8008,9,32);
}
unsigned import_calls=0;
void fixture_import(const recomp_generated::ImportEntry& import,sharp_retro::State& s,sharp_retro::Memory& m) {
 if(import.address!=0x402050 || std::string(import.symbol)!="MulDiv") throw std::runtime_error("unexpected import");
 auto sp=unsigned(s.gpr[4]); auto a=unsigned(m.load(sp+4,32)),b=unsigned(m.load(sp+8,32)),d=unsigned(m.load(sp+12,32));
 if(a!=12 || b!=9 || d!=3) throw std::runtime_error("wrong stack arguments");
 ++import_calls; s.pc=unsigned(m.load(sp,32)); s.gpr[4]=sp+16; s.gpr[0]=36;
 s.defined_gpr&=~((1u<<1)|(1u<<2)); s.defined_flags=0;
}
int main() {
 using sharp_retro::Exit;
 for(auto entry:{0x401000u,0x401080u,0x4010a0u,0x4010c0u}) {
  Memory m; sharp_retro::State s; setup(s,m); std::uint64_t budget=100;
  if(recomp_generated::execute_guest(entry,0x12345678,s,m,budget)!=Exit::returned || s.gpr[0]!=21 || s.gpr[4]!=0x8004) return 1;
  if(s.gpr[3]!=0x11223344 || s.gpr[5]!=0xaabbccdd || s.gpr[6]!=0x778899aa || s.gpr[7]!=0x55667788) return 2;
 }
 { Memory m; sharp_retro::State s; setup(s,m); std::uint64_t budget=3;
  if(recomp_generated::execute_guest(0x401000,0x12345678,s,m,budget)!=Exit::budget_exhausted || s.pc!=0x401040 || budget!=0) return 3;
  budget=5; if(recomp_generated::resume_guest(0x12345678,s,m,budget)!=Exit::returned || budget!=0 || s.gpr[0]!=21) return 4;
 }
 { Memory m; sharp_retro::State s; setup(s,m,6); std::uint64_t budget=200;
  if(recomp_generated::execute_guest(0x4010e0,0x12345678,s,m,budget)!=Exit::returned || s.gpr[0]!=6 || s.gpr[4]!=0x8004) return 5;
 }
 for(auto entry:{0x401160u,0x4011a0u}) {
  Memory m; sharp_retro::State s; setup(s,m); std::uint64_t budget=100;
  if(recomp_generated::execute_guest(entry,0x12345678,s,m,budget,fixture_import)!=Exit::returned || s.gpr[0]!=36 || s.gpr[4]!=0x8004) return 6;
 }
 if(import_calls!=2) return 7;
 { Memory m; sharp_retro::State s; setup(s,m); m.target=0x4011e0; std::uint64_t budget=100;
  if(recomp_generated::execute_guest(0x401160,0x12345678,s,m,budget,fixture_import)!=Exit::returned || s.gpr[0]!=24 || import_calls!=2) return 8;
 }
 for(auto entry:{0x401120u,0x401140u,0x4011c0u}) {
  Memory m; sharp_retro::State s; setup(s,m); std::uint64_t budget=100; bool failed=false;
  try {
   (void)recomp_generated::execute_guest(entry,0x12345678,s,m,budget,fixture_import);
   // Copies can retain unknown bits; a full return-value observation cannot.
   (void)sharp_retro::read_gpr(s,0);
  }
  catch(const std::runtime_error&) { failed=true; }
  if(!failed) return 9;
 }
 { Memory m; sharp_retro::State s; setup(s,m); m.target=0xdeadc0de; std::uint64_t budget=100; bool failed=false;
  try { (void)recomp_generated::execute_guest(0x401160,0x12345678,s,m,budget,fixture_import); }
  catch(const std::runtime_error&) { failed=true; } if(!failed) return 10;
 }
 // A missing-code pause consumes no guest units and retains the exact stack.
 // A supplied step resumes in place. Claiming a load without supplying its PC fails.
 { Memory m; sharp_retro::State s; setup(s,m); std::uint64_t budget=100;
  recomp_generated::missing_guest_code=[](std::uint32_t pc) { return pc==0xdeadc0de; };
  bool failed=false;
  try { (void)recomp_generated::execute_guest(0x401120,0x12345678,s,m,budget); }
  catch(const std::runtime_error& e) { failed=std::string(e.what())=="candidate did not supply missing PC"; }
  if(!failed || s.pc!=0xdeadc0de || budget!=98 || s.gpr[4]!=0x7ffc || m.load(0x7ffc,32)!=0x401127) return 11;
  recomp_generated::missing_guest_code=[](std::uint32_t pc) {
   if(pc!=0xdeadc0de) return false;
   recomp_generated::extra_guest_step=[](std::uint32_t address)->recomp_generated::GuestStep {
    if(address!=0xdeadc0de) return nullptr;
    return +[](sharp_retro::State& s,sharp_retro::Memory& m,std::uint64_t& budget) {
     if(!budget) return Exit::budget_exhausted;
     --budget; s.gpr[0]=42; s.pc=m.load(s.gpr[4],32); s.gpr[4]+=4; return Exit::returned;
    };
   }; return true;
  };
  if(recomp_generated::resume_guest(0x12345678,s,m,budget)!=Exit::returned || budget!=96 || s.gpr[0]!=42 || s.gpr[4]!=0x8004) return 12;
  recomp_generated::missing_guest_code=nullptr; recomp_generated::extra_guest_step=nullptr;
  // Removing a dynamic candidate must not leave its old function cached.
  setup(s,m); budget=100; failed=false;
  try { (void)recomp_generated::execute_guest(0x401120,0x12345678,s,m,budget); }
  catch(const std::runtime_error& e) { failed=std::string(e.what())=="untranslated guest code/import target"; }
  if(!failed || s.pc!=0xdeadc0de || budget!=98 || s.gpr[4]!=0x7ffc) return 13;
 }
}
''')
        executable=self.root / "driver"
        built=subprocess.run(["clang++","-std=c++20","-O2","-fsanitize=address,undefined","-fno-sanitize-recover=all",
                              "-I",str(self.directory),str(driver),*map(str,self.directory.glob("*.cpp")),"-o",str(executable)],
                             capture_output=True,text=True,timeout=90)
        self.assertEqual(built.returncode,0,built.stderr)
        result=subprocess.run([str(executable)],capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_umbra_native_fallback_is_forbidden_by_policy(self):
        with tempfile.TemporaryDirectory() as temporary:
            project=Path(temporary); binary=project / "umbra-import.exe"; image,functions,_=make_fixture("umbra.dll","test_symbol")
            binary.write_bytes(image)
            state=dict(self.initial,binary=str(binary),module=binary.name,binary_sha256=recomp.digest(image),functions=[functions["import"]])
            result=recomp.export(state)
            self.assertEqual(result["imports"][0]["policy"],"translate")
            self.assertIn("unknown",result["imports"][0]["contract"])
            if not shutil.which("clang++"):
                self.skipTest("policy metadata passed; runtime guard requires clang++")
            recomp.atomic_json(project / "project.json",state)
            generated=recomp.generate(project)
            directory,_=recomp.read_view(project,generated["view"])
            driver=project / "policy.cpp"
            driver.write_text(r'''
#include "functions.hpp"
#include <map>
#include <string>
struct Memory : sharp_retro::Memory {
 std::map<std::uint64_t,sharp_retro::bits> words{{0x402050,0x402050},{0x8000,0x12345678},{0x8004,12},{0x8008,9}};
 sharp_retro::bits load(std::uint64_t a,unsigned w) override { if(w!=32) throw std::runtime_error("width"); return words.at(a); }
 void store(std::uint64_t a,sharp_retro::bits v,unsigned w) override { if(w!=32) throw std::runtime_error("width"); words[a]=v; }
};
bool called=false;
void forbidden(const recomp_generated::ImportEntry&,sharp_retro::State&,sharp_retro::Memory&) { called=true; }
int main() {
 Memory m; sharp_retro::State s; s.gpr[4]=0x8000; std::uint64_t budget=100;
 try { (void)recomp_generated::execute_guest(0x401160,0x12345678,s,m,budget,forbidden); return 1; }
 catch(const std::runtime_error& e) { return !called && std::string(e.what()).find("translated module")!=std::string::npos ? 0 : 2; }
}
''')
            executable=project / "policy"
            built=subprocess.run(["clang++","-std=c++20","-O2","-I",str(directory),str(driver),
                                  *map(str,directory.glob("*.cpp")),"-o",str(executable)],capture_output=True,text=True,timeout=60)
            self.assertEqual(built.returncode,0,built.stderr)
            self.assertEqual(subprocess.run([str(executable)],timeout=10).returncode,0)


if __name__=="__main__": unittest.main()

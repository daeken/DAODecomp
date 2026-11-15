"""Bounded direct-call discovery on constructed PE32, not game validation."""
import copy
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest
from unittest import mock
from tools import recomp
from tools.recomp_reachability import expand_direct_calls, inventory_selection
from recompiler.experiments.call_fixture import make_fixture


class DirectCallDiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("dotnet") or not (recomp.ROOT.parent / "SharpRetro/Decompiler/Pe32AbiFacts.cs").exists():
            raise unittest.SkipTest("requires SharpRetro PE32 call facts")

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(); self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name); self.binary = self.root / "graph.exe"
        image = bytearray(make_fixture()[0])
        call = lambda at, target: b"\xe8" + struct.pack("<i", target - at - 5)
        codes = {0x1000: call(0x1000, 0x1040) + call(0x1005, 0x1080) + b"\xc3",
                 0x1040: call(0x1040, 0x10c0) + b"\xc3", 0x1080: b"\x90" * 7 + b"\xc3",
                 0x1084: b"\xc3", 0x10c0: bytes.fromhex("b82a000000c3")}
        for rva, code in codes.items(): image[0x200 + rva - 0x1000:0x200 + rva - 0x1000 + len(code)] = code
        self.binary.write_bytes(image); sha = recomp.digest(image)
        self.project = self.root / "project"
        self.state = dict(schema_version=1, revision=0, binary=str(self.binary), module=self.binary.name,
                          binary_sha256=sha, image_base=0x400000, sharp_retro=str(recomp.ROOT.parent / "SharpRetro"), functions=[])
        recomp.atomic_json(self.project / "project.json", self.state)
        self.inventory = self.root / "inventory.json"
        recomp.atomic_json(self.inventory, dict(module_sha256=sha, functions=[dict(rva=rva, name=f"synthetic_{rva:x}",
            body_ranges=[dict(start_rva=rva, end_rva_inclusive=rva + len(code) - 1)]) for rva, code in codes.items()]))
        self.seed = inventory_selection(self.state, self.inventory, 0x1000)
        self.plan = dict(roles=dict(main=dict(module=self.binary.name, binary_sha256=sha, functions=[self.seed])))

    def expand(self, **kwargs):
        return expand_direct_calls(self.plan, dict(main=self.project), dict(main=self.inventory),
                                   [dict(module="main", rva=0x1000)], **kwargs)

    def test_transitive_helpers_compile_but_ambiguous_target_remains_a_runtime_failure(self):
        report = self.expand(depth=2)
        self.assertEqual([a["rva"] for a in report["accepted"]], [0x1040, 0x10c0])
        self.assertEqual([a["target_rva"] for a in report["deferred"]], [0x1080])
        self.assertIn("another function entry", report["deferred"][0]["reason"])
        self.assertFalse(report["truncated"])
        functions = self.plan["roles"]["main"]["functions"]
        self.assertTrue(all("execution unobserved" in f["contract_status"] for f in functions))
        self.assertEqual(self.state, recomp.state(self.project))  # Expansion never edits source-project annotations.
        recomp.atomic_json(self.project / "project.json", dict(self.state, functions=[dict(f, annotations={}) for f in functions]))
        generated = recomp.generate(self.project); view, manifest = recomp.read_view(self.project, generated["view"])
        self.assertNotIn(0x1080, {i["rva"] for f in manifest["functions"] for i in f["instructions"]})
        if not shutil.which("clang++"): self.skipTest("requires Clang for runtime failure check")
        driver = self.root / "driver.cpp"
        driver.write_text(r'''
#include "functions.hpp"
#include "image_memory.hpp"
int main() {
 recomp_generated::ImageMemory memory; memory.map_bytes("stack",0x8000,4096,true,true); memory.seal();
 memory.store(0x8800,0x12345678,32); sharp_retro::State state; state.gpr[4]=0x8800; std::uint64_t budget=100;
 try { recomp_generated::execute_guest(0x401000,0x12345678,state,memory,budget); return 1; }
 catch(const std::runtime_error&) {
  for(const auto& entry:recomp_generated::compiled_functions()) if(entry.address==0x401080) return 3;
  return state.pc==0x401080 && state.gpr[0]==42 && state.gpr[4]==0x87fc ? 0 : 2;
 }
}
''')
        executable = self.root / "driver"
        build = subprocess.run(["clang++", "-std=c++20", "-O2", "-fsanitize=address,undefined", "-fno-sanitize-recover=all",
                                "-I", str(view), "-I", str(recomp.RUNTIME), str(driver),
                                *map(str, view.glob("*.cpp")), "-o", str(executable)], capture_output=True, text=True, timeout=90)
        self.assertEqual(build.returncode, 0, build.stderr)
        run = subprocess.run([str(executable)], capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 0, run.stderr)

    def test_budget_and_disabled_discovery_do_not_claim_missing_targets(self):
        before = copy.deepcopy(self.plan)
        with mock.patch.object(recomp, "export", side_effect=AssertionError("disabled discovery must not lift")):
            report = self.expand(depth=0)
        self.assertEqual(report["accepted"], []); self.assertEqual(self.plan, before)
        report = self.expand(depth=2, limit=1)
        self.assertTrue(report["truncated"])
        self.assertEqual([a["rva"] for a in report["accepted"]], [0x1040])
        self.assertNotIn(0x10c0, [f["rva"] for f in self.plan["roles"]["main"]["functions"]])

    def test_optional_lift_failure_is_deferred_but_seed_or_backend_failure_is_atomic(self):
        original = recomp.export; before = copy.deepcopy(self.plan)
        def fail_optional(state, *args, **kwargs):
            if state["functions"][0]["rva"] == 0x1040: raise ValueError("synthetic unsupported helper")
            return original(state, *args, **kwargs)
        with mock.patch.object(recomp, "export", side_effect=fail_optional): report = self.expand()
        self.assertEqual(report["accepted"], [])
        self.assertEqual({d["target_rva"] for d in report["deferred"]}, {0x1040, 0x1080})
        self.assertEqual(self.plan, before)
        with mock.patch.object(recomp, "export", side_effect=ValueError("required reached seed failed")):
            with self.assertRaisesRegex(ValueError, "required reached seed"): self.expand()
        self.assertEqual(self.plan, before)
        def changed_backend(state, *args, **kwargs):
            result = original(state, *args, **kwargs)
            if state["functions"][0]["rva"] == 0x1040: result["backend_artifacts"] = {"changed": "0" * 64}
            return result
        with mock.patch.object(recomp, "export", side_effect=changed_backend):
            with self.assertRaisesRegex(RuntimeError, "backend changed"): self.expand()
        self.assertEqual(self.plan, before)

    def test_selected_static_seeds_share_one_strict_export(self):
        self.plan["roles"]["main"]["functions"].append(inventory_selection(self.state, self.inventory, 0x1040))
        original = recomp.export; requests = []
        def record(state, *args, **kwargs):
            requests.append(tuple(f["rva"] for f in state["functions"]))
            return original(state, *args, **kwargs)
        with mock.patch.object(recomp, "export", side_effect=record):
            report = expand_direct_calls(self.plan, dict(main=self.project), dict(main=self.inventory),
                [dict(module="main", rva=0x1000), dict(module="main", rva=0x1040)], depth=1)
        self.assertEqual(requests[0], (0x1000, 0x1040))
        self.assertEqual([f["rva"] for f in report["accepted"]], [0x10c0])
        self.assertEqual([f["target_rva"] for f in report["deferred"]], [0x1080])

    def test_selected_intermediate_does_not_hide_its_missing_callee(self):
        self.plan["roles"]["main"]["functions"].append(inventory_selection(self.state,self.inventory,0x1040))
        report=self.expand(depth=2)
        self.assertEqual([f["rva"] for f in report["accepted"]],[0x10c0])
        self.assertEqual([f["target_rva"] for f in report["deferred"]],[0x1080])
        self.assertEqual({f["rva"] for f in self.plan["roles"]["main"]["functions"]},{0x1000,0x1040,0x10c0})

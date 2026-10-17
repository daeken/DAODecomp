import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools.daodecomp.memory import ARENA_BASE
from validation import linked_structure_cases as graph_cases
from validation import linked_structure_runner as runner

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_linked_structures", ROOT / "validation/validate_linked_structures.py")
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def write_u32(arena, offset, value):
    arena[offset:offset + 4] = value.to_bytes(4, "little")


class LinkedStructureCaseTests(unittest.TestCase):
    def test_deterministic_counts_layouts_and_full_corpus_validation(self):
        for name, public_count in (("fn_00018390", 256), ("fn_000183d0", 260)):
            public = graph_cases.cases(name, "public")
            heldout = graph_cases.cases(name, "heldout")
            self.assertEqual((len(public), len(heldout)), (public_count, 128))
            self.assertEqual(public, graph_cases.cases(name, "public"))
            self.assertEqual(heldout, graph_cases.cases(name, "heldout"))
            self.assertFalse({case["id"] for case in public} & {case["id"] for case in heldout})
            for case in public + heldout:
                graph_cases.fixture(name, case["inputs"])
        self.assertEqual(len(set(graph_cases.LAYOUTS)), 4)
        self.assertTrue(any(list_offset == 0 for list_offset, _ in graph_cases.LAYOUTS))
        self.assertTrue(any(list_offset == 480 for list_offset, _ in graph_cases.LAYOUTS))
        self.assertTrue(any(500 in nodes for _, nodes in graph_cases.LAYOUTS))
        self.assertTrue(any(nodes[0] > nodes[1] for _, nodes in graph_cases.LAYOUTS))

    def test_pointer_zero_is_a_member_not_null_and_pool_order_is_preserved(self):
        for name in graph_cases.FUNCTIONS:
            cases = graph_cases.cases(name, "public")
            case = next(item for item in cases if 0 in graph_cases.fixture(name, item["inputs"])[4])
            arena, _, _, chain, nodes = graph_cases.fixture(name, case["inputs"])
            self.assertIn(0, nodes)
            self.assertEqual(chain, [])
            self.assertEqual(len(arena), 512)
        # Public append enumerates each pool identity irrespective of numeric order.
        layouts = [case["inputs"]["nodes"] for case in graph_cases.cases("fn_000183d0")[:260]]
        self.assertTrue(any(layout.startswith("4f010000") for layout in layouts))

    def test_exact_branch_specific_read_and_write_footprints(self):
        append_cases = graph_cases.cases("fn_00018390", "public")
        empty = append_cases[0]["inputs"]
        _, reads, writes, chain, _ = graph_cases.fixture("fn_00018390", empty)
        self.assertEqual(chain, [])
        self.assertEqual(reads, [(empty["list"] + 0x1C, 4)])
        self.assertEqual(set(writes), {(empty["node"] + 8, 4), (empty["node"] + 4, 4),
                                       (empty["list"] + 0x18, 4), (empty["list"] + 0x1C, 4)})
        nonempty = next(case["inputs"] for case in append_cases
                        if graph_cases.fixture("fn_00018390", case["inputs"])[3])
        _, reads, writes, chain, _ = graph_cases.fixture("fn_00018390", nonempty)
        self.assertEqual(reads, [(nonempty["list"] + 0x1C, 4)])
        self.assertNotIn((nonempty["list"] + 0x18, 4), writes)
        self.assertIn((chain[-1] + 4, 4), writes)

        pop_cases = graph_cases.cases("fn_000183d0", "public")
        empty = pop_cases[0]["inputs"]
        _, reads, writes, _, _ = graph_cases.fixture("fn_000183d0", empty)
        self.assertEqual(reads, [(empty["list"] + 0x18, 4)])
        self.assertEqual(writes, [])
        singleton = next(case["inputs"] for case in pop_cases
                         if len(graph_cases.fixture("fn_000183d0", case["inputs"])[3]) == 1)
        _, reads, writes, chain, _ = graph_cases.fixture("fn_000183d0", singleton)
        self.assertEqual(set(reads), {(singleton["list"] + 0x18, 4), (chain[0] + 4, 4)})
        self.assertEqual(set(writes), {(singleton["list"] + 0x18, 4), (singleton["list"] + 0x1C, 4)})
        multiple = next(case["inputs"] for case in pop_cases
                        if len(graph_cases.fixture("fn_000183d0", case["inputs"])[3]) == 2)
        _, _, writes, chain, _ = graph_cases.fixture("fn_000183d0", multiple)
        self.assertEqual(set(writes), {(multiple["list"] + 0x18, 4), (chain[1] + 8, 4)})

    def test_invalid_types_layouts_and_graph_shapes_fail_closed(self):
        original = graph_cases.cases("fn_00018390")[0]["inputs"]
        bad_inputs = [
            {**original, "list": True}, {**original, "list": 481},
            {**original, "arena": "A" * 1024}, {**original, "extra": 1},
            {**original, "nodes": original["nodes"].upper()},
            {**original, "nodes": "00000000" * 4},
            {**original, "node": True}, {**original, "node": 4},
        ]
        for bad in bad_inputs:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                graph_cases.fixture("fn_00018390", bad)

        # Force list/node overlap, nonmember endpoint, broken reciprocity and a cycle.
        overlap = {**original, "list": 0}
        overlap["nodes"] = (0).to_bytes(4, "little").hex() + original["nodes"][8:]
        with self.assertRaises(ValueError):
            graph_cases.fixture("fn_00018390", overlap)
        nonmember = dict(original)
        broken_arena = bytearray.fromhex(nonmember["arena"])
        write_u32(broken_arena, nonmember["list"] + 0x18, ARENA_BASE + 500)
        write_u32(broken_arena, nonmember["list"] + 0x1C, ARENA_BASE + 500)
        nonmember["arena"] = broken_arena.hex()
        with self.assertRaises(ValueError):
            graph_cases.fixture("fn_00018390", nonmember)

        two = next(case["inputs"] for case in graph_cases.cases("fn_000183d0")
                   if len(graph_cases.fixture("fn_000183d0", case["inputs"])[3]) == 2)
        broken = dict(two)
        broken_arena = bytearray.fromhex(broken["arena"])
        _, _, _, chain, _ = graph_cases.fixture("fn_000183d0", two)
        write_u32(broken_arena, chain[1] + 8, 0)
        broken["arena"] = broken_arena.hex()
        with self.assertRaisesRegex(ValueError, "reciprocal"):
            graph_cases.fixture("fn_000183d0", broken)
        cycle = dict(two)
        cycle_arena = bytearray.fromhex(cycle["arena"])
        write_u32(cycle_arena, chain[1] + 4, ARENA_BASE + chain[0])
        cycle["arena"] = cycle_arena.hex()
        with self.assertRaises(ValueError):
            graph_cases.fixture("fn_000183d0", cycle)

    def test_negative_controls_are_full_public_corpora_for_both_functions(self):
        for name, expected in (("fn_00018390", 256), ("fn_000183d0", 260)):
            self.assertEqual(graph_cases.negative_cases(name), graph_cases.cases(name, "public"))
            self.assertEqual(len(graph_cases.negative_cases(name)), expected)


class LinkedStructureAdapterTests(unittest.TestCase):
    def test_original_dispatch_matches_raw_thiscall_stack_and_exact_footprints(self):
        function = {"name": "fn_00018390", "module_sha256": "a" * 64,
                    "rva": 0x18390, "size": 56, "code_sha256": "b" * 64}
        inputs = next(case["inputs"] for case in graph_cases.cases(function["name"])
                      if graph_cases.fixture(function["name"], case["inputs"])[3])
        captured = {}

        def execute(address, code, arena, **kwargs):
            captured.update(kwargs)
            return ARENA_BASE + inputs["node"], arena

        with patch.object(runner, "load_slice", return_value=(0x401000, b"code")), \
             patch.object(runner, "execute_memory", side_effect=execute):
            result, after = runner.dispatch_original(function, inputs, Path("reference.exe"))
        self.assertEqual(result, ARENA_BASE + inputs["node"])
        self.assertEqual(len(after), 512)
        self.assertEqual(captured["registers"], {"ecx": ARENA_BASE + inputs["list"]})
        self.assertEqual(captured["stack_arguments"], [ARENA_BASE + inputs["node"]])
        self.assertEqual(captured["stack_cleanup"], 4)
        self.assertEqual(captured["preserved_registers"], ("ecx",))
        self.assertEqual(captured["readable"], [(inputs["list"] + 0x1C, 4)])
        self.assertNotIn((inputs["list"] + 0x18, 4), captured["writable"])

    def test_pop_original_dispatch_uses_ret_zero_preserved_ecx_and_branch_footprints(self):
        function = {"name": "fn_000183d0", "module_sha256": "a" * 64,
                    "rva": 0x183d0, "size": 44, "code_sha256": "b" * 64}
        inputs = next(case["inputs"] for case in graph_cases.cases(function["name"])
                      if len(graph_cases.fixture(function["name"], case["inputs"])[3]) == 2)
        captured = {}
        chain = graph_cases.fixture(function["name"], inputs)[3]

        def execute(address, code, arena, **kwargs):
            captured.update(kwargs)
            return ARENA_BASE + chain[0], arena

        with patch.object(runner, "load_slice", return_value=(0x401000, b"code")), \
             patch.object(runner, "execute_memory", side_effect=execute):
            result, _ = runner.dispatch_original(function, inputs, Path("reference.exe"))
        self.assertEqual(result, ARENA_BASE + chain[0])
        self.assertEqual(captured["registers"], {"ecx": ARENA_BASE + inputs["list"]})
        self.assertEqual(captured["stack_arguments"], [])
        self.assertEqual(captured["stack_cleanup"], 0)
        self.assertEqual(captured["preserved_registers"], ("ecx",))
        self.assertEqual(captured["readable"], [(inputs["list"] + 0x18, 4), (chain[0] + 4, 4)])
        self.assertEqual(captured["writable"], [(inputs["list"] + 0x18, 4), (chain[1] + 8, 4)])

    def test_candidate_output_parser_rejects_incomplete_observations(self):
        inputs = graph_cases.cases("fn_000183d0")[0]["inputs"]
        for output in ("1\n00\n", "1\n" + "A" * 1024 + "\n",
                       "4294967296\n" + "00" * 512 + "\n"):
            with patch.object(runner.subprocess, "run", return_value=subprocess.CompletedProcess(
                    ["candidate"], 0, stdout=output, stderr="")):
                with self.assertRaises(RuntimeError):
                    runner.dispatch_candidate({"name": "fn_000183d0"}, inputs, Path("candidate"))


class LinkedStructureValidatorTests(unittest.TestCase):
    def test_negative_gate_compares_every_public_case_using_mutant(self):
        function = {"name": "fn_000183d0", "id": "id", "contract": "contracts/pop.json", "source": "src/pop.cpp"}
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            captured = {}

            def fake_compare(contract, cases, oracle, candidate, **kwargs):
                captured.update(cases=cases, candidate=candidate)
                rows = [{"case_id": case["id"], "status": "mismatch" if case["id"] == "public-0003" else "corpus_pass"}
                        for case in cases]
                return {"status": "failed", "cases": rows, "artifacts_unchanged": True,
                        "proof": False, "function_id": "id", "kind": "game", "repeats": 2,
                        "artifacts_sha256": {}}

            with patch.object(validator, "ROOT", root), patch.object(validator, "compare", side_effect=fake_compare), \
                 patch.object(validator, "load_json", return_value={"schema_version": 1, "function_id": "id"}), \
                 patch.object(validator, "version", return_value="test"):
                (root / "validation").mkdir()
                (root / "analysis").mkdir()
                (root / "contracts").mkdir()
                (root / "contracts/pop.json").write_text("{}")
                for rel in ("tools/daodecomp/harness.py", "tools/daodecomp/leaf.py", "tools/daodecomp/memory.py",
                            "tools/daodecomp/pe.py", "analysis/functions.json", "analysis/reference-build.json",
                            "CMakeLists.txt", "requirements-validation.txt", "src/pop.cpp"):
                    path = root / rel
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("placeholder")
                result = validator.validate_function(function, binary=root / "game.exe",
                    executable=root / "dao_linked_structure_mutant", build_dir=root, report_dir=root / "reports",
                    suite="public", expect_mismatch=True)
            self.assertTrue(result)
            self.assertEqual(captured["cases"], graph_cases.cases("fn_000183d0", "public"))
            self.assertIn("dao_linked_structure_mutant", captured["candidate"][-1])


@unittest.skipUnless((ROOT / "gamedata/bin_ship/DAOrigins.exe").is_file()
                     and importlib.util.find_spec("unicorn") is not None,
                     "pinned original binary or optional Unicorn runtime is not installed")
class LinkedStructureOriginalCompositionTests(unittest.TestCase):
    def test_original_reaches_all_heldout_append_drain_reappend_snapshots(self):
        binary = ROOT / "gamedata/bin_ship/DAOrigins.exe"
        registry = json.loads((ROOT / "analysis/functions.json").read_text())
        functions = {f["name"]: f for f in registry["functions"] if f.get("backend") == "linked-structures-001"}
        plan = graph_cases.composition_plan()
        self.assertEqual(len(plan), 24)
        for start in range(0, len(plan), 6):
            sequence = plan[start:start + 6]
            current = bytes.fromhex(sequence[0][1]["arena"])
            for name, inputs in sequence:
                self.assertEqual(inputs["arena"], current.hex(), "fixture is not the reached sequence pre-state")
                graph_cases.fixture(name, inputs)
                result, after = runner.dispatch_original(functions[name], inputs, binary)
                chain = graph_cases.fixture(name, inputs)[3]
                expected_return = (ARENA_BASE + inputs["node"] if name == "fn_00018390"
                                   else ARENA_BASE + chain[0] if chain else 0)
                self.assertEqual(result, expected_return)
                self.assertEqual(len(after), 512)
                current = after
            # Reappending the first removed node to the drained empty list yields
            # a singleton and retains every unrelated byte from the final state.
            final_name, final_inputs = sequence[-1]
            final_chain = graph_cases.active_chain(current, final_inputs["list"],
                                                  graph_cases._read_nodes(final_inputs["nodes"]))
            self.assertEqual(final_chain, [final_inputs["node"]])
        for name in graph_cases.FUNCTIONS:
            suite = graph_cases.cases(name, "heldout")
            sequence_inputs = graph_cases.composition_snapshots(name)
            self.assertTrue(all(any(case["inputs"] == inputs for case in suite) for inputs in sequence_inputs))


if __name__ == "__main__":
    unittest.main()

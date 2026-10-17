import unittest
import json
from pathlib import Path
import importlib.util

from tools.daodecomp.memory import ARENA_BASE, execute_memory
from validation.linked_structure_cases import cases, fixture, composition_snapshots, _inputs, _with_chain, _arena_seed, _model_step, LAYOUTS
from validation.linked_structure_runner import dispatch_original


class UnlinkDomainTests(unittest.TestCase):
    def test_public_and_heldout_cover_active_and_inactive_targets(self):
        public = cases("fn_00018400", "public")
        heldout = cases("fn_00018400", "heldout")
        self.assertEqual((len(public), len(heldout)), (1040, 128))
        relations = set()
        for case in public + heldout:
            _, _, _, chain, _ = fixture("fn_00018400", case["inputs"])
            relations.add((len(chain), case["inputs"]["node"] in chain))
        self.assertIn((0, False), relations)
        self.assertIn((1, True), relations)
        self.assertIn((4, True), relations)
        self.assertIn((3, False), relations)

    def test_invalid_graph_and_nonpool_target_fail_closed(self):
        inputs = cases("fn_00018400", "public")[0]["inputs"]
        with self.assertRaises(ValueError):
            fixture("fn_00018400", {**inputs, "node": True})
        with self.assertRaises(ValueError):
            fixture("fn_00018400", {**inputs, "node": 999})
        bad = dict(inputs)
        arena = bytearray.fromhex(inputs["arena"])
        arena[inputs["list"] + 0x18:inputs["list"] + 0x1c] = (ARENA_BASE + 500).to_bytes(4, "little")
        arena[inputs["list"] + 0x1c:inputs["list"] + 0x20] = (ARENA_BASE + 500).to_bytes(4, "little")
        bad["arena"] = arena.hex()
        with self.assertRaises(ValueError):
            fixture("fn_00018400", bad)


@unittest.skipUnless(__import__("importlib").util.find_spec("unicorn"), "optional Unicorn runtime absent")
class PrivateStackAllowanceTests(unittest.TestCase):
    def test_only_one_balanced_four_byte_save_at_entry_sp_minus_four(self):
        # PUSH ESI; POP ESI; RET 4, matching the measured private save shape.
        eax, _, regs = execute_memory(0x00401000, bytes.fromhex("565ec20400"), b"\0" * 16,
            registers={}, stack_arguments=[0x1234], readable=[], writable=[], stack_cleanup=4,
            balanced_stack_save="esi", return_registers=("ecx",))
        self.assertTrue(0 <= eax <= 0xffffffff)
        # A balanced second save at the same address is still forbidden.
        with self.assertRaisesRegex(RuntimeError, "multiple private stack-save"):
            execute_memory(0x00401000, bytes.fromhex("565e565ec20400"), b"\0" * 16,
                registers={}, stack_arguments=[0x1234], readable=[], writable=[], stack_cleanup=4,
                balanced_stack_save="esi")
        # The specific allowance may not swallow an unbalanced save.
        with self.assertRaises(Exception):
            execute_memory(0x00401000, bytes.fromhex("56c20400"), b"\0" * 16,
                registers={}, stack_arguments=[0x1234], readable=[], writable=[], stack_cleanup=4,
                balanced_stack_save="esi")


@unittest.skipUnless(Path(__file__).resolve().parents[1].joinpath("gamedata/bin_ship/DAOrigins.exe").is_file()
                     and importlib.util.find_spec("unicorn"), "pinned original or Unicorn runtime absent")
class OriginalUnlinkReplayTests(unittest.TestCase):
    def expected_trace(self, inputs):
        _, _, _, chain, _ = fixture("fn_00018400", inputs)
        list_offset, target = inputs["list"], inputs["node"]
        trace = [("read", list_offset + 0x18, 4)]
        for predecessor in chain:
            if predecessor == target:
                break
            trace.append(("read", predecessor + 4, 4))
        if target not in chain:
            return trace
        arena = bytes.fromhex(inputs["arena"])
        u32 = lambda offset: int.from_bytes(arena[offset:offset + 4], "little")
        prev, following = u32(target + 8), u32(target + 4)
        trace.append(("read", target + 8, 4))
        if prev:
            trace.extend([("read", target + 4, 4), ("write", prev - 0x02000000 + 4, 4),
                          ("read", target + 4, 4)])
        else:
            trace.extend([("read", target + 4, 4), ("write", list_offset + 0x18, 4),
                          ("read", target + 4, 4)])
        trace.append(("read", target + 8, 4))
        trace.append(("write", following - 0x02000000 + 8, 4) if following
                     else ("write", list_offset + 0x1c, 4))
        return trace

    def test_repeated_original_traces_and_conditional_ecx_with_semantic_mutant(self):
        root = Path(__file__).resolve().parents[1]
        registry = json.loads((root / "analysis/functions.json").read_text())
        function = next(item for item in registry["functions"] if item["name"] == "fn_00018400")
        public = cases("fn_00018400", "public")
        chosen = [public[i] for i in (0, 4, 20, 21, 22, 23, 24, 25, 100, 101, 102, 103, 400, 401, 402, 403)]
        for case in chosen:
            first = dispatch_original(function, case["inputs"], root / "gamedata/bin_ship/DAOrigins.exe")
            second = dispatch_original(function, case["inputs"], root / "gamedata/bin_ship/DAOrigins.exe")
            self.assertEqual(first, second)
            self.assertEqual(first[3], self.expected_trace(case["inputs"]))
        nonhead = next(case for case in public
                       if len(fixture("fn_00018400", case["inputs"])[3]) >= 3
                       and case["inputs"]["node"] == fixture("fn_00018400", case["inputs"])[3][1])
        observed = dispatch_original(function, nonhead["inputs"], root / "gamedata/bin_ship/DAOrigins.exe")
        self.assertNotEqual(observed[2], ARENA_BASE + nonhead["inputs"]["list"])
        mutated_ecx = ARENA_BASE + nonhead["inputs"]["list"]
        self.assertNotEqual(observed[2], mutated_ecx,
                            "semantic negative control: preserving entry ECX changes this observation")

    def test_all_original_only_states_and_reached_heldout_prestates(self):
        root = Path(__file__).resolve().parents[1]
        registry = json.loads((root / "analysis/functions.json").read_text())
        function = next(item for item in registry["functions"] if item["name"] == "fn_00018400")
        suite = cases("fn_00018400", "public") + cases("fn_00018400", "heldout")
        self.assertEqual(len(suite), 1168)
        for case in suite:
            inputs = case["inputs"]
            eax, after, ecx, trace = dispatch_original(function, inputs, root / "gamedata/bin_ship/DAOrigins.exe")
            expected_eax, expected_after = _model_step("fn_00018400", inputs)
            self.assertEqual((eax, after), (expected_eax, expected_after), case["id"])
            _, _, _, chain, _ = fixture("fn_00018400", inputs)
            expected_ecx = ARENA_BASE + inputs["list"]
            if inputs["node"] in chain:
                arena = bytes.fromhex(inputs["arena"])
                nxt = int.from_bytes(arena[inputs["node"] + 4:inputs["node"] + 8], "little")
                if nxt:
                    expected_ecx = int.from_bytes(arena[inputs["node"] + 8:inputs["node"] + 12], "little")
            self.assertEqual(ecx, expected_ecx, case["id"])
            self.assertEqual(trace, self.expected_trace(inputs), case["id"])

        # Each held-out unlink input is the next call's prestate after a real
        # original execution of the preceding unlink in that composition.
        snapshots = composition_snapshots("fn_00018400")
        self.assertEqual(len(snapshots), len(LAYOUTS))
        for index, (list_offset, node_offsets) in enumerate(LAYOUTS):
            arena = bytearray(_arena_seed("unlink-composition", "heldout", list_offset))
            _with_chain(arena, list_offset, node_offsets, (1, 3, 0))
            first = _inputs("fn_00018400", arena, list_offset, node_offsets, node_offsets[3])
            _, reached, _, _ = dispatch_original(function, first, root / "gamedata/bin_ship/DAOrigins.exe")
            self.assertEqual(snapshots[index]["arena"], reached.hex())


if __name__ == "__main__":
    unittest.main()

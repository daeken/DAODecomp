import importlib.util
import unittest

from tools.daodecomp.memory import ARENA_BASE, execute_memory
from validation.memory_cases import COPY_SIZES, BIT_FUNCTION, cases, fixture


class MemoryFixtureTests(unittest.TestCase):
    def test_deterministic_disjoint_suites_and_all_cases_valid(self):
        for name in [*COPY_SIZES, BIT_FUNCTION]:
            public, heldout = cases(name), cases(name, "heldout")
            self.assertEqual(public, cases(name))
            self.assertFalse({c['id'] for c in public} & {c['id'] for c in heldout})
            for case in public + heldout:
                fixture(name, case['inputs'])

    def test_invalid_or_wrapping_footprints_rejected(self):
        for name in [*COPY_SIZES, BIT_FUNCTION]:
            inputs = cases(name)[0]['inputs'].copy()
            inputs['destination' if name in COPY_SIZES else 'base'] = 0xffffffff
            with self.assertRaises(ValueError): fixture(name, inputs)


@unittest.skipUnless(importlib.util.find_spec("unicorn"), "optional Unicorn not installed")
class MemoryGuardTests(unittest.TestCase):
    def run_code(self, code, **changes):
        options = dict(registers={"ecx": ARENA_BASE + 3}, stack_arguments=[],
                       readable=[(3, 4)], writable=[(3, 4)], stack_cleanup=0)
        options.update(changes)
        return execute_memory(0x401000, bytes.fromhex(code), bytes(range(32)), **options)

    def test_unaligned_mutation_and_surrounding_canaries(self):
        result, after = self.run_code("8b01 83c001 8901 c3")  # load; add 1; store; ret
        self.assertEqual(result, 0x06050404)
        self.assertEqual(after, bytes(range(3)) + bytes([4, 4, 5, 6]) + bytes(range(7, 32)))

    def test_read_past_declared_source_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "read outside"):
            self.run_code("8b4101 c3")

    def test_write_crossing_destination_boundary_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "write outside"):
            self.run_code("894101 c3")

    def test_stack_argument_read_but_no_stack_write(self):
        result, _ = self.run_code("8b442404 c20400", stack_arguments=[7], stack_cleanup=4)
        self.assertEqual(result, 7)
        with self.assertRaisesRegex(RuntimeError, "write outside"):
            self.run_code("89442404 c20400", stack_arguments=[7], stack_cleanup=4)

    def test_nonvolatile_and_direction_flag_rejected(self):
        for code, error in [("31db c3", "nonvolatile"), ("fd c3", "direction flag")]:
            with self.assertRaisesRegex(RuntimeError, error): self.run_code(code)

    def test_unfinished_loop_is_not_success(self):
        with self.assertRaisesRegex(RuntimeError, "within budget"):
            self.run_code("ebfe", instruction_budget=8)

    def test_branch_beyond_reviewed_slice_is_not_success(self):
        with self.assertRaisesRegex(RuntimeError, "escaped"):
            self.run_code("eb02 90 90 90")

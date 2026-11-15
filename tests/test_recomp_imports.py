"""Whole-surface import coverage must fail closed on missing or changed slots."""
import copy
from pathlib import Path
import tempfile
import unittest
from tools import recomp, recomp_imports as imports


class ImportCoverageTests(unittest.TestCase):
    def setUp(self):
        self.bindings = imports.read_bindings()
        self.manifest = dict(modules=[dict(module="test.exe", binary_sha256="a" * 64, image_base=0x400000)],
            imports=[dict(library="KeRnEl32.DlL", symbol="IsDebuggerPresent", address=0x402000,
                          importing_module="test.exe", policy="native", contract="unknown"),
                     dict(library="USER32.dll", symbol="CreateWindowExW", address=0x402004,
                          importing_module="test.exe", policy="native", contract="unknown")])
        self.catalog = dict(records=[dict(library=r["library"], symbol=r["symbol"], policy="native",
            planning_group="test", slots=[dict(module="test.exe", binary_sha256="a" * 64,
                                              iat_rva=r["address"] - 0x400000)])
            for r in self.manifest["imports"]])

    def test_inventory_does_not_equate_partial_bindings_with_completion(self):
        report = imports.coverage(self.manifest, self.catalog, self.bindings)
        self.assertEqual(report["counts"], dict(generated_scoped_adapter=1, unimplemented=1))
        self.assertEqual(report["static_slots"], 2)
        self.assertFalse(report["all_static_imports_have_scoped_contracts"])
        self.assertEqual(self.manifest["imports"][0]["contract"], "unknown")
        empty = copy.deepcopy(self.manifest)
        empty["imports"] = []
        with self.assertRaisesRegex(ValueError, "missing pinned import slots"):
            imports.coverage(empty, self.catalog, self.bindings)

    def test_changed_identity_policy_omission_and_duplicate_refuse(self):
        for change in ("symbol", "policy", "slot", "module", "omit", "duplicate"):
            manifest = copy.deepcopy(self.manifest)
            if change == "symbol": manifest["imports"][0]["symbol"] = "isdebuggerpresent"
            elif change == "policy": manifest["imports"][0]["policy"] = "translate"
            elif change == "slot": manifest["imports"][0]["address"] += 8
            elif change == "module": manifest["modules"][0]["binary_sha256"] = "b" * 64
            elif change == "omit": manifest["imports"].pop()
            else: manifest["imports"].append(copy.deepcopy(manifest["imports"][0]))
            with self.subTest(change=change), self.assertRaises(ValueError):
                imports.coverage(manifest, self.catalog, self.bindings)

    def test_translated_modules_never_receive_a_native_binding(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["imports"][0]["policy"] = "translate"
        imports.apply_contracts(manifest["imports"], self.bindings)
        self.assertEqual(manifest["imports"][0]["contract"], "unknown")
        self.assertNotIn("adapter", manifest["imports"][0])

    def test_ambiguous_bindings_guessed_pointer_abi_and_output_rules_refuse(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bindings.json"
            for change in ("duplicate", "pointer", "cdecl", "output", "count"):
                bindings = copy.deepcopy(self.bindings)
                row = next(r for r in bindings["bindings"] if r["symbol"] == "FileTimeToSystemTime")
                if change == "duplicate": bindings["bindings"].append(copy.deepcopy(row))
                elif change == "pointer": row["arguments"][0] = dict(mode="scalar", type="void*")
                elif change == "cdecl": row["calling_convention"] = "cdecl"
                elif change == "output": row["output_defined_when"] = "always"
                else: row["arguments"][0] = dict(mode="ansi_counted", count_argument=99)
                recomp.atomic_json(path, bindings)
                with self.subTest(change=change), self.assertRaises(ValueError):
                    imports.read_bindings(path)

    def test_explicit_pointer_bridges_require_supported_abi_and_implementation_family(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bindings.json"
            for change in ("family", "argument", "result_without_bridge"):
                bindings = copy.deepcopy(self.bindings)
                row = next(r for r in bindings["bindings"] if r["symbol"] == "VirtualAlloc")
                if change == "family": row["bridge"] = "unchecked_passthrough"
                elif change == "argument": row["arguments"][0]["type"] = "guessed_object*"
                else: row.pop("bridge")
                recomp.atomic_json(path, bindings)
                with self.subTest(change=change), self.assertRaises(ValueError):
                    imports.read_bindings(path)


if __name__ == "__main__":
    unittest.main()

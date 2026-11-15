"""SDK harvesting cannot silently promote a macro or incomplete AST to an ABI."""
import copy
import json
import unittest
from tools.recomp_import_abi import parse_declarations, sdk_rows


class ImportAbiTests(unittest.TestCase):
    def test_unpinned_ambiguous_or_data_ordinal_is_not_a_function_prototype(self):
        catalog = dict(provider_inventory={"ws2_32.dll": dict(sha256="a"*64)}, records=[
            dict(id="ws2_32.dll!@ordinal:3", policy="native", library="ws2_32.dll", symbol="@ordinal:3",
                 provider_export=dict(named_aliases=["closesocket"], kind="function"))])
        self.assertEqual(sdk_rows(catalog), [dict(id="ws2_32.dll!@ordinal:3", sdk_identifier="closesocket")])
        for change in ("unpin", "ambiguous", "data"):
            invalid = copy.deepcopy(catalog)
            if change == "unpin": invalid["provider_inventory"]["ws2_32.dll"] = {}
            elif change == "ambiguous": invalid["records"][0]["provider_export"]["named_aliases"].append("other")
            else: invalid["records"][0]["provider_export"]["kind"] = "data"
            with self.subTest(change=change), self.assertRaises(ValueError): sdk_rows(invalid)

    def test_macro_rewrite_remains_an_observation_not_an_export_abi(self):
        row = dict(id="kernel32.dll!InterlockedIncrement", sdk_identifier="InterlockedIncrement")
        node = dict(kind="TypedefDecl", name="DaoImport0000", type=dict(desugaredQualType="long (*)(volatile long*)"),
                    inner=[dict(referencedDecl=dict(kind="FunctionDecl", name="_InterlockedIncrement")),
                           dict(kind="FunctionProtoType", cc="cdecl", inner=[dict(type=dict(qualType="long")),
                                dict(type=dict(qualType="volatile long*"))])])
        observed, = parse_declarations(json.dumps(node), [row])
        self.assertEqual(observed["status"], "sdk_macro_or_intrinsic")
        self.assertEqual(observed["calling_convention_observation"], "cdecl")
        self.assertFalse(observed["adapter_ready"])
        for text in ("", json.dumps(node)+json.dumps(node)):
            with self.assertRaises(ValueError): parse_declarations(text, [row])


if __name__ == "__main__": unittest.main()

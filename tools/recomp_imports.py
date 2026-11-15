"""Generate checked native bindings and audit the whole import surface.

An adapter declaration is a scoped contract, never an API/game acceptance result.
The compiler checks every generated prototype against the Windows SDK headers.
"""
import argparse
import collections
import copy
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BINDINGS = ROOT / "recompiler/native-bindings.json"
CATALOG = ROOT / "recompiler/imports.json"
SCALARS = {"DWORD", "UINT", "BOOL", "LONG", "int", "LCID", "LCTYPE"}
BRIDGE_TYPES = SCALARS | {"HANDLE", "LPVOID", "LPCVOID", "SIZE_T", "LPCSTR", "LPCWSTR", "LPSTR", "LPWSTR",
    "LPSECURITY_ATTRIBUTES", "LPDWORD", "LPOVERLAPPED", "LPOVERLAPPED_COMPLETION_ROUTINE", "PLONG",
    "LPWIN32_FIND_DATAA", "LPWIN32_FIND_DATAW", "LPSTR*", "LPWSTR*", "PULARGE_INTEGER"}
RECORDS = {"FILETIME": 8, "SYSTEMTIME": 16}
MODES = {"scalar", "ansi", "utf16", "ansi_counted", "utf16_counted", "input_record", "output_record"}


def identity(library, symbol):
    # Windows DLL basenames are insensitive; export names are sensitive.
    if not library or "/" in library or "\\" in library or not symbol:
        raise ValueError("invalid native import identity")
    return library.lower() + "!" + symbol


def read_bindings(path=BINDINGS):
    from tools.recomp import load
    data = load(path)
    if data.get("schema_version") != 1:
        raise ValueError("unsupported native binding schema")
    seen = set()
    for row in data["bindings"]:
        key = identity(row["library"], row["symbol"])
        if key in seen:
            raise ValueError("duplicate native binding: " + key)
        seen.add(key)
        if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", row["symbol"]):
            raise ValueError("generated binding requires an SDK function identifier")
        if row["library"] not in ("kernel32.dll", "user32.dll", "gdi32.dll"):
            raise ValueError("generated binding library has no reviewed SDK/link setup")
        if row.get("calling_convention") != "stdcall" or row["result"] not in SCALARS | BRIDGE_TYPES | {"void"}:
            raise ValueError("unsupported generated ABI")
        if not row.get("provenance") or not row.get("scope"):
            raise ValueError("binding needs provenance and a scoped contract")
        if row.get("bridge"):
            if row["bridge"] not in ("files", "memory") or any(a.get("mode") != "bridge" or a.get("type") not in BRIDGE_TYPES for a in row["arguments"]):
                raise ValueError("unsupported explicit bridge ABI")
            continue
        if row["result"] not in SCALARS | {"void"}:
            raise ValueError("pointer returns need an explicit ownership bridge")
        outputs = []
        for index, arg in enumerate(row["arguments"]):
            mode = arg["mode"]
            if mode not in MODES:
                raise ValueError("unsupported native argument mode")
            if mode == "scalar" and arg["type"] not in SCALARS:
                raise ValueError("unsupported scalar type")
            if mode.endswith("record"):
                if arg["type"] not in RECORDS:
                    raise ValueError("record has no reviewed complete field layout")
                if mode == "output_record":
                    outputs.append(index)
            if mode.endswith("counted"):
                count = arg.get("count_argument")
                if type(count) is not int or count < 0 or count >= len(row["arguments"]):
                    raise ValueError("invalid input span count")
                if row["arguments"][count] != {"mode": "scalar", "type": "int"}:
                    raise ValueError("counted input requires a signed 32-bit count")
        if outputs and not (row.get("output_defined_when") == "always" and row["result"] == "void" or
                            row.get("output_defined_when") == "nonzero" and row["result"] == "BOOL"):
            raise ValueError("output storage requires an explicit supported result predicate")
    return data


def contract(row):
    return (f"generated win32-stdcall; cleanup{4 * len(row['arguments'])}; " + row["scope"] +
            "; actual native API/result/last-error; known inputs and checked shared backing; "
            "ECX/EDX/XMM/arithmetic flags volatile; scoped adapter, not API/game acceptance")


def apply_contracts(imports, bindings):
    rows = {identity(r["library"], r["symbol"]): r for r in bindings["bindings"]}
    for imported in imports:
        row = rows.get(identity(imported["library"], imported["symbol"]))
        if row is not None and imported["policy"] == "native":
            imported["contract"] = contract(row)
            imported["adapter"] = "generated_checked_native"


def render_bindings(bindings):
    lines = ["// Generated from native-bindings.json. SDK prototypes are checked, never cast."]
    for row in bindings["bindings"]:
        symbol = row["symbol"]
        lines += [f'if(native_library_is(import.library,"{row["library"]}") && std::strcmp(import.symbol,"{symbol}")==0) {{']
        if row.get("bridge"):
            signature = f'{row["result"]}(WINAPI*)({",".join(a["type"] for a in row["arguments"])})'
            lines += [f"static_assert(std::is_same_v<decltype(&::{symbol}),{signature}>);",
                      f"native_bridge_{symbol}(args,result);", f'cleanup={len(row["arguments"]) * 4};',
                      f'returns_eax={str(row["result"] != "void").lower()};', "return true;", "}"]
            continue
        types = []
        for index, arg in enumerate(row["arguments"]):
            mode = arg["mode"]
            if mode == "scalar":
                ty = arg["type"]
                expression = f"args.template scalar<{ty}>({index})"
            elif mode.endswith("record"):
                ty = ("const " if mode == "input_record" else "") + arg["type"] + "*"
                expression = f'args.template record<{arg["type"]},{str(mode == "output_record").lower()}>({index})'
                lines.append(f'static_assert(sizeof({arg["type"]})=={RECORDS[arg["type"]]});')
                if mode == "output_record":
                    lines.append(f"auto output_address_{index}=argument({index});")
            else:
                char = "char" if mode.startswith("ansi") else "wchar_t"
                ty = f"const {char}*"
                count = f'args.template scalar<int>({arg["count_argument"]})' if mode.endswith("counted") else "-1"
                expression = f'args.template text<{char}>({index},{str(arg.get("nullable", False)).lower()},{count})'
            types.append(ty)
            lines.append(f"auto a{index}={expression};")
        signature = f'{row["result"]}(WINAPI*)({",".join(types)})'
        lines += [f"static_assert(std::is_same_v<decltype(&::{symbol}),{signature}>);"]
        call = f'::{symbol}({",".join(f"a{i}" for i in range(len(types)))})'
        if row["result"] == "void":
            lines += [f"call_native([&] {{ {call}; }});", "returns_eax=false;"]
        else:
            lines += [f"result=std::uint32_t(call_native([&] {{ return {call}; }}));"]
        for index, arg in enumerate(row["arguments"]):
            if arg["mode"] == "output_record":
                succeeded = "true" if row["output_defined_when"] == "always" else "result!=0"
                lines.append(f'args.finish_output(output_address_{index},sizeof({arg["type"]}),{succeeded});')
        lines += [f'cleanup={len(types) * 4};', "return true;", "}"]
    return "\n".join(lines) + "\nreturn false;\n"


def coverage(manifest, catalog, bindings):
    """Audit slots, not just names, against the independent pinned PE inventory."""
    imported = copy.deepcopy(manifest["imports"])
    apply_contracts(imported, bindings)
    modules = {m["module"]: m for m in manifest["modules"]}
    expected = {}
    for record in catalog["records"]:
        key = identity(record["library"], record["symbol"])
        for slot in record["slots"]:
            slot_key = (slot["module"], slot["binary_sha256"], slot["iat_rva"])
            if slot_key in expected:
                raise ValueError("duplicate catalog slot")
            expected[slot_key] = (key, record["policy"], record["planning_group"])
    seen, grouped = set(), {}
    for item in imported:
        module = modules[item["importing_module"]]
        slot = (module["module"], module["binary_sha256"], item["address"] - module["image_base"])
        if slot in seen:
            raise ValueError("duplicate manifest slot")
        seen.add(slot)
        key = identity(item["library"], item["symbol"])
        wanted = expected.get(slot)
        if wanted is None or wanted[:2] != (key, item["policy"]):
            raise ValueError("import differs from pinned catalog: " + str(slot))
        status = ("translated_module" if item["policy"] == "translate" else
                  "generated_scoped_adapter" if item.get("adapter") == "generated_checked_native" else
                  "explicit_scoped_adapter" if item.get("contract") and not item["contract"].startswith("unknown") else
                  "unimplemented")
        row = grouped.setdefault(key, dict(id=key, status=status, planning_group=wanted[2], slots=[]))
        if row["status"] != status:
            raise ValueError("inconsistent import contracts across slots")
        row["slots"].append(dict(module=slot[0], binary_sha256=slot[1], iat_rva=slot[2]))
    if seen != set(expected):
        raise ValueError("manifest is missing pinned import slots")
    rows = sorted(grouped.values(), key=lambda r: r["id"])
    return dict(schema_version=1, static_slots=len(seen), unique_imports=len(rows),
                counts=dict(collections.Counter(r["status"] for r in rows)), records=rows,
                groups={g: dict(collections.Counter(r["status"] for r in rows if r["planning_group"] == g))
                        for g in sorted({r["planning_group"] for r in rows})},
                all_static_imports_have_scoped_contracts=all(r["status"] != "unimplemented" for r in rows),
                acceptance="Declaration coverage only. Scoped/translated entries can have unsupported inputs and callees. "
                           "Dynamic lookup, callback, thread and COM method coverage are separate obligations.")


def main():
    from tools import recomp
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    parser.add_argument("--bindings", type=Path, default=BINDINGS)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-contracts", action="store_true")
    args = parser.parse_args()
    report = coverage(recomp.load(args.manifest), recomp.load(args.catalog), read_bindings(args.bindings))
    report["inputs"] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in (args.manifest, args.catalog, args.bindings, Path(__file__))}
    recomp.atomic_json(args.output, report)
    print(json.dumps({k: report[k] for k in ("static_slots", "unique_imports", "counts", "all_static_imports_have_scoped_contracts")}, indent=2))
    return int(args.require_contracts and not report["all_static_imports_have_scoped_contracts"])


if __name__ == "__main__":
    raise SystemExit(main())

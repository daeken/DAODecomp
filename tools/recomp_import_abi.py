"""Harvest SDK declarations for the complete pinned Windows import inventory.

This produces ABI research inputs, not runnable adapters. In particular, SDK
macros/intrinsics may have a different ABI from the corresponding DLL export.
"""
import argparse
import collections
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
from tools import recomp, recomp_imports

MIDDLEWARE = {"binkw32.dll", "fmodex.dll", "fmod_event.dll", "speedtreert.dll",
              "physxloader.dll", "nxcooking.dll", "nxcharacter.dll"}
HEADERS = ("winsock2.h", "ws2tcpip.h", "windows.h", "nb30.h", "psapi.h", "shlobj.h",
           "shellapi.h", "mmsystem.h", "oleauto.h", "d3d9.h", "d3dx9.h", "dinput.h")


def sdk_rows(catalog):
    rows = []
    for row in catalog["records"]:
        if row["policy"] != "native" or row["library"] in MIDDLEWARE:
            continue
        name = row["symbol"]
        if name.startswith("@ordinal:"):
            provider = catalog["provider_inventory"].get(row["library"], {})
            export = row.get("provider_export") or {}
            aliases = export.get("named_aliases", [])
            if not provider.get("sha256") or len(aliases) != 1 or export.get("kind") != "function":
                raise ValueError("ordinal needs one named alias from a pinned provider: " + row["id"])
            name = aliases[0]
        if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", name):
            raise ValueError("invalid SDK identifier")
        rows.append(dict(id=row["id"], sdk_identifier=name))
    return sorted(rows, key=lambda r: r["id"])


def probe_source(rows):
    return ("#define WIN32_LEAN_AND_MEAN\n#define DIRECTINPUT_VERSION 0x0800\n" +
            "".join(f"#include <{header}>\n" for header in HEADERS) +
            '_Static_assert(sizeof(void*)==4 && sizeof(long)==4,"requires Windows x86 data model");\n' +
            "".join(f'typedef __typeof__(&{row["sdk_identifier"]}) DaoImport{i:04d};\n'
                    for i, row in enumerate(rows)))


def walk(node):
    yield node
    for child in node.get("inner", []):
        yield from walk(child)


def parse_declarations(text, rows):
    decoder, nodes = json.JSONDecoder(), {}
    while text.strip():
        text = text.lstrip()
        node, end = decoder.raw_decode(text)
        text = text[end:]
        name = node.get("name")
        if node.get("kind") != "TypedefDecl" or name in nodes:
            raise ValueError("unexpected/duplicate SDK declaration")
        nodes[name] = node
    if set(nodes) != {f"DaoImport{i:04d}" for i in range(len(rows))}:
        raise ValueError("SDK AST omitted or added import declarations")
    results = []
    for index, row in enumerate(rows):
        node = nodes[f"DaoImport{index:04d}"]
        referenced = {n["referencedDecl"]["name"] for n in walk(node)
                      if n.get("referencedDecl", {}).get("kind") == "FunctionDecl"}
        if len(referenced) != 1:
            raise ValueError("SDK identifier did not resolve to one function")
        actual, = referenced
        # The outer FunctionProtoType is visited before any callback parameters.
        function = next((n for n in walk(node) if n.get("kind") == "FunctionProtoType"), None)
        if function is None or not function.get("inner"):
            raise ValueError("SDK declaration has no complete prototype")
        types = [n["type"]["qualType"] for n in function["inner"]]
        results.append(dict(row, sdk_resolved_identifier=actual,
                            status="sdk_declaration" if actual == row["sdk_identifier"] else "sdk_macro_or_intrinsic",
                            declared_cpp_type=node["type"]["desugaredQualType"],
                            calling_convention_observation=function["cc"], variadic=bool(function.get("variadic")),
                            return_type=types[0], parameter_types=types[1:],
                            adapter_ready=False))
    return results


def inspect_middleware(rows, catalog, work, compiler, wine, prefix):
    """Demangled names are declarations in the binary, not memory contracts."""
    source = recomp.ROOT / "recompiler/experiments/demangle_exports.c"
    executable = work / "demangle-exports.exe"
    build = [str(compiler), "-x", "c", "-std=c11", "-O2", "-static", str(source), "-ldbghelp", "-o", str(executable)]
    built = subprocess.run(build, capture_output=True, text=True, timeout=120)
    (work / "demangle-build.log").write_text(built.stdout + built.stderr)
    if built.returncode:
        raise ValueError("export-name inspector build failed: " + built.stderr)
    mangled = [row for row in rows if row["status"] == "needs_middleware_abi" and row["id"].split("!", 1)[1].startswith("?")]
    names = [row["id"].split("!", 1)[1] for row in mangled]
    command = [str(wine.absolute()), str(executable)]
    env = dict(os.environ, WINEPREFIX=str(prefix.absolute()), WINEDEBUG="-all", MVK_CONFIG_LOG_LEVEL="0")
    output, errors = work / "demangle-output.tsv", work / "demangle-errors.log"
    with output.open("w") as stdout, errors.open("w") as stderr:
        ran = subprocess.run(command, input="".join(name+"\n" for name in names), text=True,
                             stdout=stdout, stderr=stderr, env=env, timeout=60)
    lines = output.read_text().splitlines()
    if ran.returncode or len(lines) != len(names):
        raise ValueError("export-name inspection failed or returned incomplete results")
    for row, name, line in zip(mangled, names, lines):
        fields = line.split("\t")
        if len(fields) != 2 or fields[0] != name or not fields[1] or fields[1] == name:
            raise ValueError("export-name inspector identity mismatch")
        row.update(status="msvc_export_declaration", decorated_declaration=fields[1])
    originals = {row["id"]: row for row in catalog["records"]}
    for row in rows:
        if row["status"] != "needs_middleware_abi": continue
        symbol = originals[row["id"]]["symbol"]
        match = re.fullmatch(r"_[A-Za-z_][A-Za-z_0-9]*@(\d+)", symbol)
        if match:
            row.update(status="stdcall_stack_decoration", decorated_stack_bytes=int(match[1]))
        else: row["status"] = "middleware_signature_unknown"
    return dict(build_argv=build, execution_argv=command,
                scope="Wine dbghelp demangles export names only. No middleware or game code is loaded/called; "
                      "declarations/stack decorations do not establish sizes, ownership, callbacks or output semantics.",
                artifacts={str(p): recomp.digest(p.read_bytes()) for p in (source, executable, output, errors, wine.absolute())})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=recomp_imports.CATALOG)
    parser.add_argument("--compiler", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--wine", type=Path, help="also demangle all middleware C++ exports in one native inspector run")
    parser.add_argument("--wine-prefix", type=Path)
    args = parser.parse_args()
    if bool(args.wine) != bool(args.wine_prefix): parser.error("--wine and --wine-prefix are required together")
    catalog = recomp.load(args.catalog)
    rows = sdk_rows(catalog)
    work = args.work_dir.absolute()
    work.mkdir(parents=True, exist_ok=True)
    source, deps = work / "sdk-imports.c", work / "sdk-imports.d"
    source.write_text(probe_source(rows))
    compiler = args.compiler.absolute() # Preserve llvm-mingw's target driver name.
    command = [str(compiler), "-x", "c", "-std=c11", "-fsyntax-only", "-MD", "-MF", str(deps),
               "-MT", "probe", "-Xclang", "-ast-dump=json", "-Xclang", "-ast-dump-filter=DaoImport", str(source)]
    result = subprocess.run(command, capture_output=True, text=True, timeout=120)
    (work / "sdk-ast.jsonl").write_text(result.stdout)
    (work / "sdk-errors.log").write_text(result.stderr)
    if result.returncode:
        raise ValueError("SDK probe failed; no ABI inventory published: " + result.stderr)
    observations = parse_declarations(result.stdout, rows)
    inspected = {row["id"] for row in observations}
    observations.extend(dict(id=row["id"], status="needs_middleware_abi", adapter_ready=False)
                        for row in catalog["records"] if row["policy"] == "native" and row["id"] not in inspected)
    middleware = inspect_middleware(observations, catalog, work, compiler, args.wine, args.wine_prefix) if args.wine else None
    dependencies = [Path(p) for p in shlex.split(deps.read_text().split(":", 1)[1].replace("\\\n", ""))]
    artifacts = [args.catalog, source, Path(__file__), compiler,
                 *([compiler.parent / "clang"] if (compiler.parent / "clang").exists() else []), *dependencies]
    report = dict(schema_version=1,
        scope="SDK declaration research only. No adapter or export ABI acceptance; macro/intrinsic aliases, memory effects, "
              "ownership, callbacks, COM methods, threads, varargs and middleware ABIs require explicit review.",
        counts=dict(collections.Counter(row["status"] for row in observations)), records=sorted(observations, key=lambda r:r["id"]),
        middleware_inspection=middleware,
        command=command, compiler_version=subprocess.check_output([str(compiler), "--version"], text=True).strip(),
        artifacts={str(p.absolute()): recomp.digest(p.read_bytes()) for p in artifacts})
    recomp.atomic_json(args.output, report)
    print(json.dumps(report["counts"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

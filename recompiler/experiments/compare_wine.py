"""Bounded comparison of two pinned DAO slices against generated C++.

Reference: actual relocated PE32 instruction slices under Wine WoW64/Rosetta.
Candidate: independently compiled generated C++ on macOS ARM64, plus ASan/UBSan.
This is an isolated corpus experiment, not game/Windows hardware equivalence.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))
from tools import recomp
from tools.daodecomp.pe import fingerprint

PIN = "2346caee611002d4dff6ecef68eb315b63a37004dd98b39c11a9c26c0b45bfb3"
FUNCTIONS = [(0x18760, 10, "d49dc09416edfcaa5bdba34999de4daf67864c92e9c04fad2e3707991fe36fba"),
             (0x24030, 10, "fde7b389ab38b8362fc6d34289cc38373db36da8c3aa6b9e1a26128474e2e542")]


def run(argv, *, data=None, env=None):
    result = subprocess.run(list(map(str, argv)), input=data, capture_output=True, text=True,
                            timeout=90, env=env)
    if result.returncode:
        raise RuntimeError(f"{argv[0]} exited {result.returncode}: {result.stderr[-4000:]}")
    return result.stdout.replace("\r\n", "\n")


def observations(text, count):
    lines = text.splitlines()
    if len(lines) != count:
        raise ValueError("missing or extra observations")
    for line in lines:
        parts = line.split()
        if len(parts) != 3 or any(not p.isdecimal() or not 0 <= int(p) < 2**32 for p in parts[:2]) or \
                len(parts[2]) != 1024 or any(c not in "0123456789abcdef" for c in parts[2]):
            raise ValueError("malformed observation")
    return lines


def store_bit_mutation(text, setter):
    """Same store-value corruption for raw accesses and recovered field accessors.

    The original slices, fixtures, observations, comparisons and required semantic
    disagreement are unchanged. Only the candidate mutation site follows lowering.
    """
    structured = setter.get("structure_lowering") and setter.get("structures")
    needle = "memory.store(field_address, value, 32);" if structured else "memory.store(address, value, 32);"
    expected = 1 if structured else (2 if setter["control_flow"].startswith("structured;") else 1)
    if text.count(needle) != expected:
        raise ValueError("mutation location changed; review experiment")
    return text.replace(needle, needle.replace(", value,", ", value ^ 1,"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=ROOT.parent / "local/recomp/project")
    parser.add_argument("--wine", type=Path, required=True)
    parser.add_argument("--cc", type=Path, required=True, help="i686-w64-mingw32-clang")
    parser.add_argument("--output", type=Path, default=ROOT.parent / "local/recomp/wine-comparison")
    parser.add_argument("--wine-prefix", type=Path, default=ROOT.parent / "local/recomp/wine-prefix")
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    project = args.project.resolve()
    initial = recomp.state(project)
    binary = recomp.checked_binary(initial)
    if initial["binary_sha256"] != PIN:
        raise ValueError("experiment requires the pinned DAO build")
    identity = fingerprint(binary)
    view_id = recomp.load(project / "current.json")["view"]
    view, manifest = recomp.read_view(project, view_id)
    if manifest["project_sha256"] != recomp.digest(recomp.encoded(initial)):
        raise ValueError("regenerate after annotation edits")
    required = {rva for rva, _, _ in FUNCTIONS}
    if not required <= {f["rva"] for f in manifest["functions"]}:
        raise ValueError("generate both experiment functions first")
    here = Path(__file__).resolve().parent
    original = out / "original.exe"
    run([args.cc.absolute(), "-std=c11", "-O2", here / "wine_original.c", "-o", original])
    sources = [view / (f"fn_{rva:08x}.cpp") for rva, _, _ in FUNCTIONS]
    candidate = out / "candidate"
    sanitized = out / "candidate-sanitized"
    windows_candidate = out / "candidate-win64.exe"
    windows32_candidate = out / "candidate-win32.exe"
    base = ["clang++", "-std=c++20", "-O2", "-I", view, here / "wine_candidate.cpp", *sources]
    run([*base, "-o", candidate])
    run([*base, "-fsanitize=address,undefined", "-fno-sanitize-recover=all", "-o", sanitized])
    windows_cxx = args.cc.absolute().parent / "x86_64-w64-mingw32-clang++"
    run([windows_cxx, "-std=c++20", "-O2", "-static", "-I", view,
         here / "wine_candidate.cpp", *sources, "-o", windows_candidate])
    windows32_cxx = args.cc.absolute().parent / "i686-w64-mingw32-clang++"
    run([windows32_cxx, "-std=c++20", "-O2", "-static", "-I", view,
         here / "wine_candidate.cpp", *sources, "-o", windows32_candidate])
    mutant_source = out / "mutant.cpp"
    text = sources[1].read_text()
    setter = next(f for f in manifest["functions"] if f["rva"] == 0x24030)
    mutant_source.write_text(store_bit_mutation(text, setter))
    mutant = out / "mutant"
    run(["clang++", "-std=c++20", "-O2", "-I", view, here / "wine_candidate.cpp",
         sources[0], mutant_source, "-o", mutant])
    environment = dict(os.environ, WINEPREFIX=str(args.wine_prefix.resolve()), WINEDEBUG="-all",
                       MVK_CONFIG_LOG_LEVEL="0", WINEDLLOVERRIDES="mscoree,mshtml=")
    rng = random.Random(0xDA02026)
    cases = [{"object": obj, "value": value, "seed": seed}
             for obj in (0, 1, 3, 16, 399, 400)
             for value in (0, 1, 0x7fffffff, 0x80000000, 0xffffffff)
             for seed in (0, 1, 0xffffffff)]
    cases += [{"object": rng.randrange(401), "value": rng.getrandbits(32), "seed": rng.getrandbits(32)}
              for _ in range(100)]
    recomp.atomic_json(out / "cases.json", cases)
    data = "".join(f"{c['object']} {c['value']} {c['seed']}\n" for c in cases)
    results = []
    contents = binary.read_bytes()
    for mode, (rva, size, expected) in enumerate(FUNCTIONS):
        section = next(s for s in identity["sections"] if s["rva"] <= rva and rva + size <= s["rva"] + s["file_size"])
        offset = section["file_offset"] + rva - section["rva"]
        code = contents[offset:offset + size]
        if hashlib.sha256(code).hexdigest() != expected:
            raise ValueError("slice bytes changed")
        sliced = out / f"fn_{rva:08x}.bin"
        sliced.write_bytes(code)
        # Wine takes Windows paths; Z: is the isolated prefix's host-filesystem mapping.
        wine_path = "Z:" + str(sliced).replace("/", "\\")
        references = [observations(run([args.wine.resolve(), original, wine_path, mode], data=data,
                                       env=environment), len(cases)) for _ in range(2)]
        candidates = [observations(run([candidate, mode], data=data), len(cases)) for _ in range(2)]
        windows = [observations(run([args.wine.resolve(), windows_candidate, mode], data=data,
                                    env=environment), len(cases)) for _ in range(2)]
        windows32 = [observations(run([args.wine.resolve(), windows32_candidate, mode], data=data,
                                      env=environment), len(cases)) for _ in range(2)]
        sanitized_result = observations(run([sanitized, mode], data=data), len(cases))
        if any(value != references[0] for value in [*references[1:], *candidates, *windows, *windows32, sanitized_result]):
            raise ValueError(f"comparison or repeat disagreement at RVA {rva:x}")
        for label, values in (("original", references[0]), ("candidate", candidates[0])):
            (out / f"fn_{rva:08x}-{label}.txt").write_text("\n".join(values) + "\n")
        results.append({"rva": rva, "slice_sha256": expected, "cases": len(cases),
                        "repetitions_per_side": 2, "observation_sha256": recomp.digest(encoded_lines(references[0]))})
    changed = observations(run([mutant, 1], data=data), len(cases))
    if changed == references[0]:
        raise ValueError("memory mutation was not detected")
    report = {"schema_version": 1, "status": "corpus_agreement", "binary_sha256": PIN,
              "view": view_id, "functions": results, "negative_control": "store-bit mutation detected",
              "host": {"system": platform.platform(), "machine": platform.machine()},
              "wine_version": run([args.wine.resolve(), "--version"]).strip(),
              "wine_prefix": str(args.wine_prefix.resolve()),
              "compiler": run(["clang++", "--version"]).splitlines()[0],
              "candidate_targets": ["macOS ARM64 normal and ASan/UBSan", "Windows x86 and x64 under Wine/Rosetta"],
              "reference_compiler": run([args.cc.absolute(), "--version"]).splitlines()[0],
              "observations": "full EAX, ECX normalized to arena offset, all 512 arena bytes",
              "limits": ["Wine WoW64/Rosetta reference; no native x86 hardware evidence",
                         "isolated relocation-independent slices; no game initialization/integration",
                         "no reference flags, original stack footprint, exception or OS-effect comparison",
                         "bounded cases; candidate stack/return/nonvolatile checks are adapter checks"],
              "artifacts": {str(p): recomp.digest(p.read_bytes()) for p in
                            [binary, args.wine.resolve(), args.cc.absolute(), windows_cxx, windows32_cxx,
                             args.cc.absolute().parent / "clang", original, candidate, windows_candidate, windows32_candidate, sanitized, mutant,
                             here / "wine_original.c", here / "wine_candidate.cpp", Path(__file__).resolve(),
                             out / "cases.json", *sources, view / "runtime.hpp", view / "functions.hpp"]}}
    recomp.atomic_json(out / "report.json", report)
    print(json.dumps(report, indent=2))


def encoded_lines(lines):
    return ("\n".join(lines) + "\n").encode()


if __name__ == "__main__":
    main()

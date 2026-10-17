"""Reproducible differential checks of reviewed game slices, no Windows needed."""
import argparse
import hashlib
from importlib.metadata import version
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.daodecomp.harness import compare, file_hash, load_json, write_json


def corpus():
    values = list(range(40))
    values += [1 << bit for bit in range(32)]
    values += [0xffffffff ^ (1 << bit) for bit in range(32)]
    values += [0xffffffff, 0xfffffffe, 0x80000001, 0x01020304, 0xdeadbeef,
               0xaaaaaaaa, 0x55555555, 0x00ff00ff, 0xff00ff00]
    values += [int.from_bytes(hashlib.sha256(f"DAODecomp-leaves-v1:{i}".encode()).digest()[:4], "little")
               for i in range(64)]
    return [{"id": f"u32-{v:08x}", "inputs": {"value": v}} for v in dict.fromkeys(values)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, default=ROOT / "gamedata/bin_ship/DAOrigins.exe")
    parser.add_argument("--build-dir", type=Path, default=ROOT / "build")
    parser.add_argument("--expect-mismatch", action="store_true")
    args = parser.parse_args()
    executable = args.build_dir.resolve() / (("dao_leaf_mutant" if args.expect_mismatch else "dao_leaf_runner") +
                                             (".exe" if sys.platform == "win32" else ""))
    if not executable.is_file() or not args.binary.is_file():
        parser.error("build the C++ runner and provide the pinned original binary first")
    cases = corpus()
    if args.expect_mismatch:
        cases = [c for c in cases if c["inputs"]["value"] in (0, 31, 32, 0xffffffff)]
    case_path = ROOT / ("reports/leaves-mutant-cases.json" if args.expect_mismatch else "reports/leaves-cases.json")
    write_json(case_path, cases)
    registry = load_json(ROOT / "analysis/functions.json")
    selected = [f for f in registry["functions"] if not args.expect_mismatch or f["name"] == "bit_mask_or_all"]
    success = bool(selected)
    for function in selected:
        runner = ROOT / "validation/leaf_runner.py"
        oracle = [sys.executable, str(runner), "original", str(args.binary.resolve())]
        candidate = [sys.executable, str(runner), "candidate", str(executable)]
        artifacts = [args.binary, executable, runner, Path(__file__), case_path,
                     ROOT / "tools/daodecomp/harness.py", ROOT / "tools/daodecomp/leaf.py",
                     ROOT / "tools/daodecomp/pe.py", ROOT / "analysis/functions.json",
                     ROOT / "analysis/reference-build.json", ROOT / function["contract"],
                     ROOT / "include/dao/primitives.hpp", ROOT / "src/primitives.cpp",
                     ROOT / "validation/native_runner.cpp", ROOT / "CMakeLists.txt",
                     ROOT / "requirements-validation.txt", args.build_dir / "CMakeCache.txt"]
        compile_commands = args.build_dir / "compile_commands.json"
        if compile_commands.exists():
            artifacts.append(compile_commands)
        report = compare(load_json(ROOT / function["contract"]), cases, oracle, candidate,
                         repeats=2, artifacts=artifacts)
        report["backend_versions"] = {"unicorn": version("unicorn"), "python": platform.python_version()}
        report["scope"] = "Unicorn x86 original slice versus native compiled C++; corpus evidence only"
        report["native_windows_validated"] = False
        suffix = "-mutant" if args.expect_mismatch else ""
        destination = ROOT / f'reports/{function["name"]}{suffix}.json'
        write_json(destination, report)
        counts = {state: sum(c["status"] == state for c in report["cases"])
                  for state in sorted({c["status"] for c in report["cases"]})}
        print(f'{function["name"]}: {counts}; report: {destination}; SHA256: {file_hash(destination)}', flush=True)
        if args.expect_mismatch:
            success &= (counts.get("mismatch", 0) > 0 and set(counts) <= {"corpus_pass", "mismatch"}
                        and report["artifacts_unchanged"])
        else:
            success &= report["status"] == "corpus_pass"
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())

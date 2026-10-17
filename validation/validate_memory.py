"""Differential validation for reviewed memory routines and an overlap mutation."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from importlib.metadata import version
from pathlib import Path
import platform
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.daodecomp.harness import compare, file_hash, load_json, write_json
from validation.memory_cases import cases as memory_cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, default=ROOT / "gamedata/bin_ship/DAOrigins.exe")
    parser.add_argument("--build-dir", type=Path, default=ROOT / "build")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports/memory")
    parser.add_argument("--suite", choices=("public", "heldout", "all"), default="public")
    parser.add_argument("--function", action="append")
    parser.add_argument("--jobs", type=int, choices=range(1, 5), default=1)
    parser.add_argument("--expect-mismatch", action="store_true")
    args = parser.parse_args()
    exe = "dao_memory_mutant" if args.expect_mismatch else "dao_memory_runner"
    executable = args.build_dir.resolve() / (exe + (".exe" if sys.platform == "win32" else ""))
    if not executable.is_file() or not args.binary.is_file():
        parser.error("build the memory runner and provide the original binary first")
    registry = load_json(ROOT / "analysis/functions.json")
    selected = [f for f in registry["functions"] if f.get("backend") == "memory-001"
                and f["status"] in ("implemented", "corpus_pass", "reviewed", "integrated")]
    if args.function and not set(args.function) <= {f["name"] for f in selected}:
        parser.error("unknown or unimplemented memory function")
    selected = [f for f in selected if (not args.function or f["name"] in args.function)
                and (not args.expect_mismatch or f["name"] == "fn_00061fa0")]
    if not selected or (args.expect_mismatch and args.suite != "public"):
        parser.error("no functions selected, or negative control requested outside public suite")

    def validate(function):
        suites = ("public", "heldout") if args.suite == "all" else (args.suite,)
        cases = [c for suite in suites for c in memory_cases(function["name"], suite)]
        suffix = "-mutant" if args.expect_mismatch else "-" + args.suite
        case_path = args.report_dir / (function["name"] + suffix + "-cases.json")
        write_json(case_path, cases)
        runner = ROOT / "validation/memory_runner.py"
        oracle = [sys.executable, str(runner), "original", str(args.binary.resolve())]
        candidate = [sys.executable, str(runner), "candidate", str(executable)]
        artifacts = [args.binary, executable, case_path, Path(__file__), runner,
                     ROOT / "validation/memory_cases.py", ROOT / "validation/memory_native_runner.cpp",
                     ROOT / "tools/daodecomp/harness.py", ROOT / "tools/daodecomp/leaf.py",
                     ROOT / "tools/daodecomp/memory.py", ROOT / "tools/daodecomp/pe.py",
                     ROOT / "analysis/functions.json", ROOT / "analysis/reference-build.json",
                     ROOT / function["contract"], ROOT / "CMakeLists.txt", ROOT / "requirements-validation.txt",
                     args.build_dir / "CMakeCache.txt", *sorted((ROOT / "include/dao").rglob("*.hpp")),
                     *sorted((ROOT / "src").rglob("*.cpp"))]
        if (args.build_dir / "compile_commands.json").exists():
            artifacts.append(args.build_dir / "compile_commands.json")
        started = time.monotonic()
        report = compare(load_json(ROOT / function["contract"]), cases, oracle, candidate, repeats=2, artifacts=artifacts)
        report.update(elapsed_seconds=round(time.monotonic() - started, 3), suite=args.suite,
                      suite_case_counts={s: sum(c["id"].startswith(s + "-") for c in cases) for s in ("public", "heldout")},
                      backend_versions={"unicorn": version("unicorn"), "python": platform.python_version()},
                      native_windows_validated=False,
                      scope="Guarded Unicorn x86 slice versus native C++; full arena and normalized return; corpus evidence only")
        destination = args.report_dir / (function["name"] + suffix + ".json")
        write_json(destination, report)
        counts = {s: sum(c["status"] == s for c in report["cases"]) for s in sorted({c["status"] for c in report["cases"]})}
        print(f'{function["name"]}: {counts}; report: {destination}; SHA256: {file_hash(destination)}', flush=True)
        if args.expect_mismatch:
            return counts.get("mismatch", 0) > 0 and set(counts) <= {"corpus_pass", "mismatch"} and report["artifacts_unchanged"]
        return report["status"] == "corpus_pass"

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        return 0 if all(list(pool.map(validate, selected))) else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Validate the bounded disjoint linked-structure packet against the pinned original."""
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
from validation.linked_structure_cases import FUNCTIONS, cases, negative_cases

BACKEND = "linked-structures-001"
PIPELINE_STATUSES = {"contracted", "implemented", "corpus_pass", "reviewed", "integrated"}


def validate_function(function, *, binary, executable, build_dir, report_dir, suite, expect_mismatch):
    name = function["name"]
    selected_cases = negative_cases(name) if expect_mismatch else [
        case for selected_suite in (("public", "heldout") if suite == "all" else (suite,))
        for case in cases(name, selected_suite)
    ]
    suffix = "-mutant" if expect_mismatch else "-" + suite
    case_path = report_dir / (name + suffix + "-cases.json")
    write_json(case_path, selected_cases)
    runner = ROOT / "validation/linked_structure_runner.py"
    oracle = [sys.executable, str(runner), "original", str(binary.resolve())]
    candidate = [sys.executable, str(runner), "candidate", str(executable.resolve())]
    artifacts = [binary, executable, case_path, Path(__file__), runner,
                 ROOT / "validation/linked_structure_cases.py",
                 ROOT / "validation/linked_structure_native_runner.cpp",
                 ROOT / "tests/test_linked_structures.py",
                 ROOT / "tools/daodecomp/harness.py", ROOT / "tools/daodecomp/leaf.py",
                 ROOT / "tools/daodecomp/memory.py", ROOT / "tools/daodecomp/pe.py",
                 ROOT / "analysis/functions.json", ROOT / "analysis/reference-build.json",
                 ROOT / function["contract"], ROOT / function["source"], ROOT / "CMakeLists.txt",
                 ROOT / "requirements-validation.txt", build_dir / "CMakeCache.txt",
                 *sorted((ROOT / "include/dao").rglob("*.hpp")),
                 *sorted((ROOT / "src").rglob("*.cpp"))]
    compile_commands = build_dir / "compile_commands.json"
    if compile_commands.exists():
        artifacts.append(compile_commands)
    started = time.monotonic()
    report = compare(load_json(ROOT / function["contract"]), selected_cases,
                     oracle, candidate, repeats=2, artifacts=artifacts)
    report.update(elapsed_seconds=round(time.monotonic() - started, 3), suite=suite,
                  suite_case_counts={key: sum(case["id"].startswith(key + "-") for case in selected_cases)
                                     for key in ("public", "heldout")},
                  backend_versions={"unicorn": version("unicorn"), "python": platform.python_version()},
                  native_windows_validated=False,
                  scope="Guarded original x86 leaf versus native C++; exact conditional dword footprints, raw full EAX, conditional ECX observation and complete 512-byte arena; bounded corpus evidence only")
    destination = report_dir / (name + suffix + ".json")
    write_json(destination, report)
    counts = {state: sum(row["status"] == state for row in report["cases"])
              for state in sorted({row["status"] for row in report["cases"]})}
    print(f"{name}: {counts}; report: {destination}; SHA256: {file_hash(destination)}", flush=True)
    if expect_mismatch:
        return (counts.get("mismatch", 0) > 0 and set(counts) <= {"corpus_pass", "mismatch"}
                and report["artifacts_unchanged"])
    return report["status"] == "corpus_pass"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, default=ROOT / "gamedata/bin_ship/DAOrigins.exe")
    parser.add_argument("--build-dir", type=Path, default=ROOT / "build")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports/linked-structures")
    parser.add_argument("--suite", choices=("public", "heldout", "all"), default="public")
    parser.add_argument("--function", action="append")
    parser.add_argument("--jobs", type=int, choices=range(1, 5), default=1)
    parser.add_argument("--expect-mismatch", action="store_true")
    args = parser.parse_args()
    executable_name = "dao_linked_structure_mutant" if args.expect_mismatch else "dao_linked_structure_runner"
    executable = args.build_dir.resolve() / (executable_name + (".exe" if sys.platform == "win32" else ""))
    if not executable.is_file() or not args.binary.is_file():
        parser.error("build the linked-structure runner and provide the pinned original binary first")
    functions = [function for function in load_json(ROOT / "analysis/functions.json")["functions"]
                 if function.get("backend") == BACKEND and function["status"] in PIPELINE_STATUSES
                 and function["name"] in FUNCTIONS]
    if args.function and not set(args.function) <= {function["name"] for function in functions}:
        parser.error("unknown or uncontracted linked-structure function")
    selected = [function for function in functions
                if (not args.function or function["name"] in args.function)]
    if not selected or (args.expect_mismatch and args.suite != "public"):
        parser.error("no functions selected, or negative control requested outside public suite")

    def run(function):
        return validate_function(function, binary=args.binary, executable=executable,
                                 build_dir=args.build_dir.resolve(), report_dir=args.report_dir,
                                 suite=args.suite, expect_mismatch=args.expect_mismatch)

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        return 0 if all(pool.map(run, selected)) else 1


if __name__ == "__main__":
    raise SystemExit(main())

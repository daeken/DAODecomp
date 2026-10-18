"""Validate the characterized indexed-store slices against the pinned original."""
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
from tools.daodecomp.batch import compare_batch
from validation.indexed_field_cases import FIELD_SPECS, NEGATIVE_NAMES, cases, negative_cases

BACKEND = "indexed-stores-001"
PIPELINE_STATUSES = {"contracted", "implemented", "corpus_pass", "reviewed", "integrated"}


def validate_function(function, *, binary, executable, build_dir, report_dir, suite, expect_mismatch, execution="single", batch_size=128):
    name = function["name"]
    selected_cases = negative_cases(name) if expect_mismatch else [
        case for selected_suite in (("public", "heldout") if suite == "all" else (suite,))
        for case in cases(name, selected_suite)]
    suffix = "-mutant" if expect_mismatch else "-" + suite
    case_path = report_dir / (name + suffix + "-cases.json")
    write_json(case_path, selected_cases)
    runner = ROOT / "validation/indexed_field_runner.py"
    oracle = [sys.executable, str(runner), "original", str(binary.resolve())]
    candidate = [sys.executable, str(runner), "candidate", str(executable.resolve())]
    artifacts = [binary, executable, case_path, Path(__file__), runner,
                 ROOT / "validation/indexed_field_cases.py",
                 ROOT / "validation/indexed_field_native_runner.cpp",
                 ROOT / "validation/indexed_field_mutant.hpp",
                 ROOT / "tools/freeze_indexed_fields_pair.py",
                 ROOT / "tools/daodecomp/harness.py", ROOT / "tools/daodecomp/leaf.py",
                 ROOT / "tools/daodecomp/memory.py", ROOT / "tools/daodecomp/pe.py",
                 ROOT / "analysis/functions.json", ROOT / "analysis/reference-build.json",
                 ROOT / function["contract"], ROOT / "CMakeLists.txt", ROOT / "requirements-validation.txt",
                 build_dir / "CMakeCache.txt",
                 *sorted((ROOT / "include/dao").rglob("*.hpp")),
                 *sorted((ROOT / "src").rglob("*.cpp"))]
    if execution == "batch":
        runner = ROOT / "validation/indexed_field_batch_runner.py"
        oracle = [sys.executable, str(runner), "original", str(binary.resolve())]
        candidate = [sys.executable, str(runner), "candidate", str(executable.resolve())]
        artifacts += [ROOT / "tools/daodecomp/batch.py", runner,
                      ROOT / "validation/indexed_field_batch_native.cpp"]
    compile_commands = build_dir / "compile_commands.json"
    if compile_commands.exists():
        artifacts.append(compile_commands)
    started = time.monotonic()
    comparison = compare_batch if execution == "batch" else compare
    options = {"batch_size": batch_size} if execution == "batch" else {}
    report = comparison(load_json(ROOT / function["contract"]), selected_cases,
                        oracle, candidate, repeats=2, artifacts=artifacts, **options)
    report.update(elapsed_seconds=round(time.monotonic() - started, 3), suite=suite,
                  suite_case_counts={key: sum(case["id"].startswith(key + "-") for case in selected_cases)
                                     for key in ("public", "heldout")},
                  backend_versions={"unicorn": version("unicorn"), "python": platform.python_version()},
                  native_windows_validated=False,
                  scope="Existing guarded memory backend; exact indexed integer byte/word/dword access and complete 512-byte arena; emulator corpus evidence only")
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
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports/indexed-fields")
    parser.add_argument("--suite", choices=("public", "heldout", "all"), default="public")
    parser.add_argument("--function", action="append")
    parser.add_argument("--jobs", type=int, choices=range(1, 5), default=1)
    parser.add_argument("--expect-mismatch", action="store_true")
    parser.add_argument("--execution", choices=("single", "batch"), default="single",
                        help="Opt-in POSIX fresh-child batching; single remains the reference/fallback")
    parser.add_argument("--batch-size", type=int, choices=range(1,129), default=128)
    args = parser.parse_args()
    exe_name = "dao_indexed_field_mutant" if args.expect_mismatch else "dao_indexed_field_runner"
    if args.execution == "batch":
        if sys.platform == "win32":
            parser.error("batch execution requires POSIX; use --execution single")
        suffix = ".dylib" if sys.platform == "darwin" else ".so"
        exe_name = "libdao_indexed_field_batch" + ("_mutant" if args.expect_mismatch else "")
        executable = args.build_dir.resolve() / (exe_name + suffix)
    else:
        executable = args.build_dir.resolve() / (exe_name + (".exe" if sys.platform == "win32" else ""))
    if not executable.is_file() or not args.binary.is_file():
        parser.error("build the indexed-store runner and provide the pinned original binary first")
    functions = [f for f in load_json(ROOT / "analysis/functions.json")["functions"]
                 if f.get("backend") == BACKEND and f["status"] in PIPELINE_STATUSES
                 and f["name"] in FIELD_SPECS and f.get("recovery_group") == "indexed-fields-002"]
    if args.function and not set(args.function) <= {f["name"] for f in functions}:
        parser.error("unknown or uncontracted indexed-store function")
    selected = [f for f in functions if (not args.function or f["name"] in args.function)
                and (not args.expect_mismatch or f["name"] in NEGATIVE_NAMES)]
    if not selected or (args.expect_mismatch and args.suite != "public"):
        parser.error("no functions selected, or negative control requested outside public suite")

    def run(function):
        return validate_function(function, binary=args.binary, executable=executable,
                                 build_dir=args.build_dir.resolve(), report_dir=args.report_dir,
                                 suite=args.suite, expect_mismatch=args.expect_mismatch,
                                 execution=args.execution, batch_size=args.batch_size)

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        return 0 if all(pool.map(run, selected)) else 1


if __name__ == "__main__":
    raise SystemExit(main())

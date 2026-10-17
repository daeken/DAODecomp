"""Run the deterministic acceptance checks and publish evidence only on success."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
MAX_JOBS = 4
DEFAULT_TIMEOUT = 3600


def is_windows_platform():
    return os.name == "nt"


def build_commands(build_dir, output_dir, jobs, windows=None):
    """Return ordered (name, argv, cwd, log) steps, with platform-aware CMake paths."""
    build_dir, output_dir = Path(build_dir).resolve(), Path(output_dir).resolve()
    windows = is_windows_platform() if windows is None else windows
    if windows:
        raise ValueError("full checkpoint is unavailable on Windows until both frozen validators accept a separate multi-config executable and CMakeCache path")
    config = "RelWithDebInfo"
    build_command = ["cmake", "--build", str(build_dir), "--config", config, "--parallel", str(jobs)]
    test_command = ["ctest", "--test-dir", str(build_dir), "--output-on-failure"]
    demo_dir = build_dir
    py = sys.executable
    common = ["--binary", str(ROOT / "gamedata/bin_ship/DAOrigins.exe"), "--build-dir", str(demo_dir)]
    return [
        ("configure", ["cmake", "-S", str(ROOT), "-B", str(build_dir), "-DCMAKE_BUILD_TYPE=" + config], ROOT),
        ("build", build_command, ROOT), ("unittest", [py, "-m", "unittest", "discover", "-s", "tests", "-v"], ROOT),
        ("ctest", test_command, ROOT),
        ("demo_good", [py, str(ROOT / "examples/synthetic/demo.py"), "--build-dir", str(demo_dir)], ROOT),
        ("demo_mutant", [py, str(ROOT / "examples/synthetic/demo.py"), "--expect-mismatch", "--build-dir", str(demo_dir)], ROOT),
        ("scalar_all", [py, str(ROOT / "validation/validate_leaves.py"), "--suite", "all", "--jobs", str(jobs), "--report-dir", str(output_dir / "reports/scalar"), *common], ROOT),
        ("scalar_negative", [py, str(ROOT / "validation/validate_leaves.py"), "--expect-mismatch", "--report-dir", str(output_dir / "reports/scalar"), *common], ROOT),
        ("memory_all", [py, str(ROOT / "validation/validate_memory.py"), "--suite", "all", "--jobs", str(jobs), "--report-dir", str(output_dir / "reports/memory"), *common], ROOT),
        ("memory_negative", [py, str(ROOT / "validation/validate_memory.py"), "--expect-mismatch", "--report-dir", str(output_dir / "reports/memory"), *common], ROOT),
        ("object_counters_all", [py, str(ROOT / "validation/validate_object_counters.py"), "--suite", "all", "--jobs", str(jobs), "--report-dir", str(output_dir / "reports/object-counters"), *common], ROOT),
        ("object_counters_negative", [py, str(ROOT / "validation/validate_object_counters.py"), "--expect-mismatch", "--report-dir", str(output_dir / "reports/object-counters"), *common], ROOT),
        ("indexed_stores_all", [py, str(ROOT / "validation/validate_indexed_stores.py"), "--suite", "all", "--jobs", str(jobs), "--report-dir", str(output_dir / "reports/indexed-stores"), *common], ROOT),
        ("indexed_stores_negative", [py, str(ROOT / "validation/validate_indexed_stores.py"), "--expect-mismatch", "--report-dir", str(output_dir / "reports/indexed-stores"), *common], ROOT),
    ]


def publication_paths(output_dir):
    """Derive accepted positive and negative report paths from current registry/backends."""
    registry = json.loads((ROOT / "analysis/functions.json").read_text())
    positives, negatives = [], []
    active_object_counters = False
    active_indexed_stores = False
    for function in registry["functions"]:
        status = function.get("status")
        if status not in {"implemented", "corpus_pass", "reviewed", "integrated"}:
            continue
        backend = function.get("backend", "scalar")
        if backend == "scalar":
            positives.append(output_dir / "reports/scalar" / (function["name"] + "-all.json"))
            if function["name"] == "bit_mask_or_all":
                negatives.append(output_dir / "reports/scalar/bit_mask_or_all-mutant.json")
        elif backend == "memory-001":
            positives.append(output_dir / "reports/memory" / (function["name"] + "-all.json"))
            if function["name"] == "fn_00061fa0":
                negatives.append(output_dir / "reports/memory/fn_00061fa0-mutant.json")
        elif backend == "object-counters-001":
            active_object_counters = True
            positives.append(output_dir / "reports/object-counters" / (function["name"] + "-all.json"))
            if function["name"] == "fn_00061f40":
                negatives.append(output_dir / "reports/object-counters/fn_00061f40-mutant.json")
        elif backend == "indexed-stores-001":
            active_indexed_stores = True
            positives.append(output_dir / "reports/indexed-stores" / (function["name"] + "-all.json"))
            if function["name"] == "fn_00347d10":
                negatives.append(output_dir / "reports/indexed-stores/fn_00347d10-mutant.json")
        else:
            raise ValueError(f"unsupported validation backend for implemented function {function['name']}: {backend}")
    expected_negative_controls = 2 + int(active_object_counters) + int(active_indexed_stores)
    if not positives or len(negatives) != expected_negative_controls:
        raise ValueError("registry lacks an expected scalar, memory, or active backend negative-control function")
    return positives, negatives


def validate_record_path(path):
    path = Path(path).resolve()
    allowed = (ROOT / "analysis/validation").resolve()
    if path.parent != allowed or path.suffix != ".json" or path.exists():
        raise ValueError("--record must be a new .json file directly under analysis/validation")
    return path


def validate_output_path(path):
    path = Path(path).resolve()
    reports = (ROOT / "reports").resolve()
    if path == reports or reports not in path.parents:
        raise ValueError("--output-dir must be a new directory under the repository reports/ directory")
    return path


def invoke(runner, argv, timeout):
    try:
        result = runner(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=False, timeout=timeout)
        return result.returncode, result.stdout or ""
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        return 124, output + f"\nTimed out after {timeout} seconds\n"
    except Exception as exc:
        return 127, f"{type(exc).__name__}: {exc}\n"


def run_checkpoint(build_dir, output_dir, record_path, jobs, *, timeout=DEFAULT_TIMEOUT, runner=subprocess.run):
    build_dir, output_dir = Path(build_dir).resolve(), validate_output_path(output_dir)
    record_path = validate_record_path(record_path)
    if jobs not in range(1, MAX_JOBS + 1):
        raise ValueError(f"jobs must be between 1 and {MAX_JOBS}")
    if timeout < 1:
        raise ValueError("timeout must be a positive number of seconds")
    if is_windows_platform():
        raise ValueError("full checkpoint is unavailable on Windows until both frozen validators accept separate executable and CMakeCache paths")
    if output_dir.exists():
        raise FileExistsError(f"output directory already exists: {output_dir}")
    output_dir.mkdir(parents=True)
    (output_dir / "logs").mkdir()
    checkpoint = {"schema_version": 1, "status": "running", "started_at": time.time(), "jobs": jobs, "steps": []}
    checkpoint_path = output_dir / "checkpoint.json"

    def save():
        checkpoint["updated_at"] = time.time()
        checkpoint_path.write_text(json.dumps(checkpoint, indent=2) + "\n")

    save()
    for name, argv, cwd in build_commands(build_dir, output_dir, jobs):
        started = time.monotonic()
        log = output_dir / "logs" / (name + ".log")
        try:
            result = runner(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=False, timeout=timeout)
            output = result.stdout or ""
            code = result.returncode
        except subprocess.TimeoutExpired as exc:
            output = exc.stdout or ""
            if isinstance(output, bytes):
                output = output.decode("utf-8", errors="replace")
            output += f"\nTimed out after {timeout} seconds\n"
            code = 124
        except Exception as exc:
            output, code = f"{type(exc).__name__}: {exc}\n", 127
        log.write_text(output)
        step = {"name": name, "argv": argv, "exit_code": code, "elapsed_seconds": round(time.monotonic() - started, 3), "log": str(log)}
        checkpoint["steps"].append(step)
        if code:
            checkpoint.update(status="failed", failed_step=name, finished_at=time.time())
            save()
            return 1
        save()

    temporary_record = record_path.with_name("." + record_path.stem + ".checkpoint-tmp.json")
    readme = ROOT / "README.md"
    readme_original = None
    active_step = "record_validation"
    owns_temporary_record = False
    try:
        readme_original = readme.read_bytes()
        if temporary_record.exists():
            raise FileExistsError(f"temporary record already exists: {temporary_record}")
        positives, negatives = publication_paths(output_dir)
        argv = [sys.executable, str(ROOT / "tools/record_validation.py")]
        for path in positives:
            argv += ["--report", str(path)]
        for path in negatives:
            argv += ["--negative-report", str(path)]
        argv += ["--output", str(temporary_record)]
        started = time.monotonic()
        owns_temporary_record = True
        code, output = invoke(runner, argv, timeout)
        log = output_dir / "logs/record_validation.log"
        log.write_text(output)
        checkpoint["steps"].append({"name": active_step, "argv": argv, "exit_code": code,
                                    "elapsed_seconds": round(time.monotonic() - started, 3), "log": str(log)})
        if code:
            raise RuntimeError(f"record_validation exited {code}")
        recorded = json.loads(temporary_record.read_text())
        evidence_statuses = [{"function_id": item["function_id"], "status": item["status"],
                              "negative_control": item["negative_control"]} for item in recorded["records"]]
        active_step = "update_progress"
        argv = [sys.executable, str(ROOT / "tools/update_progress.py")]
        started = time.monotonic()
        code, output = invoke(runner, argv, timeout)
        log = output_dir / "logs/update_progress.log"
        log.write_text(output)
        checkpoint["steps"].append({"name": active_step, "argv": argv, "exit_code": code,
                                    "elapsed_seconds": round(time.monotonic() - started, 3), "log": str(log)})
        if code:
            raise RuntimeError(f"update_progress exited {code}")
        temporary_record.replace(record_path)
    except Exception as exc:
        if owns_temporary_record:
            temporary_record.unlink(missing_ok=True)
        if active_step == "update_progress" and readme_original is not None:
            readme.write_bytes(readme_original)
        checkpoint.update(status="failed", failed_step=active_step, failure=f"{type(exc).__name__}: {exc}",
                          finished_at=time.time())
        save()
        return 1
    checkpoint.update(status="passed", finished_at=time.time(), published_record=str(record_path),
                       reports=[str(p) for p in positives + negatives], artifacts_unchanged=True,
                       evidence_status="emulator_corpus_agreement", evidence_records=evidence_statuses,
                       proof=False, native_windows_validated=False)
    save()
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", type=Path, default=ROOT / "build")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--jobs", type=int, choices=range(1, MAX_JOBS + 1), default=min(4, os.cpu_count() or 1))
    parser.add_argument("--record", type=Path, required=True, help="new analysis/validation/*.json path")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="per-step timeout in seconds (default: 3600)")
    args = parser.parse_args()
    try:
        return run_checkpoint(args.build_dir, args.output_dir, args.record, args.jobs, timeout=args.timeout)
    except (ValueError, FileExistsError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())

"""Compare actual x86 fixture instructions against compiled native C++."""
import argparse
import hashlib
import itertools
from importlib.metadata import version
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.daodecomp.harness import compare, load_json, write_json


def corpus():
    triples = list(itertools.product((0, 1, 0xFFFFFFFF), repeat=3))
    for index in range(32):
        raw = hashlib.sha256(f"DAODecomp-synthetic-v1:{index}".encode()).digest()
        triples.append(tuple(int.from_bytes(raw[i:i+4], "little") for i in (0, 4, 8)))
    return [{"id": f"case-{i:03}", "inputs": dict(zip(("value", "saturations", "delta"), values))}
            for i, values in enumerate(triples)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-dir", type=Path, default=ROOT / "build")
    parser.add_argument("--expect-mismatch", action="store_true")
    args = parser.parse_args()
    suffix = ".exe" if sys.platform == "win32" else ""
    executable = args.build_dir.resolve() / (("synthetic_mutant" if args.expect_mismatch else "synthetic_candidate") + suffix)
    if not executable.is_file():
        parser.error(f"build the C++ example first: {executable}")
    folder = Path(__file__).resolve().parent
    oracle = [sys.executable, str(folder / "runner.py"), "original"]
    candidate = [sys.executable, str(folder / "runner.py"), "candidate", str(executable)]
    cases = corpus()
    write_json(ROOT / "reports/synthetic-cases.json", cases)
    report = compare(load_json(folder / "contract.json"), cases, oracle, candidate,
                     artifacts=[folder / "original_x86.py", folder / "runner.py", executable,
                                folder / "candidate.cpp", folder / "contract.json", Path(__file__),
                                ROOT / "tools/daodecomp/harness.py"])
    report["backend_versions"] = {"unicorn": version("unicorn")}
    destination = ROOT / ("reports/synthetic-mutant.json" if args.expect_mismatch else "reports/synthetic.json")
    write_json(destination, report)
    counts = {state: sum(r["status"] == state for r in report["cases"])
              for state in sorted({r["status"] for r in report["cases"]})}
    print(f"Synthetic x86 -> native C++: {counts}; report: {destination}")
    if args.expect_mismatch:
        return 0 if counts.get("mismatch", 0) > 0 and set(counts) <= {"corpus_pass", "mismatch"} and report["artifacts_unchanged"] else 1
    return 0 if report["status"] == "corpus_pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

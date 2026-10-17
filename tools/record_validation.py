"""Publish compact evidence only from unchanged, independently passing reports.

Original assets and raw reports remain local. This verifies their hashes now;
the README updater subsequently checks the recorded tracked-input hashes.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.daodecomp.harness import digest, file_hash, load_json, write_json


def record_report(root, path, function, *, negative=False):
    root, path = Path(root).resolve(), Path(path).resolve()
    raw = path.read_bytes()
    report = json.loads(raw)
    counts = dict(Counter(c["status"] for c in report["cases"]))
    valid = (counts.get("mismatch", 0) > 0 and set(counts) <= {"mismatch", "corpus_pass"}) if negative else (
        report["status"] == "corpus_pass" and set(counts) == {"corpus_pass"} and counts["corpus_pass"] > 0)
    if (not valid or report["schema_version"] != 1 or report["kind"] != "game" or report["proof"] is not False
            or report["function_id"] != function["id"] or report["artifacts_unchanged"] is not True
            or type(report["repeats"]) is not int or report["repeats"] < 2
            or report.get("native_windows_validated") is not False):
        raise ValueError("report is not acceptable emulator corpus evidence")
    artifacts = {}
    for name, expected in report["artifacts_sha256"].items():
        artifact = Path(name)
        artifact = artifact if artifact.is_absolute() else root / artifact
        relative = artifact.resolve().relative_to(root).as_posix()
        if file_hash(artifact) != expected:
            raise ValueError(f"stale artifact: {relative}")
        artifacts[relative] = expected
    required = {function["source"], function["contract"], "analysis/functions.json", "analysis/reference-build.json"}
    if not required <= artifacts.keys():
        raise ValueError("missing required evidence artifacts")
    contract = load_json(root / function["contract"])
    if contract["function_id"] != function["id"] or digest(contract) != report["contract_sha256"]:
        raise ValueError("contract identity or canonical hash mismatch")
    report_hash = hashlib.sha256(raw).hexdigest()
    if file_hash(path) != report_hash:
        raise ValueError("report changed during recording")
    return {"function_id": function["id"], "status": report["status"], "negative_control": negative,
            "report": path.relative_to(root).as_posix(), "report_sha256": report_hash,
            "case_counts": counts, "repeats_per_side": report["repeats"],
            "contract_canonical_sha256": report["contract_sha256"], "corpus_canonical_sha256": report["corpus_sha256"],
            "artifacts_unchanged": True, "artifacts_sha256": artifacts,
            "host": report["host"], "backend_versions": report.get("backend_versions", {}),
            "scope": report.get("scope"), "elapsed_seconds": report.get("elapsed_seconds"),
            "suite_case_counts": report.get("suite_case_counts", {})}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, action="append", default=[])
    parser.add_argument("--negative-report", type=Path, action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.report:
        parser.error("at least one positive report is required")
    functions = {f["id"]: f for f in load_json(ROOT / "analysis/functions.json")["functions"]}
    records = []
    for negative, paths in [(False, args.report), (True, args.negative_report)]:
        for path in paths:
            report = json.loads(path.read_text())
            records.append(record_report(ROOT, path, functions[report["function_id"]], negative=negative))
    write_json(args.output, {"schema_version": 1, "date": datetime.now(timezone.utc).date().isoformat(),
                            "evidence_level": "emulator_corpus_agreement", "proof": False,
                            "native_windows_validated": False, "records": records})
    print(f"Recorded {len(records)} verified reports in {args.output}")


if __name__ == "__main__":
    main()

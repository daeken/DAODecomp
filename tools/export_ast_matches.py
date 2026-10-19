"""Bridge retained AST results to the reviewed free-source export report.

Only metadata is projected: redundant requested module/RVA fields are checked
then omitted from private copies. Sources, objects, build receipts and comparison
results are unchanged. The existing exporter independently rechecks every row.
"""
import argparse
import copy
import json
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import export_native_sources as exporter


def equal(left, right):
    # JSON equality must distinguish bool/int and int/float.
    return json.dumps(left, sort_keys=True) == json.dumps(right, sort_keys=True)


def require(condition, reason):
    exporter.require(condition, reason)


def bridge_record(record, output, original):
    """Return a supported row after a fresh retained-artifact comparison."""
    rva = record["rva"]
    require(type(rva) is int and 0 <= rva <= 0xffffffff, "AST identity type")
    require(record["status"] == "exact_object_match", "AST not exact")
    source = Path(record["accepted_source"])
    source_raw = source.read_bytes()
    source_hash = exporter.digest(source_raw)
    require(source_hash == record["accepted_source_sha256"], "AST source binding")
    attempts = [a for a in record["attempts"] if a.get("source_sha256") == source_hash]
    require(len(attempts) == 1, "ambiguous AST accepted attempt")
    attempt = attempts[0]
    require(attempt.get("bound") is True and attempt["status"] == "exact_object_match", "AST attempt not exact")
    summary_path = Path(attempt["summary"])
    folder = summary_path.parent
    require(source.resolve() == (folder.parent / "candidate.cpp").resolve(), "AST candidate path")
    report = exporter.read_json(summary_path)
    identities = exporter.read_json(folder / "identities.json")
    require(equal(report["requested"], identities["requested"]), "AST requested binding")
    require(set(report["requested"]) == {str(rva)}, "AST requested identity")
    requested = report["requested"][str(rva)]
    require(type(requested.get("rva")) is int and requested["rva"] == rva and
            requested.get("module_sha256") == exporter.MODULE_SHA256, "AST redundant identity")
    require(equal(report["build"], exporter.read_json(folder / "run.json")), "AST build binding")
    require(type(report["build"]["exit_code"]) is int, "AST exit code type")
    if "object_path" in report:
        require(Path(report["object_path"]).resolve() == (folder / "candidate.obj").resolve(), "AST object path")
    require(equal(identities["symbols"], report["symbol_addresses"]), "AST symbol binding")
    baseline = record["baseline"]
    require(type(baseline["rva"]) is int and baseline["rva"] == rva, "AST baseline identity")
    baseline_source = Path(baseline["source"])
    require(exporter.digest(baseline_source.read_bytes()) == baseline["source_sha256"], "AST baseline source binding")
    conversion_path = baseline_source.parent / "conversion.json"
    result_path = baseline_source.parent / "result.json"
    require(conversion_path.is_file() != result_path.is_file(), "ambiguous AST baseline provenance")
    if conversion_path.is_file():
        provenance = exporter.read_json(conversion_path)
        require(provenance["module_sha256"] == exporter.MODULE_SHA256, "AST conversion module")
        raw_name, expected_raw_hash = provenance["raw_export"], provenance["export_sha256"]
    else:
        provenance = exporter.read_json(result_path)
        require(Path(provenance["source"]).resolve() == baseline_source.resolve(), "AST baseline candidate path")
        require(type(provenance["baseline"]["rva"]) is int and provenance["baseline"]["rva"] == rva, "AST baseline raw identity")
        raw_name, expected_raw_hash = provenance["baseline"]["raw_export"], provenance["baseline"]["raw_export_sha256"]
    require(type(provenance["rva"]) is int and provenance["rva"] == rva and
            provenance["source_sha256"] == baseline["source_sha256"], "AST baseline provenance")
    raw_path = Path(raw_name)
    raw_hash = exporter.digest(raw_path.read_bytes())
    require(raw_hash == expected_raw_hash, "AST raw export binding")
    # Existing exporter owns all range, compiler, symbol and actual-byte checks.
    # Project only two redundant fields; do not synthesize comparison evidence.
    projected = copy.deepcopy(report)
    projected_identities = copy.deepcopy(identities)
    for container in (projected, projected_identities):
        del container["requested"][str(rva)]["module_sha256"]
        del container["requested"][str(rva)]["rva"]
    destination = Path(output) / f"{rva:08x}-{source_hash[:16]}"
    destination.mkdir(parents=True, exist_ok=False)
    for name in ("candidate.cpp", "candidate.obj", "run.json", "compiler.json"):
        (destination / name).write_bytes((folder / name).read_bytes())
    for name, value in (("summary.json", projected), ("identities.json", projected_identities)):
        (destination / name).write_text(json.dumps(value, sort_keys=True) + "\n")
    row = {"rva": rva, "source": str(source.resolve()),
           "baseline": {"raw_export": str(raw_path.resolve()), "raw_export_sha256": raw_hash},
           "measurement": {"status": "exact_object_match", "summary": str((destination / "summary.json").resolve()), "build": report["build"]},
           "ast_origin": {"summary": str(summary_path.resolve()), "summary_sha256": exporter.digest(summary_path.read_bytes()),
                          "identities_sha256": exporter.digest((folder / "identities.json").read_bytes())}}
    # Reject type substitutions even where the older exporter uses Python ==.
    _, _, checked_source = exporter.retained_free_match(row, original)
    require(checked_source == source_raw, "AST source changed")
    from rapid_object import compare
    actual = compare.compare_bytes(original, (destination / "candidate.obj").read_bytes(),
                                   {rva: projected["requested"][str(rva)]}, projected["symbol_addresses"],
                                   source_hash, projected["compiler"], exporter.MODULE_SHA256)
    require(equal(actual["functions"], projected["functions"]), "AST typed comparison binding")
    return row


def bridge(records, output, original):
    require(exporter.digest(original) == exporter.MODULE_SHA256, "original_module_binding")
    output = Path(output)
    require(not output.exists(), "bridge output already exists")
    output.mkdir(parents=True)
    rows, skipped, seen = [], {}, set()
    for record in records:
        if record.get("status") != "exact_object_match":
            status = record.get("status") or "missing_status"
            skipped[status] = skipped.get(status, 0) + 1
            continue
        require(type(record["rva"]) is int and record["rva"] not in seen, "duplicate AST identity")
        seen.add(record["rva"])
        rows.append(bridge_record(record, output, original))
    report = {"records": rows, "skipped": skipped}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True, help="AST report containing records")
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="New private staging directory")
    args = parser.parse_args()
    report = bridge(exporter.read_json(args.report)["records"], args.output, args.original.read_bytes())
    print(json.dumps({"verified_rows": len(report["records"]), "skipped": report["skipped"], "report": str(args.output / "report.json")}))


if __name__ == "__main__":
    main()

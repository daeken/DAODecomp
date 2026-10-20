"""Publish exact source snapshots of recorded native matches, without private data.

This exports retained evidence and can recheck free object reports before export.
Read-only database snapshots let the recovery workers continue running.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys


MODULE_SHA256 = "2346caee611002d4dff6ecef68eb315b63a37004dd98b39c11a9c26c0b45bfb3"
REPO = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_rows(root, table, status):
    db = sqlite3.connect((root / "queue.sqlite3").resolve().as_uri() + "?mode=ro", uri=True)
    try:
        return db.execute(
            f"SELECT rva,source,summary FROM {table} WHERE status=? ORDER BY rva", (status,)
        ).fetchall()
    finally:
        db.close()


def snapshot(native_root, object_root):
    groups = defaultdict(list)
    for root, table, status in (
        (native_root, "native_functions", "reccmp_matched"),
        (object_root, "object_results", "exact_object_match"),
    ):
        for rva, source, summary in read_rows(root, table, status):
            groups[(status, source, summary)].append(rva)
    files, functions, units, seen = {}, [], [], set()
    for (status, source, summary_path), rvas in sorted(groups.items()):
        raw = Path(source).read_bytes()
        report_raw = Path(summary_path).read_bytes()
        report = json.loads(report_raw)
        source_hash = digest(raw)
        if report["module_sha256"] != MODULE_SHA256 or source_hash != report["source_sha256"]:
            raise ValueError(f"source/module binding mismatch: {source}")
        native = status == "reccmp_matched"
        artifact_name, artifact_key = ("candidate.dll", "recompiled_sha256") if native else ("candidate.obj", "object_sha256")
        artifact_hash = digest((Path(summary_path).parent / artifact_name).read_bytes())
        if artifact_hash != report[artifact_key]:
            raise ValueError(f"compiled artifact binding mismatch: {summary_path}")
        if native and digest((Path(summary_path).parent / "candidate.pdb").read_bytes()) != report["pdb_sha256"]:
            raise ValueError(f"debug symbol binding mismatch: {summary_path}")
        filename = f"units/{min(rvas):08x}-{source_hash[:16]}.cpp"
        unit_id = f"{status}:{source_hash}"
        if filename in files and files[filename] != raw:
            raise ValueError("source filename collision")
        files[filename] = raw
        markers = {}
        for line_number, line in enumerate(raw.decode("utf-8").splitlines(), 1):
            marker = re.search(r"//\s*FUNCTION:\s*DAO\s+0x([0-9a-fA-F]+)", line)
            if marker:
                markers.setdefault(int(marker[1], 16) - 0x400000, line_number)
        unit = {
            "id": unit_id, "source": filename, "source_sha256": source_hash,
            "comparison_report_sha256": digest(report_raw),
            "compiled_artifact_sha256": artifact_hash,
            "matched_rvas": [f"0x{r:08x}" for r in sorted(rvas)],
        }
        if native:
            unit.update(reccmp_version=report["reccmp_version"],
                        pdb_sha256=report["pdb_sha256"])
            if "operand_guard_sha256" in report:
                unit["operand_guard_sha256"] = report["operand_guard_sha256"]
            if "tool_module_sha256" in report:
                unit["comparator_modules"] = report["tool_module_sha256"]
        else:
            unit.update(comparator_modules=report["implementation_sha256"],
                        compiler_version=report["compiler"]["file_version"],
                        compiler_sha256=report["compiler"]["sha256"],
                        compiler_flags=report["build"]["flags"])
        units.append(unit)
        for rva in sorted(rvas):
            if rva in seen:
                raise ValueError(f"duplicate matched identity: {rva:08x}")
            candidates = [f for f in report["functions"] if f["rva"] == rva]
            if len(candidates) != 1 or candidates[0]["status"] != status:
                raise ValueError(f"missing matching report entry: {rva:08x}")
            evidence = candidates[0]
            if native and (evidence["score"] != 1.0 or not evidence["complete_range_compared"] or evidence["unknowns"]):
                raise ValueError(f"incomplete native comparison: {rva:08x}")
            seen.add(rva)
            functions.append({
                "rva": f"0x{rva:08x}", "status": status, "unit": unit_id,
                "source": filename, "source_sha256": source_hash,
                "annotation_line": markers.get(rva),
            })
    functions.sort(key=lambda f: f["rva"])
    return {
        "schema_version": 1, "exported_at": datetime.now(timezone.utc).isoformat(),
        "module": "DAOrigins.exe", "module_sha256": MODULE_SHA256,
        "counts": dict(sorted(Counter(f["status"] for f in functions).items())),
        "matched_functions": len(functions), "translation_units": units, "functions": functions,
        "scope": "Snapshot of existing recorded compiled-function matches; not a linked replacement or a universal equivalence proof. Other functions in each unchanged translation unit may be unmatched.",
    }, files



SELECTED_COMPILER_SHA256 = "5f6489b0d211b14ae09d93d3fb58a7bce84d070287f008e06416c9baa5564219"
SELECTED_FLAGS = ["/c", "/O2", "/Ob1", "/Oy", "/Gy", "/Z7", "/Zl", "/GS-", "/GR-", "/EHsc"]


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def retained_symbol_bindings(object_path, requested, registry):
    """Bind only anchored source identities; generated EH nodes stay distinct."""
    from rapid_object.symbol_identity import bind_symbols
    return bind_symbols(Path(object_path).read_bytes(), requested, registry)


def retained_free_match(row, original):
    """Adapt either free report row, verifying retained artifacts without a build.

    The unchanged comparator independently repeats the complete comparison. Raw
    export identities and the mechanically decoded COFF names bind relocation
    targets; stored relocation maps are never accepted as overrides.
    """
    # Support both module imports and the documented direct script invocation.
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    from rapid_object import compare

    measurement = row.get("measurement", row)
    rva = row["rva"]
    summary_path = Path(measurement["summary"])
    folder = summary_path.parent
    report_raw = summary_path.read_bytes()
    report = json.loads(report_raw)
    source = Path(row["source"]).read_bytes()
    obj = (folder / "candidate.obj").read_bytes()
    build = read_json(folder / "run.json")
    compiler = read_json(folder / "compiler.json")
    identities = read_json(folder / "identities.json")
    raw_path = row.get("raw_export") or row["baseline"]["raw_export"]
    raw = read_json(raw_path)
    if "baseline" in row:
        require(digest(Path(raw_path).read_bytes()) == row["baseline"]["raw_export_sha256"], "raw_export_binding")
    else:
        conversion = read_json(Path(row["source"]).parent / "conversion.json")
        require(digest(Path(raw_path).read_bytes()) == conversion["export_sha256"], "raw_export_binding")
        require(conversion["source_sha256"] == digest(source), "conversion_source_binding")
    require(raw["module_sha256"] == MODULE_SHA256 and raw["rva"] == rva, "original_identity_binding")
    require(report["module_sha256"] == MODULE_SHA256, "module_binding")
    require(digest(source) == report["source_sha256"] == build["source_sha256"], "source_binding")
    require((folder / "candidate.cpp").read_bytes() == source, "build_source_binding")
    require(digest(obj) == report["object_sha256"] == build["object_sha256"], "object_binding")
    require(report["build"] == measurement["build"] == build, "build_receipt_binding")
    require(build["exit_code"] == 0 and build["module_sha256"] == MODULE_SHA256 and build["flags"] == SELECTED_FLAGS, "selected_build_binding")
    require(report["compiler"] == build["compiler"] == compiler and compiler["sha256"] == SELECTED_COMPILER_SHA256, "selected_compiler_binding")
    implementation = {name: digest((REPO / "rapid_object" / name).read_bytes()) for name in ("coff.py", "compare.py")}
    require(report["implementation_sha256"] == implementation, "comparator_binding")
    requested = {rva: {key: raw[key] for key in ("original_va", "ranges", "bytes_sha256")}}
    registry = {}
    for symbol in raw["symbols"]:
        if symbol.get("kind") not in ("function", "global"):
            continue
        va = symbol["original_va"]
        kind = "fn" if symbol["kind"] == "function" else "g"
        registry[f"{kind}_{va - 0x400000:08x}"] = va
    registry[f"fn_{rva:08x}"] = raw["original_va"]
    symbols = retained_symbol_bindings(folder / "candidate.obj", requested, registry)
    normalized = {str(key): value for key, value in requested.items()}
    require(report["requested"] == normalized == identities["requested"] and identities["module_sha256"] == MODULE_SHA256, "full_original_range_binding")
    require(report["symbol_addresses"] == symbols == identities["symbols"], "symbol_identity_binding")
    actual = compare.compare_bytes(original, obj, requested, symbols, digest(source), compiler, MODULE_SHA256)
    require(actual.get("functions") == report.get("functions") and not actual.get("error"), "recomparison_binding")
    entries = actual["functions"]
    require(len(entries) == 1 and entries[0]["rva"] == rva and entries[0]["status"] == "exact_object_match", "not_complete_exact_match")
    evidence = entries[0]
    require(evidence["original_bytes_sha256"] == raw["bytes_sha256"] == evidence["relocated_bytes_sha256"] and evidence["object_size"] == evidence["original_size"], "full_bytes_binding")
    text = source.decode("utf-8")
    require(not re.search(r"(?:/Users/|/home/|[A-Za-z]:\\)", text), "private_source_path")
    markers = [number for number, line in enumerate(text.splitlines(), 1) if re.search(r"//\s*FUNCTION:\s*DAO\s+0x%08x\b" % (rva + 0x400000), line, re.I)]
    require(len(markers) == 1, "source_annotation_identity")
    filename = f"units/{rva:08x}-{digest(source)[:16]}.cpp"
    unit_id = f"exact_object_match:{digest(source)}"
    unit = {"id": unit_id, "source": filename, "source_sha256": digest(source),
            "comparison_report_sha256": digest(report_raw), "compiled_artifact_sha256": digest(obj),
            "matched_rvas": [f"0x{rva:08x}"], "comparator_modules": implementation,
            "compiler_version": compiler["file_version"], "compiler_sha256": compiler["sha256"],
            "compiler_flags": build["flags"], "provenance": "retained_free_report_recompared"}
    function = {"rva": f"0x{rva:08x}", "status": "exact_object_match", "unit": unit_id,
                "source": filename, "source_sha256": digest(source), "annotation_line": markers[0],
                "original_ranges": [{key: rr[key] for key in ("start_rva", "end_rva_inclusive")} for rr in raw["ranges"]], "original_bytes_sha256": raw["bytes_sha256"]}
    return function, unit, source


def extend_snapshot(index, files, reports, original_path, *, eh_inputs=None):
    """Keep the existing snapshot first; deterministically add verified identities.

    Every reported match is checked, including duplicates. Rejected rows are
    accounted for locally and never silently counted as matches.
    """
    original = Path(original_path).read_bytes()
    require(digest(original) == MODULE_SHA256, "original_module_binding")
    index = json.loads(json.dumps(index))
    files = dict(files)
    seen = {function["rva"] for function in index["functions"]}
    audit = {"reports": len(set(map(str, reports))), "rows": 0, "reported_matches": 0,
             "verified_matches": 0, "added": 0, "duplicates_preserved": 0,
             "rejected": [], "not_reported_match": {}}
    skipped = Counter()
    for path in sorted(set(map(Path, reports))):
        for row in read_json(path)["records"]:
            audit["rows"] += 1
            status = row.get("measurement", {}).get("status", row.get("matching_status") or row.get("conversion_status") or row.get("repair_status"))
            if status not in ("exact_object_match", "exact_eh_graph_match"):
                skipped[status or "missing_status"] += 1
                continue
            audit["reported_matches"] += 1
            try:
                if status == "exact_eh_graph_match":
                    require(eh_inputs is not None, "EH export requires trusted input paths")
                    from rapid_object.eh_source_export import retained_match
                    function, unit, source = retained_match(row, original, eh_inputs)
                else:
                    function, unit, source = retained_free_match(row, original)
            except (OSError, ValueError, KeyError, TypeError) as exc:
                audit["rejected"].append({"report": str(path), "rva": row.get("rva"), "reason": str(exc)})
                continue
            audit["verified_matches"] += 1
            if function["rva"] in seen:
                audit["duplicates_preserved"] += 1
                continue
            require(function["source"] not in files or files[function["source"]] == source, "source_filename_collision")
            files[function["source"]] = source
            index["functions"].append(function)
            existing_units = [u for u in index["translation_units"] if u["id"] == unit["id"]]
            require(len(existing_units) <= 1, "duplicate_translation_unit_identity")
            if existing_units:
                require(existing_units[0] == unit, "translation_unit_binding_collision")
            else:
                index["translation_units"].append(unit)
            seen.add(function["rva"])
            audit["added"] += 1
    index["functions"].sort(key=lambda f: f["rva"])
    index["matched_functions"] = len(index["functions"])
    index["counts"] = dict(sorted(Counter(f["status"] for f in index["functions"]).items()))
    audit["not_reported_match"] = dict(sorted(skipped.items()))
    audit["rejected_reasons"] = dict(Counter(r["reason"] for r in audit["rejected"]))
    return index, files, audit

def publish(index, files, output):
    output.mkdir(parents=True, exist_ok=True)
    for filename, raw in files.items():
        target = output / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    (output / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    counts = index["counts"]
    lines = [
        "# Recovered native C++", "",
        f"**{index['matched_functions']:,} matching functions** in this published snapshot: "
        f"{counts.get('reccmp_matched', 0):,} reccmp matches and "
        f"{counts.get('exact_object_match', 0):,} exact COFF object matches and "
        f"{counts.get('exact_eh_graph_match', 0):,} complete main/EH graph matches.", "",
        f"Snapshot: {index['exported_at']}. The running local queue may be further ahead.", "",
        "Browse the functions below, or use the [machine-readable index](index.json). "
        "The C++ files are byte-for-byte copies of the compared translation units. "
        "Each can include other, **unmatched functions** and dependency declarations; "
        "only the RVAs listed in this index have recorded matches. Units are separate "
        "compiler inputs and can repeat declarations or function definitions; do not link "
        "every file together as a game executable.", "",
        "The compiler is VC8 x86 14.00.50727.762, run under Windows 11 ARM64 translation. "
        "These are compiled-function comparison results, not a running replacement game "
        "or proof for other compilers. The original compiler patch remains unknown.", "",
        "[Object workflow](../../../docs/object-recovery.md) · "
        "[Earlier reccmp workflow](../../../docs/reccmp-loop.md)", "",
        "Refresh from retained local results with:", "", "```sh",
        "python3 tools/export_native_sources.py", "```", "",
        "The exporter checks retained source and compiled artifact hashes. Free-report "
        "imports also bind the selected compiler and full original ranges, and repeat "
        "the exact object comparison. "
        "It publishes C++ and comparison identities only; private game bytes, build "
        "products and raw reports stay local. Source names use stable RVAs; inferred "
        "types and descriptive names in generated code remain provisional.", "",
        "| Function RVA | Comparison | C++ source |", "| --- | --- | --- |",
    ]
    for function in index["functions"]:
        kind = {"reccmp_matched": "reccmp", "exact_object_match": "Exact object", "exact_eh_graph_match": "Exact main/EH graph"}[function["status"]]
        anchor = f"#L{function['annotation_line']}" if function["annotation_line"] else ""
        lines.append(f"| `{function['rva']}` | {kind} | [{Path(function['source']).name}]({function['source']}{anchor}) |")
    (output / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-root", type=Path, default=REPO / "local/rapid-native")
    parser.add_argument("--object-root", type=Path, default=REPO / "local/rapid-object")
    parser.add_argument("--output", type=Path, default=REPO / "src/native/recovered")
    parser.add_argument("--free-report", type=Path, action="append", default=[])
    parser.add_argument("--original", type=Path)
    parser.add_argument("--eh-inputs", type=Path, help="Coordinator-owned inventory/compiler/static-library paths for full EH export")
    parser.add_argument("--audit", type=Path, help="Private import accounting, outside the publication tree")
    args = parser.parse_args()
    index, files = snapshot(args.native_root, args.object_root)
    if args.free_report:
        if not args.original or not args.audit:
            parser.error("--free-report requires --original and --audit")
        if args.audit.resolve().is_relative_to(args.output.resolve()):
            parser.error("private audit must be outside the publication tree")
        index, files, audit = extend_snapshot(index, files, args.free_report, args.original, eh_inputs=read_json(args.eh_inputs) if args.eh_inputs else None)
        args.audit.parent.mkdir(parents=True, exist_ok=True)
        args.audit.write_text(json.dumps(audit, indent=2) + "\n")
    publish(index, files, args.output)
    print(json.dumps({"matched_functions": index["matched_functions"], "counts": index["counts"], "source_files": len(files), "output": str(args.output)}))


if __name__ == "__main__":
    main()

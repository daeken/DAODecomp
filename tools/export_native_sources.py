"""Publish exact source snapshots of recorded native matches, without private data.

This exports existing evidence; it does not compare or accept new functions.
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
        f"{counts.get('exact_object_match', 0):,} exact COFF object matches.", "",
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
        "The exporter checks the retained source and compiled artifact hashes. "
        "It publishes C++ and comparison identities only; private game bytes, build "
        "products and raw reports stay local. Source names use stable RVAs; inferred "
        "types and descriptive names in generated code remain provisional.", "",
        "| Function RVA | Comparison | C++ source |", "| --- | --- | --- |",
    ]
    for function in index["functions"]:
        kind = "reccmp" if function["status"] == "reccmp_matched" else "Exact object"
        anchor = f"#L{function['annotation_line']}" if function["annotation_line"] else ""
        lines.append(f"| `{function['rva']}` | {kind} | [{Path(function['source']).name}]({function['source']}{anchor}) |")
    (output / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-root", type=Path, default=REPO / "local/rapid-native")
    parser.add_argument("--object-root", type=Path, default=REPO / "local/rapid-object")
    parser.add_argument("--output", type=Path, default=REPO / "src/native/recovered")
    args = parser.parse_args()
    index, files = snapshot(args.native_root, args.object_root)
    publish(index, files, args.output)
    print(json.dumps({"matched_functions": index["matched_functions"], "counts": index["counts"], "source_files": len(files), "output": str(args.output)}))


if __name__ == "__main__":
    main()

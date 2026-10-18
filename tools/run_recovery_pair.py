"""Bounded proposal -> deterministic gates -> independent review, without integration.

The manifest is a coordinator-owned trust boundary, not a security sandbox. Only
declared support files are copied; original binaries are hashed in place. Model
output is source data, never commands. See docs/paired-recovery.md.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import signal
import subprocess
import sys
import tempfile
import time


MODELS = ("gpt-6.1-sol", "gpt-6.1-sol", "gpt-6.1-sol")
TOOL_TYPES = {"command_execution", "file_change", "mcp_tool_call", "web_search",
              "image_generation", "collab_tool_call"}
REVIEW_SCHEMA = {"type": "object", "properties": {
    "decision": {"type": "string", "enum": ["approve", "reject", "needs-evidence"]},
    "summary": {"type": "string"},
    "issues": {"type": "array", "items": {"type": "object", "properties": {
        "severity": {"type": "string", "enum": ["blocking", "evidence", "note"]},
        "function": {"type": "string"}, "detail": {"type": "string"}},
        "required": ["severity", "function", "detail"], "additionalProperties": False}},
    "limitations": {"type": "array", "items": {"type": "string"}}},
    "required": ["decision", "summary", "issues", "limitations"], "additionalProperties": False}


class PairError(ValueError):
    pass


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise PairError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load(path):
    def invalid(value):
        raise PairError(f"nonfinite JSON: {value}")
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=pairs,
                      parse_constant=invalid)


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
                         encoding="utf-8")
    temporary.replace(path)


def rel(value):
    if (not isinstance(value, str) or not value or "\\" in value
            or PurePosixPath(value).is_absolute() or ".." in PurePosixPath(value).parts
            or str(PurePosixPath(value)) != value):
        raise PairError(f"expected normalized relative path: {value!r}")
    return value


def exact(value, keys, label):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise PairError(f"wrong {label} fields")


def checked_file(root, name):
    path = root / rel(name)
    # Do not copy a symlink, including one in an ancestor directory.
    if not path.is_file() or path.resolve() != path.absolute():
        raise PairError(f"missing or symlinked snapshot file: {name}")
    return path


def check_manifest(m, root):
    exact(m, {"schema_version", "group", "packet", "candidate", "functions", "snapshot",
              "reference", "commands", "review_evidence"}, "manifest")
    if m["schema_version"] != 1 or not isinstance(m["group"], str) or not m["group"]:
        raise PairError("unsupported/empty manifest")
    rel(m["packet"])
    target = rel(m["candidate"])
    if not target.startswith("src/") or not target.endswith(".cpp"):
        raise PairError("candidate must be one src/*.cpp proposal")
    if not isinstance(m["snapshot"], dict) or not m["snapshot"] or target in m["snapshot"]:
        raise PairError("declare frozen support files separately from candidate")
    for name, expected in m["snapshot"].items():
        if (not isinstance(expected, str) or len(expected) != 64
                or any(c not in "0123456789abcdef" for c in expected)):
            raise PairError("invalid snapshot SHA-256")
        if Path(name).suffix.lower() in {".exe", ".dll", ".dmp", ".gpr", ".rep"}:
            raise PairError("original binaries/captures cannot enter snapshots")
        if sha(checked_file(root, name)) != expected:
            raise PairError(f"frozen input hash mismatch: {name}")
    if m["packet"] not in m["snapshot"] or "tools/run_model_packet.py" not in m["snapshot"]:
        raise PairError("packet and implementation launcher must be frozen")
    exact(m["reference"], {"path", "sha256"}, "reference")
    binary = Path(m["reference"]["path"])
    if not binary.is_absolute() or not binary.is_file() or sha(binary) != m["reference"]["sha256"]:
        raise PairError("reference binary identity mismatch")
    if not isinstance(m["functions"], list) or not m["functions"]:
        raise PairError("empty function set")
    names, ids = set(), set()
    for f in m["functions"]:
        exact(f, {"name", "id", "contract", "corpora"}, "function")
        if not all(isinstance(f[k], str) and f[k] for k in ("name", "id")):
            raise PairError("invalid function identity")
        if f["name"] in names or f["id"] in ids:
            raise PairError("duplicate function")
        names.add(f["name"])
        ids.add(f["id"])
        exact(f["corpora"], {"public", "heldout"}, "corpora")
        for name in [f["contract"], *f["corpora"].values()]:
            if rel(name) not in m["snapshot"]:
                raise PairError("contract/corpus not frozen")
        contract = load(root / f["contract"])
        if contract.get("function_id") != f["id"]:
            raise PairError("contract identity mismatch")
        suite_ids = []
        for name in f["corpora"].values():
            corpus = load(root / name)
            if not isinstance(corpus, list) or not corpus:
                raise PairError("empty corpus")
            case_ids = [c["id"] for c in corpus]
            if len(set(case_ids)) != len(case_ids):
                raise PairError("duplicate corpus case")
            suite_ids.append(set(case_ids))
        if suite_ids[0] & suite_ids[1]:
            raise PairError("public and held-out case IDs overlap")
    for name in m["review_evidence"]:
        if rel(name) not in m["snapshot"]:
            raise PairError("review evidence not frozen")
    exact(m["commands"], {"build", "public", "heldout", "negative"}, "command stages")
    report_paths = set()
    for stage, commands in m["commands"].items():
        if not isinstance(commands, list) or not commands:
            raise PairError(f"empty {stage} stage")
        covered = set()
        for command in commands:
            exact(command, {"argv", "timeout_seconds", "reports"}, "command")
            if (not isinstance(command["argv"], list) or not command["argv"]
                    or any(not isinstance(a, str) or not a for a in command["argv"])):
                raise PairError("commands must be nonempty argv arrays")
            if (type(command["timeout_seconds"]) is not int
                    or not 1 <= command["timeout_seconds"] <= 3600):
                raise PairError("subprocess timeout must be 1..3600 seconds")
            if not isinstance(command["reports"], list) or (stage != "build" and not command["reports"]):
                raise PairError("deterministic gates require reports")
            for report in command["reports"]:
                exact(report, {"path", "function", "corpus", "expect"}, "report")
                path = rel(report["path"])
                if path in report_paths or report["function"] not in names:
                    raise PairError("duplicate report path or unknown function")
                report_paths.add(path)
                covered.add(report["function"])
                if (report["corpus"] != ("heldout" if stage == "heldout" else "public")
                        or report["expect"] != ("mismatch" if stage == "negative" else "pass")):
                    raise PairError("gate/corpus/expectation mismatch")
        if stage in {"public", "heldout"} and covered != names:
            raise PairError(f"{stage} does not cover all functions")


def run_command(argv, cwd, output, timeout, stdin=None):
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    result = {"argv": argv, "cwd": str(cwd), "timeout_seconds": timeout, "timed_out": False}
    with (output / "stdout.log").open("wb") as stdout, (output / "stderr.log").open("wb") as stderr:
        try:
            with subprocess.Popen(argv, cwd=cwd, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr,
                                  start_new_session=(os.name == "posix")) as process:
                try:
                    process.communicate(stdin, timeout=timeout)
                except subprocess.TimeoutExpired:
                    result["timed_out"] = True
                    if os.name == "posix":
                        os.killpg(process.pid, signal.SIGKILL)
                    else:
                        process.kill()
                    process.communicate()
                result["exit_code"] = process.returncode
        except OSError as exc:
            result.update(exit_code=None, error=str(exc))
    result["elapsed_seconds"] = round(time.monotonic() - started, 3)
    write(output / "run.json", result)
    return result


def events_metrics(directory):
    usage, tool_items, errors = [], [], []
    for line in (directory / "events.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        event = json.loads(line, object_pairs_hook=pairs)
        if event.get("type") == "turn.completed" and "usage" in event:
            usage.append(event["usage"])
        if event.get("type") in {"turn.failed", "error"}:
            errors.append(event)
        item = event.get("item", {})
        if event.get("type") in {"item.started", "item.completed"} and item.get("type") in TOOL_TYPES:
            tool_items.append(item["type"])
    return {"usage": usage, "tool_items": tool_items, "errors": errors}


def request_model(kind, prompt, directory, model, root, launcher, python, review_names=None):
    """Implementation uses the existing auth/launcher; review has its own schema."""
    directory.mkdir(parents=True, exist_ok=False)
    prompt_path = directory / "prompt.txt"
    prompt_path.write_text(prompt, encoding="utf-8")
    if kind == "implementation":
        response_dir = directory / "request"
        outer = run_command([python, str(launcher), str(prompt_path), str(response_dir),
                             "--model", model, "--timeout", "180"], root,
                            directory / "launcher", 195)
        metrics = load(response_dir / "run.json") if (response_dir / "run.json").exists() else {}
        metrics.update(outer=outer)
    else:
        response_dir = directory
        schema = directory / "response-schema.json"
        configured_schema = json.loads(json.dumps(REVIEW_SCHEMA))
        configured_schema["properties"]["issues"]["items"]["properties"]["function"]["enum"] = ["*", *(review_names or [])]
        write(schema, configured_schema)
        argv = ["codex", "exec", "--model", model, "--sandbox", "read-only", "--ephemeral",
                "--ignore-user-config", "--skip-git-repo-check", "-c", 'model_reasoning_effort="medium"',
                "--json", "--output-schema", str(schema), "--output-last-message",
                str(directory / "response.json"), "-"]
        # Empty working directory, no tools permitted by prompt; tool events invalidate the review.
        workspace = directory / "empty-workspace"
        workspace.mkdir()
        metrics = run_command(argv, workspace, directory / "process", 180, prompt.encode())
        shutil.copyfile(directory / "process/stdout.log", directory / "events.jsonl")
    metrics.update(kind=kind, requested_model=model, prompt_sha256=sha(prompt_path), reused=False)
    if (response_dir / "events.jsonl").is_file():
        try:
            metrics.update(events_metrics(response_dir))
        except (ValueError, TypeError) as exc:
            metrics["errors"] = [str(exc)]
    write(directory / "metrics.json", metrics)
    if (metrics.get("exit_code") != 0 or metrics.get("timed_out")
            or metrics.get("outer", {}).get("exit_code", 0) != 0
            or metrics.get("tool_items") or metrics.get("errors")):
        raise PairError(f"{kind} model request failed or attempted tools")
    return load(response_dir / "response.json"), metrics


def source_response(response, names):
    exact(response, {"source", "functions", "uncertainties"}, "implementation response")
    if not isinstance(response["source"], str) or not response["source"].strip():
        raise PairError("empty source proposal")
    if len(response["source"].encode()) > 1024 * 1024:
        raise PairError("source exceeds 1 MiB")
    if not isinstance(response["functions"], list):
        raise PairError("functions must be an array")
    seen = []
    for function in response["functions"]:
        exact(function, {"name", "suggested_name", "explanation"}, "function note")
        if any(not isinstance(v, str) or not v for v in function.values()):
            raise PairError("empty/nonstring function note")
        seen.append(function["name"])
    if len(seen) != len(names) or set(seen) != set(names):
        raise PairError("proposal function set differs from packet")
    if not isinstance(response["uncertainties"], list) or any(not isinstance(x, str) for x in response["uncertainties"]):
        raise PairError("uncertainties must be strings")
    return response["source"]


def review_response(response, names):
    exact(response, {"decision", "summary", "issues", "limitations"}, "review response")
    if response["decision"] not in {"approve", "reject", "needs-evidence"}:
        raise PairError("invalid review decision")
    if not isinstance(response["summary"], str) or not response["summary"].strip():
        raise PairError("empty review summary")
    if not isinstance(response["issues"], list) or not isinstance(response["limitations"], list):
        raise PairError("invalid review issues/limitations")
    for issue in response["issues"]:
        exact(issue, {"severity", "function", "detail"}, "review issue")
        if (issue["severity"] not in {"blocking", "evidence", "note"}
                or issue["function"] not in {*names, "*"}
                or not isinstance(issue["detail"], str) or not issue["detail"].strip()):
            raise PairError("invalid review issue")
    if any(not isinstance(x, str) or not x.strip() for x in response["limitations"]):
        raise PairError("invalid review limitation")
    if response["decision"] == "approve" and any(i["severity"] != "note" for i in response["issues"]):
        raise PairError("approval contains unresolved blocking/evidence issues")
    return response["decision"]


def verify_tree(m, tree, source_hash):
    for name, expected in m["snapshot"].items():
        if sha(checked_file(tree, name)) != expected:
            raise PairError(f"frozen snapshot changed: {name}")
    if sha(checked_file(tree, m["candidate"])) != source_hash:
        raise PairError("candidate changed during deterministic gates")
    if sha(m["reference"]["path"]) != m["reference"]["sha256"]:
        raise PairError("reference binary changed during execution")


def inspect_report(path, declaration, m, tree):
    report = load(path)
    f = next(f for f in m["functions"] if f["name"] == declaration["function"])
    corpus = load(tree / f["corpora"][declaration["corpus"]])
    expected = {c["id"]: digest(c) for c in corpus}
    rows = report.get("cases", [])
    if (report.get("schema_version") != 1 or report.get("function_id") != f["id"]
            or report.get("proof") is not False or report.get("artifacts_unchanged") is not True
            or type(report.get("repeats")) is not int or report["repeats"] < 2
            or report.get("contract_sha256") != digest(load(tree / f["contract"]))
            or report.get("corpus_sha256") != digest(corpus)
            or not isinstance(rows, list) or len(rows) != len(expected)
            or len({r["case_id"] for r in rows}) != len(expected)
            or {r["case_id"]: r["case_sha256"] for r in rows} != expected):
        raise PairError(f"invalid/incomplete deterministic report: {path}")
    artifacts = report.get("artifacts_sha256", {})
    for required in (tree / m["candidate"], tree / f["contract"], Path(m["reference"]["path"])):
        if artifacts.get(str(required)) != sha(required):
            raise PairError(f"report does not bind tested source/contract/reference: {required}")
    batch_requested = any('--execution' in cmd['argv'] and
                          cmd['argv'][cmd['argv'].index('--execution')+1] == 'batch'
                          for stage in m['commands'].values() for cmd in stage)
    if batch_requested:
        backend = report.get('execution_backend', {})
        processes = backend.get('process_counts', [])
        if (backend.get('name') != 'posix-fresh-child-batch-v1'
                or backend.get('case_process_isolation') != 'fresh-fork-session'
                or backend.get('supervisor_reuse') != 'none across sides or repetitions'
                or len(processes) != 2 * report['repeats']
                or any(p.get('case_processes') != len(expected) or p.get('supervisor_processes') != 1 for p in processes)):
            raise PairError('batch report lacks complete fresh-child execution provenance')
        original_command = report.get('oracle_command', [])
        candidate_command = report.get('candidate_command', [])
        adapter = 'object_bitfield' if m['group'] == 'object-bitfields-001' else 'indexed_field'
        runner = tree / f'validation/{adapter}_batch_runner.py'
        if (len(original_command) != 4 or len(candidate_command) != 4
                or original_command[1:3] != [str(runner), 'original']
                or candidate_command[1:3] != [str(runner), 'candidate']
                or original_command[0] != candidate_command[0]
                or original_command[3] != m['reference']['path']):
            raise PairError('batch report command identity mismatch')
        library = Path(candidate_command[3])
        stem = f'libdao_{adapter}_batch' + ('_mutant' if declaration['expect'] == 'mismatch' else '')
        if library.parent != tree / 'build' or library.name not in (stem+'.dylib',stem+'.so'):
            raise PairError('batch report native library identity mismatch')
        required_batch = [library, runner, tree/'tools/daodecomp/batch.py',
                          tree/f'validation/{adapter}_batch_native.cpp',
                          tree/'CMakeLists.txt', tree/'build/CMakeCache.txt', tree/'build/compile_commands.json']
        for required in required_batch:
            if not required.is_file() or artifacts.get(str(required)) != sha(required):
                raise PairError('batch report does not bind executed adapter/library/build: '+str(required))
    counts = dict(Counter(row["status"] for row in rows))
    if declaration["expect"] == "mismatch":
        passed = (report.get("status") == "failed" and counts.get("mismatch", 0) > 0
                  and set(counts) <= {"corpus_pass", "mismatch"})
    else:
        passed = report.get("status") == "corpus_pass" and set(counts) == {"corpus_pass"}
    summary = {"report": str(path), "sha256": sha(path), "function": f["name"],
               "function_id": f["id"], "corpus": declaration["corpus"],
               "expect": declaration["expect"], "counts": counts, "passed": passed,
               "contract_canonical_json_sha256": report["contract_sha256"],
               "corpus_canonical_json_sha256": report["corpus_sha256"],
               "contract_raw_file_sha256": m["snapshot"][f["contract"]],
               "corpus_raw_file_sha256": m["snapshot"][f["corpora"][declaration["corpus"]]],
               "source_raw_file_sha256": sha(tree / m["candidate"]),
               "execution": {key: report.get(key) for key in ("host", "backend_versions", "oracle_command", "candidate_command", "execution_backend")},
               "execution_artifacts_raw_sha256": artifacts}
    if not passed:
        row = next((r for r in rows if r["status"] != "corpus_pass"), rows[0])
        summary["counterexample"] = {k: row[k] for k in ("case", "status", "differing_paths", "oracle", "candidate") if k in row}
    return summary


ARTIFACT_BINDING_HASH_DOMAIN = (
    "SHA-256(canonical JSON bytes from json.dumps(value, ensure_ascii=True, "
    "sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8') "
    "for {path, raw_file_sha256}; raw_file_sha256 is SHA-256 of raw artifact bytes"
)
ARTIFACT_MAP_HASH_DOMAIN = (
    "SHA-256(canonical JSON bytes from json.dumps(value, ensure_ascii=True, "
    "sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8') "
    "for the full path-to-raw-file-SHA256 object)"
)
EXECUTION_HASH_DOMAIN = (
    "SHA-256(canonical JSON bytes from json.dumps(value, ensure_ascii=True, "
    "sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8') "
    "for the execution provenance object)"
)


def deduplicate_prompt_provenance(value, *, mode):
    """Deduplicate direct report-summary provenance; all report payloads stay opaque."""
    if mode not in {"reviewer", "repair"}:
        raise PairError("unknown prompt provenance layout")
    evidence = json.loads(canonical(value))
    bindings, executions, reports = {}, {}, []

    def pack_report(report, location):
        if not isinstance(report, dict):
            raise PairError("invalid report summary in prompt evidence")
        artifacts_present = "execution_artifacts_raw_sha256" in report
        execution_present = "execution" in report
        if not artifacts_present and not execution_present:
            return
        row = {"location": location, "artifacts_present": artifacts_present,
               "execution_present": execution_present}
        if artifacts_present:
            artifacts = report["execution_artifacts_raw_sha256"]
            if not isinstance(artifacts, dict) or any(
                    not isinstance(path, str) or not isinstance(file_hash, str)
                    or len(file_hash) != 64
                    or any(c not in "0123456789abcdef" for c in file_hash)
                    for path, file_hash in artifacts.items()):
                raise PairError("invalid execution artifact map in prompt evidence")
            refs = []
            for path, file_hash in sorted(artifacts.items()):
                binding = {"path": path, "raw_file_sha256": file_hash}
                binding_hash = digest(binding)
                bindings[binding_hash] = binding
                refs.append(binding_hash)
            row["artifact_map_sha256"] = digest(artifacts)
            row["binding_refs"] = refs
            del report["execution_artifacts_raw_sha256"]
        if execution_present:
            execution = report["execution"]
            if not isinstance(execution, dict):
                raise PairError("invalid execution provenance in prompt evidence")
            provenance_hash = digest(execution)
            executions[provenance_hash] = execution
            row["execution_sha256"] = provenance_hash
            del report["execution"]
        reports.append(row)

    if mode == "reviewer":
        if not isinstance(evidence, list):
            raise PairError("reviewer evidence must be a stage list")
        for stage_index, stage in enumerate(evidence):
            if not isinstance(stage, dict) or not isinstance(stage.get("reports", []), list):
                raise PairError("invalid reviewer stage summary")
            for report_index, report in enumerate(stage.get("reports", [])):
                pack_report(report, [stage_index, report_index])
    else:
        if not isinstance(evidence, list):
            raise PairError("repair evidence must be a feedback list")
        for feedback_index, report in enumerate(evidence):
            if isinstance(report, dict) and "execution_artifacts_raw_sha256" in report:
                pack_report(report, [feedback_index])
    return {
        "hash_domains": {"artifact_binding": ARTIFACT_BINDING_HASH_DOMAIN,
                         "artifact_map": ARTIFACT_MAP_HASH_DOMAIN,
                         "execution_provenance": EXECUTION_HASH_DOMAIN},
        "shared_artifact_bindings": [
            {"binding_sha256": key, **bindings[key]} for key in sorted(bindings)],
        "shared_execution_provenance": [
            {"provenance_sha256": key, "value": executions[key]}
            for key in sorted(executions)],
        "report_provenance": reports,
        "evidence": evidence,
    }


def run_stage(stage, m, tree, attempt, python, source_hash):
    summaries, commands = [], []
    variables = {"python": python, "tree": str(tree), "build": str(tree / "build"),
                 "report_dir": str(attempt / "reports"), "binary": m["reference"]["path"]}
    (attempt / "reports").mkdir(exist_ok=True)
    passed = True
    for index, command in enumerate(m["commands"][stage], 1):
        verify_tree(m, tree, source_hash)
        argv = [arg.format_map(variables) for arg in command["argv"]]
        # Stale reports cannot satisfy a new command.
        for declaration in command["reports"]:
            if (attempt / "reports" / declaration["path"]).exists():
                raise PairError("report unexpectedly exists before gate")
        result = run_command(argv, tree, attempt / f"{stage}-{index}", command["timeout_seconds"])
        commands.append(result)
        verify_tree(m, tree, source_hash)
        for declaration in command["reports"]:
            path = attempt / "reports" / declaration["path"]
            if not path.is_file():
                passed = False
                summaries.append({"report": str(path), "passed": False, "error": "missing report"})
            else:
                summary = inspect_report(path, declaration, m, tree)
                summaries.append(summary)
                passed &= summary["passed"]
        passed &= result["exit_code"] == 0 and not result["timed_out"]
        if result["exit_code"] != 0 or result["timed_out"]:
            break
    result = {"stage": stage, "passed": bool(passed), "commands": commands, "reports": summaries}
    write(attempt / f"{stage}.json", result)
    return result


def repair_prompt(packet, source, gates):
    feedback = []
    for gate in gates:
        if gate["stage"] == "public":
            feedback.extend(gate["reports"])
        elif gate["stage"] == "build":
            for command in gate["commands"]:
                feedback.append({"stage": "build", "exit_code": command["exit_code"]})
    prompt_evidence = deduplicate_prompt_provenance(feedback, mode="repair")
    return (packet + "\n\nAUTOMATED PUBLIC-ONLY REPAIR\nReturn a complete replacement source response. "
            "Preserve every already-passing function implementation unchanged unless supplied public evidence "
            "identifies a defect in that implementation. Do not modify headers, contracts, oracle, comparator, corpus, ABI or acceptance "
            "criteria. Do not call tools or read/edit files. Held-out data is not supplied.\n"
            + "Previous source:\n" + source
            + "\nPublic gate evidence with hash-bound shared provenance:\n"
            + canonical(prompt_evidence))


def infrastructure_failure(gate, attempt):
    """Protected build configuration is never an implementation-model repair task."""
    if gate["stage"] != "build":
        return False
    for index, command in enumerate(gate["commands"], 1):
        if command["exit_code"] is None or command["timed_out"]:
            return True
        if command["exit_code"] != 0:
            argv = command["argv"]
            # These checks exercise protected support, not a compiler diagnostic
            # or a validated public semantic counterexample for the candidate.
            if (Path(argv[0]).stem == "ctest" or argv[1:3] == ["-m", "unittest"]
                    or any(arg.endswith("/examples/synthetic/demo.py") for arg in argv)):
                return True
            logs = "\n".join((attempt / f"build-{index}" / name).read_text(errors="replace")
                             for name in ("stdout.log", "stderr.log"))
            markers = ("Cannot find source file", "No SOURCES given to target", "CMake Error",
                       "Could NOT find", "No CMAKE_CXX_COMPILER", "is not able to compile a simple test program",
                       "FileNotFoundError:", "ModuleNotFoundError:", "ImportError:")
            if any(marker in logs for marker in markers):
                return True
    return False


def retryable_public_failure(gate):
    """Only stable semantic counterexamples justify implementation-model feedback."""
    reports = gate["reports"]
    return (bool(reports)
            and all(not c["timed_out"] and c["exit_code"] in (0, 1) for c in gate["commands"])
            and all("counts" in r and set(r["counts"]) <= {"corpus_pass", "mismatch"} for r in reports)
            and any(r["counts"].get("mismatch", 0) > 0 for r in reports))


def preflight_cmake(m, frozen, output, python):
    """Configure the declared CMake tree with an empty candidate before model spend.

    Configuration checks protected build inputs without guessing implementation
    semantics. Non-CMake command manifests retain per-attempt infrastructure checks.
    """
    command = m["commands"]["build"][0]
    argv = command["argv"]
    if Path(argv[0]).name != "cmake" or "-S" not in argv or command["reports"]:
        return None
    preflight = output / "preflight"
    preflight.mkdir()
    with tempfile.TemporaryDirectory(prefix="tree-", dir=preflight) as temporary:
        tree = Path(temporary)
        shutil.copytree(frozen, tree, dirs_exist_ok=True)
        candidate = tree / m["candidate"]
        candidate.parent.mkdir(parents=True, exist_ok=True)
        candidate.write_text("// CMake configuration preflight; no implementation.\n", encoding="utf-8")
        source_hash = sha(candidate)
        variables = {"python": python, "tree": str(tree), "build": str(tree / "build"),
                     "report_dir": str(preflight / "reports"), "binary": m["reference"]["path"]}
        verify_tree(m, tree, source_hash)
        result = run_command([arg.format_map(variables) for arg in argv], tree,
                             preflight / "configure", command["timeout_seconds"])
        verify_tree(m, tree, source_hash)
        result["passed"] = result["exit_code"] == 0 and not result["timed_out"]
        write(preflight / "result.json", result)
        return result


def reviewer_prompt(m, frozen, source, summaries, attempt):
    evidence = {name: (frozen / name).read_text(encoding="utf-8")
                for name in dict.fromkeys([m["packet"], *m["review_evidence"],
                                          *(f["contract"] for f in m["functions"])])}
    compact = deduplicate_prompt_provenance(
        [{"stage": g["stage"], "passed": g["passed"], "reports": g["reports"]} for g in summaries],
        mode="reviewer")
    build = next(g for g in summaries if g["stage"] == "build")
    build_evidence = {"commands": build["commands"], "stdout": [], "compile_commands": None}
    for index, _ in enumerate(build["commands"], 1):
        build_evidence["stdout"].append((attempt / f"build-{index}/stdout.log").read_text(errors="replace")[-6000:])
    compile_commands = attempt / "build-metadata/compile_commands.json"
    if compile_commands.is_file():
        build_evidence["compile_commands"] = load(compile_commands)
    return ("You are the independent recovery reviewer. No tools, file reads, file edits, commands, browsing, "
            "or other agents. All review material is below. Return only the configured structured review JSON, "
            "with approve/reject/needs-evidence, specific issues and limitations. Review actual instruction "
            "evidence, ABI and full return bits, memory footprint/aliasing/overlap, defined overflow/shift "
            "semantics, function identities, contract coverage and exclusions. Passing tests alone is "
            "insufficient. Treat disassembly/model explanations as hypotheses tied to recorded binary/slice "
            "hashes; identify any missing evidence. Emulator corpus agreement is not native validation or "
            "a proof of whole-game behavior. Approve only the scoped source package, never registry integration.\n"
            "For issue.function use one declared function name or '*' for a group issue; do not use 'all'. "
            "Hash domains: manifest snapshot hashes are SHA-256 of raw file bytes, including whitespace. "
            "Report contract/corpus digests are SHA-256 of parsed JSON serialized with sorted keys, "
            "separators=(',',':'), allow_nan=False, UTF-8. Different raw/canonical hashes are expected. "
            "Both labeled domains and the pipeline's verified tested source/contract/reference bindings "
            "are supplied below. Evaluate any previous review included as evidence independently; "
            "approval is not required, and unresolved evidence gaps should remain needs-evidence.\n"
            + "Frozen acceptance manifest:\n" + canonical(m) + "\nFrozen evidence:\n" + canonical(evidence)
            + "\nCandidate source raw SHA-256:\n" + sha(attempt / "candidate.cpp")
            + "\nCandidate source:\n" + source + "\nCompiler/build evidence:\n" + canonical(build_evidence)
            + "\nCompact deterministic summaries with hash-bound shared provenance:\n" + canonical(compact))


def run_pair(manifest_path, output, root, python=sys.executable, initial_response=None,
             attempts=3, reviewer_model="gpt-6.1-sol", requester=request_model):
    root, output = Path(root).resolve(), Path(output).resolve()
    if not output.is_relative_to(root / "local/pairs") or output == root / "local/pairs":
        raise PairError("output must be a new directory below ignored local/pairs/")
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    status = {"schema_version": 1, "status": "running", "host": platform.platform(),
              "attempts": [], "model_requests": [], "accepted": False,
              "native_windows_validated": False, "proof": False,
              "orchestrator_sha256": sha(__file__)}
    write(output / "status.json", status)

    def finish(state, reason):
        # Include failed requests too, whose metrics exist even when no response was accepted.
        for metrics_path in sorted(output.glob("attempt-*/model/metrics.json")) + [output / "review/metrics.json"]:
            if metrics_path.is_file():
                metrics = load(metrics_path)
                if metrics not in status["model_requests"]:
                    status["model_requests"].append(metrics)
        status.update(status=state, reason=reason, elapsed_seconds=round(time.monotonic() - started, 3))
        status["new_model_request_count"] = sum(not r.get("reused", False) for r in status["model_requests"])
        write(output / "status.json", status)
        return status

    try:
        if type(attempts) is not int or not 1 <= attempts <= 3 or reviewer_model not in {"gpt-6.1-sol", "gpt-6-luna"}:
            raise PairError("at most three attempts; reviewer must be Sol or Luna")
        m = load(manifest_path)
        check_manifest(m, root)
        status.update(group=m["group"], manifest_sha256=digest(m), functions=[f["id"] for f in m["functions"]])
        write(output / "manifest.json", m)
        frozen = output / "frozen"
        for name, expected in m["snapshot"].items():
            destination = frozen / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(checked_file(root, name), destination)
            if sha(destination) != expected:
                raise PairError(f"input changed while snapshotting: {name}")
        status["preflight"] = preflight_cmake(m, frozen, output, python)
        if status["preflight"] is not None and not status["preflight"]["passed"]:
            return finish("infrastructure-error", "CMake configuration preflight failed before any model request")
        packet = (frozen / m["packet"]).read_text(encoding="utf-8")
        prompt = packet
        names = [f["name"] for f in m["functions"]]
        for number in range(1, attempts + 1):
            attempt = output / f"attempt-{number}"
            attempt.mkdir()
            record = {"number": number, "model": MODELS[number - 1], "gates": []}
            status["attempts"].append(record)
            try:
                if number == 1 and initial_response is not None:
                    response = load(initial_response)
                    metrics = {"kind": "implementation", "reused": True, "requested_model": MODELS[0],
                               "response_sha256": sha(initial_response), "original_path": str(Path(initial_response).resolve())}
                    prior_run = Path(initial_response).parent / "run.json"
                    if prior_run.is_file():
                        metrics["original_request_metrics"] = load(prior_run)
                        if metrics["original_request_metrics"].get("tool_items"):
                            raise PairError("initial proposal attempted tools")
                    metrics["attempt_slot_model"] = MODELS[0]
                    metrics["requested_model"] = metrics.get("original_request_metrics", {}).get("requested_model")
                    write(attempt / "reused-metrics.json", metrics)
                else:
                    response, metrics = requester("implementation", prompt, attempt / "model", MODELS[number - 1],
                                                  root, frozen / "tools/run_model_packet.py", python)
                status["model_requests"].append(metrics)
                write(attempt / "response.json", response)
                source = source_response(response, names)
            except (ValueError, OSError, KeyError, TypeError) as exc:
                record.update(status="invalid-proposal", error=str(exc))
                # Missing semantics/invalid model output never turns into a successful candidate.
                prompt = packet + "\nPrevious proposal was invalid: " + str(exc) + "\nReturn strict response JSON; no tools."
                write(output / "status.json", status)
                continue
            candidate = attempt / "candidate.cpp"
            candidate.write_text(source, encoding="utf-8")
            record["source_sha256"] = sha(candidate)
            with tempfile.TemporaryDirectory(prefix="tree-", dir=attempt) as temporary:
                tree = Path(temporary)
                shutil.copytree(frozen, tree, dirs_exist_ok=True)
                (tree / m["candidate"]).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(candidate, tree / m["candidate"])
                for stage in ("build", "public", "heldout", "negative"):
                    gate = run_stage(stage, m, tree, attempt, python, sha(candidate))
                    if stage == "build":
                        for name in ("CMakeCache.txt", "compile_commands.json"):
                            if (tree / "build" / name).is_file():
                                (attempt / "build-metadata").mkdir(exist_ok=True)
                                shutil.copyfile(tree / "build" / name, attempt / "build-metadata" / name)
                    record["gates"].append(gate)
                    write(output / "status.json", status)
                    if not gate["passed"]:
                        record["status"] = stage + "-failed"
                        if infrastructure_failure(gate, attempt):
                            return finish("infrastructure-error", "protected build infrastructure failed; no implementation retry")
                        if stage == "public" and not retryable_public_failure(gate):
                            return finish("needs-evidence", "public gate has missing/error/unstable evidence; no semantic repair retry")
                        if stage in {"heldout", "negative"}:
                            return finish("needs-evidence", f"{stage} gate failed; no retry receives this evidence")
                        # Capture bounded build diagnostics for a concrete compiler repair.
                        prompt = repair_prompt(packet, source, record["gates"])
                        if stage == "build":
                            diagnostics = []
                            for index, command in enumerate(gate["commands"], 1):
                                if command["exit_code"] != 0:
                                    for name in ("stdout.log", "stderr.log"):
                                        diagnostics.append((attempt / f"build-{index}" / name).read_text(errors="replace"))
                            prompt += "\nFailed compiler command diagnostics:\n" + "\n".join(diagnostics)[-16000:]
                        break
                else:
                    record["status"] = "deterministic-gates-passed"
                    prompt = reviewer_prompt(m, frozen, source, record["gates"], attempt)
                    review, metrics = requester("review", prompt, output / "review", reviewer_model,
                                                root, frozen / "tools/run_model_packet.py", python, names)
                    status["model_requests"].append(metrics)
                    write(output / "review-response.json", review)
                    decision = review_response(review, names)
                    status["review_decision"] = decision
                    verify_tree(m, tree, sha(candidate))
                    if decision != "approve":
                        return finish("review-" + decision, "independent reviewer did not approve scoped integration package")
                    accepted = output / "accepted"
                    accepted.mkdir()
                    shutil.copyfile(candidate, accepted / "candidate.cpp")
                    write(accepted / "package.json", {"schema_version": 1, "group": m["group"],
                          "candidate_target": m["candidate"], "source_sha256": sha(candidate),
                          "manifest_sha256": digest(m), "functions": [f["id"] for f in m["functions"]],
                          "review_sha256": sha(output / "review-response.json"),
                          "scope": "frozen emulator corpus plus independent source review; integration requires coordinator",
                          "proof": False, "native_windows_validated": False})
                    status["accepted"] = True
                    return finish("accepted-for-integration", "deterministic gates and independent scoped review passed")
        return finish("implementation-exhausted", "bounded public repair attempts exhausted; no accepted package")
    except (ValueError, OSError, KeyError, TypeError) as exc:
        return finish("needs-evidence", str(exc))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--initial-response", type=Path)
    parser.add_argument("--attempts", type=int, choices=range(1, 4), default=3)
    parser.add_argument("--reviewer-model", choices=("gpt-6.1-sol", "gpt-6-luna"), default="gpt-6.1-sol")
    args = parser.parse_args()
    try:
        status = run_pair(args.manifest, args.output, args.root, str(Path(args.python).absolute()),
                          args.initial_response, args.attempts, args.reviewer_model)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps({k: status[k] for k in ("status", "reason", "elapsed_seconds", "accepted")}))
    return 0 if status["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

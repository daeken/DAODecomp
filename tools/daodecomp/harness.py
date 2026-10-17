"""Exact observation comparison. A passing corpus is evidence, not a proof."""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import signal
import subprocess
import sys
import tempfile


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _pairs(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate JSON key: {key}")
        obj[key] = value
    return obj


def _no_float(value):
    raise ValueError(f"floating-point JSON is forbidden; encode IEEE bits: {value}")


def parse_json(text):
    return json.loads(text, object_pairs_hook=_pairs, parse_float=_no_float,
                      parse_constant=_no_float)


def load_json(path):
    return parse_json(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Atomic replacement avoids leaving a plausible partial report on interruption.
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False,
                                     encoding="utf-8") as stream:
        temp = Path(stream.name)
        try:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
        except BaseException:
            temp.unlink(missing_ok=True)
            raise
    temp.replace(path)


def typed(value, kind):
    if kind == "u32":
        return type(value) is int and 0 <= value <= 0xFFFFFFFF
    if kind == "i32":
        return type(value) is int and -(1 << 31) <= value < (1 << 31)
    if kind == "bool":
        return type(value) is bool
    if kind == "bytes":
        return isinstance(value, str) and re.fullmatch(r"(?:[0-9a-f]{2})*", value) is not None
    if kind == "void":
        return value is None
    raise ValueError(f"unsupported protocol type: {kind}")


def validate_contract(contract):
    required = {"schema_version", "function_id", "kind", "inputs", "return_type", "memory", "calls", "preconditions"}
    if not isinstance(contract, dict) or set(contract) != required:
        raise ValueError("contract has missing or unknown fields")
    if type(contract["schema_version"]) is not int or contract["schema_version"] != 1:
        raise ValueError("unsupported contract schema")
    if contract["kind"] not in ("synthetic", "game") or not isinstance(contract["function_id"], str) or not contract["function_id"]:
        raise ValueError("invalid function identity")
    if not isinstance(contract["preconditions"], str) or not contract["preconditions"]:
        raise ValueError("preconditions must be documented")
    for field in ("inputs", "memory"):
        if not isinstance(contract[field], dict) or not all(isinstance(k, str) and k for k in contract[field]):
            raise ValueError(f"invalid {field} contract")
    for kind in [*contract["inputs"].values(), contract["return_type"]]:
        if kind not in ("u32", "i32", "bool", "bytes", "void"):
            raise ValueError(f"unsupported protocol type: {kind}")
    if any(type(n) is not int or n < 0 for n in contract["memory"].values()):
        raise ValueError("memory region lengths must be nonnegative byte counts")
    if not isinstance(contract["calls"], list) or not all(isinstance(n, str) and n for n in contract["calls"]) or len(set(contract["calls"])) != len(contract["calls"]):
        raise ValueError("invalid allowed call names")


def validate_cases(cases, contract):
    if not isinstance(cases, list) or not cases:
        raise ValueError("empty or invalid corpus")
    ids = set()
    for case in cases:
        if not isinstance(case, dict) or set(case) != {"id", "inputs"}:
            raise ValueError("case must contain exactly id and inputs")
        if not isinstance(case["id"], str) or not case["id"] or case["id"] in ids:
            raise ValueError("empty or duplicate case id")
        ids.add(case["id"])
        if not isinstance(case["inputs"], dict) or set(case["inputs"]) != set(contract["inputs"]):
            raise ValueError("case input fields differ from contract")
        for name, kind in contract["inputs"].items():
            if not typed(case["inputs"][name], kind):
                raise ValueError(f"invalid {kind} input: {name}")


def validate_observation(obs, case, contract):
    expected = {"schema_version", "case_id", "termination", "return", "memory", "calls"}
    if not isinstance(obs, dict) or set(obs) != expected:
        raise ValueError("observation has missing or unknown fields")
    if type(obs["schema_version"]) is not int or obs["schema_version"] != 1 or obs["case_id"] != case["id"]:
        raise ValueError("observation identity mismatch")
    # v1 accepts normal returns only. Equal crashes/timeouts are never a pass.
    if obs["termination"] != "return" or not typed(obs["return"], contract["return_type"]):
        raise ValueError("invalid termination or return value")
    if not isinstance(obs["memory"], dict) or set(obs["memory"]) != set(contract["memory"]):
        raise ValueError("observed memory regions differ from contract")
    for name, size in contract["memory"].items():
        value = obs["memory"][name]
        if not typed(value, "bytes") or len(value) != size * 2:
            raise ValueError(f"invalid memory bytes: {name}")
    if not isinstance(obs["calls"], list):
        raise ValueError("call trace must be an ordered list")
    for call in obs["calls"]:
        if not isinstance(call, dict) or set(call) != {"name", "args", "result"}:
            raise ValueError("invalid call event")
        if call["name"] not in contract["calls"] or not isinstance(call["args"], list):
            raise ValueError("unmodeled dependency call")


def invoke(command, case, contract, timeout):
    if not command or not all(isinstance(a, str) for a in command):
        return {"error": "invalid_command"}
    env = dict(os.environ, LC_ALL="C", LANG="C", TZ="UTC", PYTHONHASHSEED="0")
    request = canonical({"schema_version": 1, "function_id": contract["function_id"], "case": case})
    # Capture to disk so a broken runner cannot exhaust RAM through stdout.
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        try:
            with subprocess.Popen(command, stdin=subprocess.PIPE, stdout=out, stderr=err,
                                  env=env, start_new_session=(os.name == "posix")) as proc:
                try:
                    proc.communicate(request.encode(), timeout=timeout)
                except subprocess.TimeoutExpired:
                    if os.name == "posix":
                        os.killpg(proc.pid, signal.SIGKILL)
                    else:
                        proc.kill()
                    proc.communicate()
                    return {"error": "timeout"}
                err.seek(0)
                diagnostics = err.read(4096).decode("utf-8", errors="replace")
                if proc.returncode != 0:
                    return {"error": "runner_exit", "exit_code": proc.returncode, "stderr": diagnostics}
            out.seek(0)
            raw = out.read(1024 * 1024 + 1)
            if len(raw) > 1024 * 1024:
                return {"error": "oversized_observation"}
            obs = parse_json(raw.decode("utf-8"))
            validate_observation(obs, case, contract)
            return {"observation": obs}
        except (OSError, ValueError) as exc:
            return {"error": "invalid_runner", "detail": str(exc)}


def differing_paths(a, b, path="$"):
    if type(a) is not type(b):
        return [path]
    if isinstance(a, dict):
        if set(a) != set(b):
            return [path]
        return [p for key in sorted(a) for p in differing_paths(a[key], b[key], f"{path}.{key}")]
    if isinstance(a, list):
        if len(a) != len(b):
            return [path]
        return [p for i, (x, y) in enumerate(zip(a, b)) for p in differing_paths(x, y, f"{path}[{i}]")]
    return [] if a == b else [path]


def compare(contract, cases, oracle, candidate, *, repeats=2, timeout=5, artifacts=()):
    validate_contract(contract)
    validate_cases(cases, contract)
    if type(repeats) is not int or repeats < 2:
        raise ValueError("at least two fresh executions per side are required")
    if not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be positive and finite")
    artifact_hashes = {str(p): file_hash(p) for p in artifacts}
    rows = []
    for case in cases:
        original = [invoke(oracle, case, contract, timeout) for _ in range(repeats)]
        replacement = [invoke(candidate, case, contract, timeout) for _ in range(repeats)]
        if any("error" in run for run in original + replacement):
            status = "runner_error"
        elif any(canonical(x) != canonical(original[0]) for x in original[1:]):
            status = "oracle_nondeterministic"
        elif any(canonical(x) != canonical(replacement[0]) for x in replacement[1:]):
            status = "candidate_nondeterministic"
        elif canonical(original[0]) != canonical(replacement[0]):
            status = "mismatch"
        else:
            status = "corpus_pass"
        row = {"case_id": case["id"], "status": status, "case_sha256": digest(case)}
        if status == "corpus_pass":
            row["observation_sha256"] = digest(original[0]["observation"])
        else:
            row.update(case=case, oracle=original, candidate=replacement)
            if status == "mismatch":
                row["differing_paths"] = differing_paths(original[0]["observation"], replacement[0]["observation"])
        rows.append(row)
    unchanged = all(Path(p).is_file() and file_hash(p) == h for p, h in artifact_hashes.items())
    passed = unchanged and all(r["status"] == "corpus_pass" for r in rows)
    return {"schema_version": 1, "function_id": contract["function_id"], "kind": contract["kind"],
            "status": "corpus_pass" if passed else "failed", "proof": False,
            "contract_sha256": digest(contract), "corpus_sha256": digest(cases),
            "oracle_command": oracle, "candidate_command": candidate,
            "artifacts_sha256": artifact_hashes, "artifacts_unchanged": unchanged,
            "host": {"platform": platform.platform(), "python": sys.version.split()[0]},
            "repeats": repeats, "timeout_seconds": timeout, "cases": rows}


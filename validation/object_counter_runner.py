"""Protocol adapter for object-counters-001 over a guarded 512-byte arena."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.daodecomp.harness import load_json
from tools.daodecomp.leaf import load_slice
from tools.daodecomp.memory import ARENA_BASE, execute_memory
from validation.object_counter_cases import FIELD_OFFSETS, fixture


def dispatch_original(function, inputs, binary):
    name = function["name"]
    arena, readable, writable = fixture(name, inputs)
    address, code = load_slice(binary, function["module_sha256"], function["rva"],
                               function["size"], function["code_sha256"])
    result, after = execute_memory(address, code, arena,
                                   registers={"ecx": ARENA_BASE + inputs["object"]},
                                   stack_arguments=[], readable=readable, writable=writable,
                                   stack_cleanup=0)
    return result, after


def dispatch_candidate(function, inputs, executable):
    name = function["name"]
    arena, _, _ = fixture(name, inputs)
    completed = subprocess.run([str(executable), name],
                               input=f'{inputs["arena"]} {inputs["object"]}\n',
                               text=True, capture_output=True, check=True, timeout=3)
    lines = completed.stdout.splitlines()
    if len(lines) != 2:
        raise RuntimeError("candidate emitted wrong observation shape")
    try:
        result = int(lines[0], 10)
        after = bytes.fromhex(lines[1])
    except ValueError as exc:
        raise RuntimeError("candidate emitted invalid return or arena hex") from exc
    if not 0 <= result <= 0xffffffff or len(after) != len(arena) or lines[1] != after.hex():
        raise RuntimeError("candidate emitted invalid u32 return or 512-byte lowercase arena")
    return result, after


def main():
    request = json.load(sys.stdin)
    if (type(request) is not dict or set(request) != {"schema_version", "function_id", "case"}
            or type(request["schema_version"]) is not int or request["schema_version"] != 1):
        raise ValueError("invalid protocol request")
    registry = load_json(ROOT / "analysis/functions.json")
    function = next((item for item in registry["functions"] if item["id"] == request["function_id"]), None)
    if (function is None or function["name"] not in FIELD_OFFSETS
            or function.get("backend") != "object-counters-001"):
        raise ValueError("function is not registered for object-counters-001")
    case = request["case"]
    if not isinstance(case, dict) or set(case) != {"id", "inputs"} or type(case["id"]) is not str or not case["id"]:
        raise ValueError("invalid case envelope")
    inputs = case["inputs"]
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "original" and len(sys.argv) == 3:
        result, after = dispatch_original(function, inputs, Path(sys.argv[2]))
    elif mode == "candidate" and len(sys.argv) == 3:
        result, after = dispatch_candidate(function, inputs, Path(sys.argv[2]))
    else:
        raise ValueError("expected original <binary> or candidate <executable>")
    json.dump({"schema_version": 1, "case_id": case["id"], "termination": "return",
               "return": result, "memory": {"arena": after.hex()}, "calls": []}, sys.stdout)


if __name__ == "__main__":
    main()

"""Protocol adapter for original linked-list slices and native candidates."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.daodecomp.harness import load_json
from tools.daodecomp.leaf import load_slice
from tools.daodecomp.memory import ARENA_BASE, execute_memory
from validation.linked_structure_cases import FUNCTIONS, fixture


def dispatch_original(function, inputs, binary):
    arena, readable, writable, _, _ = fixture(function["name"], inputs)
    address, code = load_slice(binary, function["module_sha256"], function["rva"],
                               function["size"], function["code_sha256"])
    append = function["name"] == "fn_00018390"
    result, after = execute_memory(
        address, code, arena,
        registers={"ecx": ARENA_BASE + inputs["list"]},
        stack_arguments=[ARENA_BASE + inputs["node"]] if append else [],
        readable=readable, writable=writable, stack_cleanup=4 if append else 0,
        preserved_registers=("ecx",))
    return result, after


def dispatch_candidate(function, inputs, executable):
    arena, _, _, _, _ = fixture(function["name"], inputs)
    fields = [inputs["arena"], str(inputs["list"]), inputs["nodes"]]
    if function["name"] == "fn_00018390":
        fields.append(str(inputs["node"]))
    completed = subprocess.run([str(executable), function["name"]], input=" ".join(fields) + "\n",
                               text=True, capture_output=True, check=True, timeout=3)
    lines = completed.stdout.splitlines()
    if len(lines) != 2:
        raise RuntimeError("candidate emitted wrong observation shape")
    try:
        result = int(lines[0], 10)
        after = bytes.fromhex(lines[1])
    except ValueError as exc:
        raise RuntimeError("candidate emitted invalid return or arena hex") from exc
    if (not 0 <= result <= 0xFFFFFFFF or len(after) != len(arena)
            or lines[1] != after.hex()):
        raise RuntimeError("candidate emitted invalid u32 return or 512-byte lowercase arena")
    return result, after


def main():
    request = json.load(sys.stdin)
    if (type(request) is not dict or set(request) != {"schema_version", "function_id", "case"}
            or type(request["schema_version"]) is not int or request["schema_version"] != 1):
        raise ValueError("invalid protocol request")
    registry = load_json(ROOT / "analysis/functions.json")
    function = next((item for item in registry["functions"] if item["id"] == request["function_id"]), None)
    if function is None or function["name"] not in FUNCTIONS or function.get("backend") != "linked-structures-001":
        raise ValueError("function is not registered for linked-structures-001")
    case = request["case"]
    if (type(case) is not dict or set(case) != {"id", "inputs"}
            or type(case["id"]) is not str or not case["id"]):
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

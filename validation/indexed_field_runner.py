"""Protocol adapter for indexed-fields-002 original and native executions."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.daodecomp.harness import load_json
from tools.daodecomp.leaf import load_slice
from tools.daodecomp.memory import ARENA_BASE, execute_memory
from validation.indexed_field_cases import FIELD_SPECS, fixture


def dispatch_original(function, inputs, binary):
    arena, readable, writable = fixture(function["name"], inputs)
    address, code = load_slice(binary, function["module_sha256"], function["rva"],
                               function["size"], function["code_sha256"])
    return execute_memory(address, code, arena,
                          registers={"eax": inputs["entry_eax"],
                                     "ecx": ARENA_BASE + inputs["object"]},
                          stack_arguments=[inputs["index"]] + ([inputs["value"]] if FIELD_SPECS[function["name"]][0] == "set" else []),
                          readable=readable, writable=writable, stack_cleanup=8 if FIELD_SPECS[function["name"]][0] == "set" else 4,
                          preserved_registers=("ecx",))


def dispatch_candidate(function, inputs, executable):
    arena, _, _ = fixture(function["name"], inputs)
    payload = (f'{inputs["arena"]} {inputs["object"]} {inputs["index"]} '
               f'{inputs.get("value", 0)} {inputs["entry_eax"]}\n')
    completed = subprocess.run([str(executable), function["name"]], input=payload,
                               text=True, capture_output=True, check=True, timeout=3)
    lines = completed.stdout.splitlines()
    if len(lines) != 2:
        raise RuntimeError("candidate emitted wrong observation shape")
    try:
        result = int(lines[0], 10)
        after = bytes.fromhex(lines[1])
    except ValueError as exc:
        raise RuntimeError("candidate emitted invalid return or arena hex") from exc
    if not 0 <= result <= 0xFFFFFFFF or len(after) != len(arena) or lines[1] != after.hex():
        raise RuntimeError("candidate emitted invalid u32 return or 512-byte lowercase arena")
    return result, after


def main():
    request = json.load(sys.stdin)
    if (type(request) is not dict or set(request) != {"schema_version", "function_id", "case"}
            or type(request["schema_version"]) is not int or request["schema_version"] != 1):
        raise ValueError("invalid protocol request")
    registry = load_json(ROOT / "analysis/functions.json")
    function = next((f for f in registry["functions"] if f["id"] == request["function_id"]), None)
    if (function is None or function["name"] not in FIELD_SPECS
            or function.get("backend") != "indexed-stores-001"
            or function.get("recovery_group") != "indexed-fields-002"):
        raise ValueError("function is not registered for indexed-stores-001")
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

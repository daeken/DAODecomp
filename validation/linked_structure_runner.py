"""Protocol adapter for original linked-list slices and native candidates."""
import json
import hashlib
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.daodecomp.harness import load_json
from tools.daodecomp.leaf import load_slice
from tools.daodecomp.memory import ARENA_BASE, execute_memory
from tools.daodecomp.pe import fingerprint
from validation.linked_structure_cases import FUNCTIONS, fixture


def dispatch_original(function, inputs, binary):
    arena, readable, writable, _, _ = fixture(function["name"], inputs)
    unlink = function["name"] == "fn_00018400"
    if unlink:
        metadata = fingerprint(binary)
        data = Path(binary).read_bytes()
        if metadata["sha256"] != function["module_sha256"]:
            raise ValueError("reference module hash mismatch")
        rva, size = function["rva"], function["size"]
        sections = [s for s in metadata["sections"] if s["rva"] <= rva and
                    rva + size <= s["rva"] + min(s["file_size"], s["virtual_size"])]
        if len(sections) != 1:
            raise ValueError("unlink capture is not uniquely file-backed")
        section = sections[0]
        offset = section["file_offset"] + rva - section["rva"]
        code = data[offset:offset + size]
        if hashlib.sha256(code).hexdigest() != function["code_sha256"]:
            raise ValueError("unlink contiguous capture hash mismatch")
        address = metadata["image_base"] + rva
    else:
        address, code = load_slice(binary, function["module_sha256"], function["rva"],
                                   function["size"], function["code_sha256"])
    append = function["name"] == "fn_00018390"
    unlink = function["name"] == "fn_00018400"
    execution = execute_memory(
        address, code, arena,
        registers={"ecx": ARENA_BASE + inputs["list"]},
        stack_arguments=[ARENA_BASE + inputs["node"]] if append or unlink else [],
        readable=readable, writable=writable, stack_cleanup=4 if append or unlink else 0,
        preserved_registers=() if unlink else ("ecx",),
        balanced_stack_save="esi" if unlink else None,
        return_registers=("ecx",) if unlink else (), return_trace=unlink)
    if unlink:
        eax, after, observed, trace = execution
        return eax, after, observed["ecx"], trace
    return execution


def dispatch_candidate(function, inputs, executable):
    arena, _, _, _, _ = fixture(function["name"], inputs)
    fields = [inputs["arena"], str(inputs["list"]), inputs["nodes"]]
    if function["name"] in ("fn_00018390", "fn_00018400"):
        fields.append(str(inputs["node"]))
    completed = subprocess.run([str(executable), function["name"]], input=" ".join(fields) + "\n",
                               text=True, capture_output=True, check=True, timeout=3)
    lines = completed.stdout.splitlines()
    if len(lines) != (3 if function["name"] == "fn_00018400" else 2):
        raise RuntimeError("candidate emitted wrong observation shape")
    try:
        result = int(lines[0], 10)
        after = bytes.fromhex(lines[1])
        ecx = int(lines[2], 10) if function["name"] == "fn_00018400" else None
    except ValueError as exc:
        raise RuntimeError("candidate emitted invalid return or arena hex") from exc
    if (not 0 <= result <= 0xFFFFFFFF or len(after) != len(arena)
            or lines[1] != after.hex()):
        raise RuntimeError("candidate emitted invalid u32 return or 512-byte lowercase arena")
    return (result, after, ecx) if function["name"] == "fn_00018400" else (result, after)


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
        observed = dispatch_original(function, inputs, Path(sys.argv[2]))
        if function["name"] == "fn_00018400":
            result, after, ecx, _trace = observed
        else:
            result, after = observed
    elif mode == "candidate" and len(sys.argv) == 3:
        observed = dispatch_candidate(function, inputs, Path(sys.argv[2]))
        if function["name"] == "fn_00018400":
            result, after, ecx = observed
        else:
            result, after = observed
    else:
        raise ValueError("expected original <binary> or candidate <executable>")
    memory = {"arena": after.hex()}
    if function["name"] == "fn_00018400":
        memory["ecx_exit"] = ecx.to_bytes(4, "little").hex()
    json.dump({"schema_version": 1, "case_id": case["id"], "termination": "return",
               "return": result, "memory": memory, "calls": []}, sys.stdout)


if __name__ == "__main__":
    main()

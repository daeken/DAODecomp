"""Protocol adapter for memory-001, with one fresh process and arena per case."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.daodecomp.harness import load_json
from tools.daodecomp.leaf import load_slice
from tools.daodecomp.memory import ARENA_BASE, execute_memory
from validation.memory_cases import COPY_SIZES, fixture


def main():
    request = json.load(sys.stdin)
    if request["schema_version"] != 1:
        raise ValueError("wrong protocol")
    function = next(f for f in load_json(ROOT / "analysis/functions.json")["functions"]
                    if f["id"] == request["function_id"])
    name = function["name"]
    inputs = request["case"]["inputs"]
    arena, readable, writable = fixture(name, inputs)
    if sys.argv[1] == "original":
        address, code = load_slice(sys.argv[2], function["module_sha256"], function["rva"],
                                   function["size"], function["code_sha256"])
        if name in COPY_SIZES:
            registers = {"ecx": ARENA_BASE + inputs["destination"]}
            arguments = [ARENA_BASE + inputs["source"]]
        else:
            registers = {}
            arguments = [ARENA_BASE + inputs["base"], inputs["index"], inputs["enabled"]]
        result, after = execute_memory(address, code, arena, registers=registers,
                                       stack_arguments=arguments, readable=readable, writable=writable,
                                       stack_cleanup=function["abi"]["stack_cleanup"])
        if name in COPY_SIZES:
            if not ARENA_BASE <= result < ARENA_BASE + len(arena):
                raise RuntimeError("returned pointer outside fixture allocation")
            result -= ARENA_BASE
    elif sys.argv[1] == "candidate":
        fields = [inputs["arena"], inputs.get("destination", inputs.get("base", 0)),
                  inputs.get("source", 0), inputs.get("index", 0), inputs.get("enabled", 0)]
        process = subprocess.run([sys.argv[2], name], input=" ".join(map(str, fields)) + "\n",
                                 text=True, capture_output=True, check=True, timeout=3)
        lines = process.stdout.splitlines()
        if len(lines) != 2:
            raise RuntimeError("candidate emitted wrong observation shape")
        result = int(lines[0])
        after = bytes.fromhex(lines[1])
        if len(after) != len(arena):
            raise RuntimeError("candidate changed arena length")
    else:
        raise ValueError("unknown backend")
    json.dump({"schema_version": 1, "case_id": request["case"]["id"], "termination": "return",
               "return": result, "memory": {"arena": after.hex()}, "calls": []}, sys.stdout)


if __name__ == "__main__":
    main()

"""One JSON request per process, original slice or compiled native candidate."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.daodecomp.harness import load_json
from tools.daodecomp.leaf import execute_leaf, load_slice


def main():
    request = json.load(sys.stdin)
    registry = load_json(ROOT / "analysis/functions.json")
    function = next(f for f in registry["functions"] if f["id"] == request["function_id"])
    inputs = request["case"]["inputs"]
    if request["schema_version"] != 1 or set(inputs) != {"value"}:
        raise ValueError("wrong protocol or input keys")
    value = inputs["value"]
    if type(value) is not int or not 0 <= value <= 0xffffffff:
        raise ValueError("expected u32 input")
    if sys.argv[1] == "original":
        address, code = load_slice(sys.argv[2], function["module_sha256"], function["rva"],
                                   function["size"], function["code_sha256"])
        result = execute_leaf(address, code, value)
    elif sys.argv[1] == "candidate":
        raw = subprocess.run([sys.argv[2], function["name"]], input=f"{value}\n", text=True,
                             capture_output=True, check=True, timeout=3)
        result = int(raw.stdout.strip())
    else:
        raise ValueError("unknown backend")
    json.dump({"schema_version": 1, "case_id": request["case"]["id"], "termination": "return",
               "return": result, "memory": {}, "calls": []}, sys.stdout)


if __name__ == "__main__":
    main()

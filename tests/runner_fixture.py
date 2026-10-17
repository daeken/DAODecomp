"""Fault injection for the harness tests, not a game oracle."""
import json
from pathlib import Path
import sys
import time

mode = sys.argv[1]
if mode == "crash":
    raise SystemExit(17)
if mode == "hang":
    time.sleep(10)
if mode == "malformed":
    print("not JSON")
    raise SystemExit()
request = json.load(sys.stdin)
value = request["case"]["inputs"]["value"]
obs = {"schema_version": 1, "case_id": request["case"]["id"], "termination": "return",
       "return": value, "memory": {"state": "00000000"}, "calls": []}
if mode == "return_mismatch":
    obs["return"] = (value + 1) & 0xFFFFFFFF
elif mode == "memory_mismatch":
    obs["memory"]["state"] = "01000000"
elif mode == "call_mismatch":
    obs["calls"] = [{"name": "log", "args": [1], "result": None}]
elif mode == "missing_memory":
    obs["memory"] = {}
elif mode == "nondeterministic":
    path = Path(sys.argv[2])
    value = int(path.read_text()) + 1 if path.exists() else 0
    path.write_text(str(value))
    obs["return"] = value
elif mode == "bool_return":
    obs["return"] = True
json.dump(obs, sys.stdout)


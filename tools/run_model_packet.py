"""Run one explicitly requested implementation packet through a read-only CLI worker.

Records raw output, wall time and reported token usage. Does not apply code, approve
results, retry, merge or launch additional workers. Reuses normal Codex CLI auth.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--model", default="gpt-6.1-sol")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("timeout must be positive")
    packet = args.packet.resolve().read_bytes()
    packet.decode("utf-8")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    schema = {"type": "object", "properties": {
        "source": {"type": "string"},
        "functions": {"type": "array", "items": {"type": "object", "properties": {
            "name": {"type": "string"}, "suggested_name": {"type": "string"},
            "explanation": {"type": "string"}},
            "required": ["name", "suggested_name", "explanation"], "additionalProperties": False}},
        "uncertainties": {"type": "array", "items": {"type": "string"}}},
        "required": ["source", "functions", "uncertainties"], "additionalProperties": False}
    schema_path = output / "response-schema.json"
    schema_path.write_text(json.dumps(schema), encoding="utf-8")
    command = ["codex", "exec", "--model", args.model, "--sandbox", "read-only", "--ephemeral",
               "-c", 'model_reasoning_effort="medium"', "--json", "--output-schema", str(schema_path),
               "--output-last-message", str(output / "response.json"), "-"]
    started = time.monotonic()
    timed_out = False
    with (output / "events.jsonl").open("wb") as events, (output / "stderr.log").open("wb") as stderr:
        with subprocess.Popen(command, stdin=subprocess.PIPE, stdout=events, stderr=stderr,
                              start_new_session=(os.name == "posix")) as process:
            try:
                process.communicate(packet, timeout=args.timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                if os.name == "posix":
                    os.killpg(process.pid, signal.SIGKILL)
                else:
                    process.kill()
                process.communicate()
    parsed = [json.loads(line) for line in (output / "events.jsonl").read_text().splitlines() if line.strip()]
    usage = [event["usage"] for event in parsed if event.get("type") == "turn.completed" and "usage" in event]
    tools = [event.get("item", {}).get("type") for event in parsed if event.get("type") == "item.completed"
             and event.get("item", {}).get("type") in
             {"command_execution", "file_change", "mcp_tool_call", "web_search"}]
    result = {"schema_version": 1, "requested_model": args.model, "reasoning_effort": "medium",
              "packet_sha256": hashlib.sha256(packet).hexdigest(), "command": command,
              "elapsed_seconds": round(time.monotonic() - started, 3), "exit_code": process.returncode,
              "timed_out": timed_out, "usage": usage, "tool_items": tools,
              "output_exists": (output / "response.json").is_file()}
    (output / "run.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result), flush=True)
    return 0 if process.returncode == 0 and not timed_out and result["output_exists"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

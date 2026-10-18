"""Generate README progress from metadata, optionally using only Git's index.

No game files, emulator, build products or third-party Python packages are needed.
The hook updates only the generated block in the index and working README.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys

START = "<!-- progress:start -->"
END = "<!-- progress:end -->"
IMPLEMENTED = {"implemented", "corpus_pass", "reviewed", "integrated"}


def git(root, *args, data=None):
    return subprocess.run(["git", "-C", str(root), *args], input=data,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout


def relative(path):
    value = PurePosixPath(path)
    if not path or value.is_absolute() or ".." in value.parts or "\\" in path:
        raise ValueError(f"invalid repository path: {path}")
    return value


def checkpoint_inventory(registry):
    active = [f for f in registry['functions'] if f.get('status') in {'implemented','corpus_pass','reviewed','integrated'}]
    negatives = {'bit_mask_or_all','fn_00061fa0','fn_00061f40','fn_00347d10',
                 'fn_00347cf0','fn_00347d70','fn_00347db0','fn_00347eb0'}
    allowed = {'scalar','memory-001','object-counters-001','indexed-stores-001','linked-structures-001','object-bitfields-001','direct-object-fields-001','startup-string-001'}
    if any(f.get('backend','scalar') not in allowed for f in active):
        raise ValueError('unknown current checkpoint route')
    expected = {(f['id'],False) for f in active}
    expected |= {(f['id'],True) for f in active if f['name'] in negatives or f.get('backend') in {'linked-structures-001','object-bitfields-001','direct-object-fields-001','startup-string-001'}}
    return expected


class Snapshot:
    def __init__(self, root, staged=False):
        self.root = Path(root)
        self.staged = staged
        self.entries = {}
        self.cache = {}
        if staged:
            for entry in git(root, "ls-files", "--stage", "-z").split(b"\0"):
                if not entry:
                    continue
                info, name = entry.decode("utf-8").split("\t", 1)
                mode, oid, stage = info.split()
                if stage != "0":
                    raise ValueError("resolve index conflicts before updating progress")
                self.entries[name] = (mode, oid)

    def read(self, name):
        relative(name)
        if name not in self.cache:
            if self.staged:
                mode, oid = self.entries.get(name, (None, None))
                if mode not in {"100644", "100755"}:
                    raise ValueError(f"missing or non-regular staged file: {name}")
                self.cache[name] = git(self.root, "cat-file", "blob", oid)
            else:
                path = self.root / name
                if path.is_symlink() or not path.is_file():
                    raise ValueError(f"missing or non-regular file: {name}")
                self.cache[name] = path.read_bytes()
        return self.cache[name]

    def document(self, name):
        result = json.loads(self.read(name))
        if result.get("schema_version") == 2 and name.startswith("analysis/validation/"):
            unsigned = dict(result)
            expected = unsigned.pop("attestation_sha256", None)
            actual = hashlib.sha256(json.dumps(unsigned, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
            if (result.get("policy") != "clean-build-local-groups-003"
                    or result.get("fresh_clean_build") is not True
                    or result.get("complete_checkpoint") is not True
                    or result.get("proof") is not False
                    or result.get("native_windows_validated") is not False
                    or actual != expected):
                raise ValueError(f"invalid fresh reuse attestation: {name}")
            registry = self.document('analysis/functions.json')
            pairs = [(r.get('function_id'),r.get('negative_control')) for r in result.get('records',[])]
            if (any(type(negative) is not bool for _,negative in pairs)
                    or len(pairs) != len(set(pairs)) or set(pairs) != checkpoint_inventory(registry)):
                raise ValueError(f"incomplete current reuse checkpoint: {name}")
            for record in result.get("records", []):
                if (record.get("provenance_kind") != "fresh_clean_build_and_exact_execution_inputs"
                        or type(record.get("comparison_reused")) is not bool
                        or not record.get("historical_comparison")
                        or not record.get("current_identity_sha256")):
                    raise ValueError(f"incomplete reuse provenance: {name}")
        elif result.get("schema_version") != 1:
            raise ValueError(f"unsupported metadata schema: {name}")
        return result

    def validation_paths(self):
        if self.staged:
            return sorted(p for p in self.entries if p.startswith("analysis/validation/") and p.endswith(".json"))
        return sorted(p.relative_to(self.root).as_posix()
                      for p in (self.root / "analysis/validation").rglob("*.json"))


def local_artifact(path):
    first = relative(path).parts[0]
    return first in {"local", "reports", "installer", "gamedata", ".venv"} or first.startswith("build")


def evidence_matches(snapshot, function, record):
    counts = record.get("case_counts", {})
    if (record.get("status") != "corpus_pass" or record.get("negative_control") is not False
            or record.get("artifacts_unchanged") is not True
            or type(record.get("repeats_per_side")) is not int or record["repeats_per_side"] < 2
            or set(counts) != {"corpus_pass"} or type(counts["corpus_pass"]) is not int
            or counts["corpus_pass"] <= 0):
        return False
    artifacts = record.get("artifacts_sha256", {})
    required = {function["source"], function["contract"], "analysis/functions.json", "analysis/reference-build.json"}
    if not required <= artifacts.keys() or any(local_artifact(p) for p in required):
        return False
    for path, expected in artifacts.items():
        if local_artifact(path):
            continue  # Private inputs/build outputs are intentionally absent from clones.
        try:
            actual = hashlib.sha256(snapshot.read(path)).hexdigest()
        except (ValueError, FileNotFoundError):
            return False
        if actual != expected:
            return False
    return True


def progress(snapshot):
    registry = snapshot.document("analysis/functions.json")
    reference = snapshot.document("analysis/reference-build.json")
    inventory = snapshot.document("analysis/static-summary.json")
    if inventory["module_sha256"] != reference["module"]["sha256"]:
        raise ValueError("static inventory and reference build differ")
    functions = {}
    for function in registry["functions"]:
        if function["id"] in functions:
            raise ValueError(f'duplicate function identity: {function["id"]}')
        functions[function["id"]] = function
    implemented = {key: f for key, f in functions.items() if f["status"] in IMPLEMENTED}
    for function in implemented.values():
        snapshot.read(function["source"])
        contract = snapshot.document(function["contract"])
        if contract["kind"] != "game" or contract["function_id"] != function["id"]:
            raise ValueError("implemented function has a mismatched contract")
    emulated, native = {}, {}
    for path in snapshot.validation_paths():
        document = snapshot.document(path)
        for record in document.get("records", []):
            key = record.get("function_id")
            if key not in implemented or not evidence_matches(snapshot, implemented[key], record):
                continue
            if document.get("native_windows_validated") is True:
                native[key] = max(native.get(key, 0), record["case_counts"]["corpus_pass"])
            elif document.get("evidence_level") == "emulator_corpus_agreement":
                emulated[key] = max(emulated.get(key, 0), record["case_counts"]["corpus_pass"])
    return "\n".join([
        "## Progress", "",
        "<!-- Generated by tools/update_progress.py; edit the metadata, not this block. -->", "",
        "| Measure | Count |", "| --- | ---: |",
        f'| Function hypotheses in the initial main EXE inventory | {inventory["function_hypotheses"]:,} |',
        f"| Functions in the recovery registry | {len(functions):,} |",
        f"| C++ implementations | {len(implemented):,} |",
        f"| Implementations with current emulator corpus evidence | {len(emulated):,} |",
        f"| Input cases across those functions (excluding repeat runs) | {sum(emulated.values()):,} |",
        f"| Implementations with current native Windows corpus evidence | {len(native):,} |", "",
        "Corpus evidence is not a universal equivalence proof. The inventory is provisional;",
        "these counts are not a percentage of whole-game completion. Evidence counts require",
        "the recorded tracked-input hashes to match this revision; private binaries and",
        "local reports are not rechecked by this README updater.", "",
        "Sources: [function registry](analysis/functions.json),",
        "[static inventory summary](analysis/static-summary.json), and",
        "[validation records](analysis/validation/).",
    ])


def replace_block(readme, content):
    if readme.count(START) != 1 or readme.count(END) != 1:
        raise ValueError("README must contain exactly one progress:start/progress:end marker pair")
    before, remainder = readme.split(START)
    if END not in remainder:
        raise ValueError("README progress markers are out of order")
    _, after = remainder.split(END)
    newline = "\r\n" if "\r\n" in readme else "\n"
    return before + START + newline + content.replace("\n", newline) + newline + END + after


def update(root, staged=False, check=False):
    snapshot = Snapshot(root, staged)
    before = snapshot.read("README.md")
    content = progress(snapshot)
    after = replace_block(before.decode("utf-8"), content).encode("utf-8")
    if check:
        if before != after:
            raise ValueError("README progress is stale; run python3 tools/update_progress.py")
        return False
    working = Path(root) / "README.md"
    if working.is_symlink():
        raise ValueError("README must be a regular file")
    working_before = working.read_bytes()
    working_after = replace_block(working_before.decode("utf-8"), content).encode("utf-8")
    # Compute both replacements before touching either copy. Keep all other edits.
    if staged and before != after:
        oid = git(root, "hash-object", "-w", "--stdin", data=after).decode().strip()
        mode = snapshot.entries["README.md"][0]
        git(root, "update-index", "--cacheinfo", f"{mode},{oid},README.md")
    if working_before != working_after:
        working.write_bytes(working_after)
    return before != after or working_before != working_after


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true", help="use Git's index and stage only the generated README block")
    parser.add_argument("--check", action="store_true", help="fail if progress is stale; do not edit anything")
    args = parser.parse_args()
    try:
        root = Path(git(Path.cwd(), "rev-parse", "--show-toplevel").decode().strip())
        if update(root, staged=args.staged, check=args.check):
            print("Updated README progress" + (" in the commit and working copy." if args.staged else "."))
        return 0
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        print(f"Progress update failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

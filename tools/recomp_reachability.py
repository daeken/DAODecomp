"""Bounded static helper selection for startup exploration, never acceptance.

Only compiled direct call/jump operands supply edges. Candidate ownership and
original bytes must match the pinned inventory. An optional helper that cannot
translate stays absent from the dispatcher and will fail if execution reaches it.
"""
import copy
from collections import deque
from pathlib import Path
import struct
import subprocess
from tools import recomp
from tools.daodecomp.pe import fingerprint


def inventory_selection(state, index_path, rva):
    index_path = Path(index_path)
    index_sha = recomp.digest(index_path.read_bytes())
    index = recomp.load(index_path)
    if recomp.digest(index_path.read_bytes()) != index_sha:
        raise RuntimeError("inventory changed while reading direct-call bounds")
    if index["module_sha256"].lower() != state["binary_sha256"]:
        raise ValueError("inventory module identity changed")
    matches = [f for f in index["functions"] if f["rva"] == rva]
    if len(matches) != 1 or not matches[0]["body_ranges"]:
        raise ValueError("target needs reviewed discovery bounds")
    function = matches[0]
    bounds = function["body_ranges"]
    if min(b["start_rva"] for b in bounds) != rva:
        raise ValueError("inventory range starts before entry")
    if any(b["end_rva_inclusive"] < b["start_rva"] for b in bounds):
        raise ValueError("invalid inventory code range")
    end = max(b["end_rva_inclusive"] for b in bounds) + 1
    if any(any(b["start_rva"] <= f["rva"] <= b["end_rva_inclusive"] for b in bounds)
           for f in index["functions"] if f["rva"] != rva):
        raise ValueError("inventory owned ranges cross another function entry; review bounds")
    binary = recomp.checked_binary(state)
    pe, image = fingerprint(binary), binary.read_bytes()
    if pe["sha256"] != state["binary_sha256"] or recomp.digest(image) != state["binary_sha256"]:
        raise RuntimeError("binary changed while reading direct-call bounds")
    size = end - rva
    sections = [s for s in pe["sections"] if s["rva"] <= rva and end <= s["rva"] + s["file_size"]]
    if len(sections) != 1:
        raise ValueError("inventory bounds exceed original file-backed bytes")
    offset = sections[0]["file_offset"] + rva - sections[0]["rva"]
    return dict(rva=rva, size=size, purpose="static direct-call candidate; " + function["name"],
                ranges=[dict(rva=b["start_rva"], size=b["end_rva_inclusive"] - b["start_rva"] + 1) for b in bounds],
                slice_sha256=recomp.digest(image[offset:offset + size]), inventory=str(index_path.resolve()),
                inventory_sha256=index_sha, inventory_body_ranges=bounds,
                bounds_status="traversal envelope of pinned inventory hypotheses; actual decoding/lifting required",
                contract_status="static startup exploration only; execution unobserved; signature/behavior unknown")


def overlaps_selection(selection, functions):
    return any(a["rva"] < b["rva"] + b["size"] and b["rva"] < a["rva"] + a["size"]
               for a in (selection.get("ranges") or [selection])
               for function in functions for b in (function.get("ranges") or [function]))


def expand_direct_calls(plan, projects, inventories, seeds, depth=2, limit=64):
    """Atomically extend the in-memory plan after individual candidate lifts.

    Seeds are selected entries; they can include explicitly requested static
    roots as well as reached functions. Every seed must translate. Depth and
    attempt limits bound discovery, not program execution or validation.
    """
    if not 0 <= depth <= 8 or not 1 <= limit <= 512:
        raise ValueError("invalid direct-call discovery budget")
    working = copy.deepcopy(plan)
    states, spaces = {}, {}
    for role, project in projects.items():
        state = recomp.state(Path(project))
        binary = recomp.checked_binary(state)
        pe = fingerprint(binary)
        identity = working["roles"][role]
        if state["module"] != identity["module"] or state["binary_sha256"] != identity["binary_sha256"]:
            raise ValueError("direct-call project differs from pinned module")
        if pe["format"] != "PE32" or pe["architecture"] != "x86" or pe["image_base"] != state["image_base"]:
            raise ValueError("direct-call project differs from its PE32 namespace")
        image = binary.read_bytes()
        optional = struct.unpack_from("<I", image, 0x3c)[0] + 24
        spaces[role] = (state["image_base"], struct.unpack_from("<I", image, optional + 56)[0])
        states[role] = state
    if any(base < other + length and other < base + size
           for role, (base, size) in spaces.items() for name, (other, length) in spaces.items() if role != name):
        raise ValueError("direct-call modules overlap")
    queue = deque((seed["module"], seed["rva"], 0) for seed in seeds) if depth else deque()
    visited, attempts, accepted, deferred, edges, backends = set(), 0, [], [], [], {}
    lifted = {}
    inventory_snapshots = {}
    truncated = False

    def lift_many(role, selections):
        state = states[role]
        functions = []
        for selection in selections:
            existing = next((f for f in state["functions"] if f["rva"] == selection["rva"]), {})
            if existing and existing["size"] != selection["size"]:
                raise ValueError("candidate conflicts with annotated function bounds")
            functions.append(dict(selection, annotations=existing.get("annotations", {}), structures=existing.get("structures", {})))
        result = recomp.export(dict(state, functions=functions))
        if sorted(f["rva"] for f in result["functions"]) != sorted(f["rva"] for f in selections):
            raise RuntimeError("direct-call exporter returned different function identities")
        snapshot = dict(artifacts=result["backend_artifacts"], module_policy_sha256=result["module_policy_sha256"])
        fingerprint = recomp.digest(recomp.encoded(snapshot))
        if backends and fingerprint not in backends:
            raise RuntimeError("backend changed during direct-call discovery")
        backends[fingerprint] = snapshot
        return result["functions"], fingerprint

    def lift(role, selection):
        functions, fingerprint = lift_many(role, [selection])
        return functions[0], fingerprint

    # Already-selected roots can be translated together. This avoids one bridge
    # startup per constructor when explicitly exploring all selected code.
    if depth:
        for role in states:
            rvas = {seed["rva"] for seed in seeds if seed["module"] == role}
            selections = [f for f in working["roles"][role]["functions"] if f["rva"] in rvas]
            if len(selections) != len(rvas):
                raise ValueError("direct-call seed is not selected")
            if selections:
                functions, seed_backend = lift_many(role, selections)
                lifted.update({(role, f["rva"]): (f, seed_backend) for f in functions})

    while queue:
        role, rva, distance = queue.popleft()
        if (role, rva) in visited:
            continue
        visited.add((role, rva))
        selection = next(f for f in working["roles"][role]["functions"] if f["rva"] == rva)
        # A reached seed must translate; failure propagates to the caller.
        function, backend = lifted.get((role, rva)) or lift(role, selection)
        if distance >= depth:
            continue
        owned_instructions = {spaces[role][0] + i["rva"] for i in function["instructions"]}
        for transfer in function["abi"]["transfers"]:
            target = transfer["direct_target"]
            if transfer["kind"] not in ("Call", "Jmp") or target is None or target in owned_instructions:
                continue
            owner = next((name for name, (base, size) in spaces.items() if base <= target < base + size), None)
            edge = dict(from_module=role, from_rva=rva, instruction_rva=transfer["instruction_rva"],
                        target=target, target_module=owner, distance=distance + 1)
            edges.append(edge)
            if owner is None:
                edge["status"] = "outside translated module namespaces"
                continue
            target_rva = target - spaces[owner][0]
            edge["target_rva"] = target_rva
            if any(f["rva"] == target_rva for f in working["roles"][owner]["functions"]):
                edge["status"] = "already selected"
                # Selection does not imply that this helper's own callees were
                # explored. Follow it within the same depth bound as new code.
                queue.append((owner,target_rva,distance+1))
                continue
            if (owner, target_rva) in visited:
                edge["status"] = "previously deferred"
                continue
            if attempts >= limit:
                edge["status"] = "discovery attempt limit; target remains unresolved"
                truncated = True
                continue
            attempts += 1
            try:
                candidate = inventory_selection(states[owner], inventories[owner], target_rva)
                previous_sha = inventory_snapshots.setdefault(owner, candidate["inventory_sha256"])
                if previous_sha != candidate["inventory_sha256"]:
                    raise RuntimeError("inventory changed during direct-call discovery")
                if overlaps_selection(candidate, working["roles"][owner]["functions"]):
                    raise ValueError("direct-call candidate overlaps a selected function; review ownership")
                translated, candidate_backend = lift(owner, candidate)
            except (ValueError, subprocess.TimeoutExpired) as error:
                visited.add((owner, target_rva))
                edge["status"] = "deferred; target remains unresolved"
                deferred.append(dict(edge, reason=str(error)))
                continue
            candidate["direct_call_provenance"] = dict(edge, code_sha256=translated["code_sha256"],
                                                       backend_sha256=candidate_backend)
            working["roles"][owner]["functions"].append(candidate)
            working["roles"][owner]["functions"].sort(key=lambda f: f["rva"])
            edge["status"] = "selected after lift; execution unobserved"
            accepted.append(dict(module=owner, rva=target_rva, size=candidate["size"], distance=distance + 1))
            lifted[(owner, target_rva)] = (translated, candidate_backend)
            queue.append((owner, target_rva, distance + 1))
    for role, state in states.items():
        recomp.checked_binary(state)
    for role, sha in inventory_snapshots.items():
        if recomp.digest(Path(inventories[role]).read_bytes()) != sha:
            raise RuntimeError("inventory changed during direct-call discovery")
    plan.clear()
    plan.update(working)
    return dict(scope="Static helper discovery only, not behavioral acceptance. Deferral adds no code or fallback; missing dispatch targets fail if reached.",
                depth=depth, limit=limit, attempts=attempts, truncated=truncated, seeds=seeds,
                accepted=accepted, deferred=deferred, edges=edges, backends=backends)

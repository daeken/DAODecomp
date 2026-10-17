"""Deterministic disjoint-list fixtures for linked-structures-001."""
import hashlib
import itertools
import struct

ARENA_BASE = 0x02000000
ARENA_SIZE = 512
LIST_SIZE = 32
NODE_SIZE = 12
LIST_LIMIT = ARENA_SIZE - LIST_SIZE
NODE_LIMIT = ARENA_SIZE - NODE_SIZE
FUNCTIONS = {"fn_00018390": "append", "fn_000183d0": "pop"}

# Four deliberately different layouts: unaligned objects, a list ending exactly
# at byte 512, node offset zero, an end-of-arena node, and nonmonotonic pool order.
LAYOUTS = (
    (0, (131, 32, 421, 233)),
    (480, (0, 144, 64, 300)),
    (173, (335, 0, 500, 37)),
    (71, (131, 0, 421, 233)),
)


def _u32(data, offset):
    return struct.unpack_from("<I", data, offset)[0]


def _put_u32(data, offset, value):
    struct.pack_into("<I", data, offset, value & 0xFFFFFFFF)


def _ptr(offset):
    return ARENA_BASE + offset


def _read_nodes(encoded):
    if type(encoded) is not str or len(encoded) != 32 or any(c not in "0123456789abcdef" for c in encoded):
        raise ValueError("nodes must be 16 bytes of lowercase hex offsets")
    return struct.unpack("<4I", bytes.fromhex(encoded))


def _check_intervals(list_offset, node_offsets):
    intervals = [(list_offset, list_offset + LIST_SIZE, "list")]
    intervals.extend((off, off + NODE_SIZE, f"node {index}") for index, off in enumerate(node_offsets))
    for start, end, label in intervals:
        limit = LIST_LIMIT if label == "list" else NODE_LIMIT
        if type(start) is not int or not 0 <= start <= limit or end > ARENA_SIZE:
            raise ValueError(f"{label} interval outside arena")
    for i, (start, end, label) in enumerate(intervals):
        for other_start, other_end, other_label in intervals[i + 1:]:
            if start < other_end and other_start < end:
                raise ValueError(f"overlapping {label} and {other_label}")


def active_chain(arena, list_offset, node_offsets):
    """Return ordered node offsets after strict canonical-graph validation."""
    node_by_pointer = {_ptr(offset): offset for offset in node_offsets}
    head, tail = _u32(arena, list_offset + 0x18), _u32(arena, list_offset + 0x1C)
    if head == 0 or tail == 0:
        if head != 0 or tail != 0:
            raise ValueError("empty list must have null head and tail")
        return []
    if head not in node_by_pointer or tail not in node_by_pointer:
        raise ValueError("list endpoint is not a pool node")
    chain, seen, previous = [], set(), 0
    pointer = head
    while pointer:
        if pointer not in node_by_pointer or pointer in seen:
            raise ValueError("active chain contains a foreign node or cycle")
        offset = node_by_pointer[pointer]
        if _u32(arena, offset + 8) != previous:
            raise ValueError("active previous links are not reciprocal")
        seen.add(pointer)
        chain.append(offset)
        following = _u32(arena, offset + 4)
        if following and following not in node_by_pointer:
            raise ValueError("active next link is not a pool node")
        previous, pointer = pointer, following
    if not chain or chain[-1] != node_by_pointer[tail] or _u32(arena, chain[-1] + 4) != 0:
        raise ValueError("tail does not terminate the active chain")
    if len(chain) != len(seen):
        raise ValueError("invalid active chain")
    return chain


def fixture(name, inputs):
    if name not in FUNCTIONS:
        raise ValueError("unknown linked-structure function")
    expected = {"arena", "list", "nodes"} | ({"node"} if name == "fn_00018390" else set())
    if type(inputs) is not dict or set(inputs) != expected:
        raise ValueError("input keys differ from linked-structure function contract")
    arena_hex = inputs["arena"]
    if type(arena_hex) is not str or len(arena_hex) != ARENA_SIZE * 2 or any(
            c not in "0123456789abcdef" for c in arena_hex):
        raise ValueError("expected 512-byte lowercase hex arena")
    list_offset = inputs["list"]
    if type(list_offset) is not int or not 0 <= list_offset <= LIST_LIMIT:
        raise ValueError("list offset must be a u32 in 0..480")
    node_offsets = _read_nodes(inputs["nodes"])
    if len(set(node_offsets)) != 4:
        raise ValueError("pool must contain four distinct node offsets")
    _check_intervals(list_offset, node_offsets)
    arena = bytes.fromhex(arena_hex)
    chain = active_chain(arena, list_offset, node_offsets)
    if name == "fn_00018390":
        node = inputs["node"]
        if type(node) is not int or node not in node_offsets:
            raise ValueError("append node must be a pool offset")
        if node in chain:
            raise ValueError("append node must be inactive")
        if len(chain) > 3:
            raise ValueError("append input must leave pool capacity")
        writable = [(node + 8, 4), (node + 4, 4), (list_offset + 0x1C, 4)]
        if chain:
            writable.append((chain[-1] + 4, 4))
        else:
            writable.append((list_offset + 0x18, 4))
        readable = [(list_offset + 0x1C, 4)]
    else:
        if len(chain) > 4:
            raise ValueError("pop input exceeds pool capacity")
        readable = [(list_offset + 0x18, 4)]
        writable = []
        if chain:
            readable.append((chain[0] + 4, 4))
            if len(chain) == 1:
                writable = [(list_offset + 0x18, 4), (list_offset + 0x1C, 4)]
            else:
                writable = [(list_offset + 0x18, 4), (chain[1] + 8, 4)]
    return arena, readable, writable, chain, node_offsets


def _arena_seed(name, suite, index):
    return b"".join(hashlib.sha256(
        f"linked-structures-001:{name}:{suite}:{index}:{chunk}".encode()).digest()
        for chunk in range(16))


def _inputs(name, arena, list_offset, node_offsets, node=None):
    inputs = {"arena": bytes(arena).hex(), "list": list_offset,
              "nodes": struct.pack("<4I", *node_offsets).hex()}
    if name == "fn_00018390":
        inputs["node"] = node
    return inputs


def _with_chain(arena, list_offset, node_offsets, identities):
    """Initialize just endpoints and active links; inactive bytes stay arbitrary."""
    _put_u32(arena, list_offset + 0x18, _ptr(node_offsets[identities[0]]) if identities else 0)
    _put_u32(arena, list_offset + 0x1C, _ptr(node_offsets[identities[-1]]) if identities else 0)
    for i, identity in enumerate(identities):
        offset = node_offsets[identity]
        _put_u32(arena, offset + 4, _ptr(node_offsets[identities[i + 1]]) if i + 1 < len(identities) else 0)
        _put_u32(arena, offset + 8, _ptr(node_offsets[identities[i - 1]]) if i else 0)


def _model_step(name, inputs):
    arena, _, _, chain, node_offsets = fixture(name, inputs)
    after = bytearray(arena)
    list_offset = inputs["list"]
    if name == "fn_00018390":
        offset = inputs["node"]
        tail = chain[-1] if chain else None
        _put_u32(after, offset + 8, _ptr(tail) if tail is not None else 0)
        if tail is not None:
            _put_u32(after, tail + 4, _ptr(offset))
        _put_u32(after, offset + 4, 0)
        if not chain:
            _put_u32(after, list_offset + 0x18, _ptr(offset))
        _put_u32(after, list_offset + 0x1C, _ptr(offset))
        return _ptr(offset), bytes(after)
    if not chain:
        return 0, bytes(after)
    old = chain[0]
    following = _u32(arena, old + 4)
    if following == 0:
        _put_u32(after, list_offset + 0x18, 0)
        _put_u32(after, list_offset + 0x1C, 0)
    else:
        _put_u32(after, list_offset + 0x18, following)
        _put_u32(after, node_offsets[next(i for i, off in enumerate(node_offsets) if _ptr(off) == following)] + 8, 0)
    return _ptr(old), bytes(after)


def composition_plan():
    """Return per-layout append/drain/reappend operations with pre-state inputs."""
    result = []
    for layout_index, (list_offset, node_offsets) in enumerate(LAYOUTS):
        arena = bytearray(_arena_seed("composition", "composition", layout_index))
        _with_chain(arena, list_offset, node_offsets, (1, 3))
        steps = [("append", 0), ("pop", None), ("pop", None), ("pop", None), ("pop", None),
                 ("append", 1)]
        # Four pop calls are sufficient to remove three linked nodes and observe
        # the canonical empty-list no-op before reusing a node with retained links.
        current = bytes(arena)
        for operation, identity in steps:
            step_name = "fn_00018390" if operation == "append" else "fn_000183d0"
            op_inputs = _inputs(step_name, current, list_offset, node_offsets,
                                node_offsets[identity] if operation == "append" else None)
            result.append((step_name, op_inputs))
            _, current = _model_step(step_name, op_inputs)
    return result


def composition_snapshots(name):
    """Return pre-state inputs from deterministic append/drain/reappend sequences."""
    if name not in FUNCTIONS:
        raise ValueError("unknown linked-structure function")
    return [inputs for function, inputs in composition_plan() if function == name]


def _heldout_inputs(name, index):
    layout_index = index % len(LAYOUTS)
    list_offset, node_offsets = LAYOUTS[layout_index]
    # Stable per-case entropy varies payloads and inactive link garbage without
    # deriving expected behavior from a candidate or from an output oracle.
    seed = _arena_seed(name, "heldout-random", index)
    arena = bytearray(seed)
    identities = list(range(4))
    identities.sort(key=lambda item: hashlib.sha256(seed + bytes([item])).digest())
    if name == "fn_00018390":
        length = index % 4
        active = identities[:length]
        inactive = identities[length:]
        node = inactive[(index // 4) % len(inactive)]
    else:
        length = index % 5
        active = identities[:length]
        node = None
    _with_chain(arena, list_offset, node_offsets, active)
    return _inputs(name, bytes(arena), list_offset, node_offsets,
                   node_offsets[node] if node is not None else None)


def cases(name, suite="public"):
    if name not in FUNCTIONS or suite not in ("public", "heldout"):
        raise ValueError("unknown function or suite")
    inputs_list = []
    if suite == "public":
        for list_offset, node_offsets in LAYOUTS:
            arena_seed = bytearray(_arena_seed(name, "public", len(inputs_list) // 64))
            if name == "fn_00018390":
                for length in range(4):
                    for order in itertools.permutations(range(4), length):
                        for node_identity in range(4):
                            if node_identity in order:
                                continue
                            arena = bytearray(arena_seed)
                            _with_chain(arena, list_offset, node_offsets, order)
                            inputs_list.append(_inputs(name, arena, list_offset, node_offsets,
                                                       node_offsets[node_identity]))
            else:
                for length in range(5):
                    for order in itertools.permutations(range(4), length):
                        arena = bytearray(arena_seed)
                        _with_chain(arena, list_offset, node_offsets, order)
                        inputs_list.append(_inputs(name, arena, list_offset, node_offsets))
    else:
        inputs_list = composition_snapshots(name)
        # Keep the sequence-reached snapshots explicit in heldout, then fill to
        # the fixed suite size with stable independent valid graph states.
        index = 0
        seen = {repr(item) for item in inputs_list}
        while len(inputs_list) < 128:
            item = _heldout_inputs(name, index)
            index += 1
            if repr(item) not in seen:
                seen.add(repr(item))
                inputs_list.append(item)
    expected_count = 256 if name == "fn_00018390" and suite == "public" else 260 if suite == "public" else 128
    if len(inputs_list) != expected_count:
        raise AssertionError(f"unexpected {suite} corpus size for {name}: {len(inputs_list)}")
    result = []
    for index, inputs in enumerate(inputs_list):
        fixture(name, inputs)
        result.append({"id": f"{suite}-{index:04d}", "inputs": inputs})
    return result


def negative_cases(name):
    if name not in FUNCTIONS:
        raise ValueError("unknown linked-structure function")
    return cases(name, "public")

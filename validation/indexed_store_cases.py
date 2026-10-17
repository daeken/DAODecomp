"""Deterministic initialized-arena cases for indexed store slices."""
import hashlib
import struct

ARENA_SIZE = 512
MAX_OBJECT_OFFSET = 128
STORE_WIDTHS = {"fn_00347d10": (0x12A, 2), "fn_00347d50": (0x138, 1)}
_VALUES = (0, 1, 0x7F, 0x80, 0xFF, 0x100, 0x101, 0x7FFF, 0x8000,
           0xFFFF, 0x10000, 0x10001, 0x80000000, 0xFFFFFFFF)


def fixture(name, inputs):
    if name not in STORE_WIDTHS or type(inputs) is not dict or set(inputs) != {
            "arena", "entry_eax", "index", "object", "value"}:
        raise ValueError("unknown function or input keys")
    arena_hex = inputs["arena"]
    if (type(arena_hex) is not str or len(arena_hex) != ARENA_SIZE * 2
            or any(c not in "0123456789abcdef" for c in arena_hex)):
        raise ValueError("expected 512-byte lowercase hex arena")
    for key in ("entry_eax", "index", "value"):
        if type(inputs[key]) is not int or not 0 <= inputs[key] <= 0xFFFFFFFF:
            raise ValueError(f"{key} must be a u32")
    obj = inputs["object"]
    if type(obj) is not int or not 0 <= obj <= MAX_OBJECT_OFFSET:
        raise ValueError("object offset must be an integer in 0..128")
    arena = bytes.fromhex(arena_hex)
    low = inputs["index"] & 0xFF
    if low >= 7:
        return arena, [], []
    field, width = STORE_WIDTHS[name]
    start = obj + field + width * low
    if start + width > ARENA_SIZE:
        raise ValueError("store footprint outside arena")
    return arena, [], [(start, width)]


def _arena(name, suite, index):
    return b"".join(hashlib.sha256(
        f"object-fields-001:{name}:{suite}:{index}:{chunk}".encode()).digest()
        for chunk in range(16))


def cases(name, suite="public"):
    if name not in STORE_WIDTHS or suite not in ("public", "heldout"):
        raise ValueError("unknown function or suite")
    args = []
    if suite == "public":
        prefixes = (0, 0x100, 0xFFFF0000, 0x80000000)
        eax_values = (0, 0x12345600, 0xFFFF0000, 0xFFFFFFFF)
        objects = (0, 1, 3, 64, 128)
        for group, (prefix, eax) in enumerate(zip(prefixes, eax_values)):
            for low in range(256):
                i = len(args)
                args.append(dict(object=objects[i % len(objects)], index=prefix | low,
                                 value=_VALUES[i % len(_VALUES)], entry_eax=eax))
        all_values = sorted(set(_VALUES) | {1 << bit for bit in range(32)})
        for low in range(7):
            for value in all_values:
                args.append(dict(object=3, index=0x12340000 | low, value=value,
                                 entry_eax=0xA5C3FF01))
    else:
        for i in range(128):
            seed = hashlib.sha256(f"{name}:heldout:{i}".encode()).digest()
            index = int.from_bytes(seed[1:5], "little")
            if i % 2 == 0:
                index = (index & 0xFFFFFF00) | (seed[5] % 7)
            args.append(dict(object=seed[0] % 129, index=index,
                             value=int.from_bytes(seed[6:10], "little"),
                             entry_eax=int.from_bytes(seed[10:14], "little")))
    result = []
    for i, values in enumerate(args):
        case = {"id": f"{suite}-{i:04d}", "inputs": {
            "arena": _arena(name, suite, i).hex(), **values}}
        fixture(name, case["inputs"])
        result.append(case)
    return result


def negative_cases(name):
    if name != "fn_00347d10":
        raise ValueError("negative control applies only to fn_00347d10")
    return cases(name, "public")

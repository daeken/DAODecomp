"""Deterministic 512-byte initialized-arena cases for the three counter slices."""
import hashlib
import struct

ARENA_SIZE = 512
MAX_OBJECT_OFFSET = 128
FIELD_OFFSETS = {
    "fn_00061f40": 0xD0,
    "fn_00061f60": 0xD4,
    "fn_00061f80": 0xD8,
}


def fixture(name, inputs):
    if name not in FIELD_OFFSETS or not isinstance(inputs, dict) or set(inputs) != {"arena", "object"}:
        raise ValueError("unknown function or input keys")
    arena_hex, obj = inputs["arena"], inputs["object"]
    if (type(arena_hex) is not str or len(arena_hex) != ARENA_SIZE * 2
            or any(char not in "0123456789abcdef" for char in arena_hex)):
        raise ValueError("expected 512-byte lowercase hex arena")
    if type(obj) is not int or not 0 <= obj <= MAX_OBJECT_OFFSET:
        raise ValueError("object offset must be a u32 in 0..128")
    start = obj + FIELD_OFFSETS[name]
    if start + 4 > ARENA_SIZE:
        raise ValueError("counter footprint outside arena")
    return bytes.fromhex(arena_hex), [(start, 4)], [(start, 4)]


def _arena(name, suite, index):
    return b"".join(hashlib.sha256(
        f"object-fields-001:{name}:{suite}:{index}:{chunk}".encode()
    ).digest() for chunk in range(16))


def cases(name, suite="public"):
    if name not in FIELD_OFFSETS or suite not in ("public", "heldout"):
        raise ValueError("unknown function or suite")
    if suite == "public":
        values = sorted({0, 1, 2, 3, 0x7ffffffe, 0x7fffffff, 0x80000000,
                         0xfffffffc, 0xfffffffd, 0xfffffffe, 0xffffffff,
                         *(1 << bit for bit in range(32)),
                         *((1 << bit) - 1 for bit in range(1, 33))})
        arguments = [dict(object=obj, old=value)
                     for obj in (0, 1, 3, 64, 128) for value in values]
    else:
        arguments = []
        for index in range(128):
            seed = hashlib.sha256(f"{name}:heldout:{index}".encode()).digest()
            arguments.append(dict(object=seed[0] % 129,
                                  old=int.from_bytes(seed[1:5], "little")))
    result = []
    for index, args in enumerate(arguments):
        arena = bytearray(_arena(name, suite, index))
        offset = args["object"] + FIELD_OFFSETS[name]
        arena[offset:offset + 4] = struct.pack("<I", args["old"])
        case = {"id": f"{suite}-{index:04d}",
                "inputs": {"arena": arena.hex(), "object": args["object"]}}
        fixture(name, case["inputs"])
        result.append(case)
    return result


def negative_cases(name):
    """Use the exact public corpus for the D0-only sentinel-return mutation."""
    if name != "fn_00061f40":
        raise ValueError("the defined negative control applies only to fn_00061f40")
    return cases(name, "public")

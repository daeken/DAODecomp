"""Frozen public and held-out inputs for reviewed memory-001 routines."""
import hashlib

COPY_SIZES = {"fn_00061fa0": 16, "fn_0013af20": 24}
BIT_FUNCTION = "fn_0035bc40"
ARENA_SIZE = 128


def fixture(name, inputs):
    keys = {"arena", "destination", "source"} if name in COPY_SIZES else {"arena", "base", "index", "enabled"}
    if name not in {*COPY_SIZES, BIT_FUNCTION} or set(inputs) != keys:
        raise ValueError("unknown function or input keys")
    if (type(inputs["arena"]) is not str or len(inputs["arena"]) != 2 * ARENA_SIZE
            or any(c not in "0123456789abcdef" for c in inputs["arena"])):
        raise ValueError("expected 128-byte lowercase hex arena")
    if any(type(inputs[k]) is not int or not 0 <= inputs[k] <= 0xffffffff for k in keys - {"arena"}):
        raise ValueError("expected u32 arguments")
    if name in COPY_SIZES:
        n = COPY_SIZES[name]
        if any(inputs[k] + n > ARENA_SIZE for k in ("destination", "source")):
            raise ValueError("copy footprint outside arena")
        readable, writable = [(inputs["source"], n)], [(inputs["destination"], n)]
    else:
        offset = inputs["base"] + 4 * (inputs["index"] >> 5)
        if offset + 4 > ARENA_SIZE:
            raise ValueError("bit footprint outside arena")
        readable = writable = [(offset, 4)]
    return bytes.fromhex(inputs["arena"]), readable, writable


def cases(name, suite="public"):
    if suite not in ("public", "heldout") or name not in {*COPY_SIZES, BIT_FUNCTION}:
        raise ValueError("unknown function or suite")
    arguments = []
    if name in COPY_SIZES:
        n = COPY_SIZES[name]
        if suite == "public":
            arguments = [{"destination": 40 + delta, "source": 40} for delta in range(-n, n + 1)]
            arguments += [{"destination": dst, "source": src} for dst, src in [(0, 104), (104, 0), (3, 91), (91, 3)]]
        else:
            for i in range(80):
                seed = hashlib.sha256(f"memory-001-offsets:{name}:{i}".encode()).digest()
                arguments.append({"destination": seed[0] % (129 - n), "source": seed[1] % (129 - n)})
    else:
        if suite == "public":
            arguments = [{"base": base, "index": index, "enabled": enabled}
                         for base in (0, 3, 64)
                         for index in (0, 1, 7, 31, 32, 33, 63, 64, 127, 191, 255)
                         for enabled in (0, 1, 2, 255, 256, 257, 0x80000000, 0xffffffff)]
        else:
            for i in range(128):
                seed = hashlib.sha256(f"memory-001-bit:{i}".encode()).digest()
                base = seed[0] % 80
                index = int.from_bytes(seed[1:5], "little") % (((128 - base) // 4) * 32)
                arguments.append({"base": base, "index": index, "enabled": int.from_bytes(seed[5:9], "little")})
    result = []
    for i, args in enumerate(arguments):
        arena = b"".join(hashlib.sha256(f"memory-001:{suite}:{name}:{i}:{j}".encode()).digest() for j in range(4))
        # Include all-zero/all-one data as well as changing canaries and source words.
        if suite == "public" and i % 5 == 0:
            arena = bytes([0 if i % 10 == 0 else 255]) * ARENA_SIZE
        inputs = {"arena": arena.hex(), **args}
        fixture(name, inputs)
        result.append({"id": f"{suite}-{i:04d}", "inputs": inputs})
    return result

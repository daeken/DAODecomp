"""Deterministic pilot inputs. Freeze this file before model dispatch.

The implementation workers receive neither corpus. 'heldout' uses a separate
hash domain and is retained as a separate result for measuring generalization.
"""
import hashlib

BYTE_FUNCTIONS = {"fn_004d79c0", "fn_004b6e70", "fn_004b65b0", "fn_004b64d0"}
INTEGER_FUNCTIONS = {"fn_00184920", "fn_0052aad0", "fn_005851a0", "fn_005c0c00"}


def cases(name, suite="public"):
    if suite not in ("public", "heldout") or name not in BYTE_FUNCTIONS | INTEGER_FUNCTIONS:
        raise ValueError("unknown pilot function or suite")
    if suite == "public":
        if name in BYTE_FUNCTIONS:
            values = list(range(256))
        else:
            values = list(range(40))
            values += [1 << i for i in range(32)] + [0xffffffff ^ (1 << i) for i in range(32)]
            values += [0xffffffff, 0x80000001, 0x7fffffff, 0xfffffffe]
            values += [(base + offset) & 0xffffffff for base in
                       (-2000, -1900, -400, -100, -20, 20, 100, 400, 1900, 2000, 2100, 2400)
                       for offset in (-1, 0, 1)]
    else:
        values = [int.from_bytes(hashlib.sha256(f"DAODecomp-luna001-heldout:{name}:{i}".encode()).digest()[:4], "little")
                  for i in range(64)]
        if name in BYTE_FUNCTIONS:
            # Cover all low-byte values again with unrelated upper-register bits.
            values += [((i * 0x9e3779b1) & 0xffffff00) | i for i in range(256)]
        else:
            # Deliberately include multiples and neighboring values missed by uniform random draws.
            values += [v & 0xffffffff for base in (-2147483600, -800, -500, 0, 500, 800, 2147483600)
                       for v in (base - 1, base, base + 1)]
    return [{"id": f"{suite}-{v:08x}", "inputs": {"value": v}} for v in dict.fromkeys(values)]

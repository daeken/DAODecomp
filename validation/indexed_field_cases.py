"""Proposed extension of indexed-store fixtures; no recovered function semantics."""
import hashlib
import random

ARENA_SIZE = 512
MAX_OBJECT_OFFSET = 64
FIELD_SPECS = {
    "fn_00347cf0": ("get", 0x12a, 2, 7),
    "fn_00347d30": ("get", 0x138, 1, 7),
    "fn_00347d70": ("get", 0x13f, 1, 7),
    "fn_00347d90": ("set", 0x13f, 1, 7),
    "fn_00347db0": ("get", 0x148, 4, 7),
    "fn_00347dd0": ("set", 0x148, 4, 7),
    "fn_00347df0": ("get", 0x164, 4, 7),
    "fn_00347e10": ("set", 0x164, 4, 7),
    "fn_00347e70": ("get", 0x19c, 2, 6),
    "fn_00347e90": ("get", 0x1a8, 1, 6),
    "fn_00347eb0": ("set", 0x1a8, 1, 6),
}
NEGATIVE_NAMES = ("fn_00347cf0", "fn_00347d70", "fn_00347db0", "fn_00347eb0")
_VALUES = [0, 1, 0x7f, 0x80, 0xff, 0x100, 0x101, 0x7fff, 0x8000,
           0xffff, 0x10000, 0x10001, 0x80000000, 0xffffffff] + [1 << b for b in range(32)]


# Raw compact JSON + newline identities from original-only preparation.
CHARACTERIZED_CASE_HASHES = {'fn_00347cf0-heldout-cases.json': '82b8ae1ab51e99048c714c3d702dee8027d54fadf8c95cc3c02d0eaa853160e1', 'fn_00347cf0-public-cases.json': 'addbfde7805f8e941d914c6791bb57e228664ebb332c24c8567e3495448e045d', 'fn_00347d30-heldout-cases.json': '5770b487e96d18a092102d3b8c57b4af7539f8adfe2dae39895677bb15ecf421', 'fn_00347d30-public-cases.json': '90f5545f04b701beb980c0ca2b25034c960f90b03832c9c33bf4fa7c4f38f2c1', 'fn_00347d70-heldout-cases.json': '0aafbaa6d391112f7bb02d13879c912ba913e7a631623af54c6a8e8ddcec7f57', 'fn_00347d70-public-cases.json': '8eeea6598d9c13d5fc9105bbc689658e53a71cf9e6f1e248ea3ec7cec8ef9fca', 'fn_00347d90-heldout-cases.json': '99cdc39c0c2b010a96a5cbb71fe35022c1c1339acdf78f3e076844c1b735a422', 'fn_00347d90-public-cases.json': '83b29230c3b49752c6c11fb79847f510938e30a20d9c92aeee40ba671e1afc93', 'fn_00347db0-heldout-cases.json': '4e7a5e6b247eb24a9eb6dc74a30673f5023b2cdf9edc1b7261808869772aee8d', 'fn_00347db0-public-cases.json': '87cfbd86aed7e489bd59248f25818f5a92cbd1b85ae2045cea2732019c5015ad', 'fn_00347dd0-heldout-cases.json': 'f3be206980b79f5af558cc89a6fae45c33389999583cba9dff69c676ebd77935', 'fn_00347dd0-public-cases.json': 'e1ed8e92abfe8a9c3a8646f414cf5c4c11e0fd8fd1b02dd6af91de3ba6022fc9', 'fn_00347df0-heldout-cases.json': 'a6f1e6140eee698e226e7f6cababac0eda6e4d727c801e2d4a824cb6642afaea', 'fn_00347df0-public-cases.json': '72e02e0cdf582171f5f6f85d7b6d895e6368282b8372447852fb8b1fab21d2a1', 'fn_00347e10-heldout-cases.json': '638e89b5adbd5746571a766f53ca3ba7d7b2922a99f97cbe342021652881b8ac', 'fn_00347e10-public-cases.json': '9e5313b3e77d9e799eceddd7370934515da7c65d20e3c23e80058e4ca97aac4d', 'fn_00347e70-heldout-cases.json': '36bd8181669d01071f325043074412ce90a9b1e0b77179cd4a48edc7ae09d7dc', 'fn_00347e70-public-cases.json': '764bccec853320ef219aa4dd9e6c0c00b34a411ee7a6a2bd0556f3858bcfdbd1', 'fn_00347e90-heldout-cases.json': '584dbdd232f92ade698eb2ffa0aabaa20de1c072d8867b814db066cc846855f5', 'fn_00347e90-public-cases.json': '303760461892e7f9c46eb1e7986bb86f961c5df99e05539ade7e86cf66467fd5', 'fn_00347eb0-heldout-cases.json': '087dc9c77f623db47c044f21cc4d44b23d1d36eaa5fdfa9848c70322fe1c6225', 'fn_00347eb0-public-cases.json': 'b35bd4f464e4e9128febf95472244bbfdf82b508b87458e17d735e2c3000368b'}


def fixture(name, inputs):
    if name not in FIELD_SPECS:
        raise ValueError("unknown indexed field")
    kind, field, width, limit = FIELD_SPECS[name]
    expected = {"arena", "object", "index", "entry_eax"} | ({"value"} if kind == "set" else set())
    if type(inputs) is not dict or set(inputs) != expected:
        raise ValueError("wrong input keys")
    arena = inputs["arena"]
    if (type(arena) is not str or len(arena) != 1024
            or any(c not in "0123456789abcdef" for c in arena)):
        raise ValueError("expected 512-byte lowercase hex arena")
    for key in expected - {"arena", "object"}:
        if type(inputs[key]) is not int or not 0 <= inputs[key] <= 0xffffffff:
            raise ValueError("expected u32 " + key)
    obj = inputs["object"]
    if type(obj) is not int or not 0 <= obj <= MAX_OBJECT_OFFSET:
        raise ValueError("object must be integer 0..64")
    low = inputs["index"] & 255
    if low >= limit:
        return bytes.fromhex(arena), [], []
    at = obj + field + width * low
    if at + width > ARENA_SIZE:
        raise ValueError("footprint exceeds arena")
    return bytes.fromhex(arena), ([(at, width)] if kind == "get" else []), ([(at, width)] if kind == "set" else [])


def cases(name, suite="public"):
    if name not in FIELD_SPECS or suite not in ("public", "heldout"):
        raise ValueError("unknown function/suite")
    kind, off, width, limit = FIELD_SPECS[name]
    rva = int(name[3:], 16)
    args = []
    if suite == "public":
        for prefix, eax in zip((0, 0x100, 0xffff0000, 0x80000000),
                               (0, 0x12345600, 0xffff0000, 0xffffffff)):
            for low in range(256):
                args.append(dict(object=(0, 1, 3, 32, 64)[len(args) % 5], index=prefix | low,
                                 entry_eax=eax, value=_VALUES[len(args) % len(_VALUES)]))
        for low in range(limit):
            for value in sorted(set(_VALUES)):
                args.append(dict(object=3, index=0x12340000 | low, entry_eax=0xa5c3ff01,
                                 value=value, field_bits=value))
    else:
        rng = random.Random(f"memory-batch-003:{rva}:heldout")
        for i in range(128):
            index = rng.getrandbits(32)
            if i % 2 == 0:
                index = (index & 0xffffff00) | (i % limit)
            args.append(dict(object=rng.randrange(65), index=index,
                             entry_eax=rng.getrandbits(32), value=rng.getrandbits(32)))
    result = []
    for i, entry in enumerate(args):
        values = dict(entry)
        arena = bytearray(b"".join(hashlib.sha256(f"{name}:{suite}:{i}:{j}".encode()).digest()
                                  for j in range(16)))
        if "field_bits" in values:
            bits = values.pop("field_bits")
            at = values["object"] + off + width * (values["index"] & 255)
            arena[at:at + width] = (bits & ((1 << (8 * width)) - 1)).to_bytes(width, "little")
        inputs = dict(arena=arena.hex(), **values)
        if kind == "get":
            inputs.pop("value")
        fixture(name, inputs)
        result.append(dict(id=f"{suite}-{i:04d}", inputs=inputs))
    return result


def negative_cases(name):
    if name not in NEGATIVE_NAMES:
        raise ValueError("unknown negative control")
    return cases(name, "public")

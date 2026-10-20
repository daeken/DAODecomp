"""Strict source identities; compiler-generated names never alias their parent.

A generated name may describe a graph relationship but does not establish any
original address. Binding still requires the caller's explicit registry entry.
"""
import re
from .coff import Coff
from .constructor_identity import constructor_identity

_GENERATED = re.compile(r'^__(ehhandler|ehfuncinfo|unwindtable|unwindfunclet)\$(.+)$')
_C = re.compile(r'^_?(fn|g)_([0-9a-fA-F]{8})(?:@\d+)?$')
_CPP = re.compile(r'^\?(fn|g)_([0-9a-fA-F]{8})@\S+$')


def generated_identity(name):
    if not isinstance(name, str):
        return None
    found = _GENERATED.fullmatch(name)
    if not found:
        return None
    kind, parent = found.groups()
    ordinal = None
    if kind == 'unwindfunclet':
        parent, sep, suffix = parent.rpartition('$')
        if not sep or not suffix.isdigit() or not parent:
            return {'kind': kind, 'parent_symbol': None, 'ordinal': None, 'supported_name': False}
        ordinal = int(suffix)
    return {'kind': kind, 'parent_symbol': parent, 'ordinal': ordinal, 'supported_name': True}


def source_identity(name):
    """Only a source identifier at the start of its decoration has an RVA."""
    if not isinstance(name, str) or generated_identity(name) is not None:
        return None
    found = _C.fullmatch(name) or _CPP.fullmatch(name)
    if not found:
        return constructor_identity(name)
    return found[1], int(found[2], 16)


def bind_symbols(object_bytes, requested, registry):
    """Pure counterpart of historical binding; mutate requested only uniquely.

    No generated node, import pointer or nested embedded identifier gains an
    address. This deliberately tightens accidental substring recognition.
    """
    obj = Coff(object_bytes)
    addresses, defined = {}, {}
    for symbol in obj.symbols.values():
        identity = source_identity(symbol.name)
        if identity is None:
            continue
        kind, rva = identity
        record = registry.get('%s_%08x' % (kind, rva))
        if record is None:
            continue
        addresses[symbol.name] = record['original_va'] if type(record) is dict else record
        if kind == 'fn' and rva in requested and symbol.section > 0:
            defined.setdefault(rva, []).append(symbol.name)
    for rva, names in defined.items():
        if len(names) == 1:
            requested[rva]['symbol'] = names[0]
    return addresses

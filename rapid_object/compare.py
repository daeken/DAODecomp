"""Conservative, relocation-aware exact COFF comparison; no execution or proof.

No relocation fields are wildcarded. Different instruction sequences are retained
as nonmatches. Range/signature hypotheses are not verified by this comparison.
"""
import hashlib
import json
from pathlib import Path
import re
import struct
from .coff import Coff, CoffError, unpack


def sha(data):
    return hashlib.sha256(data).hexdigest()


class PE:
    def __init__(self, data):
        self.data = data
        if data[:2] != b'MZ':
            raise CoffError('requires_PE_original')
        peoff, = unpack('<I', data, 0x3c)
        if data[peoff:peoff + 4] != b'PE\0\0':
            raise CoffError('bad_PE_signature')
        machine, count, _, _, _, opt, _ = unpack('<HHIIIHH', data, peoff + 4)
        magic, = unpack('<H', data, peoff + 24)
        if machine != 0x14c or magic != 0x10b or opt < 96:
            raise CoffError('requires_PE32_i386')
        self.image_base, = unpack('<I', data, peoff + 24 + 28)
        self.sections = []
        for i in range(count):
            _, vs, va, size, ptr, _, _, _, _, flags = unpack('<8sIIIIIIHHI', data, peoff + 24 + opt + 40 * i)
            if ptr + size > len(data):
                raise CoffError('PE_section_out_of_bounds')
            self.sections.append((va, min(vs, size), ptr, flags))

    def read(self, rva, size):
        found = [(va, ptr) for va, length, ptr, flags in self.sections if flags & 0x20000000 and va <= rva and rva + size <= va + length]
        if len(found) != 1 or size <= 0:
            raise CoffError('original_range_not_unique_backed_executable')
        va, ptr = found[0]
        return self.data[ptr + rva - va:ptr + rva - va + size]


def normalize_requested(requested, image_base):
    out = {}
    for key, item in requested.items():
        rva = int(key, 0) if isinstance(key, str) else key
        if type(rva) is not int or not 0 <= rva <= 0xffffffff:
            raise CoffError('invalid_requested_RVA')
        if rva in out:
            raise CoffError('duplicate_requested_RVA')
        va = item.get('original_va', image_base + rva)
        if va != image_base + rva or va > 0xffffffff:
            raise CoffError('original_VA_identity_conflict')
        ranges = item.get('ranges', item.get('body_ranges'))
        if ranges is None and 'start_rva' in item:
            ranges = [{'start_rva': item['start_rva'], 'end_rva_inclusive': item['end_rva_inclusive']}]
        out[rva] = dict(item, original_va=va, ranges=ranges)
    if not out:
        raise CoffError('empty_requested_functions')
    return out


def compare_bytes(original, object_bytes, requested, symbols=None, source_sha256=None, compiler=None, module_sha256=None):
    """Inputs are bytes; symbols maps exact COFF names to explicit original VAs.

    requested keys are RVAs; values contain full inventory `ranges` (inclusive
    start/end RVAs), optional symbol, original_va and original bytes_sha256.
    Stable fn_RVA / _fn_RVA[@N] names map only to requested entries. Other decorated
    symbols need an explicit symbol entry or per-function `symbol` field.
    """
    report = {'schema_version': 1, 'backend': 'i386_coff_exact_v1', 'proof': False,
              'native_windows_execution': False, 'reccmp_used': False,
              'module_sha256': sha(original), 'object_sha256': sha(object_bytes),
              'source_sha256': source_sha256, 'compiler': compiler, 'functions': []}
    report['implementation_sha256'] = {p.name: sha(p.read_bytes()) for p in (Path(__file__), Path(__file__).with_name('coff.py'))}
    try:
        if module_sha256 is not None and module_sha256 != sha(original):
            raise CoffError('module_sha256_mismatch')
        pe = PE(original)
        obj = Coff(object_bytes)
        requested = normalize_requested(requested, pe.image_base)
        addresses = dict(symbols or {})
        if any(type(v) is not int or not 0 <= v <= 0xffffffff for v in addresses.values()):
            raise CoffError('invalid_symbol_address')
        # Exact explicit names and stable names establish identities independently
        # of candidate bytes or any desired matching relocation value.
        assigned = {}
        for symbol in obj.symbols.values():
            match = re.fullmatch(r'_?fn_([0-9a-fA-F]{8})(?:@\d+)?', symbol.name)
            rva = int(match.group(1), 16) if match else None
            explicit = [r for r, spec in requested.items() if spec.get('symbol') == symbol.name]
            if len(explicit) > 1:
                raise CoffError('ambiguous_requested_symbol')
            if explicit:
                if rva is not None and rva != explicit[0]:
                    raise CoffError('symbol_identity_conflict')
                rva = explicit[0]
            if rva in requested:
                va = requested[rva]['original_va']
                if symbol.name in addresses and addresses[symbol.name] != va:
                    raise CoffError('symbol_identity_conflict')
                addresses[symbol.name] = va
                if symbol.section > 0:
                    assigned.setdefault(rva, []).append(symbol)
        report['symbol_addresses'] = addresses
        report['requested'] = {str(r): s for r, s in requested.items()}
        section_bases = {}
        conflicting_sections = set()
        spans = {}
        errors = {}
        for rva, spec in requested.items():
            try:
                matches = assigned.get(rva, [])
                if len(matches) != 1:
                    raise CoffError('missing_or_ambiguous_function_symbol')
                sym = matches[0]
                sec, start, size, evidence = obj.function_span(sym)
                base = spec['original_va'] - start
                if sec.number in section_bases and section_bases[sec.number] != base:
                    conflicting_sections.add(sec.number)
                    raise CoffError('conflicting_section_placement')
                section_bases[sec.number] = base
                spans[rva] = (sym, sec, start, size, evidence)
            except CoffError as exc:
                errors[rva] = str(exc)
        # A shared section placement conflict invalidates every function in it.
        for rva, (sym, sec, start, size, evidence) in spans.items():
            if sec.number in conflicting_sections or section_bases[sec.number] != requested[rva]['original_va'] - start:
                errors[rva] = 'conflicting_section_placement'
        for rva, spec in requested.items():
            entry = {'rva': rva, 'original_va': spec['original_va'], 'status': 'inconclusive', 'diagnostics': []}
            report['functions'].append(entry)
            try:
                if rva in errors:
                    raise CoffError(errors[rva])
                ranges = spec['ranges']
                if not isinstance(ranges, list) or len(ranges) != 1:
                    raise CoffError('unsupported_noncontiguous_or_missing_original_ranges')
                rr = ranges[0]
                lo, hi = rr['start_rva'], rr['end_rva_inclusive']
                if lo != rva or type(hi) is not int or hi < lo:
                    raise CoffError('original_range_entry_or_bounds')
                reference = pe.read(lo, hi - lo + 1)
                if spec.get('bytes_sha256') is not None and sha(reference) != spec['bytes_sha256']:
                    raise CoffError('original_range_sha256_mismatch')
                sym, sec, start, size, evidence = spans[rva]
                entry.update(symbol=sym.name, section=sec.number, object_offset=start,
                             object_size=size, original_size=len(reference), boundary_evidence=evidence,
                             original_bytes_sha256=sha(reference), original_bytes_hex=reference.hex(),
                             object_bytes_hex=sec.data[start:start + size].hex(), relocations=[])
                patched = bytearray(sec.data[start:start + size])
                for rel in sec.relocations:
                    if rel.kind not in (6, 0x14):
                        raise CoffError(f'unsupported_relocation_kind:{rel.kind}')
                    width = 4
                    if rel.offset >= start + size or rel.offset + width <= start:
                        continue
                    if rel.offset < start or rel.offset + width > start + size:
                        raise CoffError('relocation_crosses_function_boundary')
                    if rel.kind not in (6, 0x14):
                        raise CoffError(f'unsupported_relocation_kind:{rel.kind}')
                    target = obj.symbols[rel.symbol]
                    if target.section == -1:
                        raise CoffError('unsupported_absolute_symbol:' + target.name)
                    if target.storage == 105 or target.section == -2 or (target.section == 0 and target.value):
                        raise CoffError('weak_debug_or_common_symbol:' + target.name)
                    placed = None
                    if target.section > 0 and not any(tsec.number == target.section and tstart <= target.value < tstart + tsize
                                                      for _, tsec, tstart, tsize, _ in spans.values()):
                        raise CoffError('unexamined_defined_target:' + target.name)
                    if target.section in section_bases:
                        placed = section_bases[target.section] + target.value
                    if target.name in addresses:
                        address = addresses[target.name]
                        if placed is not None and placed != address:
                            raise CoffError('target_placement_identity_conflict:' + target.name)
                    elif placed is not None:
                        address = placed
                    else:
                        raise CoffError('unresolved_symbol:' + target.name)
                    offset = rel.offset - start
                    addend, = unpack('<I', patched, offset)
                    value = address + addend
                    if target.section > 0:
                        effective = (target.value + addend) & 0xffffffff
                        if not any(tsec.number == target.section and tstart <= effective < tstart + tsize
                                   for _, tsec, tstart, tsize, _ in spans.values()):
                            raise CoffError('unexamined_effective_defined_target:' + target.name)
                    if rel.kind == 0x14:
                        value -= spec['original_va'] + offset + 4
                    struct.pack_into('<I', patched, offset, value & 0xffffffff)
                    entry['relocations'].append({'offset': offset, 'kind': rel.kind, 'symbol': target.name,
                                                 'target_va': address, 'addend_u32': addend, 'patched_u32': value & 0xffffffff})
                candidate = bytes(patched)
                entry['relocated_bytes_sha256'] = sha(candidate)
                entry['relocated_bytes_hex'] = candidate.hex()
                if candidate == reference:
                    entry['status'] = 'exact_object_match'
                else:
                    entry['status'] = 'nonmatch'
                    entry['diagnostics'].append('full_function_bytes_differ')
                    entry['first_differences'] = [{'offset': i, 'original': a, 'candidate': b} for i, (a, b) in enumerate(zip(reference, candidate)) if a != b][:32]
                    if len(candidate) != len(reference):
                        entry['diagnostics'].append('full_function_length_differs_no_prefix_acceptance')
            except (CoffError, KeyError, TypeError, ValueError) as exc:
                entry['diagnostics'].append(str(exc))
        report['counts'] = {label: sum(f['status'] == label for f in report['functions']) for label in ('exact_object_match', 'nonmatch', 'inconclusive')}
    except (CoffError, UnicodeError, ValueError, TypeError, struct.error) as exc:
        report.update(error=str(exc), counts={'exact_object_match': 0, 'nonmatch': 0, 'inconclusive': len(requested)})
    return report


def compare_object(original_path, object_path, requested, symbols=None, source_sha256=None, compiler=None, module_sha256=None):
    report = compare_bytes(Path(original_path).read_bytes(), Path(object_path).read_bytes(), requested, symbols,
                           source_sha256, compiler, module_sha256)
    report.update(original_path=str(Path(original_path).resolve()), object_path=str(Path(object_path).resolve()))
    return report


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('original'); p.add_argument('object'); p.add_argument('identities', help='JSON with requested, symbols and optional module_sha256')
    args = p.parse_args()
    print(json.dumps(compare_object(args.original, args.object, **json.loads(Path(args.identities).read_text())), indent=2, sort_keys=True))

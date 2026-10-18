"""Strict, small i386 COFF reader. Not a linker; unknown semantics fail closed.

Layout: https://learn.microsoft.com/en-us/windows/win32/debug/pe-format
"""
from dataclasses import dataclass
import struct


class CoffError(ValueError):
    pass


def unpack(fmt, data, offset):
    size = struct.calcsize(fmt)
    if offset < 0 or offset + size > len(data):
        raise CoffError('truncated_structure')
    return struct.unpack_from(fmt, data, offset)


@dataclass(frozen=True)
class Symbol:
    index: int
    name: str
    value: int
    section: int
    type: int
    storage: int
    aux: tuple


@dataclass(frozen=True)
class Relocation:
    offset: int
    symbol: int
    kind: int


@dataclass(frozen=True)
class Section:
    number: int
    name: str
    data: bytes
    characteristics: int
    relocations: tuple


class Coff:
    def __init__(self, data):
        self.data = bytes(data)
        machine, count, _, symoff, nsyms, opt, _ = unpack('<HHIIIHH', data, 0)
        if machine != 0x14c or opt or not count:
            raise CoffError('requires_standard_i386_coff')
        if 20 + count * 40 > len(data):
            raise CoffError('truncated_sections')
        if not symoff or symoff < 20 + count * 40:
            raise CoffError('missing_or_overlapping_symbol_table')
        end = symoff + nsyms * 18
        strlen, = unpack('<I', data, end)
        if strlen < 4 or end + strlen > len(data):
            raise CoffError('malformed_string_table')
        strings = data[end:end + strlen]

        def string_at(offset):
            if offset < 4 or offset >= len(strings):
                raise CoffError('bad_string_offset')
            stop = strings.find(b'\0', offset)
            if stop < 0:
                raise CoffError('unterminated_string')
            return strings[offset:stop].decode('ascii', errors='strict')

        def name(raw, section=False):
            if section and raw.startswith(b'/'):
                try:
                    return string_at(int(raw[1:].rstrip(b'\0')))
                except ValueError as exc:
                    raise CoffError('bad_section_name') from exc
            if raw[:4] == b'\0' * 4:
                return string_at(struct.unpack('<I', raw[4:])[0])
            return raw.rstrip(b'\0').decode('ascii', errors='strict')

        self.symbols = {}
        i = 0
        while i < nsyms:
            raw, value, sec, typ, storage, naux = unpack('<8sIhHBB', data, symoff + i * 18)
            if i + naux >= nsyms:
                raise CoffError('auxiliary_table_overrun')
            if sec > count or sec < -2:
                raise CoffError('invalid_symbol_section')
            aux = tuple(data[symoff + j * 18:symoff + (j + 1) * 18] for j in range(i + 1, i + 1 + naux))
            self.symbols[i] = Symbol(i, name(raw), value, sec, typ, storage, aux)
            i += 1 + naux
        self.sections = []
        # Object regions must never alias header/symbol/string/other sections.
        occupied = [(0, 20 + count * 40), (symoff, end + strlen)]

        def region(offset, size, label):
            if not size:
                return b''
            if offset <= 0 or offset + size > len(data):
                raise CoffError('out_of_bounds_' + label)
            if any(offset < hi and lo < offset + size for lo, hi in occupied):
                raise CoffError('overlapping_' + label)
            occupied.append((offset, offset + size))
            return data[offset:offset + size]

        for i in range(count):
            raw, _, va, size, ptr, rp, lp, nr, nl, flags = unpack('<8sIIIIIIHHI', data, 20 + 40 * i)
            if va or flags & 0x01000000:
                raise CoffError('unsupported_section_address_or_relocation_overflow')
            if ptr == 0 and flags & 0x80 and size > 64 * 1024 * 1024:
                raise CoffError('uninitialized_section_size_budget')
            body = bytes(size) if ptr == 0 and flags & 0x80 else region(ptr, size, 'section')
            relraw = region(rp, nr * 10, 'relocations')
            region(lp, nl * 6, 'line_numbers')
            rels = []
            occupied_fields = set()
            for j in range(nr):
                off, sym, kind = unpack('<IIH', relraw, j * 10)
                if sym not in self.symbols:
                    raise CoffError('relocation_symbol_missing_or_auxiliary')
                # Width is known only for these two supported relocation kinds.
                width = 4 if kind in (6, 0x14) else 1
                if off + width > len(body):
                    raise CoffError('relocation_out_of_bounds')
                fields = set(range(off, off + width))
                if fields & occupied_fields:
                    raise CoffError('overlapping_relocations')
                occupied_fields |= fields
                rels.append(Relocation(off, sym, kind))
            self.sections.append(Section(i + 1, name(raw, True), body, flags, tuple(rels)))
        for sym in self.symbols.values():
            if sym.section > 0 and sym.value > len(self.sections[sym.section - 1].data):
                # Uninitialized data has a declared size and is represented separately
                # by a COFF section with null PointerToRawData; unsupported here.
                raise CoffError('symbol_out_of_bounds')

    def function_span(self, symbol):
        if symbol.section <= 0 or symbol.type & 0x30 != 0x20 or symbol.storage != 2:
            raise CoffError('not_defined_external_function')
        section = self.sections[symbol.section - 1]
        if not section.characteristics & 0x20000000:
            raise CoffError('function_not_executable')
        others = [s for s in self.symbols.values() if s.section == symbol.section and s.type & 0x30 == 0x20 and s.index != symbol.index]
        if symbol.aux:
            if len(symbol.aux) != 1:
                raise CoffError('ambiguous_function_auxiliary')
            size, = unpack('<I', symbol.aux[0], 4)
            evidence = 'function_definition_auxiliary'
        elif section.characteristics & 0x1000 and symbol.value == 0 and not others:
            definitions = [s for s in self.symbols.values() if s.section == symbol.section and s.storage == 3 and s.type == 0 and s.value == 0 and s.name == section.name and len(s.aux) == 1]
            if len(definitions) != 1:
                raise CoffError('missing_unique_comdat_section_definition')
            size, nr, _ = unpack('<IHH', definitions[0].aux[0], 0)
            selection = definitions[0].aux[0][14]
            if size != len(section.data) or nr != len(section.relocations) or selection not in (1, 2, 3, 4, 6, 7):
                raise CoffError('inconsistent_or_associative_comdat')
            evidence = 'entire_single_function_comdat'
        else:
            raise CoffError('unknown_function_boundary')
        if not size or symbol.value + size > len(section.data):
            raise CoffError('function_size_out_of_bounds')
        if any(symbol.value < s.value + 1 and s.value < symbol.value + size for s in others):
            raise CoffError('overlapping_function_symbols')
        return section, symbol.value, size, evidence

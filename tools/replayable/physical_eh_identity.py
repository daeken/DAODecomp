"""Strict fixed-image substitution identity, independent of node-byte pairing.

The result describes a pinned object at a derived original placement, with the
entire surrounding original image and architectural context unchanged. It is not
an actual link/deployment result, a C++ theorem, or a model of opaque execution.
Every runtime section must be placed once and match completely. Unsupported
object/linker features, extra bytes, and unknown placements fail closed.
"""
import re
import struct
from rapid_object.coff import Coff
from rapid_object.eh_graph import Original, sha
from tools.replayable.ebp_eh_candidate import inspect
from tools.replayable.range_eh import metadata, reachable, need

VERSION = 'fixed-original-image-physical-EH-identity-v1'


def check(original, owned_ranges, object_bytes, main_name, external_bindings):
    result = dict(schema=VERSION, status='unsupported', acceptance_supported=False,
                  original_sha256=sha(original), object_sha256=sha(object_bytes),
                  placements=[], anchors=[], sections=[], blockers=[], proof=False,
                  linked_placement_proven=False,
                  context='identical original preferred-address image and complete architectural state; unchanged surrounding bytes and environment')
    try:
        reader = Original(original)
        obj = Coff(object_bytes)
        # COMMON allocations and weak/special definitions may have no section.
        # A section-only walk therefore cannot establish complete object storage.
        need(struct.unpack_from('<H', object_bytes, 18)[0] == 0, 'physical_COFF_file_flags')
        section_definitions = {}
        for sym in obj.symbols.values():
            if sym.section == 0:
                need(sym.value == 0 and sym.storage == 2 and sym.type in (0, 32) and not sym.aux,
                     'physical_unplaced_or_special_external_definition')
            elif sym.section < 0:
                need(sym.section == -1 and sym.name in ('@comp.id', '@feat.00')
                     and sym.storage == 3 and sym.type == 0 and not sym.aux
                     and (sym.name != '@feat.00' or sym.value == 1)
                     and sum(x.name == sym.name for x in obj.symbols.values()) == 1,
                     'physical_unsupported_absolute_or_debug_definition')
            else:
                sec = obj.sections[sym.section-1]
                definition = (sym.name == sec.name and sym.value == 0 and sym.type == 0
                              and sym.storage == 3 and len(sym.aux) == 1)
                if definition:
                    need(sym.section not in section_definitions, 'physical_duplicate_section_definition')
                    length, nr, nl, checksum, association, selection, reserved, high = struct.unpack('<IHHIhBBH', sym.aux[0])
                    need(length == len(sec.data) and nr == len(sec.relocations) and nl == reserved == high == 0,
                         'physical_section_definition_extent_or_aux')
                    need(struct.unpack_from('<H', object_bytes, 20+40*(sec.number-1)+34)[0] == 0,
                         'physical_line_number_metadata_unsupported')
                    section_definitions[sym.section] = (association, selection)
                else:
                    need(not sym.aux and sym.storage in (2, 3, 6) and sym.type in (0, 32)
                         and sym.value < len(sec.data), 'physical_unsupported_defined_symbol')
        need(set(section_definitions) == {s.number for s in obj.sections}, 'physical_missing_section_definition')
        candidate = inspect(object_bytes, main_name)
        need(owned_ranges and len(owned_ranges) <= 64, 'physical_owned_ranges')
        previous = 0
        for lo, hi in owned_ranges:
            need(type(lo) is int and type(hi) is int and previous <= lo < hi <= 0x100000000,
                 'physical_owned_range_order')
            reader.read(lo, hi-lo, True)
            previous = hi
        need(sum(hi-lo for lo, hi in owned_ranges) <= 65536, 'physical_owned_budget')
        start = owned_ranges[0][0]
        graph = metadata(reader, reader.read(start, 16, True))
        mains = [s for s in obj.symbols.values() if s.name == main_name and s.section > 0]
        need(len(mains) == 1, 'physical_main_identity')
        main = mains[0]
        bases = {}

        def anchor(role, section, offset, address):
            base = address-offset
            result['anchors'].append(dict(role=role, section=section, offset=offset,
                                          address=address, derived_base=base))
            need(section not in bases or bases[section] == base,
                 'physical_inconsistent_section_placement:'+str(section))
            bases[section] = base

        anchor('main', main.section, main.value, start)
        for role in ('handler', 'FuncInfo', 'unwind_map', 'try_map'):
            a, b = graph[role], candidate[role]
            anchor(role, b['section'], b['offset'], a['va'])
            need(a['size'] == b['size'], 'physical_metadata_extent:'+role)
        atries, btries = graph['try_map']['entries'], candidate['try_map']['entries']
        need(len(atries) == len(btries), 'physical_try_count')
        for i, (a, b) in enumerate(zip(atries, btries)):
            x, y = a['handlers'], b['handlers']
            anchor('handler_table_'+str(i), y['section'], y['offset'], x['va'])
            need(x['size'] == y['size'] and len(x['entries']) == len(y['entries']),
                 'physical_handler_count')
            for j, (ae, be) in enumerate(zip(x['entries'], y['entries'])):
                anchor('catch_%s_%s' % (i, j), main.section, be['offset'], ae['entry_va'])
        # Main inventory and every dependency instruction are checked at their
        # actual offsets; never zip instructions into an invented placement.
        original_main = reachable(reader, start, [])
        original_owned = {a for lo, hi in owned_ranges for a in range(lo, hi)}
        main_bytes = {a for x in original_main['instructions'] for a in range(x['pc'], x['pc']+x['length'])}
        need(main_bytes == original_owned, 'physical_original_inventory_CFG')
        mapped_main = {bases[main.section]+a for x in candidate['main']['instructions'] for a in range(x['pc'], x['pc']+x['length'])}
        need(mapped_main == main_bytes, 'physical_main_offsets_or_extent')
        dependencies = []
        continuations = set()
        for t in atries:
            for h in t['handlers']['entries']:
                d = reachable(reader, h['entry_va'], owned_ranges)
                dependencies.append(d)
                continuations.update(d['continuation_candidates'])
        for entry in sorted(continuations):
            if not any(lo <= entry < hi for lo, hi in owned_ranges):
                dependencies.append(reachable(reader, entry, owned_ranges))
        need(len(dependencies) == len(candidate['dependencies']), 'physical_dependency_count')
        original_code = set(main_bytes)
        for a, b in zip(dependencies, candidate['dependencies']):
            aa = {(x['pc'], x['length']) for x in a['instructions']}
            bb = {(bases[main.section]+x['pc'], x['length']) for x in b['instructions']}
            need(aa == bb, 'physical_dependency_offsets_or_extent')
            span = {at for pc, length in aa for at in range(pc, pc+length)}
            need(not span & original_code, 'physical_dependency_overlap')
            original_code.update(span)
        code_section = obj.sections[main.section-1]
        need(original_code == set(range(start, start+len(code_section.data))), 'physical_code_gaps_or_suffix')
        # No assumed padding or discarded runtime section. Linker-only/debug
        # records have narrowly checked roles and never supply placement evidence.
        safe_indices = []
        for sec in obj.sections:
            if sec.number in bases:
                continue
            if sec.name == '.sxdata':
                need(sec.characteristics == 0x300200 and not sec.relocations and len(sec.data) % 4 == 0,
                     'physical_sxdata_shape')
                safe_indices.extend(struct.unpack('<'+'I'*(len(sec.data)//4), sec.data))
            elif sec.name in ('.debug$S', '.debug$T'):
                need(sec.characteristics in (0x42100040, 0x42101040), 'physical_debug_section_flags')
            elif sec.name == '.drectve':
                need(sec.characteristics == 0x100a00 and not sec.relocations,
                     'physical_directive_section')
                need(re.fullmatch(rb'\s*(?:/DEFAULTLIB:"(?:LIBCMT|OLDNAMES)"\s*)*', sec.data) is not None,
                     'physical_unknown_link_directive')
            else:
                need(not sec.data and not sec.relocations and sec.name in ('.text', '.data', '.bss'),
                     'physical_extra_runtime_section:'+sec.name)
        # Only the selected root COMDAT and its associated runtime sections can
        # participate. Other definitions must be nonallocating section records.
        for sec in obj.sections:
            association, selection = section_definitions[sec.number]
            if sec.number == main.section:
                need((association, selection) == (0, 1), 'physical_main_COMDAT_selection')
            elif sec.characteristics & 0x1000:
                need((association, selection) == (main.section, 5), 'physical_COMDAT_association')
            else:
                need((association, selection) == (0, 0), 'physical_unexpected_section_selection')
        for sym in obj.symbols.values():
            if sym.section > 0 and sym.section not in bases:
                sec = obj.sections[sym.section-1]
                need(sym.name == sec.name and sym.value == 0 and sym.type == 0
                     and sym.storage == 3 and len(sym.aux) == 1, 'physical_unplaced_symbol_definition')
        handlers = [x.index for x in obj.symbols.values()
                    if x.name == candidate['handler']['symbol'] and x.section == candidate['handler']['section']
                    and x.value == candidate['handler']['offset']]
        need(len(handlers) == 1 and safe_indices == handlers, 'physical_missing_or_extra_SAFESEH')
        opt = struct.unpack_from('<I', original, 0x3c)[0]+24
        lr, ls = struct.unpack_from('<II', original, opt+96+10*8)
        need(lr and ls >= 64, 'physical_loadconfig_missing')
        load = reader.read(reader.pe.image_base+lr, 72)
        need(struct.unpack_from('<I', load)[0] >= 72, 'physical_loadconfig_size')
        cookie, table, count = struct.unpack_from('<III', load, 60)
        need(0 < count <= 65536 and cookie == external_bindings.get('___security_cookie'), 'physical_cookie_or_SAFESEH')
        table_bytes = reader.read(table, count*4)
        safe = struct.unpack('<'+'I'*count, table_bytes)
        need(list(safe) == sorted(set(safe)) and graph['handler']['va']-reader.pe.image_base in safe,
             'physical_original_SAFESEH_identity')
        result['SAFESEH'] = dict(table_sha256=sha(table_bytes), handler=graph['handler']['va'], cookie=cookie)
        spans = []
        for number, base in sorted(bases.items()):
            sec = obj.sections[number-1]
            size = len(sec.data)
            need(sec.characteristics & ~0x00f00000 in (0x60001020, 0x40001040),
                 'physical_runtime_section_flags')
            align = (sec.characteristics >> 20) & 15
            need(1 <= align <= 14 and base % (1 << (align-1)) == 0, 'physical_section_alignment')
            need(0 <= base < base+size <= 0x100000000, 'physical_section_address')
            need(not any(base < hi and lo < base+size for lo, hi in spans), 'physical_section_overlap')
            spans.append((base, base+size))
            permissions = sec.characteristics & 0xe0000000
            original_sections = [x for x in reader.pe.sections if x[0] <= base-reader.pe.image_base and base-reader.pe.image_base+size <= x[0]+x[1]]
            need(len(original_sections) == 1 and original_sections[0][3] & 0xe0000000 == permissions,
                 'physical_section_permissions')
            expected = reader.read(base, size, bool(permissions & 0x20000000))
            patched = bytearray(sec.data)
            references = []
            for rel in sec.relocations:
                need(rel.kind in (6, 0x14) and rel.offset+4 <= size, 'physical_relocation_kind_or_extent')
                need(struct.unpack_from('<I', sec.data, rel.offset)[0] == 0, 'physical_nonzero_relocation_addend')
                sym = obj.symbols[rel.symbol]
                if sym.section > 0:
                    need(sym.section in bases and 0 <= sym.value < len(obj.sections[sym.section-1].data), 'physical_unplaced_symbol')
                    target = bases[sym.section]+sym.value
                else:
                    need(sym.section == 0 and sym.value == 0 and sym.storage == 2 and sym.name in external_bindings,
                         'physical_unresolved_external:'+sym.name)
                    need(sum(x.name == sym.name for x in obj.symbols.values()) == 1, 'physical_ambiguous_symbol')
                    target = external_bindings[sym.name]
                need(type(target) is int and 0 <= target <= 0xffffffff, 'physical_binding_address')
                value = target if rel.kind == 6 else (target-(base+rel.offset+4)) & 0xffffffff
                struct.pack_into('<I', patched, rel.offset, value)
                references.append(dict(offset=rel.offset, kind=rel.kind, symbol=sym.name, target=target))
            row = dict(section=number, base=base, size=size, original_sha256=sha(expected),
                       relocated_sha256=sha(patched), equal=bytes(patched) == expected,
                       references=references)
            result['sections'].append(row)
            need(row['equal'], 'physical_section_bytes_differ:'+str(number))
            result['placements'].append(dict(section=number, base=base, size=size))
        result.update(status='identical_at_derived_original_placement', acceptance_supported=True,
                      bytes_compared=sum(x['size'] for x in result['sections']),
                      surrounding_image_unchanged=True,
                      numeric_call_continuation_and_trap_context='identical only in the complete fixed original image/context')
    except (ValueError, KeyError, TypeError, struct.error, UnicodeError) as exc:
        result['blockers'].append(str(exc))
    return result

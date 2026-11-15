"""Read-only, relocation-backed code-pointer discovery for native PE32 data.

Numeric words in resources are not evidence of pointer origins. Proposals remain
unaccepted translation hypotheses; this module never edits projects or contracts.
"""
import bisect
import hashlib
import struct
from tools.recomp_native import PE32


def _rtti_origin(pe, head, sites, ordinary):
    """Recognize linked MSVC32 RTTI, including one/two-entry virtual tables.

    Layout reference: Wine dlls/msvcrt/cxx.h (32-bit rtti_object_locator,
    rtti_object_hierarchy and rtti_base_descriptor). Every pointer in the
    recognition chain must have its own original HIGHLOW relocation.
    """
    def read(rva, size):
        if not any(s['rva'] <= rva and rva + size <= s['rva'] +
                   min(s['virtual_size'], s['file_size']) for s in ordinary):
            raise ValueError('RTTI leaves file-backed ordinary data')
        return pe.read(rva, size)

    def pointer(rva):
        if rva not in sites:
            raise ValueError('RTTI pointer has no relocation evidence')
        return struct.unpack('<I', read(rva, 4))[0] - pe.info['image_base']

    try:
        locator = pointer(head - 4)
        signature, offset, construction, _, _ = struct.unpack('<IiIII', read(locator, 20))
        if signature != 0:
            return None
        descriptor, hierarchy = pointer(locator + 12), pointer(locator + 16)
        hs, attributes, count, _ = struct.unpack('<IIII', read(hierarchy, 16))
        if hs != 0 or not 1 <= count <= 4096:  # Explicit static-discovery budget.
            return None
        bases = pointer(hierarchy + 12)
        read(bases, count * 4)
        for index in range(count):
            base = pointer(bases + index * 4)
            read(base, 24)
            base_type = pointer(base)
            if index == 0 and base_type != descriptor:
                return None  # The first hierarchy entry describes this class.
        name = bytearray()
        for index in range(1024):
            byte = read(descriptor + 8 + index, 1)[0]
            if byte == 0:
                break
            if not 32 <= byte < 127:
                return None
            name.append(byte)
        else:
            return None  # Name-discovery budget exhausted; no implied acceptance.
        if not name.startswith((b'.?AV', b'.?AU')):
            return None
        return dict(vtable_rva=head, locator_rva=locator, type_descriptor_rva=descriptor,
                    mangled_type_name=name.decode('ascii'), subobject_offset=offset,
                    construction_displacement=construction, hierarchy_attributes=attributes,
                    base_classes=count)
    except (ValueError, struct.error):
        return None


def highlow_sites(pe):
    """Authenticate PE32 pointer sources without assuming a section's purpose."""
    rva, size = pe.directory(5)
    relocations = pe.read(rva, size) if size else b''
    cursor = 0
    sites = set()
    while cursor < len(relocations):
        if len(relocations) - cursor < 8:
            raise ValueError('truncated relocation block')
        page, length = struct.unpack_from('<II', relocations, cursor)
        if page & 4095 or length < 8 or length % 2 or length > len(relocations) - cursor:
            raise ValueError('invalid relocation block')
        for offset in range(cursor + 8, cursor + length, 2):
            word = struct.unpack_from('<H', relocations, offset)[0]
            kind, delta = word >> 12, word & 4095
            if kind == 0:
                continue
            if kind != 3:
                # HIGHADJ consumes an additional word, which must not silently
                # become another purported relocation/pointer source.
                raise ValueError('unsupported PE32 relocation type')
            site = page + delta
            if site in sites:
                raise ValueError('duplicate relocation source')
            sites.add(site)
        cursor += length
    return sites


def pointer_runs(binary, minimum=3):
    if type(minimum) is not int or minimum < 1:
        raise ValueError('invalid pointer-run length')
    pe = PE32(binary)
    sections = []
    for index, section in enumerate(pe.sections):
        flags = struct.unpack_from('<I', pe.data, pe.section_table + index * 40 + 36)[0]
        sections.append(dict(section, flags=flags))
    code = [(s['rva'], s['rva'] + min(s['virtual_size'], s['file_size']))
            for s in sections if s['flags'] & 0x20000000]
    ordinary = [s for s in sections if s['name'] in ('.rdata', '.data') and
                s['flags'] & 0x40000000 and not s['flags'] & 0x20000000]
    sites = highlow_sites(pe)
    pointers = {}
    for site in sorted(sites):
        if not any(s['rva'] <= site and site + 4 <= s['rva'] +
                   min(s['virtual_size'], s['file_size']) for s in ordinary):
            continue
        target = struct.unpack('<I', pe.read(site, 4))[0] - pe.info['image_base']
        if any(low <= target < high for low, high in code):
            pointers[site] = target
    all_runs, run = [], []
    for site, target in sorted(pointers.items()):
        if run and site != run[-1][0] + 4:
            all_runs.append(run)
            run = []
        run.append((site, target))
    if run:
        all_runs.append(run)
    runs, rtti = [], []
    for run in all_runs:
        origin = _rtti_origin(pe, run[0][0], sites, ordinary)
        if len(run) >= minimum or origin:
            runs.append(run)
            if origin:
                rtti.append(dict(origin, entries=len(run)))
    targets = {}
    for run in runs:
        for site, target in run:
            targets.setdefault(target, []).append(site)
    return pe, targets, dict(relocated_data_code_pointers=len(pointers), pointer_runs=len(runs),
                            rtti_short_tables=sum(row['entries'] < minimum for row in rtti),
                            rtti_tables=rtti)


def unowned_targets(targets, catalog):
    entries, spans = set(), []
    for row in catalog:
        entries.add(row['rva'])
        spans.append((row['rva'], row['rva']))  # A refused selection is still an entry barrier.
        spans.extend((span['rva'], span['rva'] + span['size'])
                     for span in row.get('selection', {}).get('ranges', []))
    spans.sort()
    starts, ends = [], []
    for low, high in spans:
        starts.append(low)
        ends.append(max(high, ends[-1] if ends else 0))
    result = {}
    for rva, sites in targets.items():
        index = bisect.bisect_right(starts, rva) - 1
        if rva not in entries and not (index >= 0 and rva < ends[index]):
            result[rva] = sites
    return result, spans


def propose_bounds(pe, targets, occupied, instruction_limit=10000):
    import capstone
    if type(instruction_limit) is not int or instruction_limit < 1:
        raise ValueError('invalid instruction discovery budget')
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoder.detail = True
    boundaries = sorted(set(targets) | {low for low, high in occupied})
    proposals, rejected = [], []
    for entry in sorted(targets):
        section = next(s for s in pe.sections if s['rva'] <= entry <
                       s['rva'] + min(s['virtual_size'], s['file_size']))
        limit = section['rva'] + min(section['virtual_size'], section['file_size'])
        index = bisect.bisect_right(boundaries, entry)
        if index < len(boundaries):
            limit = min(limit, boundaries[index])
        pending, instructions, byte_owner = [entry], {}, {}
        external, indirect, error = [], [], None
        pc = entry
        while pending and not error:
            pc = pending.pop()
            if pc in instructions:
                continue
            if not entry <= pc < limit:
                external.append(pc)
                continue
            if pc in byte_owner:
                error = 'branch enters instruction interior'
                break
            decoded = list(decoder.disasm(pe.read(pc, min(15, limit - pc)),
                                          pe.info['image_base'] + pc, count=1))
            if not decoded:
                error = 'undecodable path at ownership boundary'
                break
            instruction = decoded[0]
            if instruction.id in (capstone.x86.X86_INS_INT3, capstone.x86.X86_INS_UD2,
                                  capstone.x86.X86_INS_HLT):
                error = 'trap or padding path requires review'
                break
            if any(pc + i in byte_owner for i in range(instruction.size)):
                error = 'overlapping instruction boundaries'
                break
            instructions[pc] = instruction
            for i in range(instruction.size):
                byte_owner[pc + i] = pc
            if len(instructions) > instruction_limit:
                error = 'instruction discovery budget exhausted'
                break
            if instruction.group(capstone.CS_GRP_RET):
                continue
            if instruction.group(capstone.CS_GRP_INT) or instruction.group(capstone.CS_GRP_IRET):
                error = 'nonlocal interrupt continuation requires review'
                break
            if instruction.group(capstone.CS_GRP_JUMP):
                if len(instruction.operands) == 1 and instruction.operands[0].type == capstone.x86.X86_OP_IMM:
                    pending.append(instruction.operands[0].imm - pe.info['image_base'])
                else:
                    indirect.append(dict(rva=pc, bytes=instruction.bytes.hex()))
                if instruction.id != capstone.x86.X86_INS_JMP:
                    pending.append(pc + instruction.size)
            else:
                pending.append(pc + instruction.size)
        fallthrough = [pc for pc, ins in instructions.items() if pc + ins.size == limit and
                       not (ins.group(capstone.CS_GRP_RET) or ins.id == capstone.x86.X86_INS_JMP)]
        if error or fallthrough:
            rejected.append(dict(rva=entry, reason=error or 'fallthrough reaches another ownership boundary',
                                 failure_rva=pc, limit_rva=limit))
            continue
        spans = []
        for pc, instruction in sorted(instructions.items()):
            if spans and spans[-1]['rva'] + spans[-1]['size'] == pc:
                spans[-1]['size'] += instruction.size
            else:
                spans.append(dict(rva=pc, size=instruction.size))
        size = max(span['rva'] + span['size'] for span in spans) - entry
        proposals.append(dict(rva=entry, size=size, ranges=spans, extra_entries=sorted(instructions),
            slice_sha256=hashlib.sha256(pe.read(entry, size)).hexdigest(), source_pointer_rvas=targets[entry],
            instruction_count=len(instructions), explicit_external_transfers=sorted(set(external)),
            unresolved_indirect_branches=indirect, catalog_source='static_code_pointer_hypothesis',
            contract_status='signature, behavior and CFG completeness unknown; not accepted',
            bounds_status='recursive decode before known ownership or another relocation-backed pointer-run target',
            behavioral_acceptance=False))
    return proposals, rejected

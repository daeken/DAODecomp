"""Original-byte/relocation-backed guarded PE32 jump-table hypotheses.

Executable-section tables require a real decoded indirect-jump origin and an
unsigned guard. Numeric words alone never become roots. This discovers bounded
table prefixes, not complete CFGs, function ABIs or accepted behavior.
"""
import hashlib
import struct
import capstone
from capstone import x86
from pathlib import Path


def guarded_tables(pe, instructions, sites, max_entries=4096, lookbehind=8):
    if type(max_entries) is not int or max_entries < 1 or type(lookbehind) is not int or not 2 <= lookbehind <= 64:
        raise ValueError('invalid switch discovery budget')
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoder.detail = True
    image_base = pe.info['image_base']
    ending, candidates = {}, []
    for row in instructions:
        rva, data = row['rva'], bytes.fromhex(row['bytes'])
        if type(rva) is not int or not 0 <= rva < 2**32 or not 1 <= len(data) <= 15:
            raise ValueError('invalid instruction metadata')
        ending.setdefault(rva + len(data), []).append((rva, data))
        # Canonical absolute [index*4+disp32]; prefixes/other addressing forms
        # remain outside this recognizer rather than receiving guessed bounds.
        if len(data) == 7 and data[:2] == b'\xff\x24' and data[2] & 0xc7 == 0x85 and data[2] & 0x38 != 0x20:
            candidates.append((rva, data))

    def decode(rva, data):
        if pe.read(rva, len(data)) != data:
            raise ValueError('instruction bytes differ from pinned original')
        result = list(decoder.disasm(data, image_base + rva, count=1))
        if len(result) != 1 or result[0].size != len(data):
            raise ValueError('independent instruction boundary differs')
        return result[0]

    def previous(end):
        rows = ending.get(end, [])
        if len(rows) != 1:
            raise ValueError('missing or ambiguous contiguous guard instruction')
        return rows[0][0], decode(*rows[0])

    def family(reg):
        name = decoder.reg_name(reg)
        for root, aliases in {'eax': ('eax','ax','al','ah'), 'ebx': ('ebx','bx','bl','bh'),
                              'ecx': ('ecx','cx','cl','ch'), 'edx': ('edx','dx','dl','dh'),
                              'esi': ('esi','si'), 'edi': ('edi','di'),
                              'esp': ('esp','sp'), 'ebp': ('ebp','bp')}.items():
            if name in aliases:
                return root
        return name

    sections = []
    for index, section in enumerate(pe.sections):
        flags = struct.unpack_from('<I', pe.data, pe.section_table + index * 40 + 36)[0]
        sections.append(dict(section, flags=flags))
    code = [(s['rva'], s['rva'] + min(s['virtual_size'], s['file_size']))
            for s in sections if s['flags'] & 0x20000000]
    tables, rejected = [], []
    for rva, data in candidates:
        try:
            jump = decode(rva, data)
            operand = jump.operands[0]
            if jump.id != x86.X86_INS_JMP or operand.type != x86.X86_OP_MEM or operand.mem.base or operand.mem.segment or operand.mem.scale != 4:
                raise ValueError('unsupported indirect jump addressing')
            index = operand.mem.index
            guard_rva, guard = previous(rva)
            if guard.id not in (x86.X86_INS_JA, x86.X86_INS_JAE) or len(guard.operands) != 1 or guard.operands[0].type != x86.X86_OP_IMM:
                raise ValueError('no adjacent unsigned out-of-range guard')
            cursor = guard_rva
            for _ in range(lookbehind - 1):
                cmp_rva, comparison = previous(cursor)
                cursor = cmp_rva
                if comparison.id == x86.X86_INS_CMP:
                    break
                if comparison.id not in (x86.X86_INS_MOV, x86.X86_INS_MOVZX, x86.X86_INS_MOVSX, x86.X86_INS_LEA, x86.X86_INS_NOP):
                    raise ValueError('guard flags or index not preserved')
                if any(family(reg) == family(index) for reg in comparison.regs_access()[1]):
                    raise ValueError('guard index modified before branch')
            else:
                raise ValueError('guard lookbehind budget exhausted')
            operands = comparison.operands
            if (len(operands) != 2 or operands[0].type != x86.X86_OP_REG or operands[0].reg != index or
                    operands[1].type != x86.X86_OP_IMM or operands[0].size != 4):
                raise ValueError('comparison does not bound the actual table index')
            bound = operands[1].imm
            count = bound + (guard.id == x86.X86_INS_JA)
            if not 0 <= bound < 2**32 or not 1 <= count <= max_entries:
                raise ValueError('jump-table entry budget exhausted or empty bound')
            default = guard.operands[0].imm - image_base
            if cmp_rva <= default < rva + len(data):
                raise ValueError('out-of-range branch re-enters guarded chain')
            if rva + 3 not in sites:
                raise ValueError('table-address operand has no HIGHLOW source')
            table = (operand.mem.disp & 0xffffffff) - image_base
            if not any(s['rva'] <= table and table + count * 4 <= s['rva'] + min(s['virtual_size'], s['file_size'])
                       for s in sections if s['flags'] & 0x40000000):
                raise ValueError('table is not file-backed readable storage')
            targets = []
            for slot in range(count):
                source = table + slot * 4
                if source not in sites:
                    raise ValueError('jump-table target word has no HIGHLOW source')
                target = struct.unpack('<I', pe.read(source, 4))[0] - image_base
                if not any(low <= target < high for low, high in code):
                    raise ValueError('jump-table target is not file-backed executable storage')
                targets.append(dict(index=slot, source_pointer_rva=source, rva=target))
            tables.append(dict(jump_rva=rva, jump_bytes=data.hex(), cmp_rva=cmp_rva,
                guard_rva=guard_rva, default_rva=default, unsigned_bound=bound,
                table_rva=table, table_sha256=hashlib.sha256(pe.read(table, count * 4)).hexdigest(),
                targets=targets, behavioral_acceptance=False,
                scope='guarded relocated table-prefix hypothesis; CFG completeness and behavior unknown'))
        except (ValueError, struct.error) as error:
            rejected.append(dict(jump_rva=rva, reason=str(error)))
    return tables, rejected


def prepare(generation, overlay, output):
    """Propose disjoint case fragments; never widen existing function ranges."""
    import gzip
    import json
    import time
    from tools import recomp, recomp_bulk
    from tools.recomp_bulk_build import require_whole_inventory
    from tools.recomp_native import PE32
    from tools.recomp_pointer_discovery import highlow_sites, propose_bounds, unowned_targets

    generation, overlay, output = generation.absolute(), overlay.absolute(), output.absolute()
    run_report = recomp.load(generation / 'report.json'); require_whole_inventory(run_report)
    descriptor = recomp.load(overlay / 'overlay.json')
    overlay_sha = recomp.digest((overlay / 'overlay.json').read_bytes())
    if run_report.get('entry_overlay_sha256') != overlay_sha:
        raise ValueError('base discovery overlay differs from generation input')
    for name, identity in descriptor['files'].items():
        if recomp.digest((overlay / name).read_bytes()) != identity:
            raise ValueError('base discovery overlay changed')
    out = output / str(time.time_ns()); out.mkdir(parents=True)
    summary = {}
    for role in ('main', 'umbra'):
        context = recomp.load(generation / role / 'context.json')
        state = recomp.state(Path(context['project']))
        if recomp.digest(recomp.encoded(state)) != context['project_sha256']:
            raise ValueError('project changed after generation')
        pe = PE32(recomp.checked_binary(state)); sites = highlow_sites(pe)
        catalog = list(map(json.loads, (generation / role / 'catalog.jsonl').open()))
        targets, origins, tables, rejected, inspected = {}, {}, [], [], 0
        for row in map(json.loads, (generation / role / 'results.jsonl').open()):
            if row['status'] != 'generated_only' or not row['coverage']['indirect_jumps']:
                continue
            marker = recomp_bulk.load_shard(generation.parent.parent / 'cache', row['key'], state['binary_sha256'], row['rva'])
            metadata = generation.parent.parent / 'cache' / row['key'] / 'function.json.gz'
            function = json.loads(gzip.decompress(metadata.read_bytes()))
            if function['rva'] != row['rva']:
                raise ValueError('generated function identity differs')
            discovered, refusals = guarded_tables(pe, function['instructions'], sites)
            inspected += 1
            for table in discovered:
                table.update(function_rva=row['rva'], metadata_sha256=marker['files']['function.json.gz'])
                tables.append(table)
                for target in table['targets']:
                    rva = target['rva']; source = target['source_pointer_rva']
                    targets.setdefault(rva, []).append(source)
                    origins.setdefault(rva, []).append(dict(function_rva=row['rva'], jump_rva=table['jump_rva'],
                        table_rva=table['table_rva'], index=target['index'], source_pointer_rva=source,
                        metadata_sha256=table['metadata_sha256']))
            rejected.extend(dict(refusal, function_rva=row['rva']) for refusal in refusals)
        targets = {rva: sorted(set(sources)) for rva, sources in targets.items()}
        targets, occupied = unowned_targets(targets, catalog)
        proposals, bounds_refusals = propose_bounds(pe, targets, occupied)
        selected = recomp.load(overlay / (role + '-role.json'))
        selected_roots = {f['rva'] for f in selected['functions']}; spans = []
        for proposal in proposals:
            if proposal['rva'] in selected_roots:
                raise ValueError('case proposal overrides an existing selection')
            for span in proposal['ranges']:
                low, high = span['rva'], span['rva'] + span['size']
                if any(low < b and a < high for a, b in occupied):
                    raise ValueError('case proposal overlaps existing ownership')
                spans.append((low, high))
            proposal.update(discovery_kind='guarded_jump_table_case_fragment',
                bounds_status='recursive decode bounded by existing ownership and other discovered case roots',
                purpose='unaccepted guarded jump-table case fragment; entry ABI and behavior unknown',
                module_sha256=state['binary_sha256'], module=state['module'], switch_origins=origins[proposal['rva']])
            selected['functions'].append(proposal)
        spans.sort()
        if any(b > c for (a, b), (c, d) in zip(spans, spans[1:])):
            raise ValueError('competing case fragment ownership')
        selected['functions'].sort(key=lambda f: f['rva'])
        recomp.atomic_json(out / (role + '-role.json'), selected)
        report = dict(binary_sha256=state['binary_sha256'], module=state['module'], inspected=inspected,
            known_catalog_sha256=recomp.digest((generation / role / 'catalog.jsonl').read_bytes()),
            tables=tables, rejected_tables=rejected, unowned_targets=len(targets), proposals=proposals,
            rejected_bounds=bounds_refusals, game_acceptance=False)
        recomp.atomic_json(out / (role + '-switch-proposals.json'), report)
        summary[role] = dict(inspected=inspected, tables=len(tables), rejected_tables=len(rejected),
            unowned_targets=len(targets), proposed=len(proposals), rejected_bounds=len(bounds_refusals),
            instructions=sum(p['instruction_count'] for p in proposals))
        print({'role': role, **summary[role]}, flush=True)
    (out / 'switch-discovery.py').write_bytes(Path(__file__).read_bytes())
    from tools import recomp_pointer_discovery
    (out / 'pointer-discovery.py').write_bytes(Path(recomp_pointer_discovery.__file__).read_bytes())
    descriptor.update(status='disjoint guarded relocated switch-case hypotheses; existing ownership and contracts preserved',
        base_overlay=dict(path=str(overlay), sha256=overlay_sha),
        generation_run=str(generation), generation_report_sha256=recomp.digest((generation / 'report.json').read_bytes()),
        switch_discovery=summary, behavioral_acceptance=False, game_acceptance=False)
    descriptor['files'] = {p.name: recomp.digest(p.read_bytes()) for p in out.iterdir() if p.is_file()}
    recomp.atomic_json(out / 'overlay.json', descriptor)
    return out, summary


def main():
    import argparse
    import json
    from tools import recomp
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generation', type=Path, required=True)
    parser.add_argument('--overlay', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=recomp.ROOT / 'local/recomp/switch-overlays')
    args = parser.parse_args()
    out, summary = prepare(args.generation, args.overlay, args.output)
    recomp.atomic_json(recomp.ROOT / 'local/recomp/startup/switch-overlay-latest.json',
                       dict(overlay=str(out), summary=summary, game_acceptance=False))
    print(json.dumps(dict(overlay=str(out), summary=summary)), flush=True)


if __name__ == '__main__': main()

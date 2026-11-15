"""Discover relocated code addresses materialized by original PE32 instructions.

MOV/PUSH immediates and absolute LEA can construct callbacks outside static
tables. Memory dereferences and numeric words alone are not pointer origins.
All proposed bodies remain unaccepted, with unknown ABI and behavior.
Executable sections can contain data; address materialization is not itself
proof of a callable function boundary.
"""
import bisect
import struct
from pathlib import Path
import capstone
from capstone import x86
from tools.recomp_pointer_discovery import highlow_sites, propose_bounds, unowned_targets


class InstructionPointerScanner:
    def __init__(self, pe):
        self.pe = pe
        self.decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        self.decoder.detail = True
        executable = []
        for index, section in enumerate(pe.sections):
            flags = struct.unpack_from('<I', pe.data, pe.section_table + index * 40 + 36)[0]
            if flags & 0x20000000:
                executable.append((section['rva'], section['rva'] + min(section['virtual_size'], section['file_size'])))
        self.sources = {}
        for site in highlow_sites(pe):
            if not any(low <= site and site + 4 <= high for low, high in executable):
                continue
            target = struct.unpack('<I', pe.read(site, 4))[0] - pe.info['image_base']
            if any(low <= target < high for low, high in executable):
                self.sources[site] = target
        self.source_rvas = sorted(self.sources)

    def intersects(self, ranges):
        for span in ranges:
            index = bisect.bisect_left(self.source_rvas, span['rva'])
            if index < len(self.source_rvas) and self.source_rvas[index] < span['rva'] + span['size']:
                return True
        return False

    def scan(self, instructions):
        origins, rejected = [], []
        for row in instructions:
            rva, data = row['rva'], bytes.fromhex(row['bytes'])
            if type(rva) is not int or not 0 <= rva < 2**32 or not 1 <= len(data) <= 15:
                raise ValueError('invalid instruction metadata')
            first = bisect.bisect_left(self.source_rvas, rva)
            last = bisect.bisect_left(self.source_rvas, rva + len(data))
            sources = self.source_rvas[first:last]
            if not sources:
                continue
            try:
                if self.pe.read(rva, len(data)) != data:
                    raise ValueError('instruction bytes differ from pinned original')
                decoded = list(self.decoder.disasm(data, self.pe.info['image_base'] + rva, count=1))
                if len(decoded) != 1 or decoded[0].size != len(data):
                    raise ValueError('independent instruction boundary differs')
                ins = decoded[0]; operands = ins.operands
                offset, value, kind = None, None, None
                if (ins.id == x86.X86_INS_MOV and len(operands) == 2 and
                        operands[0].type in (x86.X86_OP_REG, x86.X86_OP_MEM) and operands[0].size == 4 and
                        operands[1].type == x86.X86_OP_IMM and ins.imm_size == 4):
                    offset, value, kind = ins.imm_offset, operands[1].imm, 'mov_immediate'
                elif (ins.id == x86.X86_INS_PUSH and len(operands) == 1 and
                      operands[0].type == x86.X86_OP_IMM and operands[0].size == 4 and ins.imm_size == 4):
                    offset, value, kind = ins.imm_offset, operands[0].imm, 'push_immediate'
                elif (ins.id == x86.X86_INS_LEA and len(operands) == 2 and
                      operands[0].type == x86.X86_OP_REG and operands[0].size == 4 and
                      operands[1].type == x86.X86_OP_MEM and ins.disp_size == 4 and
                      not operands[1].mem.base and not operands[1].mem.index and not operands[1].mem.segment):
                    offset, value, kind = ins.disp_offset, operands[1].mem.disp, 'lea_absolute'
                actual = rva + offset if offset is not None else None
                for source in sources:
                    if source + 4 > rva + len(data):
                        reason = 'relocation crosses instruction boundary'
                    elif source != actual or (value & 0xffffffff) != self.pe.info['image_base'] + self.sources[source]:
                        reason = 'relocation is not a supported code-address materialization'
                    else:
                        origins.append(dict(rva=self.sources[source], source_pointer_rva=source,
                            instruction_rva=rva, instruction_bytes=data.hex(), kind=kind,
                            behavioral_acceptance=False))
                        continue
                    rejected.append(dict(instruction_rva=rva, source_pointer_rva=source, reason=reason))
            except (ValueError, struct.error) as error:
                rejected.append(dict(instruction_rva=rva, reason=str(error)))
        return origins, rejected


class ClosureBudgetError(ValueError):
    def __init__(self, rounds, targets):
        super().__init__('materialized code-pointer closure round budget exhausted')
        self.rounds, self.targets = rounds, targets


def discover_closure(scanner, initial_origins, catalog, max_rounds=32):
    if type(max_rounds) is not int or not 1 <= max_rounds <= 128:
        raise ValueError('invalid pointer closure budget')
    origins, seen_origins = {}, set()
    def add(items, source_kind, owner):
        for item in items:
            key = (item['rva'], item['source_pointer_rva'], item['instruction_rva'])
            if key in seen_origins:
                continue
            seen_origins.add(key)
            origins.setdefault(item['rva'], []).append(dict(item, source_kind=source_kind, source_owner_rva=owner))
    for owner, items in initial_origins:
        add(items, 'generated_original_instruction', owner)
    scanned, rejected_sources = set(), []
    for round_index in range(max_rounds):
        pointers = {rva: sorted({p['source_pointer_rva'] for p in rows}) for rva, rows in origins.items()}
        targets, occupied = unowned_targets(pointers, catalog)
        proposals, rejected_bounds = propose_bounds(scanner.pe, targets, occupied)
        for proposal in proposals:
            identity = (proposal['rva'], proposal['slice_sha256'], tuple(proposal['extra_entries']))
            if identity in scanned:
                continue
            scanned.add(identity)
            instructions = []
            for rva in proposal['extra_entries']:
                span = next(s for s in proposal['ranges'] if s['rva'] <= rva < s['rva'] + s['size'])
                raw = scanner.pe.read(rva, min(15, span['rva'] + span['size'] - rva))
                instruction = next(scanner.decoder.disasm(raw, scanner.pe.info['image_base'] + rva, count=1))
                instructions.append(dict(rva=rva, bytes=instruction.bytes.hex()))
            found, rejected = scanner.scan(instructions)
            add(found, 'bounded_original_body_hypothesis', proposal['rva'])
            rejected_sources.extend(dict(item, source_owner_rva=proposal['rva']) for item in rejected)
        updated = {rva: [p['source_pointer_rva'] for p in rows] for rva, rows in origins.items()}
        updated, _ = unowned_targets(updated, catalog)
        if set(updated) == set(targets):
            for proposal in proposals:
                proposal.update(discovery_kind='materialized_instruction_code_pointer',
                    bounds_status='recursive decode bounded by known ownership and materialized code-address roots',
                    pointer_origins=origins[proposal['rva']])
            return dict(proposals=proposals, rejected_bounds=rejected_bounds, origins=origins,
                        unowned_targets=len(targets), closure_rounds=round_index + 1,
                        rejected_closure_sources=rejected_sources)
    raise ClosureBudgetError(max_rounds, sorted(updated))


def prepare(generation, output, overlay=None, max_rounds=32):
    import gzip
    import json
    import time
    from tools import recomp, recomp_bulk, recomp_pointer_discovery
    from tools.recomp_bulk_build import require_whole_inventory
    from tools.recomp_native import PE32
    generation, output = generation.absolute(), output.absolute()
    report = recomp.load(generation / 'report.json'); require_whole_inventory(report)
    overlay = (overlay or Path(report['entry_overlay'])).absolute()
    overlay_sha = recomp.digest((overlay / 'overlay.json').read_bytes())
    if overlay_sha != report.get('entry_overlay_sha256'):
        raise ValueError('base discovery overlay differs from generation input')
    descriptor = recomp.load(overlay / 'overlay.json')
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
        scanner = InstructionPointerScanner(PE32(recomp.checked_binary(state)))
        catalog = list(map(json.loads, (generation / role / 'catalog.jsonl').open()))
        by_rva = {entry['rva']: entry for entry in catalog}
        inspected, initial, rejected, metadata_bindings = 0, [], [], {}
        for row in map(json.loads, (generation / role / 'results.jsonl').open()):
            if row['status'] != 'generated_only' or not scanner.intersects(by_rva[row['rva']]['selection']['ranges']):
                continue
            marker = recomp_bulk.load_shard(generation.parent.parent / 'cache', row['key'], state['binary_sha256'], row['rva'])
            metadata = generation.parent.parent / 'cache' / row['key'] / 'function.json.gz'
            function = json.loads(gzip.decompress(metadata.read_bytes()))
            if function['rva'] != row['rva']:
                raise ValueError('generated function identity differs')
            found, refusals = scanner.scan(function['instructions']); inspected += 1
            initial.append((row['rva'], found))
            metadata_bindings[str(row['rva'])] = marker['files']['function.json.gz']
            rejected.extend(dict(item, function_rva=row['rva']) for item in refusals)
        try:
            closure = discover_closure(scanner, initial, catalog, max_rounds)
        except ClosureBudgetError as error:
            recomp.atomic_json(out / (role + '-closure-exhausted.json'), dict(
                status=str(error), rounds=error.rounds, targets=error.targets, game_acceptance=False))
            raise
        selected = recomp.load(overlay / (role + '-role.json'))
        roots = {f['rva'] for f in selected['functions']}; _, occupied = unowned_targets({}, catalog)
        spans = []
        for proposal in closure['proposals']:
            if proposal['rva'] in roots:
                raise ValueError('instruction-pointer proposal overrides an existing selection')
            for span in proposal['ranges']:
                low, high = span['rva'], span['rva'] + span['size']
                if any(low < b and a < high for a, b in occupied):
                    raise ValueError('instruction-pointer proposal overlaps existing ownership')
                spans.append((low, high))
            proposal.update(purpose='unaccepted materialized code-pointer target; entry ABI and behavior unknown',
                            module_sha256=state['binary_sha256'], module=state['module'])
            selected['functions'].append(proposal)
        spans.sort()
        if any(b > c for (a, b), (c, d) in zip(spans, spans[1:])):
            raise ValueError('competing instruction-pointer ownership')
        selected['functions'].sort(key=lambda f: f['rva'])
        recomp.atomic_json(out / (role + '-role.json'), selected)
        evidence = dict(binary_sha256=state['binary_sha256'], module=state['module'],
            inspected_generated_bodies=inspected, source_scope='authenticated generated instructions and bounded target-body hypotheses; unsupported bodies remain unknown',
            known_catalog_sha256=recomp.digest((generation / role / 'catalog.jsonl').read_bytes()),
            metadata_bindings=metadata_bindings, rejected_sources=rejected, **closure, game_acceptance=False)
        recomp.atomic_json(out / (role + '-instruction-pointer-proposals.json'), evidence)
        summary[role] = dict(inspected=inspected, materialized_targets=len(closure['origins']),
            unowned_targets=closure['unowned_targets'], proposed=len(closure['proposals']),
            rejected_bounds=len(closure['rejected_bounds']), rejected_sources=len(rejected),
            closure_rounds=closure['closure_rounds'], instructions=sum(p['instruction_count'] for p in closure['proposals']))
        print(dict(role=role, **summary[role]), flush=True)
    (out / 'instruction-pointer-discovery.py').write_bytes(Path(__file__).read_bytes())
    (out / 'pointer-discovery.py').write_bytes(Path(recomp_pointer_discovery.__file__).read_bytes())
    descriptor.update(status='disjoint materialized instruction code-pointer hypotheses; ownership/contracts preserved',
        base_overlay=dict(path=str(overlay), sha256=overlay_sha), generation_run=str(generation),
        generation_report_sha256=recomp.digest((generation / 'report.json').read_bytes()),
        instruction_pointer_discovery=summary, behavioral_acceptance=False, game_acceptance=False)
    descriptor['files'] = {p.name: recomp.digest(p.read_bytes()) for p in out.iterdir() if p.is_file()}
    recomp.atomic_json(out / 'overlay.json', descriptor)
    return out, summary


def main():
    import argparse
    import json
    from tools import recomp
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generation', type=Path, required=True)
    parser.add_argument('--overlay', type=Path)
    parser.add_argument('--output', type=Path, default=recomp.ROOT / 'local/recomp/instruction-pointer-overlays')
    parser.add_argument('--max-rounds', type=int, default=32)
    args = parser.parse_args()
    out, summary = prepare(args.generation, args.output, args.overlay, args.max_rounds)
    recomp.atomic_json(recomp.ROOT / 'local/recomp/startup/instruction-pointer-overlay-latest.json',
                       dict(overlay=str(out), summary=summary, game_acceptance=False))
    print(json.dumps(dict(overlay=str(out), summary=summary)), flush=True)


if __name__ == '__main__': main()

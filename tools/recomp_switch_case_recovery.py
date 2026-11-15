"""Recover guarded/compressed switch cases within unaccepted owner envelopes.

Original bytes, guard paths, index maps and HIGHLOW sources are evidence for
proposals, not complete CFG or behavior proofs. Existing accepted contracts,
annotations, other owners, literal tables and skipped alignment stay intact.
"""
import hashlib
import bisect
import struct
from pathlib import Path
import capstone
from capstone import x86


def section_spans(pe, flag):
    return [(s['rva'], s['rva'] + min(s['virtual_size'], s['file_size']))
            for i, s in enumerate(pe.sections)
            if struct.unpack_from('<I', pe.data, pe.section_table + i * 40 + 36)[0] & flag]


class OriginalGraph:
    def __init__(self, pe, instructions):
        self.pe = pe
        self.decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32); self.decoder.detail = True
        self.rows, self.ends, self.incoming, self.cache = {}, {}, {}, {}
        for row in instructions:
            rva, data = row['rva'], bytes.fromhex(row['bytes'])
            if type(rva) is not int or not 0 <= rva < 2**32 or not 1 <= len(data) <= 15 or rva in self.rows:
                raise ValueError('invalid/duplicate original instruction metadata')
            self.rows[rva] = data; self.ends.setdefault(rva + len(data), []).append(rva)
        for rva, data in self.rows.items():
            if data[0] in (0xe9, 0xeb) or 0x70 <= data[0] <= 0x7f or len(data) >= 2 and data[0] == 0x0f and 0x80 <= data[1] <= 0x8f:
                ins = self.decode(rva)
                if ins.group(capstone.CS_GRP_JUMP) and ins.operands[0].type == x86.X86_OP_IMM:
                    self.incoming.setdefault(ins.operands[0].imm - pe.info['image_base'], []).append(rva)

    def decode(self, rva):
        if rva not in self.cache:
            data = self.rows[rva]
            if self.pe.read(rva, len(data)) != data:
                raise ValueError('instruction bytes differ from pinned original')
            decoded = list(self.decoder.disasm(data, self.pe.info['image_base'] + rva, count=1))
            if len(decoded) != 1 or decoded[0].size != len(data):
                raise ValueError('independent instruction boundary differs')
            self.cache[rva] = decoded[0]
        return self.cache[rva]

    def predecessors(self, rva):
        result = [(src, 'taken') for src in self.incoming.get(rva, [])]
        previous = self.ends.get(rva, [])
        if len(previous) > 1:
            raise ValueError('ambiguous predecessor instruction boundaries')
        for src in previous:
            ins = self.decode(src)
            if ins.id != x86.X86_INS_JMP and not ins.group(capstone.CS_GRP_RET) and not ins.group(capstone.CS_GRP_INT):
                result.append((src, 'fallthrough'))
        return sorted(set(result))

    def family(self, reg):
        name = self.decoder.reg_name(reg)
        for group in [('eax','ax','al','ah'),('ecx','cx','cl','ch'),('edx','dx','dl','dh'),('ebx','bx','bl','bh'),
                      ('esp','sp'),('ebp','bp'),('esi','si'),('edi','di')]:
            if name in group: return group[0]
        return name

    def preserves(self, ins, index):
        if ins.id not in (x86.X86_INS_MOV, x86.X86_INS_MOVZX, x86.X86_INS_MOVSX, x86.X86_INS_LEA,
                          x86.X86_INS_NOP, x86.X86_INS_PUSH, x86.X86_INS_POP):
            return False
        return not any(self.family(reg) == self.family(index) for reg in ins.regs_access()[1])

    def guarded_count(self, node, index, max_entries, budget):
        pending, seen = [(node, [])], set()
        remaining = [budget]
        def consume():
            remaining[0] -= 1
            if remaining[0] < 0: raise ValueError('guard provenance budget exhausted')
        while pending:
            at, path = pending.pop(0)
            if at in seen: continue
            seen.add(at)
            for source, edge in self.predecessors(at):
                consume(); ins = self.decode(source)
                inclusive = (edge == 'fallthrough' and ins.id == x86.X86_INS_JA or
                             edge == 'taken' and ins.id == x86.X86_INS_JBE)
                exclusive = (edge == 'fallthrough' and ins.id == x86.X86_INS_JAE or
                             edge == 'taken' and ins.id == x86.X86_INS_JB)
                if inclusive or exclusive:
                    cursor, comparison_path = source, []
                    while True:
                        consume(); preds = self.predecessors(cursor)
                        if len(preds) != 1: break
                        cmp_rva, cmp_edge = preds[0]; comparison = self.decode(cmp_rva)
                        if comparison.id == x86.X86_INS_CMP:
                            operands = comparison.operands
                            if (len(operands) != 2 or operands[0].type != x86.X86_OP_REG or operands[0].reg != index or
                                    operands[0].size != 4 or operands[1].type != x86.X86_OP_IMM): break
                            bound = operands[1].imm; count = bound + int(inclusive)
                            if not 0 <= bound < 2**32 or not 1 <= count <= max_entries:
                                raise ValueError('guarded index budget exhausted or empty bound')
                            other = ins.operands[0].imm - self.pe.info['image_base'] if edge == 'fallthrough' else source + ins.size
                            chain = [node, source, cmp_rva, *path, *comparison_path]
                            if any(pc <= other < pc + len(self.rows[pc]) for pc in chain):
                                raise ValueError('out-of-range branch re-enters guarded chain')
                            return count, dict(cmp_rva=cmp_rva, guard_rva=source, guard_edge=edge,
                                unsigned_bound=bound, path_rvas=chain, input_index=self.decoder.reg_name(index))
                        if cmp_edge == 'taken' and comparison.id == x86.X86_INS_JMP or cmp_edge == 'fallthrough' and self.preserves(comparison, index):
                            comparison_path.append(cmp_rva); cursor = cmp_rva
                        else: break
                elif edge == 'taken' and ins.id == x86.X86_INS_JMP or edge == 'fallthrough' and self.preserves(ins, index):
                    pending.append((source, path + [source]))
        raise ValueError('no supported unsigned guard path for actual index')


def cfg_tables(pe, instructions, sites, max_entries=4096, guard_budget=64):
    if type(max_entries) is not int or max_entries < 1 or type(guard_budget) is not int or not 1 <= guard_budget <= 4096:
        raise ValueError('invalid CFG switch discovery budget')
    graph = OriginalGraph(pe, instructions); readable = section_spans(pe, 0x40000000); code = section_spans(pe, 0x20000000)
    def read(rva, size):
        if not any(a <= rva and rva + size <= b for a, b in readable):
            raise ValueError('switch table leaves file-backed readable storage')
        return pe.read(rva, size)
    tables, rejected = [], []
    for rva, data in graph.rows.items():
        if not (len(data) == 7 and data[:2] == b'\xff\x24' and data[2] & 0xc7 == 0x85 and data[2] & 0x38 != 0x20): continue
        try:
            jump = graph.decode(rva); operand = jump.operands[0]; index = operand.mem.index
            if jump.id != x86.X86_INS_JMP or operand.type != x86.X86_OP_MEM or operand.mem.base or operand.mem.segment:
                raise ValueError('unsupported jump table addressing')
            remap, node, input_index = None, rva, index
            previous = graph.ends.get(rva, [])
            if len(previous) == 1:
                address = previous[0]; candidate = graph.decode(address); args = candidate.operands
                if (candidate.id == x86.X86_INS_MOVZX and len(args) == 2 and args[0].type == x86.X86_OP_REG and
                        args[0].reg == index and args[0].size == 4 and args[1].type == x86.X86_OP_MEM and args[1].size == 1):
                    mem = args[1].mem
                    if mem.segment or bool(mem.base) == bool(mem.index) or mem.index and mem.scale != 1 or candidate.disp_size != 4:
                        raise ValueError('unsupported compressed index-map addressing')
                    source = address + candidate.disp_offset
                    if source not in sites: raise ValueError('index-map address has no HIGHLOW source')
                    input_index = mem.base or mem.index; node = address
                    remap = dict(instruction_rva=address, source_pointer_rva=source,
                                 rva=(mem.disp & 0xffffffff) - pe.info['image_base'])
            count, witness = graph.guarded_count(node, input_index, max_entries, guard_budget)
            if remap:
                values = read(remap['rva'], count); indices = sorted(set(values))
                remap.update(size=count, bytes=values.hex(), sha256=hashlib.sha256(values).hexdigest())
            else: indices = list(range(count))
            if rva + jump.disp_offset not in sites: raise ValueError('table address has no HIGHLOW source')
            table = (operand.mem.disp & 0xffffffff) - pe.info['image_base']; targets = []
            for slot in indices:
                source = table + slot * 4
                if source not in sites: raise ValueError('case target word has no HIGHLOW source')
                target = struct.unpack('<I', read(source, 4))[0] - pe.info['image_base']
                if not any(a <= target < b for a, b in code): raise ValueError('case target is not file-backed executable storage')
                targets.append(dict(index=slot, source_pointer_rva=source, rva=target))
            tables.append(dict(jump_rva=rva, table_rva=table, targets=targets, remap=remap,
                guard_witness=witness, kind='compressed_byte_index' if remap else 'guarded_cfg',
                scope='guarded table-reference hypothesis; other paths and CFG completeness unknown', behavioral_acceptance=False))
        except (ValueError, struct.error) as error: rejected.append(dict(jump_rva=rva, reason=str(error)))
    return tables, rejected


def recover_owner(pe, selection, instructions, tables, catalog, protected=False, instruction_limit=10000, forbidden_data=()):
    if protected: raise ValueError('accepted/reviewed owner requires separate bounds review')
    if type(instruction_limit) is not int or instruction_limit < 1: raise ValueError('invalid case recovery budget')
    graph = OriginalGraph(pe, instructions); entry, end = selection['rva'], selection['rva'] + selection['size']
    other = sorted((s['rva'], s['rva'] + s['size']) for row in catalog if row['rva'] != entry
                   for s in row.get('selection', {}).get('ranges', []))
    starts, maximum = [], []
    for a,b in other:
        starts.append(a); maximum.append(max(b, maximum[-1] if maximum else 0))
    def overlaps_other(a,b):
        index = bisect.bisect_left(starts,b)-1
        return index >= 0 and maximum[index] > a
    other_roots = sorted({row['rva'] for row in catalog if row['rva'] != entry})
    def contains_other_root(a,b):
        index = bisect.bisect_left(other_roots,a)
        return index < len(other_roots) and other_roots[index] < b
    code = section_spans(pe, 0x20000000)
    known_bytes = {rva + n: rva for rva, raw in graph.rows.items() for n in range(len(raw))}
    data_spans = list(forbidden_data) + [(p['source_pointer_rva'], p['source_pointer_rva'] + 4) for table in tables for p in table['targets']]
    data_spans += [(t['remap']['rva'], t['remap']['rva'] + t['remap']['size']) for t in tables if t['remap']]
    if any(pc < b and a < pc+len(raw) for pc,raw in graph.rows.items() for a,b in data_spans):
        raise ValueError('authenticated table overlaps currently decoded instruction')
    pending = [p['rva'] for table in tables for p in table['targets']]
    discovered, byte_owner, external, unresolved, calls = {}, {}, set(), [], []
    while pending:
        pc = pending.pop()
        if pc in graph.rows or pc in discovered: continue
        if pc in known_bytes: raise ValueError('case path enters an existing instruction interior')
        if pc < entry or pc >= end or contains_other_root(pc,pc+1) or overlaps_other(pc,pc+1):
            external.add(pc); continue
        if pc in byte_owner: raise ValueError('case path enters a discovered instruction interior')
        raw = pe.read(pc, min(15, end - pc)); decoded = list(graph.decoder.disasm(raw, pe.info['image_base'] + pc, count=1))
        if not decoded: raise ValueError('case path is undecodable at owner envelope boundary')
        ins = decoded[0]; limit = pc + ins.size
        if not any(a <= pc and limit <= b for a, b in code): raise ValueError('case path leaves executable storage')
        if ins.id in (x86.X86_INS_INT3,x86.X86_INS_UD2,x86.X86_INS_HLT): raise ValueError('case reaches trap or padding')
        if any(pc < b and a < limit for a,b in data_spans) or overlaps_other(pc,limit) or contains_other_root(pc,limit):
            raise ValueError('case instruction overlaps table data or another owner')
        if any(pc+n in known_bytes or pc+n in byte_owner for n in range(ins.size)):
            raise ValueError('case instruction overlaps existing/discovered instruction bytes')
        if ins.group(capstone.CS_GRP_INT) or ins.group(capstone.CS_GRP_IRET): raise ValueError('nonlocal case continuation requires review')
        discovered[pc] = ins
        for n in range(ins.size): byte_owner[pc+n] = pc
        if len(discovered) > instruction_limit: raise ValueError('case instruction budget exhausted')
        if ins.group(capstone.CS_GRP_RET): continue
        if ins.group(capstone.CS_GRP_JUMP):
            if ins.operands[0].type == x86.X86_OP_IMM: pending.append(ins.operands[0].imm - pe.info['image_base'])
            else: unresolved.append(dict(rva=pc,bytes=ins.bytes.hex()))
            if ins.id != x86.X86_INS_JMP: pending.append(limit)
        else:
            if ins.group(capstone.CS_GRP_CALL): calls.append(dict(rva=pc,bytes=ins.bytes.hex()))
            pending.append(limit)
    # Add only decoded bytes; merge adjacent intervals without filling holes.
    intervals = sorted([(s['rva'],s['rva']+s['size']) for s in selection['ranges']] +
                       [(pc,pc+ins.size) for pc,ins in discovered.items()])
    merged = []
    for a,b in intervals:
        if merged and a <= merged[-1][1]: merged[-1] = (merged[-1][0],max(merged[-1][1],b))
        else: merged.append((a,b))
    result = dict(selection, ranges=[dict(rva=a,size=b-a) for a,b in merged],
                  extra_entries=sorted(set(selection.get('extra_entries',[])) | set(discovered)))
    return result, dict(added_instructions=[dict(rva=pc,bytes=ins.bytes.hex()) for pc,ins in sorted(discovered.items())],
        external_transfers=sorted(external), unresolved_indirect_branches=unresolved, calls=calls,
        previous_ranges=selection['ranges'], proposed_ranges=result['ranges'],
        scope='unaccepted owner-envelope correction from original case paths; ABI and CFG completeness unknown', behavioral_acceptance=False)


def table_data(tables):
    return [(p['source_pointer_rva'],p['source_pointer_rva']+4) for t in tables for p in t['targets']] + [
        (t['remap']['rva'],t['remap']['rva']+t['remap']['size']) for t in tables if t['remap']]


def prepare(generation, output, max_rounds=16):
    import gzip
    import json
    import time
    from tools import recomp, recomp_bulk, recomp_pointer_discovery
    from tools.recomp_native import PE32
    from tools.recomp_pointer_discovery import highlow_sites
    from tools.recomp_bulk_build import require_whole_inventory
    if type(max_rounds) is not int or not 1 <= max_rounds <= 128: raise ValueError('invalid owner recovery round budget')
    generation, output = generation.absolute(), output.absolute()
    run_report = recomp.load(generation/'report.json'); require_whole_inventory(run_report)
    overlay = Path(run_report['entry_overlay']); descriptor = recomp.load(overlay/'overlay.json')
    overlay_sha = recomp.digest((overlay/'overlay.json').read_bytes())
    if overlay_sha != run_report['entry_overlay_sha256']: raise ValueError('input overlay identity changed')
    for name,sha in descriptor['files'].items():
        if recomp.digest((overlay/name).read_bytes()) != sha: raise ValueError('input overlay file changed')
    out = output/str(time.time_ns()); out.mkdir(parents=True)
    (out/'switch-case-recovery.py').write_bytes(Path(__file__).read_bytes())
    (out/'pointer-discovery.py').write_bytes(Path(recomp_pointer_discovery.__file__).read_bytes())
    registry_path = recomp.ROOT/'analysis/functions.json'
    registry = recomp.load(registry_path)['functions']; registry_sha = recomp.digest(registry_path.read_bytes()); summary = {}
    for role in ('main','umbra'):
        context = recomp.load(generation/role/'context.json'); state = recomp.state(Path(context['project']))
        if recomp.digest(recomp.encoded(state)) != context['project_sha256']: raise ValueError('project changed after generation')
        pe = PE32(recomp.checked_binary(state)); sites = highlow_sites(pe)
        protected = {int(r['id'].rsplit(':rva-',1)[1],16) for r in registry
                     if r.get('module_sha256') == state['binary_sha256'] and r.get('module','').lower() == state['module'].lower()}
        catalog = list(map(json.loads,(generation/role/'catalog.jsonl').open())); owners = {r['rva']:r for r in catalog}
        selected = recomp.load(overlay/(role+'-role.json')); selections = {s['rva']:s for s in selected['functions']}
        records, refusals, all_data = {}, [], []
        for row in map(json.loads,(generation/role/'results.jsonl').open()):
            if row['status'] != 'generated_only' or not row['coverage']['indirect_jumps']: continue
            marker = recomp_bulk.load_shard(generation.parent.parent/'cache',row['key'],state['binary_sha256'],row['rva'])
            metadata = generation.parent.parent/'cache'/row['key']/'function.json.gz'
            function = json.loads(gzip.decompress(metadata.read_bytes()))
            if function['rva'] != row['rva']: raise ValueError('function metadata identity differs')
            try: tables,rejected = cfg_tables(pe,function['instructions'],sites)
            except ValueError as error:
                refusals.append(dict(rva=row['rva'],reason=str(error),stage='guard_metadata')); continue
            all_data.extend(table_data(tables))
            records[row['rva']] = dict(instructions=function['instructions'],tables=tables,rejected_tables=rejected,
                metadata_sha256=marker['files']['function.json.gz'])
        proposals = []
        for rva,record in sorted(records.items()):
            if not record['tables']: continue
            owner = owners[rva]; previous = owner['selection']; current = previous
            instructions = record['instructions']; changes = []; tables = record['tables']; rejected = record['rejected_tables']
            owner_data = list(all_data)
            try:
                if rva in protected or owner['catalog_source'] in ('reviewed_startup','annotated_project'):
                    # Do not request review for owners that need no correction.
                    known = {i['rva'] for i in instructions}
                    if any(current['rva'] <= t['rva'] < current['rva']+current['size'] and t['rva'] not in known
                           for table in tables for t in table['targets']):
                        raise ValueError('accepted/reviewed owner requires separate bounds review')
                    continue
                for round_index in range(max_rounds):
                    updated, evidence = recover_owner(pe,current,instructions,tables,catalog,forbidden_data=owner_data)
                    added = evidence['added_instructions']
                    if not added: break
                    changes.append(evidence); current = updated
                    instructions = sorted([*instructions,*added],key=lambda i:i['rva'])
                    tables,rejected = cfg_tables(pe,instructions,sites)
                    # Newly recognized data must not become code in this round.
                    owner_data.extend(table_data(tables))
                else: raise ValueError('case recovery round budget exhausted')
                if not changes: continue
                revised = dict(selections.get(rva,previous),ranges=current['ranges'],extra_entries=current['extra_entries'])
                revised['case_recovery'] = dict(previous_selection_sha256=recomp.digest(recomp.encoded(previous)),
                    generation_run=str(generation),metadata_sha256=record['metadata_sha256'],
                    scope='unaccepted range/entry proposal inside unchanged owner envelope; original annotations/contracts preserved')
                selections[rva] = revised
                all_data = owner_data
                owners[rva] = dict(owner,selection=dict(current)); catalog = [owners[row['rva']] for row in catalog]
                proposals.append(dict(rva=rva,previous_selection=previous,proposed_selection=current,changes=changes,
                    tables=tables,rejected_tables=rejected,metadata_sha256=record['metadata_sha256'],
                    added_bytes=sum(s['size'] for s in current['ranges'])-sum(s['size'] for s in previous['ranges']),
                    added_instructions=sum(len(c['added_instructions']) for c in changes),rounds=round_index+1,
                    behavioral_acceptance=False))
            except ValueError as error: refusals.append(dict(rva=rva,reason=str(error),stage='case_paths'))
        selected['functions'] = [selections[rva] for rva in sorted(selections)]
        recomp.atomic_json(out/(role+'-role.json'),selected)
        evidence = dict(binary_sha256=state['binary_sha256'],module=state['module'],
            known_catalog_sha256=recomp.digest((generation/role/'catalog.jsonl').read_bytes()),
            inspected_generated_owners=len(records),tables=[dict(t,owner_rva=rva) for rva,r in records.items() for t in r['tables']],
            rejected_tables=[dict(t,owner_rva=rva) for rva,r in records.items() for t in r['rejected_tables']],
            proposals=proposals,refusals=refusals,
            scope='Original case paths inside unaccepted owner envelopes only; external transfers and unsupported inputs remain unresolved',game_acceptance=False)
        recomp.atomic_json(out/(role+'-case-recovery.json'),evidence)
        summary[role] = dict(inspected=len(records),tables=len(evidence['tables']),
            compressed_tables=sum(t['remap'] is not None for t in evidence['tables']),
            updated_owners=len(proposals),added_instructions=sum(p['added_instructions'] for p in proposals),
            added_bytes=sum(p['added_bytes'] for p in proposals),refused_owners=len(refusals),
            rejected_tables=len(evidence['rejected_tables']))
        print(dict(role=role,**summary[role]),flush=True)
    descriptor.update(status='unaccepted switch case/shared-tail coverage proposals; envelope and accepted contracts unchanged',
        base_overlay=dict(path=str(overlay),sha256=overlay_sha),generation_run=str(generation),
        generation_report_sha256=recomp.digest((generation/'report.json').read_bytes()),
        protected_registry_sha256=registry_sha,decoder_version=capstone.__version__,
        case_recovery=summary,behavioral_acceptance=False,game_acceptance=False)
    descriptor['files'] = {p.name:recomp.digest(p.read_bytes()) for p in out.iterdir() if p.is_file()}
    recomp.atomic_json(out/'overlay.json',descriptor)
    return out,summary


def main():
    import argparse
    import json
    from tools import recomp
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generation',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=recomp.ROOT/'local/recomp/case-coverage-overlays')
    parser.add_argument('--max-rounds',type=int,default=16)
    args = parser.parse_args();out,summary = prepare(args.generation,args.output,args.max_rounds)
    recomp.atomic_json(recomp.ROOT/'local/recomp/startup/case-coverage-overlay-latest.json',
                       dict(overlay=str(out),summary=summary,game_acceptance=False))
    print(json.dumps(dict(overlay=str(out),summary=summary)),flush=True)


if __name__ == '__main__': main()

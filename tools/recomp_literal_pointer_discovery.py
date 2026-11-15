"""Find relocation-backed code addresses outside emitted instructions.

Executable sections also contain dispatch data. These are literal-origin and
bounded-decode hypotheses, not inferred table bounds or accepted functions.
Nonexecutable resource words and relocation operands inside emitted instructions
stay excluded.
"""
import gzip
import json
from pathlib import Path
import struct
import time
from tools import recomp, recomp_bulk, recomp_pointer_discovery
from tools.recomp_bulk_build import require_whole_inventory
from tools.recomp_native import PE32


class ExecutableLiteralScanner:
    def __init__(self, pe):
        self.pe = pe
        self.code = [(s['rva'], s['rva'] + min(s['virtual_size'], s['file_size']))
                     for i, s in enumerate(pe.sections)
                     if struct.unpack_from('<I', pe.data, pe.section_table + i * 40 + 36)[0] & 0x20000000]
        extent = max((b for a, b in self.code), default=0)
        self.known = bytearray(extent)
        self.lengths = bytearray(extent)

    def executable(self, rva, size=1):
        return any(a <= rva and rva + size <= b for a, b in self.code)

    def record_emitted(self, instructions):
        for row in instructions:
            rva, data = row['rva'], bytes.fromhex(row['bytes'])
            if type(rva) is not int or not 1 <= len(data) <= 15 or not self.executable(rva, len(data)):
                raise ValueError('invalid emitted instruction span')
            if self.pe.read(rva, len(data)) != data:
                raise ValueError('emitted instruction differs from pinned original')
            if self.known[rva]:
                if self.known[rva] != 1 or self.lengths[rva] != len(data):
                    raise ValueError('conflicting emitted instruction boundaries')
            elif any(self.known[rva:rva + len(data)]):
                raise ValueError('overlapping emitted instruction boundaries')
            self.known[rva:rva + len(data)] = bytes([2]) * len(data)
            self.known[rva] = 1
            self.lengths[rva] = len(data)

    def scan(self):
        origins, excluded = [], []
        for source in sorted(recomp_pointer_discovery.highlow_sites(self.pe)):
            if not self.executable(source):
                continue
            if not self.executable(source, 4):
                excluded.append(dict(source_pointer_rva=source, reason='source crosses executable file-backed storage'))
                continue
            if any(self.known[source:source + 4]):
                excluded.append(dict(source_pointer_rva=source, reason='relocation overlaps emitted instruction bytes'))
                continue
            data = self.pe.read(source, 4)
            target = struct.unpack('<I', data)[0] - self.pe.info['image_base']
            if not self.executable(target):
                excluded.append(dict(source_pointer_rva=source, reason='target is not file-backed module code'))
                continue
            origins.append(dict(rva=target, source_pointer_rva=source, source_bytes=data.hex(),
                                kind='relocated_word_outside_emitted_instructions', behavioral_acceptance=False))
        literal_bytes = bytearray(len(self.known))
        for row in origins:
            source = row['source_pointer_rva']
            literal_bytes[source:source + 4] = bytes([1]) * 4
        targets, retained, refused = {}, [], []
        for row in origins:
            target = row['rva']
            reason = ('target overlaps another candidate literal word' if literal_bytes[target] else
                      'target is an emitted instruction interior' if self.known[target] == 2 else None)
            if reason:
                refused.append(dict(row, reason=reason))
                continue
            targets.setdefault(target, []).append(row['source_pointer_rva'])
            retained.append(row)
        return dict(targets=targets, origins=retained, refused=refused, excluded_sources=excluded,
                    scope='Original HIGHLOW words outside emitted instructions; data/callable status and dispatch index bounds remain hypotheses.')


def prepare(generation, output):
    generation, output = generation.absolute(), output.absolute()
    report = recomp.load(generation / 'report.json')
    require_whole_inventory(report)
    prior = Path(report['entry_overlay'])
    descriptor = recomp.load(prior / 'overlay.json')
    if recomp.digest((prior / 'overlay.json').read_bytes()) != report['entry_overlay_sha256']:
        raise ValueError('input overlay changed')
    for name, identity in descriptor['files'].items():
        if recomp.digest((prior / name).read_bytes()) != identity:
            raise ValueError('input overlay member changed')
    out = output / str(time.time_ns())
    out.mkdir(parents=True)
    summary = {}
    for role in ('main', 'umbra'):
        context = recomp.load(generation / role / 'context.json')
        state = recomp.state(Path(context['project']))
        if recomp.digest(recomp.encoded(state)) != context['project_sha256']:
            raise ValueError('project changed after generation')
        scanner = ExecutableLiteralScanner(PE32(recomp.checked_binary(state)))
        catalog = list(map(json.loads, (generation / role / 'catalog.jsonl').open()))
        bindings = {}
        for row in map(json.loads, (generation / role / 'results.jsonl').open()):
            if row['status'] != 'generated_only':
                continue
            cache = generation.parent.parent / 'cache'
            marker = recomp_bulk.load_shard(cache, row['key'], state['binary_sha256'], row['rva'])
            function = json.loads(gzip.decompress((cache / row['key'] / 'function.json.gz').read_bytes()))
            if function['rva'] != row['rva']:
                raise ValueError('function metadata identity differs')
            scanner.record_emitted(function['instructions'])
            bindings[str(row['rva'])] = marker['files']['function.json.gz']
        found = scanner.scan()
        targets, occupied = recomp_pointer_discovery.unowned_targets(found['targets'], catalog)
        proposals, refused_bounds = recomp_pointer_discovery.propose_bounds(scanner.pe, targets, occupied)
        literal_spans = [(r['source_pointer_rva'], r['source_pointer_rva'] + 4) for r in found['origins'] + found['refused']]
        selected = recomp.load(prior / (role + '-role.json'))
        roots = {f['rva'] for f in selected['functions']}
        added, spans = [], []
        for proposal in proposals:
            if any(s['rva'] < b and a < s['rva'] + s['size'] for s in proposal['ranges'] for a, b in literal_spans):
                refused_bounds.append(dict(rva=proposal['rva'], reason='decoded hypothesis overlaps candidate literal storage'))
                continue
            if proposal['rva'] in roots:
                raise ValueError('literal-origin proposal overrides existing entry')
            for span in proposal['ranges']:
                a, b = span['rva'], span['rva'] + span['size']
                if any(a < y and x < b for x, y in occupied):
                    raise ValueError('literal-origin proposal overlaps existing ownership')
                spans.append((a, b))
            proposal.update(purpose='unaccepted executable-section literal code-pointer hypothesis',
                            module_sha256=state['binary_sha256'], module=state['module'],
                            pointer_origins=[r for r in found['origins'] if r['rva'] == proposal['rva']])
            selected['functions'].append(proposal)
            added.append(proposal)
        spans.sort()
        if any(b > c for (a, b), (c, d) in zip(spans, spans[1:])):
            raise ValueError('competing literal-origin ownership')
        selected['functions'].sort(key=lambda f: f['rva'])
        recomp.atomic_json(out / (role + '-role.json'), selected)
        recomp.checked_binary(state)
        owned_unknown = [r for r in found['origins'] if r['rva'] not in targets and scanner.known[r['rva']] != 1]
        evidence = dict(binary_sha256=state['binary_sha256'], module=state['module'],
                        metadata_bindings=bindings, known_catalog_sha256=recomp.digest((generation / role / 'catalog.jsonl').read_bytes()),
                        **found, proposals=added, refused_bounds=refused_bounds, owned_unregistered_targets=owned_unknown,
                        game_acceptance=False)
        recomp.atomic_json(out / (role + '-literal-pointer-proposals.json'), evidence)
        summary[role] = dict(literal_origins=len(found['origins']), targets=len(found['targets']),
                             unowned_targets=len(targets), proposed=len(added), rejected_bounds=len(refused_bounds),
                             ambiguous_targets=len(found['refused']), owned_unregistered_targets=len(owned_unknown))
        print(dict(role=role, **summary[role]), flush=True)
    for name, source in [('literal-controller.py', Path(__file__)), ('pointer-controller.py', Path(recomp_pointer_discovery.__file__))]:
        (out / name).write_bytes(source.read_bytes())
    descriptor.update(status='unaccepted literal-origin proposals; no dispatch-bound or callable-entry proof',
                      base_overlay=dict(path=str(prior), sha256=recomp.digest((prior / 'overlay.json').read_bytes())),
                      generation_run=str(generation), generation_report_sha256=recomp.digest((generation / 'report.json').read_bytes()),
                      literal_pointer_discovery=summary, game_acceptance=False, behavioral_acceptance=False)
    descriptor['files'] = {p.name: recomp.digest(p.read_bytes()) for p in out.iterdir() if p.is_file()}
    recomp.atomic_json(out / 'overlay.json', descriptor)
    return out, summary


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generation', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=recomp.ROOT / 'local/recomp/literal-pointer-overlays')
    args = parser.parse_args()
    out, summary = prepare(args.generation, args.output)
    recomp.atomic_json(recomp.ROOT / 'local/recomp/startup/literal-pointer-overlay-latest.json',
                       dict(overlay=str(out), summary=summary, game_acceptance=False))
    print(out, flush=True)


if __name__ == '__main__':
    main()

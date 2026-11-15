"""Whole-inventory, cached C++ generation. Output is hypotheses, never acceptance.

Each function has an independent artifact transaction. One failed lift does not
abort its neighbors. Original-byte coverage and ownership remain separate facts.
"""
import argparse
from collections import Counter
import gzip
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from tools import recomp, recomp_storage
from tools.daodecomp.pe import fingerprint

DEFAULT_INVENTORIES = {
    'main': recomp.ROOT / 'local/analysis/functions.json',
    'umbra': recomp.ROOT / 'local/recomp/startup/umbra-analysis/functions.json',
}
DEFAULT_PROJECTS = {'main': recomp.ROOT / 'local/recomp/project', 'umbra': recomp.ROOT / 'local/recomp/umbra'}


def read_rva(image, pe, rva, size):
    matches = [s for s in pe['sections'] if s['rva'] <= rva and rva + size <= s['rva'] + s['file_size']]
    if len(matches) != 1 or size <= 0:
        raise ValueError('range is not uniquely file-backed')
    offset = matches[0]['file_offset'] + rva - matches[0]['rva']
    result = image[offset:offset + size]
    if len(result) != size:
        raise ValueError('truncated original range')
    return result


def selection_for(item, annotated, reviewed, image, pe):
    rva = item['rva']
    if type(rva) is not int or not 0 <= rva < 2**32:
        raise ValueError('invalid inventory RVA')
    source = reviewed or annotated
    if source:
        size = source['size']
        spans = source.get('ranges') or [dict(rva=rva, size=size)]
    else:
        spans = [dict(rva=b['start_rva'], size=b['end_rva_inclusive'] - b['start_rva'] + 1) for b in item['body_ranges']]
        size = max(b['rva'] + b['size'] for b in spans) - rva
    if annotated and annotated['size'] != size:
        raise ValueError('inventory/review bounds conflict with existing annotations')
    if type(size) is not int or size <= 0 or rva + size > 2**32 or not spans:
        raise ValueError('invalid traversal envelope')
    spans = sorted(spans, key=lambda b: b['rva'])
    end = rva
    for span in spans:
        if (type(span['rva']) is not int or type(span['size']) is not int or span['size'] <= 0 or
                span['rva'] < end or span['rva'] < rva or span['rva'] + span['size'] > rva + size):
            raise ValueError('invalid or overlapping owned ranges')
        read_rva(image, pe, span['rva'], span['size'])
        end = span['rva'] + span['size']
    envelope = read_rva(image, pe, rva, size)
    if source and source.get('slice_sha256') and recomp.digest(envelope) != source['slice_sha256']:
        raise ValueError('reviewed original slice changed')
    extra = (reviewed or {}).get('extra_entries', (annotated or {}).get('extra_entries', []))
    if any(not any(b['rva'] <= value < b['rva'] + b['size'] for b in spans) for value in extra):
        raise ValueError('extra entry outside owned ranges')
    return dict(rva=rva, size=size, ranges=spans, extra_entries=extra,
                annotations=(annotated or {}).get('annotations', {}), structures=(annotated or {}).get('structures', {}))


def function_key(pipeline, module, binary_sha, prefix, selection):
    return recomp.digest(recomp.encoded(dict(pipeline=pipeline, module=module.lower(), binary_sha256=binary_sha,
                                             module_prefix=prefix, selection=selection)))


def load_shard(cache, key, binary_sha, rva):
    directory = cache / key
    marker = recomp.load(directory / 'complete.json')
    if (marker['schema_version'] != 1 or marker['artifact_key'] != key or marker['binary_sha256'] != binary_sha or
            marker['rva'] != rva or marker['behavioral_acceptance'] is not False or
            marker['status'] not in ('generated_only', 'generation_failed', 'interrupted_unknown')):
        raise ValueError('function shard identity/status changed')
    required = {'function.cpp', 'function.json.gz'} if marker['status'] == 'generated_only' else {'failure.json'}
    if set(marker['files']) != required:
        raise ValueError('incomplete function shard')
    for name, identity in marker['files'].items():
        if Path(name).name != name or recomp.digest((directory / name).read_bytes()) != identity:
            raise ValueError('function shard bytes changed: ' + name)
    return marker


def coverage(cache, key, selection, image, pe):
    with gzip.open(cache / key / 'function.json.gz', 'rt') as source:
        function = json.load(source)
    if function['rva'] != selection['rva'] or function['size'] != selection['size']:
        raise ValueError('generated function identity changed')
    end = -1
    covered = 0
    for instruction in function['instructions']:
        rva, code = instruction['rva'], bytes.fromhex(instruction['bytes'])
        if not code or rva < end or not any(b['rva'] <= rva and rva + len(code) <= b['rva'] + b['size'] for b in selection['ranges']):
            raise ValueError('lifted instruction leaves/overlaps declared ownership')
        if read_rva(image, pe, rva, len(code)) != code:
            raise ValueError('lifted bytes differ from pinned original')
        end = rva + len(code)
        covered += len(code)
    owned = sum(b['size'] for b in selection['ranges'])
    indirect = sum(t['kind'] == 'Jmp' and t['direct_target'] is None for t in function['abi']['transfers'])
    return dict(instruction_count=len(function['instructions']), covered_inventory_bytes=covered,
                owned_inventory_bytes=owned, uncovered_inventory_bytes=owned - covered,
                indirect_jumps=indirect, unselected_call_continuations=len(function['unselected_call_continuations']),
                scope='Original-byte inventory coverage only; not CFG completeness or behavioral acceptance.')


def ownership_components(entries):
    intervals = sorted((b['rva'], b['rva'] + b['size'], entry['rva']) for entry in entries if 'selection' in entry for b in entry['selection']['ranges'])
    groups, owners, start, end = [], set(), 0, -1
    for left, right, owner in intervals:
        if left >= end:
            if len(owners) > 1:
                groups.append(dict(start_rva=start, end_rva=end, functions=sorted(owners)))
            start, end, owners = left, right, {owner}
        else:
            end = max(end, right)
            owners.add(owner)
    if len(owners) > 1:
        groups.append(dict(start_rva=start, end_rva=end, functions=sorted(owners)))
    return groups


def freeze_backend(output, dispatch):
    with recomp.locked(recomp.ROOT / 'local/recomp/bridge-build'):
        command = ['dotnet', 'build', str(recomp.BRIDGE), '-c', 'Release', '--nologo',
                   '-p:SharpRetroRoot=' + str(recomp.ROOT.parent / 'SharpRetro')]
        result = subprocess.run(command, capture_output=True, text=True, timeout=180)
        (output / 'bridge-build.log').write_text(result.stdout + result.stderr)
        if result.returncode:
            raise RuntimeError('bridge build failed; see bridge-build.log')
        files = {p.name: p.read_bytes() for p in recomp.DLL.parent.iterdir() if p.suffix in ('.dll', '.hpp', '.json')}
        policy = recomp.load(recomp.MODULE_POLICY)
        if policy['schema_version'] != 1 or policy['default_import_policy'] != 'native':
            raise ValueError('unexpected module policy')
        descriptor = dict(schema_version=1, backend={name: recomp.digest(data) for name, data in files.items()},
                          controller_sha256=recomp.digest(Path(__file__).read_bytes()),
                          storage_controller_sha256=recomp.digest(Path(recomp_storage.__file__).read_bytes()),
                          bridge_source_sha256=recomp.digest((recomp.BRIDGE.parent / 'Program.cs').read_bytes()),
                          dispatch=dispatch, module_policy=policy,
                          host=dict(platform=sys.platform, machine=os.uname().machine,
                                    dotnet=subprocess.check_output(['dotnet', '--version'], text=True).strip()))
        identity = recomp.digest(recomp.encoded(descriptor))
        target = output / 'backends' / identity
        target.mkdir(parents=True, exist_ok=True)
        for name, data in files.items():
            path = target / name
            if path.exists():
                if path.read_bytes() != data:
                    raise ValueError('frozen backend changed')
            else:
                path.write_bytes(data)
        for name, payload in [('controller.py', Path(__file__).read_bytes()), ('storage-controller.py',Path(recomp_storage.__file__).read_bytes()), ('bridge-program.cs', (recomp.BRIDGE.parent / 'Program.cs').read_bytes())]:
            path = target / name
            if path.exists() and path.read_bytes() != payload:
                raise ValueError('frozen controller source changed')
            path.write_bytes(payload)
        recomp.atomic_json(target / 'pipeline.json', descriptor)
        return identity, target, descriptor


def normalize_error(error):
    intrinsic = re.search(r'intrin\.([\w.-]+)', error)
    if intrinsic:
        return error.split(':', 1)[0] + ': intrinsic ' + intrinsic.group(1)
    error = re.sub(r'0x[0-9a-fA-F]+', '0xADDR', error)
    return re.sub(r'%\d+|\b(?:var|tmp|v)\d+\b', '%TEMP', error)


def write_unknown(cache, item, binary_sha, cause):
    cache.mkdir(exist_ok=True)
    key = item['key']
    with tempfile.TemporaryDirectory(prefix='.unknown-', dir=cache) as temporary:
        staging = Path(temporary) / 'shard'
        staging.mkdir()
        failure = dict(status='interrupted_unknown', error=cause, behavioral_acceptance=False)
        recomp.atomic_json(staging / 'failure.json', failure)
        marker = dict(schema_version=1, binary_sha256=binary_sha, rva=item['rva'], artifact_key=key,
                      status='interrupted_unknown', behavioral_acceptance=False, stage='process', error_type='ProcessIncomplete', error=cause,
                      files={'failure.json': recomp.digest((staging / 'failure.json').read_bytes())})
        recomp.atomic_json(staging / 'complete.json', marker)
        staging.rename(cache / key)


def generate_batch(items, state, prefix, cache, backend, descriptor, directory, timeout, dispatch):
    pending = list(items)
    attempt = 0
    while pending:
        name = f'{items[0]["rva"]:08x}-{attempt}'
        request = dict(schema_version=1, binary=state['binary'], binary_sha256=state['binary_sha256'],
                       functions=[dict(item['selection'], artifact_key=item['key']) for item in pending],
                       module_prefix=prefix, import_policy={k: v['policy'] for k, v in descriptor['module_policy']['modules'].items()},
                       isolate_failures=True, artifact_directory=str(cache), dispatch=dispatch)
        command = ['dotnet', str(backend / 'Recomp.Bridge.dll')]
        cause = None
        with (directory / (name + '.stdout')).open('wb') as stdout, (directory / (name + '.stderr')).open('wb') as stderr:
            try:
                result = subprocess.run(command, input=json.dumps(request).encode(), stdout=stdout, stderr=stderr, timeout=timeout)
                if result.returncode:
                    cause = f'bridge process exit {result.returncode}; {name}.stderr'
            except subprocess.TimeoutExpired:
                cause = f'bridge process timeout after {timeout}s; {name}.stderr'
        incomplete = [item for item in pending if not (cache / item['key'] / 'complete.json').exists()]
        if cause is None:
            response = recomp.load(directory / (name + '.stdout'))
            if response['binary_sha256'] != state['binary_sha256'] or not response['artifact_mode'] or not response['failure_isolation'] or incomplete:
                raise ValueError('incomplete/incorrect bulk bridge response')
            metadata = directory / 'module.json.gz'
            response.pop('functions')
            if not metadata.exists():
                with gzip.open(metadata, 'wt') as stream:
                    json.dump(response, stream)
            return
        if not incomplete:
            return
        # Only the first uncommitted entry is attributed an unknown attempt.
        # Remaining entries still get their own independent generation attempt.
        write_unknown(directory / 'unknown', incomplete[0], state['binary_sha256'], cause)
        if len(incomplete) == len(pending) and attempt >= 2:
            raise RuntimeError('repeated bridge process failure without completed shards; see batch diagnostics')
        pending = incomplete[1:]
        attempt += 1


def known_catalog(inventory,annotated,reviewed):
    """Retain every static hypothesis and every existing bounded selection."""
    rows=[];seen=set()
    for row in inventory:
        if row['rva'] in seen:raise ValueError('duplicate inventory entry identity')
        seen.add(row['rva']);rows.append(dict(row,catalog_source='static_inventory'))
    for rva in sorted((set(annotated)|set(reviewed))-seen):
        source=reviewed.get(rva) or annotated[rva]
        origin='reviewed_startup' if rva in reviewed else 'annotated_project'
        # Discovery overlays share the startup-selection transport, but have
        # neither reviewed bounds nor accepted function contracts.
        if source.get('catalog_source')=='static_code_pointer_hypothesis':
            origin='static_code_pointer_hypothesis'
        rows.append(dict(rva=rva,name=source.get('purpose','existing selected entry'),
                         catalog_source=origin))
    return sorted(rows,key=lambda row:row['rva'])


def generate_module(role, project, inventory_path, startup, output, pipeline, backend, descriptor, args, run_dir):
    state = recomp.state(project)
    binary = recomp.checked_binary(state)
    image = binary.read_bytes()
    pe = fingerprint(binary)
    inventory = recomp.load(inventory_path)
    if inventory['module_sha256'] != state['binary_sha256'] or pe['format'] != 'PE32' or pe['architecture'] != 'x86':
        raise ValueError('inventory/project module mismatch')
    rule = descriptor['module_policy']['modules'].get(state['module'].lower())
    if rule and (rule['sha256'] != state['binary_sha256'] or rule['policy'] != 'translate'):
        raise ValueError('module policy forbids this translation')
    if startup and (startup['module'] != state['module'] or startup['binary_sha256'] != state['binary_sha256']):
        raise ValueError('startup annotations differ from pinned module')
    prefix = '' if role == 'main' else 'm_' + recomp.digest((state['module'].lower() + ':' + state['binary_sha256']).encode())[:16] + '_'
    annotated = {f['rva']: f for f in state['functions']}
    reviewed = {f['rva']: f for f in (startup or {}).get('functions', [])}
    module_dir = run_dir / role
    module_dir.mkdir()
    cache = output / 'cache'
    cache.mkdir(exist_ok=True)
    if not hasattr(args,'_artifact_content_index'):
        args._artifact_content_index=recomp_storage.content_index(cache)
    entries = []
    seen = set()
    catalog=known_catalog(inventory['functions'],annotated,reviewed)
    for item in catalog:
        rva = item['rva']
        if rva in seen:
            raise ValueError('duplicate inventory entry identity')
        seen.add(rva)
        entry = dict(rva=rva, id=f'{state["binary_sha256"]}:{state["module"]}:rva-{rva:08x}',
                     inventory_name=item.get('name'),catalog_source=item['catalog_source'], behavioral_acceptance=False)
        try:
            selection = selection_for(item, annotated.get(rva), reviewed.get(rva), image, pe)
            entry.update(selection=selection, key=function_key(pipeline, state['module'], state['binary_sha256'], prefix, selection))
        except (ValueError, KeyError, TypeError) as error:
            entry.update(status='preparation_failed', stage='inventory', error=str(error))
        entries.append(entry)
    recomp.atomic_json(module_dir / 'ownership.json', dict(scope='Inventory-range overlap components, not accepted function ownership.', components=ownership_components(entries)))
    with (module_dir / 'catalog.jsonl').open('w') as stream:
        for entry in entries:
            stream.write(json.dumps(entry, separators=(',', ':')) + '\n')
    context = dict(role=role, module=state['module'], binary_sha256=state['binary_sha256'], module_prefix=prefix,
                   project=str(project), project_sha256=recomp.digest(recomp.encoded(state)), inventory=str(inventory_path),
                   inventory_sha256=recomp.digest(Path(inventory_path).read_bytes()), pipeline=pipeline, inventory_functions=len(inventory['functions']),
                   catalog_functions=len(entries),additional_selected_entries=len(entries)-len(inventory['functions']),
                   scope='Whole inventory hypotheses; no original-function or game acceptance.')
    recomp.atomic_json(module_dir / 'context.json', context)
    for name, data in [('project.json', recomp.encoded(state)), ('startup-role.json', recomp.encoded(startup))]:
        with gzip.open(module_dir / (name + '.gz'), 'wb') as stream:
            stream.write(data)
    counts = Counter()
    errors = Counter()
    examples = {}
    totals = Counter()
    candidates = [entry for entry in entries if 'selection' in entry]
    if args.limit is not None:
        candidates = candidates[:args.limit]
    selected = {entry['rva'] for entry in candidates}
    rows = module_dir / 'results.jsonl'
    with rows.open('w') as stream:
        for offset in range(0, len(entries), args.batch_size):
            group = entries[offset:offset + args.batch_size]
            missing = [item for item in group if item['rva'] in selected and not (cache / item['key'] / 'complete.json').exists()]
            if missing:
                if shutil.disk_usage(output).free < args.min_free_mb * 1024**2:
                    raise RuntimeError('generation stopped at free-space floor; completed shards retained')
                generate_batch(missing, state, prefix, cache, backend, descriptor, module_dir, args.batch_timeout, args.dispatch)
                recomp_storage.share_completed(cache,missing,args._artifact_content_index)
            for entry in group:
                row = {k: v for k, v in entry.items() if k != 'selection'}
                if 'selection' in entry and entry['rva'] not in selected:
                    row.update(status='not_attempted', stage='limit')
                elif 'selection' in entry:
                    location = cache if (cache / entry['key'] / 'complete.json').exists() else module_dir / 'unknown'
                    marker = load_shard(location, entry['key'], state['binary_sha256'], entry['rva'])
                    row.update(status=marker['status'], stage=marker.get('stage'), error_type=marker.get('error_type'), error=marker.get('error'))
                    if marker['status'] == 'generated_only':
                        facts = coverage(cache, entry['key'], entry['selection'], image, pe)
                        row['coverage'] = facts
                        for key in ('covered_inventory_bytes', 'owned_inventory_bytes', 'uncovered_inventory_bytes', 'indirect_jumps', 'unselected_call_continuations'):
                            totals[key] += facts[key]
                        counts['inventory_coverage_complete' if facts['uncovered_inventory_bytes'] == 0 else 'inventory_coverage_partial'] += 1
                counts[row['status']] += 1
                if row.get('error'):
                    key = (str(row.get('stage')), str(row.get('error_type')), normalize_error(row['error']))
                    errors[key] += 1
                    examples.setdefault(key, [])
                    if len(examples[key]) < 5:
                        examples[key].append(row['id'])
                stream.write(json.dumps(row, separators=(',', ':')) + '\n')
            stream.flush()
            progress = dict(**context, status='generating', processed=sum(counts[k] for k in ('generated_only', 'generation_failed', 'preparation_failed', 'interrupted_unknown', 'not_attempted')), counts=dict(counts), coverage_totals=dict(totals))
            recomp.atomic_json(module_dir / 'report.json', progress)
            if offset % (args.batch_size * 10) == 0:
                print(json.dumps(dict(module=role, processed=progress['processed'], total=len(entries), counts=dict(counts))), flush=True)
    recomp.checked_binary(state)
    progress.update(status='completed inventory generation attempt; not behavioral validation', failure_groups=[dict(stage=k[0], error_type=k[1], error=k[2], functions=count, examples=examples[k]) for k, count in errors.most_common()])
    recomp.atomic_json(module_dir / 'report.json', progress)
    return progress


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=recomp.ROOT / 'local/recomp/bulk')
    parser.add_argument('--role', choices=('main', 'umbra', 'all'), default='all')
    parser.add_argument('--batch-size', type=int, default=64)
    parser.add_argument('--batch-timeout', type=int, default=180)
    parser.add_argument('--min-free-mb', type=int, default=256)
    parser.add_argument('--limit', type=int, help='explicit probe limit; unattempted entries stay in the denominator')
    parser.add_argument('--dispatch', action='store_true')
    args = parser.parse_args(argv)
    if not 1 <= args.batch_size <= 512 or args.batch_timeout <= 0 or args.min_free_mb < 0 or (args.limit is not None and args.limit <= 0):
        parser.error('invalid batch/budget settings')
    output = args.output.absolute()
    output.mkdir(parents=True, exist_ok=True)
    with recomp.locked(output):
        pipeline, backend, descriptor = freeze_backend(output, args.dispatch)
        run_dir = output / 'runs' / str(time.time_ns())
        run_dir.mkdir(parents=True)
        startup = recomp.load(recomp.ROOT / 'recompiler/startup.json')
        report = dict(status='running', pipeline=pipeline, directory=str(run_dir), modules={}, behavioral_acceptance=False, game_acceptance=False)
        recomp.atomic_json(output / 'latest.json', report)
        try:
            for role in (('main', 'umbra') if args.role == 'all' else (args.role,)):
                report['modules'][role] = generate_module(role, DEFAULT_PROJECTS[role], DEFAULT_INVENTORIES[role], startup['roles'][role], output, pipeline, backend, descriptor, args, run_dir)
                recomp.atomic_json(output / 'latest.json', report)
            report['status'] = 'completed inventory generation attempt; compilation/runtime remain separate'
        except Exception as error:
            report.update(status='stopped; incomplete attempt', error=str(error))
            raise
        finally:
            recomp.atomic_json(run_dir / 'report.json', report)
            recomp.atomic_json(output / 'latest.json', report)
        print(json.dumps(dict(status=report['status'], directory=str(run_dir), counts={role: data['counts'] for role, data in report['modules'].items()}), indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

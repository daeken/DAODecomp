"""Freeze reviewed indexed-field support into existing paired recovery format.

Dry-run performs all reference/corpus consistency checks but cannot approve support.
No models, build, dispatch, source implementation or evidence promotion occurs here.
"""
import argparse
from collections import Counter
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.run_recovery_pair import check_manifest, digest, load, sha, write
from tools.daodecomp.leaf import load_slice
from validation.indexed_field_cases import FIELD_SPECS, NEGATIVE_NAMES, cases

GROUP = 'indexed-fields-002'
CANDIDATE = 'src/indexed_fields.cpp'
PIN = '2346caee611002d4dff6ecef68eb315b63a37004dd98b39c11a9c26c0b45bfb3'
EVIDENCE = 'local/pilots/memory-batch-003'
NAMES = tuple(FIELD_SPECS)
CORPUS_SUMMARY = f'{EVIDENCE}/indexed-fields-002-corpus-summary.json'
REVIEW_REQUIRED = {
    CORPUS_SUMMARY,
    'CMakeLists.txt', 'analysis/functions.json', 'include/dao/guest_memory.hpp',
    'include/dao/indexed_fields.hpp', 'validation/indexed_field_cases.py',
    'validation/indexed_field_runner.py', 'validation/indexed_field_native_runner.cpp',
    'validation/validate_indexed_fields.py', 'tools/freeze_indexed_fields_pair.py',
    'tools/validate_checkpoint.py', 'tools/daodecomp/memory.py', 'tools/daodecomp/harness.py',
    'tools/daodecomp/leaf.py', 'tools/daodecomp/pe.py', 'tests/test_indexed_fields.py',
    'tests/guest_memory_narrow.cpp', 'tests/indexed_field_mutant.cpp',
    'validation/indexed_field_mutant.hpp', 'contracts/indexed-fields-002.packet.json',
    *(f'contracts/functions/{name}.json' for name in NAMES),
    f'{EVIDENCE}/characterization.json', f'{EVIDENCE}/slices.txt',
    f'{EVIDENCE}/caller-contexts.json', f'{EVIDENCE}/evidence-hashes.json',
    *(f'{EVIDENCE}/{name}-{suite}-cases.json' for name in NAMES for suite in ('public', 'heldout')),
}


BATCH_REVIEW_REQUIRED = {
    'tools/incremental_checkpoint.py','tools/update_progress.py','tests/test_incremental_checkpoint.py','tests/test_incremental_batch_provider.py','tests/test_throughput_integration.py',
    'tools/daodecomp/batch.py', 'tools/run_recovery_pair.py', 'validation/indexed_field_batch_runner.py',
    'validation/indexed_field_batch_native.cpp', 'tests/test_batch.py',
    'tests/support/batch_fault_runner.py', 'docs/validation.md',
}


def review_required(execution='single'):
    if execution not in ('single', 'batch'):
        raise ValueError('unknown execution mode')
    return REVIEW_REQUIRED | (BATCH_REVIEW_REQUIRED if execution == 'batch' else set())


# Source-review prompt material is intentionally separate from acceptance hash coverage.
# Every exact corpus remains in REVIEW_REQUIRED and the manifest snapshot.
REVIEW_PROMPT_EVIDENCE = {
    CORPUS_SUMMARY, 'CMakeLists.txt', 'include/dao/guest_memory.hpp',
    'include/dao/indexed_fields.hpp', 'validation/indexed_field_cases.py',
    'validation/indexed_field_runner.py', 'validation/indexed_field_native_runner.cpp',
    'validation/indexed_field_mutant.hpp', 'validation/validate_indexed_fields.py',
    'tools/daodecomp/memory.py', 'tools/freeze_indexed_fields_pair.py',
    'tools/validate_checkpoint.py', 'tests/test_indexed_fields.py',
    'tests/guest_memory_narrow.cpp', 'tests/indexed_field_mutant.cpp',
    'contracts/indexed-fields-002.packet.json', f'{EVIDENCE}/characterization.json',
    f'{EVIDENCE}/slices.txt', f'{EVIDENCE}/caller-contexts.json',
}


def corpus_summary(root):
    """Derive compact observations from exact fixtures; no approval or pass claims."""
    result = {
        'schema_version': 1, 'kind': 'deterministic frozen-corpus coverage, not approval',
        'group': GROUP, 'reference_module_sha256': PIN,
        'hash_domains': {
            'raw_file_sha256': 'SHA-256 of exact file bytes including whitespace/newline',
            'canonical_json_sha256': "SHA-256(json.dumps(parsed_json, ensure_ascii=True, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8'))",
        },
        'derivation_source_raw_sha256': sha(root / 'tools/freeze_indexed_fields_pair.py'),
        'fixture_source_raw_sha256': sha(root / 'validation/indexed_field_cases.py'),
        'original_characterization_raw_sha256': sha(root / EVIDENCE / 'characterization.json'),
        'functions': [],
        'limitations': [
            'Coverage lists describe enumerated fixture inputs, not exhaustive state or semantic proof.',
            'Public and heldout cases were prepared by the same producer; summary is not independent acceptance.',
            'Heldout even-numbered cases force index=i%limit. For six-slot functions, even i only selects even indexes; the remaining accepted odd indexes depend on random odd-numbered states.',
            'Actual missing accepted indexes and forced-subset indexes are reported separately per function/suite without altering fixtures.',
            'One initialized512-byte ordinary-RAM arena, object offsets0..64; no second data pointer, concurrency, MMIO, faulting inputs, x87 or Windows caller integration.',
            'Original-only characterization and later acceptance reports have separate provenance; this summary does not assert their outcomes or approve a candidate.',
        ],
    }
    for name in NAMES:
        kind, field, width, limit = FIELD_SPECS[name]
        entry = {'name': name, 'operation': kind, 'field_offset': field,
                 'width_bytes': width, 'accepted_low_index_count': limit, 'suites': {}}
        for suite in ('public', 'heldout'):
            path = root / EVIDENCE / f'{name}-{suite}-cases.json'
            fixture_cases = load(path)
            if cases(name, suite) != fixture_cases:
                raise ValueError('summary input differs from exact frozen fixtures: ' + str(path))
            counts = Counter(c['inputs']['index'] & 255 for c in fixture_cases)
            accepted = [c for c in fixture_cases if (c['inputs']['index'] & 255) < limit]
            rejected = len(fixture_cases) - len(accepted)
            indexes = sorted({c['inputs']['index'] & 255 for c in accepted})
            objects = {c['inputs']['object'] for c in fixture_cases}
            forced = [c for i, c in enumerate(fixture_cases) if suite == 'heldout' and i % 2 == 0]
            forced_indexes = sorted({c['inputs']['index'] & 255 for c in forced})
            field_values = []
            for c in accepted:
                inputs = c['inputs']
                if kind == 'set':
                    field_values.append(inputs['value'] & ((1 << (width * 8)) - 1))
                else:
                    at = inputs['object'] + field + width * (inputs['index'] & 255)
                    field_values.append(int.from_bytes(bytes.fromhex(inputs['arena'])[at:at+width], 'little'))
            entry['suites'][suite] = {
                'path': path.relative_to(root).as_posix(), 'raw_file_sha256': sha(path),
                'canonical_json_sha256': digest(fixture_cases), 'case_count': len(fixture_cases),
                'case_id_prefix': suite + '-', 'accepted_case_count': len(accepted),
                'rejected_case_count': rejected, 'distinct_index_low_bytes': len(counts),
                'accepted_indexes_present': indexes,
                'accepted_indexes_missing': sorted(set(range(limit)) - set(indexes)),
                'accepted_index_case_counts': {str(k): counts[k] for k in range(limit)},
                'forced_even_heldout_case_count': len(forced),
                'forced_even_heldout_indexes_present': forced_indexes,
                'forced_even_heldout_indexes_missing': sorted(set(range(limit)) - set(forced_indexes)) if forced else [],
                'object_offset_range': [min(objects), max(objects)],
                'distinct_object_offsets': len(objects),
                'distinct_object_alignments_mod4': len({v % 4 for v in objects}),
                'distinct_incoming_eax_upper24_patterns': len({c['inputs']['entry_eax'] >> 8 for c in fixture_cases}),
                'distinct_high_index24_patterns': len({c['inputs']['index'] >> 8 for c in fixture_cases}),
                'distinct_accepted_field_bit_patterns': len(set(field_values)),
                'accepted_zero_field_cases': field_values.count(0),
                'accepted_all_ones_field_cases': field_values.count((1 << (width * 8)) - 1),
            }
        result['functions'].append(entry)
    result['total_cases'] = {suite: sum(f['suites'][suite]['case_count'] for f in result['functions'])
                             for suite in ('public', 'heldout')}
    return result


def verify_corpus_summary(root):
    if load(root / CORPUS_SUMMARY) != corpus_summary(root):
        raise ValueError('corpus coverage summary is stale or inconsistent')


def prompt_evidence(review_rel, execution="single"):
    # A real independent review is always included. Its hash coverage remains complete.
    review_required(execution)
    return sorted(REVIEW_PROMPT_EVIDENCE | {review_rel} | (BATCH_REVIEW_REQUIRED if execution == "batch" else set()))


def required_files(root, execution="single"):
    files = set(review_required(execution))
    # Explicit snapshot closure includes all CMake tests/sources, unlike the prior missing-test failure.
    for folder, patterns in [('src', ('*.cpp',)), ('include', ('*.hpp',)),
                             ('validation', ('*.py', '*.cpp', '*.hpp')), ('tools', ('*.py',)),
                             ('tests', ('*.py', '*.cpp')), ('examples/synthetic', ('*.py', '*.cpp', '*.json')),
                             ('contracts/functions', ('*.json',))]:
        for pattern in patterns:
            files.update(p.relative_to(root).as_posix() for p in (root / folder).rglob(pattern))
    files.update(('.githooks/pre-commit', 'analysis/reference-build.json', 'requirements-validation.txt', 'README.md',
                  'docs/paired-recovery.md'))
    return sorted(files - {CANDIDATE})


def verify_inputs(root, binary):
    source = load(root / EVIDENCE / 'characterization.json')
    hashes = load(root / EVIDENCE / 'evidence-hashes.json')
    if sha(binary) != PIN or source['binary_sha256'] != PIN:
        raise ValueError('wrong original binary')
    registry = load(root / 'analysis/functions.json')
    originals = {f['name']: f for f in source['functions']}
    rows = []
    for name in NAMES:
        original = originals[name]
        row = next(f for f in registry['functions'] if f['name'] == name)
        if (row['backend'] != 'indexed-stores-001' or row.get('recovery_group') != GROUP
                or row['source'] != CANDIDATE or row['module_sha256'] != PIN
                or row['status'] not in ('contracted', 'implemented', 'corpus_pass', 'reviewed', 'integrated')):
            raise ValueError('wrong proposed registry domain/status')
        for key in ('size', 'code_sha256'):
            if row[key] != original[key]:
                raise ValueError('registry/slice identity mismatch')
        if row['rva'] != int(original['rva'], 16):
            raise ValueError('RVA mismatch')
        load_slice(binary, PIN, row['rva'], row['size'], row['code_sha256'])
        contract = load(root / row['contract'])
        kind = FIELD_SPECS[name][0]
        inputs = dict(arena='bytes', object='u32', index='u32', entry_eax='u32')
        if kind == 'set':
            inputs['value'] = 'u32'
        if (contract['function_id'] != row['id'] or contract['inputs'] != inputs
                or contract['memory'] != {'arena': 512} or contract['return_type'] != 'u32'
                or contract['calls'] != []):
            raise ValueError('contract interface mismatch')
        for suite in ('public', 'heldout'):
            filename = f'{name}-{suite}-cases.json'
            path = root / EVIDENCE / filename
            if sha(path) != hashes[filename] or cases(name, suite) != load(path):
                raise ValueError('characterized corpus changed: ' + filename)
        rows.append(row)
    return rows


def approved_review(root, report_path, execution="single"):
    report = load(report_path)
    if report.get('decision') not in ('approve', 'approve_current_bounded_domain', 'approved_for_current_bounded_domain'):
        raise ValueError('independent acceptance review has not approved support')
    reviewed = report.get('reviewed_artifacts_sha256', {})
    if not review_required(execution) <= reviewed.keys():
        raise ValueError('review lacks required support/contract/corpus hash coverage')
    for name, expected in reviewed.items():
        # Reject traversal/symlinks using the same coordinator trust-boundary helper.
        from tools.run_recovery_pair import checked_file
        if sha(checked_file(root, name)) != expected:
            raise ValueError('reviewed input changed: ' + name)
    return report


def commands(execution="single"):
    review_required(execution)
    build = [dict(argv=['cmake', '-S', '{tree}', '-B', '{build}', '-DCMAKE_BUILD_TYPE=RelWithDebInfo', '-DPython3_EXECUTABLE={python}'], timeout_seconds=120, reports=[]),
             dict(argv=['cmake', '--build', '{build}', '--parallel', '2'], timeout_seconds=180, reports=[]),
             dict(argv=['{python}', '-m', 'unittest', 'discover', '-s', 'tests', '-v'], timeout_seconds=300, reports=[]),
             dict(argv=['ctest', '--test-dir', '{build}', '--output-on-failure'], timeout_seconds=300, reports=[])]
    for extra in ([], ['--expect-mismatch']):
        build.append(dict(argv=['{python}', '{tree}/examples/synthetic/demo.py', '--build-dir', '{build}', *extra], timeout_seconds=120, reports=[]))
    build.append(dict(argv=['{python}', '-c', "import pathlib,shutil,sys; d=pathlib.Path(sys.argv[2]); d.mkdir(parents=True,exist_ok=True); [shutil.copyfile(pathlib.Path(sys.argv[1])/n,d/n) for n in ('synthetic.json','synthetic-mutant.json','synthetic-cases.json')]", '{tree}/reports', '{report_dir}/synthetic'], timeout_seconds=10, reports=[]))
    stages = dict(build=build)
    for stage in ('public', 'heldout', 'negative'):
        names = NEGATIVE_NAMES if stage == 'negative' else NAMES
        suite = 'heldout' if stage == 'heldout' else 'public'
        suffix = '-mutant' if stage == 'negative' else '-' + suite
        argv = ['{python}', '{tree}/validation/validate_indexed_fields.py', '--binary', '{binary}', '--build-dir', '{build}', '--report-dir', '{report_dir}', '--suite', suite, '--jobs', '2']
        if execution == 'batch':
            argv += ['--execution', 'batch']
        if stage == 'negative':
            argv.append('--expect-mismatch')
        stages[stage] = [dict(argv=argv, timeout_seconds=3600, reports=[dict(path=name+suffix+'.json', function=name, corpus=suite, expect='mismatch' if stage == 'negative' else 'pass') for name in names])]
    return stages


def packet_text(root, rows):
    text = ['Implement exactly eleven pinned integer indexed-field helpers as C++20. Only src/indexed_fields.cpp is writable. Return one complete source; use namespace dao and include dao/indexed_fields.hpp. Do not use tools, models, agents or external files; no recovered implementation exists yet.',
            'Follow actual original instructions and exact contracts. Guest offsets are never host pointers. All 32 return bits matter, including upper incoming EAX bits on rejected byte/word getters and setters. Use only exact-width GuestMemory methods. No widening narrow reads/writes, no host aliasing casts, no fabricated original names or success stubs.',
            'This is isolated ordinary RAM with object offsets0..64 in a512-byte arena. The original preserves ECX/nonvolatile registers, stack balance and DF. Other volatile registers/flags are excluded at this high-level mapping; no binary ABI bridge or parent-caller equivalence is asserted.',
            (root / 'include/dao/guest_memory.hpp').read_text(), (root / 'include/dao/indexed_fields.hpp').read_text(),
            'Complete original slice decoding and instruction bytes (original labels unknown):\n' + (root / EVIDENCE / 'slices.txt').read_text(),
            'Observed direct caller contexts:\n' + (root / EVIDENCE / 'caller-contexts.json').read_text()]
    for row in rows:
        text += [row['id']+' slice SHA256 '+row['code_sha256'], (root / row['contract']).read_text()]
    text += ['No heldout cases/outcomes supplied. Do not edit support, oracle, comparator, fixtures, headers or acceptance. Return function notes using exact function names, source, and remaining uncertainties.']
    return '\n\n'.join(text)+'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--execution', choices=('single','batch'), default='single',
                        help='Opt into reviewed fresh-child batching for all three deterministic gates')
    parser.add_argument('--write-review-summary', action='store_true',
                        help='derive/update compact ignored coverage artifact; does not approve or freeze')
    parser.add_argument('--label', default='freeze-1')
    parser.add_argument('--review-report', type=Path)
    parser.add_argument('--binary', type=Path, default=ROOT / 'gamedata/bin_ship/DAOrigins.exe')
    args = parser.parse_args()
    if not re.fullmatch('[a-z0-9][a-z0-9-]{0,39}', args.label):
        parser.error('invalid freeze label')
    if args.write_review_summary:
        write(ROOT / CORPUS_SUMMARY, corpus_summary(ROOT))
    verify_corpus_summary(ROOT)
    support = required_files(ROOT, args.execution)
    if any(not (ROOT / name).is_file() for name in support):
        parser.error('missing protected support')
    rows = verify_inputs(ROOT, args.binary)
    if not args.freeze:
        print(json.dumps(dict(status='review-preparation-only-not-frozen', functions=len(rows), support_files=support, execution=args.execution, commands=commands(args.execution), review_required_sha256={name:sha(ROOT/name) for name in sorted(review_required(args.execution))}, model_requests=0), indent=2))
        return 0
    if args.review_report is None:
        parser.error('--freeze requires independent --review-report')
    if any(row['status'] != 'contracted' for row in rows):
        parser.error('freeze requires unimplemented contracted batch')
    approved_review(ROOT, args.review_report, args.execution)
    review_rel = args.review_report.resolve().relative_to(ROOT).as_posix()
    destination = ROOT / f'local/pairs/{GROUP}-{args.label}'
    manifest_path = ROOT / f'local/pairs/{GROUP}-{args.label}-manifest.json'
    if destination.exists() or manifest_path.exists():
        parser.error('freeze destination exists; preserve prior outputs')
    destination.mkdir(parents=True)
    packet = destination / 'packet.txt';packet.write_text(packet_text(ROOT, rows))
    declared = []
    for row in rows:
        corpora = {}
        for suite in ('public', 'heldout'):
            name = f'{row["name"]}-{suite}.json'
            dest = destination / name
            shutil.copyfile(ROOT / EVIDENCE / f'{row["name"]}-{suite}-cases.json', dest)
            corpora[suite] = dest.relative_to(ROOT).as_posix()
        declared.append(dict(name=row['name'],id=row['id'],contract=row['contract'],corpora=corpora))
    support += [review_rel, packet.relative_to(ROOT).as_posix(), *[path for f in declared for path in f['corpora'].values()]]
    manifest = dict(schema_version=1,group=GROUP,packet=packet.relative_to(ROOT).as_posix(),candidate=CANDIDATE,functions=declared,snapshot={name:sha(ROOT/name) for name in sorted(set(support))},reference=dict(path=str(args.binary.resolve()),sha256=PIN),commands=commands(args.execution),review_evidence=prompt_evidence(review_rel,args.execution))
    check_manifest(manifest, ROOT)
    write(manifest_path, manifest)
    print(json.dumps(dict(status='frozen-not-dispatched', manifest=str(manifest_path), manifest_sha256=sha(manifest_path), model_requests=0)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

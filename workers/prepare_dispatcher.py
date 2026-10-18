"""Freeze the current startup queue and reviewed background packet, without requests.

Creates no approval and does not initialize/reset the existing provider ledger.
The independent controller reviewer must approve the exact resulting config.
"""
import argparse
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recovery_dispatcher import atomic, bound, digest, load, regular, require


def prepare(root, destination):
    root, destination = root.resolve(), destination.absolute()
    require(destination.is_relative_to(root / 'local') and not destination.exists(),
            'new ignored controller directory required')
    destination.mkdir(parents=True)
    startup = root / 'local/pilots/startup-windows-001'
    seed = load(startup / 'frontier-proposal.json')
    hashes = load(startup / 'artifact-hashes.json')
    for name, expected in hashes['output_sha256'].items():
        bound(root / name, expected)
    require(digest(root / 'gamedata/bin_ship/DAOrigins.exe') == seed['module_sha256'], 'wrong pinned original')
    reference = {'path': str(root / 'gamedata/bin_ship/DAOrigins.exe'),
                 'module': seed['module'], 'sha256': seed['module_sha256']}
    sections = re.split(r'\n(?=RVA [0-9a-f]{8} )', (startup / 'selected-disassembly.txt').read_text())
    by_rva = {re.match(r'\s*RVA ([0-9a-f]{8}) ', section).group(1): section
              for section in sections if re.match(r'\s*RVA ([0-9a-f]{8}) ', section)}
    tasks = []
    units = [{'id': 'loader-capture', 'functions': [], 'bounded_depth': 0,
              'objective': seed['loader_capture_scope']['task'],
              'body_ranges': {}, 'windows_milestone': 'M1: original normal-loader capture through probable WinMain'}]
    units += seed['units_in_priority_order']
    for n, unit in enumerate(units):
        context_dir = destination / 'context' / unit['id']
        context_dir.mkdir(parents=True)
        atomic(context_dir / 'unit.json', unit)
        if unit['id'] == 'loader-capture':
            selected = '\n'.join(by_rva[r] for r in ['004e3024', '004f4907', '004e2e44', '00016ad0'])
        else:
            selected = '\n'.join(by_rva.get(f['rva'], 'Instruction listing absent for RVA ' + f['rva'] +
                '; ranges/hash/edge context only. Missing instruction semantics stay unknown.') for f in unit['functions'])
        (context_dir / 'instructions.txt').write_text(selected)
        context = [context_dir / 'unit.json', context_dir / 'instructions.txt',
                   startup / 'handoff.md', root / 'AGENTS.md', root / 'docs/validation.md',
                   root / 'docs/windows-reference.md']
        inputs = {str(p): digest(p) for p in context}
        inputs[str(startup / 'frontier-proposal.json')] = digest(startup / 'frontier-proposal.json')
        objective = unit.get('objective', 'Prepare bounded characterization and frozen-support proposal for unit ' + unit['id'] +
                             '. Prioritize its Windows startup milestone and exact observed dependencies. '
                             'Do not adopt guessed contracts; preserve unresolved evidence and measured continuation.')
        task = {'id': unit['id'], 'kind': 'startup-preparation', 'priority': n,
                'functions': [f['id'] for f in unit['functions']], 'depth': 0,
                'body_ranges': {f['id']: [[r['start_rva'], r['end_rva_inclusive']]
                                          for r in f['body_ranges_hypothesis']] for f in unit['functions']},
                'objective': objective, 'inputs': inputs, 'context': [str(p) for p in context],
                'depends_on': [], 'implementation_dependencies': unit.get('depends_on_units', [])}
        tasks.append(task)
    packet_dir = root / 'local/pilots/memory-batch-007/packet-v1'
    manifest_path = packet_dir / 'run/manifest.json'
    manifest = load(manifest_path)
    background_inputs = {str(manifest_path): digest(manifest_path)}
    tree = packet_dir / 'tree'
    for name, expected in manifest['snapshot'].items():
        background_inputs[str(bound(tree / name, expected))] = expected
    for path, expected in [
        (root / 'workers/deepseek_packet.py', '730060709990324e7d25e473b36397169ff46e011d21055b3d042353858d9282'),
        (packet_dir / 'review/acceptance-review.json', '9c3ca09486c795915ee6a3493ed225b3b0632e89005b8ff116885d7b99219272'),
        (packet_dir / 'full-proposal.patch', 'f2318db89d727c0f5a4c17cde583ff0f60200d7c7791ff9cf3d4551bb0e5e559'),
        (root / 'local/pilots/direct-field-extensibility-001/review/acceptance-review.json',
         '5375c82e4cca6412f3087efaec9f2d1ae39ab5a4933cd6b71339f93d33d95062')]:
        background_inputs[str(bound(path, expected))] = expected
    support_review_path = packet_dir / 'review/acceptance-review.json'
    support_review = load(support_review_path)
    compatibility_review = load(root / 'local/pilots/direct-field-extensibility-001/review/acceptance-review.json')
    changed = {row['path'] for row in load(packet_dir / 'changed-paths.json')}
    changed.update(compatibility_review['reviewed_artifacts_sha256'])
    promotion_files, approved_artifacts = {}, {}
    for name in sorted(changed):
        source = tree / name
        expected = support_review['reviewed_artifacts_sha256'][name]
        bound(source, expected)
        current = root / name
        current_sha = digest(current) if current.is_file() else None
        if current_sha == expected:
            continue
        promotion_files[name] = {'source': str(source), 'sha256': expected, 'base_sha256': current_sha}
        approved_artifacts[name] = expected
    target = manifest['candidate']
    promotion_files[target] = {'source': 'accepted-candidate', 'sha256': None,
                               'base_sha256': digest(root / target)}
    # Preserve the exact independently reviewed Windows publication-key repair
    # when composing the older93-function support tree. This is a proposal-only
    # override for the forthcoming controller review, not a frozen packet edit.
    fixture_name = 'tests/test_direct_field_publication_data.py'
    original = (tree / fixture_name).read_text()
    needle = 'source=cache.source_manifest(root),registry_sha256='
    require(original.count(needle) == 1, 'unexpected promotion fixture structure')
    replacement = 'source={Path(rel).as_posix():digest for rel,digest in cache.source_manifest(root).items()},registry_sha256='
    repaired = original.replace(needle, replacement)
    override = destination / 'promotion-overrides' / fixture_name
    override.parent.mkdir(parents=True)
    override.write_text(repaired)
    compile(repaired, fixture_name, 'exec')
    promotion_files[fixture_name] = {'source': str(override), 'sha256': digest(override),
                                     'base_sha256': digest(root / fixture_name)}
    background_inputs[str(override)] = digest(override)
    archive = root / 'analysis/validation/direct-object-fields-001.json'
    promotion = {'base_commit': None, 'files': promotion_files,
                 'support_review_artifacts': approved_artifacts,
                 'review': str(support_review_path), 'review_sha256': digest(support_review_path),
                 'archive_records': {archive.relative_to(root).as_posix(): digest(archive)}}
    sys.path.insert(0, str(root))
    from tools.incremental_checkpoint import publication_inventory
    import hashlib, json
    inventory = sorted(publication_inventory())
    require(len(inventory) == 117 and sum(not negative for _, negative in inventory) == 69,
            'deferred producer requires exact current69+48 inventory')
    promotion['deferred_checkpoint'] = {
        'path': 'analysis/validation/direct-object-fields-ci-001.json',
        'producer_attestation': 'reports/checkpoint-direct-object-fields-ci-001/reuse-attestation.json',
        'registry_sha256': digest(root / 'analysis/functions.json'),
        'inventory_sha256': hashlib.sha256(json.dumps(inventory, separators=(',', ':')).encode()).hexdigest()}
    tasks.append({'id': 'ready24-direct-fields', 'kind': 'frozen-packet',
                  # Second lane gets this frozen independent job while lane one
                  # begins loader preparation; later startup work keeps priority.
                  'priority': 0, 'functions': [f['id'] for f in manifest['functions']],
                  'root': str(tree), 'manifest': str(manifest_path), 'manifest_sha256': digest(manifest_path),
                  'inputs': background_inputs, 'depends_on': [],
                  'preserved_prefix': {'path': str(tree / 'evidence/accepted-direct-object-fields-prefix.txt'),
                                       'sha256': digest(tree / 'evidence/accepted-direct-object-fields-prefix.txt')},
                  'promotion': promotion,
                  'new_functions': 24, 'existing_functions_preserved': 22})
    trusted = ['workers/recovery_dispatcher.py', 'workers/prepare_dispatcher.py',
               'workers/deepseek_packet.py', 'tools/run_recovery_pair.py', 'tools/run_model_packet.py']
    config = {'schema_version': 1, 'root': str(root), 'python': str(root / '.venv/bin/python'),
              'ledger': str(root / 'local/providers/deepseek-daily'),
              'cmake_bin': '/opt/homebrew/Cellar/cmake/4.2.0/bin',
              'publication_code': {p: digest(root / p) for p in ['tools/incremental_checkpoint.py', 'tools/update_progress.py']},
              'trusted_code': {p: digest(root / p) for p in trusted}, 'reference': reference,
              'opening_model_requests': 2,
              'opening_model_request_evidence': 'Director opening debit: setup agent and planned independent controller reviewer, 2026-10-18 activation; no other requests dispatched.',
              'checkpoint_barriers': [{'record': str(root / 'analysis/validation/direct-object-fields-001.json')}],
              'max_depth': 3, 'tasks': tasks}
    config['controller_reviewed_overrides'] = {fixture_name: digest(override)}
    atomic(destination / 'config.json', config)
    atomic(destination / 'request-adjustments/windows-ci-fixture.json', {
        'id': 'windows-ci-fixture', 'count': 1,
        'evidence': 'Director authorized an additional Windows CI fixture repair agent during setup; conservatively charged before continuous launch.'})
    atomic(destination / 'review-request.json', {'decision': 'pending',
           'config_sha256': digest(destination / 'config.json'), 'trusted_code': config['trusted_code'],
           'scope': 'Review exact dispatcher, seed builder, tests and configuration before runtime launch; no approval fabricated.'})
    return config


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--state-dir', type=Path, required=True)
    args = parser.parse_args()
    prepare(args.root, args.state_dir)

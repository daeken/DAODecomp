"""Opt-in local per-backend reuse; never imports legacy reports into the cache.

Every invocation clean-builds and runs infrastructure gates. Cache entries originate
only from a successful execution by this driver under the same current identity.
Historical comparison reports stay immutable; a new reuse attestation names both
historical comparison inputs and current build/source provenance. No v1 backfill.
"""
import argparse
import ctypes
import hashlib
import importlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import sysconfig
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import validate_checkpoint as checkpoint
from tools.record_validation import record_report

VERSION = 2
POLICY = 'clean-build-local-groups-003'
GROUPS = {
    'scalar': ('scalar', 'dao_leaf'),
    'memory': ('memory', 'dao_memory'),
    'object_counters': ('object-counters', 'dao_object_counter'),
    'indexed_stores': ('indexed-stores', 'dao_indexed_store'),
    'indexed_fields': ('indexed-fields', 'dao_indexed_field'),
    'linked_structures': ('linked-structures', 'dao_linked_structure'),
    'object_bitfields': ('object-bitfields', 'dao_object_bitfield'),
    'direct_object_fields': ('direct-object-fields', 'dao_direct_object_field'),
}
LEGACY_GROUPS = tuple(g for g in GROUPS if g not in {'object_bitfields','direct_object_fields'})
BATCH_IMAGES = {'indexed_fields':'dao_indexed_field_batch', 'object_bitfields':'dao_object_bitfield_batch', 'direct_object_fields':'dao_direct_object_field_batch'}
# Exact existing report dependency from validate_linked_structures.py; no tests/* rule.
DECLARED_VALIDATION_DEPENDENCIES = {
    'linked_structures': ('tests/test_linked_structures.py',),
}
ACTIVE = {'implemented', 'corpus_pass', 'reviewed', 'integrated'}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def files_manifest(paths):
    result = {}
    for path in sorted(set(map(Path, paths))):
        if path.is_symlink() or not path.is_file():
            raise ValueError(f'missing artifact: {path}')
        result[str(path.absolute())] = file_hash(path)
    return result



def resolved_provider_files(paths):
    """Hash resolved runtime providers while binding every original lookup path."""
    paths = tuple(map(Path, paths))
    bindings = {str(p.absolute()): str(p.resolve(strict=True)) for p in paths}
    files = files_manifest(Path(target) for target in bindings.values())
    if bindings != {str(p.absolute()): str(p.resolve(strict=True)) for p in paths}:
        raise ValueError('runtime provider resolution changed during hashing')
    return files, bindings


def source_manifest(root):
    # Membership is hashed, including newly added files. No inferred TU narrowing.
    paths = [root / 'CMakeLists.txt', root / 'requirements-validation.txt',
             root / 'analysis/reference-build.json']
    for name in ('src', 'include', 'tools', 'validation', 'contracts', 'examples', 'tests'):
        paths += [p for p in (root / name).rglob('*') if p.is_file()
                  and '__pycache__' not in p.parts and p.suffix != '.pyc']
    current = {str(Path(p).relative_to(root)): file_hash(p) for p in sorted(set(paths))}
    registry = root/'analysis/functions.json'
    if registry.is_file():
        direct = [f for f in json.loads(registry.read_text()).get('functions', [])
                  if f.get('status') in ACTIVE and f.get('backend') == 'direct-object-fields-001']
        if direct:
            # Public deterministic fixtures/reference metadata; private packet
            # copies, captures and original binaries remain excluded below local/.
            selected = [root/'slices.json',
                        *[root/f"corpus/{f['name']}-{suite}.json"
                          for f in direct for suite in ('public','heldout')]]
            current.update({Path(p).relative_to(root).as_posix(): value
                            for p, value in files_manifest(selected).items()})
    return current


# These two variables describe the shell/tool invocation, not guest execution.
# Supported groups are call-free integer/memory adapters; validation uses no shell.
# Every other variable (including all loader, Python, locale and path settings)
# stays keyed. Full excluded-variable provenance is retained hash-only outside keys.
INVOCATION_METADATA = {'CODEX_TOOL_CALL_ID', 'SHLVL'}


def environment_identity(environ):
    return digest({key: value for key, value in environ.items() if key not in INVOCATION_METADATA})


def invocation_environment(environ):
    return {'full_sha256': digest(dict(environ)),
            'excluded_sha256': {key: hashlib.sha256(environ[key].encode()).hexdigest()
                               for key in sorted(INVOCATION_METADATA) if key in environ}}


def provider_inventory(directories, inactive_links=()):
    """Keep provider path membership and symlink resolution, including directories."""
    roots = {Path(d).resolve(strict=True) for d in directories}
    inactive = {Path(p).absolute() for p in inactive_links}
    paths, membership = [], {}
    for directory in sorted(map(Path, directories)):
        if not directory.is_dir():
            raise ValueError(f'unknown Python provider: {directory}')
        for path in [directory, *directory.rglob('*')]:
            if '__pycache__' in path.parts or path.suffix == '.pyc':
                continue
            target = path.resolve(strict=True)
            if path.is_symlink() and path.is_dir() and not any(target == r or r in target.parents for r in roots):
                if path.absolute() not in inactive:
                    raise ValueError(f'unknown linked Python provider: {path}')
            kind = 'directory' if path.is_dir() else 'file' if path.is_file() else 'unknown'
            if kind == 'unknown':
                raise ValueError(f'unsupported Python provider member: {path}')
            membership[str(path.absolute())] = {'kind': kind, 'resolved': str(target)}
            if path.is_file():
                paths.append(path)
    return paths, membership


def runtime_manifest():
    """Closed, deliberately broad local macOS provider; unsupported hosts rerun.

    Python stdlib and installed packages include .pth/startup providers and actual
    resolved libunicorn. All current dyld shared-cache members are rehashed.
    Environment and loader image membership are part of identity. Unknown images
    outside the on-disk closure fail closed. Never trusts a version string alone.
    """
    if sys.platform != 'darwin':
        raise ValueError('runtime provider supports macOS only; rerun without reuse')
    host = platform.platform()  # Resolve lazy platform providers before image inventory.
    unicorn = importlib.import_module('unicorn.unicorn_py3.unicorn')
    native = Path(unicorn.uclib._name).resolve(strict=True)
    paths = [Path(sys.executable).resolve(), native]
    directories = {Path(sysconfig.get_path(key)) for key in ('stdlib', 'purelib', 'platlib')}
    # A venv's inactive base-site link is not an execution search provider.
    base_site = Path(sysconfig.get_path('stdlib'))/'site-packages'
    inactive = [base_site] if base_site.resolve() not in {Path(v or os.getcwd()).resolve() for v in sys.path} else []
    provider_paths, membership = provider_inventory(directories, inactive)
    paths.extend(provider_paths)
    cache = Path('/System/Volumes/Preboot/Cryptexes/OS/System/Library/dyld')
    caches = sorted(cache.glob('dyld_shared_cache_*'))
    if not caches:
        raise ValueError('missing dyld shared cache provider')
    paths.extend(caches)
    cache_members = set()
    for mapping in cache.glob('*.map'):
        cache_members.update(line.strip() for line in mapping.read_text().splitlines() if line.startswith('/'))
    if not cache_members:
        raise ValueError('missing dyld cache image membership')
    dyld = ctypes.CDLL(None)
    dyld._dyld_image_count.restype = ctypes.c_uint32
    dyld._dyld_get_image_name.argtypes = [ctypes.c_uint32]
    dyld._dyld_get_image_name.restype = ctypes.c_char_p
    images = []
    for index in range(dyld._dyld_image_count()):
        name = dyld._dyld_get_image_name(index).decode()
        images.append(name)
        path = Path(name)
        if path.is_file():
            paths.append(path)
        elif name not in cache_members:
            raise ValueError(f'unresolved loader image: {name}')
    known = {ROOT.resolve(), Path(sysconfig.get_path('stdlib')).resolve(),
             Path(sysconfig.get_path('purelib')).resolve(), Path(sysconfig.get_path('platlib')).resolve()}
    for name in sys.path:
        path = Path(name or os.getcwd()).resolve()
        if path.exists() and path not in known and not any(p in path.parents for p in known):
            raise ValueError(f'unknown Python search provider: {path}')
    # Candidate subprocesses inherit this exact environment. External Python path
    # providers cannot be quietly omitted from the closed package inventory.
    if any(os.environ.get(k) for k in ('PYTHONPATH', 'PYTHONHOME', 'PYTHONSTARTUP',
                                      'DYLD_INSERT_LIBRARIES', 'DYLD_LIBRARY_PATH',
                                      'DYLD_FRAMEWORK_PATH')):
        raise ValueError('unsupported dynamic runtime provider environment')
    runtime_files, resolutions = resolved_provider_files(paths)
    for path in provider_paths:
        if membership[str(path.absolute())]['resolved'] != resolutions[str(path.absolute())]:
            raise ValueError('Python provider resolution changed during inventory')
    return {'provider': 'macos-full-python-dyld-v1', 'files': runtime_files,
            'loaded_images': images, 'actual_libunicorn': str(native),
            'host': host, 'sys_path': list(sys.path), 'provider_membership': membership,
            'resolution_bindings': resolutions,
            'environment_sha256': environment_identity(os.environ)}


def native_dependencies(executables):
    """Resolve linked native providers; unknown rpath/install names disable reuse."""
    cache_dir = Path('/System/Volumes/Preboot/Cryptexes/OS/System/Library/dyld')
    members = set()
    for mapping in cache_dir.glob('*.map'):
        members.update(line.strip() for line in mapping.read_text().splitlines() if line.startswith('/'))
    initial = {Path(p).resolve() for p in executables}
    pending = list(map(Path, executables))
    found = set()
    bindings = {}
    while pending:
        binary = pending.pop().resolve(strict=True)
        if binary in found:
            continue
        found.add(binary)
        output = subprocess.check_output(['otool', '-L', str(binary)], text=True)
        install_id = None
        if binary.suffix == '.dylib':
            ids = subprocess.check_output(['otool', '-D', str(binary)], text=True).splitlines()[1:]
            if len(ids) != 1:
                raise ValueError(f'unknown Mach-O install identity: {binary}')
            install_id = ids[0].strip()
        for line in output.splitlines()[1:]:
            name = line.strip().split(' (', 1)[0]
            if name == install_id:
                continue  # LC_ID_DYLIB identifies this hashed image, not a load dependency.
            if name in members:
                continue  # Covered by the freshly hashed complete dyld cache.
            if not name.startswith('/'):
                raise ValueError(f'unsupported native dependency provider: {name}')
            dependency = Path(name)
            bindings[name] = str(dependency.resolve(strict=True))
            if dependency != binary:
                pending.append(dependency)
    return {'files': files_manifest(found - initial), 'bindings': bindings}


OWNER_FILE = '.incremental-build-owner.json'


def owner_document(root, build):
    return {'schema_version': 1, 'policy': POLICY, 'source_root': str(root.resolve()),
            'build_root': str(build.absolute())}


def prepare_build(root, build):
    # Ownership is never inferred from a CMakeCache or a directory name alone.
    if build.is_symlink() or build.parent != root or not build.name.startswith('build-incremental'):
        raise ValueError('use a dedicated direct-child build-incremental* directory; symlinks are forbidden')
    expected = owner_document(root, build)
    if build.exists():
        try:
            marker = build/OWNER_FILE
            if marker.is_symlink() or json.loads(marker.read_text()) != expected:
                raise ValueError('build directory is not owned by this tool')
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError('refusing to clear an unowned build directory') from exc
        shutil.rmtree(build)
    build.mkdir()
    (build/OWNER_FILE).write_text(json.dumps(expected, sort_keys=True)+'\n')


def build_provenance(build):
    files = [p for p in build.rglob('*') if p.is_file()]
    result = {'files': files_manifest(files),
              'resolution_bindings': {str(p.absolute()): str(p.resolve()) for p in files}}
    cache_entries = {}
    for line in (build/'CMakeCache.txt').read_text().splitlines():
        if '=' in line and ':' in line.split('=', 1)[0]:
            name, value = line.split('=', 1)
            cache_entries[name.split(':', 1)[0]] = value
    tools = [cache_entries[name] for name in ('CMAKE_CXX_COMPILER', 'CMAKE_LINKER', 'CMAKE_MAKE_PROGRAM')]
    cmake = shutil.which('cmake')
    if cmake is None:
        raise ValueError('unknown CMake provider')
    result['invoked_build_tools'] = files_manifest([*tools, cmake])
    return result


def current_runtime(build):
    # Build provenance is deliberately outside the reusable execution identity.
    return runtime_manifest()


def selected_entries(registry, group):
    if registry.get('schema_version') != 1:
        raise ValueError('unsupported registry version')
    functions = registry['functions']
    for key in ('id', 'name'):
        values = [f[key] for f in functions]
        if len(values) != len(set(values)):
            raise ValueError(f'ambiguous registry {key}')
    def route(f):
        backend = f.get('backend', 'scalar')
        if backend == 'indexed-stores-001':
            return 'indexed_fields' if f.get('recovery_group') == 'indexed-fields-002' else 'indexed_stores'
        return {'scalar': 'scalar', 'memory-001': 'memory',
                'object-counters-001': 'object_counters',
                'linked-structures-001': 'linked_structures',
                'object-bitfields-001':'object_bitfields',
                'direct-object-fields-001':'direct_object_fields'}.get(backend)
    for function in functions:
        if function.get('status') in ACTIVE and route(function) is None:
            raise ValueError('unsupported registry routing')
    object_rows = [f for f in functions if f.get('status') in ACTIVE and route(f) == 'object_bitfields']
    if object_rows:
        from validation.object_bitfield_cases import NAMES
        if {f['name'] for f in object_rows} != set(NAMES) or any(f.get('recovery_group') != 'object-bitfields-001' for f in object_rows):
            raise ValueError('incomplete or unknown object-bitfield registry route')
    direct_rows = [f for f in functions if f.get('status') in ACTIVE and route(f) == 'direct_object_fields']
    if direct_rows:
        from validation.direct_object_field_cases import NAMES
        if {f['name'] for f in direct_rows} != set(NAMES) or any(f.get('recovery_group') != 'direct-object-fields-001' for f in direct_rows):
            raise ValueError('incomplete or unknown direct-object-field registry route')
    return sorted((f for f in functions if f.get('status') in ACTIVE and route(f) == group),
                  key=lambda f: f['id'])


def required_groups(registry):
    # Legacy six groups retain their controls; the additional group is all-or-none.
    selected_entries(registry, 'scalar')
    return (*LEGACY_GROUPS, *(g for g in ('object_bitfields','direct_object_fields') if selected_entries(registry,g)))


def group_execution(steps, group):
    plan, configurations = [], []
    for name, argv, _ in steps:
        if name not in (group+'_all', group+'_negative'):
            continue
        kept, index, mode, size = [], 0, 'single', None
        seen = set()
        while index < len(argv):
            token = argv[index]
            if token in {'--report-dir','--execution','--batch-size'}:
                if token in seen or index+1 >= len(argv):
                    raise ValueError('duplicate or missing execution argument')
                seen.add(token)
                value = argv[index+1]
                if token == '--report-dir':
                    index += 2
                    continue  # Only output destination is nonsemantic.
                if token == '--execution': mode = value
                else:
                    size = int(value)
                    if not 1 <= size <= 128: raise ValueError('invalid batch size')
            kept.append(token)
            index += 1
        if mode not in {'single','batch'} or (mode == 'batch' and group not in BATCH_IMAGES):
            raise ValueError('unsupported execution mode')
        if group in {'object_bitfields','direct_object_fields'} and mode != 'batch':
            raise ValueError('object bitfields require batch execution')
        configurations.append((mode,size if size is not None else (128 if mode == 'batch' else None)))
        plan.append({'step':name,'argv':kept})
    if [p['step'] for p in plan] != [group+'_all',group+'_negative'] or len(set(configurations)) != 1:
        raise ValueError('missing or inconsistent positive/negative execution plan')
    mode,size = configurations[0]
    return {'mode':mode,'batch_size':size,'commands':plan}


def execution_images(build, group, execution):
    if execution['mode'] == 'batch':
        if group not in BATCH_IMAGES: raise ValueError('unsupported batch group')
        return [build/('lib'+BATCH_IMAGES[group]+suffix+'.dylib') for suffix in ('','_mutant')]
    if group in {'object_bitfields','direct_object_fields'}: raise ValueError('group requires batch images')
    _,prefix = GROUPS[group]
    return [build/(prefix+suffix) for suffix in ('_runner','_mutant')]


def actual_corpora(group, functions):
    if group == 'scalar':
        from validation.validate_leaves import corpus
        from validation.scalar_cases import cases as pilot_cases
        def positive(f):
            return [c for suite in ('public', 'heldout') for c in pilot_cases(f['name'], suite)] if f.get('pilot') == 'luna-001' else corpus()
        def negative(f):
            values = pilot_cases(f['name'], 'public') if f.get('pilot') == 'luna-001' else corpus()
            return [c for c in values if c['inputs']['value'] in (0, 31, 32, 0xffffffff)] if f['name'] == 'bit_mask_or_all' else None
    else:
        module = importlib.import_module('validation.'+{
            'memory': 'memory_cases', 'object_counters': 'object_counter_cases',
            'indexed_stores': 'indexed_store_cases', 'indexed_fields': 'indexed_field_cases',
            'linked_structures': 'linked_structure_cases', 'object_bitfields':'object_bitfield_cases', 'direct_object_fields':'direct_object_field_cases'}[group])
        def positive(f):
            return [c for suite in ('public', 'heldout') for c in module.cases(f['name'], suite)]
        def negative(f):
            if group == 'memory':
                return module.cases(f['name'], 'public') if f['name'] == 'fn_00061fa0' else None
            names = {'object_counters': {'fn_00061f40'}, 'indexed_stores': {'fn_00347d10'}}
            controls = set(module.NEGATIVE_NAMES) if group in {'indexed_fields','object_bitfields','direct_object_fields'} else names.get(group)
            return module.negative_cases(f['name']) if controls is None or f['name'] in controls else None
    result = {}
    for function in functions:
        controls = negative(function)
        def bind(values):
            return {'sha256': digest(values), 'rows': [{'case_id': c['id'], 'case_sha256': digest(c)} for c in values]}
        result[function['id']] = {'positive': bind(positive(function)),
                                  'negative': bind(controls) if controls is not None else None}
    return result


def group_identity(root, build, group, registry, source, runtime, execution=None, corpora=None):
    if group not in GROUPS or runtime.get('provider') != 'macos-full-python-dyld-v1':
        raise ValueError('unsupported group or runtime provider')
    execution = execution or {'mode': 'single', 'commands': []}
    functions = selected_entries(registry, group)
    images = execution_images(build,group,execution)
    execution_sources = {name: value for name, value in source.items()
                         if (name.startswith(('tools/', 'validation/')) and name.endswith('.py'))
                         or name in {'requirements-validation.txt', 'analysis/reference-build.json'}}
    for name in DECLARED_VALIDATION_DEPENDENCIES.get(group, ()):
        execution_sources[name] = source[name]  # Missing declared input fails closed.
    selected_data = []
    if group == 'object_bitfields':
        selected_data = [root/'validation/object_bitfield_specs.json',
                         *[root/f"validation/object_bitfield_corpus/{f['name']}-{suite}.json"
                           for f in functions for suite in ('public','heldout')]]
    if group == 'direct_object_fields':
        selected_data = [root/'slices.json',
                         *[root/f"corpus/{f['name']}-{suite}.json"
                           for f in functions for suite in ('public','heldout')]]
    return {'schema_version': VERSION, 'policy': POLICY, 'group': group,
            'functions': functions, 'source': execution_sources, 'data':files_manifest(selected_data),
            'reference_descriptor': file_hash(root/'analysis/reference-build.json'),
            'contracts': files_manifest([root/f['contract'] for f in functions]),
            'corpora': actual_corpora(group, functions) if corpora is None else corpora,
            'executables': files_manifest([*images, root/'gamedata/bin_ship/DAOrigins.exe']),
            'native_dependencies': native_dependencies(images), 'runtime': runtime,
            'execution': execution, 'suites': ['public', 'heldout'], 'repeats_per_side': 2,
            'required_negative_controls': True}


def historical_role(root, artifact, function, report_path, identity):
    relative = artifact.absolute().relative_to(root).as_posix()
    if (str(artifact.absolute()) in identity['executables']
            or str(artifact.absolute()) in identity['native_dependencies']['files']):
        return 'execution_image'
    if str(artifact.absolute()) in identity.get('data', {}):
        return 'execution_selected_data'
    if relative == 'analysis/functions.json':
        return 'historical_registry_current_selected_projection'
    if relative == 'CMakeLists.txt' or (relative.startswith('build-incremental') and artifact.name in {'CMakeCache.txt', 'compile_commands.json'}):
        return 'historical_build_current_fresh_attestation'
    if artifact.suffix in {'.cpp', '.hpp', '.h'} and relative.startswith(('src/', 'include/', 'validation/', 'tests/', 'examples/')):
        return 'historical_compiled_source_current_fresh_attestation'
    if str(artifact.absolute()) in identity['executables']:
        return 'execution_image'
    if relative == 'analysis/reference-build.json':
        return 'execution_reference_descriptor'
    if relative == function['contract']:
        return 'selected_contract'
    if relative in DECLARED_VALIDATION_DEPENDENCIES.get(identity['group'], ()):
        if relative not in identity['source']:
            raise ValueError(f'declared validation dependency is not keyed: {artifact}')
        return 'execution_declared_validation_dependency'
    if relative in identity['source']:
        return 'execution_source_or_runtime_declaration'
    expected_cases = report_path.with_name(report_path.stem+'-cases.json')
    if artifact.absolute() == expected_cases.absolute():
        return 'immutable_comparison_cases'
    raise ValueError(f'unknown historical artifact role: {artifact}')


def verify_entry(root, entry, identity, expected):
    if (entry.get('schema_version') != VERSION or entry.get('policy') != POLICY
            or entry.get('identity') != identity
            or entry.get('payload_sha256') != digest(entry.get('payload'))):
        raise ValueError('invalid cache version, identity or payload')
    payload = entry['payload']
    if set(payload) != set(expected) or not payload:
        raise ValueError('incomplete positive/negative control cache')
    by_id = {f['id']: f for f in identity['functions']}
    verified = []
    for report_path, negative in expected.items():
        saved = payload[report_path]
        path = Path(report_path)
        if saved['report_sha256'] != file_hash(path):
            raise ValueError('missing or tampered comparison report')
        report = json.loads(path.read_text())
        function = by_id[report['function_id']]
        # Registry content may have unrelated additions. Preserve the historical
        # hash honestly; all selected entries are bound in the identity above.
        artifacts = report['artifacts_sha256']
        for name, expected_hash in artifacts.items():
            artifact = Path(name) if Path(name).is_absolute() else root / name
            current_hash = file_hash(artifact)
            role = historical_role(root, artifact, function, path, identity)  # Missing historical artifacts always rerun.
            if role.startswith('historical_'):
                continue  # Old hashes remain historical; current provenance is separate.
            if current_hash != expected_hash:
                raise ValueError(f'stale comparison execution artifact: {artifact}')
        # Reuse the unchanged recorder for all its strict report checks, with a
        # private historical registry snapshot, never changing the old report.
        # Equivalent checks below avoid pretending its stale registry is current.
        corpus_kind = 'negative' if negative else 'positive'
        corpus_binding = identity['corpora'][function['id']][corpus_kind]
        if (corpus_binding is None or report.get('corpus_sha256') != corpus_binding['sha256']
                or [{'case_id': row.get('case_id'), 'case_sha256': row.get('case_sha256')}
                    for row in report['cases']] != corpus_binding['rows']):
            raise ValueError('cached corpus differs from actual current selected corpus')
        counts = saved['case_counts']
        rows = report['cases']
        observed = {status: sum(r['status'] == status for r in rows)
                    for status in set(r['status'] for r in rows)}
        if counts != observed or saved['negative_control'] is not negative:
            raise ValueError('case accounting changed')
        valid = (observed.get('mismatch', 0) > 0 and set(observed) <= {'mismatch', 'corpus_pass'}) if negative else (
            report['status'] == 'corpus_pass' and set(observed) == {'corpus_pass'} and observed['corpus_pass'] > 0)
        required = {function['source'], function['contract'], 'analysis/functions.json', 'analysis/reference-build.json'}
        normalized = {str((Path(n) if Path(n).is_absolute() else root/n).resolve()) for n in artifacts}
        if (not valid or report['schema_version'] != 1 or report['kind'] != 'game'
                or report['proof'] is not False or report['native_windows_validated'] is not False
                or report['artifacts_unchanged'] is not True
                or type(report['repeats']) is not int or report['repeats'] < 2
                or not {str((root/n).resolve()) for n in required} <= normalized
                or digest(json.loads((root/function['contract']).read_text())) != report['contract_sha256']):
            raise ValueError('unacceptable cached comparison')
        verified.append(saved)
    return verified


def lookup_entry(root, path, identity, expected_new):
    """A malformed/missing/stale entry is always a miss, never partial evidence."""
    try:
        entry = json.loads(Path(path).read_text())
        names = {Path(p).name: negative for p, negative in expected_new.items()}
        old = entry['payload']
        if len(old) != len(names) or {Path(p).name for p in old} != set(names):
            raise ValueError('missing public/heldout or negative-control reports')
        expected = {p: names[Path(p).name] for p in old}
        return entry, verify_entry(root, entry, identity, expected)
    except (ValueError, OSError, KeyError, TypeError, AttributeError):
        return None, None


def seal(identity, records):
    payload = {str((ROOT / r['report']).resolve()): r for r in records}
    return {'schema_version': VERSION, 'policy': POLICY, 'identity': identity,
            'payload': payload, 'payload_sha256': digest(payload),
            'comparison_completed_at_unix': time.time()}


def execute(argv, cwd, log):
    with log.open('w') as stream:
        subprocess.run(argv, cwd=cwd, stdout=stream, stderr=subprocess.STDOUT,
                       check=True, timeout=3600)


def run(build, output, cache, jobs, groups=None, identity_only=False, batch_size=128):
    if jobs not in range(1, 5):
        raise ValueError('jobs must be between 1 and 4')
    registry_initial = json.loads((ROOT/'analysis/functions.json').read_text())
    complete_groups = required_groups(registry_initial)
    groups = complete_groups if groups is None else tuple(groups)
    if not groups or not set(groups) <= set(GROUPS) or len(set(groups)) != len(groups):
        raise ValueError('unsupported or duplicate group selection')
    if (ROOT not in build.parents or ROOT/'reports' not in output.parents
            or ROOT/'local' not in cache.parents):
        raise ValueError('build must be within snapshot; output under reports/ and cache under local/')
    if output.exists():
        raise ValueError('output must be new')
    output.mkdir(parents=True)
    cache.mkdir(parents=True, exist_ok=True)
    source_before = source_manifest(ROOT)
    prepare_build(ROOT, build)
    steps = checkpoint.build_commands(build, output, jobs, **({'batch_size':batch_size} if batch_size != 128 else {}))
    if ([name for name, _, _ in steps[:6]] !=
            ['configure', 'build', 'unittest', 'ctest', 'demo_good', 'demo_mutant']
            or {name for name, _, _ in steps[6:]} !=
            {group+suffix for group in complete_groups for suffix in ('_all', '_negative')}):
        raise ValueError('unsupported checkpoint acceptance plan')
    # --clean-first prevents trusting a stale executable even if timestamps lie.
    for name, argv, cwd in steps[:2 if identity_only else 6]:
        if name == 'configure' and sys.platform == 'darwin':
            # Apple ld documents this flag for timestamp-independent output.
            # This configures the build; executable bytes are never rewritten.
            argv = [*argv, *['-DCMAKE_'+kind+'_LINKER_FLAGS=-Wl,-reproducible'
                            for kind in ('EXE', 'SHARED', 'MODULE')]]
        if name == 'build':
            # A removed CMake target must not leave a usable stale executable.
            for _, prefix in GROUPS.values():
                for suffix in ('_runner', '_mutant'):
                    (build/(prefix+suffix)).unlink(missing_ok=True)
            for target in ('synthetic_candidate', 'synthetic_mutant'):
                (build/target).unlink(missing_ok=True)
            argv = [*argv, '--clean-first']
        execute(argv, cwd, output/(name+'.log'))
    if source_before != source_manifest(ROOT):
        raise ValueError('source changed during clean build')
    registry = json.loads((ROOT/'analysis/functions.json').read_text())
    positives, negatives = checkpoint.publication_paths(output)
    build_before = build_provenance(build)
    # Settle all supported Python case-provider imports before runtime inventory.
    for module in ('validate_leaves', 'scalar_cases', 'memory_cases', 'object_counter_cases',
                   'indexed_store_cases', 'indexed_field_cases', 'linked_structure_cases', 'object_bitfield_cases', 'direct_object_field_cases'):
        importlib.import_module('validation.'+module)
    corpora_before = {g: actual_corpora(g, selected_entries(registry, g)) for g in groups}
    try:
        runtime = current_runtime(build)
    except (ValueError, OSError, AttributeError, subprocess.SubprocessError) as exc:
        runtime = None  # Unknown closure always executes all groups again.
        (output/'runtime-unavailable.log').write_text(str(exc)+'\n')
    attestations = []
    entries = {}
    inventories = {}
    plans = []
    for group in groups:
        directory, _ = GROUPS[group]
        expected_new = {str(p): p in negatives for p in positives+negatives if p.parent.name == directory}
        if not expected_new:
            raise ValueError('selected checkpoint group has no required comparison reports')
        execution = group_execution(steps, group)
        identity = group_identity(ROOT, build, group, registry, source_before, runtime, execution, corpora_before[group]) if runtime else None
        if identity_only:
            plans.append({'group': group, 'cache_key': digest(identity) if identity else None,
                          'identity': identity})
            continue
        destination = cache/(digest(identity)+'.json') if identity else None
        reused = False
        records = None
        entry = None
        if destination is not None:
            entry, records = lookup_entry(ROOT, destination, identity, expected_new)
            reused = records is not None
        if records is None:
            for name, argv, cwd in steps[6:]:
                if name.startswith(group+'_'):
                    execute(argv, cwd, output/(name+'.log'))
            by_id = {f['id']: f for f in selected_entries(registry, group)}
            records = [record_report(ROOT, p, by_id[json.loads(Path(p).read_text())['function_id']], negative=n)
                       for p, n in expected_new.items()]
            if identity:
                entry = seal(identity, records)
                verify_entry(ROOT, entry, identity, expected_new)
        entries[group] = entry
        inventories[group] = expected_new
        attestations.append({'group': group, 'reused': reused, 'cache': str(destination) if destination else None,
                             'identity_sha256': digest(identity), 'records': records,
                             'historical_comparisons': [r['report'] for r in records],
                             'current_build_verified_at_unix': time.time()})
    if runtime is not None:
        runtime_after = current_runtime(build)
        if runtime_after != runtime:
            changed = [key for key in runtime if runtime.get(key) != runtime_after.get(key)]
            (output/'runtime-instability.json').write_text(json.dumps({'changed_fields': changed,
                'new_images': sorted(set(runtime_after['loaded_images'])-set(runtime['loaded_images'])),
                'removed_images': sorted(set(runtime['loaded_images'])-set(runtime_after['loaded_images']))}, indent=2)+'\n')
            raise ValueError('runtime changed during checkpoint')
    if source_before != source_manifest(ROOT):
        raise ValueError('source changed during checkpoint')
    if build_before != build_provenance(build):
        raise ValueError('fresh build artifacts changed during checkpoint')
    if json.loads((ROOT/'analysis/functions.json').read_text()) != registry:
        raise ValueError('registry changed during checkpoint')
    if identity_only:
        result = {'schema_version': VERSION, 'policy': POLICY, 'status': 'identity_only',
                  'fresh_clean_build': True, 'runtime_available': runtime is not None,
                  'plans': plans, 'source_attestation': source_before, 'build_attestation': build_before, 'invocation_environment': invocation_environment(os.environ),
                  'usable_for_progress': False, 'proof': False, 'native_windows_validated': False}
        (output/'identity-plan.json').write_text(json.dumps(result, indent=2)+'\n')
        return result
    for attestation in attestations:
        if attestation['cache'] is None:
            continue
        entry = entries[attestation['group']]
        if attestation['reused']:
            entry = json.loads(Path(attestation['cache']).read_text())
        current = group_identity(ROOT, build, attestation['group'], registry, source_before, runtime,
                                 group_execution(steps, attestation['group']))
        names = {Path(p).name: n for p, n in inventories[attestation['group']].items()}
        expected = {p: names[Path(p).name] for p in entry['payload']}
        if len(expected) != len(names):
            raise ValueError('control inventory changed during checkpoint')
        verify_entry(ROOT, entry, current, expected)
    # Publish cache entries only after complete before/after input attestation.
    # A failed or interrupted checkpoint cannot seed later reuse.
    for attestation in attestations:
        if attestation['cache'] is not None and not attestation['reused']:
            destination = Path(attestation['cache'])
            pending = destination.with_suffix('.pending-'+str(os.getpid()))
            pending.write_text(json.dumps(entries[attestation['group']], indent=2)+'\n')
            pending.replace(destination)
    result = {'schema_version': VERSION, 'policy': POLICY, 'status': 'passed',
              'fresh_clean_build': True, 'source': source_before,
              'invocation_environment': invocation_environment(os.environ),
              'build_attestation': build_before,
              'registry_sha256': file_hash(ROOT/'analysis/functions.json'),
              'groups': attestations, 'proof': False, 'native_windows_validated': False,
              'complete_checkpoint': set(groups) == set(complete_groups),
              'usable_for_progress': set(groups) == set(complete_groups) and runtime is not None,
              'scope': 'local emulator corpus evidence; fresh attestation with historical comparisons'}
    (output/'reuse-attestation.json').write_text(json.dumps(result, indent=2)+'\n')
    if result['usable_for_progress']:
        (output/'current-evidence.json').write_text(json.dumps(publication_document(result), indent=2)+'\n')
    return result


def publication_inventory():
    positives, negatives = checkpoint.publication_paths(ROOT/'reports/__inventory__')
    registry = json.loads((ROOT/'analysis/functions.json').read_text())
    by_name = {f['name']:f['id'] for f in registry['functions'] if f.get('status') in ACTIVE}
    return {(by_name[path.name.removesuffix('-mutant.json').removesuffix('-all.json')],negative)
            for negative,paths in ((False,positives),(True,negatives)) for path in paths}


def publication_document(result):
    """Compact current provenance; never rewrites the historical v1 comparison.

    This is a new policy record. Its artifacts describe the fresh attestation,
    while historical_comparison retains the unmodified comparison provenance.
    The updater still rechecks every tracked current input, including the entire
    registry; a subsequent unrelated registry addition needs a new attestation,
    but permits comparison reuse when selected entries/executables are identical.
    """
    if result.get('usable_for_progress') is not True or result.get('complete_checkpoint') is not True or result['schema_version'] != VERSION or result['policy'] != POLICY or result['status'] != 'passed':
        raise ValueError('unacceptable checkpoint attestation')
    actual = [(r['function_id'],r['negative_control']) for g in result['groups'] for r in g['records']]
    if len(actual) != len(set(actual)) or set(actual) != publication_inventory():
        raise ValueError('incomplete current checkpoint publication inventory')
    artifacts = dict(result['source'])
    artifacts['analysis/functions.json'] = result['registry_sha256']
    records = []
    for group in result['groups']:
        for historical in group['records']:
            record = {key: value for key, value in historical.items() if key != 'artifacts_sha256'}
            record.update(artifacts_sha256=artifacts,
                          provenance_kind='fresh_clean_build_and_exact_execution_inputs',
                          comparison_reused=group['reused'],
                          current_identity_sha256=group['identity_sha256'],
                          historical_comparison={'report': historical['report'],
                              'report_sha256': historical['report_sha256'],
                              'artifacts_sha256': historical['artifacts_sha256']})
            records.append(record)
    document = {'schema_version': VERSION, 'policy': POLICY,
                'evidence_level': 'emulator_corpus_agreement', 'proof': False,
                'native_windows_validated': False, 'fresh_clean_build': True,
                'complete_checkpoint': True,
                'created_at_unix': time.time(), 'records': records,
                'build_attestation': result.get('build_attestation', {})}
    document['attestation_sha256'] = digest(document)
    return document


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--cache-dir', type=Path, required=True)
    parser.add_argument('--group', action='append', choices=GROUPS, help='partial experiment only; cannot publish progress')
    parser.add_argument('--identity-only', action='store_true', help='clean build and compare input identities only; executes no corpus and publishes no evidence')
    parser.add_argument('--batch-size',type=int,choices=range(1,129),default=128)
    parser.add_argument('--record', type=Path, help='optional new analysis/validation/*.json publication')
    parser.add_argument('--jobs', type=int, choices=range(1, 5), default=2)
    args = parser.parse_args()
    if (args.group or args.identity_only) and args.record:
        parser.error('partial group experiment cannot publish a checkpoint')
    record = checkpoint.validate_record_path(args.record) if args.record else None
    run(args.build_dir.absolute(), args.output_dir.resolve(), args.cache_dir.resolve(), args.jobs, args.group, args.identity_only,args.batch_size)
    if record is not None:
        if not (args.output_dir/'current-evidence.json').is_file():
            raise ValueError('runtime closure unavailable; fresh reports exist but reuse provenance cannot be published')
        with record.open('xb') as stream:
            stream.write((args.output_dir/'current-evidence.json').read_bytes())


if __name__ == '__main__':
    main()

"""Build native PE32 replacements with original data RVAs and compiled C++ code.

The Windows loader owns imports, resources and static TLS. Original executable
sections are retained as non-executable data (jump tables/constants may live
there); only newly compiled code is executable. No original-code fallback exists.
Generated images and extracted data belong under ignored local/.
"""
import argparse
from collections import Counter, deque
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import struct
import subprocess
import sys
import time

from tools import recomp, recomp_boot
from tools.daodecomp.pe import fingerprint


def align(value, boundary=4096):
    return (value + boundary - 1) & -boundary


class PE32:
    def __init__(self, path):
        self.path = Path(path)
        self.info = fingerprint(path)
        if self.info['architecture'] != 'x86' or self.info['format'] != 'PE32':
            raise ValueError('native replacement requires PE32 x86')
        self.data = bytearray(self.path.read_bytes())
        self.optional = struct.unpack_from('<I', self.data, 60)[0] + 24
        self.section_table = self.optional + struct.unpack_from('<H', self.data, self.optional - 4)[0]
        if struct.unpack_from('<I', self.data, self.optional + 32)[0] != 4096:
            raise ValueError('native replacement requires 4096-byte section alignment')
        if struct.unpack_from('<I', self.data, self.optional + 92)[0] != 16:
            raise ValueError('unexpected PE directory count')
        self.sections = self.info['sections']
        self.end = align(max(s['rva'] + max(s['virtual_size'], s['file_size']) for s in self.sections))

    def directory(self, index):
        return struct.unpack_from('<II', self.data, self.optional + 96 + index * 8)

    def set_directory(self, index, value):
        struct.pack_into('<II', self.data, self.optional + 96 + index * 8, *value)

    def offset(self, rva, size):
        for section in self.sections:
            if section['rva'] <= rva and rva + size <= section['rva'] + section['file_size']:
                return section['file_offset'] + rva - section['rva']
        raise ValueError(f'PE RVA {rva:#x}+{size:#x} is not file backed')

    def read(self, rva, size):
        offset = self.offset(rva, size)
        return bytes(self.data[offset:offset + size])

    def imports(self):
        rva, size = self.directory(1)
        if not rva and not size:
            return []
        result = []
        for cursor in range(rva, rva + size, 20):
            descriptor = self.read(cursor, 20)
            words = struct.unpack('<IIIII', descriptor)
            if not any(words):
                return result
            if not words[0] or not words[3] or not words[4]:
                raise ValueError('imports require separate original lookup and address tables')
            # Bound imports must be rebound by the real loader at process start.
            result.append(struct.pack('<IIIII', words[0], 0, 0, words[3], words[4]))
        raise ValueError('unterminated PE import descriptor table')


def prepare_image(original_path, directory):
    """Extract data and emit a layout object; no original section is executable."""
    original = PE32(original_path)
    directory.mkdir(parents=True, exist_ok=True)
    sections = original.sections
    if sections[0]['rva'] != 4096 or any(a['rva'] >= b['rva'] for a, b in zip(sections, sections[1:])):
        raise ValueError('unexpected original section layout')
    assembly, order = [], []
    for index, section in enumerate(sections):
        name = f'.g{index:05d}'
        order.append(name)
        extent = (sections[index + 1]['rva'] if index + 1 < len(sections) else original.end) - section['rva']
        if max(section['file_size'], section['virtual_size']) > extent:
            raise ValueError('overlapping original PE sections')
        characteristics = struct.unpack_from('<I', original.data, original.section_table + index * 40 + 36)[0]
        if not characteristics & 0x40000000:
            raise ValueError('original section is not readable')
        blob = directory / (name + '.bin')
        blob.write_bytes(original.read(section['rva'], section['file_size']))
        flags = 'dw' if characteristics & 0x80000000 else 'dr'
        assembly += [f'.section {name},"{flags}"', '.balign 4096', f'.incbin {json.dumps(str(blob.absolute()))}']
        if extent > section['file_size']:
            assembly.append(f'.space {extent - section["file_size"]}')
    # One page holds combined descriptors. Its capacity is checked after link.
    order.append('.gmeta')
    assembly += ['.section .gmeta,"dr"', '.balign 4096', '.space 4096']
    source = directory / 'original-data.S'
    source.write_text('\n'.join(assembly) + '\n')
    layout = directory / 'section-order.txt'
    layout.write_text('\n'.join(order + ['.text', '.rdata', '.data']) + '\n')
    return original, source, layout


def finalize_image(original, linked_path, output):
    if output.is_symlink() or output.resolve() == original.path.resolve():
        raise ValueError('replacement output must not overwrite or link to the original')
    linked = PE32(linked_path)
    if linked.info['image_base'] != original.info['image_base']:
        raise ValueError('linked module moved from its pinned preferred base')
    for index, section in enumerate(original.sections):
        actual = linked.sections[index]
        if actual['name'] != f'.g{index:05d}' or actual['rva'] != section['rva']:
            raise ValueError('linker did not preserve original data RVAs')
        flags = struct.unpack_from('<I', linked.data, linked.section_table + index * 40 + 36)[0]
        if flags & 0x20000000:
            raise ValueError('original instruction bytes became executable')
        if linked.read(section['rva'], section['file_size']) != original.read(section['rva'], section['file_size']):
            raise ValueError('original initialized data changed during link')
    metadata = next(s for s in linked.sections if s['name'] == '.gmeta')
    original_descriptors = original.imports()
    # This address-preserving profile pins Umbra at its original preferred base.
    # Let Windows load it before relocatable retained SDKs (FMOD also prefers
    # 0x10000000). Preserve the relative order of all other original imports.
    # This is an explicit startup composition difference, not equivalence proof.
    def provider_name(descriptor):
        rva = struct.unpack('<IIIII', descriptor)[3]
        name = bytearray()
        for index in range(260):
            byte = original.read(rva + index, 1)[0]
            if not byte:
                return name.decode('ascii').lower()
            name.append(byte)
        raise ValueError('unterminated provider name')
    original_descriptors.sort(key=lambda d: provider_name(d) != 'umbra.dll')
    descriptors = original_descriptors + linked.imports()
    table = b''.join(descriptors) + bytes(20)
    if len(table) > metadata['file_size']:
        raise ValueError('combined import descriptors exceed reserved page')
    offset = linked.offset(metadata['rva'], len(table))
    linked.data[offset:offset + len(table)] = table
    linked.set_directory(1, (metadata['rva'], len(table)))
    # Export RVAs, resources and the original TLS directory still designate the
    # original data at exactly the same addresses. Compiled TLS must be emulated
    # independently; sharing a static TLS index would corrupt both templates.
    for index in (0, 2):
        linked.set_directory(index, original.directory(index))
    if original.directory(9)[0]:
        if linked.directory(9)[0]:
            raise ValueError('compile native support with -femulated-tls before adopting original static TLS')
        tls = struct.unpack('<IIIIII', original.read(original.directory(9)[0], 24))
        if tls[3] and original.read(tls[3] - original.info['image_base'], 4) != bytes(4):
            raise ValueError('original TLS callbacks need the generic translated-entry bridge')
        linked.set_directory(9, original.directory(9))
    # Discontiguous IATs are bound through descriptors. Original load-config,
    # relocations, certificates and debug records are not host executable data.
    linked.set_directory(12, (0, 0))
    linked.set_directory(5, (0, 0))
    struct.pack_into('<H', linked.data, linked.optional + 68,
                     struct.unpack_from('<H', original.data, original.optional + 68)[0])
    struct.pack_into('<I', linked.data, linked.optional + 64, 0)  # stale checksum
    # Both original and newly linked code use this pinned address domain.
    flags = struct.unpack_from('<H', linked.data, linked.optional + 70)[0]
    struct.pack_into('<H', linked.data, linked.optional + 70, flags & ~0x40)  # no ASLR
    coff = struct.unpack_from('<H', linked.data, linked.optional - 2)[0]
    struct.pack_into('<H', linked.data, linked.optional - 2, coff | 1)  # fixed base
    output.write_bytes(linked.data)
    return dict(original_sha256=original.info['sha256'], output_sha256=recomp.digest(linked.data),
                original_image_base=original.info['image_base'], original_data_end=original.end,
                original_sections_executable=False, combined_import_descriptors=len(descriptors),
                translated_umbra_loaded_first=True, windows_static_tls=bool(original.directory(9)[0]), game_acceptance=False)


def run(command, log, timeout=1200):
    command = list(map(str, command))
    with log.open('w') as stream:
        result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, timeout=timeout)
    if result.returncode:
        raise RuntimeError(f'{log.name}: exit {result.returncode}: {log.read_text()[-3000:]}')
    return command


def native_link(cxx, original, objects, source, layout, directory, output, dll=False):
    """Use lld's COFF section ordering, unavailable through its MinGW driver."""
    toolchain = cxx.parent.parent
    library = toolchain / 'i686-w64-mingw32/lib'
    builtins = list((toolchain / 'lib/clang').glob('*/lib/windows/libclang_rt.builtins-i386.a'))
    if len(builtins) != 1:
        raise ValueError('ambiguous/missing i386 compiler runtime')
    data_object = directory / 'original-data.obj'
    commands = [run([cxx, '-c', source, '-o', data_object], directory / 'assemble.log')]
    unpatched = directory / 'linked-unpatched.dll' if dll else directory / 'linked-unpatched.exe'
    command = [cxx.parent / 'lld-link', '/lldmingw', '/machine:x86', '/subsystem:console',
               '/base:' + hex(original.info['image_base']), '/dynamicbase:no', '/fixed',
               '/sectionlayout:' + str(layout), '/out:' + str(unpatched), '/map:' + str(directory / 'link.map')]
    if dll:
        command += ['/dll', '/implib:' + str(directory / 'host-exports.a')]
    command += [library / ('dllcrt2.o' if dll else 'crt2.o'), library / 'crtbegin.o', data_object, *objects]
    command += [library / 'libc++.a', library / 'libmingw32.a', builtins[0]]
    command += [library / ('lib' + name + '.a') for name in
                ('unwind', 'moldname', 'mingwex', 'msvcrt', 'advapi32', 'shell32', 'user32', 'gdi32', 'winmm', 'kernel32')]
    command += [library / 'crtend.o']
    commands.append(run(command, directory / 'link.log'))
    report = finalize_image(original, unpatched, output)
    report['build_argv'] = commands
    recomp.atomic_json(directory / 'layout-report.json', report)
    return report


def build_library(out, view, manifest, cxx):
    source = out / 'source'
    source.mkdir(parents=True, exist_ok=True)
    for name, sha in manifest['files'].items():
        if name == 'CMakeLists.txt':
            continue
        target = source / name
        if not target.exists() or recomp.digest(target.read_bytes()) != sha:
            target.write_bytes((view / name).read_bytes())
    cmake_text = (view / 'CMakeLists.txt').read_text() + '\ntarget_precompile_headers(recomp_generated PRIVATE runtime.hpp)\n'
    cmake = source / 'CMakeLists.txt'
    if not cmake.exists() or cmake.read_text() != cmake_text:
        cmake.write_text(cmake_text)
    build = out / 'build'
    commands = [run(['cmake', '-S', source, '-B', build, '-G', 'Ninja', '-DCMAKE_SYSTEM_NAME=Windows',
                     '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_CXX_FLAGS_RELEASE=-O2 -g0 -DNDEBUG -femulated-tls',
                     '-DRECOMP_NATIVE_EXECUTION=ON', '-DCMAKE_CXX_COMPILER=' + str(cxx),
                     '-DCMAKE_AR=' + str(cxx.parent / 'llvm-ar'), '-DCMAKE_RANLIB=' + str(cxx.parent / 'llvm-ranlib')],
                    out / 'configure.log'),
                run(['cmake', '--build', build, '--target', 'recomp_generated', '--parallel', '4'], out / 'build.log', 2400)]
    return source, build / 'librecomp_generated.a', commands


def stage_retained(stage, original_directory, inventory):
    """Copy retained providers, never either original translated code module."""
    records = {}
    for source in sorted(original_directory.iterdir()):
        if not source.is_file() or source.suffix.lower() != '.dll' or source.name.lower() == 'umbra.dll':
            continue
        destination = stage / source.name
        sha = recomp.digest(source.read_bytes())
        if not destination.exists() or recomp.digest(destination.read_bytes()) != sha:
            shutil.copy2(source, destination)
        records[source.name] = dict(source=str(source), sha256=sha)
    # PhysX's original provider was installed outside the game directory. Keep
    # its pinned provider local instead of adding the original install to PATH.
    provider = inventory['provider_inventory']['physxloader.dll']
    source = Path(provider['path'])
    if recomp.digest(source.read_bytes()) != provider['sha256']:
        raise ValueError('retained PhysXLoader provider changed')
    shutil.copy2(source, stage / 'PhysXLoader.dll')
    records['PhysXLoader.dll'] = provider
    return records


def stage_assets(stage, original_install):
    """Independent writable asset tree; APFS clones do not alter originals."""
    records = []
    for name in ('Addins', 'Offers', 'data', 'modules', 'packages'):
        source, target = original_install / name, stage.parent / name
        if source.is_symlink() or not source.is_dir() or target.is_symlink():
            raise ValueError('asset staging requires direct installation directories')
        if not target.exists():
            if sys.platform == 'darwin':
                run(['cp', '-cR', source, target], stage.parent / ('clone-' + name + '.log'), 1200)
            else:
                shutil.copytree(source, target)
        records.append(dict(source=str(source), destination=str(target), independent_copy=True))
    return records


def freeze_native_sources(out, view_id, cxx, plan):
    sources = {'recomp_native.py': Path(__file__), 'native_process.cpp': recomp.RUNTIME / 'native_process.cpp',
               'native_callback_entry.hpp': recomp.RUNTIME / 'native_callback_entry.hpp',
               'native_entry.c': recomp.RUNTIME / 'native_entry.c'}
    contents = {name: path.read_bytes() for name, path in sources.items()}
    contents['startup.json'] = recomp.encoded(plan)
    identity = dict(view=view_id, source_sha256={name: recomp.digest(data) for name, data in contents.items()},
                    compiler=str(cxx), compiler_sha256=recomp.digest(cxx.read_bytes()),
                    compiler_artifacts={str(p): recomp.digest(p.read_bytes()) for p in
                        (cxx.parent / 'clang', cxx.parent / 'ld.lld', cxx.parent / 'lld-link')},
                    compiler_version=subprocess.check_output([str(cxx), '--version'], text=True))
    directory = out / 'build-inputs' / recomp.digest(recomp.encoded(identity))
    directory.mkdir(parents=True, exist_ok=True)
    for name, data in contents.items():
        target = directory / name
        if target.exists() and target.read_bytes() != data:
            raise ValueError('immutable native build input changed')
        if not target.exists():
            target.write_bytes(data)
    recomp.atomic_json(directory / 'identity.json', identity)
    return directory, identity


MISSING_NATIVE_CODE={'untranslated guest code/import target','untranslated guest function target'}


def native_missing_entries(report):
    """All distinct measured code gaps, never timeout/trace/return guesses."""
    if report.get('timed_out'): return []
    result=[];seen=set()
    for event in report.get('events',[]):
        if event.get('event') not in ('native_startup_frontier','native_callback_frontier') or event.get('reason') not in MISSING_NATIVE_CODE:
            continue
        pc=event.get('pc')
        if type(pc) is not int or not 0<pc<=0xffffffff:
            raise ValueError('native missing-code frontier has no valid measured PC')
        if pc not in seen: result.append(event);seen.add(pc)
    return result


def native_observation(report):
    """Thread attach/ABI trace tails cannot replace a main failure/outcome."""
    if report.get('timed_out'):
        return dict(event='native_observation_timeout', reason='native process timed out; main outcome unknown', game_acceptance=False)
    events=report.get('events', [])
    failures=[event for event in events if event.get('event') in ('native_startup_frontier','native_callback_frontier')]
    if failures:
        runtime=[event for event in failures if event.get('reason') not in MISSING_NATIVE_CODE]
        return (runtime or failures)[-1]
    main_returns=[event for event in events if event.get('event')=='native_translated_return' and event.get('module')==0x400000]
    if main_returns: return main_returns[-1]
    return dict(event='native_incomplete_observation', reason='no main return or frontier recorded', game_acceptance=False)


def read_native_events(path):
    """Index outcomes without duplicating a potentially huge full ABI trace.

    Every non-ABI event remains in order. The complete log is retained and hashed;
    only repetitive ABI entry/exit records have a bounded inline diagnostic tail.
    This storage index does not validate calls or grant game acceptance.
    """
    events = []
    counts = Counter()
    tail = deque(maxlen=64)
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for line in stream:
            digest.update(line)
            if not line.startswith(b'{'):
                continue
            try:
                event = json.loads(line.decode('utf-8', errors='replace'))
            except json.JSONDecodeError:
                continue
            if not isinstance(event, dict):
                continue
            kind = event.get('event')
            if kind in ('native_abi_enter', 'native_abi_exit'):
                counts[kind] += 1
                tail.append(event)
            else:
                events.append(event)
    return events, dict(counts=dict(counts), tail=list(tail),
                        full_log=str(path), full_log_sha256=digest.hexdigest(),
                        scope='Storage index only; complete ABI records remain in the full log; no call or game acceptance.')


def execute_native(stage, out, wine, prefix, budget, timeout, arguments, wine_debug='-all'):
    plan = recomp.load(recomp_boot.PLAN)
    profile = recomp_boot.checked_startup_profile(prefix, plan['process_state'])
    env = dict(os.environ, WINEPREFIX=str(prefix), WINEDEBUG=wine_debug, MVK_CONFIG_LOG_LEVEL='0',
               WINEDLLOVERRIDES='mscoree,mshtml=', RECOMP_INSTRUCTION_BUDGET=str(budget))
    argv = [str(wine), str(stage / 'DAOrigins.exe'), *arguments]
    build_data = (out / 'build-report.json').read_bytes()
    build_identity = recomp.digest(build_data)
    build_snapshot = out / 'build-reports' / (build_identity + '.json.gz')
    build_snapshot.parent.mkdir(exist_ok=True)
    if build_snapshot.exists():
        if gzip.decompress(build_snapshot.read_bytes()) != build_data:
            raise ValueError('immutable native build report changed')
    else:
        build_snapshot.write_bytes(gzip.compress(build_data, compresslevel=3, mtime=0))
    build = recomp.load(out / 'build-report.json')
    # Retain exact executed candidates, not merely mutable filenames. Compressed
    # content-addressed blobs stay local and can be restored with hash checking.
    executed_images = {}
    for name in ('DAOrigins.exe', 'umbra.dll', 'recomp_runtime.dll'):
        data = (stage / name).read_bytes()
        sha = recomp.digest(data)
        blob = out / 'artifacts' / (sha + '.gz')
        blob.parent.mkdir(exist_ok=True)
        if blob.exists():
            if recomp.digest(gzip.decompress(blob.read_bytes())) != sha:
                raise ValueError('archived native candidate changed')
        else:
            blob.write_bytes(gzip.compress(data, compresslevel=3, mtime=0))
        executed_images[name] = dict(sha256=sha, compressed_blob=str(blob))
    started = time.time_ns()
    run_directory = out / 'runs' / str(started)
    run_directory.mkdir(parents=True, exist_ok=False)
    stdout_path, stderr_path = run_directory / 'stdout', run_directory / 'stderr'
    timed_out = False
    with stdout_path.open('wb') as stdout, stderr_path.open('wb') as stderr:
        # Keep the familiar live-log names, replacing their links rather than
        # opening/truncating them. Reports bind the independent per-run paths.
        for path, alias in ((stdout_path, out / 'run.stdout'), (stderr_path, out / 'run.stderr')):
            temporary = out / ('.' + alias.name + '.' + str(started))
            try:
                os.link(path, temporary)
                os.replace(temporary, alias)
            finally:
                temporary.unlink(missing_ok=True)
        process = subprocess.Popen(argv, cwd=stage, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGKILL)
            code = process.wait()
    events, abi_trace = read_native_events(stderr_path)
    artifacts = [stage / 'DAOrigins.exe', stage / 'umbra.dll', stage / 'recomp_runtime.dll', stdout_path, stderr_path]
    report = dict(status='incomplete; native startup exploration', game_acceptance=False, argv=argv,
                  exit_code=code, timed_out=timed_out, elapsed_seconds=(time.time_ns()-started)/1e9,
                  execution_environment={key: env.get(key) for key in
                      ('WINEPREFIX', 'WINEDEBUG', 'MVK_CONFIG_LOG_LEVEL', 'WINEDLLOVERRIDES',
                       'RECOMP_INSTRUCTION_BUDGET', 'RECOMP_TRACE_NATIVE_CALLS')},
                  checked_filesystem_profile=profile, events=events, native_abi_trace=abi_trace, budget=budget,
                  executed_images=executed_images,
                  view=build['view'], build_report_sha256=build_identity, build_report_snapshot=str(build_snapshot),
                  artifacts={str(p): abi_trace['full_log_sha256'] if p == stderr_path else recomp.digest(p.read_bytes())
                             for p in artifacts})
    report['observation']=native_observation(report)
    recomp.atomic_json(out / 'run-report.json', report)
    recomp.atomic_json(out / 'runs' / (str(started)+'.json'), report)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=recomp.ROOT / 'local/recomp/project')
    parser.add_argument('--umbra-project', type=Path, default=recomp.ROOT / 'local/recomp/umbra')
    parser.add_argument('--output', type=Path, default=recomp.ROOT / 'local/recomp/native-game')
    parser.add_argument('--cxx', type=Path, default=recomp.ROOT / 'local/tools/recomp/llvm-mingw-20261104-ucrt-macos-universal/bin/i686-w64-mingw32-clang++')
    parser.add_argument('--run', action='store_true', help='run the replacement entry under Wine after building')
    parser.add_argument('--wine', type=Path, default=recomp.ROOT / 'local/tools/recomp/Wine Stable.app/Contents/Resources/wine/bin/wine')
    parser.add_argument('--wine-prefix', type=Path, default=recomp.ROOT / 'local/recomp/wine-prefix')
    parser.add_argument('--wine-debug', default='-all', help='explicit Wine diagnostic channels, e.g. --wine-debug=+seh')
    parser.add_argument('--budget', type=int, default=500000000)
    parser.add_argument('--run-timeout', type=int, default=60)
    parser.add_argument('--game-argument', action='append', default=[])
    parser.add_argument('--advance', action='store_true', help='select an observed missing entry using the pinned function inventory')
    parser.add_argument('--call-depth', type=int, default=0, help='with --advance, also select translatable direct callees to this depth')
    parser.add_argument('--call-limit', type=int, default=64, help='maximum optional direct-callee lift attempts')
    parser.add_argument('--call-seeds', choices=('reached', 'selected'), default='reached', help='expand from newly reached entries or all current plan entries')
    args = parser.parse_args(argv)
    out = args.output.absolute()
    cxx = args.cxx.absolute()  # preserve target wrapper argv[0]
    if args.budget <= 0 or args.run_timeout <= 0:
        parser.error('budget and timeout must be positive')
    if not 0 <= args.call_depth <= 8 or not 1 <= args.call_limit <= 512 or (args.call_depth and not args.advance):
        parser.error('invalid direct-call discovery options; --call-depth requires --advance')
    if args.call_seeds == 'selected' and not args.call_depth:
        parser.error('--call-seeds selected requires --call-depth')
    for project in (args.project.absolute(), args.umbra_project.absolute()):
        install = recomp.checked_binary(recomp.state(project)).parent.parent.resolve()
        if out.resolve().is_relative_to(install):
            parser.error('replacement output must be separate from the original install')
    out.mkdir(parents=True, exist_ok=True)
    with recomp.locked(out / 'build-lock'):
        try:
            plan = recomp.load(recomp_boot.PLAN)
            projects = {'main': args.project.absolute(), 'umbra': args.umbra_project.absolute()}
            inventories = {'main': recomp.ROOT / 'local/analysis/functions.json',
                           'umbra': recomp.ROOT / 'local/recomp/startup/umbra-analysis/functions.json'}
            additions = []
            expansion = None
            if args.advance:
                previous = recomp.load(out / 'run-report.json')
                if previous['timed_out'] or not previous['events']:
                    raise ValueError('prior native run has no completed missing-code frontier')
                event = native_observation(previous)
                if event.get('reason') not in MISSING_NATIVE_CODE:
                    raise ValueError('prior native frontier needs runtime/ABI debugging, not more code')
                adapter = out / 'frontier-selection'
                # Concurrent callbacks can expose independent bodies in one run.
                # Admit every observed target before paying for another startup.
                targets=native_missing_entries(previous)
                recomp.atomic_json(adapter / 'last-execution.json', dict(runs=[dict(module='main',events=[target]) for target in targets]))
                additions = recomp_boot.advance_frontier(adapter, plan, projects, inventories)
                if args.call_depth:
                    from tools.recomp_reachability import expand_direct_calls
                    plan_snapshot = recomp_boot.PLAN.read_bytes()
                    seeds = additions if args.call_seeds == 'reached' else [dict(module=role, rva=f['rva'])
                              for role in projects for f in plan['roles'][role]['functions']]
                    expansion = expand_direct_calls(plan, projects, inventories, seeds, args.call_depth, args.call_limit)
                    expansion['seed_mode'] = args.call_seeds
                    recomp.atomic_json(out / 'call-discovery' / (recomp.digest(recomp.encoded(expansion))+'.json'), expansion)
                    if expansion['accepted']:
                        if recomp_boot.PLAN.read_bytes() != plan_snapshot:
                            raise ValueError('startup plan changed during native direct-call discovery')
                        recomp.atomic_json(recomp_boot.PLAN, plan)
            states = {role: recomp_boot.prepare(project, plan['roles'][role]) for role, project in projects.items()}
            for state in states.values():
                install = recomp.checked_binary(state).parent.parent.resolve()
                if out.resolve().is_relative_to(install):
                    raise ValueError('replacement output must be separate from the original install')
            for role, state in states.items():
                recomp.atomic_json(out / (role + '-project/project.json'), state)
            generated = recomp.generate(out / 'main-project', linked_modules=[out / 'umbra-project'])
            view, manifest = recomp.read_view(out / 'main-project', generated['view'])
            frozen_sources, identity = freeze_native_sources(out, generated['view'], cxx, plan)
            source, library, commands = build_library(out, view, manifest, cxx)
            stage = out / 'bin_ship'
            stage.mkdir(exist_ok=True)
            runtime = stage / 'recomp_runtime.dll'
            runtime_imports = out / 'recomp_runtime.a'
            commands.append(run([cxx, '-std=c++20', '-O2', '-femulated-tls', '-DRECOMP_NATIVE_EXECUTION=1', '-shared', '-static',
                                 '-I', source, frozen_sources / 'native_process.cpp', library, '-ladvapi32', '-lwinmm',
                                 '-luser32', '-lshell32', '-lgdi32', '-Wl,--image-base,0x20000000',
                                 '-Wl,--out-implib,' + str(runtime_imports), '-o', runtime], out / 'runtime-link.log'))
            reports = {}
            for role, state in states.items():
                directory = out / (role + '-image')
                original, data_source, layout = prepare_image(recomp.checked_binary(state), directory)
                config = directory / 'native_image_config.hpp'
                config.write_text('#pragma once\n' + '\n'.join(
                    f'#define RECOMP_{key} {value}u' for key, value in
                    [('IMAGE_BASE', state['image_base']), ('IMAGE_EXTENT', original.end),
                     ('ENTRY', state['image_base'] + plan['roles'][role]['entry_rva']),
                     ('IS_DLL', int(role == 'umbra'))]) + '\n')
                obj = directory / 'native_entry.obj'
                commands.append(run([cxx, '-x', 'c', '-O2', '-I', directory, '-c', frozen_sources / 'native_entry.c', '-o', obj],
                                    directory / 'compile.log'))
                reports[role] = native_link(cxx, original, [obj, runtime_imports], data_source, layout, directory,
                                            stage / state['module'], dll=role == 'umbra')
            retained = stage_retained(stage, recomp.checked_binary(states['main']).parent,
                                      recomp.load(recomp.ROOT / 'recompiler/imports.json'))
            assets = stage_assets(stage, recomp.checked_binary(states['main']).parent.parent)
            report = dict(status='built; not game acceptance', view=generated['view'], functions=len(manifest['functions']),
                          modules=reports, runtime_sha256=recomp.digest(runtime.read_bytes()),
                          retained_providers=retained, assets=assets, added_functions=additions, build_argv=commands,
                          call_discovery=expansion, native_source_identity=identity,
                          frozen_native_sources=str(frozen_sources), game_acceptance=False)
            recomp.atomic_json(out / 'build-report.json', report)
            (out / 'build-failure.json').unlink(missing_ok=True)
            if args.run:
                result = execute_native(stage, out, args.wine.absolute(), args.wine_prefix.absolute(), args.budget,
                                        args.run_timeout, args.game_argument, wine_debug=args.wine_debug)
                print(json.dumps(dict(status=result['status'], report=str(out / 'run-report.json'),
                                      events=result['events'][-3:], exit_code=result['exit_code']), indent=2))
                return 3
            print(json.dumps(dict(status=report['status'], report=str(out / 'build-report.json'), functions=report['functions']), indent=2))
            return 0
        except Exception as error:
            recomp.atomic_json(out / 'build-failure.json', dict(status='incomplete', error=str(error), game_acceptance=False))
            print('recomp_native: ' + str(error), file=sys.stderr)
            return 1


if __name__ == '__main__':
    raise SystemExit(main())

"""Narrow retained-artifact adapter. No orchestration, generation, compile or export.

The trusted C# process supplies an immutable request and an output report path.
Ordinary comparison and bounded EH graph comparison remain existing backends.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import subprocess


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def safe(project, name):
    path = Path(name)
    require(path.is_absolute(), 'relative_registered_path')
    require(not any(p.is_symlink() for p in [path, *path.parents]), 'symlink_path')
    path = path.resolve()
    require(any(path.is_relative_to(Path(root).resolve()) and path != Path(root).resolve()
                for root in project['allowed_roots']), 'path_outside_registered_roots')
    return path


LOADED = {}


def read(project, name):
    path = str(safe(project, name))
    require(path in LOADED, 'unbound_input_path')
    return LOADED[path]


def native_eh_symbols(object_bytes):
    """Actual compiler-generated dependencies override any ordinary profile label."""
    from rapid_object.coff import Coff
    from rapid_object.symbol_identity import generated_identity
    return any(generated_identity(sym.name) is not None for sym in Coff(object_bytes).symbols.values())


def run(request):
    project = request['project']
    target = request['build']['config']
    inputs = request['inputs']
    for name, expected in inputs.items():
        # Code implementation paths originate in the trusted engine, not project data.
        data = Path(name).read_bytes()
        require(expected != 'missing' and sha(data) == expected, 'submitted_input_missing_or_changed')
        LOADED[str(Path(name).resolve())] = data
    from rapid_object import compare, eh_native, eh_graph
    from rapid_object.coff import Coff
    from rapid_object.static_crt_identity import inventory_entries
    import capstone

    original = read(project, project['original'])
    inventory = read(project, project['inventory'])
    compiler = read(project, project['compiler'])
    module_hash = sha(original)
    require(module_hash == project['module_sha256'], 'original_module_pin')
    require(sha(compiler) == project['compiler_sha256'], 'compiler_actual_pin')
    inv = json.loads(inventory)
    require(inv['module_sha256'] == module_hash, 'inventory_module_binding')
    reader = eh_graph.Original(original)
    require(inv['image_base'] == reader.pe.image_base, 'inventory_image_base')
    entries = inventory_entries(inventory, module_hash, reader)
    folder = safe(project, target['folder'])
    source, obj = (read(project, str(folder / n)) for n in ('candidate.cpp', 'candidate.obj'))
    build = json.loads(read(project, str(folder / 'run.json')))
    compiler_receipt = json.loads(read(project, str(folder / 'compiler.json')))
    expected_source = request['build'].get('expected_source_sha256')
    require(not expected_source or sha(source) == expected_source, 'imported_candidate_source_binding')
    require(type(build['exit_code']) is int and build['exit_code'] == 0 and
            build['linked'] is False and build['original_executed'] is False, 'unsupported_build_receipt')
    require(build['module_sha256'] == module_hash and build['source_sha256'] == sha(source)
            and build['object_sha256'] == sha(obj), 'retained_build_input_binding')
    require(build['compiler'] == compiler_receipt and compiler_receipt['sha256'] == sha(compiler),
            'compiler_receipt_binding')
    coff = Coff(obj)
    requested, symbols = eh_native.inferred_requests(source, coff, entries, reader)
    require(target['rva'] in requested, 'requested_target_missing_from_source_or_object')
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True

    def requires_eh(data, address):
        return any(op.type == capstone.x86.X86_OP_MEM and op.mem.segment == capstone.x86.X86_REG_FS
                   and op.mem.disp == 0 for ins in md.disasm(data, address) for op in ins.operands)

    needs_eh = target['profile'] == 'eh' or native_eh_symbols(obj)
    for spec in requested.values():
        ranges = spec['ranges']
        for ran in ranges:
            address = reader.pe.image_base + ran['start_rva']
            raw = reader.read(address, ran['end_rva_inclusive'] - ran['start_rva'] + 1, True)
            needs_eh |= requires_eh(raw, address)
    for sec in coff.sections:
        if sec.characteristics & 0x20:
            needs_eh |= requires_eh(sec.data, 0)
    if needs_eh:
        require(project.get('eh_policy') is not None, 'EH_profile_or_FS0_requires_registered_EH_policy')
        pins = json.loads(read(project, project['eh_policy']))
        require(build['flags'] == pins['compiler_flags'], 'EH_selected_flags')
        libraries = {name: read(project, path) for name, path in (project.get('libraries') or {}).items()}
        report = eh_native.check(original, inventory, compiler, libraries, source, obj, build, pins)
        rows = report.get('functions', [])
        require(any(f['rva'] == target['rva'] for f in rows), 'EH_target_not_compared')
        status = ('full_match' if report['status'] == 'exact_eh_graph_match' else
                  'mismatch' if report['status'] == 'eh_graph_nonmatch' else 'inconclusive')
    else:
        require(project.get('compiler_flags') is not None and build['flags'] == project['compiler_flags'],
                'ordinary_selected_flags')
        report = compare.compare_bytes(original, obj, requested, symbols, sha(source), build['compiler'],
                                       module_sha256=module_hash)
        rows = report.get('functions', [])
        require(not report.get('error') and rows and {f['rva'] for f in rows} == set(requested),
                'incomplete_comparison')
        status = ('full_match' if all(f['status'] == 'exact_object_match' for f in rows) else
                  'mismatch' if all(f['status'] in ('nonmatch', 'exact_object_match') for f in rows) else
                  'inconclusive')
    strict_status=status
    certificate=None
    abi_certificate=None
    if not needs_eh and status=='mismatch' and (target.get('allow_encoding_equivalence') is True or target['profile']=='abi_effects'):
        try:
            from tools.replayable.encoding_check import certify_report
            certificate=certify_report(report,project,inputs)
            report['encoding_equivalence']=certificate
            status='encoding_equivalent'
        except (ValueError,KeyError,TypeError,OSError,subprocess.SubprocessError) as exc:
            # No ambiguous compiler action occurs in this host-only checker. A
            # refused optional lane preserves its fresh strict nonmatch outcome.
            report['encoding_refusal']=str(exc) if isinstance(exc,ValueError) else type(exc).__name__
    if not needs_eh and status=='mismatch' and (target.get('allow_abi_effects_equivalence') is True or target['profile']=='abi_effects'):
        try:
            from tools.replayable.abi_effects_check import certify_report
            abi_certificate=certify_report(report,project,inputs)
            report['abi_effects_diagnostic']=abi_certificate
            report['abi_effects_policy_blocker']='pending_user_observation_scope;ordinary_exception_unwinding_not_proved'
        except (ValueError,KeyError,TypeError,OSError,subprocess.SubprocessError) as exc:
            report['abi_effects_refusal']=str(exc) if isinstance(exc,ValueError) else type(exc).__name__
    compact = dict(schema_version=1, status=status, strict_status=strict_status, match_kind=status if status in ('encoding_equivalent','abi_trace_equivalent') else 'exact' if status=='full_match' else 'none', backend=report['backend'],
                   requested_rva=target['rva'], module_sha256=module_hash, source_sha256=sha(source),
                   object_sha256=sha(obj), compiler_sha256=sha(compiler),
                   input_snapshot_sha256=sha(json.dumps(inputs, sort_keys=True).encode()),
                   functions=[{k: f[k] for k in ('rva', 'status', 'original_size', 'object_size', 'counts',
                                                'all_bytes_accounted', 'diagnostics', 'blockers') if k in f}
                              for f in rows],
                   blockers=report.get('blockers', []), fresh_comparison=True, compilation_performed=False,
                   cached_verdict_reused=False, proof=False,
                   scope='pinned retained compiled artifacts and supported full ranges/graphs; external semantics unmodeled',
                   compiler_provenance='retained receipt plus actual registered compiler hash; complete compiler installation closure not attested')
    if certificate is not None:compact['encoding_equivalence']=certificate
    if abi_certificate is not None:compact.update(abi_effects_diagnostic=abi_certificate,abi_effects_acceptance_enabled=False,abi_effects_policy_blocker='pending_user_observation_scope;ordinary_exception_unwinding_not_proved')
    return compact, report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--adapter-root', required=True)
    parser.add_argument('--report-path', required=True)
    args = parser.parse_args()
    sys.path.insert(0, args.adapter_root)
    request = json.load(sys.stdin)
    try:
        compact, report = run(request)
    except (ValueError, KeyError, TypeError, OSError, UnicodeError, ImportError) as exc:
        # No private path, raw source/binary or provider credentials in normal output.
        reason = str(exc) if isinstance(exc, ValueError) and re.fullmatch('[A-Za-z0-9_:+.-]{1,160}', str(exc)) else type(exc).__name__
        compact = dict(schema_version=1, status='inconclusive', blockers=[reason], fresh_comparison=False,
                       compilation_performed=False, cached_verdict_reused=False, proof=False)
        report = compact
    raw = json.dumps(report, sort_keys=True).encode()
    path = Path(args.report_path)
    with path.open('xb') as output:
        output.write(raw)
    compact['report_artifact'] = 'sha256:' + sha(raw)
    print(json.dumps(compact, sort_keys=True))


if __name__ == '__main__':
    main()

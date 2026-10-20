"""Whole-inventory tail-rule applicability analysis; never compiles or accepts sources.

Every inventory identity is accounted for in RVA order. A cheap complete-range
instruction check excludes shapes outside the new linear terminal-jump rule.
Remaining shapes are lifted with the registered SharpRetro runtime and passed to
both actual frontend runtimes. Generated C++ is a hypothesis, not match credit.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def classify(data, pc, decoder):
    import capstone
    from capstone.x86 import X86_OP_IMM
    insns = list(decoder.disasm(data, pc))
    if not insns or sum(i.size for i in insns) != len(data):
        return 'incomplete_disassembly', insns
    last = insns[-1]
    if last.mnemonic != 'jmp' or len(last.operands) != 1 or last.operands[0].type != X86_OP_IMM:
        return 'no_terminal_direct_jump', insns
    if pc <= last.operands[0].imm < pc + len(data):
        return 'internal_terminal_jump', insns
    if any(i.group(capstone.CS_GRP_JUMP) or i.group(capstone.CS_GRP_RET) or i.group(capstone.CS_GRP_IRET) for i in insns[:-1]):
        return 'nonlinear_terminal_jump', insns
    return 'typed_check_required', insns


def frontend(dotnet, runtime, lifted, rva, image_base, image_end, module):
    request = dict(lift=lifted, rva=rva, image_base=image_base, image_end=image_end, module=module)
    run = subprocess.run([dotnet, str(runtime), 'recover-ir'], input=json.dumps(request), text=True,
                         capture_output=True, timeout=30)
    if run.returncode:
        return dict(status='frontend_process_failure', blocker='nonzero_exit:' + str(run.returncode))
    return json.loads(run.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry', type=Path, required=True)
    parser.add_argument('--project', required=True)
    parser.add_argument('--runtime', type=Path, required=True)
    parser.add_argument('--baseline-runtime', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    import capstone
    from rapid_object.compare import PE
    registry = json.loads(args.registry.read_text())
    project = next(p for p in registry['projects'] if p['id'] == args.project)
    original = Path(project['original']).read_bytes()
    inventory_data = Path(project['inventory']).read_bytes()
    inventory = json.loads(inventory_data)
    if sha(original) != project['module_sha256'] or inventory['module_sha256'] != project['module_sha256']:
        raise ValueError('binary_inventory_pin_mismatch')
    pe = PE(original)
    peoff = struct.unpack_from('<I', original, 0x3c)[0]
    image_end = pe.image_base + struct.unpack_from('<I', original, peoff + 24 + 56)[0]
    cfg_path = Path(project['replayable']['lifter_config'])
    cfg = json.loads(cfg_path.read_text())
    resolve = lambda value: Path(value) if Path(value).is_absolute() else cfg_path.parent / value
    lifter = resolve(cfg['adapter_dll'])
    dotnet = cfg.get('dotnet', 'dotnet')
    manifest_path = resolve(cfg['build_manifest'])
    manifest = json.loads(manifest_path.read_text())
    actual_assemblies = {p.name: sha(p.read_bytes()) for p in lifter.parent.glob('*.dll')}
    if actual_assemblies != manifest['assemblies_sha256']:
        raise ValueError('lifter_assembly_manifest_mismatch')
    binding = dict(module_sha256=sha(original), inventory_sha256=sha(inventory_data),
                   runtime_sha256=sha(args.runtime.read_bytes()), baseline_runtime_sha256=sha(args.baseline_runtime.read_bytes()),
                   lifter_manifest_sha256=sha(manifest_path.read_bytes()), lifter_assemblies_sha256=actual_assemblies,
                   scan_implementation_sha256=sha(Path(__file__).read_bytes()), capstone_version=capstone.__version__)
    args.output.mkdir(parents=True, exist_ok=False)
    counts, blockers = Counter(), Counter()
    begin = time.monotonic()
    lifter_process = subprocess.Popen([dotnet, str(lifter)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, text=True, bufsize=1)
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True
    try:
        with (args.output / 'identities.jsonl').open('x') as rows:
            for f in sorted(inventory['functions'], key=lambda f: f['rva']):
                rva = f['rva']
                row = dict(rva=rva, status='unsupported_inventory_ranges', compiled=False, matched=False)
                ranges = f['body_ranges']
                if len(ranges) == 1 and ranges[0]['start_rva'] == rva:
                    try:
                        raw = pe.read(rva, ranges[0]['end_rva_inclusive'] - rva + 1)
                        if len(raw) != f['body_bytes']:
                            raise ValueError('inventory_body_size_disagrees')
                        status, decoded = classify(raw, pe.image_base + rva, md)
                        row['status'] = status
                        if status == 'typed_check_required':
                            payload = dict(hex=raw.hex(), pc=pe.image_base + rva, id=str(rva))
                            lifter_process.stdin.write(json.dumps(payload) + '\n')
                            lifter_process.stdin.flush()
                            lifted = json.loads(lifter_process.stdout.readline())
                            if 'adapter_error' in lifted:
                                row.update(status='lifter_error', blocker=lifted['adapter_error'])
                            elif [(i.address, i.size, i.bytes.hex()) for i in decoded] != [(i['pc'], i['length'], i['raw_hex']) for i in lifted['instructions']]:
                                row['status'] = 'independent_decoder_disagreement'
                            else:
                                candidate = frontend(dotnet, args.runtime, lifted, rva, pe.image_base, image_end, project['module'])
                                row.update(status='typed_unsupported', blocker=candidate.get('blocker', candidate['status']))
                                if candidate['status'] == 'generated':
                                    if candidate['ir']['exit_kind'] != 'tail_call':
                                        raise ValueError('candidate_not_tail_exit')
                                    baseline = frontend(dotnet, args.baseline_runtime, lifted, rva, pe.image_base, image_end, project['module'])
                                    row.update(status='generated_tail_hypothesis', source_sha256=sha(candidate['source'].encode()),
                                               baseline_status=baseline['status'], baseline_blocker=baseline.get('blocker'),
                                               target=candidate['ir']['effects'][-1]['value'])
                                    row.pop('blocker', None)
                    except (ValueError, OSError, KeyError, subprocess.TimeoutExpired) as exc:
                        row.update(status='analysis_failure', blocker=type(exc).__name__ + ':' + str(exc))
                counts[row['status']] += 1
                if 'blocker' in row:
                    blockers[row['blocker']] += 1
                rows.write(json.dumps(row, sort_keys=True) + '\n')
                if sum(counts.values()) % 1000 == 0:
                    rows.flush()
                    print(json.dumps(dict(scanned=sum(counts.values()), total=len(inventory['functions']), generated_tail_hypotheses=counts['generated_tail_hypothesis'])), flush=True)
    finally:
        lifter_process.stdin.close()
        lifter_process.terminate()
        lifter_process.wait(timeout=10)
        lifter_process.stdout.close()
        lifter_process.stderr.close()
    if sha(args.runtime.read_bytes()) != binding['runtime_sha256'] or sha(args.baseline_runtime.read_bytes()) != binding['baseline_runtime_sha256']:
        raise ValueError('frontend_runtime_changed_during_scan')
    report = dict(schema_version=1, binding=binding, inventory_identities=len(inventory['functions']),
                  accounted_identities=sum(counts.values()), counts=dict(counts), blockers=dict(blockers),
                  elapsed_seconds=round(time.monotonic() - begin, 3), vm_compiles=0, comparisons=0,
                  accepted_sources=0, provider_calls=0, proof=False,
                  scope='whole-inventory static preconditions then actual typed-lift/frontend applicability; generated sources remain unchecked hypotheses')
    (args.output / 'summary.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()

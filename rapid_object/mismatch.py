"""Deterministic diagnostics for complete COFF comparison reports, never acceptance.

Labels describe observed decoded differences. Repair causes remain hypotheses;
no operand, target, flags or signedness difference is normalized into equivalence.
The caller must bind and verify artifacts separately before trusting a census.
"""
import argparse
from collections import Counter
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path

SCHEMA_VERSION = 1
MAX_BYTES = 65536
MAX_INSTRUCTIONS = 8192
MAX_ALIGNMENT_PRODUCT = 1000000
PRIMARY_ORDER = (
    'boundary_or_range', 'relocation_resolution', 'unsupported_comparison',
    'unsupported_decode', 'stack_cleanup', 'branch_condition', 'call_target',
    'operand_width', 'instruction_selection', 'stack_displacement',
    'memory_displacement', 'memory_addressing', 'register', 'immediate',
    'control_flow_shape', 'prologue_epilogue', 'larger_structural_difference',
    'encoding_difference', 'unknown',
)
HYPOTHESES = {
    'stack_cleanup': 'Check calling convention, argument count and explicit stack adjustments.',
    'branch_condition': 'Check the source comparison and signedness against original instructions.',
    'call_target': 'Check dependency identity and call declarations.',
    'operand_width': 'Check source operand types and load/store widths.',
    'instruction_selection': 'Check expression structure and actual compiler lowering.',
    'stack_displacement': 'Check frame layout, local sizes and stack-relative accesses.',
    'memory_displacement': 'Check field offsets, indexing and layout hypotheses.',
    'memory_addressing': 'Check pointer/index expression structure and operand roles.',
    'register': 'Check register allocation and expression shape; this is not evidence of a semantic difference alone.',
    'immediate': 'Check constants and arithmetic types against the original.',
}


def tool_binding():
    import capstone
    paths = (Path(__file__), Path(capstone.__file__), Path(capstone._cs._name))
    return {'schema_version': SCHEMA_VERSION, 'capstone': capstone.__version__,
            'max_bytes': MAX_BYTES, 'max_instructions': MAX_INSTRUCTIONS, 'max_alignment_product': MAX_ALIGNMENT_PRODUCT,
            'sha256': {str(p.resolve()): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}


def _decode(data, base):
    from capstone import Cs, CS_ARCH_X86, CS_MODE_32
    if len(data) > MAX_BYTES:
        raise ValueError('diagnostic_byte_budget_exceeded')
    md = Cs(CS_ARCH_X86, CS_MODE_32); md.detail = True
    instructions = []
    for ins in md.disasm(data, base):
        if len(instructions) >= MAX_INSTRUCTIONS:
            raise ValueError('diagnostic_instruction_budget_exceeded')
        operands = []
        for op in ins.operands:
            value = {'type': op.type, 'size': op.size, 'access': op.access}
            if op.type == 1: value['register'] = ins.reg_name(op.reg)
            elif op.type == 2: value['immediate'] = op.imm
            elif op.type == 3:
                mem = op.mem
                value['memory'] = {'segment': ins.reg_name(mem.segment), 'base': ins.reg_name(mem.base),
                                   'index': ins.reg_name(mem.index), 'scale': mem.scale, 'displacement': mem.disp}
            operands.append(value)
        instructions.append({'offset': ins.address - base, 'size': ins.size,
                             'mnemonic': ins.mnemonic, 'operands_text': ins.op_str,
                             'operands': operands, 'bytes_hex': ins.bytes.hex(),
                             'eflags': ins.eflags, 'groups': list(ins.groups),
                             'prefix': list(ins.prefix),
                             'registers_read': [ins.reg_name(r) for r in ins.regs_read],
                             'registers_written': [ins.reg_name(r) for r in ins.regs_write]})
    if sum(i['size'] for i in instructions) != len(data):
        raise ValueError('incomplete_linear_decode')
    return instructions


def _flow(ins):
    name = ins['mnemonic']
    if name.startswith('j') and name != 'jmp': return 'conditional_branch'
    if name.startswith('loop'): return 'conditional_branch'
    if name == 'jmp': return 'jump'
    if name in ('call', 'lcall'): return 'call'
    if name.startswith('ret'): return 'return'
    return None


def _shape(ins):
    return ins['mnemonic'], tuple((o['type'], o['size']) for o in ins['operands'])


def _alignment_shape(ins):
    # This key aligns diagnostic examples only; it never establishes equivalence.
    return _flow(ins) or ins['mnemonic'], tuple(o['type'] for o in ins['operands'])


def _stack_adjustment(ins):
    ops = ins['operands']
    return ins['mnemonic'].startswith('ret') or (ins['mnemonic'] in ('add','sub','lea') and ops and ops[0].get('register') == 'esp')


def _frame_instruction(ins):
    return _stack_adjustment(ins) or ins['mnemonic'] in ('enter','leave') or (
        ins['mnemonic'] in ('push','pop','mov') and any(o.get('register') in ('esp','ebp') for o in ins['operands']))


def _pair_labels(a, b):
    labels = set()
    if a['bytes_hex'] == b['bytes_hex'] and a['operands'] == b['operands']: return labels
    af, bf = _flow(a), _flow(b)
    if af == bf == 'conditional_branch' and a['mnemonic'] != b['mnemonic']:
        labels.add('branch_condition')
    elif a['mnemonic'] != b['mnemonic']:
        labels.add('instruction_selection')
    if _stack_adjustment(a) or _stack_adjustment(b): labels.add('stack_cleanup')
    if len(a['operands']) != len(b['operands']): labels.add('instruction_selection')
    for x, y in zip(a['operands'], b['operands']):
        if x['type'] != y['type']:
            labels.add('instruction_selection'); continue
        if x['size'] != y['size']: labels.add('operand_width')
        if x['type'] == 1 and x['register'] != y['register']:
            labels.add('register')
            if af == bf == 'call': labels.add('call_target')
        elif x['type'] == 2 and x['immediate'] != y['immediate']:
            labels.add('call_target' if af == bf == 'call' else 'control_flow_shape' if af in ('jump','conditional_branch') and bf in ('jump','conditional_branch') else 'immediate')
        elif x['type'] == 3:
            xm, ym = x['memory'], y['memory']
            if xm['displacement'] != ym['displacement']:
                stack = xm['base'] in ('esp','ebp') and ym['base'] in ('esp','ebp')
                labels.add('stack_displacement' if stack else 'memory_displacement')
                if af == bf == 'call': labels.add('call_target')
            if any(xm[k] != ym[k] for k in ('base','index','scale','segment')):
                labels.add('memory_addressing')
                if af == bf == 'call': labels.add('call_target')
    if (a['prefix'],a['eflags'],a['registers_read'],a['registers_written']) != (b['prefix'],b['eflags'],b['registers_read'],b['registers_written']):
        # Differences here are observable decoder metadata; never discard them.
        labels.add('instruction_selection')
    if not labels: labels.add('encoding_difference')
    return labels


def classify_function(entry, example_limit=8):
    """Classify one unchanged comparator function entry, with compact byte-backed offsets.

    Linear decoding and sequence alignment are diagnostic heuristics, not recovered
    CFG/semantics. Inconclusive comparisons are never analyzed as fully relocated.
    """
    if type(example_limit) is not int or not 0 <= example_limit <= 32:
        raise ValueError('invalid_example_limit')
    result = {'rva': entry.get('rva'), 'comparison_status': entry.get('status'),
              'diagnostic_only': True, 'acceptance_changed': False,
              'uncertainty': 'Observed instruction differences; causes and semantics are not established.',
              'primary': 'unknown', 'labels': [], 'examples': [],
              'diagnostics': entry.get('diagnostics', [])}
    status = entry.get('status')
    if status == 'exact_object_match':
        result.update(primary='existing_exact_report', labels=['existing_exact_report']); return result
    if status != 'nonmatch':
        ds = ' '.join(str(d) for d in result['diagnostics'])
        if any(t in ds for t in ('range','boundary','noncontiguous','placement','size_out_of_bounds','function_symbol','function_auxiliary','function_comdat')): label = 'boundary_or_range'
        elif any(t in ds for t in ('relocation','target','unresolved_symbol','absolute_symbol','weak_debug_or_common')): label = 'relocation_resolution'
        elif 'unsupported' in ds or 'requires_' in ds: label = 'unsupported_comparison'
        else: label = 'unknown'
        result.update(primary=label, labels=[label]); return result
    try:
        if 'relocated_bytes_hex' not in entry or 'original_bytes_hex' not in entry:
            raise ValueError('missing_complete_comparison_bytes')
        original = bytes.fromhex(entry['original_bytes_hex']); candidate = bytes.fromhex(entry['relocated_bytes_hex'])
        if not original or not candidate: raise ValueError('empty_comparison_bytes')
        for data, field in ((original,'original_bytes_sha256'),(candidate,'relocated_bytes_sha256')):
            if field in entry and hashlib.sha256(data).hexdigest() != entry[field]:
                raise ValueError('comparison_byte_hash_mismatch')
        base = entry.get('original_va', 0)
        if type(base) is not int or not 0 <= base <= 0xffffffff: raise ValueError('invalid_original_va')
        a, b = _decode(original, base), _decode(candidate, base)
    except (ValueError, TypeError, KeyError) as exc:
        result.update(primary='unsupported_decode', labels=['unsupported_decode'], decode_error=str(exc)); return result
    result['original_instruction_count'], result['candidate_instruction_count'] = len(a), len(b)
    result['same_instruction_shapes'] = [_shape(i) for i in a] == [_shape(i) for i in b]
    labels = set(); pairs = []; structural = []
    if len(a) == len(b) and result['same_instruction_shapes']:
        pairs = list(zip(range(len(a)),range(len(b))))
        result['alignment'] = 'positional_identical_shapes'
    elif len(a)*len(b) > MAX_ALIGNMENT_PRODUCT:
        labels.add('larger_structural_difference')
        result['alignment'] = 'diagnostic_alignment_budget_exceeded'
        result['uncertainty'] += ' Detailed pair alignment was skipped under a fixed budget.'
    else:
        matcher = SequenceMatcher(None, [_alignment_shape(i) for i in a], [_alignment_shape(i) for i in b], autojunk=False)
        result['alignment'] = 'heuristic_sequence_alignment'
        for tag, i, j, k, l in matcher.get_opcodes():
            if j-i == l-k:
                pairs.extend(zip(range(i,j),range(k,l)))
            else:
                labels.add('larger_structural_difference')
                structural.append({'kind':tag,'original_instruction_range':[i,j], 'candidate_instruction_range':[k,l],
                                   'original_offset':a[i]['offset'] if i<len(a) else len(original),
                                   'candidate_offset':b[k]['offset'] if k<len(b) else len(candidate)})
    counts = Counter()
    changed_pairs = 0
    result['paired_instruction_count'] = len(pairs)
    result['unpaired_instruction_counts'] = {'original': len(a)-len(pairs), 'candidate': len(b)-len(pairs)}
    for i,j in pairs:
        one = _pair_labels(a[i],b[j]); labels |= one; counts.update(one)
        changed_pairs += bool(one)
        if one and (_frame_instruction(a[i]) or _frame_instruction(b[j])) and (i<3 or i>=len(a)-3 or j<3 or j>=len(b)-3):
            labels.add('prologue_epilogue')
        if one and len(result['examples']) < example_limit:
            result['examples'].append({'original':a[i], 'candidate':b[j], 'labels':sorted(one)})
    # Different flow-instruction sequence is an observed shape difference, not a
    # claim to reconstruct all edges or distinguish code from inline data.
    flow_a = [(_flow(i), i['mnemonic']) for i in a if _flow(i)]
    flow_b = [(_flow(i), i['mnemonic']) for i in b if _flow(i)]
    if flow_a != flow_b: labels.add('control_flow_shape')
    if len(original) != len(candidate): result['length_difference'] = len(candidate)-len(original)
    if not labels: labels.add('unknown')
    result['labels'] = [k for k in PRIMARY_ORDER if k in labels]
    result['primary'] = result['labels'][0]
    result['changed_instruction_pair_count'] = changed_pairs
    result['changed_pair_label_counts'] = dict(sorted(counts.items()))
    result['structural_examples'] = structural[:example_limit]
    if result['primary'] in HYPOTHESES: result['repair_hypothesis'] = HYPOTHESES[result['primary']]
    return result


def classify_report(report, example_limit=8):
    """Diagnostics only; the incoming report's acceptance statuses are preserved."""
    return {'schema_version': SCHEMA_VERSION, 'diagnostic_only': True,
            'tool_binding': tool_binding(), 'input_report_sha256': hashlib.sha256(json.dumps(report,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'module_sha256': report.get('module_sha256'), 'object_sha256': report.get('object_sha256'),
            'source_sha256': report.get('source_sha256'), 'report_error': report.get('error'),
            'functions': [classify_function(f,example_limit) for f in report.get('functions',[])]}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('report',type=Path);parser.add_argument('--output',type=Path)
    args=parser.parse_args();raw=args.report.read_bytes();result=classify_report(json.loads(raw));result['input_file_sha256']=hashlib.sha256(raw).hexdigest()
    text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.output: args.output.write_text(text)
    else: print(text,end='')

if __name__=='__main__': main()

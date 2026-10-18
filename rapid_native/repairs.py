"""Bounded source-only repair planning from retained compiler comparisons."""
import json
from pathlib import Path
import re


def attempt_numbers(folder):
    numbers=sorted(int(p.name.split('-')[1]) for p in Path(folder).glob('attempt-*') if p.is_dir() and re.fullmatch(r'attempt-[1-9][0-9]*',p.name))
    if numbers and numbers!=list(range(1,numbers[-1]+1)):raise ValueError('attempt_sequence_gap')
    return numbers


def quality(functions):
    return (sum(f['status']=='reccmp_matched' for f in functions),sum((f.get('score') or 0.0) for f in functions))


def progress_decision(attempt,functions,requested,previous,max_repairs=6,stagnation_limit=3,transport_failure=False):
    current=quality(functions);old=tuple(previous.get('quality',[0,0]));stagnation=0
    if attempt>1:stagnation=0 if current>old else previous.get('stagnation',0)+1
    all_matched=current[0]==requested
    repair=not all_matched and attempt<1+max_repairs and stagnation<stagnation_limit and not transport_failure
    reason='all_matched' if all_matched else ('transport_failure' if transport_failure else ('repair_limit' if attempt>=1+max_repairs else ('stagnation_limit' if stagnation>=stagnation_limit else 'repair_pending')))
    return {'quality':list(current),'stagnation':stagnation,'needs_repair':repair,'stop_reason':reason}


def feedback_for(folder,remaining,best,last_attempt):
    folder=Path(folder);rvas={f['rva'] for f in remaining};best_by_rva={f['rva']:f for f in best};sources={};functions=[];diagnostics=[]
    for rva in sorted(rvas):
        selected=best_by_rva.get(rva);record={'rva':rva,'best_result':({k:selected.get(k) for k in ('rva','original_va','score','status','unknowns','source','summary','original_size_used','recompiled_size')} if selected else None)}
        if selected and selected.get('operand_differences'):record['actual_operand_differences']=selected['operand_differences'][:2]
        if selected:
            source=Path(selected['source']);sources[str(source)]=source.read_text()
            diff=Path(selected['summary']).parent/f"diff-{selected.get('original_va',0):08x}.txt"
            if diff.exists():record['actual_best_diff']=re.sub(r'\x1b\[[0-9;]*m','',diff.read_text())[:2500]
        functions.append(record)
    latest=folder/f'attempt-{last_attempt}'
    if (latest/'candidate.cpp').exists():sources[str(latest/'candidate.cpp')]=(latest/'candidate.cpp').read_text()
    for path in sorted(latest.glob('build-*/*')):
        if path.name in ('build.log','compare.log'):
            diagnostics.append(path.name+'\n'+path.read_text(errors='replace')[:6000])
    return {'instruction':'Return ONLY currently requested unmatched functions, with required class declarations and out-of-line definitions. Omit matched definitions and every unrequested function from previous source files. Use each selected best source with its corresponding actual best diff; latest compiler/compare logs may explain failures. Native C++98 only; no assembly, fixtures, wrappers or success stubs. Several bounded repair attempts are available, but every output must make a concrete change justified by these observed differences.',
        'best_sources':sources,'functions':functions,'latest_diagnostics':'\n'.join(diagnostics)[:12000],'previous_attempt':last_attempt}

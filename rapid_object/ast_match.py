"""Bounded AST comparison hypotheses; only the unchanged exact comparator accepts.

No mutation is semantic evidence. Every nonmatch remains UNVALIDATED. Source
edits use byte offsets from a complete target-aware parse, never text guesses.
"""
import argparse
from collections import Counter
import copy
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from . import ghidra_compile_fix as fix
from . import ghidra_state_fix as state
from rapid.factory import REPO
from rapid.packets import PIN
from workers.deepseek_packet import atomic, sha

ROOT = REPO / 'local/matching-frontier-002'
OPS = {'!=': ['>', '<', '==', '<=', '>='], '==': ['<=', '>=', '!=', '<', '>'],
       '<': ['<=', '>', '>=', '==', '!='], '<=': ['<', '>=', '>', '==', '!='],
       '>': ['>=', '<', '<=', '==', '!='], '>=': ['>', '<=', '<', '==', '!=']}


def parse(source, folder, name='parse'):
    folder = Path(folder); folder.mkdir(parents=True, exist_ok=True)
    path = folder / (name + '.cpp'); path.write_bytes(source.encode())
    tool = shutil.which('clang++')
    if not tool: raise ValueError('clang_unavailable')
    result = subprocess.run([tool, *fix.CLANG_FLAGS, str(path.resolve())], capture_output=True, timeout=30)
    (folder / (name + '.stderr')).write_bytes(result.stderr)
    if path.read_bytes() != source.encode(): raise ValueError('parse_source_changed')
    if result.returncode: raise ValueError('incomplete_parse')
    ast = json.loads(result.stdout)
    if ast.get('kind') != 'TranslationUnitDecl': raise ValueError('missing_translation_unit')
    return ast


def proposals(source, ast, limit=8):
    """Single-site integer comparison operators and pure operand orientation only."""
    if not 1 <= limit <= 8: raise ValueError('variant_budget')
    raw = source.encode(); masked = fix.mask(source).encode()
    # The existing masker preserves character offsets; require ASCII so those are bytes.
    if not source.isascii(): raise ValueError('non_ascii_source')
    aliases = {n['name']: n['type']['qualType'] for n in fix.walk(ast)
               if n.get('kind') == 'TypedefDecl' and 'name' in n and 'type' in n}
    sites = []
    for node in fix.walk(ast):
        if node.get('kind') != 'BinaryOperator' or node.get('opcode') not in OPS: continue
        children = node.get('inner', [])
        if len(children) != 2: continue
        if any(fix.type_kind(c.get('type', {}).get('qualType', ''), aliases) != 'integer32' for c in children): continue
        span = fix.offsets(node); left, right = map(fix.offsets, children)
        if not span or not left or not right: continue
        a, b = span
        if not (0 <= a == left[0] < left[1] <= right[0] < right[1] == b <= len(raw)): continue
        # Macro ranges are not editable spelling ranges.
        if any('expansionLoc' in loc or 'spellingLoc' in loc for n in fix.walk(node) for loc in n.get('range', {}).values()): continue
        gap = masked[left[1]:right[0]]; op = node['opcode'].encode()
        matches = list(re.finditer(rb'(?<![<>=!])' + re.escape(op) + rb'(?![=])', gap))
        if len(matches) != 1: continue
        loc = left[1] + matches[0].start()
        if raw[loc:loc+len(op)] != op: continue
        before = raw[a:b].decode(); lhs = raw[left[0]:left[1]].decode(); rhs = raw[right[0]:right[1]].decode()
        zero = any(n.get('kind') == 'IntegerLiteral' and n.get('value') == '0' for n in fix.walk(node))
        pure = not any(n.get('kind') in ('CallExpr','CXXMemberCallExpr','CXXOperatorCallExpr','CompoundAssignOperator') or n.get('opcode') in ('++','--','=') or 'volatile' in n.get('type',{}).get('qualType','') for n in fix.walk(node))
        target_type = 'int' if all(fix.canonical_type(c['type']['qualType'],aliases).startswith('unsigned ') for c in children) else 'unsigned int'
        sites.append((not zero, a, loc, op, before, lhs, rhs, b, pure, target_type))
    groups = []
    for zero_last, a, loc, op, before, lhs, rhs, b, pure, target_type in sorted(sites):
        group=[]
        # VC8 retains unsigned ordered-zero branches which a guessed signed
        # nonzero expression loses. These remain hypotheses until exact matching.
        if not zero_last and rhs.strip() == '0' and op.decode() in ('!=','=='):
            ordered='>' if op==b'!=' else '<='
            group.append({'kind':'unsigned_ordered_zero_hypothesis','start':a,'end':b,'before':before,'replacement':'((unsigned int)('+lhs+')) '+ordered+' 0u'})
        for new in OPS[op.decode()]:
            group.append({'kind':'integer_comparison_hypothesis','start':loc,'end':loc+len(op),'before':op.decode(),'replacement':new,'expression':before})
        if op.decode() in ('<','<=','>','>='):
            group.insert(1,{'kind':'integer_comparison_signedness_hypothesis','start':a,'end':b,'before':before,'replacement':'(('+target_type+')('+lhs+')) '+op.decode()+' (('+target_type+')('+rhs+'))'})
        if pure:
            reverse={'<':'>','<=':'>=','>':'<','>=':'<=','==':'==','!=':'!='}[op.decode()]
            group.append({'kind':'pure_comparison_orientation','start':a,'end':b,'before':before,'replacement':'('+rhs+') '+reverse+' ('+lhs+')'})
        groups.append(group)
    # Round robin across sites avoids spending the whole budget on one comparison.
    seen = {sha(raw)}; out = []
    for i in range(8):
        for group in groups:
            if i >= len(group): continue
            edit = group[i]; changed = raw[:edit['start']] + edit['replacement'].encode() + raw[edit['end']:]
            digest = sha(changed)
            if digest in seen: continue
            seen.add(digest); out.append({'source':changed.decode(),'source_sha256':digest,'edit':edit,'status':'UNVALIDATED'})
            if len(out) == limit: return out
    return out


def baseline(case):
    source = Path(case['source']).read_text(); report = json.loads(Path(case['summary']).read_text())
    if sha(source.encode()) != case['source_sha256'] or report['source_sha256'] != case['source_sha256']: raise ValueError('baseline_source_identity')
    obj = Path(case['summary']).parent/'candidate.obj'
    if not obj.is_file() or sha(obj.read_bytes()) != report['object_sha256']: raise ValueError('baseline_object_identity')
    if report.get('module_sha256') != PIN or len(report['functions']) != 1 or report['functions'][0]['rva'] != case['rva']: raise ValueError('baseline_identity')
    current = fix.tool_bindings()
    if report['implementation_sha256'] != {k:current['code_sha256'][k] for k in ('coff.py','compare.py')} or report['compiler']['sha256'] != current['expected_cl_sha256']: raise ValueError('baseline_tool_identity')
    return source, report


def stratified(cases, count):
    buckets = {}
    for c in sorted(cases,key=lambda x:x['rva']):
        key=(next((n for n in (32,64,128,512) if c['size']<=n),1024), min(c.get('relocations',0),2))
        buckets.setdefault(key,[]).append(c)
    out=[]
    while len(out)<count and any(buckets.values()):
        for key in sorted(buckets):
            if buckets[key] and len(out)<count:out.append(buckets[key].pop(0))
    return out


def prepare(root=ROOT):
    root = Path(root); census = json.loads((REPO/'local/matching-frontier-001/retained-census.json').read_text())
    candidates = [dict(c, category='near') for c in census['near_candidates'] if c['size'] >= 24]
    # Controls are immutable retained exact sources selected independently of mutation support.
    controls = []
    for p in sorted((REPO/'local/deterministic-compile-001/sweep').glob('*/build/summary.json')):
        r = json.loads(p.read_text()); f = r.get('functions',[])
        src = p.parent.parent/'candidate.cpp'
        if len(f)==1 and f[0]['status']=='exact_object_match' and src.is_file():
            controls.append({'rva':f[0]['rva'],'size':f[0]['original_size'],'source':str(src),'summary':str(p),'source_sha256':r['source_sha256'],'category':'control'})
    selected=[]; deferred=[]
    for c in candidates:
        folder = root/'prepare'/f"{c['rva']:08x}"
        try:
            source,_=baseline(c); ast=parse(source,folder); variants=proposals(source,ast,4)
            if not variants: raise ValueError('no_supported_integer_comparison')
            c['variant_count']=len(variants);c['variant_limit']=4;selected.append(c)
            atomic(folder/'proposals.json', {'variants':variants,'baseline':c})
        except ValueError as e: deferred.append({'case':c,'reason':str(e)})
    # All supported near cases, at most 100; deterministic stratification over RVA.
    selected=stratified(selected,100)
    atomic(root/'plan.json',{'cases':stratified(controls,10)+selected,'deferred':deferred,'bindings':fix.tool_bindings(),'pilot_sha256':sha(Path(__file__).read_bytes()),'paid_provider_calls':0})
    return {'eligible':len(selected),'deferred':len(deferred),'controls':min(10,len(controls))}


def evaluate(case, root):
    from .build import build_and_compare
    folder=Path(root)/'pilot'/f"{case['rva']:08x}";folder.mkdir(parents=True,exist_ok=True)
    source, report=baseline(case); started=time.time(); base=folder/'baseline.cpp'
    if base.exists() and base.read_bytes()!=source.encode():raise ValueError('retained_baseline_changed')
    base.write_bytes(source.encode()); ast=parse(source,folder,'baseline-parse')
    variants=proposals(source,ast,case.get('variant_limit',8)) if case['category']!='control' else [{'source':source,'source_sha256':sha(source.encode()),'edit':None}]
    record={'rva':case['rva'],'category':case['category'],'baseline':case,'attempts':[],'status':'UNVALIDATED','paid_provider_calls':0}
    # Reuse the existing full-range report cache validation, including immutable source/object/compiler bindings.
    current=state.bindings(); raw={'module_sha256':PIN,'rva':case['rva'],**report['requested'][str(case['rva'])]}
    registry={}
    for name,address in report['symbol_addresses'].items():
        found=re.search(r'(?:^|[?_])(fn|g)_([0-9a-fA-F]{8})(?=@|$)',name)
        if found:registry[found[1]+'_'+found[2].lower()]=address
    seen_objects={report['functions'][0].get('object_bytes_hex')}
    for n,v in enumerate(variants):
        attempt=folder/f'variant-{n:02d}';attempt.mkdir(exist_ok=True);path=attempt/'candidate.cpp'
        if path.exists() and path.read_bytes()!=v['source'].encode():raise ValueError('cached_variant_source_changed')
        path.write_bytes(v['source'].encode())
        parse(v['source'],attempt)
        output=attempt/'build';summary_path=output/'summary.json'
        if summary_path.exists(): summary=json.loads(summary_path.read_text())
        elif output.exists(): raise ValueError('interrupted_build_retained')
        else:
            with (REPO/'local/rapid-object/vm-build.lock').open('a+') as lock:
                fcntl.flock(lock,fcntl.LOCK_EX)
                summary=build_and_compare(path,output,{case['rva']:copy.deepcopy(raw)},registry)
        build=summary.get('build',{});obj=output/'candidate.obj';valid=False
        if build.get('exit_code')==0 and obj.is_file():
            valid=state.report_bound(summary,case,raw,v['source_sha256'],sha(obj.read_bytes()),build,current) and build.get('source_sha256')==v['source_sha256'] and build.get('object_sha256')==sha(obj.read_bytes()) and json.loads((output/'run.json').read_text())==build and sha(path.read_bytes())==v['source_sha256']
        status=summary['functions'][0]['status'] if valid else 'inconclusive'
        machine=summary.get('functions',[{}])[0].get('object_bytes_hex') if summary.get('functions') else None
        record['attempts'].append({'variant':n,'edit':v['edit'],'source_sha256':v['source_sha256'],'summary':str(summary_path),'bound':bool(valid),'status':status,'compiled_identical':machine in seen_objects,'elapsed_seconds':build.get('elapsed_seconds')})
        if machine:seen_objects.add(machine)
        atomic(attempt/'attempt.json',record['attempts'][-1])
        if valid and status=='exact_object_match':
            record.update(status=status,accepted_source=str(path),accepted_source_sha256=v['source_sha256'],matched_bytes=summary['functions'][0]['original_size']);break
    record['elapsed_seconds']=round(time.time()-started,3);atomic(folder/'result.json',record);return record


def run(root=ROOT,max_cases=0):
    root=Path(root);owner=(root/'owner.lock').open('a+');fcntl.flock(owner,fcntl.LOCK_EX|fcntl.LOCK_NB)
    plan=json.loads((root/'plan.json').read_text())
    if plan['pilot_sha256']!=sha(Path(__file__).read_bytes()) or plan['bindings']!=fix.tool_bindings():raise ValueError('plan_tool_changed')
    started=time.time();records=[]
    for c in plan['cases'][:max_cases or None]:
        records.append(evaluate(c,root));near=[r for r in records if r['category']=='near'];controls=[r for r in records if r['category']=='control']
        value={'pid':os.getpid(),'completed':len(records),'near_completed':len(near),'controls_completed':len(controls),'new_distinct_exact_matches':sum(r['status']=='exact_object_match' for r in near),'matched_body_bytes':sum(r.get('matched_bytes',0) for r in near),'attempts':sum(len(r['attempts']) for r in records),'compiled_identical':sum(a['compiled_identical'] for r in records for a in r['attempts']),'controls_exact':sum(r['status']=='exact_object_match' for r in controls),'elapsed_seconds':round(time.time()-started,3),'paid_provider_calls':0,'proof':False,'records':records}
        atomic(root/'STATUS.json',value)
    return {k:v for k,v in value.items() if k!='records'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['prepare','run']);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--max-cases',type=int,default=0);a=p.parse_args()
    print(json.dumps(prepare(a.root) if a.command=='prepare' else run(a.root,a.max_cases),indent=2))

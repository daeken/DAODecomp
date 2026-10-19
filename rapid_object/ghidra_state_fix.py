"""Additive, byte-backed native FS DWORD lowering; other unknown state stays unknown."""
from collections import Counter
from functools import lru_cache
from pathlib import Path
import copy
import fcntl
import json
import re
import signal
import time
from . import ghidra_compile_fix as fix
from . import ghidra_seed as seed
from rapid.factory import REPO,MAIN
from rapid.packets import PIN
from workers.deepseek_packet import atomic,encode,sha

ROOT=REPO/'local/toolkit-evolution-002'
STATE=re.compile(r'\b(?:in_|unaff_|extraout_|unaff_retaddr|register0x)\w*')
INTRINSICS='''extern "C" unsigned long __readfsdword(unsigned long);
extern "C" void __writefsdword(unsigned long,unsigned long);
#pragma intrinsic(__readfsdword)
#pragma intrinsic(__writefsdword)
'''


@lru_cache(maxsize=1)
def image():
    import pefile
    data=(MAIN/'gamedata/bin_ship/DAOrigins.exe').read_bytes()
    if sha(data)!=PIN:raise ValueError('original_pin')
    return pefile.PE(data=data,fast_load=True)


def instruction_evidence(record,pe=None):
    """Decode every retained range. Only explicit native FS DWORD MOVs at offset zero."""
    from capstone import Cs,CS_ARCH_X86,CS_MODE_32,CS_OP_MEM,CS_AC_READ,CS_AC_WRITE
    from capstone.x86 import X86_REG_FS
    if record.get('module_sha256')!=PIN:raise ValueError('original_identity')
    pe=pe or image();md=Cs(CS_ARCH_X86,CS_MODE_32);md.detail=True;rows=[];parts=[]
    for rr in record['ranges']:
        start=rr['start_rva'];size=rr['end_rva_inclusive']-start+1;data=pe.get_data(start,size);parts.append(data);ins=list(md.disasm(data,record.get('image_base',0x400000)+start))
        if size<=0 or len(data)!=size or sum(i.size for i in ins)!=size:raise ValueError('incomplete_original_decode')
        for i in ins:
            for op in i.operands:
                if op.type!=CS_OP_MEM or op.mem.segment!=X86_REG_FS:continue
                row={'address':i.address,'bytes':i.bytes.hex(),'mnemonic':i.mnemonic,'operands':i.op_str,'read':bool(op.access&CS_AC_READ),'write':bool(op.access&CS_AC_WRITE)};rows.append(row)
                if i.mnemonic!='mov' or op.size!=4 or op.mem.base or op.mem.index or op.mem.disp!=0 or row['read']==row['write']:raise ValueError('unsupported_original_fs_access')
    if sha(b''.join(parts))!=record['bytes_sha256']:raise ValueError('original_range_hash')
    return {'instructions':rows,'reads':sum(r['read'] for r in rows),'writes':sum(r['write'] for r in rows),'bytes_sha256':record['bytes_sha256']}


def lower_fs0(record,evidence):
    """No values are invented: every pseudo-base use must be a matched FS:[0] access."""
    out=copy.deepcopy(record);source=record.get('draft') or '';code=fix.mask(source)
    tokens=set(STATE.findall(code))
    if tokens!={'unaff_FS_OFFSET'}:raise ValueError('other_or_missing_unmodeled_state')
    # Only the observed scalar DWORD pointer form. No arrays, aliases or address-taking.
    declarations=list(re.finditer(r'(?m)^\s*(int|uint|undefined4)\s*\*\s*unaff_FS_OFFSET\s*;',code))
    if len(declarations)!=1:raise ValueError('unsupported_fs_declaration')
    value_type=declarations[0].group(1)
    if value_type!='int':
        aliases=re.findall(r'\btypedef\s+([^;{}]+?)\s+'+value_type+r'\s*;',fix.mask(record.get('type_declarations_hypothesis','')))
        if len(aliases)!=1 or ' '.join(aliases[0].split())!='unsigned int':raise ValueError('unsupported_fs_value_type')
    changes=[{'kind':'fs_pseudobase_declaration','start':declarations[0].start(),'end':declarations[0].end(),'replacement':''}];reads=0;writes=0
    occupied=[(declarations[0].start(),declarations[0].end())]
    # Writes must be complete standalone statements. Compound/nested assignments remain unknown.
    for m in re.finditer(r'(?m)^[ \t]*\*\s*unaff_FS_OFFSET\s*=\s*([^;\n]+);',code):
        rhs=source[m.start(1):m.end(1)]
        if re.search(r'(?<![=!<>])=(?!=)|\+\+|--',fix.mask(rhs)):raise ValueError('unsupported_fs_write_expression')
        changes.append({'kind':'fs_dword_write_zero','start':m.start(),'end':m.end(),'replacement':'  __writefsdword(0,(unsigned long)('+rhs+'));'});occupied.append((m.start(),m.end()));writes+=1
    for m in re.finditer(r'\*\s*unaff_FS_OFFSET\b',code):
        if any(a<=m.start()<b for a,b in occupied):continue
        # No lvalue/compound assignment, indexing, address-taking or subpiece use.
        before=code[:m.start()].rstrip();after=code[m.end():].lstrip()
        if before.endswith(('*','&','++','--')) or after.startswith(('[','.','++','--')) or re.match(r'(?:[+*/%&|^<>-]*=(?!=))',after):raise ValueError('unsupported_fs_lvalue')
        changes.append({'kind':'fs_dword_read_zero','start':m.start(),'end':m.end(),'replacement':'(('+value_type+')__readfsdword(0))'});occupied.append((m.start(),m.end()));reads+=1
    for m in re.finditer(r'\bunaff_FS_OFFSET\b',code):
        if not any(a<=m.start()<b for a,b in occupied):raise ValueError('unconsumed_fs_base_use')
    if reads!=evidence['reads'] or writes!=evidence['writes'] or not reads or not writes:raise ValueError('fs_access_count_mismatch')
    for c in sorted(changes,key=lambda x:x['start'],reverse=True):source=source[:c['start']]+c['replacement']+source[c['end']:]
    out['draft']=source;out['type_declarations_hypothesis']=record.get('type_declarations_hypothesis','')+'\n'+INTRINSICS
    return out,changes


@lru_cache(maxsize=1)
def decoder_bindings():
    import capstone,pefile
    return {'capstone':capstone.__version__,'pefile':pefile.__version__,'requirements_sha256':sha((REPO/'requirements-native.txt').read_bytes())}


def bindings():
    return {'state_fix_sha256':sha(Path(__file__).read_bytes()),'compile_fix':fix.tool_bindings(),'decoder':decoder_bindings()}


def repair(record,folder,baseline_source=None,evidence=None):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    try:
        evidence=evidence or instruction_evidence(record);changed,changes=lower_fs0(record,evidence)
    except ValueError as e:
        result={'schema_version':1,'rva':record['rva'],'module_sha256':record.get('module_sha256'),'status':'no_source','source':None,'source_sha256':None,'diagnostics':[str(e)],'changes':[],'paid_requests':0};atomic(folder/'state-repair.json',result);return result
    atomic(folder/'lowered-export.json',changed);result=fix.repair(changed,folder/'compile-fix',baseline_source)
    result={**result,'state_changes':changes,'original_instruction_evidence':evidence,'tool_bindings':bindings()}
    if result.get('source') is not None:(folder/'candidate.cpp').write_bytes(result['source'].encode())
    atomic(folder/'state-repair.json',result);return result


def census(root=ROOT):
    root=Path(root);root.mkdir(parents=True,exist_ok=True);cases=fix.inventory();rows=[];tokens=Counter();groups=Counter();ready=[]
    compiled={}
    for p in (REPO/'local/deterministic-compile-001/sweep').glob('*/result*.json'):
        r=json.loads(p.read_text())
        if r.get('compile_success'):compiled[r['rva']]=r
    for case in cases:
        if case['rva'] in compiled:continue
        raw=json.loads(Path(case['raw_export']).read_text());ts=sorted(set(STATE.findall(fix.mask(raw.get('draft') or ''))))
        if not ts:continue
        tokens.update(ts);group='other_incoming_or_call_state'
        if ts==['unaff_FS_OFFSET']:
            try:
                ev=instruction_evidence(raw);_,changes=lower_fs0(raw,ev);group='supported_fs0';ready.append(case)
            except ValueError as e:group=str(e)
        groups[group]+=1;rows.append({'rva':case['rva'],'tokens':ts,'category':group,'raw_export':case['raw_export']})
    value={'module_sha256':PIN,'observed':len(cases),'blocked_state':len(rows),'token_functions':tokens.most_common(),'categories':dict(groups),'rows':rows,'supported_cases':ready,'paid_requests':0,'tool_bindings':bindings()};atomic(root/'state-census.json',value)
    controls=[c for c in cases if c['category']=='control'];selected=fix.stratified(ready,80)+fix.stratified(controls,20)
    for case in selected:case['category']='control' if case['category']=='control' else 'fs0'
    atomic(root/'pilot-selection.json',{'cases':selected,'tool_bindings':bindings(),'paid_requests':0});atomic(root/'sweep-plan.json',{'cases':ready,'tool_bindings':bindings(),'paid_requests':0,'launched':False});(root/'sweep.paused').write_text('paused until independent review\n')
    return {k:v for k,v in value.items() if k not in ('rows','supported_cases')}


def proposal_for(case,folder):
    raw=json.loads(Path(case['raw_export']).read_text());baseline=Path(case['source']).read_text() if case.get('source') else None
    if case['category']=='control':
        proposal=fix.repair(raw,folder/'control-fix',baseline)
        if proposal.get('source') is not None:(folder/'candidate.cpp').write_bytes(proposal['source'].encode())
        return proposal
    return repair(raw,folder,baseline)


def report_bound(report,case,raw,source_sha,obj_sha,build,current):
    req=report.get('requested',{});functions=report.get('functions',[])
    return set(req)=={str(case['rva'])} and all(req[str(case['rva'])].get(k)==raw.get(k) for k in ('original_va','ranges','bytes_sha256')) and report.get('module_sha256')==PIN and report.get('source_sha256')==source_sha and report.get('object_sha256')==obj_sha and report.get('compiler')==build.get('compiler') and (build.get('compiler') or {}).get('sha256')==current['compile_fix']['expected_cl_sha256'] and report.get('implementation_sha256')=={n:current['compile_fix']['code_sha256'][n] for n in ('coff.py','compare.py')} and len(functions)==1 and functions[0].get('rva')==case['rva']


def evaluate(case,root):
    from .build import build_and_compare
    fix.verify_baseline(case);folder=Path(root)/f"{case['rva']:08x}";folder.mkdir(parents=True,exist_ok=True);path=folder/'result.json';current=bindings()
    if path.exists():
        cached=json.loads(path.read_text())
        if cached['baseline']!=case:raise ValueError('state_cache_baseline_changed')
        if cached['tool_bindings']!=current:
            # Queue/binding-only edits may reuse historical builds only after exact
            # reproduction under the current complete source recipe and dependencies.
            check=folder/'resume-check'/sha(encode(current));check.mkdir(parents=True,exist_ok=True);proposal=proposal_for(case,check)
            if proposal.get('source_sha256')!=cached.get('source_sha256') or proposal['status']!=cached['repair_status']:raise ValueError('state_recipe_changed_use_new_root')
            if proposal.get('source') is not None and sha((check/'candidate.cpp').read_bytes())!=cached['source_sha256']:raise ValueError('state_regenerated_source_binding')
            cached={**cached,'resume_verified_tool_bindings':current,'resume_verification':str(check)}
        raw=json.loads(Path(case['raw_export']).read_text())
        if cached.get('source_sha256') and (not (folder/'candidate.cpp').is_file() or sha((folder/'candidate.cpp').read_bytes())!=cached['source_sha256']):raise ValueError('state_cache_source_changed')
        if cached.get('compile_success'):
            report=json.loads(Path(cached['summary']).read_text());obj=Path(cached['summary']).parent/'candidate.obj';req=report.get('requested',{}).get(str(case['rva']),{});build=cached['build']
            if not Path(cached['summary']).resolve().is_relative_to(folder.resolve()) or not obj.is_file() or not report_bound(report,case,raw,cached['source_sha256'],sha(obj.read_bytes()),build,current) or report.get('functions')!=cached['comparison_functions'] or cached.get('matching_status')!=report['functions'][0]['status'] or build.get('exit_code')!=0 or build.get('source_sha256')!=cached['source_sha256'] or build.get('object_sha256')!=sha(obj.read_bytes()) or build.get('module_sha256')!=PIN or json.loads((obj.parent/'run.json').read_text())!=build:raise ValueError('state_cache_artifact_binding')
        return cached
    raw=json.loads(Path(case['raw_export']).read_text());started=time.time()
    proposal=proposal_for(case,folder)
    result={'schema_version':1,'rva':case['rva'],'category':case['category'],'baseline_status':case['baseline_status'],'baseline':case,'tool_bindings':current,'source_sha256':proposal.get('source_sha256'),'repair_status':proposal['status'],'diagnostics':proposal.get('diagnostics',[]),'compile_success':False,'matching_status':None,'comparison_functions':[],'paid_requests':0}
    if proposal.get('source') is not None:
        source=folder/'candidate.cpp';requested={case['rva']:{k:raw[k] for k in ('original_va','ranges','bytes_sha256')}};summary=None
        # Known transport-only failure can retry retained source once; all receipts retained.
        for attempt in range(2):
            output=folder/('build' if attempt==0 else 'build-transport-retry-1')
            if output.exists():raise ValueError('interrupted_state_build_no_reset')
            with (REPO/'local/rapid-object/vm-build.lock').open('a+') as lock:
                fcntl.flock(lock,fcntl.LOCK_EX);summary=build_and_compare(source,output,requested,proposal['symbol_addresses'])
            build=summary.get('build') or {}
            if not (build.get('exit_code')==255 and build.get('compiler') is None and not build.get('object_sha256')):break
        obj=output/'candidate.obj';compiled=build.get('exit_code')==0 and (build.get('compiler') or {}).get('sha256')==current['compile_fix']['expected_cl_sha256'] and build.get('source_sha256')==result['source_sha256'] and build.get('module_sha256')==PIN and sha(source.read_bytes())==result['source_sha256'] and obj.is_file() and sha(obj.read_bytes())==build.get('object_sha256')
        result.update(build=build,compile_success=bool(compiled),summary=str(output/'summary.json'),comparison_functions=summary.get('functions',[]),matching_status=summary['functions'][0]['status'] if compiled and report_bound(summary,case,raw,result['source_sha256'],build['object_sha256'],build,current) else None,error=summary.get('error'),transport_retries=attempt)
        log=output/'build.log';result['compiler_errors']=re.findall(r'error (C\d+)\s*:\s*([^\n]+)',log.read_text(errors='replace')) if log.is_file() else []
    result['elapsed_seconds']=round(time.time()-started,3);atomic(path,result);return result


def summarize(records,started):
    value=fix.summarize(records,started);value['tool_bindings']=bindings();value['source_emitted']=sum(bool(r.get('source_sha256')) for r in records);value['transport_retries']=sum(r.get('transport_retries',0) for r in records);return value


def run(root=ROOT,sweep=False,resume=False,max_cases=0):
    root=Path(root);plan=json.loads((root/('sweep-plan.json' if sweep else 'pilot-selection.json')).read_text());owner=(root/'owner.lock').open('a+');fcntl.flock(owner,fcntl.LOCK_EX|fcntl.LOCK_NB);records=[];started=time.time();stop=False
    def stopping(*args):
        nonlocal stop
        stop=True
    old=signal.signal(signal.SIGTERM,stopping)
    try:
        if sweep and resume:(root/'sweep.paused').unlink(missing_ok=True)
        for case in plan['cases']:
            if stop or (sweep and (root/'sweep.paused').exists()) or (max_cases and len(records)>=max_cases):break
            area='pilot' if not sweep or (root/'pilot'/f"{case['rva']:08x}"/'result.json').exists() else 'sweep'
            records.append(evaluate(case,root/area));atomic(root/('sweep-status.json' if sweep else 'pilot-results.json'),summarize(records,started))
        if stop:(root/'sweep.paused').write_text('stopped after retained build\n')
        return summarize(records,started)
    finally:signal.signal(signal.SIGTERM,old);fcntl.flock(owner,fcntl.LOCK_UN);owner.close()


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['census','pilot','sweep','pause']);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--resume',action='store_true');p.add_argument('--max-cases',type=int,default=0);a=p.parse_args()
    if a.command=='census':value=census(a.root)
    elif a.command=='pause':(a.root/'sweep.paused').write_text('operator pause\n');value={'paused':True}
    else:value=run(a.root,a.command=='sweep',a.resume,a.max_cases)
    print(json.dumps(value,indent=2))

"""Additive deterministic compile repairs; baseline seed sweep and acceptance stay unchanged."""
from collections import Counter,defaultdict
import copy
from functools import lru_cache
import json
from pathlib import Path
import re
import shutil
import subprocess
import time
from . import ghidra_seed as seed
from rapid.factory import REPO
from rapid.packets import PIN
from workers.deepseek_packet import atomic,encode,sha

ROOT=REPO/'local/deterministic-compile-001'
BASELINE=REPO/'local/cost-reduction-001/full-seed'
CLANG_FLAGS=['-target','i686-pc-windows-msvc','-fms-extensions','-fms-compatibility-version=14','-std=c++98','-fsyntax-only','-ferror-limit=0','-Wno-everything','-Xclang','-ast-dump=json']


def mask(text):
    return ''.join(''.join('\n' if c=='\n' else ' ' for c in m.group()) if m.group().startswith(('//','/*','"',"'")) else m.group() for m in seed.TOKENS.finditer(text))


def split_parameters(text):
    result=[];depth=0;start=0
    for i,c in enumerate(mask(text)):
        if c in '([':depth+=1
        elif c in ')]':depth-=1
        elif c==',' and depth==0:result.append(text[start:i].strip());start=i+1
        if depth<0:raise ValueError('unbalanced_parameter_list')
    if depth:raise ValueError('unbalanced_parameter_list')
    result.append(text[start:].strip());return result


def receiver_spacing(record):
    """Repair the old converter's comma-crossing receiver parse, without changing the draft body."""
    text=record.get('draft') or '';header,sep,_=text.partition('{')
    if not sep or '__thiscall' not in mask(header):return record,[]
    own=[s for s in record.get('symbols',[]) if s.get('kind')=='function' and s.get('rva')==record['rva']]
    if not own:return record,[]
    found=re.search(r'(?<!\w)'+re.escape(own[0]['token'])+r'\s*\(',mask(header))
    if not found:return record,[]
    end=header.rfind(')');params=header[found.end():end];parts=split_parameters(params)
    if not parts:return record,[]
    first=parts[0];formal=re.fullmatch(r'\s*(.+?)([A-Za-z_]\w*)\s*',first)
    if not formal:return record,[]
    typ,name=formal.groups();typ=typ.strip()
    if not typ or '(' in typ or ')' in typ or ',' in typ:return record,[]
    normalized=typ+' '+name
    # Scalar first parameters already parse correctly. Pointer names need an explicit separator.
    if not typ.endswith('*') or first==normalized:return record,[]
    first_start=found.end()+len(params)-len(params.lstrip());first_end=first_start+len(first)
    changed=copy.deepcopy(record);changed['draft']=text[:first_start]+normalized+text[first_end:]
    return changed,[{'kind':'receiver_parameter_boundary','before':first,'after':normalized,'evidence':'first top-level formal; retain every subsequent parameter and entire body'}]


def walk(node):
    yield node
    for child in node.get('inner',[]):yield from walk(child)


def canonical_type(typ,aliases):
    for _ in range(12):
        replaced=seed.replace_identifiers(typ,aliases)
        if replaced==typ:break
        typ=replaced
    return re.sub(r'\s+',' ',typ).strip()


def type_kind(typ,aliases):
    typ=canonical_type(typ,aliases)
    if '*' in typ and not any(c in typ for c in '()[]') and not re.search(r'\b(?:__ptr64|__far|_far)\b',typ):return 'pointer'
    typ=re.sub(r'\b(?:const|volatile)\b','',typ).strip()
    if typ in ('int','unsigned int','signed int','long','long int','unsigned long','unsigned long int','signed long','signed long int'):return 'integer32'
    return 'other'


def bit_preserving_cast(lhs,rhs,aliases):
    a=type_kind(lhs,aliases);b=type_kind(rhs,aliases)
    if (a,b) not in (('pointer','pointer'),('pointer','integer32'),('integer32','pointer')):return False
    if a=='pointer' and b=='pointer':
        l=canonical_type(lhs,aliases);r=canonical_type(rhs,aliases)
        # C-style related-class pointer casts can adjust addresses. Only scalar
        # pointees are established here; record/enum/unknown pointees stay unresolved.
        scalar={'void','char','signed char','unsigned char','short','short int','signed short','signed short int','unsigned short','unsigned short int','int','signed int','unsigned int','long','long int','signed long','signed long int','unsigned long','unsigned long int','float','double','bool','__int64','unsigned __int64','signed __int64'}
        for typ in (l,r):
            base=re.sub(r'\b(?:const|volatile)\b|\*',' ',typ)
            if ' '.join(base.split()) not in scalar:return False
        if any(re.search(r'\b'+q+r'\b',r) and not re.search(r'\b'+q+r'\b',l) for q in ('const','volatile')):return False
    return True


def offsets(node):
    rr=node.get('range',{});lo=rr.get('begin',{});hi=rr.get('end',{})
    if 'offset' not in lo or 'offset' not in hi or 'tokLen' not in hi:return None
    return lo['offset'],hi['offset']+hi['tokLen']


def ast_casts(source,ast):
    """Only whole invalid assignment expressions with known, native-width preserving conversions."""
    aliases={n['name']:n['type']['qualType'] for n in walk(ast) if n.get('kind')=='TypedefDecl' and 'name' in n and 'type' in n}
    raw=source.encode();edits=[]
    for node in walk(ast):
        if node.get('kind')!='RecoveryExpr' or len(node.get('inner',[]))!=2:continue
        lhs,rhs=node['inner'];left=offsets(lhs);right=offsets(rhs)
        if not left or not right or not 0<=left[0]<left[1]<=right[0]<right[1]<=len(raw):continue
        if raw[left[1]:right[0]].strip()!=b'=':continue
        lt=lhs.get('type',{}).get('desugaredQualType',lhs.get('type',{}).get('qualType',''));rt=rhs.get('type',{}).get('desugaredQualType',rhs.get('type',{}).get('qualType',''))
        if not bit_preserving_cast(lt,rt,aliases):continue
        if any(not (right[1]<=e['start'] or right[0]>=e['end']) for e in edits):continue
        expr=raw[right[0]:right[1]].decode();cast_type=lhs['type']['qualType'];edits.append({'start':right[0],'end':right[1],'replacement':'('+cast_type+')('+expr+')','kind':'native32_explicit_assignment_cast','lhs_type':lt,'rhs_type':rt,'before':expr})
    for edit in sorted(edits,key=lambda e:e['start'],reverse=True):raw=raw[:edit['start']]+edit['replacement'].encode()+raw[edit['end']:]
    return raw.decode(),edits


def repair(record,folder,baseline_source=None,clang='clang++'):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True);started=time.time();modified,changes=receiver_spacing(record);converted=seed.convert_export(modified)
    result={'schema_version':1,'rva':record['rva'],'module_sha256':PIN,'raw_draft':record.get('draft'),'changes':changes,'status':'no_source','source':None,'diagnostics':converted['diagnostics'],'symbol_addresses':converted.get('symbol_addresses',{}),'paid_requests':0}
    if converted['status']!='converted':atomic(folder/'repair.json',result);return result
    source=converted['source'];tool=shutil.which(clang)
    if tool:
        version=subprocess.run([tool,'--version'],capture_output=True,text=True,timeout=10).stdout.splitlines()[0];result['clang']={'path':tool,'version':version,'flags':CLANG_FLAGS}
        for attempt in range(3):
            current=folder/f'clang-input-{attempt}.cpp';current.write_bytes(source.encode());run=subprocess.run([tool,*CLANG_FLAGS,str(current)],capture_output=True,timeout=30)
            (folder/f'clang-{attempt}.stderr').write_bytes(run.stderr)
            try:ast=json.loads(run.stdout)
            except (ValueError,UnicodeError):result['diagnostics'].append('clang_ast_unavailable');break
            changed,edits=ast_casts(source,ast)
            if not edits:break
            result['changes'].extend(edits);source=changed
    else:result['diagnostics'].append('clang_not_available_receiver_only')
    result.update(status='source_ready',source=source,source_sha256=sha(source.encode()),changed_from_baseline=source!=baseline_source if baseline_source is not None else True,elapsed_seconds=round(time.time()-started,3));(folder/'candidate.cpp').write_bytes(source.encode());atomic(folder/'repair.json',result);return result


def inventory(baseline=BASELINE):
    baseline=Path(baseline);cases=[];seen=set()
    for chunk in sorted(baseline.glob('chunk-*')):
        report=chunk/'sample-report.json'
        if report.exists():
            value=json.loads(report.read_text());report_sha256=sha(report.read_bytes())
            for row in value['records']:
                rva=row['rva'];status=row.get('measurement',{}).get('status',row['conversion_status']);source=Path(row['source']) if row.get('source') else None;log=Path(row.get('measurement',{}).get('compiler_log',''))
                if status=='compile_or_transport_error':
                    text=log.read_text(errors='replace') if log.is_file() else '';first=re.search(r'error (C\d+)\s*:\s*([^\n]+)',text)
                    if first is None:continue
                    category='receiver' if first[1] in ('C2065','C2146') and ('param_' in first[2]) else 'pointer_conversion' if first[1]=='C2440' else 'other_compiler'
                elif status=='no_source':category='no_source'
                elif status in ('exact_object_match','nonmatch','inconclusive'):category='control'
                else:continue
                cases.append({'rva':rva,'category':category,'baseline_status':status,'source':str(source) if source else None,'source_sha256':sha(source.read_bytes()) if source and source.exists() else None,'raw_export':row['raw_export'],'raw_export_sha256':sha(Path(row['raw_export']).read_bytes()),'baseline_report':str(report),'baseline_report_sha256':report_sha256,'compiler_log':str(log) if log.is_file() else None,'compiler_log_sha256':sha(log.read_bytes()) if log.is_file() else None,'diagnostics':row.get('diagnostics',[])});seen.add(rva)
        receipt=chunk/'conversion-receipt.json'
        if receipt.exists():
            for cache in sorted(Path(json.loads(receipt.read_text())['folder']).glob('*/conversion.json')):
                value=json.loads(cache.read_text());rva=value['rva']
                if rva in seen or value['status']!='no_source':continue
                raw=Path(value['raw_export']);cases.append({'rva':rva,'category':'no_source','baseline_status':'no_source','source':None,'source_sha256':None,'raw_export':str(raw),'raw_export_sha256':sha(raw.read_bytes()),'baseline_report':str(cache),'baseline_report_sha256':sha(cache.read_bytes()),'compiler_log':None,'compiler_log_sha256':None,'diagnostics':value.get('diagnostics',[])});seen.add(rva)
    return cases


def stratified(cases,count):
    buckets=defaultdict(list)
    for case in cases:
        raw=json.loads(Path(case['raw_export']).read_text());size=sum(r['end_rva_inclusive']-r['start_rva']+1 for r in raw.get('ranges',[]));bin=next((i for i,n in enumerate((32,128,512)) if size<=n),3);calls=sum(s.get('kind')=='function' and s.get('rva')!=case['rva'] for s in raw.get('symbols',[]));buckets[(bin,min(calls,2))].append(case)
    for group in buckets.values():group.sort(key=lambda c:sha(encode({'rva':c['rva'],'experiment':'deterministic-compile-v1'})))
    selected=[]
    while len(selected)<count and any(buckets.values()):
        for key in sorted(buckets):
            if buckets[key] and len(selected)<count:selected.append(buckets[key].pop())
    return selected


def prepare(root=ROOT,baseline=BASELINE):
    root=Path(root);root.mkdir(parents=True,exist_ok=True);cases=inventory(baseline);selected=[]
    limits={'receiver':30,'pointer_conversion':30,'other_compiler':10,'no_source':10,'control':20}
    for category,count in limits.items():
        pool=[c for c in cases if c['category']==category and (category!='no_source' or any('this_parameter' in d for d in c['diagnostics']))];selected.extend(stratified(pool,count))
    value={'schema_version':1,'module_sha256':PIN,'cases':selected,'cases_observed':len(cases),'categories':dict(Counter(c['category'] for c in cases)),'selected_categories':dict(Counter(c['category'] for c in selected)),'paid_requests':0,'baseline_immutable':True};atomic(root/'pilot-selection.json',value);return {k:v for k,v in value.items() if k!='cases'}


@lru_cache(maxsize=1)
def tool_bindings():
    from .build import VCVARS
    compiler=shutil.which('clang++');clang={'path':compiler,'flags':CLANG_FLAGS}
    if compiler:
        clang.update(binary_sha256=sha(Path(compiler).resolve().read_bytes()),version=subprocess.run([compiler,'--version'],capture_output=True,text=True,timeout=10).stdout.splitlines()[0])
    return {'repair_sha256':sha(Path(__file__).read_bytes()),'seed_sha256':sha(Path(seed.__file__).read_bytes()),'clang':clang,'vcvars':VCVARS,'expected_cl_sha256':'5f6489b0d211b14ae09d93d3fb58a7bce84d070287f008e06416c9baa5564219','code_sha256':{name:sha((Path(__file__).parent/name).read_bytes()) for name in ('build.py','coff.py','compare.py')}}


def verify_baseline(case):
    pairs=[('raw_export','raw_export_sha256'),('source','source_sha256'),('baseline_report','baseline_report_sha256'),('compiler_log','compiler_log_sha256')]
    for path_key,hash_key in pairs:
        if case.get(path_key) and (not Path(case[path_key]).is_file() or sha(Path(case[path_key]).read_bytes())!=case[hash_key]):raise ValueError('baseline_binding_changed:'+path_key)
    raw=json.loads(Path(case['raw_export']).read_text())
    if raw.get('module_sha256')!=PIN or raw.get('rva')!=case['rva']:raise ValueError('baseline_original_identity_changed')


def cached_result(case,folder):
    retries=sorted(folder.glob('result-after-transport-retry-*.json'))
    path=retries[-1] if retries else folder/'result.json'
    if not path.exists():return None
    result=json.loads(path.read_text())
    old=result.get('baseline',{});core=('rva','baseline_status','source_sha256','raw_export_sha256')
    if any(old.get(k)!=case.get(k) for k in core):raise ValueError('cached_baseline_domain_changed')
    verify_baseline(old)
    if result.get('source'):
        source=folder/'candidate.cpp'
        if not source.is_file() or sha(source.read_bytes())!=result.get('source_sha256'):raise ValueError('repair_cache_source_binding')
    if result.get('compile_success'):
        summary_path=Path(result['summary']);obj=summary_path.parent/'candidate.obj'
        if not summary_path.resolve().is_relative_to(folder.resolve()):raise ValueError('repair_cache_summary_path')
        if not obj.is_file() or not summary_path.is_file():raise ValueError('repair_cache_missing_object_or_summary')
        report=json.loads(summary_path.read_text());functions=report.get('functions',[])
        if report.get('module_sha256')!=PIN or report.get('source_sha256')!=result['source_sha256'] or report.get('object_sha256')!=sha(obj.read_bytes()) or len(functions)!=1 or functions[0].get('rva')!=case['rva'] or functions[0].get('status')!=result.get('matching_status'):raise ValueError('repair_cache_comparison_binding')
        raw=json.loads(Path(case['raw_export']).read_text());requested=report.get('requested',{}).get(str(case['rva']),{})
        if raw.get('module_sha256')!=PIN or raw.get('rva')!=case['rva'] or any(requested.get(k)!=raw.get(k) for k in ('original_va','ranges','bytes_sha256')):raise ValueError('repair_cache_original_request_binding')
        current=tool_bindings();expected_impl={n:current['code_sha256'][n] for n in ('coff.py','compare.py')};compiler=(result.get('build') or {}).get('compiler') or {}
        if report.get('implementation_sha256')!=expected_impl or compiler.get('sha256')!=current['expected_cl_sha256'] or report.get('compiler')!=compiler:raise ValueError('repair_cache_comparator_or_compiler_binding')
    current=tool_bindings()
    if result.get('tool_bindings')!=current:
        # Reproduce source under current repair/seed/Clang code; never recompile merely
        # because queue/cache plumbing changed, and never relabel the historical run.
        check=folder/'resume-check'/sha(encode(current));check_result=check/'repair.json'
        regenerated=json.loads(check_result.read_text()) if check_result.exists() else repair(json.loads(Path(case['raw_export']).read_text()),check,Path(case['source']).read_text() if case.get('source') else None)
        if regenerated.get('source_sha256')!=result.get('source_sha256') or regenerated['status']!=result['repair_status']:raise ValueError('repair_recipe_changed_use_new_output_root')
        if regenerated.get('source') is not None and (not (check/'candidate.cpp').is_file() or sha((check/'candidate.cpp').read_bytes())!=result.get('source_sha256')):raise ValueError('resume_regenerated_source_binding')
        result={**result,'resume_verified_tool_bindings':current,'resume_verification':str(check_result)}
    return result


def evaluate(case,root,compile_unchanged=True):
    import fcntl
    from .build import build_and_compare
    folder=Path(root)/f"{case['rva']:08x}";result_path=folder/'result.json'
    verify_baseline(case);cached=cached_result(case,folder)
    if cached is not None:return cached
    folder.mkdir(parents=True,exist_ok=True);raw=Path(case['raw_export']);source=Path(case['source']) if case.get('source') else None
    if sha(raw.read_bytes())!=case['raw_export_sha256'] or (source and sha(source.read_bytes())!=case['source_sha256']):raise ValueError('baseline_binding_changed')
    original=json.loads(raw.read_text());baseline=source.read_text() if source else None;proposal=repair(original,folder,baseline);record={'tool_bindings':tool_bindings(),'implementation_sha256':sha(Path(__file__).read_bytes()),'repair_elapsed_seconds':proposal.get('elapsed_seconds',0),'changed_from_baseline':proposal.get('changed_from_baseline',False),'rva':case['rva'],'category':case['category'],'baseline_status':case['baseline_status'],'baseline':case,'repair_status':proposal['status'],'changes':proposal['changes'],'source_sha256':proposal.get('source_sha256'),'source':str(folder/'candidate.cpp') if proposal['source'] else None,'compile_success':False,'matching_status':None,'paid_requests':0}
    if baseline is not None:(folder/'baseline.cpp').write_bytes(baseline.encode())
    if proposal['source'] and (compile_unchanged or proposal['changed_from_baseline']):
        requested={case['rva']:{k:original[k] for k in ('original_va','ranges','bytes_sha256')}}
        with (REPO/'local/rapid-object/vm-build.lock').open('a+') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            try:summary=build_and_compare(folder/'candidate.cpp',folder/'build',requested,proposal['symbol_addresses'])
            except Exception as exc:summary={'error':type(exc).__name__+':'+str(exc),'functions':[]}
        build=summary.get('build') or {};obj=folder/'build/candidate.obj';compiled=build.get('exit_code')==0 and (build.get('compiler') or {}).get('sha256')==tool_bindings()['expected_cl_sha256'] and build.get('module_sha256')==PIN and build.get('source_sha256')==record['source_sha256'] and sha((folder/'candidate.cpp').read_bytes())==record['source_sha256'] and bool(build.get('object_sha256')) and obj.is_file() and sha(obj.read_bytes())==build['object_sha256']
        record.update(compile_success=bool(compiled),matching_status=summary.get('functions',[{}])[0].get('status') if compiled and summary.get('functions') else None,build=summary.get('build'),error=summary.get('error'),summary=str(folder/'build/summary.json'))
        log=folder/'build/build.log';text=log.read_text(errors='replace') if log.exists() else '';record['compiler_errors']=list(dict.fromkeys(re.findall(r'error (C\d+)\s*:\s*([^\n]+)',text)))
    if proposal['source'] and not compile_unchanged and not proposal['changed_from_baseline']:record['stop_reason']='no_supported_source_change_baseline_failure_retained'
    atomic(result_path,record);return record


def run_pilot(root=ROOT):
    root=Path(root);selection=json.loads((root/'pilot-selection.json').read_text());records=[];started=time.time()
    for case in selection['cases']:
        records.append(evaluate(case,root/'pilot'));value=summarize(records,started);atomic(root/'pilot-progress.json',value)
    value=summarize(records,started);atomic(root/'pilot-results.json',value);return value


def summarize(records,started):
    failed=[r for r in records if r['category']!='control'];controls=[r for r in records if r['category']=='control']
    return {'measured':len(records),'baseline_failures_or_no_source':len(failed),'improved_to_compile':sum(r['compile_success'] for r in failed),'controls':len(controls),'controls_compiled':sum(r['compile_success'] for r in controls),'control_compile_regressions':sum(not r['compile_success'] for r in controls),'control_match_regressions':sum(r['baseline_status']=='exact_object_match' and r['matching_status']!='exact_object_match' for r in controls),'control_matching_changes':sum(r['baseline_status']!=r['matching_status'] for r in controls),'matching':dict(Counter(r['matching_status'] or 'not_compared' for r in records)),'remaining_compiler_first_errors':dict(Counter((r.get('compiler_errors') or [('no_error_code','')])[0][0] for r in failed if not r['compile_success'])),'elapsed_seconds':round(time.time()-started,3),'sum_vm_build_seconds':round(sum((r.get('build') or {}).get('elapsed_seconds',0) for r in records),3),'sum_repair_seconds':round(sum(r.get('repair_elapsed_seconds',0) for r in records),3),'records':records,'paid_requests':0,'promoted':False}


def retry_transports(root=ROOT,area='pilot'):
    import fcntl
    from .build import build_and_compare
    root=Path(root);retried=[]
    for path in sorted((root/area).glob('*/result.json')):
        original=json.loads(path.read_text());build=original.get('build') or {};folder=path.parent
        if original.get('compile_success') or build.get('exit_code')!=255 or build.get('compiler') is not None or build.get('object_sha256'):continue
        target=folder/'result-after-transport-retry-1.json'
        if target.exists():retried.append(json.loads(target.read_text()));continue
        case=original['baseline'];verify_baseline(case);source=folder/'candidate.cpp'
        if not source.is_file() or sha(source.read_bytes())!=original['source_sha256']:raise ValueError('transport_retry_source_binding')
        output=folder/'build-transport-retry-1'
        if output.exists():raise ValueError('retained_interrupted_transport_retry_no_reset')
        raw=json.loads(Path(case['raw_export']).read_text());proposal=json.loads((folder/'repair.json').read_text());requested={case['rva']:{k:raw[k] for k in ('original_va','ranges','bytes_sha256')}}
        with (REPO/'local/rapid-object/vm-build.lock').open('a+') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);summary=build_and_compare(source,output,requested,proposal['symbol_addresses'])
        build=summary.get('build') or {};obj=output/'candidate.obj';compiled=build.get('exit_code')==0 and (build.get('compiler') or {}).get('sha256')==tool_bindings()['expected_cl_sha256'] and build.get('module_sha256')==PIN and build.get('source_sha256')==original['source_sha256'] and sha(source.read_bytes())==original['source_sha256'] and bool(build.get('object_sha256')) and obj.is_file() and sha(obj.read_bytes())==build['object_sha256']
        text=(output/'build.log').read_text(errors='replace') if (output/'build.log').exists() else ''
        result={**original,'tool_bindings':tool_bindings(),'retained_source_no_regeneration':True,'prior_result_sha256':sha(path.read_bytes()),'compile_success':bool(compiled),'build':build,'summary':str(output/'summary.json'),'matching_status':summary.get('functions',[{}])[0].get('status') if compiled and summary.get('functions') else None,'compiler_errors':list(dict.fromkeys(re.findall(r'error (C\d+)\s*:\s*([^\n]+)',text))),'transport_retry':1,'error':summary.get('error')};atomic(target,result);retried.append(result)
    atomic(root/(area+'-transport-retries.json'),{'records':retried,'retained_sources':True,'paid_requests':0});return {'retried':len(retried),'compiled':sum(r['compile_success'] for r in retried),'records':retried}


def prepare_sweep(root=ROOT,baseline=BASELINE,paused=True):
    root=Path(root);root.mkdir(parents=True,exist_ok=True);observed=inventory(baseline);eligible=[];retained=Counter()
    for case in observed:
        if case['category']=='control':retained['baseline_already_compiles']+=1;continue
        raw=json.loads(Path(case['raw_export']).read_text());_,receiver_changes=receiver_spacing(raw)
        if case['category'] in ('receiver','pointer_conversion') or receiver_changes:eligible.append(case)
        else:retained[case['diagnostics'][0].split(':')[0] if case.get('diagnostics') else 'no_supported_repair_for_first_error']+=1
    plan={'schema_version':1,'module_sha256':PIN,'prepared_at':time.time(),'implementation_sha256':sha(Path(__file__).read_bytes()),'observed':len(observed),'eligible':len(eligible),'retained_reasons':dict(retained),'cases':eligible,'paid_requests':0,'promoted':False,'launched':False,'baseline':str(baseline)};atomic(root/'sweep-plan.json',plan)
    if paused:(root/'sweep.paused').write_text('prepared; awaiting coordinator launch\n')
    return {k:v for k,v in plan.items() if k!='cases'}


def run_sweep(root=ROOT,resume=False,max_cases=0,follow=False):
    import fcntl
    import signal
    root=Path(root);plan=json.loads((root/'sweep-plan.json').read_text());lock=(root/'sweep-owner.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);records=[];seen=set();started=time.time();stopping=False;baseline_complete=False;last_chunks=-1
    if resume:(root/'sweep.paused').unlink(missing_ok=True)
    def stop(signum,frame):
        nonlocal stopping
        stopping=True
    previous_term=signal.signal(signal.SIGTERM,stop);previous_int=signal.signal(signal.SIGINT,stop)
    try:
        while True:
            for case in plan['cases']:
                if case['rva'] in seen:continue
                if stopping or (root/'sweep.paused').exists() or (max_cases and len(records)>=max_cases):break
                records.append(evaluate(case,root/'sweep',compile_unchanged=False));seen.add(case['rva']);atomic(root/'sweep-status.json',{**summarize(records,started),'planned':len(plan['cases']),'paused':False,'follow':follow})
            if stopping or (root/'sweep.paused').exists() or (max_cases and len(records)>=max_cases):break
            if not follow:break
            baseline=Path(plan['baseline']);status=json.loads((baseline/'compile-summary.json').read_text());baseline_complete=status.get('completed',False)
            if status.get('chunks_complete')!=last_chunks:
                prepare_sweep(root,baseline,paused=False);plan=json.loads((root/'sweep-plan.json').read_text());last_chunks=status.get('chunks_complete')
                if any(c['rva'] not in seen for c in plan['cases']):continue
            if baseline_complete:break
            atomic(root/'sweep-status.json',{**summarize(records,started),'planned':len(plan['cases']),'paused':False,'follow':True,'waiting_for_baseline':True});time.sleep(20)
        paused=stopping or (root/'sweep.paused').exists()
        if stopping:(root/'sweep.paused').write_text('graceful stop after current build\n')
        value={**summarize(records,started),'planned':len(plan['cases']),'paused':paused,'follow':follow,'baseline_completed':baseline_complete,'completed':len(seen)==len(plan['cases']) and (not follow or baseline_complete)};atomic(root/'sweep-status.json',value);return value
    finally:
        signal.signal(signal.SIGTERM,previous_term);signal.signal(signal.SIGINT,previous_int);fcntl.flock(lock,fcntl.LOCK_UN);lock.close()


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['prepare','pilot','prepare-sweep','sweep','retry-transports','pause']);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--baseline',type=Path,default=BASELINE);p.add_argument('--resume',action='store_true');p.add_argument('--max-cases',type=int,default=0);p.add_argument('--follow',action='store_true');a=p.parse_args()
    if a.command=='prepare':value=prepare(a.root,a.baseline)
    elif a.command=='pilot':value=run_pilot(a.root)
    elif a.command=='prepare-sweep':value=prepare_sweep(a.root,a.baseline)
    elif a.command=='sweep':value=run_sweep(a.root,a.resume,a.max_cases,a.follow)
    elif a.command=='retry-transports':value=retry_transports(a.root)
    else:(a.root/'sweep.paused').write_text('operator pause\n');value={'paused':True}
    print(json.dumps(value,indent=2))

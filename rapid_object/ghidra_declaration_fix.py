"""Restore omitted callback typedefs from a read-only Ghidra type graph; no calls changed."""
from collections import Counter
from pathlib import Path
import fcntl
import json
import re
import signal
import subprocess
import time
from . import ghidra_seed as seed, ghidra_compile_fix as fix, ghidra_state_fix as state
from rapid.factory import REPO
from rapid.packets import PIN
from workers.deepseek_packet import atomic, encode, sha

ROOT=REPO/'local/toolkit-evolution-005'
JAVA=r'''import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.*;
import com.google.gson.*;
import java.nio.file.*;
import java.util.*;
public class ExportCallbackTypes extends GhidraScript {
 JsonObject type(DataType d,int depth) { JsonObject j=new JsonObject();if(d==null)return j;
 j.addProperty("name",d.getName());j.addProperty("display",d.getDisplayName());j.addProperty("class",d.getClass().getName());j.addProperty("length",d.getLength());j.addProperty("path",d.getPathName());if(depth>12)return j;
 if(d instanceof Pointer)j.add("pointee",type(((Pointer)d).getDataType(),depth+1));
 if(d instanceof TypeDef)j.add("base",type(((TypeDef)d).getBaseDataType(),depth+1));
 if(d instanceof FunctionDefinition){FunctionDefinition f=(FunctionDefinition)d;j.addProperty("cc",f.getCallingConventionName());j.addProperty("varargs",f.hasVarArgs());j.add("return",type(f.getReturnType(),depth+1));JsonArray a=new JsonArray();for(ParameterDefinition p:f.getArguments())a.add(type(p.getDataType(),depth+1));j.add("arguments",a);}return j;}
 public void run() throws Exception {JsonObject out=new JsonObject();out.addProperty("module_sha256",currentProgram.getExecutableSHA256());out.addProperty("image_base",currentProgram.getImageBase().getOffset());out.addProperty("ghidra_version",ghidra.framework.Application.getApplicationVersion());out.addProperty("language",currentProgram.getLanguageID().toString());out.addProperty("compiler_spec",currentProgram.getCompilerSpec().getCompilerSpecID().toString());JsonArray a=new JsonArray();Iterator<DataType> it=currentProgram.getDataTypeManager().getAllDataTypes();while(it.hasNext()){monitor.checkCancelled();DataType d=it.next();if(d instanceof FunctionDefinition)a.add(type(d,0));}out.add("function_types",a);Files.writeString(Paths.get(getScriptArgs()[0]),new GsonBuilder().setPrettyPrinting().create().toJson(out));}
}'''


def export_types(root=ROOT):
    root=Path(root);folder=root/'types';folder.mkdir(parents=True,exist_ok=True)
    script=folder/'ExportCallbackTypes.java';script.write_text(JAVA);output=folder/'graph.json'
    if output.exists():raise ValueError('type_export_exists_use_retained_receipt_or_new_root')
    before=seed.project_fingerprint();started=time.time()
    command=[str(seed.GHIDRA/'support/analyzeHeadless'),str(seed.PROJECT),'DAOOrigins','-process','DAOrigins.exe','-noanalysis','-readOnly','-scriptPath',str(folder.resolve()),'-postScript',script.name,str(output.resolve()),'-max-cpu','2']
    with (folder/'export.log').open('wb') as log:proc=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=180)
    after=seed.project_fingerprint()
    if proc.returncode or before!=after or not output.exists():raise ValueError('type_export_failed_or_project_changed')
    graph=json.loads(output.read_text())
    if graph.get('module_sha256')!=PIN or graph.get('image_base')!=0x400000 or graph.get('language')!='x86:LE:32:default' or graph.get('compiler_spec')!='windows':raise ValueError('type_export_original_target')
    receipt={'graph':str(output.resolve()),'graph_sha256':sha(output.read_bytes()),'project_store_sha256_before':before,'project_store_sha256_after':after,'script_sha256':sha(script.read_bytes()),'command':command,'elapsed_seconds':round(time.time()-started,3),'exit_code':proc.returncode,'paid_requests':0}
    atomic(folder/'receipt.json',receipt);return receipt


def load_graph(root):
    receipt=json.loads((Path(root)/'types/receipt.json').read_text());path=Path(receipt['graph'])
    if sha(path.read_bytes())!=receipt['graph_sha256'] or receipt['script_sha256']!=sha(JAVA.encode()) or receipt['project_store_sha256_before']!=receipt['project_store_sha256_after']:raise ValueError('type_graph_binding')
    graph=json.loads(path.read_text())
    if graph.get('module_sha256')!=PIN or graph.get('image_base')!=0x400000 or graph.get('language')!='x86:LE:32:default' or graph.get('compiler_spec')!='windows':raise ValueError('type_graph_target')
    return graph,receipt


def scalar_type(t,depth=0):
    """Render only explicit ABI-sized primitive/pointer metadata. Records/arrays stay unknown."""
    if depth>8:raise ValueError('callback_type_depth')
    cls=t.get('class','').rsplit('.',1)[-1];name=t.get('name');size=t.get('length')
    if cls in ('TypeDefDB','TypedefDataType'):return scalar_type(t.get('base',{}),depth+1)
    if cls in ('PointerDB','PointerDataType'):
        if size!=4 or not t.get('pointee'):raise ValueError('callback_pointer_unknown_or_width')
        return scalar_type(t['pointee'],depth+1)+' *'
    allowed={('void',0):'void',('char',1):'char',('signed char',1):'signed char',('uchar',1):'unsigned char',('byte',1):'unsigned char',('short',2):'short',('ushort',2):'unsigned short',('int',4):'int',('uint',4):'unsigned int',('long',4):'long',('ulong',4):'unsigned long',('longlong',8):'__int64',('ulonglong',8):'unsigned __int64',('float',4):'float',('double',8):'double'}
    # Named records may imitate primitive spelling; accept only genuine built-in scalar classes.
    classes={'VoidDataType','CharDataType','SignedCharDataType','UnsignedCharDataType','ByteDataType','ShortDataType','UnsignedShortDataType','IntegerDataType','UnsignedIntegerDataType','LongDataType','UnsignedLongDataType','LongLongDataType','UnsignedLongLongDataType','FloatDataType','DoubleDataType'}
    if cls not in classes or (name,size) not in allowed:raise ValueError('callback_scalar_unknown:'+str(name))
    return allowed[(name,size)]


def typedef_for(name,graph):
    rows=[t for t in graph.get('function_types',[]) if t.get('name')==name]
    if not rows:raise ValueError('callback_type_missing:'+name)
    signatures=[]
    for t in rows:
        if t.get('class','').rsplit('.',1)[-1] not in ('FunctionDefinitionDB','FunctionDefinitionDataType') or t.get('cc') not in ('__cdecl','__stdcall','__fastcall') or not isinstance(t.get('varargs'),bool) or not isinstance(t.get('arguments'),list):raise ValueError('callback_abi_unknown:'+name)
        args=[scalar_type(a) for a in t['arguments']]
        if 'void' in args:raise ValueError('callback_void_parameter')
        if t['varargs']:
            if t['cc']!='__cdecl' or not args:raise ValueError('callback_variadic_abi_unknown')
            args.append('...')
        signatures.append('typedef '+scalar_type(t.get('return',{}))+' '+t['cc']+' '+name+'('+(', '.join(args) if args else 'void')+');')
    if len(set(signatures))!=1:raise ValueError('callback_type_ambiguous:'+name)
    return signatures[0]


def restore_declarations(source,graph):
    code=fix.mask(source);names=sorted(set(re.findall(r'\b_func_\d+\b',code)));declarations=[]
    for name in names:
        # Existing actual typedefs/declarations or macros are outside this omission repair.
        if re.search(r'\btypedef\b[^;{}]*\b'+re.escape(name)+r'\b[^;{}]*;',code) or re.search(r'\b(?:struct|class|enum)\s+'+re.escape(name)+r'\b|(?m:^\s*#\s*define\s+'+re.escape(name)+r'\b)',code):raise ValueError('callback_already_declared_or_conflicting:'+name)
        declarations.append({'name':name,'declaration':typedef_for(name,graph),'hypothesis':True})
    return ('\n'.join(d['declaration'] for d in declarations)+'\n' if declarations else '')+source,declarations


def bindings(root):
    graph,receipt=load_graph(root)
    return {'declaration_fix_sha256':sha(Path(__file__).read_bytes()),'type_graph_sha256':receipt['graph_sha256'],'type_export_receipt_sha256':sha((Path(root)/'types/receipt.json').read_bytes()),'compile_fix':fix.tool_bindings(),'state_fix_sha256':sha(Path(state.__file__).read_bytes())}


def snapshots(root=ROOT):
    """Immutable deduplicated view: any observed compiled result outranks older failures."""
    root=Path(root);root.mkdir(parents=True,exist_ok=True);observed={};files={};completed=[]
    for area in ('deterministic-compile-001','toolkit-evolution-002','toolkit-evolution-003'):
        for p in sorted((REPO/'local'/area).glob('*/????????/result*.json')):
            value=json.loads(p.read_text());rva=value['rva'];files[str(p)]=sha(p.read_bytes());old=observed.get(rva)
            if old is None or (value.get('compile_success'),p.stat().st_mtime_ns)>(old[0].get('compile_success'),old[1].stat().st_mtime_ns):observed[rva]=(value,p)
        status=REPO/'local'/area/'sweep-status.json'
        if status.exists():
            data=json.loads(status.read_text());completed.append({'path':str(status),'sha256':sha(status.read_bytes()),'snapshot_mtime':status.stat().st_mtime,'summary':{k:v for k,v in data.items() if k not in ('records','tool_bindings')}})
    rows=[];first=Counter();targets=[];controls=[];graph,_=load_graph(root)
    for rva,(r,p) in sorted(observed.items()):
        source=p.parent/'candidate.cpp';base=r['baseline'];raw=Path(base['raw_export'])
        if not source.is_file():continue
        if sha(source.read_bytes())!=r.get('source_sha256'):raise ValueError('snapshot_source_binding')
        case={'rva':rva,'category':'control' if r.get('compile_success') else 'callback','baseline_status':r.get('matching_status') if r.get('compile_success') else 'compile_failure','source':str(source),'source_sha256':sha(source.read_bytes()),'raw_export':str(raw),'raw_export_sha256':sha(raw.read_bytes()),'baseline_report':str(p),'baseline_report_sha256':files[str(p)],'compiler_log':None,'compiler_log_sha256':None}
        errors=r.get('compiler_errors',[]);error=errors[0] if errors else [None,None]
        if r.get('compile_success'):controls.append(case)
        else:
            first[tuple(error)]+=1
            try:
                _,changes=restore_declarations(source.read_text(),graph)
                if changes and error[0]=='C2065' and any("'"+d['name']+"'" in (error[1] or '') for d in changes):targets.append(case)
            except ValueError:pass
        rows.append({'rva':rva,'compiled':bool(r.get('compile_success')),'first_error':error,'result':str(p),'result_sha256':files[str(p)]})
    atomic(root/'census.json',{'snapshot_at':time.time(),'rows':rows,'unique_source_identities':len(rows),'callback_targets':len(targets),'first_errors':[{'code':k[0],'message':k[1],'count':v} for k,v in first.most_common()],'result_inputs':files,'live_sweep_snapshots':completed,'paid_requests':0})
    exact=[c for c in controls if c['baseline_status']=='exact_object_match'];chosen=fix.stratified(exact,min(10,len(exact)));chosen+=fix.stratified([c for c in controls if c not in chosen],20-len(chosen))
    selected=fix.stratified(targets,80)+chosen
    atomic(root/'pilot-selection.json',{'cases':selected,'tool_bindings':bindings(root),'paid_requests':0});atomic(root/'sweep-plan.json',{'cases':targets,'tool_bindings':bindings(root),'launched':False});(root/'sweep.paused').write_text('not authorized before independent review\n')
    return {'unique_source_identities':len(rows),'callback_targets':len(targets),'selected':len(selected),'compiled_controls_available':len(controls)}


def symbol_addresses(raw):
    result={}
    for sym in raw.get('symbols',[]):
        address=sym.get('original_va');kind=sym.get('kind')
        if not isinstance(address,int) or address<0x400000 or kind not in ('function','global'):raise ValueError('dependency_identity')
        name=('fn_' if kind=='function' else 'g_')+f'{address-0x400000:08x}';row={'original_va':address,'kind':kind}
        if name in result and result[name]!=row:raise ValueError('dependency_ambiguity')
        result[name]=row
    return result


def evaluate(case,root,area='pilot'):
    from .build import build_and_compare
    root=Path(root).resolve();fix.verify_baseline(case);graph,_=load_graph(root);current=bindings(root);folder=root/area/f"{case['rva']:08x}";folder.mkdir(parents=True,exist_ok=True)
    raw=json.loads(Path(case['raw_export']).read_text());receipt=load_graph(root)[1]
    if raw.get('analysis_revision',{}).get('project_store_sha256')!=receipt.get('project_store_sha256_before'):raise ValueError('callback_source_project_revision')
    original=Path(case['source']).read_text();source,changes=(original,[]) if case['category']=='control' else restore_declarations(original,graph);digest=sha(source.encode());path=folder/'candidate.cpp';result_path=folder/'result.json';raw=json.loads(Path(case['raw_export']).read_text())
    if result_path.exists():
        result=json.loads(result_path.read_text())
        if result['baseline']!=case or any(result['tool_bindings'].get(k)!=v for k,v in current.items() if k!='declaration_fix_sha256') or result['source_sha256']!=digest or not path.is_file() or sha(path.read_bytes())!=digest:raise ValueError('declaration_resume_source_or_recipe_binding')
        if result.get('compile_success'):
            output=Path(result['summary']).parent;report=json.loads((output/'summary.json').read_text());obj=output/'candidate.obj';build=result['build']
            if not output.resolve().is_relative_to(folder.resolve()) or not obj.is_file() or not state.report_bound(report,case,raw,digest,sha(obj.read_bytes()),build,current) or report.get('functions')!=result['comparison_functions'] or report['functions'][0]['status']!=result['matching_status'] or build.get('exit_code')!=0 or build.get('module_sha256')!=PIN or build.get('object_sha256')!=sha(obj.read_bytes()) or build.get('source_sha256')!=digest or json.loads((output/'run.json').read_text())!=build:raise ValueError('declaration_resume_artifact_binding')
        if result['tool_bindings']!=current:result={**result,'resume_verified_tool_bindings':current,'resume_verified_source_sha256':digest}
        return result
    path.write_text(source);started=time.time();requested={case['rva']:{k:raw[k] for k in ('original_va','ranges','bytes_sha256')}}
    for attempt in range(2):
        output=folder/('build' if attempt==0 else 'build-transport-retry-1')
        if output.exists():raise ValueError('interrupted_declaration_build_no_reset')
        with (REPO/'local/rapid-object/vm-build.lock').open('a+') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);report=build_and_compare(path,output,requested,symbol_addresses(raw))
        build=report.get('build') or {}
        if not (build.get('exit_code')==255 and build.get('compiler') is None and not build.get('object_sha256')):break
    obj=output/'candidate.obj';compiled=build.get('exit_code')==0 and (build.get('compiler') or {}).get('sha256')==current['compile_fix']['expected_cl_sha256'] and build.get('module_sha256')==PIN and build.get('source_sha256')==digest and sha(path.read_bytes())==digest and obj.is_file() and build.get('object_sha256')==sha(obj.read_bytes())
    errors=re.findall(r'error (C\d+)\s*:\s*([^\n]+)',(output/'build.log').read_text(errors='replace')) if (output/'build.log').exists() else []
    result={'rva':case['rva'],'baseline':case,'category':case['category'],'tool_bindings':current,'source_sha256':digest,'changes':changes,'compile_success':bool(compiled),'matching_status':report['functions'][0]['status'] if compiled and state.report_bound(report,case,raw,digest,build['object_sha256'],build,current) else None,'comparison_functions':report.get('functions',[]),'build':build,'summary':str(output/'summary.json'),'compiler_errors':errors,'elapsed_seconds':round(time.time()-started,3),'transport_retries':attempt,'paid_requests':0}
    atomic(result_path,result);return result


def summarize(records,started):
    targets=[r for r in records if r['category']!='control'];controls=[r for r in records if r['category']=='control']
    return {'measured':len(records),'targets':len(targets),'target_compile_success':sum(r['compile_success'] for r in targets),'controls':len(controls),'control_compile_success':sum(r['compile_success'] for r in controls),'new_exact_matches':sum(r['matching_status']=='exact_object_match' for r in targets),'control_matching_regressions':sum(r['baseline']['baseline_status']=='exact_object_match' and r['matching_status']!='exact_object_match' for r in controls),'matching_statuses':dict(Counter(r['matching_status'] or 'not_compared' for r in records)),'first_errors':dict(Counter(r['compiler_errors'][0][0] if r['compiler_errors'] else 'no_error_code' for r in records if not r['compile_success'])),'transport_retries':sum(r['transport_retries'] for r in records),'wall_seconds':round(time.time()-started,3),'sum_build_seconds':round(sum(r['build'].get('elapsed_seconds',0) for r in records),3),'paid_requests':0,'records':records}


def run(root=ROOT,max_cases=0,sweep=False,resume=False):
    root=Path(root);plan=json.loads((root/('sweep-plan.json' if sweep else 'pilot-selection.json')).read_text());started=time.time();records=[];stop=False
    def stopping(*args):
        nonlocal stop
        stop=True
    owner=(root/'owner.lock').open('a+');fcntl.flock(owner,fcntl.LOCK_EX|fcntl.LOCK_NB);old=signal.signal(signal.SIGTERM,stopping)
    try:
        if sweep and resume:(root/'sweep.paused').unlink(missing_ok=True)
        for case in plan['cases']:
            if stop or (sweep and (root/'sweep.paused').exists()) or (max_cases and len(records)>=max_cases):break
            area='pilot' if not sweep or (root/'pilot'/f"{case['rva']:08x}"/'result.json').exists() else 'sweep'
            records.append(evaluate(case,root,area));atomic(root/('sweep-status.json' if sweep else 'pilot-results.json'),summarize(records,started))
        if stop and sweep:(root/'sweep.paused').write_text('stopped after retained build\n')
        return {k:v for k,v in summarize(records,started).items() if k!='records'}
    finally:signal.signal(signal.SIGTERM,old);owner.close()


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['export-types','census','pilot','sweep','pause']);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--max-cases',type=int,default=0);p.add_argument('--resume',action='store_true');a=p.parse_args()
    if a.command=='pause':(a.root/'sweep.paused').write_text('operator pause\n');value={'paused':True}
    else:value=export_types(a.root) if a.command=='export-types' else snapshots(a.root) if a.command=='census' else run(a.root,a.max_cases,a.command=='sweep',a.resume)
    print(json.dumps(value,indent=2))

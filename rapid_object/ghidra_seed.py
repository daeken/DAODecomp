"""Offline Ghidra draft seed experiment. No provider calls, queue changes or match promotion."""
from collections import defaultdict
import json
from pathlib import Path
import re
import subprocess
import time
from workers.deepseek_packet import atomic,encode,sha
from rapid.factory import MAIN,REPO
from rapid.packets import PIN

DEFAULT_ROOT=REPO/'local/cost-reduction-001/seed'
GHIDRA=MAIN/'local/tools/ghidra_12.1.4_PUBLIC'
PROJECT=MAIN/'local/ghidra'
FORCED=(0x136c0,0x28f0,0x18210)


def representative_sample(functions,count=200):
    if count<len(FORCED):raise ValueError('sample_count_must_include_examples')
    index={f['rva']:f for f in functions};selected=[r for r in FORCED if r in index];buckets=defaultdict(list)
    for f in functions:
        size=f.get('body_bytes',sum(rr['end_rva_inclusive']-rr['start_rva']+1 for rr in f.get('ranges',f.get('body_ranges',[]))))
        size_bin=next((i for i,limit in enumerate((16,64,256,1024)) if size<=limit),4);calls=len(f.get('direct_calls',[]));key=(size_bin,min(calls,2))
        if f['rva'] not in selected:buckets[key].append(f['rva'])
    for group in buckets.values():group.sort(key=lambda r:sha(encode({'module':PIN,'rva':r,'sample':'ghidra-seed-v1'})))
    keys=sorted(buckets)
    while len(selected)<min(count,len(index)):
        for key in keys:
            if buckets[key] and len(selected)<count:selected.append(buckets[key].pop())
    return selected


def project_fingerprint(path=PROJECT/'DAOOrigins.rep'):
    """Persistent analyzed-program content, not Ghidra's per-open event counter."""
    path=Path(path);files=sorted(p for p in (path/'idata').rglob('*') if p.is_file() and (p.suffix in ('.gbf','.prp') or p.name=='~index.dat'))
    if not files:raise ValueError('missing_persistent_project_store')
    return sha(encode({str(p.relative_to(path)):sha(p.read_bytes()) for p in files}))


def select(root=DEFAULT_ROOT,count=200,timeout=15):
    from .catalog import open_store
    root=Path(root);root.mkdir(parents=True,exist_ok=True);store=open_store();functions=[json.loads(row[0]) for row in store.db.execute('SELECT details_json FROM catalog')]
    rvas=representative_sample(functions,count);script=REPO/'tools/ghidra/ExportCandidates.java'
    settings={'exporter_sha256':sha(script.read_bytes()),'project_store_sha256':project_fingerprint(),'timeout_seconds':timeout,'decompiler_options':'Ghidra defaults; read-only existing analyzed program; no reanalysis','inventory_sha256':sha((MAIN/'local/analysis/functions.json').read_bytes()),'sample_method':'size[<=16,64,256,1024,larger] x direct_calls[0,1,2+] deterministic SHA rank round-robin plus three requested examples'}
    value={'schema_version':1,'module_sha256':PIN,'rvas':rvas,'timeout_seconds':timeout,'settings':settings};atomic(root/'selection.json',value);return value


def export(root=DEFAULT_ROOT):
    root=Path(root).resolve();selection=json.loads((root/'selection.json').read_text())
    if selection['settings'].get('exporter_sha256')!=sha((REPO/'tools/ghidra/ExportCandidates.java').read_bytes()) or selection['settings'].get('project_store_sha256')!=project_fingerprint():raise ValueError('export_settings_or_project_changed_run_select_again')
    folder=root/'export'/sha(encode(selection['settings']));folder.mkdir(parents=True,exist_ok=True)
    command=[str(GHIDRA/'support/analyzeHeadless'),str(PROJECT),'DAOOrigins','-process','DAOrigins.exe','-noanalysis','-readOnly','-scriptPath',str(REPO/'tools/ghidra'),'-postScript','ExportCandidates.java',str(root/'selection.json'),str(folder),'-max-cpu','2'];started=time.time()
    with (root/'export.log').open('wb') as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=max(180,count_timeout(selection)))
    if selection['settings']['project_store_sha256']!=project_fingerprint():raise RuntimeError('project_changed_during_export')
    receipt={'command':command,'exit_code':result.returncode,'elapsed_seconds':round(time.time()-started,3),'folder':str(folder),'settings_sha256':folder.name,'requested':len(selection['rvas']),'export_files':len(list(folder.glob('*.json'))),'paid_requests':0};atomic(root/'export-receipt.json',receipt);return receipt


def count_timeout(selection):return len(selection['rvas'])*selection['timeout_seconds']+180



# A lexical pass preserves literals/comments: address names in strings are not symbols.
TOKENS=re.compile(r'//(?:[^\n]*\\\r?\n)*[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[A-Za-z_$][A-Za-z_0-9$]*|.',re.DOTALL)


def replace_identifiers(text,mapping):
    return ''.join(mapping.get(m.group(),m.group()) if re.fullmatch(r'[A-Za-z_$][A-Za-z_0-9$]*',m.group()) else m.group() for m in TOKENS.finditer(text))


def code_only(text):
    return ''.join(' ' if m.group().startswith(('//','/*','"',"'")) else m.group() for m in TOKENS.finditer(text))


def declarator(typ,name):
    typ=typ.strip();arrays=re.search(r'(\[[^\]]+\])+$',typ)
    if arrays:return typ[:arrays.start()].strip()+' '+name+arrays.group()
    return typ+' '+name


def canonicalize_draft(record):
    """Address-name normalization only, also available for unsupported raw drafts."""
    base=record.get('image_base',0x400000);mapping={};addresses={};diagnostics=[];ambiguous=set()
    for sym in record.get('symbols',[]):
        token=sym.get('token','');address=sym.get('original_va')
        if not re.fullmatch(r'[A-Za-z_]\w*',token) or type(address) is not int or address<base or sym.get('kind') not in ('function','global'):
            diagnostics.append('unresolved_symbol_identity:'+token);continue
        canonical=('fn_' if sym['kind']=='function' else 'g_')+f'{address-base:08x}'
        if token in mapping and mapping[token]!=canonical:ambiguous.add(token)
        else:mapping[token]=canonical;addresses[canonical]={'original_va':address,'kind':sym['kind']}
    for token in ambiguous:mapping.pop(token,None);diagnostics.append('ambiguous_symbol_token:'+token)
    return {'canonical_draft':replace_identifiers(record.get('draft') or '',mapping),'identifier_map':mapping,'symbol_addresses':addresses,'normalization_diagnostics':diagnostics}


def convert_export(record):
    """Best-effort deterministic syntactic conversion, explicitly provisional ABI/types."""
    result={'schema_version':1,'rva':record['rva'],'module_sha256':record.get('module_sha256'),'status':'no_source','source':None,'draft':record.get('draft'),'diagnostics':[],'signature_status':'hypothesis','symbol_addresses':{},'declaration_hypotheses':[]}
    result.update(canonicalize_draft(record))
    def stop(reason):result['diagnostics'].append(reason);return result
    if record.get('module_sha256')!=PIN:return stop('module_pin')
    if record.get('status')!='decompiled' or not record.get('draft'):return stop('no_decompiler_draft')
    source=record['draft'];code=code_only(source);rva=record['rva'];base=record.get('image_base',0x400000);name=f'fn_{rva:08x}'
    if re.search(r'\b(?:in_|unaff_|extraout_|unaff_retaddr|register0x)\w*',code):return stop('unmodeled_register_or_stack_input')
    if re.search(r'\b(?:float10|float16|undefined16|int16|uint16|__vector|__builtin|__asm|asm)\b',code):return stop('unsupported_extended_type_or_instruction')
    if record.get('type_error'):return stop('type_export_error:'+record['type_error'])
    header,sep,body=source.partition('{')
    if not sep or not body.rstrip().endswith('}'):return stop('unrecognized_function_definition')
    own=[s for s in record.get('symbols',[]) if s['kind']=='function' and s.get('rva')==rva]
    if not own:return stop('missing_definition_symbol')
    own_token=own[0]['token'];match=re.search(r'(?<!\w)'+re.escape(own_token)+r'\s*\(',header)
    if not match:return stop('unrecognized_definition_name')
    prefix=header[:match.start()].strip();params=header[match.end():].strip()
    if not params.endswith(')'):return stop('unrecognized_parameter_list')
    params=params[:-1].strip();body='{'+body;mapping={};declarations=[];symbols={};hypotheses=[]
    for sym in record.get('symbols',[]):
        token=sym['token'];address=sym.get('original_va')
        if not re.fullmatch(r'[A-Za-z_]\w*',token) or address is None or address<base:return stop('unsupported_symbol_identity:'+token)
        canonical=('fn_' if sym['kind']=='function' else 'g_')+f'{address-base:08x}'
        if token in mapping and mapping[token]!=canonical:return stop('ambiguous_symbol_token:'+token)
        mapping[token]=canonical;symbols[canonical]={'original_va':address,'kind':sym['kind']};hypotheses.append(sym)
        if sym['kind']=='global':declarations.append('extern "C" '+declarator(sym['type_hypothesis'],canonical)+';')
        elif sym.get('rva')!=rva:
            proto=sym.get('prototype_hypothesis','')
            if sym.get('calling_convention_hypothesis')=='unknown' or not proto:
                declarations.append('extern "C" unsigned int __cdecl '+canonical+'(...); /* ABI/return type unknown, provisional declaration */')
            elif '__thiscall' in proto:return stop('unsupported_thiscall_dependency_declaration:'+token)
            else:
                proto=replace_identifiers(proto,{sym.get('name',token):canonical,token:canonical})
                if canonical not in proto:return stop('unsupported_dependency_name:'+token)
                declarations.append('extern "C" '+proto+';')
    source_body=replace_identifiers(body,mapping)
    # Integer CONCAT/SUB operators have defined unsigned bit semantics. Other helpers stay unknown.
    helpers=[]
    for helper in sorted(set(re.findall(r'\b([A-Z][A-Z_]*\d*)\s*\(',code_only(source_body)))):
        if helper.startswith(('FUN_','LAB_')):return stop('unresolved_symbol:'+helper)
        concat=re.fullmatch(r'CONCAT([1-8])([1-8])',helper);sub=re.fullmatch(r'SUB([1-8])([1-8])',helper)
        if concat and sum(map(int,concat.groups()))<=8:
            high,low=map(int,concat.groups());hm=(1<<(high*8))-1;lm=(1<<(low*8))-1
            helpers.append(f'inline unsigned __int64 {helper}(unsigned __int64 a,unsigned __int64 b) {{ return ((a & 0x{hm:x}ui64) << {low*8}) | (b & 0x{lm:x}ui64); }}')
        elif sub and int(sub[2])<=int(sub[1]):
            width=int(sub[2]);mask=(1<<(width*8))-1
            helpers.append(f'inline unsigned __int64 {helper}(unsigned __int64 a,unsigned int n) {{ return (a >> (n*8)) & 0x{mask:x}ui64; }}')
        elif helper=='CARRY4':helpers.append('inline bool CARRY4(unsigned int a,unsigned int b) { return (unsigned __int64)a+b > 0xffffffffui64; }')
        else:return stop('unsupported_helper:'+helper)
    # Ghidra names integer subpieces as var._offset_width_; preserve lvalue accesses explicitly.
    widths={1:'unsigned char',2:'unsigned short',4:'unsigned int',8:'unsigned __int64'}
    for part in re.findall(r'\b([A-Za-z_]\w*)\._(\d+)_(\d+)_',source_body):
        variable,offset,width=part;width=int(width)
        if width not in widths:return stop('unsupported_subpiece_width:'+str(width))
        source_body=source_body.replace(variable+'._'+offset+'_'+str(width)+'_',f'(*(({widths[width]}*)((unsigned char*)&{variable}+{offset})))')
    if re.search(r'\._\d+_\d+_',source_body):return stop('unsupported_subpiece_expression')
    cc='__thiscall' if '__thiscall' in prefix else None;types=record.get('type_declarations_hypothesis','')
    types=re.sub(r'^\s*typedef[^;]*\b(?:bool|wchar_t)\s*;\s*','',types,flags=re.MULTILINE)
    types='typedef unsigned int pointer32;\ntypedef unsigned int code(...);\n'+types
    # Native Windows x86 __int64 is the VC8 spelling; this is a width-preserving syntax conversion.
    types=re.sub(r'\blong long\b','__int64',types)
    declarations=[replace_identifiers(d,mapping) for d in declarations];prefix=replace_identifiers(prefix,mapping);params=replace_identifiers(params,mapping)
    if cc:
        # A native method uses the existing ECX receiver; no wrapper or adapter is emitted.
        formal=re.match(r'\s*(.+?)\s+([A-Za-z_]\w*)\s*(?:,|$)',params)
        if not formal:return stop('unrecognized_this_parameter')
        this_type,this_name=formal.groups();rest=params[formal.end():].strip() or 'void';return_type=prefix.replace('__thiscall','').strip();klass=f'Seed_{rva:08x}'
        source_body=replace_identifiers(source_body,{this_name:'(('+this_type+')this)'})
        declaration=f'struct {klass} {{ {return_type} __thiscall {name}({rest}); }};'
        definition=f'{return_type} __thiscall {klass}::{name}({rest})\n'+source_body
        declarations.append(declaration)
    else:definition=prefix+' '+name+'('+params+')\n'+source_body
    generated='// Provisional deterministic Ghidra seed; signatures/types remain hypotheses.\n'+types+'\n'+'\n'.join(dict.fromkeys(declarations))+'\n'+'\n'.join(helpers)+f'\n// FUNCTION: DAO 0x{base+rva:08x}\n'+definition
    # Unresolved names or known register pseudo-values cannot become successful helper stubs.
    if re.search(r'\b(?:FUN|DAT|PTR|thunk_FUN)_[0-9a-fA-F]{8}\b',code_only(generated)):return stop('unresolved_decompiler_symbol')
    result.update(status='converted',source=generated,symbol_addresses=symbols,declaration_hypotheses=hypotheses,source_sha256=sha(generated.encode()));return result


def convert_sample(root=DEFAULT_ROOT):
    root=Path(root);selection=json.loads((root/'selection.json').read_text());export_receipt=json.loads((root/'export-receipt.json').read_text());folder=Path(export_receipt['folder']);version=sha(Path(__file__).read_bytes());export_bindings={str(r):sha((folder/f'{r:08x}.json').read_bytes()) if (folder/f'{r:08x}.json').exists() else None for r in selection['rvas']};cache_key=sha(encode({'converter':version,'exports':export_bindings}));out=root/'converted'/cache_key;out.mkdir(parents=True,exist_ok=True);counts=defaultdict(int);started=time.time()
    for rva in selection['rvas']:
        raw=folder/f'{rva:08x}.json';target=out/f'{rva:08x}';target.mkdir(exist_ok=True)
        binding=sha(raw.read_bytes()) if raw.exists() else None;cache=target/'conversion.json'
        result=json.loads(cache.read_text()) if cache.exists() else {}
        valid=result.get('export_sha256')==binding and result.get('converter_sha256')==version and result.get('rva')==rva and result.get('module_sha256')==PIN
        if result.get('status')=='converted':valid=valid and type(result.get('source')) is str and sha(result['source'].encode())==result.get('source_sha256')
        if not valid:
            record=json.loads(raw.read_text()) if raw.exists() else {'rva':rva,'module_sha256':PIN,'status':'missing_export'};result=convert_export(record);result.update(export_sha256=binding,converter_sha256=version,raw_export=str(raw));atomic(cache,result)
        candidate=target/'candidate.cpp'
        expected=result.get('source');actual=candidate.read_bytes() if candidate.exists() else None
        if actual is not None and (expected is None or sha(actual)!=result.get('source_sha256')):
            # Preserve unbound edits while restoring the exact source stored in this bound cache.
            saved=target/('candidate-unbound-'+sha(actual)+'.cpp')
            if not saved.exists():saved.write_bytes(actual)
        if expected is not None and (actual is None or sha(actual)!=result['source_sha256']):candidate.write_bytes(expected.encode())
        elif expected is None and candidate.exists():candidate.unlink()
        if result.get('draft'):(target/'draft.c').write_text(result['draft'])
        counts[result['status']]+=1
    receipt={'schema_version':1,'requested':len(selection['rvas']),'counts':dict(counts),'elapsed_seconds':round(time.time()-started,3),'folder':str(out),'converter_sha256':version,'cache_key':cache_key,'paid_requests':0};atomic(root/'conversion-receipt.json',receipt);return receipt


def conversion_integrity(converted,receipt,rva,candidate):
    if converted.get('module_sha256')!=PIN or converted.get('rva')!=rva or converted.get('converter_sha256')!=receipt.get('converter_sha256'):return 'conversion_identity_or_converter_binding'
    raw=Path(converted.get('raw_export',''))
    if not raw.is_file() or sha(raw.read_bytes())!=converted.get('export_sha256'):return 'conversion_export_binding'
    if converted.get('status')=='converted':
        source=converted.get('source')
        if type(source) is not str or sha(source.encode())!=converted.get('source_sha256'):return 'cached_source_binding'
        if not candidate.is_file() or sha(candidate.read_bytes())!=converted['source_sha256']:return 'emitted_source_binding'
    return None


def measure_sample(root=DEFAULT_ROOT,limit=0):
    """Compile each converted source independently under the existing shared VM lock."""
    import fcntl
    import sqlite3
    from .build import build_and_compare,VCVARS
    root=Path(root);conversion=json.loads((root/'conversion-receipt.json').read_text());folder=Path(conversion['folder']);selection=json.loads((root/'selection.json').read_text())
    # Offline seed measurement must not compete with an undrained production claim.
    queue=REPO/'local/rapid-object/queue.sqlite3'
    if queue.exists():
        db=sqlite3.connect('file:'+str(queue)+'?mode=ro',uri=True)
        try:
            paused=db.execute("SELECT value FROM meta WHERE key='paused'").fetchone()[0]=='1';claimed=db.execute("SELECT count(*) FROM batches WHERE state='claimed'").fetchone()[0]
            if not paused or claimed:raise RuntimeError('production_must_be_paused_and_drained')
        finally:db.close()
    implementation={n:sha((REPO/'rapid_object'/n).read_bytes()) for n in ('build.py','coff.py','compare.py')};started=time.time();records=[]
    for rva in selection['rvas']:
        target=folder/f'{rva:08x}';converted=json.loads((target/'conversion.json').read_text());record={'rva':rva,'conversion_status':converted['status'],'raw_export':converted['raw_export'],'source':str(target/'candidate.cpp') if converted['source'] else None,'diagnostics':converted['diagnostics'],'paid_requests':0}
        integrity=conversion_integrity(converted,conversion,rva,target/'candidate.cpp')
        if integrity:
            record['measurement']={'status':'cache_integrity_error','diagnostics':[integrity],'promoted':False};records.append(record);atomic(root/'measurement-progress.json',summarize_records(records,selection,root,started));continue
        if converted['source']:
            raw=json.loads(Path(converted['raw_export']).read_text());bindings={'source_sha256':converted['source_sha256'],'original_bytes_sha256':raw['bytes_sha256'],'module_sha256':PIN,'implementation':implementation,'vcvars':VCVARS}
            key=sha(encode(bindings));output=target/'builds'/key;cache=output/'measurement.json'
            if cache.exists() and json.loads(cache.read_text()).get('bindings')==bindings:measurement=json.loads(cache.read_text())
            else:
                output.parent.mkdir(exist_ok=True);requested={rva:{'original_va':raw['original_va'],'ranges':raw['ranges'],'bytes_sha256':raw['bytes_sha256']}}
                with (REPO/'local/rapid-object/vm-build.lock').open('a+') as lock:
                    fcntl.flock(lock,fcntl.LOCK_EX)
                    try:summary=build_and_compare(target/'candidate.cpp',output,requested,converted['symbol_addresses'])
                    except Exception as exc:summary={'error':type(exc).__name__+':'+str(exc)[:300],'functions':[]};output.mkdir(parents=True,exist_ok=True)
                status='compile_or_transport_error' if summary.get('error') else summary['functions'][0]['status'] if len(summary.get('functions',[]))==1 else 'comparison_missing'
                log=(output/'build.log').read_text(errors='replace') if (output/'build.log').exists() else ''
                measurement={'schema_version':1,'bindings':bindings,'status':status,'summary':str(output/'summary.json'),'compiler_log':str(output/'build.log'),'compiler_errors':list(dict.fromkeys(re.findall(r'error (C[0-9]+):?[^\n]*',log))),'build':summary.get('build'),'diagnostics':summary.get('functions',[{}])[0].get('diagnostics',[]) if summary.get('functions') else [summary.get('error')],'promoted':False};atomic(cache,measurement)
            record.update(measurement=measurement,measurement_file=str(cache))
        records.append(record)
        report=summarize_records(records,selection,root,started);atomic(root/'measurement-progress.json',report)
        if limit and sum(r['conversion_status']=='converted' for r in records)>=limit:break
    report=summarize_records(records,selection,root,started);atomic(root/'sample-report.json',report);return report


def summarize_records(records,selection,root,started):
    counts=defaultdict(int);categories=defaultdict(int);exported=0
    for record in records:
        raw=Path(record['raw_export'])
        if raw.exists() and json.loads(raw.read_text()).get('status')=='decompiled':exported+=1
        status=record.get('measurement',{}).get('status',record['conversion_status']);counts[status]+=1
        for diagnostic in record.get('diagnostics',[])+record.get('measurement',{}).get('diagnostics',[]):categories[str(diagnostic).split(':')[0]]+=1
        for code in record.get('measurement',{}).get('compiler_errors',[]):categories['compiler_'+code]+=1
    count=len(records);compiled=sum(counts[s] for s in ('exact_object_match','nonmatch','inconclusive'));converted=sum(r['conversion_status']=='converted' for r in records)
    return {'schema_version':1,'requested':len(selection['rvas']),'measured':count,'exported_drafts':exported,'converted_sources':converted,'compiled_objects':compiled,'counts':dict(counts),'failure_categories':dict(categories),'rates_of_measured':{'export':exported/max(count,1),'conversion':converted/max(count,1),'compile':compiled/max(count,1),'exact_match':counts['exact_object_match']/max(count,1)},'elapsed_measurement_seconds':round(time.time()-started,3),'export_receipt':str(Path(root)/'export-receipt.json'),'conversion_receipt':str(Path(root)/'conversion-receipt.json'),'records':records,'paid_requests':0,'promoted':False,'evidence':'standalone native VC8 COFF comparison only; no game execution or signature proof'}


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['select','export','convert','measure']);p.add_argument('--root',type=Path,default=DEFAULT_ROOT);p.add_argument('--count',type=int,default=200);p.add_argument('--limit',type=int,default=0);a=p.parse_args();fn={'select':lambda:select(a.root,a.count),'export':lambda:export(a.root),'convert':lambda:convert_sample(a.root),'measure':lambda:measure_sample(a.root,a.limit)}[a.command];print(json.dumps(fn(),indent=2))

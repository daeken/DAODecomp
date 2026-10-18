"""All-inventory profile on the same durable Store, transport and budget ledgers."""
import fcntl
import json
import multiprocessing
import os
from pathlib import Path
import signal
import time
from workers import deepseek_packet as provider
from rapid.factory import DEFAULT_GLOBAL,DEFAULT_LEDGER
from rapid.packets import PIN
from rapid.store import reserve_global,settle_global
from rapid_native.propose import prepare_request,request_packet
from rapid_native.queue import claim_native
from rapid_native.repairs import attempt_numbers
from .catalog import ROOT,open_store,entry,registry
from .packets import packet
from .build import VCVARS,build_and_compare


def read(path,default=None):return json.loads(path.read_text()) if path.exists() else ({} if default is None else default)


def quality(f):
    a=bytes.fromhex(f.get('original_bytes_hex',''));b=bytes.fromhex(f.get('relocated_bytes_hex',''))
    return 1.0 if f['status']=='exact_object_match' else sum(x==y for x,y in zip(a,b))/max(len(a),len(b),1)


def best_results(folder):
    selection=read(folder/'selection.json');allowed=set(selection.get('rvas',[]));best={}
    if selection.get('split_parent'):
        parent=folder.parent/selection['split_parent']
        best={f['rva']:f for f in best_results(parent) if f['rva'] in allowed}
    for attempt in attempt_numbers(folder):
        source=folder/f'attempt-{attempt}/candidate.cpp';report=folder/f'attempt-{attempt}/build/summary.json';value=read(report)
        packet_value=read(folder/f'attempt-{attempt}/packet.json');domain={f['rva']:f for f in packet_value.get('functions',[])}
        functions=value.get('functions',[])
        if not source.exists() or not domain or not packet_value.get('context_complete') or len(functions)!=len(domain) or {f['rva'] for f in functions}!=set(domain):continue
        if allowed and not set(domain).issubset(allowed):continue
        obj=report.parent/'candidate.obj'
        implementation={name:provider.sha((Path(__file__).parent/name).read_bytes()) for name in ('coff.py','compare.py')}
        if value.get('implementation_sha256')!=implementation or value.get('module_sha256')!=PIN or provider.sha(source.read_bytes())!=value.get('source_sha256') or not obj.exists() or provider.sha(obj.read_bytes())!=value.get('object_sha256'):continue
        if any(f.get('original_bytes_sha256')!=domain[f['rva']]['bytes_sha256'] for f in functions if f['status']!='inconclusive'):continue
        requested=value.get('requested',{})
        if any(requested.get(str(r),{}).get('ranges')!=domain[r]['ranges'] for r in domain):continue
        for f in value['functions']:
            current={**f,'score':quality(f),'source':str(source),'summary':str(report)};old=best.get(f['rva'])
            if old is None or (old['status']!='exact_object_match' and (f['status']=='exact_object_match' or current['score']>old['score'])):best[f['rva']]=current
    return list(best.values())


def ingest(store,batch,functions):
    with store.db:
        for f in functions:
            old=store.db.execute('SELECT status,score FROM object_results WHERE rva=?',(f['rva'],)).fetchone()
            if old and (old[0]=='exact_object_match' or old[1]>f['score']):continue
            store.db.execute('INSERT OR REPLACE INTO object_results VALUES(?,?,?,?,?,?)',(f['rva'],batch,f['status'],f['score'],f['source'],f['summary']))
            store.db.execute('UPDATE catalog SET state=? WHERE rva=?',(f['status'],f['rva']))


def next_packet(store,batch,max_repairs=6):
    folder=store.root/'batches'/batch;selection=read(folder/'selection.json');previous=read(folder/'result.json');numbers=attempt_numbers(folder)
    if numbers and not previous.get('needs_work'):raise ValueError('no_authorized_continuation')
    for number in numbers:
        record=read(folder/f'attempt-{number}/result.json')
        if record.get('outcome') in ('interrupted_unknown','timeout','transport_error') or 'charged_nanodollars' not in record:raise ValueError('unknown_paid_outcome_no_replay')
    if previous.get('repairs',0)>max_repairs:raise ValueError('repair_limit')
    best=best_results(folder);matched={f['rva'] for f in best if f['status']=='exact_object_match'};rvas=[r for r in selection['rvas'] if r not in matched]
    if not rvas:raise ValueError('all_matched')
    feedback=[];sources={}
    for f in best:
        if f['rva'] in rvas:
            source=Path(f['source']).read_text();binding=provider.sha(source.encode());sources[binding]=source;feedback.append({'rva':f['rva'],'best_source_sha256':binding,'comparison':{k:v for k,v in f.items() if k not in ('source','original_bytes_hex','object_bytes_hex','relocated_bytes_hex')}})
    if previous.get('compiler_feedback'):
        feedback.append(previous['compiler_feedback'])
        if previous.get('latest_source') and Path(previous['latest_source']).exists():
            source=Path(previous['latest_source']).read_text();binding=provider.sha(source.encode());sources[binding]=source
            feedback.append({'latest_failed_source_sha256':binding,'diagnostics':'compiler_feedback immediately above applies to this exact source'})
    prior=None
    if previous.get('context_page',0) and previous.get('latest_source'):prior=Path(previous['latest_source']).read_text()
    value=packet(store,rvas,previous.get('context_page',0),{'function_feedback':feedback,'best_sources':sources} if feedback else None,prior)
    try:prepare_request(value)
    except ValueError:
        # Retain essential bytes/identities while dropping optional diagnostics. A still oversized
        # single-page request stays explicitly blocked, never silently excluded or billed.
        value['related_context']=[];prepare_request(value)
    return value,(numbers[-1]+1 if numbers else 1)


def decision(previous,value,request,best,max_repairs=6,stagnation_limit=3):
    result={'context_page':previous.get('context_page',0),'repairs':previous.get('repairs',0),'stagnation':previous.get('stagnation',0),'needs_work':False}
    matched={f['rva'] for f in best if f['status']=='exact_object_match'}
    if request.get('outcome') in ('timeout','transport_error','interrupted_unknown') or 'charged_nanodollars' not in request:return {**result,'stop_reason':'unknown_paid_outcome_no_replay'}
    if request['outcome']=='success' and not value['context_complete']:
        return {**result,'context_page':result['context_page']+1,'needs_work':True,'stop_reason':'context_continuation'}
    if request['outcome']=='success' and all(f['rva'] in matched for f in value['functions']):return {**result,'stop_reason':'all_matched'}
    q=sum(f['score'] for f in best);old=previous.get('best_quality',-1)
    result['stagnation']=result['stagnation']+1 if q<=old else 0;result['best_quality']=q
    if result['repairs']>=max_repairs:return {**result,'stop_reason':'repair_limit'}
    if result['stagnation']>=stagnation_limit:return {**result,'stop_reason':'stagnation'}
    return {**result,'repairs':result['repairs']+1,'needs_work':True,'stop_reason':'repair_pending'}


def split_batch(store,batch,rvas,reason,previous=None):
    """Known consumed response only: smaller new groups, same durable identity ownership."""
    children=[];previous=previous or {}
    if len(rvas)<2:return children
    halves=[rvas[:len(rvas)//2],rvas[len(rvas)//2:]]
    for subset in halves:
        ident=provider.sha(provider.encode({'parent':batch,'rvas':subset}));folder=store.root/'batches'/ident;folder.mkdir(parents=True,exist_ok=True)
        provider.atomic(folder/'selection.json',{'module_sha256':PIN,'rvas':subset,'split_parent':batch,'reason':reason})
        provider.atomic(folder/'result.json',{'final_record':True,'needs_work':True,'repairs':previous.get('repairs',0),'context_page':previous.get('context_page',0),'stop_reason':'split_continuation','latest_source':previous.get('latest_source')})
        children.append((ident,subset))
    with store.db:
        for ident,subset in children:
            store.db.execute('INSERT OR IGNORE INTO batches(id,state,functions,created) VALUES(?,?,?,?)',(ident,'pending',json.dumps(subset),time.time()))
            store.db.executemany('UPDATE identities SET batch=? WHERE rva=?',[(ident,r) for r in subset])
            store.db.executemany("UPDATE catalog SET batch=?,state='queued_split' WHERE rva=?",[(ident,r) for r in subset])
    return [ident for ident,_ in children]


def process_batch(root,batch,request_id,value,attempt,vcvars,ledger_dir,global_db,max_repairs=6,stagnation_limit=3):
    store=open_store(root);folder=Path(root)/'batches'/batch;previous=read(folder/'result.json');where=folder/f'attempt-{attempt}'
    result={'final_record':True,'outcome':'error','needs_work':False,'attempt':attempt}
    if previous.get('latest_source'):result['latest_source']=previous['latest_source']
    try:
        if where.exists():raise ValueError('attempt_reuse')
        request=request_packet(where,value,request_id,ledger_dir,global_db);result['provider_outcome']=request['outcome']
        if request['outcome']=='success':
            result['latest_source']=str(where/'candidate.cpp')
            if value['context_complete']:
                requested={f['rva']:{k:f[k] for k in ('original_va','ranges','bytes_sha256')} for f in value['functions']}
                with (Path(root)/'vm-build.lock').open('a+') as lock:
                    fcntl.flock(lock,fcntl.LOCK_EX)
                    report=build_and_compare(where/'candidate.cpp',where/'build',requested,registry(store),vcvars)
                if report.get('error'):result['compiler_feedback']={'build_error':report['error'],'compiler_log':(where/'build/build.log').read_text(errors='replace')[-16000:] if (where/'build/build.log').exists() else 'VM transport failed'}
        elif request['outcome']=='invalid_response' and request.get('http_status')==200 and (where/'raw-response.json').exists() and 'charged_nanodollars' in request and len(value['functions'])>1 and previous.get('repairs',0)<max_repairs:
            result.update(split_children=split_batch(store,batch,[f['rva'] for f in value['functions']],'known_complete_invalid_source_or_output_limit',{**previous,'repairs':previous.get('repairs',0)+1}),stop_reason='split_known_complete_response',outcome='retained_error')
            history=folder/'history';history.mkdir(exist_ok=True);provider.atomic(history/f'attempt-{attempt}.json',result)
            provider.atomic(folder/'result.json',result);store.finish(batch,'complete','split_complete_response');return
        best=best_results(folder);ingest(store,batch,best)
        result.update(decision(previous,value,request,best,max_repairs,stagnation_limit),functions=best,outcome='retained',requested_rvas=read(folder/'selection.json')['rvas'])
        if request['outcome']!='success':result['compiler_feedback']={'provider_outcome':request['outcome'],'finish_reason':request.get('finish_reason'),'instruction':'Return complete structured C++ source for the requested identities; previous paid response retained.'}
        state='pending' if result['needs_work'] else ('interrupted_unknown' if result['stop_reason']=='unknown_paid_outcome_no_replay' else 'complete')
    except BaseException as exc:
        result.update(error=type(exc).__name__+':'+str(exc)[:240]);state='error'
    history=folder/'history';history.mkdir(exist_ok=True);provider.atomic(history/f'attempt-{attempt}.json',result);provider.atomic(folder/'result.json',result)
    store.finish(batch,state,'repair_'+result.get('stop_reason','error') if result['needs_work'] else result.get('stop_reason',result.get('error')))
    with store.db:
        store.db.execute("UPDATE catalog SET state=? WHERE batch=? AND state NOT IN ('exact_object_match','native_attested')",('continuation_pending' if result['needs_work'] else 'retained_'+state,batch))


def reconcile(store):
    for batch, in store.db.execute("SELECT id FROM batches WHERE state='claimed'").fetchall():
        value=read(store.root/'batches'/batch/'result.json')
        if value.get('final_record') and not value.get('dispatching'):
            ingest(store,batch,value.get('functions',[]));store.finish(batch,'pending' if value.get('needs_work') else 'complete','repair_reconciled' if value.get('needs_work') else 'reconciled')
        else:
            store.finish(batch,'interrupted_unknown','paid_outcome_not_replayed')
            with store.db:store.db.execute("UPDATE catalog SET state='interrupted_unknown' WHERE batch=? AND state!='exact_object_match'",(batch,))


def status(root=ROOT):
    store=open_store(root);value=store.status();cost=reserved=attempts=0;proposed=set();tokens={'prompt_tokens':0,'completion_tokens':0}
    for path in (Path(root)/'batches').glob('*/attempt-*/result.json'):
        r=read(path);cost+=r.get('charged_nanodollars',0);attempts+=int('attempt_id' in r)
        if (path.parent/'candidate.cpp').exists():proposed.update(f['rva'] for f in read(path.parent/'packet.json').get('functions',[]))
        if 'attempt_id' in r and 'charged_nanodollars' not in r:reserved+=r.get('reserved_nanodollars',0)
        for key in tokens:tokens[key]+=(r.get('usage') or {}).get(key,0)
    counts=dict(store.db.execute('SELECT state,count(*) FROM catalog GROUP BY state'));results=dict(store.db.execute('SELECT status,count(*) FROM object_results GROUP BY status'))
    value.update(functions_proposed_unvalidated=len(proposed),profile='all-inventory-coff',catalogued=sum(counts.values()),catalog_states=counts,object_results=results,exact_object_matches=results.get('exact_object_match',0),imported_native_attestations=counts.get('native_attested',0),provider_attempts=attempts,conservative_estimated_budget_debit_nanodollars=cost,outstanding_reserved_nanodollars=reserved,tokens=tokens,limits=read(Path(root)/'runtime-config.json'),updated_at=time.time())
    value.pop('functions_verified',None);return value


def run(root=ROOT,vcvars=VCVARS,ledger_dir=DEFAULT_LEDGER,global_db=DEFAULT_GLOBAL,lanes=16,request_ceiling=120,max_repairs=6,stagnation_limit=3,max_dispatches=0,only_batch=None):
    if not 1<=lanes<=16 or not 1<=request_ceiling<=120 or not 0<=max_repairs<=6:raise ValueError('object_limits')
    root=Path(root);store=open_store(root);lock=(root/'owner.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);reconcile(store);store.pause(False)
    (root/'owner.pid').write_text(str(os.getpid())+'\n');active={};ctx=multiprocessing.get_context('spawn');stopping=False;dispatched=0
    provider.atomic(root/'runtime-config.json',{'provider_lanes':lanes,'vm_build_lanes':1,'requests_per_1800_seconds':request_ceiling,'max_repairs':max_repairs,'stagnation_limit':stagnation_limit,'daily_cap_usd':50,'timezone':'America/Chicago','max_dispatches':max_dispatches,'only_batch':only_batch})
    def stop(signum,frame):
        nonlocal stopping
        stopping=True
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    try:
        while True:
            for batch,p in list(active.items()):
                if p.is_alive():continue
                p.join();active.pop(batch)
                if not read(root/'batches'/batch/'result.json').get('final_record'):store.finish(batch,'interrupted_unknown','worker_exited_unknown')
            if stopping:store.pause(True)
            while not store.paused() and len(active)<lanes and (not max_dispatches or dispatched<max_dispatches):
                batch=claim_native(store,prefer_repair=dispatched%3==2,only_batch=only_batch)
                if batch is None:break
                if batch in active:store.finish(batch,'pending','repair_worker_draining');break
                try:value,attempt=next_packet(store,batch,max_repairs);_,_,maximum,_=prepare_request(value)
                except Exception as exc:
                    remaining=[r for r in read(root/'batches'/batch/'selection.json')['rvas'] if r not in {f['rva'] for f in best_results(root/'batches'/batch) if f['status']=='exact_object_match'}]
                    children=split_batch(store,batch,remaining,'mechanical_input_budget_split',read(root/'batches'/batch/'result.json')) if isinstance(exc,ValueError) and str(exc)=='request_cap' else []
                    store.finish(batch,'complete' if children else 'input_budget_blocked','input_split' if children else type(exc).__name__+':'+str(exc))
                    if not children:
                        with store.db:store.db.execute("UPDATE catalog SET state='input_budget_blocked' WHERE batch=? AND state!='exact_object_match'",(batch,))
                    continue
                with provider.Ledger(ledger_dir).locked() as ledger:
                    day=provider.local_day();used=sum(a['charged_nanodollars'] for a in ledger['attempts'] if a['day']==day)
                    if ledger['opening_debit']['day']==day:used+=ledger['opening_debit']['charged_nanodollars']
                if used+maximum>provider.CAP:store.finish(batch,'pending','daily_budget_wait');break
                request_id,_=reserve_global(global_db,'object-'+batch+f'-attempt-{attempt}',ceiling=request_ceiling)
                if request_id is None:store.finish(batch,'pending','request_cycle_wait');break
                store.request(batch,request_id)
                if store.paused():settle_global(global_db,request_id,'cancelled_before_provider');store.finish(batch,'pending','paused_before_dispatch');break
                previous=read(root/'batches'/batch/'result.json');provider.atomic(root/'batches'/batch/'result.json',{**previous,'final_record':False,'dispatching':True,'attempt':attempt,'request_id':request_id})
                p=ctx.Process(target=process_batch,args=(root,batch,request_id,value,attempt,vcvars,ledger_dir,global_db,max_repairs,stagnation_limit));p.start();active[batch]=p;dispatched+=1
            value=status(root);value.update(owner_pid=os.getpid(),inflight=list(active),dispatched_this_run=dispatched);provider.atomic(root/'status.json',value)
            if (stopping or store.paused() or (max_dispatches and dispatched>=max_dispatches)) and not active:break
            if only_batch and not active and not store.db.execute("SELECT 1 FROM batches WHERE id=? AND state='pending'",(only_batch,)).fetchone():break
            time.sleep(2)
    finally:
        for p in active.values():p.join(timeout=400)
        provider.atomic(root/'status.json',status(root));fcntl.flock(lock,fcntl.LOCK_UN);lock.close()

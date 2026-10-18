"""Native profile for the existing small Store/two-process scheduler."""
from collections import deque
import fcntl
import json
import multiprocessing
import os
from pathlib import Path
import re
import signal
import time
from workers import deepseek_packet as provider
from rapid.store import Store,reserve_global,settle_global
from rapid.factory import REPO,MAIN,DEFAULT_GLOBAL,DEFAULT_LEDGER
from rapid.packets import PIN
from .propose import packet,prepare_request,request_packet
from .pipeline import compare

ROOT=REPO/'local/rapid-native'
VCVARS=r'C:\Users\daeken\tools\VC8-SP1\vcvars.cmd'
PILOT=REPO/'local/reccmp-pilot/native/attempt-2/build-o2/summary.json'


def native_store(root):
    store=Store(root)
    store.db.execute('''CREATE TABLE IF NOT EXISTS native_functions(rva INTEGER PRIMARY KEY,batch TEXT NOT NULL,status TEXT NOT NULL,score REAL,source TEXT NOT NULL,summary TEXT NOT NULL)''');store.db.commit()
    return store


def ingest(store,batch,functions):
    with store.db:
        for function in functions:
            old=store.db.execute('SELECT status,score FROM native_functions WHERE rva=?',(function['rva'],)).fetchone()
            if old and (old[0]=='reccmp_matched' or (old[1] is not None and old[1]>(function.get('score') or 0))):continue
            store.db.execute('INSERT OR REPLACE INTO native_functions VALUES(?,?,?,?,?,?)',(function['rva'],batch,function['status'],function.get('score'),function['source'],function['summary']))


def seed_pilot(store,path=PILOT):
    path=Path(path)
    if not path.exists():return
    summary=json.loads(path.read_text());source=path.parent/'candidate.cpp';binary=path.parent/'candidate.dll'
    if summary['module_sha256']!=PIN or provider.sha(source.read_bytes())!=summary['source_sha256'] or provider.sha(binary.read_bytes())!=summary['recompiled_sha256']:raise ValueError('pilot_bindings')
    functions=[{**f,'source':str(source),'summary':str(path)} for f in summary['functions'] if f['status']=='reccmp_matched' and f['score']==1.0 and not f['unknowns'] and f['complete_range_compared']]
    ingest(store,'retained-paid-pilot',functions)


def prepare(root=ROOT,max_groups=0):
    import pefile
    from capstone import Cs,CS_ARCH_X86,CS_MODE_32,CS_OP_IMM,CS_OP_MEM,CS_GRP_JUMP
    root=Path(root);store=native_store(root)
    lock=(root/'owner.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    seed_pilot(store);raw=(MAIN/'gamedata/bin_ship/DAOrigins.exe').read_bytes()
    if provider.sha(raw)!=PIN:raise ValueError('original_pin')
    inventory=json.loads((MAIN/'local/analysis/functions.json').read_text());original={f['rva']:f for f in inventory['functions']}
    excluded={f['rva'] for f in json.loads((MAIN/'analysis/functions.json').read_text())['functions']}
    excluded.update(r[0] for r in store.db.execute('SELECT rva FROM native_functions WHERE status="reccmp_matched"'))
    owned={r[0] for r in store.db.execute('SELECT rva FROM identities')}
    pe=pefile.PE(data=raw);base=pe.OPTIONAL_HEADER.ImageBase;md=Cs(CS_ARCH_X86,CS_MODE_32);md.detail=True
    ranges=sorted((r['start_rva'],r['end_rva_inclusive'],f['rva']) for f in original.values() for r in f['body_ranges']);overlaps=set();active=[]
    for start,end,rva in ranges:
        active=[v for v in active if v[1]>=start]
        for _,_,other in active:
            if other!=rva:overlaps.update((other,rva))
        active.append((start,end,rva))
    allowed=set('mov movzx movsx lea add adc sub sbb and or xor not neg inc dec cmp test shl sal shr sar rol ror rcl rcr imul mul idiv div cdq cwd cwde cbw push pop ret nop bswap xchg bt bts btr btc'.split())
    graph={};parents={};eligible={};rejections=[]
    for rva,f in original.items():
        rr=f['body_ranges'];decoded=[]
        for r in rr:
            b=pe.get_data(r['start_rva'],r['end_rva_inclusive']-r['start_rva']+1)
            decoded.extend(md.disasm(b,base+r['start_rva']))
        calls=[i.operands[0].imm-base for i in decoded if i.mnemonic=='call' and i.operands and i.operands[0].type==CS_OP_IMM]
        graph[rva]=[t for t in calls if t in original]
        for target in graph[rva]:parents.setdefault(target,[]).append(rva)
        reason=None
        if rva in excluded:reason='historical_or_seeded_match'
        elif rva in owned:reason='already_queued'
        elif len(rr)!=1 or rr[0]['start_rva']!=rva:reason='noncontiguous_boundary'
        elif rva in overlaps:reason='overlapping_boundary'
        elif not 1<=f['body_bytes']<=256 or len(decoded)>96:reason='large_body_delayed'
        else:
            size=rr[0]['end_rva_inclusive']-rva+1;section=pe.get_section_by_rva(rva)
            if not section or not section.Characteristics&0x20000000 or rr[0]['end_rva_inclusive']>=section.VirtualAddress+min(section.Misc_VirtualSize,section.SizeOfRawData):reason='nonexecutable_or_unbacked'
            elif not decoded or sum(i.size for i in decoded)!=size or decoded[-1].mnemonic!='ret':reason='incomplete_decode_or_no_return'
            else:
                for i in decoded:
                    jump=i.group(CS_GRP_JUMP)
                    if not (i.mnemonic in allowed or jump or i.mnemonic.startswith(('set','cmov'))):reason='unsupported_instruction';break
                    if jump and (not i.operands or i.operands[0].type!=CS_OP_IMM or not base+rva<=i.operands[0].imm<base+rva+size):reason='external_or_indirect_branch';break
                    if any(o.type==CS_OP_MEM and (i.reg_name(o.mem.base) not in ('esp','ebp') or o.mem.index or o.mem.segment or abs(o.mem.disp)>512) for o in i.operands):reason='nonstack_memory_or_segment';break
                    if not jump and any(o.type==CS_OP_IMM and pe.get_section_by_rva(o.imm-base) is not None for o in i.operands if o.type==CS_OP_IMM and o.imm>=base):reason='potential_unmapped_address_constant';break
        if reason:rejections.append({'rva':rva,'reason':reason});continue
        b=pe.get_data(rva,size)
        eligible[rva]={'name':f'fn_{rva:08x}','rva':rva,'original_va':base+rva,'bytes_sha256':provider.sha(b),'bytes_hex':b.hex(),'size':size,'instructions':[f'{i.address:08x}: {i.mnemonic} {i.op_str}' for i in decoded],'inventory_hypothesis':f}
    walk=deque([pe.OPTIONAL_HEADER.AddressOfEntryPoint,0x16ad0,0x4e19e0,0xc2480]);seen=set();order=[]
    while walk:
        rva=walk.popleft()
        if rva in seen:continue
        seen.add(rva)
        if rva in eligible:order.append(rva)
        walk.extend(graph.get(rva,[]))
    order.extend(r for r in sorted(eligible) if r not in seen)
    template=packet([]);template['profile']='call-free-stack-integer-v1';available=set(eligible);groups=0
    for index,seed in enumerate(order):
        if seed not in available:continue
        related=[target for parent in parents.get(seed,[]) for target in graph.get(parent,[])]
        choices=list(dict.fromkeys([seed]+related+order[index+1:index+100]));group=[];instructions=0
        for rva in choices:
            if rva not in available:continue
            f=eligible[rva];trial={**template,'functions':sorted(group+[f],key=lambda item:item['rva'])}
            if len(provider.encode(trial))>30000 or instructions+len(f['instructions'])>160:continue
            group.append(f);instructions+=len(f['instructions'])
            if len(group)>=16:break
        if not group:rejections.append({'rva':seed,'reason':'packet_output_budget'});available.remove(seed);continue
        value={**template,'functions':sorted(group,key=lambda f:f['rva'])};ident=provider.sha(provider.encode(value));folder=root/'batches'/ident;folder.mkdir(parents=True,exist_ok=True,mode=0o700);provider.atomic(folder/'packet.json',value)
        if store.add(ident,[f['rva'] for f in value['functions']]):groups+=1
        available.difference_update(f['rva'] for f in group)
        if max_groups and groups>=max_groups:break
    store.pause(True)
    provider.atomic(root/'preparation.json',{'schema_version':1,'module_sha256':PIN,'profile':'call-free-stack-integer-v1','groups_added':groups,'eligible_new_functions':len(eligible),'exclusions':rejections,'max_functions':16,'max_packet_bytes':30000,'max_instructions':160,'boundary_provenance':'existing_static_inventory_hypotheses'})
    fcntl.flock(lock,fcntl.LOCK_UN);lock.close();return status(root)


def best_functions(evaluations):
    best={}
    for source,summary_path,summary in evaluations:
        for f in summary.get('functions',[]):
            candidate={**f,'source':str(source),'summary':str(summary_path)};old=best.get(f['rva'])
            if old is None or (old['status']!='reccmp_matched' and (f['status']=='reccmp_matched' or (f.get('score') or 0)>(old.get('score') or 0))):best[f['rva']]=candidate
    return list(best.values())


def next_packet(root,batch):
    folder=Path(root)/'batches'/batch;value=json.loads((folder/'packet.json').read_text());result=folder/'result.json'
    previous=json.loads(result.read_text()) if result.exists() else {}
    if previous.get('needs_repair'):
        source=folder/'attempt-1/candidate.cpp';feedback={'previous_source':source.read_text(),'summary':previous.get('functions',[]),'instruction':'Keep already matched definitions unchanged. Repair remaining mismatches from actual compiler/reccmp diagnostics using native C++ only. This is the single repair; no assembly or wrappers.'}
        diagnostics=[]
        for path in sorted((folder/'attempt-1').glob('build-*/*')):
            if path.name=='build.log' or path.name.startswith('diff-'):
                diagnostics.append(path.name+'\n'+re.sub(r'\x1b\[[0-9;]*m','',path.read_text(errors='replace'))[:16000])
        feedback['actual_diagnostics']='\n'.join(diagnostics)[:65000];value['repair_feedback']=feedback
        return value,2
    return value,1


def evaluate(root,batch,attempt,vcvars):
    folder=Path(root)/'batches'/batch/f'attempt-{attempt}';source=folder/'candidate.cpp'
    # Single isolated VM build phase; provider lanes stay independent processes.
    with (Path(root)/'vm-build.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        for trial in (1,2):
            output=folder/f'build-{trial}'
            try:result=compare(source,output,vcvars)
            except Exception as exc:return None,{'error':type(exc).__name__,'transport_failure':True}
            if (output/'summary.json').exists():return (source,output/'summary.json',result),None
            # One mechanical transport retry; compiler/diff failures go to model repair.
            build_exit=output/'build-exit.txt'
            if build_exit.exists():return None,{'error':'compiler_or_compare_failure','transport_failure':False}
        return None,{'error':'vm_transport_failure','transport_failure':True}



def retained_evaluations(folder,attempt,requested):
    evaluations=[]
    for number in range(1,attempt+1):
        source=folder/f'attempt-{number}/candidate.cpp'
        for path in sorted((folder/f'attempt-{number}').glob('build-*/summary.json')):
            summary=json.loads(path.read_text());functions=summary.get('functions',[])
            if summary.get('module_sha256')!=PIN or len(functions)!=len(requested) or {f['rva'] for f in functions}!=requested:continue
            checks=[(source,'source_sha256'),(path.parent/'candidate.dll','recompiled_sha256'),(path.parent/'candidate.pdb','pdb_sha256')]
            if any(not artifact.is_file() or provider.sha(artifact.read_bytes())!=summary.get(key) for artifact,key in checks):continue
            evaluations.append((source,path,summary))
    return evaluations

def process_batch(root,batch,request_id,value,attempt,vcvars,ledger_dir,global_db):
    root=Path(root);store=native_store(root);folder=root/'batches'/batch;result={'schema_version':1,'packet_sha256':batch,'final_record':False,'outcome':'error','needs_repair':False}
    try:
        if provider.sha((folder/'packet.json').read_bytes())!=batch:raise ValueError('packet_identity')
        request=request_packet(folder/f'attempt-{attempt}',value,request_id,ledger_dir,global_db)
        if request['outcome']!='success':raise ValueError('provider_'+request['outcome'])
        observed,error=evaluate(root,batch,attempt,vcvars);requested={f['rva'] for f in value['functions']}
        best=best_functions(retained_evaluations(folder,attempt,requested))
        if observed and {f['rva'] for f in observed[2]['functions']}!=requested:raise ValueError('comparison_domain_mismatch')
        matched=sum(f['status']=='reccmp_matched' for f in best)
        repair=(attempt==1 and matched<len(requested) and not (error and error['transport_failure']))
        result.update(outcome='success',functions=best,attempts=attempt,needs_repair=repair,matched=matched,requested=len(requested),error=error)
        state='pending' if repair else 'complete'
    except BaseException as exc:
        result['error']=type(exc).__name__;state='error'
    if 'functions' not in result:
        result['functions']=best_functions(retained_evaluations(folder,attempt,{f['rva'] for f in value['functions']}))
    result['final_record']=True;provider.atomic(folder/'result.json',result);store.finish(batch,state,'repair_pending' if result['needs_repair'] else None)


def reconcile(store):
    for batch, in store.db.execute("SELECT id FROM batches WHERE state='claimed'").fetchall():
        path=store.root/'batches'/batch/'result.json';value=json.loads(path.read_text()) if path.exists() else {}
        if value.get('final_record') and not value.get('dispatching'):
            ingest(store,batch,value.get('functions',[]));store.finish(batch,'pending' if value.get('needs_repair') else ('complete' if value.get('outcome')=='success' else 'error'),'reconciled_retained_result')
        else:store.finish(batch,'interrupted_unknown','paid_outcome_not_replayed')


def status(root=ROOT):
    root=Path(root);store=native_store(root);value=store.status();counts=dict(store.db.execute('SELECT status,count(*) FROM native_functions GROUP BY status'));cost=0;requests=0;latencies=[];tokens={'prompt_tokens':0,'completion_tokens':0};reserved=0
    for path in (root/'batches').glob('*/attempt-*/result.json'):
        record=json.loads(path.read_text());cost+=record.get('charged_nanodollars',0);requests+=int('attempt_id' in record)
        if 'attempt_id' in record and 'charged_nanodollars' not in record:reserved+=record.get('reserved_nanodollars',0)
        for key in tokens:tokens[key]+=(record.get('usage') or {}).get(key,0)
        if 'elapsed_seconds' in record:latencies.append(record['elapsed_seconds'])
    value.update(profile='native-reccmp',reccmp_matched=counts.get('reccmp_matched',0),retained_unmatched=counts.get('retained_unmatched',0),native_functions_observed=sum(counts.values()),provider_attempts=requests,charged_nanodollars=cost,outstanding_reserved_nanodollars=reserved,tokens=tokens,mean_provider_seconds=sum(latencies)/len(latencies) if latencies else None,seeded_paid_pilot=4,updated_at=time.time())
    return value


def run(root=ROOT,vcvars=VCVARS,ledger_dir=DEFAULT_LEDGER,global_db=DEFAULT_GLOBAL):
    root=Path(root);store=native_store(root);lock=(root/'owner.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    reconcile(store);seed_pilot(store);store.pause(False);(root/'owner.pid').write_text(str(os.getpid())+'\n');active={};ctx=multiprocessing.get_context('spawn');stopping=False
    def stop(signum,frame):
        nonlocal stopping
        stopping=True
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    try:
        while True:
            for batch,p in list(active.items()):
                if p.is_alive():continue
                p.join();active.pop(batch);path=root/'batches'/batch/'result.json';value=json.loads(path.read_text()) if path.exists() else {}
                if value.get('final_record') and not value.get('dispatching'):ingest(store,batch,value.get('functions',[]))
                else:store.finish(batch,'interrupted_unknown','worker_exited_unknown')
            if stopping:store.pause(True)
            while not store.paused() and len(active)<2:
                batch=store.next()
                if batch is None:break
                if batch in active:
                    store.finish(batch,'pending','worker_draining');break
                try:value,attempt=next_packet(root,batch);body,_,maximum,_=prepare_request(value)
                except Exception as exc:
                    store.finish(batch,'error','packet_preflight_'+type(exc).__name__);continue
                with provider.Ledger(ledger_dir).locked() as ledger:
                    day=provider.local_day();used=sum(a['charged_nanodollars'] for a in ledger['attempts'] if a['day']==day)
                    if ledger['opening_debit']['day']==day:used+=ledger['opening_debit']['charged_nanodollars']
                    exhausted=used+maximum>provider.CAP
                if exhausted:store.finish(batch,'pending','daily_budget_wait');break
                request_id,next_cycle=reserve_global(global_db,'native-'+batch+f'-attempt-{attempt}')
                if request_id is None:store.finish(batch,'pending','request_cycle_wait');break
                store.request(batch,request_id)
                if store.paused():settle_global(global_db,request_id,'cancelled_before_provider');store.finish(batch,'pending','paused_before_dispatch');break
                provider.atomic(root/'batches'/batch/'result.json',{'final_record':False,'dispatching':True,'attempt':attempt,'request_id':request_id})
                p=ctx.Process(target=process_batch,args=(root,batch,request_id,value,attempt,vcvars,ledger_dir,global_db));p.start();active[batch]=p
            value=status(root);value.update(owner_pid=os.getpid(),inflight=list(active));provider.atomic(root/'status.json',value)
            if stopping and not active:break
            time.sleep(2 if active else 15)
    finally:
        for p in active.values():p.join(timeout=400)
        provider.atomic(root/'status.json',status(root));fcntl.flock(lock,fcntl.LOCK_UN);lock.close()

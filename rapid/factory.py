"""Two process lanes; no retries; all proposals remain unvalidated."""
import argparse
import fcntl
import json
import multiprocessing
import os
import re
from pathlib import Path
import shutil
import signal
import subprocess
import time
from workers import deepseek_packet as provider
from rapid.store import Store, reserve_global, settle_global
from rapid.packets import prepare, PIN

REPO=Path(__file__).resolve().parents[1]
MAIN=Path('/Users/daeken/projects/DAODecomp')
DEFAULT_GLOBAL=MAIN/'local/dispatcher-setup-001/runtime-final/state.sqlite3'
DEFAULT_LEDGER=MAIN/'local/providers/deepseek-daily'


def build_request(packet):
    names=[f['name'] for f in packet['functions']]
    if not names or len(names)!=len(set(names)): raise ValueError('duplicate_or_empty_functions')
    instructions=('Return exactly one JSON object with no markdown fences, matching this schema: '+json.dumps(provider.RESPONSE_SCHEMA))
    body=provider.encode({'model':'deepseek-flash','messages':[{'role':'system','content':instructions},{'role':'user','content':provider.encode(packet).decode()}],
        'thinking':{'type':'enabled'},'reasoning_effort':'low','response_format':{'type':'json_object'},'max_tokens':provider.MAX_OUTPUT,'stream':False})
    if len(body)>provider.MAX_INPUT_BYTES: raise ValueError('input_byte_cap')
    domain=[{'name':f['name'],'id':f"{packet['module']}:{packet['module_sha256']}:rva-{f['rva']:08x}"} for f in packet['functions']]
    manifest={'schema_version':1,'candidate_only':True,'abi_sha256':packet['abi_sha256'],'functions':domain}
    bindings={'manifest_sha256':provider.sha(provider.encode(manifest)),'packet_sha256':provider.sha(provider.encode(packet)),
        'response_schema_sha256':provider.sha(provider.encode(provider.RESPONSE_SCHEMA)),'request_sha256':provider.sha(body),'function_domain_sha256':provider.sha(provider.encode(domain))}
    maximum=(len(body)+2048)*provider.RATES['uncached']+provider.MAX_OUTPUT*provider.RATES['output']
    return body,bindings,maximum,names,manifest


def compile_source(source,folder,repo=REPO):
    compiler=shutil.which('clang++') or shutil.which('c++')
    if compiler is None: return False,'compiler_unavailable'
    try:
        run=subprocess.run([compiler,'-std=c++20','-fsyntax-only','-I',str(repo),str(source)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=45)
        (folder/'compile.log').write_bytes(run.stdout[:1024*1024])
        return run.returncode==0,compiler
    except subprocess.TimeoutExpired:
        (folder/'compile.log').write_text('compile_timeout\n'); return False,compiler


def execute(root,batch,ledger_dir,global_db,request_id):
    root=Path(root); folder=root/'batches'/batch; result={'schema_version':1,'packet_sha256':batch,'validation_status':'unvalidated','compile_ready':False,'outcome':'error','final_record':False}
    outcome='transport_error'; usage=None; attempt=None; started=time.time()
    try:
        packet=provider.strict_json((folder/'packet.json').read_bytes())
        if provider.sha(provider.encode(packet))!=batch or packet['module_sha256']!=PIN: raise ValueError('packet_identity')
        header=provider.read_regular(REPO/'rapid/context.hpp')
        if provider.sha(header)!=packet['abi_sha256']: raise ValueError('abi_changed_before_dispatch')
        abi_folder=root/'abi'/packet['abi_sha256']; abi_folder.mkdir(parents=True,exist_ok=True,mode=0o700)
        abi_header=abi_folder/'context.hpp'
        if abi_header.exists() and abi_header.read_bytes()!=header: raise ValueError('abi_object_collision')
        abi_header.write_bytes(header)
        body,bindings,maximum,names,manifest=build_request(packet)
        (folder/'request.json').write_bytes(body); provider.atomic(folder/'manifest.json',manifest)
        result.update(**bindings,abi_sha256=packet['abi_sha256'],abi_header=str(abi_header),module_sha256=PIN,functions=packet['functions'],request_id=request_id,
            model='deepseek-flash',reasoning_effort='low',max_tokens=provider.MAX_OUTPUT,request_bytes=len(body),automatic_retry=False)
        ledger=provider.Ledger(ledger_dir); attempt,day=ledger.reserve(bindings,maximum)
        result.update(attempt_id=attempt,budget_day=day,reserved_nanodollars=maximum)
        provider.atomic(folder/'result.json',result)
        # Existing vetted transport handles credential echo scanning and SIGALRM.
        # Never log key values, arbitrary network exception strings, or headers.
        key=provider.read_regular(Path.home()/'.deepseek.key',4096).decode().strip()
        if not key or not key.isascii() or any(c.isspace() for c in key): raise provider.Refusal('credential_unavailable')
        outcome,raw,http_status=provider.transport(body,key); del key
        result['http_status']=http_status
        if raw is not None:
            (folder/'raw-response.json').write_bytes(raw)
            result['raw_response_sha256']=provider.sha(raw)
            try:
                envelope=provider.strict_json(raw); usage=provider.normalized_usage(envelope.get('usage'))
                result.update(returned_model=provider.safe_identifier(envelope.get('model')),provider_request_id=provider.safe_identifier(envelope.get('id')))
                choices=envelope.get('choices')
                if type(choices) is not list or len(choices)!=1: raise ValueError('choices')
                choice=choices[0]; result['finish_reason']=provider.safe_identifier(choice.get('finish_reason'))
                if choice.get('finish_reason')!='stop': raise ValueError('incomplete_response')
                message=choice['message']
                if message.get('tool_calls') or message.get('function_call'): raise ValueError('unexpected_tools')
                response=provider.source_response(provider.strict_json(message['content']),names)
                provider.atomic(folder/'response.json',response)
                source=response['source'].encode(); digest=provider.sha(source)
                objects=root/'objects'; objects.mkdir(exist_ok=True,mode=0o700)
                target=objects/(digest+'.cpp')
                if target.exists() and target.read_bytes()!=source: raise ValueError('source_object_collision')
                target.write_bytes(source); (folder/'source.cpp').write_bytes(source)
                ready,compiler=compile_source(folder/'source.cpp',folder)
                # A declaration-only proposal cannot count as a produced ABI body.
                definitions=all(re.search(r'\bvoid\s+'+re.escape(name)+r'\s*\([^;{}]*\)\s*\{',response['source']) for name in names)
                ready=ready and definitions
                result.update(response_sha256=provider.sha((folder/'response.json').read_bytes()),source_sha256=digest,source_object=str(target),
                    compile_ready=ready,compiler=compiler,uncertainties=response['uncertainties'],function_notes=response['functions'])
                outcome='success'
            except Exception: outcome='invalid_response'
        result['outcome']=outcome
    except provider.Refusal as exc:
        result['error']=str(exc) if str(exc) in {'daily_budget_exhausted','credential_unavailable'} else 'provider_refusal'
    except BaseException as exc:
        result['error']=type(exc).__name__
    finally:
        if attempt is not None:
            try:
                charged=provider.Ledger(ledger_dir).settle(attempt,outcome,usage)
                result.update(charged_nanodollars=charged,estimated_nanodollars=provider.price_usage(usage),usage=usage,charge_is_uncertain_reservation=usage is None)
            except Exception: result['ledger_settlement']='unknown_reservation_retained'
        result['final_record']=True
        result['elapsed_seconds']=round(time.time()-started,3)
        provider.atomic(folder/'result.json',result)
        settle_global(global_db,request_id,'complete' if result.get('outcome')=='success' else 'error')
        Store(root).finish(batch,'complete' if result.get('outcome')=='success' else 'error',result.get('error'))


def status(root):
    store=Store(root); value=store.status(); ready=produced=0; cost=0; seconds=[]; usage={'prompt_tokens':0,'completion_tokens':0}
    for batch,state in store.db.execute("SELECT id,state FROM batches WHERE state IN ('complete','error')"):
        path=Path(root)/'batches'/batch/'result.json'
        if not path.exists(): continue
        result=json.loads(path.read_text()); n=len(result.get('function_notes',[]))
        produced+=n; ready+=n if result.get('compile_ready') else 0
        cost+=result.get('charged_nanodollars',0); seconds.append(result.get('elapsed_seconds',0))
        for key in usage: usage[key]+=(result.get('usage') or {}).get(key,0)
    value.update(functions_proposed_unvalidated=produced,functions_compile_ready_unvalidated=ready,charged_nanodollars=cost,
        average_request_seconds=sum(seconds)/len(seconds) if seconds else None,tokens=usage,updated_at=time.time())
    return value


def run(root,ledger_dir,global_db,pilot=False):
    root=Path(root); store=Store(root)
    lock=(root/'owner.lock').open('a+')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    (root/'owner.pid').write_text(str(os.getpid())+'\n'); store.reconcile(); store.pause(False)
    context=multiprocessing.get_context('spawn'); active={}; dispatched=0; stopping=False
    def stop(signum,frame):
        nonlocal stopping
        stopping=True
    signal.signal(signal.SIGTERM,stop); signal.signal(signal.SIGINT,stop)
    try:
        while True:
            for batch,process in list(active.items()):
                if not process.is_alive():
                    process.join(); active.pop(batch)
                    row=store.db.execute('SELECT state FROM batches WHERE id=?',(batch,)).fetchone()
                    if row and row[0]=='claimed': store.finish(batch,'interrupted_unknown','child_exited_without_final_record')
            if stopping: store.pause(True)
            while not stopping and not store.paused() and len(active)<2 and (not pilot or dispatched<2):
                batch=store.next()
                if batch is None: break
                # Daily cap is independently enforced at exact body reservation in child.
                with provider.Ledger(ledger_dir).locked() as ledger:
                    day=provider.local_day(); charged=sum(a['charged_nanodollars'] for a in ledger['attempts'] if a['day']==day)
                    if ledger['opening_debit']['day']==day: charged+=ledger['opening_debit']['charged_nanodollars']
                    packet=provider.strict_json((root/'batches'/batch/'packet.json').read_bytes()); maximum=build_request(packet)[2]
                    exhausted=charged+maximum>provider.CAP
                if exhausted:
                    store.finish(batch,'pending','daily_budget_wait'); break
                request_id,next_cycle=reserve_global(global_db,batch)
                if request_id is None:
                    store.finish(batch,'pending','request_cycle_wait'); break
                store.request(batch,request_id)
                if store.paused():
                    settle_global(global_db,request_id,'cancelled_before_provider'); store.finish(batch,'pending','paused_before_provider'); break
                process=context.Process(target=execute,args=(root,batch,ledger_dir,global_db,request_id))
                process.start(); active[batch]=process; dispatched+=1
            value=status(root); value.update(owner_pid=os.getpid(),inflight=list(active),pilot=pilot)
            provider.atomic(root/'status.json',value)
            if (stopping or (pilot and dispatched>=2)) and not active: break
            # Pilot does not transition automatically unless mechanical checks pass.
            if pilot and dispatched>=2 and not active: break
            time.sleep(2 if active else 15)
    finally:
        for process in active.values(): process.join(timeout=provider.TIMEOUT+60)
        provider.atomic(root/'status.json',status(root)); fcntl.flock(lock,fcntl.LOCK_UN); lock.close()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=REPO/'local/rapid')
    p.add_argument('--main',type=Path,default=MAIN)
    p.add_argument('--global-db',type=Path,default=DEFAULT_GLOBAL)
    p.add_argument('--ledger',type=Path,default=DEFAULT_LEDGER)
    sub=p.add_subparsers(dest='command',required=True)
    prep=sub.add_parser('prepare'); prep.add_argument('--max-groups',type=int,default=0)
    runner=sub.add_parser('run'); runner.add_argument('--pilot',action='store_true')
    pause=sub.add_parser('pause'); pause.add_argument('--resume',action='store_true')
    sub.add_parser('status')
    args=p.parse_args(); os.umask(0o077)
    if args.command=='prepare': value=prepare(args.root,args.main,REPO,args.max_groups)
    elif args.command=='status': value=status(args.root)
    elif args.command=='pause':
        store=Store(args.root); store.pause(not args.resume); value=store.status()
    else:
        run(args.root,args.ledger,args.global_db,args.pilot); value=status(args.root)
    print(json.dumps(value,sort_keys=True,indent=2))
if __name__=='__main__': main()

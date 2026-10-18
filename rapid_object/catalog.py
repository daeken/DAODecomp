"""Every inventory identity is catalogued; difficult cases become work, not exclusions."""
from collections import deque
import json
from pathlib import Path
from rapid.store import Store
from rapid.factory import MAIN,REPO
from rapid.packets import PIN
from workers.deepseek_packet import atomic,encode,sha

ROOT=REPO/'local/rapid-object'


def open_store(root=ROOT):
    store=Store(root)
    store.db.executescript('''CREATE TABLE IF NOT EXISTS catalog(rva INTEGER PRIMARY KEY,identity TEXT UNIQUE NOT NULL,state TEXT NOT NULL,batch TEXT,signature_json TEXT NOT NULL,details_json TEXT NOT NULL,native_evidence_json TEXT);
    CREATE TABLE IF NOT EXISTS object_symbols(name TEXT PRIMARY KEY,kind TEXT NOT NULL,original_va INTEGER NOT NULL,details_json TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS object_results(rva INTEGER PRIMARY KEY,batch TEXT NOT NULL,status TEXT NOT NULL,score REAL NOT NULL,source TEXT NOT NULL,summary TEXT NOT NULL);''');store.db.commit();return store


def pages(units,cap=36000):
    result=[];current=[];size=0
    for unit in units:
        cost=len(encode(unit))
        if current and size+cost>cap:result.append(current);current=[];size=0
        current.append(unit);size+=cost
    if current or not result:result.append(current)
    return result


def group_order(functions,graph,entry):
    queue=deque([entry,0x16ad0,0x4e19e0,0xc2480]);seen=set();order=[]
    while queue:
        rva=queue.popleft()
        if rva in seen:continue
        seen.add(rva)
        if rva in functions:order.append(rva)
        queue.extend(graph.get(rva,[]))
    order.extend(r for r in sorted(functions) if r not in seen);return order


def read_native_attestations(path=None):
    import sqlite3
    path=Path(path) if path is not None else REPO/'local/rapid-native/queue.sqlite3'
    if not path.exists():return {}
    db=sqlite3.connect('file:'+str(path)+'?mode=ro',uri=True);result={};cache={}
    try:
        for rva,source,summary_path in db.execute("SELECT rva,source,summary FROM native_functions WHERE status='reccmp_matched'"):
            path=Path(summary_path)
            if summary_path not in cache:
                try:
                    report=json.loads(path.read_text());valid=report['module_sha256']==PIN and sha(Path(source).read_bytes())==report['source_sha256'] and sha((path.parent/'candidate.dll').read_bytes())==report['recompiled_sha256']
                    cache[summary_path]=report if valid else None
                except (OSError,KeyError,ValueError):cache[summary_path]=None
            report=cache[summary_path]
            if report and sha(Path(source).read_bytes())==report['source_sha256'] and any(f['rva']==rva and f['status']=='reccmp_matched' and f['score']==1.0 and f.get('complete_range_compared') and not f.get('unknowns') for f in report['functions']):result[rva]={'kind':'existing_native_reccmp_attestation','source':source,'summary':summary_path,'source_sha256':report['source_sha256'],'binary_sha256':report['recompiled_sha256']}
    finally:db.close()
    return result


def assign_groups(store,functions,native,entry_rva,max_group_functions=12):
    root=store.root;graph={r:f['direct_calls'] for r,f in functions.items()};parents={}
    for r,targets in graph.items():
        for t in targets:parents.setdefault(t,[]).append(r)
    if native and any(r not in {row[0] for row in store.db.execute('SELECT rva FROM identities')} for r in native):
        rvas=sorted(set(native)&set(functions));ident='native-attested-'+sha(encode(rvas));store.add(ident,rvas);store.finish(ident,'complete','imported_existing_attestation_no_provider_request')
        with store.db:store.db.executemany('UPDATE catalog SET batch=? WHERE rva=?',[(ident,r) for r in rvas])
        atomic(root/'imported-native-attestations.json',{str(r):native[r] for r in rvas})
    order=group_order(functions,graph,entry_rva);available=set(functions)-{r[0] for r in store.db.execute('SELECT rva FROM identities')};groups=0
    for index,seed in enumerate(order):
        if seed not in available:continue
        candidates=list(dict.fromkeys([seed]+graph.get(seed,[])+[target for caller in parents.get(seed,[]) for target in graph.get(caller,[])]+order[index+1:index+100]));group=[];size=0
        for rva in candidates:
            if rva not in available:continue
            entry=functions[rva];cost=len(encode(entry['context_pages'][0]))
            if group and (len(entry['context_pages'])>1 or size+cost>50000):continue
            if not group or len(entry['context_pages'])==1:group.append(rva);size+=cost
            if len(entry['context_pages'])>1 or len(group)>=max_group_functions:break
        ident=sha(encode({'module_sha256':PIN,'functions':group}));folder=root/'batches'/ident;folder.mkdir(parents=True,exist_ok=True,mode=0o700)
        atomic(folder/'selection.json',{'module_sha256':PIN,'rvas':group});store.add(ident,group)
        with store.db:store.db.executemany('UPDATE catalog SET batch=? WHERE rva=?',[(ident,r) for r in group])
        available.difference_update(group);groups+=1
    return groups


def prepare(root=ROOT,max_group_functions=12):
    import fcntl
    import pefile
    from capstone import Cs,CS_ARCH_X86,CS_MODE_32,CS_OP_IMM,CS_OP_MEM
    root=Path(root);store=open_store(root);lock=(root/'owner.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    if store.db.execute('SELECT count(*) FROM catalog').fetchone()[0]:
        functions={r:json.loads(details) for r,details in store.db.execute('SELECT rva,details_json FROM catalog')}
        native={r:json.loads(ev) for r,ev in store.db.execute('SELECT rva,native_evidence_json FROM catalog WHERE native_evidence_json IS NOT NULL')}
        groups=assign_groups(store,functions,native,0x4e3024,max_group_functions);store.pause(True)
        report={'catalogued':len(functions),'all_identities_owned':store.db.execute('SELECT count(*) FROM identities').fetchone()[0],'native_attested':len(native),'new_generation_identities':len(functions)-len(native),'groups_added':groups,'excluded':0,'existing_catalog_preserved':True}
        fcntl.flock(lock,fcntl.LOCK_UN);lock.close();return report
    raw=(MAIN/'gamedata/bin_ship/DAOrigins.exe').read_bytes();inventory_raw=(MAIN/'local/analysis/functions.json').read_bytes();inventory=json.loads(inventory_raw)
    if sha(raw)!=PIN or inventory['module_sha256']!=PIN:raise ValueError('original_or_inventory_pin')
    pe=pefile.PE(data=raw);base=pe.OPTIONAL_HEADER.ImageBase;md=Cs(CS_ARCH_X86,CS_MODE_32);md.detail=True;functions={};graph={};symbols={};parents={};native=read_native_attestations()
    pe.parse_data_directories(directories=[1]);imports={}
    for module in getattr(pe,'DIRECTORY_ENTRY_IMPORT',[]):
        for item in module.imports:imports[item.address]={'dll':module.dll.decode(errors='replace'),'name':item.name.decode(errors='replace') if item.name else None,'ordinal':item.ordinal}
    for original in inventory['functions']:
        rva=original['rva'];units=[];ranges=[];whole=bytearray();calls=[];refs=set();returns=[];errors=[];observations={'indirect_calls':[],'segmented_access':False,'floating_point':False}
        for rr in original['body_ranges']:
            start=rr['start_rva'];size=rr['end_rva_inclusive']-start+1
            try:b=pe.get_data(start,size)
            except Exception:b=b'';errors.append({'range':rr,'error':'unreadable_original_bytes'})
            whole.extend(b);ranges.append({**rr,'bytes_sha256':sha(b),'read_bytes':len(b),'expected_bytes':size})
            ins=list(md.disasm(b,base+start));decoded=sum(i.size for i in ins)
            for i in ins:
                units.append({'address':i.address,'bytes':i.bytes.hex(),'instruction':i.mnemonic+' '+i.op_str})
                if i.mnemonic.startswith('f') or any('xmm' in i.reg_name(reg) for reg in i.regs_read):observations['floating_point']=True
                if i.mnemonic=='ret':returns.append(i.operands[0].imm if i.operands else 0)
                if i.mnemonic=='call':
                    if i.operands and i.operands[0].type==CS_OP_IMM:calls.append(i.operands[0].imm-base)
                    else:observations['indirect_calls'].append({'address':i.address,'operand':i.op_str})
                for operand in i.operands:
                    value=None
                    if operand.type==CS_OP_MEM:
                        if operand.mem.segment:observations['segmented_access']=True
                        if not operand.mem.base and not operand.mem.index:value=operand.mem.disp&0xffffffff
                    elif operand.type==CS_OP_IMM and i.mnemonic not in ('call','jmp') and not i.mnemonic.startswith('j'):value=operand.imm&0xffffffff
                    if value is not None and value>=base and pe.get_section_by_rva(value-base) is not None:refs.add(value)
            if decoded<len(b):
                errors.append({'range':rr,'error':'incomplete_decode','decoded_bytes':decoded})
                for offset in range(decoded,len(b),64):units.append({'address':base+start+offset,'bytes':b[offset:offset+64].hex(),'instruction':'<undecoded original bytes; unknown semantics>'})
            if len(b)!=size:errors.append({'range':rr,'error':'incomplete_original_range_read'})
        signature={'status':'unknown','inventory_signature_hypothesis':original.get('signature_hypothesis'),'inventory_calling_convention_hypothesis':original.get('calling_convention_hypothesis'),'observed_ret_cleanup_bytes':sorted(set(returns)),'warning':'undefined fn(void) is not evidence of zero arguments; declarations may be refined in candidate C++'}
        entry={'name':f'fn_{rva:08x}','rva':rva,'original_va':base+rva,'ranges':ranges,'bytes_sha256':sha(whole),'signature_hypothesis':signature,'direct_calls':calls,'address_references':sorted(refs),'observations':observations,'boundary_provenance':'static_inventory_hypothesis','errors':errors,'context_pages':pages(units)}
        functions[rva]=entry;graph[rva]=calls
        for target in calls:parents.setdefault(target,[]).append(rva)
        symbols[entry['name']]={'kind':'function_identity','original_va':base+rva,'signature_hypothesis':signature}
        for address in refs:
            name=f'g_{address-base:08x}';data=pe.get_data(address-base,32)
            symbols[name]={'kind':'import_slot' if address in imports else 'operand_address_hypothesis','original_va':address,'observed_in_function_rva':rva,'bytes_hex':data.hex(),'import':imports.get(address),'declaration_hypothesis':f'extern "C" unsigned char {name}[]; /* refine the type locally; never define a successful stub */'}
    for caller,targets in graph.items():
        for target in targets:
            name=f'fn_{target:08x}'
            symbols.setdefault(name,{'kind':'observed_direct_call_target','original_va':base+target,'observed_in_function_rva':caller,'signature_hypothesis':{'status':'unknown'}})
    for address,record in imports.items():symbols.setdefault(f'g_{address-base:08x}',{'kind':'import_slot','original_va':address,'import':record})
    for rva,record in functions.items():record['incoming_calls']=parents.get(rva,[])
    with store.db:
        store.db.executemany('INSERT INTO object_symbols VALUES(?,?,?,?)',[(name,record['kind'],record['original_va'],json.dumps(record)) for name,record in symbols.items()])
        for rva,entry in functions.items():
            identity=f'DAOrigins.exe:{PIN}:rva-{rva:08x}';attestation=native.get(rva)
            store.db.execute('INSERT INTO catalog VALUES(?,?,?,?,?,?,?)',(rva,identity,'native_attested' if attestation else 'queued',None,json.dumps(entry['signature_hypothesis']),json.dumps(entry),json.dumps(attestation) if attestation else None))
    groups=assign_groups(store,functions,native,pe.OPTIONAL_HEADER.AddressOfEntryPoint,max_group_functions)
    store.pause(True);report={'schema_version':1,'module_sha256':PIN,'inventory_sha256':sha(inventory_raw),'catalogued':len(functions),'native_attested':len(native),'new_generation_identities':len(functions)-len(native),'new_batches':groups,'multirange_identities':sum(len(f['ranges'])!=1 for f in functions.values()),'context_paged_identities':sum(len(f['context_pages'])>1 for f in functions.values()),'all_identities_owned':store.db.execute('SELECT count(*) FROM identities').fetchone()[0],'excluded':0,'signature_status':'unknown unless explicitly recorded as a hypothesis'}
    atomic(root/'preparation.json',report);fcntl.flock(lock,fcntl.LOCK_UN);lock.close();return report


def entry(store,rva):return json.loads(store.db.execute('SELECT details_json FROM catalog WHERE rva=?',(rva,)).fetchone()[0])

def registry(store):return {name:json.loads(value) for name,value in store.db.execute('SELECT name,details_json FROM object_symbols')}

"""Static bytes, not decompiler authority, form immutable candidate packets."""
import hashlib
import json
from pathlib import Path
from collections import deque
from workers.deepseek_packet import encode, sha, atomic
from rapid.store import Store

PACKET_CAP=40000
OUTPUT_ESTIMATE_CAP=20000
FUNCTION_CAP=20

def output_estimate(functions):
    return sum(500+80*len(f['instructions']) for f in functions)

PIN='2346caee611002d4dff6ecef68eb315b63a37004dd98b39c11a9c26c0b45bfb3'

def prepare(root,main,repo,max_groups=0):
    import pefile
    from capstone import Cs,CS_ARCH_X86,CS_MODE_32,CS_OP_IMM
    root=Path(root); main=Path(main); repo=Path(repo); store=Store(root)
    binary=main/'gamedata/bin_ship/DAOrigins.exe'; data=binary.read_bytes()
    if sha(data)!=PIN: raise ValueError('binary_pin_mismatch')
    inventory=json.loads((main/'local/analysis/functions.json').read_text())
    if inventory['module_sha256']!=PIN: raise ValueError('inventory_pin_mismatch')
    existing={f['rva'] for f in json.loads((main/'analysis/functions.json').read_text())['functions']}
    pe=pefile.PE(data=data,fast_load=True); image_base=pe.OPTIONAL_HEADER.ImageBase
    decoder=Cs(CS_ARCH_X86,CS_MODE_32); decoder.detail=True
    original={f['rva']:f for f in inventory['functions']}
    ranges=sorted((r['start_rva'],r['end_rva_inclusive'],f['rva']) for f in original.values() for r in f['body_ranges'])
    overlaps=set(); active=[]
    for start,end,rva in ranges:
        active=[v for v in active if v[1]>=start]
        for _,_,other in active:
            if other!=rva: overlaps.update((other,rva))
        active.append((start,end,rva))
    packets={}; graph={}; rejected=[]
    for rva,f in original.items():
        reason=None; rr=f['body_ranges']
        if rva in existing: reason='registered_identity'
        elif len(rr)!=1: reason='multi_range_delayed'
        elif rva in overlaps: reason='overlapping_inventory_ranges'
        elif rr[0]['start_rva']!=rva: reason='nonentry_range'
        if reason: rejected.append({'rva':rva,'reason':reason}); continue
        start=rr[0]['start_rva']; end=rr[0]['end_rva_inclusive']; size=end-start+1
        section=pe.get_section_by_rva(start)
        if section is None or not section.Characteristics & 0x20000000 or end>=section.VirtualAddress+min(section.Misc_VirtualSize,section.SizeOfRawData):
            rejected.append({'rva':rva,'reason':'nonexecutable_or_unbacked_range'}); continue
        body=pe.get_data(start,size); ins=list(decoder.disasm(body,image_base+start))
        if len(body)!=size or sum(i.size for i in ins)!=size:
            rejected.append({'rva':rva,'reason':'incomplete_decode'}); continue
        calls=[i.operands[0].imm-image_base for i in ins if i.mnemonic=='call' and i.operands and i.operands[0].type==CS_OP_IMM]
        # Traverse large startup nodes even when their packet is delayed.
        graph[rva]=[c for c in calls if c in original]
        if size>1800:
            rejected.append({'rva':rva,'reason':'large_body_delayed','body_bytes':size}); continue
        packets[rva]={'name':f'fn_{rva:08x}','rva':rva,'start_rva':start,'end_rva_inclusive':end,'bytes_sha256':sha(body),'bytes_hex':body.hex(),
            'instructions':[{'address':i.address,'bytes':i.bytes.hex(),'mnemonic':i.mnemonic,'op_str':i.op_str} for i in ins],
            'direct_calls':calls,'hypothesis':f}
    # Startup breadth first, then connected compact groups from the remaining inventory.
    queue=deque([pe.OPTIONAL_HEADER.AddressOfEntryPoint,0x16ad0,0x4e19e0,0xc2480]); seen=set(); order=[]
    while queue:
        rva=queue.popleft()
        if rva in seen: continue
        seen.add(rva)
        if rva in packets: order.append(rva)
        queue.extend(graph.get(rva,[]))
    order.extend(r for r in sorted(packets) if r not in seen)
    header=(repo/'rapid/context.hpp').read_bytes(); interface=(repo/'rapid/INTERFACE.md').read_text()
    base={'schema_version':1,'evidence_kind':'static_hypotheses','module':'DAOrigins.exe','module_sha256':PIN,'image_base':image_base,'abi_sha256':sha(header),
          'abi_header':header.decode(),'abi_interface':interface,
          'instructions_to_author':"Never simplify or approximate unknown SEH, FS/TLS, FP, allocator, exception or atomic semantics into success: call c.unsupported with the precise reason on those paths. Unknown call targets must resolve explicitly or throw; missing semantics are never successful zero returns. Begin every function with c.tick(); every loop must tick on each iteration. Generate algorithmic ordinary C++20 for every listed function. Include rapid/context.hpp. Global void fn_XXXXXXXX(rapid::Context& c). Preserve exact all GPR exits, memory accesses, actual entry stack and RET cleanup. Use guest uint32 addresses, defined unsigned wraparound and exact signed/shift behavior. Preserve any stack-local writes observable in complete memory comparison. Internal flags must be correct even if final flags excluded. Each function and each loop must tick. Known direct calls use c.call_rva(rva, actual continuation VA); unresolved dependencies may use resolver which throws when absent. Tail calls must retain callee returned marker. Never pretend unsupported instructions, FP, exceptions, calls or paths succeeded: c.unsupported with explicit reason, and describe limitations in uncertainties. No assembler, host pointer casts, interpreter, dispatch loop over instruction opcodes, or successful zero stubs. Do not execute the binary. The inventory ranges/signatures are hypotheses. Source is an unvalidated proposal. Include every requested function exactly once. Do not implement extra functions outside the requested set."}
    owned={r[0] for r in store.db.execute('SELECT rva FROM identities')}; available=set(packets)-owned; groups=0
    for index,seed in enumerate(order):
        if seed not in available: continue
        candidates=[seed]+graph.get(seed,[])
        # Neighboring inventory entries provide a bounded related/locality group.
        candidates+=order[index+1:index+45]
        group=[]
        for rva in dict.fromkeys(candidates):
            if rva not in available: continue
            trial={**base,'functions':group+[packets[rva]]}
            if len(encode(trial))>PACKET_CAP or output_estimate(trial['functions'])>OUTPUT_ESTIMATE_CAP:
                if not group: rejected.append({'rva':rva,'reason':'needs_larger_packet_or_output_budget'}); available.remove(rva)
                continue
            group.append(packets[rva])
            if len(group)>=FUNCTION_CAP: break
        if not group: continue
        packet={**base,'functions':group}; raw=encode(packet); ident=sha(raw); folder=root/'batches'/ident
        folder.mkdir(parents=True,exist_ok=True,mode=0o700); atomic(folder/'packet.json',packet)
        if store.add(ident,[f['rva'] for f in group]): groups+=1
        available.difference_update(f['rva'] for f in group)
        if max_groups and groups>=max_groups: break
    atomic(root/'preparation.json',{'module_sha256':PIN,'inventory_sha256':sha((main/'local/analysis/functions.json').read_bytes()),'abi_sha256':sha(header),'eligible_functions':len(packets),'new_groups':groups,'rejected':rejected,'unvalidated':True})
    return {'groups_added':groups,'eligible_functions':len(packets),'rejected':len(rejected),**store.status()}


def shrink_undispatched(root):
    """One-time measured preparation correction; never touches attempted batches."""
    store=Store(root); root=Path(root); changed=0; delayed=0
    for batch,created in store.db.execute("SELECT id,created FROM batches WHERE state='pending' AND request_id IS NULL ORDER BY created").fetchall():
        parent=json.loads((root/'batches'/batch/'packet.json').read_text())
        base={k:v for k,v in parent.items() if k!='functions'}
        base['instructions_to_author']='Never approximate unsupported SEH/FS/TLS/FP/exception/allocator or unknown instruction semantics into success: immediately c.unsupported with a precise reason on affected paths. Unknown calls must resolve or throw. Begin EVERY function with c.tick(), tick every loop iteration. '+base['instructions_to_author']
        chunks=[]; current=[]
        for function in parent['functions']:
            trial=current+[function]
            if current and (len(encode({**base,'functions':trial}))>PACKET_CAP or output_estimate(trial)>OUTPUT_ESTIMATE_CAP or len(trial)>FUNCTION_CAP):
                chunks.append(current); current=[]
            current.append(function)
        if current: chunks.append(current)
        children=[]
        for index,functions in enumerate(chunks):
            packet={**base,'functions':functions}; raw=encode(packet); ident=sha(raw)
            folder=root/'batches'/ident; folder.mkdir(parents=True,exist_ok=True,mode=0o700); atomic(folder/'packet.json',packet)
            large=len(raw)>PACKET_CAP or output_estimate(functions)>OUTPUT_ESTIMATE_CAP
            state='needs_larger_budget' if large else 'pending'; delayed+=int(large)
            children.append((ident,state,[f['rva'] for f in functions],created+index*0.000001))
        with store.db:
            # The runtime is stopped and its owner lock is held by the caller.
            row=store.db.execute('SELECT state,request_id FROM batches WHERE id=?',(batch,)).fetchone()
            if row!=('pending',None): raise RuntimeError('attempted_batch_repartition_refused')
            for ident,state,rvas,when in children:
                store.db.execute('INSERT INTO batches(id,state,functions,created,error) VALUES(?,?,?,?,?)',(ident,state,json.dumps(rvas),when,'single_function_output_or_input_budget' if state!='pending' else None))
                for rva in rvas: store.db.execute('UPDATE identities SET batch=? WHERE rva=? AND batch=?',(ident,rva,batch))
            store.db.execute("UPDATE batches SET state='superseded_undispatched',error='measured_pilot_output_cap' WHERE id=?",(batch,))
        changed+=1
    atomic(root/'repacket-preparation.json',{'original_pending_batches':changed,'delayed_single_function_batches':delayed,'input_packet_cap':PACKET_CAP,'output_token_estimate_cap':OUTPUT_ESTIMATE_CAP,'estimate':'500/function + 80/instruction; heuristic only','preserved_attempted_batches':True})
    return store.status()

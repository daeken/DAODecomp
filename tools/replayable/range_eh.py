"""Nonaccepting original-rooted VC8 EBP EH inspection. No compiler/source contract.

Exception entries and return-value continuation candidates stay separate from
inventory ownership. Bounded reachable decoding is an observation, not a claim
that arbitrary runtime targets or unwind semantics have been implemented.
"""
import struct
import capstone
from capstone.x86 import X86_OP_IMM
from rapid_object.eh_graph import handler_shape, node


def need(ok, why):
    if not ok: raise ValueError(why)


def metadata(reader, first):
    # Fixed rooted frame *form*, no module addresses/descriptor values embedded.
    need(len(first)>=16 and first[:6]==bytes.fromhex('558bec6aff68') and first[10:16]==bytes.fromhex('64a100000000'),'EBP_EH_registration_prefix_required')
    handler=struct.unpack_from('<I',first,6)[0]
    hb=reader.read(handler,27,True);hp=handler_shape(hb)
    need(hp['cookie_checked'],'EBP_EH_cookie_handler_required')
    descriptor=struct.unpack_from('<I',hb,hp['descriptor_field'])[0]
    runtime=handler+hp['runtime_field']+4+struct.unpack_from('<i',hb,hp['runtime_field'])[0]
    cookie_check=handler+hp['cookie_field']+4+struct.unpack_from('<i',hb,hp['cookie_field'])[0]
    reader.read(runtime,1,True);reader.read(cookie_check,1,True)
    db=reader.read(descriptor,36);words=struct.unpack('<9I',db)
    magic,states,uv,tries,tv,ips,ipva,estype,flags=words
    need(magic==0x19930522 and 1<=states<=32 and 1<=tries<=16 and ips==ipva==estype==0 and flags==1,'EBP_EH_FuncInfo_domain')
    need(descriptor%4==uv%4==tv%4==0,'unaligned_EBP_EH_metadata')
    regions=[(handler,handler+27),(descriptor,descriptor+36),(uv,uv+8*states),(tv,tv+20*tries)]
    for i,(lo,hi) in enumerate(regions):
        need(not any(lo<end and begin<hi for begin,end in regions[:i]),'overlapping_EBP_EH_nodes')
    def claim(va,size):
        need(not any(va<hi and lo<va+size for lo,hi in regions),'overlapping_EBP_EH_nodes');regions.append((va,va+size))
    ub=reader.read(uv,states*8);unwind=[]
    for i in range(states):
        parent,action=struct.unpack_from('<iI',ub,i*8)
        need(-1<=parent<i,'cyclic_or_invalid_unwind_state')
        need(action==0,'nonzero_unwind_action_not_inspected')
        unwind.append(dict(state=i,to_state=parent,action_va=action))
    tb=reader.read(tv,tries*20);tryrows=[]
    for i in range(tries):
        low,high,catchhigh,count,hv=struct.unpack_from('<5I',tb,i*20)
        need(low<=high<catchhigh<states and 1<=count<=8 and hv%4==0,'invalid_try_state_or_handler_extent')
        claim(hv,count*16);handlers=reader.read(hv,count*16);entries=[]
        for j in range(count):
            adjectives,typeva,displacement,entry=struct.unpack_from('<4I',handlers,j*16)
            need(adjectives==0x40 and typeva==0 and displacement==0,'typed_or_bound_catch_not_inspected')
            reader.read(entry,1,True);entries.append(dict(entry_va=entry,adjectives=adjectives,type_va=typeva,catch_object_displacement=displacement))
        tryrows.append(dict(try_low=low,try_high=high,catch_high=catchhigh,handlers=node(handlers,va=hv,entries=entries)))
    # Intersecting try regions must nest, never cross. Catch ownership is still
    # a runtime/source recovery obligation, not a normal branch into the parent.
    for i,a in enumerate(tryrows):
        for b in tryrows[:i]:
            al,ah=a['try_low'],a['try_high'];bl,bh=b['try_low'],b['try_high']
            need(ah<bl or bh<al or al<=bl<=bh<=ah or bl<=al<=ah<=bh,'crossing_try_regions')
    return dict(handler=node(hb,va=handler,profile=hp,runtime_target_va=runtime,cookie_check_target_va=cookie_check),FuncInfo=node(db,va=descriptor,states=states,try_blocks=tries,flags=flags),unwind_map=node(ub,va=uv,transitions=unwind),try_map=node(tb,va=tv,entries=tryrows),source_recovery_supported=False,exception_semantics_proven=False)


def reachable(reader,entry,owned,max_instructions=128,max_distance=4096):
    """Exact reachable instruction graph, ending at returns/traps/owned edges.

    No opaque linear bound or padding scan. Calls retain unknown effects and
    normal continuation; INT3 remains a trap, not proof the call is noreturn.
    """
    md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);md.detail=True
    pending=[entry];rows={};edges=[];continuations=set()
    def owner(va):return any(lo<=va<hi for lo,hi in owned)
    while pending:
        pc=pending.pop()
        if pc in rows:continue
        need(not owner(pc),'exception_entry_overlaps_parent_owned_range')
        need(len(rows)<max_instructions and abs(pc-entry)<=max_distance,'exception_graph_budget')
        # Exact reads avoid crossing section boundaries merely to fetch 15bytes.
        raw=b'';ins=None
        for length in range(1,16):
            raw=reader.read(pc,length,True);decoded=list(md.disasm(raw,pc,count=1))
            if decoded:ins=decoded[0];break
        need(ins is not None and ins.size==len(raw),'exception_dependency_decode')
        need(not any(lo<pc+ins.size and pc<hi for lo,hi in owned),'exception_instruction_overlaps_owned_range')
        need(not any(a<pc+ins.size and pc<a+r['length'] for a,r in rows.items()),'exception_instruction_overlap')
        rows[pc]=dict(pc=pc,length=ins.size,raw_hex=raw.hex(),mnemonic=ins.mnemonic,operands=ins.op_str)
        def edge(kind,target):
            if target is None:scope='unknown'
            elif owner(target):scope='parent_owned'
            else:scope='exception_dependency';pending.append(target)
            edges.append(dict(pc=pc,kind=kind,target=target,scope=scope))
        if ins.group(capstone.CS_GRP_RET):
            edge('return_runtime_continuation_unknown',None)
            # Literal EAX return convention is a candidate dependency root only.
            predecessors=[r for a,r in rows.items() if a+r['length']==pc]
            if len(predecessors)==1:
                prev=predecessors[0];d=list(md.disasm(bytes.fromhex(prev['raw_hex']),prev['pc']))[0]
                if d.mnemonic=='mov' and len(d.operands)==2 and d.reg_name(d.operands[0].reg)=='eax' and d.operands[1].type==X86_OP_IMM:continuations.add(d.operands[1].imm)
        elif ins.mnemonic in ('int3','ud2'):edge('architectural_trap',None)
        elif ins.group(capstone.CS_GRP_JUMP):
            need(len(ins.operands)==1 and ins.operands[0].type==X86_OP_IMM,'indirect_exception_dependency_edge')
            edge('jump',ins.operands[0].imm)
            if ins.mnemonic!='jmp':edge('fallthrough',pc+ins.size)
        else:
            if ins.group(capstone.CS_GRP_CALL):
                target=ins.operands[0].imm if len(ins.operands)==1 and ins.operands[0].type==X86_OP_IMM else None
                edges.append(dict(pc=pc,kind='call_effects_throw_termination_unknown',target=target,scope='external_unknown'))
            edge('fallthrough',pc+ins.size)
    return dict(entry_va=entry,instructions=[rows[k]for k in sorted(rows)],edges=edges,continuation_candidates=sorted(continuations),complete_under_decode_budget=True,semantics_proven=False)


def inspect(request,caller,lift_dependency):
    from rapid_object.eh_graph import Original
    from pathlib import Path
    original=Path(request['project']['original']).read_bytes();reader=Original(original)
    ranges=caller['lift']['ranges'];owned=[(r['start_va'],r['end_va_exclusive'])for r in ranges]
    first=bytes.fromhex(''.join(r['raw_hex']for r in ranges[0]['lift']['instructions']))
    graph=metadata(reader,first)
    need(not any(lo<node['va']+node['size'] and node['va']<hi for lo,hi in owned for node in (graph['handler'],graph['FuncInfo'],graph['unwind_map'],graph['try_map'])),'EH_metadata_or_handler_overlaps_parent')
    # Bind real PE LoadConfig cookie/SAFESEH, same obligations as existing EH path.
    po=struct.unpack_from('<I',original,0x3c)[0];opt=po+24
    lr,ls=struct.unpack_from('<II',original,opt+96+10*8);need(lr and ls>=64,'EH_missing_PE_load_config')
    load=reader.read(reader.pe.image_base+lr,72);need(struct.unpack_from('<I',load)[0]>=72,'EH_missing_complete_declared_load_config')
    cookie,table,count=struct.unpack_from('<III',load,60);need(0<count<=65536,'EH_safe_handler_table_budget');handlers=reader.read(table,count*4)
    need(graph['handler']['va']-reader.pe.image_base in struct.unpack('<'+'I'*count,handlers),'EH_handler_not_SAFESEH_registered')
    handler=graph['handler'];hr=handler['va']-reader.pe.image_base
    handler_lift=lift_dependency(dict(request,rva=hr,entry=dict(rva=hr,body_bytes=handler['size'],body_ranges=[dict(start_rva=hr,end_rva_inclusive=hr+handler['size']-1)])))
    dependencies=[];candidates=set()
    for row in graph['try_map']['entries']:
        for h in row['handlers']['entries']:
            g=reachable(reader,h['entry_va'],owned);dependencies.append(dict(role='catch_entry',graph=g));candidates.update(g['continuation_candidates'])
    for entry in sorted(candidates):
        if not any(lo<=entry<hi for lo,hi in owned):dependencies.append(dict(role='literal_return_continuation_candidate',graph=reachable(reader,entry,owned)))
    for dep in dependencies:
        dep['typed_instructions']=[]
        # Group only genuinely adjacent graph rows, never decode absent gaps.
        groups=[]
        for row in dep['graph']['instructions']:
            if groups and groups[-1][-1]['pc']+groups[-1][-1]['length']==row['pc']:groups[-1].append(row)
            else:groups.append([row])
        for group in groups:
            lo=group[0]['pc']-reader.pe.image_base;size=sum(r['length']for r in group)
            derived=lift_dependency(dict(request,rva=lo,entry=dict(rva=lo,body_bytes=size,body_ranges=[dict(start_rva=lo,end_rva_inclusive=lo+size-1)])))
            dep['typed_instructions'].append(derived)
    import hashlib
    return dict(schema='original_EBP_try_graph_inspection_v1',caller_slice_sha256=caller['binary_slice_sha256'],graph=graph,handler_lift=handler_lift,dependencies=dependencies,typed_lift_errors=handler_lift['lift']['lift_errors']+sum(g['lift']['lift_errors']for d in dependencies for g in d['typed_instructions']),typed_opaque_instructions=handler_lift['lift']['opaque_instructions']+sum(g['lift']['opaque_instructions']for d in dependencies for g in d['typed_instructions']),security_cookie_va=cookie,safe_handler_table_sha256=hashlib.sha256(handlers).hexdigest(),source_recovery_supported=False,proof=False,blocker='EBP parent-frame/state/catch-continuation source recovery and complete candidate multi-try EH graph comparison unsupported; inspection is not acceptance')

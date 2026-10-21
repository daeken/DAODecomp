"""Complete, nonaccepting COFF graph inspection for the bounded EBP catch profile.

References select every metadata/catch/continuation node. Generated names only
check parent consistency. All bytes in the parent's COMDAT and metadata section
must be owned exactly once; no padding, trap, or exception edge is discarded.
Runtime continuation semantics and external runtime identities remain unknown.
"""
import re,struct
import capstone
from capstone.x86 import X86_OP_IMM
from rapid_object.coff import Coff
from rapid_object.eh_graph import handler_shape,node
from tools.replayable.range_eh import need

GENERATED=re.compile(r'^__(ehhandler|ehfuncinfo|unwindtable|tryblocktable|catchsym|catch)\$(.+)$')


def inspect(object_bytes,main_name):
    obj=Coff(object_bytes)
    mains=[s for s in obj.symbols.values() if s.name==main_name and s.section>0]
    need(len(mains)==1,'candidate_main_nonunique_or_missing');main=mains[0]
    need(main.value==0 and main.type&0x30==0x20 and main.storage==2,'candidate_main_not_COMDAT_root')
    used=set();regions=[];symbol_nodes={}
    def section(sym,code):
        need(sym.section>0 and sym.storage in (2,3),'candidate_node_not_defined')
        s=obj.sections[sym.section-1]
        need(bool(s.characteristics&0x20000000)==code,'candidate_node_section_kind')
        return s
    def parent(sym,kind):
        match=GENERATED.fullmatch(sym.name);need(match is not None,'candidate_generated_name_required')
        k,p=match.groups()
        if k in ('catchsym','catch'):
            p,sep,ordinal=p.rpartition('$');need(sep and ordinal.isdigit(),'candidate_generated_ordinal')
        need(k==kind and p==main.name,'candidate_generated_parent_conflict');used.add(sym.index)
    def claim(sym,size,code=False):
        sec=section(sym,code);lo=sym.value;hi=lo+size
        need(size>0 and 0<=lo<hi<=len(sec.data),'candidate_node_extent')
        need(not any(n==sym.section and lo<b and a<hi for n,a,b in regions),'candidate_node_overlap')
        regions.append((sym.section,lo,hi));symbol_nodes[sym.name]=(sym.section,lo)
        return sec.data[lo:hi]
    def refs(sym,size,expected):
        sec=section(sym,False if sym.type==0 else True)
        rs=[r for r in sec.relocations if sym.value<=r.offset<sym.value+size]
        need(len(rs)==len(expected) and sorted((r.offset-sym.value,r.kind)for r in rs)==sorted(expected),'candidate_metadata_relocations')
        out={}
        for r in rs:
            need(r.offset+4<=sym.value+size and struct.unpack_from('<I',sec.data,r.offset)[0]==0,'candidate_reference_addend_or_extent')
            need(r.symbol in obj.symbols,'candidate_missing_relocation_symbol');out[r.offset-sym.value]=obj.symbols[r.symbol]
        return out
    sec=section(main,True)
    # The main's dedicated code section includes interleaved catch/continuation
    # fragments. function_span(main) alone would truncate at the first catch.
    need(sec.characteristics&0x1000,'candidate_main_requires_COMDAT')
    need(not any(s.index!=main.index and s.section==main.section and s.storage==2 and s.type&0x30==0x20 for s in obj.symbols.values()),'candidate_shared_main_code_section')
    raw=sec.data;need(len(raw)<=16384,"candidate_code_section_budget")
    need(len(raw)>=16 and raw[:6]==bytes.fromhex('558bec6aff68') and raw[10:16]==bytes.fromhex('64a100000000'),'candidate_EBP_registration_prefix')
    roots=[r for r in sec.relocations if r.offset==6 and r.kind==6]
    need(len(roots)==1 and struct.unpack_from('<I',raw,6)[0]==0,'candidate_handler_root_relocation')
    handler=obj.symbols[roots[0].symbol];parent(handler,'ehhandler');hb=claim(handler,27,True);hp=handler_shape(hb)
    need(hp['cookie_checked'],'candidate_cookie_handler_required');hr=refs(handler,27,[(13,0x14),(18,6),(23,0x14)])
    for at in (13,23):
        s=hr[at];need(s.section==0 and s.value==0 and s.storage==2,'candidate_runtime_not_external')
    descriptor=hr[18];parent(descriptor,'ehfuncinfo');db=claim(descriptor,36);words=struct.unpack('<9I',db)
    magic,states,uv,tries,tv,ips,ipva,estype,flags=words
    need(magic==0x19930522 and 1<=states<=32 and 1<=tries<=16 and uv==tv==ips==ipva==estype==0 and flags==1,'candidate_FuncInfo_domain')
    dr=refs(descriptor,36,[(8,6),(16,6)]);unwind,trytable=dr[8],dr[16];parent(unwind,'unwindtable');parent(trytable,'tryblocktable')
    ub=claim(unwind,states*8);refs(unwind,states*8,[]);transitions=[]
    for i in range(states):
        to,action=struct.unpack_from('<iI',ub,8*i);need(-1<=to<i and action==0,'candidate_unwind_domain');transitions.append(dict(state=i,to_state=to,action_va=0))
    tb=claim(trytable,tries*20);tr=refs(trytable,tries*20,[(20*i+16,6)for i in range(tries)]);tryrows=[];catchroots=[]
    for i in range(tries):
        low,high,catchhigh,count,hv=struct.unpack_from('<5I',tb,20*i)
        need(low<=high<catchhigh<states and 1<=count<=8 and hv==0,'candidate_try_domain')
        handlers=tr[20*i+16];parent(handlers,'catchsym');ab=claim(handlers,count*16);ar=refs(handlers,count*16,[(16*j+12,6)for j in range(count)]);entries=[]
        for j in range(count):
            a,t,d,entry=struct.unpack_from('<4I',ab,16*j);need((a,t,d,entry)==(0x40,0,0,0),'candidate_typed_catch_unsupported')
            catch=ar[16*j+12];parent(catch,'catch');need(catch.section==main.section and catch.type&0x30==0x20,'candidate_catch_code_section');catchroots.append(catch);entries.append(dict(symbol=catch.name,offset=catch.value))
        tryrows.append(dict(try_low=low,try_high=high,catch_high=catchhigh,handlers=node(ab,symbol=handlers.name,section=handlers.section,offset=handlers.value,entries=entries)))
    for i,a in enumerate(tryrows):
        for b in tryrows[:i]:
            al,ah=a['try_low'],a['try_high'];bl,bh=b['try_low'],b['try_high'];need(ah<bl or bh<al or al<=bl<=bh<=ah or bl<=al<=ah<=bh,'candidate_crossing_try_regions')
    # Decode the actual CFG in section offsets. Relocations, not an immediate
    # zero or a parent name, establish literal return-continuation identity.
    md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);md.detail=True
    owned={};instruction_starts=set();dependencies=[];relocation_owners=set()
    def graph(entry,role,stop_owned=False):
        pending=[entry];rows={};edges=[];continuations=set()
        while pending:
            pc=pending.pop()
            if pc in rows:continue
            if stop_owned and pc in owned:
                need(owned[pc]=='main' and pc in instruction_starts,'candidate_continuation_enters_nonparent_or_instruction');continue
            need(0<=pc<len(raw) and len(rows)<128 and pc not in owned,'candidate_code_overlap_or_budget')
            xs=list(md.disasm(raw[pc:pc+15],pc,count=1));need(len(xs)==1,'candidate_code_decode');ins=xs[0];hi=pc+ins.size
            need(not any(pc<a+r['length'] and a<hi for a,r in rows.items()) and not any(a in owned for a in range(pc,hi)),'candidate_instruction_overlap')
            rs=[r for r in sec.relocations if pc<=r.offset<hi]
            need(len(rs)<=1,'candidate_instruction_relocation_count');rel=[]
            for r in rs:
                need(r.offset+4<=hi and r.kind in (6,0x14) and struct.unpack_from('<I',raw,r.offset)[0]==0,'candidate_code_relocation_domain');sym=obj.symbols[r.symbol];rel.append(dict(offset=r.offset-pc,kind=r.kind,symbol=sym.name,section=sym.section,target_offset=sym.value));relocation_owners.add(r.offset)
            rows[pc]=dict(pc=pc,length=ins.size,raw_hex=bytes(ins.bytes).hex(),mnemonic=ins.mnemonic,operands=ins.op_str,relocations=rel)
            def edge(kind,target):
                if target in owned:need(target in instruction_starts,'candidate_edge_into_parent_instruction')
                scope='unknown' if target is None else 'parent_owned' if target in owned and owned[target]=='main' else 'same_graph'
                edges.append(dict(pc=pc,kind=kind,target=target,scope=scope))
                if target is not None and scope!='parent_owned':pending.append(target)
            if ins.group(capstone.CS_GRP_RET):
                edge('return_runtime_continuation_unknown' if role!='main' else 'return',None)
                for prev in rows.values():
                    if prev['pc']+prev['length']!=pc:continue
                    prs=prev['relocations']
                    if prev['mnemonic']=='mov' and prev['operands'].startswith('eax, ') and len(prs)==1 and prs[0]['kind']==6:
                        ref=prs[0];need(ref['section']==main.section,'candidate_continuation_not_parent_code');continuations.add(ref['target_offset'])
            elif ins.mnemonic in ('int3','ud2'):edge('architectural_trap_unknown',None)
            elif ins.group(capstone.CS_GRP_JUMP):
                need(not rs and len(ins.operands)==1 and ins.operands[0].type==X86_OP_IMM,'candidate_indirect_or_relocated_jump');edge('jump',ins.operands[0].imm)
                if ins.mnemonic!='jmp':edge('fallthrough',hi)
            else:
                if ins.group(capstone.CS_GRP_CALL):
                    need(len(rs)==1 and rs[0].kind==0x14 and len(ins.operands)==1 and ins.operands[0].type==X86_OP_IMM,'candidate_unknown_call_reference');edges.append(dict(pc=pc,kind='call_effects_throw_termination_unknown',symbol=rel[0]['symbol'],scope='external_unknown'))
                edge('fallthrough',hi)
        for pc,row in rows.items():
            instruction_starts.add(pc)
            for at in range(pc,pc+row['length']):need(at not in owned,'candidate_graph_overlap');owned[at]=role
        return dict(role=role,entry_offset=entry,instructions=[rows[k]for k in sorted(rows)],edges=edges,continuation_candidates=sorted(continuations),semantics_proven=False)
    main_graph=graph(0,'main');continuations=set()
    need(len({s.value for s in catchroots})==len(catchroots),'candidate_shared_catch_entry_unsupported')
    for c in catchroots:
        g=graph(c.value,'catch_entry');g['symbol']=c.name;dependencies.append(g);continuations.update(g['continuation_candidates'])
    for entry in sorted(continuations):
        if entry in owned:need(owned[entry]=='main' and entry in instruction_starts,'candidate_continuation_into_catch_or_instruction')
        else:dependencies.append(graph(entry,'literal_return_continuation_candidate',True))
    need(set(owned)==set(range(len(raw))),'candidate_unowned_main_section_bytes')
    need(relocation_owners=={r.offset for r in sec.relocations},'candidate_unowned_code_relocation')
    expected={s.index for s in obj.symbols.values() if (m:=GENERATED.fullmatch(s.name)) and (m[2]==main.name or m[2].startswith(main.name+'$'))}
    need(expected==used,'candidate_unrooted_generated_node')
    # Complete metadata/handler sections, no extra bytes or unrelated declarations.
    for n in {r[0]for r in regions}:
        spans=sorted((a,b)for section,a,b in regions if section==n);at=0
        for lo,hi in spans:need(lo==at,'candidate_unowned_metadata_or_handler_bytes');at=hi
        need(at==len(obj.sections[n-1].data),'candidate_unowned_metadata_or_handler_bytes')
    return dict(schema='candidate_EBP_try_graph_v1',diagnostic_only=True,acceptance_supported=False,proof=False,main=main_graph,handler=node(hb,symbol=handler.name,section=handler.section,offset=handler.value,profile=hp,runtime_symbol=hr[23].name,cookie_check_symbol=hr[13].name),FuncInfo=node(db,symbol=descriptor.name,section=descriptor.section,offset=descriptor.value,states=states,try_blocks=tries,flags=flags),unwind_map=node(ub,symbol=unwind.name,section=unwind.section,offset=unwind.value,transitions=transitions),try_map=node(tb,symbol=trytable.name,section=trytable.section,offset=trytable.value,entries=tryrows),dependencies=dependencies,complete_code_bytes=len(raw),complete_metadata_and_handler_bytes=sum(b-a for _,a,b in regions),blockers=['runtime identities not established by external names','catch return continuation convention not proved','parent frame correspondence not proved','architectural traps and unknown exception effects retained'])

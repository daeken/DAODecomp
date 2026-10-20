"""Complete bounded graph byte diagnostics. Never returns acceptance placements.

Each byte is equal, different, absent, or explicitly unresolved. No byte is
masked. Edge-derived coordinates are conditional diagnostics; missing original
inventory/runtime identities remain blockers even when resolved bytes agree.
"""
import struct
from rapid_object import eh_graph as g
from rapid_object.coff import Coff,CoffError
from rapid_object.symbol_identity import source_identity,generated_identity


def compare_node(original,candidate,relocations,base,resolve):
    """Compare every byte. Unknown relocation fields remain four explicit rows."""
    raw=bytes(candidate);patched=bytearray(raw);unknown={};fields=[];occupied=set()
    for rel in relocations:
        off,kind,name=rel['offset'],rel['kind'],rel['symbol']
        if kind not in (6,0x14) or type(off)!=int or off<0 or off+4>len(raw):raise g.Unsupported('unsupported_or_crossing_relocation')
        if occupied.intersection(range(off,off+4)):raise g.Unsupported('overlapping_relocation_fields')
        occupied.update(range(off,off+4));index=rel.get('symbol_index');target,reason=resolve(name,index)
        addend=struct.unpack_from('<I',raw,off)[0]
        field=dict(offset=off,kind=kind,symbol=name,symbol_index=index,raw_addend_u32=addend)
        if target is None:
            field.update(state='unresolved',reason=reason)
            for k in range(off,off+4):unknown[k]=reason
        else:
            value=(target+addend-(base+off+4 if kind==0x14 else 0))&0xffffffff
            struct.pack_into('<I',patched,off,value);field.update(state='edge_or_source_resolved_diagnostic_only',value_u32=value,basis=reason)
        fields.append(field)
    rows=[]
    for i in range(max(len(original),len(raw))):
        a=original[i] if i<len(original) else None;b=patched[i] if i<len(patched) else None
        state='unresolved_relocation' if i in unknown else 'missing_original_byte' if a is None else 'missing_candidate_byte' if b is None else 'equal' if a==b else 'different'
        rows.append(dict(offset=i,original=a,candidate_raw=raw[i] if i<len(raw) else None,candidate_resolved=b,state=state,unresolved_reason=unknown.get(i)))
    return dict(original_size=len(original),candidate_size=len(raw),relocations=fields,bytes=rows,counts={s:sum(r['state']==s for r in rows) for s in sorted({r['state'] for r in rows})})


def compare_graphs(original,object_bytes,requested,symbols=None,*,module_sha256):
    report=dict(diagnostic_only=True,acceptance_supported=False,proof=False,module_sha256=g.sha(original),object_sha256=g.sha(object_bytes),functions=[])
    observations=g.diagnose(original,object_bytes,requested,symbols,module_sha256=module_sha256)
    report['discarded_generated_address_claims']=observations.get('discarded_generated_address_claims',{})
    if observations.get('error'):return dict(report,error=observations['error'],state='incomplete')
    reader=g.Original(original);obj=Coff(object_bytes);safe=symbols or {}
    for observed in observations['functions']:
        row=dict(rva=observed['rva'],nodes={},blockers=list(observed['blockers']),upstream_differences=list(observed['differences']),state='incomplete');report['functions'].append(row)
        try:
            if 'original' not in observed or 'candidate' not in observed:raise g.Unsupported('incomplete_graph:'+','.join(observed['blockers']))
            a,b=observed['original'],observed['candidate'];spec=next(v for k,v in g.normalize_requested(requested,reader.pe.image_base).items() if k==row['rva'])
            main=next(s for s in obj.symbols.values() if s.name==spec['symbol']);sec,lo,n,evidence=obj.function_span(main);mainraw=sec.data[lo:lo+n]
            originalmain=reader.read(spec['original_va'],spec['ranges'][0]['end_rva_inclusive']-spec['ranges'][0]['start_rva']+1,True)
            pairs={'main':(dict(va=spec['original_va'],bytes_hex=originalmain.hex()),dict(symbol=main.name,symbol_index=main.index,section=main.section,offset=lo,size=n,bytes_hex=mainraw.hex()))}
            for name in ('handler','FuncInfo','unwind_map','action'):
                cand=dict(b[name]);matches=[s for s in obj.symbols.values() if s.name==cand['symbol'] and s.section==cand['section'] and s.value==cand['offset']]
                if len(matches)!=1:raise g.Unsupported('ambiguous_generated_node_symbol_identity')
                cand['symbol_index']=matches[0].index;pairs[name]=(a[name],cand)
            dependencies=b['defined_action_dependencies']
            if len(dependencies)!=1:raise g.Unsupported('missing_or_extra_delete_helper')
            helper=dict(dependencies[0]);action=b['action'];action_rels=[r for r in obj.sections[action['section']-1].relocations if r.offset==action['offset']+action['profile']['target_field']]
            if len(action_rels)!=1:raise g.Unsupported('ambiguous_action_helper_reference')
            helper_sym=obj.symbols[action_rels[0].symbol]
            if (helper_sym.name,helper_sym.section,helper_sym.value)!=(helper['symbol'],helper['section'],helper['offset']):raise g.Unsupported('helper_coordinate_identity_conflict')
            helper['symbol_index']=helper_sym.index;hva=a['action']['external_target_va'];hb=reader.read(hva,5,True)
            if helper['size']!=5 or hb[0]!=0xe9 or bytes.fromhex(helper['bytes_hex'])[0]!=0xe9:raise g.Unsupported('unsupported_complete_delete_helper_boundary')
            pairs['delete_helper']=(dict(va=hva,bytes_hex=hb.hex()),helper)
            row['blockers'].append('delete_helper_original_inventory_boundary_unverified')
            placements={}
            original_spans=[];candidate_spans=[]
            for key,(orig,cand) in pairs.items():
                if cand['symbol_index'] in placements:raise g.Unsupported('ambiguous_candidate_node_correspondence')
                size=len(bytes.fromhex(cand['bytes_hex']));olen=len(bytes.fromhex(orig['bytes_hex']))
                if any(orig['va']<hi and lo<orig['va']+olen for lo,hi in original_spans):raise g.Unsupported('overlapping_original_complete_nodes')
                if any(sec==cand['section'] and cand['offset']<hi and lo<cand['offset']+size for sec,lo,hi in candidate_spans):raise g.Unsupported('overlapping_candidate_complete_nodes')
                original_spans.append((orig['va'],orig['va']+olen));candidate_spans.append((cand['section'],cand['offset'],cand['offset']+size))
                placements[cand['symbol_index']]=orig['va']
            def resolve(name,index):
                sym=obj.symbols.get(index)
                if sym is None or sym.name!=name:return None,'missing_or_conflicting_COFF_symbol_index'
                if index in placements:return placements[index],'actual_graph_edge_and_symbol_index_correspondence; original_inventory_boundary_unverified'
                if sym.section!=0 or sym.value or sym.storage!=2:return None,'unsupported_or_uncompared_defined_dependency:'+name+':index='+str(index)
                identity=source_identity(name)
                if identity is not None:
                    address=reader.pe.image_base+identity[1]
                    if name in safe and type(safe[name]) is int and safe[name]==address:return address,'existing_RVA_source_binding'
                    return None,'missing_or_conflicting_RVA_source_binding:'+name
                return None,'runtime_or_other_external_identity_unverified:'+name
            covered=set()
            for key,(orig,cand) in pairs.items():
                section=obj.sections[cand['section']-1];start=cand['offset'];size=len(bytes.fromhex(cand['bytes_hex']));rels=[]
                for r in section.relocations:
                    if r.offset<start+size and start<r.offset+4 and not (start<=r.offset and r.offset+4<=start+size):raise g.Unsupported('relocation_crosses_complete_node')
                    if start<=r.offset<start+size:
                        rels.append(dict(offset=r.offset-start,kind=r.kind,symbol=obj.symbols[r.symbol].name,symbol_index=r.symbol));covered.add((section.number,r.offset))
                result=compare_node(bytes.fromhex(orig['bytes_hex']),bytes.fromhex(cand['bytes_hex']),rels,orig['va'],resolve)
                result.update(original_va=orig['va'],candidate_symbol=cand['symbol'],correspondence_basis='actual root/reference edges; conditional original boundaries')
                row['nodes'][key]=result
            row['counts']={s:sum(n['counts'].get(s,0) for n in row['nodes'].values()) for s in sorted({s for n in row['nodes'].values() for s in n['counts']})}
            row['state']='byte_differences_with_unresolved_identity' if row['counts'].get('different') or row['counts'].get('missing_original_byte') or row['counts'].get('missing_candidate_byte') else 'resolved_bytes_agree_identity_unresolved'
            row['graph_dependency_coverage_complete']=not any(f.get('reason','').startswith(('unsupported_or_uncompared_defined_dependency','missing_or_conflicting_COFF_symbol_index')) for n in row['nodes'].values() for f in n['relocations'])
            if not row['graph_dependency_coverage_complete']:row['state']='incomplete'
            row['compared_graph_nodes']=6;row['complete_byte_accounting']=sum(row['counts'].values())==sum(max(n['original_size'],n['candidate_size']) for n in row['nodes'].values())
            row['blockers'].extend(f['reason'] for n in row['nodes'].values() for f in n['relocations'] if f['state']=='unresolved')
        except (CoffError,ValueError,KeyError,TypeError,StopIteration,struct.error) as exc:row['blockers'].append(str(exc))
    return report

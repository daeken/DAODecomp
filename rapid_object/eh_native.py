"""Complete bounded x86 COFF main/EH graph byte comparison.

This does not change the public nonaccepting diagnostic API or old comparator.
Trusted pins describe reusable toolchain/original inputs, never per-function
placements. The only per-function authored input is source C++ with its existing
identity annotation. Metadata/code correspondence follows actual operand edges.
"""
from pathlib import Path
import json,re,struct
import capstone,platform
from rapid_object import eh_graph as g,eh_graph_compare as diagnostic
from rapid_object.coff import Coff,CoffError
from rapid_object.symbol_identity import source_identity,bind_symbols
if __package__:
    from .static_crt_identity import ROOTS,canonical,require,recognize,inventory_entries,decode_fields,mapped_address
else:
    from static_crt_identity import ROOTS,canonical,require,recognize,inventory_entries,decode_fields,mapped_address


def implementation_hashes():
    paths=[Path(__file__),Path(__file__).with_name('static_crt_identity.py'),Path(g.__file__),Path(diagnostic.__file__),Path(g.__file__).with_name('coff.py'),Path(g.__file__).with_name('compare.py'),Path(g.__file__).with_name('symbol_identity.py'),Path(g.__file__).with_name('constructor_identity.py'),Path(__file__).parents[1]/'tools/replayable/ebp_eh_native.py',Path(__file__).parents[1]/'tools/replayable/ebp_eh_compare.py',Path(__file__).parents[1]/'tools/replayable/ebp_eh_candidate.py',Path(__file__).parents[1]/'tools/replayable/range_eh.py',Path(__file__).parents[1]/'tools/replayable/terminal_calls.py']
    return {p.name:g.sha(p.read_bytes()) for p in paths}


def terminal_profile(role,data,base):
    """Complete reachable straight-line profiles: no branch is silently dropped."""
    if role=='handler':
        profile=g.handler_shape(data);expected=['mov','jmp'] if not profile['cookie_checked'] else ['mov','lea','mov','xor','call','mov','jmp']
    elif role=='action':
        profile=g.action_shape(data);expected=['mov','push','call','pop','ret'] if len(data)==11 else ['mov','jmp'] if profile['kind']=='load_receiver_ecx_tail_jump' else ['lea','jmp']
    elif role=='delete_helper':
        require(len(data)==5 and data[0]==0xe9,'unsupported_complete_delete_helper');expected=['jmp'];profile={}
    else:raise g.Unsupported('unknown_terminal_profile')
    ins=decode_fields(data,[]);require([i.mnemonic for i in ins]==expected,'unsupported_reachable_helper_CFG')
    # Pattern checks fix every opcode/width, retaining variable offsets/operands.
    # Calls are external boundaries with fallthrough; the last RET/JMP ends this CFG.
    require(ins[-1].mnemonic in ('ret','jmp') and all(i.mnemonic not in ('ret','jmp') and not i.mnemonic.startswith('j') for i in ins[:-1]),'nonterminal_or_unsupported_CFG')
    return dict(basis='complete_operand_rooted_straight_line_CFG',size=len(data),instructions=[dict(offset=i.address,size=i.size,mnemonic=i.mnemonic) for i in ins],profile=profile)


def inferred_requests(source,obj,entries,reader,*,allow_split=False):
    text=source.decode('utf-8');markers=[int(x,16)-reader.pe.image_base for x in re.findall(r'^\s*//\s*FUNCTION:\s*\S+\s+0x([0-9a-fA-F]+)\s*$',text,re.M)]
    if not markers:
        markers=sorted({identity[1] for sym in obj.symbols.values() if sym.section>0 and (sym.type&0x30)==0x20 and (identity:=source_identity(sym.name)) is not None and identity[0]=='fn' and re.search(r'(?<![A-Za-z0-9_])fn_%08x\b'%identity[1],text)})
    require(markers and len(markers)==len(set(markers)),'missing_or_duplicate_source_identity')
    requested={}
    for rva in markers:
        require(rva in entries,'source_RVA_not_in_inventory');f=entries[rva];ranges=f['body_ranges']
        require(ranges and (len(ranges)==1 or allow_split) and ranges[0]['start_rva']==rva,'unsupported_main_inventory_ranges')
        previous=-1;parts=[]
        for part in ranges:
            lo,hi=part['start_rva'],part['end_rva_inclusive']+1;require(0<=lo<hi and lo>=previous,'invalid_main_inventory_ranges');previous=hi;parts.append(reader.read(reader.pe.image_base+lo,hi-lo,True))
        requested[rva]=dict(ranges=ranges,bytes_sha256=g.sha(b''.join(parts)))
    registry={}
    for sym in obj.symbols.values():
        identity=source_identity(sym.name)
        if identity is None:continue
        kind,rva=identity;address=reader.pe.image_base+rva
        if kind=='fn':require(rva in entries,'source_callee_identity_not_in_inventory')
        else:mapped_address(reader,address)
        registry['%s_%08x'%(kind,rva)]=address
    bindings=bind_symbols(obj.data,requested,registry)
    require(all('symbol' in r for r in requested.values()),'missing_or_ambiguous_defined_main')
    return requested,bindings


def paired_indexes(obj,spec,observed):
    mains=[s for s in obj.symbols.values() if s.name==spec['symbol']];require(len(mains)==1,'ambiguous_main_index');pairs={'main':mains[0].index};c=observed['candidate']
    for name in ('handler','FuncInfo','unwind_map','action'):
        d=c[name];found=[s for s in obj.symbols.values() if (s.name,s.section,s.value)==(d['symbol'],d['section'],d['offset'])]
        require(len(found)==1,'ambiguous_generated_index');pairs[name]=found[0].index
    action=c['action'];sec=obj.sections[action['section']-1];rels=[r for r in sec.relocations if r.offset==action['offset']+action['profile']['target_field']]
    require(len(rels)==1,'ambiguous_helper_reference');pairs['delete_helper']=rels[0].symbol
    require(len(set(pairs.values()))==6,'aliased_graph_nodes');return pairs


def check(original,inventory,compiler,libraries,source,object_bytes,build,pins,*,cached=None):
    report=dict(schema_version=1,backend='i386_coff_eh_graph_v1',ordinary_acceptance_supported=False,proof=False,status='inconclusive',functions=[],blockers=[])
    try:
        hashes=dict(module_sha256=g.sha(original),inventory_sha256=g.sha(inventory),compiler_sha256=g.sha(compiler),libraries_sha256={n:g.sha(b) for n,b in sorted(libraries.items())},source_sha256=g.sha(source),object_sha256=g.sha(object_bytes),build_sha256=g.sha(canonical(build)),policy_sha256=g.sha(canonical(pins)),implementations=implementation_hashes(),capstone_version=capstone.__version__,python_version=platform.python_version())
        report['trusted_input_policy']=json.loads(canonical(pins));report['inputs']=hashes;report['input_key']=g.sha(canonical(hashes));report['cached_verdict_reused']=False
        if cached is not None:require(cached.get('input_key')==report['input_key'],'stale_cached_input_binding')
        for key in ('module_sha256','inventory_sha256','compiler_sha256','libraries_sha256'):require(hashes[key]==pins[key],'pinned_'+key+'_mismatch')
        require(isinstance(pins['toolchain_archive_sha256'],str) and re.fullmatch('[0-9a-f]{64}',pins['toolchain_archive_sha256']) is not None,'missing_toolchain_archive_provenance')
        require(build['module_sha256']==hashes['module_sha256'] and build['source_sha256']==hashes['source_sha256'] and build['object_sha256']==hashes['object_sha256'],'build_input_binding_mismatch')
        require(build['compiler']['sha256']==hashes['compiler_sha256'] and build['flags']==pins['compiler_flags'],'selected_compiler_or_flags_mismatch')
        require(type(build['exit_code']) is int and build['exit_code']==0 and build['linked'] is False and build['original_executed'] is False,'unsupported_build_receipt')
        runtime=recognize(original,inventory,libraries);report['runtime_identity']=runtime
        reader=g.Original(original);obj=Coff(object_bytes);entries=inventory_entries(inventory,g.sha(original),reader);requested,symbols=inferred_requests(source,obj,entries,reader,allow_split=True)
        if any(len(spec['ranges'])>1 for spec in requested.values()):
            from tools.replayable.ebp_eh_native import compare_nonmatch
            report.update(compare_nonmatch(original,inventory,libraries,object_bytes,requested,symbols,runtime))
            return report
        observed=g.diagnose(original,object_bytes,requested,symbols,module_sha256=g.sha(original));graph=diagnostic.compare_graphs(original,object_bytes,requested,symbols,module_sha256=g.sha(original))
        require(not observed.get('error') and not graph.get('error'),'upstream_diagnostic_error:'+str(observed.get('error') or graph.get('error')))
        report['requested']=requested;report['source_bindings']=symbols
        for rva,spec in requested.items():
            row=dict(rva=rva,status='inconclusive',nodes={},blockers=[]);report['functions'].append(row)
            try:
                os=[x for x in observed['functions'] if x['rva']==rva];gs=[x for x in graph['functions'] if x['rva']==rva];require(len(os)==len(gs)==1,'missing_or_ambiguous_graph_result');o,d=os[0],gs[0]
                require('candidate' in o and 'original' in o and len(d['nodes'])==6 and d.get('complete_byte_accounting') is True,'incomplete_supported_graph:'+','.join(o.get('blockers',[])))
                indexes=paired_indexes(obj,spec,o);placements={index:d['nodes'][name]['original_va'] for name,index in indexes.items()}
                def resolve(name,index):
                    sym=obj.symbols.get(index)
                    if sym is None or sym.name!=name:return None,'missing_or_conflicting_COFF_index'
                    if index in placements:return placements[index],'actual_operand_edge_and_COFF_index_correspondence'
                    if sym.section!=0 or sym.value or sym.storage!=2:return None,'unpaired_defined_or_unsupported_dependency'
                    if name in runtime['root_bindings']:
                        expected_type=0 if name==ROOTS[2] else 32
                        if sym.type!=expected_type:return None,'runtime_reference_type_conflict'
                        return runtime['root_bindings'][name],'independent_static_CRT_identity'
                    if source_identity(name) is not None and name in symbols:return symbols[name],'anchored_source_RVA_identity'
                    return None,'unidentified_external_dependency:'+name
                for name,n in d['nodes'].items():
                    a=bytes(x['original'] for x in n['bytes'][:n['original_size']]);b=bytes(x['candidate_raw'] for x in n['bytes'][:n['candidate_size']]);role=dict(original_size=len(a),candidate_size=len(b))
                    if name in ('handler','action','delete_helper'):
                        role['original_span']=terminal_profile(name,a,n['original_va']);role['candidate_span']=terminal_profile(name,b,0)
                    if name=='FuncInfo':g.descriptor_shape(a);g.descriptor_shape(b);role['span_basis']='complete_VC8_FuncInfo9words; maxState1, no try/IP/ESType entries, EHflags1'
                    if name=='unwind_map':require(len(a)==len(b)==8 and struct.unpack_from('<i',a)[0]==struct.unpack_from('<i',b)[0]==-1,'unsupported_complete_unwind_map');role['span_basis']='complete1entry_unwind_map; state0_to_minus1'
                    if name not in ('FuncInfo','unwind_map'):decode_fields(b,n['relocations'])
                    # Original terminal nodes are paired only through observed registration/map/action roots.
                    result=diagnostic.compare_node(a,b,n['relocations'],n['original_va'],resolve);result.update(role,original_va=n['original_va'],candidate_symbol=n['candidate_symbol'],candidate_symbol_index=indexes[name],original_sha256=g.sha(a),candidate_raw_sha256=g.sha(b));row['nodes'][name]=result
                row['counts']={state:sum(n['counts'].get(state,0) for n in row['nodes'].values()) for state in sorted({state for n in row['nodes'].values() for state in n['counts']})}
                row['all_bytes_accounted']=sum(row['counts'].values())==sum(max(n['original_size'],n['candidate_size']) for n in row['nodes'].values())
                require(row['all_bytes_accounted'],'incomplete_byte_accounting')
                if row['counts'].get('unresolved_relocation'):
                    row['blockers'].extend(f['reason'] for n in row['nodes'].values() for f in n['relocations'] if f['state']=='unresolved')
                else:row['status']='exact_eh_graph_match' if set(row['counts'])=={'equal'} else 'eh_graph_nonmatch'
            except (CoffError,KeyError,ValueError,TypeError,StopIteration,struct.error,UnicodeError) as exc:row['blockers'].append(str(exc))
        require(report['functions'],'empty_results')
        statuses={f['status'] for f in report['functions']}
        report['status']='exact_eh_graph_match' if statuses=={'exact_eh_graph_match'} else 'eh_graph_nonmatch' if 'inconclusive' not in statuses else 'inconclusive'
        report['scope']='exact bounded compiled artifact graph; external semantics unmodeled; not whole game proof; publication requires fresh trusted export recheck'
    except (CoffError,KeyError,ValueError,TypeError,StopIteration,struct.error,UnicodeError) as exc:report['blockers'].append(str(exc))
    return report

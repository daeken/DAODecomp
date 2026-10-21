"""Split-range native routes with an immutable nonaccepting node diagnostic.

compare_nonmatch preserves the historical per-node diagnostic/refusal. The
separate compare_complete route can accept only freshly checked full physical
section identity in the unchanged original image/context.
"""
from rapid_object.eh_graph import Original
from tools.replayable.ebp_eh_compare import compare
from tools.replayable.terminal_calls import derive,SYMBOL


def compare_nonmatch(original,inventory,libraries,object_bytes,requested,symbols,runtime):
    reader=Original(original);bindings=dict(runtime['root_bindings']);bindings.update(symbols)
    terminal=derive(original,inventory,libraries);bindings[SYMBOL]=terminal['target']
    rows=[]
    for rva,spec in requested.items():
        ranges=[(reader.pe.image_base+r['start_rva'],reader.pe.image_base+r['end_rva_inclusive']+1)for r in spec['ranges']]
        diagnostic=compare(original,ranges,object_bytes,spec['symbol'],external_bindings=bindings)
        complete=diagnostic.get('state')!='diagnostic_incomplete' and bool(diagnostic.get('nodes'))
        counts=diagnostic.get('counts',{})
        accounted=complete and all(n['equal']+n['different']+n['unresolved']==sum(max(c['original_size'],c['candidate_size'])for c in n['chunks']) if n['chunks'] else n['different']==max(n['original_size'],n['candidate_size']) for n in diagnostic.get('nodes',[]))
        different=accounted and counts.get('different',0)>0
        rows.append(dict(rva=rva,status='eh_graph_nonmatch' if different else 'inconclusive',nodes={n['name']:n for n in diagnostic.get('nodes',[])},counts=counts,all_bytes_accounted=accounted,acceptance_supported=False,blockers=[b for b in diagnostic['blockers'] if b!='runtime identities not established by external names']+(['unresolved_generated_or_external_reference'] if counts.get('unresolved') else [])+['multi_try_acceptance_not_implemented'],diagnostic=diagnostic))
    return dict(functions=rows,requested=requested,source_bindings=symbols,terminal_runtime_identity=terminal,status='eh_graph_nonmatch' if rows and all(r['status']=='eh_graph_nonmatch'for r in rows) else 'inconclusive',acceptance_supported=False,scope='complete split-range main/EH strict compiled-artifact nonmatch; equality cannot pass without supported parent-frame/continuation/trap obligations')


def compare_complete(original,inventory,libraries,object_bytes,requested,symbols,runtime):
    """Keep the legacy diagnostic intact; only complete section identity accepts."""
    from tools.replayable.physical_eh_identity import check
    report=compare_nonmatch(original,inventory,libraries,object_bytes,requested,symbols,runtime)
    bindings={}
    for source in (runtime['root_bindings'],symbols,{SYMBOL:report['terminal_runtime_identity']['target']}):
        for name,target in source.items():
            if name in bindings and bindings[name]!=target:
                report.update(status='inconclusive',acceptance_supported=False)
                report['blockers']=['physical_conflicting_external_bindings']
                return report
            bindings[name]=target
    reader=Original(original)
    for row in report['functions']:
        spec=requested[row['rva']]
        ranges=[(reader.pe.image_base+r['start_rva'],reader.pe.image_base+r['end_rva_inclusive']+1)for r in spec['ranges']]
        result=check(original,ranges,object_bytes,spec['symbol'],bindings)
        row['physical_identity']=result
        row['legacy_diagnostic_blockers']=list(row['blockers'])
        row['blockers']=[b for b in row['blockers']if b!='multi_try_acceptance_not_implemented']
        if result['acceptance_supported']:
            row.update(status='exact_eh_graph_match',acceptance_supported=True,blockers=[],
                       all_bytes_accounted=True,counts={'equal':result['bytes_compared']},
                       nodes={'section_'+str(s['section']):dict(original_size=s['size'],candidate_size=s['size'],original_sha256=s['original_sha256'],candidate_raw_sha256=s['relocated_sha256'])for s in result['sections']})
        else:
            row['blockers']+=result['blockers']
    statuses={r['status']for r in report['functions']}
    report.update(status='exact_eh_graph_match'if statuses=={'exact_eh_graph_match'}else 'eh_graph_nonmatch'if statuses=={'eh_graph_nonmatch'}else 'inconclusive',
                  acceptance_supported=statuses=={'exact_eh_graph_match'},
                  scope='complete physical section identity at derived original placement with unchanged original image/context; no linked replacement or source theorem')
    return report

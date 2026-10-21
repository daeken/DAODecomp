"""Complete split-range strict nonmatch reporting, with no acceptance shortcut.

A concrete native byte/extent difference can establish nonidentity even while
other exception obligations are unresolved. Equality is never accepted here:
parent-frame/continuation and trap-resumption relations still require support.
The independent diagnostic remains nonaccepting, including with bound references.
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

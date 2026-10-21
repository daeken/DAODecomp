"""Independent complete-node diagnostic; never a source-acceptance backend.

Every byte is equal, different, or an explicitly unresolved external reference.
An unresolved runtime/cookie/callee identity cannot become a match by masking its
relocation. Catch/continuation frame semantics also remain explicit obligations.
"""
import struct
from rapid_object.coff import Coff
from rapid_object.eh_graph import Original
from rapid_object.compare import sha
from tools.replayable.range_eh import metadata,reachable,need
from tools.replayable.ebp_eh_candidate import inspect


def compare(original,owned_ranges,object_bytes,main_name):
    result=dict(schema='EBP_try_graph_comparison_diagnostic_v1',diagnostic_only=True,acceptance_supported=False,proof=False,original_sha256=sha(original),object_sha256=sha(object_bytes),nodes=[],blockers=[])
    try:
        reader=Original(original);obj=Coff(object_bytes);candidate=inspect(object_bytes,main_name)
        need(owned_ranges and len(owned_ranges)<=64,'original_owned_range_count')
        need(sum(hi-lo for lo,hi in owned_ranges)<=65536,'original_owned_byte_budget')
        previous=0
        for lo,hi in owned_ranges:
            need(0<=lo<hi<=0x100000000 and lo>=previous,'original_owned_range_order');reader.read(lo,hi-lo,True);previous=hi
        main=reachable(reader,owned_ranges[0][0],[])
        covered={at for row in main['instructions']for at in range(row['pc'],row['pc']+row['length'])}
        need(covered=={at for lo,hi in owned_ranges for at in range(lo,hi)},'original_main_CFG_inventory_disagrees')
        graph=metadata(reader,reader.read(owned_ranges[0][0],16,True));dependencies=[];continuations=set()
        for t in graph['try_map']['entries']:
            for h in t['handlers']['entries']:
                g=reachable(reader,h['entry_va'],owned_ranges);dependencies.append(g);continuations.update(g['continuation_candidates'])
        for entry in sorted(continuations):
            if not any(lo<=entry<hi for lo,hi in owned_ranges):dependencies.append(reachable(reader,entry,owned_ranges))
        need(len(dependencies)==len(candidate['dependencies']),'dependency_graph_count_differs')
        starts={row['pc']for row in main['instructions']};all_code=set(covered)
        for dep in dependencies:
            for edge in dep['edges']:
                if edge['scope']=='parent_owned':need(edge['target'] in starts,'original_dependency_enters_instruction')
            for row in dep['instructions']:
                span=set(range(row['pc'],row['pc']+row['length']));need(not all_code.intersection(span),'original_dependency_overlap');all_code.update(span)
        meta=[graph[k]for k in ('handler','FuncInfo','unwind_map','try_map')]+[t['handlers']for t in graph['try_map']['entries']]
        need(not any(all_code.intersection(range(n['va'],n['va']+n['size']))for n in meta),'original_metadata_overlaps_code')
        # Derived graph pairings do not establish external symbol identity.
        placement={};pairs=[]
        def pair(name,a,b,code=False):
            if code:
                av=a['instructions'];bv=b['instructions'];pairs.append((name,av,bv,None));
                if len(av)==len(bv):
                    for ar,br in zip(av,bv):placement[(main_section,br['pc'])]=ar['pc']
            else:
                placement[(b['section'],b['offset'])]=a['va'];pairs.append((name,None,None,(a,b)))
        main_symbols=[s for s in obj.symbols.values()if s.name==main_name and s.section>0];need(len(main_symbols)==1,'candidate_main_identity');main_section=main_symbols[0].section
        pair('main',main,candidate['main'],True)
        for name in ('handler','FuncInfo','unwind_map','try_map'):pair(name,graph[name],candidate[name])
        need(len(graph['try_map']['entries'])==len(candidate['try_map']['entries']),'try_region_count_differs')
        for i,(a,b) in enumerate(zip(graph['try_map']['entries'],candidate['try_map']['entries'])):pair('handler_table_'+str(i),a['handlers'],b['handlers'])
        for i,(a,b) in enumerate(zip(dependencies,candidate['dependencies'])):pair('dependency_'+str(i),a,b,True)
        totals=dict(equal=0,different=0,unresolved=0,original=0,candidate=0)
        for name,ar,br,data in pairs:
            row=dict(name=name,chunks=[],equal=0,different=0,unresolved=0,original_size=0,candidate_size=0);result['nodes'].append(row)
            if data:
                a,b=data;chunks=[(a['va'],bytes.fromhex(a['bytes_hex']),b['section'],b['offset'],bytes.fromhex(b['bytes_hex']))]
            else:
                row.update(original_instruction_count=len(ar),candidate_instruction_count=len(br))
                # Different counts are differences, never an invitation to drop
                # an unmatched suffix. Preserve each side's complete byte count.
                if len(ar)!=len(br):
                    row.update(original_size=sum(x['length']for x in ar),candidate_size=sum(x['length']for x in br),different=max(sum(x['length']for x in ar),sum(x['length']for x in br)),blocker='instruction_count_differs');chunks=[]
                else:chunks=[(a['pc'],bytes.fromhex(a['raw_hex']),main_section,b['pc'],bytes.fromhex(b['raw_hex']))for a,b in zip(ar,br)]
            for ova,ob,section,off,cb in chunks:
                chunk=dict(original_va=ova,candidate_section=section,candidate_offset=off,original_size=len(ob),candidate_size=len(cb),unresolved_references=[]);patched=bytearray(cb);unknown=set()
                for rel in obj.sections[section-1].relocations:
                    if not off<=rel.offset<off+len(cb):continue
                    at=rel.offset-off;need(at+4<=len(cb),'comparison_relocation_extent');sym=obj.symbols[rel.symbol];target=placement.get((sym.section,sym.value))
                    if target is None:
                        unknown.update(range(at,at+4));chunk['unresolved_references'].append(dict(offset=at,kind=rel.kind,symbol=sym.name));continue
                    need(rel.kind in (6,0x14),'comparison_relocation_kind');struct.pack_into('<I',patched,at,(target if rel.kind==6 else target-(ova+at+4))&0xffffffff)
                eq=sum(a==b for i,(a,b)in enumerate(zip(ob,patched))if i not in unknown);diff=max(len(ob),len(cb))-eq-len(unknown)
                chunk.update(equal=eq,different=diff,unresolved=len(unknown));row['chunks'].append(chunk);row['equal']+=eq;row['different']+=diff;row['unresolved']+=len(unknown);row['original_size']+=len(ob);row['candidate_size']+=len(cb)
            totals['equal']+=row['equal'];totals['different']+=row['different'];totals['unresolved']+=row['unresolved'];totals['original']+=row['original_size'];totals['candidate']+=row['candidate_size']
        result.update(state='diagnostic_differences' if totals['different'] else 'diagnostic_external_identity_unresolved',counts=totals,candidate_complete_code_bytes=candidate['complete_code_bytes'],candidate_complete_metadata_and_handler_bytes=candidate['complete_metadata_and_handler_bytes'])
        result['blockers']=candidate['blockers']
    except (ValueError,KeyError,TypeError,struct.error) as e:result.update(state='diagnostic_incomplete');result['blockers'].append(str(e))
    return result

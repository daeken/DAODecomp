"""Diagnostic-only bounded x86 EH graph comparison. Never an acceptance adapter.

Reference paths, not embedded parent names or FuncInfo markers, select nodes.
All code/data bytes of each supported node are retained. Missing boundaries,
runtime identity and parent-frame semantics are explicit blockers; no address
map from this module may be passed through as acceptance evidence.
"""
import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
from capstone.x86 import X86_OP_MEM
from .coff import Coff, CoffError, unpack
from .compare import PE, normalize_requested, compare_bytes, sha
from .symbol_identity import generated_identity


class Unsupported(CoffError):
    pass


class Original:
    def __init__(self, raw):
        self.pe = PE(raw)

    def read(self, va, size, code=False):
        if type(va) is not int or size <= 0 or not 0 <= va <= 0xffffffff - size + 1:
            raise Unsupported('original_address_or_size')
        rva = va - self.pe.image_base
        found = [(start, ptr) for start, length, ptr, flags in self.pe.sections
                 if start <= rva and rva + size <= start + length
                 and flags & 0x40000000 and (not code or flags & 0x20000000)]
        if len(found) != 1:
            raise Unsupported('original_range_not_unique_backed')
        start, ptr = found[0]
        return self.pe.data[ptr+rva-start:ptr+rva-start+size]


def node(data, **identity):
    return dict(identity, size=len(data), sha256=sha(data), bytes_hex=data.hex())


def handler_shape(data):
    if len(data) == 10 and data[0] == 0xb8 and data[5] == 0xe9:
        return {'cookie_checked': False, 'descriptor_field': 1, 'runtime_field': 6}
    if (len(data) == 27 and data[:6] == bytes.fromhex('8b5424088d42')
            and data[7:9] == bytes.fromhex('8b4a') and data[10:13] == bytes.fromhex('33c8e8')
            and data[17] == 0xb8 and data[22] == 0xe9):
        return {'cookie_checked': True, 'context_argument_esp_offset': 8,
                'cookie_xor_parent_offset': struct.unpack('b', data[6:7])[0],
                'cookie_load_parent_offset': struct.unpack('b', data[9:10])[0],
                'cookie_field': 13, 'descriptor_field': 18, 'runtime_field': 23}
    raise Unsupported('unsupported_or_incomplete_handler_code')


def descriptor_shape(data):
    if len(data) != 36:
        raise Unsupported('incomplete_FuncInfo')
    words = struct.unpack('<9I', data)
    if words[0] != 0x19930522 or words[1] != 1 or words[3:] != (0,0,0,0,0,1):
        raise Unsupported('unsupported_FuncInfo_fields')
    return {'magic': words[0], 'states': words[1], 'try_blocks': 0,
            'ip_map_entries': 0, 'flags': words[8]}


def action_shape(data):
    if (len(data) == 11 and data[:2] == b'\x8b\x45' and data[3:5] == b'\x50\xe8'
            and data[9:] == b'\x59\xc3'):
        return {'kind': 'load_word_push_call_pop_ret', 'parent_ebp_offset': struct.unpack('b',data[2:3])[0],
                'target_field': 5, 'target_kind': 0x14}
    if len(data) == 8 and data[:2] == b'\x8d\x4d' and data[3] == 0xe9:
        return {'kind': 'address_ecx_tail_jump', 'parent_ebp_offset': struct.unpack('b',data[2:3])[0],
                'target_field': 4, 'target_kind': 0x14}
    if len(data) == 8 and data[:2] == b'\x8b\x4d' and data[3] == 0xe9:
        return {'kind': 'load_receiver_ecx_tail_jump', 'parent_ebp_offset': struct.unpack('b',data[2:3])[0],
                'target_field': 4, 'target_kind': 0x14}
    raise Unsupported('unsupported_or_incomplete_unwind_action')


def frame_observations(data, va):
    md = Cs(CS_ARCH_X86, CS_MODE_32); md.detail = True
    xs = list(md.disasm(data, va))
    if sum(i.size for i in xs) != len(data):
        raise Unsupported('incomplete_main_decode')
    writes = []
    for i in xs:
        if i.mnemonic == 'mov' and len(i.operands) == 2 and i.operands[0].type == X86_OP_MEM:
            o = i.operands[0]
            if i.reg_name(o.mem.base) in ('esp','ebp'):
                writes.append({'instruction_offset':i.address-va,'base':i.reg_name(o.mem.base),
                               'displacement':o.mem.disp,'width_bytes':o.size,'instruction':i.mnemonic+' '+i.op_str})
    return {'decoded_bytes':len(data),'decoded_instructions':len(xs),
            'initial_state_minus_one_push':data[:2] == b'\x6a\xff','stack_writes':writes,
            'parent_runtime_frame_binding':'unknown; raw offsets are not normalized or treated as equivalent'}


def original_graph(reader, main_va, data):
    # Exact observed entry root. A pointer-looking word or marker elsewhere is
    # insufficient. The following FS load binds this to the registration prefix.
    if len(data) < 13 or data[:3] != b'\x6a\xff\x68' or data[7:13] != bytes.fromhex('64a100000000'):
        raise Unsupported('original_handler_reference_not_bound_entry_prefix')
    hva, = unpack('<I',data,3)
    first = reader.read(hva, 1, True)
    hsize = 10 if first == b'\xb8' else 27
    hb = reader.read(hva,hsize,True); hp = handler_shape(hb)
    descriptor, = unpack('<I',hb,hp['descriptor_field'])
    runtime = hva + hp['runtime_field'] + 4 + unpack('<i',hb,hp['runtime_field'])[0]
    reader.read(runtime,1,True)
    hd = node(hb,va=hva,boundary_basis='complete supported terminal-jump profile; inventory boundary unverified',profile=hp,runtime_target_va=runtime)
    if hp['cookie_checked']:
        hd['cookie_check_target_va'] = hva+hp['cookie_field']+4+unpack('<i',hb,hp['cookie_field'])[0]
        reader.read(hd['cookie_check_target_va'],1,True)
    db = reader.read(descriptor,36); dp = descriptor_shape(db); uv, = unpack('<I',db,8)
    if descriptor & 3 or uv & 3: raise Unsupported('unaligned_EH_metadata')
    ub = reader.read(uv,8); state, av = unpack('<iI',ub,0)
    if state != -1: raise Unsupported('unsupported_unwind_state_transition')
    # Both supported action forms have an explicit terminal transfer. They are
    # different forms, never flattened or normalized into each other.
    prefix = reader.read(av,4,True)
    action_size = 8 if prefix[:2] in (b'\x8d\x4d', b'\x8b\x4d') and prefix[3] == 0xe9 else 11
    ab = reader.read(av,action_size,True); ap = action_shape(ab)
    target = av+ap['target_field']+4+unpack('<i',ab,ap['target_field'])[0]
    reader.read(target,1,True)
    ranges=[(main_va,main_va+len(data)),(hva,hva+hsize),(descriptor,descriptor+36),(uv,uv+8),(av,av+len(ab))]
    for j,(lo,hi) in enumerate(ranges):
        if any(lo < end and begin < hi for begin,end in ranges[:j]): raise Unsupported('overlapping_original_graph_nodes')
    return {'handler':hd,'FuncInfo':node(db,va=descriptor,fields=dp),'unwind_map':node(ub,va=uv,state_transition=[0,-1]),
            'action':node(ab,va=av,profile=ap,external_target_va=target),
            'main_frame':frame_observations(data,main_va),
            'coverage':'complete bytes of supported bounded profiles; inventory and runtime frame proof remain missing'}


def candidate_graph(obj, main, start, size):
    sec = obj.sections[main.section-1]; raw=sec.data[start:start+size]
    generated=[s for s in obj.symbols.values() if generated_identity(s.name) and generated_identity(s.name)['parent_symbol']==main.name]
    if len(generated)!=4 or len({s.name for s in generated})!=4: raise Unsupported('incomplete_or_extra_parent_generated_inventory')
    if raw[:3] != b'\x6a\xff\x68' or raw[7:13] != bytes.fromhex('64a100000000'):
        raise Unsupported('candidate_handler_reference_not_bound_entry_prefix')
    def span(sym, length=None):
        if sym.section <= 0 or sym.storage not in (2,3): raise Unsupported('graph_node_not_defined')
        section=obj.sections[sym.section-1]
        nexts=[s.value for s in obj.symbols.values() if s.section==sym.section and s.value>sym.value and (s.type & 0x30 == 0x20 or generated_identity(s.name))]
        end=min(nexts,default=len(section.data))
        if length is not None and end-sym.value != length: raise Unsupported('incomplete_or_overlapping_generated_span:'+sym.name)
        if end<=sym.value: raise Unsupported('empty_generated_span')
        return section,sym.value,end-sym.value
    def target(section, lo, length, offset, kind, expected_all):
        rels=[r for r in section.relocations if lo <= r.offset < lo+length]
        if {(r.offset-lo,r.kind) for r in rels} != set(expected_all): raise Unsupported('unsupported_or_incomplete_graph_relocations')
        found=[r for r in rels if r.offset==lo+offset and r.kind==kind]
        if len(found)!=1 or offset+4>length: raise Unsupported('missing_graph_reference')
        if unpack('<I',section.data,lo+offset)[0] != 0: raise Unsupported('nonzero_graph_reference_addend')
        return obj.symbols[found[0].symbol]
    def require_identity(sym, kind):
        identity=generated_identity(sym.name)
        if not identity or not identity['supported_name'] or identity['kind']!=kind or identity['parent_symbol']!=main.name or (kind=='unwindfunclet' and identity['ordinal']!=0): raise Unsupported('generated_graph_identity_conflict')
    roots=[r for r in sec.relocations if r.offset==start+3 and r.kind==6]
    if len(roots)!=1 or unpack('<I',raw,3)[0]!=0: raise Unsupported('candidate_handler_root_relocation')
    handler=obj.symbols[roots[0].symbol];require_identity(handler,'ehhandler');hs,hl,hn=span(handler);
    if handler.type & 0x30 != 0x20 or not hs.characteristics & 0x20000000: raise Unsupported('handler_not_executable_function')
    hb=hs.data[hl:hl+hn];hp=handler_shape(hb)
    expected=[(hp['descriptor_field'],6),(hp['runtime_field'],0x14)]
    if hp['cookie_checked']: expected.append((hp['cookie_field'],0x14))
    descriptor=target(hs,hl,hn,hp['descriptor_field'],6,expected);require_identity(descriptor,'ehfuncinfo')
    runtime=target(hs,hl,hn,hp['runtime_field'],0x14,expected)
    if runtime.section!=0 or runtime.value or runtime.storage!=2: raise Unsupported('runtime_reference_not_plain_external')
    hnode=node(hb,symbol=handler.name,section=handler.section,offset=hl,boundary_basis='next generated function or section end; diagnostic only',profile=hp,runtime_symbol=runtime.name)
    if hp['cookie_checked']:
        cookie=target(hs,hl,hn,hp['cookie_field'],0x14,expected)
        if cookie.section!=0 or cookie.value or cookie.storage!=2: raise Unsupported('cookie_runtime_reference_not_plain_external')
        hnode['cookie_check_symbol']=cookie.name
    ds,dl,dn=span(descriptor,36)
    if descriptor.type or ds.characteristics & 0x20000000: raise Unsupported('FuncInfo_not_data')
    db=ds.data[dl:dl+dn];dp=descriptor_shape(db)
    unwind=target(ds,dl,dn,8,6,[(8,6)]);require_identity(unwind,'unwindtable');us,ul,un=span(unwind,8);ub=us.data[ul:ul+un]
    if unpack('<i',ub,0)[0] != -1: raise Unsupported('unsupported_candidate_unwind_state_transition')
    action=target(us,ul,un,4,6,[(4,6)]);require_identity(action,'unwindfunclet');acs,al,an=span(action)
    if action.type & 0x30 != 0x20 or not acs.characteristics & 0x20000000: raise Unsupported('action_not_executable_function')
    ab=acs.data[al:al+an];ap=action_shape(ab)
    end=target(acs,al,an,ap['target_field'],ap['target_kind'],[(ap['target_field'],ap['target_kind'])]);dependencies=[]
    if end.section>0:
        es,el,en,evidence=obj.function_span(end)
        if any(r.kind not in (6,0x14) or r.offset < el or r.offset+4 > el+en for r in es.relocations): raise Unsupported('unsupported_defined_dependency_relocation')
        dependencies.append(node(es.data[el:el+en],symbol=end.name,section=end.section,offset=el,boundary_basis=evidence,
                                 relocations=[{'offset':r.offset-el,'kind':r.kind,'symbol':obj.symbols[r.symbol].name} for r in es.relocations if el<=r.offset<el+en],
                                 original_correspondence='unknown; no symbol-name or tail-jump alias'))
    elif end.section != 0 or end.value or end.storage!=2: raise Unsupported('action_target_not_supported')
    return {'handler':hnode,'FuncInfo':node(db,symbol=descriptor.name,section=descriptor.section,offset=dl,fields=dp),
            'unwind_map':node(ub,symbol=unwind.name,section=unwind.section,offset=ul,state_transition=[0,-1]),
            'action':node(ab,symbol=action.name,section=action.section,offset=al,profile=ap,target_symbol=end.name),
            'defined_action_dependencies':dependencies,'defined_dependency_original_identity_complete':False if dependencies else True,'main_frame':frame_observations(raw,0),
            'coverage':'complete supported generated spans; extra defined dependencies have no accepted original identity'}


def diagnose(original, object_bytes, requested, symbols=None, *, module_sha256):
    """Return observations/blockers only. This does not return usable placements."""
    report={'diagnostic_only':True,'acceptance_supported':False,'proof':False,
            'module_sha256':sha(original),'object_sha256':sha(object_bytes),'functions':[],
            'discarded_generated_address_claims':{k:v for k,v in (symbols or {}).items() if generated_identity(k)}}
    try:
        if sha(original)!=module_sha256: raise Unsupported('module_sha256_mismatch')
        reader=Original(original); obj=Coff(object_bytes); specs=normalize_requested(requested,reader.pe.image_base)
        safe_symbols={k:v for k,v in (symbols or {}).items() if generated_identity(k) is None}
        legacy=compare_bytes(original,object_bytes,requested,safe_symbols,module_sha256=module_sha256)
        if 'error' in legacy:
            report.update(state='diagnostic_incomplete',error='unchanged_comparator:'+legacy['error'],
                          legacy_comparator={'error':legacy['error'],'counts':legacy['counts']})
            return report
        for rva,spec in specs.items():
            row={'rva':rva,'differences':[],'blockers':[
                'diagnostic_graph_pairing_is_not_acceptance_identity',
                'exception_runtime_symbol_identity_unverified',
                'complete_original_dependency_inventory_boundaries_unverified',
                'parent_runtime_frame_offsets_and_main_state_binding_unverified']}
            report['functions'].append(row)
            try:
                ranges=spec['ranges']
                if not isinstance(ranges,list) or len(ranges)!=1 or ranges[0]['start_rva']!=rva: raise Unsupported('unsupported_main_ranges')
                length=ranges[0]['end_rva_inclusive']-rva+1; raw=reader.read(spec['original_va'],length,True)
                if spec.get('bytes_sha256') and sha(raw)!=spec['bytes_sha256']: raise Unsupported('original_main_sha256_mismatch')
                matches=[s for s in obj.symbols.values() if s.name==spec.get('symbol')]
                if len(matches)!=1 or generated_identity(matches[0].name): raise Unsupported('missing_or_generated_main_identity')
                main=matches[0]; sec,start,size,evidence=obj.function_span(main)
                row['main']={'original_size':len(raw),'candidate_size':size,'candidate_boundary_basis':evidence}
                if size!=len(raw):row['differences'].append('complete_main_length_differs')
                row['original']=original_graph(reader,spec['original_va'],raw)
                row['candidate']=candidate_graph(obj,main,start,size)
                a,b=row['original'],row['candidate']
                for key in ('cookie_checked','context_argument_esp_offset','cookie_xor_parent_offset','cookie_load_parent_offset'):
                    if a['handler']['profile'].get(key)!=b['handler']['profile'].get(key):row['differences'].append('handler_'+key+'_differs')
                if a['FuncInfo']['fields']!=b['FuncInfo']['fields']:row['differences'].append('FuncInfo_fields_differ')
                if a['unwind_map']['state_transition']!=b['unwind_map']['state_transition']:row['differences'].append('state_transition_differs')
                if a['action']['profile']!=b['action']['profile']:row['differences'].append('unwind_action_form_or_frame_offset_differs')
                if a['action']['size']!=b['action']['size']:row['differences'].append('complete_action_length_differs')
                supplied=(symbols or {}).get(b['handler']['runtime_symbol'])
                if supplied is not None and supplied!=a['handler']['runtime_target_va']:row['differences'].append('runtime_target_address_claim_conflict')
                if b['action']['target_symbol'] in (symbols or {}) and not b['defined_action_dependencies']:
                    if symbols[b['action']['target_symbol']]!=a['action']['external_target_va']:row['differences'].append('cleanup_target_address_claim_conflict')
                elif not b['defined_action_dependencies']:row['blockers'].append('cleanup_target_identity_unverified')
                if b['defined_action_dependencies']:row['blockers'].append('defined_action_dependency_original_identity_unverified')
                if a['handler']['profile']['cookie_checked']:row['blockers'].append('cookie_runtime_symbol_identity_unverified')
                prior=next((f for f in legacy['functions'] if f['rva']==rva),None)
                if prior is None: raise Unsupported('unchanged_comparator:missing_function_result')
                row['legacy_comparator']={'status':prior['status'],'diagnostics':prior['diagnostics']}
                if row['legacy_comparator']['status']=='inconclusive':
                    row['blockers'].extend('unchanged_comparator:'+d for d in row['legacy_comparator']['diagnostics'])
                row['state']='diagnostic_differences' if row['differences'] else 'diagnostic_identity_still_unresolved'
            except (CoffError,KeyError,ValueError,TypeError,struct.error) as exc:
                row.update(state='diagnostic_incomplete');row['blockers'].append(str(exc))
    except (CoffError,KeyError,ValueError,TypeError,struct.error) as exc:
        report['error']=str(exc)
    return report

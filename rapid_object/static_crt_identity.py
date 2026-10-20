"""Experimental static-CRT artifact recognition, never an ordinary acceptance gate.

The caller supplies trusted content pins for the selected toolchain/library and
original inventory. Literal-byte searches are identification hypotheses only.
Root routines are compared with every relocation byte resolved from independent
unique dependency profiles; immediate dependency semantics remain external.
"""
import hashlib
import json
import struct
import re
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
from rapid_object.coff import Coff, CoffError
from rapid_object.eh_graph import Original, Unsupported
from rapid_object.compare import sha

ROOTS=('___CxxFrameHandler3','@__security_check_cookie@4','___security_cookie')


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


def require(condition,reason):
    if not condition:raise Unsupported(reason)


def decode_fields(data,relocations):
    """A relocation must cover one entire encoded x86 address operand."""
    md=Cs(CS_ARCH_X86,CS_MODE_32);md.detail=True;ins=list(md.disasm(data,0))
    require(sum(i.size for i in ins)==len(data),'incomplete_x86_decode')
    occupied=set()
    for r in relocations:
        off,kind=r['offset'],r['kind']
        require(type(off) is int and kind in (6,20) and 0<=off<=len(data)-4,'unsupported_relocation_field')
        require(not occupied.intersection(range(off,off+4)),'overlapping_relocation_fields');occupied.update(range(off,off+4))
        owners=[i for i in ins if i.address<=off and off+4<=i.address+i.size]
        require(len(owners)==1,'relocation_crosses_instruction');i=owners[0]
        branch=(i.mnemonic=='call' or i.mnemonic.startswith('j')) and i.imm_size==4
        expected=[i.address+i.imm_offset] if branch and i.imm_size==4 else []
        if not branch:
            if i.imm_size==4:expected.append(i.address+i.imm_offset)
            if i.disp_size==4:expected.append(i.address+i.disp_offset)
        require(off in expected and kind==(20 if branch else 6),'relocation_kind_or_operand_conflict')
    return ins


def mapped_address(reader,address,code=False):
    if code:reader.read(address,1,True);return
    raw=reader.pe.data;peoff=struct.unpack_from('<I',raw,0x3c)[0]
    count=struct.unpack_from('<H',raw,peoff+6)[0];opt=struct.unpack_from('<H',raw,peoff+20)[0];matches=[]
    for k in range(count):
        _,vs,rva,size,_,_,_,_,_,flags=struct.unpack_from('<8sIIIIIIHHI',raw,peoff+24+opt+40*k)
        if rva<=address-reader.pe.image_base<rva+max(vs,size) and flags&0x40000000:matches.append(k)
    require(len(matches)==1,'runtime_reference_not_unique_mapped')


def archive_members(raw):
    require(raw[:8]==b'!<arch>\n','not_COFF_archive');at=8;longs=b''
    while at<len(raw):
        offset=at;head=raw[at:at+60];require(len(head)==60 and head[58:]==b'`\n','bad_archive_header')
        try:size=int(head[48:58]);name=head[:16].decode('ascii').strip()
        except (ValueError,UnicodeError):raise Unsupported('bad_archive_member')
        require(size>=0 and at+60+size<=len(raw),'truncated_archive_member');body=raw[at+60:at+60+size];at+=60+size
        if at%2:require(at<len(raw),'missing_archive_padding');at+=1
        if name=='//':longs=body;continue
        if name=='/':continue
        if name.startswith('/') and name[1:].isdigit():
            k=int(name[1:]);end=longs.find(b'\0',k);require(0<=k<end,'bad_archive_long_name');name=longs[k:end].decode('ascii')
        yield offset,name,body


def inventory_entries(raw,module_sha256,reader):
    inv=json.loads(raw);require(inv.get('module_sha256')==module_sha256,'inventory_module_binding')
    require(inv.get('image_base')==reader.pe.image_base,'inventory_image_base_binding');entries={}
    for f in inv['functions']:
        rva=f['rva'];require(type(rva) is int and rva not in entries,'duplicate_or_invalid_inventory_RVA')
        ranges=f['body_ranges'];require(isinstance(ranges,list) and ranges,'empty_inventory_range')
        entries[rva]=f
    return entries


def definitions(libraries,names):
    out={name:[] for name in names}
    for library,raw in sorted(libraries.items()):
        for offset,member,body in archive_members(raw):
            if not any(name.encode() in body for name in names):continue
            # Import-object records do not establish a static definition.
            if body[:4]==b'\0\0\xff\xff':continue
            if body[:2]==b'\0\0':
                normalized=bytearray(body);struct.pack_into('<H',normalized,0,0x14c);directive=Coff(normalized)
                require(all(s.name=='.drectve' and not s.relocations and not s.characteristics&0x20000000 for s in directive.sections),'unsupported_machine_zero_object')
                require(not any(s.storage==2 and s.section>0 for s in directive.symbols.values()),'machine_zero_definition')
                require(all(not section.data for section in directive.sections) and not any(s.name in names and s.storage==105 for s in directive.symbols.values()),'unsupported_or_conflicting_archive_alias')
                continue
            obj=Coff(body)
            for sym in obj.symbols.values():
                if sym.name not in names or sym.section<=0:continue
                require(sym.storage==2,'runtime_definition_not_external')
                section=obj.sections[sym.section-1]
                if sym.type & 0x30==0x20:
                    section,start,size,basis=obj.function_span(sym);code=True
                else:
                    require(sym.name==ROOTS[2] and sym.type==0 and sym.value==0 and len(section.data)==4 and not section.relocations and section.characteristics&0x80000000,'unsupported_runtime_data_definition')
                    defs=[s for s in obj.symbols.values() if s.section==sym.section and s.storage==3 and s.name==section.name and s.value==0 and len(s.aux)==1]
                    require(len(defs)==1 and struct.unpack_from('<I',defs[0].aux[0])[0]==4 and defs[0].aux[0][14] in (1,2,3,4,6,7),'runtime_data_span_unbound')
                    start,size,basis,code=0,4,'complete4BdataCOMDAT',False
                data=section.data[start:start+size];rels=[]
                for r in section.relocations:
                    if r.offset<start+size and start<r.offset+4:
                        require(start<=r.offset and r.offset+4<=start+size,'runtime_relocation_crosses_span')
                        target=obj.symbols[r.symbol];require(target.storage in (2,3) and target.section>=0,'unsupported_runtime_relocation_symbol')
                        rels.append(dict(offset=r.offset-start,kind=r.kind,symbol=target.name,symbol_index=r.symbol,addend_u32=struct.unpack_from('<I',section.data,r.offset)[0]))
                if code:decode_fields(data,rels)
                out[sym.name].append(dict(symbol=sym.name,library=library,library_sha256=sha(raw),archive_member=member,archive_offset=offset,object_sha256=sha(body),symbol_index=sym.index,section=sym.section,offset=start,size=size,boundary=basis,code=code,bytes_hex=data.hex(),relocations=rels))
    for name,found in out.items():require(len(found)==1,'missing_or_ambiguous_runtime_definition:'+name)
    return {name:found[0] for name,found in out.items()}


def recognize(original,inventory_raw,libraries):
    reader=Original(original);entries=inventory_entries(inventory_raw,sha(original),reader)
    roots=definitions(libraries,set(ROOTS));needed=set(ROOTS)
    for d in roots.values():needed.update(r['symbol'] for r in d['relocations'])
    defs=definitions(libraries,needed);profiles={}
    for name,d in defs.items():
        code=bytes.fromhex(d['bytes_hex']);matches=[];examined=0
        if not d['code']:
            for rva,size,ptr,flags in reader.pe.sections:
                if not flags&0x80000000 or not flags&0x40000000:continue
                body=reader.pe.data[ptr:ptr+size];at=0
                while True:
                    at=body.find(code,at)
                    if at<0:break
                    va=reader.pe.image_base+rva+at
                    if va%4==0:matches.append(dict(va=va,bytes_hex=code.hex(),edges=[]))
                    at+=1
        else:
            holes={i for r in d['relocations'] for i in range(r['offset'],r['offset']+4)}
            for rva,f in entries.items():
                ranges=f['body_ranges']
                if ranges!=[{'start_rva':rva,'end_rva_inclusive':rva+len(code)-1}]:continue
                ref=reader.read(reader.pe.image_base+rva,len(code),True);examined+=1
                if any(a!=b for i,(a,b) in enumerate(zip(code,ref)) if i not in holes):continue
                va=reader.pe.image_base+rva;edges=[];known={};valid=True
                for r in d['relocations']:
                    off=r['offset'];v=struct.unpack_from('<I',ref,off)[0]
                    address=(v+(va+off+4 if r['kind']==20 else 0)-r['addend_u32'])&0xffffffff
                    if r['symbol'] in known and known[r['symbol']]!=address:valid=False;break
                    known[r['symbol']]=address
                    try:mapped_address(reader,address,r['kind']==20)
                    except CoffError:valid=False;break
                    edges.append(dict(r,target_va=address,original_field_u32=v))
                if valid:matches.append(dict(va=va,bytes_hex=ref.hex(),edges=edges))
        profiles[name]=dict(definition=d,examined_same_size=examined,matches=matches)
    # Propagate shared relocation/data constraints; no desired address chooses a match.
    changed=True
    while changed:
        changed=False
        for name,p in profiles.items():
            keep=[m for m in p['matches'] if all(e['symbol'] not in profiles or e['target_va'] in {x['va'] for x in profiles[e['symbol']]['matches']} for e in m['edges'])]
            if len(keep)!=len(p['matches']):changed=True;p['matches']=keep
    for name,p in profiles.items():require(len(p['matches'])==1,'nonunique_or_missing_runtime_profile:'+name)
    identities={name:p['matches'][0]['va'] for name,p in profiles.items()};full={}
    for name in ROOTS:
        p=profiles[name];d=p['definition'];m=p['matches'][0];patched=bytearray.fromhex(d['bytes_hex'])
        for r in d['relocations']:
            require(r['symbol'] in identities,'runtime_root_dependency_unbound')
            v=(identities[r['symbol']]+r['addend_u32']-(m['va']+r['offset']+4 if r['kind']==20 else 0))&0xffffffff;struct.pack_into('<I',patched,r['offset'],v)
        require(bytes(patched)==bytes.fromhex(m['bytes_hex']),'runtime_root_complete_bytes_differ')
        full[name]=dict(va=m['va'],size=len(patched),bytes_hex=patched.hex(),sha256=sha(patched),all_bytes_compared=True)
    return dict(status='independent_unique_profile_and_edge_identity',root_bindings={name:identities[name] for name in ROOTS},root_complete_comparisons=full,profiles=profiles,external_dependency_semantics='unknown; immediate identity profiles are not transitive semantic equivalence')

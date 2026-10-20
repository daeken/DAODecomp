"""Original-derived VC8 exceptional terminal identity, not a function-name oracle.

No acceptance verdict, guessed boundary, runtime stub, or arbitrary noreturn list.
The bound library definition, complete pinned inventory and independently named
PE import/data edges must agree. The Windows noncontinuable-exception contract
is an explicit profile assumption; arbitrary handler/debugger context mutation
and whole-program behavior are not proved.
"""
import struct
from rapid_object.static_crt_identity import definitions, inventory_entries, require
from rapid_object.eh_graph import Original
from rapid_object.compare import sha

SYMBOL='__CxxThrowException@8'
TEMPLATE='?ExceptionTemplate@?1??_CxxThrowException@@9@8@4UEHExceptionRecord@@B'
IMPORT='__imp__RaiseException@16'


def bind_complete_function(definition, reader, entries, symbols):
    """No desired target picks an identity: require one complete resolved match."""
    code=bytes.fromhex(definition['bytes_hex']);patched=bytearray(code)
    for edge in definition['relocations']:
        require(edge['symbol'] in symbols,'terminal_runtime_dependency_unbound')
        require(edge['kind']==6 and edge['addend_u32']==0,'terminal_runtime_relocation_domain')
        at=edge['offset'];require(0<=at<=len(code)-4,'terminal_runtime_relocation_bounds')
        struct.pack_into('<I',patched,at,symbols[edge['symbol']])
    matches=[]
    for rva,entry in entries.items():
        if entry['body_ranges']!=[dict(start_rva=rva,end_rva_inclusive=rva+len(code)-1)]:continue
        raw=reader.read(reader.pe.image_base+rva,len(code),True)
        if raw==bytes(patched):matches.append(reader.pe.image_base+rva)
    require(len(matches)==1,'terminal_runtime_nonunique_or_missing_complete_match')
    return dict(target=matches[0],size=len(code),bytes_sha256=sha(patched),complete_bytes_compared=True,
                library_sha256=definition['library_sha256'],object_sha256=definition['object_sha256'],symbol=definition['symbol'],resolved_symbols=symbols)


def readonly_data_identity(reader, expected):
    matches=[]
    for rva,size,ptr,flags in reader.pe.sections:
        if not flags&0x40000000 or flags&0xa0000000:continue # read-only, non-code
        body=reader.pe.data[ptr:ptr+size];at=0
        while True:
            at=body.find(expected,at)
            if at<0:break
            va=reader.pe.image_base+rva+at
            if va%4==0:matches.append(va)
            at+=1
    require(len(matches)==1,'terminal_exception_template_nonunique_or_missing')
    return matches[0]


def exception_template(libraries):
    # The local static symbol belongs to the SAME exact archive member as the
    # runtime root; no search using a caller-supplied target or metadata name.
    from rapid_object.static_crt_identity import archive_members
    from rapid_object.coff import Coff
    root=definitions(libraries,{SYMBOL})[SYMBOL];raw=libraries[root['library']]
    bodies=[body for offset,name,body in archive_members(raw) if offset==root['archive_offset']]
    require(len(bodies)==1 and sha(bodies[0])==root['object_sha256'],'terminal_archive_member_binding')
    obj=Coff(bodies[0]);found=[s for s in obj.symbols.values() if s.name==TEMPLATE and s.section>0]
    require(len(found)==1,'terminal_exception_template_symbol')
    symbol=found[0];section=obj.sections[symbol.section-1]
    require(symbol.value==0 and symbol.type==0 and symbol.storage==3 and len(section.data)==32 and not section.relocations and section.characteristics&0x40000000 and not section.characteristics&0xa0000000,'terminal_exception_template_shape')
    # VC8 EHExceptionRecord fields: Code, Flags, Next, Address, Count, Info[3].
    words=struct.unpack('<8I',section.data)
    require(words[0]==0xe06d7363 and words[1]==1 and words[2:4]==(0,0) and words[4]==3 and words[6:]==(0,0),'terminal_noncontinuable_exception_template')
    require({e['symbol'] for e in root['relocations']}=={TEMPLATE,IMPORT} and len(root['relocations'])==2,'terminal_CRT_dependency_domain')
    return root,section.data


def derive(original, inventory, libraries):
    import pefile
    reader=Original(original);entries=inventory_entries(inventory,sha(original),reader)
    root,template=exception_template(libraries)
    pe=pefile.PE(data=original,fast_load=True);pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT']])
    imports=[item.address for module in getattr(pe,'DIRECTORY_ENTRY_IMPORT',[]) if module.dll.lower()==b'kernel32.dll' for item in module.imports if item.name==b'RaiseException']
    require(len(imports)==1,'terminal_RaiseException_import_nonunique_or_missing')
    data=readonly_data_identity(reader,template)
    binding=bind_complete_function(root,reader,entries,{TEMPLATE:data,IMPORT:imports[0]})
    binding.update(profile='vc8-CxxThrowException-noncontinuable-v1',exception_template_sha256=sha(template),exception_template_va=data,RaiseException_import_va=imports[0],normal_return_supported=False,
        assumptions=['unmodified bound VC8 runtime/data and named KERNEL32 RaiseException import',
        'Windows noncontinuable exception cannot resume at the call continuation; handler/debugger arbitrary context rewriting excluded'],
        effects='exception dispatch, handlers, memory effects, termination and exceptional destinations remain unknown',proof=False)
    return binding

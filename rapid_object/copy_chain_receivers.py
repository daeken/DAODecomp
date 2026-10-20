"""Observed receivers for one bounded field-copy/list-walk source shape.

Unknown virtual and nested indirect calls remain unknown. Complete caller/callee
bytes support a C++ hypothesis; acceptance remains the unchanged full comparator.
"""
import re,json
import capstone
from . import ast_match as m,eh_graph as g
from .conditional_construction import Unsupported,sha
from .lookup_receiver_flags import capture

def propose(source,ast,rva,bound,original,inventory):
 raw=source.encode()
 if not source.isascii() or sha(raw)!=bound.get('source_sha256') or sha(original)!=bound.get('module_sha256'):raise Unsupported('source_or_original_binding')
 nodes=list(m.fix.walk(ast))
 if any(n.get('isInvalid') or n.get('kind') in ('RecoveryExpr','UnresolvedLookupExpr') for n in nodes):raise Unsupported('incomplete_AST')
 for name,kind in [('uint','unsigned int'),('undefined4','unsigned int'),('undefined1','unsigned char'),('code','unsigned int (...)')]:
  ts=[n for n in nodes if n.get('kind')=='TypedefDecl' and n.get('name')==name and not n.get('isImplicit')]
  if len(ts)!=1 or ts[0]['type']['qualType']!=kind:raise Unsupported('consumed_type_'+name)
 own=[n for n in nodes if n.get('kind')=='CXXMethodDecl' and n.get('name')=='fn_%08x'%rva and any(c.get('kind')=='CompoundStmt' for c in n.get('inner',[]))]
 if len(own)!=1:raise Unsupported('unique_own_method')
 f=own[0];body=next(n for n in f['inner'] if n.get('kind')=='CompoundStmt')
 if f['type']['qualType']!='void (int) __attribute__((thiscall))':raise Unsupported('method_type')
 if [(n.get('name'),n['type']['qualType']) for n in f['inner'] if n.get('kind')=='ParmVarDecl']!=[('param_2','int')]:raise Unsupported('parameters')
 def span(n):
  if any('spellingLoc'in p or 'expansionLoc'in p for p in n.get('range',{}).values()):raise Unsupported('macro')
  p=m.fix.offsets(n)
  if not p or not 0<=p[0]<p[1]<=len(raw):raise Unsupported('span')
  return p
 for n in [f]+list(m.fix.walk(body)):
  if 'range'in n:span(n)
 a,b=span(body);text=raw[a:b].decode();compact=re.sub(r'\s+','',text)
 template='{int*piVar1;undefined4uVar2;fn_FIRST(param_2);*(undefined1*)(param_2+0x2c)=*(undefined1*)(((int)this)+0x2c);*(undefined4*)(param_2+0x30)=*(undefined4*)(((int)this)+0x30);fn_SECOND(*(undefined4**)(((int)this)+0x34)+2,**(undefined4**)(((int)this)+0x34));*(undefined4*)(param_2+0x38)=*(undefined4*)(((int)this)+0x38);*(undefined4*)(param_2+0x3c)=*(undefined4*)(((int)this)+0x3c);*(undefined4*)(param_2+0x40)=*(undefined4*)(((int)this)+0x40);*(undefined1*)(param_2+0x44)=*(undefined1*)(((int)this)+0x44);for(piVar1=*(int**)(((int)this)+0x18);piVar1!=(int*)0x0;piVar1=(int*)piVar1[10]){uVar2=(**(code**)(*piVar1+0x3c))();fn_THIRD(uVar2);}return;}'
 pattern=re.escape(template)
 for name in ['FIRST','SECOND','THIRD']:pattern=pattern.replace(name,'([0-9a-f]{8})')
 match=re.fullmatch(pattern,compact)
 if not match:raise Unsupported('complete_retained_body_shape')
 names=match.groups();reader=g.Original(original);va=reader.pe.image_base+rva
 if re.findall(r'^// FUNCTION: DAO (0x[0-9a-fA-F]+)$',source,re.M)!=[f'0x{va:08x}']:raise Unsupported('unique_source_marker')
 for name in names:
  decl='extern "C" unsigned int __cdecl fn_'+name+'(...);'
  if source.count(decl)!=1 or source.index(decl)>=span(f)[0]:raise Unsupported('callee_declaration')
 spec=bound['requested'].get(str(rva),bound['requested'].get(rva))
 if not spec or len(spec['ranges'])!=1 or spec['ranges'][0]['start_rva']!=rva:raise Unsupported('original_range')
 ran=spec['ranges'][0];code=reader.read(va,ran['end_rva_inclusive']-rva+1,True)
 if len(code)!=109 or sha(code)!=spec['bytes_sha256'] or sha(code)!=ran['bytes_sha256']:raise Unsupported('original_range_hash')
 xs=list(capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32).disasm(code,va))
 expected=[('push','esi'),('push','edi'),('mov','edi, dword ptr [esp + 0xc]'),('push','edi'),('mov','esi, ecx'),('call',hex(reader.pe.image_base+int(names[0],16))),('movzx','eax, byte ptr [esi + 0x2c]'),('mov','byte ptr [edi + 0x2c], al'),('mov','ecx, dword ptr [esi + 0x30]'),('mov','dword ptr [edi + 0x30], ecx'),('mov','eax, dword ptr [esi + 0x34]'),('mov','edx, dword ptr [eax]'),('push','edx'),('add','eax, 8'),('push','eax'),('lea','ecx, [edi + 0x34]'),('call',hex(reader.pe.image_base+int(names[1],16))),('mov','eax, dword ptr [esi + 0x38]'),('mov','dword ptr [edi + 0x38], eax'),('mov','ecx, dword ptr [esi + 0x3c]'),('mov','dword ptr [edi + 0x3c], ecx'),('mov','edx, dword ptr [esi + 0x40]'),('mov','dword ptr [edi + 0x40], edx'),('movzx','eax, byte ptr [esi + 0x44]'),('mov','byte ptr [edi + 0x44], al'),('mov','esi, dword ptr [esi + 0x18]'),('test','esi, esi'),('je',hex(va+104)),('lea','ecx, [ecx]'),('mov','edx, dword ptr [esi]'),('mov','eax, dword ptr [edx + 0x3c]'),('mov','ecx, esi'),('call','eax'),('push','eax'),('mov','ecx, edi'),('call',hex(reader.pe.image_base+int(names[2],16))),('mov','esi, dword ptr [esi + 0x28]'),('test','esi, esi'),('jne',hex(va+80)),('pop','edi'),('pop','esi'),('ret','4')]
 if sum(x.size for x in xs)!=109 or [(x.mnemonic,x.op_str) for x in xs]!=expected:raise Unsupported('complete_original_instruction_profile')
 inv=json.loads(inventory)
 if inv['module_sha256']!=sha(original) or inv['image_base']!=reader.pe.image_base:raise Unsupported('inventory_binding')
 entries={}
 for entry in inv['functions']:
  if entry['rva'] in entries:raise Unsupported('duplicate_inventory_identity')
  entries[entry['rva']]=entry
 captures=[capture(reader,entries[int(n,16)],cleanup,allow_indirect_calls=(i==2)) for i,(n,cleanup) in enumerate(zip(names,[4,8,4]))]
 # Replace the entire checked body so accepted whitespace variation cannot defeat edits.
 new=BODY
 for key,name in zip(['FIRST','SECOND','THIRD'],names):new=new.replace(key,name)
 candidate=raw[:a]+new.encode()+raw[b:]
 for name in names:candidate=candidate.replace(('extern "C" unsigned int __cdecl fn_'+name).encode(),('unsigned int __cdecl fn_'+name).encode())
 return candidate.decode(),dict(rva=rva,source_sha256=sha(raw),candidate_sha256=sha(candidate),original_sha256=sha(original),original_range_sha256=sha(code),inventory_sha256=sha(inventory),original_instructions=len(xs),callees=captures,virtual_call=dict(slot_bytes=60,receiver='current list node',target='unknown',semantics='unknown'),arithmetic='unsigned32 address additions',hypothesis_only=True,unknowns=['all callee and virtual-call semantics','nominal field/list layouts and object extents'],acceptance='unchanged complete relocation-aware comparator only')

BODY='{\n  int *piVar1;\n  undefined4 uVar2;\n  \n  ((uint(__thiscall*)(void*,unsigned int))&fn_FIRST)(this,param_2);\n  *(undefined1 *)((uint)param_2 + 0x2cu) = *(undefined1 *)((uint)this + 0x2cu);\n  *(undefined4 *)((uint)param_2 + 0x30u) = *(undefined4 *)((uint)this + 0x30u);\n  ((uint(__thiscall*)(void*,void*,unsigned int))&fn_SECOND)((void*)((uint)param_2 + 0x34u),*(undefined4 **)((uint)this + 0x34u) + 2,**(undefined4 **)((uint)this + 0x34u));\n  *(undefined4 *)((uint)param_2 + 0x38u) = *(undefined4 *)((uint)this + 0x38u);\n  *(undefined4 *)((uint)param_2 + 0x3cu) = *(undefined4 *)((uint)this + 0x3cu);\n  *(undefined4 *)((uint)param_2 + 0x40u) = *(undefined4 *)((uint)this + 0x40u);\n  *(undefined1 *)((uint)param_2 + 0x44u) = *(undefined1 *)((uint)this + 0x44u);\n  for (piVar1 = *(int **)((uint)this + 0x18u); piVar1 != (int *)0x0; piVar1 = (int *)piVar1[10]) {\n    uVar2 = ((uint(__thiscall*)(void*))(**(code **)(*(uint*)piVar1 + 0x3cu)))(piVar1);\n    ((uint(__thiscall*)(void*,unsigned int))&fn_THIRD)((void*)param_2,uVar2);\n  }\n  return;\n}'

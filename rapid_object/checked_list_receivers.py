"""Bounded checked-list receiver spelling; unknown error/virtual effects stay unknown.

Complete original caller/callee bytes bind the proposal. Only the unchanged
whole-function comparator can accept the emitted C++.
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
 if f['type']['qualType']!='void (undefined4) __attribute__((thiscall))':raise Unsupported('method_type')
 if [(n.get('name'),n['type']['qualType']) for n in f['inner'] if n.get('kind')=='ParmVarDecl']!=[('param_2','undefined4')]:raise Unsupported('parameters')
 def span(n):
  if any('spellingLoc'in p or 'expansionLoc'in p for p in n.get('range',{}).values()):raise Unsupported('macro')
  p=m.fix.offsets(n)
  if not p or not 0<=p[0]<p[1]<=len(raw):raise Unsupported('span')
  return p
 for n in [f]+list(m.fix.walk(body)):
  if 'range'in n:span(n)
 a,b=span(body);text=raw[a:b].decode();compact=re.sub(r'\s+','',text)
 template='{intiVar1;intiVar2;intiVar3;int*piVar4;undefined1local_8[8];piVar4=(int*)fn_FIRST(local_8,param_2);iVar1=*piVar4;iVar2=piVar4[1];iVar3=*(int*)(((int)this)+4);if((iVar1==0)||(iVar1!=((int)this))){fn_ERROR();}if(iVar2!=iVar3){if(iVar1==0){fn_ERROR();}if(iVar2==*(int*)(iVar1+4)){fn_ERROR();}if(*(undefined4**)(iVar2+0x28)!=(undefined4*)0x0){(**(code**)**(undefined4**)(iVar2+0x28))(1);}fn_LAST(local_8,iVar1,iVar2);}return;}'
 pattern=re.escape(template).replace('FIRST','(?P<first>[0-9a-f]{8})').replace('LAST','(?P<last>[0-9a-f]{8})')
 pattern=pattern.replace('ERROR','(?P<error>[0-9a-f]{8})',1).replace('ERROR','(?P=error)')
 match=re.fullmatch(pattern,compact)
 if not match:raise Unsupported('complete_retained_body_shape')
 names=[match.group(k) for k in ['first','error','last']];reader=g.Original(original);va=reader.pe.image_base+rva
 if re.findall(r'^// FUNCTION: DAO (0x[0-9a-fA-F]+)$',source,re.M)!=[f'0x{va:08x}']:raise Unsupported('unique_source_marker')
 for name in names:
  decl='extern "C" unsigned int __cdecl fn_'+name+'(...);'
  if source.count(decl)!=1 or source.index(decl)>=span(f)[0]:raise Unsupported('callee_declaration')
 spec=bound['requested'].get(str(rva),bound['requested'].get(rva))
 if not spec or len(spec['ranges'])!=1 or spec['ranges'][0]['start_rva']!=rva:raise Unsupported('original_range')
 ran=spec['ranges'][0];code=reader.read(va,ran['end_rva_inclusive']-rva+1,True)
 if len(code)!=109 or sha(code)!=spec['bytes_sha256'] or sha(code)!=ran['bytes_sha256']:raise Unsupported('original_range_hash')
 xs=list(capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32).disasm(code,va))
 expected=[('mov','eax, dword ptr [esp + 4]'),('sub','esp, 8'),('push','ebx'),('push','ebp'),('push','esi'),('push','edi'),('mov','esi, ecx'),('push','eax'),('lea','ecx, [esp + 0x14]'),('push','ecx'),('mov','ecx, esi'),('call',hex(reader.pe.image_base+int(names[0],16))),('mov','edi, dword ptr [eax]'),('test','edi, edi'),('mov','ebx, dword ptr [eax + 4]'),('mov','ebp, dword ptr [esi + 4]'),('je',hex(va+42)),('cmp','edi, esi'),('je',hex(va+47)),('call',hex(reader.pe.image_base+int(names[1],16))),('cmp','ebx, ebp'),('je',hex(va+99)),('test','edi, edi'),('jne',hex(va+60)),('call',hex(reader.pe.image_base+int(names[1],16))),('cmp','ebx, dword ptr [edi + 4]'),('jne',hex(va+70)),('call',hex(reader.pe.image_base+int(names[1],16))),('mov','ecx, dword ptr [ebx + 0x28]'),('test','ecx, ecx'),('je',hex(va+85)),('mov','edx, dword ptr [ecx]'),('mov','eax, dword ptr [edx]'),('push','1'),('call','eax'),('push','ebx'),('push','edi'),('lea','ecx, [esp + 0x18]'),('push','ecx'),('mov','ecx, esi'),('call',hex(reader.pe.image_base+int(names[2],16))),('pop','edi'),('pop','esi'),('pop','ebp'),('pop','ebx'),('add','esp, 8'),('ret','4')]
 if sum(x.size for x in xs)!=109 or [(x.mnemonic,x.op_str) for x in xs]!=expected:raise Unsupported('complete_original_instruction_profile')
 inv=json.loads(inventory)
 if inv['module_sha256']!=sha(original) or inv['image_base']!=reader.pe.image_base:raise Unsupported('inventory_binding')
 entries={}
 for entry in inv['functions']:
  if entry['rva'] in entries:raise Unsupported('duplicate_inventory_identity')
  entries[entry['rva']]=entry
 captures=[capture(reader,entries[int(names[i],16)],cleanup) for i,cleanup in [(0,8),(2,12)]]
 new=BODY
 for key,name in zip(['FIRST','ERROR','LAST'],names):new=new.replace(key,name)
 candidate=raw[:a]+new.encode()+raw[b:]
 for name in [names[0],names[2]]:candidate=candidate.replace(('extern "C" unsigned int __cdecl fn_'+name).encode(),('unsigned int __cdecl fn_'+name).encode())
 return candidate.decode(),dict(rva=rva,source_sha256=sha(raw),candidate_sha256=sha(candidate),original_sha256=sha(original),original_range_sha256=sha(code),inventory_sha256=sha(inventory),original_instructions=len(xs),callees=captures,error_handler=dict(rva=int(names[1],16),semantics='unknown; not assumed to return, throw, terminate or succeed'),virtual_call=dict(slot_bytes=0,receiver='single observed pointer load at node+0x28',target='unknown',semantics='unknown'),arithmetic='unsigned32 field address additions',hypothesis_only=True,unknowns=['external/error/virtual callee semantics','nominal object and iterator layouts'],acceptance='unchanged complete relocation-aware comparator only')

BODY='{\n  int iVar1;\n  int iVar2;\n  int iVar3;\n  int *piVar4;\n  undefined1 local_8 [8];\n  \n  piVar4 = (int *)((uint(__thiscall*)(void*,void*,undefined4))&fn_FIRST)(this,local_8,param_2);\n  iVar1 = *piVar4;\n  iVar2 = piVar4[1];\n  iVar3 = *(int *)((uint)this + 4u);\n  if ((iVar1 == 0) || (iVar1 != ((int)this))) {\n    fn_ERROR();\n  }\n  if (iVar2 != iVar3) {\n    if (iVar1 == 0) {\n      fn_ERROR();\n    }\n    if (iVar2 == *(int *)((uint)iVar1 + 4u)) {\n      fn_ERROR();\n    }\n    undefined4* observed_receiver = *(undefined4 **)((uint)iVar2 + 0x28u);\n    if (observed_receiver != (undefined4*)0) {\n      ((uint(__thiscall*)(void*,uint))(**(code **)*observed_receiver))(observed_receiver,1u);\n    }\n    ((uint(__thiscall*)(void*,void*,int,int))&fn_LAST)(this,local_8,iVar1,iVar2);\n  }\n  return;\n}'

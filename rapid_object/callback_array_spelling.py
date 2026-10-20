"""Conservative retained callback-array spelling hypothesis; no callback stub.

Unknown targets/effects stay unknown. This proposal preserves useful nonmatches;
source recognition and distance reductions cannot grant acceptance.
"""
import re
import capstone
from . import ast_match as m,eh_graph as g
from .conditional_construction import Unsupported,sha

def propose(source,ast,rva,bound,original):
 raw=source.encode()
 if not source.isascii() or sha(raw)!=bound.get('source_sha256') or sha(original)!=bound.get('module_sha256'):raise Unsupported('source_or_original_binding')
 nodes=list(m.fix.walk(ast))
 if any(n.get('isInvalid') or n.get('kind') in ('RecoveryExpr','UnresolvedLookupExpr') for n in nodes):raise Unsupported('incomplete_AST')
 for name,kind in [('uint','unsigned int'),('undefined4','unsigned int'),('code','unsigned int (...)')]:
  ts=[n for n in nodes if n.get('kind')=='TypedefDecl' and n.get('name')==name and not n.get('isImplicit')]
  if len(ts)!=1 or ts[0]['type']['qualType']!=kind:raise Unsupported('consumed_type_'+name)
 own=[n for n in nodes if n.get('kind')=='CXXMethodDecl' and n.get('name')=='fn_%08x'%rva and any(c.get('kind')=='CompoundStmt' for c in n.get('inner',[]))]
 if len(own)!=1:raise Unsupported('unique_own_method')
 f=own[0];body=next(n for n in f['inner'] if n.get('kind')=='CompoundStmt')
 if f['type']['qualType']!='void (undefined4, undefined4) __attribute__((thiscall))':raise Unsupported('method_type')
 if [(n.get('name'),n['type']['qualType']) for n in f['inner'] if n.get('kind')=='ParmVarDecl']!=[('param_2','undefined4'),('param_3','undefined4')]:raise Unsupported('parameters')
 def span(n):
  if any('spellingLoc'in p or 'expansionLoc'in p for p in n.get('range',{}).values()):raise Unsupported('macro')
  p=m.fix.offsets(n)
  if not p or not 0<=p[0]<p[1]<=len(raw):raise Unsupported('span')
  return p
 for n in [f]+list(m.fix.walk(body)):
  if 'range'in n:span(n)
 a,b=span(body);text=raw[a:b].decode();compact=re.sub(r'\s+','',text)
 template='{intiVar1;undefined4*puVar2;uintuVar3;uintuVar4;if(*(int*)(((int)this)+0x130)==0){uVar3=0;}else{uVar3=*(int*)(((int)this)+0x134)-*(int*)(((int)this)+0x130)>>2;}uVar4=0;if(uVar3!=0){do{iVar1=*(int*)(((int)this)+0x130);if((iVar1==0)||((uint)(*(int*)(((int)this)+0x134)-iVar1>>2)<=uVar4)){puVar2=&g_GLOBAL;}else{puVar2=(undefined4*)(iVar1+uVar4*4);}(*(code*)*puVar2)(param_2,param_3);uVar4=uVar4+1;}while(uVar4<uVar3);}return;}'
 pattern=re.escape(template).replace('GLOBAL','([0-9a-f]{8})')
 match=re.fullmatch(pattern,compact)
 if not match:raise Unsupported('complete_retained_body_shape')
 name=match.group(1);reader=g.Original(original);va=reader.pe.image_base+rva
 if re.findall(r'^// FUNCTION: DAO (0x[0-9a-fA-F]+)$',source,re.M)!=[f'0x{va:08x}']:raise Unsupported('unique_source_marker')
 decl='extern "C" undefined4 g_'+name+';'
 if source.count(decl)!=1 or source.index(decl)>=span(f)[0]:raise Unsupported('global_declaration')
 spec=bound['requested'].get(str(rva),bound['requested'].get(rva))
 if not spec or len(spec['ranges'])!=1 or spec['ranges'][0]['start_rva']!=rva:raise Unsupported('original_range')
 ran=spec['ranges'][0];code=reader.read(va,ran['end_rva_inclusive']-rva+1,True)
 if len(code)!=109 or sha(code)!=spec['bytes_sha256'] or sha(code)!=ran['bytes_sha256']:raise Unsupported('original_range_hash')
 xs=list(capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32).disasm(code,va))
 expected=[('push','ebx'),('push','esi'),('push','edi'),('mov','edi, ecx'),('mov','eax, dword ptr [edi + 0x130]'),('test','eax, eax'),('jne',hex(va+19)),('xor','ebx, ebx'),('jmp',hex(va+30)),('mov','ebx, dword ptr [edi + 0x134]'),('sub','ebx, eax'),('sar','ebx, 2'),('xor','esi, esi'),('test','ebx, ebx'),('jbe',hex(va+103)),('push','ebp'),('mov','ebp, dword ptr [esp + 0x18]'),('lea','esp, [esp]'),('mov','ecx, dword ptr [edi + 0x130]'),('test','ecx, ecx'),('je',hex(va+80)),('mov','eax, dword ptr [edi + 0x134]'),('sub','eax, ecx'),('sar','eax, 2'),('cmp','esi, eax'),('jae',hex(va+80)),('mov','eax, ecx'),('lea','eax, [eax + esi*4]'),('jmp',hex(va+85)),('mov','eax, '+hex(reader.pe.image_base+int(name,16))),('mov','ecx, dword ptr [esp + 0x14]'),('mov','edx, dword ptr [eax]'),('push','ebp'),('push','ecx'),('call','edx'),('add','esi, 1'),('cmp','esi, ebx'),('jb',hex(va+48)),('pop','ebp'),('pop','edi'),('pop','esi'),('pop','ebx'),('ret','8')]
 if sum(x.size for x in xs)!=109 or [(x.mnemonic,x.op_str) for x in xs]!=expected:raise Unsupported('complete_original_instruction_profile')
 new=BODY.replace('GLOBAL',name)
 candidate=raw[:a]+new.encode()+raw[b:]
 return candidate.decode(),dict(rva=rva,source_sha256=sha(raw),candidate_sha256=sha(candidate),original_sha256=sha(original),original_range_sha256=sha(code),original_instructions=len(xs),callback=dict(target='unknown',normal_return_cleanup_bytes=8,ABI='stdcall spelling hypothesis; no formal callee semantics',effects='unknown'),arithmetic='unsigned32 address additions/subtractions; selected VC8 signed reinterpretation and SAR',hypothesis_only=True,remaining_unknowns=['callback semantics and nominal callback-array/object extents','compiler register allocation and bounds-check scheduling'],acceptance='unchanged complete comparator only; retained output is nonmatch')

BODY='{\n  int iVar1;\n  undefined4 *puVar2;\n  uint uVar3;\n  uint uVar4;\n  \n  if (*(int *)((uint)this + 0x130u) == 0) {\n    uVar3 = 0;\n  }\n  else {\n    uVar3 = (int)(*(uint *)((uint)this + 0x134u) - *(uint *)((uint)this + 0x130u)) >> 2;\n  }\n  uVar4 = 0;\n  if (((unsigned int)(uVar3)) > 0u) {\n    do {\n      iVar1 = *(int *)((uint)this + 0x130u);\n      if ((iVar1 == 0) || ((uint)((int)(*(uint *)((uint)this + 0x134u) - (uint)iVar1) >> 2) <= uVar4)) {\n        puVar2 = &g_GLOBAL;\n      }\n      else {\n        puVar2 = (undefined4 *)(iVar1 + uVar4 * 4);\n      }\n      ((uint(__stdcall*)(undefined4,undefined4))*puVar2)(param_2,param_3);\n      uVar4 = uVar4 + 1;\n    } while (uVar4 < uVar3);\n  }\n  return;\n}'

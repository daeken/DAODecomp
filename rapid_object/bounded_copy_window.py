"""Bounded page-window source hypothesis with defined 32-bit arithmetic.

The complete retained body and original instruction profile are preconditions.
Unknown copy-call semantics remain external; only the unchanged comparator accepts.
"""
import re
import capstone
from . import ast_match as m,eh_graph as g
from .conditional_construction import Unsupported,sha
from .branch_zero_fix import rewrite as zero_rewrite

def propose(source,ast,rva,bound,original):
 raw=source.encode()
 if not source.isascii() or sha(raw)!=bound.get('source_sha256') or sha(original)!=bound.get('module_sha256'):raise Unsupported('source_or_original_binding')
 nodes=list(m.fix.walk(ast))
 if any(n.get('isInvalid') or n.get('kind') in ('RecoveryExpr','UnresolvedLookupExpr') for n in nodes):raise Unsupported('incomplete_AST')
 for name,kind in [('uint','unsigned int'),('size_t','uint')]:
  types=[n for n in nodes if n.get('kind')=='TypedefDecl' and n.get('name')==name and not n.get('isImplicit')]
  if len(types)!=1 or types[0]['type']['qualType']!=kind:raise Unsupported('consumed_type_'+name)
 own=[n for n in nodes if n.get('kind')=='CXXMethodDecl' and n.get('name')=='fn_%08x'%rva and any(c.get('kind')=='CompoundStmt' for c in n.get('inner',[]))]
 if len(own)!=1:raise Unsupported('unique_own_method')
 f=own[0];body=next(n for n in f['inner'] if n.get('kind')=='CompoundStmt')
 if f['type']['qualType']!='size_t (int, int) __attribute__((thiscall))':raise Unsupported('method_type')
 params=[n for n in f['inner'] if n.get('kind')=='ParmVarDecl']
 if [(n.get('name'),n['type']['qualType']) for n in params]!=[('param_2','int'),('param_3','int')]:raise Unsupported('parameters')
 def span(n):
  if any('spellingLoc'in p or 'expansionLoc'in p for p in n.get('range',{}).values()):raise Unsupported('macro')
  p=m.fix.offsets(n)
  if not p or not 0<=p[0]<p[1]<=len(raw):raise Unsupported('span')
  return p
 for n in [f]+list(m.fix.walk(body)):
  if 'range'in n:span(n)
 a,b=span(body);text=raw[a:b].decode();compact=re.sub(r'\s+','',text)
 pattern=r'\{intiVar1;size_t_Size;\*\(int\*\)\(param_2\+0x28cc\)=\*\(int\*\)\(param_2\+0x28cc\)\+param_3;iVar1=\*\(int\*\)\(param_2\+0x28cc\);_Size=0x1000;if\(\(\(iVar1\+0x1000<=\*\(int\*\)\(param_2\+0x28d0\)\)\|\|\(_Size=\*\(int\*\)\(param_2\+0x28d0\)-iVar1,-1<\(int\)_Size\)\)&&\(\*\(int\*\)\(\(\(int\)this\)\+0x28fc\)!=0\)\)\{if\(_Size==0\)\{return0;\}fn_([0-9a-f]{8})\(\(void\*\)\(\*\(int\*\)\(param_2\+0x28c8\)\*0x1000\+0x8c8\+param_2\),\(void\*\)\(\*\(int\*\)\(\(\(int\)this\)\+0x28fc\)\+iVar1\),_Size\);\}return_Size;\}'
 match=re.fullmatch(pattern,compact)
 if not match:raise Unsupported('complete_retained_body_shape')
 callee=match.group(1);reader=g.Original(original);va=reader.pe.image_base+rva
 markers=re.findall(r'^// FUNCTION: DAO (0x[0-9a-fA-F]+)$',source,re.M)
 if markers!=[f'0x{va:08x}']:raise Unsupported('unique_source_marker')
 decl='extern "C" void * __cdecl fn_'+callee+'(void * _Dst, void * _Src, size_t _Size);'
 if source.count(decl)!=1 or source.index(decl)>=span(f)[0]:raise Unsupported('callee_declaration')
 spec=bound['requested'].get(str(rva),bound['requested'].get(rva))
 if not spec or len(spec['ranges'])!=1 or spec['ranges'][0]['start_rva']!=rva:raise Unsupported('original_range')
 ran=spec['ranges'][0];code=reader.read(va,ran['end_rva_inclusive']-rva+1,True)
 if len(code)!=109 or sha(code)!=spec['bytes_sha256'] or sha(code)!=ran['bytes_sha256']:raise Unsupported('original_range_hash')
 xs=list(capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32).disasm(code,va))
 expected=[('mov','eax, dword ptr [esp + 4]'),('mov','edx, dword ptr [esp + 8]'),('add','dword ptr [eax + 0x28cc], edx'),('mov','edx, dword ptr [eax + 0x28d0]'),('push','ebx'),('push','esi'),('push','edi'),('mov','edi, dword ptr [eax + 0x28cc]'),('lea','ebx, [edi + 0x1000]'),('cmp','ebx, edx'),('mov','esi, 0x1000'),('jle',hex(va+50)),('sub','edx, edi'),('mov','esi, edx'),('js',hex(va+101)),('mov','ecx, dword ptr [ecx + 0x28fc]'),('test','ecx, ecx'),('je',hex(va+101)),('test','esi, esi'),('jne',hex(va+72)),('pop','edi'),('pop','esi'),('xor','eax, eax'),('pop','ebx'),('ret','8'),('add','ecx, edi'),('push','esi'),('push','ecx'),('mov','ecx, dword ptr [eax + 0x28c8]'),('shl','ecx, 0xc'),('lea','edx, [ecx + eax + 0x8c8]'),('push','edx'),('call',hex(reader.pe.image_base+int(callee,16))),('add','esp, 0xc'),('pop','edi'),('mov','eax, esi'),('pop','esi'),('pop','ebx'),('ret','8')]
 if sum(x.size for x in xs)!=109 or [(x.mnemonic,x.op_str) for x in xs]!=expected:raise Unsupported('complete_original_instruction_profile')
 # Reuse the separately tested signed32 predicate identity before restructuring.
 _,predicate=zero_rewrite(source,ast,bound)
 new='{\n  int iVar1;\n  size_t _Size;\n  \n  *(uint *)((uint)param_2 + 0x28ccu) = *(uint *)((uint)param_2 + 0x28ccu) + (uint)param_3;\n  iVar1 = *(int *)((uint)param_2 + 0x28ccu);\n  _Size = 0x1000;\n  if ((int)((uint)iVar1 + 0x1000u) > *(int *)((uint)param_2 + 0x28d0u)) {\n    _Size = *(uint *)((uint)param_2 + 0x28d0u) - (uint)iVar1;\n    if ((int)_Size < 0) return _Size;\n  }\n  if (*(uint *)((uint)this + 0x28fcu) != 0) {\n    if (_Size == 0) {\n      return 0;\n    }\n    fn_{callee}((void *)(*(uint *)((uint)param_2 + 0x28c8u) * 0x1000u + 0x8c8u + (uint)param_2),\n            (void *)(*(uint *)((uint)this + 0x28fcu) + (uint)iVar1),_Size);\n  }\n  return _Size;\n}'.replace('{callee}',callee)
 candidate=raw[:a]+new.encode()+raw[b:]
 return candidate.decode(),dict(rva=rva,source_sha256=sha(raw),candidate_sha256=sha(candidate),original_sha256=sha(original),original_range_sha256=sha(code),original_instructions=len(xs),predicate=predicate,callee_rva=int(callee,16),arithmetic='unsigned32 additions/multiply/subtract with explicit target signed reinterpretations',hypothesis_only=True,unknowns=['copy-call formal semantics','nominal object and buffer extents'],acceptance='unchanged complete relocation-aware comparator only')

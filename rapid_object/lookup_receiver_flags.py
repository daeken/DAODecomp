"""Byte-backed call-context and narrow flag-extraction source hypothesis.

This bounded retained-body rule restores observed ECX inputs and spells three
flag tests at their observed byte width. Callee semantics remain unknown; only
the unchanged complete object comparator can accept compiled C++.
"""
import json,re
import capstone
from . import ast_match as m,eh_graph as g
from .conditional_construction import Unsupported,sha

_ECX_WRITES={capstone.x86.X86_REG_ECX,capstone.x86.X86_REG_CX,capstone.x86.X86_REG_CL,capstone.x86.X86_REG_CH}

def capture(reader,entry,cleanup):
 ranges=entry['body_ranges'];by={};hashes=[]
 if not ranges or ranges[0]['start_rva']!=entry['rva']:raise Unsupported('callee_ranges')
 md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);md.detail=True
 for r in ranges:
  va=reader.pe.image_base+r['start_rva'];raw=reader.read(va,r['end_rva_inclusive']-r['start_rva']+1,True);xs=list(md.disasm(raw,va))
  if not xs or sum(x.size for x in xs)!=len(raw) or any(x.address in by for x in xs):raise Unsupported('callee_decode_or_overlap')
  by.update((x.address,x) for x in xs);hashes.append(dict(start_rva=r['start_rva'],end_rva_inclusive=r['end_rva_inclusive'],bytes_sha256=sha(raw)))
 pc=reader.pe.image_base+entry['rva'];context=None;prefix_seen=set()
 while pc in by and pc not in prefix_seen:
  prefix_seen.add(pc);x=by[pc];reads,writes=x.regs_access()
  if x.mnemonic=='call':context='unwritten_ECX_forwarded_to_unknown_nested_call';break
  if x.mnemonic.startswith('j') or _ECX_WRITES.intersection(writes):break
  if any(o.type==capstone.x86.X86_OP_MEM and o.mem.base==capstone.x86.X86_REG_ECX for o in x.operands):context='direct_original_ECX_memory_operand_before_clobber';break
  if x.mnemonic=='mov' and len(x.operands)==2 and x.operands[1].type==capstone.x86.X86_OP_REG and x.operands[1].reg==capstone.x86.X86_REG_ECX:context='fullword_original_ECX_copy_before_clobber';break
  pc+=x.size
 if context is None:raise Unsupported('callee_ECX_context_unknown')
 seen=set();todo=[reader.pe.image_base+entry['rva']];returns=[];calls=[]
 branch={'jmp','je','jne','js','jns','ja','jae','jb','jbe','jg','jge','jl','jle','jo','jno','jp','jnp'}
 while todo:
  pc=todo.pop()
  if pc in seen:continue
  if pc not in by:raise Unsupported('callee_CFG_boundary')
  seen.add(pc);x=by[pc];n=x.mnemonic
  if n=='ret':
   returns.append(0 if not x.operands else x.operands[0].imm if len(x.operands)==1 and x.operands[0].type==capstone.x86.X86_OP_IMM else -1);continue
  if any(x.group(k) for k in [1,2,3,4,5,7]) and n not in branch|{'call'}:raise Unsupported('callee_control')
  if n=='call':
   if len(x.operands)!=1 or x.operands[0].type!=capstone.x86.X86_OP_IMM:raise Unsupported('callee_indirect_call')
   reader.read(x.operands[0].imm,1,True);calls.append(x.operands[0].imm)
  if n in branch:
   if len(x.operands)!=1 or x.operands[0].type!=capstone.x86.X86_OP_IMM:raise Unsupported('callee_branch')
   todo.append(x.operands[0].imm)
  if n!='jmp':todo.append(pc+x.size)
 if seen!=set(by) or not returns or set(returns)!={cleanup}:raise Unsupported('callee_complete_cleanup')
 return dict(rva=entry['rva'],ranges=hashes,instructions=len(by),return_cleanup_bytes=cleanup,ECX_context=context,nested_calls=calls,formal_semantics='unknown; register context is an observation, not a callee contract')

def propose(source,ast,rva,bound,original,inventory):
 raw=source.encode()
 if not source.isascii() or sha(raw)!=bound.get('source_sha256') or sha(original)!=bound.get('module_sha256'):raise Unsupported('source_or_original_binding')
 nodes=list(m.fix.walk(ast))
 if any(n.get('isInvalid') or n.get('kind') in ('RecoveryExpr','UnresolvedLookupExpr') for n in nodes):raise Unsupported('incomplete_AST')
 consumed=[n for n in nodes if n.get('kind')=='TypedefDecl' and n.get('name')=='uint']
 if len(consumed)!=1 or consumed[0]['type']['qualType']!='unsigned int':raise Unsupported('consumed_type_uint')
 consumed=[n for n in nodes if n.get('kind')=='TypedefDecl' and n.get('name')=='undefined4']
 if len(consumed)!=1 or consumed[0]['type']['qualType']!='unsigned int':raise Unsupported('consumed_type_undefined4')
 consumed=[n for n in nodes if n.get('kind')=='TypedefDecl' and n.get('name')=='undefined1']
 if len(consumed)!=1 or consumed[0]['type']['qualType']!='unsigned char':raise Unsupported('consumed_type_undefined1')
 own=[n for n in nodes if n.get('kind')=='CXXMethodDecl' and n.get('name')=='fn_%08x'%rva and any(c.get('kind')=='CompoundStmt' for c in n.get('inner',[]))]
 if len(own)!=1:raise Unsupported('unique_own_method')
 f=own[0];body=next(n for n in f['inner'] if n.get('kind')=='CompoundStmt')
 def span(n):
  if any('spellingLoc'in p or 'expansionLoc'in p for p in n.get('range',{}).values()):raise Unsupported('macro')
  p=m.fix.offsets(n)
  if not p or not 0<=p[0]<p[1]<=len(raw):raise Unsupported('span')
  return p
 for n in [f]+list(m.fix.walk(body)):
  if 'range'in n:span(n)
 def text(n):a,b=span(n);return raw[a:b].decode()
 compact=re.sub(r'\s+','',text(body));pat=r'\{uintuVar1;intiVar2;undefined1local_10\[16\];fn_([0-9a-f]{8})\(local_10,\*\(undefined4\*\)\(\(\(int\)this\)\+8\)\);iVar2=fn_([0-9a-f]{8})\(param_2\);if\(\(\(\(iVar2!=0\)&&\(uVar1=\*\(uint\*\)\(iVar2\+4\),-1<\(int\)uVar1\)\)&&\(\(uVar1>>0x1d&1\)==0\)\)&&\(\(\(uVar1>>0x1e&1\)==0&&\(\(uVar1&0xffff\)==5\)\)\)\)\{fn_([0-9a-f]{8})\(\*\(int\*\)\(iVar2\+8\)\+\*\(int\*\)\(\(\(int\)this\)\+4\),param_3\);\}return;\}'
 match=re.fullmatch(pat,compact)
 if not match:raise Unsupported('complete_retained_body_shape')
 names=list(match.groups());params=[n for n in f['inner'] if n.get('kind')=='ParmVarDecl']
 if [(n.get('name'),n['type'].get('desugaredQualType')) for n in params]!=[('param_2','unsigned int'),('param_3','unsigned int')]:raise Unsupported('parameters')
 if f['type']['qualType']!='void (undefined4, undefined4) __attribute__((thiscall))':raise Unsupported('method_type')
 byte=[n for n in nodes if n.get('kind')=='TypedefDecl' and n.get('name')=='byte']
 if len(byte)!=1 or byte[0]['type']['qualType']!='unsigned char':raise Unsupported('unsigned_byte_type')
 reader=g.Original(original);va=reader.pe.image_base+rva;spec=bound['requested'].get(str(rva),bound['requested'].get(rva))
 if not spec or len(spec['ranges'])!=1 or spec['ranges'][0]['start_rva']!=rva:raise Unsupported('original_range')
 ran=spec['ranges'][0];code=reader.read(va,ran['end_rva_inclusive']-rva+1,True)
 if len(code)!=109 or sha(code)!=spec['bytes_sha256'] or sha(code)!=ran['bytes_sha256']:raise Unsupported('original_range_hash')
 xs=list(capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32).disasm(code,va));dest=hex(va+102)
 expected=[('sub','esp, 0x10'),('push','esi'),('mov','esi, ecx'),('mov','eax, dword ptr [esi + 8]'),('mov','edx, dword ptr [esi]'),('push','eax'),('lea','ecx, [esp + 8]'),('push','ecx'),('mov','ecx, dword ptr [edx]'),('call',hex(reader.pe.image_base+int(names[0],16))),('mov','eax, dword ptr [esp + 0x18]'),('push','eax'),('lea','ecx, [esp + 8]'),('call',hex(reader.pe.image_base+int(names[1],16))),('test','eax, eax'),('je',dest),('mov','ecx, dword ptr [eax + 4]'),('mov','edx, ecx'),('shr','edx, 0x1f'),('test','dl, 1'),('jne',dest),('mov','edx, ecx'),('shr','edx, 0x1d'),('test','dl, 1'),('jne',dest),('mov','edx, ecx'),('shr','edx, 0x1e'),('test','dl, 1'),('jne',dest),('movzx','ecx, cx'),('cmp','ecx, 5'),('jne',dest),('mov','eax, dword ptr [eax + 8]'),('mov','edx, dword ptr [esp + 0x1c]'),('add','eax, dword ptr [esi + 4]'),('mov','ecx, dword ptr [esi]'),('push','edx'),('push','eax'),('call',hex(reader.pe.image_base+int(names[2],16))),('pop','esi'),('add','esp, 0x10'),('ret','8')]
 if sum(x.size for x in xs)!=109 or [(x.mnemonic,x.op_str) for x in xs]!=expected:raise Unsupported('complete_original_instruction_profile')
 inv=json.loads(inventory)
 if inv['module_sha256']!=sha(original) or inv['image_base']!=reader.pe.image_base:raise Unsupported('inventory_binding')
 entries={}
 for e in inv['functions']:
  if e['rva'] in entries:raise Unsupported('duplicate_inventory_identity')
  entries[e['rva']]=e
 captures=[capture(reader,entries[int(n,16)],c) for n,c in zip(names,[8,4,8])]
 calls=[n for n in m.fix.walk(body) if n.get('kind')=='CallExpr']
 if len(calls)!=3:raise Unsupported('three_calls')
 expected_calls=['fn_'+names[0]+'(local_10,*(undefined4*)(((int)this)+8))','fn_'+names[1]+'(param_2)','fn_'+names[2]+'(*(int*)(iVar2+8)+*(int*)(((int)this)+4),param_3)']
 replacements=['((unsigned int(__thiscall*)(void*,void*,unsigned int))&fn_'+names[0]+')((void*)**(unsigned int**)this,local_10,*(undefined4 *)(((int)this) + 8))','((unsigned int(__thiscall*)(void*,unsigned int))&fn_'+names[1]+')(local_10,param_2)','((unsigned int(__thiscall*)(void*,unsigned int,unsigned int))&fn_'+names[2]+')(*(void**)this,*(uint *)(iVar2 + 8) + *(uint *)(((int)this) + 4),param_3)']
 edits=[]
 for n,old,new in zip(calls,expected_calls,replacements):
  if re.sub(r'\s+','',text(n))!=old:raise Unsupported('call_identity_or_arguments')
  a,b=span(n);edits.append((a,b,new))
 for old,new in [('-1<(int)uVar1','(((byte)(uVar1 >> 0x1f) & 1) == 0)'),('uVar1>>0x1d&1','(byte)(uVar1 >> 0x1d) & 1'),('uVar1>>0x1e&1','(byte)(uVar1 >> 0x1e) & 1')]:
  found=[n for n in m.fix.walk(body) if n.get('kind')=='BinaryOperator' and re.sub(r'\s+','',text(n))==old]
  if len(found)!=1:raise Unsupported('unique_flag_expression')
  a,b=span(found[0]);edits.append((a,b,new))
 for n in set(names):
  found=list(re.finditer(r'extern "C" unsigned int __cdecl fn_'+n+r'\(\.\.\.\);',source))
  if len(found)!=1 or found[0].start()>=span(f)[0]:raise Unsupported('callee_declaration')
  edits.append((found[0].start(),found[0].start()+len('extern "C" '),''))
 candidate=raw
 for a,b,t in sorted(edits,reverse=True):candidate=candidate[:a]+t.encode()+candidate[b:]
 return candidate.decode(),dict(rva=rva,source_sha256=sha(raw),candidate_sha256=sha(candidate),original_sha256=sha(original),original_range_sha256=sha(code),inventory_sha256=sha(inventory),original_instructions=len(xs),callees=captures,byte_tests=[31,29,30],arithmetic='explicit unsigned32 final address add',hypothesis_only=True,unknowns=['callee and nested-call formal semantics','nominal local16 type and object-field layouts'],preserved='source explicit arguments and null/type tests; original byte-observed receiver values, extraction widths and32bit wrap')

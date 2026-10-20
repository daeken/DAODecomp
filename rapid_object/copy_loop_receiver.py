"""Restore byte-observed receivers in a bounded bulk-copy source hypothesis.

No callee implementation is supplied. Complete original caller/callee ranges and
source spans support the proposal; only the unchanged full object checker accepts.
The retained Ghidra names and 32-bit loop layout are explicit scope limits.
"""
import json,re
import capstone
from . import ast_match as m,eh_graph as g
from .conditional_construction import sha,Unsupported

_ECX_WRITES={capstone.x86.X86_REG_ECX,capstone.x86.X86_REG_CX,capstone.x86.X86_REG_CL,capstone.x86.X86_REG_CH}

def callee_capture(reader,entry,cleanup):
 ranges=entry['body_ranges']
 if len(ranges)!=1 or ranges[0]['start_rva']!=entry['rva']:raise Unsupported('callee_range')
 va=reader.pe.image_base+entry['rva'];raw=reader.read(va,ranges[0]['end_rva_inclusive']-entry['rva']+1,True)
 md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);md.detail=True;xs=list(md.disasm(raw,va));by={x.address:x for x in xs}
 if not xs or sum(x.size for x in xs)!=len(raw):raise Unsupported('callee_decode')
 # The complete straight-line entry must consume incoming ECX before a write,
 # call or branch; no speculative propagation through an unknown call.
 live=False
 for x in xs:
  reads,writes=x.regs_access()
  if _ECX_WRITES.intersection(writes) or x.mnemonic=='call' or x.mnemonic.startswith('j'):break
  if capstone.x86.X86_REG_ECX in reads:
   ops=x.operands
   live=(x.mnemonic=='mov' and len(ops)==2 and all(o.type==capstone.x86.X86_OP_REG and o.size==4 for o in ops) and ops[1].reg==capstone.x86.X86_REG_ECX and ops[0].reg!=capstone.x86.X86_REG_ECX)
   break
 if not live:raise Unsupported('callee_receiver_livein')
 seen=set();todo=[va];returns=[]
 while todo:
  pc=todo.pop()
  if pc in seen:continue
  if pc not in by:raise Unsupported('callee_CFG_boundary')
  seen.add(pc);x=by[pc];n=x.mnemonic
  if n=='ret':
   value=0 if not x.operands else x.operands[0].imm if len(x.operands)==1 and x.operands[0].type==capstone.x86.X86_OP_IMM else -1
   returns.append(value);continue
  if any(x.group(k) for k in [1,2,3,4,5,7]) and n not in ('call','jmp','je','jne','jbe'):raise Unsupported('callee_control')
  if n=='call' and (len(x.operands)!=1 or x.operands[0].type!=capstone.x86.X86_OP_IMM):raise Unsupported('callee_indirect_call')
  if n.startswith('j'):
   if len(x.operands)!=1 or x.operands[0].type!=capstone.x86.X86_OP_IMM:raise Unsupported('callee_branch')
   todo.append(x.operands[0].imm)
  if n!='jmp':todo.append(pc+x.size)
 if seen!=set(by) or not returns or set(returns)!={cleanup}:raise Unsupported('callee_complete_cleanup')
 return dict(rva=entry['rva'],bytes_sha256=sha(raw),bytes=len(raw),receiver='incoming_ECX_before_write_or_transfer',return_cleanup_bytes=cleanup,CFG_instructions=len(xs),formal_semantics='unknown; nested call implementations remain external')

def propose(source,ast,rva,bound,original,inventory):
 raw=source.encode()
 if not source.isascii() or sha(raw)!=bound.get('source_sha256') or sha(original)!=bound.get('module_sha256'):raise Unsupported('source_or_original_binding')
 nodes=list(m.fix.walk(ast))
 if any(n.get('isInvalid') or n.get('kind') in ('RecoveryExpr','UnresolvedLookupExpr') for n in nodes):raise Unsupported('incomplete_AST')
 consumed=[n for n in nodes if n.get('kind')=='TypedefDecl' and n.get('name')=='uint']
 if len(consumed)!=1 or consumed[0]['type']['qualType']!='unsigned int':raise Unsupported('consumed_type_uint')
 consumed=[n for n in nodes if n.get('kind')=='TypedefDecl' and n.get('name')=='undefined4']
 if len(consumed)!=1 or consumed[0]['type']['qualType']!='unsigned int':raise Unsupported('consumed_type_undefined4')
 own=[n for n in nodes if n.get('kind')=='FunctionDecl' and n.get('name')=='fn_%08x'%rva and any(c.get('kind')=='CompoundStmt' for c in n.get('inner',[]))]
 if len(own)!=1:raise Unsupported('unique_own_function')
 f=own[0];body=next(n for n in f['inner'] if n.get('kind')=='CompoundStmt')
 def span(n):
  if any('spellingLoc'in p or 'expansionLoc'in p for p in n.get('range',{}).values()):raise Unsupported('macro')
  p=m.fix.offsets(n)
  if not p or not 0<=p[0]<p[1]<=len(raw):raise Unsupported('span')
  return p
 for n in [f]+list(m.fix.walk(body)):
  if 'range'in n:span(n)
 def text(n):a,b=span(n);return raw[a:b].decode()
 params=[n for n in f['inner'] if n.get('kind')=='ParmVarDecl']
 if f['type']['qualType']!='int *(int *, undefined4 *, undefined4 *, int)':raise Unsupported('function_type')
 if [(n.get('name'),n['type']['qualType']) for n in params]!=[('param_1','int *'),('param_2','undefined4 *'),('param_3','undefined4 *'),('param_4','int')]:raise Unsupported('signature')
 pat=r'\{undefined4\*puVar1;\*param_1=param_4;for\(;param_2!=param_3;param_2=param_2\+0x22\)\{puVar1=\(undefined4\*\)\*param_1;if\(puVar1!=\(undefined4\*\)0x0\)\{\*puVar1=0;puVar1\[1\]=0;puVar1\[2\]=0;fn_([0-9a-f]{8})\(param_2\+3\);fn_([0-9a-f]{8})\(\*param_2,param_2\[1\]\);fn_([0-9a-f]{8})\(param_2\+4\);\}\*param_1=\*param_1\+0x88;\}returnparam_1;\}'
 match=re.fullmatch(pat,re.sub(r'\s+','',text(body)))
 if not match:raise Unsupported('complete_retained_body_shape')
 names=list(match.groups());reader=g.Original(original);va=reader.pe.image_base+rva;spec=bound['requested'].get(str(rva),bound['requested'].get(rva))
 if not spec or len(spec['ranges'])!=1 or spec['ranges'][0]['start_rva']!=rva:raise Unsupported('original_range')
 ran=spec['ranges'][0];code=reader.read(va,ran['end_rva_inclusive']-rva+1,True)
 if len(code)!=109 or sha(code)!=spec['bytes_sha256'] or sha(code)!=ran['bytes_sha256']:raise Unsupported('original_range_hash')
 xs=list(capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32).disasm(code,va))
 expected=[('mov','eax, dword ptr [esp + 0x10]'),('push','ebx'),('mov','ebx, dword ptr [esp + 8]'),('push','ebp'),('mov','ebp, dword ptr [esp + 0x14]'),('push','edi'),('mov','edi, dword ptr [esp + 0x14]'),('cmp','edi, ebp'),('mov','dword ptr [ebx], eax'),('je',hex(va+103)),('push','esi'),('lea','ebx, [ebx]'),('mov','esi, dword ptr [ebx]'),('xor','eax, eax'),('cmp','esi, eax'),('je',hex(va+86)),('lea','ecx, [edi + 0xc]'),('push','ecx'),('lea','ecx, [esi + 0xc]'),('mov','dword ptr [esi], eax'),('mov','dword ptr [esi + 4], eax'),('mov','dword ptr [esi + 8], eax'),('call',hex(reader.pe.image_base+int(names[0],16))),('mov','edx, dword ptr [edi + 4]'),('mov','eax, dword ptr [edi]'),('push','edx'),('push','eax'),('mov','ecx, esi'),('call',hex(reader.pe.image_base+int(names[1],16))),('lea','ecx, [edi + 0x10]'),('push','ecx'),('lea','ecx, [esi + 0x10]'),('call',hex(reader.pe.image_base+int(names[2],16))),('add','dword ptr [ebx], 0x88'),('add','edi, 0x88'),('cmp','edi, ebp'),('jne',hex(va+32)),('pop','esi'),('pop','edi'),('pop','ebp'),('mov','eax, ebx'),('pop','ebx'),('ret','')]
 if sum(x.size for x in xs)!=109 or [(x.mnemonic,x.op_str) for x in xs]!=expected:raise Unsupported('complete_original_instruction_profile')
 inv=json.loads(inventory)
 if inv['module_sha256']!=sha(original) or inv['image_base']!=reader.pe.image_base:raise Unsupported('inventory_binding')
 entries={}
 for e in inv['functions']:
  if e['rva'] in entries:raise Unsupported('duplicate_inventory_identity')
  entries[e['rva']]=e
 captures=[callee_capture(reader,entries[int(n,16)],c) for n,c in zip(names,[4,8,4])]
 calls=[n for n in m.fix.walk(body) if n.get('kind')=='CallExpr']
 expressions=['param_2 + 3','*param_2,param_2[1]','param_2 + 4'];receivers=['puVar1 + 3','puVar1','puVar1 + 4'];types=['void*,void*','void*,unsigned int,unsigned int','void*,void*'];edits=[]
 if len(calls)!=3:raise Unsupported('three_calls')
 for node,n,arg,recv,typ in zip(calls,names,expressions,receivers,types):
  if re.sub(r'\s+','',text(node))!='fn_'+n+'('+arg.replace(' ','')+')':raise Unsupported('call_identity_or_arguments')
  a,b=span(node);edits.append((a,b,'((unsigned int(__thiscall*)('+typ+'))&fn_'+n+')('+recv+','+arg+')'))
 advances=[n for n in m.fix.walk(body) if n.get('kind')=='BinaryOperator' and n.get('opcode')=='=' and re.sub(r'\s+','',text(n))=='*param_1=*param_1+0x88']
 if len(advances)!=1:raise Unsupported('unique_destination_advance')
 a,b=span(advances[0]);edits.append((a,b,'*param_1 = (int)((uint)*param_1 + 0x88u)'))
 for n in set(names):
  pattern=r'extern "C" unsigned int __cdecl fn_'+n+r'\(\.\.\.\);';found=list(re.finditer(pattern,source))
  if len(found)!=1 or found[0].start()>=span(f)[0]:raise Unsupported('callee_declaration')
  edits.append((found[0].start(),found[0].start()+len('extern "C" '),''))
 candidate=raw
 for a,b,t in sorted(edits,reverse=True):candidate=candidate[:a]+t.encode()+candidate[b:]
 return candidate.decode(),dict(rva=rva,source_sha256=sha(raw),candidate_sha256=sha(candidate),original_sha256=sha(original),original_range_sha256=sha(code),inventory_sha256=sha(inventory),original_instructions=len(xs),callees=captures,hypothesis_only=True,preserved='all existing source arguments, zero stores, null guard, loop stride, destination advance and return; only byte-observed receiver/calling-convention inputs restored')

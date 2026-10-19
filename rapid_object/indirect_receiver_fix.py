"""AST-bound indirect receiver hypothesis. No semantic-preservation assertion.
Only a complete unchanged comparator match can validate generated machine code.
"""
import re
from rapid_object import ast_match as m
from capstone import Cs,CS_ARCH_X86,CS_MODE_32,CS_GRP_JUMP,CS_GRP_CALL
from capstone.x86 import X86_OP_REG,X86_OP_MEM,X86_OP_IMM

class Unsupported(ValueError):pass

def add(x,n):
 n&=0xffffffff
 if n==0:return x
 if x[0]=='const':return ('const',(x[1]+n)&0xffffffff)
 if x[0]=='add':return add(x[1],x[2]+n)
 return ('add',x,n)

def strip(n):
 while n.get('kind') in ('ImplicitCastExpr','ParenExpr','CStyleCastExpr') and len(n.get('inner',[]))==1:n=n['inner'][0]
 return n

def unknown(x):return x==('unknown',) or isinstance(x,tuple) and any(unknown(v) for v in x)

def original_edge(function):
 data=bytes.fromhex(function['original_bytes_hex']);md=Cs(CS_ARCH_X86,CS_MODE_32);md.detail=True;ins=list(md.disasm(data,function['original_va']))
 if sum(i.size for i in ins)!=len(data):raise Unsupported('incomplete_decode')
 edges=[i for i in ins if (i.group(CS_GRP_CALL) or i.mnemonic=='jmp') and i.operands and i.operands[0].type!=X86_OP_IMM]
 if len(edges)!=1:raise Unsupported('not_one_indirect_edge')
 edge=edges[0];regs={r:('entry',r) for r in ('eax','ecx','edx','ebx','esi','edi','ebp','esp')};writes=[]
 def address(op):
  mm=op.mem
  if mm.segment or mm.index:raise Unsupported('segmented_or_indexed_prefix')
  if mm.base and md.reg_name(mm.base)=='esp':raise Unsupported('stack_based_receiver_prefix')
  return add(regs[md.reg_name(mm.base)] if mm.base else ('const',0),mm.disp)
 def value(op):
  if op.size!=4:return ('unknown',)
  if op.type==X86_OP_REG:return regs.get(md.reg_name(op.reg),('unknown',))
  if op.type==X86_OP_MEM:return ('load',address(op))
  if op.type==X86_OP_IMM:return ('const',op.imm&0xffffffff)
  return ('unknown',)
 for i in ins:
  if i.address==edge.address:
   target=value(i.operands[0]);receiver=regs['ecx']
   if unknown(target) or unknown(receiver):raise Unsupported('unknown_edge_inputs')
   # Demand the observed target itself is loaded through this receiver's vtable.
   if target[0]!='load':raise Unsupported('not_pointer_loaded_target')
   table=target[1];slot=0
   if table[0]=='add':table,slot=table[1],table[2]
   if table!=('load',receiver) or slot%4:raise Unsupported('target_not_receiver_vtable_slot')
   return {'edge_va':edge.address,'edge_kind':edge.mnemonic,'receiver':receiver,'target':target,'slot':slot,'prefix_instructions':[(x.address,x.bytes.hex(),x.mnemonic,x.op_str) for x in ins if x.address<edge.address],'register_state':regs,'unknown_formal_stack_arguments':True,'unknown_callee_semantics':True,'edx_livein_not_inferred':True}
  ops=i.operands
  if i.group(CS_GRP_CALL) or i.group(CS_GRP_JUMP):raise Unsupported('nonlinear_or_earlier_call_prefix')
  if i.mnemonic=='mov' and len(ops)==2 and ops[0].type==X86_OP_REG and ops[0].size==4:
   regs[md.reg_name(ops[0].reg)]=value(ops[1])
  elif i.mnemonic=='lea' and len(ops)==2 and ops[0].type==X86_OP_REG and ops[0].size==4:regs[md.reg_name(ops[0].reg)]=address(ops[1])
  elif i.mnemonic=='push' and len(ops)==1 and ops[0].type==X86_OP_REG and md.reg_name(ops[0].reg) in ('ebx','esi','edi','ebp'):pass
  elif i.mnemonic in ('nop','cmp','test'):pass
  else:raise Unsupported('unsupported_prefix_effect')
 raise Unsupported('edge_unreached')

def rewrite(source,ast,report):
 if not source.isascii():raise Unsupported('non_ascii_source')
 f=report['functions'][0];rva=f['rva'];raw=source.encode()
 own=[n for n in m.fix.walk(ast) if n.get('kind') in ('FunctionDecl','CXXMethodDecl') and n.get('name')==f'fn_{rva:08x}' and any(c.get('kind')=='CompoundStmt' for c in n.get('inner',[]))]
 if len(own)!=1:raise Unsupported('own_identity')
 own=own[0];aliases={n['name']:n['type']['qualType'] for n in m.fix.walk(ast) if n.get('kind')=='TypedefDecl'}
 if own.get('variadic'):raise Unsupported('variadic_own_function')
 params=[n for n in own.get('inner',[]) if n.get('kind')=='ParmVarDecl'];env={}
 if own['kind']=='CXXMethodDecl':
  if params:raise Unsupported('own_explicit_stack_parameters')
 elif params:
  if len(params)!=1 or 'fastcall' not in own['type']['qualType'] or m.fix.type_kind(params[0]['type']['qualType'],aliases) not in ('integer32','pointer'):raise Unsupported('unbound_entry_parameters')
  env[params[0]['id']]=('entry','ecx')
 for n in ast.get('inner',[]):
  for v in m.fix.walk(n):
   if v.get('kind')!='VarDecl' or not v.get('name','').startswith('g_'):continue
   name=v['name'];match=re.fullmatch('g_([0-9a-fA-F]{8})',name)
   if not match:continue
   addr=0x400000+int(match[1],16)
   if not any(addr==a and name in symbol for symbol,a in report['symbol_addresses'].items()):continue
   if m.fix.type_kind(v['type']['qualType'],aliases) in ('pointer','integer32'):env[v['id']]=('load',('const',addr))
 def expr(n):
  n=strip(n);k=n.get('kind');cs=n.get('inner',[])
  if k=='CXXThisExpr':return ('entry','ecx')
  if k=='DeclRefExpr':return env.get(n['referencedDecl']['id'],('unknown',))
  if k=='IntegerLiteral':return ('const',int(n['value'])&0xffffffff)
  if k=='UnaryOperator' and n.get('opcode')=='*' and len(cs)==1 and (m.fix.type_kind(n['type']['qualType'],aliases) in ('integer32','pointer') or n['type']['qualType'].rstrip().endswith('*')):return ('load',expr(cs[0]))
  if k=='BinaryOperator' and n.get('opcode') in ('+','-') and len(cs)==2:
   rhs=expr(cs[1]);lt=cs[0].get('type',{}).get('qualType','');scale=1
   if rhs[0]!='const':return ('unknown',)
   if m.fix.type_kind(lt,aliases)=='pointer':
    pointee=m.fix.canonical_type(lt,aliases).rstrip().removesuffix('*').strip()
    if m.fix.type_kind(pointee,aliases) not in ('integer32','pointer'):return ('unknown',)
    scale=4
   return add(expr(cs[0]),rhs[1]*scale*(1 if n['opcode']=='+' else -1))
  return ('unknown',)
 calls=[n for n in m.fix.walk(own) if n.get('kind')=='CallExpr']
 if len(calls)!=1:raise Unsupported('not_one_source_call')
 call=calls[0]
 if len(call.get('inner',[]))!=1 or call['type']['qualType']!='unsigned int':raise Unsupported('existing_call_arguments_or_return_not_supported')
 callee=strip(call['inner'][0])
 if callee.get('kind')!='UnaryOperator' or callee.get('opcode')!='*':raise Unsupported('not_indirect_function_dereference')
 pointer=callee['inner'][0];evidence=original_edge(f)
 if expr(pointer)!=evidence['target']:raise Unsupported('source_target_dataflow_disagrees')
 # Bind the receiver to an existing scalar AST subexpression of the same target.
 candidates=[]
 for n in m.fix.walk(pointer):
  if expr(n)==evidence['receiver'] and m.fix.type_kind(n.get('type',{}).get('qualType',''),aliases) in ('integer32','pointer'):
   span=m.fix.offsets(n)
   if span:candidates.append((span,n))
 spans=sorted(set(s for s,n in candidates),key=lambda s:(s[1]-s[0],s))
 if not spans:raise Unsupported('no_existing_ast_receiver')
 receiver_span=spans[0]
 if sum(s[1]-s[0]==receiver_span[1]-receiver_span[0] for s in spans)!=1:raise Unsupported('ambiguous_ast_receiver')
 if any(n.get('kind') in ('CallExpr','CXXMemberCallExpr','CompoundAssignOperator') or n.get('opcode') in ('++','--','=') or 'volatile' in n.get('type',{}).get('qualType','') for n in m.fix.walk(pointer)):raise Unsupported('effectful_or_volatile_target')
 for n in m.fix.walk(call):
  if any('expansionLoc' in loc or 'spellingLoc' in loc for loc in n.get('range',{}).values()):raise Unsupported('macro_source_span')
 span=m.fix.offsets(call);targetspan=m.fix.offsets(call['inner'][0])
 if not span or not targetspan or not span[0]<=targetspan[0]<targetspan[1]<=span[1] or not targetspan[0]<=receiver_span[0]<receiver_span[1]<=targetspan[1]:raise Unsupported('invalid_ast_spans')
 target=raw[targetspan[0]:targetspan[1]].decode();receiver=raw[receiver_span[0]:receiver_span[1]].decode()
 replacement='((unsigned int (__thiscall *)(void *))('+target+'))((void *)('+receiver+'))'
 changed=raw[:span[0]]+replacement.encode()+raw[span[1]:]
 return changed.decode(),{'kind':'observed_indirect_receiver_hypothesis','status':'UNVALIDATED','semantic_preservation_claim':False,'original_edge':evidence,'receiver_source':receiver,'target_source_unchanged':target,'span':span,'receiver_span':receiver_span,'before':raw[span[0]:span[1]].decode(),'replacement':replacement,'limits':'Unknown target formal stack/EDX inputs and semantics stay unknown. Existing return hypothesis retained. No acceptance without complete exact comparison.'}

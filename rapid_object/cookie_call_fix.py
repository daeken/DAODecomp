"""Byte-backed rejection of a spurious last cookie argument, not ABI inference.

Only first direct calls with a linear, completely decoded entry are supported.
The original cookie is proven stored before FS installation; all subsequently
pushed words belong to the observed call setup and are caller-cleaned. Unknown
callee formal types/semantics remain unknown. Exact comparison alone accepts.
"""
import re
from rapid_object import ast_match as m
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from capstone.x86 import X86_OP_REG,X86_OP_IMM,X86_OP_MEM,X86_REG_ESP,X86_REG_EAX,X86_REG_FS
class Unsupported(ValueError):pass

def evidence(f,cookie_va,delta):
 data=bytes.fromhex(f['original_bytes_hex']);md=Cs(CS_ARCH_X86,CS_MODE_32);md.detail=True;ins=list(md.disasm(data,f['original_va']))
 if sum(x.size for x in ins)!=len(data):raise Unsupported('incomplete_original_decode')
 sp=0;cookie_push=None;installed=None;args=[];site=None
 for j,i in enumerate(ins[:128]):
  ops=i.operands;n=i.mnemonic
  if n=='call':site=(j,i);break
  if i.group(1) or i.group(3) or n in ('enter','leave','int','ud2','hlt'):raise Unsupported('nonlinear_entry_before_first_call')
  if n=='push':
   if len(ops)!=1 or ops[0].size!=4 or 0x66 in i.prefix:raise Unsupported('nonword_push')
   if installed is not None:args.append(i)
   if j>=2:
    a,b=ins[j-2:j];ao,bo=a.operands,b.operands
    if a.mnemonic=='mov' and len(ao)==2 and ao[0].type==X86_OP_REG and ao[0].reg==X86_REG_EAX and ao[1].type==X86_OP_MEM and ao[1].size==4 and not ao[1].mem.base and not ao[1].mem.index and not ao[1].mem.segment and ao[1].mem.disp&0xffffffff==cookie_va and b.mnemonic=='xor' and len(bo)==2 and bo[0].type==bo[1].type==X86_OP_REG and bo[0].reg==X86_REG_EAX and bo[1].reg==X86_REG_ESP and ops[0].type==X86_OP_REG and ops[0].reg==X86_REG_EAX:
     if sp!=delta:raise Unsupported('cookie_entry_delta_disagrees')
     if cookie_push is not None:raise Unsupported('multiple_cookie_pushes')
     cookie_push=i.address
   sp-=4
  elif n=='sub' and len(ops)==2 and ops[0].type==X86_OP_REG and ops[0].reg==X86_REG_ESP and ops[1].type==X86_OP_IMM:
   if installed is not None:raise Unsupported('post_install_nonargument_allocation')
   sp-=ops[1].imm
  elif X86_REG_ESP in i.regs_access()[1]:raise Unsupported('unsupported_stack_mutation')
  if n=='mov' and len(ops)==2 and ops[0].type==X86_OP_MEM and ops[0].size==4 and ops[1].type==X86_OP_REG and ops[1].size==4 and ops[0].mem.segment==X86_REG_FS and not ops[0].mem.base and not ops[0].mem.index and ops[0].mem.disp==0:
   if installed is not None or cookie_push is None:raise Unsupported('unbound_FS_install')
   installed=i.address
 if site is None or installed is None or cookie_push is None:raise Unsupported('no_bound_cookie_first_call')
 j,i=site
 if [p.address for p in ins[j-len(args):j]] != [p.address for p in args]:raise Unsupported('noncontiguous_argument_pushes')
 if len(i.operands)!=1 or i.operands[0].type!=X86_OP_IMM or i.operands[0].size!=4 or any(i.prefix):raise Unsupported('first_call_not_direct')
 if not args:raise Unsupported('zero_stack_argument_subgroup_deferred')
 # Caller cleanup may follow a single non-stack MOV of the return value.
 tail=ins[j+1:j+3];cleanup=None
 for t in tail:
  op=t.operands
  if t.mnemonic=='add' and len(op)==2 and op[0].type==X86_OP_REG and op[0].reg==X86_REG_ESP and op[1].type==X86_OP_IMM:
   cleanup=op[1].imm;break
  if t.mnemonic!='mov' or X86_REG_ESP in t.regs_access()[1]:break
 if cleanup!=len(args)*4:raise Unsupported('argument_push_cleanup_not_balanced')
 return {'original_first_call_va':i.address,'target_va':i.operands[0].imm,'argument_pushes':[{'va':p.address,'instruction':p.mnemonic+' '+p.op_str} for p in args],'argument_count':len(args),'caller_cleanup_bytes':cleanup,'cookie_push_va':cookie_push,'FS_install_va':installed,'cookie_va':cookie_va,'entry_cookie_delta':delta,'callee_formal_contract':'unknown; observed setup only'}

def callee_profile(f):
 """Complete one-word forwarding wrapper; other implicit semantics stay unknown."""
 data=bytes.fromhex(f['original_bytes_hex']);md=Cs(CS_ARCH_X86,CS_MODE_32);md.detail=True;xs=list(md.disasm(data,f['original_va']))
 if sum(i.size for i in xs)!=len(data) or len(xs)!=6 or any(any(i.prefix) for i in xs):raise Unsupported('callee_not_complete_forwarding_wrapper')
 if [i.mnemonic for i in xs]!=['mov','push','push','call','add','ret']:raise Unsupported('callee_not_forwarding_wrapper')
 a,b,c,d,e,z=[i.operands for i in xs]
 if not (len(a)==2 and a[0].type==X86_OP_REG and a[0].reg==X86_REG_EAX and a[1].type==X86_OP_MEM and a[1].size==4 and a[1].mem.base==X86_REG_ESP and not a[1].mem.index and not a[1].mem.segment and a[1].mem.disp==4):raise Unsupported('callee_not_single_first_stack_word')
 if not (len(b)==1 and b[0].type==X86_OP_IMM and b[0].size==4 and len(c)==1 and c[0].type==X86_OP_REG and c[0].reg==X86_REG_EAX and c[0].size==4):raise Unsupported('callee_not_forwarding_word_and_constant')
 if not (len(d)==1 and d[0].type==X86_OP_IMM and len(e)==2 and e[0].type==X86_OP_REG and e[0].reg==X86_REG_ESP and e[1].type==X86_OP_IMM and e[1].imm==8 and not z):raise Unsupported('callee_cleanup_or_edge_unsupported')
 return {'va':f['original_va'],'body_sha256':m.sha(data),'body_bytes':len(data),'observed_entry_stack_word_reads':[4],'explicit_entry_register_liveins':['esp'],'nested_target_va':d[0].imm,'nested_explicit_stack_words':2,'return_cleanup_bytes':0,'formal_signature_inferred':False,'implicit_nested_semantics':'unknown'}

def strip(n):
 while n.get('kind') in ('ImplicitCastExpr','ParenExpr') and len(n.get('inner',[]))==1:n=n['inner'][0]
 return n

def rewrite(source,ast,report,callees):
 if not source.isascii() or ast.get('kind')!='TranslationUnitDecl' or len(report.get('functions',[]))!=1:raise Unsupported('source_ast_report_identity')
 nodes=list(m.fix.walk(ast))
 if any(n.get('kind') in ('RecoveryExpr','UnresolvedLookupExpr') or n.get('isInvalid') or n.get('containsErrors') for n in nodes):raise Unsupported('incomplete_ast')
 f=report['functions'][0];raw=source.encode();own=[n for n in nodes if n.get('kind')=='FunctionDecl' and n.get('name')==f"fn_{f['rva']:08x}" and any(c.get('kind')=='CompoundStmt' for c in n.get('inner',[]))]
 if len(own)!=1:raise Unsupported('stable_function_identity')
 loc=own[0].get('loc',{});off=loc.get('offset')
 if type(off) is not int or raw[off:off+len(own[0]['name'])].decode()!=own[0]['name'] or 'spellingLoc' in loc or 'expansionLoc' in loc:raise Unsupported('function_source_binding')
 body=next(c for c in own[0]['inner'] if c['kind']=='CompoundStmt');bn=list(m.fix.walk(body));aliases={n['name']:n['type']['qualType'] for n in nodes if n.get('kind')=='TypedefDecl'}
 if any('spellingLoc' in loc or 'expansionLoc' in loc for n in bn for loc in n.get('range',{}).values()):raise Unsupported('macro_source_span')
 # Exact existing frame-lowering spelling plus actual own VarDecl binding.
 pat=re.compile(r'(?m)^\s*(?P<v>\w+) = (?P<g>g_[0-9a-f]{8}) \^ \(\(unsigned int\)_AddressOfReturnAddress\(\) \+ 0x(?P<d>[0-9a-f]{8})u\);')
 matches=list(pat.finditer(source))
 if len(matches)!=1:raise Unsupported('not_single_cookie_assignment')
 match=matches[0];var=match['v'];decl=[n for n in bn if n.get('kind')=='VarDecl' and n.get('name')==var]
 if len(decl)!=1 or decl[0].get('init') or m.fix.canonical_type(decl[0]['type']['qualType'],aliases)!='unsigned int':raise Unsupported('cookie_not_unique_unsigned_local')
 did=decl[0]['id'];assigns=[n for n in bn if n.get('kind')=='BinaryOperator' and n.get('opcode')=='=' and n.get('inner') and strip(n['inner'][0]).get('referencedDecl',{}).get('id')==did]
 if len(assigns)!=1:raise Unsupported('cookie_mutation_or_missing_assignment')
 span=m.fix.offsets(assigns[0]);expected=match.group(0).strip()[:-1]
 if not span or raw[span[0]:span[1]].decode()!=expected:raise Unsupported('cookie_assignment_source_binding')
 gva=0x400000+int(match['g'][2:],16);symbolvals={a for n,a in report.get('symbol_addresses',{}).items() if re.search(r'(?:^|[?_])'+match['g']+r'(?=@|$)',n)}
 if symbolvals!={gva}:raise Unsupported('cookie_global_not_bound')
 topvars=[]
 for n in ast.get('inner',[]):
  topvars.extend(n.get('inner',[]) if n.get('kind')=='LinkageSpecDecl' else [n])
 globals_=[n for n in topvars if n.get('kind')=='VarDecl' and n.get('name')==match['g'] and not n.get('init') and n.get('storageClass')!='static']
 if len(globals_)!=1 or m.fix.canonical_type(globals_[0]['type']['qualType'],aliases)!='unsigned int':raise Unsupported('cookie_global_type_or_storage')
 greferences=[n for n in m.fix.walk(assigns[0]) if n.get('kind')=='DeclRefExpr' and n.get('referencedDecl',{}).get('name')==match['g']]
 if len(greferences)!=1 or greferences[0].get('referencedDecl',{}).get('id')!=globals_[0]['id']:raise Unsupported('cookie_global_decl_identity')
 delta=int(match['d'],16);delta=delta-(1<<32) if delta&(1<<31) else delta;proof=evidence(f,gva,delta)
 callee=callees.get(proof['target_va'])
 if callee is None:raise Unsupported('callee_body_not_bound')
 profile=callee_profile(callee)
 if profile['va']!=proof['target_va'] or proof['argument_count']!=1:raise Unsupported('callee_entry_argument_setup_disagrees')
 proof['callee_observation']=profile
 calls=[]
 for n in bn:
  if n.get('kind')=='CallExpr' and n.get('inner'):
   callee=strip(n['inner'][0]);name=callee.get('referencedDecl',{}).get('name','')
   if re.fullmatch(r'fn_[0-9a-f]{8}',name):calls.append((m.fix.offsets(n),n,name))
 calls.sort(key=lambda c:c[0] or (-1,-1))
 if not calls:raise Unsupported('no_direct_source_call')
 cspan,call,name=calls[0];args=call['inner'][1:]
 if not cspan or not re.match(re.escape(name)+r'\s*\(',raw[cspan[0]:cspan[1]].decode()):raise Unsupported('callee_source_binding')
 if proof['target_va']!=0x400000+int(name[3:],16):raise Unsupported('first_call_identity_disagrees')
 if len(args)!=proof['argument_count']+1:raise Unsupported('not_exactly_one_extra_argument')
 last=strip(args[-1])
 if last.get('kind')!='DeclRefExpr' or last.get('referencedDecl',{}).get('id')!=did:raise Unsupported('last_argument_not_bound_cookie')
 if not cspan or span[1]>=cspan[0]:raise Unsupported('cookie_not_initialized_before_call')
 # Call must be an ordinary top-level statement or a simple assignment RHS;
 # refuse introspection, unevaluated operands, conditional/nested call contexts.
 container=[n for n in body['inner'] if m.fix.offsets(n) and m.fix.offsets(n)[0]<=cspan[0] and m.fix.offsets(n)[1]>=cspan[1]]
 if len(container)!=1:raise Unsupported('not_direct_body_statement')
 n=container[0]
 if n.get('kind')=='BinaryOperator' and n.get('opcode')=='=' and len(n.get('inner',[]))==2:n=n['inner'][1]
 while n.get('kind') in ('ImplicitCastExpr','CStyleCastExpr','ParenExpr') and len(n.get('inner',[]))==1:n=n['inner'][0]
 if n is not call:raise Unsupported('nested_or_unevaluated_call')
 refs=[n for n in bn if n.get('kind')=='DeclRefExpr' and n.get('referencedDecl',{}).get('id')==did]
 if len(refs)!=2:raise Unsupported('additional_cookie_uses_deferred')
 aspans=[m.fix.offsets(a) for a in args]
 if any(x is None for x in aspans):raise Unsupported('argument_spans')
 a=aspans[-2][1];b=aspans[-1][1]
 if not re.fullmatch(r'\s*,\s*'+re.escape(var),raw[a:b].decode()):raise Unsupported('argument_source_binding')
 candidate=raw[:a]+raw[b:]
 return candidate.decode(),{'kind':'original_cookie_not_call_argument','status':'UNVALIDATED','source_edit':{'span':[a,b],'before':raw[a:b].decode(),'replacement':''},'original':proof,'source_call':name,'cookie_declaration_id':did,'source_sha256':m.sha(raw),'candidate_sha256':m.sha(candidate),'semantic_preservation_claim':False,'remaining_unknowns':['callee formal types/semantics','native SEH frame','unknown inputs and return/receiver conventions'],'acceptance':'unchanged complete relocation-aware comparator only'}

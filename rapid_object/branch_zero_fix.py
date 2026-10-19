"""Signed negative-one threshold spelling hypotheses, bound to actual AST spans.

For an already signed 32-bit integer, -1 < x and x >= 0 select the same
integer values. No acceptance or whole-function semantic proof is provided.
"""
import re
from rapid_object import ast_match as m
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from capstone.x86 import X86_OP_REG,X86_OP_IMM

class Unsupported(ValueError):pass

def strip(n):
 while n.get('kind') in ('ImplicitCastExpr','ParenExpr') and len(n.get('inner',[]))==1:n=n['inner'][0]
 return n

def minus_one(n):
 n=strip(n);cs=n.get('inner',[])
 return n.get('kind')=='UnaryOperator' and n.get('opcode')=='-' and len(cs)==1 and strip(cs[0]).get('kind')=='IntegerLiteral' and strip(cs[0]).get('value')=='1'

def zero_sign_evidence(f):
 data=bytes.fromhex(f['original_bytes_hex']);md=Cs(CS_ARCH_X86,CS_MODE_32);md.detail=True;ins=list(md.disasm(data,f['original_va']))
 if sum(i.size for i in ins)!=len(data):raise Unsupported('incomplete_original_decode')
 observations=[]
 for a,b in zip(ins,ins[1:]):
  ops=a.operands
  test=a.mnemonic=='test' and len(ops)==2 and ops[0].type==ops[1].type==X86_OP_REG and ops[0].reg==ops[1].reg and ops[0].size==4
  cmp=a.mnemonic=='cmp' and len(ops)==2 and ops[1].type==X86_OP_IMM and ops[1].imm==0 and ops[0].size==4
  if (test or cmp) and b.mnemonic in ('jl','jge','js','jns'):observations.append({'test_va':a.address,'test_bytes':a.bytes.hex(),'test':a.mnemonic+' '+a.op_str,'branch_va':b.address,'branch_bytes':b.bytes.hex(),'branch':b.mnemonic+' '+b.op_str})
 if not observations:raise Unsupported('no_original_signed_zero_branch_evidence')
 return observations

def rewrite(source,ast,report):
 if not source.isascii():raise Unsupported('non_ascii_source')
 if ast.get('kind')!='TranslationUnitDecl' or len(report.get('functions',[]))!=1:raise Unsupported('complete_ast_and_one_function_required')
 f=report['functions'][0];raw=source.encode();rva=f['rva'];nodes=list(m.fix.walk(ast));aliases={n['name']:n['type']['qualType'] for n in nodes if n.get('kind')=='TypedefDecl'}
 own=[n for n in nodes if n.get('kind') in ('FunctionDecl','CXXMethodDecl') and n.get('name')==f'fn_{rva:08x}' and any(x.get('kind')=='CompoundStmt' for x in n.get('inner',[]))]
 if len(own)!=1:raise Unsupported('stable_function_identity')
 observations=zero_sign_evidence(f);edits=[]
 for node in m.fix.walk(own[0]):
  if node.get('kind')!='BinaryOperator' or node.get('opcode') not in ('<','>','<=','>='):continue
  cs=node.get('inner',[])
  if len(cs)!=2:continue
  left,right=cs;op=node['opcode'];negative=minus_one(left);idx=1 if negative else 0
  if not negative and not minus_one(right):continue
  if negative and op not in ('<','>=') or not negative and op not in ('>','<='):continue
  # Require both promoted operands to be signed 32-bit, never change their types.
  types=[m.fix.canonical_type(c.get('type',{}).get('qualType',''),aliases) for c in cs]
  if any(t not in ('int','signed int','long','long int','signed long','signed long int') for t in types):continue
  operand=cs[idx]
  if any(n.get('kind') in ('CallExpr','CXXMemberCallExpr','CXXOperatorCallExpr','CompoundAssignOperator') or n.get('opcode') in ('++','--','=') or 'volatile' in n.get('type',{}).get('qualType','') for n in m.fix.walk(operand)):continue
  constant_span=m.fix.offsets(strip(cs[1-idx]))
  if not constant_span or not re.fullmatch(r'-\s*1',m.fix.mask(source)[constant_span[0]:constant_span[1]]):raise Unsupported('constant_source_identity')
  span=m.fix.offsets(node);value_span=m.fix.offsets(operand)
  if not span or not value_span or not 0<=span[0]<=value_span[0]<value_span[1]<=span[1]<=len(raw):raise Unsupported('invalid_ast_span')
  if any('expansionLoc' in loc or 'spellingLoc' in loc for n in m.fix.walk(node) for loc in n.get('range',{}).values()):raise Unsupported('macro_source_span')
  before=raw[span[0]:span[1]].decode();value=raw[value_span[0]:value_span[1]].decode();replacement='('+value+') '+('>=' if op in ('<','>') else '<')+' 0'
  # Verify current spelling agrees with the complete AST at every edit boundary.
  ls,rs=map(m.fix.offsets,cs)
  if not ls or not rs or not span[0]==ls[0]<ls[1]<=rs[0]<rs[1]==span[1]:raise Unsupported('operand_spans')
  gap=m.fix.mask(source)[ls[1]:rs[0]]
  if gap.strip()!=op:raise Unsupported('operator_source_identity')
  edits.append({'span':span,'before':before,'replacement':replacement,'operand_source':value,'promoted_types':types})
 if not edits:raise Unsupported('no_supported_signed_negative_one_threshold')
 edits.sort(key=lambda e:e['span'])
 if any(a['span'][1]>b['span'][0] for a,b in zip(edits,edits[1:])):raise Unsupported('overlapping_sites')
 for e in reversed(edits):a,b=e['span'];raw=raw[:a]+e['replacement'].encode()+raw[b:]
 return raw.decode(),{'kind':'signed_negative_one_to_zero_threshold','status':'UNVALIDATED','sites':edits,'original_zero_sign_branches':observations,'integer_predicate_identity':'For signed32 x, x>-1 iff x>=0; x<=-1 iff x<0. Operand evaluated once; no arithmetic introduced.','whole_function_semantic_proof':False,'acceptance':'unchanged complete relocation-aware comparator only'}

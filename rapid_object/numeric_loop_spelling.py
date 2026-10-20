"""Bounded byte-backed numeric-loop source hypothesis; no acceptance extension.

A zero-extended lookup digit can be stored as unsigned32 instead of a byte and
loaded in a FOR condition. The complete comparator may still refuse codegen
choices such as constant rematerialization and alignment.
"""
import re,capstone
from . import ast_match as m,eh_graph as g
from .conditional_construction import Unsupported,sha

def propose(source,ast,rva,bound,original):
 raw=source.encode()
 if not source.isascii() or sha(raw)!=bound.get('source_sha256') or sha(original)!=bound.get('module_sha256'):raise Unsupported('source_or_original_binding')
 nodes=list(m.fix.walk(ast))
 if any(n.get('isInvalid') or n.get('kind') in ('RecoveryExpr','UnresolvedLookupExpr') for n in nodes):raise Unsupported('incomplete_AST')
 consumed=[n for n in nodes if n.get('kind')=='TypedefDecl' and n.get('name')=='uint']
 if len(consumed)!=1 or consumed[0]['type']['qualType']!='unsigned int':raise Unsupported('consumed_type_uint')
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
 compact=re.sub(r'\s+','',text(body));pat=r"\{char\*pcVar1;charcVar2;bytebVar3;intiVar4;uintuVar5;intiVar6;iVar6=1;uVar5=10;if\(param_1==\(char\*\)0x0\)\{returnparam_2;\}cVar2=\*param_1;if\(cVar2=='-'\)\{param_1=param_1\+1;iVar6=-1;\}else\{if\(cVar2=='\$'\)\{uVar5=0x10;\}elseif\(cVar2!='\+'\)goto(LAB_[0-9a-fA-F]{8});param_1=param_1\+1;\}\1:iVar4=0;bVar3=\(&g_([0-9a-f]{8})\)\[\*param_1\];while\(bVar3<uVar5\)\{iVar4=iVar4\*uVar5\+\(uint\)bVar3;pcVar1=param_1\+1;param_1=param_1\+1;bVar3=\(&g_\2\)\[\*pcVar1\];\}returniVar4\*iVar6;\}"
 found=re.fullmatch(pat,compact)
 if not found:raise Unsupported('complete_retained_body_shape')
 label,table=found.groups();params=[n for n in f['inner'] if n.get('kind')=='ParmVarDecl']
 if f['type']['qualType']!='int (char *, int)':raise Unsupported('function_type')
 if [(n.get('name'),n['type']['qualType']) for n in params]!=[('param_1','char *'),('param_2','int')]:raise Unsupported('signature')
 digits=[n for n in nodes if n.get('kind')=='VarDecl' and n.get('name')=='bVar3' and span(body)[0]<=span(n)[0]<span(body)[1]]
 tables=[n for n in nodes if n.get('kind')=='VarDecl' and n.get('name')=='g_'+table]
 if len(digits)!=1 or digits[0]['type'].get('desugaredQualType')!='unsigned char' or len(tables)!=1 or tables[0]['type'].get('desugaredQualType')!='unsigned char':raise Unsupported('unsigned_byte_lookup')
 reader=g.Original(original);va=reader.pe.image_base+rva;spec=bound['requested'].get(str(rva),bound['requested'].get(rva))
 if not spec or len(spec['ranges'])!=1 or spec['ranges'][0]['start_rva']!=rva:raise Unsupported('original_range')
 ran=spec['ranges'][0];code=reader.read(va,ran['end_rva_inclusive']-rva+1,True)
 if len(code)!=109 or sha(code)!=spec['bytes_sha256'] or sha(code)!=ran['bytes_sha256']:raise Unsupported('original_range_hash')
 xs=list(capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32).disasm(code,va));tv=reader.pe.image_base+int(table,16)
 expected=[('mov','edx, dword ptr [esp + 4]'),('test','edx, edx'),('push','esi'),('push','edi'),('mov','edi, 1'),('mov','esi, 0xa'),('jne',hex(va+27)),('mov','eax, dword ptr [esp + 0x10]'),('pop','edi'),('pop','esi'),('ret',''),('mov','al, byte ptr [edx]'),('cmp','al, 0x2d'),('jne',hex(va+40)),('add','edx, edi'),('or','edi, 0xffffffff'),('jmp',hex(va+57)),('cmp','al, 0x24'),('jne',hex(va+51)),('mov','esi, 0x10'),('jmp',hex(va+55)),('cmp','al, 0x2b'),('jne',hex(va+57)),('add','edx, edi'),('movsx','ecx, byte ptr [edx]'),('movzx','ecx, byte ptr [ecx + %s]'%hex(tv)),('xor','eax, eax'),('cmp','ecx, esi'),('jae',hex(va+103)),('lea','esp, [esp]'),('imul','eax, esi'),('add','eax, ecx'),('movsx','ecx, byte ptr [edx + 1]'),('movzx','ecx, byte ptr [ecx + %s]'%hex(tv)),('add','edx, 1'),('cmp','ecx, esi'),('jb',hex(va+80)),('imul','eax, edi'),('pop','edi'),('pop','esi'),('ret','')]
 if sum(x.size for x in xs)!=109 or [(x.mnemonic,x.op_str) for x in xs]!=expected:raise Unsupported('complete_original_instruction_profile')
 # Edits affect only complete bound spans; preserved prefix/control and signed
 # character lookup expression remain literal copies of the retained source.
 edits=[]
 for n,old,new in [('bVar3','byte bVar3','uint bVar3'),('iVar4','int iVar4','uint iVar4')]:
  decls=[x for x in m.fix.walk(body) if x.get('kind')=='VarDecl' and x.get('name')==n]
  if len(decls)!=1 or text(decls[0])!=old:raise Unsupported('unique_local_type')
  a,b=span(decls[0]);edits.append((a,b,new))
 items=body['inner'];loop=[n for n in items if n.get('kind')=='WhileStmt']
 if len(loop)!=1:raise Unsupported('one_loop')
 # The preceding assignments and loop are inside a single source label statement.
 start=source.index('  iVar4 = 0;',span(body)[0],span(body)[1]);a,b=span(loop[0])
 replacement='for (iVar4 = 0; (bVar3 = (&g_'+table+')[*param_1]) < uVar5; param_1 = param_1 + 1) {\n    iVar4 = iVar4 * uVar5 + bVar3;\n  }'
 edits.append((start,b,replacement));candidate=raw
 for a,b,t in sorted(edits,reverse=True):candidate=candidate[:a]+t.encode()+candidate[b:]
 return candidate.decode(),dict(rva=rva,source_sha256=sha(raw),candidate_sha256=sha(candidate),original_sha256=sha(original),original_range_sha256=sha(code),original_instructions=len(xs),table_rva=int(table,16),digit_type_hypothesis='unsigned32, every source definition is an unsigned8 lookup',arithmetic='unsigned32 multiply/add and final sign multiplication; target int return conversion retains observed32bits',hypothesis_only=True,remaining_unknowns=['global table layout and negative character-index footprint','compiler constant rematerialization/alignment profile'])

"""Bounded conditional native construction hypothesis from retained C++ and bytes.

Only the complete existing main/EH comparator accepts the emitted source. This
recognizer checks the entire retained function, original instruction profile and
actual cleanup edge; it does not infer an unknown callee implementation.
"""
import hashlib,re,struct
import capstone
from . import ast_match as m,eh_graph as g

class Unsupported(ValueError): pass
sha=lambda b:hashlib.sha256(b).hexdigest()

def propose(source,ast,rva,bound,original):
 if not source.isascii() or bound.get('source_sha256')!=sha(source.encode()) or bound.get('module_sha256')!=sha(original):raise Unsupported('source_or_original_binding')
 nodes=list(m.fix.walk(ast));raw=source.encode()
 if any(n.get('isInvalid') or n.get('kind') in ('RecoveryExpr','UnresolvedLookupExpr') for n in nodes):raise Unsupported('incomplete_AST')
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
 a,b=span(f);bs,be=span(body);text=raw[bs:be].decode();compact=re.sub(r'\s+','',text)
 # Full retained-body match refuses every unaccounted side effect or call.
 pat=r'\{uintuVar1;intiVar2;intlocal_c;undefined1\*puStack_8;undefined4local_4;local_4=0xffffffff;puStack_8=&g_([0-9a-f]{8});local_c=\(\(int\)__readfsdword\(0\)\);uVar1=g_([0-9a-f]{8})\^\(\(unsignedint\)_AddressOfReturnAddress\(\)\+0xfffffff0u\);__writefsdword\(0,\(unsignedlong\)\(\(int\)&local_c\)\);if\(\(param_1!=\(int\*\)0x0\)&&\(\*param_1==0\)\)\{iVar2=fn_([0-9a-f]{8})\((0x[0-9a-f]+|[0-9]+),uVar1\);local_4=0;if\(iVar2==0\)\{iVar2=0;\}else\{iVar2=fn_([0-9a-f]{8})\(0\);\}\*param_1=iVar2;\}__writefsdword\(0,\(unsignedlong\)\(local_c\)\);return([0-9]+);\}'
 match=re.fullmatch(pat,compact)
 if not match:raise Unsupported('complete_retained_body_shape')
 handler,cookie,allocator,size,ctor,result=match.groups();size=int(size,0);result=int(result)
 params=[n for n in f['inner'] if n.get('kind')=='ParmVarDecl']
 if len(params)!=1 or params[0].get('name')!='param_1' or params[0].get('type',{}).get('qualType')!='int *' or f['type']['qualType']!='undefined4 (int *)':raise Unsupported('signature')
 if not 1<=size<=127 or not 0<=result<=0x7fffffff:raise Unsupported('bounded_size_or_result')
 requested=bound.get('requested',{});spec=requested.get(str(rva),requested.get(rva))
 if not spec or len(spec['ranges'])!=1 or spec['ranges'][0]['start_rva']!=rva:raise Unsupported('original_range')
 reader=g.Original(original);va=reader.pe.image_base+rva;ran=spec['ranges'][0];code=reader.read(va,ran['end_rva_inclusive']-rva+1,True)
 if sha(code)!=spec['bytes_sha256'] or sha(code)!=ran['bytes_sha256']:raise Unsupported('original_range_hash')
 ins=list(capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32).disasm(code,va))
 expected=[('push','-1'),('push',hex(reader.pe.image_base+int(handler,16))),('mov','eax, dword ptr fs:[0]'),('push','eax'),('push','esi'),('mov','eax, dword ptr [%s]'%hex(reader.pe.image_base+int(cookie,16))),('xor','eax, esp'),('push','eax'),('lea','eax, [esp + 8]'),('mov','dword ptr fs:[0], eax'),('mov','esi, dword ptr [esp + 0x18]'),('test','esi, esi'),('je',hex(va+87)),('cmp','dword ptr [esi], 0'),('jne',hex(va+87)),('push',hex(size) if size>=10 else str(size)),('call',hex(reader.pe.image_base+int(allocator,16))),('add','esp, 4'),('mov','dword ptr [esp + 0x18], eax'),('test','eax, eax'),('mov','dword ptr [esp + 0x10], 0'),('je',hex(va+83)),('push','0'),('mov','ecx, eax'),('call',hex(reader.pe.image_base+int(ctor,16))),('jmp',hex(va+85)),('xor','eax, eax'),('mov','dword ptr [esi], eax'),('mov','eax, '+(hex(result) if result>=10 else str(result))),('mov','ecx, dword ptr [esp + 8]'),('mov','dword ptr fs:[0], ecx'),('pop','ecx'),('pop','esi'),('add','esp, 0xc'),('ret','')]
 if sum(i.size for i in ins)!=len(code) or len(code)!=109 or [(i.mnemonic,i.op_str) for i in ins]!=expected:raise Unsupported('complete_original_instruction_profile')
 graph=g.original_graph(reader,va,code);action=graph['action']
 if action['profile']['kind']!='load_word_push_call_pop_ret' or action['profile']['parent_ebp_offset']!=4:raise Unsupported('cleanup_action')
 helper=action['external_target_va'];tail=reader.read(helper,5,True)
 if tail[0]!=0xe9:raise Unsupported('cleanup_helper')
 cleanup=helper+5+struct.unpack_from('<i',tail,1)[0];reader.read(cleanup,1,True);cleanup_rva=cleanup-reader.pe.image_base
 declaration=r'extern "C" unsigned int __cdecl fn_'+ctor+r'\(\.\.\.\);'
 found=list(re.finditer(declaration,source))
 if len(found)!=1 or found[0].start()>=a or re.search(r'\b(?:struct|class)\s+fn_'+ctor+r'\b',source):raise Unsupported('constructor_declaration_or_collision')
 x,y=found[0].span();prefix=source[:a];prefix=prefix[:x]+prefix[y:]
 cls='fn_'+ctor
 definition='''extern "C" void __cdecl fn_%08x(void*);
struct %s {
 char opaque[%d];
 __forceinline static void *operator new(unsigned n) {return (void*)fn_%s(n);}
 __forceinline static void operator delete(void*p) {fn_%08x(p);}
 %s(int);
};
'''%(cleanup_rva,cls,size,allocator,cleanup_rva,cls)
 candidate=prefix+definition+raw[a:bs].decode()+'{\n if(param_1 && !*param_1) *param_1=(int)new '+cls+'(0);\n return '+str(result)+';\n}'+source[b:]
 return candidate,dict(rva=rva,source_sha256=sha(raw),candidate_sha256=sha(candidate.encode()),original_sha256=sha(original),original_range_sha256=sha(code),original_instructions=len(ins),allocation_size_hypothesis=size,constructor_rva=int(ctor,16),cleanup_helper_va=helper,cleanup_target_rva=cleanup_rva,hypothesis_only=True,unknowns=['nominal object layout/lifetime','constructor implementation semantics'],preserved='complete observed caller and cleanup instruction profile; external calls remain unresolved implementations')

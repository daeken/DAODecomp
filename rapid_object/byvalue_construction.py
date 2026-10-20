"""Bounded base-construction/by-value-argument source hypothesis.

The copy-constructor declaration is a C++ type hypothesis that permits VC8 copy
elision. No copy implementation is supplied; an emitted unknown dependency cannot
pass the unchanged complete native graph checker.
"""
import re,struct
import capstone
from .conditional_construction import Unsupported,sha
from . import ast_match as m,eh_graph as g

def propose(source,ast,rva,bound,original):
 raw=source.encode()
 if not source.isascii() or sha(raw)!=bound.get('source_sha256') or sha(original)!=bound.get('module_sha256'):raise Unsupported('source_or_original_binding')
 nodes=list(m.fix.walk(ast))
 if any(n.get('isInvalid') or n.get('kind') in ('RecoveryExpr','UnresolvedLookupExpr') for n in nodes):raise Unsupported('incomplete_AST')
 own=[n for n in nodes if n.get('kind')=='CXXMethodDecl' and n.get('name')=='fn_%08x'%rva and any(c.get('kind')=='CompoundStmt' for c in n.get('inner',[]))]
 if len(own)!=1:raise Unsupported('unique_own_method')
 f=own[0];body=next(n for n in f['inner'] if n.get('kind')=='CompoundStmt')
 for n in [f]+list(m.fix.walk(body)):
  if any('spellingLoc'in p or 'expansionLoc'in p for p in n.get('range',{}).values()):raise Unsupported('macro')
 a,b=m.fix.offsets(f);bs,be=m.fix.offsets(body)
 if not 0<=a<bs<be<=b<=len(raw):raise Unsupported('source_spans')
 params=[n for n in f['inner'] if n.get('kind')=='ParmVarDecl']
 if len(params)!=1 or params[0].get('name')!='param_2' or params[0]['type']['qualType']!='int':raise Unsupported('parameter')
 compact=re.sub(r'\s+','',raw[bs:be].decode())
 pat=r'\{intlocal_c;undefined1\*puStack_8;undefined4local_4;puStack_8=&g_([0-9a-f]{8});local_c=\(\(int\)__readfsdword\(0\)\);__writefsdword\(0,\(unsignedlong\)\(\(int\)&local_c\)\);\*\(undefined4\*\)\(\(\(int\)this\)\+4\)=0;\*\(undefined4\*\)\(\(\(int\)this\)\+8\)=0;\*\(undefined4\*\)\(\(\(int\)this\)\+0xc\)=0;local_4=0;if\(param_2!=0\)\{fn_([0-9a-f]{8})\(0\);fn_([0-9a-f]{8})\(param_2\);\}__writefsdword\(0,\(unsignedlong\)\(local_c\)\);return\(\(int\)this\);\}'
 found=re.fullmatch(pat,compact)
 if not found:raise Unsupported('complete_retained_body_shape')
 handler,ctor,callee=found.groups();reader=g.Original(original);va=reader.pe.image_base+rva;spec=bound['requested'].get(str(rva),bound['requested'].get(rva))
 if not spec or len(spec['ranges'])!=1 or spec['ranges'][0]['start_rva']!=rva:raise Unsupported('original_range')
 ran=spec['ranges'][0];code=reader.read(va,ran['end_rva_inclusive']-rva+1,True)
 if len(code)!=109 or sha(code)!=spec['bytes_sha256'] or sha(code)!=ran['bytes_sha256']:raise Unsupported('original_range_hash')
 ins=list(capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32).disasm(code,va));pairs=[(i.mnemonic,i.op_str) for i in ins]
 cookie=struct.unpack_from('<I',code,18)[0] if code[17]==0xa1 else 0
 expected=[('push','-1'),('push',hex(reader.pe.image_base+int(handler,16))),('mov','eax, dword ptr fs:[0]'),('push','eax'),('push','ecx'),('push','esi'),('push','edi'),('mov','eax, dword ptr [%s]'%hex(cookie)),('xor','eax, esp'),('push','eax'),('lea','eax, [esp + 0x10]'),('mov','dword ptr fs:[0], eax'),('mov','esi, ecx'),('mov','dword ptr [esp + 0xc], esi'),('xor','eax, eax'),('mov','dword ptr [esi + 4], eax'),('mov','dword ptr [esi + 8], eax'),('mov','dword ptr [esi + 0xc], eax'),('mov','edi, dword ptr [esp + 0x20]'),('cmp','edi, eax'),('mov','dword ptr [esp + 0x18], eax'),('jbe',hex(va+87)),('sub','esp, 8'),('mov','ecx, esp'),('mov','dword ptr [esp + 0x28], esp'),('push','eax'),('call',hex(reader.pe.image_base+int(ctor,16))),('push','edi'),('mov','ecx, esi'),('call',hex(reader.pe.image_base+int(callee,16))),('mov','eax, esi'),('mov','ecx, dword ptr [esp + 0x10]'),('mov','dword ptr fs:[0], ecx'),('pop','ecx'),('pop','edi'),('pop','esi'),('add','esp, 0x10'),('ret','4')]
 if sum(i.size for i in ins)!=109 or pairs!=expected:raise Unsupported('complete_original_instruction_profile')
 graph=g.original_graph(reader,va,code);action=graph['action']
 if action['profile']['kind']!='load_receiver_ecx_tail_jump' or action['profile']['parent_ebp_offset']!=-16:raise Unsupported('cleanup_action')
 helper=action['external_target_va'];tail=reader.read(helper,5,True)
 if tail[0]!=0xe9:raise Unsupported('cleanup_helper')
 cleanup=helper+5+struct.unpack_from('<i',tail,1)[0]-reader.pe.image_base;reader.read(reader.pe.image_base+cleanup,1,True)
 prefix=source[:a];suffix=source[b:]
 for name in (ctor,callee):
  pat=r'extern "C" unsigned int __cdecl fn_'+name+r'\(\.\.\.\);[^\n]*\n'
  if len(re.findall(pat,prefix))!=1:raise Unsupported('callee_declaration')
  prefix=re.sub(pat,'',prefix)
 decl=r'struct Seed_%08x \{ int __thiscall fn_%08x\(int param_2\); \};\n'%(rva,rva)
 if len(re.findall(decl,prefix))!=1:raise Unsupported('method_declaration')
 prefix=re.sub(decl,'',prefix)
 if re.search(r'\b(?:struct|class)\s+fn_(?:'+ctor+'|%08x'%rva+r')\b',source):raise Unsupported('class_collision')
 base='ConstructionBase_%08x'%rva
 if base in source:raise Unsupported('base_collision')
 definition='''unsigned int fn_%08x(...);
struct fn_%s { unsigned word; unsigned char flag; fn_%s(int); fn_%s(const fn_%s&); ~fn_%s(); };
struct %s {
 unsigned unknown,begin,end,capacity;
 void __thiscall fn_%s(unsigned,fn_%s);
 __forceinline %s() {begin=0;end=0;capacity=0;}
 __forceinline ~%s() {((void(__thiscall*)(void*))&fn_%08x)(this);}
};
struct fn_%08x:%s {fn_%08x(int);};
fn_%08x::fn_%08x(int param_2) {
 if((unsigned)param_2>0) this->fn_%s(param_2,fn_%s(0));
}'''%(cleanup,ctor,ctor,ctor,ctor,ctor,base,callee,ctor,base,base,cleanup,rva,base,rva,rva,rva,callee,ctor)
 candidate=prefix+definition+suffix
 return candidate,dict(rva=rva,source_sha256=sha(raw),candidate_sha256=sha(candidate.encode()),original_sha256=sha(original),original_range_sha256=sha(code),original_instructions=len(ins),temporary_size_hypothesis=8,base_size_hypothesis=16,constructor_rva=int(ctor,16),cleanup_helper_va=helper,cleanup_target_rva=cleanup,hypothesis_only=True,unknowns=['nominal object layout/lifetime','external callee/constructor/destructor implementations','copy-constructor implementation is absent and must not be emitted'])

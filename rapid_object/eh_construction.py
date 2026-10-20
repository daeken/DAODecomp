"""Narrow DAO constructor source hypothesis; compiled full-graph checking is required."""
import hashlib,re
from rapid_object import ast_match as m
class Unsupported(ValueError):pass
sha=lambda x:hashlib.sha256(x).hexdigest()
def propose(source,ast,rva,expected_sha):
 if not source.isascii() or sha(source.encode())!=expected_sha:raise Unsupported('source_binding')
 raw=source.encode();nodes=list(m.fix.walk(ast))
 if any(n.get('isInvalid') or n.get('kind') in ('RecoveryExpr','UnresolvedLookupExpr') for n in nodes):raise Unsupported('incomplete_AST')
 own=[n for n in nodes if n.get('kind')=='FunctionDecl' and n.get('name')=='fn_%08x'%rva and any(c.get('kind')=='CompoundStmt' for c in n.get('inner',[]))]
 if len(own)!=1:raise Unsupported('own_function')
 f=own[0];body=next(n for n in f['inner'] if n.get('kind')=='CompoundStmt');bn=list(m.fix.walk(body))
 def span(n):
  if any('spellingLoc'in p or 'expansionLoc'in p for p in n.get('range',{}).values()):raise Unsupported('macro')
  p=m.fix.offsets(n)
  if not p or not 0<=p[0]<p[1]<=len(raw):raise Unsupported('span')
  return p
 for n in [f]+bn:
  if 'range'in n:span(n)
 def text(n):a,b=span(n);return raw[a:b].decode()
 if any(n.get('kind') in ('GotoStmt','WhileStmt','ForStmt','DoStmt','CXXNewExpr','CXXTryStmt','CXXThrowExpr') or 'volatile' in n.get('type',{}).get('qualType','') for n in bn):raise Unsupported('control_or_volatile')
 expected_decls=['uint uVar1;','undefined4 *puVar2;','undefined4 *puVar3;','int local_c;','undefined1 *puStack_8;','undefined4 local_4;']
 items=body.get('inner',[])
 if len(items)!=17 or [text(n) for n in items[:6]]!=expected_decls:raise Unsupported('complete_retained_body_shape')
 patterns=[r'local_4 = 0xffffffff',r'puStack_8 = &g_[0-9a-f]{8}',r'local_c = \(\(int\)__readfsdword\(0\)\)',r'uVar1 = g_00815234 \^ \(\(unsigned int\)_AddressOfReturnAddress\(\) \+ 0xffffffe[8c]u\)',r'__writefsdword\(0,\(unsigned long\)\(\(int\)&local_c\)\)',r'puVar2 = \(undefined4 \*\)fn_00013660\(4\)',r'local_4 = 0',r'puVar3 = \(undefined4 \*\)0x0']
 if any(not re.fullmatch(pattern,text(n)) for n,pattern in zip(items[6:14],patterns)) or items[14].get('kind')!='IfStmt' or text(items[15])!='__writefsdword(0,(unsigned long)(local_c))' or text(items[16])!='return puVar3':raise Unsupported('unknown_omitted_effect_or_frame_spelling')

 ifs=[n for n in body['inner'] if n.get('kind')=='IfStmt'];rets=[n for n in bn if n.get('kind')=='ReturnStmt']
 if len(ifs)!=1 or len(ifs[0]['inner'])!=2 or len(rets)!=1 or body['inner'][-1] is not rets[0]:raise Unsupported('single_exit_null_guard')
 then=ifs[0]['inner'][1];statements=then.get('inner',[])
 if len(statements)!=3 or statements[0].get('kind')!='CallExpr' or statements[1].get('kind')!='BinaryOperator' or statements[1].get('opcode')!='=' or statements[2].get('kind')!='BinaryOperator' or statements[2].get('opcode')!='=':raise Unsupported('three_statement_constructor_body')
 # Narrow retained pointer/result spelling, independently bound to this complete AST.
 if not re.fullmatch(r'puVar3\s*=\s*puVar2',text(statements[2])) or not re.fullmatch(r'\*puVar2\s*=\s*\(undefined4\)\s*\(&g_[0-9a-f]{8}\)',text(statements[1])):raise Unsupported('existing_suffix_shape')
 if not re.fullmatch(r'puVar2\s*!=\s*\(undefined4 \*\)0x0',text(ifs[0]['inner'][0])):raise Unsupported('existing_null_guard')
 if text(rets[0]).strip()!='return puVar3':raise Unsupported('existing_return')
 allocs=[n for n in bn if n.get('kind')=='CallExpr' and any(x.get('referencedDecl',{}).get('name')=='fn_00013660' for x in m.fix.walk(n.get('inner',[{}])[0]))]
 if len(allocs)!=1 or text(allocs[0])!='fn_00013660(4)':raise Unsupported('only_observed_four_byte_allocation')
 params=[n for n in f['inner'] if n.get('kind')=='ParmVarDecl']
 if len(params)>1 or (params and params[0]['type']['qualType'] not in ('undefined4','uint','unsigned int','int')):raise Unsupported('argument_type')
 paramdecl=', '.join(text(n) for n in params);paramvalues=', '.join(n['name'] for n in params)
 ctor='fn_000d2080' if params else 'fn_000d2070';call=text(statements[0])
 if ctor not in call:raise Unsupported('callee_cleanup_family')
 pvars=[n for n in bn if n.get('kind')=='VarDecl' and n.get('name')=='puVar2'];qvars=[n for n in bn if n.get('kind')=='VarDecl' and n.get('name')=='puVar3']
 if len(pvars)!=1 or len(qvars)!=1:raise Unsupported('receiver_result_identity')
 rid=pvars[0]['id'];qid=qvars[0]['id'];a,b=span(then);segment=raw[a+1:span(statements[2])[0]]
 edits=[]
 for n in m.fix.walk(then):
  if n.get('kind')=='DeclRefExpr' and n.get('referencedDecl',{}).get('id')==rid:
   x,y=span(n)
   if x<span(statements[2])[0]:edits.append((x-(a+1),y-(a+1),b'((undefined4*)this)'))
 for x,y,v in sorted(edits,reverse=True):segment=segment[:x]+v+segment[y:]
 # No escaped result variable may enter the new constructor body.
 if b'puVar2' in segment or b'puVar3' in segment:raise Unsupported('receiver_or_result_escape')
 declpat=r'extern "C" unsigned int __cdecl '+ctor+r'\(\.\.\.\);';matches=list(re.finditer(declpat,source))
 if len(matches)!=1:raise Unsupported('provisional_callee_declaration')
 start,end=span(f);bs,be=span(body);header=raw[start:bs].decode();prefix=raw[:start].decode();suffix=raw[end:].decode();prefix=prefix[:matches[0].start()]+prefix[matches[0].start():matches[0].end()].replace('extern "C" ','',1)+prefix[matches[0].end():]
 typename='EHConstruction_%08x'%rva
 if typename in source:raise Unsupported('wrapper_identity_collision')
 helper='''extern "C" void __cdecl fn_000b9080(void*);
struct '''+typename+''' {unsigned int opaque_word;
__forceinline static void *operator new(unsigned int n){return (void*)fn_00013660(n);}
__forceinline static void operator delete(void*p){fn_000b9080(p);}
__forceinline '''+typename+'''('''+paramdecl+''') {'''+segment.decode()+'''}
};
typedef char '''+typename+'''_Size[(sizeof('''+typename+''')==4)?1:-1];
'''
 candidate=prefix+helper+header+'{ return (undefined4*)new '+typename+'('+paramvalues+'); }'+suffix
 return candidate,dict(rva=rva,baseline_sha256=expected_sha,candidate_sha256=sha(candidate.encode()),allocation_size_hypothesis=4,alignment_hypothesis=4,observed_callee_access_bytes=4,wrapper_type=typename,allocation_scope='class-specific only',cleanup_target_va=0x4b9080,constructor=ctor,constructor_parameters=paramdecl,constructor_body=segment.decode(),source_receiver_decl_id=rid,source_result_decl_id=qid,hypothesis_only=True,rollout_ready=False,unknowns=['object lifetime/layout nominal type','callee formal semantics','runtime/metadata binding'],preserved='existing constructor call, actual parameter values, vptr store, allocator target/size, null result and return pointer; compiler emits EH')

def compose(proposals):
 """Only combine already-bound distinct hypotheses; no duplicate wrapper identities."""
 seen=set();parts=[]
 for candidate,meta in proposals:
  name=meta['wrapper_type']
  if name in seen:raise Unsupported('duplicate_wrapper_identity')
  if sha(candidate.encode())!=meta['candidate_sha256']:raise Unsupported('candidate_binding')
  seen.add(name);parts.append(candidate.encode())
 return b'\n'.join(parts)

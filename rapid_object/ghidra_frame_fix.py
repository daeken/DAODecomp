"""Byte-backed entry-stack address expressions, not a reconstructed native SEH frame."""
from collections import Counter
from pathlib import Path
import copy
import fcntl
import json
import re
import signal
import time
from . import ghidra_state_fix as state
from . import ghidra_compile_fix as fix
from rapid.factory import REPO
from rapid.packets import PIN
from workers.deepseek_packet import atomic,encode,sha

ROOT=REPO/'local/toolkit-evolution-003'
INTRINSIC='extern "C" void * _AddressOfReturnAddress(void);\n#pragma intrinsic(_AddressOfReturnAddress)\n'
STACK=re.compile(r'\bstack0x[0-9a-fA-F]+\b')
COOKIE=re.compile(r'(?m)^[ \t]*(?P<dest>[A-Za-z_]\w*)\s*=\s*(?P<cookie>[A-Za-z_]\w*)\s*\^\s*(?P<address>\(\s*uint\s*\)\s*&\s*(?P<stack>stack0x[0-9a-fA-F]+))\s*;')


def cookie_expression(record):
    source=record.get('draft') or '';code=fix.mask(source)
    if re.search(r'\b(?:inline|_inline|__inline|_forceinline|__forceinline|naked)\b',code.partition('{')[0]):raise ValueError('entry_boundary_not_out_of_line')
    matches=list(COOKIE.finditer(code));tokens=list(STACK.finditer(code))
    if len(matches)!=1 or len(tokens)!=1 or not matches[0].start('stack')==tokens[0].start():raise ValueError('not_single_cookie_address_only')
    aliases=re.findall(r'\btypedef\s+([^;{}]+?)\s+uint\s*;',fix.mask(record.get('type_declarations_hypothesis','')))
    if len(aliases)!=1 or ' '.join(aliases[0].split())!='unsigned int':raise ValueError('cookie_address_type_not_proven_u32')
    match=matches[0];token=match['stack'];value=int(token[7:],16)
    if value>0xffffffff or value<0x80000000:raise ValueError('not_negative_original_frame_address')
    symbols=[s for s in record.get('symbols',[]) if s.get('token')==match['cookie'] and s.get('kind')=='global']
    addresses={s.get('original_va') for s in symbols}
    if len(addresses)!=1 or type(next(iter(addresses),None)) is not int:raise ValueError('unresolved_cookie_global_identity')
    return match,{'stack_token':token,'original_delta':value-0x100000000,'cookie_token':match['cookie'],'cookie_va':next(iter(addresses))}


def frame_evidence(record,pe=None):
    """Track only a fixed linear entry prologue, refusing unknown SP changes/calls/control flow."""
    from capstone import Cs,CS_ARCH_X86,CS_MODE_32,CS_OP_REG,CS_OP_IMM,CS_OP_MEM,CS_GRP_JUMP,CS_GRP_CALL,CS_GRP_RET,CS_GRP_INT,CS_GRP_IRET,CS_GRP_BRANCH_RELATIVE
    from capstone.x86 import X86_REG_ESP,X86_REG_DS
    _,expression=cookie_expression(record);pe=pe or state.image();fs=state.instruction_evidence(record,pe)
    if record.get('module_sha256')!=PIN or record.get('image_base')!=0x400000 or record.get('original_va')!=0x400000+record['rva']:raise ValueError('original_entry_identity')
    rr=record['ranges'][0]
    if rr['start_rva']!=record['rva']:raise ValueError('no_entry_range')
    size=rr['end_rva_inclusive']-rr['start_rva']+1;data=pe.get_data(rr['start_rva'],size);md=Cs(CS_ARCH_X86,CS_MODE_32);md.detail=True;ins=list(md.disasm(data,record['original_va']))
    if len(data)!=size or sum(i.size for i in ins)!=size:raise ValueError('incomplete_original_prologue_range')
    # Full range hash and FS evidence are checked by the frozen state layer as well.
    affine={X86_REG_ESP:0};cookies={};rows=[];sites=[]
    def finish(reason):
        matching=[x for x in sites if x['delta']==expression['original_delta']]
        if len(matching)>1:raise ValueError('ambiguous_cookie_delta_sites')
        if not matching:raise ValueError('cookie_stack_delta_mismatch' if sites else reason)
        return {**expression,'prologue':rows,'cookie_sites':sites,'matched_site':matching[0],'boundary':reason,'address_role':'original entry return-slot address plus byte-derived signed delta; not replacement local-frame storage'}
    def canonical(reg):
        name=md.reg_name(reg);families={'eax':('eax','ax','ah','al'),'ebx':('ebx','bx','bh','bl'),'ecx':('ecx','cx','ch','cl'),'edx':('edx','dx','dh','dl'),'esi':('esi','si'),'edi':('edi','di'),'ebp':('ebp','bp'),'esp':('esp','sp')}
        for full,names in families.items():
            if name in names:
                from capstone import x86
                return getattr(x86,'X86_REG_'+full.upper())
        return reg
    def absolute_cookie(op):return op.type==CS_OP_MEM and op.size==4 and op.mem.segment in (0,X86_REG_DS) and not op.mem.base and not op.mem.index and op.mem.disp&0xffffffff==expression['cookie_va']
    for i in ins[:128]:
        rows.append({'address':i.address,'bytes':i.bytes.hex(),'mnemonic':i.mnemonic,'operands':i.op_str,'entry_sp_delta_before':affine.get(X86_REG_ESP)})
        if i.address-record['original_va']>512:raise ValueError('prologue_budget')
        ops=i.operands;mn=i.mnemonic
        # Do not scan through traps or mode/control transfers to a later cookie site.
        # Capstone supplies control groups; explicit traps/system exits without a
        # control group (notably UD2/HLT/XABORT) are conservative boundaries too.
        control_groups=(CS_GRP_JUMP,CS_GRP_CALL,CS_GRP_RET,CS_GRP_INT,CS_GRP_IRET,CS_GRP_BRANCH_RELATIVE)
        stop_opcodes={'enter','leave','ud0','ud1','ud2','hlt','rsm','vmcall','vmmcall','vmrun','vmlaunch','vmresume','xabort','enclu','encls','enclv','bound'}
        if any(i.group(g) for g in control_groups) or mn in stop_opcodes:return finish('nonlinear_or_callee_modified_frame')
        if mn=='xor' and len(ops)==2 and ops[0].type==CS_OP_REG and ops[0].size==4 and ops[0].reg!=X86_REG_ESP:
            delta=None
            if ops[0].reg in cookies and ops[1].type==CS_OP_REG:delta=affine.get(ops[1].reg)
            elif ops[0].reg in affine and absolute_cookie(ops[1]):delta=affine[ops[0].reg]
            if delta is not None:
                sites.append({'address':i.address,'bytes':i.bytes.hex(),'delta':delta,'cookie_va':expression['cookie_va']})
        writes=i.regs_access()[1];handled=set()
        if mn=='push':
            if len(ops)!=1 or ops[0].size!=4 or 0x66 in i.prefix:raise ValueError('unsupported_push_width')
            affine[X86_REG_ESP]-=4;handled.add(X86_REG_ESP)
        elif mn=='pop':
            if len(ops)!=1 or ops[0].type!=CS_OP_REG or ops[0].size!=4 or ops[0].reg==X86_REG_ESP:raise ValueError('unsupported_pop')
            affine[X86_REG_ESP]+=4;handled.add(X86_REG_ESP)
        elif mn in ('add','sub') and len(ops)==2 and ops[0].type==CS_OP_REG and ops[0].reg==X86_REG_ESP and ops[1].type==CS_OP_IMM:
            affine[X86_REG_ESP]+=(1 if mn=='add' else -1)*ops[1].imm;handled.add(X86_REG_ESP)
        elif mn=='mov' and len(ops)==2 and ops[0].type==CS_OP_REG and ops[0].size==4:
            dest=ops[0].reg;source_affine=affine.get(ops[1].reg) if ops[1].type==CS_OP_REG else None;source_cookie=cookies.get(ops[1].reg) if ops[1].type==CS_OP_REG else None;affine.pop(dest,None);cookies.pop(dest,None)
            if source_affine is not None:affine[dest]=source_affine
            elif source_cookie is not None:cookies[dest]=source_cookie
            elif absolute_cookie(ops[1]):cookies[dest]=expression['cookie_va']
            if dest==X86_REG_ESP and dest not in affine:raise ValueError('unknown_stack_assignment')
            handled.add(dest)
        elif mn=='lea' and len(ops)==2 and ops[0].type==CS_OP_REG and ops[0].size==4 and ops[1].type==CS_OP_MEM:
            dest=ops[0].reg;mem=ops[1].mem;value=affine.get(mem.base);affine.pop(dest,None);cookies.pop(dest,None)
            if value is not None and not mem.index and not mem.segment:affine[dest]=value+mem.disp
            if dest==X86_REG_ESP and dest not in affine:raise ValueError('unknown_stack_lea')
            handled.add(dest)
        for written in writes:
            reg=canonical(written)
            if reg in handled:continue
            if reg==X86_REG_ESP:raise ValueError('unknown_dynamic_stack_change')
            affine.pop(reg,None);cookies.pop(reg,None)
    raise ValueError('no_matching_cookie_prologue_or_budget')


def lower_frame(record,evidence):
    match,expression=cookie_expression(record)
    if any(evidence.get(k)!=v for k,v in expression.items()):raise ValueError('frame_expression_evidence_binding')
    out=copy.deepcopy(record);source=record['draft'];address='((unsigned int)_AddressOfReturnAddress() + 0x'+f"{expression['original_delta']&0xffffffff:08x}"+'u)'
    out['draft']=source[:match.start('address')]+address+source[match.end('address'):];out['type_declarations_hypothesis']=record.get('type_declarations_hypothesis','')+'\n'+INTRINSIC
    return out,{'kind':'original_entry_stack_address','before':source[match.start('address'):match.end('address')],'after':address,'proof':evidence,'native_seh_frame_reconstructed':False}


def bindings():return {'frame_fix_sha256':sha(Path(__file__).read_bytes()),'state':state.bindings()}


def prepare(root=ROOT):
    root=Path(root);root.mkdir(parents=True,exist_ok=True);source=REPO/'local/toolkit-evolution-002/deferred-stack.json';cases=[x['case'] for x in json.loads(source.read_text())['cases']];ready=[];deferred=[];examples=[]
    for case in cases:
        fix.verify_baseline(case);raw=json.loads(Path(case['raw_export']).read_text())
        try:proof=frame_evidence(raw);state.instruction_evidence(raw);lower_frame(raw,proof);ready.append(case)
        except ValueError as e:deferred.append({'case':case,'reason':str(e)})
    controls=[x for x in json.loads((REPO/'local/toolkit-evolution-002/pilot-selection.json').read_text())['cases'] if x['category']=='control'];chosen=fix.stratified(ready,80)+controls
    for case in ready:case['category']='frame'
    receipt={'module_sha256':PIN,'observed':len(cases),'supported':len(ready),'deferred':len(deferred),'deferred_reasons':dict(Counter(x['reason'] for x in deferred)),'tool_bindings':bindings(),'paid_requests':0,'source_plan_sha256':sha(source.read_bytes())};atomic(root/'preparation.json',receipt);atomic(root/'deferred.json',{'cases':deferred,'preparation':receipt});atomic(root/('pilot-selection-proposed.json' if (root/'pilot-selection.json').exists() else 'pilot-selection.json'),{'cases':chosen,'tool_bindings':bindings()});atomic(root/'sweep-plan.json',{'cases':ready,'tool_bindings':bindings(),'launched':False});(root/'sweep.paused').write_text('paused before review\n');return receipt


def evaluate(case,root):
    fix.verify_baseline(case);folder=Path(root)/f"{case['rva']:08x}";folder.mkdir(parents=True,exist_ok=True);raw=json.loads(Path(case['raw_export']).read_text());current=bindings();record_path=folder/'result.json'
    derived=copy.deepcopy(case)
    if case['category']!='control':
        proof=frame_evidence(raw);changed,change=lower_frame(raw,proof);data=encode(changed);path=folder/'frame-export.json'
        if path.exists() and path.read_bytes()!=data:raise ValueError('frame_recipe_changed_use_new_root')
        if not path.exists():atomic(path,changed)
        derived.update(raw_export=str(path),raw_export_sha256=sha(path.read_bytes()))
        evidence_path=folder/'frame-evidence.json'
        if evidence_path.exists() and json.loads(evidence_path.read_text())!=change:evidence_path=folder/('frame-evidence-'+current['frame_fix_sha256']+'.json')
        atomic(evidence_path,change)
    if record_path.exists():
        old=json.loads(record_path.read_text())
        if old['original_baseline']!=case or old['derived_case']!=derived:raise ValueError('frame_baseline_cache_changed')
    result=state.evaluate(derived,folder/'native')
    result={**result,'original_baseline':case,'derived_case':derived,'frame_tool_bindings':current,'native_seh_frame_reconstructed':False}
    if record_path.exists():atomic(folder/'reconciled-result.json',result)
    else:atomic(record_path,result)
    return result


def run(root=ROOT,sweep=False,resume=False,max_cases=0):
    root=Path(root);plan=json.loads((root/('sweep-plan.json' if sweep else 'pilot-selection.json')).read_text());owner=(root/'owner.lock').open('a+');fcntl.flock(owner,fcntl.LOCK_EX|fcntl.LOCK_NB);records=[];started=time.time();stop=False
    def stopping(*args):
        nonlocal stop
        stop=True
    old=signal.signal(signal.SIGTERM,stopping)
    try:
        if sweep and resume:(root/'sweep.paused').unlink(missing_ok=True)
        for case in plan['cases']:
            if stop or (sweep and (root/'sweep.paused').exists()) or (max_cases and len(records)>=max_cases):break
            area='pilot' if not sweep or (root/'pilot'/f"{case['rva']:08x}"/'result.json').exists() else 'sweep';records.append(evaluate(case,root/area));value={**state.summarize(records,started),'frame_tool_bindings':bindings()};atomic(root/('sweep-status.json' if sweep else 'pilot-results.json'),value)
        if stop:(root/'sweep.paused').write_text('stop after retained build\n')
        return {**state.summarize(records,started),'frame_tool_bindings':bindings()}
    finally:signal.signal(signal.SIGTERM,old);fcntl.flock(owner,fcntl.LOCK_UN);owner.close()


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['prepare','pilot','sweep','pause']);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--resume',action='store_true');p.add_argument('--max-cases',type=int,default=0);a=p.parse_args()
    if a.command=='prepare':value=prepare(a.root)
    elif a.command=='pause':(a.root/'sweep.paused').write_text('operator pause\n');value={'paused':True}
    else:value=run(a.root,a.command=='sweep',a.resume,a.max_cases)
    print(json.dumps(value,indent=2))

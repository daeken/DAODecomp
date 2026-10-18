"""At most two paid native pilot attempts; paid output is never silently retried."""
import argparse
import json
from pathlib import Path
import time
from workers import deepseek_packet as provider
from rapid.factory import DEFAULT_GLOBAL,DEFAULT_LEDGER,MAIN,REPO
from rapid.packets import PIN
from rapid.store import reserve_global,settle_global


NATIVE_INSTRUCTIONS='Emit one C++98 translation unit containing every requested ordinary native x86 function. Use real __cdecl/__stdcall/__fastcall inferred from actual register/stack behavior and RET cleanup; no Context, wrappers, inline assembly, naked functions, opcode arrays, helper simulation, extra runtime, headers, external calls, tests, contracts or fixtures. Each function has its exact requested fn_RVA name and an immediately preceding // FUNCTION: DAO 0xORIGINAL_VA annotation, in increasing address order. Return machine semantics, preserve 32-bit unsigned wrapping; use unsigned int for 32-bit values. Use signed only when defined and required. Selected functions are call-free integer/pointer-memory slices: preserve observed object fields, arrays, buffer loops, read/write widths, aliasing and index scaling. For ECX object helpers use small inferred C++98 class declarations and OUT-OF-LINE __thiscall member definitions when needed; put each RVA annotation immediately before its emitting definition, with the requested fn_RVA method name. Keep every required declaration in this single source. No unknown successful stubs or invented callees. Infer native parameter types and control flow from actual bytes. Aim for matching generated instruction behavior under Microsoft VC8 x86 /O2 /Ob1 /Oy /GS- /GR- /EHsc /Zi. Do not invent input restrictions or success stubs. Keep functions separate and non-inline; no dllexport needed. Return source, exact requested function notes, and uncertainties using the response JSON schema. Unknown remains unknown. Compiler/reccmp output may drive up to six bounded repairs; return ONLY currently requested unmatched functions and omit all other prior definitions. Preserve the best observed source behavior, using actual latest/best differences; a source-level function is the only authored per-function artifact.'


def packet(rvas,feedback=None):
    import pefile
    from capstone import Cs,CS_ARCH_X86,CS_MODE_32
    binary=MAIN/'gamedata/bin_ship/DAOrigins.exe'; raw=binary.read_bytes()
    if provider.sha(raw)!=PIN: raise ValueError('binary_pin')
    inventory=json.loads((MAIN/'local/analysis/functions.json').read_text())
    if inventory['module_sha256']!=PIN: raise ValueError('inventory_pin')
    index={f['rva']:f for f in inventory['functions']}; pe=pefile.PE(data=raw); md=Cs(CS_ARCH_X86,CS_MODE_32)
    functions=[]
    for rva in sorted(rvas):
        f=index[rva]; ranges=f['body_ranges']
        if len(ranges)!=1 or ranges[0]['start_rva']!=rva: raise ValueError('noncontiguous_boundary')
        size=ranges[0]['end_rva_inclusive']-rva+1; b=pe.get_data(rva,size); ins=list(md.disasm(b,pe.OPTIONAL_HEADER.ImageBase+rva))
        if sum(i.size for i in ins)!=size or any(i.mnemonic=='call' for i in ins): raise ValueError('decode_or_call')
        functions.append({'name':f'fn_{rva:08x}','rva':rva,'original_va':pe.OPTIONAL_HEADER.ImageBase+rva,'bytes_sha256':provider.sha(b),'bytes_hex':b.hex(),'size':size,'instructions':[f'{i.address:08x}: {i.mnemonic} {i.op_str}' for i in ins],'inventory_hypothesis':f})
    value={'schema_version':1,'module':'DAOrigins.exe','module_sha256':PIN,'compiler_hypothesis':'VC8/VS2005 SP1; exact original compiler patch unknown','target':'native Windows x86 C++98','functions':functions,
      'instructions_to_author':NATIVE_INSTRUCTIONS}
    if feedback is not None: value['repair_feedback']=feedback
    return value


def prepare_request(value):
    domain=[{'name':f['name'],'id':f"DAOrigins.exe:{PIN}:rva-{f['rva']:08x}"} for f in value['functions']]
    body=provider.encode({'model':'deepseek-flash','messages':[{'role':'system','content':'Return exactly one JSON object, without markdown fences, matching: '+json.dumps(provider.RESPONSE_SCHEMA)},{'role':'user','content':provider.encode(value).decode()}],'thinking':{'type':'enabled'},'reasoning_effort':'low','response_format':{'type':'json_object'},'max_tokens':32768,'stream':False})
    if len(body)>provider.MAX_INPUT_BYTES: raise ValueError('request_cap')
    bindings={'manifest_sha256':provider.sha(provider.encode({'native_pilot':True,'domain':domain})),'packet_sha256':provider.sha(provider.encode(value)),'response_schema_sha256':provider.sha(provider.encode(provider.RESPONSE_SCHEMA)),'request_sha256':provider.sha(body),'function_domain_sha256':provider.sha(provider.encode(domain))}
    maximum=(len(body)+2048)*provider.RATES['uncached']+32768*provider.RATES['output']
    return body,bindings,maximum,domain


def request_packet(folder,value,request_id,ledger_dir=DEFAULT_LEDGER,global_db=DEFAULT_GLOBAL):
    folder=Path(folder); folder.mkdir(parents=True,mode=0o700,exist_ok=False)
    provider.atomic(folder/'packet.json',value)
    body,bindings,maximum,domain=prepare_request(value)
    (folder/'request.json').write_bytes(body); ledger=provider.Ledger(ledger_dir); attempt=None; outcome='transport_error'; usage=None; started=time.time()
    result={'schema_version':1,**bindings,'request_id':request_id,'automatic_retry':False,'requested_model':'deepseek-flash','reasoning_effort':'low','outcome':'interrupted_unknown','validation_status':'native_comparison_pending'}
    provider.atomic(folder/'result.json',result)
    try:
        attempt,day=ledger.reserve(bindings,maximum); result.update(attempt_id=attempt,budget_day=day,reserved_nanodollars=maximum)
        provider.atomic(folder/'result.json',result)
        key=provider.read_regular(Path.home()/'.deepseek.key',4096).decode().strip()
        if not key or not key.isascii() or any(c.isspace() for c in key): raise provider.Refusal('credential_unavailable')
        outcome,raw,http=provider.transport(body,key); del key; result['http_status']=http
        if raw is not None:
            (folder/'raw-response.json').write_bytes(raw); envelope=provider.strict_json(raw); usage=provider.normalized_usage(envelope.get('usage'))
            result['returned_model']=provider.safe_identifier(envelope.get('model'))
            choices=envelope.get('choices')
            if type(choices) is not list or len(choices)!=1: raise ValueError('choice_count')
            choice=choices[0]; result['finish_reason']=provider.safe_identifier(choice.get('finish_reason'))
            if choice.get('message',{}).get('tool_calls') or choice.get('message',{}).get('function_call'): raise ValueError('unexpected_tools')
            if choice.get('finish_reason')!='stop': outcome='invalid_response'
            else:
                try:
                    response=provider.source_response(provider.strict_json(choice['message']['content']),[f['name'] for f in domain])
                    provider.atomic(folder/'response.json',response); source=response['source'].encode(); (folder/'candidate.cpp').write_bytes(source)
                    result.update(source_sha256=provider.sha(source),uncertainties=response['uncertainties']); outcome='success'
                except Exception: outcome='invalid_response'
    except provider.Refusal as exc: result['error']='provider_refusal'
    except Exception as exc: result['error']=type(exc).__name__; outcome='invalid_response'
    finally:
        if attempt:
            result['charged_nanodollars']=ledger.settle(attempt,outcome,usage)
        result.update(outcome=outcome,usage=usage,elapsed_seconds=round(time.time()-started,3))
        provider.atomic(folder/'result.json',result); settle_global(global_db,request_id,'complete' if outcome=='success' else 'error')
    return result


def propose(root,rvas,feedback=None):
    root=Path(root); root.mkdir(parents=True,exist_ok=True,mode=0o700)
    attempts=sorted(root.glob('attempt-*'))
    if len(attempts)>=2: raise RuntimeError('pilot_two_attempt_limit')
    value=packet(rvas,feedback); folder=root/f'attempt-{len(attempts)+1}'
    prepare_request(value)
    request_id,next_cycle=reserve_global(DEFAULT_GLOBAL,'native-'+folder.name)
    if request_id is None: raise RuntimeError('request_budget_wait')
    request_packet(folder,value,request_id)
    return folder

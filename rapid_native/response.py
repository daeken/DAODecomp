"""Native source-only JSON response; identity comes from C++ annotations."""
import re
from workers import deepseek_packet as provider

SOURCE_SCHEMA={'type':'object','properties':{'source':{'type':'string'},'uncertainties':{'type':'array','items':{'type':'string'}}},'required':['source'],'additionalProperties':False}
MARKER=re.compile(r'^\s*//\s*FUNCTION:\s+(\S+)\s+(0x[0-9a-fA-F]+)\s*$',re.M)


def parse_response(value,expected_vas):
    if type(value) is not dict:raise ValueError('native_response_object_required')
    source=value.get('source')
    if type(source) is not str or not source.strip() or len(source.encode())>1024*1024:raise ValueError('native_source_type_or_size')
    uncertainties=value.get('uncertainties',[])
    if type(uncertainties) is not list or any(type(item) is not str for item in uncertainties):raise ValueError('native_uncertainties_type')
    if len(provider.encode(value))>2*1024*1024:raise ValueError('native_response_size')
    markers=MARKER.findall(source)
    if any(target!='DAO' for target,_ in markers):raise ValueError('unexpected_source_marker_target')
    addresses=[int(address,16) for _,address in markers];expected=list(expected_vas)
    if len(expected)!=len(set(expected)) or not expected:raise ValueError('invalid_expected_domain')
    if len(addresses)!=len(set(addresses)):raise ValueError('duplicate_source_marker')
    if len(addresses)!=len(expected) or set(addresses)!=set(expected):raise ValueError('source_marker_domain_mismatch')
    if addresses!=sorted(addresses):raise ValueError('source_marker_order')
    # Ancillary notes from old paid responses are deliberately irrelevant.
    return {'source':source,'uncertainties':uncertainties}


def retained_response(raw,expected_vas):
    if len(raw)>4*1024*1024:raise ValueError('native_envelope_size')
    envelope=provider.strict_json(raw)
    if type(envelope) is not dict:raise ValueError('native_envelope_type')
    choices=envelope.get('choices')
    if type(choices) is not list or len(choices)!=1 or type(choices[0]) is not dict:raise ValueError('native_choices')
    choice=choices[0];message=choice.get('message')
    if choice.get('finish_reason')!='stop':raise ValueError('native_incomplete_response')
    if type(message) is not dict or type(message.get('content')) is not str or message.get('tool_calls') or message.get('function_call'):raise ValueError('native_message')
    return parse_response(provider.strict_json(message['content']),expected_vas),envelope

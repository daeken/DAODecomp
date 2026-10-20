"""Bound retained replayable evidence to a fresh existing comparison, never cl.

The durable C# caller selects jobs, regenerates source and owns publication.
Only private working folders receive reports; public metadata is allowlisted by
that caller. Historical request inputs must still exist unchanged.
"""
import json,re,os
from pathlib import Path
from tools.replayable.encoding_check import parse,digest


def need(ok,reason):
    if not ok:raise ValueError(reason)


def read(project,path):
    p=Path(path)
    need(p.is_absolute() and not any(x.is_symlink() for x in (p,*p.parents)),'export_symlink_or_relative_input')
    normalized=Path(os.path.abspath(p))
    need(any(normalized.is_relative_to(Path(os.path.abspath(root))) and normalized!=Path(os.path.abspath(root)) for root in project['allowed_roots']),'export_input_outside_roots')
    return normalized.read_bytes()


def check(request,folder,source,selected):
    import replayable_adapter as pipeline
    old=selected['request'];result=selected['result'];project=dict(allowed_roots=request['export_read_roots']);job=selected['job_id'];previous=Path(old['project']['replayable']['output_root'])/job
    need(re.fullmatch('[0-9a-f]{32}',job) is not None and old['operation']=='replayable' and old['compile'] is True,'export_replayable_compiled_job')
    need(result['status'] in ('full_match','encoding_equivalent') and result['status']==selected['status'] and result.get('proof') is False,'export_nonaccepting_result')
    need(parse(read(project,previous/'request.json'))==old and parse(read(project,previous/'result.json'))==result,'export_durable_file_binding')
    need(old['rva']==request['rva'] and old['entry']==request['entry'] and old['recipe']==request['recipe'] and old['project']==request['project'],'export_selected_request_binding')
    for path,expected in old['inputs'].items():need(digest(read(project,path))==expected,'export_historical_input_changed')
    names={'candidate.cpp':'source_sha256','build/candidate.obj':'object_sha256','comparison.json':'comparison_sha256','retained-comparison.json':'retained_comparison_sha256','retained-check-request.json':'retained_request_sha256'}
    for path,key in names.items():need(digest(read(project,previous/path))==result[key],'export_historical_artifact_changed')
    for path,key in [('callee-lifts.json','callee_lifts_sha256'),('eh-evidence.json','eh_evidence_sha256')]:
        if key in result:need(digest(read(project,previous/path))==result[key],'export_historical_dependency_changed')
    raw=read(project,previous/'candidate.cpp');need(raw==source.encode()==(folder/'candidate.cpp').read_bytes()==(folder/'build/candidate.cpp').read_bytes(),'export_regenerated_source_changed')
    receipt=parse(read(project,previous/'build/run.json'));need(receipt==parse((folder/'build/run.json').read_bytes()),'export_receipt_copy_changed')
    need(type(receipt['exit_code']) is int and receipt['exit_code']==0 and receipt['linked'] is False and receipt['original_executed'] is False,'export_confirmed_compiler_exit')
    need(read(project,previous/'build/candidate.obj')==(folder/'build/candidate.obj').read_bytes(),'export_object_copy_changed')
    is_batch='group_parent' in old
    if is_batch:
        allowed=('build/run.json','build/compiler.json','build/start.json','build/exit.json','build/build-exit.txt')
        need(set(result['batch_provenance'])==set(allowed) and result['group_job_id']==old['group_parent'],'export_durable_batch_provenance')
        for name in allowed:need(digest(read(project,previous/name))==result['batch_provenance'][name],'export_batch_provenance_changed')
        need('batch' in receipt,'export_batch_receipt_missing')
        pipeline.verify_batch_build(old,previous,receipt)
    else:need('batch' not in receipt and 'batch_provenance' not in result and 'group_job_id' not in result,'export_ordinary_batch_spoof')
    saved=parse(read(project,previous/'retained-check-request.json'))
    for path,expected in saved['inputs'].items():need(digest(read(project,path))==expected,'export_historical_retained_input_changed')
    need(receipt==result['build'],'export_historical_build_receipt_changed')
    need(saved['project']==request['project'] and saved['build']['config']['rva']==old['rva'] and saved['build']['expected_source_sha256']==digest(raw),'export_retained_request_identity')
    need(result['retained_check']['status']==result['status'],'export_historical_gate_disagreement')
    if result['status']=='encoding_equivalent':
        certificate=parse(read(project,previous/'encoding-equivalence.json'))
        need(digest(read(project,previous/'encoding-equivalence.json'))==result['encoding_equivalence_sha256'] and certificate==result['encoding_equivalence']==result['retained_check']['encoding_equivalence'] and result['strict_status']=='mismatch' and result['match_kind']=='encoding_equivalent' and result['proof'] is False,'export_historical_encoding_binding')
    fresh=pipeline.compare_built(request,folder,source)
    need(fresh['status']==result['status'],'export_fresh_comparison_disagrees')
    if fresh['status']=='encoding_equivalent':need(fresh['encoding_equivalence']==result['encoding_equivalence'],'export_fresh_encoding_disagrees')
    for path,expected in old['inputs'].items():need(digest(read(project,path))==expected,'export_historical_input_changed_during_check')
    return fresh

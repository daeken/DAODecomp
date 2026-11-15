"""Propose canonical instruction owners without dropping generated functions.

Every shared PC must have identical independently authenticated original bytes.
This is a registry proposal, not a source/behavioral equivalence certificate.
"""
import argparse
from collections import defaultdict
import gzip
import json
from pathlib import Path
from tools import recomp,recomp_bulk
from tools.daodecomp.pe import fingerprint
from tools.recomp_bulk_build import require_whole_inventory


def propose(compilation):
    inputs=recomp.load(compilation/'inputs.json');generation=Path(inputs['generation_run']);report=recomp.load(generation/'report.json')
    require_whole_inventory(report)
    expected=sum(m['counts'].get('generated_only',0) for m in report['modules'].values())
    if len(inputs['functions'])!=expected or len({(r['module'],r['rva']) for r in inputs['functions']})!=expected:
        raise ValueError('compilation function inventory is incomplete or duplicated')
    if recomp.digest((generation/'report.json').read_bytes())!=inputs['generation_report_sha256']:
        raise ValueError('generation report changed')
    owners={};conflicts=defaultdict(list);ranks={};originals={};cache=generation.parent.parent/'cache'
    for role in ('main','umbra'):
        context=recomp.load(generation/role/'context.json');state=recomp.state(Path(context['project']));binary=recomp.checked_binary(state)
        if state['binary_sha256']!=context['binary_sha256']:raise ValueError('module identity changed')
        originals[role]=(state,binary.read_bytes(),fingerprint(binary))
    for record in inputs['functions']:
        state,image,pe=originals[record['module']];marker=recomp_bulk.load_shard(cache,record['artifact_key'],state['binary_sha256'],record['rva'])
        if marker['status']!='generated_only' or marker['files']['function.cpp']!=record['source_sha256']:raise ValueError('generated function changed')
        data=json.loads(gzip.decompress((cache/record['artifact_key']/'function.json.gz').read_bytes()));name=data['name'];ranks[name]=(-len(data['instructions']),record['rva'],name)
        evidence=dict(symbol=name,artifact_key=record['artifact_key'],source_sha256=record['source_sha256'],metadata_sha256=marker['files']['function.json.gz'],binary_sha256=state['binary_sha256'],module=record['module'])
        for instruction in data['instructions']:
            pc=state['image_base']+instruction['rva'];code=instruction['bytes'];candidate=(code,evidence)
            if pc in owners:
                if not conflicts[pc]:conflicts[pc].append(owners[pc])
                if any(c[0]!=code or c[1]['binary_sha256']!=state['binary_sha256'] or c[1]['module']!=record['module'] for c in conflicts[pc]):
                    raise ValueError('shared instruction differs in original bytes or module identity')
                original=recomp_bulk.read_rva(image,pe,instruction['rva'],len(bytes.fromhex(code)))
                if original!=bytes.fromhex(code):raise ValueError('shared instruction differs from pinned original')
                conflicts[pc].append(candidate)
            else:owners[pc]=candidate
    assignments=[]
    for pc,group in sorted(conflicts.items()):
        candidates=[item[1] for item in group]
        if len({c['symbol'] for c in candidates})!=len(candidates):raise ValueError('instruction repeated within one function')
        owner=min(candidates,key=lambda c:ranks[c['symbol']])['symbol']
        assignments.append(dict(address=pc,instruction_bytes=group[0][0],owner=owner,candidates=sorted(candidates,key=lambda c:c['symbol']),
            rationale='Prefer the body with the most authenticated instructions, then the lowest entry RVA. All functions remain compiled and registered; shared PC bytes are identical.'))
    return dict(schema_version=1,compilation_inputs_sha256=recomp.digest((compilation/'inputs.json').read_bytes()),generation_report_sha256=inputs['generation_report_sha256'],
        assignments=assignments,functions_retained=len(inputs['functions']),instruction_entries=len(owners),shared_instruction_addresses=len(assignments),
        scope='Explicit registry ownership proposal for byte-identical original instructions; no dropped function, source-equivalence proof, function acceptance or game acceptance.',game_acceptance=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--compilation',required=True,type=Path);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    result=propose(args.compilation.absolute());recomp.atomic_json(args.output,result);print(json.dumps({k:result[k] for k in ['functions_retained','instruction_entries','shared_instruction_addresses','game_acceptance']},indent=2))
if __name__=='__main__':main()

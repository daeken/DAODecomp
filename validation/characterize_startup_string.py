"""Execute only the pinned 48-byte original in existing guarded Unicorn backend."""
import json,sys,platform,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.daodecomp.harness import load_json,write_json,file_hash,digest
from tools.daodecomp.leaf import load_slice
from tools.daodecomp.memory import execute_memory
from validation.startup_string_cases import *
from importlib.metadata import version

def main(binary,output):
    row=load_json(ROOT/'evidence/startup-string-identity.json')
    addr,code=load_slice(binary,row['module_sha256'],row['rva'],row['size'],row['code_sha256'])
    rows=[]
    for suite in ('public','heldout'):
        for case in cases(NAME,suite):
            inputs=case['inputs'];arena,readable,writable=fixture(NAME,inputs);wanted,trace=expected(inputs)
            results=[]
            for repeat in range(2):
                result,after,actual=execute_memory(addr,code,arena,registers={},stack_arguments=[inputs['string'],inputs['search']],readable=readable,writable=writable,stack_cleanup=0,instruction_budget=4096,return_trace=True)
                if result!=wanted or after!=arena or actual!=trace:raise RuntimeError(f'characterization mismatch {case["id"]}')
                results.append(digest({'return':result,'arena':after.hex(),'trace':actual}))
            if len(set(results))!=1:raise RuntimeError('nondeterminism')
            rows.append({'case_id':case['id'],'case_sha256':digest(case),'observation_sha256':results[0],'return':result,'ordered_read_count':len(actual)})
    guardrails={}
    arena,readable,writable=fixture(NAME,cases(NAME)[0]['inputs'])
    probes={'no-readable':{'readable':[]},'write-denied':{'code':bytes.fromhex('c60001c3')},'escape':{'code':bytes.fromhex('eb7f')},'budget':{'instruction_budget':1},'wrong-cleanup':{'stack_cleanup':8}}
    for name,change in probes.items():
        args={'registers':{'eax':BASE},'stack_arguments':[BASE,0],'readable':readable,'writable':writable,'stack_cleanup':0,'instruction_budget':4096}
        pcode=change.pop('code',code);args.update(change)
        try:execute_memory(addr,pcode,arena,**args)
        except Exception as exc:guardrails[name]=type(exc).__name__+': '+str(exc)
        else:raise RuntimeError('guardrail accepted '+name)
    report={'schema_version':1,'kind':'original-characterization-not-candidate-acceptance','identity':row['id'],'slice_sha256':hashlib.sha256(code).hexdigest(),'module_sha256':file_hash(binary),'host':{'platform':platform.platform(),'machine':platform.machine(),'python':platform.python_version(),'unicorn':version('unicorn')},'cases':rows,'case_count':len(rows),'original_repeats':2,'guardrails':guardrails,'proof':False,'native_windows_validated':False,'caller_body_executed':False,'artifact_sha256':{str(p.relative_to(ROOT)):file_hash(p) for p in [Path(__file__),ROOT/'tools/daodecomp/memory.py',ROOT/'tools/daodecomp/leaf.py',ROOT/'validation/startup_string_cases.py',ROOT/'evidence/startup-string-identity.json',*[ROOT/f'validation/startup_string_corpus/{NAME}-{s}.json' for s in ('public','heldout')]]}}
    write_json(output,report);print(json.dumps({'case_count':len(rows),'guardrails':guardrails,'host':report['host']}))
if __name__=='__main__':main(sys.argv[1],sys.argv[2])

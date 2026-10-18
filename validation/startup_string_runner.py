"""One fresh process/machine per case; existing strict guest-memory executor unchanged."""
import json,sys,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.daodecomp.harness import load_json
from tools.daodecomp.leaf import load_slice
from tools.daodecomp.memory import execute_memory
from validation.startup_string_cases import fixture,expected,NAME

def main():
    req=load_json_stream()
    function=load_json(ROOT/'evidence/startup-string-identity.json')
    if req['schema_version']!=1 or req['function_id']!=function['id']:raise ValueError('wrong protocol/function')
    inputs=req['case']['inputs'];arena,readable,writable=fixture(NAME,inputs)
    if sys.argv[1]=='original':
        address,code=load_slice(sys.argv[2],function['module_sha256'],function['rva'],function['size'],function['code_sha256'])
        result,after,trace=execute_memory(address,code,arena,registers={},stack_arguments=[inputs['string'],inputs['search']],readable=readable,writable=writable,stack_cleanup=0,instruction_budget=4096,return_trace=True)
        if trace!=expected(inputs)[1]:raise RuntimeError('original ordered reads differ from reviewed characterization')
    elif sys.argv[1]=='candidate':
        p=subprocess.run([sys.argv[2]],input=f"{inputs['arena']} {inputs['string']} {inputs['search']}\n",text=True,capture_output=True,check=True,timeout=3)
        lines=p.stdout.splitlines()
        if len(lines)!=2:raise ValueError('bad native result shape')
        result=int(lines[0]);after=bytes.fromhex(lines[1])
        if len(after)!=256 or not 0<=result<=0xffffffff:raise ValueError('bad result/arena')
        if result and not (readable[0][0]<=result-0x02000000<sum(readable[0]) and (result-inputs['string'])%2==0):raise ValueError('return outside declared units')
    else:raise ValueError('unknown side')
    json.dump({'schema_version':1,'case_id':req['case']['id'],'termination':'return','return':result,'memory':{'arena':after.hex()},'calls':[]},sys.stdout)

def load_json_stream():
    from tools.daodecomp.harness import parse_json
    return parse_json(sys.stdin.read())
if __name__=='__main__':main()

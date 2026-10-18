"""Original-only draft descriptor adapter on unchanged production fresh-child transport."""
import argparse,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.daodecomp.batch import serve
from tools.daodecomp.harness import validate_contract,validate_cases
from tools.daodecomp.memory import ARENA_BASE,execute_memory
from validation.indexed_field_batch_runner import preload_slices

def fixture(function,inputs):
    if type(inputs) is not dict or set(inputs)!={'arena','object','value','entry_eax'}:raise ValueError('input fields')
    for key in ('object','value','entry_eax'):
        if type(inputs[key]) is not int or not 0<=inputs[key]<=0xffffffff:raise ValueError('expectedu32')
    if type(inputs['arena']) is not str:raise ValueError('arena type')
    arena=bytes.fromhex(inputs['arena'])
    if len(arena)!=512 or arena.hex()!=inputs['arena']:raise ValueError('512byte lowercase arena')
    obj=inputs['object'];kind,off,width,_=function['spec']
    def bounded(offset,size):
        if not 0<=offset<offset+size<=512:raise ValueError('bounded footprint')
        return (offset,size)
    if kind in ('store','clamp','constant'):reads=[];writes=[bounded(obj+off,width)]
    elif kind=='store_mark':reads=[];writes=[bounded(obj+off,4),bounded(obj+0x1b9,1)]
    elif kind=='flag_predicate':reads=[bounded(obj+0x99,1),bounded(obj+off,4)];writes=[bounded(obj+0x99,1),bounded(obj+0x119,1)]
    else:reads=[bounded(obj+off,width)];writes=[]
    if not 0<=obj<512:raise ValueError('object offset')
    return arena,reads,writes

class Adapter:
    def __init__(self,binary,mutant=False):
        fs=json.loads((ROOT/'slices.json').read_text());self.functions={f['id']:f for f in fs}
        if len(self.functions)!=len(fs):raise ValueError('duplicate identities')
        self.slices=preload_slices(binary,fs);self.mutant=mutant
        self.contracts={f['id']:json.loads((ROOT/'contracts'/f"{f['name']}.json").read_text()) for f in fs}
        for identity,contract in self.contracts.items():
            validate_contract(contract)
            if contract['function_id']!=identity:raise ValueError('contractidentity')
    def validate_request(self,request):
        if type(request) is not dict or set(request)!={'schema_version','function_id','case'} or type(request['schema_version']) is not int or request['schema_version']!=1 or type(request['function_id']) is not str or request['function_id'] not in self.functions:raise ValueError('requestidentity')
        validate_cases([request['case']],self.contracts[request['function_id']]);fixture(self.functions[request['function_id']],request['case']['inputs'])
    def execute(self,request):
        f=self.functions[request['function_id']];inputs=request['case']['inputs'];arena,reads,writes=fixture(f,inputs)
        address,code=self.slices[f['id']]
        if self.mutant:code=bytes.fromhex(f['mutant_hex'])
        args=[inputs['value']] if f['stack_arguments'] else []
        result,after,regs=execute_memory(address,code,arena,registers={'eax':inputs['entry_eax'],'ecx':ARENA_BASE+inputs['object']},stack_arguments=args,readable=reads,writable=writes,stack_cleanup=4*len(args),return_registers=('ecx',))
        return {'schema_version':1,'case_id':request['case']['id'],'termination':'return','return':result,'memory':{'arena':after.hex(),'exit_ecx':struct.pack('<I',regs['ecx']).hex()},'calls':[]}
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('binary',type=Path);parser.add_argument('--mutant',action='store_true');a=parser.parse_args()
    adapter=Adapter(a.binary,a.mutant);serve(adapter.execute,adapter.validate_request)
if __name__=='__main__':main()

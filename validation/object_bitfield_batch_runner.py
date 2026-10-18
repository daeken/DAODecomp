"""Proposal adapter reusing reviewed batch transport and immutable slice preloader."""
import argparse
import ctypes
from pathlib import Path
import struct
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.daodecomp.batch import serve
from tools.daodecomp.harness import load_json,validate_contract,validate_cases
from tools.daodecomp.memory import ARENA_BASE,execute_memory
from validation.indexed_field_batch_runner import preload_slices
from validation.object_bitfield_cases import SPECS,fixture
from types import MappingProxyType
class MemoryRange(ctypes.Structure):
    _fields_=[('offset',ctypes.c_uint32),('size',ctypes.c_uint32)]
class ObjectBitfieldAdapter:
    def __init__(self,mode,artifact,functions=None):
        fs=functions if functions is not None else [f for f in load_json(ROOT/'analysis/functions.json')['functions'] if f.get('recovery_group')=='object-bitfields-001']
        if len(fs)!=len(SPECS) or {f['name'] for f in fs}!=set(SPECS) or len({f['id'] for f in fs})!=len(fs) or any(f.get('backend')!='object-bitfields-001' for f in fs):
            raise ValueError('registry mismatch')
        self.functions=MappingProxyType({f['id']:f for f in fs});self.mode=mode
        self.contracts=MappingProxyType({f['id']:load_json(ROOT/f['contract']) for f in fs})
        for identity,contract in self.contracts.items():
            validate_contract(contract)
            if contract['function_id']!=identity:raise ValueError('contract mismatch')
        if mode=='original':self.slices=preload_slices(artifact,fs)
        elif mode=='candidate':
            self.library=ctypes.CDLL(str(Path(artifact).resolve()));self.native=self.library.dao_object_bitfield_case
            byteptr=ctypes.POINTER(ctypes.c_uint8);u32ptr=ctypes.POINTER(ctypes.c_uint32);rangeptr=ctypes.POINTER(MemoryRange)
            self.native.argtypes=[ctypes.c_char_p,byteptr,*([ctypes.c_uint32]*4),rangeptr,ctypes.c_uint32,rangeptr,ctypes.c_uint32,u32ptr,u32ptr,byteptr]
            self.native.restype=ctypes.c_int
        else:raise ValueError('invalid side')
    def validate_request(self,request):
        if type(request) is not dict or set(request)!={'schema_version','function_id','case'} or type(request['schema_version']) is not int or request['schema_version']!=1 or type(request['function_id']) is not str or request['function_id'] not in self.functions:raise ValueError('invalid request')
        validate_cases([request['case']],self.contracts[request['function_id']]);fixture(self.functions[request['function_id']]['name'],request['case']['inputs'])
    def execute(self,request):
        f=self.functions[request['function_id']];case=request['case'];inputs=case['inputs'];name=f['name'];kind=SPECS[name][0]
        arena,reads,writes=fixture(name,inputs)
        if self.mode=='original':
            args=[] if kind=='graph' else [ARENA_BASE+inputs['source'] if kind=='copy' else inputs['value']]
            result,after,regs=execute_memory(*self.slices[f['id']],arena,registers={'eax':inputs['entry_eax'],'ecx':ARENA_BASE+inputs['object']},stack_arguments=args,readable=reads,writable=writes,stack_cleanup=len(args)*4,return_registers=('ecx',))
            if kind=='copy':result=(result-ARENA_BASE)&0xffffffff
            ecx=regs['ecx']
        else:
            buf=ctypes.c_uint8*512;before=buf.from_buffer_copy(arena);afterbuf=buf();resultbuf=ctypes.c_uint32();ecxbuf=ctypes.c_uint32()
            readbuf=(MemoryRange*len(reads))(*(MemoryRange(*r) for r in reads));writebuf=(MemoryRange*len(writes))(*(MemoryRange(*r) for r in writes))
            status=self.native(name.encode('ascii'),before,inputs['object'],inputs['value'],inputs['source'],inputs['entry_eax'],readbuf,len(reads),writebuf,len(writes),ctypes.byref(resultbuf),ctypes.byref(ecxbuf),afterbuf)
            if status!=0:raise RuntimeError('native adapter error '+str(status))
            result=resultbuf.value;ecx=ecxbuf.value;after=bytes(afterbuf)
        return {'schema_version':1,'case_id':case['id'],'termination':'return','return':result,'memory':{'arena':after.hex(),'exit_ecx':struct.pack('<I',ecx).hex()},'calls':[]}
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=('original','candidate'));parser.add_argument('artifact',type=Path);parser.add_argument('--case-timeout',type=float,default=5);args=parser.parse_args()
    adapter=ObjectBitfieldAdapter(args.mode,args.artifact);serve(adapter.execute,adapter.validate_request,timeout=args.case_timeout)
if __name__=='__main__':main()

"""Draft original/native mapping using reviewed production fresh-child transport."""
import argparse,ctypes,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.daodecomp.batch import serve
from validation.direct_field_batch_runner import Adapter as OriginalAdapter,fixture
class MemoryRange(ctypes.Structure):
 _fields_=[('offset',ctypes.c_uint32),('size',ctypes.c_uint32)]
class Adapter(OriginalAdapter):
 def __init__(self,mode,artifact):
  self.mode=mode
  if mode=='original':super().__init__(artifact)
  elif mode=='candidate':
   import json
   from tools.daodecomp.harness import validate_contract
   fs=json.loads((ROOT/'slices.json').read_text());self.functions={f['id']:f for f in fs}
   self.contracts={f['id']:json.loads((ROOT/'contracts'/f"{f['name']}.json").read_text()) for f in fs}
   for identity,contract in self.contracts.items():
    validate_contract(contract)
    if contract['function_id']!=identity:raise ValueError('contractidentity')
   self.library=ctypes.CDLL(str(Path(artifact).resolve()));self.native=self.library.dao_direct_object_field_case
   p=ctypes.POINTER(ctypes.c_uint8);u=ctypes.POINTER(ctypes.c_uint32);r=ctypes.POINTER(MemoryRange)
   self.native.argtypes=[ctypes.c_char_p,p,*([ctypes.c_uint32]*3),r,ctypes.c_uint32,r,ctypes.c_uint32,u,u,p];self.native.restype=ctypes.c_int
  else:raise ValueError('mode')
 def execute(self,request):
  if self.mode=='original':return super().execute(request)
  f=self.functions[request['function_id']];inputs=request['case']['inputs'];arena,reads,writes=fixture(f,inputs)
  buffer=ctypes.c_uint8*512;before=buffer.from_buffer_copy(arena);after=buffer();result=ctypes.c_uint32();ecx=ctypes.c_uint32()
  rb=(MemoryRange*len(reads))(*(MemoryRange(*r) for r in reads));wb=(MemoryRange*len(writes))(*(MemoryRange(*w) for w in writes))
  status=self.native(f['name'].encode(),before,inputs['object'],inputs['value'],inputs['entry_eax'],rb,len(reads),wb,len(writes),ctypes.byref(result),ctypes.byref(ecx),after)
  if status:raise RuntimeError('native adapter status '+str(status))
  return {'schema_version':1,'case_id':request['case']['id'],'termination':'return','return':result.value,'memory':{'arena':bytes(after).hex(),'exit_ecx':struct.pack('<I',ecx.value).hex()},'calls':[]}
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=('original','candidate'));parser.add_argument('artifact',type=Path);a=parser.parse_args();adapter=Adapter(a.mode,a.artifact);serve(adapter.execute,adapter.validate_request)
if __name__=='__main__':main()

"""Opt-in immutable preload adapter; execution is always in fresh POSIX children."""
import argparse
import ctypes
import hashlib
import os
from pathlib import Path
import sys
from types import MappingProxyType

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.daodecomp.batch import serve
from tools.daodecomp.harness import load_json, validate_contract, validate_cases
from tools.daodecomp.pe import fingerprint
from tools.daodecomp.memory import ARENA_BASE, execute_memory
from validation.indexed_field_cases import FIELD_SPECS, fixture


def preload_slices(binary, functions):
    """Verify independent fingerprint/data reads and return immutable reviewed bytes."""
    metadata = fingerprint(binary)
    data = Path(binary).read_bytes()
    if (hashlib.sha256(data).hexdigest() != metadata['sha256']
            or metadata['architecture'] != 'x86' or metadata['format'] != 'PE32'):
        raise ValueError('reference module identity or architecture mismatch')
    result = {}
    for function in functions:
        if metadata['sha256'] != function['module_sha256']:
            raise ValueError('reference module hash mismatch')
        rva, size = function['rva'], function['size']
        if type(rva) is not int or type(size) is not int or rva < 0 or size <= 0:
            raise ValueError('invalid reviewed slice range')
        sections = [s for s in metadata['sections'] if s['rva'] <= rva
                    and rva + size <= s['rva'] + min(s['file_size'], s['virtual_size'])]
        if len(sections) != 1:
            raise ValueError('slice is not uniquely file-backed')
        section = sections[0]
        offset = section['file_offset'] + rva - section['rva']
        code = data[offset:offset+size]
        if len(code) != size or hashlib.sha256(code).hexdigest() != function['code_sha256']:
            raise ValueError('instruction slice hash mismatch')
        result[function['id']] = (metadata['image_base']+rva, code)
    return MappingProxyType(result)


class IndexedFieldAdapter:
    def __init__(self, mode, artifact):
        if os.name != 'posix':
            raise RuntimeError('batch adapter requires POSIX; use existing single-case runner')
        fs = [f for f in load_json(ROOT/'analysis/functions.json')['functions']
              if f['name'] in FIELD_SPECS and f.get('recovery_group') == 'indexed-fields-002'
              and f.get('backend') == 'indexed-stores-001']
        if len(fs) != len(FIELD_SPECS) or len({f['id'] for f in fs}) != len(fs):
            raise ValueError('indexed-field registry identity mismatch')
        self.functions = MappingProxyType({f['id']:f for f in fs})
        self.contracts = MappingProxyType({f['id']:load_json(ROOT/f['contract']) for f in fs})
        for identity, contract in self.contracts.items():
            validate_contract(contract)
            if identity != contract['function_id']:
                raise ValueError('contract function identity mismatch')
        self.mode = mode
        if mode == 'original':
            # Load module code only; never construct/emulate a Unicorn machine in
            # the supervisor. Imports are immutable preloads, not saved CPU state.
            import unicorn
            import unicorn.x86_const
            self.slices = preload_slices(artifact, fs)
        elif mode == 'candidate':
            self.library = ctypes.CDLL(str(Path(artifact).resolve()))
            self.native = self.library.dao_indexed_field_case
            ptr = ctypes.POINTER(ctypes.c_uint8)
            self.native.argtypes = [ctypes.c_char_p, ptr, ctypes.c_uint32, ctypes.c_uint32,
                                    ctypes.c_uint32, ctypes.c_uint32,
                                    ctypes.POINTER(ctypes.c_uint32), ptr]
            self.native.restype = ctypes.c_int
        else:
            raise ValueError('invalid side')

    def validate_request(self, request):
        if (type(request) is not dict or set(request) != {'schema_version','function_id','case'}
                or type(request['schema_version']) is not int or request['schema_version'] != 1
                or type(request['function_id']) is not str or request['function_id'] not in self.functions):
            raise ValueError('invalid registered indexed-field request')
        contract = self.contracts[request['function_id']]
        validate_cases([request['case']], contract)
        fixture(self.functions[request['function_id']]['name'], request['case']['inputs'])

    def execute(self, request):
        function = self.functions[request['function_id']]
        name = function['name']; case = request['case']; inputs = case['inputs']
        arena, readable, writable = fixture(name, inputs)
        if self.mode == 'original':
            setter = FIELD_SPECS[name][0] == 'set'
            result, after = execute_memory(*self.slices[function['id']], arena,
                registers={'eax':inputs['entry_eax'],'ecx':ARENA_BASE+inputs['object']},
                stack_arguments=[inputs['index']] + ([inputs['value']] if setter else []),
                readable=readable, writable=writable, stack_cleanup=8 if setter else 4,
                preserved_registers=('ecx',))
        else:
            buffer_type = ctypes.c_uint8 * len(arena)
            before = buffer_type.from_buffer_copy(arena)
            after_buffer = buffer_type()
            returned = ctypes.c_uint32()
            status = self.native(name.encode('ascii'), before, inputs['object'], inputs['index'],
                                 inputs.get('value',0), inputs['entry_eax'], ctypes.byref(returned), after_buffer)
            if status != 0:
                raise RuntimeError(f'native adapter failed with status {status}')
            result, after = returned.value, bytes(after_buffer)
        return {'schema_version':1,'case_id':case['id'],'termination':'return','return':result,
                'memory':{'arena':after.hex()},'calls':[]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('original','candidate'))
    parser.add_argument('artifact',type=Path)
    parser.add_argument('--case-timeout',type=float,default=5)
    args = parser.parse_args()
    adapter = IndexedFieldAdapter(args.mode,args.artifact)
    serve(adapter.execute,adapter.validate_request,timeout=args.case_timeout)

if __name__ == '__main__':
    main()

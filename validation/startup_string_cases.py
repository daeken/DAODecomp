"""Bounded stable ordinary RAM domain. No source-level wchar_t/CRT identity claim."""
import hashlib,json
from pathlib import Path
NAME='fn_004e2d29'
ARENA_SIZE=256
NEGATIVE_NAMES=(NAME,)
BASE=0x02000000

def fixture(name, inputs):
    if name != NAME or set(inputs)!={'arena','string','search'}:raise ValueError('unknown function/input shape')
    if type(inputs['arena']) is not str or len(inputs['arena']) != ARENA_SIZE*2 or any(c not in '0123456789abcdef' for c in inputs['arena']):raise ValueError('arena must be lowercase hex')
    if any(type(inputs[k]) is not int or not 0 <= inputs[k] <= 0xffffffff for k in ('string','search')):raise ValueError('u32 argument required')
    arena=bytes.fromhex(inputs['arena']);start=inputs['string']
    if not BASE <= start < BASE+ARENA_SIZE:raise ValueError('string pointer outside arena')
    off=start-BASE;end=off
    while True:
        if end+2>ARENA_SIZE:raise ValueError('no complete zero terminator in arena')
        word=int.from_bytes(arena[end:end+2],'little');end+=2
        if word==0:break
    return arena,[(off,end-off)],[]

def cases(name,suite='public'):
    if name!=NAME or suite not in ('public','heldout'):raise ValueError('unknown function/suite')
    return json.loads((Path(__file__).parent/'startup_string_corpus'/f'{name}-{suite}.json').read_text())

def negative_cases(name):return cases(name,'public')

def expected(inputs):
    arena,readable,_=fixture(NAME,inputs);off=inputs['string']-BASE;end=off+readable[0][1]-2
    target=inputs['search']&0xffff
    matches=[p for p in range(off,end+1,2) if int.from_bytes(arena[p:p+2],'little')==target]
    result=BASE+matches[-1] if matches else 0
    # Independent expected read trace derived from byte-backed forward scan then backward compare.
    back=end;trace=[('read',p,2) for p in range(off,end+1,2)]
    while back!=off:
        trace.append(('read',back,2))
        if int.from_bytes(arena[back:back+2],'little')==target:break
        back-=2
    trace.append(('read',back,2))
    return result,trace

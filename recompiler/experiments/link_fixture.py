"""Constructed PE32 pair with colliding function RVAs and a named/ordinal export."""
import struct
from recompiler.experiments.call_fixture import make_fixture

CALLER_BASE=0x400000
PROVIDER_BASE=0x30000000
RVA=0x1160
BIAS=PROVIDER_BASE+0x20c0
COUNTER=PROVIDER_BASE+0x2250
TABLE=PROVIDER_BASE+0x20d0


def make_pair(ordinal=False):
    caller,functions,_=make_fixture('fixture_provider.dll','transform')
    caller=bytearray(caller)
    # Follow the IAT call with a real indirect vtable call through provider data.
    # The pointed-to value remains a guest VA; dispatch must select compiled C++.
    args=bytes.fromhex('6a03ff74240cff74240c')
    indirect=args+b'\xb9'+struct.pack('<I',TABLE)+bytes.fromhex('8b01ffd0c3')
    original_size=functions['import']['size']
    start=0x200+RVA-0x1000+original_size-1
    caller[start:start+len(indirect)]=indirect
    functions['import']['size']+=len(indirect)-1
    if ordinal:
        struct.pack_into('<I',caller,0x640,0x80000007)
        struct.pack_into('<I',caller,0x650,0x80000007)
    provider,_,_=make_fixture(base=PROVIDER_BASE)
    provider=bytearray(provider)+bytearray(0x200)
    # Same function RVA as caller; distinct module and VA. Three stack arguments,
    # including a constant third argument from the existing constructed caller.
    code=bytes.fromhex('8b4424046bc003034424080305')+struct.pack('<I',BIAS)
    code+=bytes.fromhex('0305')+struct.pack('<I',COUNTER)+bytes.fromhex('ff05')+struct.pack('<I',COUNTER)+bytes.fromhex('c20c00')
    provider[0x200+RVA-0x1000:0x200+RVA-0x1000+len(code)]=code
    struct.pack_into('<H',provider,0x86,3)
    struct.pack_into('<I',provider,0x98+56,0x4000)
    struct.pack_into('<II',provider,0x98+96,0x3000,0x200)
    struct.pack_into('<I',provider,0x178+40+8,0x300) # BSS tail beyond initialized .idata
    struct.pack_into('<8sIIII',provider,0x178+80,b'.edata',0x200,0x3000,0x200,0x800)
    struct.pack_into('<I',provider,0x178+80+36,0x40000040)
    struct.pack_into('<IIHHIIIIIII',provider,0x800,0,0,0,0,0x3080,7,4,4,0x3040,0x3060,0x3070)
    struct.pack_into('<IIII',provider,0x840,RVA,0x20c0,0x2250,0x20d0)
    provider[0x880:0x895]=b'fixture_provider.dll\0'
    offset=0xa0
    for i,name in enumerate(('transform','bias','counter','vtable')):
        struct.pack_into('<I',provider,0x860+4*i,0x3000+offset)
        struct.pack_into('<H',provider,0x870+2*i,i)
        raw=name.encode()+b'\0'; provider[0x800+offset:0x800+offset+len(raw)]=raw; offset+=len(raw)
    struct.pack_into('<I',provider,0x6c0,11)
    struct.pack_into('<I',provider,0x6d0,PROVIDER_BASE+RVA)
    return bytes(caller),functions['import'],bytes(provider),dict(rva=RVA,size=len(code),annotations={})

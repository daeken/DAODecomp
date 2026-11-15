"""Constructed PE32 integer/call fixture. Not original game evidence."""
import struct

BASE=0x400000
IAT=0x402050
VTABLE=0x403000
STOP=0x12345678


def make_fixture(library="KERNEL32.dll",symbol="MulDiv",base=BASE):
    functions={}
    code=bytearray(b"\xcc"*0x300)
    def put(name,rva,data):
        data=bytes(data)
        code[rva-0x1000:rva-0x1000+len(data)]=data
        functions[name]={"rva":rva,"size":len(data),"annotations":{}}
    def call(at,target): return b"\xe8"+struct.pack("<i",target-at-5)
    push_args=bytes.fromhex("ff742408ff742408")
    put("caller",0x1000,push_args+call(0x1008,0x1040)+bytes.fromhex("83c408c3"))
    put("callee",0x1040,bytes.fromhex("8b44240403442408c3"))
    put("stdcall",0x1060,bytes.fromhex("8b44240403442408c20800"))
    put("stdcall_caller",0x1080,push_args+call(0x1088,0x1060)+b"\xc3")
    put("indirect",0x10a0,push_args+bytes.fromhex("8b01ffd083c408c3"))
    put("tail",0x10c0,b"\xe9"+struct.pack("<i",0x1040-0x10c0-5))
    # mov eax,[esp+4]; test; jz base; dec; push; call self; add esp,4;
    # add eax,1; ret; base: xor eax,eax; ret.
    recursion=bytearray(bytes.fromhex("8b44240485c074104850"))
    recursion+=call(0x10e0+len(recursion),0x10e0)
    recursion+=bytes.fromhex("83c40483c001c331c0c3")
    # The base begins at byte 22; JZ's continuation is byte 8.
    recursion[7]=22-8
    put("recursive",0x10e0,recursion)
    put("unknown",0x1120,bytes.fromhex("b8dec0addeffd0c3"))
    put("stop_jump",0x1140,b"\xe9"+struct.pack("<i",STOP-(base+0x1140)-5))
    import_args=bytes.fromhex("6a03ff74240cff74240c")
    import_call=b"\xff\x15"+struct.pack("<I",base+0x2050)
    put("import",0x1160,import_args+import_call+b"\xc3")
    put("thunk",0x1180,b"\xff\x25"+struct.pack("<I",base+0x2050))
    put("thunk_caller",0x11a0,import_args+call(0x11aa,0x1180)+b"\xc3")
    put("undefined_after_import",0x11c0,import_args+import_call+bytes.fromhex("89c8c3"))
    put("three_args",0x11e0,bytes.fromhex("8b442404034424080344240cc20c00"))

    data=bytearray(0x800)
    data[:2]=b"MZ"; struct.pack_into("<I",data,0x3c,0x80); data[0x80:0x84]=b"PE\0\0"
    struct.pack_into("<HHIIIHH",data,0x84,0x14c,2,0,0,0,0xe0,2)
    opt=0x98; struct.pack_into("<H",data,opt,0x10b)
    struct.pack_into("<I",data,opt+16,0x1000); struct.pack_into("<I",data,opt+28,base)
    struct.pack_into("<II",data,opt+32,0x1000,0x200)
    struct.pack_into("<II",data,opt+56,0x3000,0x200)
    struct.pack_into("<I",data,opt+92,16)
    struct.pack_into("<II",data,opt+96+8,0x2000,40)
    section=opt+0xe0
    struct.pack_into("<8sIIII",data,section,b".text",len(code),0x1000,len(code),0x200)
    struct.pack_into("<I",data,section+36,0x60000020)
    struct.pack_into("<8sIIII",data,section+40,b".idata",0x200,0x2000,0x200,0x600)
    struct.pack_into("<I",data,section+76,0xc0000040)
    data[0x200:0x200+len(code)]=code
    # Import descriptors, lookup array and one live IAT slot.
    struct.pack_into("<IIIII",data,0x600,0x2040,0,0,0x2060,0x2050)
    struct.pack_into("<I",data,0x640,0x2080); struct.pack_into("<I",data,0x650,0x2080)
    lib=library.encode("ascii")+b"\0"; sym=b"\0\0"+symbol.encode("ascii")+b"\0"
    if len(lib)>32 or len(sym)>128: raise ValueError("fixture import name too large")
    data[0x660:0x660+len(lib)]=lib; data[0x680:0x680+len(sym)]=sym
    return bytes(data),functions,bytes(code)

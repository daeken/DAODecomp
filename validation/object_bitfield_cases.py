"""Frozen proposal fixtures for object-bitfields-001; no recovered bodies."""
import json
from pathlib import Path
from tools.daodecomp.memory import ARENA_BASE
SPECS = json.loads((Path(__file__).with_name('object_bitfield_specs.json')).read_text())
def fixture(name, inputs):
    if name not in SPECS or type(inputs) is not dict or set(inputs) != {'arena','object','value','source','entry_eax'}:
        raise ValueError('invalid object-bitfield inputs')
    for k in ('object','value','source','entry_eax'):
        if type(inputs[k]) is not int or not 0 <= inputs[k] <= 0xffffffff:
            raise ValueError('expected u32 '+k)
    if type(inputs['arena']) is not str:
        raise ValueError('invalid arena')
    a=bytes.fromhex(inputs['arena'])
    if len(a)!=512 or inputs['arena'] != a.hex():
        raise ValueError('expected512byte lowercase hex arena')
    def bounded(o,n):
        if not 0 <= o < o+n <= len(a): raise ValueError('invalid footprint')
        return o,n
    def ptr(o):
        bounded(o,4)
        return int.from_bytes(a[o:o+4],'little')
    kind,off,w,mask,cond=SPECS[name];o=inputs['object']
    if o>=512:raise ValueError('invalid object offset')
    if kind=='copy':read=[bounded(inputs['source']+0x10,20)];write=[bounded(o+0x10,20)]
    elif kind=='graph':
        first=ptr(o+0x9c)-ARENA_BASE;second=ptr(first+0x11c)
        if second:read=[bounded(o+0x9c,4),bounded(first+0x11c,4),bounded(second-ARENA_BASE+0x64,1)]
        else:
            fallback=ptr(o+0x98)-ARENA_BASE
            read=[bounded(o+0x9c,4),bounded(first+0x11c,4),bounded(o+0x98,4),bounded(fallback+0x50,1)]
        write=[]
    elif kind=='packed':read=[bounded(o+off,1),bounded(o+0x14e,1)];write=read[:]
    elif kind=='color':read=[bounded(o+0x137,1)];write=[bounded(o+off,w)]
    else:read=[bounded(o+off,w)];write=read[:]
    return a,read,write

NAMES=tuple(SPECS)
NEGATIVE_NAMES=NAMES
CORPUS_FILES={'fn_0052a680-heldout.json': '5dd2cbcda5c8f6ad0d73a8203a60b42bbe8444b1f2652aae3d63b61e4bb2bff9', 'fn_0052a680-public.json': 'f1dadbe7f8b7ac7c885c38e976049d045c06f5d9432b650515d94f169614e541', 'fn_0052a820-heldout.json': 'd91e6cdc625190c8ec1713ff23dbd9a7712b50fa03a5d8a617cb04ea03ae7d80', 'fn_0052a820-public.json': '1332ef495551d9984da78057169f3fd5042e306ef62229459d3d4fb0b4ab3d9b', 'fn_0052a840-heldout.json': '53701a90ca6d10346d348ec7544b1f85b09aa66000e019eb6c1a0ff1ca9074d8', 'fn_0052a840-public.json': 'f6ab09aae176a6af738008eb02b320410bbfc1e1f89a6acedb510f5e176d58e8', 'fn_0052a860-heldout.json': '7ab960fb4137db79894fec0beac9cb1b3cf70a4d189ad16cdbc1f2be1a582d1b', 'fn_0052a860-public.json': 'c4efa394c7f0cdba202a7ec4c97310708f5ad2f75b0d21099594b9cb3796129c', 'fn_0052a950-heldout.json': '9efeee4804001f88267708521acc10f5e652f98891d9430b50ea2cf1834f33ee', 'fn_0052a950-public.json': '43466a314abbba1f753adf8fcf7e5e0691297d9e2e47321b32506812dbd579fe', 'fn_0052a9d0-heldout.json': 'f41c8aabe96edcdfd57f617c90307c05d13644c2c04ef130981af703821dbe3c', 'fn_0052a9d0-public.json': '0250ea2a98202ac3fd95f3d2c3bf49e72231ea8a35616305bbaf805851c9bcd5', 'fn_0052a9f0-heldout.json': '7d9349d4146bbaa4fd2bfb2daf6b8594ac35ab8c3606f31e967026cc2414cab2', 'fn_0052a9f0-public.json': 'b28298057e1141de93aabda4298c004ac22352da7a710201906942299818daca', 'fn_0052aa10-heldout.json': '9781058a5722d5dd3c221b3c51c1304071ead584c5f3a1548398d98409862ced', 'fn_0052aa10-public.json': '7bda0619cdfe59bf718d88a867f0c837f2be375fc4d68090564e689de5ee8db5', 'fn_0052aa30-heldout.json': '9022ae7a3ae5fccfb38e949532b4ceaf470c4426940f7d209e777b1921ac42b1', 'fn_0052aa30-public.json': 'd1257d3fdde5cb24ad4b4d5e68443b477e7761d5e03fa394c643c182c8e23f20', 'fn_0052aa50-heldout.json': '97ca717c04249d18c024b301d54a42a3ac5abfe5bdf131b7563f05a2a528268e', 'fn_0052aa50-public.json': '28b5a8bcdbae6149270766932088ef1f225c799e18c608a285a1d5ff28d2218b', 'fn_0052aa70-heldout.json': 'd5e5288c764944a93d5f5835a94454bc3ba68dae66e9664e41e58a8ce3944acf', 'fn_0052aa70-public.json': '1fc1bbd19d78ad63655a414a472dd62d056975de1c4dc30722cd335ff02931c4', 'fn_0052aa90-heldout.json': '222411f4f32ac8b1e5ae306f62c4ab306198fb8149ec6e9b1e0be1234bf459b0', 'fn_0052aa90-public.json': '9e65e973954b0a5bf14db15af5fe543380d644992740ed6c0c66b7c66525198a', 'fn_0052ab30-heldout.json': '02da693cc9f53f53186b2a6a827d57e10f8ab11263370d0cd4efaaffc961d54c', 'fn_0052ab30-public.json': '6d981a7e92af423f7acc43135f8a106ba4370c925250a38a3bbcba75c4c462a0', 'fn_0052ab70-heldout.json': '60912c5d94c2071bcc30dce4340b75cb475ccbdf6dd4d9c962359b51d4edc9c4', 'fn_0052ab70-public.json': 'cc50d31df5e38d1510143ccf9e9309a4877842813d5415e8b05a43ea03e8ff05', 'fn_0052abe0-heldout.json': 'f3b7643d4af18a7559a1b4890d36f20804f42d82c6939fdb17082b0f5e271d2b', 'fn_0052abe0-public.json': 'dd46a4ceb6dbcbc1799babfe7030da36cfd954aa2a9cbad432a72fdb94c8a294'}
# Raw immutable corpus digests are written by the preparation sealer below.
def cases(name,suite='public'):
    if name not in SPECS or suite not in ('public','heldout'):raise ValueError('unknown function/suite')
    from tools.daodecomp.harness import load_json,file_hash
    path=Path(__file__).with_name('object_bitfield_corpus')/f'{name}-{suite}.json'
    expected=CORPUS_FILES.get(path.name)
    if expected is None or file_hash(path)!=expected:raise ValueError('frozen corpus changed')
    result=load_json(path)
    for case in result:fixture(name,case['inputs'])
    return result

def negative_cases(name):
    return cases(name,'public')

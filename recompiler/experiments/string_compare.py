"""Build constructed native controls for plain and repeated CMPS/SCAS widths."""
import argparse,json
from pathlib import Path
from tools import recomp,recomp_native
from recompiler.experiments.call_fixture import make_fixture
FORMS=[]
for repeat in (0,0xf3,0xf2):
    for scan in (False,True):
        for width in (8,16,32):
            code=(b'\x66' if width==16 else b'')+(bytes([repeat]) if repeat else b'')+bytes([(0xae if scan else 0xa6)+(width!=8)])
            FORMS.append(dict(code=code,width=width,scan=scan,repeat=bool(repeat),not_equal=repeat==0xf2))
def project_at(project):
    image,_,_=make_fixture();image=bytearray(image);functions=[]
    import struct
    struct.pack_into('<I',image,0x98+28,0x31000000)
    for index,form in enumerate(FORMS):
        code=form['code']+b'\xc3';image[0x200+index*32:0x200+index*32+len(code)]=code;functions.append(dict(rva=0x1000+index*32,size=len(code),annotations={}))
    project.mkdir(parents=True,exist_ok=True);binary=project/'string-compare.exe';binary.write_bytes(image)
    recomp.atomic_json(project/'project.json',dict(schema_version=1,revision=0,binary=str(binary),module=binary.name,binary_sha256=recomp.digest(image),image_base=0x31000000,sharp_retro=str(recomp.ROOT.parent/'SharpRetro'),functions=functions))
    return functions

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=recomp.ROOT/'local/recomp/string-compare');args=parser.parse_args();out=args.output.absolute();out.mkdir(parents=True,exist_ok=True)
    project_at(out/'project');generated=recomp.generate(out/'project');view,manifest=recomp.read_view(out/'project',generated['view']);compiler=recomp.ROOT/'local/tools/recomp/llvm-mingw-20261104-ucrt-macos-universal/bin/i686-w64-mingw32-clang++'
    source,library,commands=recomp_native.build_library(out,view,manifest,compiler)
    text='struct StringCase {unsigned width;bool scan,repeat,not_equal;};\nstatic const StringCase string_cases[]={\n'
    for form in FORMS:text+='{'+str(form['width'])+','+','.join(str(form[k]).lower() for k in ['scan','repeat','not_equal'])+'},\n'
    (source/'string_cases.inc').write_text(text+'};\n');driver=out/'string_compare.cpp';driver.write_bytes(Path(__file__).with_suffix('.cpp').read_bytes())
    asm='.text\n.p2align 5\n.globl _string_reference_code\n.def _string_reference_code; .scl 2; .type 32; .endef\n_string_reference_code:\n'
    for form in FORMS:
        for down in (False,True):
            # Enter through a normal C ABI, set DF inside the raw reference,
            # capture flags, then clear DF before returning to C++.
            code=bytes([0xfd if down else 0xfc])+form['code']
            asm+='.byte '+','.join(str(v) for v in code)+'\npushfl\npopl _string_reference_flags\ncld\nret\n.p2align 5,0xcc\n'
    asm+='.byte 195\n';reference=out/'reference.S';reference.write_text(asm);exe=out/'control.exe'
    commands.append(recomp_native.run([compiler,'-std=c++20','-O2','-femulated-tls','-DRECOMP_NATIVE_EXECUTION=1','-static','-I',source,driver,reference,library,'-ladvapi32','-lwinmm','-luser32','-lshell32','-lgdi32','-o',exe],out/'control-build.log'))
    report=dict(status='constructed native control built; execution pending',view=generated['view'],image_sha256=recomp.digest(exe.read_bytes()),build_argv=commands,game_acceptance=False);recomp.atomic_json(out/'build-report.json',report);print(json.dumps(report,indent=2))
if __name__=='__main__':main()

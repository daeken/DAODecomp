"""Construct native x87 conditional moves and integer flag comparisons."""
import argparse,json,struct
from pathlib import Path
from tools import recomp,recomp_native
from recompiler.experiments.call_fixture import make_fixture
FORMS=[dict(code=bytes([first,second])) for first in (0xda,0xdb) for second in range(0xc0,0xe0)]+[dict(code=bytes([first,second])) for first in (0xdb,0xdf) for second in range(0xe8,0xf8)]
def project_at(project):
    original,_,_=make_fixture();image=bytearray(0x4200);image[:0x200]=original[:0x200];image[0x200:]=b'\xcc'*0x4000
    struct.pack_into('<H',image,0x86,1);struct.pack_into('<I',image,0x98+28,0x31000000);struct.pack_into('<I',image,0x98+56,0x5000)
    image[0x98+96:0x98+96+128]=bytes(128);struct.pack_into('<I',image,0x180,0x4000);struct.pack_into('<I',image,0x188,0x4000)
    functions=[]
    for index,form in enumerate(FORMS):
        code=form['code']+b'\xc3';image[0x200+index*32:0x200+index*32+len(code)]=code;functions.append(dict(rva=0x1000+index*32,size=len(code),annotations={}))
    project.mkdir(parents=True,exist_ok=True);binary=project/'x87-flags.exe';binary.write_bytes(image)
    recomp.atomic_json(project/'project.json',dict(schema_version=1,revision=0,binary=str(binary),module=binary.name,binary_sha256=recomp.digest(image),image_base=0x31000000,sharp_retro=str(recomp.ROOT.parent/'SharpRetro'),functions=functions))
    return functions

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=recomp.ROOT/'local/recomp/x87-flags');args=parser.parse_args();out=args.output.absolute();out.mkdir(parents=True,exist_ok=True)
    project_at(out/'project');generated=recomp.generate(out/'project');view,manifest=recomp.read_view(out/'project',generated['view']);compiler=recomp.ROOT/'local/tools/recomp/llvm-mingw-20261104-ucrt-macos-universal/bin/i686-w64-mingw32-clang++'
    source,library,commands=recomp_native.build_library(out,view,manifest,compiler)
    driver=out/'x87_flags.cpp';driver.write_bytes(Path(__file__).with_suffix('.cpp').read_bytes())
    asm='.text\n.p2align 5\n.globl _shift_reference_code\n.def _shift_reference_code; .scl 2; .type 32; .endef\n_shift_reference_code:\n'
    for form in FORMS:
        code=form['code']+b'\xc3';asm+='.byte '+','.join(str(v) for v in code+b'\xcc'*(32-len(code)))+'\n'
    asm+='.byte 195\n';reference=out/'reference.S';reference.write_text(asm);exe=out/'control.exe'
    commands.append(recomp_native.run([compiler,'-std=c++20','-O2','-femulated-tls','-DRECOMP_NATIVE_EXECUTION=1','-static','-I',source,driver,reference,library,'-ladvapi32','-lwinmm','-luser32','-lshell32','-lgdi32','-o',exe],out/'control-build.log'))
    report=dict(status='constructed native control built; execution pending',view=generated['view'],image_sha256=recomp.digest(exe.read_bytes()),build_argv=commands,game_acceptance=False);recomp.atomic_json(out/'build-report.json',report);print(json.dumps(report,indent=2))
if __name__=='__main__':main()

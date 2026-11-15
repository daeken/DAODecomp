"""Build a constructed differential control for integer x87 memory arithmetic and extended stores."""
import argparse
import json
from pathlib import Path
from tools import recomp, recomp_native
from recompiler.experiments.call_fixture import make_fixture

FORMS=[bytes([op,reg<<3,0xc3]) for op in [0xda,0xde] for reg in [0,1,4,5,6,7]]+[bytes.fromhex('db38c3')]


def project_at(project):
    image,_,_=make_fixture();image=bytearray(image);functions=[]
    for index in range(len(FORMS)):
        rva=0x1000+index*16
        image[0x200+index*16:0x203+index*16]=FORMS[index]
        functions.append(dict(rva=rva,size=3,annotations={}))
    project.mkdir(parents=True,exist_ok=True);binary=project/'integer-memory.exe';binary.write_bytes(image)
    recomp.atomic_json(project/'project.json',dict(schema_version=1,revision=0,binary=str(binary),module=binary.name,
        binary_sha256=recomp.digest(image),image_base=0x400000,sharp_retro=str(recomp.ROOT.parent/'SharpRetro'),functions=functions))
    return functions


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=recomp.ROOT/'local/recomp/x87-integer-memory')
    args=parser.parse_args();out=args.output.absolute();out.mkdir(parents=True,exist_ok=True)
    functions=project_at(out/'project');generated=recomp.generate(out/'project')
    view,manifest=recomp.read_view(out/'project',generated['view'])
    cxx=recomp.ROOT/'local/tools/recomp/llvm-mingw-20261104-ucrt-macos-universal/bin/i686-w64-mingw32-clang++'
    source,library,commands=recomp_native.build_library(out,view,manifest,cxx)
    driver=out/'x87_integer_memory.cpp';driver.write_bytes(Path(__file__).with_suffix('.cpp').read_bytes())
    executable=out/'control.exe'
    commands.append(recomp_native.run([cxx,'-std=c++20','-O2','-femulated-tls','-DRECOMP_NATIVE_EXECUTION=1','-static',
        '-I',source,driver,library,'-ladvapi32','-lwinmm','-luser32','-lshell32','-lgdi32','-o',executable],out/'control-build.log'))
    result=dict(status='constructed native control built; execution pending',functions=len(functions),view=generated['view'],
        image_sha256=recomp.digest(executable.read_bytes()),driver_sha256=recomp.digest(driver.read_bytes()),build_argv=commands,
        host='macOS ARM64 cross-compile to Windows i686; no native x86 Windows execution yet',game_acceptance=False)
    recomp.atomic_json(out/'build-report.json',result);print(json.dumps(result,indent=2))


if __name__=='__main__':main()

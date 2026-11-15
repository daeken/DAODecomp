"""Build separate native callback MMX controls; retain the old fixture unchanged."""
import argparse,json
from pathlib import Path
from tools import recomp,recomp_native
from recompiler.experiments.call_fixture import make_fixture


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--baseline',action='store_true');parser.add_argument('--output',type=Path);args=parser.parse_args()
    out=args.output.absolute() if args.output else recomp.ROOT/('local/recomp/callback-baseline-mmx-transport' if args.baseline else 'local/recomp/callback-mmx');out.mkdir(parents=True,exist_ok=True)
    image,functions,_=make_fixture(base=0x31000000);image=bytearray(image);selection=functions['import'];code=bytes(image[0x360:0x360+selection['size']])
    if not args.baseline:code=bytes.fromhex('0fdbd9')+code[:-1]+bytes.fromhex('0febd4c3');image[0x360:0x360+len(code)]=code;selection=dict(selection,size=len(code))
    project=out/'project';project.mkdir(exist_ok=True);binary=project/'callback.exe';binary.write_bytes(image)
    recomp.atomic_json(project/'project.json',dict(schema_version=1,revision=0,binary=str(binary),module=binary.name,binary_sha256=recomp.digest(image),image_base=0x31000000,sharp_retro=str(recomp.ROOT.parent/'SharpRetro'),functions=[selection]))
    generated=recomp.generate(project);view,manifest=recomp.read_view(project,generated['view']);cxx=recomp.ROOT/'local/tools/recomp/llvm-mingw-20261104-ucrt-macos-universal/bin/i686-w64-mingw32-clang++';source,library,commands=recomp_native.build_library(out,view,manifest,cxx)
    (source/'native_callback_entry.hpp').write_bytes((recomp.RUNTIME/'native_callback_entry.hpp').read_bytes());driver=out/'control.cpp';driver.write_bytes((Path(__file__).with_name('native_callback_entry.cpp') if args.baseline else Path(__file__).with_suffix('.cpp')).read_bytes())
    assembly=out/'reference.S';assembly.write_text('.text\n.globl _mmx_callback_reference\n_mmx_callback_reference:\n.byte '+','.join(str(b) for b in code)+'\n')
    commands.append(recomp_native.run([cxx,'-std=c++20','-O2','-femulated-tls','-DRECOMP_NATIVE_EXECUTION=1','-static','-I',source,driver,assembly,library,'-ladvapi32','-lwinmm','-luser32','-lshell32','-lgdi32','-o',out/'control.exe'],out/'control-build.log'))
    report=dict(status='constructed callback control built; execution pending',view=generated['view'],build_argv=commands,baseline=args.baseline,game_acceptance=False);recomp.atomic_json(out/'build-report.json',report);print(json.dumps(report,indent=2))
if __name__=='__main__':main()

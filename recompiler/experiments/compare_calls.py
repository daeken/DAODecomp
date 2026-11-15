"""Synthetic native-x86/candidate call chains and actual Kernel32 MulDiv.

Not DAO/Umbra or whole-game validation. The native reference executes exactly
the constructed x86 bytes supplied to the decompiler, plus Wine's real MulDiv.
"""
import argparse
import json
import os
from pathlib import Path
import platform
import random
import sys

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]; sys.path.insert(0,str(ROOT))
from tools import recomp
from call_fixture import make_fixture,BASE
from compare_wine import run


def values(text,count):
    rows=text.splitlines()
    if len(rows)!=count or any(not row.isdecimal() or not 0<=int(row)<2**32 for row in rows):
        raise ValueError("missing, malformed or extra native call observations")
    return list(map(int,rows))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wine",type=Path,required=True); parser.add_argument("--cc",type=Path,required=True)
    parser.add_argument("--output",type=Path,default=ROOT / "local/recomp/call-comparison")
    parser.add_argument("--wine-prefix",type=Path,default=ROOT / "local/recomp/wine-prefix")
    args=parser.parse_args(); out=args.output.resolve(); out.mkdir(parents=True,exist_ok=True)
    fixture_base=0x30000000 # The original CRT heap occupies the unit fixture's 0x400000 on Wine.
    image,functions,code=make_fixture(base=fixture_base); binary=out / "fixture.exe"; binary.write_bytes(image)
    raw=out / "fixture-text.bin"; raw.write_bytes(code)
    project=out / "project"
    state={"schema_version":1,"revision":0,"binary":str(binary),"module":binary.name,"binary_sha256":recomp.digest(image),
           "image_base":fixture_base,"sharp_retro":str(ROOT.parent / "SharpRetro"),"functions":list(functions.values())}
    recomp.atomic_json(project / "project.json",state); generated=recomp.generate(project)
    view,manifest=recomp.read_view(project,generated["view"])
    cc=args.cc.absolute(); cxx32=cc.parent / "i686-w64-mingw32-clang++"; cxx64=cc.parent / "x86_64-w64-mingw32-clang++"
    original=out / "original.exe"; candidate32=out / "candidate32.exe"; candidate64=out / "candidate64.exe"
    run([cc,"-std=c11","-O2",HERE / "wine_calls_original.c","-Wl,--image-base,0x20000000","-Wl,--disable-dynamicbase","-o",original])
    sources=sorted(view.glob("*.cpp"))
    for compiler,output in ((cxx32,candidate32),(cxx64,candidate64)):
        assembly=[view / "native_abi_call.S"] if compiler==cxx32 else []
        run([compiler,"-std=c++20","-O2","-static","-I",view,HERE / "wine_calls_candidate.cpp",*sources,*assembly,
             "-ladvapi32","-lwinmm","-lshell32","-lgdi32","-o",output])
    # Corrupt only the candidate's known cdecl callee result, not the reference,
    # signatures, import implementation, fixtures or observation comparison.
    mutant_source=out / "mutant-callee.cpp"; text=(view / "fn_00001040.cpp").read_text()
    needle="return fn_00001040_detail::run(s,memory,budget);"
    if text.count(needle)!=2: raise ValueError("mutation site changed; review experiment")
    mutant_source.write_text(text.replace(needle,"auto result=fn_00001040_detail::run(s,memory,budget); s.gpr[0]^=1; return result;"))
    mutant=out / "mutant.exe"
    run([cxx32,"-std=c++20","-O2","-static","-I",view,HERE / "wine_calls_candidate.cpp",
         *[p for p in sources if p.name!="fn_00001040.cpp"],view / "native_abi_call.S",mutant_source,
         "-ladvapi32","-lwinmm","-lshell32","-lgdi32","-o",mutant])
    rng=random.Random(0xc011ab1)
    cases=[{"kind":kind,"first":a,"second":b} for kind in range(8)
           for a,b in [(0,0),(1,1),(2,3),(0x7fffffff,1),(0x80000000,0xffffffff),(0xffffffff,0xffffffff)]
           if kind!=4 or a<=8]
    cases += [{"kind":kind,"first":rng.randrange(9) if kind==4 else rng.getrandbits(32),"second":rng.getrandbits(32)}
              for kind in range(8) for _ in range(30)]
    recomp.atomic_json(out / "cases.json",cases)
    data="".join(f"{c['kind']} {c['first']} {c['second']}\n" for c in cases)
    wine=args.wine.resolve(); env=dict(os.environ,WINEPREFIX=str(args.wine_prefix.resolve()),WINEDEBUG="-all",MVK_CONFIG_LOG_LEVEL="0",WINEDLLOVERRIDES="mscoree,mshtml=")
    win_raw="Z:"+str(raw).replace("/","\\"); results={}
    for name,command in (("original",[wine,original,win_raw]),("candidate32",[wine,candidate32]),("candidate64",[wine,candidate64])):
        repeat=[values(run(command,data=data,env=env),len(cases)) for _ in range(2)]
        if repeat[0]!=repeat[1]: raise ValueError("nondeterministic "+name)
        results[name]=repeat[0]; recomp.atomic_json(out / (name+"-observations.json"),repeat[0])
    if any(value!=results["original"] for value in results.values()): raise ValueError("native/candidate disagreement")
    changed=values(run([wine,mutant],data=data,env=env),len(cases))
    if changed==results["original"]: raise ValueError("callee-result mutation was not detected")
    artifacts=[binary,raw,original,candidate32,candidate64,mutant,mutant_source,*sources,view / "functions.hpp",view / "native_imports.hpp",
               view / "runtime.hpp",HERE / "wine_calls_original.c",HERE / "wine_calls_candidate.cpp",HERE / "call_fixture.py",Path(__file__).resolve(),
               HERE / "compare_wine.py",out / "cases.json",recomp.MODULE_POLICY,cc,cxx32,cxx64,cc.parent / "clang",wine]
    report={"schema_version":1,"status":"synthetic_corpus_agreement","cases":len(cases),"repetitions_per_side":2,
            "view":generated["view"],"binary_sha256":state["binary_sha256"],"host":platform.platform(),
            "fixture_base":fixture_base,
            "wine_version":run([wine,"--version"]).strip(),"compiler":run([cc,"--version"]).splitlines()[0],
            "observations":"raw full EAX; original runner checks outer stack balance; candidate additionally checks guest ESP/return and nonvolatile GPR sentinels",
            "coverage":["cdecl","callee-cleanup calls","indirect guest vtable call","tail jump","bounded recursion",
                        "native Kernel32 MulDiv scalar stdcall bridge","import thunk","live IAT retargeting to translated code"],
            "negative_control":"changed translated callee return; semantic difference detected",
            "limits":["constructed PE32 instruction fixture; no game/DLL function equivalence claim",
                      "original Windows x86 and candidate x86/x64 execute under Wine/Rosetta",
                      "native import coverage is only pointer-free MulDiv; other signatures/callbacks/FP unknown",
                      "native volatile registers/flags are not compared; candidate invalidates ECX/EDX/flags and rejects later reads"],
            "abi_facts":[{"rva":f["rva"],"abi":f["abi"]} for f in manifest["functions"]],
            "artifacts":{str(p):recomp.digest(p.read_bytes()) for p in artifacts}}
    recomp.atomic_json(out / "report.json",report); print(json.dumps(report,indent=2))


if __name__=="__main__": main()

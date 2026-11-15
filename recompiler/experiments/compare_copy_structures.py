"""Wine comparison for the 13-field sequential copy and its guest32 views.

Uses the same exact observation parser/comparison as the earlier leaf experiment.
This is a separate bounded domain, not promotion of its draft registry contract.
"""
import argparse
import json
import os
from pathlib import Path
import platform
import random
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0,str(ROOT))
from tools import recomp
from tools.daodecomp.pe import fingerprint
from compare_wine import PIN, observations, run, encoded_lines

RVA = 0x52ab70
SLICE = "519f2703b79dbe90b39143fd25563eac6b9b300d71d82bfa2d6c165b82c2c4de"


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project",type=Path,default=ROOT / "local/recomp/project")
    parser.add_argument("--output",type=Path,default=ROOT / "local/recomp/wine-structures-copy")
    parser.add_argument("--wine",type=Path,required=True)
    parser.add_argument("--cc",type=Path,required=True)
    parser.add_argument("--wine-prefix",type=Path,default=ROOT / "local/recomp/wine-prefix")
    args=parser.parse_args()
    out=args.output.resolve(); out.mkdir(parents=True,exist_ok=True)
    project=args.project.resolve(); initial=recomp.state(project); binary=recomp.checked_binary(initial)
    if initial["binary_sha256"]!=PIN: raise ValueError("requires the pinned DAO binary")
    view_id=recomp.load(project / "current.json")["view"]
    view,manifest=recomp.read_view(project,view_id)
    if manifest["project_sha256"]!=recomp.digest(recomp.encoded(initial)): raise ValueError("regenerate after edits")
    function=next(f for f in manifest["functions"] if f["rva"]==RVA)
    if not function["structure_lowering"] or sorted(len(o["fields"]) for o in function["structures"])!=[13,13]:
        raise ValueError("expected two observed 13-field guest32 views")
    source=view / "fn_0052ab70.cpp"
    original=out / "original.exe"; candidate=out / "candidate"; sanitized=out / "sanitized"; windows=out / "candidate-win64.exe"
    windows32=out / "candidate-win32.exe"
    cc=args.cc.absolute(); cxx=cc.parent / "x86_64-w64-mingw32-clang++"; cxx32=cc.parent / "i686-w64-mingw32-clang++"
    run([cc,"-std=c11","-O2",HERE / "wine_copy_original.c","-o",original])
    base=["-std=c++20","-O2","-I",view,HERE / "wine_copy_candidate.cpp",source]
    run(["clang++",*base,"-o",candidate])
    run(["clang++",*base,"-fsanitize=address,undefined","-fno-sanitize-recover=all","-o",sanitized])
    run([cxx,*base,"-static","-o",windows])
    run([cxx32,*base,"-static","-o",windows32])
    mutant_source=out / "mutant.cpp"; text=source.read_text(); needle="memory.store(field_address, value, 8);"
    if text.count(needle)!=8: raise ValueError("mutation location changed; review experiment")
    mutant_source.write_text(text.replace(needle,"memory.store(field_address, value ^ 1, 8);",1))
    mutant=out / "mutant"
    run(["clang++","-std=c++20","-O2","-I",view,HERE / "wine_copy_candidate.cpp",mutant_source,"-o",mutant])
    rng=random.Random(0x52ab70)
    cases=sorted({(dst,max(0,min(476,dst+delta)),seed)
                  for dst in (0,1,3,16,200,476) for delta in (-19,-8,-2,-1,0,1,2,8,19)
                  for seed in (0,1,0xffffffff)} |
                 {(rng.randrange(477),rng.randrange(477),rng.getrandbits(32)) for _ in range(100)})
    recomp.atomic_json(out / "cases.json",[{"object":d,"source":s,"seed":seed} for d,s,seed in cases])
    data="".join(f"{d} {s} {seed}\n" for d,s,seed in cases)
    identity=fingerprint(binary); section=next(s for s in identity["sections"] if s["rva"]<=RVA and RVA+103<=s["rva"]+s["file_size"])
    offset=section["file_offset"]+RVA-section["rva"]; code=binary.read_bytes()[offset:offset+103]
    if recomp.digest(code)!=SLICE: raise ValueError("original slice changed")
    sliced=out / "fn_0052ab70.bin"; sliced.write_bytes(code)
    wine=args.wine.resolve(); wine_path="Z:"+str(sliced).replace("/","\\")
    env=dict(os.environ,WINEPREFIX=str(args.wine_prefix.resolve()),WINEDEBUG="-all",MVK_CONFIG_LOG_LEVEL="0",WINEDLLOVERRIDES="mscoree,mshtml=")
    results={}
    for label,command in (("original",[wine,original,wine_path]),("candidate-arm64",[candidate]),
                          ("candidate-win64",[wine,windows]),("candidate-win32",[wine,windows32])):
        repeat=[observations(run(command,data=data,env=env),len(cases)) for _ in range(2)]
        if repeat[0]!=repeat[1]: raise ValueError("nondeterministic "+label)
        results[label]=repeat[0]
        (out / (label+".txt")).write_bytes(encoded_lines(repeat[0]))
    results["sanitized"]=observations(run([sanitized],data=data),len(cases))
    expected=results["original"]
    if any(value!=expected for value in results.values()): raise ValueError("original/candidate disagreement")
    changed=observations(run([mutant],data=data),len(cases))
    if changed==expected: raise ValueError("store-bit mutation was not detected")
    recomp.checked_binary(initial)
    contract=ROOT / "contracts/functions/fn_0052ab70.json"
    artifacts=[binary,source,view / "runtime.hpp",view / "functions.hpp",original,candidate,sanitized,windows,windows32,mutant,mutant_source,
               HERE / "wine_copy_original.c",HERE / "wine_copy_candidate.cpp",Path(__file__).resolve(),HERE / "compare_wine.py",
               cc,cc.parent / "clang",cxx,cxx32,wine,out / "cases.json",contract]
    report={"schema_version":1,"status":"corpus_agreement","module":"DAOrigins.exe","binary_sha256":PIN,
            "rva":RVA,"slice_sha256":SLICE,"view":view_id,"cases":len(cases),"repetitions_per_normal_side":2,
            "structures":function["structures"],"negative_control":"first byte-field store bit corrupted; semantic difference detected",
            "observations":"arena-relative EAX return, raw full ECX, all 512 arena bytes",
            "observation_sha256":recomp.digest(encoded_lines(expected)),"host":platform.platform(),
            "wine_version":run([wine,"--version"]).strip(),"compiler":run(["clang++","--version"]).splitlines()[0],
            "wine_prefix":str(args.wine_prefix.resolve()),
            "reference_compiler":run([cc,"--version"]).splitlines()[0],
            "limits":["Wine WoW64/Rosetta original, Windows x86/x64 candidates, macOS ARM64 normal and ASan/UBSan candidate",
                      "isolated integer/memory slice; class identity, object size and initialization unknown",
                      "overlapping, self and unaligned copies in a bounded corpus; no general equivalence proof",
                      "original flags/stack footprints not compared; existing draft contract is a reference, not promoted"],
            "artifacts":{str(p):recomp.digest(p.read_bytes()) for p in artifacts}}
    recomp.atomic_json(out / "report.json",report)
    print(json.dumps(report,indent=2))


if __name__=="__main__": main()

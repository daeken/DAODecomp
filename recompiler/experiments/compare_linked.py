"""Compare a real synthetic EXE/DLL call with a translated, standalone bundle.

The Windows loader resolves the reference import. Candidates run the recovered
caller/callee with copied data and a rewritten guest IAT, without loading that DLL.
This is infrastructure evidence, not DAO/Umbra behavioral validation.
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
from compare_wine import run


def observations(text,count):
    rows=text.splitlines(); result=[]
    if len(rows)!=count: raise ValueError("missing or extra linked observations")
    for row in rows:
        columns=row.split()
        if len(columns)!=2 or any(not c.isdecimal() or not 0<=int(c)<2**32 for c in columns):
            raise ValueError("malformed linked observation")
        result.append(list(map(int,columns)))
    return result


def selected_project(project,binary,start,end):
    state={"schema_version":1,"revision":0,"binary":str(binary),"module":binary.name,
           "binary_sha256":recomp.digest(binary.read_bytes()),"sharp_retro":str(ROOT.parent / "SharpRetro"),"functions":[]}
    metadata=recomp.export(state,include_data=True); state["image_base"]=metadata["image_base"]
    exports={e["name"]:e["address"] for e in metadata["exports"]}
    address=exports[start]; size=exports[end]-address
    if not 0<size<256: raise ValueError("unexpected experiment function bounds")
    state["functions"]=[{"rva":address-state["image_base"],"size":size,"annotations":{},
                         "contract_status":"synthetic two-word call and shared counter experiment"}]
    recomp.atomic_json(project / "project.json",state)
    return state,exports


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wine",type=Path,required=True); parser.add_argument("--cc",type=Path,required=True)
    parser.add_argument("--output",type=Path,default=ROOT / "local/recomp/link-comparison")
    parser.add_argument("--wine-prefix",type=Path,default=ROOT / "local/recomp/wine-prefix")
    args=parser.parse_args(); out=args.output.resolve(); out.mkdir(parents=True,exist_ok=True)
    # A failed rerun cannot leave an earlier successful report at the same path.
    recomp.atomic_json(out / "report.json",{"status":"in_progress","evidence":"synthetic only"})
    cc=args.cc.absolute(); cxx32=cc.parent / "i686-w64-mingw32-clang++"; cxx64=cc.parent / "x86_64-w64-mingw32-clang++"
    provider=out / "fixture_provider.dll"; implib=out / "fixture_provider.a"; original=out / "original.exe"
    run([cc,"-shared",HERE / "link_provider.s","-Wl,--export-all-symbols","-Wl,--image-base,0x30000000",
         "-Wl,--disable-dynamicbase","-Wl,--out-implib,"+str(implib),"-o",provider])
    run([cc,"-std=c11","-O2",HERE / "link_original.c",HERE / "link_caller.s",implib,
         "-Wl,--export-all-symbols","-Wl,--image-base,0x20000000","-Wl,--disable-dynamicbase","-o",original])
    root=out / "caller-project"; dependency=out / "provider-project"
    caller_state,caller_exports=selected_project(root,original,"experiment_entry","experiment_end")
    provider_state,provider_exports=selected_project(dependency,provider,"translated_transform@8","provider_end")
    generated=recomp.generate(root,linked_modules=[dependency],require_translated_code=True)
    view,manifest=recomp.read_view(root,generated["view"])
    bindings=[b for b in manifest["link"]["bindings"] if b["library"].lower()==provider.name.lower()]
    if len(bindings)!=1 or bindings[0]["status"]!="translated_code": raise ValueError("expected one translated provider binding")
    addresses={"entry":caller_exports["experiment_entry"],"target":provider_exports["translated_transform@8"],
               "slot":bindings[0]["address"],"counter":provider_exports["provider_counter"],"bias":provider_exports["provider_bias"]}
    header=out / "fixture_addresses.hpp"
    header.write_text("#pragma once\n"+"".join(f"inline constexpr unsigned fixture_{name}=0x{value:08x}u;\n" for name,value in addresses.items()))
    sources=sorted(view.glob("*.cpp")); candidates={}
    for name,compiler,flags in (("candidate32",cxx32,["-static"]),("candidate64",cxx64,["-static"]),
                                ("candidate_arm64","clang++",["-fsanitize=address,undefined","-fno-sanitize-recover=all"])):
        executable=out / (name+(".exe" if name!="candidate_arm64" else "")); candidates[name]=executable
        assembly=[view / "native_abi_call.S"] if compiler==cxx32 else []
        libraries=["-ladvapi32","-lwinmm","-lshell32","-lgdi32"] if compiler in (cxx32,cxx64) else []
        run([compiler,"-std=c++20","-O2",*flags,"-I",view,"-I",out,HERE / "link_candidate.cpp",*sources,*assembly,*libraries,"-o",executable])
    function=next(f for f in manifest["functions"] if f["module"]==provider.name)
    source=view / (function["name"]+".cpp"); text=source.read_text()
    needle="return "+function["name"]+"_detail::run(s,memory,budget);"
    if text.count(needle)!=2: raise ValueError("changed callee mutation site")
    mutant_source=out / "mutant.cpp"
    mutant_source.write_text(text.replace(needle,"auto exit="+function["name"]+"_detail::run(s,memory,budget); s.gpr[0]^=1; return exit;"))
    mutant=out / "mutant.exe"
    run([cxx32,"-std=c++20","-O2","-static","-I",view,"-I",out,HERE / "link_candidate.cpp",
         *[s for s in sources if s!=source],view / "native_abi_call.S",mutant_source,"-ladvapi32","-lwinmm","-lshell32","-lgdi32","-o",mutant])
    edges=[0,1,2,0x7fffffff,0x80000000,0xfffffffe,0xffffffff]; rng=random.Random(0x11ab1e)
    cases=[dict(first=a,second=b,count=n) for a in edges for b in edges for n in (1,2)]
    cases += [dict(first=rng.getrandbits(32),second=rng.getrandbits(32),count=1+i%2) for i in range(100)]
    recomp.atomic_json(out / "cases.json",cases)
    data="".join(f"{c['first']} {c['second']} {c['count']}\n" for c in cases)
    wine=args.wine.resolve(); env=dict(os.environ,WINEPREFIX=str(args.wine_prefix.resolve()),WINEDEBUG="-all",MVK_CONFIG_LOG_LEVEL="0",WINEDLLOVERRIDES="mscoree,mshtml=")
    native=[observations(run([wine,original],data=data,env=env),len(cases)) for _ in range(2)]
    if native[0]!=native[1]: raise ValueError("nondeterministic original")
    results={"original":native[0]}; hidden=provider.with_suffix(".dll.hidden")
    provider.rename(hidden)
    try:
        # Executables remain in the same directory; the original DLL is absent.
        for name,executable in candidates.items():
            command=[executable,str(view)] if name=="candidate_arm64" else [wine,executable,"Z:"+str(view).replace("/","\\")]
            repeat=[observations(run(command,data=data,env=env),len(cases)) for _ in range(2)]
            if repeat[0]!=repeat[1] or repeat[0]!=native[0]: raise ValueError("linked disagreement: "+name)
            results[name]=repeat[0]
        changed=observations(run([wine,mutant,"Z:"+str(view).replace("/","\\")],data=data,env=env),len(cases))
        differences=sum(a!=b for a,b in zip(changed,native[0]))
        if not differences: raise ValueError("callee mutation undetected")
    finally:
        hidden.rename(provider)
    for name,value in results.items(): recomp.atomic_json(out / (name+"-observations.json"),value)
    artifacts=[provider,original,implib,header,*candidates.values(),mutant,mutant_source,*sources,
               *[view / p for p in manifest["files"]],HERE / "link_provider.s",HERE / "link_caller.s",
               HERE / "link_original.c",HERE / "link_candidate.cpp",Path(__file__).resolve(),HERE / "compare_wine.py",
               recomp.ROOT / "tools/recomp.py",recomp.ROOT / "tools/recomp_link.py",out / "cases.json",cc,cxx32,cxx64,cc.parent / "clang",wine]
    report={"schema_version":1,"status":"synthetic_corpus_agreement","cases":len(cases),"repetitions_per_side":2,
            "view":generated["view"],"host":platform.platform(),"addresses":addresses,
            "modules":[dict(module=s["module"],sha256=s["binary_sha256"]) for s in (caller_state,provider_state)],
            "wine_version":run([wine,"--version"]).strip(),"compiler":run([cc,"--version"]).splitlines()[0],
            "observations":"full EAX and provider counter; candidate additionally checks IAT, initial BSS/bias, guest return/ESP and nonvolatile GPR sentinels",
            "coverage":["normal Windows loader EXE-to-DLL import in reference","translated inter-module stdcall and return",
                        "module-scoped symbols and module identities","initialized data and zero-filled BSS","shared global state across repeated calls",
                        "candidate execution with original provider DLL absent","ARM64 ASan/UBSan"],
            "negative_control":{"change":"translated callee EAX xor 1","semantic_mismatches":differences},
            "limits":["synthetic modules, not DAO/Umbra function equivalence or game startup",
                      "Windows x86 reference and x86/x64 candidates run under Wine/Rosetta, not native x86 hardware",
                      "candidate maps data at preferred guest addresses; TLS, CRT and DLL entry initialization are not run",
                      "native imports in fixture runtimes are outside selected function paths"],
            "abi_facts":[dict(id=f["id"],abi=f["abi"]) for f in manifest["functions"]],
            "artifacts":{str(p):recomp.digest(p.read_bytes()) for p in artifacts}}
    recomp.atomic_json(out / "report.json",report)
    print(json.dumps({k:v for k,v in report.items() if k not in ("artifacts","abi_facts")},indent=2))


if __name__=="__main__": main()

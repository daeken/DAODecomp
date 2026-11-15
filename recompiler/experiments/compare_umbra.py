"""Bounded original-DLL comparisons for imported Umbra Commander accessors.

Constructed machine states, not initialized visibility scenarios. Contract and
original slice hashes are checked before lifting or execution. No API stubs.
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
from tools.daodecomp.pe import fingerprint
from recompiler.experiments.compare_wine import run

CONTRACT=ROOT / "recompiler/contracts/umbra-commander.json"


def checked_contract(binary):
    contract=recomp.load(CONTRACT); identity=fingerprint(binary)
    if identity["sha256"]!=contract["binary_sha256"] or identity["image_base"]!=contract["image_base"]:
        raise ValueError("Umbra reference identity changed")
    image=binary.read_bytes()
    for function in contract["functions"]:
        rva,size=function["rva"],function["size"]
        sections=[s for s in identity["sections"] if s["rva"]<=rva and rva+size<=s["rva"]+s["file_size"]]
        if len(sections)!=1: raise ValueError("function slice is not unambiguous file-backed code")
        offset=sections[0]["file_offset"]+rva-sections[0]["rva"]
        if recomp.digest(image[offset:offset+size])!=function["slice_sha256"]: raise ValueError("Umbra instruction bytes changed")
    return contract,identity


def cases_for(contract):
    rng=random.Random(0x0ccb1201); cases=[]
    words=[0,1,0xff,0x100,0x7fffffff,0x80000000,0xfffffffe,0xffffffff]
    layouts=[(0,128,512),(1,129,513),(32,32,512),(64,256,512),(128,64,512)]
    branch_rvas={0x5e270,0x5e2c0,0x5e430,0x5e490}
    for kind,function in enumerate(contract["functions"]):
        for object_offset,inner,nested in layouts:
            for word in words:
                for mode in ([0,1,0xffffffff] if function["rva"] in branch_rvas else [0]):
                    cases.append(dict(kind=kind,object=object_offset,inner=inner,nested=nested,mode=mode,word=word,
                                      first=word&255,second=rng.getrandbits(32),seed=rng.getrandbits(32)))
        if function["rva"]==0x5e400:
            # First byte-store aliases the object's inner pointer. A second load
            # must follow its changed value, rather than caching the old pointer.
            for first in (0,1,2,127,128,129,254,255):
                cases.append(dict(kind=kind,object=132,inner=128,nested=512,mode=0,word=0xffffffff,
                                  first=first,second=rng.getrandbits(32),seed=rng.getrandbits(32)))
    return cases


def observations(text,count):
    rows=text.splitlines(); result=[]
    if len(rows)!=count: raise ValueError("missing or extra Umbra observations")
    for row in rows:
        cols=row.split()
        if len(cols)!=11 or any(not x.isdecimal() or not 0<=int(x)<2**32 for x in cols[:10]):
            raise ValueError("malformed register/global observation")
        if len(cols[10])!=2048 or any(c not in "0123456789abcdef" for c in cols[10]):
            raise ValueError("malformed arena observation")
        result.append([*map(int,cols[:10]),cols[10]])
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wine",type=Path,required=True); parser.add_argument("--cc",type=Path,required=True)
    parser.add_argument("--binary",type=Path,default=ROOT / "gamedata/bin_ship/umbra.dll")
    parser.add_argument("--project",type=Path,default=ROOT / "local/recomp/project")
    parser.add_argument("--provider-project",type=Path,default=ROOT / "local/recomp/umbra")
    parser.add_argument("--output",type=Path,default=ROOT / "local/recomp/umbra-commander")
    parser.add_argument("--wine-prefix",type=Path,default=ROOT / "local/recomp/wine-prefix")
    args=parser.parse_args(); out=args.output.resolve(); out.mkdir(parents=True,exist_ok=True)
    recomp.atomic_json(out / "report.json",dict(status="in_progress",evidence="bounded Umbra machine states only"))
    frozen_paths=[CONTRACT,Path(__file__).resolve(),HERE / "compare_wine.py",HERE / "umbra_original.c",
                  HERE / "umbra_invoke.s",HERE / "umbra_candidate.cpp",HERE / "umbra_fixture.h",
                  ROOT / "tools/recomp.py",ROOT / "tools/recomp_link.py",recomp.MODULE_POLICY]
    frozen_inputs={str(p):recomp.digest(p.read_bytes()) for p in frozen_paths}
    binary=args.binary.resolve(); contract,identity=checked_contract(binary)
    root_state=recomp.state(args.project.resolve()); provider_state=recomp.state(args.provider_project.resolve())
    if provider_state["binary_sha256"]!=contract["binary_sha256"]: raise ValueError("provider project identity differs")
    # Stage selections. Successful experiments do not silently promote the
    # accepted registry or overwrite the user's annotated recovery project.
    selections={f["rva"]:f for f in provider_state["functions"]}
    for function in contract["functions"]:
        existing=selections.get(function["rva"])
        if existing and existing["size"]!=function["size"]: raise ValueError("existing selection bounds differ")
        selections.setdefault(function["rva"],dict(rva=function["rva"],size=function["size"],annotations={},
                                                 contract=str(CONTRACT.relative_to(ROOT)),contract_status="bounded experimental machine contract"))
    provider_state=dict(provider_state,functions=sorted(selections.values(),key=lambda f:f["rva"]))
    staged_root=out / "caller-project"; staged_provider=out / "provider-project"
    recomp.atomic_json(staged_root / "project.json",root_state); recomp.atomic_json(staged_provider / "project.json",provider_state)
    generated=recomp.generate(staged_root,linked_modules=[staged_provider]); view,manifest=recomp.read_view(staged_root,generated["view"])
    selected={f["rva"]:f for f in manifest["functions"] if f["module"].lower()=="umbra.dll"}
    for function in contract["functions"]:
        if selected[function["rva"]]["code_sha256"]!=function["instruction_sha256"]:
            raise ValueError("lifted instruction identity changed; review contract")
    data=next(s for s in identity["sections"] if s["name"]==".data")
    header=out / "umbra_contract.hpp"
    header.write_text("#pragma once\n"+f"#define umbra_function_count {len(contract['functions'])}u\n"+
                      f"#define umbra_data_base 0x{identity['image_base']+data['rva']:08x}u\n#define umbra_data_size {data['virtual_size']}u\n"+
                      "static const unsigned umbra_function_rvas[]={"+",".join(hex(f["rva"]) for f in contract["functions"])+"};\n"+
                      "static const unsigned umbra_cleanups[]={"+",".join(str(f["cleanup_bytes"]) for f in contract["functions"])+"};\n")
    cc=args.cc.absolute(); cxx32=cc.parent / "i686-w64-mingw32-clang++"; cxx64=cc.parent / "x86_64-w64-mingw32-clang++"
    original=out / "original.exe"
    run([cc,"-std=c11","-O2","-I",out,HERE / "umbra_original.c",HERE / "umbra_invoke.s","-o",original])
    sources=sorted(view.glob("*.cpp")); candidates={}
    for name,compiler,flags in (("candidate32",cxx32,["-static"]),("candidate64",cxx64,["-static"]),
                                ("candidate_arm64","clang++",["-fsanitize=address,undefined","-fno-sanitize-recover=all"])):
        executable=out / (name+("" if name=="candidate_arm64" else ".exe")); candidates[name]=executable
        assembly=[view / "native_abi_call.S"] if compiler==cxx32 else []
        libraries=["-ladvapi32","-lwinmm","-lshell32","-lgdi32"] if compiler in (cxx32,cxx64) else []
        run([compiler,"-std=c++20","-O2",*flags,"-I",view,"-I",out,"-I",HERE,HERE / "umbra_candidate.cpp",*sources,*assembly,*libraries,"-o",executable])
    cases=cases_for(contract); recomp.atomic_json(out / "cases.json",cases)
    input_data="".join(" ".join(str(case[key]) for key in ("kind","object","inner","nested","mode","word","first","second","seed"))+"\n" for case in cases)
    wine=args.wine.resolve(); env=dict(os.environ,WINEPREFIX=str(args.wine_prefix.resolve()),WINEDEBUG="-all",MVK_CONFIG_LOG_LEVEL="0",WINEDLLOVERRIDES="mscoree,mshtml=")
    win=lambda p:"Z:"+str(p).replace("/","\\")
    results={}
    for name,command in [("original",[wine,original,win(binary)]),*[(name,[path,str(view)] if name=="candidate_arm64" else [wine,path,win(view)]) for name,path in candidates.items()]]:
        repeat=[observations(run(command,data=input_data,env=env),len(cases)) for _ in range(2)]
        recomp.atomic_json(out / (name+"-observations.json"),repeat[0])
        if repeat[0]!=repeat[1]: raise ValueError("nondeterministic "+name)
        if results and repeat[0]!=results["original"]:
            mismatches=[dict(case=case,original=a,candidate=b) for case,a,b in zip(cases,results["original"],repeat[0]) if a!=b]
            recomp.atomic_json(out / (name+"-mismatches.json"),mismatches)
            raise ValueError(f"{name}: {len(mismatches)} semantic mismatches")
        results[name]=repeat[0]
    mutations=[]; mutation_files=[]
    # Independent failures: delegated helper's return and the setResult store.
    # Neither changes the oracle, fixtures, contracts or observation comparator.
    for rva,kind in ((0xc0080,"helper_return"),(0x5e400,"result_store")):
        function=selected[rva]; source=view / (function["name"]+".cpp"); text=source.read_text()
        if kind=="helper_return":
            needle="return "+function["name"]+"_detail::run(s,memory,budget);"
            if text.count(needle)!=2: raise ValueError("changed helper mutation site")
            changed=text.replace(needle,"auto exit="+function["name"]+"_detail::run(s,memory,budget); s.gpr[0]^=1; return exit;")
        else:
            # Keep exact emitted accesses, then corrupt the observable result
            # byte after a completed call, using its original entry pointer.
            needle="return "+function["name"]+"_detail::run(s,memory,budget);"
            if text.count(needle)!=2: raise ValueError("changed store mutation site")
            changed=text.replace(needle,"auto object=std::uint32_t(s.gpr[1]); auto inner=std::uint32_t(memory.load(object,32)); auto exit="+
                                 function["name"]+"_detail::run(s,memory,budget); memory.store(inner+4,memory.load(inner+4,8)^1,8); return exit;")
        mutant_source=out / (kind+".cpp"); mutant_source.write_text(changed); mutant=out / (kind+".exe")
        run([cxx32,"-std=c++20","-O2","-static","-I",view,"-I",out,"-I",HERE,HERE / "umbra_candidate.cpp",
             *[p for p in sources if p!=source],view / "native_abi_call.S",mutant_source,
             "-ladvapi32","-lwinmm","-lshell32","-lgdi32","-o",mutant])
        changed_rows=observations(run([wine,mutant,win(view)],data=input_data,env=env),len(cases))
        mismatches=[i for i,(a,b) in enumerate(zip(results["original"],changed_rows)) if a!=b]
        if not mismatches: raise ValueError("undetected "+kind+" mutation")
        mutations.append(dict(kind=kind,mismatches=len(mismatches),case_indexes=mismatches)); mutation_files.extend([mutant,mutant_source])
    checked_contract(binary)
    if any(recomp.digest(Path(p).read_bytes())!=sha for p,sha in frozen_inputs.items()):
        raise ValueError("experiment inputs changed during execution; rerun the frozen inputs")
    artifacts=[binary,CONTRACT,header,original,*candidates.values(),*mutation_files,*[view / p for p in manifest["files"]],
               HERE / "umbra_original.c",HERE / "umbra_invoke.s",HERE / "umbra_candidate.cpp",HERE / "umbra_fixture.h",
               Path(__file__).resolve(),HERE / "compare_wine.py",ROOT / "tools/recomp.py",ROOT / "tools/recomp_link.py",out / "cases.json",cc,cxx32,cxx64,cc.parent / "clang",wine]
    per_function=[dict(id=f["id"],rva=f["rva"],cases=sum(c["kind"]==i for c in cases),abi=selected[f["rva"]]["abi"],
                       delegated_calls=selected[f["rva"]]["abi"]["transfers"]) for i,f in enumerate(contract["functions"])]
    report=dict(schema_version=1,status="bounded_original_dll_corpus_agreement",cases=len(cases),repetitions_per_side=2,
                view=generated["view"],host=platform.platform(),wine_version=run([wine,"--version"]).strip(),
                compiler=run([cc,"--version"]).splitlines()[0],contract_sha256=recomp.digest(CONTRACT.read_bytes()),
                functions=per_function,link=manifest["link"],mutations=mutations,frozen_inputs=frozen_inputs,
                observations=contract["observations"],scope=contract["scope"],
                limits=["Wine WoW64/Rosetta reference and x86/x64 candidates; native ARM64 candidate with sanitizers; no native x86 hardware corroboration",
                        "constructed valid memory graphs and explicitly controlled global; no claim of initialized Umbra object invariants or visibility scenario",
                        "candidate does not load original DLL or execute its initialization; every selected integer path is executed from supplied machine state",
                        "remaining unselected imports/functions, x87/SSE, native callback/pointer APIs, TLS/SEH and game startup remain unresolved"],
                artifacts={str(p):recomp.digest(p.read_bytes()) for p in artifacts})
    recomp.atomic_json(out / "report.json",report)
    recomp.atomic_json(out / "validated-selections.json",dict(binary_sha256=contract["binary_sha256"],functions=provider_state["functions"],report=str(out / "report.json")))
    print(json.dumps(dict(status=report["status"],cases=len(cases),functions=len(per_function),
                          code_ready=manifest["link"]["code_ready"],incomplete_translated=manifest["link"]["incomplete_translated"],
                          mutations=[dict(kind=m["kind"],mismatches=m["mismatches"]) for m in mutations]),indent=2))


if __name__=="__main__": main()

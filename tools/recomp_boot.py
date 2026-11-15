"""Generate, build and run the current actual startup frontier under Wine.

Every run remains incomplete until initialized gameplay is demonstrated. Original
code bytes are read only by the compiler/lifter; the candidate runs generated C++.
"""
import argparse
import json
import os
import shutil
from pathlib import Path, PureWindowsPath
import re
import subprocess
import struct
import sys
import time
from tools import recomp
from tools.daodecomp.pe import fingerprint

PLAN=recomp.ROOT / "recompiler/startup.json"


def _wine_personal_paths(prefix):
    """Read the two Documents routes, including Wine's active-user expansion.

    This deliberately handles only the string forms needed here. An unknown or
    ambiguous registry export is not evidence of an isolated runtime profile.
    """
    explorer=r"Software\Microsoft\Windows\CurrentVersion\Explorer"
    sections={explorer+r"\Shell Folders":"shell",explorer+r"\User Shell Folders":"user",
              "Volatile Environment":"environment"}
    sections={key.replace("\\","\\\\").casefold():value for key,value in sections.items()}
    values={};seen=set();section=None
    registry=prefix/"user.reg"
    if registry.is_symlink() or not registry.is_file():
        raise ValueError("runtime Documents requires a direct Wine user.reg")
    for line in registry.read_text(encoding="utf-8").splitlines():
        header=re.fullmatch(r"\[([^]]+)\](?:\s+\d+)?",line)
        if header:
            section=sections.get(header[1].casefold())
            if section is not None:
                if section in seen: raise ValueError("duplicate runtime profile registry section")
                seen.add(section)
            continue
        if section is None or not line.startswith('"'): continue
        name,separator,value=line.partition("=")
        wanted='"USERPROFILE"' if section=="environment" else '"Personal"'
        if name.casefold()!=wanted.casefold(): continue
        if not separator or section in values:
            raise ValueError("ambiguous runtime profile registry value")
        if value.startswith("str(2):"): value=value[len("str(2):"):]
        try: decoded=json.loads(value)
        except (ValueError,TypeError) as exc:
            raise ValueError("unsupported runtime profile registry string") from exc
        if not isinstance(decoded,str) or any(ord(c)<32 for c in decoded):
            raise ValueError("invalid runtime profile registry string")
        values[section]=decoded
    if not {"shell","user"}<=values.keys():
        raise ValueError("Wine Documents registry routes are missing")
    resolved={}
    for name in ("shell","user"):
        value=values[name]
        if "%" in value:
            profile=values.get("environment")
            if not profile: raise ValueError("Wine active USERPROFILE is unknown")
            value=re.sub(r"%USERPROFILE%",lambda _:profile,value,flags=re.IGNORECASE)
        path=PureWindowsPath(value)
        if "%" in value or path.drive.casefold()!="c:" or not path.is_absolute() or ".." in path.parts:
            raise ValueError("unsupported Wine Documents registry route")
        resolved[name]=str(path)
    return resolved


def checked_startup_profile(prefix,process_state):
    """Check the owned directory and both offline Wine Documents routes."""
    contract=process_state.get("filesystem_profile")
    if contract is None: return None
    relative=contract.get("documents_relative")
    if not isinstance(relative,str) or not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise ValueError("invalid runtime Documents profile path")
    directory=prefix / relative
    if directory.is_symlink() or not directory.is_dir() or not directory.resolve().is_relative_to(prefix.resolve()):
        raise ValueError("runtime Documents must be a direct directory inside the configured Wine prefix")
    parts=Path(relative).parts
    if not parts or parts[0]!="drive_c":
        raise ValueError("runtime Documents must map to the Wine C drive")
    expected=PureWindowsPath("C:/",*parts[1:])
    configured=contract.get("windows_personal_path",str(expected))
    if not isinstance(configured,str) or PureWindowsPath(configured)!=expected:
        raise ValueError("configured Windows Documents path differs from its owned directory")
    routes=_wine_personal_paths(prefix)
    if any(PureWindowsPath(value)!=expected for value in routes.values()):
        raise ValueError("Wine Documents registry routes differ from the configured owned directory")
    return dict(contract,wine_prefix=str(prefix.resolve()),documents_directory=str(directory.resolve()),
                registry_personal_paths=routes,
                validation_scope="Offline directory and registry routes checked; runtime shell API resolution is separate evidence")


def advance_frontier(out,plan,projects,inventories):
    """Select observed missing entries using pinned byte-checked range hypotheses."""
    prior=recomp.load(out / "last-execution.json")
    additions=[]
    states={role:recomp.state(path) for role,path in projects.items()}
    ranges={}
    for role,state in states.items():
        image=recomp.checked_binary(state).read_bytes()
        optional=struct.unpack_from("<I",image,0x3c)[0]+24
        ranges[role]=(state["image_base"],struct.unpack_from("<I",image,optional+56)[0])
    for run in prior["runs"]:
        event=run["events"][-1]; role=run["module"]
        if event.get("reason") not in ("untranslated guest code/import target","untranslated guest function target"): continue
        address=event["pc"]
        # A missing target can be in either translated module after a cross-call.
        owner=next((r for r,(base,size) in ranges.items() if base<=address<base+size),None)
        if owner is None: raise ValueError(f"missing target {address:#x} has no selected module owner")
        state=states[owner]; rva=address-state["image_base"]
        if any(f["rva"]==rva for f in plan["roles"][owner]["functions"]): continue
        index_path=inventories[owner]; index=recomp.load(index_path)
        if index["module_sha256"].lower()!=state["binary_sha256"]: raise ValueError("inventory module identity changed")
        matches=[f for f in index["functions"] if f["rva"]==rva]
        if len(matches)!=1 or not matches[0]["body_ranges"]:
            raise ValueError(f"missing target {address:#x} needs reviewed discovery bounds")
        hypothesized=matches[0]; bounds=hypothesized["body_ranges"]
        if min(b["start_rva"] for b in bounds)!=rva: raise ValueError("inventory range starts before entry")
        end=max(b["end_rva_inclusive"] for b in bounds)+1
        if any(any(b["start_rva"]<=f["rva"]<=b["end_rva_inclusive"] for b in bounds)
               for f in index["functions"] if f["rva"]!=rva):
            raise ValueError("inventory owned ranges cross another function entry; review bounds")
        size=end-rva; pe=fingerprint(Path(state["binary"])); image=Path(state["binary"]).read_bytes()
        sections=[s for s in pe["sections"] if s["rva"]<=rva and rva+size<=s["rva"]+s["file_size"]]
        if len(sections)!=1: raise ValueError("inventory bounds exceed original file-backed bytes")
        offset=sections[0]["file_offset"]+rva-sections[0]["rva"]
        selection=dict(rva=rva,size=size,purpose="observed startup target; "+hypothesized["name"],
                       ranges=[dict(rva=b["start_rva"],size=b["end_rva_inclusive"]-b["start_rva"]+1) for b in bounds],
                       slice_sha256=recomp.digest(image[offset:offset+size]),inventory=str(index_path),
                       inventory_sha256=recomp.digest(index_path.read_bytes()),
                       bounds_status="traversal envelope of static range hypotheses, including gaps; actual reachable decode/lift must succeed",
                       inventory_body_ranges=bounds,
                       contract_status="startup exploration; process state and native boundaries incomplete")
        plan["roles"][owner]["functions"].append(selection)
        plan["roles"][owner]["functions"].sort(key=lambda f:f["rva"]); additions.append(dict(module=owner,rva=rva,size=size))
    if additions: recomp.atomic_json(PLAN,plan)
    return additions


def prepare(project, role):
    state=recomp.state(project); binary=recomp.checked_binary(state); pe=fingerprint(binary)
    if state["module"]!=role["module"] or state["binary_sha256"]!=role["binary_sha256"] or pe["entry_rva"]!=role["entry_rva"]:
        raise ValueError("startup project differs from pinned module/entry identity")
    functions={f["rva"]:f for f in state["functions"]}; image=binary.read_bytes()
    for selection in role["functions"]:
        rva,size=selection["rva"],selection["size"]
        sections=[s for s in pe["sections"] if s["rva"]<=rva and rva+size<=s["rva"]+s["file_size"]]
        if len(sections)!=1: raise ValueError("startup slice is not uniquely file-backed")
        offset=sections[0]["file_offset"]+rva-sections[0]["rva"]
        if recomp.digest(image[offset:offset+size])!=selection["slice_sha256"]: raise ValueError("startup bytes changed")
        if rva in functions:
            if functions[rva]["size"]!=size: raise ValueError("startup bounds conflict with existing annotations")
        else:
            if any(a["rva"]<b["rva"]+b["size"] and b["rva"]<a["rva"]+a["size"]
                   for a in (selection.get("ranges") or [selection]) for f in functions.values() for b in (f.get("ranges") or [f])):
                raise ValueError("startup selection overlaps another function")
            functions[rva]=dict(rva=rva,size=size,annotations={},contract="recompiler/startup.json",
                                ranges=selection.get("ranges"),contract_status=selection["contract_status"])
        # Selection metadata belongs to this reviewed plan; variable annotations
        # remain attached to their existing instruction-origin identities.
        functions[rva]["extra_entries"]=selection.get("extra_entries",[])
    return dict(state,functions=sorted(functions.values(),key=lambda f:f["rva"]),
                data_regions=role.get("data_regions",[]))


def execute(argv, *, output=None, env=None, timeout=180):
    result=subprocess.run(list(map(str,argv)),capture_output=True,text=True,env=env,timeout=timeout)
    if output:
        output.with_suffix(".stdout").write_text(result.stdout)
        output.with_suffix(".stderr").write_text(result.stderr)
    if result.returncode: raise RuntimeError(f"build exited {result.returncode}: {result.stderr[-3000:]}")
    return result.stdout


def build_startup_cache(out,view,manifest,args,implib=None):
    """Keep stable source paths/mtimes, while immutable views remain the inputs."""
    requested=getattr(args,"build_generator","auto")
    generator=("Ninja" if shutil.which("ninja") else "Unix Makefiles") if requested=="auto" else requested
    if generator=="Ninja" and not shutil.which("ninja"):
        raise ValueError("Ninja build generator was requested but is unavailable")
    source=out / "native-source"; source.mkdir(exist_ok=True)
    previous=recomp.load(source / "managed-files.json") if (source / "managed-files.json").exists() else []
    for name in previous:
        if name not in manifest["files"] and Path(name).name==name: (source / name).unlink(missing_ok=True)
    for name,sha in manifest["files"].items():
        if name=="CMakeLists.txt": continue
        target=source / name
        if not target.exists() or recomp.digest(target.read_bytes())!=sha: target.write_bytes((view / name).read_bytes())
    text=(view / "CMakeLists.txt").read_text()
    # CMake quotes, not shell strings. Paths remain structured argv everywhere.
    quote=lambda path:'"'+str(path).replace('\\','/').replace('"','\\"')+'"'
    # Every generated function includes the same machine-state runtime. Cache
    # its parsed headers when rebuilding a large bundle after ISA changes.
    text+='\ntarget_precompile_headers(recomp_generated PRIVATE '+quote(source / "runtime.hpp")+')\n'
    text+='\nadd_executable(recomp_startup '+quote(recomp.RUNTIME / "startup_main.cpp")+')\n'
    text+='target_link_libraries(recomp_startup PRIVATE recomp_generated advapi32'+(' '+quote(implib) if implib else '')+')\n'
    text+='target_link_options(recomp_startup PRIVATE -static -Wl,--image-base,0x20000000)\n'
    from tools.recomp_live import identity_header
    identity=source / 'live_identity.hpp'; identity_text=identity_header(manifest,args.cxx)
    if not identity.exists() or identity.read_text()!=identity_text: identity.write_text(identity_text)
    text+='target_compile_definitions(recomp_startup PRIVATE RECOMP_LIVE_CANDIDATES=1)\n'
    text+='set_target_properties(recomp_startup PROPERTIES RUNTIME_OUTPUT_DIRECTORY '+quote(out)+')\n'
    if args.flat_memory:
        text+='target_compile_definitions(recomp_startup PRIVATE RECOMP_FLAT_MEMORY=1 RECOMP_MAIN_IMAGE_SIZE='+str(manifest['modules'][0]['image_size'])+')\n'
    cmake=source / "CMakeLists.txt"
    if not cmake.exists() or cmake.read_text()!=text: cmake.write_text(text)
    recomp.atomic_json(source / "managed-files.json",list(manifest["files"]))
    compiler=args.cxx.absolute()
    # Make's generated flags.make contains per-source PCH options. Adding a
    # function changes it and rebuilds every object/PCH. Ninja keeps stable
    # compile edges for existing functions; use a distinct generator cache.
    prefix="native-build-ninja-" if generator=="Ninja" else "native-build-"
    build=out / (prefix+recomp.digest(str(compiler).encode())[:12])
    # Guest PCs and immutable generated sources provide startup diagnostics.
    # Full compiler debug records made this exploratory bundle hundreds of MiB;
    # retain the existing optimization/assertion flags without those records.
    commands=[["cmake","-S",source,"-B",build,"-G",generator,"-DCMAKE_BUILD_TYPE=RelWithDebInfo",
               "-DCMAKE_CXX_FLAGS_RELWITHDEBINFO=-O2 -g0 -DNDEBUG","-DCMAKE_SYSTEM_NAME=Windows",
               "-DRECOMP_NATIVE_EXECUTION=OFF", # Legacy strict explorer; native process launcher is separate.
               "-DCMAKE_CXX_COMPILER="+str(compiler),"-DCMAKE_AR="+str(compiler.parent / "llvm-ar"),"-DCMAKE_RANLIB="+str(compiler.parent / "llvm-ranlib")],
              ["cmake","--build",build,"--target","recomp_startup","--parallel","2"]]
    for i,command in enumerate(commands): execute(command,output=out / ("incremental-build-"+str(i)),timeout=1200 if i else 240)
    return out / "recomp_startup.exe",build / "librecomp_generated.a",commands


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project",type=Path,default=recomp.ROOT / "local/recomp/project")
    parser.add_argument("--umbra-project",type=Path,default=recomp.ROOT / "local/recomp/umbra")
    parser.add_argument("--output",type=Path,default=recomp.ROOT / "local/recomp/startup")
    parser.add_argument("--wine",type=Path,default=recomp.ROOT / "local/tools/recomp/Wine Stable.app/Contents/Resources/wine/bin/wine")
    parser.add_argument("--cxx",type=Path,default=recomp.ROOT / "local/tools/recomp/llvm-mingw-20261104-ucrt-macos-universal/bin/i686-w64-mingw32-clang++")
    parser.add_argument("--build-generator",choices=("auto","Ninja","Unix Makefiles"),default="auto",help="prefer Ninja for incremental startup builds when available; keep separate generator caches")
    parser.add_argument("--wine-prefix",type=Path,default=recomp.ROOT / "local/recomp/wine-prefix")
    parser.add_argument("--budget",type=int,default=1000000)
    parser.add_argument("--game-argument",action="append",default=[],help="argument for the logical game command line (repeatable)")
    parser.add_argument("--flat-memory",action=argparse.BooleanOptionalAction,default=True,help="reserve actual guest addresses and use checked native data backing")
    parser.add_argument("--advance",action="store_true",help="select observed missing code targets from pinned inventory hypotheses before building")
    parser.add_argument("--call-depth",type=int,default=0,help="with --advance, also select individually translatable direct-call helpers to this depth (0 disables static expansion)")
    parser.add_argument("--call-limit",type=int,default=64,help="maximum optional helper lift attempts per direct-call expansion")
    parser.add_argument("--call-seeds",choices=("reached","selected"),default="reached",help="expand from newly reached entries, or explicitly explore all startup-plan function bodies (including unexecuted constructors)")
    parser.add_argument("--trace-memory",action="store_true",help="retain a bounded diagnostic history of main-image stores and node-management reads")
    parser.add_argument("--native-trace-limit",type=int,default=0,help="log the first N native calls, every 10000th call and failures; zero logs all calls (execution is unchanged)")
    parser.add_argument("--run-timeout",type=int,default=60,help="maximum seconds per bounded Wine process")
    parser.add_argument("--live",action="store_true",help="pause at missing code and add verified generated candidate DLLs; runtime changes still require a cold run")
    parser.add_argument("--live-reviewed",type=Path,action="append",default=[],help="explicit reviewed missing-inventory bounds report containing binary_sha256 and selection")
    parser.add_argument("--live-limit",type=int,default=128,help="maximum candidate DLL additions in a retained-state session")
    parser.add_argument("--live-wait-for-review",action=argparse.BooleanOptionalAction,default=True,help="keep startup paused while an explicit bounds response is prepared under live-review/")
    parser.add_argument("--mode",choices=("all","main","umbra","combined"),default="all",help="choose a startup composition; combined runs translated Umbra attach before main in one process")
    parser.add_argument("--main-inventory",type=Path,default=recomp.ROOT / "local/analysis/functions.json")
    parser.add_argument("--umbra-inventory",type=Path,default=recomp.ROOT / "local/recomp/startup/umbra-analysis/functions.json")
    args=parser.parse_args(argv); out=args.output.resolve(); out.mkdir(parents=True,exist_ok=True)
    if args.budget<=0: parser.error("instruction budget must be positive")
    if not 0<=args.native_trace_limit<=1000000 or args.run_timeout<=0: parser.error("invalid trace limit or run timeout")
    if not 0<=args.call_depth<=8 or not 1<=args.call_limit<=512: parser.error("invalid direct-call discovery budget")
    if args.call_depth and not args.advance: parser.error("--call-depth requires --advance")
    if args.call_seeds=="selected" and not args.call_depth: parser.error("--call-seeds selected requires --call-depth")
    if args.live and args.mode=="all": parser.error("--live requires one of --mode main, umbra or combined")
    if not 1<=args.live_limit<=512: parser.error("invalid retained-state candidate limit")
    if args.live_reviewed and not args.live: parser.error("--live-reviewed requires --live")
    with recomp.locked(out / "run-lock"):
        recomp.atomic_json(out / "latest.json",dict(status="running",game_started=False))
        try:
            plan=recomp.load(PLAN); selected={}
            checked_profile=checked_startup_profile(args.wine_prefix.resolve(),plan["process_state"])
            projects={"main":args.project.resolve(),"umbra":args.umbra_project.resolve()}
            inventories={"main":args.main_inventory.resolve(),"umbra":args.umbra_inventory.resolve()}
            additions=advance_frontier(out,plan,projects,inventories) if args.advance else []
            call_expansion=None
            if args.call_depth:
                from tools.recomp_reachability import expand_direct_calls
                plan_snapshot=PLAN.read_bytes()
                seeds=additions
                if args.call_seeds=="selected":
                    seeds=[*additions,*[dict(module=role,rva=f["rva"]) for role in projects for f in plan["roles"][role]["functions"]
                                       if not any(a["module"]==role and a["rva"]==f["rva"] for a in additions)]]
                expansion=expand_direct_calls(plan,projects,inventories,seeds,args.call_depth,args.call_limit)
                expansion["seed_mode"]=args.call_seeds
                expansion_path=out / "call-expansion" / (recomp.digest(recomp.encoded(expansion))+".json")
                if expansion_path.exists():
                    if expansion_path.read_bytes()!=recomp.encoded(expansion): raise ValueError("immutable call-discovery report changed")
                else: recomp.atomic_json(expansion_path,expansion)
                recomp.atomic_json(out / "call-expansion.json",expansion)
                if expansion["accepted"]:
                    if PLAN.read_bytes()!=plan_snapshot: raise ValueError("startup plan changed during direct-call discovery")
                    recomp.atomic_json(PLAN,plan)
                call_expansion=dict(report=str(expansion_path),accepted=len(expansion["accepted"]),
                                    deferred=len(expansion["deferred"]),truncated=expansion["truncated"])
            for role,project in (("main",args.project.resolve()),("umbra",args.umbra_project.resolve())):
                selected[role]=prepare(project,plan["roles"][role])
                recomp.atomic_json(out / (role+"-project") / "project.json",selected[role])
            generated=recomp.generate(out / "main-project",linked_modules=[out / "umbra-project"])
            view,manifest=recomp.read_view(out / "main-project",generated["view"])
            from tools import recomp_imports
            import_coverage=recomp_imports.coverage(manifest,recomp.load(recomp_imports.CATALOG),
                                                    recomp_imports.read_bindings(view / "native-bindings.json"))
            import_coverage["view"]=generated["view"]
            import_coverage["catalog_sha256"]=recomp.digest(recomp_imports.CATALOG.read_bytes())
            recomp.atomic_json(out / "import-coverage.json",import_coverage)
            placeholder_artifacts=[]
            implib=None
            if args.flat_memory:
                image=manifest["modules"][0]
                if image["image_base"]!=0x400000 or image["image_size"]<=4096:
                    raise ValueError("startup reservation DLL currently requires the pinned EXE base")
                assembly=out / "guestspace.s"; obj=out / "guestspace.obj"; implib=out / "guestspace.a"; placeholder=out / "recomp_guestspace.dll"
                assembly.write_text(".bss\n.globl _recomp_guestspace_marker\n_recomp_guestspace_marker:\n    .space "+str(image["image_size"]-4096)+"\n")
                execute([args.cxx.absolute(),"-c",assembly,"-o",obj],output=out / "placeholder-assemble")
                execute([args.cxx.absolute().parent / "lld-link","/dll","/noentry","/safeseh:no","/machine:x86","/base:0x400000","/dynamicbase:no",
                         "/export:recomp_guestspace_marker,DATA","/out:"+str(placeholder),"/implib:"+str(implib),obj],output=out / "placeholder-build")
                placeholder_artifacts=[assembly,obj,implib,placeholder]
            executable,library,build_commands=build_startup_cache(out,view,manifest,args,implib)
            game_path=recomp.checked_binary(selected["main"])
            game_module_path="Z:"+str(game_path).replace("/","\\")
            game_command_line=subprocess.list2cmdline([game_module_path,*args.game_argument])
            env=dict(os.environ,WINEPREFIX=str(args.wine_prefix.resolve()),WINEDEBUG="-all",MVK_CONFIG_LOG_LEVEL="0",WINEDLLOVERRIDES="mscoree,mshtml=",RECOMP_GAME_COMMAND_LINE=game_command_line,RECOMP_MAIN_MODULE_PATH=game_module_path,RECOMP_TRACE_MEMORY="1" if args.trace_memory else "0",RECOMP_NATIVE_TRACE_LIMIT=str(args.native_trace_limit))
            runs=[]; live_session=None
            fp_text=lambda role: ":".join(format(plan["process_state"]["floating_point_entry"][role][key],"x") for key in ("x87_control","x87_status","x87_tag","mxcsr"))
            for role in (("main","umbra","combined") if args.mode=="all" else (args.mode,)):
                role_env=dict(env,RECOMP_FP_ENTRY=fp_text("umbra" if role=="combined" else role),RECOMP_MAIN_FP_ENTRY=fp_text("main"))
                command=[str(args.wine.resolve()),str(executable),"Z:"+str(view).replace("/","\\"),role,str(args.budget)]
                # Wine's persistent helpers may inherit these descriptors. Wait
                # for our process, rather than waiting for every helper to close
                # a captured pipe; retain partial diagnostics even on timeout.
                trace=out / (role+".jsonl"); errors=out / (role+".stderr")
                if args.live:
                    from tools.recomp_live import run_live
                    returncode,live_session=run_live(command,env=role_env,cwd=game_path.parent,trace=trace,errors=errors,timeout=args.run_timeout,
                        out=out,view=view,manifest=manifest,compiler=args.cxx,projects={r:out/(r+'-project') for r in selected},
                        inventories=inventories,reviewed_paths=args.live_reviewed,max_candidates=args.live_limit,wait_for_review=args.live_wait_for_review)
                else:
                    with trace.open("w") as stdout, errors.open("w") as stderr:
                        result=subprocess.run(command,stdout=stdout,stderr=stderr,env=role_env,cwd=game_path.parent,timeout=args.run_timeout)
                    returncode=result.returncode
                events=[json.loads(line) for line in trace.read_text().splitlines()]
                if not events or events[-1].get("event") not in ("startup_frontier","startup_stop"):
                    raise RuntimeError("startup crashed or emitted no terminal diagnostic: "+role+" "+errors.read_text()[-2000:])
                runs.append(dict(module=role,argv=command,returncode=returncode,events=events,status="incomplete"))
            artifacts=[PLAN,recomp.RUNTIME / "startup_main.cpp",recomp.RUNTIME / "native_imports.hpp",Path(__file__).resolve(),
                       executable,library,*(out / (run['module']+".jsonl") for run in runs),view / "manifest.json",
                       out / "import-coverage.json",recomp_imports.CATALOG,recomp.ROOT / "tools/recomp_imports.py"]
            artifacts.extend(placeholder_artifacts)
            if live_session: artifacts.extend([Path(live_session['report']),recomp.ROOT/'tools/recomp_live.py',recomp.RUNTIME/'live_candidates.hpp',recomp.RUNTIME/'candidate_api.hpp',out/'native-source/live_identity.hpp'])
            if call_expansion: artifacts.extend([Path(call_expansion["report"]),recomp.ROOT / "tools/recomp_reachability.py"])
            if checked_startup_profile(args.wine_prefix.resolve(),plan["process_state"])!=checked_profile:
                raise RuntimeError("runtime Documents profile changed during startup")
            report=dict(status="incomplete",game_started=False,mode=args.mode,trace_memory=args.trace_memory,native_trace_limit=args.native_trace_limit,run_timeout=args.run_timeout,call_depth=args.call_depth,call_limit=args.call_limit,call_seeds=args.call_seeds,call_expansion=call_expansion,view=generated["view"],selected_functions=len(manifest["functions"]),live_session=live_session,
                        process_state=dict(plan["process_state"],image_backing="checked native flat data" if args.flat_memory else "guest vector data",
                                           command_line=game_command_line,main_module_path=game_module_path,working_directory=str(game_path.parent),checked_filesystem_profile=checked_profile),runs=runs,build_argv=[list(map(str,c)) for c in build_commands],
                        modules=[dict(module=s["module"],sha256=s["binary_sha256"]) for s in selected.values()],
                        artifacts={str(p):recomp.digest(p.read_bytes()) for p in artifacts})
            recomp.atomic_json(out / "latest.json",report)
            recomp.atomic_json(out / "last-execution.json",report)
            recomp.atomic_json(out / "history" / (str(time.time_ns())+".json"),report)
            print(json.dumps(dict(status="incomplete",report=str(out / "latest.json"),
                                  added=additions,call_expansion=call_expansion,frontiers=[dict(module=r["module"],**r["events"][-1]) for r in runs]),indent=2))
            return 3
        except Exception as e:
            recomp.atomic_json(out / "latest.json",dict(status="incomplete",game_started=False,error=str(e)))
            print("recomp_boot: "+str(e),file=sys.stderr); return 1


if __name__=="__main__": raise SystemExit(main())

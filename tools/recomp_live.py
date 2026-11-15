"""Retained-state startup exploration; every outcome is incomplete game evidence.

Missing generated code pauses the guest. Only newly byte-pinned, strictly lifted
functions may be added; runtime/native adapter changes require a cold restart.
"""
import copy
import json
import os
from pathlib import Path
import selectors
import struct
import subprocess
import time
from tools import recomp
from tools.daodecomp.pe import fingerprint
from tools.recomp_reachability import inventory_selection, overlaps_selection


def abi_identity(manifest, compiler):
    headers={name:manifest['files'][name] for name in ('runtime.hpp','runtime_api.hpp','candidate_api.hpp')}
    # llvm-mingw's target-named driver is a shell wrapper. Pin its actual Clang
    # binary as well, and the host's complete runtime sources, including virtual
    # memory/native providers that are not copied into the generated manifest.
    compiler_files=[compiler.absolute(),*(compiler.parent/name for name in ('clang','ld.lld') if (compiler.parent/name).is_file())]
    from tools import recomp_imports
    return recomp.digest(recomp.encoded(dict(version=1,headers=headers,backend=manifest['backend_artifacts'],
        native_bindings=recomp.digest(recomp_imports.BINDINGS.read_bytes()),
        generated_native_bindings=manifest.get('native_bindings_sha256'),
        compiler=str(compiler.absolute()),compiler_artifacts={str(p):recomp.digest(p.read_bytes()) for p in compiler_files},
        host_runtime={p.name:recomp.digest(p.read_bytes()) for p in sorted(recomp.RUNTIME.iterdir()) if p.is_file()},
        candidate_flags=['-std=c++20','-O2','-DNDEBUG','-static','-shared','-DSHARP_RETRO_EXTERNAL_UNKNOWN_ORIGIN=1'])))


def identity_header(manifest, compiler):
    identities=',\n'.join('{'+f'{m["image_base"]}u,{m["image_size"]}u,"{m["binary_sha256"]}"'+'}' for m in manifest['modules'])
    return ('#pragma once\nnamespace recomp_generated {\n'
        'inline constexpr char candidate_abi[]="'+abi_identity(manifest,compiler)+'";\n'
        'struct CandidateModuleIdentity { unsigned base,size; const char* sha256; };\n'
        'inline constexpr CandidateModuleIdentity candidate_module_identities[]={'+identities+'};\n}\n')


def checked_selection(state, selection, occupied):
    rva,size=selection['rva'],selection['size']
    pe=fingerprint(recomp.checked_binary(state)); image=Path(state['binary']).read_bytes()
    nt=struct.unpack_from('<I',image,0x3c)[0]; count=struct.unpack_from('<H',image,nt+6)[0]
    table=nt+24+struct.unpack_from('<H',image,nt+20)[0]
    executable={struct.unpack_from('<I',image,table+i*40+12)[0] for i in range(count)
                if struct.unpack_from('<I',image,table+i*40+36)[0]&0x20000000}
    sections=[s for s in pe['sections'] if s['rva']<=rva and rva+size<=s['rva']+s['file_size'] and s['rva'] in executable]
    if len(sections)!=1 or size<=0: raise ValueError('candidate is not original file-backed executable code')
    offset=sections[0]['file_offset']+rva-sections[0]['rva']
    if recomp.digest(image[offset:offset+size])!=selection['slice_sha256']: raise ValueError('candidate original bytes changed')
    if overlaps_selection(selection,occupied): raise ValueError('candidate overlaps selected function ranges')
    for region in selection.get('ranges') or [selection]:
        if region['size']<=0 or not rva<=region['rva']<region['rva']+region['size']<=rva+size:
            raise ValueError('candidate range exceeds reviewed envelope')
    return selection


def choose_selection(state, inventory, rva, reviewed, occupied):
    matches=[r for r in reviewed if r.get('binary_sha256')==state['binary_sha256'] and r.get('selection',{}).get('rva')==rva]
    if len(matches)>1: raise ValueError('ambiguous explicitly reviewed candidate bounds')
    selection=copy.deepcopy(matches[0]['selection']) if matches else inventory_selection(state,inventory,rva)
    if matches and '_review_path' in matches[0]:
        selection['bounds_review']=dict(report=matches[0]['_review_path'],sha256=matches[0]['_review_sha256'])
    selection['purpose']='observed retained-state startup target; '+selection.get('purpose','')
    selection['contract_status']='startup exploration; signature/general behavior and initialized game scenarios unaccepted'
    return checked_selection(state,selection,occupied)


def build_candidate(out, view, manifest, compiler, role, state, selection, occupied_pcs):
    module=next(m for m in manifest['modules'] if m['module']==state['module'] and m['binary_sha256']==state['binary_sha256'])
    item=dict(rva=selection['rva'],size=selection['size'],ranges=selection.get('ranges'),
              extra_entries=selection.get('extra_entries',[]),annotations={},contract='recompiler/startup.json',
              contract_status=selection['contract_status'])
    result=recomp.export(dict(state,functions=[item]),module_prefix=module['code_prefix'])
    if result['runtime']!=(view/'runtime.hpp').read_text() or result['backend_artifacts']!=manifest['backend_artifacts'] or result['module_policy_sha256']!=manifest['module_policy_sha256']:
        raise ValueError('candidate runtime/backend/policy changed; cold restart required')
    code={}; entries=[]; sources={}
    for f in result['functions']:
        sources[f['name']+'.cpp']=f.pop('source')
        entries.append((state['image_base']+f['rva'],f['name']))
        for i in f['instructions']:
            pc=state['image_base']+i['rva']
            if pc in occupied_pcs or pc in code: raise ValueError('candidate decoded PC ownership collision')
            if not any(r['rva']<=i['rva'] and i['rva']+len(bytes.fromhex(i['bytes']))<=r['rva']+r['size'] for r in selection.get('ranges') or [selection]):
                raise ValueError('candidate instruction escaped reviewed bounds')
            code[pc]=f['name']+'_step'
    needed=state['image_base']+selection['rva']
    if needed not in code: raise ValueError('candidate omits reached entry')
    sources['functions.hpp']='#pragma once\n#include "runtime_api.hpp"\nnamespace recomp_generated {\n'+''.join(
        f'sharp_retro::Exit {n}(sharp_retro::State&,sharp_retro::Memory&,std::uint64_t);\nsharp_retro::Exit {n}_step(sharp_retro::State&,sharp_retro::Memory&,std::uint64_t&);\n' for _,n in entries)+'}\n'
    for name in ('runtime.hpp','runtime_api.hpp','candidate_api.hpp'): sources[name]=(view/name).read_text()
    abi=abi_identity(manifest,compiler)
    metadata=dict(schema_version=1,scope='generated candidate DLL for incomplete retained-state startup exploration',
        base_view=view.name,abi_sha256=abi,role=role,module=state['module'],binary_sha256=state['binary_sha256'],
        image_base=state['image_base'],selection=selection,functions=result['functions'],
        backend_artifacts=result['backend_artifacts'],module_policy_sha256=result['module_policy_sha256'],
        files={n:recomp.digest(s.encode()) for n,s in sources.items()},pcs=sorted(code),
        compiler=str(compiler.absolute()),compiler_sha256=recomp.digest(compiler.read_bytes()))
    metadata['builder_sha256']=recomp.digest(Path(__file__).read_bytes())
    identity=recomp.digest(recomp.encoded(metadata)); directory=out/'live-candidates'/identity
    directory.mkdir(parents=True,exist_ok=True)
    code_text=','.join('{'+f'{pc}u,{n}'+'}' for pc,n in sorted(code.items()))
    entry_text=','.join('{'+f'{pc}u,{n}'+'}' for pc,n in entries)
    wrapper='''#include "candidate_api.hpp"
#include "functions.hpp"
namespace { recomp_generated::OriginFactory origin=nullptr; }
namespace sharp_retro {
std::uint64_t external_unknown_origin() {
 if(!origin) throw std::runtime_error("candidate unknown-origin allocator is unbound");
 return origin();
}
}
namespace recomp_generated {
static void bind(OriginFactory input) { if(!input || origin) throw std::runtime_error("candidate origin binding rejected"); origin=input; }
static const CodeEntry code[]={@CODE@};
static const FunctionEntry functions[]={@ENTRIES@};
static const CandidateDescriptor descriptor={1,sizeof(sharp_retro::State),alignof(sharp_retro::State),sizeof(sharp_retro::Memory),sizeof(sharp_retro::bits),offsetof(sharp_retro::State,pc),offsetof(sharp_retro::State,x87_st),"@ABI@","@MANIFEST@","@MODULE@",@BASE@u,code,@COUNT@u,functions,@FUNCTIONS@u,bind};
}
extern "C" __declspec(dllexport) const recomp_generated::CandidateDescriptor* recomp_candidate_v1() { return &recomp_generated::descriptor; }
'''
    for key,value in dict(CODE=code_text,ENTRIES=entry_text,ABI=abi,MANIFEST=identity,MODULE=state['binary_sha256'],BASE=state['image_base'],COUNT=len(code),FUNCTIONS=len(entries)).items():
        wrapper=wrapper.replace('@'+key+'@',str(value))
    sources['candidate.cpp']=wrapper
    files={**{n:s.encode() for n,s in sources.items()},'manifest.json':recomp.encoded(metadata)}
    for name,data in files.items():
        p=directory/name
        if p.exists() and p.read_bytes()!=data: raise ValueError('immutable candidate source changed')
        if not p.exists(): p.write_bytes(data)
    dll=directory/'candidate.dll'; report_path=directory/'build.json'
    if not report_path.exists():
        command=[str(compiler.absolute()),'-std=c++20','-O2','-DNDEBUG','-static','-shared','-DSHARP_RETRO_EXTERNAL_UNKNOWN_ORIGIN=1',
                 '-I',str(directory),*[str(directory/n) for n in sources if n.endswith('.cpp')],'-o',str(dll)]
        built=subprocess.run(command,capture_output=True,text=True,timeout=180)
        (directory/'build.stdout').write_text(built.stdout); (directory/'build.stderr').write_text(built.stderr)
        if built.returncode: raise RuntimeError('candidate build failed: '+built.stderr[-3000:])
        recomp.atomic_json(report_path,dict(argv=command,dll_sha256=recomp.digest(dll.read_bytes()),
            artifacts={str(directory/n):recomp.digest(data) for n,data in files.items()}))
    report=recomp.load(report_path)
    for p,h in report['artifacts'].items():
        if recomp.digest(Path(p).read_bytes())!=h: raise ValueError('candidate build input changed')
    if recomp.digest(dll.read_bytes())!=report['dll_sha256']: raise ValueError('candidate DLL changed')
    return dict(directory=str(directory),manifest_sha256=identity,dll_sha256=report['dll_sha256'],
                role=role,selection=selection,pcs=sorted(code),build_report=str(report_path))


def run_live(command, *, env, cwd, trace, errors, timeout, out, view, manifest, compiler, projects, inventories, reviewed_paths=(), max_candidates=128, wait_for_review=True):
    started=time.monotonic(); events=[]; candidates=[]; pending=None; problem=None
    states={role:recomp.state(p) for role,p in projects.items()}
    occupied={role:copy.deepcopy(s['functions']) for role,s in states.items()}
    occupied_pcs={f.get('image_base',manifest['modules'][0]['image_base'])+i['rva'] for f in manifest['functions'] for i in f['instructions']}
    reviewed=[dict(recomp.load(p),_review_path=str(Path(p).absolute()),_review_sha256=recomp.digest(Path(p).read_bytes())) for p in reviewed_paths]
    transcript=out/'live-session.json'; session=dict(status='incomplete',scope='retained-state exploration; final cold bundle and game scenarios required',base_view=view.name,candidates=candidates,events=events,
        argv=list(map(str,command)),environment={k:env[k] for k in env if k.startswith(('RECOMP_','WINE','MVK_'))},
        executable_sha256=recomp.digest(Path(command[1]).read_bytes()),base_manifest_sha256=recomp.digest((view/'manifest.json').read_bytes()),
        reviewed_reports={str(p):recomp.digest(Path(p).read_bytes()) for p in reviewed_paths})
    session['session_id']=str(time.time_ns())
    recomp.atomic_json(transcript,session)
    with trace.open('w') as output, errors.open('w') as stderr:
        process=subprocess.Popen(command,stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=stderr,env=dict(env,RECOMP_LIVE_CANDIDATES='1'),cwd=cwd,bufsize=0)
        selector=selectors.DefaultSelector(); selector.register(process.stdout,selectors.EVENT_READ); buffer=b''
        try:
            while selector.get_map():
                if time.monotonic()-started>timeout: raise TimeoutError('retained-state startup wall budget exhausted')
                for key,_ in selector.select(timeout=1):
                    data=os.read(key.fileobj.fileno(),65536)
                    if not data:
                        selector.unregister(key.fileobj)
                        if buffer: raise RuntimeError('startup emitted truncated JSON event')
                        continue
                    buffer+=data
                    if len(buffer)>4*1024*1024: raise RuntimeError('startup output line too large')
                    while b'\n' in buffer:
                        raw,buffer=buffer.split(b'\n',1); event=json.loads(raw); events.append(event)
                        output.write(raw.decode()+'\n'); output.flush()
                        if event.get('event')=='candidate_needed':
                            if pending: raise RuntimeError('second request before candidate acknowledgement')
                            if len(candidates)>=max_candidates: problem='candidate selection budget exhausted'
                            else:
                                try:
                                    address=event['pc']; owners=[(role,s) for role,s in states.items() if s['image_base']<=address<s['image_base']+next(m['image_size'] for m in manifest['modules'] if m['module']==s['module'])]
                                    if len(owners)!=1: raise ValueError('missing PC has no unique translated module owner')
                                    role,state=owners[0]; rva=address-state['image_base']
                                    try:
                                        selection=choose_selection(state,inventories[role],rva,reviewed,occupied[role])
                                    except ValueError as discovery_error:
                                        if not wait_for_review: raise
                                        request=out/'live-review'/session['session_id']/f'{address:08x}.request.json'
                                        response=request.with_name(f'{address:08x}.response.json')
                                        request_data=dict(status='waiting for explicit byte-bounds review',pc=address,rva=rva,role=role,
                                            binary=state['binary'],binary_sha256=state['binary_sha256'],base_view=view.name,
                                            frontier=event,reason=str(discovery_error),response=str(response))
                                        recomp.atomic_json(request,request_data)
                                        session['controller_wait']=dict(request=str(request),response=str(response),pc=address)
                                        recomp.atomic_json(transcript,session)
                                        while not response.exists():
                                            if process.poll() is not None: raise RuntimeError('startup exited while awaiting bounds review')
                                            if time.monotonic()-started>timeout: raise TimeoutError('bounds review wall budget exhausted')
                                            time.sleep(0.25)
                                        data=response.read_bytes(); report=recomp.load(response)
                                        if response.read_bytes()!=data: raise ValueError('bounds review changed during intake')
                                        reviewed.append(dict(report,_review_path=str(response),_review_sha256=recomp.digest(data)))
                                        session['reviewed_reports'][str(response)]=recomp.digest(data)
                                        session['controller_wait']=None
                                        selection=choose_selection(state,inventories[role],rva,reviewed,occupied[role])
                                    pending=build_candidate(out,view,manifest,compiler,role,state,selection,occupied_pcs)
                                except Exception as e: problem=str(e)
                            if problem:
                                process.stdin.write(b'stop\n'); process.stdin.flush()
                            else:
                                path='Z:'+str(Path(pending['directory'])/'candidate.dll').replace('/','\\')
                                process.stdin.write(('load '+pending['dll_sha256']+' '+pending['manifest_sha256']+' '+path+'\n').encode()); process.stdin.flush()
                        elif event.get('event')=='candidate_loaded':
                            if not pending or event['manifest_sha256']!=pending['manifest_sha256'] or event['dll_sha256']!=pending['dll_sha256'] or event['sequence']!=len(candidates)+1:
                                raise RuntimeError('candidate load acknowledgement differs from frozen candidate')
                            role=pending['role']; selection=pending['selection']
                            occupied[role].append(selection); occupied_pcs.update(pending['pcs']); candidates.append(pending); pending=None
                            # Persist selected source only after the host accepted ownership.
                            from tools.recomp_boot import PLAN
                            plan=recomp.load(PLAN); selected=plan['roles'][role]['functions']
                            if any(f['rva']==selection['rva'] for f in selected): raise RuntimeError('startup plan changed during candidate loading')
                            selected.append(selection); selected.sort(key=lambda f:f['rva']); recomp.atomic_json(PLAN,plan)
                            recomp.atomic_json(transcript,session)
            process.wait(timeout=10)
        except BaseException as e:
            session['controller_error']=str(e)
            if process.poll() is None: process.kill()
            process.wait(timeout=10)
            raise
        finally:
            selector.close(); process.stdout.close(); process.stdin.close()
            session.update(returncode=process.returncode,controller_stop=problem,elapsed_seconds=time.monotonic()-started,pending_candidate=pending)
            session['artifacts']={str(p):recomp.digest(p.read_bytes()) for c in candidates for p in Path(c['directory']).iterdir() if p.is_file()}
            recomp.atomic_json(transcript,session)
    return process.returncode,dict(report=str(transcript),candidates=len(candidates),controller_stop=problem)

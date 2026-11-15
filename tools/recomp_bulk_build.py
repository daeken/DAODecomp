"""Compile every generated whole-inventory C++ body; collect errors without hiding them.

This produces an object build, not a replacement EXE or behavioral acceptance.
"""
import argparse
from collections import Counter
import ctypes
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
from tools import recomp,recomp_bulk


def stage_file(source, destination, identity):
    if recomp.digest(source.read_bytes()) != identity:
        raise ValueError('generated source changed before staging')
    if destination.exists() and recomp.digest(destination.read_bytes()) == identity:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary=destination.with_name('.stage-'+str(os.getpid()))
    if temporary.exists():raise ValueError('unexpected staging file')
    try:
        cloned=False
        if sys.platform=='darwin':
            clone=ctypes.CDLL(None,use_errno=True).clonefile
            clone.argtypes=[ctypes.c_char_p,ctypes.c_char_p,ctypes.c_int];clone.restype=ctypes.c_int
            cloned=clone(os.fsencode(source),os.fsencode(temporary),0)==0
        if not cloned:
            temporary.unlink(missing_ok=True);shutil.copyfile(source,temporary)
        if recomp.digest(temporary.read_bytes())!=identity:
            raise ValueError('staged source changed')
        os.replace(temporary,destination)
    finally:temporary.unlink(missing_ok=True)


def write_if_changed(path, text):
    if not path.exists() or path.read_text()!=text:path.write_text(text)


def require_whole_inventory(report):
    if set(report['modules'])!={'main','umbra'} or report['status']!='completed inventory generation attempt; compilation/runtime remain separate':
        raise ValueError('whole main/Umbra generation attempt must finish before whole-source build')
    for module in report['modules'].values():
        if module['counts'].get('not_attempted',0) or module['processed']!=module.get('catalog_functions',module['inventory_functions']):
            raise ValueError('probe/unattempted inventory cannot be labeled a whole-source build')


def compile_inventory(generation, output, cxx, jobs, overrides=None):
    report=recomp.load(generation/'report.json')
    require_whole_inventory(report)
    bulk=generation.parent.parent;backend=bulk/'backends'/report['pipeline'];pipeline=recomp.load(backend/'pipeline.json')
    for name,identity in pipeline['backend'].items():
        if recomp.digest((backend/name).read_bytes())!=identity:raise ValueError('generation backend changed')
    header=(backend/'CppRuntime.hpp').read_text().replace('#include "IntegerRuntime.hpp"',(backend/'IntegerRuntime.hpp').read_text())
    source=output/'source';source.mkdir(parents=True,exist_ok=True);write_if_changed(source/'runtime.hpp',header)
    manual_rows={};manual_binding=None
    if overrides is not None:
        from tools.recomp_workbench import load_overrides,inside
        overrides=overrides.resolve()
        manual,manual_rows=load_overrides(overrides,generation)
        manual_binding=dict(manifest=str(overrides),manifest_sha256=recomp.digest(overrides.read_bytes()),
                            baseline_inputs_sha256=manual['baseline_inputs_sha256'])
        if manual['files']['include/runtime.hpp']!=recomp.digest(header.encode()):
            raise ValueError('manual export runtime differs from generation')
        manual_headers={}
        for name,identity in manual['files'].items():
            if name.startswith('include/') and name.endswith('.hpp'):
                target=source/Path(name).relative_to('include')
                stage_file(inside(overrides.parent,name),target,identity)
                manual_headers[name]=identity
    records=[];excluded=Counter();seen=set()
    for role in ('main','umbra'):
        module=report['modules'][role]
        if module['counts'].get('not_attempted',0) or module['processed']!=module.get('catalog_functions',module['inventory_functions']):
            raise ValueError('probe/unattempted inventory cannot be labeled a whole-source build')
        context=recomp.load(generation/role/'context.json')
        with (generation/role/'catalog.jsonl').open() as catalog:
            expected={entry['rva']:entry for entry in map(json.loads,catalog)}
        with (generation/role/'results.jsonl').open() as stream:
            for line in stream:
                row=json.loads(line)
                if row['status']!='generated_only':excluded[row['status']]+=1;continue
                catalog_entry=expected[row['rva']]
                wanted=recomp_bulk.function_key(report['pipeline'],context['module'],context['binary_sha256'],context['module_prefix'],catalog_entry['selection'])
                if row['key']!=wanted or catalog_entry['key']!=wanted:raise ValueError('function generation inputs changed')
                marker=recomp_bulk.load_shard(bulk/'cache',row['key'],context['binary_sha256'],row['rva'])
                name=context['module_prefix']+f'fn_{row["rva"]:08x}.cpp'
                if name in seen:raise ValueError('duplicate generated C++ symbol filename')
                seen.add(name);identity=marker['files']['function.cpp']
                manual_row=manual_rows.get((role,row['rva']))
                original_identity=identity
                if manual_row is not None:
                    if (manual_row['artifact_key']!=row['key'] or manual_row['source_file']!=name or
                        manual_row['source_sha256']!=identity):raise ValueError('manual function baseline differs from generation')
                    identity=manual_row['committed_source_sha256']
                    stage_file(inside(overrides.parent,manual_row['source_path']),source/name,identity)
                else:stage_file(bulk/'cache'/row['key']/'function.cpp',source/name,identity)
                records.append(dict(id=row['id'],rva=row['rva'],module=role,artifact_key=row['key'],source_file=name,source_sha256=identity,
                                    inventory_coverage=row['coverage']))
                if manual_row is not None:records[-1]['generated_source_sha256']=original_identity
    if not records:raise ValueError('no generated functions to compile')
    quote=lambda p:'"'+str(p).replace('\\','/').replace('"','\\"')+'"'
    cmake='cmake_minimum_required(VERSION 3.20)\nproject(DAODecompWholeSources LANGUAGES CXX)\nset(CMAKE_CXX_STANDARD 20)\n'
    cmake+='add_library(whole_generated OBJECT\n'+''.join('  '+quote(source/r['source_file'])+'\n' for r in records)+')\n'
    cmake+='target_include_directories(whole_generated PRIVATE '+quote(source)+')\n'
    cmake+='target_compile_definitions(whole_generated PRIVATE RECOMP_NATIVE_EXECUTION=1)\n'
    cmake+='target_precompile_headers(whole_generated PRIVATE '+quote(source/'runtime.hpp')+')\n'
    write_if_changed(source/'CMakeLists.txt',cmake)
    run_dir=output/'runs'/str(time.time_ns());run_dir.mkdir(parents=True)
    target=subprocess.check_output([str(cxx),'--print-target-triple'],text=True).strip()
    if not target.startswith('i686-'):raise ValueError('whole-source build requires the Windows x86 compiler')
    compiler_artifacts={str(p):recomp.digest(p.read_bytes()) for p in (cxx,cxx.parent/'clang',cxx.parent/'ld.lld') if p.is_file()}
    (run_dir/'builder.py').write_bytes(Path(__file__).read_bytes())
    inputs=dict(controller_sha256=recomp.digest(Path(__file__).read_bytes()),target=target,compiler_artifacts=compiler_artifacts,generation_run=str(generation),generation_report_sha256=recomp.digest((generation/'report.json').read_bytes()),pipeline=report['pipeline'],
                compiler=str(cxx),compiler_version=subprocess.check_output([str(cxx),'--version'],text=True),compiler_sha256=recomp.digest(cxx.read_bytes()),
                runtime_sha256=recomp.digest((source/'runtime.hpp').read_bytes()),cmake_sha256=recomp.digest(cmake.encode()),functions=records,
                excluded_generation_statuses=dict(excluded),scope='All generated function sources staged with exact hashes. Unsupported/unknown generation entries remain excluded and unresolved;no successful stubs.',behavioral_acceptance=False,game_acceptance=False)
    if manual_binding is not None:
        inputs['manual_overrides']=manual_binding
        from tools.recomp_workbench import compilation_overrides
        compilation_overrides(inputs)
    recomp.atomic_json(run_dir/'inputs.json',inputs)
    configure=['cmake','-S',str(source),'-B',str(output/'build'),'-G','Ninja','-DCMAKE_SYSTEM_NAME=Windows',
               '-DCMAKE_BUILD_TYPE=Release','-DCMAKE_CXX_FLAGS_RELEASE=-O2 -g0 -DNDEBUG -femulated-tls -fno-fast-math -ffp-contract=off','-DCMAKE_CXX_COMPILER='+str(cxx)]
    build=['cmake','--build',str(output/'build'),'--target','whole_generated','--parallel',str(jobs),'--','-k','0']
    state=dict(status='configuring',run_directory=str(run_dir),functions=len(records),generation_excluded=dict(excluded),configure_argv=configure,build_argv=build,
               scope='Whole-inventory generated-source compilation;not an EXE or game acceptance.',game_acceptance=False)
    recomp.atomic_json(output/'latest.json',state);started=time.time()
    with (run_dir/'configure.log').open('wb') as stream:configured=subprocess.run(configure,stdout=stream,stderr=subprocess.STDOUT)
    if configured.returncode:
        state.update(status='configuration_failed',exit_code=configured.returncode)
    else:
        state['status']='compiling';recomp.atomic_json(output/'latest.json',state)
        with (run_dir/'build.log').open('wb') as stream:result=subprocess.run(build,stdout=stream,stderr=subprocess.STDOUT)
        errors=Counter();samples={}
        with (run_dir/'build.log').open(errors='replace') as stream:
            for line in stream:
                if ': error:' not in line and 'fatal error:' not in line:continue
                message=line.split('error:',1)[-1].strip();key=recomp_bulk.normalize_error(message);errors[key]+=1
                if len(samples.setdefault(key,[]))<5:samples[key].append(line.rstrip())
        for record in records:
            if recomp.digest((source/record['source_file']).read_bytes())!=record['source_sha256']:
                raise ValueError('staged source changed during compilation')
        if recomp.digest((source/'runtime.hpp').read_bytes())!=inputs['runtime_sha256']:
            raise ValueError('runtime header changed during compilation')
        if manual_binding is not None:
            for name,identity in manual_headers.items():
                staged=source/Path(name).relative_to('include')
                if recomp.digest(staged.read_bytes())!=identity:
                    raise ValueError('manual shared header changed during compilation')
            compilation_overrides(inputs)
        objects={str(p):recomp.digest(p.read_bytes()) for p in (output/'build/CMakeFiles/whole_generated.dir').rglob('*.obj')}
        state['observed_object_artifacts']=objects
        state.update(status='compiled_all_generated_sources' if result.returncode==0 else 'compile_failures_retained',exit_code=result.returncode,
                     error_groups=[dict(error=key,occurrences=count,samples=samples[key]) for key,count in errors.most_common()])
    state['elapsed_seconds']=time.time()-started
    state['artifacts']={str(p):recomp.digest(p.read_bytes()) for p in run_dir.iterdir() if p.is_file()}
    recomp.atomic_json(run_dir/'report.json',state);recomp.atomic_json(output/'latest.json',state)
    return state


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generation',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=recomp.ROOT/'local/recomp/bulk-compile')
    parser.add_argument('--cxx',type=Path,default=recomp.ROOT/'local/tools/recomp/llvm-mingw-20261104-ucrt-macos-universal/bin/i686-w64-mingw32-clang++')
    parser.add_argument('--overrides',type=Path,help='immutable workbench manual-overrides.json export')
    parser.add_argument('--jobs',type=int,default=4);args=parser.parse_args(argv)
    if not 1<=args.jobs<=16:parser.error('invalid compiler job count')
    args.output.mkdir(parents=True,exist_ok=True)
    with recomp.locked(args.output):result=compile_inventory(args.generation.absolute(),args.output.absolute(),args.cxx.absolute(),args.jobs,args.overrides)
    print(json.dumps({k:result[k] for k in ('status','run_directory','functions','generation_excluded','exit_code','elapsed_seconds')},indent=2));return 0 if result['exit_code']==0 else 3


if __name__=='__main__':raise SystemExit(main())

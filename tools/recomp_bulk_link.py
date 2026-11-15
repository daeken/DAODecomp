"""Link whole-inventory objects into protected native replacement PE32 images.

Source generation, compilation and observed game behavior remain separate facts.
No unsupported function is replaced by a successful stub.
"""
import argparse
import gzip
import json
from pathlib import Path
import re
import subprocess
from tools import recomp, recomp_bulk, recomp_bulk_build, recomp_native, recomp_boot


def add_owner(owners, address, name):
    if not re.fullmatch(r'(?:m_[0-9a-f]{16}_)?fn_[0-9a-f]{8}', name):
        raise ValueError('invalid generated function symbol')
    if type(address) is not int or not 0 <= address < 2**32:
        raise ValueError('invalid guest32 instruction address')
    if address in owners:
        raise ValueError('ambiguous instruction ownership')
    owners[address] = name



class InstructionOwnership:
    """Explicit, input-bound choices for byte-identical shared instructions.

    Default ownership remains strict. A plan preserves every function and must
    account for every participating source/metadata identity exactly once.
    """
    def __init__(self, plan, compilation_sha, generation_sha):
        self.rows={};self.seen={}
        if plan is None:return
        if (plan.get('schema_version')!=1 or plan.get('game_acceptance') is not False or
            plan.get('compilation_inputs_sha256')!=compilation_sha or plan.get('generation_report_sha256')!=generation_sha):
            raise ValueError('ownership plan input binding changed')
        for row in plan['assignments']:
            address=row['address'];add_owner({},address,row['owner'])
            code=bytes.fromhex(row['instruction_bytes'])
            if not 1<=len(code)<=15 or code.hex()!=row['instruction_bytes']:
                raise ValueError('ownership plan instruction bytes invalid')
            candidates={}
            for candidate in row['candidates']:
                name=candidate['symbol'];add_owner({},address,name)
                if name in candidates:raise ValueError('duplicate ownership candidate')
                for key in ('artifact_key','source_sha256','metadata_sha256','binary_sha256'):
                    if not re.fullmatch('[0-9a-f]{64}',candidate[key]):raise ValueError('invalid ownership candidate identity')
                candidates[name]=candidate
            if len(candidates)<2 or row['owner'] not in candidates or address in self.rows:
                raise ValueError('invalid or duplicate ownership assignment')
            self.rows[address]=(row,candidates);self.seen[address]=set()

    def add(self, owners, address, name, code, evidence, original):
        if address not in self.rows:
            add_owner(owners,address,name);return
        row,candidates=self.rows[address]
        if (name not in candidates or candidates[name]!=evidence or code!=row['instruction_bytes'] or
            bytes.fromhex(code)!=original or name in self.seen[address]):
            raise ValueError('ownership instruction/source evidence changed')
        if address not in owners:add_owner(owners,address,row['owner'])
        elif owners[address]!=row['owner']:raise ValueError('ownership assignment changed')
        self.seen[address].add(name)

    def finish(self):
        if any(self.seen[address]!=set(candidates) for address,(_,candidates) in self.rows.items()):
            raise ValueError('ownership plan has missing or unused candidates')


def step_symbol(name):
    # i686 MinGW Clang's Itanium C++ name, including COFF's leading underscore.
    # A compiler-generated probe checks this ABI before native compilation.
    step=name+'_step'
    return '__ZN16recomp_generated'+str(len(step))+step+'ERN11sharp_retro5StateERNS0_6MemoryERy'


def registry_sources(functions, owners, imports):
    """Use COFF relocations for the large address table, avoiding a huge C++ AST."""
    template = (recomp.RUNTIME/'registry.cpp.in').read_text()
    original = 'static const std::array<CodeEntry,@CODE_COUNT@> code{{\n@CODE@\n}};'
    if template.count(original) != 1:
        raise ValueError('registry template code-table contract changed')
    template = template.replace(original,
        'extern "C" const CodeEntry recomp_whole_code[@CODE_COUNT@];\n'
        'static const std::span<const CodeEntry> code(recomp_whole_code,@CODE_COUNT@);\n'
        'static_assert(sizeof(CodeEntry)==8 && alignof(CodeEntry)==4);')
    entries = ',\n'.join(f'    {{0x{address:08x}u,{name}}}' for address,name in sorted(functions))
    quote = lambda value: json.dumps(value, ensure_ascii=True)
    rows = ',\n'.join(f'    {{0x{i["address"]:08x}u,{quote(i["library"])},{quote(i["symbol"])},'
                     + ('true' if i['policy']=='translate' else 'false') + '}'
                     for i in sorted(imports,key=lambda i:i['address']))
    if len({i['address'] for i in imports}) != len(imports):
        raise ValueError('duplicate import slot')
    if set(owners) & {i['address'] for i in imports}:
        raise ValueError('import token overlaps translated instruction')
    for token,value in dict(FUNCTION_COUNT=len(functions),ENTRIES=entries,CODE_COUNT=len(owners),
                            IMPORT_COUNT=len(imports),IMPORTS=rows).items():
        template=template.replace('@'+token+'@',str(value))
    assembly = ['.section .rdata,"dr"', '.p2align 2', '.globl _recomp_whole_code', '_recomp_whole_code:']
    for address,name in sorted(owners.items()):
        assembly += [f'.long 0x{address:08x}', f'.long {step_symbol(name)}']
    return template, '\n'.join(assembly)+'\n'


def manual_guards(overrides, states):
    """Unsupported resume/interior entries fail explicitly, never fall back."""
    source=['#include "runtime.hpp"', '#include "functions.hpp"', 'namespace recomp_generated {']
    declarations=[];aliases={}
    for (role,rva),row in sorted(overrides.items()):
        name=row['symbol'];guard=name+'_manual';aliases[name]=guard
        if not re.fullmatch(r'(?:m_[0-9a-f]{16}_)?fn_[0-9a-f]{8}',name):
            raise ValueError('invalid manual function symbol')
        supported=row['supported_rvas']
        if not supported or rva not in supported or any(type(pc) is not int or not 0<=pc<2**32 for pc in supported):
            raise ValueError('invalid manual entry declaration')
        declarations.append(f'sharp_retro::Exit {guard}_step(sharp_retro::State&,sharp_retro::Memory&,std::uint64_t&);\n')
        source.append(f'sharp_retro::Exit {guard}_step(sharp_retro::State& s,sharp_retro::Memory& m,std::uint64_t& b) {{\n switch(s.pc) {{')
        source.extend(f'case 0x{states[role]["image_base"]+pc:x}ULL:' for pc in supported)
        source.append(f'return {name}_step(s,m,b);\n default: throw std::runtime_error("manual override lacks instruction entry: {name}");\n }}\n}}')
    return '\n'.join(source)+'\n}\n',''.join(declarations),aliases


def prepare(compilation, output, ownership_plan=None):
    inputs=recomp.load(compilation/'inputs.json')
    from tools.recomp_workbench import compilation_overrides
    overrides,baseline_compilation_sha=compilation_overrides(inputs)
    generation=Path(inputs['generation_run']);report=recomp.load(generation/'report.json')
    if recomp.digest((generation/'report.json').read_bytes()) != inputs['generation_report_sha256']:
        raise ValueError('generation report changed')
    recomp_bulk_build.require_whole_inventory(report)
    bulk=generation.parent.parent;backend=bulk/'backends'/report['pipeline']
    pipeline=recomp.load(backend/'pipeline.json')
    for name,identity in pipeline['backend'].items():
        if recomp.digest((backend/name).read_bytes())!=identity:
            raise ValueError('generation backend changed')
    header=(backend/'CppRuntime.hpp').read_text().replace('#include "IntegerRuntime.hpp"',(backend/'IntegerRuntime.hpp').read_text())
    if recomp.digest(header.encode())!=inputs['runtime_sha256']:
        raise ValueError('compiled runtime header differs from generation backend')
    plan_data=recomp.load(ownership_plan) if ownership_plan is not None else None
    resolution=InstructionOwnership(plan_data,baseline_compilation_sha or recomp.digest((compilation/'inputs.json').read_bytes()),recomp.digest((generation/'report.json').read_bytes()))
    functions=[];owners={};imports=[];states={};modules=[];originals={}
    plan=recomp.load(recomp_boot.PLAN)
    for role in ('main','umbra'):
        context=recomp.load(generation/role/'context.json')
        state=recomp.state(Path(context['project']))
        # Annotations may evolve, but the pinned binary and module must match.
        if state['binary_sha256']!=context['binary_sha256'] or state['module']!=context['module']:
            raise ValueError('module identity changed')
        binary=recomp.checked_binary(state);states[role]=state
        if plan_data is not None:
            from tools.daodecomp.pe import fingerprint
            originals[role]=(binary.read_bytes(),fingerprint(binary))
        if output.resolve().is_relative_to(binary.parent.parent.resolve()):
            raise ValueError('replacement output must be separate from original install')
        metadata=json.loads(gzip.decompress((generation/role/'module.json.gz').read_bytes()))
        if metadata['binary_sha256']!=state['binary_sha256'] or metadata['image_base']!=state['image_base']:
            raise ValueError('module metadata identity changed')
        imports.extend(metadata['imports'])
        modules.append(dict(role=role,module=state['module'],binary_sha256=state['binary_sha256'],
                            image_base=state['image_base'],image_size=metadata['pe_image_size'],
                            entry_rva=plan['roles'][role]['entry_rva']))
    for record in inputs['functions']:
        state=states[record['module']]
        marker=recomp_bulk.load_shard(bulk/'cache',record['artifact_key'],state['binary_sha256'],record['rva'])
        generated_sha=record['source_sha256']
        if (record['module'],record['rva']) in overrides:
            generated_sha=record['generated_source_sha256']
        if marker['status']!='generated_only' or marker['files']['function.cpp']!=generated_sha:
            raise ValueError('compiled function shard changed')
        function=json.loads(gzip.decompress((bulk/'cache'/record['artifact_key']/'function.json.gz').read_bytes()))
        name=Path(record['source_file']).stem
        if function['name']!=name or function['rva']!=record['rva']:
            raise ValueError('function symbol/entry identity changed')
        functions.append((state['image_base']+record['rva'],name))
        evidence=dict(symbol=name,artifact_key=record['artifact_key'],source_sha256=generated_sha,
                      metadata_sha256=marker['files']['function.json.gz'],binary_sha256=state['binary_sha256'],module=record['module'])
        for instruction in function['instructions']:
            address=state['image_base']+instruction['rva'];code=instruction['bytes']
            original=recomp_bulk.read_rva(*originals[record['module']],instruction['rva'],len(bytes.fromhex(code))) if address in resolution.rows else b''
            resolution.add(owners,address,name,code,evidence,original)
    resolution.finish()
    if len({address for address,name in functions})!=len(functions):
        raise ValueError('duplicate function entry')
    # Render the existing native API/support files without retaining all function
    # sources, variables and IR in a monolithic module JSON document.
    files=recomp.render(states['main'],dict(runtime=header,functions=[],imports=imports))
    declarations=''.join(f'sharp_retro::Exit {name}(sharp_retro::State&,sharp_retro::Memory&,std::uint64_t);\n'
                         f'sharp_retro::Exit {name}_step(sharp_retro::State&,sharp_retro::Memory&,std::uint64_t&);\n'
                         for address,name in sorted(functions))
    if overrides:
        guards,guard_declarations,aliases=manual_guards(overrides,states)
        files['manual_guards.cpp']=guards
        declarations+=guard_declarations
        owners={pc:aliases.get(name,name) for pc,name in owners.items()}
        files['manual-overrides.json']=recomp.encoded(inputs['manual_overrides']).decode()
    files['functions.hpp']='#pragma once\n#include "runtime_api.hpp"\nnamespace recomp_generated {\n'+declarations+'}\n'
    files['registry.cpp'],files['registry.S']=registry_sources(functions,owners,imports)
    for name in ('native_process.cpp','native_callback_entry.hpp','native_entry.c'):
        files[name]=(recomp.RUNTIME/name).read_text()
    files['bulk_link_controller.py']=Path(__file__).read_text()
    files['native_link_controller.py']=Path(recomp_native.__file__).read_text()
    files['startup.json']=recomp.encoded(plan).decode()
    if plan_data is not None:files['instruction-ownership.json']=recomp.encoded(plan_data).decode()
    cmake='cmake_minimum_required(VERSION 3.20)\nproject(DAODecompWholeRuntime LANGUAGES CXX ASM)\n'
    cmake+='add_library(whole_runtime OBJECT registry.cpp registry.S native_process.cpp native_abi.cpp native_abi_call.S native_cpu.cpp native_simd.cpp'+(' manual_guards.cpp' if overrides else '')+')\n'
    cmake+='target_compile_features(whole_runtime PRIVATE cxx_std_20)\ntarget_compile_definitions(whole_runtime PRIVATE RECOMP_NATIVE_EXECUTION=1)\n'
    cmake+='target_include_directories(whole_runtime PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})\n'
    files['CMakeLists.txt']=cmake
    source=output/'source';source.mkdir(parents=True,exist_ok=True)
    for name,value in files.items():
        data=value.encode() if isinstance(value,str) else value
        target=source/name
        if not target.exists() or target.read_bytes()!=data:target.write_bytes(data)
    prepared=dict(status='prepared whole-program native registry; not linked or executed',
        compilation_run=str(compilation),compilation_inputs_sha256=recomp.digest((compilation/'inputs.json').read_bytes()),
        functions=len(functions),instruction_entries=len(owners),imports=len(imports),modules=modules,
        shared_instruction_assignments=len(resolution.rows),ownership_plan_sha256=recomp.digest(recomp.encoded(plan_data)) if plan_data is not None else None,
        manual_override_functions=len(overrides),
        generation_excluded=inputs['excluded_generation_statuses'],compiler=inputs['compiler'],compiler_artifacts=inputs['compiler_artifacts'],
        sources={name:recomp.digest((source/name).read_bytes()) for name in files},
        preparation_controller_sha256=recomp.digest(Path(__file__).read_bytes()),
        module_policy_sha256=recomp.digest(recomp.MODULE_POLICY.read_bytes()),
        pe_linker_sha256=recomp.digest((Path(inputs['compiler']).parent/'lld-link').read_bytes()),
        game_acceptance=False,behavioral_acceptance=False)
    recomp.atomic_json(output/'prepared.json',prepared)
    return prepared


def response_file(path, arguments):
    # Clang response-file quoting, independent of shell expansion/ARG_MAX.
    path.write_text('\n'.join('"'+str(a).replace('\\','\\\\').replace('"','\\"')+'"' for a in arguments)+'\n')


def compile_runtime(output, prepared):
    source=output/'source';cxx=Path(prepared['compiler'])
    for name,identity in prepared['sources'].items():
        if recomp.digest((source/name).read_bytes())!=identity:raise ValueError('prepared runtime input changed')
    for name,identity in prepared['compiler_artifacts'].items():
        if recomp.digest(Path(name).read_bytes())!=identity:raise ValueError('compiler changed')
    probe=source/'registry-abi-probe.cpp'
    names=['fn_00001000','m_0123456789abcdef_fn_00001000','fn_00001000_manual']
    probe.write_text('#include "runtime_api.hpp"\nnamespace recomp_generated {\n'+''.join(
        f'sharp_retro::Exit {name}_step(sharp_retro::State&,sharp_retro::Memory&,std::uint64_t&);\n'
        for name in names)+'}\n'+''.join(
        f'auto abi_probe_{index}=&recomp_generated::{name}_step;\n' for index,name in enumerate(names)))
    subprocess.run([str(cxx),'-std=c++20','-DRECOMP_NATIVE_EXECUTION=1','-S',str(probe),'-o',str(output/'registry-abi-probe.S')],check=True)
    actual=(output/'registry-abi-probe.S').read_text()
    if any(step_symbol(name) not in actual for name in names):
        raise ValueError('compiler-generated step symbol ABI differs from registry relocations')
    return [recomp_native.run(['cmake','-S',source,'-B',output/'build','-G','Ninja','-DCMAKE_SYSTEM_NAME=Windows',
                 '-DCMAKE_CXX_COMPILER='+str(cxx),'-DCMAKE_ASM_COMPILER='+str(cxx),'-DCMAKE_BUILD_TYPE=Release',
                 '-DCMAKE_CXX_FLAGS_RELEASE=-O2 -g0 -DNDEBUG -femulated-tls -fno-fast-math -ffp-contract=off'],output/'configure.log'),
            recomp_native.run(['cmake','--build',output/'build','--target','whole_runtime','--parallel','2'],output/'build.log',2400)]


def finish(output, prepared):
    compilation=Path(prepared['compilation_run']);report=recomp.load(compilation/'report.json')
    if report['status']!='compiled_all_generated_sources' or report['exit_code']!=0:
        raise ValueError('whole-source compilation must succeed before linking')
    if recomp.digest((compilation/'inputs.json').read_bytes())!=prepared['compilation_inputs_sha256']:
        raise ValueError('compilation inputs changed')
    inputs=recomp.load(compilation/'inputs.json');root=compilation.parent.parent
    from tools.recomp_workbench import compilation_overrides
    compilation_overrides(inputs)
    objects=[]
    for record in inputs['functions']:
        obj=root/'build/CMakeFiles/whole_generated.dir'/(record['source_file']+'.obj')
        if recomp.digest(obj.read_bytes())!=report['observed_object_artifacts'].get(str(obj)):
            raise ValueError('compiled function object missing or changed')
        objects.append(obj)
    commands=compile_runtime(output,prepared)
    scaffold=sorted((output/'build/CMakeFiles/whole_runtime.dir').rglob('*.obj'))
    if len(scaffold)!=7+bool(prepared.get('manual_override_functions',0)):
        raise ValueError('unexpected native runtime object inventory')
    stage=output/'bin_ship';stage.mkdir(exist_ok=True)
    cxx=Path(prepared['compiler']);runtime=stage/'recomp_runtime.dll';import_library=output/'recomp_runtime.a'
    arguments=['-shared','-static',*scaffold,*objects,'-ladvapi32','-lwinmm','-luser32','-lshell32','-lgdi32',
               '-Wl,--image-base,0x20000000','-Wl,--out-implib,'+str(import_library),'-o',runtime]
    response_file(output/'runtime-link.rsp',arguments)
    commands.append(recomp_native.run([cxx,'@'+str(output/'runtime-link.rsp')],output/'runtime-link.log',2400))
    modules={}
    if recomp.digest((cxx.parent/'lld-link').read_bytes())!=prepared['pe_linker_sha256']:
        raise ValueError('PE linker changed')
    for module in prepared['modules']:
        role=module['role'];context=recomp.load(Path(inputs['generation_run'])/role/'context.json')
        state=recomp.state(Path(context['project']));binary=recomp.checked_binary(state)
        if state['binary_sha256']!=module['binary_sha256']:raise ValueError('original module changed')
        directory=output/(role+'-image')
        original,data_source,layout=recomp_native.prepare_image(binary,directory)
        (directory/'native_image_config.hpp').write_text('#pragma once\n'+'\n'.join(
            f'#define RECOMP_{key} {value}u' for key,value in
            [('IMAGE_BASE',state['image_base']),('IMAGE_EXTENT',original.end),
             ('ENTRY',state['image_base']+module['entry_rva']),('IS_DLL',int(role=='umbra'))])+'\n')
        obj=directory/'native_entry.obj'
        commands.append(recomp_native.run([cxx,'-x','c','-O2','-I',directory,'-c',output/'source/native_entry.c','-o',obj],directory/'compile.log'))
        modules[role]=recomp_native.native_link(cxx,original,[obj,import_library],data_source,layout,directory,stage/state['module'],dll=role=='umbra')
    main_context=recomp.load(Path(inputs['generation_run'])/'main/context.json')
    install=recomp.checked_binary(recomp.state(Path(main_context['project']))).parent
    retained=recomp_native.stage_retained(stage,install,recomp.load(recomp.ROOT/'recompiler/imports.json'))
    assets=recomp_native.stage_assets(stage,install.parent)
    result=dict(status='whole-inventory generated functions linked; not game acceptance',functions=prepared['functions'],
        instruction_entries=prepared['instruction_entries'],generation_excluded=prepared['generation_excluded'],modules=modules,
        runtime_sha256=recomp.digest(runtime.read_bytes()),retained_providers=retained,assets=assets,build_argv=commands,
        prepared_sha256=recomp.digest((output/'prepared.json').read_bytes()),
        compilation_report_sha256=recomp.digest((compilation/'report.json').read_bytes()),
        runtime_objects={str(p):recomp.digest(p.read_bytes()) for p in scaffold},game_acceptance=False)
    recomp.atomic_json(output/'build-report.json',result)
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('prepare','runtime','finish'))
    parser.add_argument('--compilation',type=Path)
    parser.add_argument('--ownership-plan',type=Path,help='explicit original-byte/input-bound shared-instruction plan; default still refuses conflicts')
    parser.add_argument('--output',type=Path,default=recomp.ROOT/'local/recomp/bulk-native')
    args=parser.parse_args(argv);output=args.output.absolute();output.mkdir(parents=True,exist_ok=True)
    with recomp.locked(output/'build-lock'):
        if args.action=='prepare':
            if not args.compilation:parser.error('prepare requires --compilation RUN_DIRECTORY')
            result=prepare(args.compilation.absolute(),output,args.ownership_plan.absolute() if args.ownership_plan else None)
        else:
            prepared=recomp.load(output/'prepared.json')
            if args.action=='runtime':
                commands=compile_runtime(output,prepared)
                result=dict(status='native runtime scaffold compiled; whole-function link pending',build_argv=commands,game_acceptance=False)
                recomp.atomic_json(output/'runtime-report.json',result)
            else:result=finish(output,prepared)
    print(json.dumps({k:v for k,v in result.items() if k in ('status','functions','instruction_entries','generation_excluded','game_acceptance')},indent=2))
    return 0


if __name__=='__main__':raise SystemExit(main())

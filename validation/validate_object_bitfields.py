"""Exact frozen-corpus validation for object-bitfields-001 on reviewed POSIX batching."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from importlib.metadata import version
from pathlib import Path
import platform,sys,time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.daodecomp.harness import file_hash,load_json,write_json
from tools.daodecomp.batch import compare_batch
from validation.object_bitfield_cases import SPECS,NAMES,NEGATIVE_NAMES,cases
GROUP='object-bitfields-001'
def validate_function(function,*,binary,executable,build_dir,report_dir,suite,expect_mismatch,batch_size=128):
    name=function['name'];suites=('public',) if expect_mismatch else (('public','heldout') if suite=='all' else (suite,))
    selected=[c for selected_suite in suites for c in cases(name,selected_suite)]
    suffix='-mutant' if expect_mismatch else '-'+suite
    case_path=report_dir/(name+suffix+'-cases.json');write_json(case_path,selected)
    runner=ROOT/'validation/object_bitfield_batch_runner.py'
    oracle=[sys.executable,str(runner),'original',str(binary.resolve())]
    candidate=[sys.executable,str(runner),'candidate',str(executable.resolve())]
    artifacts=[binary,executable,case_path,Path(__file__),runner,
        ROOT/'validation/object_bitfield_cases.py',ROOT/'validation/object_bitfield_specs.json',
        ROOT/'validation/object_bitfield_batch_native.cpp',ROOT/'validation/object_bitfield_mutant.hpp',
        ROOT/'validation/indexed_field_batch_runner.py',ROOT/'validation/indexed_field_cases.py',
        ROOT/'tools/freeze_object_bitfields_pair.py',ROOT/'tools/daodecomp/batch.py',
        ROOT/'tools/daodecomp/harness.py',ROOT/'tools/daodecomp/memory.py',ROOT/'tools/daodecomp/pe.py',
        ROOT/'analysis/functions.json',ROOT/'analysis/reference-build.json',ROOT/function['contract'],
        ROOT/'CMakeLists.txt',ROOT/'requirements-validation.txt',build_dir/'CMakeCache.txt',ROOT/'src/object_bitfields.cpp',
        *[ROOT/f'validation/object_bitfield_corpus/{name}-{s}.json' for s in ('public','heldout')],
        *sorted((ROOT/'include/dao').rglob('*.hpp')),*sorted((ROOT/'src').rglob('*.cpp'))]
    commands=build_dir/'compile_commands.json'
    if commands.exists():artifacts.append(commands)
    started=time.monotonic()
    report=compare_batch(load_json(ROOT/function['contract']),selected,oracle,candidate,
                         repeats=2,artifacts=artifacts,batch_size=batch_size)
    report.update(elapsed_seconds=round(time.monotonic()-started,3),suite=suite,
        suite_case_counts={s:len(cases(name,s)) if s in suites else 0 for s in ('public','heldout')},
        backend_versions={'unicorn':version('unicorn'),'python':platform.python_version()},
        native_windows_validated=False,scope='Guarded512byte ordinary RAM; exact EAX/memory/ECX; isolated emulator corpus agreement, not whole-game proof')
    destination=report_dir/(name+suffix+'.json');write_json(destination,report)
    counts={state:sum(r['status']==state for r in report['cases']) for state in {r['status'] for r in report['cases']}}
    print(f'{name}: {counts}; report: {destination}; SHA256: {file_hash(destination)}',flush=True)
    return ((counts.get('mismatch',0)>0 and set(counts)<={'corpus_pass','mismatch'} and report['artifacts_unchanged']) if expect_mismatch else report['status']=='corpus_pass')
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary',type=Path,default=ROOT/'gamedata/bin_ship/DAOrigins.exe')
    parser.add_argument('--build-dir',type=Path,default=ROOT/'build')
    parser.add_argument('--report-dir',type=Path,default=ROOT/'reports/object-bitfields')
    parser.add_argument('--suite',choices=('public','heldout','all'),default='public')
    parser.add_argument('--function',action='append');parser.add_argument('--expect-mismatch',action='store_true')
    parser.add_argument('--jobs',type=int,choices=range(1,5),default=2)
    parser.add_argument('--execution',choices=('batch',),default='batch')
    parser.add_argument('--batch-size',type=int,choices=range(1,129),default=128)
    args=parser.parse_args()
    if sys.platform=='win32':parser.error('This reviewed batch adapter requires POSIX')
    functions=[f for f in load_json(ROOT/'analysis/functions.json')['functions'] if f.get('recovery_group')==GROUP]
    if len(functions)!=len(NAMES) or {f['name'] for f in functions}!=set(NAMES) or any(f.get('backend')!=GROUP or f['status'] not in {'contracted','implemented','corpus_pass','reviewed','integrated'} for f in functions):parser.error('incomplete/mismatched registry domain')
    if args.function and not set(args.function)<=set(NAMES):parser.error('unknown function')
    if args.expect_mismatch and args.suite!='public':parser.error('negative controls require full public corpus')
    selected=[f for f in functions if not args.function or f['name'] in args.function]
    suffix='.dylib' if sys.platform=='darwin' else '.so'
    executable=args.build_dir.resolve()/('libdao_object_bitfield_batch'+('_mutant' if args.expect_mismatch else '')+suffix)
    if not executable.is_file() or not args.binary.is_file():parser.error('Actual candidate library and pinned original binary required; no placeholder implementation is supplied')
    def run(f):return validate_function(f,binary=args.binary,executable=executable,build_dir=args.build_dir.resolve(),report_dir=args.report_dir.resolve(),suite=args.suite,expect_mismatch=args.expect_mismatch,batch_size=args.batch_size)
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:return 0 if all(pool.map(run,selected)) else 1
if __name__=='__main__':raise SystemExit(main())

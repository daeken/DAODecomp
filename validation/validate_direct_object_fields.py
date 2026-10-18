"""Frozen-domain direct-field differential group. Actual native candidate library is mandatory."""
import argparse,json,platform,sys,time
from importlib.metadata import version
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.daodecomp.batch import compare_batch
from tools.daodecomp.harness import load_json,write_json,file_hash,validate_contract,validate_cases
from validation.direct_field_batch_runner import fixture
from validation.direct_object_field_cases import cases,NAMES,SPECS,HASH_MAP,descriptor_domain,registry_domain,corpus_hashes

def validate_function(f,*,binary,build_dir,report_dir,suite,negative,batch_size=128):
 name=f['name'];contract=load_json(ROOT/f'contracts/{name}.json');suites=('public','heldout') if suite=='all' else (suite,);selected=[c for s in suites for c in cases(name,s)];validate_contract(contract);validate_cases(selected,contract)
 for case in selected:fixture(SPECS[name],case['inputs'])
 runner=ROOT/'validation/direct_object_field_batch_runner.py';suffix='.dylib' if sys.platform=='darwin' else '.so';library=build_dir/('libdao_direct_object_field_batch'+('_mutant' if negative else '')+suffix)
 if not library.is_file():raise ValueError('Actual candidate library is required; absent bodies never pass')
 case_path=report_dir/(name+('-mutant' if negative else '-'+suite)+'-cases.json');write_json(case_path,selected)
 artifacts=[binary,library,case_path,ROOT/'analysis/functions.json',ROOT/'analysis/reference-build.json',ROOT/'validation/direct_object_field_cases.py',ROOT/HASH_MAP,ROOT/'slices.json',ROOT/f'contracts/{name}.json',*[ROOT/f'corpus/{name}-{s}.json' for s in ('public','heldout')],Path(__file__),runner,ROOT/'validation/direct_field_batch_runner.py',ROOT/'validation/direct_object_field_batch_native.cpp',ROOT/'validation/direct_object_field_mutant.hpp',ROOT/'validation/indexed_field_batch_runner.py',ROOT/'validation/indexed_field_cases.py',ROOT/'tools/daodecomp/batch.py',ROOT/'tools/daodecomp/harness.py',ROOT/'tools/daodecomp/memory.py',ROOT/'tools/daodecomp/pe.py',ROOT/'tools/run_recovery_pair.py',ROOT/'tools/freeze_direct_object_fields_pair.py',ROOT/'CMakeLists.txt',ROOT/'requirements-validation.txt',ROOT/'src/direct_object_fields.cpp',build_dir/'CMakeCache.txt',build_dir/'compile_commands.json',*sorted((ROOT/'include/dao').rglob('*.hpp'))]
 report=compare_batch(contract,selected,[sys.executable,str(runner),'original',str(binary.resolve())],[sys.executable,str(runner),'candidate',str(library.resolve())],repeats=2,artifacts=artifacts,batch_size=batch_size)
 import unicorn
 report.update(suite=suite,suite_case_counts={s:len(cases(name,s)) if s in suites else 0 for s in ('public','heldout')},backend_versions={'python':platform.python_version(),'unicorn':version('unicorn')},native_windows_validated=False,scope='512byte guarded ordinary RAM; emulator corpus evidence only')
 dest=report_dir/(name+('-mutant' if negative else '-'+suite)+'.json');write_json(dest,report)
 counts={s:sum(r['status']==s for r in report['cases']) for s in {r['status'] for r in report['cases']}};print(name,counts,flush=True)
 return (set(counts)<={'corpus_pass','mismatch'} and counts.get('mismatch',0)>0 and report['artifacts_unchanged']) if negative else report['status']=='corpus_pass'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--binary',type=Path,required=True);p.add_argument('--build-dir',type=Path,required=True);p.add_argument('--report-dir',type=Path,required=True);p.add_argument('--suite',choices=('public','heldout','all'),default='public');p.add_argument('--function',action='append');p.add_argument('--expect-mismatch',action='store_true');p.add_argument('--jobs',type=int,choices=range(1,5),default=2);p.add_argument('--execution',choices=('batch',),default='batch');p.add_argument('--batch-size',type=int,choices=range(1,129),default=128);a=p.parse_args()
 try:
  rows=descriptor_domain(load_json(ROOT/'slices.json'))
  if rows!=list(SPECS.values()):raise ValueError('frozen descriptor domain changed')
  registry_domain(rows,load_json(ROOT/'analysis/functions.json')['functions'])
  corpus_hashes(ROOT/HASH_MAP,[f['name'] for f in rows])
 except (ValueError,KeyError,TypeError) as exc:p.error(str(exc))
 if a.function and not set(a.function)<={r['name'] for r in rows}:p.error('unknownfunction')
 if a.expect_mismatch and a.suite!='public':p.error('controls require public suite')
 selected=[r for r in rows if not a.function or r['name'] in a.function]
 def run(f):return validate_function(f,binary=a.binary,build_dir=a.build_dir.resolve(),report_dir=a.report_dir.resolve(),suite=a.suite,negative=a.expect_mismatch,batch_size=a.batch_size)
 with ThreadPoolExecutor(max_workers=a.jobs) as pool:return 0 if all(pool.map(run,selected)) else 1
if __name__=='__main__':raise SystemExit(main())

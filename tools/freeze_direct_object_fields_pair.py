"""Freeze disjoint22function support only after exact independent acceptance approval; no dispatch."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.run_recovery_pair import check_manifest,checked_file,sha,write,load,preflight_cmake
from validation.indexed_field_batch_runner import preload_slices
GROUP='direct-object-fields-001';CANDIDATE='src/direct_object_fields.cpp'
def support_files():
 # Complete reviewed snapshot: protected current source/test/doc dependencies, new support and evidence.
 paths=set()
 for directory in ('tools','validation','tests','include','src','examples','analysis','contracts','docs','.githooks','corpus','evidence'):
  paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
 paths.update(('CMakeLists.txt','README.md','AGENTS.md','requirements-validation.txt','slices.json','packet.txt'))
 return sorted(paths-{CANDIDATE})
def required_review():return {rel:sha(checked_file(ROOT,rel)) for rel in support_files()}
def commands(names):
 b=[{'argv':['cmake','-S','{tree}','-B','{build}','-DCMAKE_BUILD_TYPE=RelWithDebInfo','-DPython3_EXECUTABLE={python}'],'timeout_seconds':120,'reports':[]}, {'argv':['cmake','--build','{build}','--parallel','2'],'timeout_seconds':180,'reports':[]},{'argv':['{python}','-m','unittest','discover','-s','tests','-v'],'timeout_seconds':300,'reports':[]},{'argv':['ctest','--test-dir','{build}','--output-on-failure'],'timeout_seconds':300,'reports':[]}]
 for extra in ([],['--expect-mismatch']):b.append({'argv':['{python}','{tree}/examples/synthetic/demo.py','--build-dir','{build}',*extra],'timeout_seconds':120,'reports':[]})
 result={'build':b}
 for stage in ('public','heldout','negative'):
  suite='heldout' if stage=='heldout' else 'public';suffix='-mutant' if stage=='negative' else '-'+suite
  argv=['{python}','{tree}/validation/validate_direct_object_fields.py','--binary','{binary}','--build-dir','{build}','--report-dir','{report_dir}','--suite',suite,'--jobs','2','--execution','batch']
  if stage=='negative':argv+=['--expect-mismatch']
  result[stage]=[{'argv':argv,'timeout_seconds':3600,'reports':[{'path':n+suffix+'.json','function':n,'corpus':suite,'expect':'mismatch' if stage=='negative' else 'pass'} for n in names]}]
 return result
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--binary',type=Path,required=True);p.add_argument('--review-report',type=Path);p.add_argument('--output',type=Path);p.add_argument('--preflight',action='store_true');a=p.parse_args();rows=load(ROOT/'slices.json');preload_slices(a.binary,rows)
 if len(rows)!=22 or len({f['id'] for f in rows})!=22:raise ValueError('incomplete domain')
 required=required_review()
 if not a.review_report:
  print(json.dumps({'status':'independent-support-review-required','reviewed_artifacts_sha256':required},indent=2));return 0
 review=load(a.review_report)
 if review.get('decision')!='approve' or review.get('reviewed_artifacts_sha256')!=required:raise ValueError('exact independent support acceptance approval is required')
 if not a.output:raise ValueError('output required')
 review_relative=a.review_report.resolve().relative_to(ROOT).as_posix();snapshot={**required,review_relative:sha(a.review_report)}
 manifest={'schema_version':1,'group':GROUP,'packet':'packet.txt','candidate':CANDIDATE,'snapshot':snapshot,'reference':{'path':str(a.binary.resolve()),'sha256':rows[0]['module_sha256']},'functions':[{'name':f['name'],'id':f['id'],'contract':f"contracts/{f['name']}.json",'corpora':{s:f"corpus/{f['name']}-{s}.json" for s in ('public','heldout')}} for f in rows],'commands':commands([f['name'] for f in rows]),'review_evidence':['slices.json','evidence/characterization.json','evidence/support-checks.json','evidence/caller-contexts.json','include/dao/direct_object_fields.hpp','validation/direct_field_batch_runner.py','validation/direct_object_field_batch_runner.py','validation/direct_object_field_batch_native.cpp','validation/direct_object_field_mutant.hpp','validation/validate_direct_object_fields.py','tools/freeze_direct_object_fields_pair.py',review_relative]}
 check_manifest(manifest,ROOT)
 if a.output.exists():raise ValueError('preserve previous output')
 write(a.output,manifest)
 if a.preflight:
  result=preflight_cmake(manifest,ROOT,a.output.parent,sys.executable);print(json.dumps(result))
 print(str(a.output))
if __name__=='__main__':raise SystemExit(main())

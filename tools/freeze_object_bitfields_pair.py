"""Freeze exact independently reviewed object-bitfields support; never dispatch models."""
import argparse,json,re,shutil,sys,os
from importlib.metadata import version
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.run_recovery_pair import check_manifest,checked_file,digest,load,sha,write,preflight_cmake
from tools.daodecomp.leaf import load_slice
from tools.daodecomp.harness import validate_contract,validate_cases
from validation.object_bitfield_cases import NAMES,SPECS,CORPUS_FILES,cases,fixture
GROUP='object-bitfields-001';CANDIDATE='src/object_bitfields.cpp'
PIN='2346caee611002d4dff6ecef68eb315b63a37004dd98b39c11a9c26c0b45bfb3'
EVIDENCE='local/pilots/memory-batch-005/v1-frozen'
CORE={'tools/incremental_checkpoint.py','tools/update_progress.py','tests/test_incremental_checkpoint.py','tests/test_incremental_batch_provider.py','tests/test_throughput_integration.py','CMakeLists.txt','analysis/functions.json','include/dao/guest_memory.hpp','include/dao/object_bitfields.hpp',
'validation/object_bitfield_specs.json','validation/object_bitfield_cases.py','validation/object_bitfield_batch_runner.py',
'validation/object_bitfield_batch_native.cpp','validation/object_bitfield_mutant.hpp','validation/validate_object_bitfields.py',
'validation/indexed_field_batch_runner.py','validation/indexed_field_cases.py','tools/daodecomp/batch.py',
 'tools/daodecomp/memory.py','tools/daodecomp/harness.py','tools/daodecomp/leaf.py','tools/daodecomp/pe.py',
 'tools/validate_checkpoint.py','tools/run_recovery_pair.py','tools/run_model_packet.py','tools/freeze_object_bitfields_pair.py',
 'tests/test_object_bitfields.py','tests/object_bitfield_mutant.cpp','contracts/object-bitfields-001.packet.json',
 '.githooks/pre-commit','examples/synthetic/contract.json','requirements-validation.txt',
 *('contracts/functions/'+name+'.json' for name in NAMES),
 *('validation/object_bitfield_corpus/'+name for name in CORPUS_FILES)}
def review_required(root):
    return sorted(CORE|{p.relative_to(root).as_posix() for p in (root/EVIDENCE).rglob('*') if p.is_file()})
def required_files(root):
    files=set(review_required(root))
    for folder,patterns in [('src',('*.cpp',)),('include',('*.hpp',)),('validation',('*.py','*.cpp','*.hpp','*.json')),('tools',('*.py',)),('tests',('*.py','*.cpp')),('examples/synthetic',('*.py','*.cpp','*.json')),('contracts',('*.json',)),('analysis',('*.json',))]:
        for pattern in patterns:files.update(p.relative_to(root).as_posix() for p in (root/folder).rglob(pattern))
    files.update(('AGENTS.md','README.md','docs/validation.md','docs/continuous-recovery.md','docs/paired-recovery.md'))
    return sorted(files-{CANDIDATE})
def verify_runtime():
    # Fail before model dispatch if the selected validation interpreter cannot run the reviewed backend.
    import unicorn
    if os.name!='posix' or not all(hasattr(os,k) for k in ('fork','waitid','WNOWAIT')) or version('unicorn')!='2.1.4':raise ValueError('POSIX fork/waitid and pinnedUnicorn2.1.4 required')
    return {'python_executable':sys.executable,'python_version':sys.version,'unicorn':version('unicorn')}

def verify_inputs(root,binary):
    if sha(binary)!=PIN:raise ValueError('wrong reference binary')
    retained=load(root/EVIDENCE/'artifact-hashes.json')
    # v1 corpus/contract/evidence are preserved, not regenerated in this proposal.
    for name,expected in retained.items():
        if name.startswith('corpus/') or name in {'slices.json','characterization.json','original-observations.json','negative-controls.json','caller-contexts.json','contract-table.json'}:
            if sha(root/EVIDENCE/name)!=expected:raise ValueError('frozen original evidence changed: '+name)
    slices={f['name']:f for f in load(root/EVIDENCE/'slices.json')}
    found=[f for f in load(root/'analysis/functions.json')['functions'] if f.get('recovery_group')==GROUP]
    if len(found)!=len(NAMES) or {f['name'] for f in found}!=set(NAMES):raise ValueError('incomplete registry domain')
    rows=[]
    for name in NAMES:
        row=next(f for f in found if f['name']==name);original=slices[name]
        if list(SPECS[name])!=original['spec']:raise ValueError('v1 operation spec changed')
        if sha(root/EVIDENCE/'protocol-contracts'/f'{name}.json')!=retained[f'proposal/contracts/functions/{name}.json']:raise ValueError('frozen v1 protocol contract changed')
        if row.get('backend')!=GROUP or row.get('source')!=CANDIDATE or row['module_sha256']!=PIN or row['status'] not in {'contracted','implemented','corpus_pass','reviewed','integrated'}:raise ValueError('wrong registry binding')
        if row['rva']!=int(original['rva'],16) or any(row[k]!=original[k] for k in ('size','code_sha256')):raise ValueError('slice identity mismatch')
        load_slice(binary,PIN,row['rva'],row['size'],row['code_sha256'])
        contract=load(root/row['contract']);validate_contract(contract)
        if contract['function_id']!=row['id'] or contract['inputs']!={'arena':'bytes','object':'u32','value':'u32','source':'u32','entry_eax':'u32'} or contract['return_type']!='u32' or contract['memory']!={'arena':512,'exit_ecx':4} or contract['calls']!=[]:raise ValueError('contract mismatch')
        old=load(root/EVIDENCE/'protocol-contracts'/f'{name}.json') if (root/EVIDENCE/'protocol-contracts'/f'{name}.json').exists() else None
        if old is not None and contract!=old:raise ValueError('v1 protocol contract changed')
        sets=[]
        for suite,count in [('public',384),('heldout',128)]:
            path=root/f'validation/object_bitfield_corpus/{name}-{suite}.json';saved=load(path)
            if sha(path)!=CORPUS_FILES[path.name] or saved!=load(root/EVIDENCE/'corpus'/path.name) or len(saved)!=count:raise ValueError('corpus changed')
            validate_cases(saved,contract)
            for case in saved:fixture(name,case['inputs'])
            sets.append({c['id'] for c in saved})
        if sets[0]&sets[1]:raise ValueError('overlapping public/heldout IDs')
        rows.append(row)
    return rows

def approved_review(root,path):
    report=load(path)
    if report.get('decision') not in {'approve','approve_current_bounded_domain','approved_for_current_bounded_domain'}:raise ValueError('independent support review has not approved')
    reviewed=report.get('reviewed_artifacts_sha256',{})
    if not set(review_required(root))<=reviewed.keys():raise ValueError('review lacks exact support/corpus/evidence coverage')
    for name,expected in reviewed.items():
        if sha(checked_file(root,name))!=expected:raise ValueError('reviewed file changed: '+name)
    return report

def commands():
    build=[dict(argv=['cmake','-S','{tree}','-B','{build}','-DCMAKE_BUILD_TYPE=RelWithDebInfo','-DPython3_EXECUTABLE={python}'],timeout_seconds=120,reports=[]),
           dict(argv=['cmake','--build','{build}','--parallel','2'],timeout_seconds=180,reports=[]),
           dict(argv=['{python}','-m','unittest','discover','-s','tests','-v'],timeout_seconds=300,reports=[]),
           dict(argv=['ctest','--test-dir','{build}','--output-on-failure'],timeout_seconds=300,reports=[])]
    for extra in ([],['--expect-mismatch']):build.append(dict(argv=['{python}','{tree}/examples/synthetic/demo.py','--build-dir','{build}',*extra],timeout_seconds=120,reports=[]))
    build.append(dict(argv=['{python}','-c',"import pathlib,shutil,sys; d=pathlib.Path(sys.argv[2]); d.mkdir(parents=True,exist_ok=True); [shutil.copyfile(pathlib.Path(sys.argv[1])/n,d/n) for n in ('synthetic.json','synthetic-mutant.json','synthetic-cases.json')]",'{tree}/reports','{report_dir}/synthetic'],timeout_seconds=10,reports=[]))
    stages={'build':build}
    for stage in ('public','heldout','negative'):
        suite='heldout' if stage=='heldout' else 'public';suffix='-mutant' if stage=='negative' else '-'+suite
        argv=['{python}','{tree}/validation/validate_object_bitfields.py','--binary','{binary}','--build-dir','{build}','--report-dir','{report_dir}','--suite',suite,'--jobs','2','--execution','batch']
        if stage=='negative':argv+=['--expect-mismatch']
        stages[stage]=[dict(argv=argv,timeout_seconds=3600,reports=[dict(path=name+suffix+'.json',function=name,corpus=suite,expect='mismatch' if stage=='negative' else 'pass') for name in NAMES])]
    return stages

def packet_text(root,rows):
    sections=['Implement exactly15pinned object/memory helpers as C++20; only src/object_bitfields.cpp is writable. Include dao/object_bitfields.hpp and implement namespace dao declarations. No tools/models/agents/external files. Do not edit frozen support or invent calls.',
'Use defined unsigned arithmetic and exact-width GuestMemory operations; guest offsets never become host pointers. The fixed raw guest arena base is0x02000000. Every stored pointer and exit_ecx remains a guest32 address/value; use widened bounds checks when subtracting this base to obtain offsets. entry_eax is arbitrary and all observed return bits matter. source/object are offsets. exit_ecx must record actual raw guest32 exit register. copy return is destination offset, all other returns are raw EAX. Preserve sequential overlap effects. The uniform interface is a high-level observation mapping, not an original C++ signature.',
(root/'include/dao/guest_memory.hpp').read_text(),(root/'include/dao/object_bitfields.hpp').read_text(),
'Original exact slices and hypotheses:\n'+(root/EVIDENCE/'slices.json').read_text(),
'Actual direct caller contexts:\n'+(root/EVIDENCE/'caller-contexts.json').read_text()]
    for row in rows:sections+=[row['id'],(root/row['contract']).read_text()]
    sections+=['No heldout cases supplied. No recovered source exists. Return complete source with exact function notes and explicit remaining uncertainty; unknown dependencies must never be successful-zero stubs.']
    return '\n\n'.join(sections)+'\n'

def make_manifest(root,binary,rows,destination,review_rel=None):
    if destination.exists():raise ValueError('preserve previous freeze destination')
    destination.mkdir(parents=True);packet=destination/'packet.txt';packet.write_text(packet_text(root,rows))
    declared=[]
    for row in rows:
        corpora={}
        for suite in ('public','heldout'):
            target=destination/f"{row['name']}-{suite}.json";shutil.copyfile(root/f"validation/object_bitfield_corpus/{row['name']}-{suite}.json",target);corpora[suite]=target.relative_to(root).as_posix()
        declared.append(dict(name=row['name'],id=row['id'],contract=row['contract'],corpora=corpora))
    files=required_files(root)+[packet.relative_to(root).as_posix(),*[v for f in declared for v in f['corpora'].values()]]
    if review_rel:files+=[review_rel]
    prompt={'include/dao/guest_memory.hpp','include/dao/object_bitfields.hpp','validation/object_bitfield_cases.py','validation/object_bitfield_batch_native.cpp','validation/object_bitfield_mutant.hpp','validation/validate_object_bitfields.py','tools/freeze_object_bitfields_pair.py','contracts/object-bitfields-001.packet.json',f'{EVIDENCE}/characterization.json',f'{EVIDENCE}/caller-contexts.json'}
    if review_rel:prompt.add(review_rel)
    manifest=dict(schema_version=1,group=GROUP,packet=packet.relative_to(root).as_posix(),candidate=CANDIDATE,functions=declared,snapshot={f:sha(checked_file(root,f)) for f in sorted(set(files))},reference=dict(path=str(binary.resolve()),sha256=PIN),commands=commands(),review_evidence=sorted(prompt))
    check_manifest(manifest,root);return manifest

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--freeze',action='store_true');parser.add_argument('--preflight',action='store_true');parser.add_argument('--label',default='freeze-1');parser.add_argument('--review-report',type=Path);parser.add_argument('--binary',type=Path,default=ROOT/'gamedata/bin_ship/DAOrigins.exe');args=parser.parse_args()
    if not re.fullmatch('[a-z0-9][a-z0-9-]{0,39}',args.label):parser.error('invalid label')
    runtime=verify_runtime();rows=verify_inputs(ROOT,args.binary)
    for name in required_files(ROOT):checked_file(ROOT,name)
    if not args.freeze:
        result={'status':'support-preparation-not-approved','model_requests':0,'validation_runtime':runtime,'functions':len(rows),'review_required_sha256':{f:sha(ROOT/f) for f in review_required(ROOT)}}
        if args.preflight:
            destination=ROOT/f'local/pairs/{GROUP}-{args.label}-preflight-inputs';m=make_manifest(ROOT,args.binary,rows,destination)
            frozen=ROOT/f'local/pairs/{GROUP}-{args.label}-preflight-snapshot';frozen.mkdir()
            for name in m['snapshot']:
                out=frozen/name;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,out)
            output=ROOT/f'local/pairs/{GROUP}-{args.label}-preflight';output.mkdir()
            result['preflight']=preflight_cmake(m,frozen,output,sys.executable)
            if not result['preflight']['passed']:raise RuntimeError('CMake support preflight failed')
        print(json.dumps(result,indent=2));return 0
    if args.review_report is None:parser.error('--freeze requires exact independent --review-report')
    if any(row['status']!='contracted' for row in rows):parser.error('freeze requires contracted unimplemented rows')
    approved_review(ROOT,args.review_report);review_rel=args.review_report.resolve().relative_to(ROOT).as_posix()
    destination=ROOT/f'local/pairs/{GROUP}-{args.label}';manifest_path=ROOT/f'local/pairs/{GROUP}-{args.label}-manifest.json'
    if manifest_path.exists():parser.error('manifest exists; preserve prior freeze')
    m=make_manifest(ROOT,args.binary,rows,destination,review_rel);write(manifest_path,m)
    print(json.dumps({'status':'frozen-not-dispatched','model_requests':0,'manifest':str(manifest_path),'sha256':sha(manifest_path)}));return 0
if __name__=='__main__':raise SystemExit(main())

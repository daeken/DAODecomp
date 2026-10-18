import copy,json,hashlib,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from validation import object_bitfield_cases as fields, object_bitfield_batch_runner as runner, validate_object_bitfields as validator
from tools import freeze_object_bitfields_pair as freeze
from tools.daodecomp.harness import validate_contract,validate_cases
from tools.daodecomp.memory import ARENA_BASE
ROOT=Path(__file__).resolve().parents[1]
ROWS=[f for f in json.loads((ROOT/'analysis/functions.json').read_text())['functions'] if f.get('recovery_group')==freeze.GROUP]
class ObjectBitfieldTests(unittest.TestCase):
 def test_complete_immutable_v1_corpora_contracts(self):
  counts={'public':0,'heldout':0}
  private_evidence=ROOT/freeze.EVIDENCE
  for row in ROWS:
   name=row['name'];contract=json.loads((ROOT/row['contract']).read_text());validate_contract(contract)
   if private_evidence.exists():
    self.assertEqual(contract,json.loads((private_evidence/'protocol-contracts'/f'{name}.json').read_text()))
   ids=[]
   for suite,total in [('public',384),('heldout',128)]:
    cases=fields.cases(name,suite);validate_cases(cases,contract);self.assertEqual(len(cases),total)
    if private_evidence.exists():
     self.assertEqual(cases,json.loads((private_evidence/'corpus'/f'{name}-{suite}.json').read_text()))
    for case in cases:fields.fixture(name,case['inputs'])
    counts[suite]+=len(cases);ids.append({c['id'] for c in cases})
   self.assertFalse(ids[0]&ids[1])
  self.assertEqual(counts,{'public':5760,'heldout':1920});self.assertEqual(len(ROWS),15)
 def test_exact_access_spans_and_abi(self):
  adapter=object.__new__(runner.ObjectBitfieldAdapter);adapter.mode='original';adapter.functions={f['id']:f for f in ROWS};adapter.slices={f['id']:(0x400000+f['rva'],b'x') for f in ROWS}
  for row in ROWS:
   name=row['name'];kind=fields.SPECS[name][0]
   for case in [fields.cases(name)[0],fields.cases(name)[1]]:
    inputs=case['inputs'];arena,reads,writes=fields.fixture(name,inputs);seen={}
    def execute(*args,**kwargs):seen.update(kwargs);return ARENA_BASE+inputs['object'] if kind=='copy' else inputs['entry_eax'],arena,{'ecx':0x12345678}
    with patch.object(runner,'execute_memory',side_effect=execute):out=adapter.execute({'function_id':row['id'],'case':case})
    self.assertEqual(seen['readable'],reads);self.assertEqual(seen['writable'],writes)
    self.assertEqual(seen['return_registers'],('ecx',));self.assertEqual(seen['registers'],{'eax':inputs['entry_eax'],'ecx':ARENA_BASE+inputs['object']})
    self.assertEqual(seen['stack_cleanup'],0 if kind=='graph' else 4)
    self.assertEqual(seen['stack_arguments'],[] if kind=='graph' else [ARENA_BASE+inputs['source'] if kind=='copy' else inputs['value']])
    self.assertEqual(out['return'],inputs['object'] if kind=='copy' else inputs['entry_eax']);self.assertEqual(out['memory']['exit_ecx'],'78563412')
 def test_invalid_state_cannot_be_accepted(self):
  for name in fields.NAMES:
   base=fields.cases(name)[0]['inputs']
   for change in [{'object':True},{'entry_eax':1<<32},{'value':-1},{'source':True},{'arena':'AB'*512},{'object':0xffffffff},{'extra':1}]:
    with self.subTest(name=name,change=change),self.assertRaises((ValueError,TypeError)):fields.fixture(name,{**base,**change})
  for suite in ('bad','all'):
   with self.assertRaises(ValueError):fields.cases(fields.NAMES[0],suite)
 def test_registry_missing_or_wrong_domain_rejected(self):
  for rows in (ROWS[:-1],[{**r,'backend':'wrong'} for r in ROWS]):
   with self.assertRaises(ValueError):runner.ObjectBitfieldAdapter('original',Path('/absent'),rows)
 def test_freeze_support_closure_and_gate_coverage(self):
  files=freeze.required_files(ROOT)
  for name in ['.githooks/pre-commit','examples/synthetic/contract.json','validation/object_bitfield_specs.json','validation/object_bitfield_mutant.hpp','tools/daodecomp/batch.py','tools/run_recovery_pair.py','tests/test_object_bitfields.py']:self.assertIn(name,files)
  self.assertNotIn(freeze.CANDIDATE,files)
  for stage in ('public','heldout','negative'):
   commands=freeze.commands()[stage];reports=[r for c in commands for r in c['reports']]
   self.assertEqual({r['function'] for r in reports},set(fields.NAMES));self.assertEqual(len(reports),15)
  configure=freeze.commands()['build'][0]['argv'];self.assertIn('-DPython3_EXECUTABLE={python}',configure)
 def test_review_is_required_exact_and_immutable(self):
  with TemporaryDirectory() as directory:
   root=Path(directory).resolve();(root/'a').write_text('x');review=root/'review.json'
   for report in ({'decision':'reject'},{'decision':'approve','reviewed_artifacts_sha256':{}},{'decision':'approve','reviewed_artifacts_sha256':{'a':'0'*64}}):
    review.write_text(json.dumps(report))
    with patch.object(freeze,'review_required',return_value=['a']),self.assertRaises(ValueError):freeze.approved_review(root,review)
   # Mock fixture approval only; never a production support review.
   review.write_text(json.dumps({'decision':'approve','reviewed_artifacts_sha256':{'a':hashlib.sha256(b'x').hexdigest()}}))
   with patch.object(freeze,'review_required',return_value=['a']):self.assertEqual(freeze.approved_review(root,review)['decision'],'approve')
 def test_validator_uses_two_repeats_complete_exact_suite_and_required_artifacts(self):
  with TemporaryDirectory() as directory:
   dest=Path(directory);row=ROWS[0];captured={}
   def compare(contract,cases,oracle,candidate,**kwargs):captured.update(kwargs);captured['selected']=cases;return {'cases':[{'status':'corpus_pass'} for c in cases],'status':'corpus_pass','artifacts_unchanged':True}
   with patch.object(validator,'compare_batch',side_effect=compare),patch.object(validator,'version',return_value='test'):
    self.assertTrue(validator.validate_function(row,binary=dest/'original',executable=dest/'candidate',build_dir=dest,report_dir=dest,suite='all',expect_mismatch=False))
   self.assertEqual(captured['repeats'],2);self.assertEqual(captured['selected'],fields.cases(row['name'],'public')+fields.cases(row['name'],'heldout'))
   for name in ['tools/daodecomp/batch.py','validation/object_bitfield_batch_native.cpp','validation/object_bitfield_cases.py','validation/object_bitfield_specs.json','validation/object_bitfield_mutant.hpp','src/object_bitfields.cpp']:
    self.assertIn(ROOT/name,captured['artifacts'])
   report=json.loads((dest/(row['name']+'-all.json')).read_text());self.assertEqual(report['suite_case_counts'],{'public':384,'heldout':128})
 def test_group_batch_report_binding_rejects_wrong_adapter_library_and_missing_artifacts(self):
  # Structural mock report only: executes no candidate and is not game evidence.
  from tools import run_recovery_pair as pair
  from tools.daodecomp.harness import digest
  with TemporaryDirectory() as directory:
   tree=Path(directory).resolve();row=ROWS[0];case=fields.cases(row['name'])[0];contract=json.loads((ROOT/row['contract']).read_text())
   corpus_path='public.json';source='src/object_bitfields.cpp';library=tree/'build/libdao_object_bitfield_batch.dylib'
   required=[tree/source,tree/row['contract'],tree/'original',library,tree/'validation/object_bitfield_batch_runner.py',tree/'tools/daodecomp/batch.py',tree/'validation/object_bitfield_batch_native.cpp',tree/'CMakeLists.txt',tree/'build/CMakeCache.txt',tree/'build/compile_commands.json']
   for path in required:path.parent.mkdir(parents=True,exist_ok=True);path.write_text('test-only-structural-fixture')
   (tree/row['contract']).write_text(json.dumps(contract));(tree/corpus_path).write_text(json.dumps([case]))
   artifacts={str(path):pair.sha(path) for path in required}
   report={'schema_version':1,'function_id':row['id'],'proof':False,'artifacts_unchanged':True,'repeats':2,'contract_sha256':digest(contract),'corpus_sha256':digest([case]),'cases':[{'case_id':case['id'],'case_sha256':digest(case),'status':'corpus_pass'}],'artifacts_sha256':artifacts,'status':'corpus_pass','oracle_command':['python',str(tree/'validation/object_bitfield_batch_runner.py'),'original',str(tree/'original')],'candidate_command':['python',str(tree/'validation/object_bitfield_batch_runner.py'),'candidate',str(library)],'execution_backend':{'name':'posix-fresh-child-batch-v1','case_process_isolation':'fresh-fork-session','supervisor_reuse':'none across sides or repetitions','process_counts':[{'case_processes':1,'supervisor_processes':1}]*4}}
   manifest={'group':freeze.GROUP,'candidate':source,'functions':[{'name':row['name'],'id':row['id'],'contract':row['contract'],'corpora':{'public':corpus_path}}],'snapshot':{row['contract']:pair.sha(tree/row['contract']),corpus_path:pair.sha(tree/corpus_path)},'reference':{'path':str(tree/'original')},'commands':freeze.commands()}
   declaration={'function':row['name'],'corpus':'public','expect':'pass'};path=tree/'mock-report.json'
   for mutate in [lambda r:r['oracle_command'].__setitem__(1,str(tree/'validation/indexed_field_batch_runner.py')),lambda r:r['candidate_command'].__setitem__(3,str(tree/'build/libwrong.dylib')),lambda r:r['artifacts_sha256'].pop(str(tree/'validation/object_bitfield_batch_native.cpp')),lambda r:r['execution_backend']['process_counts'][0].__setitem__('case_processes',0)]:
    damaged=copy.deepcopy(report);mutate(damaged);path.write_text(json.dumps(damaged))
    with self.assertRaises(pair.PairError):pair.inspect_report(path,declaration,manifest,tree)
   path.write_text(json.dumps(report));self.assertTrue(pair.inspect_report(path,declaration,manifest,tree)['passed'])
 def test_checkpoint_promotes_complete_group_with_all_controls_only(self):
  from tools import validate_checkpoint as checkpoint
  base=json.loads((ROOT/'analysis/functions.json').read_text())
  old=[f for f in base['functions'] if f.get('recovery_group')!=freeze.GROUP]
  with TemporaryDirectory() as directory:
   root=Path(directory).resolve();(root/'analysis').mkdir()
   for size in (1,15):
    group=[{**f,'status':'implemented'} for f in ROWS[:size]]
    (root/'analysis/functions.json').write_text(json.dumps({'functions':old+group}))
    with patch.object(checkpoint,'ROOT',root):
     if size==1:
      with self.assertRaises(ValueError):checkpoint.publication_paths(root/'reports/test')
      with self.assertRaises(ValueError):checkpoint.build_commands(root/'build',root/'reports/test',2,False)
     else:
      positives,negatives=checkpoint.publication_paths(root/'reports/test')
      self.assertEqual(len([p for p in positives if 'object-bitfields' in p.parts]),15)
      self.assertEqual(len([p for p in negatives if 'object-bitfields' in p.parts]),15)
      commands=checkpoint.build_commands(root/'build',root/'reports/test',2,False)
      selected=[c for c in commands if c[0].startswith('object_bitfields')]
      self.assertEqual(len(selected),2);self.assertTrue(all('--execution' in c[1] and 'batch' in c[1] for c in selected))
if __name__=='__main__':unittest.main()

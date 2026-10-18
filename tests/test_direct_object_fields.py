"""Draft support schema/fixture/manifest checks; these are not candidate game evidence."""
import copy,json,unittest
from pathlib import Path
from validation.direct_field_batch_runner import fixture
from tools.daodecomp.harness import validate_cases,validate_contract
from tools import freeze_direct_object_fields_pair as freeze
ROOT=Path(__file__).resolve().parents[1]
ROWS=json.loads((ROOT/'slices.json').read_text())
class DirectObjectFieldSupportTests(unittest.TestCase):
 def test_exact46domain_and_disjoint_frozen_corpora(self):
  self.assertEqual(len(ROWS),46);self.assertEqual(len({r['id'] for r in ROWS}),46)
  for f in ROWS:
   self.assertEqual(f['name'],f"fn_{f['rva']:08x}");contract=json.loads((ROOT/f"contracts/{f['name']}.json").read_text());validate_contract(contract);self.assertEqual(contract['function_id'],f['id'])
   sets=[]
   for suite,count in [('public',384),('heldout',128)]:
    cases=json.loads((ROOT/f"corpus/{f['name']}-{suite}.json").read_text());validate_cases(cases,contract);self.assertEqual(len(cases),count)
    for case in cases:fixture(f,case['inputs'])
    sets.append({c['id'] for c in cases})
   self.assertFalse(sets[0]&sets[1])
 def test_invalid_arenas_and_out_of_arena_objects(self):
  for f in ROWS:
   case=json.loads((ROOT/f"corpus/{f['name']}-public.json").read_text())[0]
   for key,value in [('arena','00'),('object',512),('object',True),('value',1<<32),('entry_eax',-1)]:
    bad=copy.deepcopy(case['inputs']);bad[key]=value
    with self.assertRaises((ValueError,TypeError)):fixture(f,bad)
 def test_complete_command_domains_and_build_dependencies(self):
  names=[f['name'] for f in ROWS];cmds=freeze.commands(names)
  for stage in ('public','heldout','negative'):
   reports=[r for c in cmds[stage] for r in c['reports']];self.assertEqual({r['function'] for r in reports},set(names));self.assertEqual(len(reports),46)
   self.assertTrue(all(r['expect']==('mismatch' if stage=='negative' else 'pass') for r in reports))
  self.assertIn('-DPython3_EXECUTABLE={python}',cmds['build'][0]['argv'])
  files=freeze.support_files()
  for path in ('.githooks/pre-commit','examples/synthetic/contract.json','include/dao/direct_object_fields.hpp','validation/direct_object_field_batch_native.cpp','validation/direct_object_field_mutant.hpp','tools/run_recovery_pair.py','tests/test_direct_object_fields.py'):self.assertIn(path,files)
  self.assertNotIn(freeze.CANDIDATE,files)
 def test_pair_binding_requires_direct_group_adapter_library_and_process_provenance(self):
  # Pure report-structure fixture, not a compiled executable or game evidence.
  import tempfile
  from tools import run_recovery_pair as pair
  from tools.daodecomp.harness import digest,file_hash
  f=ROWS[0];contract=json.loads((ROOT/f"contracts/{f['name']}.json").read_text());case=json.loads((ROOT/f"corpus/{f['name']}-public.json").read_text())[0]
  with tempfile.TemporaryDirectory() as directory:
   tree=Path(directory);(tree/'build').mkdir();(tree/'src').mkdir();(tree/'validation').mkdir();(tree/'tools/daodecomp').mkdir(parents=True)
   files={'src/direct_object_fields.cpp':'// structural source fixture','contract.json':json.dumps(contract),'corpus.json':json.dumps([case]),'reference':'structural module fixture','validation/direct_object_field_batch_runner.py':'# structural runner fixture','validation/direct_object_field_batch_native.cpp':'// structural wrapper fixture','tools/daodecomp/batch.py':'# structural transport fixture','CMakeLists.txt':'# structural build fixture','build/CMakeCache.txt':'# structural cache fixture','build/compile_commands.json':'[]','build/libdao_direct_object_field_batch.so':'structural library fixture'}
   for name,data in files.items():(tree/name).write_text(data)
   function={'name':f['name'],'id':f['id'],'contract':'contract.json','corpora':{'public':'corpus.json','heldout':'corpus.json'}}
   manifest={'group':'direct-object-fields-001','candidate':'src/direct_object_fields.cpp','functions':[function],'reference':{'path':str(tree/'reference')},'snapshot':{n:file_hash(tree/n) for n in files},'commands':{'public':[{'argv':['validator','--execution','batch']}]}}
   declaration={'path':'report.json','function':f['name'],'corpus':'public','expect':'pass'}
   report={'schema_version':1,'function_id':f['id'],'proof':False,'artifacts_unchanged':True,'repeats':2,'contract_sha256':digest(contract),'corpus_sha256':digest([case]),'cases':[{'case_id':case['id'],'case_sha256':digest(case),'status':'corpus_pass'}],'status':'corpus_pass','artifacts_sha256':{str(tree/n):file_hash(tree/n) for n in files},'execution_backend':{'name':'posix-fresh-child-batch-v1','case_process_isolation':'fresh-fork-session','supervisor_reuse':'none across sides or repetitions','process_counts':[{'case_processes':1,'supervisor_processes':1} for _ in range(4)]},'oracle_command':['python',str(tree/'validation/direct_object_field_batch_runner.py'),'original',str(tree/'reference')],'candidate_command':['python',str(tree/'validation/direct_object_field_batch_runner.py'),'candidate',str(tree/'build/libdao_direct_object_field_batch.so')]}
   path=tree/'report.json';path.write_text(json.dumps(report));self.assertTrue(pair.inspect_report(path,declaration,manifest,tree)['passed'])
   broken=copy.deepcopy(report);del broken['artifacts_sha256'][str(tree/'build/libdao_direct_object_field_batch.so')];path.write_text(json.dumps(broken))
   with self.assertRaises(pair.PairError):pair.inspect_report(path,declaration,manifest,tree)
   broken=copy.deepcopy(report);broken['candidate_command'][1]=str(tree/'validation/indexed_field_batch_runner.py');path.write_text(json.dumps(broken))
   with self.assertRaises(pair.PairError):pair.inspect_report(path,declaration,manifest,tree)
   broken=copy.deepcopy(report);broken['execution_backend']['process_counts'][0]['case_processes']=0;path.write_text(json.dumps(broken))
   with self.assertRaises(pair.PairError):pair.inspect_report(path,declaration,manifest,tree)
if __name__=='__main__':unittest.main()

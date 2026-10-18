"""Composition/invalidation fixtures, not synthetic game evidence."""
import copy,json,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from tools import incremental_checkpoint as cache,validate_checkpoint as checkpoint,update_progress
from tools.daodecomp.harness import digest
from validation import direct_object_field_cases as fields,validate_direct_object_fields as validator
ROOT=Path(__file__).resolve().parents[1]
REGISTRY=json.loads((ROOT/'analysis/functions.json').read_text());ROWS=cache.selected_entries(REGISTRY,'direct_object_fields')
class DirectObjectFieldIntegrationTests(unittest.TestCase):
 def test_exact94positive73negative_nine_group_inventory_and_incomplete_promotion(self):
  self.assertEqual(len(ROWS),46);self.assertEqual(len(cache.required_groups(REGISTRY)),9)
  p,n=checkpoint.publication_paths(ROOT/'reports/inventory-fixture');self.assertEqual((len(p),len(n)),(94,73))
  self.assertEqual(len(cache.publication_inventory()),167);self.assertEqual(cache.publication_inventory(),update_progress.checkpoint_inventory(REGISTRY))
  for mutation in ('contracted','unknown-backend','wrong-group','duplicate'):
   changed=copy.deepcopy(REGISTRY);target=next(f for f in changed['functions'] if f['id']==ROWS[0]['id'])
   if mutation=='contracted':target['status']='contracted'
   elif mutation=='unknown-backend':target['backend']='unknown'
   elif mutation=='wrong-group':target['recovery_group']='unknown'
   else:changed['functions'].append(copy.deepcopy(target))
   with self.subTest(mutation=mutation),self.assertRaises(ValueError):cache.required_groups(changed)
  changed=copy.deepcopy(REGISTRY);next(f for f in changed['functions'] if f['id']==ROWS[0]['id'])['status']='contracted'
  with patch.object(checkpoint.json,'loads',return_value=changed):
   with self.assertRaises(ValueError):checkpoint.publication_paths(ROOT/'reports/inventory-fixture')
 def test_exact_corpora_selected512_and384_control_cases_per_function(self):
  bound=cache.actual_corpora('direct_object_fields',ROWS)
  for f in ROWS:
   public=fields.cases(f['name'],'public');heldout=fields.cases(f['name'],'heldout')
   self.assertEqual((len(public),len(heldout)),(384,128))
   self.assertEqual(bound[f['id']]['positive']['sha256'],digest(public+heldout));self.assertEqual(bound[f['id']]['negative']['sha256'],digest(public))
  self.assertEqual(sum(len(v['positive']['rows']) for v in bound.values()),23552)
 def test_batch_mode_size_and_missing_negative_are_not_reusable(self):
  def steps(size):return checkpoint.build_commands(ROOT/'build-incremental-fixture',ROOT/'reports/inventory-fixture',2,windows=False,batch_size=size)
  a=cache.group_execution(steps(128),'direct_object_fields');b=cache.group_execution(steps(64),'direct_object_fields');self.assertEqual(a['mode'],'batch');self.assertNotEqual(a,b)
  with self.assertRaises(ValueError):cache.group_execution([s for s in steps(128) if s[0]!='direct_object_fields_negative'],'direct_object_fields')
  changed=steps(128);argv=next(argv for name,argv,_ in changed if name=='direct_object_fields_all');argv[argv.index('--execution')+1]='single'
  with self.assertRaises(ValueError):cache.group_execution(changed,'direct_object_fields')
 def test_selected_metadata_both_corpora_normal_mutant_images_and_contracts_invalidate(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);build=root/'build-incremental-fixture';build.mkdir();shutil.copytree(ROOT/'corpus',root/'corpus');shutil.copy2(ROOT/'slices.json',root/'slices.json');(root/'validation').mkdir();shutil.copy2(ROOT/fields.HASH_MAP,root/fields.HASH_MAP)
   for f in ROWS:
    path=root/f['contract'];path.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/f['contract'],path)
   (root/'analysis').mkdir();shutil.copy2(ROOT/'analysis/reference-build.json',root/'analysis/reference-build.json');(root/'gamedata/bin_ship').mkdir(parents=True);(root/'gamedata/bin_ship/DAOrigins.exe').write_bytes(b'identity-only module fixture')
   images=cache.execution_images(build,'direct_object_fields',{'mode':'batch'})
   for i,path in enumerate(images):path.write_bytes(bytes([i,1,2,3]))
   def identity():return cache.group_identity(root,build,'direct_object_fields',REGISTRY,{}, {'provider':'macos-full-python-dyld-v1'},{'mode':'batch'},{})
   with patch.object(cache,'native_dependencies',return_value={'files':{},'bindings':{}}):
    original=identity();self.assertEqual((len(original['data']),len(original['executables'])),(94,3))
    targets=[*images,root/fields.HASH_MAP,root/'slices.json',root/'corpus'/f"{ROWS[0]['name']}-public.json",root/'corpus'/f"{ROWS[0]['name']}-heldout.json",root/ROWS[0]['contract']]
    for path in targets:
     old=path.read_bytes();path.write_bytes(old+b' ');self.assertNotEqual(original,identity(),path.name);path.write_bytes(old);self.assertEqual(original,identity());path.unlink()
     with self.assertRaises(ValueError):identity()
     path.write_bytes(old)
    for relative in (fields.HASH_MAP,'slices.json',f"corpus/{ROWS[0]['name']}-public.json"):
     self.assertEqual(cache.historical_role(root,root/relative,ROWS[0],root/'reports/x.json',original),'execution_selected_data');removed=copy.deepcopy(original);removed['data'].pop(str(root/relative))
     with self.assertRaises(ValueError):cache.historical_role(root,root/relative,ROWS[0],root/'reports/x.json',removed)
 def test_all_validator_both_suites_casefile_and_publication_dependencies(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);library=root/('libdao_direct_object_field_batch'+('.dylib' if __import__('sys').platform=='darwin' else '.so'));library.write_bytes(b'preflight-only image fixture');captured={}
   def compare(contract,cases,oracle,candidate,**kwargs):captured.update(kwargs);captured['cases']=cases;return {'status':'corpus_pass','artifacts_unchanged':True,'cases':[{'status':'corpus_pass'} for _ in cases]}
   with patch.object(validator,'compare_batch',side_effect=compare):self.assertTrue(validator.validate_function(ROWS[0],binary=root/'reference.exe',build_dir=root,report_dir=root/'reports',suite='all',negative=False,batch_size=64))
   self.assertEqual((captured['repeats'],captured['batch_size'],len(captured['cases'])),(2,64,512))
   for rel in ('analysis/functions.json','analysis/reference-build.json','slices.json','validation/direct_object_field_cases.py',fields.HASH_MAP,'src/direct_object_fields.cpp'):self.assertIn(ROOT/rel,captured['artifacts'])
   casefiles=[p for p in captured['artifacts'] if p.name.endswith('-cases.json')];self.assertEqual(len(casefiles),1);self.assertEqual(json.loads(casefiles[0].read_text()),captured['cases']);report=json.loads((root/'reports'/f"{ROWS[0]['name']}-all.json").read_text());self.assertEqual(report['suite_case_counts'],{'public':384,'heldout':128})
if __name__=='__main__':unittest.main()

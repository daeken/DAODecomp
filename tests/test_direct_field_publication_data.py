"""Generated publication fixtures exercise stale-data rejection, not game equivalence."""
import copy,json,os,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from tools import incremental_checkpoint as cache,update_progress
ROOT=Path(__file__).resolve().parents[1]
REGISTRY=json.loads((ROOT/'analysis/functions.json').read_text())
FUNCTIONS=cache.selected_entries(REGISTRY,'direct_object_fields')
SELECTED=['slices.json',*[f"corpus/{f['name']}-{s}.json" for f in FUNCTIONS for s in ('public','heldout')]]
class DirectFieldPublicationDataTests(unittest.TestCase):
 def fixture(self,root):
  source=cache.source_manifest(ROOT)
  for rel in {*source,'analysis/functions.json'}:
   target=root/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,target)
  records=[dict(function_id=fid,negative_control=negative,status='failed' if negative else 'corpus_pass',case_counts={'mismatch' if negative else 'corpus_pass':1},repeats_per_side=2,artifacts_unchanged=True,artifacts_sha256={'historical':'retained'},report='historical/report.json',report_sha256='retained') for fid,negative in sorted(cache.publication_inventory())]
  # Publication uses repository paths; the macOS-only checkpoint manifest uses host paths.
  publication_source={Path(rel).as_posix():digest for rel,digest in cache.source_manifest(root).items()}
  result=dict(schema_version=2,policy=cache.POLICY,status='passed',complete_checkpoint=True,usable_for_progress=True,source=publication_source,registry_sha256=cache.file_hash(root/'analysis/functions.json'),groups=[dict(group='synthetic-complete-inventory',records=records,reused=False,identity_sha256='synthetic-no-execution')])
  before=copy.deepcopy(records);document=cache.publication_document(result);self.assertEqual(records,before)
  path=root/'analysis/validation/publication-fixture.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(document));validated=update_progress.Snapshot(root).document('analysis/validation/publication-fixture.json')
  self.assertEqual(len(validated['records']),117);self.assertEqual(sum(not r['negative_control'] for r in validated['records']),69)
  record=next(r for r in validated['records'] if r['function_id']==FUNCTIONS[0]['id'] and not r['negative_control'])
  self.assertTrue(update_progress.evidence_matches(update_progress.Snapshot(root),FUNCTIONS[0],record))
  self.assertEqual({rel:record['artifacts_sha256'][rel] for rel in SELECTED},{rel:cache.file_hash(root/rel) for rel in SELECTED})
  return result,record,document
 def test_all45_current_selected_inputs_mutation_and_deletion_reject_generated_progress(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);result,record,document=self.fixture(root);original_source=cache.source_manifest(root)
   for rel in SELECTED:
    path=root/rel;before=path.read_bytes()
    with self.subTest(path=rel,change='one-byte'):
     path.write_bytes(before+b' ');self.assertNotEqual(cache.source_manifest(root),original_source)
     self.assertFalse(update_progress.evidence_matches(update_progress.Snapshot(root),FUNCTIONS[0],record))
    path.write_bytes(before)
    with self.subTest(path=rel,change='delete'):
     path.unlink()
     with self.assertRaises(ValueError):cache.source_manifest(root)
     self.assertFalse(update_progress.evidence_matches(update_progress.Snapshot(root),FUNCTIONS[0],record))
    path.write_bytes(before)
   self.assertEqual(cache.source_manifest(root),original_source);self.assertTrue(update_progress.evidence_matches(update_progress.Snapshot(root),FUNCTIONS[0],record))
   # Complete69+48 inventory remains mandatory, even for a synthetically generated document.
   result['groups'][0]['records'].pop()
   with self.assertRaises(ValueError):cache.publication_document(result)
   document['records'].pop();document.pop('attestation_sha256');document['attestation_sha256']=cache.digest(document);(root/'analysis/validation/publication-fixture.json').write_text(json.dumps(document))
   with self.assertRaises(ValueError):update_progress.Snapshot(root).document('analysis/validation/publication-fixture.json')
 @unittest.skipUnless(os.name=='posix','symlink rejection uses POSIX filesystem semantics')
 def test_selected_inputs_are_regular_and_private_packet_data_is_excluded(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);self.fixture(root);p=root/'slices.json';original=p.read_bytes();target=root/'local/private-copy.json';target.parent.mkdir(parents=True);target.write_bytes(original);p.unlink();p.symlink_to(target)
   with self.assertRaises(ValueError):cache.source_manifest(root)
   p.unlink();p.write_bytes(original);private=root/'local/pairs/private-corpus.json';private.parent.mkdir(parents=True);private.write_text('private packet fixture')
   manifest=cache.source_manifest(root);self.assertFalse(any(name.startswith(('local/','gamedata/','reports/')) for name in manifest));self.assertEqual(len(set(SELECTED)&manifest.keys()),45)
 def test_group_execution_source_projection_and_policy_are_unchanged(self):
  # Attestation-only additions do not enter Python execution-source projection.
  source=cache.source_manifest(ROOT);without={p:h for p,h in source.items() if p not in SELECTED}
  with tempfile.TemporaryDirectory() as directory:
   build=Path(directory);images=cache.execution_images(build,'direct_object_fields',{'mode':'batch'})
   for image in images:image.write_bytes(b'identity-only image fixture')
   with patch.object(cache,'native_dependencies',return_value={'files':{},'bindings':{}}):
    def identity(values):return cache.group_identity(ROOT,build,'direct_object_fields',REGISTRY,values,{'provider':'macos-full-python-dyld-v1'},{'mode':'batch'}, {})
    # Original game is private/optional in public CI; avoid reading it in this structural key test.
    with patch.object(cache,'files_manifest',side_effect=lambda paths:{str(p):'identity-fixture' for p in paths}):self.assertEqual(identity(source),identity(without))
  self.assertEqual(cache.POLICY,'clean-build-local-groups-003')
if __name__=='__main__':unittest.main()

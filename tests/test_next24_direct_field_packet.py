"""Frozen support domain and protected accepted prefix checks; no game execution."""
import copy,hashlib,json,re,unittest
from pathlib import Path
from validation import direct_object_field_cases as fields
from tools import freeze_direct_object_fields_pair as freeze,validate_checkpoint as checkpoint
ROOT=Path(__file__).resolve().parents[1]
class Next24PacketTests(unittest.TestCase):
 def test_accepted_prefix_and_exact_new_declarations(self):
  domain=json.loads((ROOT/'evidence/next24-packet-domain.json').read_text())
  prefix=(ROOT/'evidence/accepted-direct-object-fields-prefix.txt').read_bytes()
  self.assertEqual(hashlib.sha256(prefix).hexdigest(),domain['old_source_sha256'])
  self.assertEqual(len(prefix),domain['old_source_bytes'])
  candidate=ROOT/'src/direct_object_fields.cpp'
  if candidate.exists():self.assertTrue(candidate.read_bytes().startswith(prefix),'accepted22 source prefix changed')
  expected=set(domain['old_names']+domain['new_names']);self.assertEqual(len(expected),46)
  header=(ROOT/'include/dao/direct_object_fields.hpp').read_text()
  native=(ROOT/'validation/direct_object_field_batch_native.cpp').read_text()
  mutant=(ROOT/'validation/direct_object_field_mutant.hpp').read_text()
  self.assertEqual(set(re.findall(r'uint32_t (fn_[0-9a-f]{8})\(',header)),expected)
  self.assertEqual(set(re.findall(r'name=="(fn_[0-9a-f]{8})"',native)),expected)
  self.assertEqual(set(re.findall(r'name=="(fn_[0-9a-f]{8})"',mutant)),expected)
 def test_full46_preflight_domain_and94_publication(self):
  rows=json.loads((ROOT/'slices.json').read_text());registry=json.loads((ROOT/'analysis/functions.json').read_text())
  fields.registry_domain(rows,registry['functions']);self.assertEqual(len(fields.corpus_hashes()),92)
  for stage in ('public','heldout','negative'):
   reports=[r for c in freeze.commands(fields.NAMES)[stage] for r in c['reports']]
   self.assertEqual(len(reports),46);self.assertEqual({r['function'] for r in reports},set(fields.NAMES))
  pos,neg=checkpoint.publication_paths(ROOT/'reports/packet-structure-only')
  self.assertEqual((len(pos),len(neg)),(94,73))
  for index in (0,21,22,45):
   bad=copy.deepcopy(registry['functions']);bad=[f for f in bad if f['id']!=rows[index]['id']]
   with self.assertRaises(ValueError):fields.registry_domain(rows,bad)

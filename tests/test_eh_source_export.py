"""Synthetic acceptance/export refusals; no game or library bytes."""
import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from test_eh_native import fixture,sha
from rapid_object import eh_source_export as e

class ExportTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.folder=self.root/'build';self.folder.mkdir();kw,_,_=fixture();self.kw=kw
  kw['source']=b'// FUNCTION: DAO 0x00401000\nvoid fn_00001000();\n';kw['build']['source_sha256']=sha(kw['source']);kw['build']['compiler']['file_version']='synthetic-only';self.policy=copy.deepcopy(kw['pins']);self.original=kw['original']
  self.inputs={}
  for key in ('inventory','compiler'):
   p=self.root/key;p.write_bytes(kw[key]);self.inputs[key]=str(p)
  self.inputs['libraries']={}
  for name,raw in kw['libraries'].items():p=self.root/name;p.write_bytes(raw);self.inputs['libraries'][name]=str(p)
  (self.folder/'candidate.cpp').write_bytes(kw['source']);(self.folder/'candidate.obj').write_bytes(kw['object_bytes'])
  for name,value in [('run.json',kw['build']),('compiler.json',kw['build']['compiler'])]:(self.folder/name).write_text(json.dumps(value))
  self.patch=patch.object(e,'DAO_POLICY',self.policy);self.patch.start();self.addCleanup(self.patch.stop)
  out=e.make_rows(self.folder,self.original,self.inputs,self.root/'report');self.assertEqual(len(out['records']),1);self.row=out['records'][0]
 def test_existing_exporter_dispatch_preservation_and_duplicate(self):
  from tools import export_native_sources as publisher
  report=self.root/'rows.json';report.write_text(json.dumps({'records':[self.row]}));base=dict(functions=[],translation_units=[],matched_functions=0,counts={})
  with patch.object(publisher,'MODULE_SHA256',sha(self.original)):
   new,files,a=publisher.extend_snapshot(base,{},[report],self.write_original(),eh_inputs=self.inputs);self.assertEqual(a['added'],1);self.assertFalse(a['rejected']);self.assertEqual(len(new['translation_units']),1)
   again,againfiles,d=publisher.extend_snapshot(new,files,[report],self.write_original(),eh_inputs=self.inputs);self.assertEqual(d['duplicates_preserved'],1);self.assertEqual(again,new);self.assertEqual(againfiles,files)
 def test_existing_exporter_missing_intake_cannot_accept(self):
  from tools import export_native_sources as publisher
  report=self.root/'rows.json';report.write_text(json.dumps({'records':[self.row]}));base=dict(functions=[],translation_units=[],matched_functions=0,counts={})
  with patch.object(publisher,'MODULE_SHA256',sha(self.original)):
   new,files,a=publisher.extend_snapshot(base,{},[report],self.write_original());self.assertEqual(a['added'],0);self.assertEqual(len(a['rejected']),1)
 def write_original(self):
  p=self.root/'original.exe';p.write_bytes(self.original);return p
 def test_fresh_export(self):
  f,u,s=e.retained_match(self.row,self.original,self.inputs);self.assertEqual(f['status'],e.STATUS);self.assertEqual(u['all_graph_bytes'],101);self.assertNotIn('runtime_identity',u);self.assertEqual(s,self.kw['source'])
 def change_report(self,mutate):
  p=Path(self.row['measurement']['summary']);d=json.loads(p.read_text());mutate(d);p.write_text(json.dumps(d));self.row['measurement']['summary_sha256']=sha(p.read_bytes())
 def test_forged_status(self):
  self.change_report(lambda d:d.update(status='experimental_exact_full_graph'))
  with self.assertRaises(ValueError):e.retained_match(self.row,self.original,self.inputs)
 def test_dropped_node(self):
  self.change_report(lambda d:d['functions'][0]['nodes'].pop('action'))
  with self.assertRaises(ValueError):e.retained_match(self.row,self.original,self.inputs)
 def test_forged_missing_comparison(self):
  self.change_report(lambda d:d.update(functions=[]))
  with self.assertRaises(ValueError):e.retained_match(self.row,self.original,self.inputs)
 def test_stale_summary_hash(self):
  p=Path(self.row['measurement']['summary']);p.write_text(p.read_text()+' ')
  with self.assertRaises(ValueError):e.retained_match(self.row,self.original,self.inputs)
 def test_changed_source_invalidates(self):
  p=self.folder/'candidate.cpp';p.write_bytes(p.read_bytes()+b'\n')
  with self.assertRaises(ValueError):e.retained_match(self.row,self.original,self.inputs)
 def test_changed_object_invalidates(self):
  p=self.folder/'candidate.obj';b=bytearray(p.read_bytes());b[-1]^=1;p.write_bytes(b)
  with self.assertRaises(ValueError):e.retained_match(self.row,self.original,self.inputs)
 def test_changed_original_invalidates(self):
  with self.assertRaises(ValueError):e.retained_match(self.row,self.original+b'\0',self.inputs)
 def test_changed_inventory_invalidates(self):
  p=Path(self.inputs['inventory']);p.write_bytes(p.read_bytes()+b' ')
  with self.assertRaises(ValueError):e.retained_match(self.row,self.original,self.inputs)
 def test_changed_library_invalidates(self):
  p=Path(next(iter(self.inputs['libraries'].values())));p.write_bytes(p.read_bytes()+b' ')
  with self.assertRaises(ValueError):e.retained_match(self.row,self.original,self.inputs)
 def test_changed_compiler_invalidates(self):
  Path(self.inputs['compiler']).write_bytes(b'changed')
  with self.assertRaises(ValueError):e.retained_match(self.row,self.original,self.inputs)
 def test_changed_build_invalidates(self):
  p=self.folder/'run.json';d=json.loads(p.read_text());d['flags']+=['/bad'];p.write_text(json.dumps(d))
  with self.assertRaises(ValueError):e.retained_match(self.row,self.original,self.inputs)
 def test_candidate_policy_override_refused(self):
  self.inputs['policy']=self.policy
  with self.assertRaises(ValueError):e.retained_match(self.row,self.original,self.inputs)
 def test_bool_rva_refused(self):
  self.row['rva']=True
  with self.assertRaises(ValueError):e.retained_match(self.row,self.original,self.inputs)
 def test_partial_malformed_json_refused(self):
  p=Path(self.row['measurement']['summary']);p.write_text('{');self.row['measurement']['summary_sha256']=sha(p.read_bytes())
  with self.assertRaises(ValueError):e.retained_match(self.row,self.original,self.inputs)
 def test_source_path_swap_refused(self):
  p=self.root/'same.cpp';p.write_bytes(self.kw['source']);self.row['source']=str(p)
  with self.assertRaises(ValueError):e.retained_match(self.row,self.original,self.inputs)

if __name__=='__main__':unittest.main()

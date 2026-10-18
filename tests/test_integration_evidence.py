"""Integration packet identities fail closed before review or shared mutation."""
from pathlib import Path
import importlib.util,json,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('integration_evidence',ROOT/'workers/continuation/integration_evidence.py')
e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
class IntegrationEvidenceBindings(unittest.TestCase):
 def test_changed_bytes_rejected(self):
  with tempfile.TemporaryDirectory() as directory:
   p=Path(directory)/'evidence.json';p.write_text('{}');expected=e.sha(p);p.write_text('{"changed":true}')
   with self.assertRaises(ValueError):e.bound(p,expected)
 def test_symlink_rejected(self):
  with tempfile.TemporaryDirectory() as directory:
   p=Path(directory)/'data';p.write_text('x');link=Path(directory)/'link';link.symlink_to(p)
   with self.assertRaises(ValueError):e.bound(link,e.sha(p))
 def test_source_acceptance_required(self):
  with tempfile.TemporaryDirectory() as directory:
   p=Path(directory).resolve();(p/'accepted').mkdir();candidate=p/'accepted/candidate.cpp';candidate.write_text('source')
   package=p/'accepted/package.json';package.write_text(json.dumps({'source_sha256':e.sha(candidate)}));(p/'status.json').write_text('{"accepted":false}');(p/'review-response.json').write_text('{"decision":"approve"}')
   with self.assertRaisesRegex(ValueError,'source acceptance'):e.assemble({'root':directory},{},{'pair':str(p),'package_sha256':e.sha(package)})
if __name__=='__main__':unittest.main()

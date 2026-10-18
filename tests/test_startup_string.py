import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from validation.startup_string_cases import *
from tools import incremental_checkpoint as cache,validate_checkpoint as checkpoint
from tools.daodecomp.harness import load_json
class StartupStringTests(unittest.TestCase):
 def test_domain_edges(self):
  values=cases(NAME);self.assertTrue(any(c['inputs']['string']==BASE for c in values));self.assertTrue(any(c['inputs']['string']%2 for c in values));self.assertTrue(any(c['inputs']['string']==BASE+254 for c in values))
  self.assertTrue(any(expected(c['inputs'])[0]==BASE for c in values));self.assertTrue(any(expected(c['inputs'])[0]==0 for c in values))
 def test_reject_invalid_domain(self):
  base={'arena':('ff'*256),'string':BASE,'search':0}
  for changes in ({},{'string':0},{'string':BASE+255},{'search':True},{'search':1<<32},{'arena':'00'*255},{'arena':'AA'*256},{'string':BASE-1},{'extra':0}):
   with self.subTest(changes=changes),self.assertRaises(ValueError):fixture(NAME,{**base,**changes})
 def test_bound_first_zero(self):
  x={'arena':('0000ffff'+'aa'*252),'string':BASE,'search':0};a,r,w=fixture(NAME,x);self.assertEqual(r,[(0,2)]);self.assertEqual(w,[]);self.assertEqual(expected(x)[0],BASE)
 def test_disjoint_stable_fixtures(self):
  a,b=cases(NAME),cases(NAME,'heldout');self.assertFalse({x['id'] for x in a}&{x['id'] for x in b});self.assertEqual(cases(NAME),a)
  for c in a+b:fixture(NAME,c['inputs'])
 def test_high_bits_ignored(self):
  for c in cases(NAME):
   x=c['inputs'];self.assertEqual(expected(x),expected({**x,'search':x['search']^0xffff0000}))
 def test_checkpoint_route(self):
  r=load_json(ROOT/'analysis/functions.json');entry=load_json(ROOT/'evidence/startup-string-identity.json');entry['status']='implemented';r['functions']=[f for f in r['functions'] if f['name']!=NAME]+[entry]
  self.assertEqual([f['name'] for f in cache.selected_entries(r,'startup_strings')],[NAME]);self.assertIn('startup_strings',cache.required_groups(r));self.assertEqual(len(cache.actual_corpora('startup_strings',[entry])[entry['id']]['positive']['rows']),280)
 def test_complete_publication_projection(self):
  import tempfile
  from unittest.mock import patch
  from tools.update_progress import checkpoint_inventory
  registry=load_json(ROOT/'analysis/functions.json');entry=load_json(ROOT/'evidence/startup-string-identity.json');entry['status']='implemented'
  prior={**registry,'functions':[f for f in registry['functions'] if f['name']!=NAME]}
  projected={**prior,'functions':[*prior['functions'],entry]}
  self.assertEqual(checkpoint_inventory(projected)-checkpoint_inventory(prior),{(entry['id'],False),(entry['id'],True)})
  with tempfile.TemporaryDirectory() as temporary:
   root=Path(temporary);(root/'analysis').mkdir();(root/'analysis/functions.json').write_text(json.dumps(projected))
   with patch.object(checkpoint,'ROOT',root):
    positives,negatives=checkpoint.publication_paths(root/'output')
    self.assertEqual((len(positives),len(negatives)),(94,73))
    # Inspect the supported Unix plan; the Windows full-checkpoint guard remains.
    steps=checkpoint.build_commands(root/'build',root/'output',2,windows=False)
    with self.assertRaises(ValueError):checkpoint.build_commands(root/'build',root/'output',2,windows=True)
    self.assertEqual({n for n,_,_ in steps if n.startswith('startup_strings_')},{'startup_strings_all','startup_strings_negative'})
 def test_original_registry_unmodified(self):
  r=load_json(ROOT/'analysis/functions.json');self.assertEqual(len({x['id'] for x in r['functions']}),len(r['functions']))

 def test_invalid_startup_route_refuses(self):
  import copy
  registry=load_json(ROOT/'analysis/functions.json')
  for key,value in [('name','unknown'),('recovery_group','unknown'),('id','wrong'),('rva',0),('size',47),('source','src/other.cpp')]:
   r=copy.deepcopy(registry);r['functions'][-1]['status']='implemented';r['functions'][-1][key]=value
   with self.subTest(key=key),self.assertRaises(ValueError):cache.required_groups(r)

if __name__=='__main__':unittest.main()

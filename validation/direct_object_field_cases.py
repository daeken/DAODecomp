"""Exact frozen descriptor-domain corpora; no fixture regeneration."""
import json,re
from pathlib import Path
from tools.daodecomp.harness import file_hash,load_json
from validation.direct_field_batch_runner import fixture
ROOT=Path(__file__).resolve().parents[1]
HASH_MAP = 'validation/direct_object_field_corpus_hashes.json'
GROUP = 'direct-object-fields-001'
ACTIVE = {'implemented','corpus_pass','reviewed','integrated'}

def descriptor_domain(rows):
 if type(rows) is not list or not rows or any(type(f) is not dict for f in rows):raise ValueError('nonempty descriptor domain required')
 names=[f.get('name') for f in rows];identities=[f.get('id') for f in rows]
 if any(type(n) is not str or re.fullmatch(r'fn_[0-9a-f]{8}',n) is None for n in names) or any(type(i) is not str or not i for i in identities):raise ValueError('invalid descriptor identity')
 if len(set(names))!=len(rows) or len(set(identities))!=len(rows):raise ValueError('duplicate descriptor domain')
 return rows

def registry_domain(rows,functions):
 descriptor_domain(rows)
 registry=[f for f in functions if f.get('backend')==GROUP or f.get('recovery_group')==GROUP]
 if len(registry)!=len(rows) or any(f.get('backend')!=GROUP or f.get('recovery_group')!=GROUP or f.get('status') not in ACTIVE for f in registry):raise ValueError('incomplete registry domain')
 if len({f.get('id') for f in registry})!=len(rows) or len({f.get('name') for f in registry})!=len(rows) or {f.get('name') for f in registry}!={f['name'] for f in rows}:raise ValueError('registry/descriptor domain mismatch')
 by_name={f['name']:f for f in registry}
 for f in rows:
  r=by_name[f['name']]
  if any(r.get(k)!=f[k] for k in ('id','rva','size','code_sha256','module_sha256')) or r.get('contract')!=f"contracts/{f['name']}.json" or r.get('source')!='src/direct_object_fields.cpp':raise ValueError('registry/slice/contract binding mismatch')
 return rows

SPECS={f['name']:f for f in descriptor_domain(load_json(ROOT/'slices.json'))}
NAMES=tuple(SPECS)
NEGATIVE_NAMES=NAMES

def corpus_hashes(path=None,names=None):
 path=ROOT/HASH_MAP if path is None else Path(path)
 if path.is_symlink() or not path.is_file():raise ValueError('regular direct-field corpus hash map required')
 values=load_json(path);names=NAMES if names is None else names
 expected={f'{name}-{suite}.json' for name in names for suite in ('public','heldout')}
 if type(values) is not dict or set(values)!=expected or not expected:raise ValueError('corpus hash-map domain mismatch')
 if any(type(value) is not str or re.fullmatch(r'[0-9a-f]{64}',value) is None for value in values.values()):raise ValueError('invalid corpus SHA256')
 return values

# Validate the frozen external domain on import; calls re-read it rather than
# silently retaining stale data if the file changes within this process.
corpus_hashes()
def cases(name,suite='public'):
 if name not in SPECS or suite not in ('public','heldout'):raise ValueError('unknown function/suite')
 path=ROOT/'corpus'/f'{name}-{suite}.json'
 if file_hash(path)!=corpus_hashes()[path.name]:raise ValueError('frozen direct-field corpus changed')
 result=load_json(path)
 for case in result:fixture(SPECS[name],case['inputs'])
 return result
def negative_cases(name):return cases(name,'public')

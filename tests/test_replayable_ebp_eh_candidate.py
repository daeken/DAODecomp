"""Open COFF/PE graph constructions; diagnostic equality is never acceptance."""
import copy,struct,unittest
from test_eh_graph import coff,pe
from tools.replayable.ebp_eh_candidate import inspect
from tools.replayable.ebp_eh_compare import compare
P='?open@@YAII@Z';H='__ehhandler$'+P;D='__ehfuncinfo$'+P;U='__unwindtable$'+P;T='__tryblocktable$'+P
A='__catchsym$'+P+'$4';B='__catchsym$'+P+'$5';C='__catch$'+P+'$0';E='__catch$'+P+'$1';L='$continuation'
def fixture():
 main=bytes.fromhex('558bec6aff680000000064a100000000eb07b800000000c390c3cc')
 hb=bytes.fromhex('8b5424088d420c8b4ae433c8e800000000b800000000e900000000')
 db=struct.pack('<4I',64,0,0,0)*2+b''.join(struct.pack('<iI',p,0)for p in(-1,-1,1,1))+struct.pack('<9I',0x19930522,4,0,2,0,0,0,0,1)+struct.pack('<10I',2,2,3,1,0,0,0,3,1,0)
 sections=[('.text',main,[(6,H,6),(19,L,6)],0x60001020),('.text$x',hb,[(13,'cookie',20),(18,D,6),(23,'runtime',20)],0x60000020),('.xdata$x',db,[(12,C,6),(28,E,6),(72,U,6),(80,T,6),(116,B,6),(136,A,6)],0x40000040)]
 symbols=[(P,0,1,32,2,None),(C,18,1,32,3,None),(E,26,1,32,3,None),(L,24,1,0,6,None),(H,0,2,32,3,None),(D,64,3,0,3,None),(U,32,3,0,3,None),(T,100,3,0,3,None),(A,0,3,0,3,None),(B,16,3,0,3,None),('cookie',0,0,32,2,None),('runtime',0,0,32,2,None)]
 placements={name:[0x401000,0x401100,0x401200][sec-1]+off for name,off,sec,*_ in symbols if sec>0};placements.update(cookie=0x401400,runtime=0x401401)
 body=bytearray(b'\xcc'*0x500)
 for si,(_,data,rels,_)in enumerate(sections):
  data=bytearray(data);base=[0x401000,0x401100,0x401200][si]
  for off,sym,kind in rels:struct.pack_into('<I',data,off,(placements[sym]-(base+off+4)if kind==20 else placements[sym])&0xffffffff)
  body[base-0x401000:base-0x401000+len(data)]=data
 return pe(body),sections,symbols,[(0x401000,0x401012),(0x401019,0x40101a)]
def mutate_section(sections,index,off,value):
 n,b,r,f=sections[index];b=bytearray(b);b[off:off+len(value)]=value;sections[index]=(n,bytes(b),r,f)
class CandidateEhTests(unittest.TestCase):
 def test_all_bytes_and_return_continuation_retained_with_trap_unknown(self):
  _,s,y,_=fixture();r=inspect(coff(s,y),P);self.assertEqual(r['complete_code_bytes'],27);self.assertEqual(r['complete_metadata_and_handler_bytes'],167);self.assertFalse(r['acceptance_supported']);self.assertFalse(r['proof']);self.assertEqual(len(r['dependencies']),3);self.assertTrue(any(e['kind']=='architectural_trap_unknown'for d in r['dependencies']for e in d['edges']))
 def test_complete_pair_accounts_every_byte_but_external_identity_unknown(self):
  o,s,y,owned=fixture();r=compare(o,owned,coff(s,y),P);self.assertEqual(r['state'],'diagnostic_external_identity_unresolved',r);self.assertEqual(r['counts'],dict(equal=186,different=0,unresolved=8,original=194,candidate=194));self.assertEqual(len(r['nodes']),10);self.assertFalse(r['acceptance_supported']);self.assertNotIn('full_match',r)
 def test_catch_and_continuation_mutations_are_never_dropped(self):
  for off in (24,):
   o,s,y,owned=fixture();mutate_section(s,0,off,b'\x40');r=compare(o,owned,coff(s,y),P);self.assertEqual(r['state'],'diagnostic_differences',r);self.assertEqual(r['counts']['different'],1)
  o,s,y,owned=fixture();mutate_section(s,0,26,b'\x90');r=compare(o,owned,coff(s,y),P);self.assertEqual(r['state'],'diagnostic_incomplete')
 def test_main_span_must_include_both_owned_fragments(self):
  o,s,y,owned=fixture();r=compare(o,owned[:1],coff(s,y),P);self.assertIn('original_main_CFG_inventory_disagrees',r['blockers'])
 def test_extra_bytes_nodes_and_overlapping_tables_refuse(self):
  changes=[lambda s,y:s.__setitem__(0,(s[0][0],s[0][1]+b'\xcc',s[0][2],s[0][3])),lambda s,y:y.append(('__catch$'+P+'$9',26,1,32,3,None)),lambda s,y:y.__setitem__(8,(A,16,3,0,3,None)),lambda s,y:s.__setitem__(1,(s[1][0],s[1][1]+b'\x90',s[1][2],s[1][3]))]
  for edit in changes:
   _,s,y,_=fixture();edit(s,y)
   with self.assertRaises(ValueError):inspect(coff(s,y),P)
 def test_missing_metadata_reference_and_nonzero_addend_refuse(self):
  _,s,y,_=fixture();n,b,r,f=s[2];s[2]=(n,b,r[:-1],f)
  with self.assertRaises(ValueError):inspect(coff(s,y),P)
  _,s,y,_=fixture();mutate_section(s,2,72,struct.pack('<I',4))
  with self.assertRaises(ValueError):inspect(coff(s,y),P)
 def test_continuation_into_instruction_or_catch_refuses(self):
  for target in (2,18,19):
   _,s,y,_=fixture();y[3]=(L,target,1,0,6,None)
   with self.assertRaises(ValueError):inspect(coff(s,y),P)
 def test_wrong_parent_and_nonzero_unwind_action_refuse(self):
  _,s,y,_=fixture();name='__catch$wrong$0';y[1]=(name,18,1,32,3,None);n,b,r,f=s[2];s[2]=(n,b,[(at,name if symbol==C else symbol,k)for at,symbol,k in r],f)
  with self.assertRaises(ValueError):inspect(coff(s,y),P)
  _,s,y,_=fixture();mutate_section(s,2,36,struct.pack('<I',1))
  with self.assertRaises(ValueError):inspect(coff(s,y),P)

class DiagnosticIsolationTests(unittest.TestCase):
 def test_diagnostic_cannot_override_independent_EH_refusal(self):
  import tempfile,json,hashlib,importlib.util
  from pathlib import Path
  from unittest.mock import patch
  from rapid_object import eh_native
  from tools.replayable import ebp_eh_compare
  root=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('ebp_compare_bridge',root/'tools/decompilation-mcp/replayable_adapter.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
  o,s,y,owned=fixture();name='?fn_00001000@@YAII@Z';rename=lambda n:n.replace(P,name);y=[(rename(n),*rest)for n,*rest in y];s=[(n,b,[(at,rename(t),k)for at,t,k in rels],f)for n,b,rels,f in s];obj=coff(s,y);sha=lambda b:hashlib.sha256(b).hexdigest()
  with tempfile.TemporaryDirectory()as t:
   folder=Path(t);build=folder/'build';build.mkdir();source='// Synthetic adapter isolation fixture, not compiled evidence.\n';compiler=b'open compiler';ci=dict(sha256=sha(compiler));receipt=dict(exit_code=0,compiler=ci,flags=[],source_sha256=sha(source.encode()),module_sha256=sha(o),linked=False,original_executed=False,object_sha256=sha(obj));entry=dict(rva=0x1000,body_ranges=[dict(start_rva=lo-0x400000,end_rva_inclusive=hi-0x400001)for lo,hi in owned]);inv=dict(module_sha256=sha(o),functions=[entry])
   for path,data in [('candidate.cpp',source.encode()),('original.exe',o),('compiler.exe',compiler),('inventory.json',json.dumps(inv).encode()),('policy.json',b'{}'),('library.lib',b'open library'),('build/candidate.cpp',source.encode()),('build/candidate.obj',obj),('build/compiler.json',json.dumps(ci).encode()),('build/run.json',json.dumps(receipt).encode()),('build/build-exit.txt',b'0')]: (folder/path).write_bytes(data)
   project=dict(original=str(folder/'original.exe'),inventory=str(folder/'inventory.json'),module_sha256=sha(o),compiler=str(folder/'compiler.exe'),compiler_sha256=sha(compiler),compiler_flags=[],eh_policy=str(folder/'policy.json'),libraries={'open.lib':str(folder/'library.lib')});request=dict(project=project,rva=0x1000,entry=entry)
   with patch.object(eh_native,'check',return_value=dict(status='inconclusive',backend='open_test_only',functions=[])),patch.object(ebp_eh_compare,'compare',return_value=dict(status='full_match',forged_diagnostic=True)):
    r=a.compare_built(request,folder,source)
   self.assertEqual(r['status'],'inconclusive');self.assertEqual(json.loads((folder/'range-eh-comparison.json').read_text())['status'],'full_match');self.assertEqual(json.loads((folder/'comparison.json').read_text())['status'],'inconclusive')

class BoundNonmatchTests(unittest.TestCase):
 def test_external_binding_diagnostic_stays_nonaccepting_even_when_equal(self):
  o,s,y,owned=fixture();r=compare(o,owned,coff(s,y),P,external_bindings=dict(cookie=0x401400,runtime=0x401401));self.assertEqual(r['counts']['unresolved'],0);self.assertEqual(r['counts']['different'],0);self.assertFalse(r['acceptance_supported'])
 def test_strict_nonmatch_route_never_accepts_diagnostic_equality(self):
  from unittest.mock import patch
  from tools.replayable.ebp_eh_native import compare_nonmatch
  o,s,y,owned=fixture();spec={0x1000:dict(symbol=P,ranges=[dict(start_rva=lo-0x400000,end_rva_inclusive=hi-0x400001)for lo,hi in owned])};roots=dict(root_bindings=dict(cookie=0x401400,runtime=0x401401))
  with patch('tools.replayable.ebp_eh_native.derive',return_value=dict(target=0x401402)):
   r=compare_nonmatch(o,b'open inventory',{},coff(s,y),spec,{},roots);self.assertEqual(r['status'],'inconclusive');self.assertFalse(r['acceptance_supported']);self.assertTrue(r['functions'][0]['all_bytes_accounted'])
   mutate_section(s,0,24,b'\x40');r=compare_nonmatch(o,b'open inventory',{},coff(s,y),spec,{},roots);self.assertEqual(r['status'],'eh_graph_nonmatch');self.assertEqual(r['functions'][0]['counts']['different'],1);self.assertFalse(r['acceptance_supported'])
 def test_unowned_or_unresolved_graph_never_becomes_exact(self):
  from unittest.mock import patch
  from tools.replayable.ebp_eh_native import compare_nonmatch
  o,s,y,owned=fixture();spec={0x1000:dict(symbol=P,ranges=[dict(start_rva=lo-0x400000,end_rva_inclusive=hi-0x400001)for lo,hi in owned])}
  with patch('tools.replayable.ebp_eh_native.derive',return_value=dict(target=0x401402)):
   r=compare_nonmatch(o,b'open inventory',{},coff(s,y),spec,{},dict(root_bindings={}));self.assertEqual(r['status'],'inconclusive');self.assertEqual(r['functions'][0]['counts']['unresolved'],8)
   spec[0x1000]['ranges']=spec[0x1000]['ranges'][:1];r=compare_nonmatch(o,b'open inventory',{},coff(s,y),spec,{},dict(root_bindings={}));self.assertEqual(r['status'],'inconclusive');self.assertFalse(r['functions'][0]['all_bytes_accounted'])

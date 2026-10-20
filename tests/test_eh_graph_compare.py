import copy,hashlib,json,struct,sys,unittest
from pathlib import Path
R=next(p for p in Path(__file__).resolve().parents if (p/'rapid_object/coff.py').is_file());O=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tests')]
try:
 from rapid_object.eh_graph_compare import compare_graphs,compare_node
except ModuleNotFoundError:
 sys.path.insert(0,str(O/'proposed'));from eh_graph_compare import compare_graphs,compare_node
from test_eh_graph import fixture,coff,H,A,D,U
sha=lambda b:hashlib.sha256(b).hexdigest()
def inputs():
 o,secs,syms,req=fixture(True,True);o=bytearray(o);o[0x600:0x605]=bytes.fromhex('e94b000000');o=bytes(o)
 secs.append(('.helper',bytes.fromhex('e900000000'),[(1,'_fn_00001450',20)],0x60000020));syms=[(n,v,4 if n=='_fn_00001400' else sec,t,st,5 if n=='_fn_00001400' else size) for n,v,sec,t,st,size in syms];syms.append(('_fn_00001450',0,0,32,2,None));return o,secs,syms,req
class Tests(unittest.TestCase):
 def run_case(self,mutate=None,bindings=None):
  o,s,y,r=inputs()
  if mutate:o,s,y,r=mutate(o,s,y,r)
  return compare_graphs(o,coff(s,y),r,{'_fn_00001450':0x401450,**(bindings or {})},module_sha256=sha(o))
 def incomplete(self,r):self.assertFalse(r['acceptance_supported']);self.assertTrue(r.get('error') or any(f['state']=='incomplete' for f in r['functions']))
 def test_all_bytes_and_unknowns_present(self):
  r=self.run_case();f=r['functions'][0];self.assertTrue(f['complete_byte_accounting']);self.assertEqual(f['compared_graph_nodes'],6);self.assertEqual(f['counts']['unresolved_relocation'],8);self.assertNotIn('different',f['counts']);self.assertFalse(r['acceptance_supported'])
 def test_wrong_main_byte(self):
  def m(o,s,y,r):b=bytearray(s[0][1]);b[-1]=0x90;s[0]=(s[0][0],bytes(b),s[0][2],s[0][3]);return o,s,y,r
  self.assertEqual(self.run_case(m)['functions'][0]['counts']['different'],1)
 def test_runtime_claim_conflict_kept(self):
  r=self.run_case(bindings={'___CxxFrameHandler3':0x401501});self.assertIn('runtime_target_address_claim_conflict',r['functions'][0]['upstream_differences']);self.assertEqual(r['functions'][0]['counts']['unresolved_relocation'],8)
 def test_wrong_runtime_reference(self):
  def m(o,s,y,r):sec=s[1];rels=[(a,'_fn_00001450' if n=='___CxxFrameHandler3' else n,k) for a,n,k in sec[2]];s[1]=(sec[0],sec[1],rels,sec[3]);return o,s,y,r
  self.assertGreater(self.run_case(m)['functions'][0]['counts'].get('different',0),0)
 def test_wrong_frame_offset(self):
  def m(o,s,y,r):sec=s[1];b=bytearray(sec[1]);b[2]=0xec;s[1]=(sec[0],bytes(b),sec[2],sec[3]);return o,s,y,r
  self.assertEqual(self.run_case(m)['functions'][0]['counts']['different'],1)
 def test_wrong_map_state(self):
  def m(o,s,y,r):sec=s[2];b=bytearray(sec[1]);struct.pack_into('<i',b,0,-2);s[2]=(sec[0],bytes(b),sec[2],sec[3]);return o,s,y,r
  self.incomplete(self.run_case(m))
 def test_dropped_map_reference(self):
  def m(o,s,y,r):sec=s[2];s[2]=(sec[0],sec[1],sec[2][1:],sec[3]);return o,s,y,r
  self.incomplete(self.run_case(m))
 def test_extra_action(self):
  def m(o,s,y,r):y.append((A[:-1]+'1',0,2,32,3,None));return o,s,y,r
  self.incomplete(self.run_case(m))
 def test_missing_action(self):
  def m(o,s,y,r):y=[v for v in y if v[0]!=A];sec=s[2];s[2]=(sec[0],sec[1],[(a,H if n==A else n,k) for a,n,k in sec[2]],sec[3]);return o,s,y,r
  self.incomplete(self.run_case(m))
 def test_ambiguous_generated_reference(self):
  def m(o,s,y,r):y.append((H,11,2,32,3,None));return o,s,y,r
  self.incomplete(self.run_case(m))
 def test_wrong_helper_destination(self):
  def m(o,s,y,r):sec=s[3];s[3]=(sec[0],sec[1],[(1,'_fn_00001460',20)],sec[3]);y.append(('_fn_00001460',0,0,32,2,None));return o,s,y,r
  self.assertGreater(self.run_case(m,{'_fn_00001460':0x401460})['functions'][0]['counts']['different'],0)
 def test_helper_boundary(self):
  def m(o,s,y,r):y=[(n,v,sec,t,st,4 if n=='_fn_00001400' else size) for n,v,sec,t,st,size in y];return o,s,y,r
  self.incomplete(self.run_case(m))
 def test_original_helper_overlaps_other_node(self):
  def m(o,s,y,r):o=bytearray(o);struct.pack_into('<i',o,0x505,0x401116-0x401309);return bytes(o),s,y,r
  self.incomplete(self.run_case(m))
 def test_nonzero_handler_addend_refuses(self):
  def m(o,s,y,r):sec=s[1];b=bytearray(sec[1]);b[11+18]=1;s[1]=(sec[0],bytes(b),sec[2],sec[3]);return o,s,y,r
  self.incomplete(self.run_case(m))
 def test_missing_main_relocation(self):
  def m(o,s,y,r):sec=s[0];s[0]=(sec[0],sec[1],[],sec[3]);return o,s,y,r
  self.incomplete(self.run_case(m))
 def test_byte_engine_never_masks_unknown(self):
  r=compare_node(bytes(4),bytes(4),[dict(offset=0,kind=6,symbol='unknown')],0,lambda n,index:(None,'unknown'));self.assertEqual(len(r['bytes']),4);self.assertTrue(all(x['state']=='unresolved_relocation' for x in r['bytes']))
 def test_byte_engine_extra_and_dropped_bytes(self):
  self.assertEqual(compare_node(b'1',b'12',[],0,lambda n,index:None)['counts']['missing_original_byte'],1);self.assertEqual(compare_node(b'12',b'1',[],0,lambda n,index:None)['counts']['missing_candidate_byte'],1)
 def test_crossing_and_overlapping_fields(self):
  for rels in [[dict(offset=1,kind=6,symbol='x')],[dict(offset=0,kind=6,symbol='x')]*2]:
   with self.assertRaises(ValueError):compare_node(bytes(4),bytes(4),rels,0,lambda n,index:(1,'test'))
 def test_wrong_main_target(self):
  def m(o,s,y,r):sec=s[0];s[0]=(sec[0],sec[1],[(3,D,6)],sec[3]);return o,s,y,r
  self.incomplete(self.run_case(m))
 def test_wrong_descriptor_state_count(self):
  def m(o,s,y,r):sec=s[2];b=bytearray(sec[1]);struct.pack_into('<I',b,12,2);s[2]=(sec[0],bytes(b),sec[2],sec[3]);return o,s,y,r
  self.incomplete(self.run_case(m))
 def test_runtime_cannot_be_bound_by_generated_alias(self):
  r=self.run_case(bindings={H:0x401100,D:0x401208,U:0x401200,A:0x401300,'___CxxFrameHandler3':0x401500,'__security_check_cookie':0x401600});self.assertFalse(r['acceptance_supported']);self.assertEqual(r['functions'][0]['counts']['unresolved_relocation'],8)
 def test_helper_nonzero_addend_compares_not_masks(self):
  def m(o,s,y,r):sec=s[3];b=bytearray(sec[1]);struct.pack_into('<I',b,1,1);s[3]=(sec[0],bytes(b),sec[2],sec[3]);return o,s,y,r
  self.assertGreater(self.run_case(m)['functions'][0]['counts']['different'],0)
 def test_distinct_same_name_defined_symbols_keep_relocation_indexes(self):
  from rapid_object.coff import Coff
  o,s,y,r=inputs();o=bytearray(o);o[0x600:0x605]=bytes.fromhex('e9fbffffff');o=bytes(o)
  sec=s[3];s[3]=(sec[0],sec[1],[(1,'_fn_00001400',20)],sec[3]);s.append(('.extra',b'\xc3',[],0x60000020));y.append(('_fn_00001400',0,5,32,2,1));raw=bytearray(coff(s,y));obj=Coff(raw);definitions=[v for v in obj.symbols.values() if v.name=='_fn_00001400'];paired=next(v for v in definitions if v.section==4);unpaired=next(v for v in definitions if v.section==5)
  # The action selects the first definition, while helper JMP selects the second.
  _,_,_,_,_,_,_=struct.unpack_from('<HHIIIHH',raw,0);relptr=struct.unpack_from('<I',raw,20+40+24)[0];struct.pack_into('<I',raw,relptr+4,paired.index)
  result=compare_graphs(o,bytes(raw),r,{'_fn_00001450':0x401450},module_sha256=sha(o));row=result['functions'][0];self.assertEqual(row['state'],'incomplete');self.assertFalse(row['graph_dependency_coverage_complete']);helper=row['nodes']['delete_helper'];self.assertEqual(helper['counts']['unresolved_relocation'],4);self.assertEqual(helper['relocations'][0]['symbol_index'],unpaired.index);self.assertEqual(row['nodes']['action']['relocations'][0]['symbol_index'],paired.index);self.assertFalse(result['acceptance_supported'])

"""Open ownership/EBP metadata cases; no original bytes or acceptance fixtures."""
import copy,hashlib,json,struct,subprocess,unittest
from pathlib import Path
from tools.replayable.range_lift import spans,combine
from tools.replayable.range_eh import metadata,reachable
from test_replayable_ir import DLL,DOTNET,node,const

def part(pc,raw,body):
 return dict(mode='Bits32',pc=pc,byte_length=len(raw),decoded_bytes=len(raw),decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=[dict(pc=pc,length=len(raw),raw_hex=raw.hex(),tree=node('IlBlock',Body=body))])
def envelope():
 return combine([part(0x1000,b'\xeb\x0e',[node('IlBranch',Kind=dict(name='Jmp'),Cond=None,Target=const(0x1010))]),part(0x1010,b'\xc3',[node('IlBranch',Kind=dict(name='Ret'),Cond=None,Target=const(0))])],[(0x1000,0x1001),(0x1010,0x1010)],0)
class OwnedRangeTests(unittest.TestCase):
 def test_accounted_ranges_do_not_create_linear_instructions(self):
  x=envelope();self.assertNotIn('instructions',x);self.assertEqual(x['owned_bytes'],3);self.assertEqual(x['excluded_intervals'],[dict(start_va=0x1002,end_va_exclusive=0x1010)]);self.assertEqual(x['ranges'][1]['lift']['instructions'][0]['pc'],0x1010)
 def test_invalid_inventory_ranges(self):
  for ranges,count in [([],0),([(2,1)],0),([(0,3),(2,5)],8),([(4,5),(0,1)],4),([(1,2)],2),([(0,1)],3)]:
   with self.assertRaises(ValueError):spans(dict(body_ranges=[dict(start_rva=a,end_rva_inclusive=b)for a,b in ranges],body_bytes=count),0)
 def test_incomplete_misaligned_or_opaque_lift_refuses(self):
  for change in [lambda p:p.update(mode='Bits64'),lambda p:p.update(opaque_instructions=1),lambda p:p.update(decode_complete=False),lambda p:p['instructions'][0].update(pc=0x1001),lambda p:p.update(decoded_bytes=0)]:
   p=part(0x1000,b'\xc3',[]);change(p)
   with self.assertRaises(ValueError):combine([p],[(0x1000,0x1000)],0)
 @unittest.skipUnless(DLL.exists(),'build changed core first')
 def test_core_preserves_cross_range_jump_and_dynamic_return(self):
  x=self.core(envelope());self.assertEqual(x['status'],'inspected',x);self.assertEqual(x['ir']['owned_bytes'],3);self.assertIn(dict(pc=0x1000,kind='Jmp',target=0x1010,ownership='owned_instruction'),x['ir']['edges']);self.assertFalse(x['proof']);self.assertEqual(x['source_emission'],'unsupported')
 def core(self,x):return json.loads(subprocess.check_output([DOTNET,str(DLL),'recover-ir'],input=json.dumps(dict(owned_ranges=True,lift=x)).encode()))
 @unittest.skipUnless(DLL.exists(),'build changed core first')
 def test_core_rejects_tampered_accounting_hash_and_middle_target(self):
  for edit in [lambda x:x.update(owned_bytes=99),lambda x:x.update(entry_va=0x1010),lambda x:x['ranges'][0].update(slice_sha256='0'*64),lambda x:x['ranges'][0]['lift']['instructions'][0]['tree']['Body'][0].update(Target=const(0x1001))]:
   x=envelope();edit(x);self.assertEqual(self.core(x)['status'],'unsupported')
 @unittest.skipUnless(DLL.exists(),'build changed core first')
 def test_fallthrough_into_gap_is_explicit_external_not_next_range(self):
  x=envelope();x['ranges'][0]['lift']['instructions'][0]['tree']['Body']=[];r=self.core(x);self.assertEqual(r['status'],'inspected',r);self.assertEqual(r['ir']['edges'][0],dict(pc=0x1000,kind='fallthrough',target=0x1002,ownership='outside_owned_ranges'))

class Reader:
 def __init__(self):self.memory={}
 def put(self,va,raw):self.memory.update({va+i:b for i,b in enumerate(raw)})
 def read(self,va,size,code=False):return bytes(self.memory[va+i]for i in range(size))
def eh_fixture():
 r=Reader();handler=0x2000;descriptor=0x3000;unwind=0x3100;tries=0x3200;h1=0x3300;h2=0x3400
 prefix=bytes.fromhex('558bec6aff68')+struct.pack('<I',handler)+bytes.fromhex('64a100000000')
 hb=bytearray(bytes.fromhex('8b5424088d420c8b4ae433c8e800000000b800000000e900000000'));struct.pack_into('<I',hb,18,descriptor);r.put(handler,hb);r.put(handler+17,b'\xb8');r.put(handler+27,b'\xc3')
 r.put(descriptor,struct.pack('<9I',0x19930522,4,unwind,2,tries,0,0,0,1));r.put(unwind,b''.join(struct.pack('<iI',p,0)for p in [-1,-1,1,1]));r.put(tries,struct.pack('<10I',2,2,3,1,h1,0,0,3,1,h2));r.put(h1,struct.pack('<4I',64,0,0,0x4000));r.put(h2,struct.pack('<4I',64,0,0,0x4100));r.put(0x4000,b'\xc3');r.put(0x4100,b'\xcc');return r,prefix
class RangeEhInspectionTests(unittest.TestCase):
 def test_rooted_four_state_two_try_zero_action_graph(self):
  r,p=eh_fixture();x=metadata(r,p);self.assertEqual(x['FuncInfo']['states'],4);self.assertEqual(len(x['try_map']['entries']),2);self.assertEqual(x['unwind_map']['transitions'][2]['to_state'],1);self.assertFalse(x['exception_semantics_proven']);self.assertFalse(x['source_recovery_supported'])
 def test_root_prefix_not_descriptor_lookalike(self):
  r,p=eh_fixture()
  with self.assertRaises(ValueError):metadata(r,b'\x90'+p[1:])
 def test_cycles_actions_wrong_types_or_state_extent_refuse(self):
  for va,raw in [(0x3100,struct.pack('<iI',0,0)),(0x3100,struct.pack('<iI',-1,0x9999)),(0x3300,struct.pack('<4I',0,1,0,0x4000)),(0x3200,struct.pack('<5I',2,3,4,1,0x3300))]:
   r,p=eh_fixture();r.put(va,raw)
   with self.assertRaises(ValueError):metadata(r,p)
 def test_initial_metadata_nodes_cannot_overlap(self):
  r,p=eh_fixture();r.put(0x3000+8,struct.pack('<I',0x3000))
  with self.assertRaises(ValueError):metadata(r,p)
 def test_handler_table_overlap_refuses(self):
  r,p=eh_fixture();r.put(0x3200+16,struct.pack('<I',0x3000))
  with self.assertRaises(ValueError):metadata(r,p)
 def test_reachable_dependencies_do_not_own_parent_bytes(self):
  r=Reader();r.put(0x4000,bytes.fromhex('b810400000c3'));r.put(0x4010,b'\x90\x90');x=reachable(r,0x4000,[(0x4012,0x4013)]);self.assertEqual(x['continuation_candidates'],[0x4010]);self.assertEqual(len(x['instructions']),2)
  c=reachable(r,0x4010,[(0x4012,0x4013)]);self.assertEqual(c['edges'][-1]['scope'],'parent_owned');self.assertFalse(c['semantics_proven'])
 def test_call_may_return_and_trap_is_not_a_success_stub(self):
  r=Reader();r.put(0x4000,bytes.fromhex('e8fb0f0000cc'));x=reachable(r,0x4000,[]);self.assertEqual(len(x['instructions']),2);self.assertEqual([e['kind']for e in x['edges']],['call_effects_throw_termination_unknown','fallthrough','architectural_trap'])
 def test_dependency_budget_and_indirect_edges_refuse(self):
  r=Reader();r.put(0x4000,b'\x90'*16)
  with self.assertRaises(ValueError):reachable(r,0x4000,[],max_instructions=2)
  r=Reader();r.put(0x4000,bytes.fromhex('ffe0'))
  with self.assertRaises(ValueError):reachable(r,0x4000,[])
 def test_overlapping_parent_instruction_refuses(self):
  r=Reader();r.put(0x4000,bytes.fromhex('b801000000c3'))
  with self.assertRaises(ValueError):reachable(r,0x4000,[(0x4002,0x4003)])

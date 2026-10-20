"""Synthetic only: no original/CRT proprietary bytes; never game evidence."""
import copy,hashlib,json,struct,sys,unittest
from pathlib import Path
R=next(p for p in Path(__file__).resolve().parents if (p/'rapid_object/coff.py').is_file());sys.path[:0]=[str(R),str(R/'tests'),str(Path(__file__).resolve().parent/'proposed')]
from test_eh_graph_compare import inputs
from test_eh_graph import coff,PARENT
from rapid_object.coff import Coff
try:
 from rapid_object.static_crt_identity import ROOTS,recognize,canonical
 from rapid_object.eh_native import check,terminal_profile
except ModuleNotFoundError:
 from static_crt_identity import ROOTS,recognize,canonical
 from eh_native import check,terminal_profile
sha=lambda b:hashlib.sha256(b).hexdigest()

def archive(objects):
 out=bytearray(b'!<arch>\n')
 for i,raw in enumerate(objects):
  name=('unit%d.obj/'%i).ljust(16);out.extend((name+'0'.ljust(12)+'0'.ljust(6)+'0'.ljust(6)+'100644'.ljust(8)+str(len(raw)).ljust(10)+'`\n').encode());out.extend(raw)
  if len(raw)%2:out.extend(b'\n')
 return bytes(out)


def runtime_objects():
 def fn(name,code,rels):
  symbols=[(name,0,1,32,2,len(code))]+[(n,0,0,0 if n==ROOTS[2] else 32,2,None) for _,n,_ in rels]
  return coff([('.text',code,rels,0x60000020)],symbols)
 result=[fn(ROOTS[0],b'\xe9'+bytes(4),[(1,'internal',20)]),fn(ROOTS[1],bytes.fromhex('8b0d00000000e900000000'),[(2,ROOTS[2],6),(7,'report',20)]),fn('internal',bytes.fromhex('b801000000c3'),[]),fn('report',bytes.fromhex('b802000000c3'),[])]
 data=bytearray(coff([('.data',bytes.fromhex('a1b2c3d4'),[],0xc0101040)],[(ROOTS[2],0,1,0,2,None),('.data',0,1,0,3,4)]));symoff=struct.unpack_from('<I',data,8)[0];aux=symoff+36;data[aux:aux+18]=bytes(18);struct.pack_into('<I',data,aux,4);data[aux+14]=2;result.append(bytes(data));return result


def fixture():
 o,s,y,req=inputs();o=bytearray(o)
 def rel(site,target):return struct.pack('<i',target-(site+4))
 o[0x200+0x500:0x200+0x505]=b'\xe9'+rel(0x401501,0x401650)
 o[0x200+0x600:0x200+0x60b]=b'\x8b\x0d'+struct.pack('<I',0x402000)+b'\xe9'+rel(0x401607,0x401670)
 o[0x200+0x650:0x200+0x656]=bytes.fromhex('b801000000c3');o[0x200+0x670:0x200+0x676]=bytes.fromhex('b802000000c3');o[0x200+0x450]=0xc3
 struct.pack_into('<H',o,0x86,2);struct.pack_into('<8sIIIIIIHHI',o,0x1a0,b'.data',4,0x2000,4,len(o),0,0,0,0,0xc0000040);o.extend(bytes.fromhex('a1b2c3d4'));o=bytes(o)
 for i,sec in enumerate(s):s[i]=(sec[0],sec[1],[(a,ROOTS[1] if n=='__security_check_cookie' else n,k) for a,n,k in sec[2]],sec[3])
 y=[(ROOTS[1] if n=='__security_check_cookie' else n,v,c,t,st,size) for n,v,c,t,st,size in y]
 inv={'module_sha256':sha(o),'image_base':0x400000,'functions':[{'rva':rva,'body_ranges':[{'start_rva':rva,'end_rva_inclusive':rva+n-1}]} for rva,n in ((0x1000,14),(0x1400,5),(0x1450,1),(0x1500,5),(0x1600,11),(0x1650,6),(0x1670,6))]}
 compiler=b'SYNTHETICnotanactualcompiler';source=b'// FUNCTION: SYNTHETIC 0x00401000\nvoid fn_00001000();\n';libs={'crt.lib':archive(runtime_objects())};obj=coff(s,y);flags=['/c','/GS','/EHsc']
 invraw=canonical(inv);pins=dict(module_sha256=sha(o),inventory_sha256=sha(invraw),compiler_sha256=sha(compiler),libraries_sha256={n:sha(v) for n,v in libs.items()},compiler_flags=flags,toolchain_archive_sha256=sha(b'syntheticarchiveprovenance'))
 build=dict(module_sha256=sha(o),source_sha256=sha(source),object_sha256=sha(obj),compiler={'sha256':sha(compiler)},flags=flags,exit_code=0,linked=False,original_executed=False)
 return dict(original=o,inventory=invraw,compiler=compiler,libraries=libs,source=source,object_bytes=obj,build=build,pins=pins),s,y


def changed_world(kw,original=None,inventory=None):
 if original is not None:kw['original']=original
 inv=json.loads(kw['inventory']) if inventory is None else inventory;inv['module_sha256']=sha(kw['original']);kw['inventory']=canonical(inv);kw['pins']['module_sha256']=sha(kw['original']);kw['pins']['inventory_sha256']=sha(kw['inventory']);kw['build']['module_sha256']=sha(kw['original'])


class ExperimentTests(unittest.TestCase):
 def run_case(self,mutate=None):
  kw,s,y=fixture()
  if mutate:mutate(kw,s,y)
  return check(**kw)
 def no_match(self,r):self.assertNotEqual(r['status'],'exact_eh_graph_match');self.assertFalse(r['ordinary_acceptance_supported'])
 def candidate(self,fn):
  def mutate(kw,s,y):fn(s,y);kw['object_bytes']=coff(s,y);kw['build']['object_sha256']=sha(kw['object_bytes'])
  return mutate
 def test_complete_synthetic_positive(self):
  r=self.run_case();self.assertEqual(r['status'],'exact_eh_graph_match',r.get('blockers'));row=r['functions'][0];self.assertEqual(set(row['counts']),{'equal'});self.assertEqual(len(row['nodes']),6);self.assertTrue(row['all_bytes_accounted']);self.assertFalse(r['ordinary_acceptance_supported'])
 def test_source_identity_without_optional_annotation(self):
  def m(kw,s,y):kw['source']=b'void fn_00001000();';kw['build']['source_sha256']=sha(kw['source'])
  self.assertEqual(self.run_case(m)['status'],'exact_eh_graph_match')
 def test_runtime_roots_all_complete(self):
  r=self.run_case();self.assertEqual(set(r['runtime_identity']['root_complete_comparisons']),set(ROOTS));self.assertTrue(all(n['all_bytes_compared'] for n in r['runtime_identity']['root_complete_comparisons'].values()))
 def test_nonunique_runtime_lookalike(self):
  def m(kw,s,y):o=bytearray(kw['original']);o[0x880:0x885]=b'\xe9'+struct.pack('<i',0x401650-0x401685);inv=json.loads(kw['inventory']);inv['functions'].append({'rva':0x1680,'body_ranges':[{'start_rva':0x1680,'end_rva_inclusive':0x1684}]});changed_world(kw,bytes(o),inv)
  self.no_match(self.run_case(m))
 def test_wrong_runtime_relocation_destination(self):
  def m(kw,s,y):o=bytearray(kw['original']);struct.pack_into('<i',o,0x701,0x401670-0x401505);changed_world(kw,bytes(o))
  self.no_match(self.run_case(m))
 def test_runtime_cookie_operand_mismatch(self):
  def m(kw,s,y):o=bytearray(kw['original']);struct.pack_into('<I',o,0x802,0x402001);changed_world(kw,bytes(o))
  self.no_match(self.run_case(m))
 def test_cookie_initializer_mismatch(self):
  def m(kw,s,y):o=bytearray(kw['original']);o[-1]^=1;changed_world(kw,bytes(o))
  self.no_match(self.run_case(m))
 def test_cookie_initializer_nonunique(self):
  def m(kw,s,y):o=bytearray(kw['original']);o.extend(o[-4:]);struct.pack_into('<I',o,0x1a0+8,8);struct.pack_into('<I',o,0x1a0+16,8);changed_world(kw,bytes(o))
  self.no_match(self.run_case(m))
 def test_duplicate_runtime_archive_definition(self):
  def m(kw,s,y):kw['libraries']['crt.lib']=archive(runtime_objects()+runtime_objects()[:1]);kw['pins']['libraries_sha256']['crt.lib']=sha(kw['libraries']['crt.lib'])
  self.no_match(self.run_case(m))
 def test_wrong_runtime_archive_relocation_kind(self):
  def m(kw,s,y):objects=runtime_objects();b=bytearray(objects[0]);ptr=struct.unpack_from('<I',b,20+24)[0];struct.pack_into('<H',b,ptr+8,6);objects[0]=bytes(b);kw['libraries']['crt.lib']=archive(objects);kw['pins']['libraries_sha256']['crt.lib']=sha(kw['libraries']['crt.lib'])
  self.no_match(self.run_case(m))
 def test_wrong_runtime_archive_relocation_addend(self):
  def m(kw,s,y):objects=runtime_objects();b=bytearray(objects[0]);ptr=struct.unpack_from('<I',b,20+20)[0];struct.pack_into('<I',b,ptr+1,1);objects[0]=bytes(b);kw['libraries']['crt.lib']=archive(objects);kw['pins']['libraries_sha256']['crt.lib']=sha(kw['libraries']['crt.lib'])
  self.no_match(self.run_case(m))
 def test_truncated_archive(self):
  def m(kw,s,y):kw['libraries']['crt.lib']=kw['libraries']['crt.lib'][:-1];kw['pins']['libraries_sha256']['crt.lib']=sha(kw['libraries']['crt.lib'])
  self.no_match(self.run_case(m))
 def test_stale_module_pin(self):
  def m(kw,s,y):kw['pins']['module_sha256']='0'*64
  self.no_match(self.run_case(m))
 def test_stale_inventory_pin(self):
  def m(kw,s,y):kw['pins']['inventory_sha256']='0'*64
  self.no_match(self.run_case(m))
 def test_stale_library_pin(self):
  def m(kw,s,y):kw['pins']['libraries_sha256']['crt.lib']='0'*64
  self.no_match(self.run_case(m))
 def test_stale_compiler_pin(self):
  def m(kw,s,y):kw['pins']['compiler_sha256']='0'*64
  self.no_match(self.run_case(m))
 def test_stale_build_source(self):
  def m(kw,s,y):kw['source']+=b'changed'
  self.no_match(self.run_case(m))
 def test_stale_build_object(self):
  def m(kw,s,y):kw['build']['object_sha256']='0'*64
  self.no_match(self.run_case(m))
 def test_wrong_selected_flags(self):
  def m(kw,s,y):kw['build']['flags']=['/wrong']
  self.no_match(self.run_case(m))
 def test_stale_cache_rejected(self):
  kw,s,y=fixture();prior=check(**kw);kw['source']+=b'\n';kw['build']['source_sha256']=sha(kw['source']);self.no_match(check(**kw,cached=prior))
 def test_cache_verdict_never_trusted(self):
  kw,s,y=fixture();prior=check(**kw);prior['status']='forged';result=check(**kw,cached=prior);self.assertEqual(result['status'],'exact_eh_graph_match');self.assertFalse(result['cached_verdict_reused'])
 def test_wrong_candidate_runtime_target(self):
  def m(s,y):sec=s[1];s[1]=(sec[0],sec[1],[(a,'_fn_00001450' if n=='___CxxFrameHandler3' else n,k) for a,n,k in sec[2]],sec[3])
  self.no_match(self.run_case(self.candidate(m)))
 def test_wrong_helper_addend(self):
  def m(s,y):sec=s[3];b=bytearray(sec[1]);struct.pack_into('<I',b,1,1);s[3]=(sec[0],bytes(b),sec[2],sec[3])
  self.no_match(self.run_case(self.candidate(m)))
 def test_wrong_relocation_kind(self):
  def m(s,y):sec=s[3];s[3]=(sec[0],sec[1],[(a,n,6) for a,n,k in sec[2]],sec[3])
  self.no_match(self.run_case(self.candidate(m)))
 def test_metadata_count(self):
  def m(s,y):sec=s[2];b=bytearray(sec[1]);struct.pack_into('<I',b,12,2);s[2]=(sec[0],bytes(b),sec[2],sec[3])
  self.no_match(self.run_case(self.candidate(m)))
 def test_metadata_flag(self):
  def m(s,y):sec=s[2];b=bytearray(sec[1]);struct.pack_into('<I',b,40,0);s[2]=(sec[0],bytes(b),sec[2],sec[3])
  self.no_match(self.run_case(self.candidate(m)))
 def test_original_metadata_overlap(self):
  def m(kw,s,y):o=bytearray(kw['original']);struct.pack_into('<I',o,0x200+0x208+8,0x401208);changed_world(kw,bytes(o))
  self.no_match(self.run_case(m))
 def test_truncated_metadata(self):
  def m(s,y):sec=s[2];s[2]=(sec[0],sec[1][:-1],sec[2],sec[3])
  self.no_match(self.run_case(self.candidate(m)))
 def test_extra_generated_node(self):
  def m(s,y):n=next(n for n,*_ in y if n.startswith('__unwindfunclet$'));y.append((n[:-1]+'1',0,2,32,3,None))
  self.no_match(self.run_case(self.candidate(m)))
 def test_extra_handler_byte(self):
  def m(s,y):sec=s[1];s[1]=(sec[0],sec[1]+b'\x90',sec[2],sec[3])
  self.no_match(self.run_case(self.candidate(m)))
 def test_frame_displacement(self):
  def m(s,y):sec=s[1];b=bytearray(sec[1]);b[2]^=4;s[1]=(sec[0],bytes(b),sec[2],sec[3])
  self.no_match(self.run_case(self.candidate(m)))
 def test_main_state_entry_corruption(self):
  def m(s,y):sec=s[0];b=bytearray(sec[1]);b[1]=0;s[0]=(sec[0],bytes(b),sec[2],sec[3])
  self.no_match(self.run_case(self.candidate(m)))
 def test_state_transition(self):
  def m(s,y):sec=s[2];b=bytearray(sec[1]);struct.pack_into('<i',b,0,0);s[2]=(sec[0],bytes(b),sec[2],sec[3])
  self.no_match(self.run_case(self.candidate(m)))
 def test_duplicate_COIND_names_keep_indexes(self):
  kw,s,y=fixture();s[3]=(s[3][0],s[3][1],[(1,'_fn_00001400',20)],s[3][3]);s.append(('.other',b'\xc3',[],0x60000020));y.append(('_fn_00001400',0,5,32,2,1));b=bytearray(coff(s,y));o=Coff(b);paired=next(v for v in o.symbols.values() if v.name=='_fn_00001400' and v.section==4);rp=struct.unpack_from('<I',b,20+40+24)[0];struct.pack_into('<I',b,rp+4,paired.index);kw['object_bytes']=bytes(b);kw['build']['object_sha256']=sha(b);self.no_match(check(**kw))
 def test_terminal_decoder_refuses_branch_or_extra_effect(self):
  for raw in (bytes.fromhex('740190e900000000'),bytes.fromhex('e90000000090'),bytes.fromhex('50e900000000')):
   with self.assertRaises(ValueError):terminal_profile('delete_helper',raw,0)
 def test_original_truncation(self):
  def m(kw,s,y):changed_world(kw,kw['original'][:-1])
  self.no_match(self.run_case(m))

if __name__=='__main__':unittest.main()

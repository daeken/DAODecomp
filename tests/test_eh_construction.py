import copy,hashlib,json,sys,unittest
from pathlib import Path
R=next(p for p in Path(__file__).resolve().parents if (p/'rapid_object/coff.py').is_file());sys.path.insert(0,str(R));from rapid_object.eh_construction import propose,compose,Unsupported
from rapid_object.ast_match import parse
O=Path(__file__).resolve().parent
FIXTURE='typedef unsigned int uint; typedef unsigned int undefined4; typedef unsigned char undefined1;\nextern "C" void * _AddressOfReturnAddress(void);\nextern "C" unsigned long __readfsdword(unsigned long);\nextern "C" void __writefsdword(unsigned long,unsigned long);\nextern "C" undefined1 g_006cbe5b; extern "C" uint g_00815234;\nextern "C" unsigned int __cdecl fn_00013660(...);\nextern "C" unsigned int __cdecl fn_000d2070(...);\nextern "C" undefined1 * g_006e891c;\n// FUNCTION: DAO 0x00475040\nundefined4 * fn_00075040(void) {\n  uint uVar1;\n  undefined4 *puVar2;\n  undefined4 *puVar3;\n  int local_c;\n  undefined1 *puStack_8;\n  undefined4 local_4;\n  local_4 = 0xffffffff;\n  puStack_8 = &g_006cbe5b;\n  local_c = ((int)__readfsdword(0));\n  uVar1 = g_00815234 ^ ((unsigned int)_AddressOfReturnAddress() + 0xffffffecu);\n  __writefsdword(0,(unsigned long)((int)&local_c));\n  puVar2 = (undefined4 *)fn_00013660(4);\n  local_4 = 0;\n  puVar3 = (undefined4 *)0x0;\n  if (puVar2 != (undefined4 *)0x0) {\n    ((unsigned int (__thiscall *)(void *))(&fn_000d2070))((void *)puVar2);\n    *puVar2 = (undefined4)(&g_006e891c);\n    puVar3 = puVar2;\n  }\n  __writefsdword(0,(unsigned long)(local_c));\n  return puVar3;\n}\n'
class ConstructionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  import tempfile,shutil
  if not shutil.which('clang++'):raise unittest.SkipTest('clang++ unavailable')
  cls.tmp=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.tmp.cleanup);cls.out=Path(cls.tmp.name);cls.s=FIXTURE;cls.ast=parse(cls.s,cls.out/'base')
 def gen(self,s):return propose(s,parse(s,self.out/'mutants'),0x75040,hashlib.sha256(s.encode()).hexdigest())
 def test_deterministic_regeneration(self):
  a,meta=self.gen(self.s);b,_=self.gen(self.s);self.assertEqual(a,b);self.assertEqual(compose([(a,meta)]),a.encode());self.assertIn('static void operator delete',a);self.assertIn('fn_000b9080(p)',a);self.assertTrue(meta['hypothesis_only']);self.assertFalse(meta['rollout_ready'])
 def test_stale_source(self):
  with self.assertRaises(Unsupported):propose(self.s,self.ast,0x75040,'0'*64)
 def test_unknown_extra_effect(self):
  with self.assertRaises(Unsupported):self.gen(self.s.replace('  return puVar3;','  uVar1 = 7;\n  return puVar3;'))
 def test_unknown_call(self):
  s='void unknown();\n'+self.s.replace('  return puVar3;','  unknown();\n  return puVar3;')
  with self.assertRaises(Unsupported):self.gen(s)
 def test_wrong_allocation_size(self):
  with self.assertRaises(Unsupported):self.gen(self.s.replace('fn_00013660(4)','fn_00013660(8)'))
 def test_nontrivial_suffix(self):
  with self.assertRaises(Unsupported):self.gen(self.s.replace('    puVar3 = puVar2;','    puVar2[1] = 0;\n    puVar3 = puVar2;'))
 def test_conditional_receiver_effect(self):
  with self.assertRaises(Unsupported):self.gen(self.s.replace('    puVar3 = puVar2;','    if(puVar2) puVar3 = puVar2;'))
 def test_early_return(self):
  with self.assertRaises(Unsupported):self.gen(self.s.replace('    puVar3 = puVar2;','    return puVar2;'))
 def test_volatile(self):
  with self.assertRaises(Unsupported):self.gen(self.s.replace('  uint uVar1;','  volatile uint uVar1;'))
 def test_unknown_receiver_use(self):
  with self.assertRaises(Unsupported):self.gen(self.s.replace('    puVar3 = puVar2;','    puVar3 = puVar3;'))
 def test_unknown_null_predicate(self):
  with self.assertRaises(Unsupported):self.gen(self.s.replace('puVar2 != (undefined4 *)0x0','puVar2 == (undefined4 *)0x0'))
 def test_macro(self):
  s='#define WORD_ALLOC fn_00013660(4)\n'+self.s.replace('fn_00013660(4);','WORD_ALLOC;')
  with self.assertRaises(Unsupported):self.gen(s)
 def test_invalid_AST(self):
  a=copy.deepcopy(self.ast);a['inner'].append({'kind':'RecoveryExpr'})
  with self.assertRaises(Unsupported):propose(self.s,a,0x75040,hashlib.sha256(self.s.encode()).hexdigest())
 def test_ambiguous_declaration(self):
  s=self.s.replace('extern "C" unsigned int __cdecl fn_000d2070(...);','extern "C" unsigned int __cdecl fn_000d2070(...);\nextern "C" unsigned int __cdecl fn_000d2070(...);')
  with self.assertRaises(Unsupported):self.gen(s)
 def test_identity_collision(self):
  with self.assertRaises(Unsupported):self.gen(self.s+'\nstruct EHConstruction_00075040 {};\n')
 def test_duplicate_composition(self):
  p=self.gen(self.s)
  with self.assertRaises(Unsupported):compose([p,p])
 def test_stale_candidate_composition(self):
  c,m=self.gen(self.s)
  with self.assertRaises(Unsupported):compose([(c+' ',m)])
if __name__=='__main__':unittest.main()

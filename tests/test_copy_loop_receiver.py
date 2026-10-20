"""Synthetic receiver/cleanup and complete-source refusal controls."""
import copy,hashlib,json,shutil,tempfile,unittest,os
if os.name == 'nt':raise unittest.SkipTest('Source generation uses the existing POSIX Clang AST workflow')
from pathlib import Path
from rapid_object.copy_loop_receiver import propose,callee_capture
from rapid_object.conditional_construction import Unsupported
from rapid_object.ast_match import parse
FIXTURE='// Provisional deterministic Ghidra seed; signatures/types remain hypotheses.\ntypedef unsigned int pointer32;\ntypedef unsigned int code(...);\ntypedef unsigned char   undefined;\ntypedef unsigned char    byte;\ntypedef unsigned int    dword;\ntypedef unsigned __int64    GUID;\ntypedef pointer32 ImageBaseOffset32;\n\ntypedef __int64    longlong;\ntypedef unsigned char    uchar;\ntypedef unsigned int    uint;\ntypedef unsigned long    ulong;\ntypedef unsigned __int64    ulonglong;\ntypedef unsigned char    undefined1;\ntypedef unsigned short    undefined2;\ntypedef unsigned int    undefined4;\ntypedef unsigned __int64    undefined6;\ntypedef unsigned __int64    undefined8;\ntypedef unsigned short    ushort;\ntypedef unsigned short    word;\n\nextern "C" unsigned int __cdecl fn_00002200(...); /* ABI/return type unknown, provisional declaration */\nextern "C" unsigned int __cdecl fn_00003300(...); /* ABI/return type unknown, provisional declaration */\nextern "C" unsigned int __cdecl fn_00004400(...); /* ABI/return type unknown, provisional declaration */\n\n// FUNCTION: DAO 0x00401100\nint * fn_00001100(int *param_1,undefined4 *param_2,undefined4 *param_3,int param_4)\n{\n  undefined4 *puVar1;\n  \n  *param_1 = param_4;\n  for (; param_2 != param_3; param_2 = param_2 + 0x22) {\n    puVar1 = (undefined4 *)*param_1;\n    if (puVar1 != (undefined4 *)0x0) {\n      *puVar1 = 0;\n      puVar1[1] = 0;\n      puVar1[2] = 0;\n      fn_00002200(param_2 + 3);\n      fn_00003300(*param_2,param_2[1]);\n      fn_00004400(param_2 + 4);\n    }\n    *param_1 = *param_1 + 0x88;\n  }\n  return param_1;\n}\n\n'
sha=lambda b:hashlib.sha256(b).hexdigest()
class CopyLoopTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  if not shutil.which('clang++'):raise unittest.SkipTest('clang++ unavailable')
  cls.tmp=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.tmp.cleanup);cls.out=Path(cls.tmp.name);cls.ast=parse(FIXTURE,cls.out/'base')
 def no(self,s,reason):
  original=b'invalid synthetic PE: refusal must precede binary intake'
  with self.assertRaisesRegex(Unsupported,reason):propose(s,parse(s,self.out/'mutant'),0x1100,dict(source_sha256=sha(s.encode()),module_sha256=sha(original)),original,b'{}')
 def test_stale_source(self):
  with self.assertRaisesRegex(Unsupported,'binding'):propose(FIXTURE,self.ast,0x1100,{},b'',b'{}')
 def test_extra_effect(self):self.no(FIXTURE.replace('  return param_1;','  *param_1=7; return param_1;'),'body_shape')
 def test_wrong_guard(self):self.no(FIXTURE.replace('puVar1 != (undefined4 *)0x0','puVar1 == (undefined4 *)0x0'),'body_shape')
 def test_changed_receiver_source_offset(self):self.no(FIXTURE.replace('fn_00002200(param_2 + 3)','fn_00002200(param_2 + 2)'),'body_shape')
 def test_changed_argument(self):self.no(FIXTURE.replace('fn_00003300(*param_2,param_2[1])','fn_00003300(*param_2,param_2[2])'),'body_shape')
 def test_missing_call(self):self.no(FIXTURE.replace('      fn_00004400(param_2 + 4);',''),'body_shape')
 def test_wrong_stride(self):self.no(FIXTURE.replace('param_2 + 0x22','param_2 + 0x21'),'body_shape')
 def test_wrong_advance(self):self.no(FIXTURE.replace('*param_1 + 0x88','*param_1 + 0x84'),'body_shape')
 def test_unknown_call(self):self.no('void unknown();\n'+FIXTURE.replace('  return param_1;','  unknown(); return param_1;'),'body_shape')
 def test_volatile(self):self.no(FIXTURE.replace('  undefined4 *puVar1;','  undefined4 *volatile puVar1;'),'body_shape')
 def test_macro(self):self.no('#define CALL_COPY fn_00002200(param_2 + 3)\n'+FIXTURE.replace('fn_00002200(param_2 + 3);','CALL_COPY;'),'macro')
 def test_invalid_ast(self):
  a=copy.deepcopy(self.ast);a['inner'].append({'kind':'RecoveryExpr'})
  with self.assertRaisesRegex(Unsupported,'incomplete_AST'):propose(FIXTURE,a,0x1100,dict(source_sha256=sha(FIXTURE.encode()),module_sha256=sha(b'')),b'',b'{}')
class CalleeControls(unittest.TestCase):
 def cap(self,raw,cleanup=4):
  class Reader:
   class pe:image_base=0x400000
   def read(self,va,n,code=False):
    if va!=0x401000 or n!=len(raw):raise AssertionError('unexpected range')
    return raw
  return callee_capture(Reader(),dict(rva=0x1000,body_ranges=[dict(start_rva=0x1000,end_rva_inclusive=0x1000+len(raw)-1)]),cleanup)
 def test_complete_direct_receiver(self):self.assertEqual(self.cap(bytes.fromhex('8bc1c20400'))['return_cleanup_bytes'],4)
 def test_complete_conditional_receiver(self):self.assertEqual(self.cap(bytes.fromhex('8bc185c0740190c20400'))['CFG_instructions'],5)
 def test_wrong_cleanup(self):
  with self.assertRaisesRegex(Unsupported,'cleanup'):self.cap(bytes.fromhex('8bc1c20800'))
 def test_receiver_clobber_before_read(self):
  with self.assertRaisesRegex(Unsupported,'receiver_livein'):self.cap(bytes.fromhex('33c98bc1c20400'))
 def test_partial_receiver_register_clobbers(self):
  for prefix in ['b100','b500','66b90000']:
   with self.subTest(prefix=prefix),self.assertRaisesRegex(Unsupported,'receiver_livein'):self.cap(bytes.fromhex(prefix+'8bc1c20400'))
 def test_outside_branch(self):
  with self.assertRaisesRegex(Unsupported,'CFG_boundary'):self.cap(bytes.fromhex('8bc1eb7fc20400'))
 def test_unknown_indirect_call(self):
  with self.assertRaisesRegex(Unsupported,'indirect_call'):self.cap(bytes.fromhex('8bc1ffd0c20400'))
 def test_incomplete_decode(self):
  with self.assertRaisesRegex(Unsupported,'decode'):self.cap(bytes.fromhex('8bc10f'))
 def test_unreachable_tail(self):
  with self.assertRaisesRegex(Unsupported,'cleanup'):self.cap(bytes.fromhex('8bc1c2040090'))
if __name__=='__main__':unittest.main()

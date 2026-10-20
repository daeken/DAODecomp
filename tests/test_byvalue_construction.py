"""Source refusal controls; complete real regeneration is private evidence."""
import copy,hashlib,shutil,tempfile,unittest
import os
if os.name == "nt":
 raise unittest.SkipTest("Constructor source generation uses the existing POSIX Clang AST workflow")
from pathlib import Path
from rapid_object.byvalue_construction import propose
from rapid_object.conditional_construction import Unsupported
from rapid_object.ast_match import parse
FIXTURE='// Provisional deterministic Ghidra seed; signatures/types remain hypotheses.\ntypedef unsigned int pointer32;\ntypedef unsigned int code(...);\ntypedef unsigned char   undefined;\ntypedef unsigned char    byte;\ntypedef unsigned int    dword;\ntypedef unsigned __int64    GUID;\ntypedef pointer32 ImageBaseOffset32;\n\ntypedef __int64    longlong;\ntypedef unsigned char    uchar;\ntypedef unsigned int    uint;\ntypedef unsigned long    ulong;\ntypedef unsigned __int64    ulonglong;\ntypedef unsigned char    undefined1;\ntypedef unsigned short    undefined2;\ntypedef unsigned int    undefined4;\ntypedef unsigned __int64    undefined6;\ntypedef unsigned __int64    undefined8;\ntypedef unsigned short    ushort;\ntypedef unsigned short    word;\n\nextern "C" unsigned long __readfsdword(unsigned long);\nextern "C" void __writefsdword(unsigned long,unsigned long);\n#pragma intrinsic(__readfsdword)\n#pragma intrinsic(__writefsdword)\n\nextern "C" undefined g_00004400;\nextern "C" unsigned int __cdecl fn_00002200(...); /* ABI/return type unknown, provisional declaration */\nextern "C" unsigned int __cdecl fn_00003300(...); /* ABI/return type unknown, provisional declaration */\nstruct Seed_00001100 { int __thiscall fn_00001100(int param_2); };\n\n// FUNCTION: DAO 0x00401100\nint __thiscall Seed_00001100::fn_00001100(int param_2)\n{\n\n  int local_c;\n  undefined1 *puStack_8;\n  undefined4 local_4;\n  \n  puStack_8 = &g_00004400;\n  local_c = ((int)__readfsdword(0));\n  __writefsdword(0,(unsigned long)((int)&local_c));\n  *(undefined4 *)(((int)this) + 4) = 0;\n  *(undefined4 *)(((int)this) + 8) = 0;\n  *(undefined4 *)(((int)this) + 0xc) = 0;\n  local_4 = 0;\n  if (param_2 != 0) {\n    fn_00002200(0);\n    fn_00003300(param_2);\n  }\n  __writefsdword(0,(unsigned long)(local_c));\n  return ((int)this);\n}\n\n'
sha=lambda b:hashlib.sha256(b).hexdigest()
class ByvalueConstructionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  if not shutil.which('clang++'):raise unittest.SkipTest('clang++ unavailable')
  cls.tmp=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.tmp.cleanup);cls.out=Path(cls.tmp.name);cls.ast=parse(FIXTURE,cls.out/'base')
 def gen(self,s,ast=None):
  o=b'synthetic invalid PE; refuse before binary intake'
  return propose(s,ast if ast is not None else parse(s,self.out/'mutant'),0x1100,dict(source_sha256=sha(s.encode()),module_sha256=sha(o)),o)
 def no(self,s,reason):
  with self.assertRaisesRegex(Unsupported,reason):self.gen(s)
 def test_stale_source(self):
  with self.assertRaisesRegex(Unsupported,'binding'):propose(FIXTURE,self.ast,0x1100,{},b'')
 def test_extra_effect(self):self.no(FIXTURE.replace('  return ((int)this);','  local_4=7; return ((int)this);'),'body_shape')
 def test_missing_field(self):self.no(FIXTURE.replace(' + 0xc) = 0',' + 0xc) = 1'),'body_shape')
 def test_unknown_call(self):self.no('void unknown();\n'+FIXTURE.replace('  return ((int)this);','  unknown(); return ((int)this);'),'body_shape')
 def test_changed_constructor_argument(self):self.no(FIXTURE.replace('fn_00002200(0)','fn_00002200(1)'),'body_shape')
 def test_changed_guard(self):self.no(FIXTURE.replace('param_2 != 0','param_2 == 0'),'body_shape')
 def test_changed_return(self):self.no(FIXTURE.replace('return ((int)this)','return param_2'),'body_shape')
 def test_invalid_ast(self):
  a=copy.deepcopy(self.ast);a['inner'].append({'kind':'RecoveryExpr'})
  with self.assertRaisesRegex(Unsupported,'incomplete_AST'):self.gen(FIXTURE,a)
 def test_macro(self):self.no('#define CALL_CTOR fn_00002200(0)\n'+FIXTURE.replace('fn_00002200(0);','CALL_CTOR;'),'macro')
if __name__=='__main__':unittest.main()

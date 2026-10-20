"""Source refusal controls; real complete-graph regeneration is retained privately."""
import copy,hashlib,shutil,tempfile,unittest
import os
if os.name == "nt":
 raise unittest.SkipTest("Constructor source generation uses the existing POSIX Clang AST workflow")
from pathlib import Path
from rapid_object.conditional_construction import propose,Unsupported
from rapid_object.ast_match import parse
FIXTURE='// Provisional deterministic Ghidra seed; signatures/types remain hypotheses.\ntypedef unsigned int pointer32;\ntypedef unsigned int code(...);\ntypedef unsigned char   undefined;\ntypedef unsigned char    byte;\ntypedef unsigned int    dword;\ntypedef unsigned __int64    GUID;\ntypedef pointer32 ImageBaseOffset32;\n\ntypedef __int64    longlong;\ntypedef unsigned char    uchar;\ntypedef unsigned int    uint;\ntypedef unsigned long    ulong;\ntypedef unsigned __int64    ulonglong;\ntypedef unsigned char    undefined1;\ntypedef unsigned short    undefined2;\ntypedef unsigned int    undefined4;\ntypedef unsigned __int64    undefined6;\ntypedef unsigned __int64    undefined8;\ntypedef unsigned short    ushort;\ntypedef unsigned short    word;\n\nextern "C" void * _AddressOfReturnAddress(void);\n#pragma intrinsic(_AddressOfReturnAddress)\n\nextern "C" unsigned long __readfsdword(unsigned long);\nextern "C" void __writefsdword(unsigned long,unsigned long);\n#pragma intrinsic(__readfsdword)\n#pragma intrinsic(__writefsdword)\n\nextern "C" undefined g_00004400;\nextern "C" uint g_00005500;\nextern "C" unsigned int __cdecl fn_00003300(...); /* ABI/return type unknown, provisional declaration */\nextern "C" unsigned int __cdecl fn_00002200(...); /* ABI/return type unknown, provisional declaration */\n\n// FUNCTION: DAO 0x00401100\nundefined4 fn_00001100(int *param_1)\n{\n  uint uVar1;\n  int iVar2;\n\n  int local_c;\n  undefined1 *puStack_8;\n  undefined4 local_4;\n  \n  local_4 = 0xffffffff;\n  puStack_8 = &g_00004400;\n  local_c = ((int)__readfsdword(0));\n  uVar1 = g_00005500 ^ ((unsigned int)_AddressOfReturnAddress() + 0xfffffff0u);\n  __writefsdword(0,(unsigned long)((int)&local_c));\n  if ((param_1 != (int *)0x0) && (*param_1 == 0)) {\n    iVar2 = fn_00003300(0x20,uVar1);\n    local_4 = 0;\n    if (iVar2 == 0) {\n      iVar2 = 0;\n    }\n    else {\n      iVar2 = fn_00002200(0);\n    }\n    *param_1 = iVar2;\n  }\n  __writefsdword(0,(unsigned long)(local_c));\n  return 2;\n}\n\n'
sha=lambda b:hashlib.sha256(b).hexdigest()
class ConditionalConstructionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  if not shutil.which('clang++'):raise unittest.SkipTest('clang++ unavailable')
  cls.tmp=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.tmp.cleanup);cls.out=Path(cls.tmp.name);cls.ast=parse(FIXTURE,cls.out/'base')
 def gen(self,s,ast=None):
  original=b'synthetic invalid PE; these controls must refuse before binary intake'
  return propose(s,ast if ast is not None else parse(s,self.out/'mutant'),0x1100,dict(source_sha256=sha(s.encode()),module_sha256=sha(original)),original)
 def refused(self,s,reason,ast=None):
  with self.assertRaisesRegex(Unsupported,reason):self.gen(s,ast)
 def test_stale_source_and_module(self):
  with self.assertRaisesRegex(Unsupported,'binding'):propose(FIXTURE,self.ast,0x1100,{},b'')
 def test_extra_effect(self):self.refused(FIXTURE.replace('  return 2;','  *param_1 = 42; return 2;'),'body_shape')
 def test_unknown_call(self):self.refused('void unknown();\n'+FIXTURE.replace('  return 2;','  unknown(); return 2;'),'body_shape')
 def test_wrong_guard(self):self.refused(FIXTURE.replace('*param_1 == 0','*param_1 != 0'),'body_shape')
 def test_constructor_argument(self):self.refused(FIXTURE.replace('fn_00002200(0)','fn_00002200(1)'),'body_shape')
 def test_allocation_cookie_escape(self):self.refused(FIXTURE.replace('fn_00003300(0x20,uVar1)','fn_00003300(0x20,uVar1+1)'),'body_shape')
 def test_volatile(self):self.refused(FIXTURE.replace('  uint uVar1;','  volatile uint uVar1;'),'body_shape')
 def test_unknown_suffix(self):self.refused(FIXTURE.replace('  return 2;','  return iVar2;'),'body_shape')
 def test_parameter_type(self):
  a=copy.deepcopy(self.ast)
  from rapid_object.ast_match import fix
  for n in fix.walk(a):
   if n.get('kind')=='ParmVarDecl' and n.get('name')=='param_1':n['type']['qualType']='unsigned int *'
  self.refused(FIXTURE,'signature',a)
 def test_unbounded_size(self):self.refused(FIXTURE.replace('0x20,uVar1','0x10000,uVar1'),'bounded_size')
 def test_invalid_ast(self):
  a=copy.deepcopy(self.ast);a['inner'].append({'kind':'RecoveryExpr'});self.refused(FIXTURE,'incomplete_AST',a)
 def test_macro(self):self.refused('#define GET_ALLOC fn_00003300(0x20,uVar1)\n'+FIXTURE.replace('fn_00003300(0x20,uVar1);','GET_ALLOC;'),'macro')
if __name__=='__main__':unittest.main()

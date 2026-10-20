"""Synthetic complete-source refusals for bounded receiver families, not game proof."""
import os,unittest,copy,hashlib,tempfile,shutil
if os.name=='nt':raise unittest.SkipTest('Source generation uses the existing POSIX Clang AST workflow')
from pathlib import Path
from rapid_object import copy_chain_receivers,callback_array_spelling,checked_list_receivers
from rapid_object.ast_match import parse,fix
from rapid_object.conditional_construction import Unsupported
sha=lambda b:hashlib.sha256(b).hexdigest()
CHAIN='// Provisional deterministic Ghidra seed; signatures/types remain hypotheses.\ntypedef unsigned int pointer32;\ntypedef unsigned int code(...);\ntypedef unsigned char   undefined;\ntypedef unsigned char    byte;\ntypedef unsigned int    dword;\ntypedef unsigned __int64    GUID;\ntypedef pointer32 ImageBaseOffset32;\n\ntypedef __int64    longlong;\ntypedef unsigned char    uchar;\ntypedef unsigned int    uint;\ntypedef unsigned long    ulong;\ntypedef unsigned __int64    ulonglong;\ntypedef unsigned char    undefined1;\ntypedef unsigned short    undefined2;\ntypedef unsigned int    undefined4;\ntypedef unsigned __int64    undefined6;\ntypedef unsigned __int64    undefined8;\ntypedef unsigned short    ushort;\ntypedef unsigned short    word;\n\nextern "C" unsigned int __cdecl fn_00002200(...); /* ABI/return type unknown, provisional declaration */\nextern "C" unsigned int __cdecl fn_00003300(...); /* ABI/return type unknown, provisional declaration */\nextern "C" unsigned int __cdecl fn_00004400(...); /* ABI/return type unknown, provisional declaration */\nstruct Seed_00001100 { void __thiscall fn_00001100(int param_2); };\n\n// FUNCTION: DAO 0x00401100\nvoid __thiscall Seed_00001100::fn_00001100(int param_2)\n{\n  int *piVar1;\n  undefined4 uVar2;\n  \n  fn_00002200(param_2);\n  *(undefined1 *)(param_2 + 0x2c) = *(undefined1 *)(((int)this) + 0x2c);\n  *(undefined4 *)(param_2 + 0x30) = *(undefined4 *)(((int)this) + 0x30);\n  fn_00003300(*(undefined4 **)(((int)this) + 0x34) + 2,**(undefined4 **)(((int)this) + 0x34));\n  *(undefined4 *)(param_2 + 0x38) = *(undefined4 *)(((int)this) + 0x38);\n  *(undefined4 *)(param_2 + 0x3c) = *(undefined4 *)(((int)this) + 0x3c);\n  *(undefined4 *)(param_2 + 0x40) = *(undefined4 *)(((int)this) + 0x40);\n  *(undefined1 *)(param_2 + 0x44) = *(undefined1 *)(((int)this) + 0x44);\n  for (piVar1 = *(int **)(((int)this) + 0x18); piVar1 != (int *)0x0; piVar1 = (int *)piVar1[10]) {\n    uVar2 = (**(code **)(*piVar1 + 0x3c))();\n    fn_00004400(uVar2);\n  }\n  return;\n}\n\n'
ARRAY='// Provisional deterministic Ghidra seed; signatures/types remain hypotheses.\ntypedef unsigned int pointer32;\ntypedef unsigned int code(...);\ntypedef unsigned char   undefined;\ntypedef unsigned char    byte;\ntypedef unsigned int    dword;\ntypedef unsigned __int64    GUID;\ntypedef pointer32 ImageBaseOffset32;\n\ntypedef __int64    longlong;\ntypedef unsigned char    uchar;\ntypedef unsigned int    uint;\ntypedef unsigned long    ulong;\ntypedef unsigned __int64    ulonglong;\ntypedef unsigned char    undefined1;\ntypedef unsigned short    undefined2;\ntypedef unsigned int    undefined4;\ntypedef unsigned __int64    undefined6;\ntypedef unsigned __int64    undefined8;\ntypedef unsigned short    ushort;\ntypedef unsigned short    word;\n\nextern "C" undefined4 g_00005500;\nstruct Seed_00001100 { void __thiscall fn_00001100(undefined4 param_2,undefined4 param_3); };\n\n// FUNCTION: DAO 0x00401100\nvoid __thiscall Seed_00001100::fn_00001100(undefined4 param_2,undefined4 param_3)\n{\n  int iVar1;\n  undefined4 *puVar2;\n  uint uVar3;\n  uint uVar4;\n  \n  if (*(int *)(((int)this) + 0x130) == 0) {\n    uVar3 = 0;\n  }\n  else {\n    uVar3 = *(int *)(((int)this) + 0x134) - *(int *)(((int)this) + 0x130) >> 2;\n  }\n  uVar4 = 0;\n  if (uVar3 != 0) {\n    do {\n      iVar1 = *(int *)(((int)this) + 0x130);\n      if ((iVar1 == 0) || ((uint)(*(int *)(((int)this) + 0x134) - iVar1 >> 2) <= uVar4)) {\n        puVar2 = &g_00005500;\n      }\n      else {\n        puVar2 = (undefined4 *)(iVar1 + uVar4 * 4);\n      }\n      (*(code *)*puVar2)(param_2,param_3);\n      uVar4 = uVar4 + 1;\n    } while (uVar4 < uVar3);\n  }\n  return;\n}\n\n'
LIST='// Provisional deterministic Ghidra seed; signatures/types remain hypotheses.\ntypedef unsigned int pointer32;\ntypedef unsigned int code(...);\ntypedef unsigned char   undefined;\ntypedef unsigned char    byte;\ntypedef unsigned int    dword;\ntypedef unsigned __int64    GUID;\ntypedef pointer32 ImageBaseOffset32;\n\ntypedef __int64    longlong;\ntypedef unsigned char    uchar;\ntypedef unsigned int    uint;\ntypedef unsigned long    ulong;\ntypedef unsigned __int64    ulonglong;\ntypedef unsigned char    undefined1;\ntypedef unsigned short    undefined2;\ntypedef unsigned int    undefined4;\ntypedef unsigned __int64    undefined6;\ntypedef unsigned __int64    undefined8;\ntypedef unsigned short    ushort;\ntypedef unsigned short    word;\n\nextern "C" unsigned int __cdecl fn_00002200(...); /* ABI/return type unknown, provisional declaration */\nextern "C" unsigned int __cdecl fn_00003300(...); /* ABI/return type unknown, provisional declaration */\nextern "C" unsigned int __cdecl fn_00004400(...); /* ABI/return type unknown, provisional declaration */\nstruct Seed_00001100 { void __thiscall fn_00001100(undefined4 param_2); };\n\n// FUNCTION: DAO 0x00401100\nvoid __thiscall Seed_00001100::fn_00001100(undefined4 param_2)\n{\n  int iVar1;\n  int iVar2;\n  int iVar3;\n  int *piVar4;\n  undefined1 local_8 [8];\n  \n  piVar4 = (int *)fn_00002200(local_8,param_2);\n  iVar1 = *piVar4;\n  iVar2 = piVar4[1];\n  iVar3 = *(int *)(((int)this) + 4);\n  if ((iVar1 == 0) || (iVar1 != ((int)this))) {\n    fn_00003300();\n  }\n  if (iVar2 != iVar3) {\n    if (iVar1 == 0) {\n      fn_00003300();\n    }\n    if (iVar2 == *(int *)(iVar1 + 4)) {\n      fn_00003300();\n    }\n    if (*(undefined4 **)(iVar2 + 0x28) != (undefined4 *)0x0) {\n      (**(code **)**(undefined4 **)(iVar2 + 0x28))(1);\n    }\n    fn_00004400(local_8,iVar1,iVar2);\n  }\n  return;\n}\n\n'

class FamilyMixin:
 @classmethod
 def setUpClass(cls):
  if not shutil.which('clang++'):raise unittest.SkipTest('clang++ unavailable')
  cls.tmp=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.tmp.cleanup);cls.out=Path(cls.tmp.name);cls.ast=parse(cls.fixture,cls.out/'base')
 def invoke(self,s,ast,bound,rva=0x1100):
  args=(s,ast,rva,bound,b'')
  return self.module.propose(*args,b'{}') if self.module is not callback_array_spelling else self.module.propose(*args)
 def no(self,s,reason):
  with self.assertRaisesRegex(Unsupported,reason):self.invoke(s,parse(s,self.out/'mutant'),dict(source_sha256=sha(s.encode()),module_sha256=sha(b'')))
 def type_no(self,name,value):
  ast=copy.deepcopy(self.ast)
  for n in fix.walk(ast):
   if n.get('kind')=='TypedefDecl' and n.get('name')==name and not n.get('isImplicit'):n['type']['qualType']=value
  with self.assertRaisesRegex(Unsupported,'consumed_type_'+name):self.invoke(self.fixture,ast,dict(source_sha256=sha(self.fixture.encode()),module_sha256=sha(b'')))
 def test_source_binding(self):
  with self.assertRaisesRegex(Unsupported,'binding'):self.invoke(self.fixture,self.ast,{})
 def test_original_binding(self):
  with self.assertRaisesRegex(Unsupported,'binding'):self.invoke(self.fixture,self.ast,dict(source_sha256=sha(self.fixture.encode()),module_sha256='0'*64))
 def test_uint_type(self):self.type_no('uint','int')
 def test_word_type(self):self.type_no('undefined4','unsigned long long')
 def test_code_type(self):self.type_no('code','unsigned int (int)')
 def test_wrong_method(self):
  with self.assertRaisesRegex(Unsupported,'unique_own_method'):self.invoke(self.fixture,self.ast,dict(source_sha256=sha(self.fixture.encode()),module_sha256=sha(b'')),0x1104)
 def test_extra_effect(self):self.no(self.fixture.replace('  return;','  param_2=7; return;'),'body_shape')
 def test_field_change(self):self.no(self.fixture.replace(self.field,self.other_field),'body_shape')
 def test_call_argument(self):self.no(self.fixture.replace(self.call,self.other_call),'body_shape')
 def test_branch_change(self):self.no(self.fixture.replace(self.branch,self.other_branch),'body_shape')
 def test_parameter_change(self):self.no(self.fixture.replace('undefined4 param_2','int param_2') if self.module is not copy_chain_receivers else self.fixture.replace('int param_2','unsigned int param_2'),'method_type|parameters')
 def test_macro_span(self):self.no('#define FIELD '+self.field+'\n'+self.fixture.replace(self.field,'FIELD'),'macro')
class ChainTests(FamilyMixin,unittest.TestCase):
 fixture=CHAIN;module=copy_chain_receivers;field='0x2c';other_field='0x2d';call='fn_00004400(uVar2)';other_call='fn_00004400(1)';branch='piVar1 != (int *)0x0';other_branch='piVar1 == (int *)0x0'
class ArrayTests(FamilyMixin,unittest.TestCase):
 fixture=ARRAY;module=callback_array_spelling;field='0x130';other_field='0x138';call='(param_2,param_3)';other_call='(param_3,param_2)';branch='uVar4 < uVar3';other_branch='uVar4 <= uVar3'
class ListTests(FamilyMixin,unittest.TestCase):
 fixture=LIST;module=checked_list_receivers;field='0x28';other_field='0x2c';call='fn_00004400(local_8,iVar1,iVar2)';other_call='fn_00004400(local_8,iVar2,iVar1)';branch='iVar2 != iVar3';other_branch='iVar2 == iVar3'

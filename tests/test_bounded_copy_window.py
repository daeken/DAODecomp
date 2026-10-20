"""Synthetic complete-body refusals; not proof of the game."""
import os,unittest,hashlib,json,shutil,tempfile
if os.name=='nt':raise unittest.SkipTest('Source generation uses the existing POSIX Clang AST workflow')
from pathlib import Path
from rapid_object.bounded_copy_window import propose
from rapid_object.ast_match import parse
from rapid_object.conditional_construction import Unsupported
FIXTURE='// Provisional deterministic Ghidra seed; signatures/types remain hypotheses.\ntypedef unsigned int pointer32;\ntypedef unsigned int code(...);\ntypedef unsigned char   undefined;\ntypedef unsigned char    byte;\ntypedef unsigned int    dword;\ntypedef unsigned __int64    GUID;\ntypedef pointer32 ImageBaseOffset32;\n\ntypedef __int64    longlong;\ntypedef unsigned char    uchar;\ntypedef unsigned int    uint;\ntypedef unsigned long    ulong;\ntypedef unsigned __int64    ulonglong;\ntypedef unsigned char    undefined1;\ntypedef unsigned short    undefined2;\ntypedef unsigned int    undefined4;\ntypedef unsigned __int64    undefined6;\ntypedef unsigned __int64    undefined8;\ntypedef unsigned short    ushort;\ntypedef unsigned short    word;\ntypedef uint size_t;\n\n\nextern "C" void * __cdecl fn_00002200(void * _Dst, void * _Src, size_t _Size);\nstruct Seed_00001100 { size_t __thiscall fn_00001100(int param_2,int param_3); };\n\n// FUNCTION: DAO 0x00401100\nsize_t __thiscall Seed_00001100::fn_00001100(int param_2,int param_3)\n{\n  int iVar1;\n  size_t _Size;\n  \n  *(int *)(param_2 + 0x28cc) = *(int *)(param_2 + 0x28cc) + param_3;\n  iVar1 = *(int *)(param_2 + 0x28cc);\n  _Size = 0x1000;\n  if (((iVar1 + 0x1000 <= *(int *)(param_2 + 0x28d0)) ||\n      (_Size = *(int *)(param_2 + 0x28d0) - iVar1, -1 < (int)_Size)) &&\n     (*(int *)(((int)this) + 0x28fc) != 0)) {\n    if (_Size == 0) {\n      return 0;\n    }\n    fn_00002200((void *)(*(int *)(param_2 + 0x28c8) * 0x1000 + 0x8c8 + param_2),\n            (void *)(*(int *)(((int)this) + 0x28fc) + iVar1),_Size);\n  }\n  return _Size;\n}\n\n'

sha=lambda b:hashlib.sha256(b).hexdigest()
class WindowTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  if not shutil.which('clang++'):raise unittest.SkipTest('clang++ unavailable')
  cls.tmp=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.tmp.cleanup);cls.out=Path(cls.tmp.name);cls.ast=parse(FIXTURE,cls.out/'base')
 def no(self,s,reason):
  original=b'invalid synthetic PE: refusal before binary intake'
  with self.assertRaisesRegex(Unsupported,reason):propose(s,parse(s,self.out/'mutant'),0x1100,dict(source_sha256=sha(s.encode()),module_sha256=sha(original)),original)
 def type_no(self,name,kind):
  import copy
  from rapid_object.ast_match import fix
  ast=copy.deepcopy(self.ast)
  for n in fix.walk(ast):
   if n.get('kind')=='TypedefDecl' and n.get('name')==name and not n.get('isImplicit'):n['type']['qualType']=kind
  with self.assertRaisesRegex(Unsupported,'consumed_type_'+name):propose(FIXTURE,ast,0x1100,dict(source_sha256=sha(FIXTURE.encode()),module_sha256=sha(b'')),b'')
 def test_stale_binding(self):
  with self.assertRaisesRegex(Unsupported,'binding'):propose(FIXTURE,self.ast,0x1100,{},b'')
 def test_extra_effect(self):self.no(FIXTURE.replace('  return _Size;','  param_2=7; return _Size;'),'body_shape')
 def test_changed_size(self):self.no(FIXTURE.replace('_Size = 0x1000','_Size = 0x2000'),'body_shape')
 def test_changed_field(self):self.no(FIXTURE.replace('0x28cc','0x28c0'),'body_shape')
 def test_changed_branch(self):self.no(FIXTURE.replace('-1 < (int)_Size','-2 < (int)_Size'),'body_shape')
 def test_changed_argument(self):self.no(FIXTURE.replace('param_2),','param_3),'),'body_shape')
 def test_changed_return(self):self.no(FIXTURE.replace('return _Size','return 0'),'body_shape')
 def test_signed_uint(self):self.type_no('uint','int')
 def test_wide_size(self):self.type_no('size_t','unsigned long long')
 def test_changed_parameters(self):self.no(FIXTURE.replace('int param_3','unsigned int param_3'),'parameters|method_type')
 def test_wrong_method(self):
  with self.assertRaisesRegex(Unsupported,'unique_own_method'):propose(FIXTURE,self.ast,0x1104,dict(source_sha256=sha(FIXTURE.encode()),module_sha256=sha(b'')),b'')

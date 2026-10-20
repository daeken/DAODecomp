"""Synthetic complete-body refusal controls; real regeneration remains private."""
import copy,hashlib,shutil,tempfile,unittest,os
if os.name == 'nt':raise unittest.SkipTest('Source generation uses the existing POSIX Clang AST workflow')
from pathlib import Path
from rapid_object.numeric_loop_spelling import propose
from rapid_object.conditional_construction import Unsupported
from rapid_object.ast_match import parse
FIXTURE='// Provisional deterministic Ghidra seed; signatures/types remain hypotheses.\ntypedef unsigned int pointer32;\ntypedef unsigned int code(...);\ntypedef unsigned char   undefined;\ntypedef unsigned char    byte;\ntypedef unsigned int    dword;\ntypedef unsigned __int64    GUID;\ntypedef pointer32 ImageBaseOffset32;\n\ntypedef __int64    longlong;\ntypedef unsigned char    uchar;\ntypedef unsigned int    uint;\ntypedef unsigned long    ulong;\ntypedef unsigned __int64    ulonglong;\ntypedef unsigned char    undefined1;\ntypedef unsigned short    undefined2;\ntypedef unsigned int    undefined4;\ntypedef unsigned __int64    undefined6;\ntypedef unsigned __int64    undefined8;\ntypedef unsigned short    ushort;\ntypedef unsigned short    word;\n\nextern "C" undefined g_006e5b50;\n\n// FUNCTION: DAO 0x00401100\nint fn_00001100(char *param_1,int param_2)\n{\n  char *pcVar1;\n  char cVar2;\n  byte bVar3;\n  int iVar4;\n  uint uVar5;\n  int iVar6;\n  \n  iVar6 = 1;\n  uVar5 = 10;\n  if (param_1 == (char *)0x0) {\n    return param_2;\n  }\n  cVar2 = *param_1;\n  if (cVar2 == \'-\') {\n    param_1 = param_1 + 1;\n    iVar6 = -1;\n  }\n  else {\n    if (cVar2 == \'$\') {\n      uVar5 = 0x10;\n    }\n    else if (cVar2 != \'+\') goto LAB_00444469;\n    param_1 = param_1 + 1;\n  }\nLAB_00444469:\n  iVar4 = 0;\n  bVar3 = (&g_006e5b50)[*param_1];\n  while (bVar3 < uVar5) {\n    iVar4 = iVar4 * uVar5 + (uint)bVar3;\n    pcVar1 = param_1 + 1;\n    param_1 = param_1 + 1;\n    bVar3 = (&g_006e5b50)[*pcVar1];\n  }\n  return iVar4 * iVar6;\n}\n\n'
sha=lambda b:hashlib.sha256(b).hexdigest()
class NumericSpellingTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  if not shutil.which('clang++'):raise unittest.SkipTest('clang++ unavailable')
  cls.tmp=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.tmp.cleanup);cls.out=Path(cls.tmp.name);cls.ast=parse(FIXTURE,cls.out/'base')
 def gen(self,s,ast=None):
  o=b'invalid synthetic PE; source refusals precede binary intake'
  return propose(s,ast if ast is not None else parse(s,self.out/'mutant'),0x1100,dict(source_sha256=sha(s.encode()),module_sha256=sha(o)),o)
 def no(self,s,reason):
  with self.assertRaisesRegex(Unsupported,reason):self.gen(s)
 def test_invalid_ast(self):
  a=copy.deepcopy(self.ast);a['inner'].append({'kind':'RecoveryExpr'})
  with self.assertRaisesRegex(Unsupported,'incomplete_AST'):self.gen(FIXTURE,a)
 def test_wrong_u32_type(self):self.no(FIXTURE.replace('typedef unsigned int    uint;','typedef unsigned __int64 uint;'),'consumed_type_uint')
 def test_unknown_write(self):self.no(FIXTURE.replace('  return iVar4 * iVar6;','  *param_1=0; return iVar4*iVar6;'),'body_shape')
 def test_signed_table(self):self.no(FIXTURE.replace('typedef unsigned char   undefined;','typedef signed char undefined;'),'unsigned_byte_lookup')
 def test_signed_digit(self):self.no(FIXTURE.replace('typedef unsigned char    byte;','typedef signed char byte;'),'unsigned_byte_lookup')
 def test_unknown_call(self):self.no('void unknown();\n'+FIXTURE.replace('  return iVar4 * iVar6;','  unknown(); return iVar4*iVar6;'),'body_shape')
 def test_escaped_pointer(self):self.no(FIXTURE.replace('pcVar1 = param_1 + 1','pcVar1 = param_1 + 2'),'body_shape')
 def test_changed_threshold(self):self.no(FIXTURE.replace('uVar5 = 10','uVar5 = 8'),'body_shape')
 def test_changed_sign(self):self.no(FIXTURE.replace('iVar6 = -1','iVar6 = 1'),'body_shape')
 def test_changed_increment(self):self.no(FIXTURE.replace('param_1 = param_1 + 1','param_1 = param_1 + 2'),'body_shape')
 def test_volatile_result(self):self.no(FIXTURE.replace('  int iVar4;','  volatile int iVar4;'),'body_shape')
 def test_macro(self):self.no('#define NEXT_CHAR (param_1 + 1)\n'+FIXTURE.replace('pcVar1 = param_1 + 1','pcVar1 = NEXT_CHAR'),'macro')
if __name__=='__main__':unittest.main()

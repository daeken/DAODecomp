"""Synthetic complete-body refusal controls; real regeneration remains private."""
import copy,hashlib,shutil,tempfile,unittest,os
if os.name == 'nt':raise unittest.SkipTest('Source generation uses the existing POSIX Clang AST workflow')
from pathlib import Path
from rapid_object.lookup_receiver_flags import propose
from rapid_object.conditional_construction import Unsupported
from rapid_object.ast_match import parse
FIXTURE='// Provisional deterministic Ghidra seed; signatures/types remain hypotheses.\ntypedef unsigned int pointer32;\ntypedef unsigned int code(...);\ntypedef unsigned char   undefined;\ntypedef unsigned char    byte;\ntypedef unsigned int    dword;\ntypedef unsigned __int64    GUID;\ntypedef pointer32 ImageBaseOffset32;\n\ntypedef __int64    longlong;\ntypedef unsigned char    uchar;\ntypedef unsigned int    uint;\ntypedef unsigned long    ulong;\ntypedef unsigned __int64    ulonglong;\ntypedef unsigned char    undefined1;\ntypedef unsigned short    undefined2;\ntypedef unsigned int    undefined4;\ntypedef unsigned __int64    undefined6;\ntypedef unsigned __int64    undefined8;\ntypedef unsigned short    ushort;\ntypedef unsigned short    word;\n\nextern "C" unsigned int __cdecl fn_00002200(...); /* ABI/return type unknown, provisional declaration */\nextern "C" unsigned int __cdecl fn_00003300(...); /* ABI/return type unknown, provisional declaration */\nextern "C" unsigned int __cdecl fn_00004400(...); /* ABI/return type unknown, provisional declaration */\nstruct Seed_00001100 { void __thiscall fn_00001100(undefined4 param_2,undefined4 param_3); };\n\n// FUNCTION: DAO 0x00401100\nvoid __thiscall Seed_00001100::fn_00001100(undefined4 param_2,undefined4 param_3)\n{\n  uint uVar1;\n  int iVar2;\n  undefined1 local_10 [16];\n  \n  fn_00002200(local_10,*(undefined4 *)(((int)this) + 8));\n  iVar2 = fn_00003300(param_2);\n  if ((((iVar2 != 0) && (uVar1 = *(uint *)(iVar2 + 4), -1 < (int)uVar1)) &&\n      ((uVar1 >> 0x1d & 1) == 0)) && (((uVar1 >> 0x1e & 1) == 0 && ((uVar1 & 0xffff) == 5)))) {\n    fn_00004400(*(int *)(iVar2 + 8) + *(int *)(((int)this) + 4),param_3);\n  }\n  return;\n}\n\n'
sha=lambda b:hashlib.sha256(b).hexdigest()
class LookupSpellingTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  if not shutil.which('clang++'):raise unittest.SkipTest('clang++ unavailable')
  cls.tmp=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.tmp.cleanup);cls.out=Path(cls.tmp.name);cls.ast=parse(FIXTURE,cls.out/'base')
 def gen(self,s,ast=None):
  o=b'invalid synthetic PE; source refusals precede binary intake'
  return propose(s,ast if ast is not None else parse(s,self.out/'mutant'),0x1100,dict(source_sha256=sha(s.encode()),module_sha256=sha(o)),o,b'{}')
 def no(self,s,reason):
  with self.assertRaisesRegex(Unsupported,reason):self.gen(s)
 def test_invalid_ast(self):
  a=copy.deepcopy(self.ast);a['inner'].append({'kind':'RecoveryExpr'})
  with self.assertRaisesRegex(Unsupported,'incomplete_AST'):self.gen(FIXTURE,a)
 def test_wrong_u32_type(self):self.no(FIXTURE.replace('typedef unsigned int    uint;','typedef unsigned __int64 uint;'),'consumed_type_uint')
 def test_unknown_write(self):self.no(FIXTURE.replace('  return;','  *(int*)this=7; return;'),'body_shape')
 def test_local_size(self):self.no(FIXTURE.replace('local_10 [16]','local_10 [8]'),'body_shape')
 def test_changed_null_guard(self):self.no(FIXTURE.replace('iVar2 != 0','iVar2 == 0'),'body_shape')
 def test_changed_bit(self):self.no(FIXTURE.replace('>> 0x1d','>> 0x1c'),'body_shape')
 def test_zero_type_tag(self):self.no(FIXTURE.replace('== 5','== 0'),'body_shape')
 def test_nonshort_type_tag(self):self.no(FIXTURE.replace('== 5','== 128'),'positive_short_type_tag')
 def test_octal_type_tag(self):self.no(FIXTURE.replace('== 5','== 05'),'body_shape')
 def test_positive_tag_reaches_original_profile(self):
  from unittest.mock import patch
  original=b'invalid synthetic PE: only proving source preconditions here'
  for tag in [1,4,5,6,10,127,'0xe','0x7f']:
   source=FIXTURE.replace('== 5','== '+str(tag))
   with self.subTest(tag=tag),patch('rapid_object.lookup_receiver_flags.g.Original',side_effect=RuntimeError('original_profile_required')),self.assertRaisesRegex(RuntimeError,'original_profile_required'):
    propose(source,parse(source,self.out/('tag'+str(tag))),0x1100,dict(source_sha256=sha(source.encode()),module_sha256=sha(original)),original,b'{}')
 def test_changed_argument(self):self.no(FIXTURE.replace('fn_00003300(param_2)','fn_00003300(param_3)'),'body_shape')
 def test_unknown_call(self):self.no('void unknown();\n'+FIXTURE.replace('  return;','  unknown(); return;'),'body_shape')
 def test_signed_byte(self):self.no(FIXTURE.replace('typedef unsigned char    byte;','typedef signed char byte;'),'unsigned_byte_type')
 def test_changed_field(self):self.no(FIXTURE.replace('iVar2 + 8','iVar2 + 0xc'),'body_shape')
 def test_macro(self):self.no('#define GET_FLAGS (*(uint *)(iVar2 + 4))\n'+FIXTURE.replace('*(uint *)(iVar2 + 4)','GET_FLAGS'),'macro')
if __name__=='__main__':unittest.main()

from rapid_object.lookup_receiver_flags import capture
class MultiRangeCalleeControls(unittest.TestCase):
 def cap(self,parts,cleanup=4):
  class Reader:
   class pe:image_base=0x400000
   def read(self,va,n,code=False):
    if va==0x402000 and n==1:return b'\xc3'
    if va not in parts or len(parts[va])!=n:raise ValueError('unknown synthetic code range')
    return parts[va]
  ranges=[dict(start_rva=v-0x400000,end_rva_inclusive=v-0x400000+len(b)-1) for v,b in sorted(parts.items())]
  return capture(Reader(),dict(rva=ranges[0]['start_rva'],body_ranges=ranges),cleanup)
 def test_multirange_gap_not_silently_filled(self):
  # Full direct receiver read, JMP over a gap, separate RET4 range.
  r=self.cap({0x401000:bytes.fromhex('8b4108e908000000'),0x401010:bytes.fromhex('c20400')});self.assertEqual(len(r['ranges']),2);self.assertEqual(r['return_cleanup_bytes'],4)
 def test_unknown_nested_context_remains_unknown(self):
  r=self.cap({0x401000:bytes.fromhex('e8fb0f0000c20800')},8);self.assertIn('unknown',r['ECX_context']);self.assertIn('unknown',r['formal_semantics'])
 def test_missing_jump_destination(self):
  with self.assertRaisesRegex(Unsupported,'CFG_boundary'):self.cap({0x401000:bytes.fromhex('8b4108e908000000')})
 def test_wrong_cleanup(self):
  with self.assertRaisesRegex(Unsupported,'cleanup'):self.cap({0x401000:bytes.fromhex('8b4108c20800')})
 def test_clobber_before_nested_call(self):
  with self.assertRaisesRegex(Unsupported,'ECX_context_unknown'):self.cap({0x401000:bytes.fromhex('33c9e8f90f0000c20400')})
 def test_partial_receiver_register_clobbers_before_copy_or_call(self):
  import struct
  for prefix in ['b100','b500','66b90000']:
   p=bytes.fromhex(prefix);tails=[bytes.fromhex('8bc1c20400'),b'\xe8'+struct.pack('<i',0x402000-(0x401000+len(p)+5))+bytes.fromhex('c20400')]
   for tail in tails:
    with self.subTest(prefix=prefix,tail=tail),self.assertRaisesRegex(Unsupported,'ECX_context_unknown'):self.cap({0x401000:p+tail})
 def test_unknown_indirect_call(self):
  with self.assertRaisesRegex(Unsupported,'indirect_call'):self.cap({0x401000:bytes.fromhex('8b4108ffd0c20400')})
 def test_unreachable_tail(self):
  with self.assertRaisesRegex(Unsupported,'cleanup'):self.cap({0x401000:bytes.fromhex('8b4108c2040090')})

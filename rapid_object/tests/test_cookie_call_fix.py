from pathlib import Path
import sys,tempfile,unittest,copy,struct
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parents[1]));sys.path.insert(0,str(R))
from rapid_object import ast_match as m
if (R/'cookie_call_fix.py').exists():
 import cookie_call_fix as rule
else:
 from rapid_object import cookie_call_fix as rule
PREFIX=bytes.fromhex('6aff680030500064a100000000505156a10020500033c4508d44240c64a3000000006a04')
def function(prefix=PREFIX,cleanup=4,target=0x400200):
 va=0x401000;data=prefix+b'\xe8'+struct.pack('<i',target-(va+len(prefix)+5))+bytes((0x83,0xc4,cleanup,0xc3))
 return {'rva':0x1000,'original_va':va,'original_bytes_hex':data.hex()}
CALLEE={'rva':0x200,'original_va':0x400200,'original_bytes_hex':(bytes.fromhex('8b4424046aff50e8')+struct.pack('<i',0x400300-(0x400200+12))+bytes.fromhex('83c408c3')).hex()}
SOURCE='''typedef unsigned int uint;
extern "C" void * _AddressOfReturnAddress(void);
#pragma intrinsic(_AddressOfReturnAddress)
extern "C" uint g_00102000;
extern "C" unsigned int __cdecl fn_00000200(...);
unsigned int fn_00001000() {
 uint cookie; uint value;
 cookie = g_00102000 ^ ((unsigned int)_AddressOfReturnAddress() + 0xffffffecu);
 value = fn_00000200(4,cookie);
 return value;
}
'''
class Tests(unittest.TestCase):
 def proposal(self,s=SOURCE,f=None,symbols=None,callees=None):
  with tempfile.TemporaryDirectory() as t:
   ast=m.parse(s,t);return rule.rewrite(s,ast,{'functions':[f or function()],'symbol_addresses':symbols or {'_g_00102000':0x502000}},callees if callees is not None else {0x400200:CALLEE})
 def reject(self,s=SOURCE,f=None):
  with self.assertRaises(rule.Unsupported):self.proposal(s,f)
 def test_bound_read_only_argument_removal(self):
  s,p=self.proposal();self.assertEqual(s,SOURCE.replace('(4,cookie)','(4)'));self.assertFalse(p['semantic_preservation_claim']);self.assertEqual(p['original']['argument_count'],1)
 def test_prefixed_return_refused(self):
  bad={**CALLEE,'original_bytes_hex':CALLEE['original_bytes_hex'][:-2]+'66c3'}
  with self.assertRaises(rule.Unsupported):self.proposal(callees={0x400200:bad})
 def test_callee_body_required(self):
  with self.assertRaises(rule.Unsupported):self.proposal(callees={})
 def test_callee_second_stack_word_refused(self):
  bad={**CALLEE,'original_bytes_hex':CALLEE['original_bytes_hex'].replace('8b442404','8b442408')}
  with self.assertRaises(rule.Unsupported):self.proposal(callees={0x400200:bad})
 def test_callee_ret_cleanup_refused(self):
  bad={**CALLEE,'original_bytes_hex':CALLEE['original_bytes_hex'][:-2]+'c20400'}
  with self.assertRaises(rule.Unsupported):self.proposal(callees={0x400200:bad})
 def test_other_code_byte_identical(self):
  s,p=self.proposal();a,b=p['source_edit']['span'];self.assertEqual(s,SOURCE[:a]+SOURCE[b:])
 def test_wrong_delta(self):self.reject(SOURCE.replace('ffffffec','fffffff0'))
 def test_wrong_global_binding(self):
  with self.assertRaises(rule.Unsupported):self.proposal(symbols={'_g_00102000':0x502004})
 def test_wrong_call_identity(self):self.reject(f=function(target=0x400210))
 def test_branch_entry(self):self.reject(f=function(b'\x74\x00'+PREFIX))
 def test_cleanup_mismatch(self):self.reject(f=function(cleanup=8))
 def test_incomplete_decode(self):
  f=function();f['original_bytes_hex']+='0f';self.reject(f=f)
 def test_no_cookie_push(self):self.reject(f=function(PREFIX.replace(b'\x33\xc4\x50',b'\x33\xc4\x90')))
 def test_zero_arguments(self):self.reject(f=function(PREFIX[:-2],0))
 def test_missing_FS_install(self):self.reject(f=function(PREFIX.replace(bytes.fromhex('64a300000000'),bytes.fromhex('a30000000090'))))
 def test_no_extra_argument(self):self.reject(SOURCE.replace('(4,cookie)','(cookie)'))
 def test_unknown_extra_argument(self):self.reject(SOURCE.replace('(4,cookie)','(4,value)'))
 def test_cookie_not_last(self):self.reject(SOURCE.replace('(4,cookie)','(cookie,4)'))
 def test_additional_cookie_use(self):self.reject(SOURCE.replace(' return value;',' value += cookie;\n return value;'))
 def test_reassignment(self):self.reject(SOURCE.replace(' value = fn_',' cookie = 0;\n value = fn_'))
 def test_unevaluated_builtin(self):self.reject(SOURCE.replace('value = fn_00000200(4,cookie);','value = __builtin_constant_p(fn_00000200(4,cookie));'))
 def test_sizeof(self):self.reject(SOURCE.replace('value = fn_00000200(4,cookie);','value = sizeof(fn_00000200(4,cookie));'))
 def test_conditional_call(self):self.reject(SOURCE.replace(' value = fn_',' if (value) value = fn_'))
 def test_nested_call(self):self.reject(SOURCE.replace('value = fn_00000200(4,cookie);','value = fn_00000200(fn_00000200(4,cookie));'))
 def test_volatile(self):self.reject(SOURCE.replace('uint cookie;','volatile uint cookie;'))
 def test_signed(self):self.reject(SOURCE.replace('uint cookie;','int cookie;'))
 def test_global_shadow(self):self.reject(SOURCE.replace('uint cookie;','uint g_00102000 = 0; uint cookie;'))
 def test_macro(self):self.reject(SOURCE.replace('typedef unsigned int uint;','#define FOUR 4\ntypedef unsigned int uint;').replace('(4,cookie)','(FOUR,cookie)'))
 def test_initialized_declaration(self):self.reject(SOURCE.replace('uint cookie;','uint cookie = 0;'))
if __name__=='__main__':unittest.main()

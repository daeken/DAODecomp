"""Synthetic compiler-independent dataflow and target-aware AST refusal checks."""
import copy
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest
from rapid_object import ast_match as m
try:
    from rapid_object import allocator_receiver_fix as rule
except ImportError:
    spec=importlib.util.spec_from_file_location('allocator_receiver_fix',Path(__file__).with_name('allocator_receiver_fix.py'));rule=importlib.util.module_from_spec(spec);spec.loader.exec_module(rule)


def fixture(word=True, receiver=True, branch=b'\x74', extra=b'', callee_ret=None):
    va=0x400100; target=0x4d2080 if word else 0x4d2070; code=bytearray()
    def emit(b): code.extend(b)
    def call(t): emit(b'\xe8'+struct.pack('<i',t-(va+len(code)+5)))
    if word: emit(b'\x89\xcf')  # save existing fastcall ECX input
    emit(b'\x6a\x04');call(0x413660);emit(b'\x89\xc6\x83\xc4\x04\x85\xf6')
    emit(branch+b'\x00');patch=len(code)-1
    if word:emit(b'\x57')
    emit(b'\x89\xf1' if receiver else b'\x31\xc9');emit(extra);call(target)
    code[patch]=len(code)-(patch+1);emit(b'\xc3')
    source=('extern "C" unsigned int __cdecl fn_00013660(...);\n'
            'extern "C" unsigned int __cdecl fn_%08x(...);\n'% (target-0x400000)+
            'unsigned int * '+('__fastcall ' if word else '')+'fn_00000100('+('unsigned int arg' if word else 'void')+') {\n'
            'unsigned int *p; unsigned int *out;\n'
            'p=(unsigned int *)fn_00013660(4); out=(unsigned int *)0;\n'
            'if(p != (unsigned int *)0) { fn_%08x('%(target-0x400000)+('arg' if word else '')+'); out=p; }\nreturn out; }\n')
    end=b'\xc2\x04\x00' if word else b'\xc3'
    if callee_ret is not None:end=callee_ret
    callee={'original_va':target,'original_bytes_hex':(b'\x89\xc8\xc7\x00\x78\x56\x34\x12\x83\x05\x34\x12\x40\x00\x01'+end).hex()}
    f={'rva':0x100,'original_va':va,'original_bytes_hex':code.hex()}
    report={'source_sha256':m.sha(source.encode()),'module_sha256':m.PIN,'functions':[f],'symbol_addresses':{'_fn_00013660':0x413660,'_fn_%08x'%(target-0x400000):target}}
    return source,report,{target:callee}


class ReceiverTests(unittest.TestCase):
    def rewrite(self, word=True, edit=None, **kwargs):
        source,report,callees=fixture(word,**kwargs)
        if edit:source=edit(source);report['source_sha256']=m.sha(source.encode())
        with tempfile.TemporaryDirectory() as tmp:
            ast=m.parse(source,Path(tmp));candidate,meta=rule.rewrite(source,ast,report,callees);m.parse(candidate,Path(tmp),'changed')
        return source,candidate,meta
    def test_existing_word_argument_preserved(self):
        old,new,meta=self.rewrite();self.assertIn('((void *)p, arg)',new);self.assertIn('void *, unsigned int',new);self.assertEqual(meta['original']['callee']['return_cleanup_bytes'],4);self.assertFalse(meta['semantic_preservation_claim']);self.assertIn('out=p',new)
    def test_later_parameter_uses_preserved(self):
        old,new,meta=self.rewrite(edit=lambda s:s.replace('out=p;', 'out=p; *out=arg;'));self.assertIn('*out=arg;',new)
    def test_existing_signed_argument_type_preserved(self):
        old,new,meta=self.rewrite(edit=lambda s:s.replace('unsigned int arg','int arg'));self.assertIn('void *, int',new);self.assertIn('((void *)p, arg)',new)
    def test_zero_argument_callee_distinct(self):
        old,new,meta=self.rewrite(False);self.assertIn('((void *)p)',new);self.assertNotIn('void *, unsigned int',new);self.assertEqual(meta['original']['callee']['return_cleanup_bytes'],0)
    def test_wrong_receiver(self):
        with self.assertRaisesRegex(rule.Unsupported,'receiver_not'):self.rewrite(receiver=False)
    def test_inverted_original_guard(self):
        with self.assertRaisesRegex(rule.Unsupported,'receiver_not'):self.rewrite(branch=b'\x75')
    def test_partial_receiver_write(self):
        with self.assertRaisesRegex(rule.Unsupported,'partial_register'):self.rewrite(extra=b'\xb1\x01')
    def test_extra_original_call(self):
        with self.assertRaisesRegex(rule.Unsupported,'not_unique'):self.rewrite(extra=b'\xe8\x00\x00\x00\x00')
    def test_wrong_callee_cleanup(self):
        with self.assertRaisesRegex(rule.Unsupported,'callee_identity'):self.rewrite(callee_ret=b'\xc3')
    def test_wrong_source_argument(self):
        with self.assertRaisesRegex(rule.Unsupported,'not_bound_word'):self.rewrite(edit=lambda s:s.replace('fn_000d2080(arg)','fn_000d2080(arg+1)'))
    def test_no_guessed_missing_argument(self):
        with self.assertRaisesRegex(rule.Unsupported,'entry_ABI'):self.rewrite(edit=lambda s:s.replace('fn_000d2080(arg)','fn_000d2080()'))
    def test_receiver_reassignment(self):
        with self.assertRaisesRegex(rule.Unsupported,'mutation'):self.rewrite(edit=lambda s:s.replace('if(p !=','p=out; if(p !='))
    def test_receiver_address_escape(self):
        with self.assertRaisesRegex(rule.Unsupported,'mutation'):self.rewrite(edit=lambda s:s.replace('if(p !=','(void)&p; if(p !='))
    def test_receiver_early_use(self):
        with self.assertRaisesRegex(rule.Unsupported,'early_use'):self.rewrite(edit=lambda s:s.replace('if(p !=','out=p; if(p !='))
    def test_nonzero_null_guard(self):
        with self.assertRaisesRegex(rule.Unsupported,'null_guard'):self.rewrite(edit=lambda s:s.replace('if(p != (unsigned int *)0)','if(p != (unsigned int *)(1+0))'))
    def test_side_effect_guard(self):
        with self.assertRaisesRegex(rule.Unsupported,'null_guard'):self.rewrite(edit=lambda s:s.replace('if(p != (unsigned int *)0)','if((p != (unsigned int *)0) && 1)'))
    def test_wrong_source_allocator_size(self):
        with self.assertRaisesRegex(rule.Unsupported,'allocator_setup'):self.rewrite(edit=lambda s:s.replace('fn_00013660(4)','fn_00013660(8)'))
    def test_macro_call(self):
        with self.assertRaisesRegex(rule.Unsupported,'macro'):self.rewrite(edit=lambda s:'#define CTOR(x) fn_000d2080(x)\n'+s.replace('fn_000d2080(arg)','CTOR(arg)'))
    def test_nested_constructor_call(self):
        with self.assertRaisesRegex(rule.Unsupported,'first_guarded'):self.rewrite(edit=lambda s:s.replace('fn_000d2080(arg);','out=(unsigned int *)fn_000d2080(arg);'))
    def test_argument_mutation(self):
        with self.assertRaisesRegex(rule.Unsupported,'parameter_other'):self.rewrite(edit=lambda s:s.replace('if(p !=','arg=3; if(p !='))
    def test_volatile_receiver(self):
        with self.assertRaisesRegex(rule.Unsupported,'receiver_storage'):self.rewrite(edit=lambda s:s.replace('unsigned int *p;','unsigned int * volatile p;'))
    def test_extra_source_call(self):
        with self.assertRaisesRegex(rule.Unsupported,'additional_source_call'):self.rewrite(edit=lambda s:'extern int other();\n'+s.replace('if(p !=','other(); if(p !='))
    def test_source_identity(self):
        s,r,c=fixture();r['source_sha256']='0'*64
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(rule.Unsupported,'bound_source'):rule.rewrite(s,m.parse(s,Path(tmp)),r,c)
    def test_decoder_truncation(self):
        s,r,c=fixture();r['functions'][0]['original_bytes_hex']+='0f'
        with self.assertRaisesRegex(rule.Unsupported,'incomplete_original'):rule.original_evidence(r['functions'][0],rule.callee_profile(next(iter(c.values()))),'entry:ecx')
    def test_wrong_argument_machine_provenance(self):
        s,r,c=fixture();r['functions'][0]['original_bytes_hex']=r['functions'][0]['original_bytes_hex'].replace('5789f1','5689f1',1)
        with self.assertRaisesRegex(rule.Unsupported,'argument_dataflow'):rule.original_evidence(r['functions'][0],rule.callee_profile(next(iter(c.values()))),'entry:ecx')
    def test_callee_edx_livein(self):
        s,r,c=fixture();f=next(iter(c.values()));f['original_bytes_hex']=f['original_bytes_hex'].replace('89c8','89d0',1)
        with self.assertRaisesRegex(rule.Unsupported,'receiver_livein'):rule.callee_profile(f)
    def test_callee_stack_read(self):
        s,r,c=fixture();f=next(iter(c.values()));f['original_bytes_hex']='8b442404'+f['original_bytes_hex'][4:]
        with self.assertRaisesRegex(rule.Unsupported,'receiver_livein'):rule.callee_profile(f)
    def test_callee_unknown_identity(self):
        s,r,c=fixture();f=next(iter(c.values()));f['original_va']+=0x100
        with self.assertRaisesRegex(rule.Unsupported,'identity'):rule.callee_profile(f)
    def test_narrow_parameter_refused(self):
        with self.assertRaisesRegex(rule.Unsupported,'not_bound_word'):self.rewrite(edit=lambda s:s.replace('unsigned int arg','unsigned short arg'))
    def test_integer_receiver_refused(self):
        with self.assertRaisesRegex(rule.Unsupported,'receiver_storage'):self.rewrite(edit=lambda s:s.replace('unsigned int *p;','unsigned int p;').replace('p=(unsigned int *)fn_00013660(4)','p=fn_00013660(4)').replace('if(p != (unsigned int *)0)','if(p != 0)').replace('out=p','out=(unsigned int *)p'))
    def test_callee_extra_instruction(self):
        s,r,c=fixture();f=next(iter(c.values()));f['original_bytes_hex']+='90'
        with self.assertRaisesRegex(rule.Unsupported,'complete_observed'):rule.callee_profile(f)
    def test_wrong_allocator_symbol(self):
        s,r,c=fixture();r['symbol_addresses']['_fn_00013660']+=4
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(rule.Unsupported,'allocator_symbol'):rule.rewrite(s,m.parse(s,Path(tmp)),r,c)
    def test_range_edge_outside(self):
        s,r,c=fixture();raw=bytearray.fromhex(r['functions'][0]['original_bytes_hex']);j=raw.index(0x74);raw[j+1]=127;r['functions'][0]['original_bytes_hex']=raw.hex()
        with self.assertRaisesRegex(rule.Unsupported,'outside_range'):rule.original_evidence(r['functions'][0],rule.callee_profile(next(iter(c.values()))),'entry:ecx')

    def test_loop_suffix_backedge_refused(self):
        s,r,c=fixture();raw=bytes.fromhex(r['functions'][0]['original_bytes_hex']);r['functions'][0]['original_bytes_hex']=(raw[:-1]+b'\xe2\xf9'+raw[-1:]).hex()
        with self.assertRaisesRegex(rule.Unsupported,'CFG_control_transfer:loop'):rule.original_evidence(r['functions'][0],rule.callee_profile(next(iter(c.values()))),'entry:ecx')
    def test_suffix_interrupt_refused(self):
        s,r,c=fixture();raw=bytes.fromhex(r['functions'][0]['original_bytes_hex']);r['functions'][0]['original_bytes_hex']=(raw[:-1]+b'\xcd\x80'+raw[-1:]).hex()
        with self.assertRaisesRegex(rule.Unsupported,'CFG_control_transfer:int'):rule.original_evidence(r['functions'][0],rule.callee_profile(next(iter(c.values()))),'entry:ecx')

if __name__=='__main__':unittest.main()

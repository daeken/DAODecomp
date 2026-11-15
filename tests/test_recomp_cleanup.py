"""Unsigned-emitter rewrite controls; not original-game validation."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from tools import recomp_cleanup as c


HEADER = '''using bits = unsigned __int128;
inline bits mask(unsigned width) { return width == 128 ? ~bits(0) : (bits(1) << width) - 1; }
inline bits narrow(bits value, unsigned width) { return value & mask(width); }
'''


class CleanupTests(unittest.TestCase):
    def test_nested_masks_keep_smallest_width_and_single_evaluation(self):
        source = 'auto x=narrow((narrow((narrow((next()), 64)), 32)), 64);'
        after, report = c.simplify(source)
        self.assertEqual(after, 'auto x=narrow(next(), 32);')
        self.assertEqual(after.count('next()'), 1)
        self.assertEqual(report['rules']['nested_masks'], 2)
        self.assertEqual(c.simplify(after)[0], after)

    def test_constants_fold_without_signed_or_overwide_literal(self):
        source = 'a=narrow((((bits(0x0ULL) << 64) | bits(0xffffffffffffffffULL))), 32);'
        self.assertEqual(c.simplify(source)[0], 'a=bits(0xffffffffULL);')
        high = 'a=((bits(0x1ULL) << 64) | bits(0x2ULL));'
        self.assertEqual(c.simplify(high)[0], high)
        self.assertEqual(c.simplify('a=narrow(bits(4), 0);')[0], 'a=bits(0x0ULL);')
        self.assertEqual(c.simplify('a=narrow(bits(4), 128);')[0], 'a=bits(0x4ULL);')

    def test_strings_comments_raw_strings_macros_and_other_helpers_stay_intact(self):
        source = '''// narrow(narrow(next(),64),32)
const char* a="narrow(narrow(next(),64),32)";
const char* b=R"tag(narrow(narrow(next(),64),32))tag";
#define X narrow(narrow(next(),64),32) \\
 + narrow(narrow(next(),64),32)
a=object.narrow(narrow(next(),64),32);
b=other::narrow(narrow(next(),64),32);
'''
        self.assertEqual(c.simplify(source)[0], source)

    def test_comma_operator_and_lambda_evaluation_order_are_preserved(self):
        source = 'auto x=narrow((narrow((first(),second()),64)),32);'
        self.assertEqual(c.simplify(source)[0], 'auto x=narrow((first(),second()), 32);')
        source = 'auto x=narrow(([&]()->bits{auto a=first();auto b=second();return a+b;}()),64);'
        after, _ = c.simplify(source)
        self.assertIn('auto a=first();auto b=second();return a+b;', after)
        self.assertEqual(after.count('first()'), 1)
        self.assertEqual(after.count('second()'), 1)

    def test_only_literal_and_one_register_getter_lambda_is_inlined(self):
        source = 'x=([&]()->bits{auto a=narrow(read_gpr_mask(s,4,0xffffffffULL),32);auto b=bits(4);return a-b;}());'
        self.assertEqual(c.simplify(source)[0], source)
        after, report = c.simplify(source, inline_register_literals=True)
        self.assertEqual(after, 'x=(narrow(read_gpr_mask(s,4,0xffffffffULL),32) - bits(4));')
        self.assertEqual(report['rules']['literal_arithmetic_lambdas'], 1)
        for getter in ('memory.load(4,32)', 'read_gpr_mask(s,index,mask)', 'temporary_with_destructor()'):
            source = 'x=([&]()->bits{auto a=' + getter + ';auto b=bits(4);return a-b;}());'
            self.assertEqual(c.simplify(source, inline_register_literals=True)[0], source)
        source = 'x=([&]()->bits{auto a=read_gpr_mask(s,4,15);auto b=read_gpr_mask(s,5,15);return a-b;}());'
        self.assertEqual(c.simplify(source, inline_register_literals=True)[0], source)

    def test_unknown_widths_overrides_and_malformed_input_refuse_or_remain(self):
        for source in ['x=narrow(narrow(next(),128),width);',
                       'x=narrow(narrow(next(),129),32);',
                       'x=narrow(narrow(next(),32),129);']:
            self.assertEqual(c.simplify(source)[0], source)
        c.require_runtime(HEADER)
        with self.assertRaisesRegex(ValueError, 'contract differs'):
            c.require_runtime(HEADER.replace('value & mask(width)', 'value'))
        with self.assertRaisesRegex(ValueError, 'unbalanced'):
            c.simplify('narrow((x,32);')
        with self.assertRaisesRegex(ValueError, 'budget'):
            c.simplify('narrow(narrow(x,64),32)', max_rounds=0)

    @unittest.skipUnless(shutil.which('clang++'), 'requires C++ compiler')
    def test_executed_unsigned_boundaries_and_ordered_effects_match(self):
        body = '''bits sample(bits input, unsigned& order) {
 auto first=[&]()->bits{order=order*10+1;return input;};
 auto second=[&]()->bits{order=order*10+2;return bits(0xffffffffffffffffULL);};
 return narrow((narrow(([&]()->bits{auto a=narrow(first(),64);auto b=narrow(second(),64);return a+b;}()),64)),32);
}'''
        after, _ = c.simplify(body)
        code = HEADER + '\nnamespace before {\n' + body + '\n}\nnamespace after {\n' + after + '\n}\n' + '''
int main(){
 bits values[]={0,1,0xffffffffULL,0x100000000ULL,0xffffffffffffffffULL,~bits(0)};
 for(auto value:values){unsigned a=0,b=0;if(before::sample(value,a)!=after::sample(value,b)||a!=12||a!=b)return 1;}
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'control.cpp').write_text(code)
            subprocess.run([shutil.which('clang++'), '-std=c++20', '-O2', str(root / 'control.cpp'), '-o', str(root / 'control')], capture_output=True, check=True)
            subprocess.run([str(root / 'control')], capture_output=True, check=True)

    @unittest.skipUnless(shutil.which('clang++'), 'requires C++ compiler')
    def test_inlined_getter_keeps_one_call_and_exception_side_effects(self):
        body = '''bits sample(State& s) {
 return narrow(([&]()->bits{auto a=narrow(read_gpr_mask(s,4,0xffffffffULL),32);auto b=bits(4);return a-b;}()),32);
}'''
        after, report = c.simplify(body, inline_register_literals=True)
        self.assertEqual(report['rules']['literal_arithmetic_lambdas'], 1)
        code = HEADER + '''
struct State { bits value; unsigned calls=0; bool fail=false; };
bits read_gpr_mask(State& s,unsigned,unsigned long long){++s.calls;if(s.fail)throw 7;return s.value;}
''' + '\nnamespace before {\n' + body + '\n}\nnamespace after {\n' + after + '\n}\n' + '''
int main(){
 bits values[]={0,1,3,4,0xffffffffULL,0x100000000ULL,~bits(0)};
 for(auto value:values){
  State a{value},b{value};if(before::sample(a)!=after::sample(b)||a.calls!=1||b.calls!=1)return 1;
  a=State{value,0,true};b=a;unsigned caught=0;
  try{before::sample(a);}catch(int code){if(code==7)++caught;}
  try{after::sample(b);}catch(int code){if(code==7)++caught;}
  if(caught!=2||a.calls!=1||b.calls!=1)return 2;
 }
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'control.cpp').write_text(code)
            subprocess.run([shutil.which('clang++'), '-std=c++20', '-O2', str(root / 'control.cpp'), '-o', str(root / 'control')], capture_output=True, check=True)
            subprocess.run([str(root / 'control')], capture_output=True, check=True)

"""Open fixed-width bit arithmetic, not original-game acceptance."""
import copy,json,subprocess,unittest
from test_replayable_ir import DLL,DOTNET,node,ty,reg,const,write
from test_replayable_stackargs import row,ret

def cast(op,x,bits,signed=False):
 t=ty(bits);t['Signed']=signed
 return node('IlCast',Kind=dict(name=op),X=x,Ty=t)
def binary(op,a,b,bits,signed=False):
 t=ty(bits);t['Signed']=signed
 return node('IlBin',Op=dict(name=op),L=a,R=b,Ty=t)
def fixture(expr,source=False):
 rows=[row(0x502000,[write(0,cast('Zext',expr,64))]),row(0x502001,ret(0),'c3')]
 for r in rows:r.update(opaque_markers=[],lift_error=None)
 return dict(lift=dict(schema='sharpretro_instruction_lift_v1',mode='Bits32',decode_complete=True,lift_errors=0,opaque_instructions=0,instructions=rows),flow_paths=not source,source_profiles=source,callee_lifts=[],rva=0x2000,image_base=0x500000,image_end=0x600000,module='open.exe')
def signed(x,w):return x-(1<<w)if x>>(w-1)else x

@unittest.skipUnless(DLL.exists(),'build changed component first')
class SignedBitsTests(unittest.TestCase):
 def recover(self,p):return json.loads(subprocess.check_output([DOTNET,str(DLL),'recover-ir'],input=json.dumps(p).encode()))
 def value(self,e):
  r=self.recover(fixture(e));self.assertEqual(r['status'],'recovered',r);return r['ir']['normal_paths'][0]['exit']['return']['value']
 def test_sign_extension_extremes(self):
  for w in (8,16,32):
   for x in (0,1,(1<<(w-1))-1,1<<(w-1),(1<<w)-1):
    self.assertEqual(self.value(cast('Sext',const(x,w),64,True)),signed(x,w)&0xffffffff)
 def test_full_product_high_half_and_wrapped_low_half(self):
  values=(0,1,0x7fffffff,0x80000000,0xffffffff)
  for a,b in [(a,b)for a in values for b in values]:
   product=binary('Mul',cast('Sext',const(a),64,True),cast('Sext',const(b),64,True),64,True);expected=(signed(a,32)*signed(b,32))&((1<<64)-1)
   self.assertEqual(self.value(cast('Trunc',product,32)),expected&0xffffffff)
   self.assertEqual(self.value(cast('Trunc',binary('Shr',product,const(32,64),64,True),32)),expected>>32)
 def test_arithmetic_and_logical_shift_are_distinct(self):
  for w in (8,16,32):
   for x in (0,1,(1<<(w-1))-1,1<<(w-1),(1<<w)-1):
    for n in (0,1,w-1):
     self.assertEqual(self.value(binary('Sar',const(x,w),const(n,8),w)),(signed(x,w)>>n)&((1<<w)-1))
     self.assertEqual(self.value(binary('Shr',const(x,w),const(n,8),w)),x>>n)
 def test_masked_architectural_count_and_unproven_count_boundary(self):
  for n in (0,31,32,33,255):
   count=binary('And',const(n,8),const(31,8),8)
   self.assertEqual(self.value(binary('Sar',const(0x80000000),count,32)),(signed(0x80000000,32)>>(n&31))&0xffffffff)
  for count in (const(32,8),reg(1)):
   r=self.recover(fixture(binary('Sar',const(1),count,32)));self.assertEqual(r['status'],'unsupported');self.assertEqual(r['blocker'],'arithmetic_shift_count_unproven')
 def test_signed_comparison_flag_relation_including_overflow(self):
  for a,b in ((0,0xffffffff),(0x80000000,1),(0x7fffffff,0xffffffff),(0xffffffff,0),(0x80000000,0x7fffffff)):
   x,y=const(a),const(b);delta=binary('Sub',x,y,32);sf=cast('Trunc',binary('Shr',delta,const(31),32),1);of=binary('Ne',binary('And',binary('And',binary('Xor',x,y,32),binary('Xor',x,delta,32),32),const(0x80000000),32),const(0),1)
   self.assertEqual(self.value(binary('Ne',sf,of,1)),int(signed(a,32)<signed(b,32)))
   self.assertEqual(self.value(binary('Ult',x,y,1)),int(a<b))
 def test_bad_cast_and_float_width_refuse(self):
  for e in (cast('Bitcast',const(1,8),32,True),cast('Sext',const(1,32),16,True),cast('Sext',const(1,1),32,True)):
   self.assertEqual(self.recover(fixture(e))['status'],'unsupported')
  e=const(1);e['Ty']=dict(type='LiftIl.IlType+F',Bits=32);self.assertEqual(self.recover(fixture(e))['status'],'unsupported')
 def test_graph_preserves_signed_product_and_extension(self):
  expr=cast('Trunc',binary('Mul',cast('Sext',const(0xffffffff),64,True),cast('Sext',const(0x80000000),64,True),64,True),32);p=fixture(expr);p.pop('flow_paths');p['graph_paths']=True;r=self.recover(p);self.assertEqual(r['status'],'recovered',r);self.assertEqual(r['ir']['blocks'][0]['registers']['0']['value'],0x80000000)
 def test_source_profile_retains_faulting_read_and_unsigned_math(self):
  value=node('IlLoad',Addr=reg(1),Ty=ty(32));expr=cast('Trunc',binary('Shr',binary('Mul',cast('Sext',value,64,True),cast('Sext',const(17),64,True),64,True),const(32,64),64,True),32);p=fixture(expr,True);r=self.recover(p);self.assertEqual(r['status'],'generated',r);self.assertEqual(r['profile_attempts'][-1]['profile'],'readonly_scalar_paths');self.assertIn('read32(',r['source']);self.assertIn('bits64',r['source']);self.assertFalse(r['proof']);self.assertEqual(sum(e['kind']=='memory_read'for e in r['ir']['flow']['normal_paths'][0]['effects']),1)
 def test_undefined_flag_used_as_result_refuses(self):
  p=fixture(const(0),True);p['lift']['instructions'][0]['tree']['Body']=[node('IlWriteReg',Kind=dict(name='Eflags'),Idx=7,Val=node('IlUndefined',Ty=ty(1),Reason='open undefined')),write(0,node('IlReadReg',Kind=dict(name='Eflags'),Idx=7,Ty=ty(1)))];r=self.recover(p);self.assertEqual(r['status'],'unsupported');self.assertIn('undefined_flag',r['blocker'])

 def test_ambiguous_signed_binary_width_is_not_assumed(self):
  for e in (binary('Mul',const(2,32),const(3,32),64,True),binary('Sar',const(128,8),const(1,8),32,True)):
   r=self.recover(fixture(e));self.assertEqual(r['status'],'unsupported');self.assertIn('width',r['blocker'])

 def test_emitted_wide_variable_product_and_shift_have_wide_operands(self):
  # Review counterexamples: x=0x80000000 gives high32(x*x)=0x40000000;
  # zero-extending x then shifting by32 gives0, never a 32-bit shift by32.
  x=cast('Zext',cast('Trunc',reg(1),32),64)
  for expr in (binary('Shr',binary('Mul',x,x,64),const(32,64),64),binary('Shr',x,const(32,64),64)):
   r=self.recover(fixture(cast('Trunc',expr,32),True));self.assertEqual(r['status'],'generated',r)
   source=r['source'];self.assertIn('static_cast<bits64>(reinterpret_cast<unsigned int>(this))',source)
   self.assertNotIn('(reinterpret_cast<unsigned int>(this) * reinterpret_cast<unsigned int>(this))',source)
   self.assertNotIn('(reinterpret_cast<unsigned int>(this) >>',source)
  self.assertEqual(((0x80000000*0x80000000)&((1<<64)-1))>>32,0x40000000)
 def test_comparison_does_not_narrow_operands_to_boolean_width(self):
  expr=binary('Ult',cast('Trunc',reg(1),32),const(0x80000000),1)
  r=self.recover(fixture(expr,True));self.assertEqual(r['status'],'generated',r)
  self.assertIn('< 2147483648u',r['source']);self.assertNotIn('reinterpret_cast<unsigned int>(this)) & 1u) <',r['source'])

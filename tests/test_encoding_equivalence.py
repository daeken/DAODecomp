import struct
import tempfile
import shutil
import subprocess
import unittest
from pathlib import Path
from rapid_object.encoding_equivalence import certify_range,Refusal,Relocation,instruction_fields,decode
import copy


def store(base,index,*,scale=0,mod=1,disp=4,bits=8,imm=0,prefix=b''):
    opcode=b'\xc6' if bits==8 else b'\xc7'
    if bits==16:prefix+=b'\x66'
    displacement=b'' if mod==0 and base!=5 else struct.pack('<b',disp) if mod==1 else struct.pack('<i',disp)
    return prefix+opcode+bytes([(mod<<6)|4,(scale<<6)|(index<<3)|base])+displacement+imm.to_bytes(bits//8,'little')


def mock_lift(raw,pc):
 # Open typed adapter-contract fixture, not a measured SharpRetro result.
 f=instruction_fields(decode(raw,pc)[0])
 def ty(bits):return {'type':'LiftIl.IlType+I','Bits':bits,'Signed':False}
 def node(kind,bits,**kw):return dict(type='LiftIl.'+kind,Ty=ty(bits),**kw)
 def add(a,b):return node('IlBin',64,Op={'name':'Add'},L=a,R=b)
 regs=[node('IlReadReg',64,Kind={'name':'X86'},Idx=x) for x in (f['base'],f['index'])]
 address=node('IlCast',64,Kind={'name':'Zext'},X=node('IlCast',32,Kind={'name':'Trunc'},X=add(add(*regs),node('IlConst',64,Bits={'decimal':str(f['displacement']&0xffffffffffffffff)}))))
 row={'offset':0,'pc':pc,'length':len(raw),'raw_hex':raw.hex(),'lift_error':None,'opaque_markers':[],'decoded':{'P':{},'M':{'BaseReg':f['base'],'IndexReg':f['index'],'Scale':1,'Disp':f['displacement'],'IsReg':False,'RipRelative':False}},'tree':{'type':'LiftIl.IlBlock','Body':[{'type':'LiftIl.IlLet','Id':0,'Val':address},{'type':'LiftIl.IlStore','Addr':node('IlTmp',64,Id=0),'Val':node('IlConst',f['width_bits'],Bits={'decimal':str(f['immediate'])})}]}}
 return {'schema':'sharpretro_instruction_lift_v1','mode':'Bits32','pc':pc,'byte_length':len(raw),'decoded_bytes':len(raw),'decode_complete':True,'unprocessed_hex':'','lift_errors':0,'opaque_instructions':0,'instructions':[row]}
def mock_pair(a,b,pc):return [mock_lift(a,pc),mock_lift(b,pc)]

class EncodingEquivalenceTests(unittest.TestCase):
    def check(self,a,b,**kwargs):
        return certify_range(a,b,pc=kwargs.pop('pc',0x1000),complete_length=kwargs.pop('complete_length',len(a)),lift_pair=kwargs.pop('lift_pair',mock_pair),**kwargs)
    def test_generic_positive_register_pairs_widths_displacement_boundaries(self):
        count=0
        for base,index in [(0,1),(1,7),(2,3),(3,6),(6,7),(7,0)]:
            for bits in [8,16,32]:
                for mod,disp in [(0,0),(1,-128),(1,0),(1,127),(2,-0x80000000),(2,0x7fffffff)]:
                    with self.subTest(base=base,index=index,bits=bits,disp=disp):
                        a=b'\x90'+store(base,index,bits=bits,mod=mod,disp=disp)+b'\xc3'
                        b=b'\x90'+store(index,base,bits=bits,mod=mod,disp=disp)+b'\xc3'
                        result=self.check(a,b);self.assertEqual(result['status'],'encoding_equivalent');self.assertFalse(result['whole_function_equivalence_proven']);count+=1
        self.assertEqual(count,108)
    def test_immediate_bit_patterns(self):
        for bits in [8,16,32]:
            for immediate in [0,1,1<<(bits-1),(1<<bits)-1]:
                result=self.check(store(0,1,bits=bits,imm=immediate),store(1,0,bits=bits,imm=immediate))
                self.assertEqual(result['effect']['value'],immediate)
    def test_multiple_differences_and_other_same_size_displacement_form(self):
        with self.assertRaises(Refusal):self.check(store(0,1)+store(2,3),store(1,0)+store(3,2))
        with self.assertRaises(Refusal):self.check(store(0,1,mod=2,disp=0),store(1,0,mod=2,disp=1))
    def test_nonunit_scale(self):
        with self.assertRaises(Refusal):self.check(store(0,1,scale=1),store(1,0,scale=1))
    def test_segment_sensitive_base_and_index(self):
        for special in [4,5]:
            with self.subTest(special=special),self.assertRaises(Refusal):self.check(store(special,1),store(1,special))
    def test_no_base_and_no_index(self):
        with self.assertRaises(Refusal):self.check(store(5,1,mod=0),store(1,5,mod=0)+b'\x90'*4)
        with self.assertRaises(Refusal):self.check(store(0,4),store(4,0))
    def test_displacement_width_opcode_immediate_and_prefix_differences(self):
        a=store(0,1)
        bad=[store(1,0,disp=5),store(1,0,bits=16),store(1,0,imm=1),
             b'\x67'+store(1,0),b'\x64'+store(1,0),bytes([0xc7])+store(1,0)[1:]]
        for b in bad:
            with self.subTest(b=b.hex()),self.assertRaises(Refusal):self.check(a,b)
    def test_identical_unsupported_prefixes(self):
        for prefix in [b'\x64',b'\x67',b'\xf0',b'\xf2',b'\xf3',b'\x66\x66']:
            with self.subTest(prefix=prefix.hex()),self.assertRaises(Refusal):self.check(store(0,1,prefix=prefix),store(1,0,prefix=prefix))
    def test_nonstore_or_non_immediate_and_extra_difference(self):
        for a,b in [(bytes.fromhex('8d440804'),bytes.fromhex('8d440104')),
                    (bytes.fromhex('88440804'),bytes.fromhex('88440104')),
                    (store(0,1)+b'\x90',store(1,0)+b'\x91')]:
            with self.subTest(a=a.hex()),self.assertRaises(Refusal):self.check(a,b)
    def test_range_missing_conflicting_and_partial_decode(self):
        a,b=store(0,1),store(1,0)
        for left,right,n in [(a,b,len(a)+1),(a,b[:-1],len(a)),(a+b'\x0f',b+b'\x0f',len(a)+1)]:
            with self.subTest(n=n),self.assertRaises(Refusal):self.check(left,right,complete_length=n)
    def test_resolved_relocation_and_unresolved_changed_duplicate(self):
        pc=0x1000;target=0x2000
        a=b'\xe8'+struct.pack('<I',target-pc-5)+store(0,1)+b'\xc3'
        raw=b'\xe8'+b'\0'*4+store(1,0)+b'\xc3';rel=Relocation(1,0x14,target,0)
        self.assertEqual(self.check(a,raw,relocations=[rel])['relocations_checked'],1)
        for rels in [[],[Relocation(1,0x14,None,0)],[Relocation(1,0x14,target+1,0)],[rel,rel],
                     [Relocation(1,0x99,target,0)],[Relocation(1,0x14,target,1)]]:
            with self.subTest(rels=rels),self.assertRaises(Refusal):self.check(a,raw,relocations=rels)
    def test_direct_branch_to_instruction_interior_refused(self):
        a=b'\xeb\x01'+store(0,1)+b'\xc3';b=b'\xeb\x01'+store(1,0)+b'\xc3'
        with self.assertRaisesRegex(Refusal,'interior'):self.check(a,b)
    def test_exact_match_is_not_normalized_or_claimed(self):
        a=store(0,1)
        with self.assertRaises(Refusal):self.check(a,a)

    def test_missing_bad_unknown_and_forged_typed_lift_refuse(self):
        a,b=store(0,1),store(1,0)
        for mutation in ('missing','mode','raw','partial','extra_effect','value','register','undefined','tmp'):
            def lifted(left,right,pc):
                rows=mock_pair(left,right,pc)
                if mutation=='missing':return []
                target=rows[1];row=target['instructions'][0];body=row['tree']['Body']
                if mutation=='mode':target['mode']='Bits64'
                elif mutation=='raw':row['raw_hex']=left.hex()
                elif mutation=='partial':target['decode_complete']=False
                elif mutation=='extra_effect':body.append({'type':'LiftIl.IlUndefined'})
                elif mutation=='value':body[1]['Val']['Bits']['decimal']='1'
                elif mutation=='register':body[0]['Val']['X']['X']['L']['L']['Idx']=2
                elif mutation=='undefined':body[0]['Val']['X']['X']['L']['L']={'type':'LiftIl.IlUndefined','Reason':'IMUL1 flag 2','Ty':{'type':'LiftIl.IlType+I','Bits':64,'Signed':False}}
                elif mutation=='tmp':body[1]['Addr']['Id']=1
                return rows
            with self.subTest(mutation=mutation),self.assertRaises(Refusal):self.check(a,b,lift_pair=lifted)
    def test_incoming_register_value_change_is_never_an_encoding_relation(self):
        with self.assertRaises(Refusal):self.check(bytes.fromhex('8bc1'),bytes.fromhex('8bc2'))
    def test_indirect_control_target_unknown_refuses(self):
        with self.assertRaisesRegex(Refusal,'indirect_control'):self.check(bytes.fromhex('ffd0')+store(0,1),bytes.fromhex('ffd0')+store(1,0))

if __name__=='__main__':unittest.main()

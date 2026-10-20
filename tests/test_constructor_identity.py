import unittest
from rapid_object.constructor_identity import constructor_identity

class ConstructorIdentityTests(unittest.TestCase):
 def test_supported_global_int_constructor(self):
  self.assertEqual(constructor_identity('??0fn_00001234@@QAE@H@Z'),('fn',0x1234))
  self.assertEqual(constructor_identity('??0fn_0000AbCd@@QAE@H@Z'),('fn',0xabcd))
 def test_supported_global_zero_argument_constructor(self):
  self.assertEqual(constructor_identity('??0fn_00001234@@QAE@XZ'),('fn',0x1234))
  self.assertEqual(constructor_identity('??0fn_0000AbCd@@QAE@XZ'),('fn',0xabcd))
 def test_zero_argument_near_misses_refuse(self):
  for name in ['??0fn_00001234@@QEAA@XZ','??0fn_00001234@@QAA@XZ','??0fn_00001234@@QAG@XZ','??0fn_00001234@@QBE@XZ','??0fn_00001234@@QAE@X@Z','??0fn_0001234@@QAE@XZ','??0fn_000001234@@QAE@XZ','??0Wrapper_fn_00001234@@QAE@XZ','??0fn_00001234@Namespace@@QAE@XZ','__imp_??0fn_00001234@@QAE@XZ','__ehhandler$??0fn_00001234@@QAE@XZ','__unwindfunclet$??0fn_00001234@@QAE@XZ$0','??0fn_00001234@@QAE@XZsuffix','prefix??0fn_00001234@@QAE@XZ']:
   with self.subTest(name=name):self.assertIsNone(constructor_identity(name))
 def test_other_special_members_and_embedded_names_refuse(self):
  for name in ['??1fn_00001234@@QAE@XZ','??2fn_00001234@@SAPAXI@Z','??3fn_00001234@@SAXPAX@Z','?other@fn_00001234@@QAEXXZ','??0Wrapper_fn_00001234@@QAE@H@Z','??0fn_00001234@Namespace@@QAE@H@Z','??0fn_00001234@@QAE@I@Z','??0fn_00001234@@QEAA@H@Z','__imp_??0fn_00001234@@QAE@H@Z','__ehhandler$??0fn_00001234@@QAE@H@Z','__unwindfunclet$??0fn_00001234@@QAE@H@Z$0','??0fn_00001234@@QAE@H@Zsuffix','prefix??0fn_00001234@@QAE@H@Z',None,123]:
   with self.subTest(name=name):self.assertIsNone(constructor_identity(name))
if __name__=='__main__':unittest.main()

class ConstructorBindingTests(unittest.TestCase):
 def renamed(self,new):
  from test_eh_native import fixture,sha
  from test_eh_graph import coff,PARENT
  kw,s,y=fixture()
  def rename(n):return n.replace(PARENT,new)
  s=[(a,b,[(o,rename(n),k) for o,n,k in rs],fl) for a,b,rs,fl in s];y=[(rename(n),v,c,t,st,size) for n,v,c,t,st,size in y];kw['object_bytes']=coff(s,y);kw['build']['object_sha256']=sha(kw['object_bytes']);return kw,s,y
 def test_defined_constructor_and_generated_parent_stay_distinct(self):
  from rapid_object.eh_native import check
  kw,_,_=self.renamed('??0fn_00001000@@QAE@H@Z');r=check(**kw);self.assertEqual(r['status'],'exact_eh_graph_match',r);self.assertEqual(r['requested'][0x1000]['symbol'],'??0fn_00001000@@QAE@H@Z')
 def test_unsupported_constructor_decoration_cannot_bind_main(self):
  from rapid_object.eh_native import check
  for name in ['??0fn_00001000@@QAE@I@Z','??1fn_00001000@@QAE@XZ','??2fn_00001000@@SAPAXI@Z']:
   kw,_,_=self.renamed(name)
   with self.subTest(name=name):self.assertNotEqual(check(**kw)['status'],'exact_eh_graph_match')
 def test_external_constructor_binding_uses_pinned_identity(self):
  from test_eh_native import fixture,sha
  from test_eh_graph import coff
  from rapid_object.eh_native import check
  kw,s,y=fixture();old='_fn_00001450';new='??0fn_00001450@@QAE@H@Z';s=[(a,b,[(o,new if n==old else n,k) for o,n,k in rs],fl) for a,b,rs,fl in s];y=[(new if n==old else n,v,c,t,st,size) for n,v,c,t,st,size in y];kw['object_bytes']=coff(s,y);kw['build']['object_sha256']=sha(kw['object_bytes']);self.assertEqual(check(**kw)['status'],'exact_eh_graph_match')

 def external(self,new):
  from test_eh_native import fixture,sha
  from test_eh_graph import coff
  kw,s,y=fixture();old='_fn_00001450'
  s=[(a,b,[(o,new if n==old else n,k) for o,n,k in rs],fl) for a,b,rs,fl in s]
  y=[(new if n==old else n,v,c,t,st,size) for n,v,c,t,st,size in y]
  kw['object_bytes']=coff(s,y);kw['build']['object_sha256']=sha(kw['object_bytes']);return kw
 def test_zero_argument_constructor_main_and_external_bind_independently(self):
  from rapid_object.eh_native import check
  main,_,_=self.renamed('??0fn_00001000@@QAE@XZ')
  self.assertEqual(check(**main)['status'],'exact_eh_graph_match')
  external=self.external('??0fn_00001450@@QAE@XZ')
  self.assertEqual(check(**external)['status'],'exact_eh_graph_match')
 def test_constructor_wrong_main_rva_does_not_self_bind(self):
  from rapid_object.eh_native import check
  for rva in ('00001450','00001001','00009999'):
   for suffix in ('XZ','H@Z'):
    kw,_,_=self.renamed('??0fn_'+rva+'@@QAE@'+suffix)
    with self.subTest(rva=rva,suffix=suffix):self.assertNotEqual(check(**kw)['status'],'exact_eh_graph_match')
 def test_constructor_external_wrong_target_and_unknown_identity_refuse(self):
  from rapid_object.eh_native import check
  for rva in ('00001000','00001400','00001451','00009999'):
   for suffix in ('XZ','H@Z'):
    with self.subTest(rva=rva,suffix=suffix):self.assertNotEqual(check(**self.external('??0fn_'+rva+'@@QAE@'+suffix))['status'],'exact_eh_graph_match')
 def test_zero_argument_generated_or_wrapped_names_cannot_bind_main_or_external(self):
  from rapid_object.eh_native import check
  for template in ('__imp_??0fn_{rva}@@QAE@XZ','__ehhandler$??0fn_{rva}@@QAE@XZ','__unwindfunclet$??0fn_{rva}@@QAE@XZ$0','??0fn_{rva}@Namespace@@QAE@XZ','??0Wrapper_fn_{rva}@@QAE@XZ','??0fn_{rva}@@QAE@XZsuffix','??0fn_{rva}@@QEAA@XZ'):
   with self.subTest(template=template):
    kw,_,_=self.renamed(template.format(rva='00001000'))
    self.assertNotEqual(check(**kw)['status'],'exact_eh_graph_match')
    self.assertNotEqual(check(**self.external(template.format(rva='00001450')))['status'],'exact_eh_graph_match')

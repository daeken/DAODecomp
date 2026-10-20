import unittest
from rapid_object.constructor_identity import constructor_identity

class ConstructorIdentityTests(unittest.TestCase):
 def test_supported_global_int_constructor(self):
  self.assertEqual(constructor_identity('??0fn_00001234@@QAE@H@Z'),('fn',0x1234))
  self.assertEqual(constructor_identity('??0fn_0000AbCd@@QAE@H@Z'),('fn',0xabcd))
 def test_other_special_members_and_embedded_names_refuse(self):
  for name in ['??1fn_00001234@@QAE@XZ','??2fn_00001234@@SAPAXI@Z','??3fn_00001234@@SAXPAX@Z','?other@fn_00001234@@QAEXXZ','??0Wrapper_fn_00001234@@QAE@H@Z','??0fn_00001234@Namespace@@QAE@H@Z','??0fn_00001234@@QAE@I@Z','??0fn_00001234@@QAE@XZ','??0fn_00001234@@QEAA@H@Z','__imp_??0fn_00001234@@QAE@H@Z','__ehhandler$??0fn_00001234@@QAE@H@Z','__unwindfunclet$??0fn_00001234@@QAE@H@Z$0','??0fn_00001234@@QAE@H@Zsuffix','prefix??0fn_00001234@@QAE@H@Z',None,123]:
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

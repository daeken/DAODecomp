import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from rapid_object import ast_match as m


class AstMatchTests(unittest.TestCase):
    def variants(self, source, limit=8):
        with tempfile.TemporaryDirectory() as temp:
            return m.proposals(source,m.parse(source,temp),limit)

    def test_zero_comparison_first_and_bounded_deterministic(self):
        source='int f(int a,int b){return a<b && b!=0;}'
        a=self.variants(source);b=self.variants(source)
        self.assertEqual(a,b);self.assertEqual(len(a),8)
        self.assertEqual(a[0]['source'],'int f(int a,int b){return a<b && ((unsigned int)(b)) > 0u;}')
        self.assertEqual(a[1]['source'],'int f(int a,int b){return a<=b && b!=0;}')
        self.assertEqual(len({x['source_sha256'] for x in a}),8)
        self.assertTrue(all(x['status']=='UNVALIDATED' for x in a))

    def test_float_pointer_and_narrow_comparisons_not_mutated(self):
        self.assertEqual(self.variants('int f(float a,float b){return a<b;}'),[])
        self.assertEqual(self.variants('int f(int *a,int *b){return a<b;}'),[])

    def test_comments_and_strings_untouched(self):
        source='int f(int x){const char *s="x!=0"; /* x!=0 */ return x!=0;}'
        for v in self.variants(source):
            self.assertIn('"x!=0"; /* x!=0 */',v['source'])

    def test_complete_parse_required(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaisesRegex(ValueError,'incomplete_parse'):
                m.parse('int f(){return missing;}',t)

    def test_no_operand_reversal_for_calls_or_volatile(self):
        for source in ('int g(); int f(){return g()!=0;}', 'int f(volatile int &v){return v!=0;}'):
            self.assertFalse(any(v['edit']['kind']=='pure_comparison_orientation' for v in self.variants(source)))

    def test_unsigned_zero_rule_is_generic(self):
        for op,ordered in (('!=','>'),('==','<=')):
            v=self.variants('int f(int a){return a'+op+'0;}')
            self.assertEqual(v[0]['edit']['kind'],'unsigned_ordered_zero_hypothesis')
            self.assertIn(')) '+ordered+' 0u',v[0]['source'])

    def test_macros_not_edited(self):
        self.assertEqual(self.variants('#define C(x) ((x)!=0)\nint f(int x){return C(x);}'),[])

    def test_baseline_source_and_object_are_bound(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t).resolve();source=root/'candidate.cpp';source.write_text('int f(){return 0;}')
            obj=root/'candidate.obj';obj.write_bytes(b'object')
            summary=root/'summary.json'
            report={'source_sha256':m.sha(source.read_bytes()),'object_sha256':m.sha(obj.read_bytes())}
            summary.write_text(json.dumps(report))
            case={'source':str(source),'summary':str(summary),'source_sha256':report['source_sha256']}
            source.write_text('int f(){return 1;}')
            with self.assertRaisesRegex(ValueError,'baseline_source_identity'):m.baseline(case)
            source.write_text('int f(){return 0;}');obj.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'baseline_object_identity'):m.baseline(case)

    def test_exact_label_without_artifact_binding_cannot_accept(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t).resolve();(root/'local/rapid-object').mkdir(parents=True)
            source='int f(int x){return x!=0;}'
            case={'rva':1,'category':'near'}
            request={'original_va':0x400001,'ranges':[],'bytes_sha256':'unknown'}
            retained={'requested':{'1':request},'symbol_addresses':{},'functions':[{'object_bytes_hex':'baseline'}]}
            def fake_build(path, output, requested, registry):
                output.mkdir();(output/'candidate.obj').write_bytes(b'object')
                return {'build':{'exit_code':0},'functions':[{'status':'exact_object_match','object_bytes_hex':'different'}]}
            with patch.object(m,'REPO',root), patch.object(m,'baseline',return_value=(source,retained)), patch.object(m,'parse',return_value={}), patch.object(m,'proposals',return_value=[{'source':source,'source_sha256':m.sha(source.encode()),'edit':None}]), patch.object(m.state,'bindings',return_value={}), patch.object(m.state,'report_bound',return_value=False), patch('rapid_object.build.build_and_compare',side_effect=fake_build):
                result=m.evaluate(case,root)
            self.assertEqual(result['status'],'UNVALIDATED')
            self.assertEqual(result['attempts'][0]['status'],'inconclusive')
            self.assertNotIn('accepted_source',result)

    def test_nonascii_refused(self):
        with self.assertRaisesRegex(ValueError,'non_ascii'):
            m.proposals('// é\n',{})

    def test_bad_budget_refused(self):
        for n in (0,9):
            with self.assertRaisesRegex(ValueError,'variant_budget'):m.proposals('',{},n)


if __name__=='__main__':unittest.main()

"""Synthetic parser/type controls; compilation is separate from matching credit."""
import tempfile
import json
import time
from pathlib import Path
import unittest
from unittest.mock import patch
from rapid.packets import PIN
from workers.deepseek_packet import atomic,sha
from rapid_object.ghidra_compile_fix import receiver_spacing,split_parameters,ast_casts,bit_preserving_cast,repair,verify_baseline,cached_result,summarize,run_sweep,evaluate


def record(draft):
    return {'rva':0x1000,'module_sha256':PIN,'image_base':0x400000,'status':'decompiled','draft':draft,'symbols':[{'kind':'function','token':'FUN_00401000','name':'FUN_00401000','rva':0x1000,'original_va':0x401000,'calling_convention_hypothesis':'unknown'}],'type_declarations_hypothesis':'typedef unsigned int uint;\ntypedef unsigned int undefined4;\ntypedef unsigned char undefined;'}


def assignment(source,left,right,lt,rt,operator='='):
    lo=source.index(left);ro=source.index(right,lo+len(left))
    def node(text,offset,typ):return {'kind':'DeclRefExpr','range':{'begin':{'offset':offset},'end':{'offset':offset,'tokLen':len(text)}},'type':{'qualType':typ}}
    return {'kind':'RecoveryExpr','inner':[node(left,lo,lt),node(right,ro,rt)]}


class CompileFixTests(unittest.TestCase):
    def test_receiver_boundary_retains_all_parameters_and_body(self):
        raw=record('void __thiscall FUN_00401000(int *param_1,int *param_2,uint param_3) { *param_1 = *param_2 + param_3; }')
        fixed,changes=receiver_spacing(raw);self.assertEqual(len(changes),1);self.assertIn('(int * param_1,int *param_2,uint param_3)',fixed['draft']);self.assertEqual(raw['draft'].partition('{')[2],fixed['draft'].partition('{')[2]);self.assertIn('int *param_1,',raw['draft'])
        with tempfile.TemporaryDirectory() as tmp,patch('rapid_object.ghidra_compile_fix.shutil.which',return_value=None):
            result=repair(raw,Path(tmp).resolve());self.assertEqual(result['status'],'source_ready');self.assertIn('fn_00001000(int *param_2,uint param_3)',result['source']);self.assertIn('((int *)this)',result['source']);self.assertNotIn('int *param_1,int',result['source'])
    def test_top_level_parameter_split_handles_function_pointer(self):
        self.assertEqual(split_parameters('int *p,void (*cb)(int,int),uint a[3]'),['int *p','void (*cb)(int,int)','uint a[3]'])
        with self.assertRaises(ValueError):split_parameters('int (*p')
    def test_scalar_receiver_and_nonreceiver_unchanged(self):
        for raw in (record('void __thiscall FUN_00401000(int p,int q) { }'),record('void FUN_00401000(int *p) { }')):self.assertEqual(receiver_spacing(raw)[1],[])
    def test_native_pointer_assignment_cast_keeps_entire_rhs(self):
        source='destination = address + count;';ast=assignment(source,'destination','address + count','unsigned int','int *')
        fixed,edits=ast_casts(source,ast);self.assertEqual(fixed,'destination = (unsigned int)(address + count);');self.assertEqual(len(edits),1)
    def test_object_pointer_signedness_and_void_pointer_are_explicit(self):
        self.assertTrue(bit_preserving_cast('int *','unsigned int *',{}));self.assertTrue(bit_preserving_cast('unsigned int *','void *',{}));self.assertTrue(bit_preserving_cast('void *','unsigned int',{}))
    def test_no_narrowing_unknown_function_pointer_or_qualifier_drop(self):
        for lhs,rhs in [('unsigned char','int *'),('unsigned __int64','int *'),('bool','int *'),('unsigned int','int * __ptr64'),('<dependent type>','int *'),('code *','int *'),('char *','const char *'),('int *','volatile int *')]:
            self.assertFalse(bit_preserving_cast(lhs,rhs,{'code':'unsigned int (...)'}),(lhs,rhs))
    def test_record_pointer_casts_cannot_adjust_base_addresses(self):
        source='d = b;';ast=assignment(source,'d','b','D *','B *')
        self.assertEqual(ast_casts(source,ast),(source,[]))
        for lhs,rhs in [('struct D *','struct B *'),('D *','B *'),('D *','void *')]:
            self.assertFalse(bit_preserving_cast(lhs,rhs,{}))
        self.assertFalse(bit_preserving_cast('DerivedPtr','BasePtr',{'DerivedPtr':'D *','BasePtr':'B *'}))

    def test_alias_width_resolved_without_guessing_small_undefined(self):
        self.assertTrue(bit_preserving_cast('undefined4','int *',{'undefined4':'unsigned int'}));self.assertFalse(bit_preserving_cast('undefined','int *',{'undefined':'unsigned char'}))
    def test_nonassignment_and_macro_locations_not_rewritten(self):
        source='destination == address;';ast=assignment(source,'destination','address','unsigned int','int *');self.assertEqual(ast_casts(source,ast),(source,[]));ast['inner'][1]['range']['begin']={'spellingLoc':{'offset':15}};self.assertEqual(ast_casts(source,ast),(source,[]))
    def test_unknown_state_and_helpers_stay_no_source(self):
        for body in ('return in_EAX;','return MYSTERY4(7);'):
            raw=record('unsigned int FUN_00401000(void) { '+body+' }')
            with tempfile.TemporaryDirectory() as tmp:result=repair(raw,Path(tmp).resolve());self.assertEqual(result['status'],'no_source');self.assertIsNone(result['source']);self.assertEqual(result['raw_draft'],raw['draft'])
    def test_utf8_ast_byte_offsets_preserve_source_prefix(self):
        source='/* é */ destination = address;';raw=source.encode();left=raw.index(b'destination');right=raw.index(b'address');ast={'kind':'RecoveryExpr','inner':[{'range':{'begin':{'offset':left},'end':{'offset':left,'tokLen':11}},'type':{'qualType':'unsigned int'}},{'range':{'begin':{'offset':right},'end':{'offset':right,'tokLen':7}},'type':{'qualType':'int *'}}]};fixed,_=ast_casts(source,ast);self.assertEqual(fixed,'/* é */ destination = (unsigned int)(address);')

class CompileFixRuntimeTests(unittest.TestCase):
    def test_baseline_hash_mismatch_stops_before_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp).resolve()/'raw.json';atomic(path,{'module_sha256':PIN,'rva':1});case={'rva':1,'raw_export':str(path),'raw_export_sha256':sha(path.read_bytes())};verify_baseline(case);path.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'baseline_binding_changed'):verify_baseline(case)
    def test_fresh_wrong_original_identity_is_refused_before_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw=Path(tmp).resolve()/'raw.json';atomic(raw,{'module_sha256':PIN,'rva':2});case={'rva':1,'raw_export':str(raw),'raw_export_sha256':sha(raw.read_bytes())}
            with patch('rapid_object.build.build_and_compare') as build:
                with self.assertRaisesRegex(ValueError,'baseline_original_identity_changed'):evaluate(case,Path(tmp)/'cases')
                build.assert_not_called()

    def test_resume_checks_source_object_compiler_and_comparator(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();build=root/'build';build.mkdir();source=root/'candidate.cpp';source.write_bytes(b'fixed');raw=root/'raw.json';original={'module_sha256':PIN,'rva':1,'original_va':0x400001,'ranges':[{'start_rva':1,'end_rva_inclusive':30}],'bytes_sha256':'whole-original'};atomic(raw,original);obj=build/'candidate.obj';obj.write_bytes(b'object')
            case={'rva':1,'baseline_status':'compile_or_transport_error','raw_export':str(raw),'raw_export_sha256':sha(raw.read_bytes())};tools={'code_sha256':{'coff.py':'coff','compare.py':'compare'},'expected_cl_sha256':'cl'}
            result={'baseline':case,'tool_bindings':tools,'source':str(source),'source_sha256':sha(source.read_bytes()),'compile_success':True,'summary':str(build/'summary.json'),'matching_status':'nonmatch','build':{'compiler':{'sha256':'cl'}}};atomic(root/'result.json',result)
            report={'module_sha256':PIN,'source_sha256':result['source_sha256'],'object_sha256':sha(obj.read_bytes()),'implementation_sha256':tools['code_sha256'],'compiler':{'sha256':'cl'},'requested':{'1':{k:original[k] for k in ('original_va','ranges','bytes_sha256')}},'functions':[{'rva':1,'status':'nonmatch'}]};atomic(build/'summary.json',report)
            with patch('rapid_object.ghidra_compile_fix.tool_bindings',return_value=tools):
                self.assertTrue(cached_result(case,root)['compile_success']);source.write_bytes(b'changed')
                with self.assertRaisesRegex(ValueError,'source_binding'):cached_result(case,root)
                source.write_bytes(b'fixed');obj.write_bytes(b'changed')
                with self.assertRaisesRegex(ValueError,'comparison_binding'):cached_result(case,root)
                obj.write_bytes(b'object');report['requested']['1']['ranges']=[{'start_rva':1,'end_rva_inclusive':1}];atomic(build/'summary.json',report)
                with self.assertRaisesRegex(ValueError,'original_request_binding'):cached_result(case,root)
                report['requested']['1']['ranges']=original['ranges'];report['compiler']={'sha256':'different'};atomic(build/'summary.json',report)
                with self.assertRaisesRegex(ValueError,'comparator_or_compiler_binding'):cached_result(case,root)
                report['compiler']={'sha256':'cl'};report['implementation_sha256']={};atomic(build/'summary.json',report)
                with self.assertRaisesRegex(ValueError,'comparator_or_compiler_binding'):cached_result(case,root)
    def test_exit_zero_without_bound_object_is_not_compile_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();raw=root/'raw.json';data=record('unsigned int FUN_00401000(void) { return 1; }');data.update(original_va=0x401000,ranges=[{'start_rva':0x1000,'end_rva_inclusive':0x1000}],bytes_sha256='original');atomic(raw,data)
            case={'rva':0x1000,'category':'receiver','baseline_status':'no_source','raw_export':str(raw),'raw_export_sha256':sha(raw.read_bytes()),'source':None};repo=root/'repo';(repo/'local/rapid-object').mkdir(parents=True)
            with patch('rapid_object.ghidra_compile_fix.REPO',repo),patch('rapid_object.ghidra_compile_fix.tool_bindings',return_value={'expected_cl_sha256':'cl'}),patch('rapid_object.ghidra_compile_fix.shutil.which',return_value=None),patch('rapid_object.build.build_and_compare',return_value={'build':{'exit_code':0},'error':'missing_object','functions':[{'rva':0x1000,'status':'exact_object_match'}]}):
                result=evaluate(case,root/'cases');self.assertFalse(result['compile_success']);self.assertIsNone(result['matching_status'])

    def test_matching_regression_count_is_separate_from_compilation(self):
        row={'category':'control','compile_success':True,'baseline_status':'exact_object_match','matching_status':'nonmatch'};summary=summarize([row],time.time());self.assertEqual(summary['control_compile_regressions'],0);self.assertEqual(summary['control_match_regressions'],1)
    def test_paused_sweep_does_not_evaluate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();atomic(root/'sweep-plan.json',{'cases':[{'rva':1}],'baseline':str(root)});(root/'sweep.paused').write_text('paused')
            with patch('rapid_object.ghidra_compile_fix.evaluate') as evaluate:
                result=run_sweep(root);evaluate.assert_not_called();self.assertTrue(result['paused'])
    def test_follow_discovers_later_completed_chunk_and_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();baseline=root/'baseline';baseline.mkdir();plan={'cases':[{'rva':1}],'baseline':str(baseline)};atomic(root/'sweep-plan.json',plan);atomic(baseline/'compile-summary.json',{'chunks_complete':1,'completed':False})
            def refresh(*args,**kwargs):
                state=json.loads((baseline/'compile-summary.json').read_text());atomic(root/'sweep-plan.json',{**plan,'cases':[{'rva':1}]+([{'rva':2}] if state['completed'] else [])})
            def finish_wait(*args):atomic(baseline/'compile-summary.json',{'chunks_complete':2,'completed':True})
            def evaluate(case,*args,**kwargs):return {'rva':case['rva'],'category':'receiver','compile_success':True,'baseline_status':'compile_or_transport_error','matching_status':'nonmatch'}
            with patch('rapid_object.ghidra_compile_fix.prepare_sweep',side_effect=refresh),patch('rapid_object.ghidra_compile_fix.time.sleep',side_effect=finish_wait),patch('rapid_object.ghidra_compile_fix.evaluate',side_effect=evaluate) as build:
                result=run_sweep(root,follow=True);self.assertEqual(build.call_count,2);self.assertTrue(result['completed']);self.assertTrue(result['baseline_completed'])

if __name__=='__main__':unittest.main()

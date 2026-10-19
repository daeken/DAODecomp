"""Generic omitted-declaration controls; no game-function fixtures."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from rapid_object import ghidra_declaration_fix as decl
from rapid.packets import PIN
from workers.deepseek_packet import sha


def scalar(name='void',length=0,cls='VoidDataType'):
    return {'name':name,'length':length,'class':'ghidra.program.model.data.'+cls}


def graph():
    return {'function_types':[{'name':'_func_7','class':'ghidra.program.database.data.FunctionDefinitionDB','cc':'__cdecl','varargs':False,'return':scalar(),'arguments':[]}]}


class Declarations(unittest.TestCase):
    def test_metadata_callback_restored_and_every_existing_byte_preserved(self):
        source='extern "C" int f(_func_7 *p);\nint body() { return f((_func_7 *)123); }'
        out,changes=decl.restore_declarations(source,graph())
        self.assertEqual(out,'typedef void __cdecl _func_7(void);\n'+source)
        self.assertTrue(changes[0]['hypothesis']);self.assertEqual(len(changes),1)
    def test_no_actual_reference_changes_nothing(self):
        for source in ('int f(){return 7;}','// _func_7\nint f(){return 7;}','// continued \\\n_func_7\nint f(){return 7;}','const char*s="_func_7";'):
            self.assertEqual(decl.restore_declarations(source,graph()),(source,[]))
    def test_missing_metadata_unknown_cc_and_ambiguous_signatures_refused(self):
        for mutate in (lambda g:g['function_types'].clear(),lambda g:g['function_types'][0].update(cc='unknown'),lambda g:g['function_types'].append({**g['function_types'][0],'cc':'__stdcall'})):
            g=graph();mutate(g)
            with self.assertRaises(ValueError):decl.restore_declarations('_func_7 *p;',g)
    def test_duplicate_equivalent_metadata_is_not_ambiguous(self):
        g=graph();g['function_types'].append(copy.deepcopy(g['function_types'][0]));self.assertEqual(len(decl.restore_declarations('_func_7 *p;',g)[1]),1)
    def test_explicit_scalar_width_and_pointer_arguments(self):
        g=graph();g['function_types'][0].update(cc='__stdcall')
        g['function_types'][0]['arguments']=[scalar('int',4,'IntegerDataType'),{'class':'x.PointerDB','length':4,'pointee':scalar()}]
        self.assertEqual(decl.typedef_for('_func_7',g),'typedef void __stdcall _func_7(int, void *);')
    def test_width_record_null_pointer_or_nested_callback_not_fabricated(self):
        for typ in (scalar('int',2,'IntegerDataType'),scalar('int',4,'StructureDB'),{'class':'x.PointerDB','length':8,'pointee':scalar()},{'class':'x.PointerDB','length':4,'pointee':{}},graph()['function_types'][0]):
            g=graph();g['function_types'][0]['arguments']=[typ]
            with self.assertRaises(ValueError):decl.typedef_for('_func_7',g)
    def test_no_unknown_or_void_argument_list_becomes_empty(self):
        for args in (None,[scalar()]):
            g=graph();g['function_types'][0]['arguments']=args
            with self.assertRaises(ValueError):decl.typedef_for('_func_7',g)
    def test_variadic_requires_explicit_cdecl_and_fixed_argument(self):
        g=graph();g['function_types'][0]['varargs']=True
        with self.assertRaises(ValueError):decl.typedef_for('_func_7',g)
        g['function_types'][0]['arguments']=[scalar('int',4,'IntegerDataType')]
        self.assertIn('(int, ...)',decl.typedef_for('_func_7',g));g['function_types'][0]['cc']='__stdcall'
        with self.assertRaises(ValueError):decl.typedef_for('_func_7',g)
    def test_existing_definition_and_macro_not_overridden(self):
        for source in ('typedef int _func_7; _func_7 *p;','struct _func_7; _func_7 *p;','#define _func_7 int\n_func_7 *p;'):
            with self.assertRaisesRegex(ValueError,'already_declared'):decl.restore_declarations(source,graph())
    def test_symbol_addresses_preserve_rva_namespace(self):
        self.assertEqual(decl.symbol_addresses({'symbols':[{'kind':'function','original_va':0x401000}]}),{'fn_00001000':{'original_va':0x401000,'kind':'function'}})
        with self.assertRaises(ValueError):decl.symbol_addresses({'symbols':[{'kind':'function','original_va':0x1000}]})


class BuildBindings(unittest.TestCase):
    def run_fake(self,tmp,mutate_source=False,compiler='expected',object_exists=True):
        root=Path(tmp);source=root/'baseline.cpp';source.write_text('_func_7 *p;');raw=root/'raw.json';raw.write_text(json.dumps({'rva':0x1000,'module_sha256':PIN,'original_va':0x401000,'ranges':[],'bytes_sha256':'original','symbols':[],'analysis_revision':{'project_store_sha256':'project'}}));baseline=root/'baseline.json';baseline.write_text('{}')
        case={'rva':0x1000,'category':'callback','baseline_status':'compile_failure','source':str(source),'source_sha256':sha(source.read_bytes()),'raw_export':str(raw),'raw_export_sha256':sha(raw.read_bytes()),'baseline_report':str(baseline),'baseline_report_sha256':sha(baseline.read_bytes())}
        current={'compile_fix':{'expected_cl_sha256':'expected','code_sha256':{'coff.py':'coff','compare.py':'compare'}}}
        def build(src,out,requested,symbols):
            out.mkdir();digest=sha(src.read_bytes());obj=b'object'
            if object_exists:(out/'candidate.obj').write_bytes(obj)
            receipt={'exit_code':0,'compiler':{'sha256':compiler},'source_sha256':digest,'object_sha256':sha(obj),'module_sha256':PIN};report={'build':receipt,'module_sha256':PIN,'source_sha256':digest,'object_sha256':sha(obj),'compiler':receipt['compiler'],'requested':{str(k):v for k,v in requested.items()},'functions':[{'rva':0x1000,'status':'exact_object_match'}],'implementation_sha256':{'coff.py':'coff','compare.py':'compare'}}
            (out/'run.json').write_text(json.dumps(receipt));(out/'summary.json').write_text(json.dumps(report))
            if mutate_source:src.write_text('changed')
            return report
        with patch.object(decl,'load_graph',return_value=(graph(),{'project_store_sha256_before':'project'})),patch.object(decl,'bindings',return_value=current),patch('rapid_object.build.build_and_compare',side_effect=build):
            result=decl.evaluate(case,root)
            return result,case,current
    def test_good_object_is_required_and_wrong_compiler_source_never_match(self):
        for args in ({'mutate_source':True},{'compiler':'wrong'},{'object_exists':False}):
            with tempfile.TemporaryDirectory() as tmp:
                result,_,_=self.run_fake(tmp,**args);self.assertFalse(result['compile_success']);self.assertIsNone(result['matching_status'])
    def test_cached_full_range_compiler_and_actual_object_verified(self):
        for field in ('requested','compiler','object'):
            with tempfile.TemporaryDirectory() as tmp:
                result,case,current=self.run_fake(tmp);self.assertTrue(result['compile_success']);out=Path(result['summary']);report=json.loads(out.read_text())
                if field=='requested':report['requested'][str(case['rva'])]['bytes_sha256']='prefix'
                elif field=='compiler':report['compiler']['sha256']='wrong'
                else:(out.parent/'candidate.obj').write_bytes(b'changed')
                out.write_text(json.dumps(report))
                with patch.object(decl,'load_graph',return_value=(graph(),{'project_store_sha256_before':'project'})),patch.object(decl,'bindings',return_value=current),self.assertRaises(ValueError):decl.evaluate(case,Path(tmp))
    def test_cached_source_and_recipe_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            result,case,current=self.run_fake(tmp);(Path(tmp)/'pilot/00001000/candidate.cpp').write_text('changed')
            with patch.object(decl,'load_graph',return_value=(graph(),{'project_store_sha256_before':'project'})),patch.object(decl,'bindings',return_value=current),self.assertRaises(ValueError):decl.evaluate(case,Path(tmp))
    def test_raw_project_mismatch_refuses_before_any_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            result,case,current=self.run_fake(tmp);raw=Path(case['raw_export']);value=json.loads(raw.read_text());value['analysis_revision']['project_store_sha256']='different';raw.write_text(json.dumps(value));case['raw_export_sha256']=sha(raw.read_bytes())
            with patch.object(decl,'load_graph',return_value=(graph(),{'project_store_sha256_before':'project'})),patch.object(decl,'bindings',return_value=current),patch('rapid_object.build.build_and_compare') as build,self.assertRaisesRegex(ValueError,'source_project_revision'):
                decl.evaluate(case,Path(tmp))
            build.assert_not_called()
    def test_byte_identical_recipe_reconciliation_preserves_historical_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            result,case,current=self.run_fake(tmp);path=Path(result['summary']).parent.parent/'result.json';historic=json.loads(path.read_text());historic['tool_bindings']['declaration_fix_sha256']='old';path.write_text(json.dumps(historic));current={**current,'declaration_fix_sha256':'new'}
            with patch.object(decl,'load_graph',return_value=(graph(),{'project_store_sha256_before':'project'})),patch.object(decl,'bindings',return_value=current):verified=decl.evaluate(case,Path(tmp))
            self.assertEqual(verified['tool_bindings']['declaration_fix_sha256'],'old');self.assertEqual(verified['resume_verified_tool_bindings']['declaration_fix_sha256'],'new');self.assertEqual(json.loads(path.read_text()),historic)
    def test_type_graph_cache_binds_content_script_target_and_persistent_revision(self):
        for bad in ('content','script','target','revision'):
            with tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);folder=root/'types';folder.mkdir();value={**graph(),'module_sha256':PIN,'image_base':0x400000,'language':'x86:LE:32:default','compiler_spec':'windows'}
                if bad=='target':value['module_sha256']='wrong'
                path=folder/'graph.json';path.write_text(json.dumps(value));receipt={'graph':str(path),'graph_sha256':sha(path.read_bytes()),'script_sha256':sha(decl.JAVA.encode()),'project_store_sha256_before':'project','project_store_sha256_after':'project'}
                if bad=='content':path.write_text('{}')
                if bad=='script':receipt['script_sha256']='wrong'
                if bad=='revision':receipt['project_store_sha256_after']='different'
                (folder/'receipt.json').write_text(json.dumps(receipt))
                with self.assertRaises(ValueError):decl.load_graph(root)
    def test_no_provider_code_and_no_live_module_write(self):
        self.assertNotIn('propose(',Path(decl.__file__).read_text());self.assertIn('-readOnly',decl.JAVA if '-readOnly' in decl.JAVA else Path(decl.__file__).read_text())


if __name__=='__main__':unittest.main()

"""Generic Ghidra draft conversion controls; no game/decompiler/VM required."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from workers.deepseek_packet import atomic
from rapid.packets import PIN
from rapid_object.ghidra_seed import FORCED,representative_sample,replace_identifiers,convert_export,convert_sample,canonicalize_draft,measure_sample,project_fingerprint


def draft(text='unsigned int FUN_00401000(void) { return 1; }',symbols=None):
    return {'rva':0x1000,'module_sha256':PIN,'image_base':0x400000,'status':'decompiled','draft':text,'symbols':symbols or [{'kind':'function','token':'FUN_00401000','name':'FUN_00401000','rva':0x1000,'original_va':0x401000,'calling_convention_hypothesis':'unknown'}],'type_declarations_hypothesis':''}


class GhidraSeedTests(unittest.TestCase):
    def test_representative_sample_is_stable_and_includes_examples(self):
        funcs=[{'rva':r,'body_bytes':(r%5+1)*40,'direct_calls':list(range(r%3))} for r in range(300)]+[{'rva':r,'body_bytes':6,'direct_calls':[]} for r in FORCED]
        a=representative_sample(funcs,200);b=representative_sample(list(reversed(funcs)),200)
        self.assertEqual(a,b);self.assertEqual(len(set(a)),200);self.assertTrue(set(FORCED).issubset(a))
        self.assertEqual(len(representative_sample(funcs,1000)),len(funcs))
    def test_lexical_names_do_not_change_strings_or_comments(self):
        text='DAT_00401000 + otherDAT_00401000; "DAT_00401000"; /* DAT_00401000 */ // DAT_00401000\n'
        self.assertEqual(replace_identifiers(text,{'DAT_00401000':'g_00001000'}),'g_00001000 + otherDAT_00401000; "DAT_00401000"; /* DAT_00401000 */ // DAT_00401000\n')
    def test_backslash_continued_comments_stay_verbatim(self):
        text='// ignored '+chr(92)+'\nDAT_00402000\nDAT_00402000;\n'
        mapping={'DAT_00402000':'g_00002000'}
        self.assertEqual(replace_identifiers(text,mapping),'// ignored '+chr(92)+'\nDAT_00402000\ng_00002000;\n')
        record=draft(text+'unsigned int FUN_00401000(void) { return 1; }');record['symbols'].append({'kind':'global','token':'DAT_00402000','original_va':0x402000,'type_hypothesis':'unsigned int','size':4})
        self.assertTrue(canonicalize_draft(record)['canonical_draft'].startswith('// ignored '+chr(92)+'\nDAT_00402000\ng_00002000;'))
        self.assertEqual(replace_identifiers('$DAT_00402000',mapping),'$DAT_00402000')

    def test_unsupported_draft_still_exposes_canonical_names(self):
        record=draft('unsigned int FUN_00401000(void) { return in_EAX + DAT_00402000; }');record['symbols'].append({'kind':'global','token':'DAT_00402000','original_va':0x402000,'type_hypothesis':'unsigned int','size':4})
        result=convert_export(record);self.assertEqual(result['status'],'no_source');self.assertIn('fn_00001000',result['canonical_draft']);self.assertIn('g_00002000',result['canonical_draft']);self.assertEqual(result['draft'],record['draft']);self.assertEqual(result['identifier_map']['DAT_00402000'],'g_00002000')

    def test_rva_global_mapping_and_extern_no_definition(self):
        record=draft('unsigned int FUN_00401000(void) { return DAT_00402000; }');record['symbols'].append({'kind':'global','token':'DAT_00402000','original_va':0x402000,'type_hypothesis':'unsigned int','size':4})
        result=convert_export(record);self.assertEqual(result['status'],'converted');self.assertIn('extern "C" unsigned int g_00002000;',result['source']);self.assertNotIn('g_00402000',result['source']);self.assertEqual(result['symbol_addresses']['g_00002000']['original_va'],0x402000)
    def test_unknown_calls_are_declarations_not_success_stubs(self):
        record=draft('unsigned int FUN_00401000(void) { return FUN_00403000(7); }');record['symbols'].append({'kind':'function','token':'FUN_00403000','name':'FUN_00403000','rva':0x3000,'original_va':0x403000,'calling_convention_hypothesis':'unknown','prototype_hypothesis':'undefined FUN_00403000()'})
        result=convert_export(record);self.assertEqual(result['status'],'converted');self.assertIn('fn_00003000(...);',result['source']);self.assertEqual(result['source'].count('{'),1);self.assertEqual(result['signature_status'],'hypothesis')
    def test_register_unknown_and_helpers_keep_raw_draft(self):
        for body,reason in [('return in_EAX;','unmodeled_register_or_stack_input'),('return UNKNOWN8(1);','unsupported_helper:UNKNOWN8')]:
            record=draft('unsigned int FUN_00401000(void) {'+body+'}');result=convert_export(record);self.assertEqual(result['status'],'no_source');self.assertEqual(result['draft'],record['draft']);self.assertIsNone(result['source']);self.assertIn(reason,result['diagnostics'])
    def test_concat_is_defined_unsigned_bit_operation(self):
        result=convert_export(draft('unsigned int FUN_00401000(unsigned int x) { return CONCAT31(x,1); }'))
        self.assertEqual(result['status'],'converted');self.assertIn('a & 0xffffffui64',result['source']);self.assertIn('b & 0xffui64',result['source']);self.assertIn('<< 8',result['source'])
    def test_native_thiscall_method_has_no_wrapper(self):
        result=convert_export(draft('unsigned int __thiscall FUN_00401000(int param_1,int param_2) { return *(unsigned int *)(param_1+param_2); }'))
        self.assertEqual(result['status'],'converted');self.assertIn('Seed_00001000::fn_00001000(int param_2)',result['source']);self.assertIn('((int)this)+param_2',result['source']);self.assertEqual(result['source'].count('// FUNCTION:'),1)
    def test_extended_float_and_bad_identity_do_not_invent_source(self):
        record=draft('float10 FUN_00401000(void) { return 1; }');self.assertEqual(convert_export(record)['status'],'no_source');record['module_sha256']='wrong';self.assertEqual(convert_export(record)['diagnostics'],['module_pin'])
    def test_bool_builtin_typedef_removed_but_other_types_retained(self):
        record=draft();record['type_declarations_hypothesis']='typedef unsigned char bool;\ntypedef unsigned char byte;\ntypedef short wchar_t;\ntypedef long long longlong;'
        source=convert_export(record)['source'];self.assertNotIn('char bool;',source);self.assertNotIn('short wchar_t;',source);self.assertIn('typedef unsigned char byte;',source);self.assertIn('typedef __int64 longlong;',source)
    def test_project_fingerprint_changes_with_saved_program_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);store=root/'idata/00/program.db';store.mkdir(parents=True);file=store/'db.1.gbf';file.write_bytes(b'first saved types')
            first=project_fingerprint(root);file.write_bytes(b'other saved types');self.assertNotEqual(project_fingerprint(root),first)

    def test_measurement_cannot_reuse_match_for_mutated_or_deleted_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();exports=root/'exports';exports.mkdir();atomic(root/'selection.json',{'rvas':[0x1000]});atomic(root/'export-receipt.json',{'folder':str(exports)})
            record=draft();record.update(original_va=0x401000,ranges=[{'start_rva':0x1000,'end_rva_inclusive':0x1000}],bytes_sha256='original-range');atomic(exports/'00001000.json',record);receipt=convert_sample(root);source=Path(receipt['folder'])/'00001000/candidate.cpp'
            repo=root/'repo';(repo/'rapid_object').mkdir(parents=True);(repo/'local/rapid-object').mkdir(parents=True)
            for name in ('build.py','coff.py','compare.py'):(repo/'rapid_object'/name).write_text(name)
            def build(path,output,requested,registry):
                output.mkdir(parents=True);return {'functions':[{'rva':0x1000,'status':'exact_object_match','diagnostics':[]}],'build':{'elapsed_seconds':0}}
            with patch('rapid_object.ghidra_seed.REPO',repo),patch('rapid_object.build.build_and_compare',side_effect=build) as compiler:
                self.assertEqual(measure_sample(root)['counts']['exact_object_match'],1);self.assertEqual(compiler.call_count,1)
                source.write_text('different C++');result=measure_sample(root);self.assertEqual(result['counts']['cache_integrity_error'],1);self.assertEqual(compiler.call_count,1)
                source.unlink();result=measure_sample(root);self.assertEqual(result['counts']['cache_integrity_error'],1);self.assertEqual(compiler.call_count,1)

    def test_success_and_failure_conversion_cache_preserve_draft(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();exports=root/'exports';exports.mkdir();atomic(root/'selection.json',{'rvas':[0x1000]});atomic(root/'export-receipt.json',{'folder':str(exports)})
            record=draft();atomic(exports/'00001000.json',record);receipt=convert_sample(root);folder=Path(receipt['folder'])/'00001000';first=(folder/'candidate.cpp').read_bytes();self.assertEqual(convert_sample(root)['counts'],{'converted':1});self.assertEqual((folder/'candidate.cpp').read_bytes(),first)
            (folder/'candidate.cpp').write_text('mutated emitted source');convert_sample(root);self.assertEqual((folder/'candidate.cpp').read_bytes(),first)
            self.assertEqual(len(list(folder.glob('candidate-unbound-*.cpp'))),1)
            (folder/'candidate.cpp').unlink();convert_sample(root);self.assertEqual((folder/'candidate.cpp').read_bytes(),first)
            cache=json.loads((folder/'conversion.json').read_text());cache['converter_sha256']='wrong';atomic(folder/'conversion.json',cache);convert_sample(root);self.assertNotEqual(json.loads((folder/'conversion.json').read_text())['converter_sha256'],'wrong')
            record=draft('unsigned int FUN_00401000(void) { return in_EAX; }');atomic(exports/'00001000.json',record);second=convert_sample(root);self.assertEqual(second['counts'],{'no_source':1});second_folder=Path(second['folder'])/'00001000';self.assertNotEqual(folder,second_folder);self.assertFalse((second_folder/'candidate.cpp').exists());self.assertEqual((folder/'candidate.cpp').read_bytes(),first);cached=json.loads((second_folder/'conversion.json').read_text());self.assertEqual(cached['draft'],record['draft']);self.assertIsNone(cached['source'])

if __name__=='__main__':unittest.main()

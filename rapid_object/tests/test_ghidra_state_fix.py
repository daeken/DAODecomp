"""Generic native-state lowering and immutable-result controls; no game fixtures."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from rapid.packets import PIN
from workers.deepseek_packet import atomic,sha
from rapid_object import ghidra_state_fix as state


class MemoryPE:
    def __init__(self,data):self.data=data
    def get_data(self,rva,size):return self.data[rva-0x1000:rva-0x1000+size]


def record(draft=None,data=bytes.fromhex('64a10000000064a30000000064a300000000c3')):
    return {'rva':0x1000,'original_va':0x401000,'module_sha256':PIN,'image_base':0x400000,'status':'decompiled','ranges':[{'start_rva':0x1000,'end_rva_inclusive':0x1000+len(data)-1}],'bytes_sha256':sha(data),'draft':draft or 'void FUN_00401000(void) {\n int *unaff_FS_OFFSET;\n int old;\n old = *unaff_FS_OFFSET;\n *unaff_FS_OFFSET = 7;\n *unaff_FS_OFFSET = old;\n}', 'symbols':[{'kind':'function','rva':0x1000,'original_va':0x401000,'token':'FUN_00401000','name':'FUN_00401000'}],'type_declarations_hypothesis':'typedef unsigned int uint; typedef unsigned int undefined4;'}


def evidence():return {'reads':1,'writes':2,'instructions':[]}


class LoweringTests(unittest.TestCase):
    def test_every_read_and_write_retained_as_real_intrinsic(self):
        raw=record();out,changes=state.lower_fs0(raw,evidence())
        self.assertIn('old = ((int)__readfsdword(0));',out['draft']);self.assertIn('__writefsdword(0,(unsigned long)(7));',out['draft']);self.assertIn('__writefsdword(0,(unsigned long)(old));',out['draft']);self.assertEqual(len(changes),4);self.assertIn('int *unaff_FS_OFFSET;',raw['draft']);self.assertIn('#pragma intrinsic(__writefsdword)',out['type_declarations_hypothesis'])
    def test_byte_evidence_checks_full_hash_and_exact_fs_width_offset_direction(self):
        raw=record();data=bytes.fromhex('64a10000000064a30000000064a300000000c3');ev=state.instruction_evidence(raw,MemoryPE(data));self.assertEqual((ev['reads'],ev['writes']),(1,2));self.assertEqual(len(ev['instructions']),3)
        for data in (bytes.fromhex('64a104000000c3'),bytes.fromhex('6466a100000000c3'),bytes.fromhex('648b00c3'),bytes.fromhex('64ff0500000000c3')):
            bad=record(data=data)
            with self.assertRaisesRegex(ValueError,'unsupported_original_fs_access'):state.instruction_evidence(bad,MemoryPE(data))
        bad=record();bad['bytes_sha256']='wrong'
        with self.assertRaisesRegex(ValueError,'original_range_hash'):state.instruction_evidence(bad,MemoryPE(bytes.fromhex('64a10000000064a30000000064a300000000c3')))
    def test_read_preserves_signed_scalar_type_and_rejects_unproven_width(self):
        out,_=state.lower_fs0(record(),evidence());self.assertIn('((int)__readfsdword(0))',out['draft'])
        raw=record();raw['draft']=raw['draft'].replace('int *unaff_FS_OFFSET','uint *unaff_FS_OFFSET');raw['type_declarations_hypothesis']='typedef unsigned short uint;'
        with self.assertRaisesRegex(ValueError,'unsupported_fs_value_type'):state.lower_fs0(raw,evidence())
        for types in ('// typedef unsigned int uint;\ntypedef unsigned short uint;', 'typedef unsigned int uint; typedef unsigned short uint;', '/* typedef unsigned int uint; */', 'typedef unsigned int uint; typedef unsigned int uint;'):
            raw['type_declarations_hypothesis']=types
            with self.assertRaisesRegex(ValueError,'unsupported_fs_value_type'):state.lower_fs0(raw,evidence())

    def test_incomplete_decode_never_lowered(self):
        raw=record(data=b'\x64')
        with self.assertRaisesRegex(ValueError,'incomplete_original_decode'):state.instruction_evidence(raw,MemoryPE(b'\x64'))
    def test_other_incoming_or_call_state_stays_unknown(self):
        for token in ('in_EAX','in_ECX','extraout_EDX','unaff_retaddr','in_stack_00000004'):
            raw=record();raw['draft']+='\n// '+token;self.assertEqual(len(state.lower_fs0(raw,evidence())[1]),4)
            raw['draft']+='\nint use = '+token+';'
            with self.assertRaisesRegex(ValueError,'other_or_missing'):state.lower_fs0(raw,evidence())
    def test_mismatched_static_access_counts_stay_unknown(self):
        with self.assertRaisesRegex(ValueError,'count_mismatch'):state.lower_fs0(record(),{'reads':2,'writes':2})
    def test_scalar_base_alias_nonzero_offset_and_compound_use_refused(self):
        for replace in ('old = (int)unaff_FS_OFFSET;','old = unaff_FS_OFFSET[1];','old = *(unaff_FS_OFFSET + 1);','*unaff_FS_OFFSET += 1;','*unaff_FS_OFFSET = old = 1;'):
            raw=record();raw['draft']=raw['draft'].replace('old = *unaff_FS_OFFSET;',replace)
            with self.assertRaises(ValueError):state.lower_fs0(raw,evidence())
    def test_macro_and_comments_not_rewritten_into_state(self):
        raw=record();raw['draft']=raw['draft'].replace('int old;','int old;\n // *unaff_FS_OFFSET = 99;\n const char *s="*unaff_FS_OFFSET";')
        out,_=state.lower_fs0(raw,evidence());self.assertIn('// *unaff_FS_OFFSET = 99;',out['draft']);self.assertIn('"*unaff_FS_OFFSET"',out['draft'])
    def test_unsupported_evidence_preserves_no_source_not_success(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(state,'instruction_evidence',side_effect=ValueError('unsupported_original_fs_access')):
            result=state.repair(record(),Path(tmp).resolve());self.assertEqual(result['status'],'no_source');self.assertIsNone(result['source']);self.assertEqual(result['diagnostics'],['unsupported_original_fs_access'])
    def test_conversion_preserves_native_identity_and_no_success_stub(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=state.repair(record(),Path(tmp).resolve(),evidence=evidence());self.assertEqual(out['status'],'source_ready');self.assertIn('// FUNCTION: DAO 0x00401000',out['source']);self.assertIn('extern "C" unsigned long __readfsdword',out['source']);self.assertNotIn('return 0;',out['source'])


class StateRuntimeTests(unittest.TestCase):
    def test_pause_prevents_new_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();atomic(root/'sweep-plan.json',{'cases':[{'rva':1}]});(root/'sweep.paused').write_text('paused')
            with patch.object(state,'evaluate') as evaluate:
                self.assertEqual(state.run(root,sweep=True)['measured'],0);evaluate.assert_not_called()
    def test_source_cache_mutation_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();raw=root/'raw.json';atomic(raw,record());case={'rva':0x1000,'raw_export':str(raw),'raw_export_sha256':sha(raw.read_bytes()),'category':'fs0','baseline_status':'no_source'};folder=root/'pilot/00001000';folder.mkdir(parents=True);(folder/'candidate.cpp').write_text('changed');atomic(folder/'result.json',{'baseline':case,'tool_bindings':{'test':1},'source_sha256':sha(b'original'),'compile_success':False})
            with patch.object(state,'bindings',return_value={'test':1}):
                with self.assertRaisesRegex(ValueError,'state_cache_source_changed'):state.evaluate(case,root/'pilot')
    def test_cached_requested_artifacts_and_matching_status_stay_bound(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();raw=root/'raw.json';original=record();atomic(raw,original);case={'rva':0x1000,'raw_export':str(raw),'raw_export_sha256':sha(raw.read_bytes()),'category':'fs0','baseline_status':'no_source'};folder=root/'pilot/00001000';build=folder/'build';build.mkdir(parents=True);(folder/'candidate.cpp').write_bytes(b'source');(build/'candidate.obj').write_bytes(b'object')
            tools={'state_fix_sha256':'code','compile_fix':{'expected_cl_sha256':'cl','code_sha256':{'coff.py':'coff','compare.py':'compare'}}};receipt={'compiler':{'sha256':'cl'},'source_sha256':sha(b'source'),'object_sha256':sha(b'object'),'module_sha256':PIN,'exit_code':0};functions=[{'rva':0x1000,'status':'nonmatch'}];report={'requested':{'4096':{k:original[k] for k in ('original_va','ranges','bytes_sha256')}},'source_sha256':sha(b'source'),'object_sha256':sha(b'object'),'module_sha256':PIN,'compiler':receipt['compiler'],'functions':functions,'implementation_sha256':tools['compile_fix']['code_sha256']};atomic(build/'summary.json',report)
            cached={'baseline':case,'tool_bindings':tools,'source_sha256':sha(b'source'),'compile_success':True,'summary':str(build/'summary.json'),'build':receipt,'comparison_functions':functions,'matching_status':'nonmatch'};atomic(folder/'result.json',cached);atomic(build/'run.json',receipt)
            with patch.object(state,'bindings',return_value=tools):
                self.assertEqual(state.evaluate(case,root/'pilot')['matching_status'],'nonmatch')
                cached['matching_status']='exact_object_match';atomic(folder/'result.json',cached)
                with self.assertRaisesRegex(ValueError,'state_cache_artifact_binding'):state.evaluate(case,root/'pilot')
                cached['matching_status']='nonmatch';atomic(folder/'result.json',cached);report['requested']['4096']['ranges']=[{'start_rva':0x1000,'end_rva_inclusive':0x1000}];atomic(build/'summary.json',report)
                with self.assertRaisesRegex(ValueError,'state_cache_artifact_binding'):state.evaluate(case,root/'pilot')

    def test_postbuild_source_mutation_cannot_credit_compile_or_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();(root/'local/rapid-object').mkdir(parents=True);raw=root/'raw.json';atomic(raw,record());case={'rva':0x1000,'raw_export':str(raw),'raw_export_sha256':sha(raw.read_bytes()),'category':'fs0','baseline_status':'no_source'}
            def proposal(case,folder):
                (folder/'candidate.cpp').write_bytes(b'original');return {'status':'source_ready','source':'original','source_sha256':sha(b'original'),'symbol_addresses':{}}
            def build(source,output,*args):
                source.write_bytes(b'changed during build');output.mkdir();(output/'candidate.obj').write_bytes(b'object');return {'build':{'exit_code':0,'compiler':{'sha256':'cl'},'source_sha256':sha(b'original'),'module_sha256':PIN,'object_sha256':sha(b'object')},'functions':[{'rva':0x1000,'status':'exact_object_match'}]}
            with patch.object(state,'REPO',root),patch.object(state,'bindings',return_value={'compile_fix':{'expected_cl_sha256':'cl'}}),patch.object(state,'proposal_for',side_effect=proposal),patch('rapid_object.build.build_and_compare',side_effect=build):
                result=state.evaluate(case,root/'pilot');self.assertFalse(result['compile_success']);self.assertIsNone(result['matching_status'])

    def test_fresh_wrong_identity_stops_before_repair_or_vm(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();raw=root/'raw.json';data=record();data['rva']=2;atomic(raw,data);case={'rva':1,'raw_export':str(raw),'raw_export_sha256':sha(raw.read_bytes())}
            with patch.object(state,'repair') as repair:
                with self.assertRaisesRegex(ValueError,'original_identity_changed'):state.evaluate(case,root/'pilot')
                repair.assert_not_called()


if __name__=='__main__':unittest.main()

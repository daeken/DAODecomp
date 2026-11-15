"""Whole-inventory isolation and artifact integrity; not game equivalence."""
import copy
import gzip
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from tools import recomp,recomp_bulk as bulk
from test_recomp import pe32
from tools.daodecomp.pe import fingerprint


class BulkStorageTests(unittest.TestCase):
    def setUp(self):
        temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup)
        self.root=Path(temporary.name);self.binary=self.root/'fixture.exe'
        self.binary.write_bytes(pe32(bytes.fromhex('9090c3')));self.image=self.binary.read_bytes();self.pe=fingerprint(self.binary)
        self.selection=dict(rva=0x1000,size=3,ranges=[dict(rva=0x1000,size=3)],annotations={},structures={},extra_entries=[])

    def shard(self, function):
        cache=self.root/'cache';key='a'*64;directory=cache/key;directory.mkdir(parents=True)
        (directory/'function.cpp').write_text('constructed source')
        with gzip.open(directory/'function.json.gz','wt') as stream:json.dump(function,stream)
        marker=dict(schema_version=1,artifact_key=key,binary_sha256=self.pe['sha256'],rva=0x1000,status='generated_only',behavioral_acceptance=False,
                    files={name:recomp.digest((directory/name).read_bytes()) for name in ('function.cpp','function.json.gz')})
        recomp.atomic_json(directory/'complete.json',marker)
        return cache,key

    def test_partial_inventory_coverage_and_indirect_paths_remain_visible(self):
        function=dict(rva=0x1000,size=3,instructions=[dict(rva=0x1000,bytes='90'),dict(rva=0x1002,bytes='c3')],
                      abi=dict(transfers=[dict(kind='Jmp',direct_target=None)]),unselected_call_continuations=[0x1003])
        cache,key=self.shard(function)
        bulk.load_shard(cache,key,self.pe['sha256'],0x1000)
        facts=bulk.coverage(cache,key,self.selection,self.image,self.pe)
        self.assertEqual((facts['covered_inventory_bytes'],facts['uncovered_inventory_bytes'],facts['indirect_jumps'],facts['unselected_call_continuations']),(2,1,1,1))
        function['instructions'][0]['bytes']='91'
        with gzip.open(cache/key/'function.json.gz','wt') as stream:json.dump(function,stream)
        with self.assertRaisesRegex(ValueError,'shard bytes changed'):bulk.load_shard(cache,key,self.pe['sha256'],0x1000)
        with self.assertRaisesRegex(ValueError,'differ from pinned'):bulk.coverage(cache,key,self.selection,self.image,self.pe)

    def test_function_cache_keys_preserve_independent_annotation_edits(self):
        first=copy.deepcopy(self.selection);second=copy.deepcopy(self.selection);second['rva']=0x2000
        key=lambda item:bulk.function_key('pipeline','fixture.exe',self.pe['sha256'],'',item)
        before=(key(first),key(second));first['annotations']={'origin:1':dict(name='counter',type='u32')}
        self.assertNotEqual(before[0],key(first));self.assertEqual(before[1],key(second))
        self.assertNotEqual(key(first),bulk.function_key('new-pipeline','fixture.exe',self.pe['sha256'],'',first))

    def test_overlapping_inventory_entries_are_reported_without_ownership_claims(self):
        entries=[dict(rva=0x1000,selection=self.selection),dict(rva=0x1001,selection=dict(ranges=[dict(rva=0x1001,size=2)]))]
        self.assertEqual(bulk.ownership_components(entries),[dict(start_rva=0x1000,end_rva=0x1003,functions=[0x1000,0x1001])])
        original=copy.deepcopy(self.selection)
        item=dict(rva=0x1000,body_ranges=[dict(start_rva=0x1000,end_rva_inclusive=0x1002)])
        self.assertEqual(bulk.selection_for(item,original,None,self.image,self.pe),self.selection)
        self.assertEqual(original,self.selection)

    def test_process_unknown_has_no_successful_body(self):
        cache=self.root/'attempt-unknown';item=dict(rva=0x1000,key='b'*64)
        bulk.write_unknown(cache,item,self.pe['sha256'],'deadline')
        marker=bulk.load_shard(cache,item['key'],self.pe['sha256'],0x1000)
        self.assertEqual(marker['status'],'interrupted_unknown');self.assertFalse((cache/item['key']/'function.cpp').exists())

    def test_error_groups_ignore_temporary_ids_and_addresses(self):
        self.assertEqual(bulk.normalize_error('failure at 0x1234 %81'),bulk.normalize_error('failure at 0x6789 %2'))
        self.assertEqual(bulk.normalize_error('Unsupported statement: (intrin.mov-seg-store %23 SS)'),
                         bulk.normalize_error('Unsupported statement: (intrin.mov-seg-store %1 SS)'))


class BulkBridgeTests(unittest.TestCase):
    def test_failed_middle_function_does_not_abort_neighbors_and_strict_mode_still_refuses(self):
        if not shutil.which('dotnet'):self.skipTest('requires .NET')
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);binary=root/'fixture.exe';binary.write_bytes(pe32(bytes.fromhex('8b44240483c001c3' '8b442404d1e8c3' 'b802000000c3')))
            output=root/'output';output.mkdir();pipeline,backend,descriptor=bulk.freeze_backend(output,False)
            selections=[dict(rva=0x1000,size=8,annotations={},structures={},ranges=[dict(rva=0x1000,size=8)],extra_entries=[]),
                        dict(rva=0x1008,size=7,annotations={'missing-origin':dict(name='counter',type=None)},structures={},ranges=[dict(rva=0x1008,size=7)],extra_entries=[]),
                        dict(rva=0x100f,size=6,annotations={},structures={},ranges=[dict(rva=0x100f,size=6)],extra_entries=[])]
            state=dict(binary=str(binary),binary_sha256=recomp.digest(binary.read_bytes()),module='fixture.exe',sharp_retro=str(recomp.ROOT.parent/'SharpRetro'),functions=selections)
            entries=[dict(rva=s['rva'],selection=s,key=bulk.function_key(pipeline,'fixture.exe',state['binary_sha256'],'',s)) for s in selections]
            cache=output/'cache';cache.mkdir();batch=output/'batch';batch.mkdir()
            bulk.generate_batch(entries,state,'',cache,backend,descriptor,batch,60,False)
            markers=[bulk.load_shard(cache,e['key'],state['binary_sha256'],e['rva']) for e in entries]
            self.assertEqual([m['status'] for m in markers],['generated_only','generation_failed','generated_only'])
            self.assertIn('Unmatched variable',markers[1]['error'])
            self.assertFalse((cache/entries[1]['key']/'function.cpp').exists())
            self.assertIn('fn_0000100f',(cache/entries[2]['key']/'function.cpp').read_text())
            with self.assertRaisesRegex(ValueError,'Unmatched variable'):recomp.export(state)

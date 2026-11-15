"""Synthetic SQLite controls; they do not describe or prove the game."""
import gzip
import json
from pathlib import Path
import tempfile
import unittest
import shutil
from unittest import mock

from tools import recomp, recomp_bulk
from tools import recomp_queries as q
from tools import recomp_workbench as w
from tests.test_recomp_workbench import fixture


class ProgramQueryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.comp=fixture(self.root,Path(shutil.which('clang++')).resolve())
        self.work=self.root/'work';w.initialize(self.comp,self.work)
        self.inputs=recomp.load(self.work/'baseline/inputs.json')
        self.generation=Path(self.inputs['generation_run']);self.cache=self.generation.parent.parent/'cache'
        for row in self.inputs['functions']:
            path=self.cache/row['artifact_key']/'function.json.gz'
            meta=json.loads(gzip.decompress(path.read_bytes()))
            if row['module']=='main':
                meta['abi']['transfers']=[{'rva':4097,'kind':'Call','direct_target':0x10001000}, {'rva':4098,'kind':'Call','direct_target':None,'import_slot':7}, {'rva':4099,'kind':'Jmp','direct_target':None}, {'rva':4100,'kind':'Call','direct_target':0x401000}]
                meta['structures']=[{'origin':'shape-A','fields':[{'origin':'field-X','offset':12,'width':4,'read':True,'write':False,'base_origin':'base-a','sites':[4097]}]}]
                meta['instructions'][0]['text']='mov eax, 0x00401000'
            path.write_bytes(gzip.compress(recomp.encoded(meta)))
            marker=recomp.load(self.cache/row['artifact_key']/'complete.json')
            marker['files']['function.json.gz']=recomp.digest(path.read_bytes())
            recomp.atomic_json(self.cache/row['artifact_key']/'complete.json',marker)
        # Fixture uses a fake compiler path, but index construction never invokes it.
        self.modules={role:dict(context={'binary_sha256':('a' if role=='main' else 'b')*64,'module':role+'.exe'},
            state={'image_base':0x400000 if role=='main' else 0x10000000},image=b'abc\0tail\0'+b'\0\0'+b'X'*32,
            pe={'size_of_image':64,'sections':[{'rva':0x1000,'file_offset':0,'file_size':48}]}) for role in ('main','umbra')}
        self.build()

    def build(self):
        with mock.patch.object(q,'_module_sources',return_value=self.modules): return q.build(self.work)

    def test_edges_distinguish_local_import_and_indirect(self):
        result=q.query(self.work,'callees',module='main',rva='1000')
        kinds={r['classification'] for r in result['items']}
        self.assertIn('import',kinds);self.assertIn('indirect',kinds);self.assertIn('direct',kinds)
        walk=q.query(self.work,'walk',module='main',rva='1000',depth=1)
        self.assertEqual(walk['total'],2)
        self.assertTrue(all('module' in row and 'rva' in row for row in walk['items']))
        self.assertEqual(q.query(self.work,'function',module='main',rva=4096)['total'],1)
        self.assertTrue(any(r['classification']=='recursive' for r in result['items']))
        callers=q.query(self.work,'callers',module='main',rva='1000')
        self.assertEqual(callers['total'],1)

    def test_field_origins_are_kept_distinct_and_limited(self):
        got=q.query(self.work,'fields',offset='c',limit=1)
        self.assertEqual(got['items'][0]['object_origin'],'shape-A')
        self.assertEqual(got['items'][0]['field_origin'],'field-X')
        self.assertFalse(got['truncated'])

    def test_stale_inputs_and_corrupt_shard_fail_closed(self):
        p=self.work/'baseline/inputs.json'; original=p.read_bytes();p.write_bytes(original+b' ')
        with self.assertRaisesRegex(ValueError,'stale'): q.query(self.work,'search',text='fn')
        p.write_bytes(original)
        row=self.inputs['functions'][0]; marker=self.cache/row['artifact_key']/'complete.json'
        marker.write_text('{}')
        with mock.patch.object(q,'_module_sources',return_value=self.modules):
            with self.assertRaises(Exception):q.build(self.work)
        self.assertTrue((self.work/'program.sqlite').exists())

    def test_limits_and_truncation(self):
        got=q.query(self.work,'search',text='fn',limit=1)
        self.assertEqual(got['total'],2);self.assertTrue(got['truncated'])
        page=q.query(self.work,'search',text='fn',limit=1,start=1)
        self.assertNotEqual(got['items'][0]['id'],page['items'][0]['id'])
        self.assertFalse(page['truncated'])
        with self.assertRaises(ValueError):q.query(self.work,'search',text='fn',limit=1001)

    def test_queries_do_not_checkout_or_write_sources(self):
        before={p.relative_to(self.work):p.read_bytes() for p in self.work.rglob('*') if p.is_file()}
        q.query(self.work,'search',text='fn')
        after={p.relative_to(self.work):p.read_bytes() for p in self.work.rglob('*') if p.is_file()}
        self.assertEqual(before,after)
        self.assertFalse((self.work/'functions').exists())

    def test_function_returns_authenticated_metadata_and_optional_source(self):
        item=q.get_function(self.work,'main',0x1000)
        self.assertEqual(item['metadata']['name'],'fn_00001000')
        self.assertFalse(item['source_included'])
        with self.assertRaisesRegex(ValueError,'exceeds requested bound'):
            q.query(self.work,'function',module='main',rva='1000',source=True,source_max_bytes=1)

    def test_original_bytes_and_terminated_string_are_bounded(self):
        with mock.patch.object(q,'_module_sources',return_value=self.modules):
            raw=q.binary_query(self.work,'bytes','main','1000',size=3)
            string=q.binary_query(self.work,'string','main','1000',encoding='ascii',max_bytes=8)
            unterminated=q.binary_query(self.work,'string','main','1004',encoding='ascii',max_bytes=3)
        self.assertEqual(raw['hex'],'616263')
        self.assertEqual(string['text'],'abc');self.assertTrue(string['terminated'])
        self.assertTrue(unterminated['truncated'])


if __name__=='__main__':unittest.main()

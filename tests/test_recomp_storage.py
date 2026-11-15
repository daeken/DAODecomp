"""Lossless view-metadata storage; all ordinary identity/file guards still run."""
import gzip
from pathlib import Path
import tempfile
import unittest
from tools import recomp


class ViewStorageTests(unittest.TestCase):
    def setUp(self):
        temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup)
        self.project=Path(temporary.name)
        content=b'constructed immutable generated source\n'
        self.manifest=dict(files={'unit.cpp':recomp.digest(content)},scope='constructed storage fixture')
        self.raw=recomp.encoded(self.manifest);self.identity=recomp.digest(self.raw)
        self.directory=self.project/'views'/self.identity;self.directory.mkdir(parents=True)
        (self.directory/'unit.cpp').write_bytes(content)
        self.pack(self.raw)

    def pack(self,data):
        (self.directory/'manifest.json.gz').write_bytes(gzip.compress(data,mtime=0))

    def test_exact_bytes_restored_and_all_ordinary_file_checks_remain_required(self):
        directory,manifest=recomp.read_view(self.project,self.identity)
        self.assertEqual(directory,self.directory);self.assertEqual(manifest,self.manifest)
        self.assertEqual((directory/'manifest.json').read_bytes(),self.raw)
        self.assertTrue((directory/'manifest.json.gz').exists())
        (directory/'unit.cpp').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'generated view changed'):
            recomp.read_view(self.project,self.identity)

    def test_changed_or_truncated_packed_metadata_never_publishes_a_manifest(self):
        self.pack(self.raw+b'changed')
        with self.assertRaisesRegex(ValueError,'identity changed'):
            recomp.read_view(self.project,self.identity)
        self.assertFalse((self.directory/'manifest.json').exists())
        self.assertFalse(list(self.directory.glob('.manifest-restore-*')))
        self.pack(self.raw)
        p=self.directory/'manifest.json.gz';p.write_bytes(p.read_bytes()[:-5])
        with self.assertRaisesRegex(ValueError,'could not be restored'):
            recomp.read_view(self.project,self.identity)
        self.assertFalse((self.directory/'manifest.json').exists())
        self.assertFalse(list(self.directory.glob('.manifest-restore-*')))

    def test_an_existing_changed_manifest_is_not_repaired_from_a_good_pack(self):
        path=self.directory/'manifest.json';changed=recomp.encoded(dict(self.manifest,changed=True));path.write_bytes(changed)
        with self.assertRaisesRegex(ValueError,'view manifest changed'):
            recomp.read_view(self.project,self.identity)
        self.assertEqual(path.read_bytes(),changed)

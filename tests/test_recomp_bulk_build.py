"""Whole-source staging safeguards; no original-function acceptance."""
from pathlib import Path
import tempfile
import unittest
from tools import recomp
from tools.recomp_bulk_build import stage_file,require_whole_inventory


class BulkBuildTests(unittest.TestCase):
    def test_staging_preserves_independent_writes_and_rejects_changed_cache(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);source=root/'immutable.cpp';source.write_bytes(b'original generated source')
            target=root/'stage/fn.cpp';identity=recomp.digest(source.read_bytes());stage_file(source,target,identity)
            self.assertNotEqual(source.stat().st_ino,target.stat().st_ino)
            target.write_bytes(b'edited staging');self.assertEqual(source.read_bytes(),b'original generated source')
            stage_file(source,target,identity);self.assertEqual(target.read_bytes(),source.read_bytes())
            source.write_bytes(b'changed cache')
            with self.assertRaisesRegex(ValueError,'source changed'):stage_file(source,target,identity)

    def test_partial_probe_cannot_be_called_whole_inventory_build(self):
        module=dict(processed=100,inventory_functions=100,counts=dict(generated_only=95,generation_failed=5))
        report=dict(status='completed inventory generation attempt; compilation/runtime remain separate',modules=dict(main=module,umbra=module))
        require_whole_inventory(report)
        report['modules']['main']=dict(processed=100,inventory_functions=100,counts=dict(generated_only=10,not_attempted=90))
        with self.assertRaisesRegex(ValueError,'probe/unattempted'):require_whole_inventory(report)
        report['modules'].pop('umbra')
        with self.assertRaisesRegex(ValueError,'main/Umbra'):require_whole_inventory(report)

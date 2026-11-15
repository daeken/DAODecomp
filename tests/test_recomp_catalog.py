"""Whole-program catalogs retain earlier reviewed roots and immutable payloads."""
from pathlib import Path
import sys
import tempfile
import unittest
from tools import recomp
from tools.recomp_bulk import known_catalog
from tools.recomp_bulk_build import require_whole_inventory
from tools.recomp_storage import share_payload


class WholeCatalogTests(unittest.TestCase):
    def test_static_inventory_does_not_drop_existing_selected_entries(self):
        inventory=[dict(rva=0x1000,name='static',body_ranges=[])]
        annotated={0x2000:dict(rva=0x2000,size=4)}
        reviewed={0x1000:dict(rva=0x1000,size=8),0x3000:dict(rva=0x3000,size=3,purpose='reviewed startup fragment')}
        rows=known_catalog(inventory,annotated,reviewed)
        self.assertEqual([row['rva'] for row in rows],[0x1000,0x2000,0x3000])
        self.assertEqual([row['catalog_source'] for row in rows],['static_inventory','annotated_project','reviewed_startup'])
        self.assertEqual(len(inventory),1)
        with self.assertRaisesRegex(ValueError,'duplicate'):known_catalog(inventory+inventory,annotated,reviewed)

    def test_completed_scan_requires_supplementary_entries_too(self):
        module=dict(inventory_functions=100,catalog_functions=102,processed=102,counts=dict(generated_only=102))
        report=dict(status='completed inventory generation attempt; compilation/runtime remain separate',modules=dict(main=module,umbra=module))
        require_whole_inventory(report)
        module['processed']=100
        with self.assertRaisesRegex(ValueError,'unattempted'):require_whole_inventory(report)

    def test_discovery_transport_does_not_imply_reviewed_provenance(self):
        discovered={0x3000:dict(rva=0x3000,size=3,
                    catalog_source='static_code_pointer_hypothesis',
                    contract_status='signature and behavior unknown',
                    behavioral_acceptance=False)}
        rows=known_catalog([],{},discovered)
        self.assertEqual(rows[0]['catalog_source'],'static_code_pointer_hypothesis')
        self.assertFalse(discovered[0x3000]['behavioral_acceptance'])
        # A static inventory entry keeps its original provenance even when an
        # overlay supplies another candidate selection for the same address.
        rows=known_catalog([dict(rva=0x3000,name='static')],{},discovered)
        self.assertEqual(rows[0]['catalog_source'],'static_inventory')

    @unittest.skipUnless(sys.platform=='darwin','requires APFS clonefile host')
    def test_shared_payloads_keep_independent_writes_and_reject_tampering(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);old=root/'old';new=root/'new';old.write_bytes(b'cached body');new.write_bytes(old.read_bytes())
            identity=recomp.digest(old.read_bytes())
            self.assertTrue(share_payload(old,new,identity))
            self.assertNotEqual(old.stat().st_ino,new.stat().st_ino)
            new.write_bytes(b'changed new view');self.assertEqual(old.read_bytes(),b'cached body')
            with self.assertRaisesRegex(ValueError,'bytes changed'):share_payload(old,new,identity)

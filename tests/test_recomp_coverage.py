"""Static entry proposals must retain binary identity and existing ownership."""
import copy
import gzip
import json
from pathlib import Path
import tempfile
import unittest
from tools.recomp_coverage import extra_entries,instruction_map


class CoverageEntryTests(unittest.TestCase):
    def test_only_exact_original_instruction_boundaries_inside_existing_ranges(self):
        image=bytes.fromhex('90c390c3');pe=dict(image_base=0x400000,sections=[dict(rva=0x1000,file_offset=0,file_size=4)])
        selection=dict(rva=0x1000,size=2,ranges=[dict(rva=0x1000,size=2)],extra_entries=[])
        row=dict(instructions=[dict(rva=0x1000,bytes='90'),dict(rva=0x1001,bytes='c3'),dict(rva=0x1003,bytes='c3')])
        before=copy.deepcopy(selection)
        self.assertEqual(extra_entries(row,selection,{0x1000},image,pe),([0x1001],1))
        self.assertEqual(selection,before)
        bad=copy.deepcopy(row);bad['instructions'][1]['bytes']='90'
        with self.assertRaisesRegex(ValueError,'bytes differ'):extra_entries(bad,selection,{0x1000},image,pe)
        bad['instructions'][1]['bytes']='c390'
        with self.assertRaisesRegex(ValueError,'ownership boundary'):extra_entries(bad,selection,{0x1000},image,pe)

    def test_matching_bytes_are_insufficient_when_decoder_rejects_boundary(self):
        selection=dict(ranges=[dict(rva=0x1000,size=1)],extra_entries=[])
        pe=dict(image_base=0x400000,sections=[dict(rva=0x1000,file_offset=0,file_size=1)])
        with self.assertRaisesRegex(ValueError,'decoder disagrees'):
            extra_entries(dict(instructions=[dict(rva=0x1000,bytes='0f')]),selection,set(),b'\x0f',pe)

    def test_incomplete_duplicate_or_wrong_module_maps_cannot_publish(self):
        header=dict(record='module',schema_version=1,module_sha256='abc',image_base=0x400000)
        function=dict(record='function',rva=0x1000,instructions=[dict(rva=0x1000,bytes='90')])
        footer=dict(record='complete',functions=1,instructions=1,behavioral_acceptance=False)
        with tempfile.TemporaryDirectory() as temporary:
            path=Path(temporary)/'map.gz'
            def write(rows):
                with gzip.open(path,'wt') as stream:
                    for row in rows:stream.write(json.dumps(row)+'\n')
            write([header,function,footer]);self.assertEqual(len(list(instruction_map(path,'abc',0x400000))),1)
            with self.assertRaisesRegex(ValueError,'identity differs'):list(instruction_map(path,'def',0x400000))
            write([header,function])
            with self.assertRaisesRegex(ValueError,'incomplete'):list(instruction_map(path,'abc',0x400000))
            write([header,function,function,footer])
            with self.assertRaisesRegex(ValueError,'duplicate'):list(instruction_map(path,'abc',0x400000))

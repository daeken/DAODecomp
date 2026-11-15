"""Instruction diagnostics must continue past failures without accepting bodies."""
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from tools import recomp
from tools.recomp_native import PE32
from tools.recomp_support_audit import collect_candidates, freeze_backend, audit_instructions, audit_in_batches
from tests.test_recomp_pointer_discovery import fixture
from recompiler.experiments.call_fixture import make_fixture


class SupportAuditCollectionTests(unittest.TestCase):
    def image(self, code):
        temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup)
        path=Path(temporary.name)/'audit.exe';data=fixture();data[0x400:0x400+len(code)]=code;path.write_bytes(data)
        return PE32(path)

    def selection(self,size):
        return [dict(rva=0x1000,selection=dict(ranges=[dict(rva=0x1000,size=size)]))]

    def test_later_instructions_and_repeated_origins_survive_a_failed_body(self):
        pe=self.image(bytes.fromhex('90d9fd90c3'))
        candidates,unknown,summary=collect_candidates(pe,self.selection(5),[dict(rva=0x1000,status='generation_failed')])
        self.assertFalse(unknown);self.assertEqual(summary['instruction_occurrences'],4)
        self.assertEqual({r['bytes'] for r in candidates},{'90','d9fd','c3'})
        self.assertEqual([o['rva'] for o in next(r for r in candidates if r['bytes']=='90')['origins']],[0x1000,0x1003])

    def test_undecodable_tail_invalid_selection_and_budget_stay_unknown(self):
        pe=self.image(bytes.fromhex('900f'))
        candidates,unknown,_=collect_candidates(pe,self.selection(2),[dict(rva=0x1000,status='generation_failed')])
        self.assertEqual([r['bytes'] for r in candidates],['90']);self.assertEqual((unknown[0]['rva'],unknown[0]['size']),(0x1001,1))
        _,unknown,_=collect_candidates(pe,[dict(rva=0x1000)],[dict(rva=0x1000,status='preparation_failed')])
        self.assertIn('no valid selection',unknown[0]['reason'])
        pe=self.image(bytes.fromhex('90c3'))
        with self.assertRaisesRegex(ValueError,'budget exhausted'):
            collect_candidates(pe,self.selection(2),[dict(rva=0x1000,status='generation_failed')],instruction_limit=1)

    def test_catalog_scope_checks_successful_bodies_without_hiding_decode_tails(self):
        pe=self.image(bytes.fromhex('900f'))
        results=[dict(rva=0x1000,status='generated_only',coverage=dict(uncovered_inventory_bytes=0))]
        candidates,unknown,summary=collect_candidates(pe,self.selection(2),results)
        self.assertFalse(candidates);self.assertFalse(unknown)
        candidates,unknown,summary=collect_candidates(pe,self.selection(2),results,scope='catalog')
        self.assertEqual([r['bytes'] for r in candidates],['90'])
        self.assertEqual(unknown[0]['rva'],0x1001)
        self.assertEqual(summary['inspected_selections'],1)
        with self.assertRaisesRegex(ValueError,'complete unique'):
            collect_candidates(pe,self.selection(2),[],scope='catalog')
        with self.assertRaisesRegex(ValueError,'complete unique'):
            collect_candidates(pe,self.selection(2),results*2,scope='catalog')

    def test_batched_audit_retains_every_encoding_and_does_not_publish_past_failure(self):
        rows=[dict(rva=i,bytes=f'{i:02x}') for i in range(5)]
        with tempfile.TemporaryDirectory() as temporary:
            directory=Path(temporary)
            with patch('tools.recomp_support_audit.audit_instructions',side_effect=lambda b,s,r,k,d:r) as audit:
                self.assertEqual(audit_in_batches(None,None,rows,None,directory,2),rows)
                self.assertEqual([len(c.args[2]) for c in audit.call_args_list],[2,2,1])
        with tempfile.TemporaryDirectory() as temporary:
            with patch('tools.recomp_support_audit.audit_instructions',side_effect=[rows[:2],RuntimeError('batch failed')]) as audit:
                with self.assertRaisesRegex(RuntimeError,'batch failed'):
                    audit_in_batches(None,None,rows,None,Path(temporary),2)
                self.assertEqual(audit.call_count,2)


    def test_invalid_entry_envelope_stays_unknown_while_original_ranges_are_audited(self):
        pe=self.image(bytes.fromhex('d9fd90c3'))
        candidates,unknown,summary=collect_candidates(pe,[dict(rva=0x1002)],[dict(rva=0x1002,status='preparation_failed')],
            diagnostic_ranges={0x1002:[dict(rva=0x1000,size=4)]})
        self.assertEqual({r['bytes'] for r in candidates},{'d9fd','90','c3'})
        self.assertEqual(summary['invalid_selection_instruction_occurrences'],3)
        self.assertEqual(summary['diagnostic_invalid_selections'],1)
        self.assertIn('no valid selection',unknown[0]['reason'])
        self.assertTrue(all(o['owner_rva']==0x1002 and o['source_kind']=='invalid_selection_inventory_range_diagnostic'
            for r in candidates for o in r['origins']))
        with self.assertRaises(ValueError):
            collect_candidates(pe,[dict(rva=0x1002)],[dict(rva=0x1002,status='preparation_failed')],
                diagnostic_ranges={0x1002:[dict(rva=0xdead0000,size=4)]})


class SupportAuditBackendTests(unittest.TestCase):
    def test_backend_reports_both_supported_and_unsupported_instructions_and_authenticates_bytes(self):
        if not shutil.which('dotnet'):self.skipTest('requires SharpRetro and .NET')
        with tempfile.TemporaryDirectory() as temporary:
            out=Path(temporary);backend=freeze_backend(out)
            from tools.recomp_support_audit import PROJECT
            self.assertEqual((out/'producers/support-audit-program.cs').read_bytes(),(PROJECT.parent/'Program.cs').read_bytes())
            self.assertEqual((out/'producers/sharp-retro-Program.cs').read_bytes(),(recomp.ROOT.parent/'SharpRetro/Decompiler/Program.cs').read_bytes())
            image,_,_=make_fixture();image=bytearray(image);image[0x200:0x204]=bytes.fromhex('90d990c3');binary=out/'audit.exe';binary.write_bytes(image)
            sha=recomp.digest(image)
            candidates=[dict(rva=rva,bytes=raw) for rva,raw in [(0x1000,'90'),(0x1001,'d9'),(0x1003,'c3')]]
            case=out/'valid';case.mkdir();results=audit_instructions(binary,sha,candidates,backend,case)
            self.assertEqual({r['bytes'] for r in results},{'90','d9','c3'})
            self.assertEqual(next(r for r in results if r['bytes']=='c3')['status'],'instruction_emission_available')
            # A truncated x87 prefix cannot become an emitted instruction;
            # the audit must still process RET after that refused boundary.
            self.assertEqual(next(r for r in results if r['bytes']=='d9')['status'],'instruction_support_unresolved')
            tampered=out/'tampered';tampered.mkdir()
            with self.assertRaisesRegex(RuntimeError,'audit process failed'):
                audit_instructions(binary,sha,[dict(rva=0x1000,bytes='c3')],backend,tampered)

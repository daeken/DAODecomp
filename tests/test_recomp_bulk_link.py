"""Whole-program registry guards, separate from game-behavior evidence."""
import unittest
from tools.recomp_bulk_link import add_owner, registry_sources, step_symbol


class BulkLinkTests(unittest.TestCase):
    def test_duplicate_instruction_ownership_cannot_silently_drop_a_body(self):
        owners={}
        add_owner(owners,0x401000,'fn_00001000')
        with self.assertRaisesRegex(ValueError,'ambiguous'):
            add_owner(owners,0x401000,'fn_00002000')
        with self.assertRaisesRegex(ValueError,'symbol'):
            add_owner(owners,0x402000,'fn_bad\n.long 0')

    def test_registry_keeps_interior_entries_and_uses_all_function_relocations(self):
        owners={0x10001004:'m_0123456789abcdef_fn_00001000',0x401000:'fn_00001000',0x401003:'fn_00001000'}
        functions=[(0x10001000,'m_0123456789abcdef_fn_00001000'),(0x401000,'fn_00001000')]
        cpp,assembly=registry_sources(functions,owners,[])
        self.assertIn('std::span<const CodeEntry> code(recomp_whole_code,3)',cpp)
        self.assertIn('std::array<FunctionEntry,2>',cpp)
        self.assertIn('.long 0x00401003\n.long '+step_symbol('fn_00001000'),assembly)
        self.assertIn('.long '+step_symbol('m_0123456789abcdef_fn_00001000'),assembly)
        self.assertLess(assembly.index('0x00401000'),assembly.index('0x10001004'))
        self.assertNotIn('@CODE',cpp)
        self.assertIn('untranslated guest code/import target',cpp)
        with self.assertRaisesRegex(ValueError,'overlaps'):
            registry_sources(functions,owners,[dict(address=0x401003,library='x.dll',symbol='x',policy='native')])

class ExplicitInstructionOwnershipTests(unittest.TestCase):
    def evidence(self,name,tag):
        return dict(symbol=name,artifact_key=tag*64,source_sha256=tag*64,metadata_sha256=tag*64,binary_sha256='a'*64,module='main')

    def plan(self):
        self.first=self.evidence('fn_00001000','1');self.second=self.evidence('fn_00001005','2')
        return dict(schema_version=1,compilation_inputs_sha256='3'*64,generation_report_sha256='4'*64,game_acceptance=False,
            assignments=[dict(address=0x401005,instruction_bytes='c3',owner='fn_00001000',candidates=[self.first,self.second])])

    def test_shared_pc_needs_every_exact_input_and_keeps_both_functions(self):
        from tools.recomp_bulk_link import InstructionOwnership
        plan=self.plan();resolver=InstructionOwnership(plan,'3'*64,'4'*64);owners={}
        resolver.add(owners,0x401005,'fn_00001005','c3',self.second,b'\xc3')
        with self.assertRaisesRegex(ValueError,'missing or unused'):resolver.finish()
        resolver.add(owners,0x401005,'fn_00001000','c3',self.first,b'\xc3');resolver.finish()
        cpp,assembly=registry_sources([(0x401000,'fn_00001000'),(0x401005,'fn_00001005')],owners,[])
        self.assertIn('std::array<FunctionEntry,2>',cpp)
        self.assertIn('0x00401005u,fn_00001005',cpp)
        self.assertIn('.long '+step_symbol('fn_00001000'),assembly)
        self.assertEqual(len(owners),1)
        with self.assertRaisesRegex(ValueError,'evidence changed'):
            resolver.add(owners,0x401005,'fn_00001000','c3',self.first,b'\xc3')

    def test_stale_wrong_bytes_identity_or_unplanned_overlap_stays_unresolved(self):
        from tools.recomp_bulk_link import InstructionOwnership
        plan=self.plan()
        for compilation,generation in [('5'*64,'4'*64),('3'*64,'5'*64)]:
            with self.assertRaisesRegex(ValueError,'binding'):InstructionOwnership(plan,compilation,generation)
        for code,evidence,original in [('90',self.first,b'\x90'),('c3',dict(self.first,source_sha256='5'*64),b'\xc3'),('c3',self.first,b'\x90')]:
            resolver=InstructionOwnership(plan,'3'*64,'4'*64)
            with self.assertRaisesRegex(ValueError,'evidence changed'):
                resolver.add({},0x401005,'fn_00001000',code,evidence,original)
        resolver=InstructionOwnership(None,'3'*64,'4'*64);owners={}
        resolver.add(owners,0x401005,'fn_00001000','c3',self.first,b'\xc3')
        with self.assertRaisesRegex(ValueError,'ambiguous'):
            resolver.add(owners,0x401005,'fn_00001005','c3',self.second,b'\xc3')

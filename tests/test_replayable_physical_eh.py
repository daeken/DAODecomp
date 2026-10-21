"""Real compiler/linker fixture checks, plus generic negative object mutations.

Set DAO_PHYSICAL_EH_FIXTURE to an independently built fixture folder containing
candidate.obj/exe/map. No game artifact is required or executed by these tests.
"""
import json, os, re, struct, unittest
from pathlib import Path
from rapid_object.coff import Coff
from rapid_object.eh_graph import Original
from tools.replayable.range_eh import reachable
from tools.replayable.physical_eh_identity import check


class PhysicalEhTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get('DAO_PHYSICAL_EH_FIXTURE')
        if not root:
            raise unittest.SkipTest('independent compiler/linker fixture not configured')
        cls.folder = Path(root)
        cls.object = (cls.folder/'candidate.obj').read_bytes()
        cls.original = (cls.folder/'candidate.exe').read_bytes()
        cls.obj = Coff(cls.object)
        symbols = {}
        for line in (cls.folder/'candidate.map').read_text().splitlines():
            m = re.match(r'\s+[0-9a-fA-F]{4}:[0-9a-fA-F]{8}\s+(\S+)\s+([0-9a-fA-F]{8})\b', line)
            if m:
                symbols[m[1]] = int(m[2], 16)
        cls.main = next(s for s in cls.obj.symbols.values() if s.storage == 2 and s.section > 0 and s.type == 32)
        cls.start = symbols[cls.main.name]
        cls.bindings = {s.name:symbols[s.name] for s in cls.obj.symbols.values() if s.section == 0 and s.name in symbols}
        graph = reachable(Original(cls.original), cls.start, [])
        cls.ranges = []
        for row in graph['instructions']:
            lo, hi = row['pc'], row['pc']+row['length']
            if cls.ranges and cls.ranges[-1][1] == lo:
                cls.ranges[-1][1] = hi
            else:
                cls.ranges.append([lo, hi])

    def run_check(self, obj=None, original=None, ranges=None, bindings=None):
        return check(self.original if original is None else original,
                     self.ranges if ranges is None else ranges,
                     self.object if obj is None else obj, self.main.name,
                     self.bindings if bindings is None else bindings)

    def mutate_section(self, number, offset, data):
        raw = bytearray(self.object)
        ptr = struct.unpack_from('<I', raw, 20+40*(number-1)+20)[0]
        raw[ptr+offset:ptr+offset+len(data)] = data
        return bytes(raw)

    def change_symbol(self, sym, value):
        raw = bytearray(self.object)
        table = struct.unpack_from('<I', raw, 8)[0]
        struct.pack_into('<I', raw, table+18*sym.index+8, value)
        return bytes(raw)

    def test_real_compiler_linker_complete_sections(self):
        r = self.run_check()
        self.assertEqual(r['status'], 'identical_at_derived_original_placement', r)
        self.assertTrue(r['acceptance_supported'])
        self.assertFalse(r['linked_placement_proven'])
        self.assertEqual(r['bytes_compared'], 318)
        self.assertEqual(len(r['placements']), 3)
        self.assertTrue(all(x['equal'] for x in r['sections']))

    def test_same_node_bytes_at_different_relative_offset(self):
        catch = next(s for s in self.obj.symbols.values() if s.name.startswith('__catch$'))
        r = self.run_check(obj=self.change_symbol(catch, catch.value+1))
        self.assertFalse(r['acceptance_supported'])
        self.assertTrue(r['blockers'])

    def test_original_catch_retarget_keeps_metadata_but_conflicts_placement(self):
        r = self.run_check()
        # Rooted catch address in the original complete handler table.
        at = next(a['address'] for a in r['anchors'] if a['role'] == 'handler_table_0')+12
        reader = Original(self.original)
        section = next(s for s in reader.pe.sections if s[0] <= at-reader.pe.image_base < s[0]+s[1])
        off = section[2]+at-reader.pe.image_base-section[0]
        raw = bytearray(self.original)
        struct.pack_into('<I', raw, off, struct.unpack_from('<I', raw, off)[0]+1)
        r = self.run_check(original=bytes(raw))
        self.assertTrue(any('inconsistent_section_placement' in b for b in r['blockers']), r)

    def test_changed_frame_store_or_state(self):
        sec = self.obj.sections[self.main.section-1]
        for pattern in (b'\x89\x65', b'\xc6\x45\xfc'):
            at = sec.data.find(pattern)
            self.assertGreaterEqual(at, 0)
            offset = at+len(pattern)
            r = self.run_check(obj=self.mutate_section(sec.number, offset, bytes([sec.data[offset]^4])))
            self.assertFalse(r['acceptance_supported'], r)

    def test_changed_call_return_pc_or_target(self):
        name = next(k for k in self.bindings if 'allocate_cpp' in k)
        b = dict(self.bindings);b[name] += 1
        r = self.run_check(bindings=b)
        self.assertTrue(any('section_bytes_differ' in x for x in r['blockers']), r)

    def test_unresolved_and_invalid_external(self):
        for value in (None, -1, 0x100000000, True):
            b = dict(self.bindings)
            name = next(k for k in b if 'allocate_cpp' in k)
            if value is None: del b[name]
            else: b[name] = value
            self.assertFalse(self.run_check(bindings=b)['acceptance_supported'])

    def test_addend_not_erased(self):
        sec = self.obj.sections[self.main.section-1]
        rel = next(x for x in sec.relocations if x.kind == 20)
        r = self.run_check(obj=self.mutate_section(sec.number, rel.offset, struct.pack('<I', 4)))
        self.assertFalse(r['acceptance_supported'])
        self.assertIn('candidate_code_relocation_domain', r['blockers'])

    def test_missing_owned_range(self):
        self.assertGreater(len(self.ranges), 1)
        r = self.run_check(ranges=self.ranges[:-1])
        self.assertIn('physical_original_inventory_CFG', r['blockers'])

    def test_extra_runtime_section_not_discarded(self):
        raw = bytearray(self.object)
        sec = next(s for s in self.obj.sections if s.name == '.debug$T')
        off = 20+40*(sec.number-1)
        raw[off:off+8] = b'.extra\0\0'
        struct.pack_into('<I', raw, off+36, 0x40300040)
        definition=next(x for x in self.obj.symbols.values()if x.section==sec.number and x.aux)
        symbol_offset=struct.unpack_from('<I',raw,8)[0]+18*definition.index
        raw[symbol_offset:symbol_offset+8]=b'.extra\0\0'
        r = self.run_check(obj=bytes(raw))
        self.assertIn('physical_extra_runtime_section:.extra', r['blockers'])

    def test_removed_trap_suffix_never_exact(self):
        sec = self.obj.sections[self.main.section-1]
        self.assertEqual(sec.data[-1], 0xcc)
        r = self.run_check(obj=self.mutate_section(sec.number, len(sec.data)-1, b'\x90'))
        self.assertFalse(r['acceptance_supported'])

    def test_missing_or_extra_safeseh(self):
        sec = next(s for s in self.obj.sections if s.name == '.sxdata')
        r = self.run_check(obj=self.mutate_section(sec.number, 0, struct.pack('<I', self.main.index)))
        self.assertIn('physical_missing_or_extra_SAFESEH', r['blockers'])

    def test_alignment_must_hold_for_whole_section(self):
        r = self.run_check()
        number = next(x['section'] for x in r['sections'] if x['size'] == 140)
        raw = bytearray(self.object);off=20+40*(number-1)+36
        flags=struct.unpack_from('<I', raw, off)[0]
        struct.pack_into('<I', raw, off, flags & ~0xf00000 | 0xe00000)
        self.assertIn('physical_section_alignment', self.run_check(obj=bytes(raw))['blockers'])

    def test_directives_cannot_change_image_layout(self):
        sec=next(s for s in self.obj.sections if s.name=='.drectve')
        r=self.run_check(obj=self.mutate_section(sec.number, 0, b'/MERGE:x=y'))
        self.assertIn('physical_unknown_link_directive', r['blockers'])

    def test_overlapping_metadata_cannot_place(self):
        sym = next(s for s in self.obj.symbols.values() if s.name.startswith('__ehfuncinfo$'))
        self.assertFalse(self.run_check(obj=self.change_symbol(sym, sym.value-4))['acceptance_supported'])

    def test_conflicting_runtime_and_source_bindings(self):
        from unittest.mock import patch
        from tools.replayable.ebp_eh_native import compare_complete
        spec={self.start-0x400000:dict(symbol=self.main.name,ranges=[dict(start_rva=a-0x400000,end_rva_inclusive=b-0x400001)for a,b in self.ranges])}
        name='___security_cookie';roots=dict(self.bindings);wrong={name:roots[name]+4}
        with patch('tools.replayable.ebp_eh_native.derive',return_value={'target':self.bindings['__CxxThrowException@8']}):
            r=compare_complete(self.original,b'fixture',{},self.object,spec,wrong,dict(root_bindings=roots))
        self.assertEqual(r['status'],'inconclusive')
        self.assertIn('physical_conflicting_external_bindings',r['blockers'])

    def test_new_route_requires_physical_gate_and_retains_diagnostic(self):
        from unittest.mock import patch
        from tools.replayable.ebp_eh_native import compare_complete
        spec={self.start-0x400000:dict(symbol=self.main.name,ranges=[dict(start_rva=a-0x400000,end_rva_inclusive=b-0x400001)for a,b in self.ranges])}
        with patch('tools.replayable.ebp_eh_native.derive',return_value={'target':self.bindings['__CxxThrowException@8']}):
            r=compare_complete(self.original,b'fixture',{},self.object,spec,{},dict(root_bindings=self.bindings))
        self.assertEqual(r['status'],'exact_eh_graph_match',r)
        row=r['functions'][0]
        self.assertFalse(row['diagnostic']['acceptance_supported'])
        self.assertTrue(row['physical_identity']['acceptance_supported'])
        self.assertEqual(row['counts'],{'equal':318})

    def test_runtime_link_remove_flag_is_not_ignored(self):
        raw=bytearray(self.object);off=20+40*(self.main.section-1)+36
        flags=struct.unpack_from('<I',raw,off)[0]
        struct.pack_into('<I',raw,off,flags|0x800)
        self.assertIn('physical_runtime_section_flags',self.run_check(obj=bytes(raw))['blockers'])

    def special_definition(self, section, value, storage, name=b'_extra'):
        raw=bytearray(self.object);table=struct.unpack_from('<I',raw,8)[0]
        raw[table:table+8]=name.ljust(8,b'\0')
        struct.pack_into('<IhHBB',raw,table+8,value,section,0,storage,0)
        return bytes(raw)

    def test_unused_COMMON_storage_is_not_a_section(self):
        r=self.run_check(obj=self.special_definition(0,4,2))
        self.assertFalse(r['acceptance_supported'])
        self.assertIn('physical_unplaced_or_special_external_definition',r['blockers'])

    def test_unused_weak_external_refuses(self):
        r=self.run_check(obj=self.special_definition(0,0,105))
        self.assertIn('physical_unplaced_or_special_external_definition',r['blockers'])
        # A complete weak-alias auxiliary record, not only malformed no-aux input.
        raw=bytearray(self.special_definition(0,0,105));table=struct.unpack_from('<I',raw,8)[0]
        raw[table+17]=1
        fallback=next(x.index for x in self.obj.symbols.values()if 'allocate_cpp' in x.name)
        raw[table+18:table+36]=struct.pack('<II',fallback,3)+bytes(10)
        self.assertIn('physical_unplaced_or_special_external_definition',self.run_check(obj=bytes(raw))['blockers'])

    def test_unknown_absolute_definition_refuses(self):
        r=self.run_check(obj=self.special_definition(-1,0x1234,2))
        self.assertIn('physical_unsupported_absolute_or_debug_definition',r['blockers'])

    def test_definition_in_discarded_debug_section_refuses(self):
        sec=next(x for x in self.obj.sections if x.name=='.debug$S')
        r=self.run_check(obj=self.special_definition(sec.number,1,3))
        self.assertIn('physical_unplaced_symbol_definition',r['blockers'])

    def test_section_definition_size_and_selection_refuse(self):
        sym=next(s for s in self.obj.symbols.values() if s.section==self.main.section and s.aux)
        table=struct.unpack_from('<I',self.object,8)[0];aux=table+18*(sym.index+1)
        raw=bytearray(self.object);struct.pack_into('<I',raw,aux,len(self.obj.sections[self.main.section-1].data)+4)
        self.assertIn('physical_section_definition_extent_or_aux',self.run_check(obj=bytes(raw))['blockers'])
        raw=bytearray(self.object);raw[aux+14]=7
        self.assertIn('physical_main_COMDAT_selection',self.run_check(obj=bytes(raw))['blockers'])

    def test_integrated_COMMON_case_stays_unsupported(self):
        from unittest.mock import patch
        from tools.replayable.ebp_eh_native import compare_complete
        spec={self.start-0x400000:dict(symbol=self.main.name,ranges=[dict(start_rva=a-0x400000,end_rva_inclusive=b-0x400001)for a,b in self.ranges])}
        with patch('tools.replayable.ebp_eh_native.derive',return_value={'target':self.bindings['__CxxThrowException@8']}):
            r=compare_complete(self.original,b'fixture',{},self.special_definition(0,4,2),spec,{},dict(root_bindings=self.bindings))
        self.assertEqual(r['status'],'inconclusive',r)
        self.assertFalse(r['acceptance_supported'])
        row=r['functions'][0]
        self.assertIn('physical_unplaced_or_special_external_definition',row['physical_identity']['blockers'])
        self.assertIn('multi_try_acceptance_not_implemented',row['legacy_diagnostic_blockers'])
        self.assertNotIn('multi_try_acceptance_not_implemented',row['blockers'])


class StandaloneBindingTests(unittest.TestCase):
    def test_candidate_check_records_physical_checker_and_dependencies(self):
        import importlib.util, sqlite3, hashlib
        root=Path(__file__).resolve().parents[1]
        spec=importlib.util.spec_from_file_location('physical_stdio',root/'tools/decompilation-mcp/tests/test_stdio.py')
        stdio=importlib.util.module_from_spec(spec);spec.loader.exec_module(stdio)
        case=stdio.StdioTests('test_durable_idempotency_two_clients_and_missing_build')
        case.setUp()
        try:
            fid=case.query(limit=1)['items'][0]['function_id']
            build=case.client.call('function_inspect',project_id='open',function_id=fid)['builds'][0]['build_id']
            job=case.client.call('candidate_check',project_id='open',build_id=build,idempotency_key='physical-inputs')
            stdio.wait_job(case.client,job['job_id'])
            with sqlite3.connect(case.root/'state/jobs.sqlite3')as db:
                request=json.loads(db.execute('SELECT request FROM jobs WHERE id=?',(job['job_id'],)).fetchone()[0])
            for name in ('physical_eh_identity.py','ebp_eh_candidate.py','range_eh.py','ebp_eh_native.py'):
                p=root/'tools/replayable'/name
                self.assertEqual(request['inputs'][str(p)],hashlib.sha256(p.read_bytes()).hexdigest())
        finally:
            case.tearDown()

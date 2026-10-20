"""Durable MCP boundary tests use deliberately invalid open binary inputs.
No proprietary compiler, SharpRetro installation or VM is used in these tests.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('replayable_stdio', ROOT / 'tools/decompilation-mcp/tests/test_stdio.py')
stdio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stdio)


def sha(data):
    return hashlib.sha256(data).hexdigest()


@unittest.skipUnless(stdio.DLL.exists(), 'build C# component first')
class PipelineBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.clients = []
        binary = b'open invalid PE, never executable'
        (self.root / 'original.exe').write_bytes(binary)
        (self.root / 'compiler.exe').write_bytes(b'open fake compiler; never executed')
        self.dll = self.root / 'lifter/adapter.dll'
        self.dll.parent.mkdir()
        self.dll.write_bytes(b'open fake adapter; never executed')
        (self.root / 'manifest.json').write_text(json.dumps(dict(revision=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), upstream_tracked_source_sha256={}, assemblies_sha256={'adapter.dll': sha(self.dll.read_bytes())}, runtime_files_sha256={})))
        (self.root / 'lifter.json').write_text(json.dumps(dict(adapter_dll=str(self.dll), build_manifest=str(self.root / 'manifest.json'), sharp_retro_checkout=str(ROOT))))
        functions = [dict(rva=rva, name='fn', body_bytes=1, body_ranges=[dict(start_rva=rva, end_rva_inclusive=rva)], signature_hypothesis='unknown', calling_convention_hypothesis='unknown') for rva in (0x1000, 0x1030, 0x1040)]
        (self.root / 'inventory.json').write_text(json.dumps(dict(module_sha256=sha(binary), image_base=0x400000, functions=functions)))
        project = dict(id='open', module='open-invalid', module_sha256=sha(binary), inventory=str(self.root / 'inventory.json'), original=str(self.root / 'original.exe'), compiler=str(self.root / 'compiler.exe'), compiler_sha256=sha((self.root / 'compiler.exe').read_bytes()), allowed_roots=[str(self.root), str(ROOT)], replayable=dict(lifter_config=str(self.root / 'lifter.json'), vm_build_lock=str(self.root / 'unused.lock'), output_root=str(self.root / 'attempts')))
        self.config = self.root / 'registry.json'
        self.config.write_text(json.dumps(dict(state_root=str(self.root / 'state'), python=__import__('sys').executable, adapter_root=str(ROOT), projects=[project])))
        self.client = self.connect()

    def connect(self):
        client = stdio.Client(self.config)
        self.clients.append(client)
        return client

    def tearDown(self):
        for client in self.clients:
            client.close()
        self.temp.cleanup()

    def submit(self, token, **extra):
        return self.client.call('replayable_run_next', project_id='open', idempotency_key=token, compile=False, **extra)

    def test_failed_first_frontier_remains_active_and_restart_idempotent(self):
        submitted = self.submit('first')
        self.assertEqual(submitted['rva'], 0x1000)
        done = stdio.wait_job(self.client, submitted['job_id'])
        self.assertEqual(done['state'], 'completed')
        self.assertEqual(done['result']['status'], 'inconclusive')
        again = self.connect().call('replayable_run_next', project_id='open', idempotency_key='first', compile=False)
        self.assertEqual(again['job_id'], submitted['job_id'])
        self.assertTrue(again['reused'])
        following = self.submit('retry-exact-frontier')
        self.assertEqual(following['rva'], 0x1000)
        stdio.wait_job(self.client, following['job_id'])
        state = self.client.call('replayable_status', project_id='open')
        self.assertEqual(state['new_pipeline_full_matches'], 0)
        self.assertEqual(state['inventory_identities'], 3)
        self.assertEqual(state['first_unresolved_rva'], 0x1000)

    def test_lifter_artifact_change_invalidates_job_key(self):
        first = self.submit('bound-to-inputs')
        stdio.wait_job(self.client, first['job_id'])
        self.dll.write_bytes(b'changed actual lifter bytes')
        with self.assertRaises(ValueError):
            self.submit('bound-to-inputs')
        second = self.submit('new-inputs')
        self.assertNotEqual(first['pipeline_key'], second['pipeline_key'])
        self.assertEqual(second['rva'], 0x1000)
        stdio.wait_job(self.client, second['job_id'])

    def test_seeded_receipt_source_object_and_report_integrity_invalidation(self):
        # Controlled persistence-only fixture: no comparison success is claimed.
        import sqlite3
        first = self.submit('receipt-fixture')
        stdio.wait_job(self.client, first['job_id'])
        folder = self.root / 'attempts' / first['job_id']
        (folder / 'build').mkdir()
        paths = {'source_sha256': folder / 'candidate.cpp', 'object_sha256': folder / 'build/candidate.obj', 'comparison_sha256': folder / 'comparison.json'}
        for path in paths.values():
            path.write_bytes(b'controlled persistence fixture')
        receipt = dict(status='full_match', **{key: sha(path.read_bytes()) for key, path in paths.items()})
        (folder / 'result.json').write_text(json.dumps(receipt))
        with sqlite3.connect(self.root / 'state/jobs.sqlite3') as db:
            db.execute("UPDATE replayable_frontier SET status='full_match'")
        self.assertEqual(self.client.call('replayable_status', project_id='open')['new_pipeline_full_matches'], 1)
        for path in paths.values():
            original = path.read_bytes()
            path.write_bytes(b'changed artifact')
            status = self.client.call('replayable_status', project_id='open')
            self.assertEqual(status['new_pipeline_full_matches'], 0)
            self.assertEqual(status['first_unresolved_rva'], 0x1000)
            path.write_bytes(original)
        (folder / 'candidate.cpp').unlink()
        self.assertEqual(self.client.call('replayable_status', project_id='open')['new_pipeline_full_matches'], 0)

    def test_external_unknown_frontier_requires_reconciliation_before_retry(self):
        import sqlite3
        first = self.submit('unknown-control')
        stdio.wait_job(self.client, first['job_id'])
        with sqlite3.connect(self.root / 'state/jobs.sqlite3') as db:
            db.execute("UPDATE replayable_frontier SET status='external_outcome_unknown'")
        with self.assertRaises(ValueError):
            self.submit('must-not-retry-unknown-external-call')

    def assert_cross_key_barrier(self, state):
        import sqlite3
        first = self.submit('cross-key-' + state)
        stdio.wait_job(self.client, first['job_id'])
        database = self.root / 'state/jobs.sqlite3'
        with sqlite3.connect(database) as db:
            db.execute("UPDATE replayable_frontier SET status=?", (state,))
        self.dll.write_bytes(b'changed frontend runtime must not clear external uncertainty')
        changed = self.client.call('replayable_status', project_id='open')
        self.assertNotEqual(changed['pipeline_key'], first['pipeline_key'])
        with self.assertRaises(ValueError):
            self.submit('changed-key-' + state)
        # A compiler/support configuration revision also gets a different key.
        config = json.loads(self.config.read_text())
        config['projects'][0]['compiler_flags'] = ['/open-fixture-revised-compiler-profile']
        self.config.write_text(json.dumps(config))
        other = self.connect()
        revised = other.call('replayable_status', project_id='open')
        self.assertNotEqual(revised['pipeline_key'], changed['pipeline_key'])
        with self.assertRaises(ValueError):
            other.call('replayable_run_next', project_id='open', idempotency_key='revised-compiler-' + state, compile=True)
        with sqlite3.connect(database) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM jobs').fetchone()[0], 1)
            rows = db.execute('SELECT input_key,status,job FROM replayable_frontier').fetchall()
        self.assertEqual(rows, [(first['pipeline_key'], state, first['job_id'])])

    def test_running_frontier_blocks_changed_input_and_compiler_keys(self):
        self.assert_cross_key_barrier('running')

    def test_external_unknown_frontier_blocks_changed_input_and_compiler_keys(self):
        self.assert_cross_key_barrier('external_outcome_unknown')

    def test_unknown_recipe_and_reordered_passes_are_rejected(self):
        recipe = dict(schema_version=1, architecture='x86-bits32-linear-v1', frontend='sharpretro-typed-v1', compiler_profile='vc8-x86-thiscall-stores-v1', steps=['emit-thiscall-stores-v1', 'raise-linear-effects-v1'])
        with self.assertRaises(ValueError):
            self.submit('bad-order', recipe_json=json.dumps(recipe))
        recipe['steps'] = ['invent-semantics']
        with self.assertRaises(ValueError):
            self.submit('bad-step', recipe_json=json.dumps(recipe))

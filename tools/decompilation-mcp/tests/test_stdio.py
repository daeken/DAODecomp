"""Real newline-framed MCP stdio integration; no external Python packages required.

Run after dotnet build tools/decompilation-mcp -c Release. DAO smoke is opt-in:
DECOMPILATION_MCP_REAL_CONFIG=/absolute/registry.json python3 -m unittest discover
-s tools/decompilation-mcp/tests -v
"""
import concurrent.futures
import hashlib
import importlib.util
import struct
import sys
import json
import os
from pathlib import Path
import queue
import shutil
import sqlite3
import subprocess
import tempfile
import threading
import time
import unittest

ROOT = Path(__file__).resolve().parents[3]
COMPONENT = ROOT / 'tools/decompilation-mcp'
DLL = COMPONENT / 'bin/Release/net10.0/Decompilation.Mcp.dll'
DOTNET = os.environ.get('DOTNET', shutil.which('dotnet') or '/usr/local/share/dotnet/dotnet')


class Client:
    def __init__(self, config):
        self.process = subprocess.Popen([DOTNET, str(DLL), 'serve', '--config', str(config)],
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL, text=True, bufsize=1)
        self.lines = queue.Queue()
        self.thread = threading.Thread(target=lambda: [self.lines.put(line) for line in self.process.stdout], daemon=True)
        self.thread.start()
        self.seq = 0
        result = self.rpc('initialize', {'protocolVersion': '2025-11-25', 'capabilities': {},
                                        'clientInfo': {'name': 'decompilation-test', 'version': '1'}})
        assert result['protocolVersion'] == '2025-11-25', result
        self.send({'jsonrpc': '2.0', 'method': 'notifications/initialized'})

    def send(self, value):
        self.process.stdin.write(json.dumps(value) + '\n')
        self.process.stdin.flush()

    def rpc(self, method, params):
        self.seq += 1
        self.send({'jsonrpc': '2.0', 'id': self.seq, 'method': method, 'params': params})
        while True:
            response = json.loads(self.lines.get(timeout=30))
            if response.get('id') == self.seq:
                if 'error' in response:
                    raise AssertionError(response['error'])
                return response['result']

    def call(self, name, **arguments):
        result = self.rpc('tools/call', {'name': name, 'arguments': arguments})
        if result.get('isError'):
            raise ValueError(result)
        return json.loads(result['content'][0]['text'])

    def close(self):
        self.process.stdin.close()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)
        self.process.stdout.close()
        self.thread.join(timeout=2)


def wait_job(client, job):
    for _ in range(150):
        value = client.call('job_get', job_id=job)
        if value['state'] not in ('queued', 'running'):
            return value
        time.sleep(.05)
    raise AssertionError('Job did not complete')


class BackendCoverageGuardTests(unittest.TestCase):
    def test_generated_EH_dependency_cannot_use_ordinary_coverage(self):
        spec = importlib.util.spec_from_file_location('decompilation_adapter', COMPONENT / 'adapter.py')
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        sys.path.insert(0, str(ROOT))
        try:
            def object_with_symbol(name):
                encoded = name.encode() + b'\0'
                header = struct.pack('<HHIIIHH', 0x14c, 1, 0, 61, 1, 0, 0)
                section = struct.pack('<8sIIIIIIHHI', b'.text', 0, 0, 1, 60, 0, 0, 0, 0, 0x60000020)
                symbol = struct.pack('<IIIhHBB', 0, 4, 0, 0, 0x20, 2, 0)
                return header + section + b'\xc3' + symbol + struct.pack('<I', len(encoded) + 4) + encoded
            self.assertFalse(adapter.native_eh_symbols(object_with_symbol('_fn_00001000')))
            for name in ('__ehhandler$fn_00001000', '__ehfuncinfo$fn_00001000',
                         '__unwindtable$fn_00001000', '__unwindfunclet$fn_00001000$0'):
                self.assertTrue(adapter.native_eh_symbols(object_with_symbol(name)), name)
        finally:
            sys.path.remove(str(ROOT))


@unittest.skipUnless(DLL.exists(), 'build the .NET component first')
class StdioTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        fixture = COMPONENT / 'fixtures/open-project'
        shutil.copy(fixture / 'inventory.json', self.root / 'inventory.json')
        shutil.copy(fixture / 'source.cpp', self.root / 'source.cpp')
        self.sha = hashlib.sha256((self.root / 'source.cpp').read_bytes()).hexdigest()
        (self.root / 'published.json').write_text(json.dumps({
            'module_sha256': '0' * 64, 'functions': [
                {'rva': '0x00001000', 'source': 'source.cpp', 'source_sha256': self.sha}]}))
        self.config = self.root / 'registry.json'
        self.config.write_text(json.dumps({
            'state_root': str(self.root / 'state'), 'python': os.sys.executable,
            'adapter_root': str(ROOT), 'projects': [{
                'id': 'open', 'module': 'open_fixture', 'module_sha256': '0' * 64,
                'inventory': str(self.root / 'inventory.json'), 'published_index': str(self.root / 'published.json'),
                'allowed_roots': [str(self.root)], 'builds': [
                    {'name': 'missing', 'folder': str(self.root / 'missing-build'), 'rva': 4096}]}]}))
        self.clients = []
        self.client = self.connect()

    def connect(self):
        client = Client(self.config)
        self.clients.append(client)
        return client

    def tearDown(self):
        for client in self.clients:
            client.close()
        self.temp.cleanup()

    def query(self, **kwargs):
        return self.client.call('function_query', project_id='open', **kwargs)

    def test_initialize_list_open_and_pagination(self):
        names = {t['name'] for t in self.client.rpc('tools/list', {})['tools']}
        self.assertEqual(names, {'project_list', 'project_open', 'function_query', 'function_inspect',
                                'corpus_find_related', 'candidate_check', 'job_get'})
        opened = self.client.call('project_open', project_id='open')
        self.assertEqual(opened['inventory_identities'], 3)
        self.assertEqual(opened['compilation'], 'unsupported')
        first = self.query(limit=1)
        second = self.query(limit=1, cursor=first['next_cursor'])
        self.assertNotEqual(first['items'][0]['function_id'], second['items'][0]['function_id'])
        with self.assertRaises(ValueError):
            self.query(cursor=first['next_cursor'], publication='published')
        for args in ({'limit': 0}, {'limit': 101}, {'publication': 'match'}, {'cursor': 'invalid'}):
            with self.subTest(args=args), self.assertRaises(ValueError):
                self.query(**args)
        with self.assertRaises(ValueError):
            self.client.call('project_open', project_id=str(self.root))

    def test_bounded_inspect_similarity_and_source_tamper(self):
        function = self.query(limit=1)['items'][0]['function_id']
        inspected = self.client.call('function_inspect', project_id='open', function_id=function, source_limit=10)
        self.assertEqual(len(inspected['source']), 10)
        self.assertTrue(inspected['source_truncated'])
        related = self.client.call('corpus_find_related', project_id='open', function_id=function)
        self.assertEqual(related['coverage'], 3)
        self.assertFalse(related['acceptance_evidence'])
        (self.root / 'source.cpp').write_text('tampered')
        inspected = self.client.call('function_inspect', project_id='open', function_id=function)
        self.assertIsNone(inspected['source'])
        self.assertEqual(inspected['source_error'], 'published_source_unavailable_or_changed')

    def test_symlink_source_escape(self):
        function = self.query(limit=1)['items'][0]['function_id']
        (self.root / 'source.cpp').unlink()
        try:
            (self.root / 'source.cpp').symlink_to(COMPONENT / 'fixtures/open-project/source.cpp')
        except OSError:
            self.skipTest('Host disallows creating symlinks')
        inspected = self.client.call('function_inspect', project_id='open', function_id=function)
        self.assertIsNone(inspected['source'])

    def test_durable_idempotency_two_clients_and_missing_build(self):
        function = self.query(limit=1)['items'][0]['function_id']
        build = self.client.call('function_inspect', project_id='open', function_id=function)['builds'][0]['build_id']
        other = self.connect()
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            requests = [pool.submit(c.call, 'candidate_check', project_id='open', build_id=build,
                                    idempotency_key='same-operation') for c in (self.client, other)]
            jobs = [future.result()['job_id'] for future in requests]
        self.assertEqual(jobs[0], jobs[1])
        done = wait_job(self.client, jobs[0])
        self.assertEqual(done['state'], 'completed')
        self.assertEqual(done['result']['status'], 'inconclusive')
        self.assertFalse(done['result']['fresh_comparison'])
        third = self.connect()
        self.assertEqual(third.call('job_get', job_id=jobs[0])['result'], done['result'])
        with sqlite3.connect(self.root / 'state/jobs.sqlite3') as db:
            self.assertEqual(db.execute('SELECT count(*) FROM jobs').fetchone()[0], 1)

    def test_inventory_drift_rejects_submission_until_snapshot_refresh(self):
        opened = self.client.call('project_open', project_id='open')
        function = self.query(limit=1)['items'][0]['function_id']
        build = self.client.call('function_inspect', project_id='open', function_id=function)['builds'][0]['build_id']
        inventory_path = self.root / 'inventory.json'
        inventory = json.loads(inventory_path.read_text())
        inventory['functions'][0]['body_ranges'][0]['end_rva_inclusive'] += 1
        inventory['functions'][0]['body_bytes'] += 1
        inventory_path.write_text(json.dumps(inventory))
        # Opening again in the same server retains the original immutable snapshot.
        self.assertEqual(self.client.call('project_open', project_id='open')['revision'], opened['revision'])
        with self.assertRaises(ValueError):
            self.client.call('candidate_check', project_id='open', build_id=build,
                             idempotency_key='inventory-drift')
        with sqlite3.connect(self.root / 'state/jobs.sqlite3') as db:
            self.assertEqual(db.execute('SELECT count(*) FROM jobs').fetchone()[0], 0)
        # A new server imports the changed inventory under a new snapshot revision.
        refreshed = self.connect()
        self.assertNotEqual(refreshed.call('project_open', project_id='open')['revision'], opened['revision'])
        submitted = refreshed.call('candidate_check', project_id='open', build_id=build,
                                   idempotency_key='inventory-drift')
        done = wait_job(refreshed, submitted['job_id'])
        self.assertEqual(done['state'], 'completed')
        self.assertEqual(done['result']['status'], 'inconclusive')  # Fixture has no compiler artifacts.
        with sqlite3.connect(self.root / 'state/jobs.sqlite3') as db:
            request = json.loads(db.execute('SELECT request FROM jobs').fetchone()[0])
        self.assertEqual(request['revision'], refreshed.call('project_open', project_id='open')['revision'])
        self.assertEqual(request['inputs'][str(inventory_path)], hashlib.sha256(inventory_path.read_bytes()).hexdigest())

    def test_interrupted_job_is_unknown_without_replay(self):
        self.client.call('project_open', project_id='open')
        ident = 'a' * 32
        with sqlite3.connect(self.root / 'state/jobs.sqlite3') as db:
            db.execute("INSERT INTO jobs(id,project,token,request,state,created,started) VALUES(?,?,?,'{}','running',?,?)",
                       (ident, 'open', 'crashed', '2026-10-19T00:00:00+00:00', '2026-10-19T00:00:00+00:00'))
        result = self.client.call('job_get', job_id=ident)
        self.assertEqual(result['state'], 'interrupted_unknown')
        self.assertEqual(result['result']['status'], 'inconclusive')


@unittest.skipUnless(os.environ.get('DECOMPILATION_MCP_REAL_CONFIG') and DLL.exists(), 'private DAO inputs not requested')
class RealDaoSmoke(unittest.TestCase):
    def test_all_inventory_and_retained_checks(self):
        client = Client(os.environ['DECOMPILATION_MCP_REAL_CONFIG'])
        try:
            opened = client.call('project_open', project_id='dao')
            self.assertEqual(opened['inventory_identities'], 27555)
            cursor = None
            identities = set()
            builds = {}
            while True:
                page = client.call('function_query', project_id='dao', limit=100, cursor=cursor)
                for row in page['items']:
                    self.assertNotIn(row['function_id'], identities)
                    identities.add(row['function_id'])
                    if row['retained_build_count']:
                        inspected = client.call('function_inspect', project_id='dao', function_id=row['function_id'], source_limit=100)
                        self.assertLessEqual(len(inspected['retained_source']['source']), 100)
                        self.assertEqual(inspected['retained_source']['comparison'], 'unchecked')
                        builds[row['rva']] = inspected['builds']
                cursor = page['next_cursor']
                if cursor is None:
                    break
            self.assertEqual(len(identities), 27555)
            results = []
            for rva, rows in builds.items():
                for row in rows:
                    submitted = client.call('candidate_check', project_id='dao', build_id=row['build_id'],
                                            idempotency_key='real-smoke-' + str(time.time_ns()))
                    result = wait_job(client, submitted['job_id'])
                    results.append({'rva': rva, **result})
            print('REAL_DAO_SMOKE=' + json.dumps(results, sort_keys=True))
            by_rva = {row['rva']: row for row in results}
            self.assertEqual(by_rva['0x000b63f0']['result']['status'], 'full_match')
            self.assertEqual(by_rva['0x000c57a0']['result']['status'], 'mismatch')
            if '0x00075040' in by_rva:
                self.assertEqual(by_rva['0x00075040']['result']['backend'], 'i386_coff_eh_graph_v1')
                self.assertEqual(by_rva['0x00075040']['result']['status'], 'full_match')
        finally:
            client.close()

    def test_tampered_retained_builds_cannot_match(self):
        original_config = json.loads(Path(os.environ['DECOMPILATION_MCP_REAL_CONFIG']).read_text())
        project = original_config['projects'][0]
        for mutation in ('source', 'object', 'flags', 'compiler', 'missing_object'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp).resolve()
                build = root / 'retained'
                shutil.copytree(project['builds'][0]['folder'], build)
                if mutation in ('source', 'object'):
                    path = build / ('candidate.cpp' if mutation == 'source' else 'candidate.obj')
                    path.write_bytes(path.read_bytes() + b'!')
                elif mutation == 'missing_object':
                    (build / 'candidate.obj').unlink()
                elif mutation == 'flags':
                    receipt = json.loads((build / 'run.json').read_text())
                    receipt['flags'] = ['/unsafe-fake']
                    (build / 'run.json').write_text(json.dumps(receipt))
                elif mutation == 'compiler':
                    receipt = json.loads((build / 'compiler.json').read_text(encoding='utf-8-sig'))
                    receipt['sha256'] = 'f' * 64
                    (build / 'compiler.json').write_text(json.dumps(receipt))
                isolated = json.loads(json.dumps(original_config))
                isolated['state_root'] = str(root / 'state')
                isolated['projects'][0]['builds'] = [{**project['builds'][0], 'folder': str(build)}]
                isolated['projects'][0]['allowed_roots'].append(str(root))
                config = root / 'registry.json'
                config.write_text(json.dumps(isolated))
                client = Client(config)
                try:
                    query = client.call('function_query', project_id='dao', name_contains='FUN_004b63f0')
                    function = query['items'][0]['function_id']
                    selected = client.call('function_inspect', project_id='dao', function_id=function)['builds'][0]
                    submitted = client.call('candidate_check', project_id='dao', build_id=selected['build_id'], idempotency_key='negative')
                    done = wait_job(client, submitted['job_id'])
                    self.assertEqual(done['state'], 'completed')
                    self.assertEqual(done['result']['status'], 'inconclusive')
                finally:
                    client.close()


if __name__ == '__main__':
    unittest.main()

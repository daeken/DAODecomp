"""Generic transport/queue fixtures; no proprietary compiler or VM is invoked."""
from contextlib import closing
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


transport = load('replayable_transport', ROOT / 'tools/decompilation-mcp/replayable_transport.py')
pipeline = load('transport_pipeline_fixture', ROOT / 'tests/test_replayable_pipeline.py')
sha = lambda data: hashlib.sha256(data).hexdigest()


def quiet():
    return dict(guest_base_exists=True, share_base_exists=True, workspace_exists=False,
                source_transfer_exists=False, diagnostic_pid=42,
                processes=[dict(name='powershell.exe', pid=42, has_command_line=True, has_executable=True)])


class TransportGuardTests(unittest.TestCase):
    def test_only_explicit_absence_and_identified_single_probe_is_quiescent(self):
        transport.validate_probe(quiet())
        for change in (dict(guest_base_exists=False), dict(share_base_exists=False),
                       dict(workspace_exists=True), dict(source_transfer_exists=True),
                       dict(processes=[]), dict(processes=[dict(name='cl.exe', pid=42)]),
                       dict(diagnostic_pid=43)):
            with self.subTest(change=change), self.assertRaises(ValueError):
                transport.validate_probe(dict(quiet(), **change))
        for field in ('workspace_exists', 'source_transfer_exists'):
            data = quiet()
            del data[field]
            with self.assertRaises(ValueError):
                transport.validate_probe(data)

    def test_any_other_launcher_or_incomplete_provenance_refuses(self):
        for name in ('cl.exe', 'c2.exe', 'link.exe', 'cmd.exe', 'powershell.exe'):
            data = quiet()
            data['processes'].append(dict(name=name, pid=99))
            with self.subTest(name=name), self.assertRaises(ValueError):
                transport.validate_probe(data)
        for flag in ('has_command_line', 'has_executable'):
            data = quiet()
            data['processes'][0][flag] = False
            with self.assertRaises(ValueError):
                transport.validate_probe(data)

    def test_launch_protocol_copies_missing_input_before_any_compiler(self):
        profile = dict(guest_root=r'C:\Fixture', guest_transfer_root=r'\\Fixture\Share', vcvars=r'C:\Compiler\vcvars.cmd')
        guest, shared, batch, script = transport.rendered_scripts(profile, 'coff-job-' + 'a' * 32, ['/c', '/O2'])
        self.assertEqual(guest, profile['guest_root'] + '\\coff-job-' + 'a' * 32)
        self.assertIn(shared.encode(), script)
        self.assertLess(script.index(b'Copy-Item -Recurse'), script.index(b'& cmd.exe'))
        self.assertIn(b'/c /O2 /FAs', batch)
        self.assertIn(b'$buildExit | Set-Content -Encoding ASCII build-exit.txt', script)


@unittest.skipUnless(pipeline.stdio.DLL.exists(), 'build C# component first')
class TransportBoundaryTests(unittest.TestCase):
    setUp = pipeline.PipelineBoundaryTests.setUp
    tearDown = pipeline.PipelineBoundaryTests.tearDown
    connect = pipeline.PipelineBoundaryTests.connect
    submit = pipeline.PipelineBoundaryTests.submit

    def seeded_unknown(self, health=None, delay=0):
        # Controlled persistence fixture, never source/object acceptance evidence.
        health = quiet() if health is None else health
        self.cli = self.root / 'probe-cli'
        self.cli.write_text('#!' + sys.executable + '\nimport json,time\ntime.sleep(' + str(delay) + ')\nprint(' + repr(json.dumps(health)) + ')\n')
        self.cli.chmod(0o700)
        (self.root / 'unused.lock').write_bytes(b'')
        self.transfer = self.root / 'transfer'
        self.transfer.mkdir()
        helper = ROOT / 'rapid_object/build.py'
        self.profile = dict(protocol='prlctl-sync-copy-v1', vm_name='Fixture', executable=str(self.cli),
                            guest_root=r'C:\Fixture', guest_transfer_root=r'\\Fixture\Share',
                            host_transfer_root=str(self.transfer), vcvars=r'C:\Compiler\vcvars.cmd',
                            build_helper=str(helper), build_helper_sha256=sha(helper.read_bytes()),
                            vm_helper=str(ROOT / 'rapid_native/pipeline.py'), vm_helper_sha256=sha((ROOT / 'rapid_native/pipeline.py').read_bytes()))
        profile_path = self.root / 'transport.json'
        profile_path.write_text(json.dumps(self.profile))
        config = json.loads(self.config.read_text())
        config['projects'][0]['replayable']['transport_config'] = str(profile_path)
        config['projects'][0]['compiler_flags'] = ['/c', '/O2']
        self.config.write_text(json.dumps(config))
        self.client = self.connect()
        first = self.submit('seeded-transport-unknown')
        pipeline.stdio.wait_job(self.client, first['job_id'])
        self.target = first['job_id']
        folder = self.root / 'attempts' / self.target
        (folder / 'build').mkdir(exist_ok=True)
        source = b'open persistence fixture, not recovered source\n'
        (folder / 'candidate.cpp').write_bytes(source)
        self.name = 'coff-job-' + 'a' * 32
        guest, _, batch, script = transport.rendered_scripts(self.profile, self.name, ['/c', '/O2'])
        (folder / 'build/build.cmd').write_bytes(batch)
        (folder / 'build/run.ps1').write_bytes(script)
        build = dict(vm='Fixture', vm_workspace=guest, source_sha256=sha(source), compiler=None,
                     object_sha256=None, flags=['/c', '/O2'], exit_code=255)
        (folder / 'build/run.json').write_text(json.dumps(build))
        for name in ('transport.stdout', 'transport.stderr'):
            (folder / 'build' / name).write_bytes(b'open fixture transport outcome unknown')
        self.original_result = dict(status='external_outcome_unknown', blocker='compiler_exit_marker_missing_no_automatic_retry', build=build)
        with closing(sqlite3.connect(self.root / 'state/jobs.sqlite3')) as db, db:
            request = json.loads(db.execute('SELECT request FROM jobs WHERE id=?', (self.target,)).fetchone()[0])
            request['compile'] = True
            request['expected_source_sha256'] = sha(source)
            self.original_request = json.dumps(request)
            db.execute('UPDATE jobs SET request=?,result=? WHERE id=?', (self.original_request, json.dumps(self.original_result), self.target))
            db.execute("UPDATE replayable_frontier SET status='external_outcome_unknown' WHERE job=?", (self.target,))
        (folder / 'request.json').write_text(self.original_request)
        (folder / 'result.json').write_text(json.dumps(self.original_result))
        self.target_folder = folder
        return first

    def abandon(self, token='abandon-fixture'):
        return self.client.call('replayable_abandon_unknown', project_id='open', unknown_job_id=self.target,
                                idempotency_key=token)

    def barrier_status(self):
        with closing(sqlite3.connect(self.root / 'state/jobs.sqlite3')) as db:
            return db.execute('SELECT status FROM replayable_frontier WHERE job=?', (self.target,)).fetchone()[0]

    def test_unregistered_profile_and_unknown_identity_refuse(self):
        with self.assertRaises(ValueError):
            self.client.call('replayable_abandon_unknown', project_id='open', unknown_job_id='a' * 32, idempotency_key='missing')
        for value in ('', 'not-a-job', '../bad'):
            with self.assertRaises(ValueError):
                self.client.call('replayable_abandon_unknown', project_id='open', unknown_job_id=value, idempotency_key='bad')

    @unittest.skipIf(os.name == 'nt', 'actual supported Parallels host requires POSIX executable/lock semantics')
    def test_nonaccepting_abandonment_preserves_unknown_and_allows_explicit_new_attempt(self):
        self.seeded_unknown()
        submitted = self.abandon()
        done = pipeline.stdio.wait_job(self.client, submitted['job_id'])
        self.assertEqual(done['result']['status'], 'abandoned_nonaccepting', done)
        self.assertFalse(done['result']['match'])
        self.assertFalse(done['result']['automatic_retry'])
        self.assertEqual(self.barrier_status(), 'abandoned_nonaccepting')
        self.assertEqual(self.client.call('job_get', job_id=self.target)['result'], self.original_result)
        self.assertEqual(json.loads((self.target_folder / 'result.json').read_text()), self.original_result)
        self.assertEqual(self.abandon()['job_id'], submitted['job_id'])
        state = self.client.call('replayable_status', project_id='open')
        self.assertEqual(state['new_pipeline_full_matches'], 0)
        self.assertEqual(state['regression_full_matches'], 0)
        retry = self.submit('explicit-new-attempt-after-nonaccepting-abandonment')
        self.assertNotEqual(retry['job_id'], self.target)
        self.assertEqual(retry['rva'], 0x1000)
        pipeline.stdio.wait_job(self.client, retry['job_id'])
        self.assertEqual(self.client.call('job_get', job_id=self.target)['result'], self.original_result)

    def test_running_target_wrong_project_and_changed_bindings_never_release(self):
        self.seeded_unknown()
        config = json.loads(self.config.read_text())
        other = dict(config['projects'][0], id='other')
        config['projects'].append(other)
        self.config.write_text(json.dumps(config))
        client = self.connect()
        with self.assertRaises(ValueError):
            client.call('replayable_abandon_unknown', project_id='other', unknown_job_id=self.target, idempotency_key='wrong-project')
        with closing(sqlite3.connect(self.root / 'state/jobs.sqlite3')) as db, db:
            db.execute("UPDATE jobs SET state='running' WHERE id=?", (self.target,))
        with self.assertRaises(ValueError):
            self.abandon('running-not-abandonable')
        self.assertEqual(self.barrier_status(), 'external_outcome_unknown')
        with closing(sqlite3.connect(self.root / 'state/jobs.sqlite3')) as db, db:
            db.execute("UPDATE jobs SET state='completed' WHERE id=?", (self.target,))
        self.dll.write_bytes(b'changed source/runtime binding')
        with self.assertRaises(ValueError):
            self.abandon('changed-old-inputs')
        self.assertEqual(self.barrier_status(), 'external_outcome_unknown')

    @unittest.skipIf(os.name == 'nt', 'actual supported Parallels host requires POSIX executable/lock semantics')
    def test_inconclusive_probe_retains_barrier_and_history_with_idempotent_retry(self):
        self.seeded_unknown(dict(quiet(), workspace_exists=True))
        submitted = self.abandon()
        done = pipeline.stdio.wait_job(self.client, submitted['job_id'])
        self.assertEqual(done['result']['status'], 'inconclusive')
        self.assertEqual(self.barrier_status(), 'external_outcome_unknown')
        self.assertEqual(self.abandon()['job_id'], submitted['job_id'])
        with self.assertRaises(ValueError):
            self.submit('barrier-still-active')
        self.assertEqual(self.client.call('job_get', job_id=self.target)['result'], self.original_result)
        another = self.abandon('explicit-read-only-reconciliation-retry')
        self.assertNotEqual(another['job_id'], submitted['job_id'])
        pipeline.stdio.wait_job(self.client, another['job_id'])
        self.assertEqual(self.barrier_status(), 'external_outcome_unknown')

    @unittest.skipIf(os.name == 'nt', 'actual supported Parallels host requires POSIX executable/lock semantics')
    def test_source_changes_during_probe_retain_barrier(self):
        self.seeded_unknown(delay=.5)
        submitted = self.abandon()
        (self.target_folder / 'candidate.cpp').write_bytes(b'changed during read-only request')
        done = pipeline.stdio.wait_job(self.client, submitted['job_id'])
        self.assertEqual(done['result']['status'], 'inconclusive')
        self.assertEqual(self.barrier_status(), 'external_outcome_unknown')
        self.assertEqual(self.client.call('job_get', job_id=self.target)['result'], self.original_result)

    @unittest.skipIf(os.name == 'nt', 'actual supported Parallels host requires POSIX executable/lock semantics')
    def test_present_host_input_retained_artifact_or_changed_script_refuses(self):
        self.seeded_unknown()
        bad = self.target_folder / 'build/candidate.obj'
        for token, path in [('host', self.transfer / self.name), ('object', bad), ('script', self.target_folder / 'build/run.ps1')]:
            original = path.read_bytes() if path.is_file() else None
            path.write_bytes(b'unexpected or changed retained input')
            submitted = self.abandon('guard-' + token)
            done = pipeline.stdio.wait_job(self.client, submitted['job_id'])
            self.assertEqual(done['result']['status'], 'inconclusive')
            self.assertEqual(self.barrier_status(), 'external_outcome_unknown')
            if original is None:
                path.unlink()
            else:
                path.write_bytes(original)

    @unittest.skipIf(os.name == 'nt', 'actual supported Parallels host requires POSIX executable/lock semantics')
    def test_shared_vm_lock_busy_refuses_without_releasing_unknown(self):
        import fcntl
        self.seeded_unknown()
        with (self.root / 'unused.lock').open('r+') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            submitted = self.abandon('busy-shared-vm-lock')
            done = pipeline.stdio.wait_job(self.client, submitted['job_id'])
            self.assertEqual(done['result']['status'], 'inconclusive')
            self.assertEqual(self.barrier_status(), 'external_outcome_unknown')
        self.assertEqual(self.client.call('job_get', job_id=self.target)['result'], self.original_result)

    @unittest.skipIf(os.name == 'nt', 'actual supported Parallels host requires POSIX executable/lock semantics')
    def test_reconciliation_serializes_and_retains_barrier_until_atomic_completion(self):
        self.seeded_unknown(delay=.5)
        first = self.abandon('first-reconciliation')
        with self.assertRaises(ValueError):
            self.abandon('must-not-run-concurrent-reconciliation')
        with self.assertRaises(ValueError):
            self.submit('must-not-dispatch-during-reconciliation')
        self.assertEqual(self.barrier_status(), 'external_outcome_unknown')
        done = pipeline.stdio.wait_job(self.client, first['job_id'])
        self.assertEqual(done['result']['status'], 'abandoned_nonaccepting', done)
        self.assertEqual(self.barrier_status(), 'abandoned_nonaccepting')
        self.assertEqual(self.client.call('job_get', job_id=self.target)['result'], self.original_result)

    @unittest.skipIf(os.name == 'nt', 'actual supported Parallels host requires POSIX executable/lock semantics')
    def test_live_target_claim_never_releases_barrier(self):
        import fcntl
        self.seeded_unknown()
        with (self.root / 'state' / (self.target + '.lock')).open('r+') as claim:
            fcntl.flock(claim, fcntl.LOCK_EX | fcntl.LOCK_NB)
            submitted = self.abandon('target-still-exiting')
            done = pipeline.stdio.wait_job(self.client, submitted['job_id'])
            self.assertEqual(done['result']['status'], 'inconclusive', done)
            self.assertEqual(self.barrier_status(), 'external_outcome_unknown')
        self.assertEqual(self.client.call('job_get', job_id=self.target)['result'], self.original_result)

    def test_missing_target_claim_is_not_recreated_as_ownership_evidence(self):
        self.seeded_unknown()
        claim = self.root / 'state' / (self.target + '.lock')
        claim.unlink()
        submitted = self.abandon('missing-original-claim')
        done = pipeline.stdio.wait_job(self.client, submitted['job_id'])
        self.assertEqual(done['result']['status'], 'inconclusive', done)
        self.assertEqual(self.barrier_status(), 'external_outcome_unknown')
        self.assertFalse(claim.exists())
        self.assertEqual(self.client.call('job_get', job_id=self.target)['result'], self.original_result)

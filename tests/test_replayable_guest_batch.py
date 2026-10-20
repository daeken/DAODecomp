import os
try:
    import fcntl
except ImportError:
    fcntl = None
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from tools.replayable import guest_batch as g


@unittest.skipUnless(os.name == 'posix', 'guest dispatch requires POSIX flock host')
class GuestBatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        (self.root/'bridge').mkdir()
        (self.root/'lock').touch()
        self.source = self.root/'source.cpp'
        self.source.write_text('int f() { return 4; }\n')
        self.hash = g.digest(self.source.read_bytes())
        self.compiler = 'a'*64
        self.profile = dict(protocol='prlctl-sync-copy-v1', vm_name='Windows 11',
            guest_root=r'C:\pilot', guest_transfer_root=r'\\Mac\Home\bridge',
            host_transfer_root=str(self.root/'bridge'), vcvars=r'C:\VC8\vcvars.cmd', shared_vm_lock=str(self.root/'lock'))

    def prepare(self, items=None):
        return g.prepare(items or [g.Item('one', self.source, self.hash, g.FLAGS)],
                         self.root/'output', self.profile, self.compiler)

    def fixture(self, batch, exit_code=0):
        m = g.read_json(batch.output/'manifest.json')
        entries=[]
        for item in m['items']:
            d=batch.transfer/item['id']
            start=dict(schema=1,nonce=batch.nonce,id=item['id'],source_sha256=item['source_sha256'])
            (d/'start.json').write_bytes(g.canonical(start))
            obj=None
            if exit_code==0:
                (d/'candidate.obj').write_bytes(b'object');obj=g.digest(b'object')
            receipt=dict(start,flags=item['flags'],compiler_sha256=self.compiler,exit_code=exit_code,object_sha256=obj,cl_seconds=.1)
            (d/'exit.json').write_bytes(g.canonical(receipt));entries.append(receipt)
        (batch.transfer/'compiler.json').write_bytes(g.canonical(dict(path=r'C:\VC8\bin\cl.exe',sha256=self.compiler,file_version='version')))
        (batch.transfer/'completed.json').write_bytes(g.canonical(dict(schema=1,nonce=batch.nonce,manifest_sha256=batch.manifest_sha256,items=entries)))

    def execute(self,batch,callback):
        with (self.root/'lock').open('r+')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            return g.execute(batch,lock_fd=lock.fileno(),authorization='persisted-caller-decision',run_vm=callback)

    def successful(self,batch,exit_code=0):
        def run(*args,**kwargs):
            self.fixture(batch,exit_code)
            return subprocess.CompletedProcess([], 1 if exit_code else 0,b'',b'')
        return self.execute(batch,run)

    def test_complete_success_and_no_replay(self):
        b=self.prepare();result=self.successful(b)
        self.assertTrue(result['succeeded']);self.assertEqual(result['items'][0]['exit_code'],0)
        self.assertTrue(b.transfer.exists())
        with self.assertRaises((ValueError,FileExistsError)):
            self.execute(b,lambda *a,**k:self.fail('replayed'))

    def test_nonzero_is_known_failure_not_success(self):
        b=self.prepare();result=self.successful(b,2)
        self.assertFalse(result['succeeded']);self.assertEqual(result['items'][0]['exit_code'],2)

    def test_timeout_preserves_and_consumes(self):
        b=self.prepare()
        def run(*a,**k):raise subprocess.TimeoutExpired('vm',1)
        with self.assertRaises(g.AmbiguousOutcome):self.execute(b,run)
        self.assertTrue((b.output/'dispatch-start.json').exists());self.assertTrue((b.output/'ambiguous.json').exists())
        with self.assertRaises(FileExistsError):self.execute(b,run)
        self.assertTrue(b.transfer.exists())

    def test_unheld_or_wrong_lock_and_missing_authorization(self):
        b=self.prepare()
        with (self.root/'lock').open('r+')as lock:
            with self.assertRaisesRegex(ValueError,'not_held'):g.check_lock(b,lock.fileno())
            fcntl.flock(lock,fcntl.LOCK_SH)
            with self.assertRaisesRegex(ValueError,'exclusive_lock'):g.check_lock(b,lock.fileno())
            fcntl.flock(lock,fcntl.LOCK_EX)
            with (self.root/'source.cpp').open('r')as wrong:
                with self.assertRaisesRegex(ValueError,'wrong_lock'):g.check_lock(b,wrong.fileno())
            with (self.root/'lock').open('r+')as unheld:
                with self.assertRaisesRegex(ValueError,'does_not_hold'):g.check_lock(b,unheld.fileno())
            with self.assertRaisesRegex(ValueError,'authorization'):g.execute(b,lock_fd=lock.fileno(),authorization='',run_vm=None)

    def test_invalid_inputs_and_injection(self):
        valid=g.Item('one',self.source,self.hash,g.FLAGS)
        for items in [[],[valid]*2,[valid]*17,[g.Item('../evil',self.source,self.hash,g.FLAGS)],[g.Item('con',self.source,self.hash,g.FLAGS)],
                      [g.Item('one',self.source,'b'*64,g.FLAGS)],
                      [g.Item('one',self.source,self.hash,('/c','/Foescape & echo yes'))]]:
            with self.subTest(items=items),self.assertRaises(ValueError):
                g.prepare(items,self.root/'output',self.profile,self.compiler)
        for value in [r'C:\VC8\x & echo foo',r'C:\%PATH%\vcvars.cmd',r'C:\x\..\bad',r'C:\x\a"b']:
            with self.subTest(value=value),self.assertRaises(ValueError):g.windows_path(value)

    def test_changed_prepared_input_no_dispatch(self):
        b=self.prepare();(b.transfer/'one'/'candidate.cpp').write_text('changed')
        with self.assertRaisesRegex(ValueError,'changed_item'):self.execute(b,lambda *a,**k:self.fail('dispatch'))
        self.assertFalse((b.output/'dispatch-start.json').exists())

    def test_missing_stale_malformed_duplicate_partial_and_hash_receipts(self):
        b=self.prepare();self.successful(b)
        files={p:p.read_bytes()for p in b.output.rglob('*')if p.is_file()}
        def mutate(path,change):
            value=g.read_json(path);change(value);path.write_bytes(g.canonical(value))
        cases=[lambda:(b.output/'one'/'exit.json').unlink(),
            lambda:mutate(b.output/'completed.json',lambda x:x.update(nonce='stale')),
            lambda:(b.output/'completed.json').write_text('{"schema":1,"schema":1}'),
            lambda:mutate(b.output/'completed.json',lambda x:x['items'].append(x['items'][0])),
            lambda:mutate(b.output/'completed.json',lambda x:x.update(items=[])),
            lambda:(b.output/'one'/'exit.json').write_text(''),
            lambda:(b.output/'one'/'candidate.obj').write_bytes(b'wrong'),
            lambda:(b.output/'one'/'candidate.cpp').write_text('wrong'),
            lambda:mutate(b.output/'compiler.json',lambda x:x.update(sha256='b'*64)),
            lambda:mutate(b.output/'one'/'exit.json',lambda x:x.update(exit_code=True)),
            lambda:(b.output/'one'/'start.json').unlink()]
        for i,case in enumerate(cases):
            for p,data in files.items():p.write_bytes(data)
            case()
            with self.subTest(case=i),self.assertRaises(g.AmbiguousOutcome):g.collect(b,0)
        for p,data in files.items():p.write_bytes(data)
        with self.assertRaises(g.AmbiguousOutcome):g.collect(b,1)

    def test_missing_envelope_object_alone_cannot_succeed(self):
        b=self.prepare()
        def run(*a,**k):
            (b.transfer/'one'/'candidate.obj').write_bytes(b'object')
            return subprocess.CompletedProcess([],0,b'',b'')
        with self.assertRaises(g.AmbiguousOutcome):self.execute(b,run)

    def test_script_changed_in_both_places_rejected(self):
        b=self.prepare()
        for d in (b.transfer,b.output):(d/'run.ps1').write_text('changed')
        with self.assertRaisesRegex(ValueError,'script_changed'):self.execute(b,lambda *a,**k:self.fail('dispatch'))

    def test_script_single_setup_fixed_compiler_and_atomic_receipts(self):
        b=self.prepare();s=(b.output/'run.ps1').read_text()
        self.assertEqual(s.count('call "C:\\VC8\\vcvars.cmd"'),1)
        self.assertIn("Save 'start.json'",s);self.assertIn("Save 'exit.json'",s);self.assertIn("Save 'completed.json'",s)
        self.assertIn('implicit_compiler_flags_unsupported',s)

if __name__=='__main__':unittest.main()

"""Transport and process-lifetime tests use real faulting child processes."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from tools.daodecomp.batch import (MAX_BATCH_CASES, MAX_TOTAL_CASES, compare_batch, fresh_call, invoke_batches)
from tools.daodecomp.harness import canonical, compare, digest

ROOT=Path(__file__).resolve().parents[1]
WORKER=ROOT/'tests/support/batch_fault_runner.py'
CONTRACT={'schema_version':1,'function_id':'test:batch','kind':'synthetic','inputs':{'value':'u32'},'return_type':'u32','memory':{'bytes':4},'calls':[],'preconditions':'Test-only small integer'}
CASES=[{'id':'one','inputs':{'value':1}},{'id':'two','inputs':{'value':2}}]

def command(mode,*args): return [sys.executable,'-B',str(WORKER),mode,*map(str,args)]

@unittest.skipUnless(os.name=='posix' and hasattr(os,'fork'),'fresh-child batching is POSIX only')
class BatchTests(unittest.TestCase):
    def invoke(self,mode,cases=CASES,**options):
        options.setdefault('timeout',.15)
        return invoke_batches(command(mode),cases,CONTRACT,**options)

    def test_success_exact_memory_and_counts(self):
        runs,count=self.invoke('normal',batch_size=1)
        self.assertEqual(count,{'supervisor_processes':1,'case_processes':2})
        self.assertEqual([r['observation']['return'] for r in runs],[1,2])
        self.assertTrue(all(r['observation']['memory']=={'bytes':'00000000'} for r in runs))

    def test_fresh_globals_and_independent_repetitions(self):
        cases=[{'id':str(i),'inputs':{'value':1}} for i in range(5)]
        report=compare_batch(CONTRACT,cases,command('stateful'),command('normal'))
        self.assertEqual(report['status'],'corpus_pass')
        self.assertEqual(len(report['execution_backend']['process_counts']),4)
        self.assertTrue(all(c['case_processes']==5 for c in report['execution_backend']['process_counts']))

    def test_status_ordering_real_nondeterminism_and_mismatch(self):
        for oracle,candidate,status in [('pid','pid','oracle_nondeterministic'),('normal','pid','candidate_nondeterministic'),('normal','mismatch','mismatch'),('normal','memory-corrupt','mismatch'),('missing','missing','runner_error')]:
            with self.subTest(status=status,side=candidate):
                report=compare_batch(CONTRACT,CASES,command(oracle),command(candidate))
                self.assertEqual(report['status'],'failed')
                self.assertEqual({r['status'] for r in report['cases']},{status})
                self.assertTrue(all('case' in r and 'oracle' in r and 'candidate' in r for r in report['cases']))

    def test_actual_case_crash_timeout_exception_and_output_faults(self):
        expected={'crash':'runner_exit','hang':'timeout','raise':'runner_exit','missing':'invalid_runner','stdout-cap':'oversized_observation','stderr-cap':'oversized_stderr','duplicate-json':'invalid_runner','wrong-id':'invalid_batch_response','bool-return':'invalid_batch_response'}
        for mode,error in expected.items():
            with self.subTest(mode=mode):
                runs,_=self.invoke(mode)
                self.assertEqual(runs[0]['error'],error)
                self.assertTrue(all('observation' not in r for r in runs))

    def test_actual_forged_transport_responses_fail_closed(self):
        for mode in ('reorder','duplicate','wrong-batch','count','process-count','missing','extra'):
            with self.subTest(mode=mode):
                runs,_=self.invoke('frame-'+mode)
                self.assertTrue(all(r['error']=='invalid_batch_response' for r in runs))
        runs,_=self.invoke('frame-output-cap',output_cap=1024)
        self.assertTrue(all(r['error']=='oversized_worker_output' for r in runs))

    def assert_not_running(self,pid):
        # An orphan may briefly remain a zombie pending the OS reaper; it must not
        # remain runnable or sleeping after process-group cleanup.
        deadline=time.monotonic()+2
        while True:
            status=subprocess.run(['ps','-o','stat=','-p',str(pid)],capture_output=True,text=True).stdout.strip()
            if not status or status.startswith('Z'): return
            if time.monotonic()>deadline: self.fail(f'descendant {pid} remains alive: {status}')
            time.sleep(.01)

    def test_descendants_killed_on_success_timeout_worker_crash_and_outer_timeout(self):
        for mode in ('descendant-success','descendant-hang','worker-crash','outer-timeout'):
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as directory:
                marker=Path(directory)/'pid'
                actual='descendant-hang' if mode=='outer-timeout' else mode
                options={'worker_timeout':.1} if mode=='outer-timeout' else {}
                if mode=='outer-timeout': options['worker_timeout']=.12
                runs,_=invoke_batches(command(actual,marker),CASES[:1],CONTRACT,timeout=.15,**options)
                self.assertTrue(marker.exists(),'fault fixture did not start its descendant')
                self.assert_not_running(int(marker.read_text()))
                if mode=='descendant-success': self.assertIn('observation',runs[0])
                elif mode=='outer-timeout': self.assertEqual(runs[0]['error'],'worker_timeout')
                else: self.assertIn('error',runs[0])

    def test_artifact_mutation_cannot_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact=Path(directory)/'artifact';artifact.write_text('before')
            report=compare_batch(CONTRACT,CASES,command('normal'),command('artifact',artifact),artifacts=[artifact])
            self.assertEqual({r['status'] for r in report['cases']},{'corpus_pass'})
            self.assertFalse(report['artifacts_unchanged']);self.assertEqual(report['status'],'failed')

    def test_limits_and_invalid_corpora(self):
        for kwargs in ({'batch_size':0},{'batch_size':129},{'batch_size':True},{'timeout':0},{'timeout':float('nan')},{'worker_timeout':-1}):
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError): self.invoke('normal',**kwargs)
        for cases in ([],CASES+CASES,[{'id':'a','inputs':{'value':True}}]):
            with self.assertRaises(ValueError): self.invoke('normal',cases=cases)
        with self.assertRaises(ValueError):
            self.invoke('normal',cases=[{'id':str(i),'inputs':{'value':1}} for i in range(MAX_TOTAL_CASES+1)])
        with self.assertRaises(ValueError): compare_batch(CONTRACT,CASES,command('normal'),command('normal'),repeats=1)

    def test_actual_batch_boundary(self):
        cases=[{'id':str(i),'inputs':{'value':i}} for i in range(MAX_BATCH_CASES+1)]
        runs,count=self.invoke('normal',cases=cases)
        self.assertEqual(len(runs),129);self.assertEqual(count['case_processes'],129)
        self.assertEqual([r['observation']['return'] for r in runs],list(range(129)))

    def test_supervisor_rejects_bad_input_frames(self):
        request={'schema_version':1,'function_id':CONTRACT['function_id'],'case':CASES[0]}
        valid={'schema_version':1,'batch_id':0,'requests':[request]}
        malformed=[b'{}\n',(canonical(valid)+'\n'+canonical(valid)+'\n').encode(),b'{"schema_version":1,"schema_version":1}\n',b'{"schema_version":1.0}\n',b'x'*262145]
        malformed.append((canonical(dict(valid,requests=[request]*129))+'\n').encode())
        for raw in malformed:
            with self.subTest(size=len(raw)):
                done=subprocess.run(command('normal'),input=raw,capture_output=True,timeout=3)
                self.assertNotEqual(done.returncode,0)

    def test_actual_emulator_budget_and_footprint_failures(self):
        try:
            import unicorn
        except ImportError:
            self.skipTest('Unicorn not installed')
        from tools.daodecomp.memory import execute_memory
        for code in (b"\xeb\xfe", b"\xa1\x00\x00\x00\x02\xc3"):
            with self.subTest(code=code.hex()):
                run=fresh_call(lambda _:execute_memory(0x401000,code,bytes(512),registers={},stack_arguments=[],readable=[],writable=[],stack_cleanup=0,instruction_budget=20),{},timeout=.5)
                self.assertEqual(run['error'],'runner_exit')

    def test_pair_freezer_batch_commands_and_review_closure(self):
        from tools import freeze_indexed_fields_pair as freeze
        modes={mode:freeze.commands(mode) for mode in ('single','batch')}
        self.assertEqual(modes['single']['build'],modes['batch']['build'])
        for stage in ('public','heldout','negative'):
            fast=modes['batch'][stage][0]['argv'];slow=modes['single'][stage][0]['argv']
            self.assertIn('--execution',fast);self.assertEqual(fast[fast.index('--execution')+1],'batch')
            self.assertNotIn('--execution',slow)
            self.assertEqual(modes['batch'][stage][0]['reports'],modes['single'][stage][0]['reports'])
        self.assertTrue(freeze.BATCH_REVIEW_REQUIRED <= freeze.review_required('batch'))
        self.assertFalse(freeze.BATCH_REVIEW_REQUIRED & freeze.review_required('single'))
        self.assertTrue(freeze.BATCH_REVIEW_REQUIRED <= set(freeze.required_files(ROOT,'batch')))
        self.assertTrue(freeze.BATCH_REVIEW_REQUIRED <= set(freeze.prompt_evidence('review.json','batch')))
        with tempfile.TemporaryDirectory() as directory:
            review=Path(directory)/'review.json'
            review.write_text(json.dumps({'decision':'approve','reviewed_artifacts_sha256':{name:'not-a-hash' for name in freeze.REVIEW_REQUIRED}}))
            with self.assertRaisesRegex(ValueError,'lacks required'):
                freeze.approved_review(ROOT,review,'batch')

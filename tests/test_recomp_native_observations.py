"""Outcome selection for concurrent native startup logs; not game acceptance."""
import unittest
import hashlib
import json
from pathlib import Path
import tempfile
from unittest import mock
from tools.recomp_native import execute_native, native_observation, native_missing_entries, read_native_events


class NativeObservationTests(unittest.TestCase):
    def test_thread_return_does_not_hide_a_failure(self):
        failure=dict(event='native_startup_frontier',pc=0x408260,reason='untranslated guest code/import target')
        report=dict(events=[failure,dict(event='native_translated_return',module=0x10000000,reason=2,eax=1)])
        self.assertEqual(native_observation(report),failure)

    def test_timeout_never_becomes_a_code_selection(self):
        result=native_observation(dict(timed_out=True,events=[dict(event='native_startup_frontier',pc=0x408260,reason='untranslated guest code/import target')]))
        self.assertEqual(result['event'],'native_observation_timeout')
        self.assertNotIn('pc',result)
        self.assertFalse(result['game_acceptance'])

    def test_main_return_is_distinguished_from_dll_teardown(self):
        main=dict(event='native_translated_return',module=0x400000,eax=0)
        self.assertEqual(native_observation(dict(events=[main,dict(event='native_translated_return',module=0x10000000,reason=0,eax=1)])),main)

    def test_only_dll_thread_attach_is_incomplete(self):
        result=native_observation(dict(events=[dict(event='native_translated_return',module=0x10000000,reason=2,eax=1)]))
        self.assertEqual(result['event'],'native_incomplete_observation')
        self.assertFalse(result['game_acceptance'])

    def test_concurrent_missing_bodies_are_deduplicated_without_trace_guesses(self):
        first=dict(event='native_callback_frontier',pc=0x413bd0,reason='untranslated guest function target')
        second=dict(event='native_callback_frontier',pc=0x4c0b00,reason='untranslated guest code/import target')
        report=dict(events=[dict(event='native_callback_entry',pc=0x400001),first,second,dict(first),
                            dict(event='native_callback_return',pc=0x400002)])
        self.assertEqual(native_missing_entries(report),[first,second])
        self.assertEqual(native_missing_entries(dict(report,timed_out=True)),[])

    def test_runtime_failure_cannot_be_hidden_by_another_threads_code_gap(self):
        runtime=dict(event='native_callback_frontier',pc=0x400001,reason='native callback returned incomplete CPU state')
        missing=dict(event='native_callback_frontier',pc=0x413bd0,reason='untranslated guest function target')
        self.assertEqual(native_observation(dict(events=[runtime,missing])),runtime)
        self.assertEqual(native_missing_entries(dict(events=[runtime,missing])),[missing])

    def test_missing_pc_must_be_concrete_and_nonwrapping(self):
        for pc in [None,True,0,-1,0x100000000,'0x413bd0']:
            with self.subTest(pc=pc),self.assertRaisesRegex(ValueError,'measured PC'):
                native_missing_entries(dict(events=[dict(event='native_callback_frontier',pc=pc,reason='untranslated guest function target')]))

    def test_dense_trace_preserves_failures_and_full_log_identity(self):
        runtime=dict(event='native_callback_frontier',pc=0x400001,reason='native callback returned incomplete CPU state')
        missing=dict(event='native_startup_frontier',pc=0x413bd0,reason='untranslated guest code/import target')
        records=[dict(event='native_abi_enter',id=i) for i in range(200)]
        records.insert(10,runtime)
        records.append(missing)
        records.extend(dict(event='native_abi_exit',id=i) for i in range(200))
        payload=b'host diagnostic\xff\n'+b''.join((json.dumps(e)+'\n').encode() for e in records)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'run.stderr';path.write_bytes(payload)
            events,trace=read_native_events(path)
            self.assertEqual(path.read_bytes(),payload)
        self.assertEqual(events,[runtime,missing])
        self.assertEqual(native_observation(dict(events=events)),runtime)
        self.assertEqual(native_missing_entries(dict(events=events)),[missing])
        self.assertEqual(trace['counts'],dict(native_abi_enter=200,native_abi_exit=200))
        self.assertEqual([e['id'] for e in trace['tail']],list(range(136,200)))
        self.assertEqual(trace['full_log_sha256'],hashlib.sha256(payload).hexdigest())

    def test_later_execution_preserves_the_previous_reports_raw_logs(self):
        payloads=[(json.dumps(dict(event='native_startup_frontier',pc=pc,
                   reason='untranslated guest code/import target'))+'\n').encode()
                  for pc in (0x401000,0x402000)]
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory);stage=out/'bin_ship';stage.mkdir()
            for name in ('DAOrigins.exe','umbra.dll','recomp_runtime.dll'):
                (stage/name).write_bytes(b'constructed runner-storage fixture '+name.encode())
            (out/'build-report.json').write_text(json.dumps(dict(view='constructed-storage-fixture')))
            plan=out/'plan.json';plan.write_text(json.dumps(dict(process_state={})))
            remaining=iter(enumerate(payloads))
            debug_channels=[]
            trace_configurations=[]
            def launch(argv,**options):
                index,payload=next(remaining)
                debug_channels.append(options['env']['WINEDEBUG'])
                trace_configurations.append(options['env'].get('RECOMP_TRACE_NATIVE_CALLS'))
                options['stdout'].write(str(index).encode())
                options['stderr'].write(payload)
                process=mock.Mock();process.wait.return_value=3
                return process
            with mock.patch('tools.recomp_native.recomp_boot.PLAN',plan), \
                 mock.patch('tools.recomp_native.subprocess.Popen',side_effect=launch):
                reports=[execute_native(stage,out,out/'wine',out/'prefix',10,1,[]),
                         execute_native(stage,out,out/'wine',out/'prefix',10,1,[],wine_debug='+seh')]
            self.assertEqual(debug_channels,['-all','+seh'])
            for index,report in enumerate(reports):
                path=Path(report['native_abi_trace']['full_log'])
                self.assertEqual(path.read_bytes(),payloads[index])
                self.assertEqual(report['artifacts'][str(path)],hashlib.sha256(payloads[index]).hexdigest())
                self.assertFalse(report['game_acceptance'])
                self.assertEqual(report['execution_environment']['WINEDEBUG'],debug_channels[index])
                self.assertEqual(report['execution_environment']['RECOMP_TRACE_NATIVE_CALLS'],trace_configurations[index])
            self.assertNotEqual(reports[0]['native_abi_trace']['full_log'],reports[1]['native_abi_trace']['full_log'])
            self.assertEqual((out/'run.stderr').read_bytes(),payloads[1])
            self.assertEqual((out/'run.stdout').read_bytes(),b'1')


if __name__=='__main__': unittest.main()

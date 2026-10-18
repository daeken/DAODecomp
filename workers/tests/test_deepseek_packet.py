"""Offline only: synthetic packet, fake HTTPS and temporary ledgers."""
import argparse
from datetime import datetime, timezone
import importlib.util
import json
import multiprocessing
from pathlib import Path
import signal
import tempfile
import time
import unittest
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1] / 'deepseek_packet.py'
spec = importlib.util.spec_from_file_location('deepseek_packet', MODULE)
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
BINDINGS = {key: 'a' * 64 for key in p.BINDING_KEYS}
DAY1 = datetime(2026, 10, 18, 23, 59, tzinfo=p.ZoneInfo('America/Chicago'))
DAY2 = datetime(2026, 10, 19, 0, 1, tzinfo=p.ZoneInfo('America/Chicago'))

def reserve_child(directory, start, queue):
    start.wait()
    try: p.Ledger(directory).reserve(BINDINGS, p.CAP // 2, DAY1); queue.put('reserved')
    except p.Refusal as error: queue.put(str(error))

class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(); self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.ledger_dir = self.root / 'ledger'
        self.ledger = p.Ledger.initialize(self.ledger_dir, 0, [], DAY1)

    def usage(self): return {'prompt_tokens': 100, 'completion_tokens': 20, 'prompt_cache_hit_tokens': 10, 'prompt_cache_miss_tokens': 90}
    def good(self): return {'source': 'void f() {}', 'functions': [{'name': 'f', 'suggested_name': 'f', 'explanation': 'synthetic'}], 'uncertainties': []}
    def envelope(self, finish='stop', usage=True, proposal=None):
        value = {'choices': [{'finish_reason': finish, 'message': {'content': json.dumps(proposal or self.good())}}],
                 'id': 'test-id', 'model': 'deepseek-flash', 'system_fingerprint': 'test'}
        if usage: value['usage'] = self.usage()
        return p.encode(value)
    def fixture(self, output='output'):
        tree = self.root / 'tree'; tree.mkdir(exist_ok=True); (tree / 'tools').mkdir(exist_ok=True)
        packet = b'Implement synthetic function f. No tools.'
        (tree / 'packet.txt').write_bytes(packet)
        launcher = ('def main():\n    schema = ' + repr(p.RESPONSE_SCHEMA) + '\n').encode()
        (tree / 'tools/run_model_packet.py').write_bytes(launcher)
        manifest = {'schema_version': 1, 'packet': 'packet.txt', 'functions': [{'name': 'f', 'id': 'synthetic:f'}],
                    'snapshot': {'packet.txt': p.sha(packet), 'tools/run_model_packet.py': p.sha(launcher)}}
        path = self.root / 'manifest.json'; path.write_bytes(p.encode(manifest))
        key = self.root / 'key'; key.write_text('fake-test-credential')
        return argparse.Namespace(manifest=path, manifest_sha256=p.sha(path.read_bytes()), root=tree, packet=tree/'packet.txt',
                                  output=self.root/output, ledger_dir=self.ledger_dir, key_file=key)
    def fake(self, status=200, raw=None, error=None, delay=0):
        calls = []
        class Connection:
            def __init__(self, host, timeout): calls.append((host, timeout))
            def request(self, method, path, body, headers):
                if error: raise error
                if delay: time.sleep(delay)
            def getresponse(self): return self
            def read(self, limit): return raw if raw is not None else b'{}'
            def close(self): pass
        Connection.status = status
        return Connection, calls

    def test_concurrent_reservations_never_exceed_cap(self):
        context = multiprocessing.get_context('fork')
        start = context.Event(); queue = context.Queue()
        children = [context.Process(target=reserve_child, args=(self.ledger_dir, start, queue)) for _ in range(4)]
        for child in children: child.start()
        start.set()
        results = [queue.get(timeout=10) for _ in children]
        for child in children: child.join(10); self.assertEqual(child.exitcode, 0)
        self.assertEqual(results.count('reserved'), 2)
        self.assertEqual(results.count('daily_budget_exhausted'), 2)
        with self.ledger.locked() as value: self.assertEqual(sum(a['charged_nanodollars'] for a in value['attempts']), p.CAP)

    def test_rollover_preserves_old_inflight_day(self):
        first, day = self.ledger.reserve(BINDINGS, p.CAP, DAY1)
        self.assertEqual(day, '2026-10-18')
        second, day = self.ledger.reserve(BINDINGS, p.CAP, DAY2)
        self.assertEqual(day, '2026-10-19')
        self.ledger.settle(first, 'timeout', None)
        with self.assertRaises(p.Refusal): self.ledger.reserve(BINDINGS, 1, DAY1)
        with self.assertRaises(p.Refusal): self.ledger.reserve(BINDINGS, 1, DAY2)
        with self.ledger.locked() as value:
            self.assertEqual([a['day'] for a in value['attempts']], ['2026-10-18', '2026-10-19'])
            self.assertEqual(value['attempts'][1]['state'], 'reserved')
        self.ledger.settle(second, 'success', self.usage())
        with self.ledger.locked() as value: self.assertEqual(value['attempts'][0]['charged_nanodollars'], p.CAP)

    def test_clock_read_under_lock_and_chicago_timezone(self):
        # UTC06:00 is midnight CST on the DST transition's following day.
        self.assertEqual(p.local_day(datetime(2026, 11, 2, 5, 59, tzinfo=timezone.utc)), '2026-11-01')
        self.assertEqual(p.local_day(datetime(2026, 11, 2, 6, 0, tzinfo=timezone.utc)), '2026-11-02')
        real_locked = self.ledger.locked
        entered = []
        from contextlib import contextmanager
        @contextmanager
        def observed():
            with real_locked() as value:
                entered.append(True); yield value
        def day(now=None): self.assertTrue(entered); return '2026-10-18'
        with patch.object(self.ledger, 'locked', observed), patch.object(p, 'local_day', day):
            self.ledger.reserve(BINDINGS, 1)

    def test_unknown_usage_and_crash_keep_maximum(self):
        first, _ = self.ledger.reserve(BINDINGS, 1000, DAY1)
        # Simulate an abrupt process death: leave first untouched, open new client.
        second, _ = p.Ledger(self.ledger_dir).reserve(BINDINGS, 2000, DAY1)
        self.assertEqual(self.ledger.settle(second, 'invalid_response', {'prompt_tokens': True}), 2000)
        with self.ledger.locked() as value:
            self.assertEqual([a['charged_nanodollars'] for a in value['attempts']], [1000, 2000])
            self.assertEqual(value['attempts'][0]['id'], first)

    def test_exact_known_cost_and_no_double_settlement(self):
        identity, _ = self.ledger.reserve(BINDINGS, 100000, DAY1)
        self.assertEqual(self.ledger.settle(identity, 'invalid_response', self.usage()), 90*300 + 10*6 + 20*1200)
        with self.assertRaises(p.Refusal): self.ledger.settle(identity, 'success', self.usage())

    def test_actual_over_reservation_is_fully_charged(self):
        identity, _ = self.ledger.reserve(BINDINGS, 1, DAY1)
        cost = self.ledger.settle(identity, 'success', {'prompt_tokens': 200000000, 'completion_tokens': 0})
        self.assertGreater(cost, p.CAP)
        with self.assertRaises(p.Refusal): self.ledger.reserve(BINDINGS, 1, DAY1)

    def test_opening_debit_binds_prior_metrics_and_counts_today(self):
        directory = self.root / 'seeded'
        ledger = p.Ledger.initialize(directory, 50_000_000, ['b'*64, 'c'*64], DAY1)
        with self.assertRaises(p.Refusal): ledger.reserve(BINDINGS, p.CAP, DAY1)
        ledger.reserve(BINDINGS, p.CAP-50_000_000, DAY1)
        with ledger.locked() as value: self.assertEqual(value['opening_debit']['evidence_sha256'], ['b'*64, 'c'*64])
        with self.assertRaises(p.Refusal): p.Ledger.initialize(directory, 0, [], DAY2)
        with self.assertRaises(p.Refusal): p.Ledger.initialize(self.root/'badseed', 1, [], DAY1)

    def test_missing_corrupt_config_or_ledger_refused(self):
        for filename, data in [('config.json', b'{}'), ('ledger.json', b'{'), ('ledger.json', b'{"version":1,"version":1}')]:
            directory = self.root / ('corrupt' + str(time.monotonic_ns()))
            ledger = p.Ledger.initialize(directory, 0, [], DAY1)
            (directory/filename).write_bytes(data)
            with self.assertRaises(p.Refusal): ledger.reserve(BINDINGS, 1, DAY1)
        (self.ledger_dir/'ledger.lock').unlink()
        with self.assertRaises(p.Refusal): self.ledger.reserve(BINDINGS, 1, DAY1)

    def test_budget_refusal_happens_before_key_or_network(self):
        args = self.fixture()
        with patch.object(p, 'local_day', return_value='2026-10-18'):
            self.ledger.reserve(BINDINGS, p.CAP)
            args.key_file.unlink()
            sender = unittest.mock.Mock()
            with self.assertRaises(p.Refusal): p.run(args, sender)
            sender.assert_not_called()

    def test_success_one_request_and_initial_response_format(self):
        args = self.fixture(); sender = unittest.mock.Mock(return_value=('success', self.envelope(), 200))
        self.assertEqual(p.run(args, sender), 0); sender.assert_called_once()
        proposal = p.strict_json((args.output/'response.json').read_bytes())
        self.assertEqual(p.source_response(proposal, ['f']), self.good())
        run = p.strict_json((args.output/'run.json').read_bytes())
        self.assertEqual(run['schema_validation'], 'pass'); self.assertEqual(run['tool_items'], [])
        self.assertEqual(run['charged_nanodollars'], p.price_usage(self.usage()))
        self.assertNotIn('fake-test-credential', repr(list(args.output.glob('*'))))
        for file in args.output.iterdir(): self.assertNotIn(b'fake-test-credential', file.read_bytes())
        with self.assertRaises(p.Refusal): p.run(args, sender)
        sender.assert_called_once()

    def test_truncation_rejects_but_charges_reported_usage(self):
        args = self.fixture(); sender = unittest.mock.Mock(return_value=('success', self.envelope(finish='length'), 200))
        self.assertEqual(p.run(args, sender), 1); sender.assert_called_once()
        run = p.strict_json((args.output/'run.json').read_bytes())
        self.assertEqual(run['schema_validation'], 'fail'); self.assertEqual(run['finish_reason'], 'length')
        self.assertFalse((args.output/'response.json').exists())
        self.assertEqual(run['charged_nanodollars'], p.price_usage(self.usage()))

    def test_http_failure_timeout_missingusage_all_charged(self):
        for index, result in enumerate([('timeout', None, None), ('http_error', None, 500), ('success', self.envelope(usage=False), 200), ('success', b'{', 200)]):
            args = self.fixture(output='output'+str(index)); sender = unittest.mock.Mock(return_value=result)
            p.run(args, sender); sender.assert_called_once()
            run = p.strict_json((args.output/'run.json').read_bytes())
            self.assertEqual(run['charged_nanodollars'], run['reserved_nanodollars'])
            self.assertTrue(run['charge_is_uncertain_reservation'])

    def test_redirects_and_errors_never_retry_or_leak(self):
        for status in (301, 302, 307, 308, 429, 500):
            factory, calls = self.fake(status=status, raw=b'fake-test-credential confidential')
            outcome, raw, observed = p.transport(b'{}', 'fake-test-credential', factory=factory)
            self.assertEqual(outcome, 'http_error'); self.assertIsNone(raw); self.assertEqual(observed, status)
            self.assertEqual(calls, [('api.deepseek.com', 300)])
        factory, calls = self.fake(error=RuntimeError('Authorization: fake-test-credential'))
        self.assertEqual(p.transport(b'{}', 'fake-test-credential', factory=factory), ('transport_error', None, None))
        self.assertEqual(len(calls), 1)

    def test_secret_echo_plain_and_json_escaped_blocked(self):
        for raw in [b'{"x":"fake-test-credential"}', b'{"x":"\\u0066ake-test-credential"}']:
            factory, _ = self.fake(raw=raw)
            self.assertEqual(p.transport(b'{}', 'fake-test-credential', factory=factory), ('credential_echo', None, 200))

    def test_absolute_deadline(self):
        factory, calls = self.fake(delay=.2)
        completed = []
        sleep = time.sleep
        previous = signal.getsignal(signal.SIGALRM)
        def delayed_request(seconds):
            sleep(seconds)
            completed.append(True)
        # Observe interruption and timer wiring without imposing a scheduler latency bound.
        with patch.object(p.time, 'sleep', side_effect=delayed_request), \
                patch.object(p.signal, 'setitimer', wraps=signal.setitimer) as timer:
            self.assertEqual(p.transport(b'{}', 'fake-test-credential', factory=factory, seconds=.02), ('timeout', None, None))
        self.assertEqual(completed, [])
        self.assertEqual(timer.call_args_list, [unittest.mock.call(signal.ITIMER_REAL, .02), unittest.mock.call(signal.ITIMER_REAL, 0)])
        self.assertEqual(signal.getsignal(signal.SIGALRM), previous)
        self.assertEqual(calls, [('api.deepseek.com', .02)])

    def test_manifest_pin_packet_schema_and_path_hashes(self):
        args = self.fixture()
        body, binding, maximum, names = p.prepare(args.manifest, args.manifest_sha256, args.root, args.packet)
        self.assertEqual(names, ['f']); self.assertEqual(binding['packet_sha256'], p.sha(args.packet.read_bytes()))
        self.assertEqual(maximum, (len(body)+2048)*300+32768*1200)
        request = p.strict_json(body)
        self.assertEqual(request['reasoning_effort'], 'low'); self.assertNotIn('tools', request)
        with self.assertRaises(p.Refusal): p.prepare(args.manifest, '0'*64, args.root, args.packet)
        args.packet.write_text('altered')
        with self.assertRaises(p.Refusal): p.prepare(args.manifest, args.manifest_sha256, args.root, args.packet)

    def test_unsafe_json_paths_schema_and_symlinks(self):
        for raw in [b'{"a":1,"a":2}', b'{"a":NaN}', b'not json']:
            with self.assertRaises(p.Refusal): p.strict_json(raw)
        for name in ['../secret', '/tmp/key', 'a/../key', 'a//b', 'a\\b', './a']:
            with self.assertRaises(p.Refusal): p.relative_file(self.root, name)
        args = self.fixture(); args.packet.unlink(); args.packet.symlink_to(args.key_file)
        with self.assertRaises(p.Refusal): p.prepare(args.manifest, args.manifest_sha256, args.root, args.packet)
        args.packet.unlink(); args.packet.write_text('synthetic')
        launcher = args.root/'tools/run_model_packet.py'
        launcher.write_text('def main():\n    schema = dict()\n')
        manifest = p.strict_json(args.manifest.read_bytes()); manifest['snapshot']['packet.txt'] = p.sha(args.packet.read_bytes()); manifest['snapshot']['tools/run_model_packet.py'] = p.sha(launcher.read_bytes())
        args.manifest.write_bytes(p.encode(manifest))
        with self.assertRaises(p.Refusal): p.prepare(args.manifest, p.sha(args.manifest.read_bytes()), args.root, args.packet)

    def test_schema_rejects_unknown_duplicate_missing_functions(self):
        bad = self.good(); bad['extra'] = 1
        with self.assertRaises(p.Refusal): p.source_response(bad, ['f'])
        bad = self.good(); bad['functions'] *= 2
        with self.assertRaises(p.Refusal): p.source_response(bad, ['f'])
        with self.assertRaises(p.Refusal): p.source_response(self.good(), ['g'])

    def test_unexpected_tool_attempt_is_rejected(self):
        args = self.fixture(); envelope = p.strict_json(self.envelope())
        envelope['choices'][0]['message']['tool_calls'] = [{'id': 'synthetic-call'}]
        sender = unittest.mock.Mock(return_value=('success', p.encode(envelope), 200))
        self.assertEqual(p.run(args, sender), 1)
        run = p.strict_json((args.output/'run.json').read_bytes())
        self.assertEqual(run['tool_items'], ['tool_attempt'])
        self.assertFalse((args.output/'response.json').exists())

    def test_input_byte_cap_before_network(self):
        args = self.fixture(); packet = b'x' * p.MAX_INPUT_BYTES
        args.packet.write_bytes(packet)
        manifest = p.strict_json(args.manifest.read_bytes()); manifest['snapshot']['packet.txt'] = p.sha(packet)
        args.manifest.write_bytes(p.encode(manifest))
        with self.assertRaises(p.Refusal):
            p.prepare(args.manifest, p.sha(args.manifest.read_bytes()), args.root, args.packet)

    def test_nested_json_escaped_secret_must_not_be_persisted(self):
        args = self.fixture()
        synthetic_key = 'fake-test-credential'
        proposal = self.good()
        proposal['source'] = '/* ' + synthetic_key + ' */ void f() {}'
        content = json.dumps(proposal).replace(synthetic_key, '\\u0066ake-test-credential')
        envelope = {'choices': [{'finish_reason': 'stop', 'message': {'content': content}}], 'usage': self.usage()}
        raw = p.encode(envelope)
        self.assertNotIn(synthetic_key.encode(), raw)
        factory, calls = self.fake(raw=raw)
        def sender(body, key):
            return p.transport(body, key, factory=factory)
        result = p.run(args, sender)
        self.assertEqual(calls, [('api.deepseek.com', 300)])
        persisted = [f for f in args.output.iterdir() if synthetic_key.encode() in f.read_bytes()]
        self.assertEqual(persisted, [], 'Decoded credential persisted in response.json')
        self.assertEqual(result, 1)

    def test_contradictory_total_usage_retains_reservation(self):
        identity, _ = self.ledger.reserve(BINDINGS, 100000, DAY1)
        usage = {'prompt_tokens': 1, 'completion_tokens': 0, 'total_tokens': 1000000}
        self.assertEqual(self.ledger.settle(identity, 'invalid_response', usage), 100000)

    def test_contradictory_cache_usage_retains_reservation(self):
        identity, _ = self.ledger.reserve(BINDINGS, 100000, DAY1)
        usage = {'prompt_tokens': 100, 'completion_tokens': 0,
                 'prompt_cache_hit_tokens': 100,
                 'prompt_tokens_details': {'cached_tokens': 0}}
        self.assertEqual(self.ledger.settle(identity, 'invalid_response', usage), 100000)

if __name__ == '__main__': unittest.main(verbosity=2)

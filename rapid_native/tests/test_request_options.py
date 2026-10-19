import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from rapid_native.propose import prepare_request, request_packet
from workers import deepseek_packet as provider


class RequestOptionsTests(unittest.TestCase):
    value = {'functions': [{'name': 'fn_00001000', 'rva': 0x1000, 'original_va': 0x401000}]}

    def test_default_preserves_thinking_and_cap(self):
        body, bindings, maximum, domain = prepare_request(self.value)
        data = json.loads(body)
        self.assertEqual(data['thinking'], {'type': 'enabled'})
        self.assertEqual(data['reasoning_effort'], 'low')
        self.assertEqual(data['max_tokens'], 32768)

    def test_disabled_mode_binding_and_reservation_follow_exact_cap(self):
        body, bindings, maximum, _ = prepare_request(self.value, thinking=False, max_tokens=8192)
        data = json.loads(body)
        self.assertEqual(data['thinking'], {'type': 'disabled'})
        self.assertNotIn('reasoning_effort', data)
        self.assertEqual(data['max_tokens'], 8192)
        self.assertEqual(bindings['request_sha256'], provider.sha(body))
        self.assertEqual(maximum, (len(body)+2048)*provider.RATES['uncached']+8192*provider.RATES['output'])
        self.assertNotEqual(bindings['request_sha256'], prepare_request(self.value)[1]['request_sha256'])

    def test_options_cannot_raise_existing_maximum(self):
        for options in ({'max_tokens': 32769}, {'max_tokens': 0}, {'max_tokens': True}, {'thinking': 'disabled'}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                prepare_request(self.value, **options)

    def test_actual_transport_keeps_truncation_unaccepted_and_settles_once(self):
        envelope = provider.encode({'model': 'deepseek-flash', 'choices': [
            {'finish_reason': 'length', 'message': {'content': '{"source":"partial'}}
        ], 'usage': {'prompt_tokens': 10, 'completion_tokens': 8192,
                     'prompt_cache_hit_tokens': 0, 'prompt_cache_miss_tokens': 10}})
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp).resolve() / 'attempt'
            with patch('rapid_native.propose.provider.Ledger') as ledger_type, \
                 patch('rapid_native.propose.provider.read_regular', return_value=b'test-only-key'), \
                 patch('rapid_native.propose.provider.transport', return_value=('success', envelope, 200)) as transport, \
                 patch('rapid_native.propose.settle_global') as settle:
                ledger = ledger_type.return_value
                ledger.reserve.return_value = ('test-attempt', '2026-10-18')
                ledger.settle.return_value = 100
                result = request_packet(folder, self.value, 'test-request', thinking=False, max_tokens=8192)
                self.assertEqual(result['outcome'], 'invalid_response')
                self.assertFalse(result['thinking'])
                self.assertEqual(result['max_tokens'], 8192)
                self.assertFalse((folder/'candidate.cpp').exists())
                self.assertTrue((folder/'raw-response.json').exists())
                self.assertEqual(json.loads(transport.call_args.args[0])['thinking'], {'type': 'disabled'})
                ledger.reserve.assert_called_once()
                ledger.settle.assert_called_once()
                settle.assert_called_once()


if __name__ == '__main__':
    unittest.main()

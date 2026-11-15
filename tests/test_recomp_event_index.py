from pathlib import Path
import hashlib
import json
import tempfile
import unittest
from tools.recomp_event_index import NativeEventIndex


class NativeEventIndexTests(unittest.TestCase):
    def test_split_failure_and_unterminated_final_record_are_retained(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "stderr"
            path.touch()
            index = NativeEventIndex(path)
            records = [{"event": "native_callback_entry", "pc": i} for i in range(200)]
            records += [{"event": "native_callback_frontier", "reason": "unknown π"},
                        {"event": "native_frontier_state", "pc": 123}]
            data = b"Wine diagnostic\n" + b"\n".join(
                json.dumps(x, ensure_ascii=False).encode() for x in records)
            for offset in range(0, len(data), 7):
                with path.open("ab") as stream:
                    stream.write(data[offset:offset + 7])
                snapshot = index.snapshot()
            self.assertEqual(snapshot["event_counts"]["native_callback_entry"], 200)
            self.assertNotIn("native_frontier_state", snapshot["event_counts"])
            result = index.snapshot(final=True)
            self.assertEqual(result["events"], records[-2:])
            from tools.recomp_native import native_observation
            self.assertEqual(native_observation(result), records[-2])
            self.assertEqual(result["tail"], records[-64:])
            self.assertEqual(result["native_abi_trace"]["full_log_sha256"], hashlib.sha256(data).hexdigest())
            self.assertEqual(result["indexed_bytes"], len(data))
            self.assertEqual(result["pending_bytes"], 0)
            with self.assertRaises(ValueError):
                index.snapshot()

    def test_replaced_truncated_and_rewritten_logs_cannot_finalize(self):
        for change in ("replace", "truncate", "rewrite"):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as temporary:
                path = Path(temporary) / "stderr"
                original = b'{"event":"native_callback_entry"}\n'
                path.write_bytes(original)
                index = NativeEventIndex(path)
                index.snapshot()
                if change == "replace":
                    other = path.with_name("replacement")
                    other.write_bytes(original)
                    other.replace(path)
                elif change == "truncate":
                    path.write_bytes(b"")
                else:
                    path.write_bytes(original.replace(b"entry", b"error"))
                with self.assertRaises(ValueError):
                    index.snapshot(final=True)

    def test_abi_counts_and_malformed_records_remain_explicit(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "stderr"
            records = [{"event": "native_abi_enter", "id": i} for i in range(100)]
            path.write_bytes(b"".join(json.dumps(x).encode() + b"\n" for x in records)
                             + b'{invalid}\n{"event":null}\n')
            result = NativeEventIndex(path).snapshot(final=True)
            self.assertEqual(result["native_abi_trace"]["counts"], {"native_abi_enter": 100})
            self.assertEqual(result["native_abi_trace"]["tail"], records[-64:])
            self.assertEqual(result["invalid_json_records"], 2)
            self.assertEqual(result["events"], [])


if __name__ == "__main__":
    unittest.main()

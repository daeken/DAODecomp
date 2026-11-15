"""Append-only exploratory log index; full logs remain the evidence artifact."""
from collections import Counter, deque
import hashlib
import json
import os
from pathlib import Path


class NativeEventIndex:
    """Keep failure records while reading each live-log byte only once.

    Live snapshots assume one append-only writer. Finalization rehashes the full
    file independently and refuses changed prefixes, replacement or truncation.
    This is a storage index, never a call validator or a game acceptance result.
    """
    repetitive = frozenset(("native_callback_entry", "native_callback_return",
                            "native_exception_observed", "native_abi_enter",
                            "native_abi_exit"))

    def __init__(self, path):
        self.path = Path(path)
        self.identity = None
        self.offset = 0
        self.digest = hashlib.sha256()
        self.pending = bytearray()
        self.counts = Counter()
        self.events = []
        self.tail = deque(maxlen=64)
        self.abi_tail = deque(maxlen=64)
        self.invalid_json_records = 0
        self.finished = False

    def _record(self, line):
        if not line.startswith(b"{"):
            return
        try:
            event = json.loads(line.decode("utf-8", errors="replace"))
        except json.JSONDecodeError:
            self.invalid_json_records += 1
            return
        if not isinstance(event, dict):
            self.invalid_json_records += 1
            return
        kind = event.get("event")
        if not isinstance(kind, str):
            self.invalid_json_records += 1
            return
        self.counts[kind] += 1
        self.tail.append(event)
        if kind in ("native_abi_enter", "native_abi_exit"):
            self.abi_tail.append(event)
        if kind not in self.repetitive:
            if len(self.events) >= 10000:
                raise ValueError("important-event storage limit; observation incomplete")
            self.events.append(event)

    def snapshot(self, *, final=False):
        if self.finished:
            raise ValueError("event index already finalized")
        with self.path.open("rb") as stream:
            info = os.fstat(stream.fileno())
            identity = (info.st_dev, info.st_ino)
            if self.identity is None:
                self.identity = identity
            if identity != self.identity or info.st_size < self.offset:
                raise ValueError("log replaced or truncated; observation incomplete")
            stream.seek(self.offset)
            while chunk := stream.read(1024 * 1024):
                self.digest.update(chunk)
                self.offset += len(chunk)
                self.pending.extend(chunk)
                start = 0
                while (end := self.pending.find(b"\n", start)) >= 0:
                    self._record(self.pending[start:end + 1])
                    start = end + 1
                del self.pending[:start]
                if len(self.pending) > 1024 * 1024:
                    raise ValueError("unterminated log record too large; observation incomplete")
            if final:
                if self.pending:
                    self._record(self.pending)
                    self.pending.clear()
                stream.seek(0)
                complete = hashlib.sha256()
                while chunk := stream.read(1024 * 1024):
                    complete.update(chunk)
                full = complete.hexdigest()
                after = os.fstat(stream.fileno())
                current = self.path.stat()
                if (full != self.digest.hexdigest() or after.st_size != self.offset
                        or after.st_mtime_ns != info.st_mtime_ns
                        or (current.st_dev, current.st_ino) != self.identity
                        or current.st_size != self.offset):
                    raise ValueError("log changed during observation; final identity refused")
                self.finished = True
        return dict(events=list(self.events), tail=list(self.tail),
                    event_counts=dict(self.counts),
                    invalid_json_records=self.invalid_json_records,
                    indexed_bytes=self.offset, pending_bytes=len(self.pending),
                    native_abi_trace=dict(
                        counts={k: self.counts[k] for k in ("native_abi_enter", "native_abi_exit")
                                if self.counts[k]}, tail=list(self.abi_tail),
                        full_log=str(self.path), full_log_sha256=self.digest.hexdigest(),
                        scope="Append-only storage index; complete log retained; no call or game acceptance."),
                    event_storage_scope="All nonrepetitive events, exact counts and bounded repetitive tail; full stderr retained.")

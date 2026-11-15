"""Small synchronous clangd client for scoped, reviewable source refactors.

The language server only sees a temporary worktree. Its edits are data returned
to the coordinator; it never writes the user's source files.
"""
import json
import os
from pathlib import Path
import select
import shutil
import subprocess
import time


class Clangd:
    def __init__(self, root, commands, timeout=60, query_drivers=()):
        self.root = Path(root).resolve()
        self.timeout = timeout
        self.serial = 0
        self.buffer = bytearray()
        self.notifications = []
        self.diagnostics = {}
        (self.root / 'compile_commands.json').write_text(json.dumps(commands))
        executable = shutil.which('clangd')
        if not executable:
            raise ValueError('clangd is required for semantic refactoring')
        self.log = (self.root / 'clangd.stderr').open('wb')
        options = ['--query-driver=' + ','.join(map(str, query_drivers))] if query_drivers else []
        self.process = subprocess.Popen([executable, *options, '--background-index=false',
            '--clang-tidy=false', '--enable-config=false', '--log=error',
            '--compile-commands-dir=' + str(self.root)], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=self.log)
        try:
            result = self.request('initialize', {
                'processId': os.getpid(), 'rootUri': self.root.as_uri(),
                'capabilities': {'general': {'positionEncodings': ['utf-16']},
                    'offsetEncoding': ['utf-16'],
                    'textDocument': {'rename': {'prepareSupport': True},
                        'semanticTokens': {'requests': {'full': True},
                            'tokenTypes': [], 'tokenModifiers': [],
                            'formats': ['relative']}}},
                'initializationOptions': {'clangdFileStatus': True}})
            encoding = result.get('offsetEncoding',
                result.get('capabilities', {}).get('positionEncoding', 'utf-16'))
            if encoding != 'utf-16':
                raise ValueError('clangd selected an unsupported position encoding')
            self.capabilities = result.get('capabilities', {})
            self.notify('initialized', {})
        except Exception:
            self.close()
            raise

    def send(self, message):
        body = json.dumps(message, ensure_ascii=False).encode()
        self.process.stdin.write(b'Content-Length: ' + str(len(body)).encode() + b'\r\n\r\n' + body)
        self.process.stdin.flush()

    def notify(self, method, params):
        self.send({'jsonrpc': '2.0', 'method': method, 'params': params})

    def receive(self, deadline):
        while True:
            boundary = self.buffer.find(b'\r\n\r\n')
            if boundary >= 0:
                headers = dict(line.split(':', 1) for line in
                    self.buffer[:boundary].decode('ascii').split('\r\n'))
                size = int(headers['Content-Length'].strip())
                if not 0 <= size <= 64 * 1024 * 1024:
                    raise ValueError('clangd response exceeded the message budget')
                start = boundary + 4
                if len(self.buffer) >= start + size:
                    value = json.loads(bytes(self.buffer[start:start + size]))
                    del self.buffer[:start + size]
                    return value
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ValueError('clangd request timed out; no source changes applied')
            if not select.select([self.process.stdout], [], [], remaining)[0]:
                continue
            chunk = os.read(self.process.stdout.fileno(), 65536)
            if not chunk:
                raise ValueError('clangd exited before completing the request')
            self.buffer.extend(chunk)

    def request(self, method, params):
        self.serial += 1
        identifier = self.serial
        self.send({'jsonrpc': '2.0', 'id': identifier, 'method': method, 'params': params})
        deadline = time.monotonic() + self.timeout
        while True:
            value = self.receive(deadline)
            if value.get('id') == identifier and 'method' not in value:
                if 'error' in value:
                    raise ValueError('clangd refused: ' + value['error'].get('message', str(value['error'])))
                return value.get('result')
            if 'method' in value and 'id' in value:
                # Never let a server request write through to the real workspace.
                result = {'applied': False, 'failureReason': 'edits require a workbench plan'} if value['method'] == 'workspace/applyEdit' else None
                if value['method'] == 'workspace/configuration':
                    result = [{} for _ in value.get('params', {}).get('items', [])]
                self.send({'jsonrpc': '2.0', 'id': value['id'], 'result': result})
            else:
                self.notifications.append(value)
                if value.get('method') == 'textDocument/publishDiagnostics':
                    params = value['params']
                    self.diagnostics[params['uri']] = params.get('diagnostics', [])

    def open(self, path):
        path = Path(path).resolve()
        self.notify('textDocument/didOpen', {'textDocument': {'uri': path.as_uri(),
            'languageId': 'cpp', 'version': 1, 'text': path.read_text()}})
        # This request waits for this AST, including its dynamic reference index.
        self.request('textDocument/documentSymbol', {'textDocument': {'uri': path.as_uri()}})

    def at(self, method, path, line, character, **extra):
        return self.request(method, {'textDocument': {'uri': Path(path).resolve().as_uri()},
            'position': {'line': line, 'character': character}, **extra})

    def close(self):
        if getattr(self, 'process', None):
            if self.process.poll() is None:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()
            for stream in (self.process.stdin, self.process.stdout):
                stream.close()
        if getattr(self, 'log', None):
            self.log.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def offset(text, position):
    """LSP UTF-16 position to Python string offset, rejecting split surrogates."""
    lines = text.splitlines(keepends=True)
    line, character = position['line'], position['character']
    if line == len(lines) and character == 0:
        return len(text)
    if not 0 <= line < len(lines) or character < 0:
        raise ValueError('source position is outside the document')
    content = lines[line].rstrip('\r\n')
    count = 0
    for i, codepoint in enumerate(content):
        if count == character:
            return sum(map(len, lines[:line])) + i
        count += 2 if ord(codepoint) > 0xffff else 1
        if count > character:
            raise ValueError('source position splits a UTF-16 surrogate pair')
    if count == character:
        return sum(map(len, lines[:line])) + len(content)
    raise ValueError('source column is outside the line')


def apply_text_edits(text, edits):
    spans = []
    for edit in edits:
        start, end = (offset(text, edit['range'][x]) for x in ('start', 'end'))
        if end < start:
            raise ValueError('reversed edit range')
        spans.append((start, end, edit['newText']))
    spans = sorted(set(spans))
    for left, right in zip(spans, spans[1:]):
        if left[1] > right[0] or left[0] == right[0]:
            raise ValueError('overlapping refactors; split them into separate plans')
    for start, end, replacement in reversed(spans):
        text = text[:start] + replacement + text[end:]
    return text

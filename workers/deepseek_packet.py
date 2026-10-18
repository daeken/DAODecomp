"""One tool-free DeepSeek packet request with a fail-closed local daily ledger.

Provider estimates are not vendor invoices. This module never executes packet code
or changes recovery acceptance. POSIX only (flock and absolute request deadline).
"""
import argparse
import ast
import contextlib
from datetime import datetime
import hashlib
import http.client
import json
import os
from pathlib import Path, PurePosixPath
import re
import signal
import stat
import sys
import tempfile
import time
import uuid
from zoneinfo import ZoneInfo

try:
    import fcntl
except ImportError:
    fcntl = None

CAP = 50_000_000_000  # integer nanodollars, $50
RATES = {'uncached': 300, 'cached': 6, 'output': 1200}
CONFIG = {'version': 1, 'timezone': 'America/Chicago', 'daily_cap_nanodollars': CAP,
          'peak_nanodollars_per_token': RATES}
MAX_OUTPUT = 32768
MAX_INPUT_BYTES = 250000
TIMEOUT = 300
SHA = re.compile(r'[0-9a-f]{64}\Z')

class Refusal(Exception):
    """Messages are fixed codes, never arbitrary exception/server text."""

def refuse(code):
    raise Refusal(code)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def encode(value):
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(',', ':')) + '\n').encode()

def strict_json(data):
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                refuse('duplicate_json_key')
            value[key] = item
        return value
    def constant(value):
        refuse('nonfinite_json')
    try:
        return json.loads(data, object_pairs_hook=pairs, parse_constant=constant)
    except (ValueError, UnicodeError, TypeError):
        refuse('invalid_json')

def exact(value, keys):
    if type(value) is not dict or set(value) != set(keys):
        refuse('invalid_fields')

def natural(value):
    return type(value) is int and value >= 0

def no_symlinks(path):
    path = Path(path).absolute()
    for component in [path, *path.parents]:
        if component.is_symlink():
            refuse('symlink_path')
    return path

def read_regular(path, limit=8 * 1024 * 1024):
    path = no_symlinks(path)
    try:
        with path.open('rb') as file:
            info = os.fstat(file.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
                refuse('invalid_file')
            value = file.read(limit + 1)
            if len(value) > limit:
                refuse('file_size_limit')
            return value
    except OSError:
        refuse('file_unavailable')

def atomic(path, value):
    """The caller owns either an exclusive ledger lock or a new output directory."""
    path = no_symlinks(path)
    descriptor, temporary = tempfile.mkstemp(prefix='.pending-', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'wb') as file:
            file.write(encode(value)); file.flush(); os.fsync(file.fileno())
        os.replace(temporary, path)
        descriptor = os.open(path.parent, os.O_RDONLY)
        try: os.fsync(descriptor)
        finally: os.close(descriptor)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)

def local_day(now=None):
    if now is None: now = datetime.now(ZoneInfo(CONFIG['timezone']))
    if now.tzinfo is None: refuse('naive_clock')
    return now.astimezone(ZoneInfo(CONFIG['timezone'])).date().isoformat()

class Ledger:
    def __init__(self, directory):
        self.directory = no_symlinks(directory)

    @classmethod
    def initialize(cls, directory, opening_debit, evidence, now=None):
        if fcntl is None: refuse('posix_required')
        if not natural(opening_debit) or opening_debit > CAP: refuse('invalid_opening_debit')
        if type(evidence) is not list or any(not isinstance(h, str) or not SHA.fullmatch(h) for h in evidence): refuse('invalid_opening_evidence')
        if opening_debit and not evidence: refuse('opening_evidence_required')
        directory = no_symlinks(directory)
        # Existing directories, including incomplete initialization, are refused.
        try: directory.mkdir(mode=0o700, parents=True, exist_ok=False)
        except OSError: refuse('ledger_already_exists_or_unavailable')
        atomic(directory / 'config.json', CONFIG)
        atomic(directory / 'ledger.json', {'version': 1, 'config_sha256': sha(encode(CONFIG)), 'attempts': [],
               'opening_debit': {'day': local_day(now), 'charged_nanodollars': opening_debit, 'evidence_sha256': evidence}})
        descriptor = os.open(directory / 'ledger.lock', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.close(descriptor)
        return cls(directory)

    @contextlib.contextmanager
    def locked(self):
        if fcntl is None: refuse('posix_required')
        lock = no_symlinks(self.directory / 'ledger.lock')
        try:
            descriptor = os.open(lock, os.O_RDWR | os.O_NOFOLLOW)
        except OSError: refuse('ledger_lock_unavailable')
        with os.fdopen(descriptor, 'r+b') as file:
            if not stat.S_ISREG(os.fstat(file.fileno()).st_mode): refuse('invalid_lock')
            fcntl.flock(file, fcntl.LOCK_EX)
            try:
                config = strict_json(read_regular(self.directory / 'config.json'))
                # Exact encoded bytes avoid bool/int equality and silent configuration changes.
                if encode(config) != encode(CONFIG): refuse('invalid_ledger_config')
                value = strict_json(read_regular(self.directory / 'ledger.json', 64 * 1024 * 1024))
                self.validate(value)
                yield value
            finally: fcntl.flock(file, fcntl.LOCK_UN)

    def validate(self, value):
        exact(value, {'version', 'config_sha256', 'attempts', 'opening_debit'})
        if type(value['version']) is not int or value['version'] != 1 or value['config_sha256'] != sha(encode(CONFIG)):
            refuse('invalid_ledger_identity')
        if type(value['attempts']) is not list: refuse('invalid_attempts')
        opening = value['opening_debit']
        exact(opening, {'day', 'charged_nanodollars', 'evidence_sha256'})
        try: datetime.strptime(opening['day'], '%Y-%m-%d')
        except (ValueError, TypeError): refuse('invalid_opening_day')
        if not natural(opening['charged_nanodollars']) or opening['charged_nanodollars'] > CAP: refuse('invalid_opening_debit')
        evidence = opening['evidence_sha256']
        if type(evidence) is not list or any(not isinstance(h, str) or not SHA.fullmatch(h) for h in evidence): refuse('invalid_opening_evidence')
        if opening['charged_nanodollars'] and not evidence: refuse('opening_evidence_required')
        seen = set()
        for attempt in value['attempts']:
            exact(attempt, {'id', 'day', 'bindings', 'reserved_nanodollars', 'charged_nanodollars', 'state', 'result'})
            if not isinstance(attempt['id'], str) or not re.fullmatch(r'[0-9a-f]{32}', attempt['id']) or attempt['id'] in seen:
                refuse('invalid_attempt_id')
            seen.add(attempt['id'])
            try: datetime.strptime(attempt['day'], '%Y-%m-%d')
            except (ValueError, TypeError): refuse('invalid_attempt_day')
            validate_bindings(attempt['bindings'])
            reserved = attempt['reserved_nanodollars']; charged = attempt['charged_nanodollars']
            if not natural(reserved) or reserved == 0 or not natural(charged): refuse('invalid_cost')
            if attempt['state'] == 'reserved':
                if charged != reserved or attempt['result'] is not None: refuse('invalid_reservation')
            elif attempt['state'] == 'settled':
                exact(attempt['result'], {'outcome', 'usage', 'estimated_nanodollars'})
                result = attempt['result']
                if result['outcome'] not in OUTCOMES: refuse('invalid_outcome')
                measured = price_usage(result['usage'])
                if result['estimated_nanodollars'] != measured or charged != (reserved if measured is None else measured):
                    refuse('invalid_settlement')
            else: refuse('invalid_attempt_state')

    def reserve(self, bindings, maximum, now=None):
        validate_bindings(bindings)
        if not natural(maximum) or maximum == 0: refuse('invalid_reservation_cost')
        with self.locked() as value:
            day = local_day(now)  # Read the clock only after acquiring the lock.
            # Every attempt belongs permanently to its dispatch/reservation day.
            # Old in-flight attempts keep their original reservation and cannot
            # spend the new day's budget or be released by a rollover.
            total = sum(a['charged_nanodollars'] for a in value['attempts'] if a['day'] == day)
            if value['opening_debit']['day'] == day: total += value['opening_debit']['charged_nanodollars']
            if total + maximum > CAP: refuse('daily_budget_exhausted')
            attempt_id = uuid.uuid4().hex
            value['attempts'].append({'id': attempt_id, 'day': day, 'bindings': bindings,
                                      'reserved_nanodollars': maximum, 'charged_nanodollars': maximum,
                                      'state': 'reserved', 'result': None})
            atomic(self.directory / 'ledger.json', value)
            return attempt_id, day

    def settle(self, attempt_id, outcome, usage):
        if outcome not in OUTCOMES: refuse('invalid_outcome')
        cost = price_usage(usage)
        # Invalid/missing usage is deliberately stored as unknown, never zero.
        usage = normalized_usage(usage)
        with self.locked() as value:
            matches = [a for a in value['attempts'] if a['id'] == attempt_id]
            if len(matches) != 1 or matches[0]['state'] != 'reserved': refuse('already_settled_or_missing')
            attempt = matches[0]
            attempt['charged_nanodollars'] = attempt['reserved_nanodollars'] if cost is None else cost
            attempt['state'] = 'settled'
            attempt['result'] = {'outcome': outcome, 'usage': usage, 'estimated_nanodollars': cost}
            atomic(self.directory / 'ledger.json', value)
            return attempt['charged_nanodollars']

OUTCOMES = {'success', 'http_error', 'timeout', 'transport_error', 'invalid_response', 'credential_echo', 'size_limit', 'credential_unavailable'}
BINDING_KEYS = {'manifest_sha256', 'packet_sha256', 'response_schema_sha256', 'request_sha256', 'function_domain_sha256'}

def validate_bindings(value):
    exact(value, BINDING_KEYS)
    if any(not isinstance(v, str) or not SHA.fullmatch(v) for v in value.values()): refuse('invalid_binding')

def normalized_usage(usage):
    if type(usage) is not dict: return None
    prompt = usage.get('prompt_tokens'); output = usage.get('completion_tokens')
    if 'total_tokens' in usage and (not natural(usage['total_tokens']) or not natural(prompt) or not natural(output) or usage['total_tokens'] != prompt + output): return None
    details = usage.get('prompt_tokens_details')
    if 'prompt_cache_hit_tokens' in usage and type(details) is dict and 'cached_tokens' in details and (not natural(details['cached_tokens']) or details['cached_tokens'] != usage['prompt_cache_hit_tokens']): return None
    cached = usage.get('prompt_cache_hit_tokens')
    if cached is None:
        details = usage.get('prompt_tokens_details')
        cached = details.get('cached_tokens', 0) if type(details) is dict else 0
    miss = usage.get('prompt_cache_miss_tokens', prompt - cached if natural(prompt) and natural(cached) else None)
    if not all(natural(x) for x in (prompt, output, cached, miss)) or cached + miss != prompt: return None
    return {'prompt_tokens': prompt, 'completion_tokens': output, 'prompt_cache_hit_tokens': cached, 'prompt_cache_miss_tokens': miss}

def price_usage(usage):
    usage = normalized_usage(usage)
    if usage is None: return None
    return usage['prompt_cache_miss_tokens'] * RATES['uncached'] + usage['prompt_cache_hit_tokens'] * RATES['cached'] + usage['completion_tokens'] * RATES['output']

def relative_file(root, name):
    if not isinstance(name, str) or '\\' in name: refuse('unsafe_relative_path')
    parts = PurePosixPath(name).parts
    if not parts or name != '/'.join(parts) or any(p in {'.', '..'} for p in parts) or PurePosixPath(name).is_absolute():
        refuse('unsafe_relative_path')
    return no_symlinks(root / name)

def prepare(manifest_path, expected_hash, root, packet_path):
    if not isinstance(expected_hash, str) or not SHA.fullmatch(expected_hash): refuse('manifest_pin_required')
    manifest_bytes = read_regular(manifest_path)
    if sha(manifest_bytes) != expected_hash: refuse('manifest_hash_mismatch')
    manifest = strict_json(manifest_bytes)
    if type(manifest) is not dict or type(manifest.get('schema_version')) is not int or manifest.get('schema_version') != 1: refuse('manifest_version')
    snapshot = manifest.get('snapshot')
    if type(snapshot) is not dict: refuse('invalid_snapshot')
    frozen_packet = relative_file(root, manifest.get('packet'))
    if no_symlinks(packet_path) != frozen_packet: refuse('packet_path_mismatch')
    packet = read_regular(frozen_packet, MAX_INPUT_BYTES)
    launcher_name = 'tools/run_model_packet.py'
    launcher = read_regular(relative_file(root, launcher_name))
    for name, data in ((manifest['packet'], packet), (launcher_name, launcher)):
        if sha(data) != snapshot.get(name): refuse('frozen_hash_mismatch')
    # Parse a literal, never import or execute the frozen launcher or support.
    try:
        tree = ast.parse(launcher.decode())
        schemas = [ast.literal_eval(n.value) for n in ast.walk(tree) if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'schema' for t in n.targets)]
    except (ValueError, SyntaxError, UnicodeError): refuse('unsafe_schema')
    if len(schemas) != 1: refuse('ambiguous_schema')
    schema = schemas[0]
    # This provider implements exactly the unchanged pair's implementation format.
    if schema != RESPONSE_SCHEMA: refuse('unsupported_schema')
    functions = manifest.get('functions')
    if type(functions) is not list or not functions: refuse('empty_function_domain')
    domain = []
    for function in functions:
        if type(function) is not dict: refuse('invalid_function_domain')
        name, identity = function.get('name'), function.get('id')
        if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', name) or not isinstance(identity, str) or not identity:
            refuse('invalid_function_domain')
        domain.append({'name': name, 'id': identity})
    if len({f['name'] for f in domain}) != len(domain) or len({f['id'] for f in domain}) != len(domain): refuse('duplicate_function_domain')
    instructions = ('Return exactly one JSON object matching this schema; no markdown fences. '
                    'The source contains the complete proposed C++ source. Include every packet function exactly once, '
                    'with nonempty name, suggested_name, explanation. No tools. JSON schema:\n' + json.dumps(schema))
    try: packet_text = packet.decode('utf-8')
    except UnicodeError: refuse('packet_not_utf8')
    body = encode({'model': 'deepseek-flash', 'messages': [{'role': 'system', 'content': instructions}, {'role': 'user', 'content': packet_text}],
                   'thinking': {'type': 'enabled'}, 'reasoning_effort': 'low', 'response_format': {'type': 'json_object'},
                   'max_tokens': MAX_OUTPUT, 'stream': False})
    # Bound serialized UTF-8 input including escaping, schema and message framing.
    if len(body) > MAX_INPUT_BYTES: refuse('input_byte_cap')
    maximum = (len(body) + 2048) * RATES['uncached'] + MAX_OUTPUT * RATES['output']
    bindings = {'manifest_sha256': sha(manifest_bytes), 'packet_sha256': sha(packet), 'response_schema_sha256': sha(encode(schema)),
                'request_sha256': sha(body), 'function_domain_sha256': sha(encode(domain))}
    return body, bindings, maximum, [f['name'] for f in domain]

RESPONSE_SCHEMA = {'type': 'object', 'properties': {
    'source': {'type': 'string'},
    'functions': {'type': 'array', 'items': {'type': 'object', 'properties': {
        'name': {'type': 'string'}, 'suggested_name': {'type': 'string'}, 'explanation': {'type': 'string'}},
        'required': ['name', 'suggested_name', 'explanation'], 'additionalProperties': False}},
    'uncertainties': {'type': 'array', 'items': {'type': 'string'}}},
    'required': ['source', 'functions', 'uncertainties'], 'additionalProperties': False}

def source_response(value, names):
    exact(value, {'source', 'functions', 'uncertainties'})
    if not isinstance(value['source'], str) or not value['source'].strip() or len(value['source'].encode()) > 1024 * 1024: refuse('invalid_source')
    if type(value['functions']) is not list: refuse('invalid_function_notes')
    seen = []
    for function in value['functions']:
        exact(function, {'name', 'suggested_name', 'explanation'})
        if any(not isinstance(v, str) or not v for v in function.values()): refuse('invalid_function_notes')
        seen.append(function['name'])
    if len(seen) != len(names) or set(seen) != set(names): refuse('function_set_mismatch')
    if type(value['uncertainties']) is not list or any(not isinstance(v, str) for v in value['uncertainties']): refuse('invalid_uncertainties')
    return value

class Deadline(Exception): pass

def on_alarm(signum, frame): raise Deadline()

def transport(body, key, factory=http.client.HTTPSConnection, seconds=TIMEOUT):
    connection = None
    previous = signal.signal(signal.SIGALRM, on_alarm)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        connection = factory('api.deepseek.com', timeout=seconds)
        connection.request('POST', '/chat/completions', body=body,
                           headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
        response = connection.getresponse()
        if response.status != 200: return 'http_error', None, response.status
        raw = response.read(4 * 1024 * 1024 + 1)
        if len(raw) > 4 * 1024 * 1024: return 'size_limit', None, 200
        if key.encode() in raw: return 'credential_echo', None, 200
        # Catch JSON-escaped echoes as well as literal credentials before any
        # content, identifier, proposal, hash or metrics reaches persistence.
        try:
            def contains_secret(value):
                if isinstance(value, str): return key in value
                if type(value) is list: return any(contains_secret(v) for v in value)
                if type(value) is dict: return any(contains_secret(k) or contains_secret(v) for k, v in value.items())
                return False
            envelope = strict_json(raw)
            if contains_secret(envelope): return 'credential_echo', None, 200
            # The proposal is a second JSON document inside message.content.
            # Scan the same decoded values that will later be persisted.
            if type(envelope) is dict and type(envelope.get('choices')) is list:
                for choice in envelope['choices']:
                    message = choice.get('message') if type(choice) is dict else None
                    if type(message) is dict and isinstance(message.get('content'), str):
                        if contains_secret(strict_json(message['content'])):
                            return 'credential_echo', None, 200
        except Refusal:
            pass  # Malformed envelope becomes invalid_response with unknown cost.
        return 'success', raw, 200
    except (Deadline, TimeoutError): return 'timeout', None, None
    except Exception: return 'transport_error', None, None
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0); signal.signal(signal.SIGALRM, previous)
        if connection is not None:
            try: connection.close()
            except Exception: pass

def safe_identifier(value):
    # Allow only short identifiers. Never persist arbitrary server/error strings.
    return value if isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9_.:-]{1,128}', value) else None

def run(args, sender=transport):
    if fcntl is None or not hasattr(signal, 'SIGALRM'): refuse('posix_required')
    body, bindings, maximum, names = prepare(args.manifest, args.manifest_sha256, no_symlinks(args.root), args.packet)
    output = no_symlinks(args.output)
    # New directory is an exclusive paid-call claim. Never resume/overwrite it.
    try: output.mkdir(mode=0o700, parents=True, exist_ok=False)
    except OSError: refuse('output_exists_or_unavailable')
    ledger = Ledger(args.ledger_dir)
    attempt_id, day = ledger.reserve(bindings, maximum)
    metrics = {'schema_version': 1, 'attempt_id': attempt_id, 'budget_day': day, **bindings,
               'requested_model': 'deepseek-flash', 'reasoning_effort': 'low', 'tool_items': [],
               'automatic_retry': False, 'max_requests': 1, 'max_tokens': MAX_OUTPUT, 'timeout_seconds': TIMEOUT,
               'input_utf8_bytes': len(body), 'reserved_nanodollars': maximum, 'estimated_peak_usd_maximum': maximum / 1e9,
               'schema_validation': 'not_run', 'output_exists': False, 'exit_code': 1}
    atomic(output / 'run.json', metrics)
    started = time.monotonic()
    # Reservation persists even if credential read, network, process, or disk fails.
    # No subprocess, environment copy, arbitrary exception text or header logging.
    outcome, raw, status = 'credential_unavailable', None, None
    try:
        key = read_regular(args.key_file, 4096).decode().strip()
        if not key or not key.isascii() or any(c.isspace() for c in key): refuse('credential_unavailable')
        outcome, raw, status = sender(body, key)
    except Exception:
        outcome, raw, status = 'credential_unavailable', None, None
    finally:
        if 'key' in locals(): del key
    usage, proposal = None, None
    if raw is not None:
        try:
            envelope = strict_json(raw)
            if type(envelope) is not dict: refuse('invalid_envelope')
            usage = normalized_usage(envelope.get('usage'))
            metrics.update(returned_model=safe_identifier(envelope.get('model')), request_id=safe_identifier(envelope.get('id')),
                           system_fingerprint=safe_identifier(envelope.get('system_fingerprint')))
            choices = envelope.get('choices')
            if type(choices) is not list or len(choices) != 1 or type(choices[0]) is not dict: refuse('invalid_choices')
            finish = choices[0].get('finish_reason')
            metrics['finish_reason'] = safe_identifier(finish)
            if finish != 'stop': refuse('incomplete_response')
            message = choices[0].get('message')
            if type(message) is not dict: refuse('invalid_message')
            if message.get('tool_calls') or message.get('function_call'):
                metrics['tool_items'] = ['tool_attempt']
                refuse('unexpected_tool_attempt')
            proposal = source_response(strict_json(message['content']), names)
            outcome = 'success'
        except Exception:
            outcome = 'invalid_response'; proposal = None
        # Raw reasoning is deliberately not saved by this reusable provider.
        metrics['raw_response_sha256'] = sha(raw)
    charged = ledger.settle(attempt_id, outcome, usage)
    metrics.update(outcome=outcome, http_status=status, usage=[usage] if usage is not None else [],
                   elapsed_seconds=round(time.monotonic() - started, 3), timed_out=outcome == 'timeout',
                   estimated_peak_nanodollars=price_usage(usage), charged_nanodollars=charged,
                   charge_is_uncertain_reservation=usage is None)
    if proposal is not None:
        atomic(output / 'response.json', proposal)
        metrics.update(schema_validation='pass', output_exists=True, exit_code=0,
                       response_sha256=sha(read_regular(output / 'response.json')),
                       source_sha256=sha(proposal['source'].encode()))
    elif outcome == 'invalid_response': metrics['schema_validation'] = 'fail'
    atomic(output / 'run.json', metrics)
    return metrics['exit_code']

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init-ledger', help='explicit first-time initialization; refuses existing directory')
    init.add_argument('--ledger-dir', type=Path, required=True)
    init.add_argument('--opening-debit-nanodollars', type=int, required=True,
                      help='explicit conservative charge for earlier calls on initialization day')
    init.add_argument('--opening-evidence', type=Path, action='append', default=[],
                      help='prior run.json; only its SHA-256 is recorded; repeat as needed')
    request = sub.add_parser('request')
    for name in ('manifest', 'root', 'packet', 'output', 'ledger-dir'):
        request.add_argument('--' + name, type=Path, required=True)
    request.add_argument('--manifest-sha256', required=True)
    request.add_argument('--key-file', type=Path, default=Path.home() / '.deepseek.key')
    args = parser.parse_args()
    try:
        if args.command == 'init-ledger':
            evidence = [sha(read_regular(path)) for path in args.opening_evidence]
            Ledger.initialize(args.ledger_dir, args.opening_debit_nanodollars, evidence)
            return 0
        return run(args)
    except Refusal as exc:
        print('DeepSeek client refused: ' + str(exc), file=sys.stderr); return 1
    except BaseException:
        # A crash/interruption leaves its reservation charged. Never print a
        # traceback that might contain credentials or an arbitrary server body.
        print('DeepSeek client stopped; inspect local ledger/run record.', file=sys.stderr); return 1

if __name__ == '__main__': raise SystemExit(main())

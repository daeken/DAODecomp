"""Bounded batch transport with a fresh POSIX process/session for every case.

Only an opt-in adapter may preload immutable data. The clean, single-threaded
supervisor never executes a case handler. No native/Unicorn state is recycled.
This is process lifetime isolation, not a security sandbox or a game loader.
"""
from __future__ import annotations
import contextlib
import ctypes
import errno
import math
import os
from pathlib import Path
import platform
import selectors
import signal
import subprocess
import sys
import tempfile
import threading
import time

from .harness import (canonical, digest, differing_paths, file_hash, parse_json,
                      validate_cases, validate_contract, validate_observation)

MAX_BATCH_CASES = 128
MAX_FRAME_BYTES = 256 * 1024
MAX_TOTAL_CASES = 8192
MAX_TOTAL_BYTES = 32 * 1024 * 1024
MAX_CASE_OUTPUT = 64 * 1024
MAX_CASE_STDERR = 4096
STATE_ENV = 'DAODECOMP_BATCH_CHILD_STATE'
TIMEOUT_ENV = 'DAODECOMP_BATCH_CASE_TIMEOUT'

# Darwin reports EPERM for a process group containing only an unreaped zombie,
# even for our own child. Do not ignore EPERM for a live inaccessible process.
# These system APIs are loaded before fork; they never invoke candidate code.
_DARWIN_PROC = None
if sys.platform == 'darwin':
    _DARWIN_PROC = ctypes.CDLL('/usr/lib/libproc.dylib', use_errno=True)
    _DARWIN_PROC.proc_listpgrppids.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_int]
    _DARWIN_PROC.proc_listpgrppids.restype = ctypes.c_int
    _DARWIN_PROC.proc_pidinfo.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_uint64, ctypes.c_void_p, ctypes.c_int]
    _DARWIN_PROC.proc_pidinfo.restype = ctypes.c_int


def _darwin_no_live_members(group):
    members = (ctypes.c_int * 1024)()
    ctypes.set_errno(0)
    count = _DARWIN_PROC.proc_listpgrppids(group, members, ctypes.sizeof(members))
    if (count == 0 and ctypes.get_errno() not in (0, errno.ESRCH)) or count < 0 or count >= len(members):
        return False
    for pid in members[:count]:
        # PROC_PIDT_SHORTBSDINFO, SDK struct proc_bsdshortinfo: 64 bytes;
        # pbsi_status is uint32 at offset 12. ESRCH also covers zombie records.
        info = (ctypes.c_uint32 * 16)()
        ctypes.set_errno(0)
        size = _DARWIN_PROC.proc_pidinfo(pid, 13, 0, info, ctypes.sizeof(info))
        if size == 0 and ctypes.get_errno() == errno.ESRCH:
            continue
        if size != ctypes.sizeof(info) or info[3] != 5:  # SZOMB
            return False
    return True


def _positive(value, name, upper):
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 < value <= upper:
        raise ValueError(f'{name} must be positive, finite and at most {upper}')


def _kill_group(pid):
    try:
        os.killpg(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    except PermissionError:
        if _DARWIN_PROC is None or not _darwin_no_live_members(pid):
            raise


def _state(path, pid):
    if path is None:
        return
    path = Path(path)
    temp = path.with_suffix('.tmp')
    temp.write_text(str(pid), encoding='ascii')
    temp.replace(path)


def _cleanup_worker(proc, state_path):
    # Freeze the supervisor before reading its active-case record. A forked child
    # waits on a start gate until this record is published, so an outer failure
    # cannot leave an unrecorded case executing. Child leaders are not reaped until
    # their groups are killed and the record is cleared, avoiding stale PID reuse.
    with contextlib.suppress(ProcessLookupError):
        os.kill(proc.pid, signal.SIGSTOP)
    try:
        raw = Path(state_path).read_text(encoding='ascii')
        pid = int(raw)
        if pid > 1:
            _kill_group(pid)
    except (OSError, ValueError):
        pass
    _kill_group(proc.pid)
    proc.wait()


def fresh_call(handler, request, *, timeout=5, output_cap=MAX_CASE_OUTPUT,
               stderr_cap=MAX_CASE_STDERR, state_path=None):
    """Execute handler only in a fresh child, capture bounded bytes, kill its group."""
    if os.name != 'posix' or not hasattr(os, 'fork'):
        raise RuntimeError('fresh-fork batching requires POSIX; use single-case fallback')
    if threading.active_count() != 1:
        raise RuntimeError('fork supervisor must be single-threaded')
    _positive(timeout, 'case timeout', 60)
    if type(output_cap) is not int or not 1 <= output_cap <= MAX_CASE_OUTPUT:
        raise ValueError('invalid case output cap')
    if type(stderr_cap) is not int or not 1 <= stderr_cap <= MAX_CASE_STDERR:
        raise ValueError('invalid case stderr cap')
    sys.stdout.flush(); sys.stderr.flush()
    read_out, write_out = os.pipe()
    read_err, write_err = os.pipe()
    gate_read, gate_write = os.pipe()
    ready_read, ready_write = os.pipe()
    pid = os.fork()
    if pid == 0:
        try:
            os.close(gate_write); os.close(ready_read)
            os.setsid()
            os.write(ready_write, b'1'); os.close(ready_write)
            if os.read(gate_read, 1) != b'1':
                os._exit(125)
            os.dup2(write_out, 1); os.dup2(write_err, 2)
            null = os.open(os.devnull, os.O_RDONLY)
            os.dup2(null, 0)
            # Handlers have only standard streams: no inherited transport/state
            # descriptors. Immutable slices/native code are already in memory.
            for fd in os.listdir('/dev/fd'):
                if fd.isdigit() and int(fd) >= 3:
                    with contextlib.suppress(OSError): os.close(int(fd))
            observation = handler(request)
            sys.stdout.flush(); sys.stderr.flush()
            raw = canonical(observation).encode('utf-8')
            while raw:
                raw = raw[os.write(1, raw):]
            os._exit(0)
        except BaseException as exc:
            with contextlib.suppress(BaseException):
                os.write(2, (type(exc).__name__ + ': ' + str(exc))[:2048].encode('utf-8', errors='replace'))
            os._exit(1)
    os.close(write_out); os.close(write_err); os.close(gate_read); os.close(ready_write)
    selector = selectors.DefaultSelector()
    buffers = {read_out: bytearray(), read_err: bytearray()}
    caps = {read_out: output_cap, read_err: stderr_cap}
    reaped = False
    error = None
    started = time.monotonic()
    try:
        # Wait for setsid before publishing the active group. Before publication
        # the case cannot execute: an outer failure closes the gate and it exits.
        if os.read(ready_read, 1) != b'1':
            raise RuntimeError('child failed to establish its session')
        os.close(ready_read); ready_read = -1
        _state(state_path, pid)
        os.write(gate_write, b'1'); os.close(gate_write); gate_write = -1
        for fd in buffers:
            os.set_blocking(fd, False)
            selector.register(fd, selectors.EVENT_READ)
        while True:
            remaining = timeout - (time.monotonic() - started)
            if remaining <= 0:
                error = {'error': 'timeout'}
                break
            for key, _ in selector.select(min(remaining, .01)):
                data = os.read(key.fd, min(8192, caps[key.fd] + 1 - len(buffers[key.fd])))
                if not data:
                    selector.unregister(key.fd)
                else:
                    buffers[key.fd].extend(data)
                    if len(buffers[key.fd]) > caps[key.fd]:
                        error = {'error': 'oversized_observation' if key.fd == read_out else 'oversized_stderr'}
                        break
            if error:
                break
            # WNOWAIT keeps the child leader reserved until group cleanup. That
            # closes the PID-reuse window when descendants outlive their parent.
            info = os.waitid(os.P_PID, pid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
            if info is not None:
                # Descendants retaining stdout must not keep a successful case
                # alive. Kill the entire case group before draining remaining data.
                _kill_group(pid)
                if not selector.get_map():
                    break
        _kill_group(pid)
        _state(state_path, 0)
        _, raw_status = os.waitpid(pid, 0)
        reaped = True
        diagnostics = bytes(buffers[read_err]).decode('utf-8', errors='replace')
        if error:
            return error
        if raw_status != 0:
            return {'error': 'runner_exit', 'exit_code': os.waitstatus_to_exitcode(raw_status), 'stderr': diagnostics}
        try:
            return {'observation': parse_json(bytes(buffers[read_out]).decode('utf-8'))}
        except (ValueError, UnicodeError) as exc:
            return {'error': 'invalid_runner', 'detail': str(exc)}
    finally:
        if not reaped:
            _kill_group(pid)
            _state(state_path, 0)
            with contextlib.suppress(ChildProcessError):
                os.waitpid(pid, 0)
        selector.close()
        for fd in (read_out, read_err, gate_write, ready_read):
            if fd >= 0:
                with contextlib.suppress(OSError): os.close(fd)


def serve(handler, validate_request, *, timeout=5):
    """Serve bounded JSON-line batch frames; cases run only in fresh_call children."""
    if TIMEOUT_ENV in os.environ:
        timeout = float(os.environ[TIMEOUT_ENV])
    _positive(timeout, 'case timeout', 60)
    seen = set()
    count = 0
    batch_id = 0
    aborted = False
    stream = sys.stdin.buffer
    while True:
        raw = stream.readline(MAX_FRAME_BYTES + 1)
        if not raw:
            return
        if len(raw) > MAX_FRAME_BYTES or not raw.endswith(b'\n'):
            raise ValueError('oversized or unterminated batch frame')
        frame = parse_json(raw.decode('utf-8'))
        if (type(frame) is not dict or set(frame) != {'schema_version', 'batch_id', 'requests'}
                or type(frame['schema_version']) is not int or frame['schema_version'] != 1
                or type(frame['batch_id']) is not int or frame['batch_id'] != batch_id
                or type(frame['requests']) is not list or not 1 <= len(frame['requests']) <= MAX_BATCH_CASES):
            raise ValueError('invalid batch envelope')
        for request in frame['requests']:
            validate_request(request)
            identity = (request['function_id'], request['case']['id'])
            if identity in seen:
                raise ValueError('duplicate case identity')
            seen.add(identity)
        count += len(frame['requests'])
        if count > MAX_TOTAL_CASES:
            raise ValueError('too many cases')
        results = []
        children = 0
        for request in frame['requests']:
            if aborted:
                run = {'error': 'worker_aborted_after_error'}
            else:
                run = fresh_call(handler, request, timeout=timeout, state_path=os.environ.get(STATE_ENV))
                children += 1
                if 'error' in run:
                    aborted = True
            results.append({'request_sha256': digest(request), 'run': run})
        response = {'schema_version': 1, 'batch_id': batch_id, 'results': results, 'child_processes': children}
        encoded = canonical(response).encode('utf-8') + b'\n'
        if len(encoded) > MAX_TOTAL_BYTES:
            raise ValueError('oversized batch response')
        sys.stdout.buffer.write(encoded); sys.stdout.buffer.flush()
        batch_id += 1


def invoke_batches(command, cases, contract, *, timeout=5, batch_size=MAX_BATCH_CASES,
                   worker_timeout=None, output_cap=MAX_TOTAL_BYTES):
    if os.name != 'posix' or not hasattr(os, 'fork') or not hasattr(os, 'waitid') or not hasattr(os, 'WNOWAIT'):
        raise RuntimeError('fresh-child batching requires POSIX waitid/WNOWAIT; use single-case fallback')
    validate_contract(contract); validate_cases(cases, contract)
    _positive(timeout, 'case timeout', 60)
    if type(batch_size) is not int or not 1 <= batch_size <= MAX_BATCH_CASES:
        raise ValueError('invalid batch size')
    if len(cases) > MAX_TOTAL_CASES:
        raise ValueError('too many cases')
    if not command or not all(type(a) is str for a in command):
        raise ValueError('invalid command')
    if type(output_cap) is not int or not 1 <= output_cap <= MAX_TOTAL_BYTES:
        raise ValueError('invalid worker output cap')
    if worker_timeout is None:
        worker_timeout = min(600, timeout * len(cases) + 10)
    _positive(worker_timeout, 'worker timeout', 3600)
    requests = [{'schema_version':1, 'function_id':contract['function_id'], 'case':case} for case in cases]
    frames = [{'schema_version':1, 'batch_id':i // batch_size, 'requests':requests[i:i+batch_size]}
              for i in range(0, len(requests), batch_size)]
    encoded = [(canonical(frame) + '\n').encode('utf-8') for frame in frames]
    if any(len(raw) > MAX_FRAME_BYTES for raw in encoded) or sum(map(len, encoded)) > MAX_TOTAL_BYTES:
        raise ValueError('oversized request batch')
    failure = None; output = b''; children = 0
    with tempfile.TemporaryDirectory(prefix='dao-batch-') as directory:
        state_path = Path(directory)/'active-child'
        env = dict(os.environ, LC_ALL='C', LANG='C', TZ='UTC', PYTHONHASHSEED='0',
                   **{STATE_ENV:str(state_path),TIMEOUT_ENV:str(timeout)})
        with tempfile.TemporaryFile() as inp, tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
            inp.write(b''.join(encoded)); inp.seek(0)
            proc = None
            try:
                proc = subprocess.Popen(command, stdin=inp, stdout=out, stderr=err, env=env, start_new_session=True)
                started = time.monotonic()
                info = None
                while info is None:
                    if os.fstat(out.fileno()).st_size > output_cap or os.fstat(err.fileno()).st_size > MAX_CASE_STDERR:
                        failure = {'error':'oversized_worker_output'}; break
                    if time.monotonic()-started >= worker_timeout:
                        failure = {'error':'worker_timeout'}; break
                    time.sleep(.005)
                    info = os.waitid(os.P_PID, proc.pid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
                if failure is None:
                    if os.fstat(out.fileno()).st_size > output_cap or os.fstat(err.fileno()).st_size > MAX_CASE_STDERR:
                        failure = {'error':'oversized_worker_output'}
                    elif info.si_code != os.CLD_EXITED or info.si_status != 0:
                        err.seek(0)
                        code = info.si_status if info.si_code == os.CLD_EXITED else -info.si_status
                        failure = {'error':'worker_exit','exit_code':code,'stderr':err.read(MAX_CASE_STDERR).decode('utf-8',errors='replace')}
                if failure is None:
                    out.seek(0); output = out.read(output_cap+1)
            except OSError as exc:
                failure = {'error':'invalid_runner','detail':str(exc)}
            finally:
                if proc is not None:
                    _cleanup_worker(proc, state_path)
    try:
        if failure:
            return [dict(failure) for _ in cases], {'supervisor_processes':1,'case_processes':None}
        lines = output.splitlines()
        if len(lines) != len(frames):
            raise ValueError('missing or extra batch response')
        runs = []
        for frame, line in zip(frames, lines):
            response = parse_json(line.decode('utf-8'))
            if (type(response) is not dict or set(response) != {'schema_version','batch_id','results','child_processes'}
                    or type(response['schema_version']) is not int or response['schema_version'] != 1
                    or type(response['batch_id']) is not int or response['batch_id'] != frame['batch_id']
                    or type(response['child_processes']) is not int or not 0 <= response['child_processes'] <= len(frame['requests'])
                    or type(response['results']) is not list or len(response['results']) != len(frame['requests'])):
                raise ValueError('invalid batch response identity/count')
            attempted = sum(type(result) is dict and type(result.get('run')) is dict
                            and result['run'].get('error') != 'worker_aborted_after_error'
                            for result in response['results'])
            if response['child_processes'] != attempted:
                raise ValueError('case process count mismatch')
            children += response['child_processes']
            for request, result in zip(frame['requests'], response['results']):
                if (type(result) is not dict or set(result) != {'request_sha256','run'}
                        or result['request_sha256'] != digest(request) or type(result['run']) is not dict):
                    raise ValueError('missing, duplicate or reordered response identity')
                run = result['run']
                if set(run) == {'observation'}:
                    validate_observation(run['observation'], request['case'], contract)
                elif type(run.get('error')) is not str or not run['error'] or 'observation' in run:
                    raise ValueError('invalid error response')
                runs.append(run)
        if len(runs) != len(cases):
            raise ValueError('dropped cases')
        return runs, {'supervisor_processes':1,'case_processes':children}
    except (ValueError, UnicodeError, KeyError) as exc:
        return [{'error':'invalid_batch_response','detail':str(exc)} for _ in cases], {'supervisor_processes':1,'case_processes':None}


def compare_batch(contract, cases, oracle, candidate, *, repeats=2, timeout=5,
                  artifacts=(), batch_size=MAX_BATCH_CASES, worker_timeout=None):
    validate_contract(contract); validate_cases(cases, contract)
    if type(repeats) is not int or repeats < 2:
        raise ValueError('at least two independent executions per side are required')
    hashes = {str(p):file_hash(p) for p in artifacts}
    observations = [[], []]
    counts = []
    for side, command in enumerate((oracle,candidate)):
        for _ in range(repeats):
            runs, processes = invoke_batches(command, cases, contract, timeout=timeout,
                                            batch_size=batch_size, worker_timeout=worker_timeout)
            observations[side].append(runs); counts.append(processes)
    rows = []
    for i, case in enumerate(cases):
        original = [run[i] for run in observations[0]]
        replacement = [run[i] for run in observations[1]]
        if any('error' in run for run in original+replacement): status='runner_error'
        elif any(canonical(x) != canonical(original[0]) for x in original[1:]): status='oracle_nondeterministic'
        elif any(canonical(x) != canonical(replacement[0]) for x in replacement[1:]): status='candidate_nondeterministic'
        elif canonical(original[0]) != canonical(replacement[0]): status='mismatch'
        else: status='corpus_pass'
        row = {'case_id':case['id'], 'status':status, 'case_sha256':digest(case)}
        if status == 'corpus_pass': row['observation_sha256']=digest(original[0]['observation'])
        else:
            row.update(case=case, oracle=original, candidate=replacement)
            if status == 'mismatch': row['differing_paths']=differing_paths(original[0]['observation'],replacement[0]['observation'])
        rows.append(row)
    unchanged = all(Path(p).is_file() and file_hash(p)==h for p,h in hashes.items())
    passed = unchanged and all(row['status']=='corpus_pass' for row in rows)
    return {'schema_version':1,'function_id':contract['function_id'],'kind':contract['kind'],
            'status':'corpus_pass' if passed else 'failed','proof':False,'contract_sha256':digest(contract),
            'corpus_sha256':digest(cases),'oracle_command':oracle,'candidate_command':candidate,
            'artifacts_sha256':hashes,'artifacts_unchanged':unchanged,
            'host':{'platform':platform.platform(),'python':sys.version.split()[0]},'repeats':repeats,
            'timeout_seconds':timeout,'cases':rows,'execution_backend':{'name':'posix-fresh-child-batch-v1',
            'batch_size':batch_size,'case_process_isolation':'fresh-fork-session','supervisor_reuse':'none across sides or repetitions',
            'process_counts':counts,'limitations':'POSIX only; single-threaded immutable preload supervisor; no native Windows corroboration; not a security sandbox'}}

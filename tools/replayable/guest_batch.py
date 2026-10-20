"""Bounded serial VC8 transport, with no scheduler, retry, comparison or acceptance.

The caller owns the global unknown barrier and holds the registered shared flock
through execute(). A dispatch-start marker permanently consumes a prepared batch,
including on timeout. Preserve that workspace and reconcile externally; never retry.
"""
from dataclasses import dataclass
from pathlib import Path
try:
    import fcntl
except ImportError:  # The dispatch host is POSIX; pure receipt parsing remains portable.
    fcntl = None
import hashlib
import json
import math
import os
import re
import shutil
import time
import uuid

MAX_ITEMS = 16
FLAGS = ('/c', '/O2', '/Ob1', '/Oy', '/Gy', '/Z7', '/Zl', '/GS', '/GR-', '/EHsc')
FLAG_PROFILES = (FLAGS, tuple('/GS-' if x == '/GS' else x for x in FLAGS))


class AmbiguousOutcome(RuntimeError):
    """Execution may have occurred; artifacts must be retained, never replayed."""


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate_json_key')
        result[key] = value
    return result


def read_json(path):
    require(path.is_file() and not path.is_symlink() and path.stat().st_size < 1024 * 1024,
            'missing_or_invalid_receipt:' + path.name)
    return json.loads(path.read_text(encoding='utf-8-sig'), object_pairs_hook=unique_object)


def plain_path(path):
    path = Path(path).absolute()
    require(not any(p.is_symlink() for p in (path, *path.parents)), 'symlink_path')
    return path


def windows_path(value):
    # CMD metacharacters, quotes, expansions and traversal are not supported.
    require(isinstance(value, str) and re.fullmatch(r'(?:[A-Za-z]:\\|\\\\)[A-Za-z0-9_. \\-]+', value)
            and '..' not in value.split('\\'), 'unsafe_windows_path')
    return value


def quote(value):
    return "'" + value.replace("'", "''") + "'"


@dataclass(frozen=True)
class Item:
    id: str
    source: Path
    source_sha256: str
    flags: tuple


@dataclass(frozen=True)
class PreparedBatch:
    output: Path
    transfer: Path
    manifest_sha256: str
    nonce: str
    guest: str
    shared: str
    vm_name: str
    lock_path: Path


def prepare(items, output, profile, compiler_sha256):
    """Copy hash-bound inputs and render scripts; does not contact the VM.

    profile uses the existing transport profile keys plus shared_vm_lock. The
    integrated caller must bind the profile/helper hashes before invoking this.
    Only the two existing complete VC8 flag profiles are supported.
    """
    items = tuple(items)
    require(1 <= len(items) <= MAX_ITEMS, 'batch_size')
    require(re.fullmatch('[0-9a-f]{64}', compiler_sha256 or '') is not None, 'compiler_sha256')
    require(profile['protocol'] == 'prlctl-sync-copy-v1', 'transport_protocol')
    require(isinstance(profile['vm_name'], str) and profile['vm_name'], 'vm_name')
    for key in ('guest_root', 'guest_transfer_root', 'vcvars'):
        windows_path(profile[key])
    ids = set()
    for item in items:
        require(re.fullmatch('[a-z][a-z0-9-]{0,63}', item.id or '') is not None and item.id not in ids,
                'invalid_or_duplicate_item_id')
        require(item.id.lower() not in {'con', 'prn', 'aux', 'nul', *['com'+str(n) for n in range(1, 10)], *['lpt'+str(n) for n in range(1, 10)]}, 'reserved_item_id')
        ids.add(item.id)
        require(type(item.flags) is tuple and item.flags in FLAG_PROFILES, 'unsupported_flags')
        require(re.fullmatch('[0-9a-f]{64}', item.source_sha256 or '') is not None, 'source_sha256')
        source = plain_path(item.source)
        require(source.is_file() and digest(source.read_bytes()) == item.source_sha256, 'source_hash_mismatch')
    output = plain_path(output)
    require(not output.exists(), 'output_exists')
    bridge = plain_path(profile['host_transfer_root'])
    require(bridge.is_dir(), 'transfer_root_missing')
    lock = plain_path(profile['shared_vm_lock'])
    require(lock.is_file(), 'registered_lock_missing')
    nonce = uuid.uuid4().hex
    name = 'coff-batch-' + nonce
    transfer = bridge / name
    guest = profile['guest_root'] + '\\' + name
    shared = profile['guest_transfer_root'] + '\\' + name
    output.mkdir(mode=0o700)
    transfer.mkdir(mode=0o700)
    entries = []
    for item in items:
        folder = transfer / item.id
        folder.mkdir(mode=0o700)
        data = Path(item.source).read_bytes()
        require(digest(data) == item.source_sha256, 'source_changed_during_prepare')
        (folder / 'candidate.cpp').write_bytes(data)
        entries.append(dict(id=item.id, source_sha256=item.source_sha256, flags=list(item.flags)))
    manifest = dict(schema=1, nonce=nonce, items=entries, compiler_sha256=compiler_sha256,
                    guest=guest, shared=shared, vm_name=profile['vm_name'], vcvars=profile['vcvars'])
    encoded = canonical(manifest)
    (transfer / 'manifest.json').write_bytes(encoded)
    (transfer / 'run.ps1').write_text(render_script(manifest), encoding='utf-8')
    for name in ('manifest.json', 'run.ps1'):
        shutil.copy2(transfer / name, output / name)
    return PreparedBatch(output, transfer, digest(encoded), nonce, guest, shared, profile['vm_name'], lock)


def render_script(m):
    # Compiler arguments are validated fixed profiles, not arbitrary shell text.
    vcvars = m['vcvars']
    compiler = vcvars.rsplit('\\', 1)[0] + '\\bin\\cl.exe'
    return f'''$ErrorActionPreference='Stop'
$guest={quote(m['guest'])}
$shared={quote(m['shared'])}
if(Test-Path -LiteralPath $guest){{throw 'guest_workspace_exists'}}
$all=[Diagnostics.Stopwatch]::StartNew()
$copy=[Diagnostics.Stopwatch]::StartNew()
Copy-Item -Recurse -LiteralPath $shared -Destination $guest
$copy.Stop()
Set-Location -LiteralPath $guest
function Save($name,$value){{
 $temp=$name+'.tmp'
 if((Test-Path -LiteralPath $name) -or (Test-Path -LiteralPath $temp)){{throw 'receipt_already_exists'}}
 $value | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 -LiteralPath $temp
 Move-Item -LiteralPath $temp -Destination $name
}}
try{{
 $m=Get-Content -Raw -LiteralPath manifest.json | ConvertFrom-Json
 if((Get-FileHash -Algorithm SHA256 manifest.json).Hash.ToLower() -ne {quote(digest(canonical(m)))}){{throw 'manifest_hash'}}
 $p={quote(compiler)}
 $info=Get-Item -LiteralPath $p
 $compiler=[PSCustomObject]@{{path=$p;sha256=(Get-FileHash -Algorithm SHA256 -LiteralPath $p).Hash.ToLower();file_version=$info.VersionInfo.FileVersion}}
 if($compiler.sha256 -ne $m.compiler_sha256){{throw 'compiler_hash'}}
 Save 'compiler.json' $compiler
 $setup=[Diagnostics.Stopwatch]::StartNew()
 & cmd.exe /d /c {quote('call "'+vcvars+'" > environment.log 2>&1 && set > environment.txt')}
 $setupExit=$LASTEXITCODE
 if($setupExit -ne 0){{throw 'vcvars_failed'}}
 foreach($line in Get-Content -LiteralPath environment.txt){{
  if($line -match '^([A-Za-z_][A-Za-z0-9_()]*)=(.*)$'){{[Environment]::SetEnvironmentVariable($Matches[1],$Matches[2],'Process')}}
 }}
 $setup.Stop()
 if($env:CL -or $env:_CL_){{throw 'implicit_compiler_flags_unsupported'}}
 $receipts=@()
 foreach($item in $m.items){{
  Push-Location -LiteralPath $item.id
  try{{
   $actual=(Get-FileHash -Algorithm SHA256 -LiteralPath candidate.cpp).Hash.ToLower()
   if($actual -ne $item.source_sha256){{throw 'source_hash'}}
   Save 'start.json' ([PSCustomObject]@{{schema=1;nonce=$m.nonce;id=$item.id;source_sha256=$actual}})
   $clock=[Diagnostics.Stopwatch]::StartNew()
   $command='"'+$p+'" /nologo '+($item.flags -join ' ')+' /FAs /Facandidate.asm /Focandidate.obj candidate.cpp > build.log 2>&1'
   & cmd.exe /d /s /c ('"'+$command+'"')
   $code=$LASTEXITCODE
   $clock.Stop()
   $object=$null
   if(Test-Path -LiteralPath candidate.obj){{$object=(Get-FileHash -Algorithm SHA256 -LiteralPath candidate.obj).Hash.ToLower()}}
   $receipt=[PSCustomObject]@{{schema=1;nonce=$m.nonce;id=$item.id;source_sha256=$actual;flags=@($item.flags);compiler_sha256=$compiler.sha256;exit_code=$code;object_sha256=$object;cl_seconds=$clock.Elapsed.TotalSeconds}}
   Save 'exit.json' $receipt
   $receipts+=,$receipt
  }} finally{{Pop-Location}}
 }}
 $all.Stop()
 Save 'completed.json' ([PSCustomObject]@{{schema=1;nonce=$m.nonce;manifest_sha256={quote(digest(canonical(m)))};items=$receipts;setup_seconds=$setup.Elapsed.TotalSeconds;copy_in_seconds=$copy.Elapsed.TotalSeconds;guest_seconds=$all.Elapsed.TotalSeconds}})
}} finally{{
 Copy-Item -Recurse -Force ($guest+'\\*') $shared
}}
if(@($receipts | Where-Object {{$_.exit_code -ne 0}}).Count -ne 0){{exit 1}}
exit 0
'''


def check_lock(batch, fd):
    """Reject wrong/unheld fd; caller acquires/release policy remains external."""
    require(fcntl is not None, 'POSIX_flock_host_required')
    stat = os.fstat(fd)
    lockstat = batch.lock_path.stat()
    require((stat.st_dev, stat.st_ino) == (lockstat.st_dev, lockstat.st_ino), 'wrong_lock_fd')
    # A shared probe must also fail: a caller's shared lock is insufficient.
    with batch.lock_path.open('r+') as probe:
        try:
            fcntl.flock(probe, fcntl.LOCK_SH | fcntl.LOCK_NB)
        except BlockingIOError:
            pass
        else:
            fcntl.flock(probe, fcntl.LOCK_UN)
            raise ValueError('caller_exclusive_lock_not_held')
    # Independent open file description cannot acquire while the caller holds it.
    with batch.lock_path.open('r+') as probe:
        try:
            fcntl.flock(probe, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise ValueError('caller_fd_does_not_hold_lock') from exc
            return
        else:
            fcntl.flock(probe, fcntl.LOCK_UN)
            raise ValueError('caller_lock_not_held')


def collect(batch, returncode):
    """Validate complete envelope and every item; never infer exit from an object."""
    try:
        m = read_json(batch.output / 'manifest.json')
        require(digest((batch.output / 'manifest.json').read_bytes()) == batch.manifest_sha256, 'manifest_changed')
        require(m['nonce'] == batch.nonce, 'batch_nonce')
        end = read_json(batch.output / 'completed.json')
        require(type(end['schema']) is int and end['schema'] == 1 and end['nonce'] == batch.nonce and end['manifest_sha256'] == batch.manifest_sha256,
                'stale_batch_receipt')
        require(type(end['items']) is list and [x['id'] for x in end['items']] == [x['id'] for x in m['items']],
                'missing_duplicate_or_reordered_items')
        compiler = read_json(batch.output / 'compiler.json')
        require(compiler['sha256'] == m['compiler_sha256'] and compiler['path'] == m['vcvars'].rsplit('\\', 1)[0]+'\\bin\\cl.exe', 'compiler_mismatch')
        results = []
        for item, embedded in zip(m['items'], end['items']):
            folder = batch.output / item['id']
            start = read_json(folder / 'start.json')
            exit = read_json(folder / 'exit.json')
            expected_start = dict(schema=1, nonce=batch.nonce, id=item['id'], source_sha256=item['source_sha256'])
            require(type(start.get('schema')) is int and start == expected_start, 'stale_or_malformed_start')
            require(type(exit.get('schema')) is int and exit == embedded, 'envelope_item_mismatch')
            require(all(exit[k] == v for k, v in expected_start.items()) and exit['flags'] == item['flags']
                    and exit['compiler_sha256'] == m['compiler_sha256'], 'item_binding_mismatch')
            require(type(exit['exit_code']) is int and -0x80000000 <= exit['exit_code'] <= 0xffffffff, 'malformed_exit')
            require(type(exit['cl_seconds']) in (int, float) and math.isfinite(exit['cl_seconds']) and exit['cl_seconds'] >= 0, 'malformed_timing')
            require(not (folder / 'candidate.cpp').is_symlink() and digest((folder / 'candidate.cpp').read_bytes()) == item['source_sha256'], 'returned_source_mismatch')
            obj = folder / 'candidate.obj'
            if exit['exit_code'] == 0:
                require(obj.is_file() and not obj.is_symlink() and digest(obj.read_bytes()) == exit['object_sha256'], 'object_hash_mismatch')
            elif obj.exists():
                require(not obj.is_symlink() and digest(obj.read_bytes()) == exit['object_sha256'], 'failed_object_hash_mismatch')
            else:
                require(exit['object_sha256'] is None, 'missing_failed_object')
            results.append(dict(id=item['id'], exit_code=exit['exit_code'], folder=str(folder), object=str(obj) if obj.exists() else None))
        require(type(returncode) is int and returncode == (1 if any(x['exit_code'] != 0 for x in results) else 0), 'transport_exit_mismatch')
        return dict(status='completed', succeeded=returncode == 0, items=results, envelope=str(batch.output / 'completed.json'))
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise AmbiguousOutcome('unconfirmed_batch_no_retry:' + str(exc)) from exc


def execute(batch, *, lock_fd, authorization, run_vm, timeout=180):
    """One synchronous dispatch. run_vm(script, vm_name, timeout=...) mirrors vm().

    authorization is the caller's persisted decision ID after checking its global
    unknown barrier. This module records it but cannot validate queue authority.
    The caller must keep lock_fd held until this function returns or raises, and
    persist ambiguous outcomes as barriers. No artifact cleanup or retry occurs.
    """
    require(isinstance(authorization, str) and re.fullmatch('[A-Za-z0-9_.:-]{1,160}', authorization) is not None,
            'caller_authorization_required')
    require(type(timeout) is int and 1 <= timeout <= 300, 'timeout')
    check_lock(batch, lock_fd)
    require(digest((batch.transfer / 'manifest.json').read_bytes()) == batch.manifest_sha256
            and (batch.output / 'manifest.json').read_bytes() == (batch.transfer / 'manifest.json').read_bytes(), 'prepared_manifest_changed')
    m = read_json(batch.output / 'manifest.json')
    require((batch.output / 'run.ps1').read_bytes() == (batch.transfer / 'run.ps1').read_bytes() == render_script(m).encode('utf-8'), 'prepared_script_changed')
    require(set(p.name for p in batch.transfer.iterdir()) == {'manifest.json', 'run.ps1', *[x['id'] for x in m['items']]}, 'stale_transfer')
    for item in m['items']:
        folder = plain_path(batch.transfer / item['id'])
        require(set(p.name for p in folder.iterdir()) == {'candidate.cpp'} and digest((folder/'candidate.cpp').read_bytes()) == item['source_sha256'], 'stale_or_changed_item')
    # Exclusive durable marker forbids replay even after transport exceptions.
    with (batch.output / 'dispatch-start.json').open('x') as marker:
        marker.write(canonical(dict(nonce=batch.nonce, authorization=authorization, started=time.time())).decode())
        marker.flush()
        os.fsync(marker.fileno())
    directory_fd = os.open(batch.output, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)
    started = time.perf_counter()
    try:
        invocation = '& ([scriptblock]::Create([System.IO.File]::ReadAllText(' + quote(batch.shared+'\\run.ps1') + ')))'
        result = run_vm(invocation, batch.vm_name, timeout=timeout)
        (batch.output / 'transport.stdout').write_bytes(result.stdout)
        (batch.output / 'transport.stderr').write_bytes(result.stderr)
        for path in batch.transfer.iterdir():
            require(not path.is_symlink(), 'returned_symlink')
            if path.is_dir():
                require(not any(p.is_symlink() for p in path.rglob('*')), 'returned_symlink')
                shutil.copytree(path, batch.output/path.name, dirs_exist_ok=False)
            elif path.name not in ('manifest.json', 'run.ps1'):
                shutil.copy2(path, batch.output/path.name)
        outcome = collect(batch, result.returncode)
        outcome['transport_exit_code'] = result.returncode
        outcome['host_dispatch_seconds'] = time.perf_counter() - started
        (batch.output / 'result.json').write_bytes(canonical(outcome))
        return outcome
    except Exception as exc:
        (batch.output / 'ambiguous.json').write_bytes(canonical(dict(nonce=batch.nonce, reason=repr(exc), retry_allowed=False)))
        if isinstance(exc, AmbiguousOutcome):
            raise
        raise AmbiguousOutcome('dispatch_outcome_unknown_no_retry:' + repr(exc)) from exc

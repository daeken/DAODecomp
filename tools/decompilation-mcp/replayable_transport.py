"""Read-only quiescence witness for one pinned synchronous compiler dispatch.

This bounded protocol never recovers a match or claims the compiler did not run.
It permits nonaccepting abandonment only when late execution cannot reach the
compiler: the exact copy input and destination are absent, and no launcher lives.
"""
import base64
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def quote(value):
    return "'" + value.replace("'", "''") + "'"


def rendered_scripts(profile, name, flags):
    guest = profile['guest_root'] + '\\' + name
    shared = profile['guest_transfer_root'] + '\\' + name
    vcvars = profile['vcvars']
    batch = ('@echo off\r\ncall "' + vcvars + '"\r\nif errorlevel 1 exit /b %errorlevel%\r\ncl\r\nwhere cl\r\n'
             'cl /nologo ' + ' '.join(flags) + ' /FAs /Facandidate.asm /Focandidate.obj candidate.cpp\r\nexit /b %errorlevel%\r\n')
    script = f'''$guest={quote(guest)}
Copy-Item -Recurse -Force {quote(shared)} $guest
Set-Location $guest
$p=Join-Path (Split-Path {quote(vcvars)}) 'bin\\cl.exe'
$i=Get-Item $p
[PSCustomObject]@{{path=$p;sha256=(Get-FileHash -Algorithm SHA256 $p).Hash.ToLower();file_version=$i.VersionInfo.FileVersion}} | ConvertTo-Json | Set-Content -Encoding UTF8 compiler.json
& cmd.exe /d /c 'build.cmd > build.log 2>&1'
$buildExit=$LASTEXITCODE
$buildExit | Set-Content -Encoding ASCII build-exit.txt
Copy-Item -Force ($guest+'\\*') {quote(shared)}
exit $buildExit
'''
    return guest, shared, batch.encode('ascii'), script.encode()


def validate_probe(data):
    require(data.get('guest_base_exists') is True and data.get('share_base_exists') is True,
            'transport_bases_unavailable')
    require(data.get('workspace_exists') is False and data.get('source_transfer_exists') is False,
            'dispatch_prefix_or_workspace_present_recovery_unsupported')
    processes = data.get('processes')
    require(isinstance(processes, list) and len(processes) == 1, 'compiler_or_launcher_active_or_probe_missing')
    probe = processes[0]
    require(probe.get('name', '').lower() == 'powershell.exe' and
            type(probe.get('pid')) is int and type(data.get('diagnostic_pid')) is int and probe['pid'] == data.get('diagnostic_pid') and
            probe.get('has_command_line') is True and probe.get('has_executable') is True,
            'unidentified_compiler_or_launcher')


@contextmanager
def vm_lock(path):
    # The supported Parallels host is POSIX. Portable tests exercise the pure guards.
    import fcntl
    with Path(path).open('r+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def witness(request, folder):
    folder = Path(folder)
    profile = json.loads(Path(request['transport_config']).read_text())
    require(request['inputs'].get(request['transport_config']) == sha(request['transport_config']), 'transport_profile_unbound')
    require(profile.get('protocol') == 'prlctl-sync-copy-v1', 'unsupported_transport_protocol')
    require(Path(profile['executable']).is_absolute() and request['inputs'].get(profile['executable']) == sha(profile['executable']), 'transport_executable_unbound')
    old = request['target_request']
    build = request['target_result']['build']
    require(build['vm'] == profile['vm_name'], 'transport_vm_changed')
    require(old['inputs'].get(profile['build_helper']) == profile['build_helper_sha256'] == sha(profile['build_helper']),
            'unattested_build_helper')
    require(old['inputs'].get(profile['vm_helper']) == profile['vm_helper_sha256'] == sha(profile['vm_helper']), 'unattested_synchronous_vm_wrapper')
    name = build['vm_workspace'].rsplit('\\', 1)[-1]
    require(re.fullmatch(r'coff-job-[0-9a-f]{32}', name) is not None, 'unsupported_workspace_identity')
    guest, shared, batch, script = rendered_scripts(profile, name, old['project']['compiler_flags'])
    require(build['vm_workspace'] == guest, 'workspace_outside_registered_transport')
    target = Path(request['target_folder'])
    require((target / 'build/build.cmd').read_bytes() == batch and
            (target / 'build/run.ps1').read_bytes() == script, 'unrecognized_synchronous_launch_script')
    require(sha(target / 'candidate.cpp') == build['source_sha256'], 'unknown_source_changed')
    expected = old.get('expected_source_sha256')
    require(expected is None or expected == build['source_sha256'], 'submitted_source_binding_changed')
    host_base = Path(profile['host_transfer_root'])
    require(host_base.is_absolute() and host_base.is_dir() and
            not any(p.is_symlink() for p in [host_base, *host_base.parents]), 'unsupported_host_transfer_root')
    transfer = host_base / name
    probe_script = f'''$guest={quote(guest)}
$shared={quote(shared)}
$shareBase={quote(profile['guest_transfer_root'])}
$guestBase={quote(profile['guest_root'])}
$names=@('cl.exe','c1xx.exe','c2.exe','link.exe','cmd.exe','powershell.exe')
$processes=@(Get-CimInstance Win32_Process | Where-Object {{$names -contains $_.Name}} | ForEach-Object {{[PSCustomObject]@{{name=$_.Name;pid=$_.ProcessId;parent_pid=$_.ParentProcessId;has_command_line=($null -ne $_.CommandLine);has_executable=($null -ne $_.ExecutablePath)}}}})
[PSCustomObject]@{{guest_base_exists=(Test-Path -LiteralPath $guestBase);share_base_exists=(Test-Path -LiteralPath $shareBase);workspace_exists=(Test-Path -LiteralPath $guest);source_transfer_exists=(Test-Path -LiteralPath $shared);diagnostic_pid=$PID;processes=$processes}} | ConvertTo-Json -Depth 5
'''
    encoded = ("$ErrorActionPreference='Stop'; $ProgressPreference='SilentlyContinue'; [Console]::OutputEncoding=[System.Text.Encoding]::UTF8\n" + probe_script).encode('utf-16-le')
    with vm_lock(old['project']['replayable']['vm_build_lock']):
        for path, digest in request['inputs'].items():
            require(sha(path) == digest, 'reconciliation_input_changed')
        base_identity = (host_base.stat().st_dev, host_base.stat().st_ino)
        require(not transfer.exists() and not transfer.is_symlink(), 'host_dispatch_input_present')
        require(not any((target / 'build' / n).exists() for n in ('build-exit.txt', 'candidate.obj', 'compiler.json')),
                'retained_artifacts_present_recovery_unsupported')
        run = subprocess.run([profile['executable'], 'exec', profile['vm_name'], '--current-user', 'powershell.exe',
                              '-NoProfile', '-EncodedCommand', base64.b64encode(encoded).decode()],
                             capture_output=True, timeout=60)
        (folder / 'probe.stdout').write_bytes(run.stdout)
        (folder / 'probe.stderr').write_bytes(run.stderr)
        require(run.returncode == 0 and len(run.stdout) <= 64000, 'read_only_probe_failed')
        data = json.loads(run.stdout.decode('utf-8-sig'))
        validate_probe(data)
        require(host_base.is_dir() and not any(p.is_symlink() for p in [host_base, *host_base.parents]) and
                (host_base.stat().st_dev, host_base.stat().st_ino) == base_identity, 'host_transfer_root_changed')
        require(not transfer.exists() and not transfer.is_symlink(), 'dispatch_input_reappeared')
        for path, digest in request['inputs'].items():
            require(sha(path) == digest, 'reconciliation_input_changed_during_probe')
        return dict(status='quiescent_absent_synchronous_prefix', probe=data,
                    original_compiler_outcome='unknown', probe_invokes_compiler=False, match=False,
                    scope='nonaccepting abandonment under registered isolated host and shared-lock protocol')


def main():
    data = json.load(sys.stdin)
    folder = Path(data['folder'])
    folder.mkdir(parents=True, exist_ok=True)
    try:
        result = witness(data['request'], folder)
    except (ValueError, OSError, KeyError, TypeError, subprocess.TimeoutExpired, ImportError) as exc:
        result = dict(status='inconclusive', blocker=type(exc).__name__ + ':' + str(exc),
                      original_compiler_outcome='unknown', probe_invokes_compiler=False, match=False)
    print(json.dumps(result))


if __name__ == '__main__':
    main()

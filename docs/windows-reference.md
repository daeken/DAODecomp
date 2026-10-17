# Windows reference handoff

## Observed Parallels guest

The available VM is **Windows 11 Pro**, version `10.0.26300`, build `26300`,
reported by `Win32_OperatingSystem`. Its OS architecture is ARM 64-bit. The
processor reports `Apple Silicon`, architecture code `12`, address/data width 64.
The generic `Get-ComputerInfo` values still say Windows 10 Pro/version 2009;
use the `Win32_OperatingSystem` result above as the OS identity.

Access from the host is through `/usr/local/bin/prlctl`, VM name `Windows 11`:

```sh
/usr/local/bin/prlctl list -a
/usr/local/bin/prlctl exec 'Windows 11' --current-user powershell.exe -NoProfile -Command 'Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,BuildNumber,OSArchitecture'
```

This is an ARM64 Windows guest. The smoke run below used x64 Python and x64
candidate executables under Windows ARM64 translation. PE headers identify those
executables as `0x8664` (AMD64); the selected compiler executable is `0xaa64`
(ARM64), targeting x64. Python's `platform.machine()` reports ARM64 here and does
not establish the Python process architecture by itself.

The original game has not been launched in this VM. Do not label these results
as native x86 Windows evidence or original-game validation.

## Reference build identity

The host's existing `gamedata/bin_ship/DAOrigins.exe` SHA-256 was checked without
copying the game install into the VM:

```text
2346caee611002d4dff6ecef68eb315b63a37004dd98b39c11a9c26c0b45bfb3
```

This matches the pinned build. The executable and assets remain in ignored local
game data; no game files were added to the VM clone.

## Isolated workspace and installed toolchain

The VM clone is `C:\Users\daeken\DAODecompWindows`, obtained from the public
repository over HTTPS. The completed smoke run on **2026-10-17** used revision
`14be457c918da7ddcd39be9080dbb3364215312d`, with a clean Git working tree.
It does not test the shared Mac working tree's uncommitted recovery changes.

Installed tools used or retained in the guest:

- Git for Windows `2.55.0.windows.5`, ARM64.
- CMake `4.4.4`, ARM64 portable distribution under
  `C:\Users\daeken\tools\cmake\cmake-4.4.4-windows-arm64`.
- Visual Studio 2022 Build Tools, installed at `C:\BuildTools`. The official
  bootstrapper reported successful completion, exit code 0.
- Selected C++ compiler: MSVC `19.44.35229.0`, at
  `C:\BuildTools\VC\Tools\MSVC\14.44.35207\bin\Hostarm64\x64\cl.exe`.
- Selected Windows SDK `10.0.26100.0`, targeting guest OS `10.0.26300`.
- Python `3.12.10`, x64, at `C:\Users\daeken\tools\Python312x64`;
  test environment `C:\Users\daeken\DAODecompWindows\.venv-x64`.
- Pinned `unicorn==2.1.4`, installed from its Windows AMD64 wheel.

ARM64 Python `3.12.10` and the earlier `.venv` remain available. The attempted
Unicorn install there selected a source distribution and failed before the
compiler was installed. The successful run used `.venv-x64`; it did not change
pinned requirements. `.venv-x64` is excluded locally through `.git/info/exclude`.

## Completed baseline smoke results

| Check | Observed result |
| --- | --- |
| CMake configure, Visual Studio 17 2022 generator, x64 | Exit 0 |
| C++ build, RelWithDebInfo | Exit 0 |
| CTest | 2/2 passed: `guest_memory` and `tooling` |
| Python suite inside CTest | 120 tests; OK, 2 skipped |
| Positive synthetic demo | 59 `corpus_pass`; exit 0 |
| Intentional-mismatch synthetic demo | 53 `corpus_pass`, 6 `mismatch`; exit 0 |

The two Python skips require the ignored original binary or saved private
characterization, which are absent in this isolated clone. The synthetic reports
record unchanged artifacts. Both demo commands use 59 deterministic cases with
two executions per side in fresh processes.

These checks compare synthetic x86 instructions in Unicorn with separately
compiled C++ and exercise the tooling. They do not execute original game code,
validate recovered functions against the game, or establish whole-game behavior.
No native original-game validation was added.

## Reproduce the successful run

From the guest clone root, use the explicit x64 environment. The process PATH
must contain the venv, Git and CMake. Exclude WindowsApps from this test process's
PATH: its `python3` Microsoft Store alias otherwise intercepts the Git pre-commit
hook and reports that Python is unavailable. This was the cause of the earlier
single unit-test failure; the hook and tests were not modified.

```powershell
Set-Location C:\Users\daeken\DAODecompWindows
$env:PATH='C:\Users\daeken\DAODecompWindows\.venv-x64\Scripts;C:\Program Files\Git\cmd;C:\Users\daeken\tools\cmake\cmake-4.4.4-windows-arm64\bin;'+ (($env:PATH -split ';' | Where-Object {$_ -notmatch 'WindowsApps'}) -join ';')
python -m pip install -r requirements-validation.txt
cmake -S . -B build-windows-x64 -G "Visual Studio 17 2022" -A x64 -DPython3_EXECUTABLE=C:/Users/daeken/DAODecompWindows/.venv-x64/Scripts/python.exe
cmake --build build-windows-x64 --config RelWithDebInfo --parallel 2
ctest --test-dir build-windows-x64 -C RelWithDebInfo --output-on-failure
python examples/synthetic/demo.py --build-dir build-windows-x64/RelWithDebInfo
python examples/synthetic/demo.py --build-dir build-windows-x64/RelWithDebInfo --expect-mismatch
```

The build type is selected by `--config` for this multi-configuration generator.
The local automation judges native commands by their exit codes, since Windows
PowerShell can promote ordinary stderr warnings into its own errors.

## Durable records and next boundary

Ignored host `local/windows-reference/` and guest clone
`local\windows-reference\` retain the session record, reusable smoke script,
configure/build/CTest/demo logs, detailed unit-test output, synthetic reports,
and JSON provenance. Provenance binds the clean commit, OS, Python, compiler and
built executable SHA-256/PE machine identities. Some PowerShell-generated logs
are UTF-16. Reports retain the exact compared-artifact hashes.

The automation finished with `status.txt` equal to `complete`; every step in
`steps.txt` has exit 0. No background smoke task remains pending. The earlier
installer and wrapper failures remain described in the ignored session record.

Original-game work still needs an invocation/capture adapter and initialized
state, plus measurement of the original x86 process's translation path. Windows
ARM64 observations must retain their translation caveat and need corroboration
before being treated as authoritative native x86 reference evidence.

## Original scalar execution proposal

A separate isolated Win32 bridge subsequently executed the ten established
call-free original scalar functions on this Windows ARM64 VM. All 3,516 frozen
cases agreed with unchanged Unicorn observations and accepted C++ results, with
two fresh original and candidate processes per case. Eight rejection/hash/budget
controls and four actual behavioral mutations behaved as expected. An independent
Sol medium review approved the bounded private proposal and its retained results.

This is translated Windows x86 execution, not native x86 hardware evidence.
The full game was not launched. The bridge still needs integration with the
project runner protocol and validation of that integrated path; recovery registry
and native-evidence counts are unchanged. See the
[record and artifact hashes](../analysis/windows-translated-scalars-001.json) and
[independent review](../analysis/reviews/windows-translated-scalars-001.json).
Private sources and observations remain under `local/windows-native-proposal/`.

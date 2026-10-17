# Windows reference handoff

The user is starting a Windows VM. Access, OS/CPU architecture and toolchain are
not established yet; no native original-game validation has run.

First record the VM's access method, Windows version, host/guest CPU architecture
and whether x86 code runs natively or through translation. Clone the repository
and copy the user's original install into ignored `gamedata/`. Verify in PowerShell:

```powershell
Get-FileHash gamedata/bin_ship/DAOrigins.exe -Algorithm SHA256
```

Expected SHA-256:
`2346caee611002d4dff6ecef68eb315b63a37004dd98b39c11a9c26c0b45bfb3`.
Keep binaries, assets and captures out of Git.

With Python, CMake and MSVC C++ tools installed, the existing infrastructure smoke
test is the Windows sequence in README. Its synthetic x86 reference still uses
Unicorn. A passing smoke test is not native original-game evidence. The full
checkpoint currently refuses Windows because the game validators need separate
multi-configuration executable and CMake-cache paths.

The first native reference adapter should target the already recovered call-free
functions and replay their existing frozen corpora. It needs a 32-bit process,
hash-checked original slices and any relocations, explicit guest memory placement,
x86 calling-convention/register/stack capture and fresh state per repetition.
Return values, all observed memory and ABI checks must match the current protocol.
Use the same negative controls; record OS, CPU/translation, compiler and runner
identity separately from emulator evidence. No native result can be claimed until
that adapter exists and actually runs. A full game loader and Windows event/lifetime
semantics remain separate work.

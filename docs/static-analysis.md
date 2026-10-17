# Repeatable static analysis

The local tool cache uses official Ghidra **12.1.4**, release
`Ghidra_12.1.4_build`, revision `8b6bbb857accdfa20dc5b2f5dea471178c2e9fbc`.
Download asset: `ghidra_12.1.4_PUBLIC_20260921.zip`, SHA-256
`ddac49f903da9d5bac833e5cc79395098b9c33cfd3279be5f31bd00387d2d4db`.
The download was checked against the GitHub release API's published digest.
Tool files, extracted binaries, analysis project and full exports stay in `local/`.

On this Apple Silicon host, the native decompiler and helpers were built with the
release's Gradle wrapper in `support/gradle` using `./gradlew buildNatives`.
Java 26 and the installed Xcode compiler were used. Ghidra's documented minimum
for this release is Java 21. Preserve executable permissions when extracting the
distribution. This setup does not require or start the Windows game.

First import, from the repository root:

```sh
mkdir -p local/ghidra local/analysis
local/tools/ghidra_12.1.4_PUBLIC/support/analyzeHeadless \
  local/ghidra DAOOrigins \
  -import gamedata/bin_ship/DAOrigins.exe \
  -scriptPath tools/ghidra \
  -postScript ExportInventory.java "$PWD/local/analysis" \
  -analysisTimeoutPerFile 1200 -max-cpu 4
```

Use a fresh project name for a fresh import. To re-export an existing analyzed
project, replace `-import ...` with `-process DAOrigins.exe -noanalysis`.
The project uses the PE loader's selected x86 Windows language/compiler and default
analysis options from the pinned release. The export records their identities.
External DLLs are not imported automatically in this run; imports are unresolved
boundaries. No PDB was available. Warnings and analysis errors remain in the local
log and must be considered before relying on any inferred function.

The tracked `ExportInventory.java` script writes `functions.json` with inferred
function starts, body ranges, signatures, thunk status and direct incoming
callsites. It also exports disassembly and decompiler hypotheses for the two
initial recovered functions. These are analysis outputs, not an authoritative
function count or complete call graph: indirect calls, tail calls, shared chunks,
embedded data and missed functions require further work.

Independent instruction disassembly was also generated with LLVM 21.1.6; Capstone
5.0.6 and pefile 2024.8.26 were used to cross-check the selected slices and their
relocation footprints. They are analysis aids, not runtime dependencies of the
validation runner.

The completed run took 190 seconds for automatic analysis and exported 27,555
function hypotheses (367 thunks; 26,388 names still start with `FUN_`). Ghidra
reported malformed resource-key and embedded-PNG data, and one decompilation read
warning at VA `0x869200`. The security-directory warning concerns file-only data.
Both selected leaves decompiled successfully with body ranges and direct callsites
matching the independent disassembly. The resource warnings and unrelated function
warning remain unresolved; analysis success does not certify every output.

Sources: [official Ghidra release](https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.4_build),
[headless analysis documentation](https://github.com/NationalSecurityAgency/ghidra/blob/Ghidra_12.1.4_build/Ghidra/RuntimeScripts/support/analyzeHeadlessREADME.md).

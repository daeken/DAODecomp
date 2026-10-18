# Native C++ compiler and reccmp loop

`rapid_native` takes an annotated C++ source file, compiles an x86 DLL and PDB,
and compares the resulting functions with the pinned original using reccmp.
The source is the only authored per-function artifact. Build files, original
sizes, source mappings, provenance and reports are generated automatically from
the source annotations and existing byte-backed inventory. There are no authored
function contracts, fixtures, corpora, native adapters or successful call stubs.
The original executable is read for analysis and is never launched by this tool.

The selected historical compiler is Microsoft C/C++ 14.00.50727.762 for x86 and
linker 8.00.50727.762, from the official Windows SDK 6.0 / VS2005 SP1 toolchain.
The original PE's linker version is 8.0, but its exact original compiler and patch
remain unknown. Using this compiler is a hypothesis to test against observed
output, not an identification of the original compiler patch.

The bounded pilot uses four actual call-free integer function ranges. DeepSeek
receives original instruction bytes and disassembly, and emits C++98 with real
native calling conventions and inline `// FUNCTION: DAO 0xORIGINAL_VA` comments.
The provider uses the existing daily ledger, credentials and transport. Every
request reserves a slot in the same persistent 12-per-1800-second-cycle global
ledger. This pilot allows two attempts total, including a possible repair. Paid,
partial and interrupted outcomes are retained; there are no automatic retries.

Run from this worktree, with its dependencies available:

```sh
/Users/daeken/projects/DAODecomp/.venv/bin/python -m rapid_native propose \
  --root local/reccmp-pilot/native \
  --rva 0x220910 --rva 0x35bca0 --rva 0x47a080 --rva 0x480630

/Users/daeken/projects/DAODecomp/.venv/bin/python -m rapid_native compare \
  --source local/reccmp-pilot/native/attempt-1/candidate.cpp \
  --output local/reccmp-pilot/native/attempt-1/build-o2 \
  --vcvars 'C:\Users\daeken\tools\VC8-SP1\vcvars.cmd'
```

Output directories are new exclusive claims. They are never overwritten. A
provider repair can use `--feedback FILE` with the concrete retained compiler
and reccmp differences, and consumes the second request. Compilation or transport
repairs to the common tooling do not require regenerating paid source.

The Windows workspace is isolated under `C:\Users\daeken\DAOReccmpPilot` with
its own Python environment. Public tooling and candidate artifacts temporarily
transfer through `Downloads/DAOReccmpPilotTransfer`; each job transfer is removed
after use. The original comes from its preexisting ignored guest copy and is
SHA-256 checked before each build. The VM is Windows 11 ARM64: the VC8 x86 tools
run under Windows translation. No guest baseline installation or game execution
is performed. Compiler executable hashes and banners are retained with each run.

The compile flags are `/O2 /Ob1 /Oy /Zi /Zl /GS- /GR- /EHsc`; linking uses
`/DLL /NOENTRY /DEBUG /OPT:NOREF /OPT:NOICF /NODEFAULTLIB /MACHINE:X86`.
No fake game entrypoint, unknown dependency or imported successful stub is added.
The reccmp checkout is pinned at `435b00e6ba65f76aee2dd793fcc7d0f5139de749`.

The comparison reads the entire original function range from the pinned inventory.
An automatic `address|type|size` CSV supplies that explicit original size to
reccmp, whose default could otherwise use the candidate PDB size and compare only
a prefix. The common audit requires the reported original size to equal the full
inventory size, verifies the actual original byte hash, checks that every decoded
instruction appears in the comparison, and requires a nonempty PDB mapping.
Missing output, partial decoding, skipped instructions, unknown placeholders,
external/indirect branch targets, calls, and non-stack references stay unmatched
in this initial deliberately small native profile. Inventory boundaries retain
their static-hypothesis provenance.

Automatic `reccmp_matched` status requires the unrounded normalized-text score to
be exactly `1.0`, a complete comparison, and no unknowns or stubs. Reccmp's
register-swap effective-match heuristic never upgrades a lower score. All other
candidates remain `retained_unmatched`. This is reccmp match evidence for the
pinned compiled artifact, not a universal proof of C++ semantics, portability,
or whole-game behavior. These counts are separate from the older recovery registry.

Each build retains `candidate.cpp`, DLL, PDB, compiler/linker log and identities,
`reccmp.json`, verbose `diff-VA.txt` files, `summary.json`, and a hash-bound run
receipt. `summary.json` contains requested, matched and retained-unmatched counts,
raw scores, compared sizes, mappings, boundary provenance and unknown reasons.

Common tooling controls, with no per-game-function test files:

```sh
/Users/daeken/projects/DAODecomp/.venv/bin/python -m unittest discover -s rapid_native/tests -v
/Users/daeken/projects/DAODecomp/.venv/bin/python -m unittest discover -s tests -v
```

The generic classification controls reject near-100% rounded scores, absent
scores, booleans masquerading as scores, prefix sizes, empty functions, missing
mappings, unresolved targets and stubs.

## Measured bounded pilot, 2026-10-18

The first paid proposal compiled successfully and produced three full raw-score
matches out of four. The fourth was a complete 50% comparison: its two return
blocks appeared in the opposite order. One DeepSeek repair, given that actual
diff, inverted the C++ source condition and preserved the other three definitions.
The second actual VC8 build produced four full `1.0` matches with no unknowns and
no effective-register heuristic upgrades. The full original sizes were 43, 13,
29 and 53 bytes; the corresponding PDB functions had those same complete sizes.

| RVA | First score | After one repair | Status |
| --- | ---: | ---: | --- |
| `00220910` | 1.0 | 1.0 | `reccmp_matched` |
| `0035bca0` | 1.0 | 1.0 | `reccmp_matched` |
| `0047a080` | 0.5 | 1.0 | `reccmp_matched` |
| `00480630` | 1.0 | 1.0 | `reccmp_matched` |

The two provider calls took 24.908 and 7.998 seconds and cost an estimated
$0.0079338 and $0.00297852, totaling **$0.01091232**. Actual successful build and
compare phases took 7.812 and 2.813 seconds. Earlier common-tooling failures
(PowerShell native-stderr handling and a long Parallels command) were retained;
they required no additional provider requests. The final compiler and reccmp
ran in the stated Windows ARM64 VM; host tooling tests ran on macOS ARM64 with
Python 3.14.7. The existing 228 tooling tests passed with seven skips, and the two
new generic classification tests passed, including the false-match mutations.

Private reproducibility evidence remains under
`local/reccmp-pilot/native/attempt-{1,2}/`, including both paid proposals and the
original nonmatch. `local/reccmp-pilot/native/pilot-receipt.json` aggregates actual
costs, durations and final hashes. The final source SHA-256 is
`e92bfbee68383b9a56beea5a7f55af295197c28b4452060b455ec676623365dc`;
the final x86 DLL SHA-256 is
`67518be66770df1a2f1c9869b490ed593715dfd50ca794f0e51b81409a6930ea`.
This pilot did not start a continuous native queue or resume the previous Context
candidate queue. Its four reccmp matches remain separate from the older registry.

## Continuous native profile

The native loop is attached to the existing `rapid.store.Store` queue and shared
budget accounting. It uses its own ignored `local/rapid-native/` queue and keeps
the previous Context queue paused. Four paid pilot matches are seeded by their
existing source/binary hashes; they are not regenerated or charged again.

```sh
/Users/daeken/projects/DAODecomp/.venv/bin/python -m rapid_native prepare
/Users/daeken/projects/DAODecomp/.venv/bin/python -m rapid_native run
/Users/daeken/projects/DAODecomp/.venv/bin/python -m rapid_native status
/Users/daeken/projects/DAODecomp/.venv/bin/python -m rapid_native pause
/Users/daeken/projects/DAODecomp/.venv/bin/python -m rapid_native pause --resume
```

Preparation leaves the queue paused. `run` acquires its single-owner lock and
resumes it. `pause` stops new provider dispatch, including repairs, while existing
provider/build work finishes and saves. SIGTERM/SIGINT also request a graceful
pause. The initial supported profile selected **87 further functions in eight
batches of 6–16 functions**. Startup breadth and shared callers establish priority;
independent supported functions fill compact groups. Each packet is limited to
30,000 bytes and 160 decoded instructions. Unsupported calls, external/indirect
branches, non-stack/segmented references, potential unmapped address constants,
large bodies, incomplete decoding and overlapping/noncontiguous boundaries are
explicitly excluded in `preparation.json`. This first profile covers a limited
subset; it does not silently invent support for the excluded functions.

There are at most two provider processes and one VM build/compare phase at a time.
Each batch gets an initial proposal and at most one repair using actual compiler
or complete reccmp diffs. Every request reserves the same persisted global slot
and daily budget before dispatch. Exhausted cycles or daily budgets wait without
model calls. A repair waiting for budget retains the initial source and scores.
A mechanical VM transport failure may retry compilation once using the same paid
source; it never triggers an extra provider request. Malformed/partial provider
responses and uncertain interrupted requests are retained without automatic replay.

The coordinator records the best source and compiled comparison for every requested
RVA in its separate `native_functions` table. An already matched function keeps
its matched source even if a later repair is worse. Missing/wrong output identities
or changed source/DLL/PDB bindings cannot enter that index. The historical recovery
registry is untouched. The compact `status.json` reports `reccmp_matched`, retained
nonmatches, request/cost/latency totals and active jobs; native
queue costs exclude the separately retained paid pilot costs. Exhausting the
supported queue leaves the daemon idle; expanding support requires an explicit
profile change, rather than fabricated dependency behavior.

The launch receipt is `local/reccmp-pilot/native-continuous-launch.json`. Queue
attachment tests use only standard-library synthetic metadata and fake results;
no game installation, compiler, VM, API credentials or additional Python packages
are needed to run `rapid_native/tests` in CI. They cover pause, deduplication,
claims, budget rollover, unknown-interruption reconciliation, retained output,
best-source preservation and rejection of wrong output identities.

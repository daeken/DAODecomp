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

The current native loop uses the existing `rapid.store.Store`, the same physical
request database/anchor/history, and the unchanged $50/calendar-day Chicago
provider ledger. The old Context queue and legacy pipeline stay paused. Native
outputs and the separate matched index remain under ignored `local/rapid-native/`.

```sh
/Users/daeken/projects/DAODecomp/.venv/bin/python -m rapid_native prepare
/Users/daeken/projects/DAODecomp/.venv/bin/python -m rapid_native continue-retained --receipt local/reccmp-scale-001/retained-continuation.json
/Users/daeken/projects/DAODecomp/.venv/bin/python -m rapid_native run --lanes 4 --request-ceiling 120 --max-repairs 6
/Users/daeken/projects/DAODecomp/.venv/bin/python -m rapid_native status
/Users/daeken/projects/DAODecomp/.venv/bin/python -m rapid_native pause
/Users/daeken/projects/DAODecomp/.venv/bin/python -m rapid_native pause --resume
```

The production defaults are **four provider lanes**, **120 total requests per
persisted 1800-second cycle**, **one serialized VM build lane**, and **up to six
repairs after an initial request**. Limits are configurable on `run` and recorded
in `runtime-config.json`, status and launch receipts. Older callers of the shared
request reservation helper keep their default ceiling of twelve; every caller
still contributes to the same persisted cycle count. Exhausted request cycles or
daily budgets wait without model calls. No ledger, cycle anchor or paid request
is reset. Preparation leaves the queue paused; `run` resumes it under a single
owner lock. Pause and SIGTERM/SIGINT stop new dispatch while existing work saves.

The expanded call-free pointer-memory profile admits observed register-relative
and indexed object fields, arrays, buffer loops and integer loads/stores. It
supports function bodies up to 2048 bytes/512 instructions, grouping up to sixteen
functions with 50,000 packet bytes and normally 320 instructions (one larger
function can occupy a packet). Startup breadth and shared callers establish
priority; independent supported functions fill groups. Calls, external/indirect
branches, absolute/indexed-global addresses, potential mapped address constants,
segmented/TLS accesses, unsupported instructions, incomplete decoding, overlaps
and noncontiguous boundaries remain explicit exclusions in `preparation.json`.
Small inferred C++98 classes with out-of-line native `__thiscall` definitions are
allowed inside the single C++ output; no dependency stubs or per-function fixtures
are introduced.

Reccmp normalization is supplemented by a reusable typed-instruction comparison.
For a match, every raw decoded instruction must also agree on mnemonic, prefixes,
address size, and each operand's width, register, memory segment/base/index/scale/
displacement, or immediate value. Internal branch targets are compared by decoded
instruction identity rather than absolute image address. Unknown targets stay
unmatched. Thus a normalized name substitution cannot conceal a field offset,
access width, index scale or base-register difference. Full original range and
instruction coverage, pinned source/DLL/PDB mappings, exact raw score `1.0`, and
all previous unknown/stub exclusions are still required. Effective-register
heuristics never upgrade a lower score. Summaries retain operand mismatches and
the guard's source hash with the actual reccmp module identities.

Repair requests contain only the still-unmatched functions. Matched definitions
are never regenerated. Each remaining function receives its best retained C++
source with the corresponding actual comparison; latest compiler diagnostics are
also supplied. Every request gets a new numeric attempt directory and budget
reservation. Attempts three through seven are handled explicitly, all sources and
failure histories are retained, and an already matched source survives a worse
later attempt. All-matched batches stop immediately; three consecutive repairs
without improvement stop a stagnant batch before its seven-request ceiling.
Fresh work receives two dispatch preferences for each repair preference, so long
repair loops cannot starve new functions. A mechanical VM transport failure may
retry compilation once with the same paid source, never a new provider request.
Interrupted or ambiguous paid requests are not replayed.

The explicit `continue-retained` action records the prior result hashes and paid
attempt numbers before requeueing known nonmatches under the larger allowance.
It does not reset attempt counts or reuse consumed requests. This scaling run
continued the existing **33 nonmatches in eight batches** from their already paid
sources. Four original pilot matches remain seeded without regeneration.

Measured expansion on 2026-10-18 selected **1,259 new functions in 98 batches**,
including **1,258 pointer-memory functions**, beyond the earlier 87-function
profile. Its same-queue smoke used sixteen compact object/field helpers with
ninety original instructions: **thirteen passed the full typed-operand/reccmp
match checks**, while three remained available for bounded repair. This raised
the separate native matched count from 58 to 71 before four-lane production.
Reccmp match evidence applies to pinned compiled artifacts and the recorded
static boundary hypotheses; it is not a universal C++ or whole-game proof.

Scaling evidence, continuation action, smoke and production launch receipts are
under `local/reccmp-scale-001/`. The compact `local/rapid-native/status.json`
reports limits, matched and retained counts, source proposals, cost/reservations,
tokens, latency and active jobs. Queue costs exclude the separately retained paid
pilot costs. The original registry and its historical evidence stay separate.

Common tests require no game, VM or compiler. Pure descriptor controls cover
memory widths, registers, index scales, displacements, segments and prefixes;
optional actual-decoder controls run when Capstone is installed. Queue controls
cover attempt three, the six-repair ceiling, plateaus, source preservation,
fresh/repair fairness, pause/reconciliation and both shared request ceilings.

The host's native runtime/decoder dependencies are pinned in
`requirements-native.txt` (Capstone 5.0.6 and pefile 2024.8.26). Linux/macOS CI
installs those pins so the actual decoded-memory mutation controls run as well
as the standard-library descriptor controls. The Windows reccmp environment and
historical compiler remain their separately pinned existing setup.

Native provider responses now require only a JSON `source` string, with optional
string-array `uncertainties`. Exact requested identities and duplicates are
checked from the C++ `FUNCTION: DAO` annotations. Redundant ancillary function
notes are ignored, including notes in older retained responses; they cannot
reject otherwise correctly identified C++ source. Source/envelope size and type
checks, strict JSON parsing and every compiler/PDB/range/operand/score check stay
in place. A measured retained-response recovery corrected one such metadata-only
rejection without a provider request: its original fifteen-function source
compiled with twelve full matches and three actual code nonmatches. Historical
provider failure/usage records and two genuinely truncated error responses were
preserved. Derived provenance is recorded in
`local/reccmp-scale-001/parser-recovery.json`.

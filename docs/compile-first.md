# Compile first, then improve matching

The current priority is to turn the free Ghidra drafts into compilable native C++
using deterministic transformations. Complete matches remain an automatic
acceptance path, but this pass does not pay for model repairs or chase differences
in otherwise compilable functions. C++ remains the only authored per-function
artifact; metadata and reports are generated.

## What is failing

The errors are a mixture of Ghidra pseudocode conventions, declaration/type
hypotheses and defects in our initial source conversion. They are not all missing
decompiler intrinsics.

In the first 6,000 measured identities, a receiver-parameter parsing bug accounted
for 215 undeclared-parameter and 71 syntax errors as the first compiler error.
The parser mishandled forms such as `int *param_1` and could consume text past the
parameter's comma. Another 147 drafts were rejected during conversion because
their receiver declaration was not recognized. These are conversion defects that
can be repaired without reconstructing the function's behavior again.

Other failures involve pointer/integer or pointer/pointer conversions that need
explicit spelling in C++. Those require the target width and expression types;
adding casts indiscriminately is not a valid repair strategy. Missing Windows API
declarations, unresolved type names, special decompiler operators and genuinely
unmodeled register/stack inputs form separate categories.

## Transformation order

1. Use token-aware normalization for recognizable source spelling and parameter
   boundaries. Preserve comments, literals and the identity of every function and
   global.
2. Use Clang's target-aware AST and source ranges for transformations that depend
   on types or expression structure. The analysis target is Windows x86, even
   though the tool runs on the Mac. Only supported, explicitly checked cases are
   rewritten; a damaged or insufficient AST does not authorize an edit.
3. Compile the resulting source with the existing historical x86 compiler. Keep
   source, input identities, transformations, compiler output and comparison
   results bound together automatically.
4. Record compilation and matching separately. The existing comparator may find
   exact matches at no inference cost, but compilation alone is not equivalence.

Clang supplies analysis for rewriting; VC8 remains the compiler used for the
existing object comparisons. No additional paid provider is involved.

## Measured repair pilot, 2026-10-19

The targeted pilot selected 80 previous failures or conversion rejections:
30 receiver-declaration errors, 30 pointer-conversion errors, 10 other compiler
errors and 10 receiver-related conversion rejections, stratified by body size and
call count. It also included 20 previously compiling controls.

| Result | Count |
| --- | ---: |
| Previously failing/rejected cases now compiling | 54 / 80 |
| Previously compiling controls still compiling | 20 / 20 |
| Control comparison-status regressions | 0 / 20 |
| Complete object matches across the full pilot | 6 / 100 |
| DeepSeek requests during the pilot | 0 |

This is a targeted repair yield, not an estimate that 67.5% of all remaining
functions can be fixed by these rules. Compilation used VC8 SP1
14.00.50727.762 x86 under Windows 11 ARM64 translation. AST analysis used Apple
Clang 21.0.0 targeting `i686-pc-windows-msvc` with C++98 and MS compatibility
version 14. These objects were neither linked into a game nor executed.

Five attempts initially failed in the Parallels transport before compiler results
were available, including two controls. All five compiled when the exact retained
source was retried once. Both attempts remain recorded. Counting those failures
as source regressions would misdiagnose the repair. The final cached reconciliation
time is not the duration of the original compilation experiment.

The reusable implementation is
[`ghidra_compile_fix.py`](../rapid_object/ghidra_compile_fix.py), with
[synthetic regression tests](../rapid_object/tests/test_ghidra_compile_fix.py).
Receiver normalization preserves formal boundaries; typed assignment edits are
limited to supported 32-bit address/integer and same-width signedness-pointer
conversions. Types remain hypotheses, and compile success does not validate them.
Unsupported widths and unknown state remain explicit failures.

## Reproduce and resume

From the configured DAO worktree, after the baseline has written completed chunk
reports, use a new output directory for a separate pilot:

```sh
python -m rapid_object.ghidra_compile_fix prepare --root local/repro-compile-fix --baseline local/cost-reduction-001/full-seed
python -m rapid_object.ghidra_compile_fix pilot --root local/repro-compile-fix
```

The pilot writes its selection and per-case source/build/comparison records
automatically. It needs the baseline raw drafts and actual source/build reports,
the configured Windows compiler, and Clang on the analysis host. This implementation
uses POSIX file locking and is currently run on macOS. It is not a standalone
Windows rewriter or an automatic port to another architecture.

For the broader repair pass:

```sh
python -m rapid_object.ghidra_compile_fix prepare-sweep --root local/repro-compile-fix --baseline local/cost-reduction-001/full-seed
python -m rapid_object.ghidra_compile_fix sweep --root local/repro-compile-fix --resume --follow
```

Preparation leaves the sweep paused. `--resume` starts it; `--follow` discovers
later completed baseline chunks and exits after the baseline and eligible work
finish. Omit `--follow` for a finite snapshot. The VM build lock is shared with
the baseline. To stop after the current case:

```sh
python -m rapid_object.ghidra_compile_fix pause --root local/repro-compile-fix
```

The same sweep command resumes retained work after checking its bindings.
`sweep-status.json` records progress and unsupported outcomes. None of these
commands calls a model or publishes recovered-function credit. Keep old outputs
when rules change so the before/after comparison remains reproducible.

Clang's [LibTooling documentation](https://clang.llvm.org/docs/LibTooling.html) and
[AST matcher tutorial](https://clang.llvm.org/docs/LibASTMatchersTutorial.html)
describe richer tooling options. This pass currently consumes Clang's JSON AST;
it does not require a libclang Python package.

## Preserve the baseline

The first baseline and repair sweeps have completed. Their converter, sources and
reports remain retained as the baseline for later rounds. Repairs use additive
modules and separate output directories so a live pass and its source bindings
cannot change underneath it. Passes share the existing VM lock, preserve failed
attempts and do not modify the comparator or production acceptance counts.

Unmodeled incoming registers, stack state and unsupported helper semantics remain
unresolved. Unknown calls are not replaced by successful dummy functions. Declared
types and signatures remain hypotheses until supported by stronger evidence.

The first repair measurement and subsequent sweep receipts live under ignored
`local/deterministic-compile-001/`. See the [$200 plan](cost-target.md) for the
broader budget and the distinction between compiled functions and a runnable
replacement executable.

## Continuing improvement loop

Each round ranks remaining failure families, selects a shared transformation,
checks its explicit preconditions, and measures a stratified real-compiler pilot
with already-compiling controls. After generic tests and independent review,
apply the rule broadly, compare unique outcomes, and pick the next root cause.
Preserve prior observations and count source publication separately. Do not build
a new per-function validation workflow around this loop.

The first completed sweeps yielded 14,174 distinct compiling identities and 1,842
exact-match reports. See the [dated aggregate results](learning-log.md) for overlap
with the 920 starting published functions and remaining limitations. Artifact
verification and source export subsequently brought the public source tree to
2,209 matching functions. Compile success and source publication remain separate.

## Round 002: explicit FS memory access

The register/stack diagnostic family contains decompiler notation for explicit
machine operations as well as genuinely unresolved inputs. Of 9,369 state-blocked
drafts, 8,014 mention `unaff_FS_OFFSET`. Original-byte decoding and a syntax-use
audit admit 7,507 under the first bounded profile: absolute DWORD `FS:[0]` MOV
reads/writes used in x86 exception registration.

[`ghidra_state_fix.py`](../rapid_object/ghidra_state_fix.py) requires the pinned
binary, complete range hashes and decoding, matching static read/write counts,
exactly one supported pointer declaration, and no unresolved pseudo-base use or
other unknown state input. It emits real VC8 `__readfsdword`/`__writefsdword`
intrinsics and preserves signed load types. Alias widths must have an unambiguous
actual typedef after comments and literals are masked. Other offsets, widths,
operations and unknown state remain unsupported. This does not reconstruct the
rest of an exception frame or establish exception-unwinding correctness.

The stratified pilot measured 80 previously blocked functions and 20 compiling
controls: **58 new sources emitted, 16 newly compiling functions, zero new exact
matches**, and no compile or comparison-status regressions in the controls.
The remaining sources and failures are retained. The three exact pilot matches
belong to existing controls. Do not extrapolate the targeted 16/80 yield to the
whole inventory.

The pilot used VC8 SP1 14.00.50727.762 x86 under Windows 11 ARM64 translation,
Capstone 5.0.6 and the existing Clang-based repair pass. Its 100-case invocation
took 123.760 seconds, reusing a two-case smoke run that took 3.405 seconds; two
transport-only retries were retained. No provider requests or game execution
occurred. The focused controls, full tooling suite and independent review passed.

Reproduce with the configured original and compiler available:

```sh
python -m rapid_object.ghidra_state_fix census --root local/repro-fs-fix
python -m rapid_object.ghidra_state_fix pilot --root local/repro-fs-fix
python -m unittest discover -s rapid_object/tests -v
```

After reviewing a measured pilot, run the retained plan with:

```sh
python -m rapid_object.ghidra_state_fix sweep --root local/repro-fs-fix --resume
python -m rapid_object.ghidra_state_fix pause --root local/repro-fs-fix
```

The current execution subset contains 1,934 cases without a `stack0x` identifier
after masking comments/literals. All 7,507 cases remain in the full plan, with the
other 5,573 explicitly deferred for stack-frame work. This scheduling partition
changes no source or acceptance rule. The shared VM lock serializes compiler
access, and retained results are reused only after their bindings verify.

All 33 pilot failures involving `stack0x` use negative frame addresses in cookie
XOR expressions. None of those 33 is a positive incoming-argument offset or a
zero return-address offset. Numeric offsets alone cannot justify an arbitrary
C++ local address. The next round investigates compiler frame/cookie reconstruction
from original instructions and storage evidence; unsupported inputs remain visible.


## Round 003: original entry-stack address values

[`ghidra_frame_fix.py`](../rapid_object/ghidra_frame_fix.py) handles a narrower
case than reconstructing a stack frame: a single cookie XOR whose only stack
pseudo-object use is `(uint)&stack0xNEG`. It derives the fixed signed offset from
the actual original prologue and expresses the address value as the native
`_AddressOfReturnAddress()` converted to unsigned32, plus that offset with
unsigned32 wraparound. It allocates no substitute local and never dereferences
the reconstructed address.

The rule requires complete pinned ranges/bytes, an unambiguous actual unsigned32
type, a resolved global, and exactly one matching cookie-XOR site in a bounded
linear prefix. Distinct cookie sites are permitted only when the expected offset
uniquely identifies one. Calls, branches, interrupts, traps and system transfers
bound the scan; dynamic/unknown SP changes, ambiguous sites and any other storage
use remain unsupported. Inline spellings, forced-inline and naked entries are
refused. The selected single-function VC8 `/Ob1 /Oy` build must preserve the
out-of-line entry boundary; changing the build profile requires fresh validation.

This reconstructs an **original address expression**, not the replacement
compiler's security/SEH frame layout, handler fields, try levels or local aliases.
Those remain unresolved. Compilation and nonmatching objects are provisional;
no cookie or check is removed and no unknown input/callee becomes a success stub.

The initial 4,103-case profile was measured on 80 previous failures plus 20
compiling controls: **62 sources emitted, 53 newly compiling, zero new exact
matches**. All controls kept identical source and comparison outcomes. The three
exact pilot results were already-matching controls. Its 100-case invocation took
264.099 seconds after a retained two-case 4.615-second smoke, including shared VM
lock waits; four transport-only retries were retained and compiled. The selected
compiler emitted real intrinsic address math without an external intrinsic call.
No objects were executed or linked into a game, and no provider requests occurred.

A second fixed-prologue cookie site adds 842 eligible identities. Its separate
16-function pilot emitted four sources but compiled none: four prototype errors,
ten unsupported three-byte subpieces and two thiscall-declaration rejections.
Thus the expanded 4,945-case plan is eligibility, not a measured success forecast.
All 116 retained source/artifact outcomes reconciled unchanged after review fixes.

With the retained FS deferred plan, original and compiler configured:

```sh
python -m rapid_object.ghidra_frame_fix prepare --root local/repro-frame-fix
python -m rapid_object.ghidra_frame_fix pilot --root local/repro-frame-fix
python -m unittest discover -s rapid_object/tests -v
# After checking the measured pilot and exact implementation:
python -m rapid_object.ghidra_frame_fix sweep --root local/repro-frame-fix --resume
python -m rapid_object.ghidra_frame_fix pause --root local/repro-frame-fix
```

Preparation preserves an existing pilot selection and leaves the sweep paused.
The sweep uses the same serialized VM lock and verifies retained bindings before
reuse. Independent review caught alternate MSVC inline qualifiers and traps not
covered by a mnemonic-prefix check; instruction groups plus explicit ungrouped
trap/system boundaries now have generic negative controls. The original needs-fix
verdict and final independent approval are retained locally.

## Round 005: restore omitted callback typedef declarations

[`ghidra_declaration_fix.py`](../rapid_object/ghidra_declaration_fix.py) closes a
specific declaration omission: a draft references a numeric `_func_N` type whose
FunctionDefinition metadata exists in the saved Ghidra project but whose typedef
was omitted from C++ export. The pass prepends the metadata-derived typedef and
preserves every existing source byte. It supplies no dependency implementation
and changes no call arguments or storage layout.

The read-only type export binds the pinned module, image base, x86 Windows
language/compiler specification, exporter and unchanged persistent project hash.
Each raw draft must come from that same project revision. Rendering requires an
unambiguous signature, explicit supported calling convention and ABI-sized
primitive/pointer types. Missing/ambiguous metadata, conflicting declarations,
unknown conventions, unsupported records/arrays/nested callbacks and incompatible
variadics are refused. Ghidra signatures remain hypotheses about the original ABI.

The fixed pilot selected 80 previously failing functions and 20 compiling controls:
**75 targets compiled, four still failed, one interrupted build remained unknown,
and zero new exact matches**. Target comparisons were 59 inconclusive and 16
nonmatches. All 20 controls retained identical source bytes and comparison statuses;
the ten exact controls were already exact. The four compiler failures were two
argument-count disagreements, one unresolved import and one pointer conversion.
The unknown empty build directory at RVA00335350 was retained without replay.

Ghidra 12.1.4 exported the graph in 3.846 seconds. VC8 SP1 14.00.50727.762 x86
compiled under Windows 11 ARM64 translation; Apple Clang 21.0.0 supplied the
existing target-aware parsing. The 104 retained build receipts, including five
transport-only retries, sum to 201.130 seconds. Per-case elapsed times including
lock waits sum to 481.489 seconds across two run episodes. A later 0.237-second
cache reconciliation performed no new builds. No DeepSeek requests were made;
separately prepaid operator work is development cost and is not priced here.

With the configured original and analyzed project:

```sh
python -m rapid_object.ghidra_declaration_fix export-types --root local/repro-callback-fix
python -m rapid_object.ghidra_declaration_fix census --root local/repro-callback-fix
python -m rapid_object.ghidra_declaration_fix pilot --root local/repro-callback-fix
python -m unittest rapid_object.tests.test_ghidra_declaration_fix -v
```

The measured 378-identity plan is a subset of retained repair sources, not the
whole remaining inventory. Its 298 identities without pilot results remain queued;
the sweep has not been launched. This round does not fix the parked round-004
helper/storage approach, which remains unapproved and unpublished.

Separately, the completed FS round-002 sweep measured **1,934/1,934 targets, 965
additional compilations and zero new exact matches**. Deduplicating its original
pilot and sweep gives 1,983 targets plus 20 controls; 985 compiled includes those
20 controls, and all three exact results are old controls. These completed FS
counts do not include the separate ongoing frame-address sweep.

## Bounded AST-guided matching pilot

[`ast_match.py`](../rapid_object/ast_match.py) searches a small retained nonmatch
frontier after compilation works. Instruction distance ranks the search only;
the unchanged comparator's complete, relocation-aware function equality is the
sole acceptance condition. The original source is retained as the baseline, and
failed variants stay local and explicitly UNVALIDATED.

The pass requires a successful complete Clang parse targeting i686 Windows MSVC
with C++98 and MSVC-14 compatibility settings. It supports ASCII source only,
checks AST integer32 types and nested source byte spans, verifies actual operator
spelling against masked comments/strings, and refuses macro expansion/spelling
ranges. Finite single-site proposals change comparison operators, compare operand
signedness, or express a zero test as an unsigned ordered comparison. Pure operand
reorientation additionally excludes calls, assignment/increment effects and
volatile reads. These are proposals about decompiler hypotheses and source forms; they are not
assumed to preserve the baseline's behavior. A nonmatch alone does not establish
that baseline behavior is wrong: equivalent comparison spellings can lower
differently with the historical compiler.

The order is deterministic and source-hash deduplicated, with a hard maximum of
eight variants per function and a four-variant pilot budget. Each variant must
parse completely before the existing VC8 build and exact comparison. The fixed
plan binds generator/dependency versions; retained attempts bind source, object,
compiler, original request/ranges and comparison implementation. Interrupted build
outputs are retained and refused, rather than silently recompiled. The shared VM
lock serializes this experiment with the frame sweep.

The retained census contained 94 equal-length nonmatches of at least 24 bytes
with at most four differing bytes. Of those, 85 supported these AST sites and nine
had no eligible integer comparison. Eligible bodies span 24–261 bytes. The pilot
uses all 85 eligible cases, stratified by body size and
relocation count, plus ten unchanged known-exact controls. This selected frontier
is not a sample of all game functions. The retained census is an input to these
commands; another project must derive its own pinned frontier first:

```sh
python -m rapid_object.ast_match prepare --root local/repro-ast-match
python -m rapid_object.ast_match run --root local/repro-ast-match
python -m unittest rapid_object.tests.test_ast_match -v
```

The initial operator-only smoke exhausted eight variants without a match. A
generic unsigned ordered-zero hypothesis then matched the full 87-byte function
at RVA005b0470 in one attempt. Both smoke episodes remain recorded separately
from the fixed pilot. Apple Clang 21.0.0 provided the AST; VC8 SP1 14.00.50727.762
x86 compiled with the existing `/O2 /Ob1 /Oy /Gy /Z7 /Zl /GS- /GR- /EHsc` profile
under Windows 11 ARM64 translation. No original or candidate game code was
executed. Zero DeepSeek calls excludes neither operator/model development cost
nor compiler and review time.

The original exporter skipped the AST result format because its status and
requested-identity fields use a different envelope. The independently reviewed
`tools/export_ast_matches.py` now generates a canonical private report from bound
AST results. It checks redundant module/RVA fields before projecting them out of
copied receipts; original reports stay unchanged. The existing exporter then
rechecks the original, source, object, compiler, ranges and complete comparison.

```sh
python tools/export_ast_matches.py \
  --report local/matching-frontier-002/STATUS.json \
  --original gamedata/bin_ship/DAOrigins.exe \
  --output local/repro-ast-export
python -m unittest tests.test_export_ast_matches -v
```

Use a new output directory for each bridge run. To extend an existing source
snapshot, load its index and translation-unit source bytes, then call
`tools.export_native_sources.extend_snapshot(index, files, [report_path], original_path)`
and `publish(index, files, output)` after checking the returned audit. This retains
previously published identities and source bytes. The exporter's standalone CLI
rebuilds a snapshot from its supplied roots/reports; omitting old free reports can
omit their functions. The AST import added seven functions while preserving all
2,209 previous records and source bytes, bringing the snapshot to **2,216**.

**Completed pilot:** 85/85 near cases and all ten controls were accounted for.
Twelve frontier sources became full exact matches, totaling 529 body bytes.
Cross-checking the existing published index identified five already-published
identities (189 bytes), leaving **seven genuinely new matching identities and
340 body bytes**. The successful smoke identity is included in those seven,
not added again. All twelve frontier wins used the unsigned ordered-zero rule;
other proposed comparison forms produced no additional matches in this budget.
All ten control sources and their compiled function bytes stayed identical.

The pilot retained 316 build attempts: 310 compiled objects and six transport
exit-255 outcomes without compiler/object receipts. Those six remain inconclusive
and were not retried or credited. All 310 compiled comparisons were freshly
recomputed against the pinned original and agreed with their retained reports.
Build receipts total 522.343 seconds; the resumed invocation took 941.162 seconds
including cache checks and shared VM waits. The earlier interrupted episode and
nine separate smoke attempts are retained; smoke elapsed time was 58.863 seconds.
These durations overlap/reuse work and must not be added as compiler time.
Eleven near-case mutations compiled to machine bodies already seen for that
function; source-hash deduplication cannot predict every compiler equivalence.

The original runner stopped after 14 complete cases; the cause is unknown.
One complete compiler/object receipt lacked only its comparison summary. Artifact
checks and the unchanged comparator finished that step without rebuilding, and
the same plan continued with a detached process. The final local
`final-pilot-receipt.json` distinguishes novel identities from the frozen status
counter, which counts improvements over selected nonmatching sources and does
not deduplicate against previously published sources. No search or acceptance
rule changed during the pilot. Seventy-three target sources remain unvalidated.

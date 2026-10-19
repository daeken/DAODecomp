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

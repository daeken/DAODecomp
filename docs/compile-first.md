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

The original free compilation pass continues against its unchanged converter and
sources. Repairs use an additive module and separate output directories so the
live pass and its source bindings cannot change underneath it. The repaired pass
shares the existing VM lock, preserves failed attempts and does not modify the
comparator or production acceptance counts.

Unmodeled incoming registers, stack state and unsupported helper semantics remain
unresolved. Unknown calls are not replaced by successful dummy functions. Declared
types and signatures remain hypotheses until supported by stronger evidence.

The first repair measurement and subsequent sweep receipts live under ignored
`local/deterministic-compile-001/`. See the [$200 plan](cost-target.md) for the
broader budget and the distinction between compiled functions and a runnable
replacement executable.

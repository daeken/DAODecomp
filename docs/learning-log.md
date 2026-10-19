# Learning log

This log records transferable findings, including failures. It is maintained
alongside the [methodology](reproducible-decompilation.md). Dates identify project
observations; values are snapshots, not live completion counters. Private receipts
remain local; public code, synthetic tests and aggregate measurements are linked.
Dollar figures concern DeepSeek usage unless stated otherwise. They exclude
engineering time and Codex coordination/tool-development usage, whose account
quota contribution has not been measured. A zero-request experiment means its
batch execution made no provider calls, not that the tooling cost nothing to build.

## 2026-10-17–18: per-function preparation became the bottleneck

The early workflow required bespoke contracts, corpora, adapters and multiple
review stages around small function batches. It produced useful isolated evidence,
but preparation and coordinator work dominated throughput. This is a qualitative
project observation, not a measured causal estimate of token savings.

**Change:** C++ is the only authored artifact per new function. Derive identity,
build inputs and comparison records automatically; test common validation machinery
instead of hand-authoring every function's validation package. Retain the earlier
94-function corpus results as historical evidence without making that workflow a
prerequisite for generating more code. See [validation](validation.md).

## 2026-10-18: linking every candidate unnecessarily restricted generation

The initial native pilot compiled a DLL for reccmp. Dependencies made arbitrary
caller/callee groups difficult to build independently.

**Change:** compile standalone COFF objects with external declarations, then resolve
supported relocations against explicit original identities. This permits unresolved
dependency implementations without fake bodies. Full boundaries and relocation
addends still matter; missing support is inconclusive. See
[object recovery](object-recovery.md) and its common negative controls.

## 2026-10-18–19: easy functions gave a misleading cost forecast

The published 920 matches comprised 807 earlier native matches and 113 new object
matches. The user reported about $32 actual billing overall, but local conservative
ledger estimates were about $13.97/807 versus $34.92/113 for those two populations.
Those ledger estimates are not the same thing as the user's bill. The matches
covered only about 0.46% of inventoried body bytes, with possible range overlap.

**Learning:** report new distinct matches, corpus composition, bytes and runtime
milestones alongside function counts. Do not extrapolate leaf costs to the whole
game or subtract imported matches from a workflow's cost denominator. See the
[cost audit and budget plan](cost-target.md).

## 2026-10-18–19: fix address identities before paying for another rewrite

In 1,706 unresolved-symbol observations, 1,516 used a VA where the stable name
required an RVA. A source-only normalizer consults the canonical registry and
preserves already-known RVA names, including uppercase hexadecimal spellings.
It does not make the comparator guess or mask addresses.

**Measured:** 20 retained batches, 175 compared function observations, exact matches
increased from 9 to 17; eight distinct new matches, zero provider calls. Identifier
boundaries, comments and quoted literals must survive unchanged. See
[`symbol_normalize.py`](../rapid_object/symbol_normalize.py) and its
[generic tests](../rapid_object/tests/test_symbol_normalize.py).

## 2026-10-18–19: non-thinking saves tokens, but useful output is the denominator

87.6% of completion tokens in 965 retained object responses were reasoning.
Truncated responses consumed about 19.9% of retained-response budget debit.
This motivated a small non-thinking experiment; it did not establish that disabling
reasoning would preserve recovery quality.

**Measured:** an initial six-group trial failed response checks. After sorting the
requested identities and canonicalizing draft names, five of six responses were
valid, two groups compiled, and one of 20 requested functions matched—already found
by the free seed pass. Combined token debits were about $0.0591 conservatively.
This was not a randomized comparison. Preserve the failed attempts and compare
new useful results per dollar, not output tokens alone. Production defaults were
not switched. See [the complete experiment summary](cost-target.md).

## 2026-10-19: Ghidra is a useful free first pass

A 200-function sample stratified by size and direct-call count produced 200 drafts,
133 provisional sources, 106 compiled objects and 12 exact matches, eight new.
Export took 6.09 seconds; compiler/comparison measurement took 186.21 seconds.

The whole 27,555-identity inventory then produced 27,553 drafts and 15,859 provisional
C++ sources in 312.59 seconds, in 28 read-only batches, with no inference calls.
The other 11,696 identities retained drafts or explicit failure reasons. Those
whole-inventory sources had not been bulk-compiled at export completion.

**Learning:** free decompilation and ordinary syntax lowering should precede paid
source generation. Keep failed/unsupported drafts instead of hiding them from the
denominator. Ghidra types, signatures and expressions remain hypotheses. Code and
reproduction commands: [Ghidra seed tooling](../rapid_object/ghidra_seed.py),
[static-analysis setup](static-analysis.md), [cost plan](cost-target.md).

## 2026-10-19: caches need persistent inputs and actual source bytes

Review found that Ghidra's in-memory modification counter was unsuitable as a
cross-run analysis revision. It also found paths where an edited/deleted candidate
could leave a stale conversion or measurement status.

**Change:** bind persistent analysis-store content, settings and tools; check it
around export. Verify source bytes before reading a measurement cache. Restore
bound generated source while preserving unbound edits separately. The final
converter reproduced all 200 historical statuses and 133 emitted source hashes,
so the old measurement could remain explicitly historical without recompilation.
See [seed regression tests](../rapid_object/tests/test_ghidra_seed.py).

## 2026-10-19: distinguish converter bugs from decompiler uncertainty

The initial receiver parser mishandled `int *param_1` and could cross a parameter
comma. In the first 6,000 measured identities this accounted for 215 first-error
undeclared-parameter cases and 71 syntax cases; another 147 drafts were rejected
for unrecognized receiver declarations. Fixing this does not require a model to
reconstruct the function again.

Pointer conversions form another large class, where target-aware AST information
is more appropriate than broad regex casts. Unknown incoming registers, stack
state and helper semantics are a different problem and cannot be assigned dummy
values. The additive [compile-first repair pass](compile-first.md) keeps the
original pass unchanged.

**Measured:** 54 of 80 targeted previous failures/conversion rejections now compile;
20 of 20 previously compiling controls still compile, without comparison-status
regressions. The full 100-case pilot includes six complete object matches and used
zero provider requests. This sample targets known repair categories and does not
estimate the yield over every remaining function. Apple Clang 21 supplied x86
AST analysis; VC8 SP1 14.00.50727.762 produced the objects in the Windows ARM64 VM.
See [the implementation and conditions](compile-first.md).

## 2026-10-19: separate transport failures from source failures

Five repair-pilot attempts failed before compiler results with a Parallels
`PrlJob_GetResult` transport error, including two unchanged control sources.
Rebuilding the exact retained sources once succeeded in all five cases. Preserve
both attempts and count retries in elapsed work; a final cache-reconciliation
duration is not the original experiment's runtime.

**Learning:** classify transport, compiler, comparison and unsupported outcomes
separately. A transport retry does not require a new model generation. Conversely,
successful process exit without the expected object is not a successful compile.
Resume records must verify actual source/object and tool identities, not just the
presence of a result file.

## 2026-10-19: equal pointer width does not make every cast harmless

A synthetic review case with multiple inheritance showed that a C-style cast
between class pointers can adjust the address even on the same 32-bit target.
Width alone therefore cannot authorize a general pointer-conversion rewrite.

**Learning:** limit the rule to the demonstrated scalar signedness/address cases
and leave unsupported class conversions unresolved. Test the transformation's
preconditions with small synthetic examples; compilation by itself would not
have exposed this behavior change.

## 2026-10-19: completed whole-inventory free compilation and repairs

Both passes completed without provider requests. The baseline measured all
27,555 identities in 28 chunks: 11,986 compiled objects, including 1,658 reported
exact matches. The additive repair sweep examined 4,424 eligible failures or
conversion rejections and produced 2,188 additional compiling functions, including
184 reported exact matches. There is no identity overlap between either pair of
baseline/repair result sets.

**Combined:** 14,174 distinct identities compile (51.44% of the inventory), and
1,842 have exact-match reports from these free passes. Deduplicating against the
920 previously published functions leaves **1,289 new unpublished matches** and
2,209 distinct reported matches overall. These aggregate counts come from retained
reports; the new sources still need artifact verification and source publication.
At the time of this aggregation, the published source index remained at 920.
Neither compilation nor the inventory percentage measures whole-game completion.

The baseline wall duration was 28,257.355 seconds (7.85 hours); the following repair
pass took 20,707.124 seconds (5.75 hours), overlapping the baseline and sharing its
VM compiler lock. Do not add those durations or treat the repair's waiting time as
compiler execution. Both used the existing VC8 x86 compiler under Windows ARM64
translation, with no linked replacement execution.

**Next limitation:** 13,381 identities still lack a compiling source in these two
passes. Of those, 9,369 retain an `unmodeled_register_or_stack_input` diagnostic;
other leading categories include extended types/instructions, declarations and
calling-convention conversion. This is a converter diagnostic census, not proof
that each binary function requires unusual machine state. Investigate shared
signature/state reconstruction rules before paying for individual rewrites; do
not invent incoming values to make the code compile.

Reproduction uses the [baseline commands](reproducible-decompilation.md) and
[repair sweep](compile-first.md). Private receipts are
`local/cost-reduction-001/full-seed/compile-summary.json`,
`local/deterministic-compile-001/sweep-status.json` and the RVA-deduplicated
`local/deterministic-compile-001/completed-aggregate.json`.

## 2026-10-19: publish free-pass matches by reusing verified compiler artifacts

The source exporter now consumes the free baseline and repair reports. It checks
the pinned original identity and complete ranges, actual source/build copies,
object/compiler/flag identities and comparator bindings, then repeats the existing
object comparison. It derives relocation targets from stable identities and actual
object symbols rather than trusting cached relocation overrides.

**Measured:** all 1,842 reported exact rows verified again, with zero rejections;
553 were already published and 1,289 were new. The resulting source tree contains
2,209 matching functions in 1,544 translation units. All 920 prior function records
and 255 source files were preserved. An independent review repeated the comparisons
and checked every staged public file. This required no model generation or VM
recompilation and did not promote the retained nonmatches.

**Learning:** retained compiler artifacts can support cheap source publication
when their actual identities still verify. A success label alone is insufficient.
Keep public C++ and sanitized provenance separate from local binaries, raw exports
and machine paths. The reusable adapter and generic tamper/missing-artifact tests
are in [the exporter](../tools/export_native_sources.py) and
[its tests](../tests/test_native_source_export.py).

## 2026-10-19: distinguish explicit FS access from unknown incoming state

The state-input blacklist hid a reusable conversion opportunity: 8,014 of 9,369
blocked drafts mention `unaff_FS_OFFSET`, and 7,507 satisfy the first byte-backed
DWORD `FS:[0]` access profile. The new shared pass checks the original instruction
forms, complete ranges, widths and static access counts before using real native
compiler intrinsics. It does not invent incoming registers or remove exception
registration operations. Review caught a typedef-width check fooled by a commented
declaration; comments/literals are now masked and an actual unique type is required.

**Measured pilot:** 58 new sources and 16 new compilations among 80 previously
blocked functions, with zero new exact matches. All 20 compiling controls retained
their source and comparison outcomes. The 100-case pilot invocation took 123.760
seconds after a 3.405-second two-case smoke run; two transport retries remain
recorded. No DeepSeek requests occurred. These are VC8 x86 object builds under
Windows ARM64 translation, not execution or exception-behavior validation.

**Next bottleneck:** 33 pilot failures contain negative frame-address placeholders
XORed with the cookie global. Among all 9,369 state-blocked drafts, 6,201 contain
`stack0x` and 6,001 contain the cookie/address pattern. An arbitrary local array
or guessed frame address would hide the problem rather than recover it. The
reviewed FS sweep therefore selects 1,934 cases without those placeholders and
retains 5,573 explicitly deferred cases. The full 7,507-case plan and partition
recipe remain available; nothing is removed from the inventory.

**Learning:** separate decompiler notation, explicit machine operations and true
incoming-state uncertainty. A generic fix can expose the next root cause without
immediately producing a match. Classify that cause before spending thousands of
known-failing compiler attempts. See [preconditions and reproduction](compile-first.md)
and the generic [regression controls](../rapid_object/tests/test_ghidra_state_fix.py).

## 2026-10-19: keep artifact readers independent of build orchestration

The free-match exporter passed on macOS and Linux but Windows CI failed because
its pure symbol helper lived in a module that transitively imported Unix-only
process locking. No build was needed for the export; the import graph introduced
the platform dependency anyway.

The isolated repair uses an export-local symbol decoder with parity tests against
the frozen build helper. A fresh child process forbids the build modules and
`fcntl` while running every retained-export acceptance/refusal control. The old
version reproduced 20 errors across seven tests; all seven passed after repair.
The full macOS tooling run passed 263 tests with seven skips. Replaying all 29
retained reports produced identical 1,842 verified rows and the same published
2,209 function records, 1,544 units and source bytes. The restricted-import check
is a regression control, not a substitute for actual Windows CI.

**Learning:** a helper can have a platform-neutral body but a platform-dependent
import graph. Keep read-only artifact processing behind pure dependencies. When
a compiler worker is running with pinned inputs, avoid changing its shared module
just to repair a reader. A small isolated helper plus explicit parity controls
can preserve the running worker; shared-module cleanup can wait for a stopped,
measured migration.

## Still unproven

- The $200 target for a runnable whole-game replacement.
- Linking the generated translation units into a functioning game.
- Generality across a second game, compiler family or architecture.
- Behavioral equivalence of compilable nonmatches.

These are explicit next investigations, not successes implied by the current
function counts or synthetic tooling tests.

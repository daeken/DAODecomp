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

## 2026-10-19: distinguish an address value from replacement frame storage

The next free rule handles one negative stack address used only in a cookie XOR.
Original instructions establish its fixed offset from entrySP. A real compiler
intrinsic returns the actual entry return-slot address; unsigned32 addition then
preserves the original address value without fabricating a local array, incoming
parameter or zero cookie. This does not reconstruct SEH frame fields or make the
remaining draft safe to run. Unknown storage uses stay unresolved.

**Measured initial pilot:** 53/80 newly compiling functions, 62 emitted sources,
20/20 unchanged controls and zero new exact matches. The 100-case invocation took
264.099 seconds, reusing a two-case 4.615-second smoke; VM lock waits and four
retained transport retries are included. A separate 16-function two-cookie-site
extension produced zero compile gains because later helper/prototype issues
blocked it. No provider requests or game execution occurred. Do not pool the
extension with the initial denominator or infer whole-inventory yield.

**Review finding:** a register-delta proof also needs an execution boundary.
Mnemonic prefixes missed INT3, UD2, INTO, IRETD and HLT, allowing a later cookie
site to appear reachable. The correction uses decoded instruction groups and
explicit ungrouped traps/system transfers. Alternate `_inline`/`__inline`
spellings also need the same entry-boundary refusal. Generic negative controls
and an independent delta review cover both corrections; all 116 retained sources
and artifact outcomes remain unchanged. Source compilation still grants no match
credit. See [preconditions and commands](compile-first.md#round-003-original-entry-stack-address-values).

**Next shared blockers:** three-byte subpiece operations, missing declarations
and prototype mismatches. Preserve their type/storage uncertainty rather than
patching individual functions or stripping security checks.

## Still unproven

- The $200 target for a runnable whole-game replacement.
- Linking the generated translation units into a functioning game.
- Generality across a second game, compiler family or architecture.
- Behavioral equivalence of compilable nonmatches.

These are explicit next investigations, not successes implied by the current
function counts or synthetic tooling tests.

## 2026-10-19: recover declaration closure before rewriting calls

A saved Ghidra FunctionDefinition for `_func_4879` was present while the C++ draft
used `_func_4879 *` without its typedef. Read-only metadata export and a narrow
numeric-callback declaration pass recover the omitted declaration while preserving
all pre-existing source bytes. Explicit type widths, convention, variadic form,
project revision and module identity must agree; missing or ambiguous metadata
stays unsupported. This repairs declaration closure and does not establish the
original signature's correctness.

**Measured:** 75/80 previously failing targets compiled; four compiler failures and
one interrupted unknown were retained. No new exact matches resulted: 59 target
comparisons were inconclusive and 16 were nonmatches. All 20 controls retained
source and comparison outcomes, including ten prior exact matches. The 104 build
receipts, including five transport retries, total 201.130 seconds of receipt time;
481.489 seconds of per-case elapsed time includes shared VM waits. A subsequent
0.237-second cache check is not the build cost. No DeepSeek calls occurred;
operator development and review were separately prepaid and remain unpriced here.

The completed, separate FS sweep produced 965 additional compilations from 1,934
targets and zero new exact matches. Its deduplicated pilot/sweep aggregate contains
1,983 targets and 20 controls; the three exact results are old controls. Keep these
counts separate from callback compilation and the ongoing frame sweep. See
[conditions and reproduction](compile-first.md#round-005-restore-omitted-callback-typedef-declarations).
The callback plan's remaining 298 cases stay queued. The parked helper/storage
round remains needs-fix; it was not published with this approved declaration pass.

## 2026-10-19: bound AST matching and deduplicate novelty against publication

An equal-length near-nonmatch frontier contained 94 bodies of at least 24 bytes
with at most four differing bytes. Eighty-five had eligible integer-comparison
AST sites (24–261-byte bodies); nine had none. Complete target-aware parsing,
validated byte spans and integer types supported deterministic comparison/source
form proposals with four variants per pilot function. Original source and failed
variants were retained. The unchanged full-range relocation-aware comparator,
not instruction distance, decided acceptance.

**Measured:** 12/85 frontier sources matched, totaling 529 bytes. Five identities
were already in the published index, so the actual new yield is **seven distinct
functions and 340 bytes**. All ten unchanged exact controls stayed byte-identical.
The frozen status counter measures frontier-source improvements; the final
receipt corrects novelty against the prior 2,209 published identities. Comparing
only with the chosen baseline would have overstated new recovery credit.

Every winning proposal used unsigned ordered-zero form. An operator-only smoke
failed in eight attempts; a subsequent generic ordered-zero smoke matched a full
87-byte function in one attempt, and that identity was independently rebuilt in
the pilot. Equivalent comparison spellings can lower differently in VC8, so a
baseline nonmatch is not evidence that its behavior was wrong. Other proposed
comparison forms added no matches in this bounded experiment.

The 316 pilot attempts contain 310 compiled objects and six retained inconclusive
transport failures, with no automatic retries. Fresh comparison of all 310
objects reproduced their reports. Build receipts total 522.343 seconds; resumed
wall time was 941.162 seconds with shared VM waits and cache checks. Nine separate
smoke attempts took 58.863 seconds elapsed. Eleven near-case variants compiled
to previously observed function bytes. These are measured development costs even
though no DeepSeek calls occurred; separately prepaid operator costs are unknown.

The approved exporter skipped the AST report format unchanged, so all new matches
remain local with hashed source/build/comparison paths. No adapter was added, and
all 2,209 prior published records, source files and provenance were preserved.
See [the conditions and commands](compile-first.md#bounded-ast-guided-matching-pilot).
No game executable was linked or run, and these compiled-artifact results do not
establish whole-game behavior. Harder functions and broader synthesis remain later
work rather than an extrapolation from this selected frontier.

## 2026-10-19: make compiler test fixtures independent of local setup

The first AST/declaration tooling checkpoint passed locally but failed five
callback tests on clean Linux CI: their fake builds still opened the real
checkout's ignored VM lock directory. The fixture now creates its own temporary
lock directory and redirects the repository path there, preserving the real
locking and source/object rejection checks. A separate run with a deliberately
absent original checkout reproduces the clean environment. This changes test
isolation only; production transformations and comparison rules are unchanged.

## 2026-10-19: bridge report formats without weakening comparison

AST results needed a small generated metadata bridge to the existing source
exporter. It validates the accepted candidate and redundant identity fields,
retains the original receipts, and produces the envelope the exporter expects.
The unchanged exporter independently repeats the full comparison before import.
Independent replay verified 12 matching identities: seven new functions totaling
340 bytes and five existing duplicates. All 2,209 prior function records,
translation-unit records and source bytes were preserved; the source index now
contains 2,216 functions. Seven generic refusal tests and the full 270-test suite
(seven skips) passed on macOS ARM64. No provider calls or new VM builds were
needed: these exact compiled artifacts already existed. Keep old publication
state as the base of incremental exports; rebuilding from incomplete input roots
can silently omit earlier imported sources.

## 2026-10-19: measure the remaining reach of a successful rewrite

Scaling the ordered-zero rewrite used a frozen census of 37,492 retained rows,
with 13,490 distinct reported compiling nonmatch identities. The conservative
selection required 24–512-byte bodies, a length difference of at most 16 bytes,
similar instruction shape, an original compare-with-zero followed by JA/JBE,
and the unchanged rule as the first proposal. Published identities and prior
pilot cases were excluded. Only two new targets qualified; neither matched.
All five unchanged exact controls passed. Seven actual build receipts total
11.928 seconds; two smoke builds were reused instead of compiled twice.

This exhausts the stated selection profile, not every possible zero-predicate
rewrite. The remaining differences in these two callers include ECX receiver
setup and stack cleanup. Their callees both return with four bytes of cleanup,
but that alone does not identify a calling convention. The next bounded
investigation uses caller and callee instructions together before proposing
declaration changes. A successful local rewrite should be measured against its
remaining population before assuming it will scale to thousands of functions.

## 2026-10-19: defer comparison extensions with low measured yield

A retained inconclusive group contained 620 defined-target references: 547
compiler string symbols, 65 floating-point literals and eight other symbols.
An isolated experiment selected 50 literal cases and ten existing exact controls.
It derived whole standalone COFF literal extents and considered only narrow or
wide terminated strings with no embedded relocations. The proposed resolver
required unique full content across backed PE sections, read-only storage,
alignment, a preceding zero unit, zero addend, and a decoded original immediate
reference to the independently selected address. It did not fill relocation
fields with whatever address would make the function match.

The experiment made three functions comparable, all nonmatches (320 original
body bytes). Forty-seven remained inconclusive; all ten exact controls stayed
exact. The remaining reasons were differing instruction layout at 26 reference
sites, ten unsupported floating-point literals, eight duplicate literals, two
uncertain string starts and one conflicting reference. Fifty focused tests
passed, including 29 new refusal/acceptance controls and 21 existing comparator
controls; the configured project environment passed 270 tests with seven skips.
The initial system-Python run lacked Unicorn and is retained as an environment
failure. No compiler builds or provider calls were needed for this experiment.

This proposal remains local, unreviewed and unadopted because its measured match
yield is zero. Original debug metadata is not categorically necessary for literal
matching, but unique byte content alone is insufficient evidence. Measure whether
a comparison extension unlocks useful matches before adding production machinery.
These two experiments used no DeepSeek calls; development and Codex costs are
separate and have not been priced here.

## 2026-10-19: classify observations before diagnosing repairs

A deterministic census freshly reproduced 14,174 retained object comparisons
without a binding failure or status change. Removing 2,181 already-published
identities left 11,993 repair candidates or unsupported comparisons. The largest
primary labels were stack adjustment/cleanup (3,658) and branch condition (1,985),
but most included broader structural differences. Only 106 unpublished nonmatches
had identical instruction shapes throughout. Small observed frontiers include
40 memory-addressing cases, 13 register cases and seven stack-cleanup cases.

Fixed label precedence makes counts reproducible; overlapping labels and bounded
instruction examples keep the primary label from hiding other differences.
Relative calls require decoded targets as well as encoded operands: identical
relative bytes at different instruction offsets can call different addresses.
That case now has a generic regression control. Unknown relocations, unsupported
ranges, incomplete decoding and alignment-budget limits remain explicit.

Fresh comparison plus initial classification took 138.731 seconds; the final
classification replay took 24.310 seconds. Thirty focused controls and the
270-test standard suite (seven skips) passed on macOS ARM64. No compiler or
provider calls were needed; engineering/review effort is separate. The
[census methodology, results and command](mismatch-analysis.md) are public;
original decoded instructions and all generated evidence stay ignored locally.

## 2026-10-19: compare paired lifted trees without treating unknowns as agreement

SharpRetro revision `685b7578457cad325226aa8923b45ded35098fa3` built successfully
with .NET 10. A small external-checkout adapter serializes actual typed Bits32
LiftIl, retaining lossless constants, register/flag/memory operations and opaque
nodes. Capstone separately checks complete instruction boundaries. Synthetic
controls demonstrate that different ADD encodings can share a tree, while
register, immediate, memory, flag, width and call/return changes remain visible.

The 40-pair retained pilot took 13.883 seconds: 25 of 30 nonmatches yielded
supported IL differences, four were opaque and one incomplete. All ten exact
controls had identical raw trees, but one was opaque. Counting all ten as
supported agreement would have hidden that limitation. Seventy-one of 80 sides
were fully supported; 720 of 3,235 decoded instructions were opaque, mostly x87.
The entire 27-byte undecoded suffix was preserved. This is a stratified pilot,
not a whole-game coverage estimate or a new equivalence acceptance path.

Twenty-six focused tests passed; independent review repeated five representative
real pairs and the controls. Portable artifact readers must not import VM build
orchestration: the adapter uses pure comparison/export helpers and explicit
original/checkout/DLL/manifest configuration. The final portable version reproduced
all 80 initial trees without structural changes. Source, binary and runtime
bindings are verified, and refreshing a manifest remains an explicit build step.
No VC8 rebuilds or provider calls occurred. See [paired-lift usage](../tools/sharpretro/README.md)
and [measured limitations](sharp-retro.md).

The first diagnostic-tool checkpoint passed Linux/macOS CI but Windows could
not import the paired tests: its job installed only the execution dependency,
while Capstone and pefile were restricted to Unix jobs. The pure diagnostic
readers now need those pinned packages on every host. CI installs the unchanged
native dependency list on Windows too and explicitly runs the portable mismatch
controls there; Unix-only orchestration suites remain separately scoped. Optional
actual SharpRetro execution still requires the explicit checkout/build configuration.

### 2026-10-19: fix the shared instruction model before interpreting IL differences

Paired lifting exposed a reusable SharpRetro addressing problem: ModRM offset
arithmetic used 64 bits even when the instruction selected a 16- or 32-bit address
size. The reviewed correction reduces the completed effective offset to the
decoded address width before segment-base addition. Operand width is separate.
It is published as [SharpRetro PR 2](https://github.com/daeken/SharpRetro/pull/2),
commit `ec8344102af8b495e5de1a869188b91bc3d4d756`, now pinned by the optional adapter.

The 24 new upstream tests reproduced 19 failures before correction; all 278
upstream tests now pass. A separately implemented address-effects protocol found
245/245 agreements with Unicorn versus 171/245 disagreements on the baseline;
independent review repeated this and added 11 passing controls. These observations
cover selected address effects, not every instruction effect or real x86 hardware.
Do not use a common lifter's agreement with itself as independent verification.

All 40 prior diagnostic inputs were replayed after rebuilding the adopted adapter:
13.692 seconds, no category changes, all ten exact controls preserved, zero new
accepted functions. Address trees changed as expected; old dependency builds and
receipts remain available. The 27-byte incomplete suffix is embedded jump-table
data, so decoder expansion would be the wrong repair. Opaque x87 semantics remain
separate work. No provider calls or VC8 builds were made; toolkit development and
independent review still consumed Codex effort. See [reproduction and limits](sharp-retro.md).

## 2026-10-19: a memory-addressing label exposed a missing receiver input

All 40 small aligned memory-addressing nonmatches were inspected against actual
bytes and complete source ASTs. Twenty-nine supported one common hypothesis:
the original indirect edge carries a receiver in ECX and reads its vtable slot,
but the provisional no-argument function-pointer call does not express that
input. The generic proposal binds both expressions to original dataflow, retains
the target and return hypothesis, and adds the observed receiver. It does not
invent callee implementations or claim unknown stack/EDX contracts are known.

One variant per target made 29 distinct VC8 attempts: 28 compiled, **16 newly
matching functions / 311 body bytes**, 12 nonmatches and one transport-255
unknown. The three successful smoke builds are included, not repeated or added
again. Ten prior exact controls were reused and freshly checked. Nonmatches
still differ in target-register selection; no register difference was normalized
away or accepted. The transport outcome is preserved without replay.

Build receipts total 45.362 seconds, with 5.367-second smoke and 42.561-second
continuation wall times. Twenty-eight generic controls and the full local
project/object suites passed, as did CMake, six C++ checks and both synthetic
demos. The independently reviewed rule and existing exporter verified sixteen
new source rows, preserving all 2,216 previous published identities and source
bytes; the snapshot now contains 2,232 functions. Engineering and review cost
remain separate from zero provider calls. See the [rule conditions and measured
reproduction](compile-first.md#bind-indirect-receiver-hypotheses-to-the-observed-call-edge).


### Unchanged receiver-rule breadth checkpoint

The follow-up applied the reviewed `indirect_receiver_fix` unchanged to the
frozen 14,174-identity retained census (11,098 compiled nonmatches). Selection
excluded 351 published nonmatch identities and 13 unpublished prior attempts;
the other 16 prior attempts were already published. The prior exit-255 input was
excluded without replay. Cheap original-edge checks left 48 cases; complete AST
checks admitted 25 new targets covering 480 original body bytes, rejecting 23
unsupported source shapes. The deterministic ascending-RVA plan had no remainder.

One variant per target used 25 new VC8 attempts: 24 compiled, nine passed the
unchanged complete relocation-aware comparator (161 body bytes), 15 remained
nonmatches and one transport exit 255 stayed unknown without retry. Ten unchanged
exact controls reused their objects and passed fresh comparisons. Selection took
3.627 seconds; the pilot took 35.185 seconds, including 32.998 seconds in build
receipts and 0.0012 seconds waiting for the shared VM lock. Compiler, target-aware
Clang settings, rule and acceptance remained those of the preceding checkpoint.
Remaining differences include tail-call/register allocation, narrow return values
and arithmetic forms; no additional repair was attempted in this round.

The existing AST bridge and source exporter freshly rebound all nine accepted
source/object/compiler/original/range/symbol/relocation records. The snapshot grew
from 2,232 to **2,241**, preserving every previous entry, translation unit and
source byte. Exact object agreement remains evidence for the pinned build, not a
proof of game behavior or of unknown ABI semantics. There were no provider calls,
new machinery reviews or worker calls; zero provider calls still cost engineering,
compiler and publication time. Paid production remains paused.

Private reproducibility inputs, exclusions, cache and receipts are retained under
`local/memory-ast-scale-001/`: `prepare.py` freezes `plan.json`, `run.py` resumes it
without replaying recorded attempts, and `final_audit.py` regenerates proposals
and rechecks current bindings before `tools/export_ast_matches.py` consumes
`accepted-exact-input.json`. Both this round's unknown RVA `0040e2e0` and the prior
unknown `00530cc0` remain retained, with no match or compile-failure credit.

Local post-integration validation on macOS ARM64 passed 296 standard tests
(33 skips), 187 object-tool tests, the CMake build, six C++ checks and both
synthetic demos (59 positive; 53 passing plus six expected negative mismatches).
The generic transformation and its tests were unchanged from the approved pilot.


### Stack-cleanup diagnosis: bounded negative result

The next round examined the frozen census's 3,658 unpublished stack-cleanup
primary labels. These labels identify instruction differences, not their causes.
A deterministic 33-case sample covered body-size and instruction-shape strata.
The most repeated exact stack-instruction pattern (117 cases) had source locals
reading their own uninitialized high bytes before clearing the low byte. Those
unknown inputs were left unresolved. A second pattern (95 cases) saved ECX and
cleared its low byte locally; every source expressed a receiver-derived integer
mask. Two generated byte-store variants at one representative function both
compiled but remained nonmatches: VC8 emitted an extra initialization store and
other register choices. Their compared bodies were identical, so this approach
was stopped rather than expanded.

The fallback screened all 10,738 currently unpublished retained nonmatches for
short, straight-line leaf callees. It required complete original decoding, a
terminal return cleanup, every consumed stack word observed as a 32-bit read,
and no unknown entry register inputs, nested calls, branches, stack mutation or
segment dependence. Nine callers reached this narrow evidence screen. Three
large callers were excluded from the small pilot and one pointer argument was
outside its integer-word AST precondition. The five eligible callers covered
372 original body bytes. The proposed AST edit retained argument expressions and
the unsigned return hypothesis while replacing an unknown variadic cdecl
external declaration with a fixed-word callee-cleanup hypothesis. RET cleanup
alone was never treated as evidence for thiscall or a unique formal signature.

All five variants compiled, but none passed the unchanged complete relocation-
aware comparator. The targeted cleanup difference disappeared in several cases;
other declaration, register, control-flow and return-cleanup differences remained.
One reduced candidate differed only at its own `ret 4`; the unused formal input
needed to justify that cleanup remains unknown, so no parameter was invented.
Ten unchanged exact controls reused their objects and passed fresh comparisons.
There were seven compiler attempts total, including the two failed smoke variants
at one function; six distinct functions were compiled. The pilot took 7.289 seconds
with 0.00025 seconds waiting for the existing VM lock. There were no new transport
unknowns, no provider calls and no source promotions. Earlier transport unknowns
were preserved without replay.

The generic prototype and 25 focused regressions remain private: zero exact-match
yield does not justify public adoption or a broader sweep. Full local tooling
checks passed 296 standard tests (33 skips) and 187 object-tool tests on macOS
ARM64. The same target-aware Apple Clang 21 / MS compatibility 14 settings and
VC8 x86 14.00.50727.762 compiler/flags were used as in the preceding checkpoints.
Zero provider calls still consumed prepaid engineering, review and compiler time.
This evidence establishes neither game behavior nor unknown ABI semantics.

Private diagnosis, source corroboration, frozen plan, all compiler products,
regeneration, independent review and receipts are under
`local/stack-abi-match-001/`. `diagnose.py` and `leaf_census.py` reproduce selection;
`prepare.py`, `run.py` and `final_audit.py` bind proposals and reuse recorded
attempts without recompiling them. The existing AST exporter accepted no rows,
and its in-memory snapshot extension preserved all **2,241** published entries,
translation units and source bytes. No acceptance rule or shared helper changed.


### Signed threshold spelling: a small positive result

A deterministic sample of 25 body-size/instruction-shape strata from 1,985
unpublished branch-primary cases was decoded and completely parsed with the
existing target-aware Clang path. Branch mnemonics alone did not identify errors:
reversed CMP operands and inverse branches can describe corresponding decisions,
and layout/call/return differences were often mixed into the same label. Three
retained pairs were also lifted through pinned SharpRetro: one reported differing
supported IL, while two remained opaque/unsupported. These diagnostics supplied
no semantic equivalence or acceptance credit.

A grounded spelling family compared a signed integer to negative one while the
original tested its sign at zero. For an already promoted signed 32-bit integer,
`-1 < x` and `x > -1` select the same values as `x >= 0`; `x <= -1` and
`-1 >= x` select the same values as `x < 0`. The generic AST helper preserves the
existing operand expression once, its type and surrounding evaluation order;
it adds no arithmetic, contract or dependency declaration. It refuses unsigned,
floating-point and wide comparisons, calls, assignments, increments, volatile
operands, macros, overlapping sites and incomplete decode. It requires original
TEST/CMP-zero plus signed-branch evidence, but that evidence is a selection guard,
not proof of source-to-instruction correspondence or whole-function behavior.
All outputs stay unvalidated until the complete unchanged comparator succeeds.

Text screening found 96 candidates; ten exceeded 256 original bytes, 22 lacked
the required original sign-test evidence, and one failed the AST preconditions.
The remaining 63 were eligible; a deterministic plan capped selection at 40 with
23 initially unselected. One variant per function was permitted. An eight-target
size-stratified smoke yielded one exact match (23 bytes) and seven nonmatches.
The wider profile stopped there. A further instruction-shape screen of the same
frozen 40 found only three threshold-only cases, including the already measured
match. Both remaining cases compiled to complete matches. Thirty planned targets
with other differences stayed unrun; there was no padding to the suggested
20–40 target quota and no claim that all eligible cases were exhausted.

Across the actual ten targets / 873 original body bytes, ten new VC8 attempts
compiled: **three new distinct exact functions / 100 body bytes**, seven retained
nonmatches and zero new unknowns. Ten unchanged exact controls reused their
objects and passed fresh comparisons. Smoke took 11.679 seconds and follow-up
3.706 seconds; compiler receipts totalled 14.443 seconds and combined VM-lock
wait was 0.00045 seconds. The existing VC8 x86 14.00.50727.762 flags under Windows
11 ARM64 translation and target-aware Apple Clang 21 / MS compatibility 14 settings
were unchanged. No game code executed. Zero provider calls still consumed prepaid
engineering, one independent review, compiler and publication time.

The exact generic helper and its 25 focused regressions received one independent
review together with all three source/export bindings. The existing reviewed AST
bridge and source exporter freshly checked full source/object/compiler/original/
range/symbol/relocation bindings, extending the snapshot from 2,241 to **2,244**
while preserving every prior entry, translation unit and source byte. Private
inputs, selection, all nonmatches, original compiler products and receipts remain
under `local/branch-ast-match-001/`. No transport unknown was replayed, and no
provider queue or wider sweep was restarted.

Run the generic tests with `python -m unittest rapid_object.tests.test_branch_zero_fix -v`.
The reusable API is `rapid_object.branch_zero_fix.rewrite(source, complete_ast, bound_report)`;
use `rapid_object.ast_match.parse` for the target-aware AST and the existing build,
cache and full comparator path for evaluation. Private `prepare.py` freezes the
plan; `run.py --measured-only --chunk-size 20` reuses completed records, and
`final_audit.py` regenerates candidates and freshly rechecks current bindings.

Post-integration checks passed 296 standard tests (33 skips), 212 object-tool
tests including the 25 new regressions, the macOS ARM64 CMake build, six C++
checks and both synthetic demo paths (59 positive; 53 passing plus six expected
negative mismatches). These tooling results are separate from the three VC8
whole-function matches and do not constitute game execution.


### Fixed stack cohort: separate a cookie argument from its frame

The next checkpoint froze all **6,487** stack-cleanup primary nonmatches from the
current deduplicated status snapshot. This is a fixed cohort, not a union of
successful repair passes. The labels are instruction symptoms: 5,347 cases mix
several stack differences. Overlapping facts include 4,716 adjacent post-call
cleanup differences, 2,438 own-return cleanup differences, 2,627 pre-call stack
adjustment differences, 5,796 push/pop differences and 1,113 partial-width stack
accesses. A pre-call adjustment does not by itself identify local allocation,
and RET cleanup does not identify thiscall or a complete signature.

Source subdivision found 2,819 explicit FS exception-frame hypotheses, 2,285
entry-stack cookie expressions and 2,143 sources passing that cookie to a call.
These sets overlap. The largest repeated exact stack signature (395 bodies)
also combines frame, receiver and call hypotheses, and fails the straight-line
first-call screen. The previous 117 unknown-high-byte mask family and five
zero-yield leaf-cleanup proposals were preserved, not replayed.

The reusable [cookie-call proposal](../rapid_object/cookie_call_fix.py) targets
one narrow subgroup. The original must store its cookie before FS installation,
then push contiguous argument words for its first direct call and perform
balanced caller cleanup. The complete callee must be a one-word forwarding
wrapper with an explicit `[ESP+4]` read, a constant-plus-word nested call and a
plain return. This is observed dataflow, not a guessed formal signature or
transitive callee semantics. Complete target-aware Clang ASTs bind an actual
32-bit unsigned local, its single cookie assignment/global identity, and the final
pure cookie argument in an ordinary top-level call or assignment. Macro,
unevaluated/introspection, nested/conditional-call, unknown-storage and extra-use
cases refuse. The only source edit removes that final argument; all other
argument expressions, memory statements, returns and frame code are retained.
Candidates remain hypotheses until the complete unchanged comparator accepts.

Of 2,143 source hypotheses, 714 passed the caller screen; 697 also passed the
complete callee screen; 670 passed complete source parsing/binding. The 27 AST
refusals were eight mutation/missing-assignment cases, fourteen definition
identity cases and five additional cookie uses. Seventeen other callees were
unsupported. All 670 eligible identities were measured once: a 24-target pilot
followed by the reviewed unchanged-rule 646-target sweep. Eight unchanged exact
controls reused their objects and passed fresh comparisons. No prior completed
or transport-unknown source attempt was replayed. Later unknown variant outcomes
never erase the earlier usable compiled baseline.

Across **670 target attempts / 71,619 original body bytes**,
656 compiled and 14 retained inconclusive build/transport outcomes.
The unchanged full comparator found **0 new distinct exact functions /
0 body bytes**. The targeted first-call explicit cleanup now agrees with the
original within the strict two-instruction diagnostic window in **652** compiled
targets. Four others schedule MOV/XOR before the same literal `ADD ESP,4`
(original and corrected amount4, versus baseline8), so all 656 compiled targets
show the corrected amount; register/flag and scheduling differences remain. In 242 cases the heuristic stack label
is absent afterward; this is diagnostic label churn, not additional recovered
functions. Residual frame, register, memory, receiver/call and control-flow
hypotheses remain. In particular, removing an excess call argument does not
reconstruct the original native SEH/unwinding frame. Unknown outcomes and all
nonmatching C++ remain private and unvalidated.

The pilot took 36.052 seconds; the full sweep took 947.395
seconds with 0.0427 seconds waiting for the existing
VM lock. Target receipts total 900.940 seconds
of build/transport time; this is not compiler CPU time. Range sizes follow the
pinned inventory boundary hypotheses, not unique game-code coverage. VC8 x86 14.00.50727.762
under Windows 11 ARM64 translation, existing flags, and target-aware Apple Clang 21
/MS compatibility 14 were unchanged. Zero provider calls still consumed prepaid
engineering, one independent review, compilation and publication time. These
observations are not game execution or a semantic-equivalence proof.

One independent review approved the exact generic helper/tests and the fixed
646-target plan, scoped to this pinned DAO image/naming convention and the
existing POSIX workflow. The helper assumes image base `0x400000` and inherits
the existing AST tool's host requirements; it is not yet a cross-game or
Windows-hosted reader. Final checks freshly rebound source/object/compiler/
original/callee/relocation evidence. The existing exporter verified
0 new rows and preserved all 2,244 prior published entries,
translation units and source bytes. Private cohort partitions, refusals,
selection hashes, all attempts and reproduction artifacts remain under
`local/stack-cohort-001/`. Both parked helper files remain unpublished.

The API is `rapid_object.cookie_call_fix.rewrite(source, complete_ast,
bound_report, actual_callee_captures)`; it only proposes C++ and provenance.
Freshly bind captures to the pinned original before invoking it, then use the
existing build/cache/comparator/export gates. Generic regressions run with
`python -m unittest rapid_object.tests.test_cookie_call_fix -v`.
Local checks passed 29 focused tests, 296 standard tests (33 skips), 241 object-
tool tests, a macOS ARM64 CMake build and six C++ checks; both synthetic demos
returned 59 positive passes and 53 passes plus six expected negative mismatches.
Synthetic results remain separate from complete native-function comparisons.


### Fixed stack cohort: compose an observed allocator-result receiver

The next subgroup kept the same **6,487** identities and started from retained
cookie-corrected C++, without rebuilding those baselines. The two constructor
leads cover 509 callers: 500 have compiled corrected inputs and nine retain
transport-unknown variants, which were excluded from replay. The complete
observed constructor bodies read ECX, store a word through that receiver,
increment a global counter and return; one removes four stack bytes, the other
removes none. Neither reads EDX, calls another function or reads an explicit
stack argument. RET4 alone was not used to infer thiscall, and the unread
existing word argument was preserved rather than replaced with a guessed value.

The [allocator receiver proposal](../rapid_object/allocator_receiver_fix.py)
binds an actual own pointer local assigned the allocator result, a simple
nonnull guard and the first ordinary constructor call in that guarded block.
Complete target-aware AST IDs/spans establish source storage and declaration
identity. Existing signed/unsigned word argument expressions and types remain
unchanged. Macro, nested/unevaluated call, early receiver escape/mutation,
pre-call parameter mutation, unsupported storage and extra-call cases refuse.
The source edit adds that actual pointer expression as the ECX receiver through
an explicit thiscall function-pointer hypothesis. It does not create a class,
assume object lifetime semantics, stub a call or alter memory/return/frame code.

Original instruction evidence separately checks the whole bounded CFG, actual
allocator argument setup, EAX return provenance, null predicate and every path
reaching the constructor. The receiver must be that return value in ECX; the
RET4 case must preserve the observed entry-ECX word as its stack argument.
Complete callee ranges and symbol identities are bound to the pinned original.
Suffix instructions are decoded and visited structurally but their data effects
remain unmodeled and are not rewritten. One independent review found a real
guard defect: LOOP in the suffix could be mistaken for fallthrough. The fixed
rule rejects unrecognized generic control transfers, including LOOP/interrupts;
the failing synthetic counterexample and original freeze were retained, and all
500 candidate sources regenerated unchanged without compiler replay. This was a
provenance/refusal defect, not a demonstrated comparator false acceptance.

All **500** compiled inputs passed the rule's explicit eligibility checks. A
stratified 24-target pilot was followed by the reviewed ascending 476-target
plan, one new variant per identity. Across **500 attempts /
51,233 original body bytes (inventory range hypotheses)**, 494 compiled and
6 new outcomes remain inconclusive. Eight unchanged exact controls
reused objects and passed fresh comparisons. The complete unchanged comparator
found **0 new exact functions / 0 matched body bytes**. The allocator-result ECX
setup passed the same provenance check in zero compiled baselines and all 494
compiled candidates. This is a targeted symptom result, not function recovery.
Residual primary categories were 373 stack cleanup and 121 instruction selection,
with six inconclusive outcomes.
The same 121 compiled baselines and candidates lack the heuristic stack label;
no primary category or stack-label presence changed in this receiver round.
Receiver dataflow improvement receives no function acceptance credit. All 6,487
full functions remain unresolved, and prior unknowns and failed C++ stay private and unvalidated.

The next shared residual is grounded more narrowly than the stack label:
all 500 originals push the source-associated handler address and share a
handler prefix with a cookie check, descriptor load and jump to one common
target; all observed descriptors start with `0x19930522`. The corrected sources
still contain explicit FS-frame hypotheses. These observations prioritize
native compiler exception/unwind-frame reconstruction on the composed inputs.
They do not yet establish a safe C++ type, unwinding or allocation-failure
contract. Unknown input/pointer semantics remain unknown.

Target build/transport receipts total 676.710
seconds, not compiler CPU time. The 476-case sweep took
705.270 seconds, including 0.0261
seconds waiting for the existing VM lock. The final pilot invocation took
31.388 seconds after the first two smoke cases were retained.
VC8 x86 14.00.50727.762 under Windows11 ARM64 translation and Apple Clang21.0.0
with i686/MS compatibility14 parsing were unchanged. Zero production inference
calls still consumed prepaid engineering, one separately accounted independent
review, builds and publication/CI time. These are static compiler observations, not game execution
or semantic-equivalence proof.

The exact generic helper/tests were independently approved for this pinned DAO
image base/naming family and existing POSIX workflow, not arbitrary games or a
Windows-hosted Python reader. Fresh final checks rebound source, objects,
compiler, original ranges, symbols and relocations. The existing exporter
verified zero rows and preserved all 2,244 entries, translation units and source
bytes. A future exact chained candidate still needs truthful lineage accepted
by the existing exporter; the current chain is not automatically that bridge's
expected provenance shape, so no invented receipt or permissive adapter was
added. Private plans, every attempt, refused controls, original/corrected review
freezes and reproduction evidence remain in `local/allocator-receiver-001/`.
Both parked helper files remain unpublished.

Validation passed 35 focused tests, 296 standard tests (33 skips), 276 object-
tool tests, the macOS ARM64 CMake build and seven CTest entries. Synthetic demos
returned 59 positive passes and 53 passes plus six expected negative mismatches;
these stay separate from complete native-function comparisons.

### Generated exception identities and bounded graph diagnostics

On 2026-10-19, retained VC8 x86 objects exposed an overly broad symbol-name rule:
an embedded `fn_RVA` in a generated EH symbol inherited the parent address.
A shared anchored binder now separates source names from generated handlers,
FuncInfo descriptors, unwind maps and funclets. Both build and export consume
the same helper. The existing comparator already refused the defined generated
targets, so this was not evidence of a prior false acceptance.

Two retained real objects were replayed, without compilation: eight accidental
aliases disappeared, both comparisons remained inconclusive, and eight existing
exact controls remained exact. The graph diagnostic follows actual original
references and candidate relocations through supported complete handler,
36-byte FuncInfo, 8-byte single-state map and cleanup-action spans. Those earlier
objects still differ in main size, cookie handling and cleanup form; runtime
identity, helper boundaries and parent-frame/state relationships remain explicit
unknowns. No placement map or acceptance result is generated.

One independent review found a real diagnostic bug: a global comparator refusal
returned no function rows, causing an uncaught iterator error. The narrow fix
retains the original refusal and marks the diagnostic incomplete; missing rows
also fail explicitly. The two real invalid-input counterexamples and generic
missing-row regression are retained. The corrected five-file proposal passed
38 focused regressions, a 334-test integration overlay (33 skips), and independent
retained-object/control replay. Review approved only the exact tooling change.

No new exact functions, matched body bytes, VM compiler builds or production
provider calls were claimed for this tooling round. Published source remains
2,244 functions. Engineering/review time still costs Codex usage. Private source,
object/compiler/original bindings, old failure, replacement freeze and review
remain under `local/eh-graph-binding-001/`,
`local/eh-graph-binding-reviewfix-002/` and `local/eh-graph-review-001/`.
See the diagnostic API and regression command in
[mismatch analysis](mismatch-analysis.md#inspect-compiler-generated-exception-dependencies).

### Construction failure cleanup: native spelling removes guard overhead

The next private experiment used compiler-visible construction and allocation
failure cleanup instead of a conditional RAII guard. Four VC8 invocations
produced three generic objects and one preserved transport-255 unknown; it was
not retried. Eight new real variants across six identities all compiled. Each
had the original complete main length (92 or 97 bytes), mnemonic/width sequence,
27-byte checked handler and 11-byte unconditional failure action. Each main
still had five raw differences carrying unresolved relocations. All eight
unchanged complete comparisons remained **inconclusive**, not exact.

Six variants introduced an extra delete-forwarding jump. Two further variants
forwarded to the independently observed destination of the original cleanup
jump, retaining unknown target semantics. They still need full graph identity
and byte comparison. Placement construction instead added storage and cleanup
arguments. Compiler `/GS` restored the checked handler; `/EHsc` behavior also
depended on actual C/C++ linkage and nothrow declarations in generic probes.
These findings are tied to VC8-SP1 14.00.50727.762, running as x86 under Windows
11 ARM64 translation, not to native x86 execution of the game.

The private generator passed 18 focused tests and 296 project tests (33 skips).
It retains four-byte layout/type hypotheses and is not ready for rollout:
separate objects reuse a wrapper name with different bodies, and global
allocation/deallocation definitions need a consistent link-safe strategy.
Complete EH graph/runtime bindings also remain unresolved. Preserve all eight
sources and objects in `local/eh-construction-lowering-003/`; do not rerun its
consumed build scripts. No candidate was published and no match count changed.


### Complete EH graph byte accounting retains the extra jump

A diagnostic comparison now accounts for every supported main/handler/metadata/
action/delete-helper byte and relocation. Replaying eight retained construction
variants found four different delete-helper bytes in each of six original-entry
forwarders. Two tail-destination forwarders had 167 or 172 resolved equal bytes
and twelve unresolved bytes each, covering all 179 or 184 captured graph bytes.
The unresolved fields are the cookie global and two runtime references. Original
inventory boundaries and runtime identities also remain unresolved. These are
conditional byte observations, with zero complete matches or body credit.

Independent review exposed a real diagnostic error: resolving by symbol name
could confuse two different COFF definitions. The narrow repair retains actual
relocation target indexes and marks an unpaired defined destination incomplete.
The old freeze and exact counterexample remain retained. The independently
approved replacement passes 23 focused regressions, including wrong targets,
map/state/frame changes, missing/extra actions, helper boundaries and byte
coverage. Eight cached exact controls remain exact; unsupported placement cleanup
remains incomplete. Local checks passed 357 project tests (33 skips) and 276 rapid-object tests
on macOS ARM64; the exact-head CI result is retained separately.

No new compiler attempts, production inference, constructor-source adoption or
change to the published 2,244-function count occurred. A read-only inventory
query found no configured VC8-SP1 lib directory; matching CRT/cookie artifacts
and complete original boundaries remain concrete evidence needs. No runtime
implementation was invented or downloaded. The constructor generator's existing
link-safety limitations remain unchanged. Private bindings, old NEEDS_FIX review,
replacement freeze, independent approval and replay reports remain under
`local/eh-graph-comparison-003/`.

### Unique constructor wrappers and complete native EH matches

A separately accounted linkage experiment replaced repeated global constructor
wrapper types and global allocation/deallocation overrides with deterministic
RVA-named types and class-specific forwarding. Its two generic and four new real
VC8-SP1 `/c /GS /EHsc` invocations all compiled, including one translation unit
containing the exact four candidate bodies. COFF retained four distinct class
delete helpers and no global new/delete definitions. The original allocation
size, actual RET0/RET4 arguments, allocation-null branch, vptr write, unconditional
exception cleanup and absence of normal-path cleanup remain reflected in the
compiled bytes. No link or game execution was performed. The four-byte nominal
class remains a source hypothesis. The old class-new transport-255 result and
all earlier failed spellings remain immutable.

Read-only discovery in the already-retained SDK archive found actual static CRT
COFF definitions. Unique original-span and shared relocation constraints identify
the roots and immediate support targets, followed by complete root byte comparisons.
This establishes bounded artifact identities, not original compiler provenance or
transitive runtime semantics. A new complete main/EH backend and source-export
bridge were reviewed together with the constructor generator by an independent
reviewer who authored neither implementation. The checker resolves every byte and
relocation across the full main, checked handler, FuncInfo, unwind map, action
and delete helper. Public diagnostics remain nonaccepting and the ordinary
comparator remains unchanged.

The integration consumed no new compiler or provider calls. Replaying 14 retained
objects preserved six original-entry forwarder nonmatches (four different helper
relocation bytes each) and one placement object's two inconclusive larger-action
bodies. Seven positive objects include duplicate observations: only **four unique
class-specific function identities** gain source credit. Their complete graphs
contain 179 bytes for each of two RET0 cases and 184 bytes for each of two RET4
cases, **726 bytes total**. Eight cached old exact controls remain exact. Fresh
export rechecks all inputs, rejects stale/forged/partial summaries and extends
**2,244 to 2,248** published functions while preserving every prior entry, unit
and source byte. Re-importing the combined object adds zero duplicate credit;
a combined-only preview has four functions and one translation unit. SDK runtime
objects and shared helpers add no recovered-function count.

Before adoption, the author and independent reviewer each passed 428 tests
(357 existing plus 71 new, 33 skips); 276 rapid-object tests also passed locally
on macOS ARM64. The earlier compiler runs used VC8-SP1 14.00.50727.762 under
Windows 11 ARM64 translation. Final adopted-code and exact-head CI receipts are
retained separately in ignored `local/eh-source-integration-001/`. Public metadata
contains artifact/provenance hashes, versions and graph measurements; raw original
and library bytes remain local. The historical 94-function emulator registry,
fixed 6,487 residual cohort and six new plus nine older transport unknowns are
unchanged. No larger constructor batch is launched by this checkpoint.

## Sequential median functions: native constructors and copy elision

The pinned inventory's 27,555 identities have an exact median body size of 109 bytes.
We worked three such functions sequentially: guarded allocation at RVA `0x7a90`,
its sibling `0xa1d0` to test reuse, then base construction with a by-value temporary
at `0x648f0`. No broad category sweep or paid provider call ran.

| RVA | Retained main comparison before | Generic result | Actual compiler variants |
| --- | --- | --- | ---: |
| `0x7a90` | 112 candidate bytes: 10 equal, 99 different, 3 extra | 109/109 main; 196/196 complete graph bytes | 3 |
| `0xa1d0` | 112 candidate bytes: 10 equal, 99 different, 3 extra | 109/109 main; 196/196 complete graph bytes | 2 |
| `0x648f0` | 77 candidate bytes: 2 equal, 75 different, 32 missing | 109/109 main; 193/193 complete graph bytes | 5 |

The before counts compare offsets across the full main ranges; the prior diagnostic
instruction edit distances were 34/38, 34/38 and 29/38. Neither measure accepts a
source. The final comparisons cover every supported main, handler, FuncInfo, unwind
map, action and terminal forwarding byte: 327 main bytes and 585 graph bytes total,
with zero different, absent or unresolved bytes. These are pinned compiler-artifact
matches, not a whole-game proof or a linked replacement.

The first hypothesis used a class constructor wrapper that called an unknown
thiscall and discarded its return. VC8 preserved an extra receiver, producing a
113-byte main. Declaring the native constructor externally on a class `fn_<RVA>`
produced the observed 109-byte caller. The generic
[`conditional_construction` rule](../rapid_object/conditional_construction.py)
checks the complete retained body, AST, bound hashes and original 35-instruction
profile; it derives the actual original cleanup/helper tail and emits class-specific
new/delete forwarding. It supplies no unknown constructor implementation. The sibling
passed through the same rule without RVA-specific source edits.

The third original caller reserves eight stack bytes, constructs directly there,
and calls a callee that cleans twelve argument bytes. The initial C++ type spelling
caused a copied temporary and a second EH state. An explicit copy-constructor
declaration permits VC8 copy elision; the
[`byvalue_construction` rule](../rapid_object/byvalue_construction.py) checks the
complete retained method and 38-instruction profile before emitting that hypothesis.
The base destructor wrapper forwards to the observed original tail destination.
No copy implementation is supplied, and emitted unknown dependencies cannot pass.
The native constructor identity recognizer supports only the observed public x86
thiscall signed-int decoration, retaining refusals for other special members and
namespace, import and generated names.

The native EH reader now selects complete eight- or eleven-byte supported action
spans and checks their actual lengths for overlap. The new eight-byte load-receiver
form retains its signed frame offset and complete terminal jump relocation. The
legacy `delete_helper` graph-node name also covers a base-destructor forwarding
node; that label is not evidence of deallocation semantics. The new constructor
identity module participates in the native EH implementation hash set.

Ten real VC8 14.00.50727.762 variants took 16.898 seconds in compiler receipts on
Windows 11 ARM64 under x86 translation; the per-target counts include failed probes
and final generic regenerations. This measures compiler latency, not model or total
analysis time. No original function execution occurred. Native callee semantics,
nominal C++ object layout/lifetime and a whole-game link remain outside these results.

The independently reviewed change passed 130 focused cases and all 461 project
tests on macOS ARM64, with 33 skips. Eighteen updated-receipt mutations across every
node of the three real COFFs all refused; independent review added action/frame/
relocation mutations, forged-summary checks, eight old object controls and four
prior EH controls. The first CTest invocation selected a system Python without the
project dependencies; the configured environment was then used for the required
checks. Windows source-parser tests explicitly skip before importing the existing
POSIX AST workflow; this readiness issue was caught during review. Portable native
graph checks continue on Windows. The fresh exporter preserves every previous
2,248 row, unit and source byte while adding these three sources, for 2,251 total.

Reproduction on the configured private installation: regenerate each selected
retained source with the two generic `propose` APIs and a complete Clang AST; compile
with the selected VC8 flags under the shared VM lock; run `tools/check_eh_native.py`
against the actual original, inventory, compiler and static library; extend the
current snapshot through `tools/export_native_sources.py` and fresh trusted inputs.
The ignored `local/median-function-001` checkpoint retains selection, all attempts,
exact source/object/original bindings, independent review and publication receipts.
That checkpoint selected `0x3cb70`, `0x44430` and `0x783b0` for the following
sequential experiment below.

### Sequential median functions: receivers, flag widths and a numeric plateau

The next three 109-byte functions were investigated in order. Two complete ordinary
object comparisons passed; the numeric parser remains unaccepted. Byte counts below
are complete offset comparisons, not an instruction-distance acceptance rule.

| RVA | Initial candidate / equal / different / missing / extra | Retained candidate / equal / different / missing / extra | Result |
| --- | --- | --- | --- |
| `0x3cb70` | 102 / 17 / 85 / 7 / 0 | 109 / 109 / 0 / 0 / 0 | Complete match |
| `0x44430` | 110 / 15 / 94 / 0 / 1 | 100 / 15 / 85 / 9 / 0 | Nonmatch |
| `0x783b0` | 88 / 10 / 78 / 21 / 0 | 109 / 109 / 0 / 0 / 0 | Complete match |

`copy_loop_receiver` restores three observed thiscall receivers in a bulk-copy
loop and spells the destination advance with unsigned 32-bit wrap. Its evidence
includes the complete caller profile and complete callee ranges, control flow and
return cleanup. `lookup_receiver_flags` restores three receivers and the observed
byte-width tests after shifts by 31, 29 and 30. An unknown nested call remains
unknown; forwarding an unchanged receiver establishes calling context only.
Both rules require the complete retained body, target-aware AST, pinned identities
and original/source/range bindings. They emit C++ calls, with no supplied unknown
callee implementations. Review caught partial ECX-register writes being overlooked
by the context evidence check; writes to ECX, CX, CL or CH now conservatively refuse.

`numeric_loop_spelling` widens the lookup digit and accumulator to unsigned 32-bit
values and moves the next-character lookup into the loop condition. This improves
correspondence of the pointer and radix registers but does not pass the full
comparison. VC8 derives radix ten with `lea esi,[edi+9]`, where the original loads
ten directly; the shorter candidate also lacks the original seven-byte alignment
instruction. Initialization order, a guarded initialization and a disabled global
optimizer were tested and retained as failed attempts. The lookup table's complete
layout and negative-index semantics remain unknown. No source was published for
this function, and its smaller candidate is not evidence of equivalence.

Fourteen actual VC8 14.00.50727.762 variants took 21.093 seconds in compiler receipts
(3, 8 and 3 variants respectively), on Windows 11 ARM64 through x86 translation,
controlled from macOS ARM64. The generic sources regenerate byte-identically from
the retained inputs. All 218 single-byte mutations of the two actual matched main
bodies refused under the unchanged comparator. No original execution or direct
paid provider calls occurred; author and independent-review assignments were
separately accounted Codex work. The ignored `local/median-function-002` checkpoint
preserves every attempt, the numeric blocker, source lineage and review history.
These function-level compiler comparisons do not establish a replacement game.

Independent review approved the corrected six-file freeze after all 514 project
tests (33 skips), three unchanged regenerations, 218 real-byte mutation refusals,
forged-report and partial-register controls, eight old object matches and 585 prior
EH graph bytes. The fresh export preserves all 2,251 previous entries, units and
source bytes and adds only the two complete matches, for 2,253 total. CMake and
CTest passed all seven checks on macOS ARM64 with the configured environment; the
synthetic positive control had 59 passes and the negative control had 53 passes
and six expected mismatches. These are synthetic results, not game execution.
The next retained sequential candidates are `0x78420`, `0x799e0` and `0x91960`;
their newest source/compiler evidence must be inspected before any new attempts.

### Sequential median functions: reuse and a bounded copy window

The next bounded round investigated `0x78420`, `0x799e0` and `0x91960` in order,
after inspecting all retained drafts and compiler reports. All three candidates
matched their entire 109-byte original ranges through the unchanged comparator.

| RVA | Initial candidate / equal / different / missing / extra | Final candidate / equal / different / missing / extra | Actual variants |
| --- | --- | --- | --- |
| `0x78420` | 88 / 10 / 78 / 21 / 0 | 109 / 109 / 0 / 0 / 0 | 1 |
| `0x799e0` | 88 / 10 / 78 / 21 / 0 | 109 / 109 / 0 / 0 / 0 | 1 |
| `0x91960` | 112 / 47 / 62 / 0 / 3 | 109 / 109 / 0 / 0 / 0 | 5 |

The two lookup callers reuse the previous receiver/byte-flag machinery. The type
comparison now accepts a positive short decimal or hexadecimal literal only when
the complete original profile has the same immediate. Values zero, above 127,
octal spellings, changed call context and mismatched original comparisons refuse.
The prior tag-five source still regenerates byte-identically; these two use four
and fourteen. The original/source marker is unique and bound to the current RVA.

The copy-window caller increments a position, chooses at most 4,096 bytes, checks
an optional source pointer and calls an external copy routine. Its formal callee
semantics and buffer/object extents remain unknown. `bounded_copy_window` requires
the complete retained body, target-aware AST, source/original/range hashes and full
39-instruction original profile before proposing C++. Unsigned 32-bit arithmetic
preserves field advancement, page multiplication, address addition and subtraction;
explicit conversions retain the selected compiler's signed interpretation.

The existing signed-threshold rule now recognizes a 32-bit register subtraction,
one fullword register copy of its result, then JS/JNS. MOV preserves the flags;
JL/JGE are deliberately excluded because signed subtraction overflow changes
SF xor OF. Replacing the minus-one comparison alone produced 109 bytes but changed
saved-register assignments. Declaration order made no difference. An explicit
early negative return followed by the optional-copy block recovered the original
allocation and complete bytes. A signed-count experiment failed and is retained.
The final source regenerates from the generic rule without another compiler run.

Seven actual VC8 14.00.50727.762 variants took 10.621 seconds in compiler receipts
on Windows 11 ARM64 under x86 translation, controlled from macOS ARM64. All 327
single-byte mutations of the three real matched objects refused, as did nine
real-source marker/tag/null-path precondition mutations. The ignored
`local/median-function-003` checkpoint binds every source, object, original range,
compiler attempt and review. No original game execution or direct paid provider
calls occurred; author and independent reviewer are separately accounted Codex
assignments. These complete compiler comparisons do not prove a whole game or
supply missing callee semantics.

On macOS ARM64 the final local suite passed 528 tests with 33 skips, the 64 focused
source/sign controls passed, and CMake/CTest passed all seven checks with the
configured environment. Synthetic controls produced 59 passes, then 53 passes and
six expected mismatches; these are infrastructure checks rather than game proof.

Independent review approved the exact six-file freeze after reproducing all three
full matches, freshly checking all seven attempts (three exact and four nonmatches),
and preserving eight prior object controls and 585 prior EH graph bytes. The fresh
export preserves all 2,253 old entries, units and source bytes and adds these three,
for 2,256 total. The next retained median candidates are `0xb63f0`, `0xc57a0` and
`0xe6f50`; no additional round was started or authorized by this checkpoint.

### Sequential median functions: list receivers and a callback-array plateau

The next bounded round inspected `0xb63f0`, `0xc57a0` and `0xe6f50` in order.
Two complete 109-byte function comparisons passed; the callback-array caller is
retained as a nonmatch. Counts below compare the entire original and relocated
candidate ranges at their offsets, and grant no partial-match credit.

| RVA | Initial candidate / equal / different / missing / extra | Retained candidate / equal / different / missing / extra | Variants |
| --- | --- | --- | --- |
| `0xb63f0` | 108 / 50 / 58 / 1 / 0 | 109 / 109 / 0 / 0 / 0 | 1 |
| `0xc57a0` | 108 / 47 / 61 / 1 / 0 | 105 / 48 / 57 / 4 / 0 | 7 |
| `0xe6f50` | 114 / 19 / 90 / 0 / 5 | 109 / 109 / 0 / 0 / 0 | 2 |

`copy_chain_receivers` restores three direct receiver contexts and a virtual
receiver during a field copy and list traversal. `checked_list_receivers` restores
two direct contexts and a virtual receiver loaded once, matching the original
single field load before its null check. All three calls to the original error
helper remain present. Its behavior is unknown; it is not declared noreturn or
replaced by a successful value. Address additions use unsigned32 arithmetic.
Both rules require complete retained bodies, target-aware ASTs, pinned source/
original/range/inventory hashes and complete original instruction profiles.

The shared context reporter retains its strict default refusal for indirect calls.
An explicit option can record an unknown 32-bit register/memory call after prior
observed receiver context, while still checking the complete recorded normal CFG
and return cleanup instructions. Targets, effects and nonlocal/exception outcomes
remain unknown; this is instruction evidence, not a semantic callee contract.
An indirect call alone cannot establish receiver context. Partial ECX-register
clobbers, wrong cleanup and incomplete control flow continue to refuse.

`callback_array_spelling` preserves a useful unaccepted hypothesis. The caller's
two pushes and lack of a matching stack adjustment suggest a callee-cleaned callback
spelling, while the reviewed unsigned ordered-zero rule restores its JBE. The
actual callback implementation and semantics remain unknown. The 105-byte output
still assigns the saved registers differently and hoists an address calculation
before the bounds branch. An implicit receiver hypothesis worsened it; inline,
typed and reference helper forms did not improve it. Comparison orientation changed
the branch spelling but did not pass. The retained variant has unsigned32 address/
subtraction wrap and the selected VC8 signed reinterpretation/arithmetic shift.
No artificial optimizer barrier or instruction emission was used to force a match.

Ten real VC8 14.00.50727.762 variants took 14.176 seconds in compiler receipts on
Windows 11 ARM64 under x86 translation, controlled from macOS ARM64. All three
sources regenerate byte-identically, and all 218 single-byte mutations of the two
matched objects refuse. Nine actual marker/external-identity mutations refuse.
Local checks passed 570 project tests (33 skips), 65 focused tests, CTest 7/7 and
both synthetic controls (59 passes; then 53 passes/six expected mismatches).
No original execution or direct paid provider calls occurred; Codex author/review
work remains separately accounted. The ignored `local/median-function-004` scope
preserves every attempt, full source/object bindings and the precise plateau.

Independent review approved the exact six-file freeze, reproduced all ten attempts,
and retained the callback-array candidate as a nonmatch. Extra unknown-call/context,
forged-report and misreported-nonmatch controls refused. Eight prior ordinary
controls and 585 prior EH graph bytes remained intact. The fresh exporter preserves
all 2,256 old entries, units and source bytes and adds only the two complete matches,
for 2,258 total. A separately authorized conditional round may inspect the retained
next candidates `0x106e40`, `0x171ac0` and `0x1dfb00` only after this checkpoint's
publication, exact-head CI and settlement complete.

## 2026-10-20 — First C# MCP slice over retained artifacts

The [implemented MCP tools](decompilation-mcp-usage.md) separate agent transport
from project indexing and durable checking. C#/.NET 10 hosts the official MCP SDK
2.2.0; a narrow Python adapter reuses the existing object/EH comparators. No
comparator port, per-function authored artifact or model call was needed to add
inventory browsing, source inspection, metadata-based related search and fresh
comparison of retained compiler products. New compilation, AST rewriting and
publication remain deferred.

The macOS ARM64 stdio pilot enumerated all 27,555 inventory identities and 2,258
historically published functions. Fresh checks reproduced one 109-byte ordinary
match, one nonmatch (105 candidate bytes against 109 original bytes, not a
similarity score), and one supported EH graph accounting for all 179 bytes across
six nodes. These are artifact checks, not new matches or game execution. The
actual original/compiler/library inputs were read; receipts do not attest the
complete compiler installation closure.

Eight real-input stdio tests passed in 7.392 seconds. The portable run passed six
and skipped two private-input tests in 1.947 seconds. The dependency-equipped
repository suite ran 604 tests with 33 skips in 60.633 seconds; an initial system
Python run failed on missing dependencies and remains recorded locally. Copied
source/object tampering, missing objects, changed flags/compiler receipts and
incomplete EH coverage could not yield full matches. Idempotency, concurrent
clients, reconnects and interrupted workers have generic controls. SDK10.0.101,
NuGet lockfile and exact source hashes are retained with the private pilot.

A real Codex discovery probe found all seven tools without a model turn or an
application restart. A separate fresh app-server process could not call a tool
on the already-open chat because it did not own that chat; direct stdio calls
established tool behavior instead. Zero direct provider, compiler or game calls
in this slice does not mean zero Codex author/reviewer development cost.

Independent review caught one inventory/revision drift bug in that first slice:
a project opened on one inventory could submit a check using later inventory
bytes. A generic test reproduced it, then verified rejection before job creation
and import under a new revision after restarting. The repair passed nine real
stdio tests, seven portable tests with two skips, and 618 repository tests with
33 skips. An independent read-only delta approved the exact correction. Codex
then discovered all seven tools from its saved registration of a versioned local
build. Opening a server connection and discovering tools are separate from an
existing chat gaining that connection; the running app was not restarted.

The first Windows CI run exposed a portable-test cleanup mistake: Python's
`sqlite3.Connection` context manager manages transactions but does not close the
connection. Four test-owned connections kept temporary database handles alive,
so Windows refused file removal after the assertions. Explicit `closing(...)`
now surrounds those transaction contexts. No assertions, server behavior or
comparison rules changed; the failed CI run remains part of the experiment.

## 2026-10-20 — Portable pipeline boundaries and full MCP coverage

Design decision, not a new recovery or runtime result: separate generic x86
effects and source manipulation from compiler-specific ABI/runtime interpretation,
build recipes and matching rules. Frontend syntax conversion remains a versioned
adapter, and DAO-specific identities/paths remain project data. A rule discovered
under VC8 is not automatically a generic x86 rule. Its demonstrated compiler and
option scope must be recorded before reuse.

The [MCP roadmap](decompilation-mcp.md#mcp-covers-the-complete-workflow) now covers
initial decompilation, deterministic pattern iteration, model source submissions,
fine-grained names/types/comments, compiler checks, source export and later linked
execution milestones. All use the same engine operations, source revisions and
durable jobs. The next implementation slice is a complete draft-to-check path,
followed by corpus propagation and transactional source refactoring.

Pipeline enhancements should be trialed as versioned JSON stacks of typed AST
edits and registered rules. Experiments branch from a fixed baseline, account
for every inventory identity, reuse only unchanged bound stages, and report gains,
regressions, inconclusive outcomes and pending work before any explicit promotion.
This is a reusable experiment description, not an extra per-function artifact.
The recipe interpreter and trial operations are still proposed capabilities.

This update changes documentation only: no new tools, compiler attempts, provider
calls, matches or execution claims. Existing read/check capabilities and reviewed
in-progress recovery artifacts are unchanged. Portability remains to be measured
against further real compiler profiles; this architecture alone does not prove it.

The follow-on direction is binary-backed replayable decompilation: keep analysis
decisions, entity names/types and transformation history as durable project state,
and regenerate C++ from it. Inspection of the pinned SharpRetro `LiftIl/Il.cs`
and `XFusionCpu/X86Lifter.cs` confirms typed per-instruction effects, not the
structured C++ recovery required by this proposal. A shared recovered IR and
compiler hooks during both reconstruction and emission are planned. Variable
names need origin/definition-use lineage; regenerated temporary numbers cannot
serve as persistent identities, and ambiguous rebinding must remain unresolved.

The proposed first experiment uses one supported median-sized function, retains
the existing Ghidra baseline, checks emitted C++ through the independent original
comparison, and tests name preservation across regeneration before wider rollout.
No SharpRetro writer, new lift semantics or regeneration mechanism was implemented
by this design update. Independent validation remains necessary when a lifter is
used to generate code; comparing its own output alone can hide shared defects.

## 2026-10-20 — New branch and a linear binary-first frontier

The user selected the replayable SharpRetro approach as active development.
The previous committed workflow is preserved as `codex/ghidra-mainline` at
`2b95feb309ff1a6f783e7508b7f4f91f798f69f8`; a separate worktree on
`codex/replayable-decompilation` starts from that history. Old uncommitted tooling
and interrupted experiment records remain intact, with an additional ignored
archive. The old 2,258 published functions are retained as historical evidence.

Recovery now starts at the earliest original inventory RVA (`0x1000`) and
advances only over consecutively accepted functions. The next entries are
`0x1030`, `0x1040`, `0x1070` and `0x10c0`. No size/ease filter chooses the
discovery examples. Rules still undergo applicability and regression checks
across the entire inventory; matches ahead of the frontier are counted separately.

The first function already produced a general lifter counterexample: the pinned
Bits32 near-CALL effects model an eight-byte return-address push, while its
surrounding PUSH/POP/RET use four-byte entries. This is an instruction-semantics
dependency to repair with generic tests and independent evidence. It must not
be hidden by dropping the faulty effects when generating C++. The branch/bootstrap
decision itself adds no new matching functions or game-execution evidence.
## 2026-10-20: First replayable original-to-object pilot

The new ascending-RVA pipeline reconstructed the first inventory function,
`0x1000`, from actual SharpRetro typed effects, generated C++, and obtained a
complete 22/22-byte object match with the selected VC8 compiler. This used one
actual compiler invocation in the Windows 11 ARM64 VM under x86 translation and
zero provider calls. It did not read an old recovered body or execute the game.
Independent review reproduced the generated source and complete comparison.
Source publication and a runnable replacement remain separate milestones.

The first function exposed real shared lifter defects. Correcting near-CALL
widths exposed related stack-segment/return behavior; independent review then
found 32-bit return-target truncation in 16-bit code. The final bounded repair
passed 329 XFusion and 14 Jit tests and was pushed directly to SharpRetro main as
`ce590d0a2f2a7e231e0529e30f2fd0d4252ca769`. Independent reference probes agreed
57/61, with four documented Intel64-prefix differences retained rather than
counted as passes. The older failing freezes and review remain available locally.

Next in order, `0x1030` exposes an unconditional tail jump. The runner leaves it
unresolved instead of choosing an easier function. The next rule should recover
tail calls generically, preserving their target and effects, then let the compiler
profile emit them. This is the intended feedback loop: each function identifies
a missing general behavior, rather than accumulating a hand-written answer.

Independent review also found an operational issue: a changed pipeline key
could bypass an earlier unknown compiler outcome. The corrected queue checks
unfinished operations across the entire project before selecting work, while
keeping cache validity specific to exact inputs. Fifteen focused tests and the
24-test MCP suite (two private-input skips) passed; the full tooling suite ran
585 tests with 33 skips on macOS ARM64. Installing an unchanged runtime at a new
path still changes its execution bindings and requires a fresh first-function
check. Prior results remain historical rather than receiving migrated credit.

## 2026-10-20: Tail-call recovery and an applicability boundary

The next function in address order, `0x1030`, motivated a general terminal
external tail-call effect and a VC8 emission profile. Two actual VM compilations
produced a 22/22-byte match for the existing `0x1000` control and an 11/11-byte
match for `0x1030`, taking 2.872 compiler seconds combined. This is one unique
matching gain in the development pipeline, with no provider calls. The original
game was not executed; development and review still consume Codex resources.

An applicability scan accounted for all 27,555 inventory identities. Of 845
linear direct-terminal-jump shapes checked through actual typed lifting, 208
generated C++ hypotheses and 637 remained unsupported. The baseline frontend
refused all 208 generated hypotheses. At this initial scan, only the frontier tail-call example had
been compiled and compared: 207 additional hypotheses remained unchecked. The
scan performed no compilations or comparisons and does not establish regression
coverage or confer acceptance.

Independent review found a useful boundary counterexample: `MOV EAX,constant;
JMP EAX` passed the declared direct-only rule after constant propagation.
Evaluating an expression to a constant does not preserve whether the instruction
was direct. The first freeze was rejected pending a check of the original branch
form and a known-register-indirect regression. The strict object comparator was
unchanged; no false object match was established. Preserve this failed freeze
and its counterexample when correcting the shared rule.

The corrected freeze checks an actual typed constant target before evaluation.
Actual open SharpRetro fixtures verify that a known register-indirect jump is
refused while direct external and range-end jumps remain supported. The same
independent reviewer approved this bounded correction. The author tooling suite
passed 593 tests with 33 skips; 23 focused and 28 standalone MCP tests (two skips)
passed on macOS ARM64. Replaying both original typed lifts reproduced their C++
exactly, and fresh unchanged comparisons of the retained objects reconfirmed
22/22 and 11/11 bytes without another VM compilation. The corrected whole-inventory
scan reproduced all 27,555 rows exactly and still grants no comparison credit.

The next sequential identity, `0x1040`, remains unsupported. It passes a stack
argument to an external callee and returns with immediate stack cleanup. Neither
the callee's cleanup nor the caller's argument interpretation may be guessed
away to balance the stack. This is the next shared ABI-recovery problem.


### Durable targeted regression checks

The tail-rule scan exposed an execution gap: its 207 additional hypotheses could
not be compiled through the ascending frontier operation without skipping the
unresolved earlier function. The bounded correction adds explicit inventory-ID
target selection to the same durable submission and execution path. Regression
rows use a reserved key namespace in the existing queue table; old clients still
observe their active/unknown barriers. Current artifact-bound counts remain
separate from recovery rows. Both
modes retain the project-wide running/unknown barrier, exact input bindings,
idempotency and shared compiler lock. An optional generated-source digest refuses
a changed scan hypothesis before compilation. This operation adds no new
transformation semantics; publication and measured affected-corpus outcomes are
recorded separately after independent review. Two development targeted MCP checks
passed complete 22/22-byte and 11/11-byte comparisons on macOS ARM64 driving the
existing Windows 11 VC8 compiler. A wrong regenerated-source digest refused before
compilation. The unchanged retained adapter additionally checked each actual
object and its ordinary/EH gate; no object check can upgrade an earlier failed
comparison. These controls are not the affected-corpus result.


The reviewed targeted operation was published and installed after both exact-head
CI workflows passed on Linux, macOS and Windows. Fresh installed ordered controls
again matched 22/22 and 11/11 bytes. The affected batch then matched **39 of 208**
hypotheses completely before its 40th dispatch, at RVA `0x000d5890`, returned a
Parallels transport error without a compiler exit marker. That attempt remains
**external outcome unknown**; **168 hypotheses are unrun**. It was not retried.
The project-wide barrier refused subsequent generation requests in both modes.

Combining the 39 regression matches with the two compiling controls gives **40
unique current native object matches**, a gain of 38 ahead identities in this
new pipeline. Recovery still stops at `0x1040`; no source was exported and no
historical source count was added to these results. All 27,555 scan rows are
accounted for separately from these comparisons. The affected batch retained 39
confirmed compiler exits; the failed dispatch does not establish whether its
remote compiler ran. Raw evidence remains private under
`local/replayable-regression-001/`. Reconciliation of the existing unknown attempt
requires separate authorization and must preserve its history.

### Preserving an uncertain compiler dispatch

The failed Parallels dispatch retained no exit marker, object or compiler receipt.
Read-only inspection found its exact guest workspace and shared launch input
absent, while both parent directories were reachable and no other compiler or
command shell was active. The old production runner was already paused with no
in-flight requests and was left untouched. These observations do not establish
whether the old compiler ran or why the transport returned its SDK error.

The bounded recovery operation supports **nonaccepting abandonment**, not inferred
failure or artifact acceptance. It verifies the original request/input/source
bindings and the registered synchronous copy-before-compile launch protocol,
holds the old worker claim and existing shared VM lock, and requires the exact
launch prefix and workspace to remain absent with only its own diagnostic shell
present. Present artifacts, active launchers, changed files, inaccessible bases
or ambiguous transport results retain the barrier. A new durable observation and
barrier release commit atomically; the original unknown request/result stay
unchanged. A later compiler request must be explicit. The older approved execution
runtime can continue its unchanged binding set, rather than transferring its
completed matches to a new generator runtime.


### Completed affected-corpus continuation

After independent review and all-three-host CI, the exact frozen transport
runtime recorded a fresh **nonaccepting abandonment** observation for the old
dispatch. Its original request/result remain external-outcome-unknown. Fresh
installed ordered controls again matched 22/22 and 11/11 bytes. The unchanged
earlier execution runtime then checked the 169 remaining candidates explicitly;
39 completed results were verified and retained without recompilation or credit
transfer to the new runtime. No further uncertain outcome occurred.

The complete affected set is **203 full matches and five mismatches out of 208**,
with **zero unrun**. Rejected RVAs are `0x13cc50`, `0x4e0da6`, `0x4e893a`,
`0x4e8bda` and `0x57b780`; neither checker accepted a prefix or changed its gates.
All 27,555 inventory rows are accounted for: 208 compared candidates and 27,347
outside this affected domain. Including the first control gives **204 unique
native object matches**, a gain of 202 over the initial two. These are pinned
compiled-object observations, not source exports or game-execution evidence.

The continuation retained 169 confirmed compiler exits totaling 230.621 measured
compiler seconds. The recovery frontier remains `0x1040`. The separate addressable
stack-argument prototype has only offline generation evidence and was excluded
from this reviewed transport release. Private receipts and complete rejected
results remain under `local/replayable-transport-001/`.

### Composing addressable stack parameters with original-derived ABI evidence

The opt-in stack profile preserves the earlier store/call/tail domains and adds
one address-taken incoming parameter forwarded to a direct callee. Its durable
operation derives callee entries and typed lifts from the pinned original module
and inventory. A complete reachable callee CFG with uniform typed RET encoding
supports a bounded *normal-return cleanup hypothesis*. Unknown nested calls stay
external: this does not establish their memory effects, termination or complete
callee stack behavior.

The original first stack-argument frontier generated C++ and passed a complete
25/25-byte VC8 object comparison, with fresh 22/22 and 11/11 prior controls.
Pilot results remain distinct from independent machinery approval and installation.
An integration test caught an empty diagnostic source field; the prior response
shape was restored. Whole-inventory analysis also exposed checked symbolic-offset
overflow on two functions. Those offsets now refuse with a stable unsupported
result rather than crashing; no wraparound value is guessed. Both earlier runtime
variants, source outputs and results remain retained locally. Dependency evidence
hashes participate in current-result integrity checks.

The added-rule applicability scan accounted for all 27,555 inventory identities
in 45.910 seconds on macOS ARM64. It generated two unchecked source hypotheses:
one is the already compiled pilot and one still needs comparison. Necessary
static preconditions excluded 27,012 identities; actual typed checking refused
534 more, and seven dependency analyses could not use discontiguous original
callee ranges. Those seven remain unresolved, not successful. The composed recipe
retains prior domains, but this denominator measures the added rule only. It grants
no new-runtime credit to the 204 retained earlier object matches. The final
630-test suite (33 skips), standalone 65 tests (two skips), seven CTest checks and
both 59-case synthetic demonstrations passed; the negative demo detected six
mismatches. These generic tests do not establish game equivalence.


After cumulative independent approval and exact-head CI on all three hosts, the
frozen runtime was installed immutably. Fresh ordered checks passed at 22/22,
11/11 and 25/25 bytes. Both added-rule candidates have now passed complete native
object comparison: the same-binding ordered stack control was retained without
recompilation and the other candidate used the public targeted operation with its
expected regenerated-source hash. The 204 earlier matches were independently
checked for unchanged input/artifact bindings and retained under their original
runtime; no matching credit was transferred to the new recipe.

There are now **206 unique pinned native object matches**, a gain of two in this
stack-argument iteration. The selected recipe has three ordered matches and one
ahead regression match. Its first unresolved function is `0x1070`: original-derived
callee CFG evidence has an external or misaligned exit, so generation refused and
no compiler was launched. The function also contains conditional caller control
flow outside this added linear rule. No further rule was implemented. The prior
five tail-call mismatches remain rejected. Both added-rule candidates are checked,
with zero unrun or new uncertain compiler outcomes; seven discontiguous-callee
analyses remain unresolved. All 27,555 rows have explicit applicability/accounting
records. There are still zero new source exports and no game-execution claim.

### Conditional calls, forwarding evidence and separate cleanup obligations

The first conditional frontier required three related capabilities. Its called
forwarder is a complete one-instruction direct JMP to another exact inventory
entry. A bounded resolver now forwards only normal-return ABI evidence through
such pure thunks, retains their raw-slice hashes and preserves the *original*
called target in generated source and object relocation binding. Cycles, missing
entries, side effects, indirect transfers, prefixes and exhausted depth refuse.
Unknown nested calls remain external; uniform return encoding is a normal-return
hypothesis, not a whole-callee stack/effect or termination proof.

A separate bounded interpreter handles one forward conditional diamond. It
records the actual typed byte load, bit/flag expressions, native frame operations,
call-entry state, outgoing words and independent caller/callee cleanup. Both
paths must reach the same live stack and preserved-register state. Differing
volatile state joins as unknown. Incoming reads name current stack storage at a
PC/memory epoch, rather than a cached value from before an unknown call. The
explicit flat32 compiler profile relates segmented stack and ordinary ESP-based
addresses; known private-frame address escapes refuse. Native ABI frame lowering
and volatile exit flags remain compiler-profile obligations verified by the full
compiled range, not ignored unknown effects.

The source profile generated a complete 36/36-byte object match for the frontier,
alongside fresh ordered 22/22, 11/11 and 25/25 controls. A control dispatch first
returned a Parallels SDK error without a compiler exit marker. The existing
reviewed MCP quiescence operation proved its absent synchronous launch prefix
safe to abandon **without acceptance**; the original unknown result was retained,
and a separate explicit request then succeeded. No compiler outcome was inferred
from host exit255, no automatic retry was added and no transport code was changed.

Generic boundary tests additionally exposed duplicate call temporaries as an
invalid target-evidence shape; they now refuse. Complete frame/call-entry evidence
and a known-frame-pointer escape guard were retained before the final pilot.
Earlier variants/results remain private. The original-body source output stayed
unchanged; no function-specific source patch or RVA guard was introduced.

The final added-rule scan assessed all 27,555 inventory identities in 128.016
seconds on macOS ARM64. Necessary static preconditions excluded 26,473 identities;
actual typed checking generated 577 hypotheses and refused 389 cases. Another 116
dependency analyses remain unresolved: 95 incomplete/opaque lifts and 21
discontiguous callee ranges. The earlier profile generated none of those 577
conditional hypotheses. At the pre-adoption freeze, one was the 36-byte pilot; the other 576 were
unchecked. Generated-candidate rows and C++ stayed identical across the known-frame-address escape
guard, which now refuses 12 known frame-address escapes earlier. This is
applicability, not comparison credit. The final 652-test suite (33 skips),
standalone 87 tests (two skips), seven CTest checks and both synthetic demos
passed; the negative demo detected six of 59 case mismatches. Prior 206 native
object matches remain under their exact original bindings, with zero source
exports. That pre-adoption freeze required independent approval and fresh installed
checks before adoption.

The first cumulative review rejected a real private-frame alias defect: a word
store at entry-SP minus one overlapped the saved return address, while the word
slot model retained its old value. The rejected freeze and actual typed-lift
counterexample remain preserved. The bounded repair requires each private word
store to be aligned relative to entry SP, fully inside the allocated negative
frame, and ordinary SP adjustments to remain aligned and nonpositive. Generic
boundary tests and the actual counterexample now refuse; all four ordered native
controls still match with unchanged generated C++. The corrected whole-inventory
scan rows are byte-identical: 577 hypotheses, including 576 still unchecked.
No full comparator was changed, and no false full match was claimed.

The corrected freeze `064dbaf9...a1ccd5f` was independently approved and its exact
source published at `46740b9`. Both CI workflows passed on macOS, Linux and
Windows. Immutable runtime `d2a6ea970751ead1` then passed fresh installed ordered
checks at `0x1000`, `0x1030`, `0x1040` and `0x1070` (22, 11, 25 and 36 bytes).
The next ordered identity, `0x10c0`, remains inconclusive with
`unsupported_conditional_input_extent`; no further rule or queue skip was added.

The installed runtime regenerated and checked all 577 affected candidates through
existing durable MCP jobs: 576 full native-object matches, one rejected mismatch,
and zero unrun candidates. At `0x476650`, both unchanged full-range gates reject
the 38-byte object against the complete 45-byte original. The prior five rejected
tail-call candidates remain rejected. The 576 new distinct matches plus the 206
retained identities give 782 distinct native-object matches under their recorded
bindings; 579 matches use the current recipe (four ordered controls plus 575
targeted jobs). Ahead regression results do not move the `0x10c0` frontier.

Ten affected-batch transport-unknown attempts remain unchanged in history. Each
continuation followed a separately invoked, reviewed nonaccepting recovery
operation with fresh bound evidence; completed jobs were reused and no unknown
attempt received match credit. Including author variants and installed controls,
this scope retained 608 managed build attempts: 596 confirmed compiler exits
(831.321 measured compiler-host seconds) and 12 uncertain attempts. No active
uncertainty barrier remains. All 27,555 scan rows have explicit accounting;
26,473 outside-domain rows, 389 typed refusals and 116 unresolved dependency
analyses received no new conditional-match credit. Receipts are under ignored
`local/replayable-conditional-calls-001`. Accepted source exports and game
execution remain zero; these are compiled-artifact observations.

The `0x10c0` EH pilot exposed a useful cross-tool distinction. Actual typed effects
supported a bounded two-terminal-arm recovery, with FS linkage, cookie, state,
unknown external call results and ordered global stores retained explicitly.
A VC8 class/new source spelling was a compiler-profile hypothesis checked against
the complete native main/EH graph, not a recovered allocator/constructor contract.
C linkage and `/GS-` failed the required compiler/EH domain; C++ linkage and `/GS`
produced the full 197-byte graph. Four relocation bytes initially stayed unknown
because an existing exact constructor-name recognizer supported only signed-int
constructors. A separately authorized exact zero-argument spelling extension now
passes generic positive, wrong-RVA/target and generated-name rejection tests. A
fresh author pilot checks all 197 bytes and the earlier ordered controls. The
unsupported-format report and failed candidate remain evidence; at that author-only stage,
no installed match count or accepted source count changed.

The final added-rule scan accounted for all 27,555 original inventory identities:
one generated EH hypothesis (`0x10c0`), 238 typed refusals, 54 unresolved dependency
analyses and 27,262 rows outside the added necessary domain. It performed no VM
compiles or comparisons and grants no credit. The single hypothesis is covered by
the author pilot; installed checks initially awaited review. Final local checks on
macOS ARM64 passed 678 Python tests (33 skipped), 107 standalone MCP tests (two
skipped), all seven CTest checks and the two synthetic demonstrations (59 positive
cases; six expected negative mismatches). Twenty retained author build attempts
used 28.381 measured compiler-host seconds; no attempt in this scope was uncertain.

The EH checkpoint is now independently approved and published as `86ccd2e`.
Both exact-head CI workflows passed on macOS, Linux and Windows. The immutable
`392438798beabd10` release is installed with the prior `d2a6ea970751ead1` release
preserved. Fresh installed MCP checks passed `0x1000`, `0x1030`, `0x1040`,
`0x1070` and `0x10c0`; the last accounts for all 197 required main/EH graph bytes.
The one added-rule candidate was retained from that exact same-binding installed
ordered job after source/object/report/dependency hash checks, avoiding a duplicate
compile. The added set is one full match, zero mismatch/unknown/unrun. There are
783 distinct historical bound native object matches (782 retained plus one gain),
with five fresh matches under the selected EH recipe. No old binding credit was
transferred: the constructor identity capability changed the checker/pipeline
binding, and its previous source version and all old artifacts remain preserved.

The installed ascending frontier is `0x1130`. Its final EH fallback reports an
unbound handler prefix, but separate read-only characterization finds no FS root
in the caller: the earlier conditional refusal is an unsupported callee exit.
The called `0x1030` has an ordered store before a tail jump, so it cannot be treated
as a pure forwarding thunk. No next-rule implementation or compiler attempt was
made for that body. This checkpoint used 25 confirmed managed compiler attempts
and 35.376 measured compiler-host seconds, with zero new uncertain attempts.
Thirteen prior completed unknown attempts remain unchanged and no active project
uncertainty barrier remains. Accepted source exports and game execution are zero.
Receipts, the full 27,555-row accounting and rollback registration are under
ignored `local/replayable-eh-frontier-001`.

The next development batch recovers normal-return ABI evidence through a bounded
store-and-tail adapter. It retains the adapter's ordered stores and original call
target, follows only an actual direct terminal jump to a unique pinned inventory
entry, and refuses changed registers/stack/flags, unknown reads, indirect exits,
cycles or exhausted depth. The terminal return evidence remains a conditional ABI
hypothesis; nested effects, throwing and termination remain unknown. An
inapplicable EH fallback no longer hides the earlier refusal for callers without
an actual FS-segment read. It does not grant an EH binding.

The first development frontier, `0x1130`, generates from its complete original
30-byte body and passes the unchanged full native-object checks. Fresh prior
controls `0x1030`, `0x1070` and `0x10c0` still match, including all 197 required EH
graph bytes. One transport attempt lacked a compiler exit marker; it remains
unknown in history, and the reviewed fresh nonaccepting reconciliation allowed a
separate attempt only after establishing its actual safety conditions. These are
provisional development results; the installed reviewed total remains 783.

Development stops at the next original identity, `0x1150`. Its complete 43-byte
body initializes a partial private stack word, supplies six by-value outgoing
arguments and performs caller cleanup. Its exact original 77-byte callee contains
an opaque one-operand multiply in the current pinned lifter. The ABI resolver
refuses this incomplete typed evidence. No later identity is substituted for the
blocked frontier, and no multiplication, input arity or return semantics are
guessed.

Validation now runs against frozen source/runtime/config snapshots in ordinary
background processes. The author consumes compact completion or exception
receipts while doing useful work; models do not judge deterministic per-function
checks. Full suites, independent machinery review and source/docs publication are
batched at coherent milestones. A disjoint 16-source transport benchmark measured
26.563 seconds for individual dispatches versus 5.607 and 5.463 seconds for two
guest loops, including unchanged comparison. All 48 checks matched, including the
EH case. That small-sample transport observation grants no new function credit
and does not itself authorize switching the durable execution protocol.

The stable call-adapter snapshot assessed all 27,555 identities in 135.979 seconds:
626 generated conditional-domain hypotheses, comprising 577 already generated by
the installed conditional frontend and 49 added by the new dependency rule.
All 49 added candidates subsequently passed complete original/object comparison
through durable targeted MCP jobs. Exact expected source hashes and every retained
source/object/report/dependency binding were checked. This is a provisional gain
of 49 distinct identities (832 including the 783 historical matches); review and
adoption remain pending. No scan row itself grants a match, and earlier mismatches
remain rejected under their original bindings.

Frozen macOS ARM64 validation passed 692 Python tests (33 skipped), 121 standalone
MCP tests (two skipped), all seven CTest checks and both README demonstrations
(59 positive cases; six expected negative mismatches). A final focused 14-test run
also covers the explicit Windows skip for POSIX-only dependency loading. The
initial incorrect demo command is retained as an invocation failure; its corrected
README commands passed without repeating the full suites. Across the frontier,
controls and added candidates, 53 compiler attempts have confirmed outcomes and
four uncertain attempts remain preserved. Each safe continuation used the existing
nonaccepting abandonment operation with fresh bound evidence. No queue, comparator
or uncertainty policy changed.

### Early iteration: representative validation and CI paused

On 2026-10-20 the user removed CI and routine full-corpus validation from the
early development loop. Both GitHub workflows, `validation-infrastructure` and
`decompilation-mcp`, are disabled through reversible repository settings; their
definitions remain checked in. The preceding checkpoint had already completed
CI, so no live run needed cancellation. Subsequent checkpoints must report CI as
disabled, not passed.

Routine work now builds changed components, runs focused generic tests and checks
at most 16 representative real functions initially: the frontier, relevant prior
matching domains, changed-rule boundaries and known failures. Each selected
function still receives complete range, relocation and required EH comparison.
The existing ordinary/EH transport pilot supplies a ready sample for batching
changes. A passing sample makes no claim about untested identities; older results
retain their original bindings and new match credit requires actual comparisons.
Broader scans and suites remain available for a concrete diagnostic need or user
request. Independent cumulative machinery review and immutable rollback remain,
without a CI wait or an automatic whole-inventory release gate.


The durable guest-batch integration keeps the C# queue authoritative and amortizes
only compiler transport. An eight-identity development sample generated six
unchanged ordinary/EH controls, retained the `0x1150` refusal and retained the
`0x476650` mismatch. Its seven serial compiles took one dispatch (2.418 seconds),
with 13.211 seconds through source generation and both unchanged comparison gates.
No unknown or retry occurred. This supports the transport mechanism on that sample;
it adds no distinct recovered identity and extrapolates no credit to other inputs.
Partial receipts and restarts are exercised by open failure fixtures. Unknown group
outcomes remain barriers; the existing single-job reconciliation is not silently
reused for the new envelope protocol.


The next bounded iteration separated private-byte state, outgoing arguments and
caller cleanup. In the first unresolved wrapper, a low-byte store updates an
initialized private word; six complete outgoing word copies remain visible, and
28 bytes of cleanup comprise 24 outgoing bytes plus four private bytes. The
minimum observed incoming extent is three words. Neither C3 nor cleanup alone
establishes formal arity. The external target, unknown effects and external return
value remain intact.

The first generated VC8 candidate was a real nonmatch: 35 bytes against the
original 43. It merged distinct repeated incoming reads. Qualifying the repeated
parameter accesses as volatile preserves those observed reads while leaving their
values and target unchanged; the resulting complete 43-byte object passes both
unchanged comparison gates. A one-byte aggregate carries the initialized byte;
its extra ABI word padding is unspecified in C++, never read as an uninitialized
scalar or filled with an invented zero. Recovered IR retains the original upper
bits, and only a complete selected-compiler artifact match grants native credit.
This remains an artifact-domain result, not universal C++ semantics proof.

The reviewed upstream IMUL repair was adopted into a separate dependency build
at commit `0269ffd3d8fb19d50a946b005434917d6ec1bd64`. Generic 8/16/32-bit adapter
checks preserve all four explicit undefined flag nodes. Consumed undefined values
refuse in each symbolic recovery path; a structural uniform-RET observation does
not turn the callee body into known semantics. The older source and adapter stay
available for rollback.

The next identity, `0x1180`, is a separate cyclic-memory capability boundary:
count-controlled backward control, null-destination guards and alternating source
word reads/destination stores with wrapping updates. It remains unsupported;
there is no memcpy, nonalias or termination assumption and no skip to `0x11c0`.
Representative validation covers nine identities, including the retained negative,
with no routine full suite, whole-inventory sweep or CI. A larger input closure
also exposed misuse of a small receipt reader for the dispatch decision. Separating
the bounded decision-document budget from strict small receipts fixes that
pre-dispatch failure without weakening compiler outcomes or comparisons.

### Ordered memory and a first natural loop (development batch 003)

The next original identity, `0x1180`, required a cyclic representation rather
than path enumeration. The new x86 pass builds block-local register/flag SSA,
explicit edges and simultaneous register joins, checks SP consistency, computes
dominators, and records a bounded reducible natural loop. Loads and stores stay
ordered events. In particular, a later POP or RET remains a memory read when an
incoming pointer might alias the private frame or entry return address; a slot
map must not manufacture an unchanged return target.

The bounded VC8 profile derives a zero-count bypass, repeated destination-null
guard, decrement-by-one termination, wrapped destination stride and alternating
word loads/stores from those effects. It does not recognize an opcode byte
sequence, function RVA, bulk-copy routine or nonoverlapping buffers. Each word
access uses a four-byte intrinsic copy; these are separate ordered accesses,
not a memcpy/memmove interpretation of the loop. Unsigned guest addresses wrap
before conversion at the selected i386 native memory boundary. Compiler-private
register saves and void return spelling remain hypotheses, with their original
architectural effects retained in the graph.

The first compiler attempt failed with a known exit because the selected portable
VC8 environment has no header search path. Declaring the standard 32-bit memcpy
intrinsic directly removed that dependency. A 49-byte candidate then failed the
complete comparison because a destination-input load moved ahead of the zero
count guard. Keeping pointer preparation inside that guard and using volatile
parameter accesses to preserve their observed load order produced a provisional
complete **49/49-byte** comparison. Volatile is an emission constraint here, not
a discovered qualification of the caller's storage. Open tests include zero,
one, exhausted large-count budgets, address wrapping, sequential overlap and
return-address aliasing; exhausted execution remains unknown.

The following `0x11c0` exercised forward branches, original external calls and
ordered word/byte object stores. A shared forward effect tree now retains those
operations and explicit unknown call results/effects. Arbitrary stores invalidate
private-stack forwarding; later stack reads become fresh memory observations.
Calls after such invalidation are refused until their outgoing argument state
can be recovered safely. A candidate compiles to the full 74-byte length, but the
strict checker still rejects a different base/index encoding in the final byte
store. The equivalent-looking instruction is **not** promoted to a match, and
`0x11c0` remains the development frontier. Rejected integer-address and memory
primitive spelling variants are retained locally; pointer-arithmetic undefined
behavior, inline assembly and comparison-policy changes were not used to force
acceptance. This is a useful CFG/memory capability checkpoint, not three new
consecutive matches or a game-execution result.

The representative native batch covered ten distinct identities in **16.45 s**:
seven prior controls plus `0x1180` passed complete comparison; `0x11c0` and the
retained `0x476650` negative remained mismatches. Final-runtime source replay
reproduced all ten sources exactly without another compiler dispatch. A later
IR refinement makes wrapped SP addresses explicit; it does not transfer native
credit to the new runtime key. Fourteen final focused checks passed, including
host syntax checking of open generated C++ with multiple memory transfers. The
representative observations leave the other **27,545 identities unverified**
under this new composition. CI, broad scans and full suites were not run under
the current sampling policy.

The first cumulative machinery review rejected two generation-domain defects
without overturning the retained native comparisons. Two independent typed
undefined flag values with the same diagnostic reason could collapse to an
invented constant equality in the graph. The corrected bounded pass refuses
`IlUndefined`, as the earlier symbolic consumers do; diagnostic text never
establishes value identity. A separate open halfword-input counterexample showed
that a 16-bit read could become an untruncated 32-bit formal parameter. The
structured profile now explicitly refuses that unsupported width, retaining its
aligned byte/word input domain. Both counterexamples and the rejected freeze are
preserved. Focused tests cover the refusals and supported boundaries; these
refusal corrections require source replay, not another VM compilation of
unchanged sampled C++.

### Separate byte equality from a bounded encoding relation

Batch003 was subsequently reviewed, published and installed. Fresh ordered
controls through `0x1180` retained eight exact comparisons and a distinct
historical total of834 native object matches; the `0x11c0` SIB difference stayed
rejected. Source exports and whole-game evidence remained zero.

A controlled compilation-unit experiment then held the generated target body,
compiler and flags fixed across12 sources. Unrelated prefix/suffix functions,
loop/branch code, unused globals/types, declaration/helper order and two separately
labeled class-name changes all produced the identical complete74-byte target.
The compiler time summed0.914s in one2.612s dispatch. This refutes those tested CU
contexts as the explanation; it does not prove CU context can never affect MSVC.
Eleven earlier address-emission spellings and a uniform size-preference sample
also failed to repair the difference. The size preference regressed controls,
so speculative pointer/layout/option rules were retained locally and not adopted.

An isolated, user-requested calibration compared authentic VC8 RTM
14.00.50727.42 with SP1.762 using a frozen210-byte ordinary function, the74-byte
case and a49-byte loop control. Across50 explicit successful compiler exits and
12 requested flag profiles per cohort, all24 completely relocated paired bodies
were identical. One no-inline pair remained inconclusive because an outlined
helper dependency was unexamined; its raw bytes and symbolic relocations also
agreed. `/Oa` was an ignored alias, not an effective additional configuration.
Compiler time summed5.055s and dispatch time15.221s. Neither cohort nor these
flags explained the SIB choice, and no production compiler/flag change followed.
The original game PE exposes linker8.0 without exact backend/option provenance;
a separate configuration utility's compiler-family metadata is not proof of the
game's compiler patch level. Further compiler calibration remains a separate lane.

The user explicitly authorized an additional encoding-equivalence check rather
than requiring exact byte equality in this case. The first rule preserves the
strict comparison and permits only one supported default-DS, scale-one base/index
swap in a MOV immediate store, with complete otherwise-identical relocated range.
It excludes ESP/EBP, unsupported prefixes/scales, changed values/widths, ambiguous
relocations and interior/indirect control targets. Fresh attested SharpRetro
output must contain the same captured store and an explicit wrapped32-bit affine
address; register coefficients and constants normalize in the fixed-width ring.
Independent undefined values, wrong incoming registers and arbitrary IR equality
are not normalized into agreement.

This is narrower than trusting a general effective-match heuristic. A standalone
probe of pinned reccmp's `find_effective_match` returned true both for the actual
swap and for an unsafe `mov eax,ecx` versus `mov eax,edx` example. The probe used
the helper with annotation imports substituted, not the complete linked-PE/PDB
CLI. It motivates a bounded rule with negative controls, not a claim that all of
reccmp is unsound or that its heuristic is an architectural proof.

The final development sample reused ten identities with fresh bound compilation:
eight prior exact matches including the complete197-byte EH graph, one separately
reported encoding-equivalent result at `0x11c0`, and the retained `0x476650`
mismatch, in17.79s with no uncertain compiler outcome. A prior18.63s run was
retained before tightening result-label/cache guards. Both fresh comparison gates
agree on accepted mode; the strict nonmatch remains in the report. Cache reads
recompute comparison and typed evidence, verify the durable result and compiler
envelope, and refuse missing, stale, forged or relabeled certificates. Fifty-five
focused tests passed; synthetic protocol fixtures grant no game/native credit.
The other27,545 identities remain unverified under the additional checking mode.

The new outcome is `encoding_equivalent`, distinct from `full_match`. This is
compiled-artifact evidence under paired architectural context, with code-byte
observations and arbitrary interior entry excluded; original external calls and
unknown effects remain aligned, not stubbed or proved. Reports keep `proof=false`
for universal function/game claims. Review/adoption and fresh installed ordered
checks are recorded locally; no development result silently transfers into a
released input key or source export.

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

# Replayable decompilation from the original binary

Active direction: `codex/replayable-decompilation`, starting 2026-10-20.
The previous committed workflow is preserved on `codex/ghidra-mainline` at
`2b95feb309ff1a6f783e7508b7f4f91f798f69f8`; `codex/rapid-recovery` and its
uncommitted local experiments remain intact. Its 2,258 published functions are
historical evidence, not new-pipeline acceptance.

The objective is a reproducible series of steps from the pinned binary to
matching, understandable C++, eventually supporting a working replacement.
We target complete matches throughout the inventory. We do not assume that
compiler version uncertainty, ambiguous boundaries or unsupported semantics have
already been resolved, or that matching functions establish a runnable game.

## The development loop

1. Select the earliest unresolved inventory identity by ascending RVA.
2. Inspect original instructions and actual typed SharpRetro effects.
3. Find the missing or incorrect general reconstruction/compiler behavior.
4. Implement a reusable pass with explicit applicability and failure conditions.
5. Run focused boundary/negative tests, a complete real-compiler comparison at
   the frontier, and a small relevant set of previously matching controls.
6. On a complete match, continue to the next consecutive identity within the
   current bounded implementation batch. Keep development results provisional.
7. Check a representative sample, initially at most 16 identities, rather than
   scanning or recompiling the whole inventory. Include the frontier, relevant
   previously matching domains, changed-rule boundaries and known failures.
   Record the selected identities and exact inputs in existing job records;
   preserve valid caches, failures and unrun work.

The user requested this tighter cadence on 2026-10-20. A small rule or successful
function does not require a new author assignment, a full test suite, independent
review, a release or an installation. An author can own several consecutive
frontiers in one bounded batch. Regressions in previously matching controls
require investigation; an unsupported next identity remains the development
frontier and must not be skipped.

The user's later instruction on the same date also pauses CI and routine full
sweeps. Choose the sample deterministically from existing evidence, covering
straight-line code, tail calls, stack arguments, conditionals and EH where relevant
to the change. For transport changes, the existing 16-source ordinary/EH pilot is
a useful starting sample. This is coverage across known cases, not a statistical
estimate of the entire inventory. Add cases when a concrete failure exposes a
gap; run broader scans or suites only when needed to resolve that finding or when
the user requests them. There is no automatic full-sweep release gate.

The development frontier records consecutive complete comparisons under an
experimental pipeline version. The released frontier and reviewed match totals
remain tied to a tested, reviewed checkpoint. Neither generation success nor an
applicability scan grants match credit. Both frontiers and pending validation
are reported explicitly, using existing job results and the compact handoff.

## Checkpoints

A checkpoint has one cumulative machinery review, rather than per-function
audits. Its bounded author may fix concrete findings and dispatch up to two
focused same-reviewer deltas, separately accounting each request at dispatch.
Completed requests stay consumed. Those repairs and an approved release need no
new director permission; disagreement, exhausted deltas or new external scope
still require escalation. This clarification joins source checkpoints and never
requires a policy-only release.

At a coherent capability milestone or the end of a bounded implementation batch:

1. Finish the representative regression sample and record its deltas and coverage.
   Outside-sample identities remain unverified under changed rules. Preserve older
   observations under their original bindings without transferring match credit.
2. Build changed components and run focused generic boundary/negative tests.
   Run harness demos when the harness changes. Full repository/standalone suites,
   CTest and inventory sweeps are available on demand, not routine release gates.
3. Obtain one independent review of the new transformation, lift, export or
   acceptance machinery, with attention to any changed comparison or binding
   rules. Fix concrete findings and test the affected delta.
4. Publish code, methodology and results available so far in one checkpoint;
   install the reviewed immutable release and run a small installed smoke check,
   preserving rollback. CI is disabled and is not a publication or installation
   gate. Reuse unchanged evidence under exact bindings.

GitHub workflows `validation-infrastructure` and `decompilation-mcp` are disabled
using their reversible repository settings; their workflow files are preserved.
Do not enable or dispatch them until the user asks to restore CI. Restore with
`gh workflow enable ci.yml` and `gh workflow enable decompilation-mcp.yml`.

Do not start another documentation-only release/CI/install cycle merely to
describe completion of this checkpoint. Save final receipts in the local handoff
and include the public results update with the next combined checkpoint.
Documentation-only edits do not invalidate unchanged execution evidence.
Existing jobs, hashes and test reports provide provenance; avoid new manually
authored per-function packets or repeated summaries of the same evidence.

This changes when broad checks and releases run, not what a complete match means.
Original full ranges, required EH dependencies, relocations and unknown outcomes
still use the independent comparison requirements. Experimental compiler inputs
remain bound to their actual version; no acceptance-policy relaxation, cached
credit transfer or ambiguous execution replay is implied.

The first five inventory entries are `0x1000`, `0x1030`, `0x1040`, `0x1070`,
and `0x10c0`. Their signatures and boundaries are discovery hypotheses.
Do not substitute more convenient examples for the first unresolved identity.
Calls may require inspecting other functions; generic tests and corpus checks
may produce matches ahead of the frontier. Record those separately.

If an identity's boundary is wrong, retain the original hypothesis and the
instruction-backed correction history. Removing a difficult entry without
evidence is not progress. Interrupted attempts remain unknown until reconciled;
starting a new branch does not authorize resetting existing request ledgers.

## Architecture

The shared core handles architectural effects, control/value flow, memory effects,
recovered entities, typed transformations and persistent source knowledge.
Compiler profiles handle ABI interpretation, helper/runtime/EH recognition,
build configuration and source-emission choices. The initial profile uses the
existing selected VC8 toolchain; the original compiler patch remains uncertain.

SharpRetro instruction IL is an input to reconstruction, not automatically
structured C++. Preserve original instruction origins and explicit unknowns.
A generic recovered IR and C++ representation permit profile-specific passes
without duplicating the whole decompiler for each compiler or game.

Do not generate matching-looking C++ by retrieving old recovered bodies,
emitting raw instruction bytes/inline assembly or hardcoding an RVA's answer.
Per-entity names, signatures and layout observations are project knowledge with
provenance. They must not become hidden target-specific transformation code.

All routine stages belong behind the same C# core/MCP API: generate, inspect,
submit corrections, trial a JSON pass recipe, compile, compare, report regressions,
publish and resume the linear queue. A minimal implemented subset must advertise
its limits. The [full design](decompilation-mcp.md) remains a roadmap wherever
there is no tested implementation.

## Durable edits and trials

The original binary, versioned analysis/knowledge and ordered transformation
history are the durable project. C++ snapshots remain publishable outputs and
regression baselines. Keep names/types attached to entity lineage and instruction
origins; merges/splits that cannot be resolved become conflicts.

Recipes select versioned typed passes and parameters. Trials branch from a fixed
baseline, record stage hashes and use existing complete comparisons. A new pass
must report unique improvements beyond its discovery function, compile/match
regressions, unsupported states and pending work. Unknown effects cannot be
replaced with zero or successful calls. A malformed/unsupported recipe fails
explicitly; incomplete work is not a clean regression result.

Model work should produce general rules, analysis corrections or replayable
source proposals. C++ remains the only required authored per-function artifact;
provenance and trial/queue records are generated by the framework.

## Bootstrap and independent evidence

The initial milestone is a real end-to-end path on RVA `0x1000`, starting from
original bytes and actual SharpRetro IL, emitting C++, compiling with the
selected VC8 installation and invoking the existing strict object comparator.
Use a small supported domain rather than an empty universal abstraction.

Fix observed lifter errors at their source and validate new semantics with
independent evidence. A generator and its lifter cannot validate each other
merely by producing agreeing trees. The existing complete original-byte/object
comparison remains independent of the generation pipeline; unsupported EH and
unresolved required relocations remain nonaccepting.

The first inspection exposed a Bits32 near-CALL stack-width inconsistency in
the pinned SharpRetro effects. The independently reviewed correction is published
in SharpRetro commit `ce590d0a2f2a7e231e0529e30f2fd0d4252ca769`. It fixes CALL
operand widths, indirect target evaluation before stack mutation, coherent
SS/stack-width handling and operand-sized near returns. The final upstream
suites passed 329 XFusion and 14 Jit tests on macOS ARM64. Independent Unicorn
probes agreed in 57 of 61 cases; four Intel64 operand-prefix differences remain
explicitly documented. This bounded Intel/C# correction does not establish
arbitrary descriptor widths, faults, Rust execution or whole-game behavior.

The first real pipeline pilot generated RVA `0x1000` solely from the corrected
typed IL and compiled it with VC8 in Windows 11 ARM64 under x86 translation.
The unchanged object comparator reported a complete **22/22-byte match**.
There was one actual compiler invocation and zero provider calls; toolkit
development/review still consumes Codex resources. The original was not executed.
This pilot result remains distinct from source publication and game execution.
The cumulative reconstruction/profile/queue machinery passed independent review,
including a correction that keeps unfinished compiler operations blocking across
pipeline-version changes. The final local suite ran 585 tests with 33 skips;
the standalone MCP suite ran 24 tests with two private-input skips. These are
macOS ARM64 test results; cross-platform CI is a separate receipt.

The next selected identity was `0x1030`. Its 11-byte body reaches an unconditional
terminal jump, which the initial straight-line reconstruction refuses as
`unsupported_control_flow`. The queue remains there; it did not skip to `0x1040`.
The next reusable capability is explicit tail-call recovery and compiler-profile
emission. No target-specific replacement body was installed to bypass this gap.

## Operations and records

Read the original checkout's `local/rapid-current-handoff.json` and follow its
current handoff and compact-status paths for owners, evidence, frontiers and next
action. Bootstrap records are historical once the pointer advances. Preserve
them without restarting old sweeps/controllers.

Use at most two implementation lanes with disjoint files. The primary toolkit
author uses GPT-6 Astra with high reasoning, as requested by the user on
2026-10-20. Independent reviewers remain Sol6.1 medium. DeepSeek production
remains paused.
Account model assignments in the existing global ledger and preserve paid budgets.
Reuse the actual shared VM build lock across worktrees. Compiler execution in
Windows 11 ARM64 under x86 translation is not native x86 hardware evidence.

Use focused tests and representative complete comparisons during development and
combined checkpoints. Retain exact reviewed dependencies and push tested changes;
record CI as disabled, not passed. Update the installed MCP only from
tested/reviewed releases, keeping its old installation recoverable.
Publish useful generated source without binaries, compiler files, assets or
private captures. Keep the learning log and reproducible methodology current.


### Bounded encoding equivalence

Exact full-function matching remains available. The additional user-authorized
opt-in checking pass distinguishes a verified architectural encoding relation
from byte equality. Its first rule permits one scale-one default-DS base/index
swap in a MOV immediate memory store, only when all remaining relocated bytes,
full boundaries, values, widths and targets agree. Fresh pinned SharpRetro typed
IL must independently agree on the wrapped address and ordered store. Prefix,
segment, special-register, control-target, relocation and unknown-effect guards
refuse unsupported cases. EH continues through its complete existing graph gate.

The recipe appends `compare-complete-x86-encoding-equivalence-v1` to the existing
ordered-memory composition and uses architecture
`x86-bits32-composed-memory-encoding-equivalence-v1`. It changes checking policy,
not generated source. `full_match` remains exact; `encoding_equivalent` is a
separate outcome with its strict nonmatch retained. Queue/status totals expose
both counts and their accepted union. The project-wide uncertainty barrier and
ascending selector still apply. Cache reads for this opt-in policy freshly
recheck the bound artifacts and accepted mode; a saved diagnostic certificate
or edited result label is insufficient.

This is bounded compiled-artifact evidence under common architectural context,
not a universal function-contract or game proof. External calls retain their
original targets and unknown effects. Code-byte observations, debugger/fetch
side channels and arbitrary entry into instruction interiors are outside this
relation. Source exports remain separate. The current local release/handoff
records identify which exact reviewed runtime is installed; development sample
results do not silently transfer into another input key.

### Terminal-aware memory composition and layout observations

The explicit architecture `x86-bits32-terminal-aware-memory-encoding-v1` adds
original/library-bound exceptional-terminal evidence and mutable forward joins
to the previous memory composition. Its profile is
`vc8-x86-flat32-terminal-aware-memory-control-v1`. Previously supported recipes
remain available, and the new composition tries their source domains first.
Fresh dependency derivation binds complete original/runtime bytes, readonly
data, imports and selected CRT archive members. A complete typed callee CFG must
reach the certified exceptional call on every path; missing RET, an arbitrary
symbol name, a propagated indirect target or an incomplete range is insufficient.
The Windows noncontinuable API assumption is explicit; nested effects and
exceptional destinations remain unknown.

Incoming extent, return cleanup and observed outgoing arguments are separate.
Observed aligned incoming-word writes can feed later loads only within the
already observed input extent. Explicit delayed caller cleanup cannot cross a
call or control boundary. Mutable join emission keeps typed register/temp
provenance and refuses unsupported state or memory effects. Complete object,
relocation and EH checks still determine outcomes; the existing narrow SIB
encoding relation is unchanged and cannot accept length-changing rearrangements.

Receiver observations describe accesses, not a guessed class declaration.
Fixed intervals and indexed expressions retain guards/origins; overlapping slots
and unknown index bounds remain ambiguous. Generated checked raw-byte views may
name fixed offsets without declaring the object's extent or indexing beyond a
proven view. Cross-method class merging needs separate receiver/type evidence.
The retained single-try comparison at `0x1210` remains a mismatch: generated source is useful
recovery evidence, but its retained native comparison is a mismatch.


The current multi-try source proposal is `lexical_catch_shared_continuation_v4`.
Generic EH interval/unwind analysis places the retry try inside the first catch;
the generated code completes that catch before continuation loads and one shared
suffix. Actual VC8 metadata now matches the original try/unwind topology, and an
open tagged-object probe observes retry cleanup before first-exception destruction.
The complete comparison remains a 506/488-byte mismatch. Unknown calls retain
potentially throwing C++ declarations, and VC8 inserts state resets; this proposal
does **not** preserve the original conditional residual-state0/state2 suffix routes.
Those obligations remain explicit in the region model and block acceptance.
A separate known-contract synthetic compiler probe shows omitted resets for a
nonthrowing C tail, without establishing any original call's throwing contract.
Historical836, public10 and frontier0x12a0 remain unchanged. The prior enclosing-
catch v3 and its lifetime counterexample remain retained rejected evidence.

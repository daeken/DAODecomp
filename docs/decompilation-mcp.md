# A reusable decompilation MCP

Status: design and roadmap, updated 2026-10-20. The first C# slice implements
inventory/source browsing, related-function search and fresh comparison of
retained compiler artifacts; see [implemented tools and setup](decompilation-mcp-usage.md).
The remaining capabilities below are planned, not implied by installing the
server. The existing whole-inventory rule recheck continues independently.

The product is a local engine for turning binaries into maintainable source.
An agent supplies judgment and difficult code; the engine supplies indexing,
compilation, comparison, reusable transformations and a durable work queue.
Its first useful loop is **inspect one mismatch, develop a reusable fix, test it,
then automatically find and check every other applicable function**.

C++ remains the only authored per-function artifact. Identity records, build
inputs, dependency maps and reports are generated. The design does not restore
the historical per-function contract/corpus/approval-packet workflow.

The 2026-10-20 architecture decision is to separate reusable **x86 semantics and
source manipulation** from **compiler-specific reconstruction and matching**.
The entire project workflow, starting with initial decompilation and continuing
through pattern repair and source refactoring, must be available through MCP.
These are requirements for subsequent slices; the installed read/check slice
does not yet implement them.

## Implementation decision

Use **C# for the core engine, job runner, CLI and MCP server**. This follows the
user's preference for Rust or C# and gives SharpRetro a direct integration path.
Keep the core independent of MCP so command-line runs, editor integrations and
automated workers use the same operations and persisted state.

Use the [official C# MCP SDK](https://github.com/modelcontextprotocol/csharp-sdk)
for the transport layer. The first slice pins .NET SDK 10.0.101 and MCP SDK
2.2.0; its protocol tests negotiate 2025-11-25. Start with local stdio; hosted remote access is a
later deployment option, not an MVP dependency.

Use a separate, versioned C++/Clang helper for source analysis and edits.
[LibTooling](https://clang.llvm.org/docs/LibTooling.html) supports standalone
tools; [AST matchers](https://clang.llvm.org/docs/LibASTMatchers.html) and the
[refactoring engine](https://clang.llvm.org/docs/RefactoringEngine.html) provide
the relevant source-transformation building blocks. Exchange structured,
batched messages with this helper. Do not build a second C++ parser in C#.

Initially adapt the working Python build/comparison/export components through
a narrow local process boundary. New engine logic belongs in C#. Port existing
components only with measured benefit and outcome parity; a comparator port is
an acceptance-system change and needs its own tests and independent review.
No Python rewrite of the new server, no simultaneous Rust implementation, and
no requirement to rewrite all working tools before delivering the first loop.

## Architecture and boundaries

```text
Agent harness / editor             CLI / unattended deterministic runner
          |                                      |
     MCP facade ---------------- C# engine API --+
                                      |
                    Project index + durable job/work queue
                    Content-addressed artifacts + source revisions
                                      |
              +-----------------------+----------------------+
              |                       |                      |
       Binary / SharpRetro     Clang AST helper       Build / check adapters
       analysis workers        and rule registry      local or compiler VM
```

One engine owns a project's mutable database and publication state. Multiple
clients attach to that engine; they do not start competing schedulers. A stdio
frontend can reconnect to a project runner through local IPC. Durable jobs
survive frontend disconnection; if the runner itself stops, resume reconciles
recorded work instead of claiming the external operation never happened.

Start with SQLite and local artifact storage, not a distributed service.
Use short serialized write transactions and parallel read/compute workers.
Separate bounded queues for CPU analysis, AST helpers and compiler backends;
each compiler host has its own capacity/lock. The existing VM lock remains
authoritative while DAO tools coexist. Async I/O does not make CPU work parallel;
CPU work gets explicitly bounded worker execution and memory limits.

Keep compiler processes and fragile/native analyzers outside the server process.
Batch small analyses and reuse loaded binary indexes/helper processes where safe.
Measure startup, decoding, hashing, AST parsing, compilation and comparison
separately before optimizing. A language change alone does not establish speed.

### Two parts of the manipulation pipeline

| Part | Owns | Must not assume |
| --- | --- | --- |
| Reusable x86 analysis and source manipulation | Instruction effects, register aliases, flags, memory widths, CFG/data flow, supported SharpRetro lifts, paired diagnostics, Clang symbol/AST operations and generic rule application | A particular C++ calling convention, exception layout, CRT helper, compiler flag, game address or code-generation preference |
| Compiler profile | Toolchain/build recipe, target ABI and language extensions, object-symbol conventions, runtime/helper identities, exception/unwind layouts, compiler idioms, and candidate spellings/options for matching | That an idiom seen in one version/flag set holds for another, or that improved similarity establishes acceptance |

The core handles x86 facts such as an instruction reading ECX, updating ESP or
returning with stack cleanup. A compiler profile interprets those facts as a
possible receiver, argument convention or compiler-generated frame. Unresolved
interpretations stay explicit. C++ signedness, aliasing and undefined behavior
still constrain any rewrite; equivalent machine expressions alone do not license
an unsafe C++ transformation.

PE/COFF parsing and relocation records belong to reusable format adapters;
compiler-specific symbol decoration and EH interpretation belong to the profile.
Ghidra export/conversion is a versioned frontend adapter: its pseudocode syntax
is not a property of x86 or of VC8. Clang is the source-analysis/edit backend,
not the authority for the selected compiler's emitted code.

Project configuration supplies the binary, asset paths, symbol/type knowledge,
selected profiles and local tool installations. DAO addresses and historical
compiler paths do not enter generic rule implementations. Reuse of a profile
across games does not imply reuse of a game's inferred signatures or layouts.

Proposed internal interfaces, **not implemented APIs**:

- `IArchitectureAnalysis`: decode/lift effects, compare supported structures and
  report coverage plus unsupported operations.
- `ICompilerProfile`: describe supported ABI/runtime features, create build
  recipes, interpret compiler-specific evidence and provide matching rules.
- `ISourceTransform`: plan bounded symbol/AST edits against a source revision,
  with explicit preconditions, affected dependencies and a candidate result.
- `IDecompilerFrontend`: discover/import functions and emit draft C++ plus
  automatically captured provenance for selected identities or groups.

Compiler profiles consume core analysis and contribute rules through the same
transform interface. The core has no dependency on a VC8 implementation.
Rule metadata records its architecture/frontend/compiler requirements, version
and demonstrated scope. A VC8-derived rule remains profile-scoped until evidence
justifies moving it into the generic layer. This metadata is authored once per
reusable rule, never once per recovered function.

The first compiler profile is the actual selected VC8 x86 toolchain and its
supported options, not a claim of support for every MSVC version. Changing a
profile invalidates the affected proposals/builds/checks. Unsupported profiles
may still permit browsing, drafting and generic diagnosis; they cannot silently
fall back to VC8 behavior or claim a full match.

Extract these boundaries incrementally as operations are added. Initially the
profile delegates to the already reviewed Python compiler/comparison machinery;
do not port or refactor a running sweep just to satisfy a directory diagram.

### Binary-backed, replayable decompilation

Long-term, the durable project is the **original binary plus versioned analysis,
knowledge and transformation history**. Generated C++ is a reproducible output
of that project, with accepted source snapshots retained for publication and
regression comparison. Improving an analysis pass should permit re-decompilation
without discarding names, types or previously established corrections.

The proposed SharpRetro route is:

```text
Pinned binary and inventory/range hypotheses
  → decoded instructions and typed machine effects
  → function CFG, cross-instruction value flow and memory effects
  → recovered variables, calls, types and structured control flow
  → C++ representation
  → compiler-profile lowering/spelling choices
  → emitted C++, historical compiler build and complete comparison
```

Preserve instruction-origin mappings and unresolved facts across every stage.
The intermediate representation above machine effects should be shared across
compiler profiles. Profiles contribute ABI recovery, helper/EH recognition,
object-model interpretation and emission choices at the stages that need them.
Compiler peculiarities cannot all be repaired in a final text writer.

Start with one shared C++ representation/emitter and profile-specific passes.
A separate writer is an option when real compiler differences justify it, while
still sharing analysis, variable identities, transformations and source maps.
Profile investment is reusable across projects using compatible toolchain/runtime
settings; it is not automatically a one-time cost for an entire compiler family.

The inspected SharpRetro pin `ec8344102af8b495e5de1a869188b91bc3d4d756`
exposes per-instruction `IlBlock` effects through `XFusionCpu.X86Lifter`, with
typed registers, memory, arithmetic, branches and explicit opaque/unimplemented
nodes. Our [current integration](../tools/sharpretro/README.md) compares these
trees diagnostically. It does not yet provide the structured C++ reconstruction
described above. Control-flow recovery, cross-instruction definitions/uses,
stack/call recovery, aliasing, C++ integer semantics and exceptions are substantive
work between lifting and emission. Rendering a sufficiently recovered C++ tree
can be straightforward; getting to that tree is not established by lift coverage.

Ghidra remains an available discovery/draft frontend and a retained baseline.
Add SharpRetro as a selectable generation backend for a supported subset first.
Use the same original/function identities, compiler profiles, job system and
comparison machinery for both. No reset of existing source or requirement to
finish a new whole-program decompiler before further recovery.

### Names and corrections survive regeneration

Names, comments, type/layout hypotheses and overrides belong in a versioned
project knowledge layer, with links to the evidence and transformation that
introduced them. This is automatically managed project state, not a new authored
contract or metadata file for each function.

Function identities remain tied to the original module/range model. Recovered
variable identities need more than a register or generated temporary number:
registers and stack slots are reused. Record origin instructions, definition/use
relationships, storage where known and the containing function, then track
lineage as values merge or split. Types and field definitions have independent
stable IDs; display spellings are not their identities.

On regeneration, replay bindings against those origins and transformation
lineages. Preserve a name automatically only when the binding is unambiguous.
A new analysis that splits one variable into two, merges values or changes a
boundary can leave an unresolved migration. Expose it in the work queue instead
of silently attaching an old name or type to the wrong value. Analysis-local
SSA/temp IDs and line numbers are not durable anchors.

Fine-grained user/model edits can target typed IR or AST nodes through the JSON
recipe, with expected base hashes and preconditions. Capture a source edit as a
replayable semantic operation when the binding is understood. Otherwise retain
it as an explicit candidate/body override with a base revision and conflict
status. Regeneration must neither discard hand-written C++ nor pretend an
unreplayable textual edit has been semantically rebased.

Recipe steps therefore declare a phase: machine analysis, recovered IR, C++ AST
or emission. Named dependencies and schema versions constrain their order.
Reject a recipe that uses a recovered-variable operation before variable recovery,
or an old node schema against a new IR. Edits to names/types invalidate the
appropriate downstream views or builds; a new lifter need not erase unaffected
knowledge, but it does require re-establishing affected bindings.

### First SharpRetro generation experiment

Take one previously inspected median-sized function with a supported instruction
subset and retain its Ghidra/C++/object baseline. Implement the smallest reusable
raising/emission steps needed for that shape, then compile and compare through
the existing independent original-byte checker. Unknown instructions, calls,
alias effects or EH remain explicit blockers; no successful placeholder output.

Exercise generic instruction/IR tests and independent evidence for new semantics.
Generating C++ and judging it with the same lifter can reproduce the same defect
on both sides, so lifted-tree agreement is not the acceptance oracle. Record
compile outcome, complete match outcome, diagnostics and elapsed cost separately.
Apply the tested steps to all applicable inventory entries, report outside-example
gains/regressions/unsupported cases, then choose the next shape.

The experiment also needs a regeneration check: attach a name and type decision,
rerun after a supported pass change, and demonstrate both preserved unambiguous
bindings and explicit refusal of an ambiguous split/merge. This tests the durable
workflow benefit rather than merely producing another one-off C++ file.

### MCP covers the complete workflow

Every pipeline operation must be available through the same engine API used by
MCP and the CLI. After one-time trusted installation and local path registration,
an agent should not need repository-specific shell scripts to move a function
from discovery to published source. External decompilers, compilers and analysis
helpers may still run as managed subprocesses.

| Stage | Planned MCP operations | Persisted output |
| --- | --- | --- |
| Initial discovery and decompilation | `project_analyze`, `decompile_start` | Versioned inventory, draft C++ and frontend provenance, including missing/unsupported results |
| Triage across the corpus | `function_query`, `function_inspect`, `corpus_find_related`, `mismatch_summarize` | Compact evidence views and reproducible selections |
| Deterministic iteration | `rewrite_plan`, `rewrite_apply`, `corpus_recheck` | Candidate revisions, complete applicability accounting and affected builds/checks |
| Difficult source repairs | `work_claim`, `candidate_submit`, `work_update` | Independently owned work, submitted C++ and retained outcomes |
| Fine-grained reconstruction and documentation | `rewrite_plan`, `rewrite_apply` | Resolved renames, typedefs, comments, signatures, fields and class proposals with change history |
| Persistent knowledge and regeneration | `knowledge_edit`, `decompile_start` | Named/typed entity decisions, replayed transformations and explicit binding conflicts |
| Compile, compare and publish | `candidate_check`, `source_export` | Compiler products, complete supported comparison results and source/provenance publication |
| Linked/run milestones | `integration_check` | Named build/launch observations with actual covered scenarios and unresolved dependencies |
| Follow or stop any long operation | `job_get`, `job_cancel` | Durable progress, cancellation and interrupted/unknown outcomes |

Tool names are illustrative except for the seven installed tools documented in
the usage guide. The future `candidate_check` accepts newly submitted candidates;
today it only rechecks registered retained builds. The compiler, decompiler and
rule profiles are selectable registered capabilities, not arbitrary shell
commands in tool arguments.

The full loop is `project_analyze` → `decompile_start` → `candidate_check` →
diagnose → `rewrite_plan`/`rewrite_apply` → `corpus_recheck` → `source_export`.
Naming, type reconstruction and explanatory source comments use those same
revision-aware edits and checks. Aliases and annotations retain their evidence
or hypothesis status; a guessed friendly name must not become a verified fact.
Language models can submit proposals through any harness; no built-in paid model
service is required.

An unattended workflow can compose these operations with limits and stop reasons,
but must not have a private acceptance path unavailable to MCP clients. Long jobs
return handles; the agent does not drive each function with repeated tool calls.
Installing custom executable adapters/rules remains an operator action, while
using their typed capabilities belongs in MCP. This avoids making arbitrary code
execution part of routine project requests.

## Project and evidence model

Register originals, source roots, compiler recipes and available adapters once
per project. Paths and private inputs stay local. A new game supplies this
configuration and imported discovery results, not handwritten function packets.

| Record | Essential contents |
| --- | --- |
| Module | Binary hash, architecture, image layout, imports, local artifact reference |
| Function identity | Module hash + RVA; versioned range hypotheses, including noncontiguous ranges |
| Source symbol | Stable symbol ID, aliases/names, versioned type and ABI hypotheses, supporting evidence |
| Candidate | Source snapshot, covered identities, parent candidate/rule, declared dependency snapshot |
| Build | Candidate, compiler/toolchain files, flags, headers/libraries, environment, object artifacts |
| Check | Original/range version, build/object, resolved identities, checker version, complete result |
| Rewrite plan | Base revision, rule/version, edits, affected identities, preconditions and check scope |
| Pipeline recipe | Versioned ordered steps, typed parameters, architecture/compiler requirements and resource limits |
| Trial | Frozen baseline, baseline/proposed recipe hashes, input snapshot, stage deltas and unresolved work |
| Work item | Scope, reason, prerequisites, priority, owner lease, attempts, result references |

An RVA identifies an inventory hypothesis, not a certified function boundary.
Splits, merges and shared tails retain history and invalidate affected checks.
Names and inferred signatures never serve as the durable identity.

Report independent dimensions rather than one ambiguous “done” flag:

- Discovery: indexed, missing source, ambiguous boundary, unsupported analysis.
- Build: not attempted, compiled, rejected, interrupted with unknown outcome.
- Comparison: unchecked, full match, mismatch, inconclusive.
- Source publication: unpublished, published at a named revision, superseded.
- Integration: standalone object, linked milestone, observed executable scenario.

A full match is the output of a named backend over its complete supported scope,
with current inputs and no unresolved required dependencies. For DAO this includes
ordinary full-range object matching and the separately supported complete EH
graph path. A matching main body with unknown exception metadata is insufficient.
Keep similarity, lifted-IL agreement and observed execution as distinct evidence.
None silently promotes a candidate or establishes a runnable game.

Retain multiple candidates. A nonmatch can be a useful starting point even if a
different candidate already matches. Never overwrite the last accepted version
with a failed refactor.

## Finding reusable work across a corpus

The index should support four progressively richer searches:

1. **Exact structural families:** instruction bytes with explicitly recorded
   relocation treatment, argument cleanup, referenced identities and body shape.
2. **Related implementations:** instruction/CFG fingerprints, constant and
   reference patterns, call neighborhoods and compiler-generated helper shapes.
3. **Source patterns:** AST queries over available candidates, such as the same
   receiver error, copy-loop spelling or construction/cleanup pattern.
4. **IL patterns:** typed SharpRetro effects, with per-operation support and
   complete/partial lift coverage visible.

Every result includes why it was selected, the index version and coverage.
Ranking may tolerate differences; acceptance cannot inherit that tolerance.
“Same mnemonic sequence” and “same normalized IL” are search signals, not proof
that code, calling conventions, memory effects or exception behavior agree.

Search within a binary first. Optional cross-project/library indexes can later
suggest previously recovered routines and compiler idioms. A suggested source
must be rebound, rebuilt and checked against the new original independently.
Copying a family label never copies match credit.

Each reviewed generic rule triggers an applicability pass over the **entire
indexed inventory**, including previously unsupported and previously matched
identities. Input absence and inapplicability are recorded, not dropped.
Only changed candidates or invalidated evidence require expensive work.
Rule composition is bounded and deduplicated by resulting source/dependencies;
cycles and exhausted variant budgets leave explicit retained outcomes.

Report unique new matches outside the rule's discovery examples. This is the
primary measure of whether a targeted fix actually generalized.

## Declarative recipes and trial runs

Represent the pipeline as a **versioned JSON recipe: an ordered stack of changes**.
Recipe edits can add/remove/reorder a step or change its typed parameters. Steps
refer to architecture-generic or compiler-profile rules explicitly. The same
recipe is usable from MCP, CLI and unattended execution; there is no parallel
prompt-only description whose behavior drifts from the engine.

Two step forms keep small experiments inexpensive:

- A declarative AST pattern and replacement built from a supported typed node
  vocabulary. Captures refer to resolved symbols/nodes, not matching text.
  Preconditions can constrain types, constants, effects, alias evidence and scope.
  The interpreter must reject unknown nodes, incomplete binding and unsupported
  effects; it cannot guess the intended C++.
- A call to a registered versioned rule with typed parameters for more complex
  analysis or compiler-specific reconstruction. Its implementation and dependency
  hashes are bound to the recipe's execution, not merely its friendly name.

The exact AST vocabulary is implementation work. For example, a local rename
must select a resolved symbol and its uses, not all instances of a spelling.
Changing an integer expression must account for width, promotions and effects,
not assume an algebraic identity is safe C++. Rules that merely propose a
different spelling can emit unvalidated alternatives; JSON is not evidence that
an edit preserves behavior. Arbitrary scripts, shell commands and executable
plugin installation are outside the recipe language.

An illustrative **future** recipe follows. The rule IDs and revision labels are
examples, not installed operations or content hashes:

```json
{
  "schema_version": 1,
  "baseline": "source-snapshot-example",
  "architecture": "x86-32",
  "compiler_profile": "vc8-x86-profile-example",
  "scope": { "inventory": "inventory-snapshot-example", "select": "all" },
  "steps": [
    {
      "id": "orient-branches",
      "kind": "registered_rule",
      "phase": "cpp_ast",
      "rule": "generic.ast.condition-orientation",
      "version": "example-v1",
      "parameters": { "form": "guard-first" }
    },
    {
      "id": "try-copy-spelling",
      "kind": "registered_rule",
      "phase": "cpp_ast",
      "rule": "compiler.vc8.copy-loop-spelling",
      "version": "example-v1",
      "parameters": { "form": "indexed" }
    }
  ],
  "limits": { "variants_per_identity": 4, "compiler_concurrency": 1 },
  "promotion": "none"
}
```

`pipeline_trial` takes the proposed recipe, an exact baseline recipe/source
snapshot, an explicit candidate-selection policy and an idempotency key. It
resolves supported capabilities and freezes actual implementation/input hashes
before scheduling. The result is an isolated candidate branch and durable job.
The default is no source promotion and no model/provider calls.

Steps consume the preceding step's result. Record before/after source hashes,
applicability, precondition failures, generated edits and diagnostics per step.
Keep provenance when multiple steps produce identical output. Bound branching
and composition; exhausted work is pending or budget-limited, not inapplicable.
A removed/reordered step restarts computation from the first invalidated stage;
no later output can retain dependencies on a step that no longer exists.

Trials account for the **entire inventory**, including previous matches,
nonmatches and unsupported identities. All cheap applicability/invalidation
checks run; expensive work runs only for affected distinct outputs or stale
bindings. A compiler/lifter/checker change can invalidate work even if C++ stays
identical. Missing artifacts require work rather than a claimed cache hit.
Explicit budgets can stop a trial, but its report must show what remains untested.

Compare baseline and trial under a named, compatible measurement policy:

| Result | Report |
| --- | --- |
| New full match | Unique identity and complete required scope, including gains outside discovery examples |
| Lost baseline full match | Exact previous candidate and changed result; retain the accepted version |
| Build regression or improvement | Newly failing/compiling identities and diagnostics; include previously compiling nonmatches |
| Mismatch change | Separate diagnostic dimensions such as bytes, ranges, references, CFG/effects and supported EH; do not turn them into acceptance |
| Inconclusive/newly unsupported | Coverage or dependencies lost, timeouts, parse/lift errors and unknown outcomes |
| Cost and coverage | Identities scanned, candidates/attempts, cache reuse, actual compiler time, pending work and measured provider calls |

A stale baseline is not a valid control: revalidate it when the current measurement
requires different bindings, or label that comparison unavailable. A trial that
changes the comparator must not use its own more-permissive verdict as evidence
of an improvement; acceptance changes retain the existing independent tests and
review process. Diagnostic metrics include their versions and incomparable values
remain separate.

`trial_compare` returns aggregate transitions, representative examples and a
paginated identity/step breakdown. It can compare two sibling experiments sharing
the same baseline. Stage records identify where source changed; attributing a
match to one particular step requires checking that intermediate result or an
explicit bounded ablation, not inferring causality from the final output.

The agent can inspect regressions, change the JSON and launch another trial.
`trial_promote` explicitly selects an exact trial revision and scope and rechecks
current publication preconditions. A whole-trial clean result and cherry-picking
individually accepted gains are different actions; neither silently drops
regressions from the report. Keep partial/inconclusive trials and useful nonmatches
available, and never overwrite accepted source with failed experiments.

This is the development loop for pipeline enhancements as well as recovery:
discover a small improvement, encode it once, run it over the corpus, examine
actual deltas, then retain, refine or discard it. A new engine/lifter/plugin build
can be selected by an immutable registered version for a trial; it is not loaded
by mutating the engine used by a live job.

## Proposed MCP surface

These are proposed tool names, not installed commands. Keep structured results
small, with schema versions, immutable references and cursor-based pagination.
Tools use MCP input/output schemas; larger material is exposed through resources
and resource links. This fits the protocol's
[tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)
and [resources](https://modelcontextprotocol.io/specification/2025-11-25/server/resources)
interfaces. Protocol support is negotiated rather than assumed.

| Tool | Inputs and useful result |
| --- | --- |
| `project_open` | Registered project/path → project ID, revision, adapter capabilities and current jobs; does not start paid work |
| `project_analyze` | Registered module, architecture/frontend profiles, analysis limits → discovery/index job with coverage and versioned range hypotheses |
| `decompile_start` | Inventory snapshot, identities/group selector, registered frontend, limits → draft C++ generation job; retain failed/unsupported outcomes |
| `knowledge_edit` | Expected revision, resolved entity IDs, names/type/comment decisions and evidence references → versioned knowledge change, affected stages and unresolved conflicts |
| `function_query` | Project, explicit filters/order/cursor → identities and separate build/check/publication states |
| `function_inspect` | Identity, evidence views, byte/item limits → source, callers/callees, ABI hypotheses, mismatch excerpts and artifact links |
| `corpus_find_related` | Identity or typed pattern, index kind/scope → ranked related functions, selection reasons and coverage |
| `candidate_submit` | Source or workspace patch, target identities, base revision, optional work claim → immutable candidate; no automatic match claim |
| `candidate_check` | Candidate, registered build/check profile, limits → durable job for compile/reuse, full comparison and diagnosis |
| `mismatch_summarize` | Explicit corpus/candidate-selection snapshot → distance distributions, overlapping symptoms, unknowns and examples |
| `rewrite_plan` | Candidate/project revision, registered rule or structured refactor, scope → generated edits, preconditions, affected set and check plan |
| `rewrite_apply` | Plan ID and expected revision → isolated candidate revision plus check job; optional promotion on complete success |
| `corpus_recheck` | Rule/input change, inventory snapshot, limits → incremental whole-inventory job and measurable outside-discovery yield |
| `pipeline_trial` | Baseline snapshot/recipe, proposed JSON recipe, candidate-selection policy and limits → isolated experiment job with whole-inventory accounting |
| `trial_compare` | Trial(s), baseline, result filters/cursor → gains, regressions, diagnostic changes, costs, coverage and pending work |
| `trial_promote` | Exact trial revision, selected scope, expected publication revision → current-check-gated promotion; no implicit adoption of all experimental rules |
| `work_claim` | Capabilities, scope/priority preferences, lease duration → atomically owned work with compact context |
| `work_update` | Claim/fencing token, operation (`heartbeat`, `submit`, `block`, `release`) → durable transition; cannot assert a match |
| `job_get` | Job ID, event cursor, bounded wait → current counts, new events, errors and result links |
| `job_cancel` | Job ID → cancellation requested; eventual status distinguishes stopped, completed and unknown external outcome |
| `source_export` | Accepted revision/set, expected publication revision → source/provenance export or precise current-binding refusal |
| `integration_check` | Source revision, registered build/launch profile, execution limits → linked or observed-run milestone; no implicit success for unresolved calls/assets |

Selectors and rewrite operations have typed, bounded schemas. Do not expose
arbitrary SQL, shell commands or code evaluation as the public query interface.
Custom rules are versioned engine extensions developed and tested once, not
arbitrary execution supplied in each tool request.

Resource examples:
`decomp://projects/{id}/snapshots/{revision}/functions/{identity}`,
`decomp://artifacts/{digest}`, and `decomp://jobs/{id}/events/{cursor}`.
Resources resolve only within the authorized project and return bounded views;
an explicit local export retrieves large artifacts. Source/binary contents are
data, never instructions to the agent. Raw proprietary bytes are not included in
ordinary tool summaries or public source exports.

Long operations return a persisted `job_id` promptly. Optionally expose
[MCP task-augmented execution](https://modelcontextprotocol.io/specification/2025-11-25/basic/utilities/tasks)
when negotiated; engine durability must not depend on a client's task support.
Reading a job never dispatches it again.

## Incremental execution and cache rules

Cache individual stages, not an undifferentiated “function passed” bit:

| Change | Required work |
| --- | --- |
| New rewrite rule | Rescan applicability across inventory; generate/check only distinct new candidates |
| Source, header, flags, compiler or target ABI | Rebuild affected translation units, then recheck their identities |
| Original range, symbol resolution or comparison implementation | Recompare affected retained objects; rebuild only if build inputs also changed |
| Lifter or diagnostic classifier | Recompute affected diagnostics; preserve separate prior matching evidence |
| Display alias only | Update display/search index; no compiler claim changes |

Stage keys bind actual content and transitive dependencies, tool versions,
configuration, original identities/ranges and target environment. Missing
artifacts or an incomplete dependency closure invalidate reuse. A changed engine
release need not invalidate unrelated stages, but untracked dependencies cannot
be treated as unchanged. Store manifests automatically.

Jobs use idempotency keys, atomic claims and fenced writes. Expired leases cannot
overwrite newer work. An interrupted external compiler/provider operation remains
unknown until its receipt is reconciled; do not blindly retry it. Pure local
analyses can be retried under a bounded policy with their old attempts retained.
Cancellation and budget exhaustion never become successful checks.

The queue supports breadth across independent groups and depth inside a claimed
caller/callee or source slice. Blocked groups do not block the whole project.
Overlapping shared-type/source edits serialize at the transaction boundary.
Models consume queue items through their chosen harness; the default server
makes no model calls. Optional provider workers later share explicit project
budgets and request accounting, with no implicit service enrollment.

## AST refactoring without losing recovered behavior

The source editor uses Clang's parsed symbols and source ranges, not global
regular-expression replacement. The analysis compile configuration records all
compatibility shims and differs explicitly from the authoritative historical
compiler. Failure to parse an old extension is an unsupported edit, not permission
to guess. Start with edits that avoid macros and unresolved symbol ambiguity.

Support three distinct operations:

| Operation | Scope and validation |
| --- | --- |
| Display name / annotation | Changes only project metadata; original evidence remains attached to stable IDs |
| Source rename / equivalent typedef | Updates resolved uses, redeclarations and affected units; rebuild and recheck before promotion |
| Signature, signedness, calling convention, field layout or class reconstruction | Changes an ABI/type hypothesis; include callers, shared declarations, layouts and generated code in the affected closure |

Class reconstruction is not just renaming `void*`: receiver placement, inheritance,
packing, vtables, construction/destruction and EH can change emitted behavior.
Offer it after simpler refactors work; incomplete use/alias coverage prevents
automatic promotion. Unproven alternatives remain inspectable draft revisions.

Every edit follows the same transaction:

1. Preview exact edits and generated dependency closure at a fixed base revision.
2. Apply into an isolated source revision; reject stale plans or overlapping edits.
3. Reparse, build and check the affected closure, preserving original inputs.
4. Atomically promote only when the configured check requirements hold.
5. Otherwise retain the candidate and diagnostic; the accepted revision stays intact.

Existing nonmatches are allowed in the project. A refactor can be kept as a draft
without claiming their equivalence; it cannot silently replace accepted source
whose current full match was lost. Similarity improvement is useful feedback,
not a substitute for the promotion rule.

## First end-to-end workflow

An agent asks for a median-size nonmatch with a common diagnostic. It inspects
one candidate and its references, then proposes a bounded AST rule. Generic tests
and a real-compiler pilot establish the rule's preconditions; independent review
is for new transformation/checking machinery, not a manual packet per function.

Once registered, `corpus_recheck` checks that rule against every indexed identity.
The engine caches no-op decisions under their exact inputs, builds new variants,
compares full required ranges/dependencies and exports new accepted source.
The agent receives counts and representative remaining differences rather than
thousands of full reports. Difficult subgroups become queue work.

Later the agent uses `rewrite_plan` to introduce a name or typedef. It sees the
actual affected uses and required rebuild set; `rewrite_apply` runs the same
checks before updating accepted source. Both workflows reuse one artifact and
revision model.

Example **illustrative request**, with no claimed results:

```json
{
  "tool": "corpus_recheck",
  "arguments": {
    "project_id": "dao",
    "inventory_snapshot": "inventory-v1",
    "rule_set_revision": "reviewed-rules-v7",
    "scope": "all",
    "limits": {
      "max_variants_per_identity": 4,
      "compiler_concurrency": 1
    },
    "idempotency_key": "inventory-v1-rules-v7"
  }
}
```

The returned job reports total indexed, scanned, missing inputs, inapplicable,
unchanged, new candidates, cache reuse, builds, full comparisons, mismatches,
inconclusive results, new full matches and exported sources. Counts identify
whether they measure identities, candidates or attempts. It also reports new
matches outside discovery examples, coverage by body bytes, elapsed/CPU/compiler
time and measured provider spend. A zero-provider run still has development cost.

## What exists and what needs work

This map describes the repository at design time. Existing modules are useful
adapters, not already portable implementations of the proposed API.

| Capability | Existing basis | Remaining work |
| --- | --- | --- |
| Inventory and coherent function groups | [`catalog.py`](../rapid_object/catalog.py) | Extract DAO-specific paths, schema and entry priorities into project configuration |
| Independent historical-compiler builds | [`build.py`](../rapid_object/build.py) | Registered backend recipes, generic dependency manifests and host capacity |
| Full object comparison and strict symbol identity | [`compare.py`](../rapid_object/compare.py), [`symbol_identity.py`](../rapid_object/symbol_identity.py) | Stable adapter result schema; retain unknowns and full-range requirements |
| Bounded EH graph acceptance | [`eh_native.py`](../rapid_object/eh_native.py), [`eh_graph_compare.py`](../rapid_object/eh_graph_compare.py) | Advertise actual supported profiles, not generic EH support |
| Mismatch diagnosis and paired IL | [`mismatch.py`](../rapid_object/mismatch.py), [SharpRetro adapter](../tools/sharpretro/README.md) | Queryable indexes and incremental diagnostic jobs; IL remains diagnostic |
| SharpRetro-generated C++ | Existing typed instruction effects and paired-lift diagnostics | Shared recovered IR, variable/call/control-flow reconstruction, compiler hooks and source emission; evaluate a supported subset first |
| AST proposals and reusable repairs | [`ast_match.py`](../rapid_object/ast_match.py) and individual reviewed rules | Uniform rule interface and Clang helper; project-wide refactors are new work |
| Durable model work queue | [`queue.py`](../rapid_object/queue.py), [`store.py`](../rapid/store.py) | Separate general work ownership from provider-specific execution |
| Whole-inventory rule propagation | Active `local/rule-recheck-001` work | Measure/test/review current work before treating it as an adopted adapter |
| Verified source export | [`export_ast_matches.py`](../tools/export_ast_matches.py) and EH exporter | One publication interface preserving backend-specific checks |
| Corpus families / cross-project reuse | Partial instruction, reference and mismatch information | New indexed search and explicit uncertainty; no inherited match credit |
| Portable C# core and MCP | [`tools/decompilation-mcp`](../tools/decompilation-mcp) | Extend the implemented retained-artifact read/check slice with the operations above |
| JSON pipeline trials | Revision/job model and existing rule interfaces | Typed recipe interpreter, isolated stage cache, comparative reports and explicit promotion |

## Delivery sequence

**First slice, implemented: a usable retained-artifact read/check loop.** The C#
CLI and stdio MCP open the existing DAO project, query/inspect candidates, run
current comparison adapters and return durable compact results. This slice
does not perform new compilation. It imports retained data without taking
production queue ownership and tests second-client/restart behavior.

**Second slice: a complete draft-to-check loop.** Introduce the architecture,
frontend, transform and compiler-profile interfaces while adapting existing
Ghidra and VC8 operations. Expose discovery/decompilation, candidate submission
and new compilation through jobs. Demonstrate draft C++ becoming a freshly built,
fully compared object entirely through MCP, without private operator scripts
between stages. Preserve nonmatches for iteration. Add the bounded SharpRetro
generation/regeneration experiment through the same frontend interface; broader
support follows measured results, not an up-front replacement of Ghidra.

**Third slice: one fix reaches the corpus.** Adopt the reviewed recheck adapter,
register existing generic/profile-scoped rules, and expose them as JSON recipe
steps. Add isolated `pipeline_trial`/`trial_compare` over the same incremental
recheck engine before automatic recipe rollout. Cache stage results and export
verified selected gains. Add richer related-function search and mismatch summaries
over those same records. Measure regressions, pending work, new matches outside
discovery cases and cache savings.

**Fourth slice: maintainable source.** Add transactional rename and typedef
refactors through Clang, then evidence-backed signature/layout/class operations.
Keep unvalidated refactors available without replacing accepted source. Link/run
profiles expose integration milestones through the same job interface as actual
reconstruction permits; none is implied by a successful function check.

**Portability check throughout.** Exercise a small openly distributable Windows
C++ fixture project with known symbols and several function/ABI/EH shapes.
Remove DAO constants from adapter configuration. The fixture tests the machinery;
it is not a claim that arbitrary Windows applications are supported. Generic
analysis/transform tests must run without loading VC8. Separately verify rejection
of unsupported profiles and profile-driven invalidation. A second real compiler
profile is a later portability test, not an assumed capability of the first one.

Do not make a new decompiler, universal equivalence solver, whole-game loader,
distributed cluster, vector database or bundled model provider prerequisites.
Existing external Ghidra/SharpRetro/compiler installations remain adapters, with
versions and capabilities reported. Never redistribute proprietary compilers,
game binaries or assets as part of the toolkit.

## Acceptance for the framework itself

- Repeated identical requests reuse the same work; reconnects and expired leases
  cannot duplicate compilation or publish stale edits.
- A rule change accounts for the complete inventory, including missing inputs;
  controlled mutations demonstrate the required cache invalidation.
- Partial ranges, unresolved required relocations, unsupported EH/lifts, deleted
  artifacts and interrupted transport remain nonaccepting outcomes.
- AST edits preserve identities through naming changes and reject stale bases,
  unresolved uses and conflicting edits; failed checks preserve accepted source.
- One complete demonstrated path goes from targeted rule to outside-discovery
  full matches and exported C++, with reproducible measurements.
- A protocol-level workflow starts from registered binary inputs, produces
  drafts, submits/rebuilds/checks candidates, applies a reusable rule, rechecks
  the corpus and exports source without hand-running intermediate scripts.
- Compiler-profile assumptions are absent from generic transforms; unsupported
  ABI/runtime features and incompatible profile changes cannot reuse acceptance.
- Source naming, type edits and documentation use the same recorded transactions
  as matching repairs, with failed edits retained and accepted source preserved.
- Recipe trials are reproducible and isolated; removing/reordering/changing a
  step invalidates downstream results. Whole-inventory reports retain losses,
  unknowns and unrun work alongside gains, and default to no promotion.
- Re-decompilation preserves unambiguous names/types through recorded entity
  lineage, reports ambiguous binding changes and preserves source overrides.
  Results generated from SharpRetro are checked independently of its lifted trees.
- A clean installation can exercise the open fixture without DAO paths, private
  binaries, proprietary compiler redistribution or a model API credential.

The first implementation should optimize for that complete loop. Its value is
measured in reusable fixes, avoided repeated work and reliable source evolution,
not the number of exposed tools.

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
| `function_query` | Project, explicit filters/order/cursor → identities and separate build/check/publication states |
| `function_inspect` | Identity, evidence views, byte/item limits → source, callers/callees, ABI hypotheses, mismatch excerpts and artifact links |
| `corpus_find_related` | Identity or typed pattern, index kind/scope → ranked related functions, selection reasons and coverage |
| `candidate_submit` | Source or workspace patch, target identities, base revision, optional work claim → immutable candidate; no automatic match claim |
| `candidate_check` | Candidate, registered build/check profile, limits → durable job for compile/reuse, full comparison and diagnosis |
| `mismatch_summarize` | Explicit corpus/candidate-selection snapshot → distance distributions, overlapping symptoms, unknowns and examples |
| `rewrite_plan` | Candidate/project revision, registered rule or structured refactor, scope → generated edits, preconditions, affected set and check plan |
| `rewrite_apply` | Plan ID and expected revision → isolated candidate revision plus check job; optional promotion on complete success |
| `corpus_recheck` | Rule/input change, inventory snapshot, limits → incremental whole-inventory job and measurable outside-discovery yield |
| `work_claim` | Capabilities, scope/priority preferences, lease duration → atomically owned work with compact context |
| `work_update` | Claim/fencing token, operation (`heartbeat`, `submit`, `block`, `release`) → durable transition; cannot assert a match |
| `job_get` | Job ID, event cursor, bounded wait → current counts, new events, errors and result links |
| `job_cancel` | Job ID → cancellation requested; eventual status distinguishes stopped, completed and unknown external outcome |
| `source_export` | Accepted revision/set, expected publication revision → source/provenance export or precise current-binding refusal |

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
| AST proposals and reusable repairs | [`ast_match.py`](../rapid_object/ast_match.py) and individual reviewed rules | Uniform rule interface and Clang helper; project-wide refactors are new work |
| Durable model work queue | [`queue.py`](../rapid_object/queue.py), [`store.py`](../rapid/store.py) | Separate general work ownership from provider-specific execution |
| Whole-inventory rule propagation | Active `local/rule-recheck-001` work | Measure/test/review current work before treating it as an adopted adapter |
| Verified source export | [`export_ast_matches.py`](../tools/export_ast_matches.py) and EH exporter | One publication interface preserving backend-specific checks |
| Corpus families / cross-project reuse | Partial instruction, reference and mismatch information | New indexed search and explicit uncertainty; no inherited match credit |
| Portable C# core and MCP | This proposal | Implement, package and test |

## Delivery sequence

**First slice: a usable read/check loop.** A C# CLI and stdio MCP open the existing
DAO project, query/inspect candidates, run the current build/check adapters and
return durable compact results. Import retained data without duplicating live
queue ownership. Establish second-client/restart behavior early.

**Second slice: one fix reaches the corpus.** Adopt the reviewed recheck adapter,
register existing rules, cache stage results and export verified gains. Add
related-function search and mismatch summaries over those same records.
Measure new matches outside discovery cases and cache savings.

**Third slice: maintainable source.** Add transactional rename and typedef
refactors through Clang, then evidence-backed signature/layout/class operations.
Keep unvalidated refactors available without replacing accepted source.

**Portability check throughout.** Exercise a small openly distributable Windows
C++ fixture project with known symbols and several function/ABI/EH shapes.
Remove DAO constants from adapter configuration. The fixture tests the machinery;
it is not a claim that arbitrary Windows applications are supported.

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
- A clean installation can exercise the open fixture without DAO paths, private
  binaries, proprietary compiler redistribution or a model API credential.

The first implementation should optimize for that complete loop. Its value is
measured in reusable fixes, avoided repeated work and reliable source evolution,
not the number of exposed tools.

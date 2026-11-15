# Manual recovery workbench

The current focus is improving individual C++ functions, names and guest layouts.
Startup/playtesting is paused. The console workbench does not invoke models, launch
workers, alter the oracle, or promote recovered functions into the accepted registry.

Run it with `.venv/bin/python -m tools.recomp_workbench`. Follow the
[recompiler setup](../recompiler/README.md#whole-module-generation-and-compilation)
to produce a baseline compilation from your local copy of the pinned game.
The workbench needs clangd/clang++
for semantic refactoring, and the compiler pinned by the baseline compilation for
candidate checks. On the current Mac, that is LLVM-MinGW targeting Windows x86.

## Start from a pinned compilation

```sh
.venv/bin/python -m tools.recomp_workbench init \
  --compilation "$COMPILATION_RUN"
.venv/bin/python -m tools.recomp_workbench catalog --module main --max-instructions 80 --limit 20
.venv/bin/python -m tools.recomp_workbench checkout --module main --rva 0x1000
.venv/bin/python -m tools.recomp_workbench packet --module main --rva 0x1000 \
  --output local/recovery/function-packet.json
.venv/bin/python -m tools.recomp_workbench symbols --module main --rva 0x1000
```

The default workspace is `local/recovery/workbench`. Use the global `--workspace`
option **before** the subcommand to select another. All game-derived function source,
instruction records and packets belong under ignored `local/`.

The baseline currently catalogs 63,612 generated bodies/fragments across main and
Umbra. This is a generated compilation inventory, not a claim of complete original
function discovery or behavioral correctness. Failed generation entries remain
outside that compilation; catalog selection does not invent successful replacements.

Checking out a function copies its source into `functions/` and records the binary
SHA-256, module and RVA, original source/metadata hashes and stable dispatcher
symbols. Generated cache files are never edited. `blobs/` retains immutable old and
new source bytes; `plans/` and `receipts/` retain changes and compiler reports.
Rechecking out a function preserves existing work.

## Rename a symbol, or record a type hypothesis

Use the current packet's `view_sha256` and a declaration from `symbols` to create a
request. Positions are **1-based UTF-16** line/column coordinates in that exact source
view. Several renames can be proposed together against one unchanged view:

```json
{
  "view_sha256": "COPY_THE_CURRENT_PACKET_VIEW_HASH",
  "renames": [
    {"line": 19, "column": 35, "new_name": "saved_esi_bits"}
  ],
  "hypotheses": [
    {
      "kind": "type_proposal",
      "origin": "COPY_THE_OBSERVED_VARIABLE_ORIGIN",
      "proposed_type": "std::uint32_t",
      "evidence": "Explain the instruction bytes, width and uses supporting this guess",
      "status": "unreviewed hypothesis"
    }
  ]
}
```

```sh
.venv/bin/python -m tools.recomp_workbench plan --module main --rva 0x1000 \
  --request local/recovery/request.json
.venv/bin/python -m tools.recomp_workbench check --plan local/recovery/workbench/plans/PLAN_SHA.json
.venv/bin/python -m tools.recomp_workbench apply --plan local/recovery/workbench/plans/PLAN_SHA.json
```

`plan` returns the actual immutable plan filename and a diff. `apply` also runs
the compiler checks, so a separate `check` is optional. A failing compile, ABI
check or stale view leaves committed source and metadata unchanged. Identical edit
ranges are deduplicated; conflicting overlapping refactors require separate plans.

clangd resolves the selected declaration and its references within the owned C++
file. Shadowed variables, strings and comments are not textually substituted.
Edits to runtime headers or other files are refused. The stable `fn_...` and
`fn_..._step` entry symbols stay fixed; human function names can be naming hypotheses
or private helpers. Rename edits are resolved in both the portable profile and the
pinned compiler's native target profile, then merged against the same source. This
covers native-only references in generated Windows x86 branches. The pinned driver
and its recorded dependencies are hash-checked before clangd is permitted to query
its system includes. Project-wide rename, macro-generated identifiers and branches
inactive in **both** profiles remain outside this version's guarantee.

For a uniquely named generated temporary, rename provenance includes the original
IL origin (instruction RVA, expression fingerprint and temporary number), the
selected compiler symbol and the exact source hash. A shadowed/ambiguous name stays
unmatched. Body replacement invalidates automatic source-name lineage; coincidentally
reusing a name does not establish the same original variable. IL temporaries are not
automatically reconstructed high-level source variables.

Type proposals can be submitted without `renames`. They persist as metadata; they
do not silently narrow storage, convert guest addresses to host pointers, or infer
function signatures. Applying a C++ type change uses the source or header workflow.
Compiler success alone cannot check aliasing, wraparound, layout or FP equivalence.

## Shared program type registry

Build the read-only program index once for each pinned generation:

```sh
.venv/bin/python -m tools.recomp_queries --workspace local/recovery/workbench build
.venv/bin/python -m tools.recomp_queries --workspace local/recovery/workbench callees --module main --rva 0x16ad0
.venv/bin/python -m tools.recomp_queries --workspace local/recovery/workbench callers --module main --rva 0xc2480
.venv/bin/python -m tools.recomp_queries --workspace local/recovery/workbench fields --offset 0x18 --width 32
```

Other queries are `function` (authenticated metadata and optional bounded source),
`walk`, `search`, `references`, `bytes`, and `string`. RVAs and addresses on the
CLI are hexadecimal. Lists include total counts, `start` and truncation; page
through them using `--limit` and `--start`. References are syntactic hexadecimal
operand candidates, including scalar immediates; they do not establish pointers.
Original-byte/string queries refuse ranges without a unique file-backed mapping.
The index covers generated-only baseline entries and reports catalog exclusions;
its static graph cannot establish dynamic reachability or function completeness.
Function results also expose authenticated recorded-workspace source blobs and
their hypotheses when a function has been checked out. These are separate from
the pinned generated source. Shared bindings and method associations appear in
function results even when an associated method has no observed object view yet.

Cross-function layouts and object bindings live in workspace `types.json`; the
generated guest-view header is `include/program_types.hpp`. Query it with
`.venv/bin/python -m tools.recomp_types --workspace local/recovery/workbench list`,
or use `show --type TYPE_ID`, `uses --type TYPE_ID`, and `methods --type TYPE_ID`.
Function packets include the registry revision, known type IDs, and bindings for
that function without recursively embedding the full registry. Query original
instruction bytes, function metadata, and callers/callees through
`tools.recomp_queries` before proposing cross-function relationships. Record the
specific binary, function and object origins with evidence. Shared type names,
fields, inheritance and method associations remain hypotheses until reviewed.
Exports authenticate `types.json` and record its hash and revision summary.

Workers write requests and evidence in their assigned directories. A coordinator
reviews them and runs:

```sh
.venv/bin/python -m tools.recomp_types --workspace local/recovery/workbench propose --request reviewed-types.json
.venv/bin/python -m tools.recomp_types --workspace local/recovery/workbench check --plan PLAN_FILE
.venv/bin/python -m tools.recomp_types --workspace local/recovery/workbench apply --plan PLAN_FILE
```

Requests contain `expected_revision`, `types`, and `bindings`. Each type has a
stable `id`, C++ `name`, `kind` (`struct` or `class`), explicit `fields`, and
nonempty `evidence` records containing a `reason`. Fields have stable IDs, names,
signed byte offsets, observed bit widths, and scalar types (`u8` through `u64`,
signed equivalents, `f32`, `f64`, or `ptr32` with an existing target type ID).
Unknown allocation size is `null`. Overlapping fields are preserved as separate
accesses. `methods` associate named roles with pinned function IDs; optional
`vtables` bind slot indices to checked original words and pinned functions or
explicit unknown target addresses. These associations do not infer source ABI.

Bindings specify pinned `function_id`, exact `object_origin`, `type_id`, evidence,
and `field_map` from every observed field origin to a shared field ID. Offset and
width mismatches fail. `view_name`, if supplied, is the **existing** generated
struct identifier. `lower: false` records a hypothesis without changing source.
Lowered bindings require unchanged generated view bodies; manual edits cannot
silently disappear. Nested pointer-follow views currently require metadata-only
bindings. Matching offsets alone never merge classes or object instances.

Shared declarations are guest-memory views, with explicit 32-bit addresses and
base-subobject offsets. They do not impose a host allocation layout or guess a
native C++ vptr or inheritance ABI. Legacy accessors preserve existing bit-level
source behavior while named accessors expose the reviewed interpretation. A type
or field rename retains its stable ID. Type plans reject stale sources, headers
or registry revisions and compiler-check all checked-out functions before
committing the shared update. Compiler checks do not validate original behavior.

## Clean generated expressions

```sh
.venv/bin/python -m tools.recomp_workbench cleanup --module main --rva 0x1040
```

This returns an unapplied source plan, using the same check/apply workflow. It
requires the pinned unsigned 128-bit `bits`, `mask` and `narrow` helper contract.
It composes constant-width nested masks, folds constant masks and zero high halves
of literal construction, removes redundant argument parentheses, and formats C++
with clang-format. Use `--no-format` to omit formatting. Comments, strings, raw
strings and preprocessor definitions are preserved.

For example, the emitted expression
`narrow((narrow((narrow((read_gpr_mask(s,6,0xffffffffULL)),64)),32)),64)`
becomes `narrow(read_gpr_mask(s,6,0xffffffffULL),32)`. The result remains the unsigned
bitvector helper's result type. Evaluation occurs once. Arithmetic lambdas containing
multiple operations or reads remain in place; memory order, exception handling,
guest register/segment widths, budget checks and dispatch entry points are retained.

The coordinator compares optimized compiler output before applying these plans.
The startup campaign kept seven initial cleanups and two later helper cleanups
unapplied when that output differed. An experimental register/literal lambda fold
also changed output and was retained only as an opt-in experiment outside the
workbench cleanup command. These deferrals are not behavioral counterexamples or
accepted changes.

## Rewrite a function in an editor

Either write a separate candidate file and submit `replacement_file`, or edit the
checked-out file and use `adopt`. A replacement request has this shape:

```json
{
  "view_sha256": "COPY_THE_CURRENT_PACKET_VIEW_HASH",
  "replacement_file": "/absolute/path/to/local/recovery/candidate.cpp",
  "supported_rvas": [4096],
  "hypotheses": [{"kind": "rewrite", "status": "unvalidated", "evidence": "Describe the intended contract and unresolved behavior"}]
}
```

For editor changes, omit `replacement_file` and run:

```sh
.venv/bin/python -m tools.recomp_workbench adopt --module main --rva 0x1000 \
  --request local/recovery/rewrite-request.json
```

`adopt` captures the draft as an immutable blob, restores the previously committed
working file and returns an unapplied plan. Review/check/apply that plan as above.
The draft remains retained even if its eventual compilation fails. Ordinary packet
and export commands refuse unrecorded direct edits.

`supported_rvas` is mandatory for body replacements. It must include the original
entry and can include only published instruction starts from that function. The
current dispatcher can resume at interior instructions, including call continuations
and budget boundaries. Declaring entry-only support does not support those resumes.
The linked registry retains all original published addresses, but a generated guard
throws explicitly on an unsupported entry into the candidate. It never returns a
successful stub or falls back to original code. Declaring an entry supported remains
a candidate claim to validate, not evidence that its semantics are correct.

Both dispatcher signatures must still compile. Private helpers may have recovered
source signatures, but the external adapters must preserve machine state, memory,
exit and budget behavior required by callers. Unknown signatures remain unknown in
the packet's ABI observations.

## Shared layouts and regeneration

Only the coordinator edits `include/recovered_types.hpp`. Prepare a self-contained
header with explicit guest widths and layout checks, then submit:

```sh
.venv/bin/python -m tools.recomp_workbench header-plan \
  --replacement local/recovery/proposed-types.hpp --expected-sha CURRENT_HEADER_SHA
```

The expected hash is in `workbench.json`. Applying a header plan checks **every**
checked-out function and invalidates their old views. Worker packets own only one
function file; unrelated function commits do not invalidate each other's views.
There is no automatic merge of conflicting edits to the same function or header.

Generating another source inventory does not overwrite this workspace. To carry
its candidates to a new compilation:

```sh
.venv/bin/python -m tools.recomp_workbench rebase \
  --compilation /absolute/path/to/new/compilation/run \
  --output local/recovery/next-workbench
```

The binary/module identities must agree. The old workspace remains intact. The
new workspace retains drafts, carried shared type specifications and **unapplied**
function plans. Old active bindings move to `pending_bindings` with their previous
baseline identity and `requires review`; they are never rebound automatically.
Custom headers are copied by relative path, while the new compilation's pinned
runtime header remains authoritative. The copied generated program type header
hash is recorded against the rebased registry.
It reports absent identities, changed generated baselines and removed entry support.
Review those plans against the new instruction/ABI observations, then check/apply
them. There is no guessed textual merge or inferred origin correspondence across
changed generations. Runtime incompatibilities still need manual repair.

## Export into the replacement build

```sh
.venv/bin/python -m tools.recomp_workbench export --output local/recovery/exports/pass-001
.venv/bin/python -m tools.recomp_bulk_build \
  --generation local/recomp/bulk/runs/1794303437453953000 \
  --output local/recomp/manual-compile \
  --overrides local/recovery/exports/pass-001/manual-overrides.json
```

Export checks all checked-out sources and publishes a fresh, hash-bound directory.
The bulk compiler replaces only those C++ files; every other generated body stays
in the build. It records **both** the original generated source hash and the manual
candidate hash. The linker authenticates both identities and applies interior-entry
guards. A shared-instruction ownership plan must be bound to the export's original
baseline compilation inputs, whose decoding evidence it describes; candidate object
and link evidence remain bound to the new compilation inputs. No function is dropped
to resolve an overlap. Use the existing bulk-link preparation/finish workflow with
the newly produced compilation run.

These reports establish syntax/ABI checking and provenance, not behavioral
equivalence. Original-byte evidence, reviewed contracts, differential validation and
integration observations remain necessary. Existing acceptance records are untouched.

## Preparing small agent jobs

The coordinator selects small functions with `catalog`, checks out disjoint files
and writes bounded packets (`packet --max-bytes`, default 128 KiB). Oversized packets
fail explicitly rather than truncating evidence. Each worker receives one packet
and returns a request against its view hash. Workers propose shared layouts instead
of editing them; the coordinator reviews/applies the plans. A later change to one
function leaves other function packets valid unless shared types change.

The CLI does not itself start agents or incur inference costs. With explicit user
authorization, the coordinator can direct Luna workers in disjoint packet batches;
the first campaign is recorded privately under `local/recovery/fleets/`, with
`local/recovery/fleet-latest.json` identifying it. Workers write proposals only.
The coordinator retains submissions, rejects unsupported origins/layout claims,
corrects address/value confusion and applies reviewed workbench plans. The initial
campaign additionally checks exact optimized LLVM output equality at the pinned
Windows x86 compiler settings before committing source renames or local declaration
type refinements. This does not establish original-binary or game equivalence.

Fixed-width local refinements preserve the lifted expression's observed width;
they do not infer source signedness or convert address bits to host pointers.
Any candidate that changes compiler output stays unapplied for separate review.
An unattended worker launcher, automatic behavioral validation of arbitrary rewrites
and 64-bit ABI migration remain subsequent work.

### First Luna campaign (November 10, 2026)

Three explicitly authorized `gpt-6-luna` workers completed nine disjoint packet
batches: 30 main-executable functions and 30 Umbra functions. Coordinator review
integrated 188 rename operations and refined 160 local declarations to the observed
32/64-bit unsigned IL representation across 51 functions. This does not establish
source-level signedness or turn guest addresses into host pointers. A further five
typing candidates changed optimized LLVM output and remain unapplied for review.
The reports also retain 195 type hypotheses and 30 observed-field layout hypotheses;
class identities, total object bounds and source signatures remain unresolved.

Every applied rename plan and local type refinement produced exactly equal optimized
LLVM output before/after at the pinned Windows x86 compiler settings. The exported
61 function objects (including the earlier manual example) compiled together using
LLVM-MinGW on macOS ARM64. The full tooling run completed 391 tests: 390 passed and
one skipped because the composition native build was absent. All six host C++ checks
and both synthetic demo commands also passed. These are candidate/compiler and
infrastructure results, not original-binary or gameplay validation.

The larger generated inventory is recorded in `local/recovery/fleet-queue.json`:
63,551 entries remain unassigned, in addition to the 60 reviewed entries and the
earlier manual example. The first campaign's workers have finished; queued entries
are not background jobs. Private submissions, rejected proposals, plans, compiler
comparison hashes, CMake inputs/objects and final reports are retained under the
directory named by `local/recovery/fleet-latest.json`.

### Walking outward from startup

The next campaign starts at the pinned PE entry RVAs, main `0x4e3024` and Umbra
`0xcb9b1`. The read-only static index follows direct calls/tail transfers between
exact compiled entries, distinguishes local control flow, and records imports,
indirect calls, overlapping-entry ambiguities and unresolved targets separately.
It is bounded to depth four and 350 bodies; the current index has 202 bodies and
171 unresolved cases. It establishes a static neighborhood, not measured startup
reachability or complete indirect-call coverage.

Related packets carry original instruction bytes, IL definitions, exact declaration
positions, caller/callee paths, authenticated import names and explicitly provisional
role notes. Large sources stay available by full path/hash, with bounded excerpts
in packets. The main path proceeds through a cookie-initialization pattern and CRT
startup to application-entry candidate RVA `0x16ad0`. Original-file-backed strings
include `DAUpdater.exe` and `-autoload`; their presence is evidence, while their
meaning and the source signature remain hypotheses to review. Subsequent batches
inspect that routine's direct helpers and Umbra's initialization dispatcher family.

The campaign, graph/controller, raw submissions, review decisions, cleanup plans,
compiler comparisons and source exports are under the directory named by
`local/recovery/startup-walk/latest.json`. Startup/playtesting stays paused during
this source recovery work.

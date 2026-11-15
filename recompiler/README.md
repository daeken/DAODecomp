# Iterative SharpRetro recovery (`recomp`)

This is the fresh recovery pipeline. The controller is a short-lived console app:
`python3 -m tools.recomp`. It builds a small .NET bridge against the sibling
`SharpRetro/Decompiler` checkout. It does not require an MCP server or model worker.
The existing recovery registry and acceptance workflow are separate.

The implementation emits **selected bounded PE32 functions**, one C++
translation unit per selection, plus a common runtime, declarations and CMake
library and diagnostic-executable targets. It uses SharpRetro's machine-state backend with explicit
registers, flags, segment bases and a bounded guest-memory interface. These are
instruction-local values, not recovered source-language variables or signatures.
The high-level Windows x64 emitter has not been made into a PE32 ABI implementation.
`recomp_image` links every selected translation and lists its guest address.
Linked views can load original non-executable data and resolve guest vtables and
imports to the compiled address registry. The current protected native composition
has reached the main menu, character creation and the Castle Cousland gameplay
HUD under Wine9/Rosetta. A fresh protected process has cold-loaded a preserved
replacement-generated save, responded to door/movement input and written a new
quicksave into its qualified owned profile. Combat, area transitions,
original-save compatibility and paired scenario behavior remain unverified. The
[current task list](../docs/replacement-runtime.md) tracks that work.

## Naming and typing functions with agents

Use the [manual recovery workbench](../docs/recovery-workbench.md) for reviewed
edits across main and Umbra. Start with a completed bulk compilation from the
steps below. The workbench uses the pinned compiler for candidate checks and
clangd for semantic renames.

```sh
.venv/bin/python -m tools.recomp_workbench init --compilation "$COMPILATION_RUN"
.venv/bin/python -m tools.recomp_queries build
.venv/bin/python -m tools.recomp_queries walk --module main --rva 0x4e3024 --depth 2
.venv/bin/python -m tools.recomp_queries callees --module main --rva 0x16ad0
.venv/bin/python -m tools.recomp_workbench checkout --module main --rva 0x16ad0
.venv/bin/python -m tools.recomp_workbench packet --module main --rva 0x16ad0 \
  --output local/recovery/application-entry.json
.venv/bin/python -m tools.recomp_types list
```

Set `COMPILATION_RUN` to the path reported by the bulk compiler. The query tools
also expose callers, instruction bytes, string data, field accesses and recorded
type uses. A packet gives the agent the pinned binary/module/RVA, source view
hash, variable origins and existing type bindings.

1. The agent uses the packet and program queries to write a rename or type request
   with evidence. A rename targets one compiler-resolved declaration. A type
   hypothesis can be keyed to the variable's origin and kept as metadata.
2. The coordinator reviews the request and uses `recomp_workbench plan`, `check`
   and `apply`. Shared classes, fields, inheritance, methods and vtable slots use
   `recomp_types propose`, `check` and `apply`. Shared bindings refer to explicit
   object and field origins.
3. The workbench keeps the source, provenance and receipts in
   `local/recovery/workbench`. Use `rebase` to carry candidates to a new
   compilation for review and `export` to feed checked overrides into a build.

The [single-project workflow](#agent-workflow) below applies compatible names
and scalar types during emission. The workbench additionally supports manual
source rewrites and cross-function guest layouts. Compiler checks validate the
candidate's syntax and ABI. Behavioral acceptance uses original execution and
the [validation workflow](../docs/validation.md).

## Whole-module generation and compilation

Use the sibling [SharpRetro checkout](https://github.com/daeken/SharpRetro/tree/0b88000191668064ff972e6cbf97d4ec7080a7d8/Decompiler)
at commit `0b88000191668064ff972e6cbf97d4ec7080a7d8` for the PE32 backend and
variable-origin API. Use `--sharp-retro /path/to/SharpRetro` on `new` to choose a
different checkout path.

The native ABI now caches normalized provider basenames across calls. Each call
still resolves the target's actual module and checks its executable page. Loader
load/unload notifications invalidate the names without retaining a DLL reference;
missing notifications or an exhausted epoch use fresh filename queries. This is
scaffold overhead reduction, not recovered-function acceptance. A constructed
Wine9/Rosetta control observed18 actual unloads and17 same-address replacements
in both the cache-enabled and disabled variants, with independent filename checks,
synchronized cross-thread invalidation, invalid-handle refusal and saturation fallback. The currently running game still
uses its earlier frozen runtime; an integrated speedup has not been measured.
Evidence: `local/recomp/startup/native-provider-cache-control-latest.json`.

The standalone Windows control is
`recompiler/experiments/native_provider_identity.cpp`. Build the companion fixture
twice with `RECOMP_IDENTITY_VALUE=0xa1` / `0xb2`, different DLL filenames, the same
fixed image base and the `DllMain@12` entry. Build the control with the runtime
include directory and pass those two DLL paths. Repeat with
`RECOMP_NATIVE_PROVIDER_CACHE_DISABLED=1` to exercise the uncached fallback.
The frozen local report retains exact compiler arguments, sources and outputs.

The active workflow attempts the entire pinned main/Umbra inventory before
iterating shared failures. From a fresh checkout, install the validation
dependencies from the [root README](../README.md#run-the-demonstration), place
the pinned game files under `gamedata/`, and initialize both projects:

```sh
.venv/bin/python -m tools.recomp new gamedata/bin_ship/DAOrigins.exe
.venv/bin/python -m tools.recomp --project local/recomp/umbra new gamedata/bin_ship/umbra.dll
```

Use the [Ghidra export procedure](../docs/static-analysis.md) for
`local/analysis/functions.json`. For Umbra, import `umbra.dll` into its own
Ghidra project and run `ExportFunctionBounds.java` with
`local/recomp/startup/umbra-analysis/functions.json` as the output file.
Pass `--cxx` to the bulk compiler if your LLVM-MinGW toolchain is installed
outside the repository's local tool cache.

From the repository root:

```sh
.venv/bin/python -m tools.recomp_bulk
.venv/bin/python -m tools.recomp_bulk_build --generation local/recomp/bulk/runs/<run-id>
```

The first command preserves annotations and binary/module/RVA identities, caches
immutable per-function artifacts, and continues after unsupported functions.
Its catalog includes the static inventories and all existing bounded project/
reviewed startup selections. Supplementary roots remain separately counted;
reviewed shared fragments are not automatically accepted source functions.
Its report separates generation errors, invalid selections, incomplete declared
byte coverage and unresolved transfers. A failed body is never a successful stub.
`--limit` is a probe; unattempted entries stay visible and cannot be presented as
a whole-inventory build. Results remain under ignored `local/recomp/bulk/`.

The second command compiles every emitted body from a completed full attempt as
Windows i686 objects using LLVM MinGW, incremental source staging and keep-going
diagnostics. It records source/toolchain identities and compiler errors under
`local/recomp/bulk-compile/`. It currently produces objects, not a linked game.
Generation and compilation do not establish function or game equivalence. The
existing selected-function commands below remain available for debugging.

Audit instruction support across both modules in one batch, including selections
whose whole-function generation succeeded:

```sh
.venv/bin/python -m tools.recomp_support_audit --generation local/recomp/bulk/runs/<run-id> --scope catalog
```

The default scope remains failed/partial selections. Catalog scope independently
decodes every selected range, authenticates representative original bytes, checks
all distinct encodings in bounded batches, and retains every occurrence in
compressed reports. Decode tails and invalid selections stay unknown; an exhausted
budget or failed batch cannot publish a completed audit. This checks emission
availability, not instruction semantics, complete control flow or game behavior.

Discover canonical MSVC x86 SEH4 handler/filter entries using original prolog
bytes, HIGHLOW pointer relocations and a build-bound instruction registry:

```sh
.venv/bin/python -m tools.recomp_seh_discovery --generation local/recomp/bulk/runs/<run-id> --linked local/recomp/<linked-run>
```

The resulting overlay adds internal entries inside existing ranges. It preserves
annotations, bounds and unknown exception contracts. Unregistered source patterns,
instruction-interior references and targets outside known ranges stay explicit.
The table parser records authenticated prefixes; it does not claim complete table
extents, other prolog variants, C++ exception metadata or nonlocal unwind support.
Regenerate using `tools.recomp_coverage generate --overlay <overlay>` before
compilation; discovery alone adds no runnable function or behavioral acceptance.

The native link stage consumes those exact objects and retains unsupported
generation entries as missing code. Preparation can run while objects compile:

```sh
.venv/bin/python -m tools.recomp_bulk_link prepare --compilation local/recomp/bulk-compile/runs/<run-id>
.venv/bin/python -m tools.recomp_bulk_link runtime
# Requires a successful terminal whole-source compilation report:
.venv/bin/python -m tools.recomp_bulk_link finish
```

The runtime scaffold uses the existing native CPU/ABI providers and a COFF
relocation table for every translated instruction address. Compiler-generated
symbol probes check its ABI. Linking emits the replacement main EXE, Umbra and
shared runtime under `local/recomp/bulk-native/`, preserving original data RVAs
and requiring permanent execution protection before translated entry.

`tools.recomp_bulk_run` is the historical composed FEX/QEMU runner, requiring the
dedicated `daodecomp-fex-host` container and Wine prefix. It does not reproduce
the current macOS Wine9/CX24 + Rosetta playtest. That playtest uses private,
process-bound controllers and frozen image/profile manifests recorded in
`local/recomp/startup/native-provider-cache-checkpoint.json`. A portable launcher
for that path remains open in the [replacement task list](../docs/replacement-runtime.md).
Keep each run's host, images, sources/providers and explicit failures attached
to its observations; results from these different execution paths are separate.

For systematic internal-branch coverage, `ExportInstructionMap.java` exports
static instruction/flow hypotheses from the existing Ghidra projects in read-only
mode. With complete gzip JSONL maps under `local/recomp/instruction-maps/`:

```sh
.venv/bin/python -m tools.recomp_coverage prepare --generation local/recomp/bulk/runs/<completed-run-id>
.venv/bin/python -m tools.recomp_coverage generate --overlay local/recomp/coverage-overlays/<overlay-id>
```

Proposals require matching module identity, pinned original bytes and independent
decoder lengths. They stay within existing ownership ranges, retain annotations
and reviewed contracts, and are published only after both complete maps validate.
Regeneration still reports failures/coverage separately. Identical completed
source/metadata payloads can share APFS storage with independent writes, avoiding
full duplicate source storage on each backend revision.

Guarded PE32 jump tables can expose real code omitted from an inventory's owned
ranges, including tables stored in executable sections. To propose separate case
fragments across both modules, use the exact overlay consumed by a completed run:

```sh
.venv/bin/python -m tools.recomp_switch_discovery --generation local/recomp/bulk/runs/<completed-run-id> --overlay local/recomp/discovery-overlays/<input-overlay-id>
.venv/bin/python -m tools.recomp_coverage generate --overlay local/recomp/switch-overlays/<overlay-id> --batch-size 512
```

The recognizer checks original instruction bytes, a matching unsigned index
guard, the relocated table address and every relocated executable target. It
examines generated instruction metadata; unsupported bodies and unrecognized
table forms remain unresolved. Proposals preserve existing function ranges and
annotations. They are code-pointer hypotheses with unknown entry ABI, behavior
and CFG completeness; rejected tables and bounds are retained in the report.

Callbacks populated by instructions instead of static tables have a separate
origin scan. It consumes the completed generation's exact input overlay:

```sh
.venv/bin/python -m tools.recomp_instruction_pointer_discovery --generation local/recomp/bulk/runs/<completed-run-id>
.venv/bin/python -m tools.recomp_coverage generate --overlay local/recomp/instruction-pointer-overlays/<overlay-id> --batch-size 512
```

Original bytes and HIGHLOW sources must match a full-width MOV/PUSH immediate
or absolute LEA. Pointer dereferences and arithmetic are excluded. The scan
follows new addresses inside bounded target-body hypotheses until no new roots
appear; exhausting the round budget refuses publication. Existing ranges and
annotations stay intact. Executable sections can contain data, so these targets
are unaccepted hypotheses rather than established callable functions. Unsupported
input bodies, operand forms and bounds remain explicit in the reports.

Relocated pointer words inside executable sections can also identify cases whose
index bounds the guarded-switch recognizer cannot establish:

```sh
.venv/bin/python -m tools.recomp_literal_pointer_discovery --generation local/recomp/bulk/runs/<completed-run-id>
.venv/bin/python -m tools.recomp_coverage generate --overlay local/recomp/literal-pointer-overlays/<overlay-id>
```

This scans original HIGHLOW words outside every emitted instruction's bytes.
Only file-backed executable sections are scanned, excluding the pinned resource
sections. Instruction operands, instruction-interior targets and targets
overlapping candidate literal storage are excluded. Each bounded proposal keeps
its original source word and module identity. Absence from emitted code does not
prove that a word is data; dispatch bounds, callable signatures and behavior stay
unknown. Existing selections and guarded-switch acceptance checks are preserved.
Bounds/ambiguity refusals remain explicit, and shared continuations still require
an authenticated ownership plan before linking.

To recover omitted switch cases and shared tails inside existing unaccepted
function envelopes:

```sh
.venv/bin/python -m tools.recomp_switch_case_recovery --generation local/recomp/bulk/runs/<completed-run-id>
.venv/bin/python -m tools.recomp_coverage generate --overlay local/recomp/case-coverage-overlays/<overlay-id> --batch-size 512
```

This follows original guard paths, including direct branch links and byte index
remaps, and adds only recursively decoded case instructions. Table storage and
skipped alignment are excluded. Proposed ranges stay inside the existing owner
envelope, stop at other owners, and preserve annotations. Accepted/reviewed roots
are protected; external continuations, rejected guards and exhausted budgets
remain explicit. The reports bind the original metadata, protected registry and
decoder version. These corrections do not grant behavioral or complete-CFG credit.

Direct calls, branches and missing return/fallthrough continuations have a
whole-module discovery pass as well:

```sh
.venv/bin/python -m tools.recomp_direct_transfer_discovery --generation local/recomp/bulk/runs/<completed-run-id>
.venv/bin/python -m tools.recomp_coverage generate --overlay local/recomp/direct-transfer-overlays/<overlay-id> --batch-size 512
```

This verifies original instruction bytes, independent decoding and relative
target arithmetic. A bounded closure proposes disjoint code fragments outside
existing ownership without guessing signatures or changing existing contracts.
Instruction interiors, indirect targets, unsupported bodies and refused bounds
remain unresolved. Reports distinguish relative operands and continuations from
relocated pointers; these proposals grant no function or game acceptance.

Add `--include-switches` to the discovery command to follow guarded and
compressed table cases outside existing ownership too. This combines switch
origins with direct-edge closure, preserves the existing owner envelopes, and
refuses a completed overlay if decoded proposals overlap authenticated table
data. Unrecognized guards and fallthrough bounds refusals remain explicit.

## Native Windows execution

To find later unsupported instructions hidden by a function's first failure:

```sh
.venv/bin/python -m tools.recomp_support_audit --generation local/recomp/bulk/runs/<completed-run-id>
```

The audit independently decodes every declared range in failed and partially
covered selections, then checks each distinct byte encoding against the pinned
original image and the current backend. Every original RVA/owner occurrence is
retained. It diagnoses instruction lowering/emission separately from production
function boundaries; it does not change the generator, contracts or registry.
Successful instruction emission is neither a compilable function nor behavioral
acceptance. Undecodable tails, invalid selections, process failures and exhausted
budgets remain unknown. Full-catalog generation, compilation and startup still
follow the instruction-family support batch.

The broad support batch covers the observed double shifts, x87 math/conditional/
integer-flag/environment operations, legacy MMX/SSE conversions, selectors and
XLAT/RDTSC. Instruction emission and constructed controls remain distinct from
whole-game behavior. INT3 delivery and invalid bounds remain explicit unknowns.
See the current counts and bounded control scopes in
[the replacement task list](../docs/replacement-runtime.md#instruction-support-batch-before-the-next-game-launch).

MMX state needs explicit capture on the measured Wine9/Rosetta profile: its
FNSAVE/FXSAVE images did not reflect direct MMX register observations. The native
bridge calibrates that relationship and carries MMX across compiled operations,
imports and protected callbacks, with unknownness retained. Architectural x86
profiles continue to use physical x87 aliases; this branch is not yet corroborated
on native x86 Windows hardware. Composed sequences and callback controls are
required in addition to individual instruction controls for this transport.

The current unlaunched whole build links 42,501 generated bodies and 2,348,042
instruction addresses. Two INT3-delivery failures and sixteen partial per-body
coverage records remain unknown. The catalog includes shared decode roots, not
just distinct source functions. Full-function and game acceptance remain separate.

When newly emitted bodies share instructions with older fragments, prepare an
explicit, input-bound ownership proposal:

```sh
.venv/bin/python -m tools.recomp_instruction_ownership --compilation <compilation-run> --output <ownership-plan.json>
.venv/bin/python -m tools.recomp_bulk_link prepare --compilation <compilation-run> --ownership-plan <ownership-plan.json> --output <link-directory>
```

The proposal checks identical pinned-original bytes and retains every function.
Preparation verifies each candidate source/metadata identity and rejects stale,
unplanned, missing or unused assignments. Default duplicate ownership still
refuses. Choosing one compiled body for a shared PC does not prove the two emitted
sources equivalent. The final batch has 814 authenticated shared addresses.

The audit also checks authenticated inventory ranges from invalid selections,
including code before entry, while retaining the original selection failure as an
unknown. This diagnostic never admits that envelope to the production generator.

Generated Windows x86 builds default to native memory and a generic native ABI
call bridge. NativeX86Memory uses real Windows memory; native API writes, returned
heap/object pointers and raw GetProcAddress/vtable targets require no per-API
memory/ownership adapters. The bridge captures actual registers, flags, x87/XMM,
last-error and returned ESP. Its assembly uses a nested TLS frame and temporarily
switches TEB stack bounds. This is currently exercised on Wine 11/macOS ARM64.
Original main/Umbra native fallback remains forbidden.

Use `build --windows --execution-profile strict` (CMake
`-DRECOMP_NATIVE_EXECUTION=OFF`) for explicit checked/symbolic validation fixtures.
The strict backend is retained independently; native execution does not turn its
unknown inputs into passing evidence. Native inputs must be concrete/captured,
and symbolic scalar stores remain explicit errors.

`python3 -m tools.recomp_native --run` builds actual replacement DAOrigins.exe and
Umbra.dll with original data at its original RVAs and native PE import/resource/TLS
metadata. Original executable bytes are retained as read-only data with permanent
DEP enforced before translated entry. Newly compiled C++
translations live in recomp_runtime.dll, which has independent C++ runtime TLS.
Windows owns import binding, module identities and the original static TLS
template. The native launcher stages retained SDK DLLs and independent asset
copies under ignored local/recomp/native-game/. Original main/Umbra native
fallback remains forbidden.

This composition has returned TRUE from translated Umbra attach and executed
main through roughly 337.8 million instruction units under Wine. Installing the
bundled PhysX system runtime cleared an error shared with the original. Earlier
runs opened the main window and the user observed the intro video, but a retained
SDK loading control exposed disabled DEP: original callback execution cannot be
excluded from those observations. With permanent DEP enforced, the current stop
included a native transfer to 0x008e79c0 (`__except_handler4`) after the game's
deliberate 0x406d1388 thread-name exception. This path now returns through compiled
handler/filter code, and worker-thread callbacks enter compiled execution.
Menu/gameplay remain unverified. Window/COM callback coverage and nonlocal
exception/unwind continuation remain active work. For a
missing-code stop, `python3 -m tools.recomp_native --advance --run` selects the
observed entry from byte-checked pinned inventory bounds and builds incrementally.
Unknown bounds/runtime semantics cannot pass. Exit 3 means incomplete exploration.
Frozen native entry sources and build/run identities accompany the local reports.
This startup composition loads fixed-base translated Umbra before retained SDKs
that prefer the same address; dependency ordering still needs original comparison.

Concrete native logical/shift/multiply/divide operations capture actual x86
flags, including otherwise undefined bits. Implementations live in
`runtime/native_cpu.cpp`, so provider changes rebuild one object. Native calls
refuse unobserved forwarded flags and unsupported trap/alignment/task modes.
Strict validation keeps unknown flags and
symbolic state unresolved. The legacy `tools.recomp_boot` command below still
selects the strict exploration profile; it is not the production native launcher.

`--advance --call-depth 1 --call-limit 128 --call-seeds selected --run` selects a
bounded batch of byte-checked, translatable direct callees; deferred helpers still
fail if reached. The native execute observer reports attempted transfers into
non-executable translated data and redirects ordinary CALL/RET entries through
`runtime/native_callback_entry.hpp`. This uses a private C++ stack and an assembly
return with actual register/FP state and RET cleanup. Before entering game code,
each process measures both the context's x87 source format and register order
against known raw values in all eight stack rotations. It prefers a matching
extended FXSAVE image and accepts legacy FSAVE only when that complete observed
image matches instead. MXCSR and XMM still come from required extended context;
missing x87 or SIMD observations are refused. Missing bodies, unknown state and
unsupported nonlocal continuations still stop explicitly.
The same calibration learns the host's execute-fault code only from the known
read-only probe. Redirection additionally requires a committed, readable,
non-executable page and the expected fault shape; executable illegal instructions,
data-access faults and inaccessible pages are refused. The callback reads its
return word directly from the current thread's validated native stack bounds and
committed page. Full observed FP/SIMD state is still required. Local Linux host
controls are separate from native Windows corroboration and game acceptance.
Local integrated experiments also compose FEX game execution with the identical
Wine 8 i386 server binary running under corrected QEMU. A separately captured
FEX-server canary failure motivated this host arrangement; the Windows images
and generic CPU/ABI transport are unchanged. The server is started explicitly
before the game, because [Wine 8's loader](https://github.com/wine-mirror/wine/blob/wine-8.0/dlls/ntdll/unix/loader.c#L716)
tries its bundled server before `WINESERVER`.
Frozen-image matched runs and individual component identities are retained under
`local/recomp/startup/fex-host/`; this is an experimental host, not a game pass.
Run history binds immutable build reports, frozen entry sources/startup plan,
generated views and compressed copies of the actual executed EXE/DLL images.
Each new run retains its own raw stdout/stderr under `runs/<run-id>/`; the
`run.stdout` and `run.stderr` names are replaceable aliases for live observation.
The runner records its selected Wine diagnostic channels and execution controls.
Use `--wine-debug=+seh` on the native launcher or follow controller to retain Wine
exception diagnostics; logging can change timing and is not a host-fault fix.
Callback failures include entry/thread, actual budget counters and raw register
state. Main entry and independent new-thread callbacks honor the same configured
instruction limit; exhausted budgets remain failures. These are exploration
bounds, separate from function acceptance and playable-game verification.

`python3 -m tools.recomp_native_follow --restart --steps 24 --call-depth 2`
runs that cycle serially for observed missing-code entries. It stops for unknown
bounds, runtime failures or its iteration limit, and records each build/run in
`local/recomp/native-game/follow-sessions/`. This console controller is bounded
startup exploration; its progress report never claims game acceptance.

The native bridge preserves the actual TEB last-error value across its own
bookkeeping. Translated direct FS:[0x34] stores and native API calls therefore
share the same thread field; the production bridge does not replace it from a
separate cached error value.

## Agent workflow

Run from the DAODecomp root; .NET 10, Python 3.10+, CMake and Clang/GCC are needed.


```sh
python3 -m tools.recomp new gamedata/bin_ship/DAOrigins.exe
python3 -m tools.recomp add --rva 0x18760 --size 10
python3 -m tools.recomp add --rva 0x24030 --size 10
python3 -m tools.recomp generate
python3 -m tools.recomp show --rva 0x18760
```

`show` returns JSON containing source, the view hash, and each visible variable's
name, width, type, defining IL, instruction RVA and persistent origin. The agent
identifies the variable **by its name in that view**:

```sh
python3 -m tools.recomp annotate --view VIEW_HASH --rva 0x18760 \
  --variable variable_2 --name loaded_flags --type u32
python3 -m tools.recomp generate
python3 -m tools.recomp build
```

Replace `VIEW_HASH` with the complete hash returned by `generate` or `show`.
Every edit invalidates the view for further edits; regenerate before the next
edit. This first conservative interface favors explicit conflicts over implicit
merging. `--dispatch` on `generate` switches the control-flow representation
without changing the annotations. `--project PATH` before the command selects a
different workspace; the default is ignored `local/recomp/project`.

## Persistence and conflicts

`project.json` is the authoritative editable state. Functions are tied to the
module name, binary SHA-256 and RVA; the selected byte range is a traversal bound,
not a claim that all enclosed bytes belong to the function. A variable annotation
is keyed by its origin, not its displayed name or source line.

Reviewed indirect branch targets can be listed as `extra_entries` (module RVAs)
on the owning function, within its selected `ranges`. They extend recursive
discovery without inventing runtime edges or separate overlapping functions.
Instruction overlaps and entries outside the bounds fail. Structure recovery
starts these entries with unknown affine facts, so primary-path assumptions
cannot leak across a table-selected entry.

Linked projects can list `data_regions` for read-only pools embedded in executable
sections. Each requires `rva`, `size`, `sha256`, `purpose` and a `provenance` object
containing the pinned `module_sha256`. Generation verifies file-backed bytes and
rejects overlaps with decoded instructions, mapped data or another pool. Only
the declared bytes are guest-readable; the backing is never executable. No
automatic whole-code-section mapping or indirect-target guessing is performed.

The machine backend's initial origin combines the instruction RVA, a digest of
the normalized instruction IL, and its canonical temporary index. Temporary
numbers in that IL are normalized by occurrence. Display numbering, C++ spelling,
and structured/dispatch emission do not participate. This is a deliberately
conservative identity: instruction/lifter changes that alter normalized IL orphan
annotations, rather than guessing that a changed value is the old one. Matching
split/merged high-level SSA lifetimes remains future work.

The tool resolves the submitted name through a content-addressed generated view,
validates the edit with the real emitter, then atomically updates the annotations.
Changed source/manifest bytes, stale views, missing origins, ambiguous/duplicate
names, C++ keywords, and incompatible integer widths refuse the transaction.
Project edits and bridge builds are locked on POSIX hosts. A view hashes its source,
runtime, declarations, project snapshot, and loaded backend artifacts; old views
remain available. Editing generated files intentionally invalidates that view.

Currently supported type annotations are `bits`, `bool`, `u8`, `u16`, `u32`, and
`u64`, provided the carrier can represent the value's full machine width. Every
use still goes through the machine backend's width handling. Signed types, host
pointers, native allocation layouts, and guessed prototypes are refused. Observed
guest-memory field views are described below. Semantic type
proposals will need separate evidence and checks before they can affect code.

## Guest32 structure recovery

Generation follows constant-offset loads/stores through entry registers, register
copies, LEA, control-flow joins and values loaded from memory. Only effective
addresses established to be zero-extended 32-bit values become fields. Each base
has its own sparse observed structure; sharing ECX or a layout across different
functions does not merge class identities. Stack-derived storage, segmented/TLS
accesses, variable indexing and conflicting base facts retain raw accesses and
appear under `unrecovered_accesses`. A loaded field later used as an address
records a relationship to the corresponding child view.

Fields record signed displacement, exact storage width, read/write sites,
overlapping access ranges and binary-derived origin. Overlapping fields retain
separate accessors over the same memory. Packing, total object size, alignment,
ownership, lifetime and original source class remain unknown.

```sh
python3 -m tools.recomp annotate-structure --view VIEW_HASH --rva 0x18760 \
  --structure object_0 --name observed_object
python3 -m tools.recomp generate
python3 -m tools.recomp annotate-field --view NEW_VIEW_HASH --rva 0x18760 \
  --structure observed_object --field field_00000018_u32 --name flags_word --type u32
python3 -m tools.recomp generate
```

Edits resolve displayed names through immutable views and persist by base/field
origins, with the same atomic validation and stale-view checks as variable edits.
Field types preserve observed storage widths. Names are annotations rather than
evidence of the original program's names.

Emitted `view_observed_object` accessors use the guest `Memory` interface. Each
access materializes its base from the original evaluated effective address minus
the observed displacement, modulo 2^32; its accessor adds the declared field
displacement modulo 2^32. This preserves the original address and evaluation
point when entry registers change, execution resumes mid-function, or objects
alias. Guest integers are never cast to host pointers. `generate --raw-memory`
retains observed metadata/annotations but emits the original raw accesses.

## Windows executable and address registry

llvm-mingw supplies Clang, LLD, Windows headers, import libraries and C++ runtime
libraries. Build a PE32 diagnostic translation bundle with:

```sh
python3 -m tools.recomp build --windows \
  --cxx local/tools/recomp/llvm-mingw-20261104-ucrt-macos-universal/bin/i686-w64-mingw32-clang++
```

The returned JSON names `recomp_image.exe`; `--list` enumerates every compiled
guest address. Native `build` also builds the diagnostic executable. Default
startup exits with an explicit diagnostic instead of simulating game startup.

## Linking translated modules and original data

Each module has its own pinned recovery project and selected functions. Explicitly
include another project to generate a single C++ library/executable containing both:

```sh
python3 -m tools.recomp generate --with-module local/recomp/umbra
python3 -m tools.recomp build --windows \
  --cxx local/tools/recomp/llvm-mingw-20261104-ucrt-macos-universal/bin/i686-w64-mingw32-clang++
```

`local/recomp/umbra` must already be initialized against the pinned `umbra.dll`.
The composition persists in the root project's `link.json`; later `generate`
commands include the same projects and their current annotations. Repeat
`--with-module` for several projects; specifying it replaces the remembered list.
`generate --standalone` removes the composition after successful generation.
Dependencies are explicit, rather than recursively inherited from another
project's composition. A provider can have an empty selection for data/export
inspection. Overlapping preferred image ranges, duplicate case-insensitive module
names and incompatible backend/runtime versions are refused. Rebasing is not
implemented.

Functions retain binary SHA-256/module/RVA identities. Provider C++ symbols and
namespaces include a module identity prefix, so equal RVAs in different modules
can link together. `show --rva RVA --module umbra.dll` selects an unambiguous
function. Edit a provider's annotations through its own project/view, then
regenerate the combined view; linked views refuse edits to another project's
functions and report the owner path.

The generated data loader copies original PE headers and each non-executable PE section into bounded
guest memory at its preferred VA, checks its initialized byte count and SHA-256,
zero-fills its uninitialized tail, and patches IAT slots. Mapped data includes
globals, constants and vtables. Existing vtable entries remain **guest addresses**;
an indirect call dispatches that address to the compiled C++ instruction registry.
The replacement never jumps into original instruction bytes. Code sections are
not mapped as readable data. Headers are read-only guest data, including the
original self-image metadata used by CRT startup. Section permissions apply after the
loader seals memory. Missing, changed, truncated, overlapping or out-of-bounds
data fails. Generated binary data artifacts stay in ignored local views.

Imports resolve by exact export name or ordinal, with Windows DLL basenames
matched case-insensitively. A supplied translated provider receives a rewritten
guest IAT entry. Other imports retain distinct tokens and require the existing
explicit native bridges. The pinned Umbra policy forbids native fallback.
Forwarded, missing or untranslated exports remain explicit statuses/failures.
`generate --require-translated-code` refuses publication if any translated import
has no compiled target or mapped data export; this checks entry availability,
not completeness of each target's callees or behavioral correctness.

The full pinned import ledger is `recompiler/imports.json`. The
[active import task list](../docs/replacement-runtime.md#native-windows-execution-active)
tracks subsystem batches ahead of startup execution. `native-bindings.json`
declares generated checked Windows x86 adapters; the SDK compiler verifies each
prototype. These share the existing FP, last-error and volatile-register boundary.
They support scalar arguments, known ANSI/UTF16 inputs (including counted spans),
and field-complete FILETIME/SYSTEMTIME outputs. Failed record outputs retain real
bytes with unknown status; output addresses are captured before calls so aliased
argument-stack writes are handled. Original backing preserves input aliases.

`python3 -m tools.recomp_imports --manifest PATH --output REPORT
--require-contracts` audits every pinned import slot and reports all missing
adapters together. The optional gate fails while any static native import lacks a
scoped declaration. Export resolution and declaration coverage do not establish
complete API, callback/COM/thread or gameplay support. Startup generation saves
this report before compilation/execution. Generated views retain their binding
specification and generated calls under their content hash.

Run the generated executable's diagnostics under Wine:

```text
recomp_image.exe --list
recomp_image.exe --bindings
recomp_image.exe --check-images Z:\path\to\generated\view
```

`--bindings` distinguishes `translated_code`, `translated_data`,
`untranslated_code`, missing/unsupported bindings, and native imports.
`--check-images` loads and verifies the artifacts and patches import slots. It
does not execute DLL entries, TLS/CRT constructors or game startup. The generated
`ImageMemory` and `initialize_linked_images` API also support bounded execution
adapters; map their stack/object regions before initializing and sealing images.
Further native pointer/callback signatures, TLS callbacks/new-thread contexts,
exceptions and full runtime initialization still need implementation and evidence.

The reproducible synthetic linking experiment builds a real x86 EXE and DLL.
Windows resolves the original's import normally; generated candidates execute
the selected caller and callee with copied globals and BSS, with the original DLL
removed. It compares full EAX and a shared counter, repeats calls within a fixture,
checks guest stack/nonvolatile obligations, and requires detection of a compiled
callee-result corruption. ARM64 runs include ASan/UBSan.

```sh
python3 recompiler/experiments/compare_linked.py \
  --wine 'local/tools/recomp/Wine Stable.app/Contents/Resources/wine/bin/wine' \
  --cc local/tools/recomp/llvm-mingw-20261104-ucrt-macos-universal/bin/i686-w64-mingw32-clang
```

This is synthetic infrastructure evidence. It does not validate DAO or Umbra
function behavior or establish that the game can start.
This bundle has no original executable/code dependency.

`registry.cpp` maps guest32 function and instruction addresses to compiled
functions. Guest addresses remain 32-bit tokens; host pointers are not written
into original object/vtable storage. Automatic vtable discovery/initialization
and full process/data-image loading are still outstanding.

Clang i686 rejects `unsigned __int128`. The machine runtime now uses Clang's
unsigned `_BitInt(128)` there, retaining `unsigned __int128` on supported 64-bit
targets. This enables real Windows x86 builds of the same guest-state backend.
It is a compiler-specific internal carrier, not an original-game ABI signature
or a claim about every instruction/library path.

## Calls, ABI observations and imports

Function steps now yield explicit transfers for calls and retain guest CALL/RET
stack effects. `execute_guest(entry, stop, state, memory, budget, handler)` runs
across selected functions until a real return reaches the explicit stop address.
`resume_guest` resumes a budget interruption at its live PC. The dispatcher also
handles indirect/vtable calls, tail jumps and recursive calls, looking up every
translated instruction address so return continuations need not be function
entries. A single budget is shared across the chain; imports consume one external
dispatch unit, not a claimed count of native DLL instructions. Unknown targets,
non-return jumps to the stop address and lack of progress cannot pass as returns.
The older `fn_*`/`invoke_guest` interfaces run one function step and may now return
`Exit::transfer`; use `execute_guest` for a complete multi-function invocation.

`show` includes ABI observations: RET cleanup bytes, traced entry-register reads,
entry-stack access spans and transfer sites, including statically identifiable
IAT slots. These are not complete source signatures. A cleanup amount does not
uniquely identify cdecl/stdcall/thiscall/fastcall, nor do reads establish a formal
parameter list or signedness. Structure/stack analysis conservatively discards
surviving register facts at call continuations until callee summaries exist.
Exported decorated names are retained separately as `export_names` and can supply
symbol-declared signatures to check against actual instructions/execution.

IAT slots are registered as explicit import tokens. The caller/loader must bind
guest IAT memory; calls read its live value, so retargeting an entry to translated
code works. Import thunks can themselves be selected and translated, preserving
their actual IAT load and jump. There is no silent static import substitution.

The first native bridge is the documented pointer-free
[`KERNEL32!MulDiv`](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-muldiv)
boundary: three signed 32-bit stack arguments, an EAX result and 12-byte callee
argument cleanup. It invokes the real platform API through the Windows headers
on Windows builds. Flat SS is required. ECX, EDX and flags are invalidated after
the call rather than invented as preserved; later reads fail explicitly until
redefined. General pointer marshalling, callbacks, FP returns, exception state and
other imports remain unimplemented. On non-Windows hosts the default bridge
refuses; an explicit handler can supply a declared synthetic test model.

### Actual entry-point exploration

The ongoing playable-build checklist is
[`docs/replacement-runtime.md`](../docs/replacement-runtime.md). Startup exploration
now follows the actual EXE and Umbra DLL entries with selected CRT code, real
Windows APIs and a JSONL failure trace:

```sh
python3 -m tools.recomp_boot
python3 -m tools.recomp_boot --advance
python3 -m tools.recomp_boot --mode combined --budget 500000000 --native-trace-limit 2000 --run-timeout 600
```

For startup iteration, add `--live` with one selected mode, for example:

```sh
python3 -m tools.recomp_boot --mode combined --budget 500000000 --native-trace-limit 2000 --run-timeout 1200 --live
```

The explorer pauses at missing generated code, verifies original byte bounds,
strictly translates and builds a candidate DLL, then resumes the same registers,
memory, budget and native lifetimes. Candidate ABI/layout, runtime/backend/compiler
identity, module hash, loaded DLL hash and PC ownership are checked. Unknown-bit
identities come from the host allocator. No original main/Umbra native fallback
is provided. New instruction/runtime/native bridges still require a cold run.

If inventory bounds are unavailable or ambiguous, `live-session.json` records a
`controller_wait` with a request and response path under `live-review/`. Keep the
process paused while reviewing original bytes, then write a response containing
`binary_sha256` and an explicit `selection` with RVA, size, original
`slice_sha256`, contract status and any reviewed ranges. The controller checks
those bytes/ownership before translating. It does not infer bounds or types from
pseudocode. Responses and hashes become candidate provenance. Use
`--no-live-wait-for-review` to stop instead, or `--live-reviewed PATH` for an
existing explicit bounds report. The finite wall/instruction/candidate budgets
remain enforced. Pauses inside native callbacks are currently refused.

`live-session.json` records the base view and ordered candidate artifacts;
`last-execution.json` keeps the incomplete startup outcome. A hot-added function
is not accepted recovery evidence. Regenerate and run the final standalone cold
bundle before any scenario acceptance.

Startup builds prefer Ninja when installed, using a separate cache from Unix
Makefiles. This avoids Make's shared per-source PCH flags file invalidating every
existing object when a function is added. Use `--build-generator "Unix Makefiles"`
to select the previous generator explicitly; actual build commands remain in each
execution report. A new generator cache needs an initial full compilation.

These commands return a nonzero status for incomplete startup. Neither a returned
DLL entry nor a captured frontier certifies initialized gameplay. `--advance`
selects newly observed missing code entries from pinned static inventories, hashes
their original bytes, then requires actual decoding/lifting to succeed. Inventory
body ranges are traversal hypotheses; envelopes can include gaps only when no
other inventory entry intervenes. Native API gaps, ambiguous bounds and unsupported
instructions remain explicit blockers. Isolated and combined modes are available.
`--advance --call-depth 3 --call-limit 64` also follows bounded direct-call
helper dependencies. `--call-seeds selected` scans every startup-plan entry,
including unexecuted constructors. Each optional candidate must have pinned,
nonoverlapping inventory bounds and translate successfully; deferred targets
remain unresolved. Reports are immutable and content-addressed under
`local/recomp/startup/call-expansion/`. These are exploration selections, not
observations that every selected function ran or behaved equivalently.

Combined mode runs the chosen partial Umbra attach before main in one process,
carrying guest module/native lifetime state forward. Original process-start DLL
attach inputs, full dependency ordering and intervening loader context remain
uncaptured; a returned attach is not initialized-game evidence.

Reached x87 value support includes m32 multiplication, both non-popping register
multiply destinations, FSINCOS, FLD ST(i), FMULP, FADDP and FSUBP register forms. Compiled native
x87 operations retain raw80 values and declared control/status/tags. Providers
preserve unknownness for untouched slots and record the conditional FSINCOS
range-failure stack behavior. Focused constructed byte controls under Wine are
instruction-debugging evidence; complete function/scenario acceptance is open.

The selected ranges, identities and incomplete process contract are in
[`startup.json`](startup.json). A stack, partial TEB fields, and initial-thread
static PE TLS data/index/vector are supplied. Other uninitialized thread fields
fail on read; full TEB/PEB state, nonempty TLS callbacks, new-thread transport and
exception dispatch remain unfinished. Main receives its measured FP fixture and
unknown incoming non-SP GPRs/flags/stack, with clear DF and a known ESP; loader
continuity is not claimed. Original headers are available for CRT self-image
checks. Raw original code is never executed by the replacement.

USER32 resource loading now accepts checked UTF16 names or ordinal16 identifiers,
with exact recorded guest module bases and known readable flat PE headers/resource
data. Shared icons/cursors have separate token lifetimes. Original instruction
pages remain inaccessible. The native resource control compared icon pixels with
a read-only original datafile mapping; it never ran the original module entry.

Owned kernel handles include mutexes, events and semaphores. WaitForSingleObjectEx,
CreateEventW and CreateSemaphoreW preserve real native results, state and errors;
nondefault security descriptors still require a typed adapter. Native control
APCs/threads are experiment infrastructure, not guest callback/thread transport.

SHELL32!SHGetFolderPathW uses the actual native profile-folder lookup with a
checked 260-WCHAR output buffer, exact CSIDL/flag bits and native HRESULT/error
state. Only the returned string including its terminator becomes defined; an
unknown tail remains unknown. Reserved owner must be NULL; user tokens currently
support NULL and the documented default-user sentinel only. The focused control
compares native buffer bytes, success/failure results and output knownness under
Wine; it does not establish game startup. Generated bundles link `shell32`.
See the [Windows API contract](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/nf-shlobj_core-shgetfolderpathw).

GetPrivateProfileStringW performs real scalar INI reads, preserving native default,
truncation and last-error behavior. Known UTF16 inputs use their checked native
backing so aliasing is retained. Output capacity counts WCHAR16 units; only the
returned string and terminator become defined. NULL section/key enumeration
remains explicitly unsupported. The temporary-file control covers native reads,
missing files/keys and zero/small output capacities, not game configuration
acceptance. See the [Windows API contract](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-getprivateprofilestringw).

QueryPerformanceFrequency returns the actual native BOOL and 64-bit counter
frequency through checked output backing; failed output remains unknown. Its
focused native comparison checks the output bytes, neighboring storage, ABI and
last-error transport. Real timing calls remain nondeterministic during startup
exploration. See the [Windows API contract](https://learn.microsoft.com/en-us/windows/win32/api/profileapi/nf-profileapi-queryperformancefrequency).

REP MOVSD transports partially known memory values, retaining known bits and
existing unknown-bit identities without consuming unknown payload as a value.
Sequential element copies keep overlap, DF, budget interruption and fault-prefix
behavior. This fixed a reached 36-byte stack-to-heap record copy at 0x008e24fa.
The trace identifies the source as SYSTEM_INFO. Its reserved WORD remains
unknown for unreviewed native providers. Focused abstract-state checks and the existing
constructed instruction/emulator comparisons are debugging evidence.

Byte memory XOR (`30 /r`, unprefixed PE32 memory forms) now transports partial
knownness and existing unknown-bit identities for AL/CL/DL/BL/AH/CH/DH/BH inputs.
Its flags retain known CF/OF, conditional SF/ZF/PF and undefined AF. Memory faults
leave arithmetic flags unchanged. The reached `30 0c 30` form has constructed
native Windows x86 controls under Wine, alongside AH and abstract partial-value
checks. These controls do not accept the complete record-processing function.

The current Wine 11 x86 GetSystemInfo writer has a separately reviewed output
refinement: exact kernel32/kernelbase file hashes, procedure RVAs and the live
thunk target must match before its actually returned reserved WORD becomes known.
Native poison observations and the compiled writer's unconditional store at
kernelbase RVA 0x77b71 support this provider-specific contract. Incomplete output
stops explicitly. Other providers keep the field unknown; no constant is supplied
as its value. See `local/recomp/startup/discovery/system-info-contract-review.json`
and the [Wine writer](https://github.com/wine-mirror/wine/blob/wine-11.0/dlls/kernelbase/memory.c#L145-L232).

Unprefixed memory PUSH (`FF /6`) loads a scalar value and its knownness/origins
before committing the stack write. ESP-relative sources use incoming ESP; failed
reads/stores preserve SP and flags. Constructed Windows x86 controls under Wine
cover copied words/flags, address forms, overlap, partial values and wraparound.

CreateDirectoryW forwards a known nonnull UTF16 path and optional default
SECURITY_ATTRIBUTES to the actual API, retaining its BOOL and last-error result.
Nondefault descriptors remain unsupported. Focused native controls create and
remove a private temporary tree; they do not certify game filesystem behavior.
See the [Windows API contract](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createdirectoryw).

Startup checks the configured direct Documents directory and both Wine registry
routes, expanding the recorded active `USERPROFILE`. A Wine9/CX24 playtest exposed
that checking only `users/daeken/Documents` was insufficient: the active user was
`crossover`, whose Documents link still led to the normal macOS Documents folder.
That run's completed autosave was preserved with its actual path; its earlier
isolated-profile metadata is superseded by the recorded erratum. The stronger
preflight refuses that mismatch without changing a live profile. These are offline
checks; actual shell API resolution remains separate evidence, and paired scenarios
must use corresponding profile state. See
`local/recomp/startup/protected-first-autosave-latest.json` and
`local/recomp/startup/profile-route-regression-observation.json`.

Inactive generated metadata can be losslessly packed as `manifest.json.gz`.
`read_view` restores it on demand only after checking decoded bytes against the
original view hash, then performs ordinary manifest/file checks. Existing changed
manifests are not overwritten from a pack. Source/data/replay files stay at their
existing paths. Consult `local/recomp/startup/view-storage/` for packed metadata.

The reached WINMM!timeGetTime boundary invokes the actual native API and returns
its DWORD value with zero argument cleanup. Generated Windows CMake bundles link
`winmm` alongside `advapi32`; manual Windows adapter builds including the full
native-import dispatcher also need `-lwinmm`. Other Winmm signatures remain
unsupported. Clock-bracket observations are transport debugging, not deterministic
timing or gameplay evidence.

GetModuleFileNameW now returns the configured UTF16 main identity or a registered
native module's actual filename, with checked WCHAR counts and measured host
truncation/error behavior. Translated DLL path identity is still unsupported.
SetCurrentDirectoryW changes the actual child process directory and retains real
success/failure results. Focused native boundary reports remain incomplete game
scenario evidence.

Explicit startup bridges include real `GetSystemInfo`, `GetSystemTimeAsFileTime`,
`QueryPerformanceCounter`, process/thread ID and tick APIs, `GetStartupInfoA`,
`GetProcessHeap`, `HeapCreate`, `HeapAlloc`, `HeapSize`, `HeapReAlloc`, `HeapFree`
and `GetVersionExA`, plus reached synchronization/TLS/FLS/environment APIs.
The reached registry boundaries `ADVAPI32!RegOpenKeyExW` and `RegCloseKey`
forward to real native calls with checked output spans and owned-key lifetimes.
Error statuses are preserved; failed out-key contents remain unknown. Other
registry calls still require an explicit bridge when reached.
Reached mutex APIs now use real CreateMutexW/WaitForSingleObject/ReleaseMutex/
CloseHandle behavior with owned kernel-handle tracking and preserved last-error.
Nondefault security descriptors and other kernel-object creation signatures
remain unsupported. Native control threads in the focused mutex check are
separate from unimplemented translated guest-thread transport.
Pointer APIs require checked x86 process backing. `ProcessMemory` registers native
allocations and OS-owned strings, preserves pointer identity and aliasing within
those ranges, and unregisters freed storage. The Windows x86 flat-memory profile
reserves the main image namespace through a replacement reservation DLL before
host CRT allocation, then supplies checked non-executable data/stack/TLS backing
at guest addresses. Explicit native adapters can use validated live spans there;
arbitrary pointer/signature guesses remain refused. Native allocation collisions
with guest-owned storage stop explicitly.

Volatile native GPRs/flags remain unknown unless specified by a bridge. The actual
CRT uses `PUSH ECX` to allocate scratch after such calls. This now stores unknown
bytes with shadow state; overwriting them makes them readable, while observing
unknown bytes still fails. It does not invent a callee-preserved ECX or a zero
result. The focused scratch regression guards this startup debugging fix.

`local/recomp/startup/latest.json` records the latest attempt;
`last-execution.json` and `history/` retain executed frontiers even if a subsequent
build fails. The runner stages source projects, preserves main-project annotations,
builds a real PE32 launcher and records calls, native returns, PC, register
definedness, consumed dispatch units and failure reasons. Use
`tools/ghidra/ExportFunctionBounds.java` for a bounds-only Umbra inventory; the
older `ExportInventory.java` additionally expects DAO-specific selected functions.

### Module boundary

[`modules.json`](modules.json) records the requested policy: translate the pinned
DAO and Umbra binaries, keep other dependencies native for now. The module hashes
are checked during generation. Native imports still require explicit contracts;
"native" does not mean an arbitrary unknown signature is callable. Imports from
Umbra that remain unbound are rejected before any native handler can run.
There is no native Umbra fallback.

The pinned Umbra DLL has 154 named exports and 89 IAT slots, all naming KERNEL32.
Its separate project under ignored `local/recomp/umbra` initially generated and
compiled `ReferenceCount::getReferenceCount` and
`Commander::Instance::getClipMask`. Export-name declarations and demangler identity
are retained in `symbol-declarations.json`. This is compile/link evidence only:
global initialization, delegated internal callees and actual object contracts are
not validated for those two exports. Combined module/data linkage is implemented
above. The imported Commander group below adds bounded execution evidence for
eleven different exports and three internal helpers.

```sh
python3 -m tools.recomp --project local/recomp/umbra new gamedata/bin_ship/umbra.dll
python3 -m tools.recomp --project local/recomp/umbra add --rva 0x60180 --size 50
python3 -m tools.recomp --project local/recomp/umbra add --rva 0x5fe50 --size 56
python3 -m tools.recomp --project local/recomp/umbra generate
```

### Imported Umbra Commander group

The current combined bundle additionally contains eleven functions actually
imported by DAO: the OcclusionQuery index, vertices, vertex count, triangle count,
triangles and wait-byte getters, its result setter, and Commander's viewer,
occlusion-query, instance and text accessors. Three internal helpers complete the
selected call paths. Each entry has a pinned module/RVA identity, original slice
and instruction hashes, machine-state preconditions, instruction-derived behavior,
observations and exclusions in
[`contracts/umbra-commander.json`](contracts/umbra-commander.json).

```sh
python3 recompiler/experiments/compare_umbra.py \
  --wine 'local/tools/recomp/Wine Stable.app/Contents/Resources/wine/bin/wine' \
  --cc local/tools/recomp/llvm-mingw-20261104-ucrt-macos-universal/bin/i686-w64-mingw32-clang
```

This experiment loads the original pinned DLL normally under Wine and runs the
selected original functions against explicit memory graphs and a controlled
module global. It does not construct source-language objects or call
`Library::init`. The candidate maps original data and runs compiled C++ without
loading the DLL or running module initialization. Generation uses staged recovery
projects; a successful report does not promote the accepted recovery registry or
overwrite the main project's annotations. The validated selections have been
added to the local Umbra project and its remembered combined bundle.

The bounded corpus covers both global-controlled layouts, zero/nonzero and
all-bits instance sentinels, unaligned and aliased objects, and the setter's two
sequential stores when the first store changes the pointer used by the second.
The wait-byte getter retains pointer-derived upper EAX bits. All eight raw GPRs,
ESP cleanup, five defined arithmetic flags and every arena byte are compared.
Native stack guards and the DLL's writable data frame are checked; the candidate
rejects writes outside the declared arena/stack frame. Internal scratch stack
bytes, AF on logical paths and actual object-lifetime invariants are explicitly
outside this contract.

Inputs and harness sources are frozen for a run. Changed input bytes, malformed
or missing observations, non-return outcomes, budget exhaustion, unknown calls,
nondeterminism and semantic differences cannot produce a successful report.
Compiled helper-return and setter-store corruptions must produce semantic
differences. Reports, observations, native/candidate build artifacts and replayable
cases remain under ignored `local/recomp/umbra-commander/`.

The separate call experiment constructs a synthetic PE32 image, executes its
exact x86 instruction bytes under Wine, and compares them with generated x86/x64
candidates calling Wine's real Kernel32 API. The native fixture uses preferred
base `0x30000000` because the native CRT heap occupies `0x400000` in this setup;
native and candidate bytes both come from that same constructed image. This
experiment is tooling evidence, not DAO or Umbra equivalence evidence.

```sh
python3 recompiler/experiments/compare_calls.py \
  --wine 'local/tools/recomp/Wine Stable.app/Contents/Resources/wine/bin/wine' \
  --cc local/tools/recomp/llvm-mingw-20261104-ucrt-macos-universal/bin/i686-w64-mingw32-clang
```

## Wine experiment

Wine 11.0 and llvm-mingw were installed under ignored `local/tools/recomp/` from
the maintained upstream archives, with SHA-256 verification:

| Archive | SHA-256 |
| --- | --- |
| [Wine 11.0_1](https://github.com/Gcenx/macOS_Wine_builds/releases/tag/11.0_1) | `b50dc50ec7f41d58b115a6b685d4d1315ba3c797bd3aa0f49213f2703cb82388` |
| [llvm-mingw 20261104 macOS universal UCRT](https://github.com/mstorsjo/llvm-mingw/releases/tag/20261104) | `66cbd5178c4a71b0d473e68ede172f8eb7d15d023e67f39201d0a69e21f6bf3c` |

The experiment requires both selections above in the current generated view:

```sh
python3 recompiler/experiments/compare_wine.py \
  --wine 'local/tools/recomp/Wine Stable.app/Contents/Resources/wine/bin/wine' \
  --cc local/tools/recomp/llvm-mingw-20261104-ucrt-macos-universal/bin/i686-w64-mingw32-clang
```

The reference runner executes the two pinned original instruction slices as real
PE32 code under Wine's WoW64 layer and Rosetta. Their direct instruction bytes
establish that these selected slices need no image relocations, imports, globals
or initialized game runtime. This is not a general way to call arbitrary functions
from an EXE. The runner uses ECX for the object and the observed stack convention.
Each deterministic fixture checks full EAX, ECX normalized to arena offset, and
every one of 512 arena bytes. The generated C++ runs as both a Windows x64 EXE
under Wine as x86 and x64, and as native macOS ARM64, with a separate ASan/UBSan run.
The controller repeats each normal side twice, rejects missing/malformed output,
and requires a compiled store-bit mutation to produce a semantic disagreement.
All candidates explicitly represent guest32 values and addresses. The x86
candidate and original use the same Windows bitness.

Cases, full observations, executable/source hashes, host/tool versions, and the
bounded report are retained under `local/recomp/wine-comparison/`. These are new
experimental observations, not promotion of existing contracts or registry status.
Original flags, stack footprints, exceptions, dependency effects and full game
execution are outside this experiment. Wine agreement is not native x86 Windows
hardware evidence or proof of general function/game equivalence.

The separate `compare_copy_structures.py` experiment selects `fn_0052ab70`, with
thirteen observed fields on each of two bases: eight bytes, four words and one
dword. Its original instructions perform sequential loads/stores without imports
or image address dependencies. It includes unaligned, identical and partially
overlapping source/destination ranges, comparing arena-relative EAX, raw full ECX
and every arena byte. It reuses the leaf experiment's exact observation parser
and comparison with a separate recorded bounded corpus.

```sh
python3 -m tools.recomp add --rva 0x52ab70 --size 103
python3 -m tools.recomp generate
python3 recompiler/experiments/compare_copy_structures.py \
  --wine 'local/tools/recomp/Wine Stable.app/Contents/Resources/wine/bin/wine' \
  --cc local/tools/recomp/llvm-mingw-20261104-ucrt-macos-universal/bin/i686-w64-mingw32-clang \
  --output local/recomp/wine-structures-copy32
```

Normal Windows x86/x64 and ARM64 candidates must agree, including repeats and
ASan/UBSan. A compiled corruption of a byte-field store must produce a semantic
difference; crashes and malformed output do not count. The earlier leaf
experiment retains its original slices, fixtures, comparisons and required
store-bit mutation; mutation-site selection additionally recognizes field setters.
Both stateless experiments reuse ignored `local/recomp/wine-prefix` to avoid
duplicating Wine's Windows files for every report. `--wine-prefix PATH` overrides
this. This is a shared OS configuration, not game-runtime snapshot isolation.

## Remaining work

1. Carry origins through high-level value recovery, lifetime splitting and merges.
2. Refine ABI observations into reviewed source signatures and callee preservation
   summaries, including narrow returns, hidden inputs and decorated export types.
   Extend translated Umbra coverage and add native pointer/callback adapters.
3. Expand instruction semantics and Windows runtime boundaries, including x87,
   SSE, indirect calls, imports, globals, TLS, SEH and initialization. Unknown
   operations/calls must remain explicit blockers.
4. Extend Wine comparisons to reviewed function contracts and initialized runtime
   scenarios, then compare replacement-executable scenarios using original assets.

## Verification

`tests/test_recomp.py` constructs synthetic PE32 containers. Its checks exercise
annotation persistence across control-flow emission, stale/invalid edits, changed
binary/view bytes, missing origins, incomplete ranges, separately compiled linkage,
wraparound, return/stack handling, guest-address registry invocation, unknown-target
failure and budget exhaustion with ASan/UBSan. `tests/test_recomp_structures.py`
adds sixteen synthetic functions for field/base recovery, overlapping widths,
nested and stack-loaded pointers, joins, indexed/segmented refusal, pointer aliasing,
modular offsets and changed entry registers. Compiled views are compared with the
raw baseline over all registers, flags/definedness, PC, memory and ordered memory
effects across bounded budgets and single-instruction resumption. A changed
accessor displacement must cause a trace/state mismatch.
Those checks test the recovery tooling, not game behavior.

`tests/test_recomp_link.py` adds constructed modules with equal function RVAs,
module-scoped identities, named/ordinal and data exports, IAT and indirect vtable
calls into a translated provider, shared mutable globals and zero-filled BSS.
Compiled sanitizer checks cover call/return and budget resumption, memory holes,
permissions, range overflow, loader artifact corruption, and SHA-256 padding
boundaries. Missing code/exports and forwarders cannot become native fallbacks;
failed strict generation preserves the previous view and composition.

```sh
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s tests -p test_recomp.py -v
```

Use the repository virtual environment for the full existing suite's pinned
Unicorn dependency. Additional SharpRetro machine-backend integration checks run
from that repository with `python3 -m unittest discover -s Decompiler/tests -p test_pipeline.py -v`.

Initial checkpoint, 2026-11-07: macOS 27.0.1 ARM64, .NET 10.0.101, Apple Clang 21.
Both the original generated view and a regenerated view with `loaded_flags: u32`
agreed on 190 cases for each selected DAO function across Wine and native candidates;
the store-bit mutation was detected. The annotated report is retained separately
at `local/recomp/wine-comparison-annotated/report.json`. The project-venv tooling
run completed 238 tests with one skip, all six C++ CTest checks passed, and both
59-case synthetic demo commands succeeded (the negative control found six
semantic mismatches). SharpRetro's nine existing machine-backend pipeline tests
and five new controller integration tests passed. An earlier system-Python 3.15
run had five missing-Unicorn-related errors; the successful full run used the
project's pinned virtual environment. These are observations on this host/build.

Structure/PE32 checkpoint on the same host: all three selected translations link
into a real Windows x86 `recomp_image.exe`, which launched under Wine and listed
their three guest addresses. Source/field annotations remain in the current view.
The two leaves agreed across 190 cases each and the thirteen-field copy across
226 cases, with Windows x86/x64 and ARM64 candidates, repeats, sanitizers and
detected store-bit mutations. Current reports are
`local/recomp/wine-structures-leaves32/report.json` and
`local/recomp/wine-structures-copy32/report.json`; bundle launch evidence is
`local/recomp/bundle-launch.json`. All 242 project-venv tests passed with one skip,
all six C++ checks passed, the nine SharpRetro machine pipeline checks passed,
and both synthetic demos retained their expected 59-case results.

An intermediate run exhausted local disk space while duplicating Wine prefixes;
it failed rather than producing comparison passes. Disposable prefixes were
removed and the final full suite/comparisons reran successfully. The two earlier
`wine-structures-copy`/`wine-structures-leaves` folders are marked superseded
because controller source changed during those runs; use the `*32` reports above.

Call/import checkpoint on macOS ARM64, .NET 10.0.101 and llvm-mingw Clang 23.1.5:
all 245 project-venv tests passed with one skip, all six C++ checks passed, all
nine SharpRetro machine pipeline checks passed, and both synthetic demos retained
their expected 59-case outcomes. The synthetic call experiment agreed across
285 cases with two fresh process runs per side, using native x86 instructions and
real Kernel32 MulDiv under Wine against generated x86/x64 candidates. The changed
callee-result control was detected. Its report is
`local/recomp/call-comparison/report.json`; it does not validate game functions.
Fresh checks of the three earlier DAO functions still agreed across 606 cases
with their mutation controls, under `local/recomp/call-regression-leaves/` and
`local/recomp/call-regression-copy/`. These reports supersede older views for the
current experimental generator, without promoting the accepted recovery registry.

The two selected Umbra exports compiled into a separate PE32 diagnostic bundle
and its address listing launched under Wine (`local/recomp/umbra/launch.json`).
No Umbra function body was executed or compared in that diagnostic launch.

Cross-module checkpoint on macOS 27.0.1 ARM64, .NET 10.0.101 and llvm-mingw Clang
23.1.5: the combined PE32 DAO/Umbra diagnostic bundle compiled and launched under
Wine 11, listed five selected functions and loaded nine data regions. All 44 DAO
Umbra imports resolved to actual export addresses; **none of those 44 imported
entries is currently translated**. The two previously selected Umbra functions
are different exports. Strict generation correctly refused the incomplete bundle
without replacing its current view. Evidence is under
`local/recomp/linked-generation.json`, `linked-build.json`, `linked-launch.json`
and `linked-strict-check.log`. This launch did not execute game or module
initialization, including DAO's TLS initialization.

The synthetic EXE/DLL experiment agreed on 198 cases, twice per side, between
Windows-loader x86 originals and generated Windows x86/x64 and sanitized native
ARM64 candidates. Shared globals persisted across calls, candidates ran with
the original provider DLL removed, and callee corruption produced 198 semantic
mismatches. Its reproducible report is `local/recomp/link-comparison/report.json`.
The Python suite completed 248 tests with one skip; all seven CTest checks
(including the tooling suite), nine SharpRetro machine pipeline checks and both
synthetic demos passed, with the negative demo retaining six expected mismatches.
These are bounded infrastructure observations on this host/build, not game
function equivalence or a working replacement game executable.

Umbra Commander checkpoint, 2026-11-08, on the same macOS ARM64 host and
llvm-mingw Clang 23.1.5/Wine 11 toolchain: eleven imported Umbra exports and three
internal helpers agreed with original DLL execution across 888 constructed
machine states, twice per side, on generated Windows x86/x64 and sanitized native
ARM64 candidates. Helper-return corruption caused 80 semantic mismatches and
setter-store corruption caused 48. See `local/recomp/umbra-commander/report.json`
and the tracked contract above. These are bounded path observations, including
both global-controlled object layouts, rather than object-lifetime or visibility
scenario validation.

The selections were integrated into the main remembered DAO/Umbra composition.
Its nineteen functions rebuilt into a PE32 library/executable; an adapter linked
against that CMake-built library repeated the 888-case original-DLL comparison
successfully. The main executable launched under Wine, listed all nineteen
functions, reported eleven translated and 33 still untranslated Umbra import
entries, and verified nine data regions. Generated source/data files matched the
validated staged view exactly. Integration evidence is
`local/recomp/umbra-commander/main-integration.json`, with generation/build records
in `local/recomp/umbra-main-generation.json` and `umbra-main-build.json`.

The full Python suite completed 250 tests with one skip, all six native CTest
checks passed, and both synthetic demo commands retained the expected 59-case
outcomes (six semantic mismatches in the negative control). Accepted recovery
registry counts were not changed. The remaining 33 imported Umbra entries,
initialization/TLS/SEH, broader native bridges and whole-game startup remain
unfinished.

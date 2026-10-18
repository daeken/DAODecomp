# Function equivalence

**Current workflow:** candidate generation is independent of validation. New
functions must not require authored contracts, fixtures, corpora, adapters or
proof annotations. The [automatic checking direction](automatic-checking.md)
supersedes the per-function preparation workflow below. Existing validators and
accepted results remain historical evidence; the following protocol documents
their behavior and the general equivalence problem, not a prerequisite for
generating new candidates.

We want corresponding initial states to produce corresponding observable outcomes:

```text
For all states s satisfying precondition P:
  observe(original(s)) = observe(candidate(map_input(s)))
```

`observe` includes the return value, externally visible memory, ordered external
effects, and termination behavior. The state mapping relates pointers/objects and
ABI layouts between the reference and replacement. Internal registers, private
stack layout, allocation addresses, compiler output and instruction counts need
not match. Calling-convention obligations still matter when crossing a binary ABI.

The largest early risk is an incomplete state contract. Comparing only return
values can miss corrupt object fields, globals, missing calls or changed error
behavior. A correct comparison of an incomplete observation is still incomplete.

## Three complementary forms of evidence

| Method | What it establishes | Best use |
| --- | --- | --- |
| Concrete differential execution | Agreement on the enumerated inputs/state | Default for every recovered function |
| Exhaustive finite enumeration | Agreement for every member of a small explicitly finite domain | Tiny enums, table transforms and bounded bit operations |
| Symbolic translation validation | No behavioral difference under a stated model and domain, if the check completes soundly | Small integer leaves and bounded memory routines |

Tests are deterministic evidence, not universal proofs. Function proofs are
conditional on input relations, dependency contracts and instruction semantics.
Composition needs caller/callee preconditions to agree, plus integration and
scenario tests; many individually passing functions do not establish a working game.

## Deterministic execution plan

1. Pin executable and dependent-module hashes. Index by RVA, independent of ASLR.
   Record compiler, target, flags, source revision/patch, adapter, loader, emulator,
   OS/runtime, CPU features and corpus/contract hashes.
2. Establish entry/exit points and ABI: stack cleanup, hidden structure returns,
   `this`, nonvolatile registers, exception conventions and TLS where relevant.
   For x86 MSVC `thiscall`, `this` normally uses ECX; confirm each actual function.
3. Build an explicit state: parameters, reachable object graph, globals, TLS and
   dependency state. Preserve aliasing, overlapping buffers and interior pointers.
   Generate only valid object graphs unless testing an observed invalid-input path.
4. Run each side from an independent identical snapshot. Restore memory and CPU/FP
   state completely or use fresh workers. A fresh process alone does not initialize
   a game object or neutralize files, services and persistent runtime state.
5. Replace time, randomness, filesystem enumeration, handles, allocation identities
   and OS callbacks at defined boundaries with deterministic tapes. Intercept all
   relevant sources, including direct timestamp instructions. Match call name,
   arguments, order, return and writes. Extra/missing calls or unconsumed tape entries
   fail. Compare allocator-visible effects when callers can observe them.
6. Capture return bits, typed fields/declared memory, globals and effect traces.
   Normalize pointers using object identity + offset while preserving aliasing and
   null distinctions. Exclude only reviewed padding/unobservable storage; every
   excluded byte needs a reason. Detect writes outside the declared footprint.
7. Repeat original/original first to find unstable fixtures, then candidate/candidate
   and original/candidate. Store failing input/state in full, minimize it while
   preserving validity, and add it to the regression corpus.

For floating point, start with exact observable bit patterns. Capture x87 precision,
rounding and tag/status state, MXCSR/FTZ/DAZ, NaNs and signed zero. Do not introduce a
global epsilon or fast-math to hide differences. Any tolerance needs a function-local
behavioral justification and is a weaker contract. Our CMake disables fast-math and
contraction; this alone does not reproduce an original x87 pipeline on ARM64.

Concurrency needs recorded scheduling or a bounded scheduler and explicit memory
ordering; a single-thread fixture cannot certify concurrent behavior. File/network,
graphics and sound dependencies need domain-specific runners. Rendering should also
compare resource/command behavior before adopting any image tolerance.

## Execution backends

| Backend | Role | Caveat |
| --- | --- | --- |
| Native Windows x86/x64 reference host | Authoritative execution on supported original architecture; initialized-state capture | Requires host and per-function invocation/capture adapter |
| Unicorn CPU emulator | Portable, fast-to-construct isolated integer/memory fixtures | CPU emulator, not a Windows loader/runtime; validate relevant semantics against native execution |
| Wine or Windows on ARM | Useful experiments and capture path if available | Record translation layers and corroborate before treating results as authoritative |
| SharpRetro XFusion lift | Candidate instruction-to-IR front end for analysis and proofs | Audit supported semantics; see sharp-retro.md |

The recommendation is to select a native Windows reference host when convenient,
while developing isolated fixtures locally. It need not block C++ implementation
or infrastructure. An EXE cannot simply be loaded as a DLL and arbitrary RVAs called:
relocations, imports, TLS, initialization, object lifetime and calling convention
must be accounted for. Live process capture may be preferable for stateful functions.

## Symbolic validation without rewriting the game in Dafny

For a selected function, lift **the original machine code and the compiled candidate
machine code** to a common semantic representation. Initially compile candidates
for the same guest ISA/ABI to reduce mapping complexity. A later native port needs
its own validation; a proof of one compiled build is not a proof of every C++ build.

Supply shared symbolic inputs and related initial heaps. Use bitvectors for machine
integers (including overflow); encode memory as byte arrays, conditions as formulas,
and modeled effects as traces. Query:

```text
P(inputs, state) AND observable_difference(original, candidate)
```

- `SAT`: solver found a candidate counterexample. Replay it against independent
  concrete execution to distinguish a code bug from an inaccurate model.
- `UNSAT`: no difference within the precisely recorded model and domain, provided
  all feasible paths/outcomes are represented and exploration is complete there.
- `UNKNOWN`, timeout, unsupported op, unresolved call, path budget or memory-address
  concretization: inconclusive. Never convert these into a pass.

Also establish nonempty preconditions, path-domain coverage for BOTH programs,
termination within the domain and frame conditions for untouched memory. Otherwise
an empty or incomplete path set can make a difference query vacuously unsatisfiable.
If loops are bounded, either state that bound as a domain limitation or prove no
valid execution exceeds it. General loops may need invariants/induction; recursion
and dependent calls need sound summaries. Uninterpreted calls are acceptable only
as explicitly justified shared contracts, not as a way to skip unknown behavior.

Potential implementations: a SharpRetro LiftIl-to-SMT backend for a restricted
integer subset, or an angr/Triton prototype. angr's documented default symbolic
memory concretizations and imperfect library summaries require special care; a
generic `explore()` success is not an equivalence certificate. Dafny could verify
handwritten algorithms, but adds a separate obligation connecting that model to
the original binary. It is not required for this workflow.

No symbolic checker is implemented in this scaffold. A useful next experiment is
one loop-free game leaf, an independently decoded/lifted candidate, and both a
successful check and a solver-generated counterexample for a known mutation.

## Implemented protocol v1

`python3 -m tools.daodecomp compare --help` exposes the comparator. Command files
contain JSON argv arrays, avoiding shell interpretation. A runner receives exactly
one JSON request on stdin and emits exactly one observation on stdout; diagnostics
go on stderr. One process per fixture/side/repetition. Request:

```json
{"schema_version":1,"function_id":"module-hash:rva","case":{"id":"edge-001","inputs":{"value":0}}}
```

Observation:

```json
{"schema_version":1,"case_id":"edge-001","termination":"return","return":0,"memory":{"counter":"0000000000000000"},"calls":[]}
```

The contract supplies exact input keys/types (`u32`, `i32`, `bool`, `bytes`, `void`),
return type, exact memory region names/byte counts, and allowed dependency names.
Each call is `{"name":"...","args":[],"result":null}` and order is significant.
The adapter owns function-specific preconditions and dependency argument semantics.
The comparator does not infer missing reads/writes or validate that the adapter's
contract captures every effect. That requires instrumentation and independent review.

Memory is lowercase hex in the declared serialization order. Floating values use
IEEE bit encodings as bytes; JSON floats, NaN, duplicate keys, missing fields, wrong
types, empty corpora and duplicate case IDs are rejected. v1 supports **normal
return only**. Exception/error outcome modeling must be added explicitly before
accepting such game functions. Crashes and timeouts always fail, even on both sides.

Reports contain hashes, commands, host, repetition count and per-case results. They
never claim proof. Passes store observation digests; failures include full observations
and replay input. Pass acceptance uses exact, type-sensitive equality, not text order
or tolerances. List every executed file/adapter/module with `--artifact`; the harness
does not discover dynamic dependencies automatically. Build configuration and backend
versions must accompany accepted game evidence. Generated local reports alone do not
promote inventory status. On POSIX timeouts kill the worker process group; on Windows
only the direct process is killed, so a future game runner must use a Job Object or
equivalent lifetime control for its descendants. This is not a security sandbox.

## Sources

- [Ghidra headless analysis](https://github.com/NationalSecurityAgency/ghidra/blob/master/Ghidra/RuntimeScripts/support/analyzeHeadlessREADME.md)
- [Unicorn concrete execution tutorial](https://www.unicorn-engine.org/docs/tutorial.html)
- [Microsoft x86 thiscall](https://learn.microsoft.com/en-us/cpp/cpp/thiscall?view=msvc-170)
- [Microsoft floating-point control](https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/control87-controlfp-control87-2?view=msvc-170)
- [Frida invocation and interception APIs](https://frida.re/docs/javascript-api/)
- [angr modeling caveats](https://docs.angr.io/en/stable/advanced-topics/gotchas.html)
- [Triton symbolic instruction semantics](https://triton-library.github.io/)


## Opt-in fresh-child indexed-field batching

On POSIX hosts supporting `fork`, `waitid(WNOWAIT)` and `/dev/fd`, build the usual
CMake targets and opt into the indexed-field adapter with:

```sh
.venv/bin/python validation/validate_indexed_fields.py --execution batch --suite public --jobs 2
.venv/bin/python validation/validate_indexed_fields.py --execution batch --suite heldout --jobs 2
.venv/bin/python validation/validate_indexed_fields.py --execution batch --expect-mismatch --jobs 2
```

`--execution single` remains the default and the existing reference/fallback.
Batching does not reduce cases, repetitions or observations. Each side/repetition
starts an independent clean Python supervisor. It verifies immutable module/slice
bytes or loads the native C ABI adapter, but never executes a function itself.
Every case runs in a fresh child session/process group with a new arena and, for
the original side, a new Unicorn machine. Native candidate calls use the unchanged
accepted C++ bodies through a separately built shared adapter, inside the child.
No initialized game runtime or native/Unicorn state is recycled.

Batches contain at most 128 cases (`--batch-size 1..128`), each request frame at
most 256 KiB and each supervisor at most 8,192 cases/32 MiB of input or output.
Case stdout is capped at 64 KiB and stderr at 4 KiB; every case has a five-second
wall deadline plus the original instruction budget. Supervisors have a separate
finite deadline. A case crash, timeout, unknown dependency, exhausted budget,
missing/duplicate/reordered identity, malformed output or output cap violation
cannot pass. After a case execution error, remaining cases are explicit runner
errors. Missing whole-worker output marks every requested case as a runner error.
The comparator retains its exact type-sensitive observation and nondeterminism
rules, full failure replay observations and artifact hashes checked before/after.

Case groups are killed on completion or failure before their leaders are reaped.
A start gate and atomic active-child record let the controller kill a case group
if its supervisor fails. This handles descendants that remain in that group;
processes deliberately escaping it with another session are outside this runtime's
isolation model. The backend is not a security sandbox. Darwin's EPERM for a
zombie-only group is accepted only after libproc reports no live group members;
EPERM with a live/unknown member fails closed. Actual crash/hang/descendant/output
faults are tested in `tests/test_batch.py`.

The initial adapter allowlist is the eleven existing `indexed-fields-002` call-free
integer/explicit-memory functions. Extending it to globals, TLS, floating point,
OS state or dependencies requires a separately reviewed adapter/state contract.
The runtime cannot certify native Windows semantics or whole-game behavior. New
reports require the same public, heldout, negative-control and independent-review
gates; this transport option does not promote registry status by itself.

For paired recovery, `tools/freeze_indexed_fields_pair.py --execution batch` selects
batching for public, heldout and negative commands in the generated manifest.
Default manifests retain the legacy path. Batch freezing additionally requires
independent acceptance-review hash coverage of the transport, native/Python adapter,
real fault tests, coordinator binding checks and these runtime limitations. The
snapshot includes all new source/test support files. Each deterministic report
binds the actual newly linked shared library, wrapper/runtime, accepted candidate
source and build inputs; the paired coordinator rejects missing library or process
provenance bindings. A dry-run prepares review material without approval or dispatch.

## Complete incremental checkpoint composition

Routine checkpoint plans select approved fresh-child batching for indexed fields
and object bitfields plus direct object fields, retaining all six legacy groups and their controls. The direct-field group requires all22 implementations and controls; complete publication requires69 positive and48 negative reports. Batch
size, mode and effective validator argv are execution-key inputs. Cache policy
`clean-build-local-groups-003` adds explicit normal/mutant shared-image and selected
object-fixture/specification bindings; it never backfills earlier policy entries.

Every invocation recreates its owned direct-child `build-incremental*` directory
at the same stable path, then configures and builds current source with reproducible
Apple linker settings. Selected outputs/dependencies must exist as regular files.
Full current source/build attestations remain separate from comparison identity.
Runtime-provider symlinks retain their original lookup paths and resolved targets;
the target bytes are hashed, and changed resolution during inventory or hashing
fails. This does not permit symlinked candidate/build artifacts. The independent
[runtime-provider review](../analysis/reviews/runtime-provider-links-001.json)
covers this distinction.
Missing/ambiguous routes, partial fifteen-function promotion, missing libraries,
changed selected contracts/corpora, stale generated targets or incomplete controls
cannot produce reusable current evidence. Publication and the v2 updater additionally
require every implemented positive and required negative record, without duplicates.

After independent combined approval and source integration, run the incremental
checkpoint with a stable shared build/cache path and a new output/record path,
then refresh README with the ordinary progress updater. A partial `--group` or
`--identity-only` experiment cannot publish progress. Historical comparisons stay
immutable; a complete fresh checkpoint supplies current provenance. Local runtime
reuse currently supports macOS only and is emulator corpus evidence, not game proof.

Batched execution requires Python to expose POSIX `fork`, `waitid` and `WNOWAIT`.
Unsupported interpreters refuse batched execution before launching a process;
their real-process batch tests are explicitly skipped while refusal tests still
run. Local production batch evidence used macOS ARM64 with Python 3.14.7;
Windows CI and unsupported macOS interpreters do not establish batch support.

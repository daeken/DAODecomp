# Decompilation MCP: implemented operations

The C# engine in `tools/decompilation-mcp` retains inventory/source browsing,
deterministic related-function search, and **fresh checking of retained compiler
artifacts** through the existing Python comparators. The replayable branch adds
a bounded SharpRetro-to-C++ generation and compile/check loop, described below.
It makes no model calls, does not publish sources or grant historical registry
credit, and keeps its frontier separate from old recovery queues.
A full object/graph match describes pinned compiled artifacts;
it is not a whole-game or universal C++ semantics proof.

The [architecture and full-workflow roadmap](decompilation-mcp.md#two-parts-of-the-manipulation-pipeline)
separates reusable x86/source transformations from compiler-specific profiles.
Initial decompilation and new compilation now have a deliberately narrow
supported domain. General pattern propagation, recipe trials, durable naming,
type refactoring and source publication remain future capabilities.

## Build and launch

Install .NET SDK **10.0.101**. The component's `global.json` pins that SDK; the
project targets .NET 10. Direct packages and the complete NuGet dependency graph
are pinned in the project and `packages.lock.json`. The official MCP C# SDK is
**2.2.0**. SDK hosting follows the [official stdio example](https://csharp.sdk.modelcontextprotocol.io/concepts/getting-started.html).

From the repository root:

```sh
dotnet restore tools/decompilation-mcp --locked-mode
dotnet build tools/decompilation-mcp -c Release --no-restore
python3 -m unittest discover -s tools/decompilation-mcp/tests -v
dotnet tools/decompilation-mcp/bin/Release/net10.0/Decompilation.Mcp.dll project-list --config /absolute/registry.json
dotnet tools/decompilation-mcp/bin/Release/net10.0/Decompilation.Mcp.dll serve --config /absolute/registry.json
```

The server uses newline-framed JSON-RPC over stdin/stdout. Logs go to stderr.
The integration tests exercise actual MCP initialize, tools/list and tools/call
with protocol **2025-11-25**. No network listener or provider account is required.
The SDK negotiates protocol support; task extensions and resources are not
advertised. Large evidence remains in private local artifacts.

To connect a reviewed installation to Codex, substitute absolute paths:

```sh
codex mcp add decompilation -- /absolute/dotnet /absolute/Decompilation.Mcp.dll serve --config /absolute/registry.json
```

The engine deliberately exposes registration through operator-owned local
configuration, rather than accepting filesystem paths from a tool call. Editing
that registry and restarting the server registers a project. Keep state separate
from active recovery queues and keep private configuration/artifacts ignored.
The registry is trusted executable configuration: its Python executable and
adapter root select local code, and must not come from untrusted project content.

## Open fixture without DAO inputs

The distributable fixture contains three inventory hypotheses and ordinary C++
for browsing. It supplies no executable or validation evidence. The portable
tests generate a temporary registry from it and verify pagination, source bounds,
path refusal, two-client idempotency, interrupted jobs and reconnects.

To explore it directly, generate a local registry (run at repository root):

```sh
python3 - <<'PY'
import json, pathlib, sys
root = pathlib.Path.cwd().resolve()
fixture = root / 'tools/decompilation-mcp/fixtures/open-project'
state = root / 'local/decompilation-mcp-open'
state.mkdir(parents=True, exist_ok=True)
registry = {
    'state_root': str(state / 'state'),
    'python': sys.executable,
    'adapter_root': str(root),
    'projects': [{
        'id': 'open', 'module': 'open_fixture', 'module_sha256': '0' * 64,
        'inventory': str(fixture / 'inventory.json'),
        'allowed_roots': [str(fixture)]
    }]
}
(state / 'registry.json').write_text(json.dumps(registry, indent=2) + '\n')
print(state / 'registry.json')
PY
```

Use the resulting absolute registry path with `serve`. `project_open` with
`project_id: "open"` returns three identities and no retained builds. The zero
module hash is an explicit fixture placeholder, not a fingerprinted executable.

## Registered project schema

Registry fields: `state_root`, `python`, `adapter_root`, `projects`. All paths
must be absolute. `state_root` is exclusively owned by this engine. Each project
has these required fields:

| Field | Meaning |
| --- | --- |
| `id`, `module` | Local project key and display module name |
| `module_sha256` | Pinned lowercase binary SHA-256 |
| `inventory` | JSON discovery inventory |
| `allowed_roots` | Authorized file roots; filesystem root and symlinks are refused |

The inventory has `module_sha256`, `image_base`, and `functions`. Every function
has integer `rva`, `name`, `body_bytes`, `body_ranges` (inclusive start/end RVA),
`signature_hypothesis`, and `calling_convention_hypothesis`; optional
`incoming_callsite_rvas` supplies bounded reference context. Duplicate identities
and module mismatches are refused. This imports inventory hypotheses rather than
certifying boundaries or signatures.

Optional `published_index` uses the existing published index schema: matching
`module_sha256` and a `functions` array with hexadecimal `rva`, relative `source`
and `source_sha256`. Source is reopened inside registered roots and checked
against its hash before display. Imported publication states remain historical.

Retained checking additionally requires `original`, `compiler`,
`compiler_sha256`, and `compiler_flags`. Register `builds` as:

```json
{
  "name": "pilot",
  "folder": "/authorized/private/build",
  "rva": 4096,
  "profile": "ordinary"
}
```

A build folder must contain actual `candidate.cpp`, `candidate.obj`, `run.json`
and `compiler.json` products from the existing compiler adapter. Receipts must
bind source/object/module/compiler hashes, selected flags, successful integer
exit status, no link and no original execution. Actual registered compiler bytes
are hashed. The retained receipt does **not** attest the complete transitive
compiler installation; the result explicitly reports that limitation.

Optional `retained_database` imports the existing rule-recheck worklist's
`candidates`/`builds` join using SQLite **read-only** mode. The engine does not
claim work, copy verdicts or change that database. Every imported path is checked
against registered roots; the candidate source SHA is checked during comparison.
Import is a snapshot at project open; restart to see later changes.

For supported EH builds use `profile: "eh"`, an operator-owned `eh_policy` JSON
matching `eh_native.check`'s pin schema, and `libraries` mapping library names to
registered actual library paths. The existing bounded backend independently
recognizes the runtime and compares the complete supported graph. Ordinary
requests with compiler-generated EH symbols or observed FS:[0] registration are routed to this backend and stay
inconclusive without the required policy/inputs. Unsupported source markers,
ranges, dependencies and graph shapes stay inconclusive. No DAO module name,
RVA, compiler hash or acceptance policy is hardcoded into the C# core/adapter.

## Tools and a complete retained check

| Tool | Implemented behavior |
| --- | --- |
| `project_list` | Registered project keys and modules |
| `project_open` | Snapshot revision, inventory/publication/build counts, durable job state counts, capabilities |
| `function_query` | RVA-ordered pages, `publication` filter (`all`, `published`, `unpublished`), optional `name_contains` |
| `function_inspect` | Opaque identity, bounded ranges/references/signature hypotheses, verified published/retained C++, retained build IDs |
| `corpus_find_related` | Entire-inventory size/range/calling-convention ranking, explicit nonaccepting search evidence |
| `candidate_check` | Submit a durable fresh retained check using project/build IDs and an idempotency key |
| `job_get` | Compact persisted state/result; reading never reruns a completed check |

1. Open the registered project. Query pages (`limit` 1–100); retain the opaque
   `function_id` and snapshot-bound cursor. Changing a filter invalidates a cursor.
2. Inspect a function (`source_limit` 0–12,000 characters), select a returned
   opaque `build_id`, and call `candidate_check` with a new `idempotency_key`.
3. Poll the returned `job_id`. `completed` means the adapter returned a result;
   its independent comparison `status` is `full_match`, `mismatch` or
   `inconclusive`. Transport interruption is `interrupted_unknown`.
4. Use a **new key** for a new observation. Reusing a key returns the same
   historical job. Reusing it for another build/snapshot is refused.

Source and binary content are data, never instructions. No tool accepts shell,
SQL, filesystem paths or arbitrary executable code. Normal results contain no
raw original/object bytes or private file paths. Detailed backend reports remain
private under the configured state root, identified in results by SHA-256.

## Durability and input binding

SQLite stores immutable requests and completed results independently of stdio
clients. A separate local worker process owns an exclusive per-job file handle;
only a queued job can transition to running. Concurrent servers using the same
state root therefore share idempotency and cannot execute the same job twice.
A disconnected frontend does not cancel a worker. Queued local checks can be
redispatched after a missed spawn; a running job whose owner disappeared becomes
`interrupted_unknown`, never an automatic successful replay. No external
compiler operations occur for retained checks; replayable compilation is explicit.
No provider operations are performed.

Submission hashes actual original/inventory/compiler/source/object/receipt/policy/
library files plus adapter/comparator/engine implementations. Input contents are
retained under `state_root/artifacts/<sha256>`; workers reject missing or changed
live inputs before comparing an in-memory snapshot. Backend reports are created
once at `state_root/<job_id>.report.json`; jobs record their digest. A completed
result has timestamps and `historical_result: true`: old reports are never fresh
validation. No automatic source acceptance or export is implemented.

An opened project's inventory hash also binds new submissions to its revision.
Changing or deleting that inventory refuses a new check before job creation;
restart the server to import the changed inventory. Existing idempotency keys
continue to identify historical jobs and do not create new observations.

## Measured first slice and limits

On macOS ARM64 with .NET SDK 10.0.101, the real MCP stdio test enumerated all
**27,555** DAO inventory identities and **2,258** imported published identities.
Fresh comparisons of retained VC8 x86 products found an ordinary **109-byte**
full match at RVA `0x000b63f0`. At `0x000c57a0`, the **105-byte candidate differs
from the 109-byte original**; these lengths are not a similarity score.
A separate retained EH check at RVA `0x00075040` accounted for all **179** bytes
across the supported six-node graph. These checks reran current comparators, using
original/compiler/library bytes; no new
compilation or game execution occurred. The original compiler products were
built under the existing Windows 11 ARM64 VM path. Private machine-local logs,
configuration, requests and exact results live under `local/decompilation-mcp-001`.

Enable private tests with:

```sh
DECOMPILATION_MCP_REAL_CONFIG=/absolute/private/registry.json python3 -m unittest discover -s tools/decompilation-mcp/tests -v
```

The private registry used by this test must register project `dao`, the two
ordinary retained examples above, and its actual dependencies. Mutation tests
copy artifacts into isolated temporary roots; source/object tampering, missing
objects, changed flags and compiler receipts cannot produce a full match.

The reviewed snapshot-binding correction passed nine stdio tests with private
inputs, and seven portable tests with two private-input skips. The repository
suite at that checkpoint ran 618 tests with 33 skips on macOS ARM64. Independent
review inspected the exact implementation and receipts; Windows/Linux results
are established separately by the `decompilation-mcp` CI workflow.

Deferred: arbitrary candidate submission, cancellation, source publication,
rule propagation, AST rewriting, work leasing for model workers, richer CFG/IL
indexes and cross-project reuse. The open fixture establishes protocol/index
portability only. It does not demonstrate arbitrary Windows app decompilation.

## Replayable linear frontier

The additional tools on `codex/replayable-decompilation` use original instructions
and typed SharpRetro effects rather than importing recovered bodies.

| Tool | Arguments and behavior |
| --- | --- |
| `replayable_run_next` | `project_id`, `idempotency_key`, optional `recipe_json`, `compile` (default true). Submit the lowest unresolved RVA to lift, reconstruct, emit, compile and compare; set `compile: false` to stop at a draft. |
| `replayable_regression_check` | `project_id`, opaque inventory `function_id`, `idempotency_key`, optional lowercase `expected_source_sha256`, `recipe_json`, `compile` (default true). Use the same generation/build/check worker for an explicit regression identity. A supplied source hash must match regenerated C++ before any compilation. |
| `replayable_abandon_unknown` | `project_id`, `unknown_job_id`, `idempotency_key`. Submit a durable nonaccepting abandonment of one completed missing-exit-marker dispatch. It never retries or accepts that attempt. Only the registered synchronous transport with absent launch input/workspace and quiescent host is supported. |
| `replayable_inspect` | `job_id`, optional `source_limit`. Read retained stage output and generated C++. |
| `replayable_status` | `project_id`. Inspect the current frontier and matches with current input/artifact bindings. |
| `job_get` | Read the submitted job's durable outcome without rerunning it. |

The current recipe accepts only this versioned sequence; other steps or ordering
are rejected. This is a foundation for trials, not an arbitrary rewrite language.

```json
{
  "schema_version": 1,
  "architecture": "x86-bits32-linear-tail-v2",
  "frontend": "sharpretro-typed-v1",
  "compiler_profile": "vc8-x86-thiscall-stores-tail-v2",
  "steps": ["raise-linear-effects-tail-v2", "emit-thiscall-stores-tail-v2"]
}
```

Register `original`, compiler identity/flags and a project-level `replayable`
object with absolute `lifter_config`, `vm_build_lock` and `output_root` paths.
The lock must be the existing shared VM lock across all clients/worktrees.
The lifter configuration provides `sharp_retro_checkout`, `adapter_dll`,
`build_manifest` and optionally `dotnet`. Its manifest binds the revision, tracked
source, assemblies and runtime files. Corrected dependencies require a new
attestation; an old clean-source pin cannot authorize a patched assembly.

The supported domain is a single contiguous Bits32 straight-line body with
explicit register/constant arithmetic, supported stack effects, direct external
member calls, constant receiver stores, a receiver return, and a terminal direct
external tail jump with restored stack and profile-preserved registers. The tail
effect retains its target, ordered ABI inputs and unknown callee result. The
direct-only boundary checks the original typed branch operand before symbolic
constant propagation; a known register-indirect jump remains unsupported. The x86 layer
records effects; an explicit compiler ABI profile selects argument, volatile,
preserved and return registers. Stack addressing retains symbolic SS and wrapped
SP. Unknown effects, arbitrary loads, indirect calls, general control flow and EH
remain unsupported. Stack-passed arguments and unknown callee cleanup, including
the next sequential `0x1040` example, are not inferred away. External calls remain
real unresolved declarations.

Targeted regression attempts have separate durable rows and match counts. They
use a reserved input-key namespace in the existing queue table, so older clients
also observe active/unknown regression jobs. They never satisfy the ascending
recovery selector, including when an ahead identity
fully matches. `replayable_status` reports `regression_full_matches`,
`ahead_regression_full_matches`, a bounded row view and its total separately from
`new_pipeline_full_matches`. A new token explicitly requests a new observation;
the old request and result remain retained. Changing the identity, mode, expected
source hash, compiler or runtime refuses reuse of the same token. Both modes
share the project-wide running/unknown barrier across every input key.

An unsupported body or mismatch retains the same frontier. Active or ambiguous
external execution requires reconciliation before retry. Idempotent reads never
replay a compiler operation. `compile: false` produces only a draft. Current
full matches require the full original range and the existing independent object
comparator. Generated objects also pass through the unchanged retained adapter,
including its native-EH/FS:[0] gate; this additional check cannot upgrade a failed
ordinary comparison. Source/object/either-report changes invalidate cached credit. Historical
published functions are not imported as successes in this new queue.

Run the standalone MCP tests after a Release build; they include the shared
generic IR/frontier tests. Private real-binary results and current ownership live
in `local/replayable-bootstrap-001/` and `local/replayable-tailcall-001/`.
The tail-call development pilot obtained complete 22/22-byte control and 11/11-byte
tail matches. Its whole-inventory scan generated 208 hypotheses, of which 207
additional examples had no comparison evidence at scan time. Later affected
regression results require their own compiler and comparison receipts; a scan
grants no matching credit. See the
[replayable methodology](replayable-decompilation.md) for the measured bootstrap
and the distinction between implementation, reviewed installation and publication.


The reviewed targeted regression pilot stopped safely after 39 complete matches,
one external-outcome-unknown dispatch and 168 unrun candidates out of 208 affected
hypotheses. Its missing compiler exit marker was not interpreted as a compile
failure or a success. The project barrier remains active across modes/keys;
recovery's unresolved identity remains `0x1040`. Including the ordered control
outside the tail rule gives 40 unique current native object matches, zero new
source exports. These are measured pinned-artifact results, not a complete corpus
check or game-execution claim.


For this narrow recovery path, register optional `replayable.transport_config`
with an absolute operator-owned JSON profile path. Protocol
`prlctl-sync-copy-v1` binds `vm_name`, absolute host `executable`, `vcvars`,
`guest_root`, `guest_transfer_root`, physical `host_transfer_root`, plus
`build_helper`/`build_helper_sha256` and `vm_helper`/`vm_helper_sha256`. This attests
the existing synchronous copy-before-compile wrapper with stop-on-error behavior,
and assumes managed compiler callers share the registered VM lock. The profile,
transport executable, Python executable, current reconciliation implementation,
original pipeline inputs and exact retained request/source/launch artifacts are
bound to each new observation.

Only a completed `compiler_exit_marker_missing_no_automatic_retry` attempt is
eligible. The original job/result remain unknown and unchanged. A successful
observation has `status: "abandoned_nonaccepting"`, `match: false` and
`automatic_retry: false`; it cannot increase either match count. A new explicit
request is required to try compilation again. Every unsupported observation
returns inconclusive and retains the project-wide barrier. Reusing an idempotency
key reads its historical observation, never replays the probe or compiler.

The opt-in stack-argument recipe composes the earlier domains with one bounded
addressable-parameter rule:

```json
{"schema_version":1,"architecture":"x86-bits32-linear-tail-stack-v1","frontend":"sharpretro-typed-v1","compiler_profile":"vc8-x86-flat32-addressable-stack-v1","steps":["raise-linear-effects-tail-v2","derive-original-normal-return-stack-v1","emit-vc8-composed-stack-v1"]}
```

Pass this as `recipe_json` to `replayable_run_next`,
`replayable_regression_check` or `replayable_status`. The previous default remains
available. A new exact pipeline key starts at the first inventory identity and
must obtain its own ordered checks; old evidence is never silently transferred.
The new recipe tries the previous profile first, retaining its generated source.
For the additional rule, it automatically decodes original direct call targets,
looks up their exact inventory entries, lifts the complete original ranges and
retains slice hashes plus typed normal-return evidence. No caller cleanup map or
per-function contract is accepted by a durable job.

The added profile currently supports one incoming four-byte slot whose address
is forwarded as one four-byte outgoing argument, with separate caller and callee
cleanup. Callee CFG/RET evidence is a normal-return ABI hypothesis; nested effects
and termination remain unknown. Missing/ambiguous ranges, conflicting exits,
indirect caller calls and unsupported source shapes refuse. Dependency evidence
joins source/object/report integrity checks. `scan_stackargs.py` assesses every
inventory identity against this added rule's preconditions and actual typed
frontend; its generated hypotheses are not comparisons or acceptance.

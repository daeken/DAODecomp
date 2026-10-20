# Decompilation MCP: implemented first slice

The C# engine in `tools/decompilation-mcp` provides inventory/source browsing,
deterministic related-function search, and **fresh checking of retained compiler
artifacts** through the existing Python comparators. It makes no model calls and
does not compile, change production queues, publish sources or grant historical
registry credit. A full object/graph match describes pinned compiled artifacts;
it is not a whole-game or universal C++ semantics proof.

The [architecture and full-workflow roadmap](decompilation-mcp.md#two-parts-of-the-manipulation-pipeline)
separates reusable x86/source transformations from compiler-specific profiles.
Initial decompilation, new compilation, pattern propagation and source refactoring
are intended to be available through MCP; they remain future capabilities, not
tools added by this documentation update.

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
compiler/provider operations are performed by this release.

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

Deferred: new candidate submission/compilation, cancellation, source publication,
rule propagation, AST rewriting, work leasing for model workers, richer CFG/IL
indexes and cross-project reuse. The open fixture establishes protocol/index
portability only. It does not demonstrate arbitrary Windows app decompilation.

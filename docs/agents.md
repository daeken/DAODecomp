# Agent-assisted recovery

The expensive asset is a trustworthy function contract and executable oracle.
Once those exist, implementation becomes a bounded search with a mechanical check.
Keep the coordinator's model context small by retrieving relevant evidence, not
repeatedly passing the entire decompilation or game executable to every worker.

The first measured [scalar pilot](../analysis/pilots/luna-001.md) now exercises this
workflow. Luna produces source from frozen disassembly/ABI packets; a coordinator
checks it against the original instructions and supplies concrete counterexamples
for one retry. The pilot retains failures and escalates an unresolved function to
Sol. Treat those results as evidence for a small scalar implementation task, not as
a whole-game acceptance rate.

## Proposed division of work

| Role | Initial model | Work |
| --- | --- | --- |
| Catalog/packet preparation | GPT-6 Luna | Labels, evidence indexing, dependency extraction; no invented signatures |
| Simple implementation | GPT-6 Luna | Integer leaves with settled ABI/types and a functioning oracle |
| Recovery/escalation | GPT-6.1 Sol | Ambiguous control flow, data layout, side effects, failed cheap attempts |
| Review/integration | GPT-6.1 Sol plus deterministic checks | Audit contracts/assumptions, run withheld cases, check caller compatibility |

This is a hypothesis to benchmark, not a claim of decompilation accuracy. Begin with
roughly 30 characterized functions across simple/medium/stateful buckets. Compare
first-pass acceptance, escaped failures, total tokens, wall time and spend per
**independently accepted function**. Do not optimize for lines emitted or raw pass
count. Keep complex fixtures on Sol until the pilot supports cheaper routing.

The official model pages currently list standard text prices per million tokens:
Sol $2 input / $10 output; Luna $0.10 input / $0.50 output (checked 2026-10-17).
Those baseline rates differ by 20x; actual cost includes retries, reasoning output,
caching and service tier. They are API prices, not an estimate of this app's quota
or a promised project total. Availability and limits depend on the account.

## Packet -> patch -> independent check

1. Coordinator selects a leaf or small strongly connected group with known contracts
   at its boundaries. Shared types must be settled first. Mark dependency gaps as
   blockers rather than dispatching workers to guess.
2. Freeze binary identity/RVA, bytes, disassembly, pseudocode, relevant callers,
   callees, structures, global accesses, known strings, ABI, valid input domain,
   oracle configuration, corpus and relevant headers. Supply hashes and allowed files.
3. Assign one worker an isolated checkout and a narrow write set. Give it the
   packet and reviewed headers, not a full parent conversation. Batch tiny related
   leaves only when they share stable types; do not parallelize dependent edits.
4. Worker proposes readable C++ with explicit machine arithmetic, builds it, runs
   differential checks, and returns the patch, measured results and unresolved
   assumptions. It may request new evidence or propose contract corrections.
5. A separate validation/review step reruns against a frozen oracle and withheld
   valid cases, checks no protected files changed, and inspects dependencies and
   undefined behavior. The implementation author does not control expected outputs.
6. Coordinator integrates the patch, reruns callers and scenario regressions, then
   updates the inventory. Store accepted evidence keyed to the exact build/corpus.

Start with at most two cheap attempts, then one Sol escalation; unresolved issues
become a concrete evidence request. Set per-packet token/time limits and a batch
spend limit before unattended runs. Retries must use counterexamples and new
information, not repeat the same prompt. Rate-limit worker dispatch and oracle
execution separately. One writer owns shared types and registry changes.

## How to run workers

The current Codex session exposes subagents and model selection, including the
requested `gpt-6.1-sol` and cheaper `gpt-6-luna`. For future explicit delegation,
use a fresh worker context with the packet and declared file ownership. Four total
agent slots are exposed in this session, leaving up to three workers alongside the
coordinator. That is a session limit, not an infrastructure promise.

For independent local CLI workers, the installed CLI supports model choice,
structured output, JSON events and a chosen working directory. After a baseline
commit and a dedicated worktree exist, an example invocation is:

```sh
codex exec --model gpt-6.1-sol --sandbox workspace-write \
  --cd /absolute/path/to/function-worktree --json \
  --output-last-message /absolute/path/to/local/function-result.txt \
  - < /absolute/path/to/local/function-prompt.txt
```

Choose `gpt-6-luna` for the measured cheap lane. Retain normal permissions and
capture usage/events; do not bypass approval or sandbox policies for throughput.
The command shape was checked against local `codex-cli 0.163.0-alpha.10.2` help;
no worker or paid API run was launched during setup. There is no unattended
dispatcher, queue locking, hard budget enforcement or auto-merge implementation yet.

`tools/run_model_packet.py PACKET OUTPUT_DIR --model gpt-6-luna` is the explicit
single-packet launcher used by the later pilot. It runs a read-only, ephemeral CLI
worker through existing login, captures structured source and usage events, and
enforces a 180-second default timeout. It neither applies the source nor retries.
The output directory must be new. On POSIX the timeout kills the process group;
Windows currently kills only the direct CLI process. This is a bounded interactive
pilot utility, not a production scheduler or a hard token/spend limiter.

The Responses API also offers native multi-agent support in beta for GPT-6.1 Sol.
Its documented subagents share the request's model. Mixed cheap/expensive routing
therefore needs independent requests/CLI workers or a host that explicitly exposes
per-agent model selection; do not assume the API's native subagent tree supports it.
Prefer a fixed external queue for predictable work ownership and budgets.

## Worker prompt outline

```text
Recover the function identified in the attached packet.
Read AGENTS.md and the packet's evidence before editing.
Use only the packet's allowed write paths.
Preserve the pinned contract, original runner, comparator and frozen corpus.
If the ABI, type or dependency is unclear, report the exact missing evidence.
Implement defined C++ behavior; do not chase binary similarity.
Run the supplied checks. Report the candidate patch, report paths, counterexamples,
and remaining uncertainties. A test pass is corpus evidence, not a proof.
Stop after the assigned attempt/token/time budget; do not change acceptance rules.
```

## Sources

- [GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol)
- [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna)
- [Responses multi-agent model and coordination behavior](https://developers.openai.com/api/docs/guides/responses-multi-agent)


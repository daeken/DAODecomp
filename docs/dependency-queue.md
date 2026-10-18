# Dependency-directed recovery queue

The user wants breadth for parallel workers and depth within each handoff, starting
at executable startup. Working behavior comes first; use stable RVA-based names
and defer speculative naming, annotation and readability work.

This document specifies the next queue change. The current packet pipeline and
acceptance gates remain in force; the graph scheduler is not yet implemented.

## Director and execution roles

The user explicitly wants the primary assistant to act as a high-level director,
not a per-packet dispatcher. A persistent program should own queue claims,
bounded worker requests, handoffs, retries, gate execution, evidence collection
and tested integration/checkpoint/CI operations. Use the existing provider and
pair pipeline rather than requiring a language-model coordinator at every step.

The director sets Windows milestones, allocation priorities and budgets, reads
compact throughput/health summaries, and resolves genuine evidence or architecture
exceptions. Routine successes do not wake it. Workers return machine-readable
artifacts and frontier continuations so their context does not need to be relayed
through the director. A separate independent reviewer still follows deterministic
gates; the dispatcher must not convert missing evidence into acceptance.

Implementation of this persistent controller is now the next infrastructure
priority. Resume existing running checkpoints before changing their execution
inputs. Retain two implementation lanes and a persistent bounded request allowance
equivalent to at most twelve model requests per nonoverlapping 30-minute cycle,
including preparation/reviews; do not reset the allowance on retries or restarts.
The daily DeepSeek cap applies in addition. The controller must refuse another
live controller and must not duplicate already-running work.

## Work selection

Use the pinned PE entry point as the first graph root. Distinguish measured direct
calls/tail calls, import boundaries and unresolved indirect targets. Every node
keeps its binary SHA-256, module and RVA. An inferred edge is not a resolved
dependency. Original instruction and caller evidence accompanies each edge.

The scheduler selects independent branches across the current frontier. Each
agent receives a bounded connected slice and enough surrounding context to follow
its dependencies several levels deep. A slice may contain several functions; it
is not constrained to one function, one source file or one arbitrary batch count.
Start with the existing two implementation lanes. Increase concurrency only when
ready work and validation capacity support it.

Prefer slices that unblock a concrete Windows startup milestone. Group cycles
for joint recovery when evidence supports that; otherwise record the unresolved
edge. Central dependencies with multiple callers receive higher priority than
unrelated leaves. Keep an independent background lane for already-frozen work.

## Handoff context

Each work unit should bind:

- Root identities, owned functions, observed edges, caller expectations and the
  Windows milestone it advances.
- Relevant instruction bytes, ABI/register/stack behavior, guest memory and
  observed effects; distinguish measured facts from hypotheses.
- Exact accepted callee contracts and source/build evidence. Unknown dependencies
  stay explicit; they cannot be replaced by successful stubs.
- Frozen public validation inputs, protected input hashes and acceptance commands.
  Held-out fixtures remain withheld from the implementation model.
- A bounded depth/function/token allowance, exclusive ownership claim and the
  deterministic continuation needed after a worker stops.

Workers can return new dependencies and proposed evidence as graph expansion.
They may recover owned callees within their frozen scope; expanding scope requires
the queue to claim and prepare the new work. Shared contracts and acceptance
criteria remain coordinator-owned. A callee already claimed elsewhere becomes a
dependency, not a duplicate implementation assignment.

## Durable states and completion

Track discovery, characterization, support review, frozen readiness, implementation,
public validation, held-out validation, negative controls, independent source
review and integration separately. A source response is a proposal, not accepted
progress. Claims and request IDs must survive restarts so a heartbeat cannot pay
for or dispatch the same attempt twice.

Failures retain their exact evidence and missing dependency. Independent branches
continue. Only public semantic counterexamples may enter bounded repair prompts;
held-out failures stop the packet. Exceeding a depth/time/model budget returns the
partial frontier without marking unvisited work complete.

Report both accepted functions and actual Windows milestones. A Windows build,
a synthetic runner, original-game execution, a partial replacement reaching a
boundary, and a working replacement game are different outcomes. Keep all five
distinct. Corpus agreement remains bounded evidence, not a universal proof.

The provider and spending controls are described in
[workers/README.md](../workers/README.md); measured throughput and remaining
execution/review costs are in [throughput-scaling.md](throughput-scaling.md).

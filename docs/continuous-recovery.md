# Continuous recovery

The user has authorized ongoing decompilation, lower-cost implementation workers,
and pushing tested progress to the existing GitHub repository. Work continues in
this chat through an active 30-minute heartbeat, `continue-daodecomp-recovery`.
The host/app must be available for scheduled local work. This is an ongoing
coordinator workflow, not a claim that the whole game can already be recovered by
an unattended source generator.

Start each continuation by reading AGENTS.md, the current Git state, and
`analysis/recovery-queue.json`. Resume unfinished work before selecting new items.
Keep one coordinator responsible for shared contracts, runners, evidence and Git.
Workers run as implementation/review pairs through the
[paired recovery pipeline](paired-recovery.md); they do not modify the shared
checkout. Do not duplicate a running worker or overwrite user edits. The
coordinator handles integration, disagreements and missing evidence, while routine
build/test/counterexample handling belongs to the pipeline.

The user's latest model preference (2026-10-17) is GPT-6.1 Sol with medium
reasoning for characterization, packet preparation, implementation, repairs and
a separate independent source reviewer. This supersedes the Luna-first policy.
The pair and single-packet launcher default to `gpt-6.1-sol`; reviewer requests
also use medium reasoning. Let active frozen jobs finish with their recorded
settings. Keep coordinator overhead low, every deterministic gate and independent
review requirement. The user subsequently authorized DeepSeek with a $50/day cap.
The reviewed [packet provider](../workers/README.md) uses the shared private ledger
at `local/providers/deepseek-daily`, calendar days in America/Chicago, and explicit
reservations for failed and successful requests. Its low-thinking 22-function
benchmark passed the unchanged deterministic gates and independent Sol review;
it adds no new recovery credit. Use this provider for suitable frozen implementation
packets and pass its response through `run_recovery_pair --initial-response`.
Keep Sol medium for preparation, ambiguity and independent review. Count all
provider calls, including failed calls, in the activation's request ceiling.

The latest work-selection priority is the executable's startup path toward a
runnable replacement on Windows. Use a [dependency-directed queue](dependency-queue.md):
breadth across independent branches, depth and coherent caller/callee context
within each handoff. Keep RVA-based names initially and defer naming/readability
work. A graph scheduler is still to be implemented; the queue records its next
actions and the startup characterization proposal. Do not confuse a synthetic
runner or the original game launching with the replacement reaching a milestone.

The user now prioritizes batched execution and conservative incremental validation
before increasing packet size. The independently reviewed fresh-child transport
checks the 11-function indexed-field group's 15,632 positive cases and four negative
controls in 274.515 seconds, 10.88 times faster than the retained legacy run. The
combined incremental checkpoint passed independent acceptance review in
`analysis/reviews/throughput-integration-001.json`. The complete 47-function shared checkpoint and an unchanged all-seven-group
cache-hit rerun passed. The latter took about 100 seconds versus 43 minutes for
the initial run, including a fresh clean build and current attestation. The queue
tracks later integration and publication status. Use the reviewed commands below;
do not count an incomplete run or partial cache experiment as accepted evidence.

After adoption, aim for batches of 20–30 related functions where existing evidence
and types permit; do not invent contracts to fill a batch. Keep at most two
implementation lanes. The target is 50–100 accepted functions per hour for suitable
groups; complex functions and missing contracts can take longer. Review once per batch. The coordinator
reads compact package/status summaries, integrates and handles disagreements.
Avoid repeated full-artifact reads, routine result relays and new infrastructure
audit/repair chains. Nonblocking tooling proposals stay in the backlog. A new
backend gets one focused preparation assignment and one independent acceptance
review; record exact unresolved evidence rather than expanding the assignment.
Measure accepted functions per model request and reported tokens, including
preparation/review overhead. Coordinator usage and weekly quota attribution remain
unknown; do not estimate them from API prices or worker token totals.

For each coherent group:

1. Check function boundaries, original module/slice identities, ABI, dependencies,
   and observable state against actual instructions and callers. Inventory entries
   are hypotheses, not ready-to-implement contracts.
2. Build a strict original adapter and independent deterministic public/held-out
   corpus. Include negative controls and invalid-footprint checks when extending
   the backend. Freeze these inputs before giving a worker its packet.
3. Default to GPT-6.1 Sol at medium effort. Preserve the existing ceiling of
   three implementation attempts per packet; each repair needs a concrete public
   counterexample or separately resolved evidence gap. Run at most two implementation workers at once and
   twelve worker requests per activation, including preparation and independent
   reviewers. This is a ceiling, not a target. Use existing CLI login, not a new paid
   service. The 180-second request timeout is not a hard token or spend limit.
4. Run build and public checks automatically first; a concrete failure may go back
   to the implementation worker within its retry budget. Then run held-out cases
   and negative controls. Held-out failures stop the packet without revealing
   those cases to a repair worker. Only after all deterministic gates pass, send
   the batch to a separate Sol reviewer for ABI, memory, arithmetic,
   contract and evidence review. Rejection or missing evidence cannot be accepted.
   Do not repeat acceptance-system or contract audits for unchanged backend machinery.
   Preserve failed attempts. Record actual usage/latency;
   distinguish worker estimates from coordinator cost and account charges.
5. Refresh affected regression evidence, run required tooling/build/synthetic
   checks, and commit/push a coherent passing checkpoint. Check CI. Keep original
   assets, raw disassembly, worker logs and reports ignored; retain hashes and
   evidence summaries in the repository. Let the pre-commit hook update progress.
6. Update the queue with accepted work, exact blockers, and the next actionable
   item, then continue independent work. One blocked function is not a reason to
   stop all recovery. Notify the user for meaningful integrated progress or a
   decision/failure requiring their attention, not unchanged polling.

The memory-001 group adds two fixed-size copies with aliasing and a bit mutation
routine. Object counters extend exact memory observations to 512-byte allocations
and distinct sentinel behavior. Indexed-store validation adds exact byte/word
writes and explicit incoming-register observations. Follow the queue's
current checkpoint and blockers. Grow toward dependent functions and subsystems,
not merely maximize tiny leaf counts.

The queue also tracks reviewed infrastructure handoffs. The incremental checkpoint
recreates an empty owned build directory and attests the complete current sources
and build. A group may reuse historical comparisons only when its actual execution
images, dependencies, runtime, contracts, registry entries, corpus and invocation
are unchanged. Missing or unverifiable evidence forces new validation or failure.
Old comparison provenance remains historical. Complete current coverage and all
infrastructure gates are required for publication; partial runs never count.
Review-prompt deduplication may consolidate repeated provenance but must preserve
every binding and acceptance requirement.

After integrating an accepted package, run one checkpoint command on the current
macOS host, choosing new output and record paths each time. Keep the source working
directory and these build/cache paths stable to permit exact reuse:

```sh
env PATH="/opt/homebrew/Cellar/cmake/4.2.0/bin:$PATH" \
  .venv/bin/python tools/incremental_checkpoint.py \
  --build-dir "$PWD/build-incremental-throughput" \
  --cache-dir "$PWD/local/checkpoint-cache/throughput-003" \
  --output-dir "$PWD/reports/checkpoint-throughput-001" \
  --record "$PWD/analysis/validation/throughput-001.json" \
  --jobs 4 --batch-size 128
.venv/bin/python tools/update_progress.py
```

Run these sequentially and stop on any failure. The checkpoint builds, runs
tooling/CTest/synthetic controls, covers all eight implemented groups and their
required negative controls (69 positive and48 negative reports), verifies report/input hashes, and publishes compact
evidence. The next command refreshes README progress. A failed step stops
publication and preserves diagnostic artifacts. Neither command stages, commits
or pushes. Exact runtime reuse currently supports macOS; the complete legacy
`tools/validate_checkpoint.py` remains available without reuse on Linux/macOS.
Windows full checkpoints are currently rejected because the game validators
do not yet accept separate executable/configuration and CMake-cache directories;
cross-platform infrastructure CI remains separate from original-game validation.

The local PATH prefix above selects the actual installed CMake executable:
the strict artifact policy rejects `/opt/homebrew/bin/cmake`, which is a symlink.
After a tool upgrade, resolve the current installation and keep that invocation
stable; changed tool/runtime identities must invalidate affected reuse.

The heartbeat can be paused or stopped when the user requests it. Missing tools,
quota or reference-host capabilities should be recorded accurately; do not invent
results, silently switch services, weaken acceptance checks, or call corpus
agreement a proof.

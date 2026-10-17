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

The user's latest priority (2026-10-17) is lower coordinator and expensive-model
overhead. Use Luna for characterization, packet preparation, implementation and
repairs, plus a separate Luna reviewer for routine source batches on established
backends. Invoke the pair with `--reviewer-model gpt-6-luna`. Reserve Sol for a
concrete failed cheap attempt, ambiguous contract, or substantive acceptance-system
change. Keep all deterministic gates and independent review requirements.

Aim for batches of 8–16 related functions where existing evidence and types permit;
do not invent contracts to fill a batch. Review once per batch. The coordinator
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
3. Prefer GPT-6 Luna at medium effort for settled contracts. Allow at most two
   attempts per packet, with a concrete counterexample for the repair; then allow
   one GPT-6.1 Sol escalation. Run at most two implementation workers at once and
   twelve worker requests per activation, including preparation and independent
   reviewers. This is a ceiling, not a target. Use existing CLI login, not a new paid
   service. The 180-second request timeout is not a hard token or spend limit.
4. Run build and public checks automatically first; a concrete failure may go back
   to the implementation worker within its retry budget. Then run held-out cases
   and negative controls. Held-out failures stop the packet without revealing
   those cases to a repair worker. Only after all deterministic gates pass, send
   the batch to a separate Luna reviewer for ABI, memory, arithmetic,
   contract and evidence review. Rejection or missing evidence cannot be accepted.
   Use Sol for substantive new acceptance-system or contract ambiguity reviews;
   do not repeat those audits for unchanged backend machinery.
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

The queue also tracks reviewed infrastructure handoffs. Evidence reuse currently
has approval only for a non-counting shadow audit; existing evidence rules and
full checkpoint checks remain in force. Review-prompt deduplication may consolidate
repeated provenance but must preserve every binding and acceptance requirement.

After integrating an accepted package, run one checkpoint command on the current
Linux/macOS host, choosing new output and record paths each time:

```sh
.venv/bin/python tools/validate_checkpoint.py \
  --output-dir reports/checkpoint-memory-001 \
  --record analysis/validation/memory-001.json --jobs 4
```

It builds, runs tooling/CTest/synthetic controls, checks all registered scalar,
memory, object-counter, indexed-store and linked-structure functions and their negative controls,
verifies report/input hashes, then
publishes compact evidence and refreshes README progress. A failed step stops
publication and leaves logs plus `checkpoint.json`. It does not stage, commit or
push. Windows full checkpoints are currently rejected because the game validators
do not yet accept separate executable/configuration and CMake-cache directories;
cross-platform infrastructure CI remains separate from original-game validation.

The heartbeat can be paused or stopped when the user requests it. Missing tools,
quota or reference-host capabilities should be recorded accurately; do not invent
results, silently switch services, weaken acceptance checks, or call corpus
agreement a proof.

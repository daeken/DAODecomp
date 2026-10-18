# Persistent recovery dispatcher

`recovery_dispatcher.py` owns routine claims, bounded model handoffs, the existing
deterministic pair pipeline, separate reviews, exact reviewed promotion, the full
incremental checkpoint, commit/push and exact-head CI. Worker responses are data;
there is no worker-provided command loop. The initial queue starts at the pinned
Windows PE startup and retains the independently frozen24-function background job.

This controller is not itself a game loader or a new validation backend. Its
startup preparation produces concrete private support files and a structured
continuation. Scope/size/JSON/Python-syntax gates run before a separate Sol medium
support review. These gates do not execute or certify the proposed Windows
capture code. The first newly proposed loader/capture adapter has a real adoption
boundary: unsupported execution remains an explicit exception/continuation for
the director. The dispatcher never executes generated Python/PowerShell merely
because a worker supplied it or a support reviewer approved its text.

## Initialization and review

The preparer reads the original startup handoff and exact approved background
support; it creates an ignored configuration, bounded per-unit context and review
request. It performs no model requests, reads no credential and does not initialize
or reset the already-existing shared DeepSeek ledger.

```sh
.venv/bin/python workers/prepare_dispatcher.py \
  --state-dir "$PWD/local/recovery-dispatcher-startup-001"
```

Use a new destination for a proposal, never to reset a running allowance. The
independent reviewer must inspect the exact dispatcher/preparer/test bytes, config,
promotion override and deterministic results. An approval artifact at
`STATE/approval.json` must contain `decision: approve`, the raw `config_sha256`,
and the exact `trusted_code` map from the config. The preparer creates no approval.
Do not run before independent approval. A changed config/code hash refuses launch.
Config changes after initialization require a separately reviewed migration;
pointing the existing database at new bytes is refused.

The configuration reserves two opening requests for setup and independent review.
The explicit `request-adjustments/windows-ci-fixture.json` adds the authorized
Windows CI fixture repair request, exactly once. Additional director-authorized
requests must be recorded as new immutable adjustment JSON (`id`, positive `count`,
`evidence`) before the next controller start; they are debits, never refunds.

## Run and observe

```sh
.venv/bin/python workers/recovery_dispatcher.py run \
  --state-dir "$PWD/local/recovery-dispatcher-startup-001"
.venv/bin/python workers/recovery_dispatcher.py status \
  --state-dir "$PWD/local/recovery-dispatcher-startup-001"
```

`run` remains alive between cycles; keep its process/host available. `once` starts
available bounded jobs and waits for those jobs to finish. It is an actual paid
execution mode, not a dry run. `status` only reads the saved compact status and
never initializes state or calls a model. The director should read task exceptions
and completed Windows milestones, not relay ordinary packets. The existing chat
heartbeat remains responsible for director-level exceptions, rather than routine
dispatch.

## Durable limits and recovery

- Two live jobs at most. The repository-wide POSIX flock prevents another
  controller, including one configured with a different state directory. Child
  jobs inherit the lock; surviving shared-checkpoint subprocesses retain it too.
- SQLite FULL transactions persist ownership, claims, stages and request IDs
  before external effects. Function identities can have only one task owner.
- At most12 reserved requests per anchored nonoverlapping1800-second cycle,
  including preparation, source/support/integration reviews, unused review slots
  and failures. A deferred review also debits its actual dispatch cycle when
  validation crosses the boundary. Wall-clock regression refuses scheduling.
- Every DeepSeek call goes through the reviewed existing provider and its one
  shared `$50/day`, America/Chicago ledger. There is no initialization/refund/retry
  action in this controller. A packet uses one frozen DeepSeek proposal, one
  independent source review, and one integration review slot. The pair is limited
  to one implementation attempt; public failure becomes an exact exception rather
  than an automatically invented repair. Held-out/negative failures never reach
  an implementation retry.
- Startup support proposals are bounded data. Only direct e8/e9 edges checked
  against original file bytes and characterized caller ranges enter the graph.
  New targets receive discovery/characterization tasks, not recovered status or
  guessed contracts. Indirects and unknown function boundaries remain unresolved.
- The existing pair orders build, public cases, held-out cases, negative controls,
  then independent source review. Its frozen support protections remain intact.
  A preserved accepted22 source prefix is checked before the append24 pair.
- Exact promotion uses config-owned destinations and base/proposed hashes,
  independently approved support, the exact accepted candidate and a separate
  integration review. A single explicit Windows fixture normalization composition
  is bound for independent controller/config review. Unowned shared edits refuse
  promotion. There is no reset/stash/force-push or automatic overwrite.
- Complete old attestations move byte-for-byte to `analysis/validation-history/`
  before a new inventory's checkpoint. A full new checkpoint, progress refresh,
  coherent commit/push and successful exact-head CI are required for completion.
  A failed step leaves a journal and an exception, not accepted publication.
- The one already-running CI refresh is a specifically named deferred checkpoint,
  rather than an unknown hash or generic completion marker. Isolated work can run
  while promotion waits up to7200seconds. Before integration review, the controller
  verifies the exact old69+48 inventory, current prepromotion sources, measured
  pass/control outcomes, self-binding and exact existing publisher projection from
  the passed producer. It retains raw bytes and SHA in the review input. Integration
  approval binds that SHA; promotion checks it again before any shared write and
  archives the exact bytes. Missing or different evidence cannot authorize adoption.
- After a crash, a surviving job excludes a second controller. Once the exclusive
  lock is available, a complete receipt is consumed; a missing receipt marks the
  job ambiguous and blocks automatic replay. Partial integration/push and uncertain
  external requests require investigation. Other independent queued tasks remain.

The initial shared69-function checkpoint is a separate measured publication; it
must finish before shared adoption. Passing orchestration tests does not establish
game behavior, original startup execution or native Windows evidence.

## Offline checks

```sh
python3 -m unittest discover -s workers/tests -v
python3 -m unittest discover -s tests -v
```

The dispatcher tests use temporary databases, synthetic PE bytes, real concurrent
local processes and the existing synthetic pair fixture. They check exclusivity,
restart ambiguity, ownership, request accounting/carry-over, graph byte checks,
scope/syntax rejection and real pair gate ordering. They read no API credential
and issue no model requests. Live startup capture and new game functions require
their own measured evidence.

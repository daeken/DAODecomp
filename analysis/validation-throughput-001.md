# Validation throughput measurement

The production fresh-child transport subsequently passed independent review
([review](reviews/batched-validation-002.json)). Its complete indexed-field public,
held-out and negative checks took **274.515 seconds**, a **10.88×** reduction
against the retained 2,986.603-second legacy measurement. It preserved all 15,632
positive cases, two repetitions per side, four negative controls and exact
observations. This measurement retains per-case process isolation; the faster
prototype below does not establish production performance.

The first 15-function object-bitfield implementation/review pair then passed all
gates without a repair request in **464.679 seconds**. The two Sol 6.1 medium
requests reported 294,709 input, 6,091 output and 991 reasoning tokens, with zero
cached input tokens. This is about 116 functions/hour for the pair stage alone;
characterization, support preparation, integration and final checkpoints are
excluded. Sustained end-to-end recovery at 50–100 functions/hour is still a target.
The independent review accounted for 251,101 input tokens; compact presentation
of repeated passing evidence is a deferred optimization, with all bindings and
acceptance requirements retained.

An isolated incremental-validation proposal also demonstrated a real cache hit
after another group's C++ source and contract changed: a fresh clean build and
current full-source attestation were still required, while the unchanged memory
comparison evidence retained its historical provenance. The 642-case memory seed
took 204 seconds and the reuse checkpoint 107 seconds, including infrastructure
checks. The combined production integration passed independent acceptance review; full
shared checkpoint publication is still pending.

The shared checkpoint exposed two fail-closed integration gaps. First, the
runtime provider rejected valid Python installation symlinks; its reviewed repair
hashes resolved files while retaining lookup-to-target bindings and the stricter
candidate artifact policy. Second, the linked-structure reports declared one
validation test file absent from the reuse identity. A separately reviewed repair
adds that exact group-scoped dependency and requires its current hash to match.
An independent audit checked 88 actual reports and 3,729 artifact declarations;
no unknown declarations remain. Unknown dependencies still fail closed.

Both repairs are integrated. The complete shared checkpoint passed all 47
functions (33,678 positive inputs), all 26 negative controls, the clean build,
196 tooling tests (one skip), six CTest checks and both synthetic demos on macOS
ARM64. Its output interval was 2,589.378 seconds. An unchanged complete rerun
rebuilt from an empty owned directory, attested current inputs and artifacts, and
reused all seven groups in 100.071 seconds: **25.88× faster**. These intervals run
from the configure log modification time to final attestation and exclude initial
process startup. The reports remain historical comparisons, with fresh current
attestations in `analysis/validation/throughput-001.json` and
`analysis/validation/throughput-reuse-001.json`. Changed or missing execution
inputs still require reruns. Earlier failed runs seeded no cache entries.

Meanwhile, a separate 22-function direct object-field packet passed its first
implementation attempt, all public/held-out/negative gates, and independent source
review in **542.294 seconds**, using two Sol medium requests. This is about 146
functions/hour at the pair stage only; its shared integration and checkpoint are
still pending. Preparation, acceptance review and checkpoint overhead remain
outside that figure. See `analysis/pilots/direct-object-fields-001.json`.

The current heartbeat's durable queue records worker assignments and reported
CLI usage. Collaboration tools do not report token usage; coordinator/account
quota attribution remains unknown. These results are local emulator corpus
evidence, not native Windows validation or universal equivalence proofs.

## Original diagnostic experiment

The indexed-field pair spent 2,987 seconds in public, held-out and negative
validation (rounded), compared with 128 seconds across its four recorded model
requests. Process startup and repeated adapter/module loading dominate this
sample. The 15,632 positive cases require 93,792 child launches in the legacy
path: two repetitions, two Python adapters and two nested native runners per case.

A disposable prototype on macOS 27.0.1 ARM64 (Apple M4, Python 3.14.7,
Unicorn 2.1.4, Apple clang 21) checked the unchanged accepted C++ bodies against
the same pinned original slices and frozen cases. Both full repetitions matched
all 62,528 retained side-observation hashes. Four negative corpora reproduced
the same 3,240 mismatches per repetition. A shuffled run and additional arena
sentinels also agreed.

| Measurement | Seconds |
| --- | ---: |
| Retained legacy public, held-out and negative validation | 2,986.603 |
| Entire prototype experiment, including extra probes and a live legacy baseline | 41.592 |
| Live legacy subset: 32 cases, two repetitions per side | 10.324 |
| Same subset using process reuse | 0.275 |
| Same subset with preloading and fresh children | 1.478 |

The full legacy and prototype runs occurred at different times. The simultaneous
32-case comparison is narrower but better controlled. Prototype subtotal timers
exclude some controller work; the entire-experiment time above includes it.

These are validation measurements, not an achieved function recovery rate.
The prototype reused native processes and therefore needs a reviewed isolation
model before adoption. Fresh automatic arenas, new Unicorn machines and shuffled
cases do not by themselves establish isolation of runtime globals or external
state. Production work will retain fresh per-case children, per-case deadlines,
strict framing, complete observations, two repetitions and all negative controls.
The existing comparator and checkpoint remain authoritative until that change
passes deterministic tests and independent review.

The user authorized batching and conservative incremental validation before
larger function packets. Incremental reuse must attest unchanged execution inputs
and freshly rebuilt artifacts, preserve historical comparison provenance, and
rerun whenever an input or required artifact cannot be verified. Frozen public
and held-out coverage, negative controls and independent source review remain
required. The subsequent target is 20–30 related functions per packet where the
evidence supports that size, with no guessed contracts to meet a quota.

Detailed private results and reproduction commands remain in
`local/benchmarks/validation-throughput-001/result.json` and `result.md`.
The durable queue tracks production proposals and their independent reviews.
This experiment adds no recovered functions and establishes no universal proof.

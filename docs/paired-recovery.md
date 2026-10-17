# Bounded implementation and review pairs

`tools/run_recovery_pair.py` runs implementation proposals through deterministic
gates before requesting an independent source review. It produces an ignored
package for coordinator integration. It does not change recovered source,
contracts, shared headers, the oracle, comparator, corpus, registry, evidence
records, queue or Git. Corpus agreement and reviewer approval remain scoped
evidence, not a proof of the game or native Windows validation.

The implementation schedule is at most two `gpt-6-luna` attempts followed by one
`gpt-6.1-sol` attempt, at medium effort. An existing first response can occupy the
first slot without a new request. Public failures supply the next attempt with
the previous source and a concrete public counterexample. Every already-passing
function is explicitly preserved in the repair prompt. Held-out and negative-control
failures stop the invocation with `needs-evidence`; they are never supplied to
an implementation retry. Missing CMake sources, compiler/configuration errors,
missing build executables and build timeouts stop with `infrastructure-error`.
An implementation model cannot repair protected infrastructure.
Public-stage missing reports, launch failures, timeouts, runner errors and
nondeterminism stop with `needs-evidence`; only stable semantic mismatches justify
a public repair retry. Candidate compilation failures include diagnostics from
the actual failed build command in the repair request.

Before any model request, a declared first CMake configure command is preflighted
with an empty candidate file in a separate disposable snapshot. This checks
protected source dependencies and compiler configuration without guessing source
semantics. Non-CMake manifests use the per-attempt infrastructure checks.

Each attempt runs, in order:

1. Build the proposal in a disposable isolated tree containing only declared
   frozen source/support files and the proposed candidate source.
2. Run public differential validation for every declared function.
3. Run held-out differential validation for every declared function.
4. Run the declared negative controls; a normal pass does not satisfy them.
5. Request one independent review only after every deterministic gate passes.

The reviewer defaults to `gpt-6.1-sol` (optionally `gpt-6-luna`). Its separate
prompt and JSON schema require `approve`, `reject` or `needs-evidence`, specific
issues and limitations. It receives the frozen manifest, instruction/ABI/contract
evidence, tested source and executable hashes, host/compiler/build information,
candidate source and compact deterministic summaries. The prompt labels raw file
hashes and canonical JSON digests separately; they intentionally hash different
byte sequences. Issue function names are constrained to declared names or `*`.
It audits memory,
aliasing, overflow, shifts, return bits, coverage and excluded state. Passing tests
alone is explicitly insufficient. A blocking or missing-evidence issue cannot
accompany approval. No approval or no valid review means no accepted package.

## Manifest

The coordinator prepares and reviews a JSON manifest **before** implementation.
It has exactly these fields:

| Field | Meaning |
| --- | --- |
| `schema_version` | `1` |
| `group` | Packet/group identifier such as `memory-001` |
| `packet` | Relative UTF-8 packet path in `snapshot` |
| `candidate` | The single proposed `src/*.cpp` target, excluded from `snapshot` |
| `snapshot` | Explicit relative support-file paths mapped to SHA-256 values |
| `reference` | Absolute original binary `path` and pinned `sha256`; read in place |
| `functions` | Objects with `name`, stable `id`, frozen `contract` path, and `corpora` paths keyed by `public` and `heldout` |
| `commands` | Nonempty `build`, `public`, `heldout`, `negative` command lists |
| `review_evidence` | Frozen UTF-8 evidence paths to include in the reviewer prompt |

Commands have exactly `argv` (a nonempty string array), `timeout_seconds`
(1–3600), and `reports` (an array). They execute without a shell. The supported
argv placeholders are `{python}`, `{tree}`, `{build}`, `{report_dir}` and
`{binary}`. Literal braces in arguments must use Python format escaping.
Do not substitute a shared checkout or build directory for the isolated tree.

Each report declaration has exactly `path` (relative to `{report_dir}`),
`function` (declared name), `corpus` (`public` or `heldout`) and `expect`
(`pass` or `mismatch`). Report filenames must be unique across all stages.
Build commands generally have no reports. Public and held-out declarations must
cover every function; negative controls use public inputs and expect a mismatch.

For memory-001 the support list includes `CMakeLists.txt`, all referenced
noncandidate C++ files (including `validation/native_runner.cpp`, the synthetic
candidate and `tests/guest_memory.cpp`), shared headers, memory adapters/case
generator, the comparator and its imports, registry/reference metadata, the
implementation launcher, reviewed contracts, frozen JSON public/held-out cases,
the packet and original-instruction review evidence. A CMake target outside the
requested memory runner still needs its source present during configuration.
Declare dependencies explicitly; the tool does not discover arbitrary imports.

The standard memory validation argv is:

```json
["{python}", "{tree}/validation/validate_memory.py", "--binary", "{binary}",
 "--build-dir", "{build}", "--report-dir", "{report_dir}",
 "--suite", "public", "--jobs", "4"]
```

Use `heldout` for the held-out stage, and public plus `--expect-mismatch` for the
negative stage. Build with CMake configure and build argv arrays, using `{tree}`
and `{build}`. Keep the binary under ignored `gamedata/` or `local/`; it is never
copied into the snapshot/package. Executable/DLL/dump/project file extensions are
rejected in support snapshots. This is a trusted coordinator manifest, not a
security sandbox or a generic untrusted-code execution service.

## Run and inspect

For the locally frozen memory-001 packet, the exercised command is:

```sh
.venv/bin/python tools/run_recovery_pair.py \
  local/pairs/memory-001-manifest.json local/pairs/memory-001-run-2 \
  --python /Users/daeken/projects/DAODecomp/.venv/bin/python \
  --initial-response local/pilots/memory-001/luna-attempt-1/response.json
```

Choose a fresh output directory for another invocation. Output must be below
ignored `local/pairs/`. `--attempts 1` limits implementation to one slot;
`--reviewer-model gpt-6-luna` changes only the independent reviewer. The runtime
Python path preserves its virtual environment. Model requests reuse existing
Codex CLI authentication; no additional service or API key is configured.

`status.json` is atomically refreshed after gates and records final state,
attempts, identities, host, elapsed time, request metrics and acceptance. A failed
model request is retained in its metrics/logs and included in the final request
count. Reused-request metrics are labeled separately from newly spent requests.
The reused proposal's actual model is retained separately from its attempt-slot
model; a reused Sol result is not mislabeled as a new Luna response.
Recorded tokens are CLI-reported worker usage, not coordinator usage or measured
account charges. Each model request is capped at 180 seconds; the implementation
launcher has a 195-second outer guard. Time limits are not token/spend limits.
POSIX command timeouts kill their process group; Windows descendant lifetime
control remains limited by the existing launcher.

Outputs include the frozen manifest/support snapshot; each source response and
candidate; exact argv, stdout/stderr, exit status and timing per command; reports;
build metadata; raw model events, schema and response; and the independent review.
Disposable build trees are removed. Reports retain their original temporary
execution paths; the frozen support and source plus commands permit a fresh
reproduction. The final `accepted/` directory contains candidate source and
package metadata only when every gate and independent review approves. Integration
still needs the coordinator's normal evidence recording and checkpoint checks.

The tool checks snapshot, candidate and original binary hashes before/after every
command and again before accepting review. It rejects incomplete reports, wrong
identities, wrong contract/corpus digests, changed inputs, missing/duplicate cases,
fewer than two repetitions, runner errors and nondeterminism. Negative controls
must contain at least one stable mismatch and no error status. Public and held-out
case IDs must be disjoint. It does not infer that a declared contract includes
every observable effect; that remains an independent evidence-review obligation.

Both model prompts forbid tools/reads/edits/other agents. CLI requests are
read-only, and tool-use events invalidate the result. The reviewer starts in an
empty directory with user configuration disabled and a separate review schema.
The implementation uses the existing `tools/run_model_packet.py` launcher. These
controls are scope enforcement with event auditing, not a claim that every CLI
capability is physically removed.

Reviewer and public-repair prompts now share repeated provenance through explicit
hash-bound tables. Structural report positions reference those tables; complete
counterexamples and arbitrary input/observation fields remain untouched. The
original reports, frozen evidence, hash domains and acceptance gates are unchanged.
The [independent review](../analysis/reviews/paired-prompt-deduplication-001.json)
checks exact reconstruction and metadata-name collision cases. The first proposal
failed review; its corrected replacement passed all 110 repository tests after
integration. On captured counter prompts, payload size fell 8.51% for review and
2.69% for public repair. These are byte measurements, not measured token, cost or
model-quality improvements. Historical runs retain their original orchestrator
hashes and prompts; this formatting applies only to subsequent requests.

## Pipeline tests and observed overhead

```sh
python3 -m unittest discover -s tests -v
```

`tests/test_recovery_pair.py` uses synthetic adapter reports to test ordering,
bounded model selection, public repair feedback, held-out failure suppression,
negative-control failure, frozen-oracle mutation rejection, empty/wrong reports,
timeouts, strict response shapes and review refusal. They test the pipeline's
failure handling; the actual game evidence comes only from its real validators.

The first live invocation, `local/pairs/memory-001-run-1`, omitted the protected
leaf runner source from its declared CMake snapshot. Three builds failed before
public validation, consuming two new implementation requests and no reviewer.
That failed invocation and all usage remain preserved as overhead. The corrected
manifest adds that existing support file without changing acceptance inputs.
Infrastructure-error classification was added with a regression test so the same
missing-source failure cannot trigger implementation retries again.

The corrected run-2 reproduced the original failure, rejected Luna's automatic
repair (`return index`, 240 public mismatches), and escalated once to Sol. Its
unchanged copy bodies and `index >> 5` return passed every deterministic memory
gate. The independent reviewer found no source-level discrepancy but requested
clearer hash-domain and execution provenance. Its refusal remains preserved; no
package was accepted. The strict local validator also rejected its unsupported
issue function value `all`.

One explicitly authorized evidence-correction invocation reuses that unchanged
Sol proposal, freezes the earlier refusal and the ABI/backend evidence, reruns
deterministic validation, and supplies the enriched provenance to one new review:

```sh
.venv/bin/python tools/run_recovery_pair.py \
  local/pairs/memory-001-evidence-manifest.json local/pairs/memory-001-run-3 \
  --python /Users/daeken/projects/DAODecomp/.venv/bin/python \
  --initial-response local/pairs/memory-001-run-2/attempt-3/model/request/response.json \
  --attempts 1
```

Its declared build prerequisites also execute both synthetic demo commands and
retain their reports. They remain infrastructure checks, separate from game
corpus evidence. Every invocation, prior refusal and request cost remains in its
own output directory; an evidence correction never erases a failed run.

Run-3 finished `accepted-for-integration` on macOS arm64 with AppleClang 21,
Python 3.14.7 and Unicorn 2.1.4. The measured positive game corpus is 642 cases
(354 public and 288 held out), each repeated twice per side. The memory negative
control has 12 stable mismatches and 25 passes. Synthetic demonstrations separately
have 59 passes and a control with 6 mismatches/53 passes. The source hash is
`91ba11c8c3c8ac16985f757358ef78e6b90a6f2e41a4abd48313efef901f6f31`.
The reviewer approved the scoped source, with native Windows and broader domains
explicitly excluded. Its prose mistakenly totaled 742 game cases; the reports
establish 642, and that arithmetic correction does not alter the preserved review.

`local/pairs/memory-001-summary.json` aggregates all three invocations and the
original pilot: seven distinct model requests, including two wasted infrastructure
requests and both reviews. It does not count reused responses again. Reported
worker usage is 195,223 input tokens, 5,976 output tokens, and 97.502 seconds of
summed request latency; cache/reasoning fields remain separately recorded. These
are worker measurements, not coordinator usage or account charges. Run-3's
151.649-second elapsed time also includes builds and deterministic validation.
Run-1/run-2 startup tool hashes were not captured and remain explicitly unknown;
run-3 records its measured startup hash. Later on-disk revisions are not substituted
for historical executions.

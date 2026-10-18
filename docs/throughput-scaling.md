# Throughput scaling

The target remains 50–100 **new, integrated functions per hour**, with all
acceptance gates retained. The latest priority is progress along executable
startup toward a runnable Windows replacement, using the
[breadth/depth dependency queue](dependency-queue.md). Function counts alone do
not establish that progress. A source-generation rate or an existing-function
benchmark does not establish the throughput target.

## Measurements on 2026-10-18

The same frozen 22-function direct-field packet now has a DeepSeek benchmark:
`analysis/pilots/deepseek-direct-fields-001.json`.

| Measurement | Result |
| --- | ---: |
| Sol implementation generation | 59.589 seconds |
| Sol independent source review | 15.426 seconds |
| Original Sol pair, including deterministic gates | 542.294 seconds |
| DeepSeek low-thinking implementation generation | 37.201 seconds |
| DeepSeek candidate's deterministic gates and separate Sol review | 476.269 seconds |
| DeepSeek successful generation plus pipeline | 513.470 seconds |
| DeepSeek pilot including initial truncated attempt | 570.967 seconds |
| DeepSeek token cost, both attempts at conservative peak prices | $0.0452166 |

Both accepted candidates passed 8,448 public cases, 2,816 held-out cases and
22 negative controls. The DeepSeek benchmark adds **zero** new recovered
functions and does not replace the existing production candidate. These are
small call-free memory helpers, not a general model-quality comparison. Runs
overlapped other work, so their timings are not a controlled speed benchmark.
The cost estimate excludes Sol, coordinator usage and account quota; it is not
a vendor invoice.

The successful DeepSeek request used `deepseek-flash`, low thinking, a 32,768
output-token limit and the original frozen implementation packet. High thinking
with a 16,384 limit previously truncated the response and was rejected. The
independent Sol reviewer still consumed 291,282 input tokens. That repeated
review context is a more substantial token target than the small candidate body.

## Ordered work

1. **Keep ordinary recovery inside reviewed families.** The exact corpus hash
   map and literal 22-function guards prevented data-only growth. Their minimal
   replacement passed independent review under
   `local/pilots/direct-field-extensibility-001/`. It must not be applied during
   the running 69-function checkpoint. Another 24 functions have original
   characterization and an isolated support proposal; they are not accepted yet.
2. **Keep compiled artifacts stable per packet.** The present direct-field
   library grows with the entire family, so adding functions still invalidates
   that family's comparisons. Separately compiled immutable packets would allow
   unchanged execution images to retain evidence. Preserve complete coverage,
   actual image/dependency hashes and fresh rebuild attestation; never merely
   ignore changed linked images. This is a proposal, not adopted behavior.
3. **Reduce redundant review context.** Supply source, instruction/ABI evidence,
   contracts, semantic coverage and compact gate results once, with exact
   artifact/corpus bindings. Let deterministic code verify the full inventory
   and per-case records. Independently review any prompt change before adoption;
   missing semantic evidence must not be hidden by summarization.
4. **Run a bounded automatic queue.** Prepared packets should advance through
   generation, public checks, held-out checks, controls and independent review
   without coordinator intervention on success. Preserve current attempt and
   request ceilings; reserve coordinator work for evidence gaps, disagreements
   and integration. Scale concurrency after measuring ready-queue depth and
   validation capacity, not merely the number of available models.
5. **Generate recognized instruction patterns mechanically.** Reviewed accessor,
   flag and copy templates can emit defined C++ and fixture proposals. Validate
   each instance against original bytes and execution, retain independent review,
   and reject unsupported patterns. Use models for ambiguous control flow and
   dependencies. This is a future extension, not a completed lifter or proof.

## Provider budget and evidence

The user authorized a **$50/day** DeepSeek cap. Use calendar days in
`America/Chicago`, persistent concurrency-safe reservations before dispatch,
and conservative peak-price input/output allowances. Failed calls and retries
count; uncertain usage retains the reservation. Seed the ledger with a $0.05
debit for the two pre-ledger calls above. The reviewed provider is now
`workers/deepseek_packet.py`; the shared ledger is initialized at
`local/providers/deepseek-daily`. The v1 blocked review and accepted v2 repair
remain under `local/pilots/deepseek-provider-001/` and `-002/`. Credentials stay
outside prompts, logs and Git.

Official references: [model identity](https://api-docs.deepseek.com/quick_start/agent_integrations/),
[thinking controls](https://api-docs.deepseek.com/guides/thinking_mode/),
and [pricing](https://api-docs.deepseek.com/quick_start/pricing/).

Track new integrated functions/hour, preparation and validation queue times,
first-attempt pass rate, attempts per accepted function, per-provider tokens and
estimated charges. Continue reporting native Windows evidence separately;
corpus agreement remains bounded evidence, not universal equivalence.

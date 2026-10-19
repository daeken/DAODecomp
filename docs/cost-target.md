# Working toward a $200 decompilation

The target is roughly **$200 total DeepSeek spend**, including the user's reported
~$32 already spent, for a useful decompilation and a replacement that runs with the
original assets. This is a spending target, not a demonstrated completion estimate.
Codex quota and engineering time are separate; we do not have dollar attribution
for coordinator/agent quota. The existing $50/calendar-day America/Chicago limit
is unchanged.

## What the measurements changed

The published snapshot contains 920 matches: 807 from the earlier native leaf
workflow and 113 from the broader object workflow. Those matches cover about
27,900 of 6,026,653 inventoried function-body bytes (0.46%). Ranges can overlap;
neither byte coverage nor the provisional 27,555 identities measures game completion.

The broader object workflow is substantially more expensive than the earlier
leaves: approximately $34.92 of conservative ledger debit for 113 new matches,
versus $13.97 for the earlier 807. These peak-rate estimates are **not** the user's
actual bill. Extrapolating $32/920 across the whole game understates the difficulty.

An audit of 965 retained object responses found:

- 87.6% of completion tokens were reasoning. Truncated responses consumed about
  19.9% of retained-response debit, usually without usable source.
- 1,516 of 1,706 unresolved-symbol observations used a virtual address where the
  stable identifier required an RVA. This is mechanically repairable source naming,
  not a reason to ask a model to rediscover the function.
- Repeated incoming-caller lists occupied 16.8% of serialized prompt bytes beyond
  a four-caller sample. Byte savings are not measured token savings.
- Most successful compilations still did not match. More full-source repairs are
  not automatically a good investment, especially for unsupported comparisons.

## Experiments completed

All comparisons used the existing full-function object comparator, unchanged.
Compiler execution was VC8 x86 in Windows 11 ARM64 translation. No experiment
executed the original game or a replacement game.

| Experiment | Measured result | Additional paid inference |
| --- | --- | ---: |
| Ghidra first pass, 200 functions stratified by size and direct calls | 200 drafts in 6.09s; 133 provisional C++ sources; 106 compiled objects; 12 exact matches, of which 8 were new | $0 |
| Address-name normalization, 20 retained batches | 175 compared function observations; exact matches increased from 9 to 17; 8 new distinct matches | $0 |
| Non-thinking Ghidra-assisted pilot, 20 functions in 6 groups | 5 valid responses; 2 groups compiled; 1 exact match, already found by the deterministic seed pass | ~$0.0271 conservative debit |

The initial version of the paid pilot spent another ~$0.0319 and failed response
checks in all six groups. The corrected pilot sorted requested functions and
canonicalized draft identifiers; parser/acceptance checks were not weakened.
Combined conservative reservations stayed below $0.20, and recorded token debits
totalled ~$0.0591. Failures remain retained. This was a small feasibility experiment,
not a controlled quality comparison with the previous thinking configuration.

The two free experiments found **16 distinct new matches** beyond the published
920; these remain experimental artifacts, not production-queue acceptance credit.
Their raw drafts, original instruction evidence, compiler outputs and receipts
are ignored local files under `local/cost-reduction-001/`.

The result supports a free first pass. It does **not** support switching the
production queue wholesale to non-thinking generation. The current paid queue
is paused and drained; its original thinking/repair defaults remain unchanged.

## Proposed production order

1. **Decompile once locally.** Export Ghidra drafts and automatically inferred
   symbol/type information for the whole inventory. Normalize names and common
   syntax mechanically, compile first, and accept complete matches through the
   existing comparator. Keep all other drafts and sources. Ghidra types and
   prototypes remain hypotheses. Start with the installed Ghidra backend;
   building another decompiler is not on the $200 critical path.
2. **Spend on specific defects.** Give DeepSeek the draft, exact requested
   identities, required dependency declarations and concrete compiler/diff feedback.
   Test a small targeted-edit mode before adopting it. Mechanical name/marker
   issues belong in tooling. Missing comparator support belongs in a tooling queue.
   Keep complete binary evidence locally without repeatedly sending every caller.
3. **Stop chasing every byte.** A complete match is an automatic acceptance path;
   a compilable nonmatch is retained, not accepted as equivalent or discarded.
   Default to one targeted repair in the proposed cheaper mode, with further work
   prioritized by startup/runtime need or demonstrated improvement. Do not spend
   six retries on every compiler-layout difference.
4. **Integrate while recovering.** Generate a canonical dependency/symbol inventory
   from the sources and objects. Select one definition per RVA and expose calling
   convention, parameter and global-layout conflicts. Fix shared conflicts by
   dependency group. Link coherent slices and use actual Windows failures to direct
   work. No new authored per-function corpora or contracts are needed.

Only C++ is authored per function. Drafts, metadata, dependency reports and build
evidence are generated. Unknown calls cannot become successful stubs, and unknown
comparisons cannot become passes.

## Budget and decision points

With ~$32 spent, the remaining ~$168 allows only **0.63 cents per remaining
inventory identity**, including repairs and integration. A proposed allocation is:

| Allocation | DeepSeek budget |
| --- | ---: |
| Already spent, user-reported | $32 |
| Small measured experiments | $5 |
| First-pass gaps after free recovery | $65 |
| Selective repairs | $48 |
| Startup, linking and runtime integration | $50 |
| Total | $200 |

These are allocations, not costs predicted to finish each stage. At peak rates,
1,500 input + 1,000 output tokens per remaining identity would cost about $43.95
for one pass; 3,000 + 2,000 would cost $87.90; 6,000 + 4,000 would cost $175.79.
This arithmetic excludes retries and assumes no additional reasoning tokens.
Free seeds must remove a material fraction of paid work, and repairs must earn
their cost. Actual billing can be lower through cache hits and off-peak rates;
do not discount the user's already-billed $32 again.
[DeepSeek pricing](https://api-docs.deepseek.com/quick_start/pricing/)

Before resuming broad paid generation, measure a targeted-repair pilot on the
retained failures: new compilable functions, new exact matches, unresolved ABI
conflicts, tokens and cost. Compare with the free seed baseline. If it mainly
rewrites working seeds or repeats structural failures, fix that bottleneck first.
Preserve the integration allocation rather than exhausting the budget on leaves.

## What “runs” still requires

The published sources are independent translation units, not a linked game.
The current build does not supply replacement startup/CRT initialization,
canonical globals, imports, TLS, vtables, exception metadata or all required
middleware boundaries. Extern declarations permit object compilation but do not
implement these dependencies. The EXE inventory may also omit required code in
other modules.

Track distinct executable milestones: a linked replacement starts; it accesses
original assets; it reaches the menu; it loads a save; a defined gameplay scenario
works. A hybrid calling unrecovered original code must be labeled as such and
does not count as the completed replacement. Near-matching bytes alone cannot
establish these milestones. A $200 runnable full-game result remains unproven.

## Implemented tooling

- `tools/ghidra/ExportCandidates.java`: read-only export from the pinned analysis.
- `rapid_object/ghidra_seed.py`: representative selection, provisional C++
  conversion, canonical draft names and offline compiler/comparator measurement.
- `rapid_object/symbol_normalize.py`: source-only, registry-backed VA/RVA fixes;
  retained originals and the comparator are unchanged.
- `rapid_native/propose.py`: optional non-thinking and bounded-output controls for
  experiments, with existing defaults and accounting preserved.

Reproduction uses the existing local Ghidra project and Windows compiler setup:

```sh
python -m rapid_object.ghidra_seed select --count 200
python -m rapid_object.ghidra_seed export
python -m rapid_object.ghidra_seed convert
python -m rapid_object.ghidra_seed measure
```

Measurement requires production to be paused and drained and uses its shared VM
lock. It grants no production acceptance credit. The measured historical sample
and its original tool revisions remain retained when tooling changes.

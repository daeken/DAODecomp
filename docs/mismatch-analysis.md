# Deterministic mismatch analysis

Use retained compiler artifacts to identify reusable repair opportunities before
paying for individual source repairs. The diagnostic classifier consumes the
existing full-range comparison report; it does not change acceptance, normalize
instructions into a match, or establish behavioral equivalence.

```sh
python -m rapid_object.mismatch path/to/comparison.json --output local/diagnosis.json
python -m unittest rapid_object.tests.test_mismatch -v
```

Each function receives a deterministic primary label, overlapping observation
labels, bounded examples with instruction offsets, and explicit uncertainty.
Identical mnemonic/operand-type/width sequences use positional pairing. Other
sequences use bounded heuristic alignment. Unknown relocations, unsupported body
ranges and incomplete decoding remain separate outcomes. A stack-adjustment or
branch label in a substantially different function is not a proven root cause.
Raw decoded original instructions belong in ignored local reports.

## First frozen census

On 2026-10-19, 29 retained reports supplied 14,174 distinct compiled identities.
The deterministic selection used the last existing compiled-summary record per
module and RVA in the frozen report order, without choosing promising scores.
Fresh comparison reproduced 1,842 exact, 11,098 nonmatching and 1,234 inconclusive
outcomes, with no input-binding failures or changed statuses. Excluding 2,181
identities already in the published index left 11,993 rows for repair ranking.
An older nonmatching candidate is not new work if another source for its identity
has already been published.

| Primary observed difference | Functions | Original body bytes |
| --- | ---: | ---: |
| Stack adjustment / return cleanup | 3,658 | 563,326 |
| Branch condition | 1,985 | 283,856 |
| Larger structural difference | 931 | 21,198 |
| Instruction selection | 726 | 54,467 |
| Call target | 725 | 64,165 |
| Stack displacement | 673 | 54,523 |
| Unresolved relocation | 654 | 185,047 |
| Control-flow sequence / target shape | 646 | 24,430 |
| Unsupported body boundary / range | 576 | 190,464 |
| Memory addressing | 379 | 18,990 |
| Memory displacement | 373 | 26,846 |
| Operand width | 368 | 31,892 |
| Register | 222 | 11,532 |
| Incomplete linear decode | 70 | 29,122 |
| Immediate | 7 | 320 |

Primary labels follow fixed precedence; overlapping labels are also retained.
Body-byte totals sum requested inventory ranges, whose boundaries remain
hypotheses. These figures are neither function sizes certified by the classifier
nor estimates of recoverable matches.

Only 106 unpublished nonmatches had identical instruction shapes throughout.
The following smaller frontiers have at most four changed aligned instruction
pairs; categories can overlap:

| Narrow observation | Functions | Body bytes |
| --- | ---: | ---: |
| Memory addressing | 40 | 766 |
| Register | 13 | 288 |
| Call target | 9 | 256 |
| Stack cleanup | 7 | 434 |
| Memory displacement | 4 | 176 |
| Stack displacement | 1 | 60 |

A separate single-pair branch-condition frontier contains one 32-byte function
with no structural insertions or deletions. These are candidates for investigation,
not automatic rewrite instructions. Check declarations and argument passing for
call/cleanup differences, pointer expressions and layout for memory differences,
and source comparison types for branch differences. Register changes can reflect
allocation decisions or different behavior.

Fresh comparison and initial categorization took 138.731 seconds; the final
diagnostic replay of saved reports took 24.310 seconds. No compiler builds or
provider calls were made. Analysis ran on macOS ARM64 with Python 3.14.7 and
Capstone 5.0.6; the retained objects came from VC8 SP1 x86 under Windows ARM64
translation. Thirty generic controls and 270 standard tests (seven skips) passed.
Development and review cost is separate from zero provider spend.

The frozen inputs, full comparisons, detailed census and stratified examples are
retained locally under `local/mismatch-census-001/`. The classifier and generic
controls are reusable; a new census must bind its own original, source, objects,
compiler receipts, comparator, decoder and publication snapshot. This census
does not include results from the concurrently running frame-repair sweep.

## Comparing lifted instructions

[SharpRetro evaluation and paired lifting](sharp-retro.md) describe the next
diagnostic layer. Typed IL can expose register, flag, memory and control-flow
effects that instruction spelling obscures. Unsupported nodes or incomplete
lifting must remain explicit. Agreement between lifted trees is a diagnostic
observation, not a replacement for the current object-match acceptance rule.

## Follow-up: inspect the cause behind the memory label

The frozen 40-case memory-addressing frontier later supported 29 AST-bound
indirect receiver proposals. The original ECX/vtable dataflow was missing from
the provisional call expression; this was not evidence to change field offsets
blindly. One variant per target produced 16 new full exact matches (311 body
bytes), 12 nonmatches and one transport unknown; ten existing exact controls
remained intact. The original census above stays a historical snapshot rather
than being relabeled after these repairs. [Conditions, limits and measurements](compile-first.md#bind-indirect-receiver-hypotheses-to-the-observed-call-edge)
describe the generic rule and unchanged acceptance gate.


The unchanged receiver-rule breadth pass exhausted its eligible frozen-census
population: 25 targets, 24 compiled, nine new exact objects / 161 body bytes,
15 retained nonmatches and one transport unknown. Ten cached exact controls
remained exact. See [compile-first](compile-first.md#unchanged-receiver-rule-breadth-checkpoint)
for exclusions, timing and the 2,241-source snapshot checkpoint.

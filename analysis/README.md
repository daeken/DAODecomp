# Function inventory

`functions.json` currently records the two recovered functions from the pinned
game binary. Their implementation status is separate from the measured evidence
in `validation/first-leaves.json`; neither has native Windows validation or a
symbolic proof. `static-summary.json` summarizes the much larger initial Ghidra
inventory, whose full output is kept under ignored `local/analysis/`.

Use `(binary SHA-256, module, RVA)` as the stable identity; labels and inferred names
can change. Preserve noncontiguous ranges, thunks and shared tails rather than
assuming every function is a single contiguous byte range.

For each entry record identity, candidate name, ranges, evidence locations, calling
convention and signature confidence, incoming/outgoing calls, global accesses,
instruction/branch counts, ownership and current status. Track imported and bundled
third-party code separately; neither may disappear from the scope denominator.

Suggested lifecycle: `discovered -> characterized -> oracle_ready -> implementing
-> corpus_pass -> reviewed -> integrated`. `blocked` includes a concrete reason.
Proof evidence is an additional field, never inferred from lifecycle status.

Report counts and code-byte coverage over the discovered inventory, unknown
executable regions, and scenario coverage. A discovered-function percentage is
not a percentage of the full game until discovery coverage is audited.


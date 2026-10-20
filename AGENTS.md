# DAODecomp working rules

- Active direction on `codex/replayable-decompilation`: original binary ->
  SharpRetro typed effects -> shared recovered IR -> compiler-profile C++ ->
  historical compiler -> independent complete comparison. Read
  `docs/replayable-decompilation.md` and current local handoff first.
  `codex/ghidra-mainline` preserves the previous committed workflow.
- Progress through the pinned inventory in ascending RVA order, beginning at
  `0x1000`. The earliest unresolved function is the frontier. No ease/size
  filtering or silent skip; dependency analysis and whole-inventory regression
  checks do not themselves advance the frontier.
- Recover reusable architecture/compiler rules with explicit preconditions.
  Do not encode target RVAs, expected output bytes or copied recovered bodies
  as transformation logic. Fix incorrect lifter semantics at the correct layer;
  unsupported semantics remain blockers, never ignored effects.
- The binary, versioned knowledge and transformation history are durable inputs;
  generated C++ is reproducible output. Names/types bind to tracked entities.
  JSON recipes/trials must preserve prior candidates and report regressions,
  unknowns and pending work. Introduce these operations through the C# MCP/core.
- Use a tight development loop: focused generic tests, a complete real-compiler
  comparison at the current frontier, and relevant previously matching controls.
  Continue through consecutive functions within a bounded implementation batch;
  do not require a director handoff, full suite, review, CI or installation after
  every small rule. Development matches and the development frontier are
  provisional until the batch passes release checks.
- During this early development phase, use a representative regression sample
  rather than a whole-inventory scan or compilation sweep. Start with at most
  16 identities covering the frontier, relevant previously matching domains,
  changed-rule boundaries and known failures. Record selection and exact inputs
  in existing job records; retain unchanged caches. Investigate sample regressions.
  Outside-sample identities are unverified under changed rules, not assumed passes.
  Broader scans and suites are on demand when a concrete finding needs them or
  the user requests them; they are not routine iteration or release gates.
- At a coherent checkpoint, build changed components, finish focused tests and
  representative complete comparisons, obtain one cumulative independent review
  of new machinery, and publish code plus documentation together. CI is temporarily
  disabled at the user's request; do not launch it, wait for it, or require it for
  publication/installation. Install the reviewed immutable release with rollback.
  Do not add a second release cycle solely to publish the first cycle's results;
  keep those results in the local handoff and the next combined checkpoint.
  Full range, relocation, EH and unknown-outcome requirements remain unchanged.
- Goal: function-level behavioral equivalence to the pinned original build, then
  a replacement executable using original assets. A byte-identical whole game is
  not required. Complete reccmp matches are an authorized automatic acceptance
  path for native x86 C++ built with the selected historical compiler; retain
  nonmatches for later iteration or other checking. Keep this evidence distinct
  from a universal proof of C++ semantics or whole-game behavior.
  The new pipeline targets complete matches across the inventory, but 100%
  coverage is an aspiration, not an assumed achievable result or a whole-game
  execution claim. Keep its counts separate from inherited published source.
- Read README.md and docs/validation.md before changing validation or recovered code.
- Never describe synthetic tests, guessed signatures, emulator-only results or a
  passing corpus as a proof of the game. Distinguish observation from inference.
- Original instruction bytes and measured execution are evidence. Decompiled
  pseudocode and model explanations are hypotheses to check against that evidence.
- The only authored artifact per new function is its decompiled C++. Do not require
  per-function contracts, fixtures, test corpora, adapters or proof annotations.
  The candidate factory records binary SHA-256 + module + RVA and provenance
  automatically. Generated candidates remain unvalidated; preserve the separate
  historical accepted-function count. Unknown stays unknown.
- New equivalence checking must consume the original binary and candidate C++
  through reusable machinery. Automatically derived inputs, compiler products,
  execution records and counterexamples may be cached, but require no per-function
  authoring or manual acceptance packet. No difference observed is not a proof.
- For reccmp, inline source annotations carry function identity. Generate build
  configuration, symbol/size metadata and reports automatically. A complete match
  requires the requested function and full original range, not a matching prefix,
  a rounded percentage, a missing comparison or an effective-match heuristic.
- Preserve observed wraparound, signedness, shifts, aliasing, layout and floating
  point behavior with defined C++ semantics. Guest pointers are not host pointers.
- Worker scope comes from its packet. Do not change the oracle, comparator, frozen
  fixtures, shared type definitions or acceptance criteria to make a candidate pass.
  Propose contract/type corrections with evidence for separate review.
- Do not stub unknown calls as successful zero returns. Missing semantics,
  exhausted budgets, crashes, solver unknown and dropped paths cannot pass.
- Use independent worktrees or disjoint owned files for concurrent work. A single
  coordinator owns shared types and registry updates. This file does not itself
  authorize launching workers or paid inference.
- Keep the original install and captures under ignored local/, or the user's
  ignored installer/ and gamedata/ directories. Do not commit game
  executables, assets, memory dumps, generated analysis projects or credentials.
- Run focused generic boundary/negative tests for changed tooling and build the
  changed components. Run the README demos when their harness is affected.
  The full `python3 -m unittest discover -s tests -v`, CTest, cross-platform CI and
  whole-corpus sweeps remain available on demand, not mandatory for each checkpoint
  during this early phase. Documentation-only changes do not rebuild unchanged
  tooling. Report actual host, sample coverage and unrun checks.
- Maintain the public methodology in `docs/reproducible-decompilation.md` and
  `docs/learning-log.md` as work proceeds. Record reusable discoveries, failed
  approaches, transformation preconditions, measured costs/yields with denominators,
  tool/source versions, reproduction steps and unresolved limitations. Distinguish
  measured results from proposals and DAO-specific assumptions from portable ideas.
  Keep proprietary inputs, raw captures and credentials local. This is shared
  experiment/tooling documentation, not a new per-function authoring requirement.


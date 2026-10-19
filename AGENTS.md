# DAODecomp working rules

- Goal: function-level behavioral equivalence to the pinned original build, then
  a replacement executable using original assets. A byte-identical whole game is
  not required. Complete reccmp matches are an authorized automatic acceptance
  path for native x86 C++ built with the selected historical compiler; retain
  nonmatches for later iteration or other checking. Keep this evidence distinct
  from a universal proof of C++ semantics or whole-game behavior.
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
- For tooling changes run `python3 -m unittest discover -s tests -v`. For C++ or
  harness changes build with CMake and run both synthetic demo commands in README.
  Report which host/build actually ran; CI definitions alone are not test results.
- Maintain the public methodology in `docs/reproducible-decompilation.md` and
  `docs/learning-log.md` as work proceeds. Record reusable discoveries, failed
  approaches, transformation preconditions, measured costs/yields with denominators,
  tool/source versions, reproduction steps and unresolved limitations. Distinguish
  measured results from proposals and DAO-specific assumptions from portable ideas.
  Keep proprietary inputs, raw captures and credentials local. This is shared
  experiment/tooling documentation, not a new per-function authoring requirement.


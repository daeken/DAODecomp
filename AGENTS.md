# DAODecomp working rules

- Goal: function-level behavioral equivalence to the pinned original build, then
  a replacement executable using original assets. Binary matching is a non-goal.
- Read README.md and docs/validation.md before changing validation or recovered code.
- Never describe synthetic tests, guessed signatures, emulator-only results or a
  passing corpus as a proof of the game. Distinguish observation from inference.
- Original instruction bytes and measured execution are evidence. Decompiled
  pseudocode and model explanations are hypotheses to check against that evidence.
- Each recovered function needs a stable binary SHA-256 + module + RVA identity,
  a contract, provenance and a reproducible validation report. Unknown stays unknown.
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


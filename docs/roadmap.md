# Milestones and completion criteria

## 0. Foundation (this scaffold)

- C++20 build, source/evidence boundaries and agent rules.
- PE fingerprinting and exact observation comparison with deterministic fixtures.
- Synthetic x86 machine-code vs native C++ demonstration and a rejected mutant.
- Tests that reject missing observations, wrong types, nondeterminism, crashes and timeouts.

This is not game decompilation progress. CI is defined for Linux/macOS/Windows;
local results establish only the host actually used.

## 1. Reference build and first oracle

Current progress: the complete extraction is checksummed, the main executable is
pinned, an initial Ghidra inventory exists, and two real instruction slices agree
with recovered C++ on a deterministic corpus. The negative control is rejected.
Native corroboration and a completeness audit of the inventory remain open.

Pin the install, inventory executable functions and scripts, choose a reference
host, characterize one function, and replay its actual instruction bytes with all
dependencies modeled. Demonstrate original/original stability and a deliberate
candidate mutation failing. Cross-check the emulator against native execution.

## 2. Recovery pilot

Recover 10-30 well-characterized functions. Measure actual model acceptance/cost
and oracle throughput. Settle shared types using multiple callers. Add held-out
cases, counterexample minimization and machine-enforced packet/hash protection.
Prototype symbolic validation on one suitable integer function. Decide whether
SharpRetro reduces the total work of building that checker.

## 3. Dependency clusters and playable slices

Replace complete call-graph clusters. Validate parser/resource behavior, game state
transitions, scripts and persistence with original assets. Add initialized-state
capture and native Windows ABI adapters as required. Maintain a runnable vertical
slice, progressing toward boot, asset loading, menus, saved-game loading and gameplay.
The precise order follows the observed binary, not a guessed engine architecture.

## 4. Whole-game integration

Account for every discovered executable region, runtime component, script system,
bundled middleware boundary and explicitly deferred area. Exercise deterministic
scenarios across content, error paths, saves, rendering/audio commands and concurrency.
Full scope should retain base game, expansions/DLC and auxiliary components in the
inventory even if staged behind the initial main-executable milestone.

"Done" requires the replacement executable to operate on original assets, with a
reviewed behavior/coverage ledger and disclosed gaps. Function counts, clean builds,
screenshots and a green test suite are each insufficient alone. No timeline or
whole-project token estimate is credible before inventory and the pilot.


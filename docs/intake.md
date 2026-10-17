# First intake after installation

1. Keep one pristine GOG installation. Record release label, installer identifiers,
   language, included expansion/DLC content and patches. Do not infer the executable
   version or architecture from the product name. Start with one exact build.
2. Fingerprint the main executable and bundled DLLs with the CLI in README. Record
   each module's relative install path and hash. Separate OS dependencies and bundled
   third-party libraries. Later, hash the asset set used by each replay fixture.
3. Confirm the executable's machine type, sections and load configuration; inspect
   imports, exports, resources/version information, relocations, RTTI, symbols and
   any relevant script bytecode. The current fingerprint tool records PE headers,
   sections and hashes; it does not yet extract those richer analysis records.
4. Create a local Ghidra project with the verified language/compiler spec. Pin the
   Ghidra version and analysis options. Export a function inventory, caller/callee
   graph, disassembly, pseudocode, globals and available type information to ignored
   `local/analysis/<binary-sha>/`. Treat inferred boundaries/signatures as hypotheses.
5. Audit executable regions without functions, jump tables, thunks, tail calls,
   indirect calls, vtables and code/data ambiguities. Measure discovery coverage.
   Scripted game logic and executable logic need distinct inventories but both
   remain part of the full behavior goal.
6. Choose a reference execution host and test a simple leaf with an established
   ABI. Corroborate local emulator execution with that host. For stateful routines,
   capture a real initialized entry state and identify its reachable memory graph.
7. Select the first 10-30 functions by ease of observation and dependency fan-in:
   pure integer helpers, bounded buffer routines, parsers, then stateful utilities.
   Their presence/names are candidates to find, not claims about the unseen binary.

Suggested local layout:

```text
local/
  game/                  # or reference an installation outside the repository
  manifests/
  ghidra/
  analysis/<sha256>/
  captures/<function-id>/
  fixtures/<function-id>/
  runs/<run-id>/
```

Ghidra 12.1.4 is installed in the ignored local tool cache. The first analysis
produced 27,555 function hypotheses, and `tools/ghidra/ExportInventory.java` exports
the inventory and selected decompilations. See [static analysis](static-analysis.md)
for pinned tool identity and reproduction commands, and
`analysis/static-summary.json` for counts, warnings and artifact hashes.
There is no live game injection or complete executable loader yet.

Native Windows on an x86-compatible CPU is the preferred reference for eventual
authoritative checks. Windows ARM translation, Wine and emulation remain possible
development aids; decide using the actual build and available host, not platform
assumptions. No full game run is required to start validating genuinely isolated
leaf functions once their code/data dependencies are known.


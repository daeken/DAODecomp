# All-inventory object recovery

This profile feeds every identity in the pinned 27,555-function inventory into a durable queue. It does not exclude calls, globals, imports, indirect calls, floating point, TLS, large functions or discontiguous ranges. The first catalog contains 26,748 new generation identities and imports 807 existing native reccmp attestations without another provider request. Imported attestations and new exact COFF matches are separate counts. All inventory signatures remain hypotheses; `undefined fn(void)` does not establish a zero-argument ABI.

The sole authored function artifact is C++98. Automatically derived packets contain original range hashes, instruction bytes, callers/callees, address references, import details and provisional declaration context. Source uses stable `fn_RVA` and `g_RVA` identities; extern declarations and out-of-line class methods are permitted. Unknown calls must remain unresolved rather than successful stubs. The compiler emits `/c /Gy /Z7` COFF objects with no link, entry point, dependency implementation or game execution. Compiler symbols are mapped mechanically to pinned identities.

The selected historical toolchain is Microsoft VC8 SP1 14.00.50727.762, running under x86 translation in Windows 11 ARM64. It is a candidate historical compiler; the exact original compiler patch remains unknown. Host dependencies are pinned in `requirements-native.txt`. The isolated VM compiler is the existing `C:\Users\daeken\tools\VC8-SP1\vcvars.cmd`; it needs no new service or global VM installation.

The object comparator accepts only exact full-range bytes after supported x86 relocations are resolved to explicit original targets. It checks relocation addends rather than masking address fields. Unknown relocation kinds, absolute COFF symbols, unexamined defined data, unsupported boundaries, missing symbols and discontiguous ranges remain inconclusive. Similarity is repair feedback only. An exact object match is evidence for that source, compiler/object and pinned original range, not universal proof of portable behavior or a complete game. All nonmatches, inconclusive comparisons and failures remain available.

The real VC8 smoke compiled two pinned functions containing an unresolved direct call and an unresolved global plus method call. Both matched their full original ranges; changing the call target or global displacement produced nonmatches. Generic mutation controls additionally reject absolute-symbol map overrides, defined-section addends escaping compared code, unsupported relocation widths, truncated comparisons and stale artifact bindings.

Run from the repository worktree using the Python environment containing the pinned host dependencies:

```sh
python -m rapid_object prepare
python -m rapid_object run --lanes 16 --request-ceiling 120 --max-repairs 6
python -m rapid_object status
python -m rapid_object pause
```

`pause` stops new dispatch while in-flight requests finish and save. SIGTERM of the recorded owner PID also drains and pauses. The owner lock prevents multiple dispatchers; VM builds serialize independently of the 16 provider processes. The old Context and native queues remain paused and retained.

State and immutable attempts live under ignored `local/rapid-object/`. `queue.sqlite3` holds the catalog, provisional symbol registry, batch ownership and best function/source result index. `preparation.json`, `runtime-config.json` and `status.json` expose coverage and limits. Each attempt retains its exact request, paid response, C++, compiler receipt, object and comparison report. The source/object/original hashes, requested identity domain and comparator implementation hashes must agree before a result enters the match index.

Large bodies use byte-backed context pages with a durable cursor. No compilation or matching credit occurs until the final page. Each continuation is a separately budgeted request, incorporates the retained prior source and cannot replay an ambiguous outcome. Input budget failures are recorded explicitly; oversized multi-function requests split mechanically. Known complete but truncated or invalid API responses also split into smaller groups. Children retain the paid parent history, best sources and consumed repair allowance. Timeout or unknown transport outcomes stop without replay.

After complete context, up to six repairs use retained best sources paired with their actual compiler or byte differences. Three nonimproving repairs stop a plateau; fully matched functions leave subsequent requests. Fresh groups receive two scheduling preferences for every one repair preference. Unsupported comparison does not block unrelated work.

Every provider call shares the existing physical request ledger, anchor and history, with at most 120 total requests per persisted 1,800-second cycle. The existing $50/calendar-day America/Chicago ledger is unchanged. Status reports a **conservative estimated budget debit**, using the existing peak rates, rather than actual billed dollars; off-peak billing can be lower. Neither a queue restart nor a split resets accounting.

The paid pilot used the production queue itself. Attempt 1 was retained with VC8 C3865 errors; automatic attempt 2 compiled in 1.797 seconds and produced one exact object match plus one inconclusive global-identity mismatch. The matched function is excluded from further repairs. The 16-lane continuous runner is launched with the defaults above; its ignored launch receipt is `local/coff-expansion-001/launch-receipt.json`. Current counts belong to `local/rapid-object/status.json`, rather than this dated pilot observation.

Common queue controls run without a game, VM or compiler:

```sh
python -m unittest discover -s rapid_object/tests -v
python -m unittest tests.test_rapid_object_coff -v
```

The original executable, generated catalog, source attempts, object files and reports remain ignored local artifacts. Historical portable registry counts are unchanged.

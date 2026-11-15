# Playable DAO replacement task list

Goal: replace DAO's main executable and Umbra code, retain the pinned original
assets and other DLLs, and reach repeatable playable Windows x86 scenarios.
Binary matching is not required. This whole-module work list is paused at the user's
request while [manual recovery tooling](recovery-workbench.md) takes priority.

## Next integrated checkpoints

The static-code-cache/LAA candidate cold-loaded the exact frozen699f input to the
Castle Cousland gameplay HUD on Wine9/CX24 + Rosetta on macOS ARM64. The user then
redirected work to manual recovery. Its process was deliberately stopped through its
monitor; no Root trial remains active. Evidence:
`local/recomp/startup/protected-static-code-cache-cold-load-latest.json`.
Do not reuse historical PID/window bindings. This observation does not establish
combat, a real area transition, matched original behavior or an integrated speedup.
Generated runtime DLLs are now archived and object caches were evicted during
[storage cleanup](local-storage.md); restore/rebuild/restage before a future trial.
Observation deadlines and hidden windows are not exits.
The current private right-hand-corridor snapshot is dd5c; the original replay retains
the separate frozen699f input. These are not a matched comparison yet.

1. When playtesting resumes, continue from the preserved frozen699f checkpoint,
   confirm the map position, and continue toward the quest marker. Preserve concrete dialogue,
   interaction outcomes and runtime failures. Do not reuse the old camera-based
   direction labels or infer game speedup from component timings.
2. Exercise combat and a real area transition. Opening a door or walking around
   Castle Cousland does not establish an area transition.
3. Save, cold-load and repeat a representative scenario. Compare the same frozen
   input with the original, recording backend/host differences and discrepancies.
4. Measure the remaining gameplay slowdown before changing dispatcher, memory or
   flag behavior. Cache enablement and constructed timing loops do not establish
   an integrated speedup.
5. Package reproducible full-build and private-profile launch instructions with
   the pinned assets/providers, exact inputs and known failures. Current local
   playtest controllers are operational evidence, not a portable release runner.

The map inspection corrected the earlier camera-based “west” label: the party
was at the right-hand end of the corridor below the Great Hall, away from the
lower-left quest marker. Existing capture/action/snapshot filenames retain that
historical label; their contents are preserved. Location evidence:
`local/recomp/startup/scene-location-correction-latest.json`.

The instruction/exception and ABI checklists below remain open where their
contracts are incomplete. Successful gameplay observations do not accept all
functions, callbacks, exception paths or instruction encodings.

The experimental dispatcher cache has been built and cold-loaded once, then stopped.
It remembers only entries from the immutable compiled-code
table, separately per thread; dynamic candidates and imports still resolve on
every visit. Collisions compare the full address, and initialization preserves
Windows last-error state. `RECOMP_DISABLE_STATIC_CODE_CACHE=1` retains binary
search for comparison. Component checks and timings are separate from gameplay
and do not establish an integrated speedup.

A bounded macOS host sample retained foreground ownership and observed no new
runtime frontier. Its PE32/Rosetta unwind is incomplete: the prominent dispatcher
address is the return site after calling generated code, not evidence that binary
search dominates CPU time. Constructed raw/provider x87 controls completed without
detected TOP mismatches with this sampler; this is limited evidence, not universal
sampling safety. Windows SuspendThread/GetThreadContext sampling remains excluded.
Evidence: `local/recomp/startup/game-mac-sample-latest.json` and
`local/recomp/startup/mac-sample-control-latest.json`.

## Whole-module iteration strategy

The user redirected the workflow from adding reached functions to generating the
entire main executable and Umbra up front. Their pinned inventories currently
contain 27,555 and 3,134 function hypotheses, respectively. Retained SDK DLLs stay
native. The target is a complete replacement build whose errors are fixed by
shared cause across the whole program.

Generation should use cached function shards with independent diagnostics. One
unsupported function must not abort analysis of the rest. Track original-byte
coverage, unresolved switch cases, ambiguous ownership/bounds, unsupported
semantics and compilation failures separately. Preserve annotations and stable
binary/module/RVA identities. Unresolved code remains an explicit failure when
reached; generating source does not grant behavioral acceptance.

The bulk bridge now isolates function failures and writes immutable per-function
source/metadata shards. The first unrestricted pass attempted all 30,689 entries:
30,146 emitted source bodies, 531 generation failures and 12 preparation failures.
Of the emitted bodies, 390 have incomplete declared inventory-byte coverage;
even complete inventory-byte coverage is not a complete control-flow or behavior
claim. Many failures share unsupported floating-point instruction families.

The next backend revision supports seven previously missing x87 add/subtract
register families (56 encodings), including reverse subtract with pop. Both
structure analysis and emission now handle them; emission checks each original
opcode before invoking the native value provider. Constructed controls on Wine
11/macOS ARM64 observed 20,160 arithmetic cases and 252 empty-stack cases with
zero mismatches, four expected refusals and restored host FP state. This is
bounded provider evidence, not original-function or Windows-hardware acceptance.
Its archived inputs/report are `local/recomp/x87-register-add-sub/evidence.json`.
A second whole-inventory attempt at
`local/recomp/bulk/runs/1794251168363626000` completed with 30,437 emitted bodies,
240 generation failures and 12 preparation failures. This is 291 additional
bodies; it does not grant behavioral acceptance.

All 30,146 first-pass bodies compiled as Windows i686 objects with zero compiler
errors, and linked into replacement main/Umbra images and a shared runtime.
The runtime registers 1,988,227 instruction addresses and 582 imports. Its first
frozen composed-host run stopped explicitly at Umbra 0x100ca32b after 7.264
seconds during process attachment. Permanent DEP was observed before entry;
original instruction pages remain data/NX. This run did not reach main or a menu.
Exact executed images/sources and the observation are retained at
`local/recomp/bulk-native/runs/1794252202009723000/report.json`.

That stop exposed a catalog regression: the static inventories omitted 802
existing reviewed selections (798 main, four Umbra), including this initializer.
The generation catalog now unions every static hypothesis with existing bounded
selections, preserving their review/contract provenance. The known catalog has
31,491 entries before the code-pointer discovery below; these include shared fragments, not 31,491 accepted source
functions. Original inventory and supplementary-entry counts remain separate.
One declared shared-tail overlap is reported; its larger inventory owner still
fails generation, so it has not created competing compiled owners.

Read-only Ghidra exports now retain all static instruction boundaries/flows.
An overlay proposes 67,951 internal entries across 387 partially covered bodies,
checking pinned original bytes and independent decoder lengths inside existing
ownership ranges. It changes neither bounds nor project annotations. Remaining
uncovered bytes and rejected/unsupported code stay explicit. The combined catalog
and coverage generation completed at `local/recomp/bulk/runs/1794252651008955000`:
31,239 emitted bodies, 240 generation failures, 12 preparation failures and 14
emitted bodies with partial inventory-byte coverage. All 31,239 bodies compiled
and linked; the runtime registers 2,136,080 instruction addresses and 582 imports.
Its build/link continuation is recorded in
`local/recomp/startup/coverage-whole-integration.json`.
Byte-identical completed cache payloads now use independent APFS clones across
backend revisions; source/metadata hashes are checked before sharing.
The existing native loader, imports, memory, callback transport and frozen-run
infrastructure remain useful for the subsequent whole-program link.
Commands and limitations are in [the recompiler guide](../recompiler/README.md).
Local generation evidence is `local/recomp/bulk/latest.json`; compilation status
is `local/recomp/bulk-compile/latest.json`. At that checkpoint, the tooling suite
ran 310 tests with one skip on macOS ARM64 after the diagnostic runner changes.
CMake, six non-tooling CTests and
both synthetic demos also passed; these checks do not establish game behavior.

## Current frontier

**The provider-cache game run is preserved and deliberately stopped; its successor
is linked but has not run.** The historical process was host74502/window41332 in
`local/recomp/mac-provider-cache/1794324762936428000` (session88205).
Its monitor recorded controlled exit-9 after8,668.438seconds, stop_requested=true,
timed_out=false and no monitor error or runtime frontier. Stable on-disk character
files were snapshotted before stopping. The new static-code-cache/LAA candidate
has the same63,612 bodies and2,422,520 instruction entries; its integrated menu,
load and gameplay observations are still pending. Current bindings and checks:
`local/recomp/startup/native-provider-cache-checkpoint.json`.
Its splash, windowed client, main menu and populated Load Game screen are
observed. The west-corridor QuickSave cold-loaded to the gameplay HUD; the returned
position is rendered and PageUp changed the camera to an overhead view.
The coarse capture bracket is292.1–366.7 seconds after load input on this shared
host, not an isolated benchmark. Longer bounded S/Q holds then produced visible travel away from the corner and
along the west corridor; combat and an area transition remain pending. Two
mouse floor orders have no observed destination marker/travel in this run and
are not counted as successful movement. Evidence:
`local/recomp/startup/protected-provider-cache-cold-load-latest.json`. A read-only process-memory
diagnostic observed notifications_available=1, epoch61 and228 filename queries
from the frozen runtime symbols; no thread suspension/context APIs were used.
This establishes cache enablement, not an integrated speedup. The private-profile route probe and staged11-file save hashes
passed before launch. This startup observation is incomplete.
The saved prior process was deliberately stopped after7,307.390 seconds to
integrate this change: stop_requested=true, timed_out=false, no monitor error.
This is a controlled incomplete observation, not a main-return or game pass.
The west-corridor quicksave has a stable private snapshot with SHA
b5b9073eb7c02d1dc5d1563799fbafa1d68689c75b86be90c902457fa8019026.
Relative pointer calibration produced a specific locked-door tooltip, a
destination marker and further corridor walking; all mouse paths are not thereby
validated.
On the new cache build, a read-only original-byte-derived observation matched
the Windows client cursor with the last WM_MOUSEMOVE coordinates and the
input object point. Five-second right-button floor orders then produced visible
destination markers and travel past the guard to the western corner; hover
identified the guard. Target positions also changed, so missed short polling
remains a hypothesis. No runtime semantics or original instructions changed.
The new dd5c0efb0e0d5edfcc557a833c9b7419ec69d5392e7744bf15e5a91d4abb26c3
quicksave is preserved separately and has not been reloaded. The live process
is tactically paused and hidden during the bounded original startup slot
through16:23UTC/early handback. Evidence:
`local/recomp/startup/mouse-polling-debug-latest.json` and
`local/recomp/startup/protected-provider-cache-west-corner-latest.json`.
The debug continuation reran376 Python tests with one skip in283.632seconds,
plus CMake/sixCTest/both demos with expected outcomes on the same macOS host. Evidence: `local/recomp/startup/relative-pointer-recovery-latest.json`
and `local/recomp/startup/protected-west-corridor-quicksave-latest.json`.

The new runtime caches only normalized native-provider basenames. Actual target
module lookup, translated-module exclusion and executable-page checks remain on
each call. DLL notifications invalidate names without retaining provider DLLs;
unavailable notifications and a saturated epoch use fresh queries. The loader
callback's compiled i686 body has no call instructions. Wine9/Rosetta controls
observed18 real unloads,17 same-address replacements and a synchronized
cross-thread replacement, in enabled and disabled-cache variants, with separate
filename queries, invalid-handle refusal and saturation checks. These are finite
native controls, not game or native Windows acceptance. Microsoft documents the
[loader callback restrictions](https://learn.microsoft.com/en-us/windows/win32/devnotes/ldrdllnotification).
The constructed baseline query loop measured about100ms for8,192 complete
identity checks versus7–8ms with filename processing omitted. This does not
measure the implemented cache or an integrated game speedup.

Whole linking retained63,612 compiled bodies and2,422,520 instruction entries;
the registry and generated runtime header match the preceding build byte for
byte. Only `native_abi.cpp` changed and `native_provider_identity.hpp` was added
to its frozen support sources. The LAA flag is carried into the new replacement
main as the same separately recorded one-byte variant. The new runtime SHA is
b070bda3156103aa12dde0bff2227be038cc684983c4989f28ea543d577775a8.
All376 Python tests completed with one skip on macOS ARM64/Python3.14.7; CMake,
six non-tooling CTests and both synthetic demos retained their expected outcomes.
Pointers: `local/recomp/startup/native-provider-cache-control-latest.json` and
`local/recomp/startup/native-provider-cache-build-in-progress.json`.
The new process subsequently wrote a stable11-file private quicksave after
westward travel. The saving toast cleared and the process remains live at an
observed tactical pause. Snapshot SHA8541fbf1b98cabd1ec227ad8b7f93af8b0314e07f88d4b73d84cf2459e62cd95;
this new snapshot has not been reloaded. Evidence:
`local/recomp/startup/protected-provider-cache-quicksave-latest.json`.
The cold-launch tooling check reran376 tests with one skip in325.033 seconds
on macOS ARM64/Python3.14.7, plus CMake/sixCTest/both demos with expected outcomes.
These infrastructure results do not establish game equivalence.

**The preceding build cold-loaded the preserved Cousland save and
responded to gameplay input.** Its now-terminal host33817/window41107, session41593 uses the same
replacement images in a qualified isolated Wine profile, without thread-context
sampling. Explicit menu selection loaded the earlier replacement-generated
quicksave (SHA699f19628a4055b5e5985ad4a7643037cab8b1c5eba935b6d504937af1a73dd3).
Captures bracket the returned HUD between178.2 and528.4 seconds after input;
this shared-host interval is not an isolated performance benchmark. A highlighted
door opened, the character walked into the corridor with a visible destination
marker, and F5 wrote a new quicksave into the owned Documents directory. Its
snapshot SHA is cc1a287733a85991687ac75186235311a856d8446113b102a491b26ed5e3284b.
The frozen input and baseline host quicksave remained unchanged. This establishes
the location of that save write, not an exhaustive audit of filesystem activity.
Exact restored-state equality, original-save compatibility, combat, area
transitions and a paired original/replacement scenario remain unverified.
Evidence: `local/recomp/startup/protected-cold-save-load-latest.json`,
`local/recomp/startup/protected-isolated-quicksave-latest.json` and
`local/recomp/startup/cold-save-checkpoint.json`.

**The previous extended run is terminal at an x87 comparison refusal.** Host49101
and session89929 ended with exit3 after9,616.892 seconds, timed_out=false. The
runtime reported `unexpected x87 comparison stack transition` at main PC0x7991cc,
RVA0x3991cc, original bytes `D8 D9` / `FCOMP ST(1)`, in owner RVA0x399130. Its
100B instruction budget retained29,386,244,765 units. This happened during a
bounded SuspendThread/GetThreadContext sampling experiment; whether sampling
affected FP state is unknown. The failed sampling process and its partial
observations are retained separately. The frontier logger did not capture the
pre/post x87 status, tags or payloads, so those inputs remain unknown. No guard
was removed. The frozen Cousland save that this replacement already reloaded is
now hash-bound as a shared scene input for a separate original-load experiment;
original compatibility and paired state equality are not yet observed. Evidence:
`local/recomp/startup/fcomp-frontier-checkpoint.json` and
`local/recomp/startup/shared-cousland-save-input.json`.
An isolated windowless control subsequently reproduced incorrect TOP even for raw
native `D8 D9` bytes when SuspendThread/GetThreadContext sampling was active. The
unsampled raw loop completed71,301,188 iterations and the unsampled existing
provider5,320,354 without a TOP failure. Sampled raw execution failed after two
samples; the sampled provider reproduced the same transition refusal after22.
These constructed finite masked-state observations implicate the diagnostic
procedure on Wine9/Rosetta; they do not reconstruct the missing live FP state or
prove game functions. Live context sampling is now excluded on this host. Policy
and frozen evidence: `local/recomp/startup/thread-context-sampling-unsafe.json`.
The unchanged-image cold-save experiment above follows this diagnostic finding;
it does not reconstruct the failed execution's missing FP inputs.

Live log monitoring now uses an append-only index rather than reparsing all
historical callback records every poll. It retains all nonrepetitive events,
exact counts, bounded repetitive tails and the complete raw log. Finalization
independently rehashes the entire file and refuses truncation, replacement or
prefix edits. Replaying the prior457,523,581-byte stderr preserved the exact
terminal frontier, every event count and the full-log SHA. This storage change
does not alter runtime semantics or grant behavioral acceptance. Replay evidence:
`local/recomp/startup/cold-index-old-log-replay.json`.

**Main menu and one menu interaction are now observed.** The frozen replacement
at `local/recomp/mac-callback-frontier-game/1794296968250698000` displayed the
Dragon Age: Origins main menu, then rendered Options after native mouse input.
The captured macOS window is bound to the staged replacement's host PID and
image hashes; no original-game window was captured. This is not gameplay or
scenario equivalence. Evidence: `local/recomp/startup/protected-menu-latest.json`.
The earlier menu checkpoint had no saves.
New Game has completed character creation using default Aedan Cousland, a male
human noble warrior, Quick Play and Normal difficulty. The larger-address build
has rendered the Human Noble opening conversation with working dialogue choices,
then the Castle Cousland gameplay HUD and tactical-view tutorial. Its initial
autosave and explicit quicksave completed; stable character/save snapshots and
hashes are preserved. Camera zoom, walking, a quicksave/reload cycle and post-load
door opening/walking into a corridor are observed. Combat, area transitions and
a matched original/replacement scenario remain unverified.
Evidence: `local/recomp/startup/protected-first-save-reload-latest.json`.

The in-process protection check records DEP3/permanent=true. A separate process
query records DEP1/permanent=false and read-only protection at original entry;
this query discrepancy is retained in the menu evidence. Native execute faults
and compiled callback returns remain observed. The original code namespaces are
linked as data/NX; these observations are not a universal Windows-host proof.


Latest linked build: **63,612 generated bodies**, 2,422,520 instruction addresses
and 582 imports. Two trap-path generation failures and53 bodies with partial
inventory-byte coverage remain explicit. Source hypotheses include shared
fragments; these counts are not accepted source-function counts. Generation:
`local/recomp/bulk/runs/1794303437453953000`; compilation:
`local/recomp/bulk-compile/runs/1794303668882038000`; current linked runtime:
`local/recomp/native-seh-entries/1794303437453953000`, SHA-256
`fff110f114b03443b981376d5042f47dde70edf110da13093dd40429b34f283d`.
An explicit large-address variant of this image is now running; its runtime and
Umbra bytes match this build exactly. Only byte142 of the replacement main image
differs (COFF flag0x20). Its main SHA-256 is
`130cca3fc86fbe886fa0c133670606110a6553c244de666af9d6f1296a548cc7`.
The pinned original main remains unchanged. Variant recipe/identities:
`local/recomp/startup/large-address-variant-latest.json`. CMake, six non-tooling
CTests and both synthetic demos passed on macOS ARM64. After the profile routing
fix, the373-test Python suite completed with one skip. The latest input/ledger
checkpoint repeated the project-environment suite in323.982 seconds, with the
same373 tests and one skip; six C++ checks and both demos also passed.

The previous extended playtest was
`local/recomp/mac-playtest/1794298338257196000` (Wine9/CX24+Rosetta), with a100B
per-entry instruction budget and2h observation limit. A second fresh-prefix
same-image launch reached the menu, New Game loading, its opening cinematic, and
a3D human character-generation preview after Escape. Character creation has now
completed on Normal and the first-area loading screen was observed. The game was
restored after a foreground handoff; its minimized0x0 client was restored using
normal window APIs. Guarded macOS CG clicks activated Quick Play and difficulty
confirmation; Wine SendInput observations alone showed hover. The game remained
alive while loading until its configured2h observation limit ended it at
7215.227 seconds, exit-9/timed_out=true. No startup/callback frontier was recorded;
this is not a spontaneous-crash observation. This
is not a playable-area/save-load result. All captures select only the
window whose owner is the known replacement host PID; original-game windows are
never captured. Current evidence:
`local/recomp/startup/protected-character-generation-latest.json`.

During that load, a bound remote VirtualQueryEx inspection measured2,025,541,632
committed bytes below2GiB,89,415,680 free bytes and a55,889,920-byte largest free
span. The executable lacked LARGE_ADDRESS_AWARE and the compiled runtime's mapped
image is about890MiB. This is a concrete address-space constraint; memory pressure
as the cause of the long load remains an inference. GetProcessMemoryInfo, I/O and
thread-time APIs returned success with zero counters on this host, so those zero
values are uninformative. Windows thread contexts did show changing compiled PCs;
sampled code included original-RVA `0xd3e30` and `0xbc450`. No loop diagnosis follows.
Evidence is retained under the prior run's `address-space-inspection.jsonl`,
`loading-thread-inspection.jsonl` and `loading-pc-symbols.json`.

The last extended replacement run was
`local/recomp/mac-playtest-large-address/1794305767559128000`, with a100B per-entry
budget and6h observation limit, Wine9/CX24+Rosetta, host PID49101/window40753.
It has reached the menu, opening cinematic, rendered character creation and
Normal Quick Play, then the rendered Human Noble opening conversation and dialogue
choices, then the Castle Cousland gameplay HUD and completed initial autosave.
An LAA-enabled inspector can query its
address map to4GiB, including about1.2GiB of additional contiguous free space at
startup. An inspector without that flag itself stops querying at2GiB; this caller
ceiling is retained rather than mistaken for the target's limit. Enabling the
flag is an explicit allocation-domain change, defined in the
[Microsoft PE specification](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format).
The new SEH code and a foreground handoff also differ from the c5 observation, so
this is not an isolated causal memory comparison or a high-pointer correctness
proof. Current checkpoint: `local/recomp/startup/large-address-playtest-checkpoint.json`.
Camera zoom, a paused move order, walking, an explicit quicksave/reload and
post-load door interaction are now observed. Captures bracket the reload's return
between273.5 and473.0 seconds after the recorded input. This was a shared-host
observation with brief thread sampling, not an isolated performance benchmark.
The HUD/character returned and responded to movement; exact restored world state
and reference equivalence remain unverified. The later cold-load observation is
recorded at the current frontier above. This older run's save is at the
normal macOS Documents location: this run's Wine active user is `crossover`, whose
Documents symlink was external. Earlier launch metadata checked only the inactive
`daeken` directory and did not establish profile isolation. The actual path and
stable save snapshot are in the autosave evidence above. The live profile was
left unchanged. Startup preflight now also checks both Wine Documents registry
routes and the recorded active-user expansion; it refuses both the source clone
and live mismatch. A separate freshly cloned profile has both routes set to the
owned directory and external Documents links detached without copying host
contents. Its native Wine9 shell-folder lookup and marker write reached that owned
directory, despite active `USERPROFILE` still being `crossover`. The qualified
fixture includes the preserved initial autosave for future cold-load scenarios.
Evidence: `local/recomp/startup/profile-route-control-latest.json`. The future
private launcher checks the live process before staging another copy and runs
the native folder probe in each fresh clone. No paired scenario equivalence
follows from these profile controls.

The current input controller is
`local/recomp/startup/shared-playtest-input.py`. Peer60069 has exited and its
signal authorization is explicitly revoked; current batches operate only on the
owned replacement. A new background original3105 has been reported but its
signal control has not been adopted. Each batch verifies the owned process and
window, obtains macOS foreground, and checks that input points are unobscured.
Exclusive presentation handoffs disable this procedure. Input receipts retain
the executed controller, agreement and frozen helper identities. Pointer actions first set the owned Win32
client cursor position, then post the guarded macOS event: a Quartz-only move
left the3D cursor on a previously hovered door in one observation. Native cursor
positioning restored movement toward the requested floor point. These are input
transport observations; game outcomes still require separate captured evidence.
Keyboard delivery now uses a guarded global HID event with a bounded hold rather
than direct-to-PID posting. Focus loss was observed during input diagnostics.
A hide/restore cycle temporarily exposed Wine's black fullscreen shield; raising
the exact owned accessibility focused window restored the game surface. Space
then removed the pause banner and a new tutorial panel appeared. This sequence
does not isolate which input/focus change was necessary, and is not evidence of
an instruction-semantics fix. Native probes recorded the owned window's active
focus, no held keys, and a one-second WM_NULL timeout; a short thread sample showed
varied compiled PCs rather than establishing a tight loop. Diagnostics are under
the live run's `input-state-initial/` and `thread-profiles/1794312919391170000/`.
After a later reference-run handoff, activation alone left the owned Wine window
offscreen even though Win32 reported it visible. A PID/window/executable-bound
Carbon show/front request activated49101; a normal hide/show cycle of only its
Win32 game window then restored the actual surface. AX and window-server checks
confirmed40753 onscreen with49101 foreground, and an owned capture showed the
same corridor HUD. No runtime or game-memory patch was used. The native action
receipt is `owned-window-visibility-cycle/report.json` under the live run; the
restored image is `after-visibility-cycle.png`. Peer3105's own application is now
hidden and its signal control remains unadopted.

An earlier candidate-only Wine9/Rosetta run was deliberately stopped after
679.082 seconds to enable more diagnostic logging. It recorded no missing target,
main return or explicit runtime frontier. Process sampling observed engine
update/render/streaming/worker threads and Wine's graphics thread; this does not
establish a visible frame or menu. Its inherited DragonAge log is byte-identical
to the source prefix and supplies no fresh startup evidence. Run:
`local/recomp/mac-literal-fixedpoint/1794294934559231000`.

An identical-image native-call trace was stopped at its capture limit after
50.576 seconds. It recorded repeated successful TryEnterCriticalSection/Leave
pairs and zero-timeout WaitForSingleObject polling; other workers were waiting
indefinitely on native events. These are measured calls, not a diagnosed deadlock
or a successful initialization. A smaller two-billion per-entry instruction
budget is now being used to locate the busy startup worker. Investigation:
`local/recomp/startup/literal-runtime-investigation.json`.

A subsequent two-billion callback budget stopped the startup worker at
`0x00419142`, immediately after the decrement in original refcount helper
`0x00419130`. This does not establish that the helper itself is looping or wrong.
The callback-failure path now invokes the existing bounded, read-only state
observer before its existing termination diagnostic, so the next capture includes
readable guest stack words and concrete register masks. Successful callback paths,
CPU state layout, original bounds and all generated bodies are unchanged.

Diagnostic linked runtime: `local/recomp/native-callback-frontier-state/1794296250000000000`,
SHA-256 `c5cdc1cbe5a328f02704241ebb6257a9afbbfcc244159579e4fc5e9f0c0ab2cb`.
All 361 Python tests passed with one skip in220.944 seconds on macOS ARM64;
CMake, six non-tooling CTests and both synthetic demos passed. The Windows i686
runtime compiled and linked; these checks do not establish game behavior. The
same-budget Wine9/Rosetta capture stopped at main `0x009350b3` with the expected
budget-exhaustion failure. The new observer recorded registers and16 readable
stack words. Three words coincide with original direct-call continuations
`0x0099c25a`, `0x0099d25f`, `0x009cb9bb`, bound to original CALL bytes. The current
helper is a hash-chain lookup; callers appear to handle script/property values.
Their high-level meaning and whether startup is looping remain unproven.
Evidence: `local/recomp/startup/callback-frontier-state-observation.json`.
The ten-billion-budget observation at
`local/recomp/mac-callback-frontier-game/1794296968250698000` subsequently displayed
the menu/Options and ended at its configured1200-second observation limit.

The latest independent instruction diagnostic covers every selection in the
pre-SEH63,612-entry catalog, including successful bodies. It checked 2,464,730
linear instruction occurrences and 349,417 module-specific exact byte encodings.
All 349,415 non-INT3 encodings emitted; only one INT3 encoding per module remains
unresolved. There were no undecodable tails in these ranges. The controller uses
bounded batches, rejects incomplete/duplicate catalog-result rosters, and retains
every occurrence in compressed reports. This establishes emission availability
for the selected ranges, not correct instruction semantics, arbitrary dynamic
code, exception delivery or full-game behavior. Audit:
`local/recomp/support-instruction-audits/1794302063926908000`.

Before the SEH pass below, a separate original-byte ledger covered57 partial
bodies, 10,817 of 11,018 uncovered owner bytes have instruction starts registered
elsewhere in the linked composition (using build-bound registry starts and
independent instruction lengths). Only 201 owner bytes lack such entries: 122 in
main and79 in Umbra. These include apparent exception filters/handlers, alignment
LEAs and detached jumps; these interpretations remain hypotheses, and overlapping
owner counts are not unique missing-code counts. Ten residual instruction entries
have original PE HIGHLOW references (six main, four Umbra), retained with exact
pointer-cell bytes for exception-metadata review. Of the56 combined-closure bounds
refusals,50 contain only INT3 bytes and six include instructions before a trap.
No contracts, bounds or guards were relaxed. The latest ledger pointer,
`local/recomp/startup/catalog-unknown-ledger-latest.json`, now identifies the
post-SEH refresh described below; these201-byte figures are historical.

Audit tooling checks ran on this macOS ARM64 host: 363 Python tests completed with
one skip, CMake built successfully, all six non-tooling CTests passed, and both
synthetic demos retained their expected positive/negative outcomes. Check logs and
input-bound reports: `local/recomp/startup/instruction-unknown-batch-latest.json`.

The canonical SEH4 metadata pass authenticates125 table prefixes /138 records
across both modules using original prolog bytes, HIGHLOW references and a
build-bound registry. It proposed ten missing internal filter/handler entries in
four existing envelopes. All four bodies now cover their declared bytes:63
instructions /174 bytes were added, with no earlier instruction removed and no
bound/annotation change. A whole-module direct/switch closure identified two
additional helpers (17 instructions /42 bytes), which now also emit, compile and
link. There are no extra generation failures. Discovery retained29 Umbra source
patterns without registered boundaries and one main handler outside known bounds.
Other prolog variants, C++ EH metadata and total table extents remain unknown.
Reports: `local/recomp/startup/seh-overlay-latest.json`,
`local/recomp/startup/seh-generation-preservation.json` and
`local/recomp/startup/seh-batch-in-progress.json`.

The remaining shared semantic batch is exception delivery and nonlocal unwinding:
authenticate exception metadata and handler entries across both modules, preserve
the original context/stack obligations at native boundaries, and support traps
without silently returning or resuming after noncontinuable exceptions. Keep this
separate from generation coverage and the ongoing save/load playtest.

A refreshed original-byte ledger now binds the currently linked SEH generation
and registry. Its53 partial envelopes contain10,844 bytes absent from their own
body coverage;10,817 of those bytes are already covered by registered instructions
from other envelopes. The remaining27 bytes comprise five3-byte `LEA ECX,[ECX]`
instructions and six2-byte unconditional branches. Each is immediately preceded
by an unconditional branch that bypasses it; the six Umbra branches duplicate the
preceding branch's destination. No HIGHLOW relocation in the scanned modules
references these11 residual instruction starts. These are static observations,
not exclusions: unknown dynamic entries and owner contracts remain unresolved.
The ledger also retains the earlier closure's rejected boundaries as historical
inputs, explicitly without claiming that closure was rerun. Evidence:
`local/recomp/catalog-unknown-ledgers/1794313343795062000/report.json` and
`residual-classification.json` in that directory. Candidate code was unchanged.

A separate batch rechecked every rejected canonical SEH source and unknown entry
against that same linked registry. All29 Umbra source patterns and the one main
handler lie outside current selection envelopes, with no registered instruction
start at those targets and no registered predecessor overlapping them. These30
entry hypotheses are a different scope from the27 residual bytes inside partial
envelopes; they must not disappear from missing-code accounting. The main handler
at RVA0x4e3609 decodes to an ESP restore, argument push and call followed by INT3.
Linear decoding does not establish its entry state, call outcome or complete
bounds. Original bytes, identities and the current registry comparison are frozen
under `local/recomp/startup/exception-source-audit-latest.json`. No selection,
exception contract, candidate code or acceptance status changed.

A combined direct/switch/materialized-address pass found one further Umbra body
and two shared prefixes. All three probes emitted and the whole-catalog build completed. The final
combined pass proposes no further bodies; 54 main and two Umbra trap/padding
bounds refusals remain, along with the main abort owner. This is closure over
those static origin classes, not arbitrary dynamic control flow. Repeated executable-literal discovery
previously proposed no additional bodies, retaining four main bounds refusals
and two ambiguous Umbra targets. Dynamic control flow and ambiguous bytes remain
unknown. Protected intro/menu/character-generation observations are recorded
above; subsequent first-area movement and local save/reload observations are
also recorded there. Combat, area transitions and paired scenarios remain unverified.

### Instruction support batch before the next game launch

The user requested a comprehensive instruction pass instead of another sequence
of reached-instruction fixes. Group every recorded failure across both modules,
implement complete families, then regenerate the complete catalog to expose any
further failures hidden behind each function's first error. No further game launch
is needed until this batch is ready. The user will observe visual progress;
original screenshots are not part of the next iteration.

The pinned baseline has 352 generation failures and 12 preparation failures.
`local/recomp/startup/remaining-support-inventory.json` binds every failure to its
binary/module/RVA, original bytes where an exact PC is reported, and generation
inputs. It is a complete grouping of recorded failures, not an exhaustive ISA/CFG
coverage claim.

- [x] Add scalar float-to-signed-int conversion support, including truncation and
  rounding variants. Constructed Wine9/Rosetta controls: 22 encodings, 4,224 physical
  comparisons, zero mismatches, 17 expected refusals, host FP state restored.
  This does not accept game functions; full-catalog regeneration is pending.
- [x] x87 extended stores and integer arithmetic: 89 first failures at FSTP m80;
  88 across FIMUL/FIDIV/FIADD/FISUB/FIDIVR/FISUBR m32. All m16/m32 forms
  and extended stores passed 202,176 constructed comparisons, 52 refusals and
  complete host FP restoration on Wine9/Rosetta. Fixture metadata allocation
  changed FP state in the first control; that failed evidence is retained and
  preparation is now isolated from measured instruction execution.
- [x] Remaining observed SSE move/conversion, min/max, reciprocal, reciprocal square root,
  square root, unpack and shuffle families.
  The first SIMD batch passed 289,536 comparisons across 754 encodings with
  zero mismatches and restored host FP state. A probe of every previously failed
  body now emits 218 of 352; 134 still fail, including additional MOVSS, CMP and
  logical forms previously hidden by first-error reporting. This is a diagnostic
  subset, not full-catalog compilation or function acceptance. Its 348-test,
  six-CTest and two-demo checkpoint is
  `local/recomp/startup/instruction-support-batch-1-checkpoint.json`.
- [x] Repeat string comparison/scanning: all 18 plain/REPE/REPNE CMPS/SCAS
  width8/16/32 forms now emit. Constructed Wine9/Rosetta controls passed 16,128
  physical comparisons in both directions; portable checks cover zero-count
  unknown inputs, partial budgets and retained fault prefixes. A reference ABI
  rejection of incoming DF1 is retained; raw reference wrappers set DF inside
  the instruction sequence and clear it before returning to C++.
- [x] Double shifts: observed SHLD/SHRD forms, including immediate versus CL
  encodings, 16/32-bit register aliases and zero-count memory write access.
- [x] Add providers for the observed x87 integer-flag comparisons, conditional
  moves, rounding, scale, remainder, transcendental and 32-bit environment forms.
  Pending/unmasked exception delivery and partial-fault environment writes remain
  explicit limitations; constructed masked-state agreement is not a proof.
- [x] Observed MMX and mixed MMX/SSE operations, including register aliasing with x87,
  EMMS, CVTPI2PS, packed arithmetic/logical/unpack operations and MOVD/MOVQ.
- [x] Observed XLAT, RDTSC and segment-selector stores; timestamps use the
  native counter and selectors use the current native x86 execution profile.
- [ ] INT3 breakpoint delivery and continuation semantics. It remains an explicit
  unsupported trap; no successful no-op or terminal-return stub was introduced.
- [ ] Authenticate bounds and entry contracts for the29 Umbra canonical SEH source
  patterns and one main handler outside current selections, as one discovery
  batch. Keep these separate from residual bytes within existing envelopes.
- [ ] Establish reachability/ownership for the11 residual instruction candidates
  within partial envelopes; static predecessor and relocation observations alone
  do not exclude dynamic entry.
- [x] Resolve observed decoder and owned-range/fallthrough diagnostics with
  original-byte evidence. Retain every original callable entry and all pre-entry
  shared regions; accepted contracts and source annotations remain protected.
- [x] Repeat full-catalog generation and contained guarded-switch recovery;
  retain concrete reports for the two remaining trap failures and partial bodies.
- [x] Compile/link every generated main/Umbra body, with explicit authenticated
  ownership for shared instruction addresses and no lost emitted body.
- [x] Classify the remaining trap paths from original bytes and isolated execution;
  establish readiness for an incomplete integrated startup experiment.
- [ ] Complete remaining trap/exception and partial-body contracts; continue
  integrated startup, menu, saves and gameplay with these gaps explicit.

The second support batch regenerated the **entire 42,492-entry catalog** with
**42,411 emitted bodies**, 69 generation failures, 12 preparation failures and
17 partially covered bodies. Every previously emitted body still emits. The
283 newly emitted bodies have not gained behavioral acceptance. All 42,411 emitted bodies compiled and linked with 2,339,376 registered
instruction addresses. No new game launch has occurred.
Generation is `local/recomp/bulk/runs/1794274470034150000`; compilation is
`local/recomp/bulk-compile/runs/1794275261604111000`. The linked runtime SHA-256
is `383ed4bbf89b73007e3540893695bf57f6c79785e0c41f8607cbc08fcc06919e`.

The new instruction audit scans every declared range of failed/partial selections
rather than stopping at the first unsupported statement. It examined 59,199
instruction occurrences / 17,433 distinct module byte encodings. The latest pass
retains 141 unresolved encodings plus 12 invalid selections; these include MMX,
x87 environment/conditional/transcendental forms, shifts, selectors, XLAT/RDTSC
and explicit traps. Linear candidates remain hypotheses, not complete CFG proof.
Audit: `local/recomp/support-instruction-audits/1794274257707909000`.

New SSE controls passed 34,560 comparisons across 90 encodings and 202,752 across
528 additional encodings. The all256 comparison-immediate experiment remains a
failed report (63,232 mismatches); eight defined legacy predicates are supported,
and higher comparison predicates explicitly refuse. Intel's
[legacy comparison encoding](https://cdrdv2-public.intel.com/812383/253666-sdm-vol-2a.pdf)
uses bits2:0. No Wine/hardware root-cause conclusion follows from that experiment.

All 352 Python tests passed with one skip in 227.876 seconds on macOS ARM64;
six CTests and both synthetic demos passed. A strict-backend PXOR regression was
fixed by retaining the existing generic zero-idiom path. An unchanged descendant
startup fixture and the complete suite were rerun after a timing failure. Failed
reports stay retained. Sources, producer snapshots and results are bound in
`local/recomp/startup/instruction-support-batch-2-checkpoint.json`.

The third batch implements the remaining observed instruction families together.
The final audit of the **same 59,199 occurrences / 17,433 module encodings** now
retains just `CC` / INT3 in each module, down from 141 unresolved module encodings.
The same 12 invalid selections remain unknown. Audit:
`local/recomp/support-instruction-audits/1794278955015088000`.
A retry of the original 352 failed bodies emits 344 and leaves eight untranslated
boundaries. Complete-catalog generation and linking are recorded separately.

Final constructed Windows i686 controls ran on **Wine9/CX24 + Rosetta, macOS ARM64**:

| Family | Encodings / sequences | Comparisons | Mismatches |
| --- | ---: | ---: | ---: |
| SHLD/SHRD | 344 | 272,128 | 0 |
| x87 math/classification | 12 | 129,024 | 0 |
| x87 FCMOV/FCOMI/FUCOMI | 96 | 1,769,472 | 0 |
| x87 environment save/restore | 4 | 3,072 | 0 |
| Selectors, XLAT and RDTSC intervals | 92 | 47,104 | 0 |
| MMX, SSE conversion and composed sequences | 977 | 750,336 | 0 |

The unique-output control bundle is
`local/recomp/instruction-batch-3-controls/1794278799340016000`.
It also passes 48 MMX unknown-state checks / eight refusal guards, 32 protected
native-to-compiled MMX callbacks, and the unchanged 17-entry callback baseline
with nested/native calls, a new thread, twelve live x87 cases, all XMM values,
last-error preservation and its existing refusal guards. These are constructed
controls, not recovered-function or playable-game acceptance. The counter control
checks an observed native interval rather than pretending independent timestamp
reads should be equal.

A composed MMX check exposed a real blind spot in the initial single-instruction
controls: on this measured Wine/Rosetta build, neither FNSAVE nor FXSAVE records
MMX register changes. Raw MOVQ observations retained the changed values while both
saved images retained the old x87 payloads. That measurement is retained in
`local/recomp/startup/mmx-physical-image-probe-latest.json`; the initial controls
are provisional and superseded. Production transport now explicitly captures and
restores MMX on that measured host profile, including imports and protected
callbacks. A runtime calibration distinguishes this from the architectural
[MMX/x87 aliasing profile](https://cdrdv2-public.intel.com/812386/253668-sdm-vol-3a.pdf),
which continues to use physical x87 aliases. Unknown operands remain unknown;
zero idioms establish only their actual destination. The architectural branch
has not run on native x86 Windows hardware here.

SHLD/SHRD also required retaining the exact immediate encoding: substituting CL
changed observed undefined flags on this host. The initial mismatch report is
retained. The final control includes all 256 CL values and representative immediate
values, and preserves the measured zero-count memory read/write access.
Environment controls do not qualify pending exceptions or partial-page fault
ordering; those paths cannot become behavioral passes from this evidence.

The completed third batch emits and links **42,501 / 42,503 catalog hypotheses**.
It retains all 42,411 previously emitted bodies, adds 90 bodies, and keeps every
previous instruction identity in changed bodies. Two deliberate INT3 paths remain
unemitted (main RVA `0x4e7f01`, Umbra RVA `0xcdd6b`); no successful trap stub or
original-execution fallback was added. Sixteen emitted bodies have partial
per-body coverage. None of these counts is recovered-function acceptance.

The twelve former preparation errors came from static body regions preceding
function entry. The repair preserves those regions under explicit lower decode
roots and preserves each original entry, rather than discarding pre-entry code.
Five truncated bodies now include their byte-adjacent compiled continuations;
one prologue extends through its original allocator branches and RET before INT3
padding. Three guarded HIGHLOW-bound switch proposals materialized new cases
inside unchanged ranges. A second whole-catalog contained-switch pass proposes
zero further changes. Bounds and switch descriptors are respectively
`local/recomp/complete-bound-overlays/1794281433722223000` and
`local/recomp/contained-switch-overlays/1794282180480675000`.

The instruction audit additionally inspected all original ranges from invalid
selections without accepting their envelopes: **60,392 occurrences / 17,775
module encodings**, including 1,193 previously skipped occurrences. INT3 remains
the only unresolved byte encoding in each module; the invalid selections stayed
unknown in that diagnostic report. Audit:
`local/recomp/support-instruction-audits/1794280842758584000`.

All 42,501 emitted bodies compiled for Windows i686 and linked with 2,348,042
unique instruction addresses. The new MMX state required a complete 42,472-body
rebuild (2,780.596 seconds); final bounds/switch changes rebuilt 31 objects in
17.049 seconds. The shared-PC plan explicitly authenticates all 814 overlapping
instruction addresses against original bytes and exact candidate/source metadata;
every function stays compiled and registered. Default duplicate ownership still
refuses. Plan: `local/recomp/startup/instruction-batch-3-final-ownership-plan.json`.

The final **357-test Python suite passed with one skip in 586.126 seconds** on
macOS ARM64 / Python3.14.7. Six CTests and both demos passed (59 agreements;
negative control 53 agreements / six expected mismatches). An intermediate
356-test run missed the unchanged descendant-start marker within its existing
120ms timeout during the full rebuild; that failed log is retained, no fixture or
threshold was relaxed, and the final complete suite passed. Current checkpoint:
`local/recomp/startup/instruction-support-batch-3-checkpoint.json`.
The linked runtime SHA-256 is
`a904f325d1b2c860a4685f0e4a6d09daf77f07bffee1eb6c2d6a55d9f211e3f4`.
That build checkpoint preceded its first game launch. A subsequent candidate-only
Wine9/Rosetta experiment is recorded under
`local/recomp/mac-instruction-batch-3/1794285303678897000`; inspect its live/final
report for the actual outcome. No original game or screenshot is needed for this
experiment. Protected intro, menu, save loading and gameplay remain unverified.

That candidate-only run ended with controlled incomplete exit3 after 84.988 seconds.
Permanent DEP flags3/permanent=true was observed. It recorded no new unsupported
instruction frontier; a fresh worker callback at original entry `0x004e6180`
exhausted its one-billion-instruction budget at `0x004c4d12`. The stopped PC is
inside a lock helper; it does not establish a repeated-loop history or prove
deadlock. The same compiled build is being examined with compressed native-call
tracing before changing the budget. Observation checkpoint:
`local/recomp/startup/instruction-batch-3-whole-checkpoint.json`.

The same-build traced repeat ended at another worker PC, `0x008f778d`, after
114.972 seconds with the same one-billion budget exhausted. Its complete compressed
call trace contains 15,426,493 ABI entry/exit records. The main thread is awaiting
event168 indefinitely; the active worker executes varied CRT/numeric work and
lock calls, while a separate thread polls the same event and its message queue.
This does not establish correct progress or a deadlock. Trace/report:
`local/recomp/mac-instruction-batch-3-trace/1794285516360852000`.
An experimental ten-billion budget run of identical images starts from another
clone of the same prefix under `local/recomp/mac-instruction-batch-3-long/1794285685567568000`.
The budget change is diagnostic; exhaustion, timeouts and missing semantics still
cannot pass. No production runtime, trap guard or accepted fixture changed.
That larger-budget run ended after 105.076 seconds with controlled incomplete
exit3 at missing indirect target `0x00910c80`, called from `0x0091d4b9`.
Original ordinary-data RVA `0x816e4c` stores that exact address with HIGHLOW
provenance. It is an isolated registration omitted by the former consecutive
pointer-run filter, and is absent from the pinned function inventory. The next
batch audits all sparse/isolated relocated code pointers across both modules,
with owned-range and bounded-decode refusals retained. This is a catalog gap,
not evidence of a new unsupported instruction. No game acceptance follows.

The complete ordinary-data HIGHLOW audit includes isolated code pointers, not
only consecutive runs or RTTI tables. It found 20,542 unowned main targets and104
Umbra targets. Bounded recursive decoding proposes 19,981 main /60 Umbra bodies
and refuses561 /44 respectively. These include exception-handler fragments and
are not an accepted source-function count. Every proposed range was checked for
overlap against the full existing catalog and other proposals; existing selections
were retained. Audit: `local/recomp/sparse-pointer-audits/1794285896631482000`.
The overlay `local/recomp/sparse-pointer-overlays/1794285990220617000` completed
whole-catalog generation in `local/recomp/bulk/runs/1794286062167616000`:
62,542 emitted bodies, the same two trap failures, zero preparation failures,
and the same16 partially covered bodies. All20,041 new proposals emit; no prior
emitted body was lost. Compilation is running separately.

All 446 fallthrough refusals were then probed as explicit shared continuations.
Each new root retains its original relocated pointer, byte-adjacent prefix and
an authenticated emitted instruction boundary in an existing owner. The proposal
copies forward original ranges into the new hypothesis; existing selections and
guards remain unchanged. All446 probes emit (418 main /28 Umbra). Shared-PC
ownership still requires the original-byte/input-bound plan before linking.
The first publication attempt had a duplicate-key Python error after probing;
its failed log is retained, the publisher was corrected, and the immutable probes
were reused. Overlay: `local/recomp/sparse-continuation-overlays/1794286506331127000`.
Its full regeneration `local/recomp/bulk/runs/1794286570660823000` emitted 62,988
bodies, retained both trap failures and recorded 24 partial-coverage selections.
Every old selection remains unchanged. The remaining 159 sparse-origin bounds
refusals comprise 125 trap/padding paths, 32 nonlocal interrupts, one undecodable
boundary and one instruction-interior branch. They remain unresolved.
Compilation, linking, closure and behavioral validation remain separate work;
no further game launch is needed until this batch is ready.

All 62,542 bodies from the initial sparse batch compiled for Windows i686 in
552.019 seconds, with zero compiler errors. Build report:
`local/recomp/bulk-compile/runs/1794286418941143000`.
The subsequent combined original-byte closure follows relative direct edges,
guarded/compressed switches and relocated MOV/PUSH/absolute LEA origins in one
controller. It proposes 279 main /11 Umbra bodies with 2,424 original instructions
and retains 169 bounds refusals. Existing owners and acceptance guards remain
unchanged. Its composed scanners, controller and metadata bindings are preserved
under `local/recomp/sparse-combined-closure-overlays/1794286830374974000`.
Whole-catalog generation of those proposals is running. The six required CTests
and both synthetic demos passed on macOS ARM64; a fresh full tooling suite is
running separately. These checks do not validate the generated game functions.

The combined closure generation `local/recomp/bulk/runs/1794286973703578000`
emitted 63,274 bodies and exposed FTST in four new CRT helpers (main RVAs
`0x4f4d20`/`0x4f4d6e`, Umbra `0xd54e0`/`0xd552e`). The two original trap failures
remain. A complete failed/partial-selection instruction audit found only FTST
and INT3 unresolved: `local/recomp/support-instruction-audits/1794287247181998000`.
Shared emission/structure handling and the native x87 provider now support the
exact FTST opcode `D9 E4`; stack/tag knowledge and integer flags are retained.
The expanded 13-operation constructed x87 control ran under Wine9/CX24 + Rosetta
on macOS ARM64: 139,776 comparisons, zero mismatches, eight refusal checks and
eight unknown-empty cases, with host FP state restored. It does not qualify
pending/unmasked exception delivery or accept game functions. Evidence:
`local/recomp/x87-math-ftst/1794287380000000000/evidence.json`.
The shared generated-state header is byte-identical, allowing object reuse.
The pre-FTST full Python suite passed 357 tests with one skip in 239.012 seconds;
the post-change full suite also passed all 357 tests with one skip in 279.133
seconds on macOS ARM64 / Python3.14.7. Whole-catalog regeneration under the new
backend is running; the generated-state header remains unchanged.

The 113 remaining composed-closure fallthrough prefixes also emit under the new
backend. The materialized original label `0x0040a67d` is now an explicit decode
root in its existing unaccepted owner (`0x0040a64c`), with every prior original
instruction retained. The abort entry remains unresolved. Proposal overlay:
`local/recomp/sparse-closure-continuation-overlays/1794287651758870000`.
A guarded controller waits for the existing cold generation, rebases the new
overlay's module-metadata provenance, and then regenerates, compiles, authenticates
shared-PC ownership and links the final batch. It stops for unexpected failures
or source changes and does not launch the game. Live state:
`local/recomp/startup/sparse-batch-finisher-latest.json`.
Current checkpoint: `local/recomp/startup/sparse-ftst-batch-checkpoint.json`.
The latest actual game observation remains the 42,501-body run; these expanded
artifacts have not yet run the game. Protected intro/menu/save/gameplay remain
unverified, and the full playable-replacement goal remains active.

The post-FTST audit of all formerly failed/partial ranges finds only INT3
unresolved in each module: 2,555 original instruction occurrences /1,083 module
encodings, with no undecodable tails. This remains scoped instruction diagnostics,
not a full CFG or function-equivalence claim. Audit:
`local/recomp/support-instruction-audits/1794288335534405000`.
The full new-backend generation `local/recomp/bulk/runs/1794287452157044000`
completed with 63,278 emitted bodies, the same two trap failures and 24 partial
selections. The controller is now generating the final shared-continuation overlay
using that matched backend's module metadata, before compilation and linking.

The completed sparse/FTST batch linked **63,391 bodies /2,415,915 instruction
addresses**. Its source compiler rebuilt only849 objects in76.677 seconds; all
62,542 prior compiled source hashes remained unchanged. An explicit original-byte
plan authenticated18,005 shared instruction addresses. Both images retained
nonexecutable original sections, and required core checks/demos passed. Build:
`local/recomp/native-sparse-ftst/1794288493275904000`.
The final direct/guarded-switch/materialized-address pass proposed no further
bodies; that is closure over those static origin classes, not arbitrary dynamic
control flow.

The candidate-only Wine9/Rosetta run then stopped after190.137 seconds with exit3
at unregistered internal target `0x005be94d`. Permanent DEP flags3/permanent=true
was observed. Its pinned source is the HIGHLOW word at main RVA `0x1bebb4` in
executable `.text`, containing bytes `4de95b00`. This dispatch data was excluded
by ordinary-data pointer scanning, and its table was not recognized by the
guarded-table analysis. No new unsupported instruction was reported. Actual run:
`local/recomp/mac-sparse-ftst/1794289134948808000`.

The new executable-literal scan authenticates relocation words outside emitted
instructions, with explicit source/target ambiguity and literal-storage guards.
It does not infer table index bounds or callable signatures. Across both modules
it proposed119 bodies, all of which emitted. Associated shared-continuation and
label probes preserve every prior instruction in the two changed owners; one
candidate that decodes literal storage remains deferred. Full tooling checks
passed361 tests with one skip in201.739 seconds on macOS ARM64 /Python3.14.7.
New dispatch/header/source-boundary fixtures remain infrastructure evidence.
Initial literal overlay: `local/recomp/literal-pointer-overlays/1794290027998208000`.

The literal-expanded build now links63,584 bodies /2,421,926 instruction addresses
under `local/recomp/native-executable-literals/1794291696988396000`; it has not run
the game. A repeat literal scan proposes zero further bodies while preserving
four main bounds refusals and two ambiguous Umbra targets. Combined direct closure
exposed13 small Umbra bodies plus10 associated shared prefixes. Their probes
emitted, and the resulting 63,607-body catalog compiled and linked successfully.
Six non-tooling CTests and both synthetic demos passed on macOS ARM64. Its final
combined scan found one more Umbra body and two shared prefixes; those three
probes also emit. The next overlay is
`local/recomp/literal-fixedpoint-continuation-overlays/1794294470117777000`. Original source/body/ownership guards remain unchanged.
Protected intro, menu, saves and gameplay remain unverified.

The remaining original traps follow exceptional paths. Main's exit chain reaches
ExitProcess; an isolated raw exit leaf terminated its Wine process with the supplied
code. Umbra's raw throw helper raised exception `0xe06d7363`, flags1, with three
parameters. Its measurement handler stopped execution at that event, so this does
not validate unwinding or prove every invocation cannot return. Negative fixture
imports deliberately returned and exposed the original breakpoint in both cases.
All four isolated observations matched their expected process outcomes on
Wine9/CX24 + Rosetta, macOS ARM64. Evidence:
`local/recomp/termination-leaf-controls/1794284899320507000`.
Both generation failures remain unresolved; no trap guard, exception contract or
successful return stub was relaxed. These observations justify an incomplete
integrated experiment, not function acceptance. The playable-replacement goal
remains active.

`tools/recomp_direct_transfer_discovery.py` authenticates original direct calls,
branches and missing fallthrough/return continuations using independent decoding
and relative target arithmetic. Bounded closure produced 90 disjoint fragment
proposals; 85 emitted and compiled, while five new generation failures remain
explicit. All previously emitted bodies still emit. There are 152 bounds refusals
and 176 targets inside existing ownership without registered instructions; neither
is treated as recovered. Existing selections, annotations and contracts stayed
intact. The full Python 3.14 suite passed 343 tests with one skip in 217.029 seconds;
CMake, six non-tooling CTests and both synthetic demos passed on macOS ARM64.
Executed producers and observation bindings are retained in
`local/recomp/startup/direct-transfer-whole-checkpoint.json`.

The previous switch-owner pass proposed 58 unaccepted owner corrections, adding
3,151 instructions and 9,127 code bytes without extending envelopes or changing
accepted/reviewed contracts. It cleared the compressed case at 0x0085c07d;
skipped alignment remained excluded. Those corrections and their 336-test
checkpoint are retained in `local/recomp/startup/case-coverage-whole-checkpoint.json`.

`tools/recomp_instruction_pointer_discovery.py` finds original code addresses
materialized by full-width MOV/PUSH immediates and absolute LEA, with HIGHLOW and
independent decode checks. It excludes dereferences and arithmetic. A bounded
closure follows addresses found in new body hypotheses; budget exhaustion cannot
publish a completed overlay. This produced 5,740 main and 274 Umbra proposals;
6,010 emitted and compiled, while four new generation failures remain explicit.
Two main bounds refusals also remain unresolved. Executable storage can contain
data, so these are entry hypotheses rather than accepted callable functions.
Original ranges and annotations were preserved. This clears 0x00863520, whose
address an original instruction at 0x008635a1 stores into a runtime callback table.

The full Python 3.14 suite passed 329 tests with one skip in 170.464 seconds;
CMake, six non-tooling CTests and both synthetic demos passed on macOS ARM64.
Exact producer/input identities and the bounded native observation are recorded
in `local/recomp/startup/instruction-pointer-whole-checkpoint.json`.

`tools/recomp_switch_discovery.py` authenticates guarded jump-table prefixes in
generated original instruction metadata, including executable-section tables.
It found 251 main tables and four Umbra tables. Of 134 unowned main targets,
120 yielded disjoint case-fragment proposals with 896 original instructions;
14 bounds refusals remain explicit. All 120 emitted, compiled and linked.
Existing function ranges and annotations were preserved. This includes the
reached 44-byte case at 0x004619ef, excluded from the original function inventory.
The remaining unsupported bodies and unrecognized table forms stay unknown.

The final Python 3.14 suite passed 323 tests with one skip in 175.361 seconds;
CMake, six non-tooling CTests and both synthetic demos passed on macOS ARM64.
The input-overlay guard was tightened to prevent accidental loss of prior
selections; a complete read-only replay produced byte-identical role selections
and proposal reports. Executed producer snapshots and that replay are bound by
`local/recomp/startup/switch-discovery-context.json`. No game acceptance follows.

The new discovery tool, `tools/recomp_pointer_discovery.py`, fixes two systematic
selection failures. Raw resource pixels no longer masquerade as code pointers:
pointer sources require real HIGHLOW relocation entries in ordinary data. Short
virtual tables additionally use linked MSVC32 RTTI evidence instead of requiring
three consecutive code pointers. The locator, type descriptor, hierarchy and
base-array links are checked against pinned bytes and relocation sources. The
RTTI layout reference is [Wine's 32-bit definitions](https://raw.githubusercontent.com/wine-mirror/wine/wine-9.0/dlls/msvcrt/cxx.h).
This identifies 2,093 main-module and 68 Umbra type-descriptor identities, with
original mangled names and subobject offsets. It does not establish complete
field layouts, source signatures or behavior.

The reached 0x00874f00 texture method was absent because its interface has only
two entries. Its RTTI identifies `.?AVD3DTexture2D@D3DDriver@@` and subobject
offset 4; the original body accesses the complete object through `this - 4`.
The updated catalog includes this method and the earlier 0x00868420 method.
Progress to the new stop is consistent with resolving those missing entries;
it is not an independent function-equivalence result.

The full project Python 3.14 suite passed 317 tests with one skip after these
discovery changes. Focused regression cases cover resource pixels, missing or
malformed relocations, instruction ownership, discovery budgets and broken RTTI
chains. Repository CMake/demo evidence and exact source bindings are recorded in
`local/recomp/startup/in-progress.json`.

The current backend revision adds all five missing x87 constant loads (`fldpi`,
`fldl2t`, `fldl2e`, `fldlg2`, `fldln2`) alongside the existing `fld1`/`fldz`.
Emission checks the original opcode; the native provider executes the selected
instruction with extended precision and the recorded rounding mode. It retains
explicit refusal for unsupported unmasked exception delivery. Constructed controls
on Wine 9/CX24 + Rosetta observed 4,032 cases with no mismatches across all TOP
positions, precision/rounding controls, empty/partial/full stacks and masked
sticky exceptions; four refusal guards passed and host FP state was restored.
This is provider debugging evidence, not original-function or game acceptance.
Inputs and the execution report are under `local/recomp/x87-constants/`.
The complete-catalog generation, compilation, linkage and bounded startup
observation completed; three previously refused bodies now emit and compile.
The full Python 3.14 suite passed 318 tests with one skip in 204.861 seconds;
CMake, six non-tooling CTests and both synthetic demos passed on macOS ARM64.
These remain separate from the Wine/Rosetta startup evidence above.

### Host and inventory investigation history

Wine + Rosetta on macOS ARM64 is the primary development target; current paired
observations use the separately retained Wine 9/CX24 build. The user's
direction is to diagnose replacement-only failures on our side, rather than
switch execution hosts to bypass them. FEX/QEMU results below are historical
secondary evidence, not the active development queue.

A matched original/replacement experiment used independent clones of the same
Wine prefix snapshot, identical retained DLLs/assets and the same staged path.
The original remained running through its 60-second observation; its trace
includes Direct3D initialization and rendering calls, with no access-violation
records. This is not a verified menu or gameplay milestone. The replacement
stopped after 44.596 seconds: a native read fault preceded an uncompiled MSVC
exception-handler thunk at 0x00a820f4. The earlier fault is the issue to diagnose;
adding the handler would not explain it. Reports are under
`local/recomp/mac-whole-comparison/1794255478567114000`.

A native-call trace placed the first read fault inside `Direct3DCreate9(32)`.
Constructed direct-call and native-bridge controls produce different outcomes
depending on layout and logging, including faults without the bridge. They do
not establish a root cause or game acceptance. The diagnostic source is
`recompiler/experiments/native_d3d_startup.cpp`; frozen reports are under
`local/recomp/native-d3d-startup/`.

With Wine's internal tracing disabled, the same replacement images ran 51.110
seconds and instead stopped explicitly at missing main code 0x00413900, called
through virtual-table slot +0x2c at 0x00414a5d. No earlier native data fault was
recorded by the runtime's exception logger. The target has no current inventory
owner, and the pinned table contains its actual original address. This exposes a
systematic inventory gap, not an unsupported instruction in an existing body.
A static scan of non-executable data runs with at least three consecutive code
pointers found 5,134 distinct unowned main-module targets, including this one.
These are discovery hypotheses; their function bounds, signatures and behavior
remain unknown. The run is
`local/recomp/mac-whole-comparison/1794258141057628000`; the scan is
`local/recomp/startup/unowned-vtable-targets.json`. The earlier fault is still
unresolved; changing logging is not a repair.

A repeat quiet comparison kept the original running through a 65-second bound,
but the replacement exited 5 after 46.530 seconds without a final frontier/main
record. Treat this as an incomplete abnormal observation, not a successful run.
That pair is `local/recomp/mac-whole-comparison/1794258331733709000`.

Further loader probes are under `local/recomp/mac-passive-runtime/`. Adding a
passive import of the runtime to the original reproduced the native read fault;
inert DLL and import-table-only controls also failed. Crucially, the probe's
**unmodified original** control (`1794258876689332000`) also exited 5 during
graphics startup, with a native 64-bit exception and a 32-bit stack address.
Its main image SHA-256 is still the pinned original and the runtime was not
loaded. Those probes use different logging/path/environment details from the
earlier matched pair. They therefore establish neither a runtime-footprint
cause nor a replacement-only bug. Stabilize the original in the exact comparison
setup before attributing the failure. No Wine, compiler, generated-code or ABI
root cause has been established, and no graphics workaround has been applied.

Fixed-path serial controls now confirm that Wine 11.0 and 11.21 can also fail
with the untouched original on this Mac. In the 11.0 control, one quiet original
run survived 20 seconds and the next quiet original run exited 5 after 1.927
seconds, with the same paths, prefix snapshot and launch environment. On 11.21,
one of three quiet original runs exited 5; both versions also ran the replacement
to the explicit missing-method stop at 0x00413900. These observations are under
`local/recomp/mac-canonical-graphics/1794259126860688000` and
`local/recomp/mac-canonical-graphics-11.21/1794259248901386000`.
An [upstream Wine report](https://list.winehq.org/hyperkitty/list/wine-bugs@list.winehq.org/thread/FQ2G55RFO6OZMTLHY66TDCNIH2VZKH6X/?sort=date)
describes a closely matching intermittent WoW64 transition fault under Rosetta.
It is unconfirmed; its matching fault pattern supports a host-transition
hypothesis but does not prove the cause of our failures.

A separately installed public Wine 9/CX24 engine remains on Mac + Rosetta. Its
installation and exact third-party host-library bindings are recorded in
`local/recomp/startup/wine-cx24-install.json`. Three quiet original runs survived
20-second bounds; a fourth survived 90 seconds and logged graphics shader
activity. No menu/visual milestone was verified. The older replacement reached
main and timed out at 65 seconds, so this is not a crash repair or game result.
See `local/recomp/mac-canonical-graphics-cx24/1794259811250366000` and
`local/recomp/mac-cx24-reference-visual/1794260031656830000`.

The code-pointer scan now has conservative disjoint traversal proposals for
4,511 previously unowned targets (70,814 independently decoded instruction
boundaries); 623 others remain rejected or uncertain. Each proposal binds the
original module hash, RVA, raw slice hash and data-pointer sources. Decoding stops
before existing ownership or another proposed entry; unresolved indirect/external
transfers and unknown signatures/behavior stay explicit. Projects, accepted
contracts, oracle fixtures and the recovery registry were not changed.

The expanded generation attempted all 36,002 catalog entries: 35,659 emitted
bodies, 331 generation failures, 12 preparation failures and 14 emitted bodies
with partial inventory-byte coverage. All 35,659 emitted bodies compiled and
linked into replacement main/Umbra images, registering 2,204,677 instruction
addresses and 582 imports. The missing 0x00413900 method emitted all 62 decoded
instructions / 160 bytes and compiled; execution of it remains to be observed.
Evidence is `local/recomp/bulk/runs/1794259360111808000` and
`local/recomp/bulk-compile/runs/1794259581769918000`.

Discovery overlays use the existing startup-selection transport. The catalog now
preserves their `static_code_pointer_hypothesis` provenance instead of labelling
them reviewed startup selections. A new full generation is running to publish
that corrected metadata; the linked executable above predates this label fix and
has no behavioral acceptance. The tooling suite ran 311 tests with one skip on
project Python 3.14; CMake, six native CTests and both synthetic demos passed.
The system Python 3.15 invocation separately failed for missing Unicorn and is
retained as a failed environment run, not counted as a pass.

### Historical published partial-build checkpoint

<!-- native-checkpoint:start -->
The last published checkpoint has 3,868 compiled functions. Its frozen run
completed translated Umbra attachment, entered main, and stopped explicitly at
missing main code 0x0087d9c0 after 41.824 seconds. This run uses FEX for the game
process and corrected QEMU for the same Wine 8 i386 server binary. Original
main/Umbra instruction pages remain non-executable, and permanent DEP is required
before translated entry. Function signatures, layouts and behavior remain
unaccepted startup hypotheses; no recovery-registry acceptance was added.

Five original indexed switch graphs in existing selections are now complete:
two helpers at 0x008652b0/0x00865310 and three inline tables in 0x00866e00.
Their 70 byte-index slots and all 2,142 owned instruction bytes were checked
against the lift. Missing cases previously escaped to the global dispatcher.
The new 47-byte 0x0086bc90 method and its already-selected direct helpers also
compile. Existing annotations and original bytes were preserved.

The FEX canary message was isolated to a separately captured foreground Wine
server. Running that identical server binary under corrected QEMU lets the FEX
game process reach ordinary missing-code stops. A matched older-image control
reached 0x008652d0 in 50.804 seconds; pure QEMU reached the same stop in 472.309
seconds. A second image pair reached 0x00867176 in 48.872 seconds on the composed
host and 346.596 seconds on pure QEMU. These are specific startup observations,
not a general performance benchmark or game-equivalence result. The FEX server
failure's root cause remains unknown; the failed runs, diagnostic trace and
matched controls are retained.

Mac Wine exception-dispatch faults and FEX's measured x87 instruction/data-pointer
limitations remain recorded. The unchanged constructed callback fixture had
passed 17 entries, 12 live x87 cases, all 128 live XMM bytes and 14 refusal guards
on Mac Wine, corrected QEMU and FEX. Budget-one fresh-thread controls refused on
all three. These bounded controls do not establish native Windows or game
acceptance. This turn's repository checks passed: 291 Python tests (one skip),
a CMake build and six non-tooling CTests, and both synthetic demos.

Protected replacement splash pixels were captured on the earlier 3,825-function
QEMU build; the 3,866-function splash was also observed. Protected replacement
intro playback, menu, save loading and gameplay remain unverified. The pinned
original independently rendered its intro on QEMU. Historical user-reported intro
ownership remains unknown; at the later Mac inspection the live Alkyhol process
was running the pinned original main executable and original Umbra.

Published evidence: `local/recomp/startup/checkpoint.json`.
Newer work: `local/recomp/startup/in-progress.json`.
Linux and composed-host observations: `local/recomp/startup/linux32-host/` and
`local/recomp/startup/fex-host/`.
<!-- native-checkpoint:end -->

Current next actions:
1. Add the missing x87 constant-load family through the existing native value
   provider, beginning with the reached `fldpi`. Check exact original encodings,
   rounding/control/status/tags and host-state restoration. Preserve pending
   exception refusals or model delivery explicitly; do not replace constants
   with approximate C++ literals or silently mask exceptions.
2. Regenerate the whole current main/Umbra catalog, compile/link all emitted
   bodies and repeat the frozen Mac/Rosetta startup comparison. Keep unresolved
   instructions, direct-call closure, exception metadata and uncertain ownership
   explicit. Do not add one-off success stubs or switch CPU hosts around failures.
3. Reach a Direct3D device and menu, compare initialized original/replacement
   scenarios, then load a save and exercise gameplay and transitions. Bind visual
   milestones to the actual replacement process and exact executed image hashes.


## Work policy

- Generate the whole main/Umbra target and fix systematic failures across it.
  Use actual startup and gameplay failures to debug the resulting replacement.
- Add focused checks when needed to debug a failure. Run repository-required
  tooling/CMake/demo checks after changes, without repeatedly broadening them.
- Unknown code, CPU/ABI semantics, exhausted budgets and
  initialization failures remain explicit failures; never successful stubs.
- Keep game bytes, generated code/data images, captures and run reports in ignored
  local/ or gamedata/. Preserve existing annotations and unrelated working edits.
- Maintain the frontier report and next action below when changing direction.
- Windows production uses native memory and the native x86 ABI. Do not add
  per-API marshalling/ownership wrappers to advance the playable build. Keep the
  checked/symbolic memory backend as an explicit validation profile.

## Native Windows execution (active)

The user explicitly chose a basically native replacement. The checked memory
backend had been requiring API-specific shadow-state bookkeeping; that is no
longer the production architecture or the work queue.

- [x] Implement one generic x86 ABI transport: real registers, flags, x87/XMM,
  last-error and observed callee stack cleanup. No per-function argument count,
  pointer codec or return-type conversion is required.
- [x] Exercise cdecl/stdcall/fastcall/thiscall, EDX:EAX and raw x87 returns,
  native heap/file pointers and a nested native callback. The prototype made
  18 calls under Wine. Its callback is native fixture code, not game code.
- [x] Add NativeX86Memory with physical Windows x86 memory accesses, without
  allocation/output shadow registries. Its address-space contract is explicit;
  portable guest fixtures remain separate. Unresolved symbolic inputs are refused.
- [x] Execute a translated constructed x86 caller through a normal native import,
  raw GetProcAddress target and native vtable-style function. Consume a native
  x87 return using translated instructions; access unregistered native heap
  storage, including unaligned reads/writes. No per-API ownership wrapper ran.
- [x] Make generated Windows builds use native execution by default. The native
  production build excludes the per-API dispatch body. Select
  `build --windows --execution-profile strict` for the validation backend.
- [x] Build native replacement DAOrigins.exe/Umbra.dll with original data RVAs,
  real PE imports/resources/static TLS and newly compiled entry code. The shared
  recomp_runtime.dll owns compiled translations and independent C++ runtime TLS.
  Windows binds the combined import tables and owns the actual module identities.
  Original instruction bytes have read-only data sections. The later permanent
  DEP requirement below closes an SDK-triggered execution-protection gap.
- [x] Run translated Umbra process attach to a normal TRUE return and enter main
  through this composition under Wine. Capture concrete CPU/FP state and use the
  real FS/TEB and a physical execution stack. This is a normal-return entry
  composition, not a capture of every original loader register/stack detail.
- [x] Observe the rebuilt process's `DragonAge` / `DASplash` window and its modal
  PhysX initialization error. Read-only Windows inspection recorded their owning
  PID and the exact staged replacement EXE path. This is visible startup, not a
  main menu, gameplay, or callback-bridge acceptance.
- [ ] Bridge native callbacks into compiled translated functions, including
  window procedures, COM interfaces and thread entry points. Outbound native SDK
  vtable calls already use the generic ABI path.
- [x] Execute ordinary native CALL/RET callbacks through compiled translations
  on private C++ stacks, including nested native calls and new-thread entry.
  The reached thread-name exception returns through compiled `__except_handler4`
  and the byte-checked source filter. This does not establish nonlocal unwind,
  all Windows/COM callback families, or a menu.
- [x] Permanently enable execution protection before translated entry. A retained
  SDK loading control disabled DEP and executed a read-only image probe; setting
  permanent DEP first prevented this across all six retained SDK loads. Earlier
  window/video observations cannot exclude execution of original callbacks.
- [ ] Complete native exception/unwind delivery and thread contexts.
- [x] Fold the 70 retained-state functions into the initial 1,994-function native
  bundle, preserving the 19 previously annotated selections. Constants and tables
  in original executable sections now have native read-only data backing.
- [ ] Continue integrated native startup to window, menu, save loading and gameplay.

Evidence: `local/recomp/startup/native-abi-prototype/report.json` and
`local/recomp/startup/native-execution-debug-report.json`. These are constructed
infrastructure observations on Wine 11/macOS ARM64, not DAO function acceptance
or a successful game launch. Original main/Umbra native fallback remains forbidden.

The native launcher is `python3 -m tools.recomp_native --run`. It stages retained
SDK DLLs and independent copies of game asset directories under ignored
`local/recomp/native-game/`; APFS copies share storage without sharing writes.
Use `--advance --run` to add an observed missing entry from the pinned inventory.
Ambiguous/missing bounds and runtime failures require debugging, not successful
stubs. Exit 3 is incomplete exploration, including a cleanly recorded frontier.

`--advance` now collects every distinct measured missing-code target from a
concurrent run. Runtime/ABI failures take precedence over another thread's code
gap; timeouts do not select targets. Direct-call discovery also traverses already
selected helpers within its depth limit, instead of treating selection as proof
that their dependencies were prepared.

Two broader passes prepared 116 and 489 additional direct helpers before cold
startup. Twenty-three candidates in the larger pass remained deferred, including
unsupported instructions and ambiguous bounds; those remain absent and fail if
reached. These counts describe generated code, not function acceptance. The
larger pass is retained in the content-addressed `call-discovery` report under
`local/recomp/native-game/`. The actual next run passed its earlier static code
gaps and reached another window-path entry.

The byte-pinned original splash procedure at main 0x00413bd0 now returns through
compiled execution into USER32, including its native tail-call return. Its class
literal is `DASplash`; this is not evidence of an interactive main window. The
message pump at 0x00413aa0 also compiles and runs. Read-only Windows inspection
now independently observes a visible `DragonAge` / `DASplash` window owned by the
staged replacement with DEP enabled and its original entry page read-only.
The protected follow batch records 68 compiled callback returns before its next
missing helper. This is window creation evidence; client pixels, the intro video,
menu and gameplay remain unverified in the protected build. Exact observations
and a contemporaneous run are retained under
`local/recomp/startup/protected-window-evidence/`.

The first native composition returned TRUE from Umbra attach after 157,324
instruction units, then reached main's missing `write_multi_char` at 0x008f1956
after 337,610,195 units. Windows assigned the original main TLS template (141
bytes) through its real TLS vector. No window/menu/gameplay is verified. The
native build explicitly loads fixed-base translated Umbra before relocatable
retained SDKs, because FMOD also prefers 0x10000000. This changes dependency
initialization order and still needs scenario-level original comparison.

Native logical, shift, multiply and divide operations now observe actual x86
arithmetic flags for concrete operands and incoming flags, including undefined
bits that CPU probes save with PUSHF/PUSHFD. Forwarded native-call flags must be
observed; TF/AC/NT exception modes remain refused. 10,712 focused observations
agreed under Wine, with 15 division-domain refusals. Producer tracing preserves
the actual thread's last-error field. Unsupported/symbolic state remains
unresolved; strict validation retains unknown flags. These are debugging checks.

The native CPU implementations live in `recompiler/runtime/native_cpu.cpp`.
Changing a provider no longer rebuilds every emitted function. The generic ABI
control also checks ID-bit transport and nine refusal cases, including unresolved
flags and narrow stores. No per-API ownership/marshalling wrapper runs.

The current generated-function count is recorded in
`local/recomp/startup/checkpoint.json`. Newly reached virtual methods
were selected in batches from original table pointers, with missing-inventory
bounds reviewed against instruction bytes, local branches, RETs and padding.
Their signatures/general behavior remain unaccepted. Native bridge bookkeeping
now preserves the actual TEB last-error field, including direct translated
FS:[0x34] writes; a focused native boundary control checks both named and raw
GetLastError calls against that field.

The reached floating-point method at main 0x00411650 now compiles and executes
beyond its earlier stop. Register FCOM/FCOMP, FCHS and the non-popping register
FDIV/FDIVR forms use compiled physical x87 instructions and captured raw state.
Current combined controls cover register/memory comparisons and division,
FUCOM/FUCOMP and their two-pop forms, signed FILD64, the added memory arithmetic
forms (FADD/FSUB/FSUBR/FDIV/FDIVR m32 and FSUBR m64), FIST m16/m32 plus
FISTP m16/m32/m64, and FABS/FST/FSTP ST(0)..ST(7). The new arithmetic/store forms preserve
raw operand bits, source rounding state and exact memory widths through physical
x87 instructions. Across the retained cases, 248,400 observations agreed under
Wine with 208 refusal checks and host FP restoration. This is instruction
debugging on Wine 11/macOS ARM64, not function acceptance or native x86 Windows
corroboration. The report is
`local/recomp/startup/x87-rep-integration-debug-report.json`.

The reached main body at 0x00a3cd60 now strictly compiles and executes to a real
dependency. Original FADD m32 bytes at 0x00a3cfe6 and FISTP m64 bytes at
0x00a3d01e have pinned instruction evidence under the native `bounds-review`
directory. This is a compilation/startup advance; it does not establish that
all branches or those later individual instructions ran during game startup.
New forms use a reserved, opcode-checked native operation tag, preserving the
shared runtime header and avoiding a rebuild of every generated function.

Plain word/dword MOVS in 32-bit address mode now preserves DF-controlled wrapping
indexes, ordered aliasing, ECX/flags and unknown scalar bits in checked memory.
Read/write faults retain incoming indexes. The integrated run passed the two
MOVSD and one MOVSW instructions in the byte-pinned `__fltout2` inventory candidate
and reached its next callee with return word 0x00903635. This is startup coverage;
the constructed Unicorn/sanitizer checks do not establish game equivalence.

The parser at main RVA 0x004f72cc now includes all twelve switch targets from its
original, ECX-bounded table. Twenty further code gaps were crossed in the shared
method batch; the missing-inventory constant leaf at 0x0079b310 was admitted only
after checking its exact original MOV/RET bytes and table references.

The independently staged original reproduced the same PhysX error. Installing
the bundled PhysX 9.15.0428 system package into the project Wine prefix supplied
the missing 2.8.1 core. The original then loaded that core and opened its main
window; our replacement also opened a `Dragon Age: Origins` window, and the user
reported the intro video playing. The two replacements without permanent DEP
ended at controlled observation timeouts (180 and 100 seconds), not a main return.
The exact previously inspected PhysXLoader bytes were preserved in an immutable
provider directory; both comparisons used that loader. Original files remained
untouched. Initial profile snapshots and run evidence are retained locally.

An SDK loading control exposed an execution-protection gap: the SDK set allowed
read-only image code to execute when DEP was not permanent. This means the prior
window/video observations do not establish that all callbacks ran through
compiled translations. Permanent DEP is now required and verified locally in
the replacement before translated entry. The reached 0x008e79c0 handler now runs
through compiled C++, calls the source thread-name exception filter, and returns
to the actual Windows dispatcher. Worker-thread entry at 0x004e6180 also enters
compiled execution; subsequent missing worker/window bodies are being recovered
from their original bytes. Do not count the older video as a pure replacement
boot. No menu, save loading, or gameplay is verified.

The callback bridge captures the actual Windows context before abandoning the
execute-fault dispatcher stack. A private C++ stack prevents translated source
stack writes from overwriting that dispatcher. Normal returns restore actual
registers, flags, x87/XMM, TEB bounds, last-error and observed RET cleanup through
a compiled assembly continuation. Return targets without executable native code
remain explicit unsupported nonlocal continuations. New-thread entries use
independent memory metadata and execution budgets over the same native images.

Every process measures x87 context register order with eight constructed native
fault/return controls, one for each TOP. The current Wine host exposes physical
register order. A separate direct FXSAVE/FXRSTOR observation also reproduced an
incorrect full x87 tag for FLD1. The outbound ABI and callback return now preserve
full x87 tags with FRSTOR rather than relying on that reconstruction. The focused
callback control passed sixteen entries, twelve live-FP cases (all TOPs, signed
zero, infinity and NaN), nested/native calls, new-thread entry, last-error checks
and ten refusal guards under Wine 11/macOS ARM64. No API-specific marshalling was
added. These are bridge debugging observations, not game-function acceptance.
Instruction counts vary with native process state and are diagnostic, not a
monotonic completion measure.
The native execute observer redirects ordinary calls into translated image data
to compiled callback execution. Missing bodies and unsupported nonlocal
continuations remain explicit frontiers.

`python3 -m tools.recomp_native_follow --restart --steps 24 --call-depth 2`
serially follows observed code gaps. Unknown bounds/runtime semantics stop it for
review; iteration limits and every progress report remain incomplete. Sessions
are retained under `local/recomp/native-game/follow-sessions/`. Required checks
passed on macOS ARM64: 284 tooling tests (one skip), six CMake checks, both
synthetic controls and nine upstream pipeline checks. No menu is verified.
Older native view metadata is losslessly gzip-packed; `recomp.read_view` restores
the exact hash-checked manifest and retains all normal source/data checks. The
latest storage pass packed 27 more historical manifests, saving about 2.0 GiB of
logical storage without dropping snapshots.

`RECOMP_TRACE_NATIVE_CALLS=1` enables generic native entry/exit records with target,
provider, thread and raw stack words; it adds no API marshalling. A traced boundary
control preserved direct TEB last-error writes and passed the nine refusal cases.
The earlier 60-second run timed out after DLL thread attaches. A longer traced
run returned to a missing-code stop after the error dialog. Thread-attach tails
and trace events no longer replace the main failure/outcome in the controller.
The full trace was retained compressed before the ownership inspection run.

Current native reports: `local/recomp/native-game/build-report.json` and
`run-report.json`, with immutable generated views, frozen native entry sources,
compiler/source/binary hashes and per-run history. Exact executed images and
their build reports are retained as compressed, content-addressed local blobs.
`tools.recomp_boot` remains
the historical strict explorer. The older strict frontiers below are historical.

## Import inventory and historical strict-backend work

[imports.json](../recompiler/imports.json) independently records all 582 static
slots: 453 distinct native imports and 44 translated Umbra imports. Both delay
import directories are empty. Every static provider/export was located offline,
including PhysXLoader.dll under the Wine prefix's NVIDIA PhysX/Common directory.
Actual loading, transitive dependencies and future computed lookups still need
native loader observations.

[import-abi.json](../recompiler/import-abi.json) records 294 direct SDK declarations,
six SDK aliases/intrinsics flagged separately, 125 demangled C++ exports,
18 stack-size decorations and ten unknown C middleware signatures. This research
is retained, but it does not impose a per-API implementation backlog on native
execution. Callback entry and actual machine ABI behavior still need verification.

Before the native architecture decision, the strict backend gained 56 batch
contracts alongside its 63 existing scoped adapters. The last synchronous
file/memory scenario made 65 native calls with 24 refusal checks, and a separate
16-resize heap regression passed. Pending OVERLAPPED operations/callbacks remain
explicitly unsupported there. Further strict per-API wrappers are deferred.
The 334 missing strict contracts are not blockers for the new native loader.

The strict inventory audit remains available for validation/debugging:

```sh
.venv/bin/python -m tools.recomp_imports \
  --manifest local/recomp/startup/main-project/views/VIEW/manifest.json \
  --output local/recomp/startup/import-coverage.json --require-contracts
```

That checks declarations only, not full API or game behavior. It is not a native
production readiness gate. SDK/decorated-name inspection remains reproducible with
`python3 -m tools.recomp_import_abi --help`.

## Milestones and concrete tasks

- [x] Link selected DAO/Umbra functions and non-executable data into a PE32 bundle.
- [x] Resolve all 44 DAO-to-Umbra import symbols; supply 11 translated entries.
- [x] **Execute the actual entry paths and record unresolved boundaries.**
  - [x] Translate the pinned EXE entry (RVA 0x4e3024), security-cookie initializer
    and CRT entry; retain separate provenance and incomplete-startup status.
  - [x] Supply real Win32 time/process/thread APIs and output-memory marshalling.
  - [x] Add a startup launcher with instruction budget, call trace, live PC/GPRs,
    failure reason and saved replay inputs. A stopped run is not a successful boot.
  - [x] Discover/select observed missing function ranges automatically,
    using byte-backed discovery; keep indirect targets explicit until executed.
  - [x] Expand bounded direct-call dependencies from reached or explicitly selected
    roots; preserve immutable provenance and unresolved optional failures.
  - [x] Keep a startup process paused at missing code and load byte-pinned candidate
    functions without discarding CPU/memory/native lifetimes; preserve shared
    unknown-origin IDs, verify the runtime ABI and record ordered plugin hashes.
    Native/model changes still require a fresh run; validate the final cold bundle.
- [ ] **Establish the Windows x86 process/native ABI.**
  - [x] Reserve original data addresses with a replacement host at another base;
    provide checked shared backing for native pointers and allocations.
  - [x] Bind reached native module lookup/dynamic symbols, TLS/FLS slot APIs,
    synchronization, environment conversion and standard I/O initialization APIs.
  - [x] Bridge reached registry open/close APIs with real failure statuses,
    checked output memory and tracked native key lifetimes.
  - [x] Bridge reached mutex creation, native waits/releases and owned-handle
    closing; preserve actual last-error/failure results and native ownership.
  - [x] Initialize selected-image PE32 TLS templates, indices and FS:[0x2c]
    for the initial thread; keep native dynamic TLS/FLS slots separate.
  - [ ] Supply remaining FS/TEB fields, nonempty TLS callbacks, new-thread
    contexts and exception dispatch before accepting dependent paths.
  - [x] Return from the partial Umbra attach fixture and run it before main in
    one process, carrying guest data and native allocations/slots forward.
  - [x] Produce DAOrigins.exe/Umbra.dll replacement artifacts with original data/
    export identities, compiled entries/callback transport, and retained SDK DLLs.
    Nonlocal exception/unwind completeness remains a separate open requirement.
  - [ ] Capture original process-start DLL attach inputs and complete main
    initialization with full dependency/loader ordering.
  - [ ] Implement reached heap, module, startup-info, command-line, file and
    synchronization APIs with explicit signatures and real native behavior.
  - [ ] Add callback/vtable entry thunks and native return/calling-convention
    adapters; audit module handles, image headers and resource access.
- [ ] **Create a real window and Direct3D device.**
  - [x] Reach the game's window/message loop and render its main menu; ordinary
    callbacks return through compiled translations on Wine9/Rosetta.
  - [ ] Bind Direct3D COM interfaces, native object pointers and method calls.
  - [ ] Implement encountered x87/SSE/string/atomic instructions and FP state.
  - [x] Capture a main-menu frame from the exact replacement process using original
    assets. Further rendering/scenario discrepancies remain open.
- [x] **Observe an interactive main menu in bounded local runs.**
  - [ ] Complete reached static constructors, configuration, assets, sound/input
    and middleware calls. Retain original FMOD/Bink/SpeedTree/PhysX binaries.
  - [ ] Resolve remaining Umbra trap/partial/dynamic paths as reached. All currently
    generated whole-batch selections are compiled; unresolved code stays unknown.
  - [x] Observe the menu on two same-image fresh-prefix Wine/Rosetta launches.
    One opened Options; the next started New Game and reached character generation.
    These observations do not certify all menu paths or continuous stability.
- [x] Start New Game and observe the character-generation3D preview.
- [x] Complete default character creation and opening conversation; observe the
  Castle Cousland HUD and preserve the completed initial autosave.
- [x] Observe camera zoom, walking, an explicit quicksave/reload cycle and
  post-load door interaction in the current replacement under Wine9/Rosetta.
- [x] Cold-load the preserved replacement-generated Cousland save in a fresh
  protected process; observe door interaction, walking and a new quicksave in
  the qualified owned profile. Original-save compatibility remains unverified.
- [ ] **Load a save and play an area.**
  - [ ] Choose a reproducible original-game save/scenario, then load it in the
    replacement and exercise movement, camera, visibility, animation and combat.
  - [ ] Resolve actual failures, preserve save/state formats, and profile hotspots
    before optimizing dispatcher/memory/flag overhead.
- [ ] **Exercise persistence and transitions.**
  - [ ] Save/reload, transition between areas and repeat representative gameplay.
  - [ ] Retain original/replacement scenario evidence, open discrepancies and
    performance observations; then package repeatable launch instructions.

## Earlier startup checkpoints

This section records earlier native and strict runs. The current published
checkpoint and next startup steps are at the beginning of this document.

The protected startup has passed clock helper 0x004cb160 after implementing
FDIVP/FDIVRP and signed FILD64 with checked original opcodes. The combined native
instruction control recorded 76,176 matching observations, 117 refusal guards
and restored host FP state under Wine 11/macOS ARM64. A failed earlier control
was traced to FP changes during unordered-set fixture setup; that setup is now
isolated, while provider and reference comparisons remain unchanged. Failed
snapshots are retained. These are instruction debugging results, not function or
game acceptance.

The next observed native callback target is 0x008192c0 and needs byte-reviewed
bounds because the pinned inventory has no usable entry. The startup controller
stopped rather than inventing its body. No menu or gameplay is verified.

The historical strict-backend frontier below predates native execution.

The earlier diagnostic bundle has nineteen selected functions. Fourteen new Umbra entries
(eleven imports and three helpers) have bounded original-DLL corpus evidence;
this is not object initialization or visibility-scenario evidence. Thirty-three
imported Umbra entries remain untranslated. The main bundle retains diagnostic commands. The separate startup composition
now executes the actual EXE and Umbra entry paths with an explicitly partial
thread/process state; complete process startup is still unverified.

Observed EXE entry: call 0x008f4907 (cookie initializer), then tail jump
0x008e2e44 (CRT entry). Umbra's DLL entry is 0x100cb9b1 and calls its cookie
initializer at 0x100d6239 before the CRT DLL attach path. These are observations
from pinned instruction bytes, not source-prototype claims.

Latest executed cold startup composition: 1,924 selected functions. A subsequent
retained-state session loaded 70 additional generated functions, making 1,994
available in that process. Its archived host and ordered DLLs replay to the same
unmapped jump-table read at PC 0x008fa740. The session consumed 337,769,222 units
and made 812,426 bridged native calls. The 70 additions still need a standalone
cold fold. No game window, menu, save loading or gameplay is verified; selected
functions are not accepted/executed counts.

The reached byte XOR now preserves partial knownness/origins and flags. Its
constructed controls compared 128 native x86 cases under Wine, plus 52 abstract
partial/correlated cases and two fault guards. The later reserved-field branch
required separate native-writer evidence: exact Wine 11 kernel32/kernelbase files,
procedure RVAs and live thunk target are checked before the actual returned
SYSTEM_INFO reserved WORD becomes known. Six native output comparisons, poison
observations and compiled writer instructions support that provider-only contract.
Other providers retain unknown reserved storage. No oracle, comparator, frozen
fixture or registered function acceptance was changed to make this startup pass.
Review: `local/recomp/startup/discovery/system-info-contract-review.json`.

The cold bundle uses Ninja. Folding the last 53 functions retained 1,867 of
1,869 prior cache artifacts, including the precompiled header. Existing generated
function objects were reused. One missing-inventory wrapper at 0x006eb1d0 was
reviewed from its ten original bytes and padding, then loaded while startup stayed
paused; its source signature/general behavior remain unaccepted.

The earlier `PUSH dword ptr [EBP-0x70]` stop is resolved by transporting scalar
knownness/origins before changing ESP. CreateDirectoryW now forwards actual native
directory creation/errors. The replacement prefix's Documents is a project-owned
directory; the former symlink to the user's Documents was preserved separately,
without copying or editing its target. This is a changed initial profile fixture.

Current stop: the narrow formatter's eight-way inline table at RVA 0x4faf21 is
deliberately unmapped. Its 32 bytes and in-function targets have been reviewed;
add a pinned read-only data region before the next cold startup. The active
priority is the native Windows execution path above. Do not restart the per-API
wrapper backlog to advance production startup. Exact events, source identities and hashes are in
`local/recomp/startup/last-execution.json` and `checkpoint.json`.
The current hot replay is `local/recomp/startup/live-replay/f6ab5c804c2efc8fd18c1eae8ef69e489ee6fa2d21e4e84baf2f12caca702dd0-d3283537a049/`;
it reached the same event, reason and PC. Native timing remains nondeterministic.

Historical live-loading observations (older bundles):

Retained-state exploration now loaded two generated Windows x86 candidate DLLs
in the running startup process: the reviewed missing-inventory wrapper at
0x006189b0 and its helper at 0x00618790. The base view contains 1,745 selected
functions; these two additions bring that session to 1,747 available functions.
It continued to an explicit missing-code stop at 0x006188f0 after 332,706,080
instruction units and 791,109 native calls. The archived host plus ordered DLLs
replayed to the same reason/PC; real native calls changed the instruction count
by 2,208. This is exploration transport evidence under Wine 11 on macOS ARM64,
not function equivalence, complete initialization or playability.

A subsequent session began with those two additions in its cold bundle, paused
for explicit byte review at 0x006188f0, and loaded five more generated candidates.
That session reached 0x004ee200 after 332,843,697 instruction units and 792,814
native calls, stopping when strict lifting refused unsupported multiplication.
Its archived host and ordered five DLLs replayed to the same reason/PC. All seven
additions were then folded into the 1,752-function cold bundle above, which
reached the same blocker. The latest hot replay is `local/recomp/startup/live-replay/50a2fc914b8ab1a25f3b512ca27cf4adf6649fb6c9aebf1a51d2c0108769656f-98a9445a28fc/`.

Candidate DLLs contain generated C++, use the host's unknown-value identity
allocator, and are checked against the pinned module, runtime/backend/compiler
identity, state layout, requested PC and existing code/import ownership. Accepted
DLLs remain loaded. Runtime/native-model changes require a cold restart, and the
final combined standalone bundle must still be exercised. Callback pauses are
currently refused. Artifacts and ordered replay are under
`local/recomp/startup/live-replay/`; the latest pointer is
`local/recomp/startup/current-live-replay.json`.

Bounded direct-call discovery now follows original instruction operands from
selected functions and strictly translates each optional helper before selection.
It checks pinned module/inventory hashes, function ownership and backend identity.
Unsupported or ambiguous candidates stay absent and fail if execution reaches
them. `--call-depth 3 --call-limit 64` expands newly reached code; adding
`--call-seeds selected` explicitly scans all startup-plan entries, including
unexecuted constructors. Two larger selected-root scans added 241 and 238 helpers,
respectively, with
15 and 18 deferred candidates after 256 attempts each; both limits were exhausted.
A helper deferred in multiple scans is not a distinct new failure each time.
These are static translation results, not executed-function or equivalence counts.
Immutable reports live in `local/recomp/startup/call-expansion/`.

The reached indirect target 0x007358c0 was absent from the initial inventory.
Its reviewed 30-byte body has one internal branch, a direct call and terminal
RET 4, followed by INT3 padding. No inventory range overlaps it. Its original
bytes, static ABI observations, pointer references and observed dispatch frontier
are recorded in `local/recomp/startup/discovery/main-3358c0-bounds.json`.
Strict translation succeeded; its source signature and general behavior remain
unaccepted.

The actual startup passed the reached `OR EDX,-1` after correcting consumption
of unknown input bits: constant-forced output bits do not require the prior
register bits, while uncovered unknown bits still fail. AF remains undefined.
A focused Wine x86 experiment compared 24 constructed instruction cases with
no mismatch in the declared outputs/defined flags. This is instruction debugging,
not a game-function acceptance result.

Reached `ADVAPI32!RegOpenKeyExW` and `RegCloseKey` now use the real native APIs,
with checked output memory and separate owned-key lifetimes. Native failure
statuses remain failures and failed out-key contents become unknown. Other
registry signatures remain unsupported. A focused native experiment checked an
existing key, predefined-key aliases, a missing-key failure, closed-handle and
invalid-output refusal, stack cleanup and last-error transport. It creates no
keys. The integrated startup progressed beyond the prior registry frontier;
the sampled game trace does not establish which registry result the game saw.

The subsequent native boundary, CreateMutexW, now creates/opens real Windows
mutexes and tracks returned kernel handles separately from registry keys, module
handles and allocations. WaitForSingleObject, ReleaseMutex and CloseHandle forward
real results and last-error values; only real successful closes retire handles.
Known UTF16 names and null/default security descriptors are supported. Nonnull
security descriptors and unregistered handle classes still need explicit adapters.
A focused native control checked recursive ownership, cross-thread timeout and
acquisition, existing-name error 183, inheritance, actual failed creation/error,
closed-handle refusal and invalid inputs. Those native control threads do not
implement translated guest threads. The registry reader regression also passed.
See `local/recomp/startup/mutex-debug-report.json` and
`registry-sync-regression-report.json`, alongside the
[Win32 mutex contract](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-createmutexw).
The running game composition passed its earlier mutex import boundary.

The former budget frontier was a finite arena prefill. Reviewed original
instructions compute approximately 384,477 iterations for the first 55 MiB arena;
bounded state capture observed the counter decreasing and 120-byte blocks
advancing. With a sufficiently large budget, this workload completes around
298 million instruction units. It was not a demonstrated infinite loop. The
subsequent larger arena allocation also succeeds after removing the prototype's
256 MiB registration cap. Actual Windows allocation extents, ownership, lifetime,
nonwrapping x86 bounds and guest-image overlap checks remain enforced. A separate
native check exercised a real 257 MiB allocation and both endpoints.

The EXE's hash-verified PE TLS directory declares a 141-byte template, no zero-fill
and an empty callback list. Each initial thread receives a private copy and module
vector; the loader writes the image's index and FS:[0x2c]. The vector is distinct
from native TlsAlloc slots. A constructed PE32 DLL loaded by Windows under Wine
checked nonzero template copying, zero-fill and native/guest thread isolation;
unallocated vector slots and nonempty callback lists remain explicit failures.
This implements initial-thread TLS data, not new native thread/context transport
or TLS callback execution. See the [PE TLS specification](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format#the-tls-section).

The CRT copying routine now passes its former PC 0x008e321e / table-read
0x008e32e0 frontier. Six reviewed pools totaling 120 bytes are mapped read-only;
reviewed case targets are compiled as additional entries in the same function.
The alignment pools deliberately exclude unused index zero, whose nominal table
base overlaps an instruction. Generation checks original byte hashes and rejects
overlaps with decoded instructions or other data. The original code remains
non-executable; guest reads stay bounded to each declared pool. Structure recovery
seeds the additional entries with unknown facts. The actual computed table target
still controls dispatch; uncompiled targets fail. This is observed startup progress,
not a copying-function equivalence result. Discovery evidence is in
`local/recomp/startup/discovery/main-4e3030-jump-tables.json`.

A second reached copying routine at 0x008e24a0 now has six analogous reviewed
pools totaling 120 bytes and 30 additional case roots. Its 869-byte envelope
matches the earlier routine after rebasing its internal table pointers and
adjusting an external branch to preserve the same absolute helper target.
This is original-byte layout evidence, not arbitrary behavioral equivalence.
The actual startup passed its prior table-read fault at 0x008e2524/0x008e25bc.
Bounds, read-only pool mapping and original-code execution refusal remain in
force. See `local/recomp/startup/discovery/main-4e24a0-jump-tables.json`.

The reached wide formatter at 0x008faf8b has an eight-way table immediately
after its 2,288-byte code interval. The original unsigned guard admits indexes
0..7; the 32-byte table ends exactly at the next inventory function. All eight
targets lie inside the existing function interval and are declared as additional
entries. Only those 32 bytes are exposed read-only. Discovery and the actual
prior read fault are recorded in
`local/recomp/startup/discovery/main-4faf8b-jump-tables.json`; this is traversal
and startup evidence, not formatter equivalence.

The original CRT loop at 0x008edc5e..0x008edc7c walks the table
0x00ada810..0x00add888. It contains 716 nonnull pointers; 681 lacked bounds in
the initial analysis inventory. Mechanical byte-checked discovery found 688
additional straight-line wrappers ending at plain RET, without crossing another
initializer or selected range. Of these, 686 were selected in bulk. The reached
MOVAPS wrapper now compiles, and the non-popping x87-store wrapper is also selected
after adding that operation. All 688 linear candidates are selected, without a
claim that all have executed. The nine entries rejected by that earlier linear scan were reviewed separately:
eight short wrappers end in direct tail jumps and are now selected, with ten
additional helpers. Their byte-backed bounds and strict translation evidence are
in `local/recomp/startup/discovery/crt-tail-initializers.json` and the immutable
call-expansion reports. The last larger wrapper has now been selected from its pinned inventory bounds
(556 bytes, no branches, 108 instructions). Every one of the 716 nonnull CRT table
entries is selected. Their dependencies and runtime paths are still incomplete. Selection
does not establish that each initializer or helper has executed.
Calls retain their actual runtime dispatch boundaries. These are traversal
hypotheses, not source signatures or behavioral acceptance; selected wrappers
need not have executed. Discovery/selection reports are under
`local/recomp/startup/discovery/crt-linear-*.json`.

This remains a partial loader composition. Umbra receives chosen attach arguments
(module 0x10000000, DLL_PROCESS_ATTACH, reserved=0) and chosen FP controls matching
the measured main-entry fixture. The original process-start attach FP/register/
reserved context is uncaptured. Main receives its measured FP fixture, unknown
non-SP GPRs/flags, clear DF and a mapped ESP. Its reused stack is reset to unknown;
loader register/stack continuity is not claimed. Full dependency ordering,
remaining TEB/PEB state and native threading remain incomplete.

No window, menu or gameplay is verified. Exact terminal events remain in
`local/recomp/startup/last-execution.json`. Incoming non-SP GPRs stay unknown;
LEAVE, base-only zero-offset LEA and scalar copies preserve copied unknown bits.
Mixed-width overlapping stack slots preserve per-byte known bits and identities.
Native x86 debugging checked 32 mixed flag probes, 32 word register saves/restores
and 32 dword register saves/restores with no observed mismatch. Those constructed
instruction cases are separate from the incomplete game startup.

The original EXE was stopped at its actual entry and FP-control helper under
WineDbg. Both captures reported x87 CW 0x027f, SW 0x0120, empty tags and MXCSR
0x1fa0. The main entry fixture now uses those measured control/status fields.
Umbra's isolated DLL-attach fixture deliberately uses those same values as a
chosen input; its original DLL_PROCESS_ATTACH FP state remains uncaptured.
`FNCLEX`, `FNINIT`, `FWAIT`, control/status stores, `FLDCW` and MXCSR load/store
now have explicit models. Legacy lifter MXCSR placeholders are replaced in the
PE32 candidate frontend; unrelated profiles refuse those forms.

Reached x87 value operations now use controlled, compiled Windows x86 instructions
with raw logical 80-bit registers, physical tag/TOP tracking, CW/status and MXCSR.
Supported forms include FLD1/FLDZ, 32/64-bit loads and popping stores, non-popping
32-bit stores, FSTP ST(0)/ST(1), signed 32-bit integer loads, and 64-bit memory
subtract/multiply/divide/add.
Unknown live operands and unmasked exception modes stop explicitly. Empty-register
bits retain their known/unknown status; store permission failures leave FP state
unchanged. FNINIT preserves physical data while rotating the logical view to TOP=0.
This does not use host double conversions or execute original code pages.

The reached Umbra identity-matrix initializer matched its original DLL function on
96 constructed FP inputs under Wine. A further 216 synthetic load/store pairs
covered sampled zeros, subnormals, infinities and NaNs, and eight FNINIT cases
checked physical data rotation. Host FP restoration and failure guards passed.
A further 576 synthetic integer/arithmetic/store sequences matched direct x86
execution over sampled integer limits, three precisions, all rounding modes and
three TOP positions. The numeric/data comparison excludes opcode and IP/DP
metadata. These are bounded debugging observations, not initialized-game validation or native
x86 hardware corroboration. Original-DLL execution is confined to the reference
experiment; the replacement retains the no-native-Umbra-fallback policy.

The startup-selected constructor at 0x0054e7e0 contains FDIVR m64 at 0x0054e842.
The body now translates that form through the controlled native x87 backend,
with memory divided by ST(0), raw 80-bit values and the existing masked-exception
requirements. A native constructed experiment compared 1,296 cases over sampled
finite/special values, three precisions, all rounding modes and three TOP values,
with live-result, 32-bit store and 64-bit store forms. Numeric raw data, tags,
control/status, MXCSR and final host state matched; three invalid-input guards
refused without changing guest state. Opcode/IP/DP metadata is excluded.
The initially failing host-state comparison localized to unknown-memory fixture
preparation before the adapter call. An independent preparation-only control
reproduced that host FP change. Isolating fixture setup preserved the original
comparators; all failed runs and controls remain recorded separately. The current
report is `local/recomp/startup/x87-reverse-debug-report.json`. These are instruction
debugging observations, not acceptance of the constructor or the game.

The next startup-selected constructor at 0x0053ff80 requires FXCH ST(1).
The backend now supports the eight canonical FXCH register forms with native
raw 80-bit exchange and tag/status transport. Native comparison covered 480
constructed cases across three TOP positions, finite/zero/NaN payloads, incoming
C1 values and live/empty operands. All matched, including 96 cases where unknown
empty payloads were replaced by known native masked-underflow results. Unknown
live values and unmasked exceptions remain explicit refusals; host FP state was
preserved. See `local/recomp/startup/x87-exchange-debug-report.json`. These are
instruction-family debugging observations, not constructor or game acceptance.

The next CRT stop at 0x008e6240 exposed a non-popping 64-bit store in the
square-root wrapper. Its helper at 0x008e625d also needs FSQRT and an 80-bit
constant load. All three forms now use the controlled native provider. The
frontend's FLD m80 intrinsic supplied a dummy 32-bit load; lowering discards that
load and the provider reads ten checked bytes instead. A constructed comparison
matched 1,296 extended-input/load/sqrt/store cases and two empty-stack stores,
with four invalid-input refusals and final host-state preservation. Earlier
division/exchange candidates were rebuilt against current headers and retained
their 1,296/480 matching cases. Reports are `x87-sqrt-store-debug-report.json`,
`x87-reverse-current-runtime-report.json` and
`x87-exchange-current-runtime-report.json` under `local/recomp/startup/`.
These remain instruction debugging, not function or game acceptance.

The shared math-return fragment at 0x008f508e is now selected once as a reviewed
13-byte traversal fragment. The inventory also attributes it to an unselected
0x008ea028 hypothesis; that inventory is unchanged. Future selection of that
hypothesis must review its shared range rather than assign duplicate PC ownership.
The fragment requires the math helper's saved control-word/EDX slot and return
frame; it is not a standalone source-function signature. See
`local/recomp/startup/discovery/main-4f508e-shared-math-exit-bounds.json`.

The reached main matrix helper at 0x004d38e0 now initializes its matrix with
three non-popping FST m32 operations followed by FSTP m32, and its calling
initializer copies the matrix through MOVAPS. A separate native x86 debugging
experiment compared 48 non-popping sequences and two empty-stack cases, including
TOP/tag/raw-register retention, readonly-store refusal and host FP restoration.
The first empty-stack fixture supplied different physical entry images on its two
sides; that failed run and the input correction remain preserved separately. The
corrected experiment retains the full raw-data/control/status/tag comparator and
excludes native IP/DP/opcode fields. These are constructed instruction observations,
not acceptance of the whole game function. The following reached constructor
at 0x00466120 also uses FSTP ST(0)/ST(1). Twelve native sequences checked both
register destinations with two TOP positions, live/empty source stacks, raw
register data and tags; newly live results stay known, and unknown live values
still fail. That constructor now executes past its x87/vector initialization.

The reached 0x004ee200 path required FMUL m32 and both non-popping register
destinations. These now execute controlled compiled x87 instructions for all
eight register indices, retaining raw80 values, TOP/tags and exact operand widths.
An independent control using constructed opcode bytes observed 6,120 numeric/
control cases, 72 unknown-empty cases and four refusal guards, with no mismatch
and host FP preserved, under Windows x86/Wine 11 on macOS ARM64. The first lift
attempt exposed two legacy intrinsic shapes; exact mnemonic/operand rewrites
corrected those shapes without relaxing unsupported forms. Failed attempt inputs
remain archived under `multiply-first-lift-failure/`.

Execution then reached the 98-byte helper at 0x004cbc40. Its FSINCOS, FLD ST(i)
and FMULP operations now have explicit native providers. FSINCOS keeps TOP/input
unchanged on its observed range failure and supplies two known results on the
push path. Register loads and multiply-pops retain physical/logical stack order
and unknownness. A separate constructed byte control observed 7,956 cases and
78 unknown-empty cases with no mismatch, four refusal guards and host FP
preservation. These are instruction-debugging observations, not acceptance of
either whole game function or initialized gameplay. Reports are
`local/recomp/startup/x87-multiply-debug-report.json` and
`local/recomp/startup/x87-trig-stack-debug-report.json`; their frozen input/header
snapshots identify the runtime each actually exercised.

The subsequent 136-byte arithmetic helper at 0x004cb640 required FADDP and FSUBP.
Both register-pop families now retain destination/operand order and rotate the
knownness mask with TOP. Independent constructed opcode controls observed 5,760
cases plus 72 unknown-empty cases, four refusal guards and host FP preservation
with no mismatch. Explicit Intel syntax avoids the AT&T subtraction spelling
ambiguity in the native provider. The integrated run passed this helper, reviewed
and hot-loaded the 30-byte conditional update wrapper at 0x004a97d0, then loaded
three more candidates in the same process before reaching WINMM!timeGetTime.

The timeGetTime boundary now forwards to the real Winmm API with its documented
no-argument DWORD return and stdcall stack behavior. Generated Windows bundles
link Winmm explicitly so its loader lifecycle precedes guest entry. Other Winmm
signatures still fail. A focused control bracketed 32 returned values with actual
native clock readings and checked return/stack/clobber/last-error transport, two
refusal guards and host FP preservation. It did not test a timer wrap or establish
deterministic game timing. See the [Microsoft signature](https://learn.microsoft.com/en-us/windows/win32/api/timeapi/nf-timeapi-timegettime)
and `local/recomp/startup/timer-debug-report.json`.

The next Unicode boundaries now preserve the configured logical main filename
for NULL/0x400000 module handles and query registered native modules directly.
GetModuleFileNameW uses checked WCHAR16 capacities with widened byte arithmetic,
actual host truncation/error conventions and raw UTF16 copying, including a
surrogate split at truncation. Eighteen direct native path comparisons plus a
logical Unicode path, surrogate truncation and three refusal guards passed.
SetCurrentDirectoryW forwards the real process effect and BOOL/error result;
six native directory/effect comparisons and invalid-pointer refusal passed, with
the control process's initial directory restored. See the
[filename contract](https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-getmodulefilenamew)
and [directory contract](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-setcurrentdirectory).
These remain native-boundary debugging observations; translated DLL filename
identity and broader file APIs still need explicit handling.

The extended owned-handle wait now forwards the BOOL32 alertable argument and
actual WaitForSingleObjectEx result/error with cleanup12. Eleven native control
cases covered acquisition, timeout and APC results, including noncanonical BOOL
bit patterns and four observed WAIT_IO_COMPLETION returns. The legacy two-argument
wait still refuses to consume an unknown third argument. Native control APCs and
threads in this experiment do not implement guest APC/thread registration.

Reached USER32 LoadIconW/LoadCursorW now use ordinal16 or checked UTF16 names and
separate shared USER-handle tracking. A translated module must be its exact
recorded base with checked flat known/readable PE32 headers and resource data;
original executable sections remain inaccessible. Icon resource 106 from those
mappings matched the original EXE's resource pixels. The reference file was opened
with [LOAD_LIBRARY_AS_DATAFILE](https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-loadlibraryexw),
which does not initialize or execute the module. System resources, missing-resource
errors and invalid module guards also passed. This is resource transport evidence,
not a rendered game window or initialized gameplay.

Native kernel ownership now includes events and semaphores. CreateEventW preserves
actual reset/state behavior, named reuse, collision errors and inheritance; sixteen
native reset/state cases and two refusal guards passed. CreateSemaphoreW preserves
signed LONG counts, actual wait decrements, reuse/errors and inheritance; eight
count cases included four real native failures and two refusal guards. Shared
USER resources keep separate lifetimes and are never closed as kernel handles.

Native scalar APIs still require an empty x87 stack. They carry the declared
control/environment and MXCSR into actual Windows calls, capture resulting state
and restore the launcher's state afterward. Native FP return/value ABI transport,
SEH/debug-trap delivery and unmasked x87 exception handling remain unfinished.

The CPU probe now retains identities for copied unknown flag bits through stack
snapshots, register moves and constant XOR. Its single-bit comparison can establish
the branch result without choosing values for those unknown bits. Full unknown
value consumption still fails. Overlapping writes replace only the written
bytes and preserve untouched bit identities; writable native pointer exposure
discards exposed identities. CPUID leaves 0/1 query the actual Windows
x86 execution host, and reached vector copies preserve bits and unknownness. PXOR zeroing and aligned
MOVDQA stores now run; misaligned stores fault explicitly, and unknown vector
stores retain unknown bytes. Canonical REP STOSB/STOSW preserve DF, wraparound, zero
counts and partial progress. AND-memory-zero retains memory read/write checks
while producing a known zero even from unknown stack contents; AF stays unknown. This remains a partial machine model; debug/trap and SEH delivery
are unfinished. CPUID register roles follow the
[Intel instruction reference](https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-vol-2a-manual.pdf).

MOVAPS memory loads/stores now copy raw 128-bit values with aligned access checks,
following [Intel's instruction reference](https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-vol-2b-manual.pdf).
Sixteen constructed copy patterns matched direct native x86 execution under Wine,
including flags and MXCSR preservation. Compiled checks retain unknownness and
verify alignment, access faults and faulting-instruction state. Unknown vector
loads conservatively retain whole-register unknownness; partial vector facts are
not claimed. The reached SBB EDX,EDX idiom now consumes only its known carry input;
unknown carry still fails. Forty-eight constructed native x86 cases checked result
bits and all arithmetic flags, with unknown incoming register values modeled on
the candidate side.

GetSystemInfo now invokes the actual Windows x86 API through a checked 36-byte
output contract. Documented fields become known; the reserved WORD and unwritten
tail remain unknown. Numeric address limits are not registered as live allocations.
The native-boundary check compared 34 documented bytes and checked void-call
clobbers, last-error behavior, output bounds and readonly refusal. See Microsoft's
[SYSTEM_INFO layout](https://learn.microsoft.com/en-us/windows/win32/api/sysinfoapi/ns-sysinfoapi-system_info).

Native classification, multibyte/UTF-16 conversion and locale mapping now execute
through Windows with explicit signatures and checked buffer sizes. Output buffers
can contain unknown bytes on entry; only bytes actually written become known.
The configured game command line and executable path are distinct from launcher
diagnostics. `GetModuleFileNameA` uses the main game's logical identity and this
host's measured truncation/last-error conventions. A Windows x86 bridge experiment
compares against native results and checks that unwritten output tails stay unknown.
Truncated non-ASCII paths and translated DLL path/handle identity remain unfinished.
GetCPInfo accepts unknown destination bytes, publishes documented fields through
the lead-byte terminator, and retains unknown padding/unused tails. Three native
code-page checks agreed on this host. Reached allocation-size queries now call real [Windows HeapSize](https://learn.microsoft.com/en-us/windows/win32/api/heapapi/nf-heapapi-heapsize)
with checked registered backing and an explicit x86 signature. HeapLock/HeapUnlock
and [HeapReAlloc](https://learn.microsoft.com/en-us/windows/win32/api/heapapi/nf-heapapi-heaprealloc)
now use real Windows calls. Size/free/resize require an exact live allocation base
and owning heap. Resizing moves unknown-byte metadata and preserves bit identities
through the guaranteed requested-size prefix; unknown allocator slack remains
conservative. Failure leaves the old mapping live; free clears its metadata. A
bounded Wine check observed sixteen actual moves and verified shrink, failure,
ownership and unknown-content lifetime behavior.

Necessary instruction debugging now preserves unknown values through `POP`, tracks
known byte/word portions of native-clobbered registers, and supports canonical
`F3 C3` near returns. Full-register consumption of unknown portions still fails.
Static ranges can omit continuations after presumed nonreturning calls. These
continuations are listed explicitly in the function manifest, and dispatch fails
if an unselected continuation is actually reached; no return behavior is assumed.

The Windows x86 host runs at 0x20000000. A small replacement reservation DLL
occupies the original EXE namespace before the host CRT allocates its heaps.
Only declared original data, stack, static-TLS and partial thread regions receive checked
native backing. Original code pages contain no original instructions and cannot
execute. Native allocations and environment-block lifetimes are tracked. The
CRT's aligned string loads can cross a logical HeapSize boundary; those reads
observe real bytes through checked Windows `ReadProcessMemory`, remain anchored
in a registered native allocation, and cannot cross guest-owned mappings.
Native API pointer conversions retain their allocation bounds. No padding values
are invented. Observed edge-read events remain recorded separately in each startup trace.

Real TLS/FLS slots and dynamic typed native bindings execute. FLS callback thunks
have been registered, but game callback execution remains unobserved. The EXE's
SetUnhandledExceptionFilter registration now installs a real native thunk and
preserves previous guest/native callback identities. Controlled Windows checks
verified registration, restoration and the explicit failure reached when its
callback is invoked without guest EXCEPTION_POINTERS/context transport. This
registration support does not implement guest exception handling.

Earlier missing-target exploration repeated startup work: four recorded cold
build/run cycles took approximately 179–204 seconds each and repeated about
332 million instruction units. Retained-state function loading now avoids that
repeat for compatible new code, including an explicit pause while original byte
bounds are reviewed. ABI/origin-ID checks and ordered replay provenance remain
required. This is an iteration tool; a paused or hot-loaded session does not
substitute for the required standalone cold gameplay run.

The startup cross-build now keeps its existing `-O2 -DNDEBUG` settings and omits
compiler debug records with `-g0`. Guest-PC diagnostics and immutable generated
sources remain available. In the first rebuilt bundle, the executable fell from
229 MiB to 23 MiB and the static library from 302 MiB to 38 MiB. Exact prior
artifacts remain preserved; this storage change is not a game-semantic claim.
The startup library also caches a parsed runtime header to avoid repeating that
header work for every function after instruction-model changes. Compiler and
build commands remain recorded with each executed bundle.

Inactive view manifests are now stored losslessly as `manifest.json.gz` when
needed. Packing verified the decoded SHA-256/size before removing the plain copy;
301 inactive manifests reclaimed about 3.47 GB. `tools.recomp.read_view` restores
exact metadata on demand, checks its original view identity, and retains ordinary
file checks. Changed/truncated packed metadata cannot publish a manifest, and an
existing changed manifest is never repaired from a good pack. Original binaries,
assets, memory captures and source/data/executable replay paths were untouched.
Current storage records are under `local/recomp/startup/view-storage/`.

Startup views keep immutable source/data hashes. Incremental Windows builds retain
unchanged source paths/timestamps. Identical files across complete immutable views
now share hard links without changing bytes or deleting snapshots. The latest executed launcher, runtime headers and exact hash-verified plan are
archived under
`local/recomp/startup/replay/3547065683716e6bb0e65bf2bf9f57174712d3ef6e714e9f9ba821d2ca9da2f1-4a50ca2736e9/`.
The archive is keyed by both generated view and executable hash. Combined replay
reached the same native wait-import PC/reason; consumed instruction units differed
by 3492 with real nondeterministic native calls. Earlier archives, including the
ten-million-unit budget stops, remain available. Repeated terminal state is not
exact game equivalence.

Historical static build libraries have been gzip-compressed with decoded SHA-256
and size checked against their original execution reports. Their executable replay
paths, original files and captures remain in place. Each affected replay directory
has `storage.json` with original logical hashes, stored-file hashes and an exact
restore command; decompress the library before rebuilding/relinking that archive.
The compression report is `local/recomp/startup/replay-library-storage.json`.

Bounded tracing can retain the last 256 main stores/node reads. Native-call trace
sampling logs an initial prefix, periodic events and failures while every call
still executes; total dispatch and omitted-trace counts remain in terminal events.
This is exploration logging, not a complete deterministic comparison tape.
`last-execution.json` retains the latest executed composition even if a later
build/selection attempt fails in `latest.json`.

The legacy PhysX prerequisite installed into the ignored Wine prefix. Launching
the original under WineDbg now yielded actual EXE-entry and FP-helper contexts.
A later Umbra entry was captured on another stack, but its DLL attach reason
was not captured. Neither this observation nor an original process listing
establishes a working menu or renderer. Owned diagnostic game/debugger processes
were stopped; no original executable or asset files were modified.


Native reproduction:
```sh
python3 -m tools.recomp_native --run
python3 -m tools.recomp_native --advance --run
python3 -m tools.recomp_native --advance --call-depth 1 --call-limit 128 --call-seeds selected --run
```
Exit 3 denotes incomplete exploration, never a successful boot. Main inventory:
`local/analysis/functions.json`. Umbra bounds-only inventory:
`local/recomp/startup/umbra-analysis/functions.json`.

Checkpoint builds ran on macOS ARM64; integrated startup used cross-compiled
Windows x86 C++ under Wine 11. Required checks: 289 Python tests completed with one skip; six
native CTest checks and nine SharpRetro machine pipeline checks passed. Both
synthetic demos retained their expected outcomes (59 agreements; negative control
53 agreements and six semantic mismatches). Those are infrastructure checks,
not startup or playability passes. Reports are in `local/recomp/startup/`.

A separate original-game reference launch was stopped after Wine application
inspection timed out. No original window/menu was verified, and its controlled
exit is not a diagnosed game fault. Original main/Umbra execution is forbidden;
the later protected-run audit above supersedes the earlier assumption that PE
section flags alone enforced this during native callbacks. That original-reference observation is recorded in
`local/recomp/startup/original-launch-baseline-process.json`.

Continuation uses the chat's persistent goal. No five-minute watchdog automation
was created: this session's automation rules disallow using a schedule to keep a
single unfinished task alive. Do not duplicate the work in scheduled workers.

Protected callback checkpoint: 3766 generated functions. Plain MOVSB and REP
MOVSB/MOVSW in 32-bit address mode now execute through the chosen Memory backend,
including both canonical word-prefix orders. An optional runtime fragment is
embedded only in affected units; the common runtime header and prior dword path
remain unchanged. Source elements are captured before writes, byte/word aliasing
is sequential, indexes/count wrap at 32 bits, flags remain unchanged, and faults
or budget stops preserve completed iterations. Zero-count repeats do not inspect
source/destination/DF. Strict scalar copies retain partial known bits/origins;
production accesses actual native memory.

Constructed Windows x86 CPU comparisons passed 368 valid-range/alias/resume
cases and nine zero-count/unknown-input controls with host FP state restored.
Expanded portable Unicorn/sanitizer checks covered wrapping addresses, faults and
partial bit facts. These are instruction debugging scopes under Wine 11/macOS
ARM64 or emulation, not native x86 Windows/game-function acceptance. The source
helper uses the original F3 A4 at 0x008f2f70 as evidence; the whole function's
signature/contract remains unaccepted. Current controls are retained in
`local/recomp/startup/rep-small-debug-latest.json`.

Protected startup advanced beyond both copy helpers (0x008f2ed8/0x008f2e51) and
several subsequent game bodies. The continuation reached a new native callback
at 0x00415260; its exact 35-byte body through RET 16 was reviewed and compiled.
That callback returned normally and also reached its 0x00414970 callee. Its
bounded original selector and nine-entry switch table have now supplied extra
decode roots, allowing the reached 0x00414b70 case to run through compiled code.
The runtime still reads the original tables and follows the computed PC.
One build stopped on actual disk exhaustion; lossless packing of older generated
metadata recovered space and a bounded retry/continuation succeeded. The failed
session remains retained; exhausted storage was never counted as a run pass.
The latest matched build/run checkpoint is authoritative. No client frame,
protected intro playback, menu, save loading or gameplay has been verified.

The user reported another intro-video observation during this continuation. A
separate Alkyhol original-game experiment was also running, so that report cannot
currently be attributed to the protected replacement. Read-only inspection did
confirm a visible replacement DASplash window with DEP enabled and original
entry bytes read-only during the 3441-function intermediate run. No protected
video/menu/playability claim follows from that splash observation. Evidence is
retained in local/recomp/startup/user-intro-video-observation.json and
video-observation-replacement-splash-binding.json.

The next continuation reviewed source tail method 0x00527b10 and both of its
direct dependencies, then prepared two contiguous original executable-pointer
runs containing reached getters 0x00587390 and 0x0081f0f0. These are static
preparation scopes, not recovered class identities or complete vtable claims.
The first run had 69 entries: 60 newly translated, one already selected and eight
deferred. The second had 34 entries: 31 newly translated, one already selected
and two deferred. Inventory bounds were byte-checked; absent bounds admitted
only exact small straight-line bodies ending in RET/JMP followed by INT3.
Unknown branch bounds remain deferred. No successful stubs or original execution
fallback were added. Original pointers and computed dispatch remain unchanged.

Integrated Windows x86/Wine 11 startup then advanced through the added bodies
and later call chains to missing main entry 0x00577fc0. That continuation’s matched
build/run contained 3620 compiled functions, returned controlled incomplete exit 3
and did not time out. Production runtime/lowering and accepted recovery registry
were unchanged; the previously executed required checks are reused, not newly
rerun for this selection-only continuation. Lossless generated-metadata packing
recovered additional space; original assets, sources and captures were retained.
The goal remains active. Protected intro playback, menu, save loading and gameplay
remain unverified. Current evidence: local/recomp/startup/checkpoint.json.

A later continuation reached 3629 functions before requiring original bounds for
0x004e6880. Its complete 55-byte body and common RET 4 were reviewed and lifted.
A depth-one pass across selected roots admitted 126 additional direct helpers:
128 attempts, two unsupported deferrals and 824 unique targets beyond its limit.
The matched protected run contained 3756 functions; this was not call-graph closure.
The retained report is native-game/selected-dependency-sweep-evidence.json under
local/recomp/.

The reached 0x004d0930 body was then reviewed through both RET 16 exits. A depth-five
pass added seven helpers and retained the unsupported segment-selector store in
0x008e10d2 as an explicit optional deferral. Its protected run exposed concurrent
missing targets: a case inside 0x004bebc0 and source body 0x004e9e20. Original
CMP EAX,5 / unsigned JA / JMP [EAX*4+0x004becb4] supplied six switch decode roots.
The complete 431-byte 0x004e9e20 envelope, local branches and RET 4 were checked;
bounded dependency preparation added one helper with no new deferrals.

The final matched run has 3766 functions and advances to 0x004bf010 / 0x004e9c90.
Both targets have usable pinned inventory bounds (29 and 30 bytes respectively).
Read-only inspection again observed the staged replacement DASplash with DEP
enabled and the source entry read-only. No protected video or menu was observed.
Production runtime/lowering and the recovery registry were unchanged; required
checks remain the previously executed results, not a new rerun.

Storage recovery losslessly packed inactive generated metadata and archived
inactive legacy strict CMake object/dependency caches as verified gzip files.
All original cache bytes, hashes, modes and timestamps remain recorded. Restore
those cache files before reusing that historical configured build, or regenerate
it from the preserved sources. The current native-game cache, executed binaries,
sources, original assets and captures were retained. A filesystem-compression
experiment saved no blocks; its temporary copy was removed without changing the
source. Storage reports are local/recomp/startup/inactive-*-cache-storage-*.json.

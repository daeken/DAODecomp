# Object counter recovery group 001

These three pinned main-executable leaves read and write one 32-bit object field.
Their original names, containing class and subsystem remain unknown.

| RVA | Bytes | Field offset | Instruction-derived behavior |
| --- | ---: | --- | --- |
| `0x00061f40` | 32 | `0xd0` | For old `0xffffffff`, store `1` and return the old value; otherwise increment and return the new value |
| `0x00061f60` | 26 | `0xd4` | Increment modulo 2^32; replace a resulting `0xffffffff` with `1`; store and return the result |
| `0x00061f80` | 26 | `0xd8` | Same increment/sentinel behavior as the preceding function, at a different field |

Original bytes, complete Capstone/LLVM decoding, relocation checks and observed
call sites support these boundaries. The two observed calls to `0x00061f40` lack
an inventory owner; their decoding anchors are retained without guessing caller
identities. Those callers immediately unwind and return, so the counter's EAX
value may escape to their callers. The observation retains all 32 EAX bits.

The reviewed boundary maps ECX to a 512-byte initialized ordinary-RAM allocation
plus an object offset from 0 through 128, permitting every byte alignment. There
are no stack arguments or callee-popped arguments. Only the selected four-byte
field may be read or written; every arena byte is compared after execution.
Nonvolatile registers, stack balance and DF are checked by the original adapter.
Other volatile registers and flags are excluded at this high-level boundary;
future binary bridges need their own caller-dependent register mappings.

This is a bounded fixture domain, not a reconstructed complete class layout.
Faults, concurrency, MMIO, exceptions and native Windows execution are excluded.
The existing checked `GuestMemory` dword access and guarded emulator remain
unchanged; a separate adapter supports the larger allocation and counter ABI.

Each function has 340 public and 128 held-out deterministic fixtures, inherited
unchanged from independent original-only characterization. They cover distinct
object offsets, unaligned fields, walking bits, unsigned/sign boundaries and
sentinel predecessors, with whole-arena canaries. Original and candidate executions
are repeated in fresh processes. The negative control returns the newly stored
value for the D0 sentinel path, where the original returns the old sentinel.

The [independent acceptance-system review](reviews/object-counters-001-contract.json)
approves the exact contracts, adapter and fixture hashes. It checks 3,870
additional original-only states across every permitted object offset, plus 36
repeated probes and 90 fresh-process adapter executions. All 95 tooling tests
pass in the project environment. This review does not approve a candidate.

Luna's first proposal passes all public D4/D8 cases but returns stored `1` on the
D0 sentinel path, producing five return mismatches. The automatic public-only
repair preserves both passing bodies and fixes the D0 return. Its second proposal
passes all 1,404 public/held-out cases, twice per side in fresh processes. The
compiled D0 negative control produces five stable mismatches and 335 passes.
The separate [Sol source review](reviews/object-counters-001-source.json) approves
the exact tested implementation. No Sol implementation escalation or manual source
repair was needed.

The [worker measurements](pilots/object-counters-001.json) retain both attempts:
three pipeline requests, 130,924 reported input tokens, 2,167 output tokens,
35.997 seconds of summed request latency, and 382.738 seconds of pipeline elapsed
time. Five infrastructure assignments across three agents are recorded separately;
their usage and coordinator/account charges were not measured.

Integration copies the accepted source unchanged and promotes exactly three
registry status fields from `contracted` to `implemented`. All identities, ABI,
source and contract paths remain identical to the frozen packet. The source-review
record retains both registry hashes and that mechanically checked transition;
current-checkout evidence is published separately by the full checkpoint.

The [integrated checkpoint](validation/object-counters-001.json) passes all 16
recovered functions across 5,562 input cases, 95 tooling tests, CTest, both
synthetic demonstrations and all three game negative controls. The reference
slices ran under Unicorn 2.1.4 on macOS arm64; the C++ build used AppleClang 21.

Original bytes, caller contexts, characterization probes and worker outputs stay
under ignored `local/pilots/`, `local/pairs/` and `reports/`. These results remain
bounded emulator corpus evidence, not a proof of complete function or game behavior.

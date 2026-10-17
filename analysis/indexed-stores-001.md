# Indexed store recovery group 001

Two pinned main-executable leaves write an indexed object field. Their original
names, class and subsystem remain unknown.

| RVA | Bytes | Accepted write |
| --- | ---: | --- |
| `0x00347d10` | 27 | Low 16 value bits at object + `0x12a` + 2 × index low byte |
| `0x00347d50` | 25 | Low 8 value bits at object + `0x138` + index low byte |

Only index low bytes 0 through 6 are accepted. Accepted calls return that low
byte zero extended. Rejected calls leave all memory untouched and return the
incoming EAX upper 24 bits with its low byte replaced by the index low byte.
Both stack arguments occupy full u32 slots; the callee pops eight argument bytes.
Original instruction slices and eighteen direct caller contexts support these
boundaries. ECX is preserved, and callers reuse it between calls.

The fixture domain is an initialized 512-byte ordinary RAM allocation with an
object offset from 0 through 128, allowing any byte alignment. No arena reads
are allowed. Only the selected byte or word can be written on accepted paths;
rejected paths permit no arena access. Every arena byte and all EAX bits are
compared. The original adapter also checks ECX, nonvolatile registers, stack
balance and DF. A C++ object argument passed by value represents the logical
object pointer; this is not a tested x86 ABI bridge. Other volatile-register and
flag effects are outside this boundary and need caller-dependent treatment when
composing functions or building that bridge.

Each function has 1,304 public and 128 held-out deterministic fixtures from
independent original-only characterization. Public inputs cover all 256 low
index bytes, incoming EAX upper bits, high index bits, accepted-slot truncation
and walking bits. The negative control preserves memory but wrongly clears EAX
upper bits for rejected word-store indexes. The checked GuestMemory extension
validates the complete narrow footprint before writing, including unaligned
little-endian words. Faults, MMIO, concurrency, exceptions, address wrap, full
class layouts and native Windows execution are outside the tested domain.

The [independent acceptance-system review](reviews/indexed-stores-001-contract.json)
approves 34 exact input hashes. It checks all 2,864 original fixture states and
18 repeats, 80 fresh-process adapter runs, and 2,046 previous memory/counter cases
against the preceding oracle. All 104 project tests, the C++ memory checks and
both synthetic demonstrations pass. This review approves the acceptance system,
not the candidate.

Luna's first implementation passed all 2,864 positive cases, twice per side in
fresh processes. The full public return-only negative control produced 747 stable
mismatches and 557 passes. The separate [Sol source review](reviews/indexed-stores-001-source.json)
approved the exact tested source without repairs or escalation. Integration
copies it unchanged and promotes only the two registry status fields. The [integrated checkpoint](validation/indexed-stores-001.json) passes all
18 recovered functions across 8,426 input cases, 104 tooling tests, CTest, both
synthetic demonstrations and all four game negative controls. Original execution
used Unicorn 2.1.4 on macOS ARM64; the native C++ build used AppleClang 21.

[Worker measurements](pilots/indexed-stores-001.json) record two pipeline requests,
123,346 reported input tokens, 1,067 output tokens and 23.441 seconds of summed
request latency. Pipeline elapsed time was 768.380 seconds, mostly deterministic
execution. Infrastructure assignments and coordinator usage are separate; their
token usage and account charges were not measured. Raw instructions, probes and
fixtures remain under ignored local/pilots/ and local/pairs/. Measurements are
bounded emulator evidence, not a proof of universal function or game equivalence.

# Bounded linked-list unlink recovery

`fn_00018400` removes a requested node from the adjacent linked-list group. It is
identified by DAOrigins.exe SHA-256
`2346caee611002d4dff6ecef68eb315b63a37004dd98b39c11a9c26c0b45bfb3`,
RVA `0x00018400`. The 78-byte contiguous capture includes a three-byte unreachable
alignment gap; its SHA-256 is
`c5eeb9077a1596efc91e13f4cd9218ff0e93fed2e4aa349a87b31578edd18754`.

The accepted C++ source hash is
`9916d667a9ed2a35a129ca8accbedc5248b8e926040c2f686b0b9cc869e10e96`.
Its API explicitly returns full EAX and the observed ECX value. Parameters are
arena offsets; stored links and register observations are raw guest addresses.
It searches the active chain, repairs the predecessor/head and successor/tail
links when found, and preserves the removed node's bytes in the disjoint domain.
The found-tail path returns zero: the final predecessor load is into EDX, not EAX.

The frozen domain is ordinary initialized 512-byte RAM containing a disjoint
32-byte list and four distinct 12-byte node allocations. The active chain is a
canonical finite ordered subset of that pool; the target may be inactive. Objects
may be unaligned, and a node at arena offset zero is distinct from null. Reads,
writes, complete arena bytes, EAX, and conditional ECX are checked. The original
adapter also checks RET 4, preserved registers and the precisely bounded optional
ESI stack save. This is not a native x86 calling-convention bridge.

On macOS ARM64, AppleClang 21 C++20 candidate execution agreed with Unicorn 2.1.4
original execution for 1,040 public and 128 held-out inputs, repeated twice per
side. The ECX negative control produced 528 expected mismatches and 512 passes,
with no errors. Synthetic controls also passed. These are bounded corpus results,
not universal proof or native Windows game evidence. Whole-game behavior,
allocation/lifetime, synchronization, concurrency, aliases, malformed graphs and
fault/MMIO behavior remain outside this contract.

An independent Sol medium review approved the exact source after all deterministic
gates. A preceding Luna reviewer rejected it using an earlier candidate's failed
report and an EDX/EAX decoding error. That rejection is retained alongside the
subsequent independent adjudication; it was not silently overridden. The earlier
malformed packets, incomplete support snapshots and two failing Luna source
proposals also remain recorded.

Eight distinct CLI model requests were used across this group's implementation
and source reviews: five Luna and three Sol, including failed requests. Reused
responses are counted once. Seven preparation/acceptance assignments are recorded
separately with unavailable token usage. See the [pilot accounting](pilots/linked-unlink-001.json),
[contract review](reviews/linked-unlink-001-contract.json), and
[source review and integration binding](reviews/linked-unlink-001-source.json).
Coordinator usage and account quota attribution are unknown. Full-checkout
regression evidence passed for all 21 implemented functions and 10,366 inputs,
with seven negative controls and 125 tooling tests. See
[the refreshed record](validation/linked-unlink-001.json).

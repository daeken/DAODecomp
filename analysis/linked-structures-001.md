# Linked structure group 001

The next group contains two pinned `DAOrigins.exe` slices from build SHA-256
`2346caee611002d4dff6ecef68eb315b63a37004dd98b39c11a9c26c0b45bfb3`.
The two implementations passed frozen deterministic checks and independent
source review. The integrated macOS ARM64 checkout passed the complete regression:
20 functions, 9,198 positive inputs, six negative controls, 120 tooling tests,
CTest and both synthetic demonstrations. These remain emulator corpus results;
native Windows original-game execution has not run.

| RVA | Extent | Original behavior under disjoint graph preconditions |
| --- | ---: | --- |
| `0x00018390` | 56 bytes | Append a node; ECX is list, one node-address stack slot, ret 4, full EAX is node address |
| `0x000183d0` | 44 bytes | Pop head; ECX is list, no stack arguments, full EAX is previous head or null |

The list endpoints are at `+0x18/+0x1c`; node next/previous links are at `+4/+8`.
Empty append clears node links and sets both endpoints to the node address.
Nonempty append reads the tail twice, with a write between those reads; old-tail
next is written, never read. Pop leaves removed-node storage unchanged only under
the disjoint preconditions. Self-loops and object overlap invalidate that claim.

Luna's first characterization was independently audited by Sol. The audit
corrects empty-append prose, excessive proposed read permissions, VA/RVA labels,
a fixture generator that only handles prefix chains, and an unqualified link
retention statement. The original handoff is preserved alongside those corrections.
Seven existing fixtures were unaffected. The independent audit records 176 original
executions, including repeated canonical, permuted, unaligned, edge and alias probes;
these remain exploratory original-only evidence, outside README recovery counts.

Caller and import bytes identify Windows event-node use: CreateEventA initializes
a node payload; pop callers use SetEvent; the append caller retains the node across
WaitForSingleObject and returns it through a ResetEvent/free-list helper. A waiter
protocol and synchronization wrappers are inferences from these calls. Runtime
behavior, lifetime and failure handling have not been validated on Windows.

The historical review proposed up to four nodes. Current acceptance preparation
chooses one 512-byte ordinary RAM arena, a disjoint 32-byte list and exactly four
distinct 12-byte pool nodes. A 16-byte metadata input encodes their four offsets;
that metadata is a fixture precondition, not an original machine argument. The
active chain is finite, reciprocal and has consistent endpoints. Append accepts
zero through three active nodes plus an inactive pool node; pop accepts zero
through four active nodes. Inactive stale links and payloads may be arbitrary.
Literal pointer zero is null; arena offset zero is the valid non-null address
`0x02000000`. Both implementations return full raw guest EAX without pointer
normalization, and the whole arena is observed.

The acceptance backend passed independent review before freezing contracts,
exact branch footprints, mapping, corpus and fresh-process adapters. Held-out
composition snapshots cover append, drain and reappend of a removed node; an
original-only replay feeds measured after-arenas into the following operation.
Candidate differential checks cover each frozen snapshot. These are finite RAM
sequence observations, not live Windows caller or concurrent composition tests.
The full-public negative controls corrupt append's raw return and pop's retained
forward link respectively.

Luna's first implementation passed all 516 public and 256 held-out inputs, each
run twice per side in fresh processes. Both full-public negative controls failed
as intended: 256 append mismatches and 240 pop mismatches, with 20 unaffected pop
cases. A separate Sol reviewer approved the exact source after these gates.
The [contract review](reviews/linked-structures-001-contract.json) and
[source review](reviews/linked-structures-001-source.json) retain their scopes,
bindings and limitations. Worker measurements are in
[the pilot record](pilots/linked-structures-001.json); the final checkout has
[fresh regression evidence](validation/linked-structures-001.json).

Local evidence: `local/pilots/linked-structures-001/independent-review.json`, raw
SHA-256 `94d1744c100896c6569157d61b1c16722a128c68d1499aebeb8b984d408e5982`.
The report binds original instructions, callers, scripts, inventory and probes.
Measurements ran under Unicorn on macOS ARM64. Game integration remains blocked
on allocator/event failures, object lifetime, synchronization and concurrent
schedules. The adjacent unlink operation can be characterized independently
against the same original build and graph invariants.

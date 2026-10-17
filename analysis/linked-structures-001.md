# Linked structure group 001: original evidence

The next group contains two pinned `DAOrigins.exe` slices from build SHA-256
`2346caee611002d4dff6ecef68eb315b63a37004dd98b39c11a9c26c0b45bfb3`.
No candidate implementation or acceptance system is approved yet.

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

A proposed first contract uses one 512-byte ordinary RAM arena, a disjoint 32-byte
list and up to four distinct 12-byte nodes. The active chain is finite, reciprocal
and has consistent endpoints. Inactive stale links may be arbitrary. Literal
pointer zero is null; arena offset zero is a valid non-null guest address. Graph
fixtures must preserve that distinction and compare all arena bytes and return bits.
This bounded proposal still needs reviewed contracts, exact branch footprints,
pointer mapping, fresh-process adapters, composition cases and negative controls.
It does not authorize implementation from the current handoff alone.

Local evidence: `local/pilots/linked-structures-001/independent-review.json`, raw
SHA-256 `94d1744c100896c6569157d61b1c16722a128c68d1499aebeb8b984d408e5982`.
The report binds original instructions, callers, scripts, inventory and probes.
Measurements ran under Unicorn on macOS ARM64. Game integration remains blocked
on allocator/event failures, object lifetime, synchronization and concurrent
schedules; isolated memory-contract preparation can proceed independently.

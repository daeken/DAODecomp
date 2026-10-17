# Memory recovery group 001

This group extends the scalar backend to exact memory observations. It contains
three dependency-free leaves from the pinned main executable:

| RVA | Bytes | Reviewed ABI | Observations |
| --- | ---: | --- | --- |
| `0x00061fa0` | 35 | ECX destination, stack source, `ret 4` | Four sequential 32-bit loads/stores; EAX destination pointer |
| `0x0013af20` | 47 | ECX destination, stack source, `ret 4` | Six sequential 32-bit loads/stores; EAX destination pointer |
| `0x0035bc40` | 44 | Stack base/index/enabled, `ret 12` | Set/clear one indexed bit; EAX is `index >> 5` |

Original names and subsystem ownership remain unknown. Ghidra boundaries and
call references were checked against Capstone disassembly, two caller contexts
for each copy, and the bit routine's caller. A second LLVM disassembly covers
every byte of each slice. No selected slice overlaps a PE base relocation or
contains calls, globals, floating-point instructions or private stack writes.

The fixture is one 128-byte allocation at guest address `0x02000000`. Serialized
pointer offsets preserve equality, arbitrary byte alignment and partial overlap.
Only source bytes may be read by the copies, only destination bytes written; the
bit routine may access only its selected four-byte word. Every byte of the arena
is compared afterward, including canaries. The two copy returns are normalized to
allocation offsets. The bit routine's full EAX value is retained even though the
observed caller ignores it; this is a stronger explicit observation, not an inferred
original C++ return type.

The C++ `GuestMemory` view uses checked, little-endian byte accesses. It avoids
host pointer casts, alignment assumptions and effective-type violations. A full
word is read before the corresponding word is written. This order matters for
partial overlap: a normal snapshot copy can produce different results.

Frozen public suites have 37, 53 and 264 cases respectively; held-out suites have
80, 80 and 128. They cover self-copy, both overlap directions, disjoint and
unaligned ranges, boundary bits, varied upper flag bits, and changing memory
canaries. The reference CPU and both processes are reset for every case and repeat.
The negative control deliberately snapshots all source words before writing.
Backend tests reject out-of-footprint access, stack writes, clobbered registers,
bad direction flags, out-of-slice execution and exhausted instruction budgets.

An [independent contract/oracle review](reviews/memory-001-contract.json) approves
this bounded acceptance setup, with no candidate approval implied. It also checks
82 overlap states and 2,048 bit states directly against original execution, and
confirms a stable memory mismatch from the overlap negative control.

Luna's first proposal passes both copy suites on public inputs. The bit routine
has correct memory writes but returns the new word instead of EAX's word index:
9 public cases pass and 255 mismatch. Its automatic repair returns the full index
and still fails 240 public cases. One Sol escalation fixes the return to
`index >> 5`, preserving the already-passing copy bodies. All 642 public and
held-out cases then pass, with two fresh executions per side; the overlap mutant
produces 12 stable mismatches. These failures and repairs remain recorded.

The first independent candidate review requested clearer execution provenance.
The pipeline accepted no package. After correcting the evidence package and
rerunning the deterministic gates on the unchanged source, a separate review
approved the scoped implementation. Its prose incorrectly totals 742 cases; the
actual reports establish 642. The [preserved source review](reviews/memory-001-source.json)
and [worker measurements](pilots/memory-001.json) retain this distinction.

Both copies succeeded on Luna's first proposal; the bit routine required Sol.
Across the original proposal and three pipeline invocations, seven distinct model
requests consumed 195,223 reported input tokens and 5,976 output tokens, including
two wasted requests from an early snapshot-configuration error and the refused
review. Those costs are retained. They exclude coordinator and infrastructure-audit
usage, and are not measured account charges. Preflight checks now reject that
configuration error before spending another implementation request. The
[workflow audit](reviews/paired-workflow.json) covers the final pipeline and
automatic checkpoint tools.

The integrated checkpoint passes all 13 recovered functions across 4,158 input
cases, 85 tooling tests, CTest, both synthetic demonstrations and both game
negative controls. Its [current evidence](validation/memory-001.json) refreshes
the earlier scalar results too. Original execution used Unicorn 2.1.4 on macOS
arm64; candidate builds used AppleClang 21. All 19 originally frozen acceptance
inputs remain unchanged.

These are bounded emulator observations, not a native Windows result or a proof
over every possible allocation, address, machine state or compiler. The original
binary, disassembly, frozen packet, initial failure reports and worker logs stay
under ignored `local/pilots/memory-001/`, `local/pairs/` and `reports/`; accepted
evidence summaries retain identities and hashes in `analysis/validation/`.

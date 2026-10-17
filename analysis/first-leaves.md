# First recovered functions

Reference: `DAOrigins.exe`, SHA-256
`2346caee611002d4dff6ecef68eb315b63a37004dd98b39c11a9c26c0b45bfb3`.
The registry records exact slice hashes, contracts, and source paths. These names
describe behavior; original names and subsystem/middleware ownership are unknown.

## RVA 0x0004a3f0 — byte_swap_u32

The 31-byte function takes one 32-bit stack argument and returns in EAX, with a
plain return instruction. It assembles the input's four bytes in reverse order
using AH/AL, zero extension, shifts and ORs. Every output bit is assigned
independently of incoming volatile registers or arithmetic flags. The only data
reads are the argument and return address. No memory writes, calls or globals.

LLVM's disassembly identifies a direct call at RVA `0x4697a`. Adjacent alignment
padding is outside the slice. The C++ implementation uses only unsigned 32-bit
operations with constant shift counts below 32.

## RVA 0x000518a0 — bit_mask_or_all

The 21-byte function takes one 32-bit stack argument and returns in EAX, with a
plain return on each path. It compares the argument to all ones. That sentinel
returns `0xffffffff`; otherwise it shifts the constant 1 by CL. The processor uses
the low five count bits for a 32-bit shift, so e.g. inputs 0, 32 and 64 all return
1. The C++ explicitly masks the count to preserve that behavior without undefined
shifts. The sentinel branch's OR with all ones overwrites every return bit.

Observed direct callsites: RVAs `0x55223`, `0x55681`, `0x5568a`, `0x6e6cb`.
No memory writes, external reads or calls occur within the slice.

## Evidence and scope

LLVM and Capstone independently decode the slices consistently. Inspection of the
PE base relocation table finds no relocations overlapping either slice. Ghidra
output is retained separately under ignored `local/analysis/`; inferred signatures
are hypotheses, not a substitute for the instruction evidence.

`validation/validate_leaves.py` reads the user's original EXE; no copied game
instruction bytes are embedded in tracked tests. It verifies the complete module
and slice hashes before executing. The original runs in Unicorn x86 at its original
virtual address. Only the code, a private stack and a return sentinel are mapped.
Instrumentation rejects reads beyond the argument/return-address footprint, all
memory writes, execution beyond the slice, nonvolatile register corruption,
incorrect stack cleanup, a set direction flag on return, or exhausted instruction
budget. The result is compared with compiled C++ on the local host.

The deterministic corpus covers small shift counts, every single bit and its
complement, special byte patterns, signed/unsigned boundaries and SHA-256-derived
inputs. Each side executes twice in fresh processes. A separate mutant discards
the all-bits sentinel and must fail with an ordinary semantic mismatch.

This establishes agreement on the recorded corpus under the emulator and reviewed
contract. It is not exhaustive enumeration, an SMT proof, a native Windows run or
evidence of whole-game behavior. Arithmetic flags and volatile registers are
excluded by the cdecl contract; caller-visible memory writes are forbidden, not
silently ignored. Other instruction forms or stateful functions require separate
review and a richer backend.

Run:

```sh
.venv/bin/python validation/validate_leaves.py
.venv/bin/python validation/validate_leaves.py --expect-mismatch
```

Generated full reports are in `reports/`. The checked-in validation record identifies
the actual host, build, corpus, result and report hashes for this initial recovery.

# SharpRetro evaluation

Current pin: `ec8344102af8b495e5de1a869188b91bc3d4d756`, the reviewed effective
address-size correction to the initial `685b7578457cad325226aa8923b45ded35098fa3`
baseline. Both were built and measured on 2026-10-19. SharpRetro remains an
external dependency. Building and comparing lifted trees does not certify its
instruction semantics.

## Implemented diagnostic tool

The [paired-lift CLI and reproduction instructions](../tools/sharpretro/README.md)
consume retained, attested COFF artifacts and the pinned original. They freshly
repeat the unchanged relocation-aware comparison, lift both complete ranges using
`XFusionCpu.X86Lifter` in Bits32 mode, and serialize typed LiftIl records with
lossless constants and explicit register, flag, memory and control-flow effects.
Capstone independently checks instruction lengths and complete boundary coverage.
An explicit external checkout/build manifest binds sources, assemblies and runtime
dependencies. No compiler VM or original game execution is needed.

The adapter reports exact tree agreement, differing supported IL, opaque or
unsupported operations, or incomplete lifting. It performs no register renaming,
address normalization, instruction dropping or semantic acceptance. Unsupported
context remains explicit even when both trees look identical. "Supported" means
that the pinned lifter emitted modeled nodes and decoder checks agreed; it does
not mean those semantics have been independently certified.

A deterministic size-stratified sample from the [mismatch census](mismatch-analysis.md)
contained 30 nonmatches: 25 produced differing supported IL, four were opaque or
unsupported, and one had an incomplete lift. All ten exact controls had identical
raw trees, but one contained opaque operations and therefore did not receive the
supported-agreement label. Across 80 function sides, 71 were fully supported and
79 had full decoder/boundary agreement. The 3,235 decoded instructions included
720 opaque instructions, mostly x87; a 27-byte undecoded suffix was retained.
The final pilot took 13.883 seconds on macOS ARM64 with no VC8 builds or provider
calls. These selected proportions are not whole-inventory coverage estimates.

Twenty-six focused machinery tests cover lossless serialization, distinct ADD
encodings yielding the same tree, changed registers/immediates/flags/memory/widths,
call and return mutations, incomplete decoding, opaque operations, context and
artifact-binding refusals. Independent review reproduced five representative real
pairs and the focused controls. Existing acceptance and published-source counts
are unchanged. Dependency build products and raw input/output evidence stay local.

## Address-size correction

The initial lifter computed ModRM offsets in a 64-bit carrier even for narrower
decoded address sizes. Base/index overflow and signed displacements could produce
the wrong effective offset. The generic fix truncates the completed offset to
the decoded address size and zero-extends it **before** adding a segment base.
Operand size is independent; FS/GS bases may contain higher bits.

The [two-file upstream change](https://github.com/daeken/SharpRetro/pull/2)
adds 24 generic NUnit cases: 19 failed on the old
implementation, and all 24 pass after the fix. All 278 upstream tests pass on
macOS ARM64 with .NET 10. A separate Capstone 5.0.6 / Unicorn 2.1.4 address-effects
comparison agrees on 245 generated cases, versus 171 disagreements with the
original implementation. An independent reviewer repeated these checks and added
11 passing controls. This is emulator evidence, not native hardware certification.

Replaying the same 40 diagnostic pairs took 13.437 seconds. Address trees changed
in 39 pairs / 76 sides / 1,413 instructions; every diagnostic category and all ten
exact controls were preserved. No new match or equivalence credit results from
this correction. The adapter must be rebuilt and its manifest refreshed explicitly
when adopting the new pin. The original reports and dependency builds are retained.
The adopted DAO adapter was rebuilt, then all 40 inputs were replayed in 13.692
seconds with identical reviewed trees and diagnostics (elapsed times excluded).
Configured tooling discovery passed 296 tests with seven unrelated optional skips.

The correction covers ModRM effective offsets only. Default segment selection,
segment limits/faults, LEA segment overrides, moffs/string addressing, paging and
unrelated instruction semantics remain outside its scope. The pilot's incomplete
27-byte suffix was traced to embedded jump-table data, not a missing instruction;
it remains an explicit incomplete linear lift. Most opaque operations are x87.

## Earlier semantic-checking research

The existing `XFusionCpu.X86Lifter` goes from decoded instructions and operand
bindings through `IlLower` to `LiftIl`. That IR has typed arithmetic/casts, register
reads/writes, loads/stores, branches, conditions and explicit flags. This is a
promising front end for a restricted instruction-to-SMT translation and can also
provide structured evidence for decompilation agents.

The boundary to respect is the difference between decoding an instruction and
having complete execution semantics. `x87.isa` represents its operations as
intrinsics; its comments place execution in a separate stack-machine tier. The
lifter also deliberately emits opaque intrinsic nodes. A proof backend must reject
an unmodeled intrinsic or supply a reviewed semantics model. It must also handle
undefined flags appropriately; retaining an old flag value is not automatically a
sound model of every hardware behavior when the architectural flag is undefined.

Recommendation: retain Ghidra for initial whole-program discovery and Unicorn/native
execution for independent evidence. Evaluate SharpRetro first on the actual integer
instruction subset in our chosen game functions. Avoid making an entire symbolic
x86 engine a prerequisite for decompiling the game.

The following remains future research, not a prerequisite for the diagnostic tool:

1. Pin SharpRetro and export a lossless, versioned LiftIl serialization for a small
   function and its compiled candidate; retain addresses and instruction bytes.
2. Translate supported bitvector/register/memory/control-flow operations to SMT.
   Reject unknown operations, implicit narrowing, unsupported addressing and traps.
3. Validate each used instruction's pre/post-state against an independent native
   or emulator reference, including flags, partial registers and memory footprints.
4. Check complete path coverage for a loop-free function; compare both end-state
   relations. Verify a mutation produces a replayable counterexample.
5. Expand only when these checks cost less than the confidence they add. Keep x87,
   complex SIMD, OS effects and concurrency outside the initial proof subset.

Using one semantics implementation to generate both the recovered code and its
expected outputs can hide the same bug on both sides. Retain independent native
execution even if SharpRetro eventually becomes the primary lifter.

Source anchors:

- [X86Lifter](https://github.com/daeken/SharpRetro/blob/685b7578457cad325226aa8923b45ded35098fa3/XFusionCpu/X86Lifter.cs)
- [LiftIl node definitions](https://github.com/daeken/SharpRetro/blob/685b7578457cad325226aa8923b45ded35098fa3/LiftIl/Il.cs)
- [x87 boundary](https://github.com/daeken/SharpRetro/blob/685b7578457cad325226aa8923b45ded35098fa3/XFusionGenerator/x87.isa)
- [Existing differential-validation scoping](https://github.com/daeken/SharpRetro/blob/685b7578457cad325226aa8923b45ded35098fa3/rust/xfusion-recomp/DIFFERENTIAL-SCOPING.md)

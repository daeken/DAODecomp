# SharpRetro evaluation

Pinned revision `685b7578457cad325226aa8923b45ded35098fa3` was inspected on
2026-10-17 and built for paired IL diagnostics on 2026-10-19. No SharpRetro source
has been vendored into DAODecomp. Building and comparing lifted trees does not
certify its instruction semantics.

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

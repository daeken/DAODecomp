# SharpRetro evaluation

Inspected revision `685b7578457cad325226aa8923b45ded35098fa3` on 2026-10-17.
This is a source inspection, not a build or certification of its instruction set.
No SharpRetro source has been vendored into DAODecomp.

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

Proposed experiment:

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

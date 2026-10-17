# Recovered source

`primitives.cpp` contains the first two recovered functions: a 32-bit byte swap and
a bit-mask helper with an all-bits sentinel. Their names describe observed behavior;
original names and subsystem ownership remain unknown. Binary identities, contracts
and evidence are recorded in `analysis/functions.json` and `analysis/first-leaves.md`.

`scalar_integer.cpp` and `scalar_byte.cpp` contain the low-cost model pilot's
arithmetic and byte-processing routines. Their stable RVA names avoid treating
model-suggested labels as original symbols. The pilot record separates Luna output,
counterexample-guided repair and Sol escalation; see `analysis/pilots/luna-001.md`.

`memory_primitives.cpp` contains sequential word copies and a bit mutation routine.
Its checked `GuestMemory` interface preserves byte alignment, aliasing and exact
write footprints without host pointer casts. See `analysis/memory-001.md` for the
bounded fixture, independent contract review and paired implementation workflow.

Add modules based on the observed call graph and ownership boundaries, rather than
guessing the game's subsystem layout. Keep ABI bridges separate from portable
behavior. The native C++ has corpus agreement with emulated original instructions;
native Windows checks and whole-game integration remain outstanding.


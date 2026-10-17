# Recovered source

`primitives.cpp` contains the first two recovered functions: a 32-bit byte swap and
a bit-mask helper with an all-bits sentinel. Their names describe observed behavior;
original names and subsystem ownership remain unknown. Binary identities, contracts
and evidence are recorded in `analysis/functions.json` and `analysis/first-leaves.md`.

Add modules based on the observed call graph and ownership boundaries, rather than
guessing the game's subsystem layout. Keep ABI bridges separate from portable
behavior. The native C++ has corpus agreement with emulated original instructions;
native Windows checks and whole-game integration remain outstanding.


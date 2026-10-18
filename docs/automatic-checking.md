# Checking without per-function authoring

The inputs are the pinned original executable and decompiled C++. A function's
RVA is already present in its name. There are no additional authored contracts,
fixtures, test corpora, wrappers, expected outputs or proof annotations. The
generator runs independently; checking never holds up unrelated decompilation.

This replaces the previous validation preparation approach. The new fixture-based
validator assignment was stopped before launch. No new semantic checker is
implemented or running at this checkpoint.

## First implementation: automatic differential execution

Build one reusable engine around the common guest-state interface. The engine
obtains register and memory states automatically, executes the original and C++
from independent copies, and compares their effects. It creates the native bridge
and compiler products internally from the candidate's exported RVA names. Nobody
writes a function-specific adapter or expected result.

Two input sources serve different purposes:

- Automatically generated machine states can find mistakes in integer and memory
  routines immediately. They establish only what those executions observed; an
  arbitrary machine state is not necessarily a reachable game state.
- Captured function-entry states from actual game execution supply initialized
  objects, globals and alias relationships for stateful code. A generic recorder
  and replay engine should collect these, rather than people designing fixtures.
  Captures remain local and are derived evidence, not authored inputs.

Use deterministic seeds or replay records, independent memory snapshots, bounded
execution and repeatability checks. Compare return/stack behavior, guest state,
memory changes and external effects that the engine actually models. Unknown
calls, exceptions, missing memory, unsupported instructions and timeouts produce
unknown outcomes. Matching faults do not establish equivalence. Missing semantics
must not become successful stubs.

The engine saves the first reproducible difference with the exact binary, source,
compiler and input identity. Repairs consume that automatically produced
counterexample. Passing executions yield **no difference observed**, never an
unqualified equivalent label. No manual counterexample-to-corpus maintenance loop
is required.

## Stronger checks where automatic reasoning is practical

Translation validation can compare the original machine code with compiled C++
through a common symbolic representation and ask whether an observable difference
exists. The shared guest-state interface supplies a reusable state relationship;
it avoids guessing and authoring a new signature for every function.

This needs real implementation work, especially around memory, calls, loops and
instruction semantics. A lifter is not itself an equivalence checker. A solver
result only supports a bounded or otherwise explicit domain when both programs'
paths are fully represented there. Unsupported paths, memory concretization,
timeouts and incomplete exploration remain unknown. Do not introduce handwritten
invariants or per-function proof scripts merely to obtain a passing label.

The practical sequence is automated counterexample discovery first, real-state
capture/replay for stateful functions, and symbolic checks for suitable small
functions. All three consume the same C++ output; none creates an additional
authoring assignment for each decompiled function.

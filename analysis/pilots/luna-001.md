# Scalar recovery pilot: Luna 001

This is a deliberately small **packet-to-C++** experiment, using eight reviewed
scalar functions from the pinned `DAOrigins.exe`. It measures implementation after
the coordinator has identified boundaries, calling conventions, valid input domains
and observable state. It does not measure autonomous discovery, whole-program
decompilation or production cost at scale.

The worker receives original disassembly, unsigned bit-pattern interfaces and ABI
facts, with neutral RVA names. It receives neither decompiler pseudocode nor the
test corpora. Two four-function batches use `gpt-6-luna` at medium reasoning effort,
with one repair attempt per batch, then a single-function `gpt-6.1-sol` escalation.
Workers run through the logged-in Codex CLI in a read-only sandbox and return
structured source text; the coordinator reviews, compiles and tests it. Each
invocation has a 180-second time limit. There is no unattended queue or auto-merge.

## Characterized functions

All addresses below are RVAs in the main executable. Original names and subsystem
ownership remain unknown. No selected slice overlaps a base relocation or contains
calls, globals, memory writes, floating-point instructions or loops.

| RVA | Bytes | Input / observed result | Behavior inferred and checked |
| --- | ---: | --- | --- |
| `0x184920` | 15 | stack / EAX, callee removes 4 argument bytes | Increment modulo 256 |
| `0x52aad0` | 15 | stack / EAX | Unsigned division by 20 |
| `0x5851a0` | 22 | stack / EAX | Signed division by 20, truncating toward zero |
| `0x5c0c00` | 78 | ECX / EAX | Divisible by 4 and either not by 100 or by 400 |
| `0x4d79c0` | 13 | AL / AL | ASCII uppercase-to-lowercase conversion |
| `0x4b6e70` | 13 | CL / AL | ASCII uppercase predicate |
| `0x4b65b0` | 33 | CL / AL | ASCII hexadecimal-digit predicate |
| `0x4b64d0` | 30 | CL / AL; ECX preserved | Reject outside `0x20..0x7d`, or `%`, double quote, apostrophe |

The last predicate accepts space and rejects tilde. Those details come from the
instructions, regardless of what a familiar text-escaping routine might do.
The calendar predicate's contract covers every signed 32-bit bit pattern, including
negative values; it does not assume that callers supply ordinary calendar years.
The increment routine's callers also populate ECX, but its body does not read it;
the functional contract therefore needs only the stack argument.

Ghidra supplies the initial boundaries and callsites. Capstone decodes the packet
instructions, the original PE relocation table is checked, and caller disassembly
confirms the selected input and return registers. The exact binary/slice identities
and ABI descriptors are in `analysis/functions.json`. Unknown original return-type
names are not inferred from register width alone.

## Frozen validation

Before dispatch, the coordinator freezes the contracts, ABI runner, shared header,
corpus generator, packet files and generated corpora. Their hashes are retained in
`local/pilots/luna-001/frozen.json`. Workers make no tool calls or file edits.

The public suite includes boundary values, signed extremes, all bit positions,
divisibility boundaries, and every byte value for the four byte functions. Held-out
cases use a separate deterministic hash domain, additional divisibility boundaries,
and all byte values again with varying upper-register bits. The two corpora remain
unchanged through repairs and escalation. Both sides execute twice in fresh
processes; each original execution creates a fresh Unicorn CPU and memory map.

The backend now models stack/EAX/ECX arguments, AL versus EAX returns, declared stack
cleanup and extra preserved-register obligations. Every unexpected memory access,
write, out-of-slice execution, bad return or budget exhaustion fails. An AL return
is explicitly normalized by the original adapter; candidate results are not masked
to conceal incorrect high bits. Unit tests exercise these ABI failure cases.

## Initial findings

Six of eight first-attempt implementations pass the public corpus unchanged. Both
source files compile with the project's strict C++20 settings on the first build.
The two failures are ordinary semantic mismatches, not emulator or runner errors:

- Calendar input `4`: original returns `1`; Luna returns `0`. The implementation
  reverses the non-century branch. Its one retry retains that error and also
  mishandles negative multiples of four. This function is escalated to Sol.
- Escape predicate input `32` (space): original returns `0`; Luna returns `1`.
  The inclusive lower bound was translated as `0x21` instead of `0x20`. Luna's
  single retry corrects this boundary.

Luna also describes both reciprocal routines as division by 10 even though its
generated arithmetic, and the original, divide by 20. The coordinator rejects
those labels; passing code does not make the model's explanation reliable.

## Final results

| Stage | Accepted functions |
| --- | ---: |
| Luna first attempt | 6 of 8 |
| Luna after one repair attempt per failed batch | 7 of 8 |
| After one Sol escalation | 8 of 8 |

All eight final implementations pass 1,556 public and 1,620 held-out cases. The two
previously recovered functions also pass their 340 regression cases: **3,516 cases
in total**, with each side executed twice. There are no runner errors or unstable
observations. The final run takes 245.933 seconds with four independent function
jobs on macOS ARM64, using Apple clang 21.0.0 and a RelWithDebInfo build. The 42
tooling tests and both synthetic controls pass; the game negative control still
detects the deliberately broken sentinel behavior.

| Worker model | Requests | Input tokens | Output tokens | Estimated standard API price |
| --- | ---: | ---: | ---: | ---: |
| GPT-6 Luna, medium | 4 | 84,781 | 3,143 | $0.010050 |
| GPT-6.1 Sol, medium | 1 | 21,907 | 470 | $0.048514 |
| Total | 5 | 106,688 | 3,613 | $0.058564 |

Individual worker requests take 8–14 seconds. The estimate uses published rates
of $0.10/$0.50 per million input/output tokens for Luna and $2/$10 for Sol; no
cached input tokens were reported. Reasoning tokens are included in output tokens.
This is roughly six cents of hypothetical worker inference, **not the total cost of
recovering these functions** or a measured charge to the ChatGPT account.

The [machine-readable experiment record](luna-001.json) preserves first-attempt
failures, retries, source/report hashes, worker usage and elapsed times. The
[validation record](../validation/scalar-pilot.json) binds the accepted results to
their contracts, corpora, build and implementation inputs. Original disassembly,
raw worker logs and full reports remain local; the repository retains their hashes.

## Limits and next experiment

These are selected easy functions with established state contracts, no data-structure
reconstruction and no dependencies. A rate from eight functions cannot predict the
whole game's acceptance rate. There is no native Windows corroboration or symbolic
proof. Covering all 256 byte values is useful finite-domain evidence under the
reviewed ABI, but does not independently prove every possible machine entry state.

Token counts come from CLI completion events. Any dollar figure is an estimate
using published standard API rates, not a charge to the logged-in ChatGPT account.
It excludes coordinator discovery, contract authoring, review, tool execution and
validation. Those costs must be included before drawing a total-cost conclusion.

The next useful sample should include bounded buffers and memory mutations, with
withheld aliasing/length cases. Keep the two-attempt cheap lane and explicit
escalation limit; the failed calendar retry demonstrates why repeated cheap-model
requests must not replace an independent acceptance check.

Sources: [GPT-6 Luna model and pricing](https://developers.openai.com/api/docs/models/gpt-6-luna),
[GPT-6.1 Sol model and pricing](https://developers.openai.com/api/docs/models/gpt-6.1-sol),
[Codex non-interactive runs and usage events](https://learn.chatgpt.com/docs/non-interactive-mode).

# Indexed integer fields, batch 002

Eleven helpers from the pinned `DAOrigins.exe` build now have independently
reviewed C++ implementations: seven getters and four setters at RVAs
`0x347cf0`, `0x347d30`, `0x347d70`, `0x347d90`, `0x347db0`, `0x347dd0`,
`0x347df0`, `0x347e10`, `0x347e70`, `0x347e90` and `0x347eb0`.
Original class names and field meanings remain unknown. The module SHA-256 is
`2346caee611002d4dff6ecef68eb315b63a37004dd98b39c11a9c26c0b45bfb3`.
Per-function slice identities, ABI and domains are in the registry and contracts.

These functions select a field using the low index byte, with six or seven
accepted slots. They preserve the observed byte/word/dword access widths,
little-endian values, rejected-index sentinels and incoming upper EAX bits.
The adapter compares all return bits and every byte of a 512-byte arena, while
the original runner checks ECX, nonvolatile registers, stack cleanup and DF.
Checked narrow reads extend the existing GuestMemory interface; the instruction
execution backend and comparator are unchanged.

The accepted pair ran on macOS ARM64 with AppleClang 21, C++20 RelWithDebInfo,
Python 3.14.7 and Unicorn 2.1.4. All 14,224 public and 1,408 held-out cases passed,
with two executions per side. Four compiled return mutations produced 747, 747,
996 and 750 stable mismatches, respectively, with no runner errors. Build,
tooling, CTest and synthetic checks passed before the independent Sol 6.1 medium
source review. The exact accepted source SHA-256 is
`ac2f8bb857bbd7a72f53347634f9b577409a4b0c41cd061c57437b11552aba35`.
Full-checkout regression publication is a separate gate; consult the current
[validation records](validation/) and generated README progress for its result.

This is bounded emulator corpus evidence, not a universal proof, native Windows
ABI validation or caller/subsystem equivalence. Public fixtures cover every
accepted index. Held-out fixtures omit slots 1 and 3 for `fn_00347e70`, and slots
1, 3 and 5 for `fn_00347e90` and `fn_00347eb0`; the reviewer retained this explicit
coverage limitation. Independent acceptance review also ran 4,224 original-only
probes, which are not independent candidate comparisons. Faults, concurrency,
MMIO, x87 behavior, object lifetime and adjacent larger callers remain outside
the contracts.

The [source review](reviews/indexed-fields-002-source.json) binds the accepted
source, frozen manifest and integration transition. The
[acceptance review](reviews/indexed-fields-002-acceptance.json) binds the prepared
contracts and support. Its [earlier refusal](reviews/indexed-fields-002-acceptance-v1.json)
is preserved: raw fixtures would have made the source-review prompt about 18 MB.
Separating prompt evidence from complete snapshot/hash coverage reduced the
matched preparation measurement to 326,039 bytes; the actual final review
prompt, including run evidence, was 444,736 bytes.

Four distinct CLI requests were spent: three implementations and one source
review, all Sol 6.1 medium. All three implementations were byte-identical; two
retries were wasted on an omitted protected test dependency. The subsequent
interpreter and synthetic-contract snapshot corrections reused that source
without new implementation requests. CLI-reported totals are 299,486 input and
9,868 output tokens, with 128.334 seconds of summed request latency. Five
preparation/acceptance assignments have unavailable token usage. These numbers
do not measure coordinator usage or account quota attribution. Full failure,
gate and usage summaries are in the [pilot record](pilots/indexed-fields-002.json).

The integrated tooling now stops protected test/dependency failures before
requesting source repairs and includes the missing snapshot dependencies.
Integration also records a test-setup correction that explicitly constructs
contracted and implemented registry states, so promotion does not invalidate
the test itself. These coordinator changes preserve the recovered source,
contracts, fixtures and observation rules; the full checkpoint tests the final
checkout before publication.

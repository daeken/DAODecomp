# DeepSeek packet provider

This is provider plumbing for a reviewed frozen implementation packet. A successful
response is an unaccepted source proposal. Pass `OUTPUT/response.json` through the
unchanged `tools/run_recovery_pair.py --initial-response` workflow, including its
deterministic gates and independent review. This client does not run gates, accept
functions, modify registry entries, execute packet/support code, or run tools for
the model. Only the original packet and response-format instructions are sent.
Other snapshot files, existing implementations and heldout corpora are not sent.

The previous high-thinking pilot exhausted 16,384 output tokens and failed strict
JSON validation. The second pilot used low thinking and 32,768 output tokens; it
returned schema-valid JSON in 37.201 seconds (20,813 input and 10,890 output tokens,
including 6,362 reasoning tokens). This motivates the defaults; it does not establish
behavioral equivalence. The provider exposes no retry, tools, model selection, or
arbitrary endpoint option. Each invocation can issue at most one HTTPS request.

## Budget and explicit first-time initialization

The persistent private ledger belongs under the repository's ignored `local/`
directory, for example `local/providers/deepseek-daily`. Do not commit it, reset it,
delete it to regain budget, create a second ledger for parallel workers, or
initialize a new ledger on each day. Every worker must use this same directory.
The API credential remains in `~/.deepseek.key`, outside packets and the ledger.
Only its file path may be configured; the value never goes into argv, environment,
logs, artifacts, subprocesses, exception text, or hashes.

The daily cap is **$50 per calendar day in America/Chicago**, including DST.
An exclusive POSIX lock serializes validation, clock reading, budget checks,
reservation and settlement. Atomic replacements and file/directory fsync preserve
each ledger update. Missing, corrupt, symlinked or incompatible ledger/config files
are refused. An existing output directory also refuses the request; use a fresh
directory for each explicitly chosen retry/new attempt.

First initialization requires an explicit opening debit. For the initial adoption
day, include **$0.05** (50,000,000 nanodollars) to cover the two pre-ledger pilots,
whose peak-price estimates total $0.0452166. Both prior metrics files are hashed
into the opening debit; neither their contents nor any model source is copied.
Run this once only after reviewing/adopting the provider:

```sh
python3 workers/deepseek_packet.py init-ledger \
  --ledger-dir local/providers/deepseek-daily \
  --opening-debit-nanodollars 50000000 \
  --opening-evidence local/pilots/deepseek-direct-fields-001/run.json \
  --opening-evidence local/pilots/deepseek-direct-fields-002/run.json
```

Initialization assigns that opening debit to the local initialization day. If
adoption happens later, account for historical calls on their actual days before
using this client; do not pretend that a newly initialized ledger represents past
days. The initial-debit command deliberately does not permit overwriting or
repairing an existing ledger. `$0` requires an explicit zero argument and is only
appropriate for a truly unused account/provider budget on initialization day.

Attempts retain their reservation day permanently: an in-flight call crossing
midnight keeps its maximum charged against its original day. A new day's calls
use the new day's cap. Settlement never moves old charges into the current day or
forgives an old in-flight call. Completed prior days remain in the same ledger.

Before reading the key or dispatching, each invocation reserves a conservative
maximum at peak rates: $0.30 per million uncached input tokens, $0.006 per million
cached input tokens, and $1.20 per million output tokens. The input estimate uses
one token per serialized UTF-8 request byte plus 2,048 framing tokens; output is
bounded at 32,768 tokens, including thinking. The serialized request must be at
most 250,000 bytes. These are explicit pricing/tokenization assumptions, **not an
authoritative vendor billing statement**. Rates must be reviewed separately if
the provider changes them. Off-peak discounts are not assumed.

Reported valid usage settles the charge to the corresponding peak-price estimate,
including a malformed or truncated completion with valid usage. Missing/invalid
usage, HTTP errors, credential failures, timeouts, and crashes retain the entire
maximum reservation. Unknown reservations are never automatically released.
Settlement is permitted once only; a reported estimate above its reservation is
charged in full and can exhaust the cap. A crash after dispatch may leave only a
reserved record; never infer that no charge occurred from a missing response.
Any later reconciliation of uncertain charges requires a separately reviewed
process using authoritative billing evidence; this client has no reset/refund tool.

## Request a frozen packet

Supply the exact reviewed manifest SHA-256, source root and original packet path.
The client verifies the pinned manifest bytes, packet hash, and frozen
`tools/run_model_packet.py` hash. It extracts that launcher's literal JSON schema
without importing/executing it, checks the supported strict response format, and
binds all function names and binary identities from the manifest. It does not
read contracts, corpora or candidate implementations. The coordinator remains
responsible for reviewing/freezing the packet and for the full manifest/gates.

```sh
python3 workers/deepseek_packet.py request \
  --manifest REVIEWED_MANIFEST.json --manifest-sha256 REVIEWED_SHA256 \
  --root FROZEN_TREE --packet FROZEN_TREE/packet.txt \
  --ledger-dir local/providers/deepseek-daily \
  --output local/pilots/NEW_ATTEMPT
```

Only `https://api.deepseek.com/chat/completions` is used, with
`deepseek-flash`, thinking enabled, low reasoning, JSON-object output and an
absolute 300-second deadline. Redirects are refused, including same-origin
redirects. There is no automatic retry. A fresh invocation, output directory and
reservation are required for an explicitly chosen retry. The response must have
one choice, finish reason `stop`, strict nonduplicate JSON and exactly the frozen
function set. Truncation cannot pass. `response.json` exists only on schema success;
`run.json` records the attempt ID, budget day, bindings, usage, latency, identifiers,
cost estimate and status. Raw thinking/server bodies and request headers are not
persisted. HTTP and exception diagnostics use fixed categories.

Paths must have no symlink components; on macOS use canonical paths under
`/private/var` if using temporary directories. This is not a malicious local-user
security sandbox. The ignored ledger directory and output claims must remain owned
by the coordinator. The ledger's immutable lock file must never be deleted or
replaced while clients are active.

## Offline verification

```sh
python3 -m unittest discover -s workers/tests -v
python3 -m unittest discover -s tests -v
```

Provider tests use synthetic packets, temporary ledgers, actual concurrent local
processes and fake HTTPS objects. They never read a real credential or call a
model/service. They cover budget races, rollover/DST, opening debits, missing and
corrupt state, crash/unknown charges, exact settlement, duplicate settlement,
output reuse, manifest/schema/path safety, redirects, secret echoes, truncation,
absolute timeout, and no retry. These tests establish provider behavior only.

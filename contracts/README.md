# Contracts and work packets

`function.packet.example.json` is an unready template, not a queue item or a
validated schema. Fill all unknown fields from evidence before assigning work.
The executable comparator's v1 contract is demonstrated by
`examples/synthetic/contract.json`; it validates its schema at runtime.

Freeze the oracle, contract, fixtures and shared headers at dispatch. The coordinator
checks those hashes again at review. A worker proposes a patch and evidence; it
cannot promote its own function. This policy is documented but an automated queue,
lease manager and promotion gate are not implemented yet.


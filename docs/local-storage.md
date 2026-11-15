# Local storage cleanup

The November 10 cleanup preserved the extracted original game, one complete original
installer archive, saves, captures, source, function records and recovery evidence.
Private receipts are under `local/cleanup/`.

Removed or compacted items:

- A stale, unindexed temporary Git pack reported as garbage by Git.
- Rebuildable CMake object/library/precompiled-header caches across old builds.
- One byte-identical duplicate installer tar. The remaining complete archive is
  `local/pilots/linked-unlink-001-backend/isolated/dao.tar`.
- 130 derived asset staging trees. Their sources in `gamedata/` remain intact;
  staging recipes and deletion receipts retain the original source/destination paths.
- Windows system trees from 127 inactive Wine prefixes. User profiles, Documents,
  registry files and saves were retained. Recreate these prefixes before reuse.
  The two qualified control prefixes remain complete.
- Raw copies of 20 generated runtime DLLs and nine large logs, after verifying
  exact compressed archives. Each receipt contains a restoration command. For
  example, use `.venv/bin/python local/recomp/startup/archive-bulk-runtime.py
  --restore RECEIPT.json` with an individual receipt from
  `local/cleanup/1794337686053425000/`.
- Duplicate immutable function payloads: 556,840 files were replaced with independent
  APFS clones after SHA verification. All paths and contents remain intact; writes
  are independent. No changed/missing payload was repaired or treated as accepted.

The major cleanup receipts are:

- `local/cleanup/1794336489931498000/report.json`
- `local/cleanup/1794337093285618000/report.json`
- `local/cleanup/1794337686053425000/report.json`
- `local/cleanup/1794337687156818000/report.json`

Their free-space measurements overlap where archive compression and deduplication
ran concurrently, so do not add all deltas as independent savings. APFS-cloned asset
trees also made logical `du` totals much larger than physical disk usage. The volume
reported roughly 76 GiB available after cleanup; subsequent work and other chats can
change that figure.

Full replacement relinking now requires regenerating evicted object caches, and an
old runtime launch needs its archived DLL restored and assets restaged first. This
is an intentional tradeoff while startup/playtesting is paused. The handwritten
workbench lives outside those generated caches and must never be treated as disposable
build output. Do not delete the last installer, original install, source blobs,
contracts or captures to reclaim routine build space.

# GOG installer extraction

Completed on 2026-10-17 using innoextract 1.9. Source: the user's seven files in
`installer/`, labeled `1.05 (a) (10692)`. The installer identifies GOG game ID
`1949616134` and Inno Setup data version `5.6.2 (unicode)`.

From the project root, the successful invocation was:

```sh
innoextract --extract --output-dir gamedata --progress=0 --color=0 \
  'installer/setup_dragon_age_origins_-_ultimate_edition_1.05_(a)_(10692).exe'
```

Pass only the `.exe`; the extractor locates all six adjacent `.bin` parts. The
previously reported error did not reproduce with this invocation, so its cause
has not been established. No installer files were modified or replaced. Extraction
finished with exit code 0 and the log ended with `Done.`

An independent pass compared every listed destination against the MD5 or SHA-1
checksum reported by the installer inventory: **32,850 passed, zero missing or
mismatched**, totaling 39,217,528,098 bytes across the extracted paths. These include
game assets, redistributables, documentation and installer support files. This
checks extraction against the supplied installer metadata; it is not a comparison
against an externally authenticated release manifest.

Evidence is local and ignored by Git:

- `local/extraction/innoextract.log`: full extraction output.
- `local/extraction/installer-inventory.txt`: expected paths and checksums.
- `local/extraction/verify_inventory.py`: the independent verification procedure.
- `local/extraction/verification.json`: per-file verification results.
- `local/manifests/installer.json`: SHA-256 fingerprints of all seven input files.
- `local/manifests/DAOrigins.exe.json`: main executable headers and SHA-256.
- `local/manifests/bin_ship.json`: fingerprints of 17 runtime executables/DLLs.

The tracked `analysis/reference-build.json` pins the main executable and extraction
summary. `gamedata/bin_ship/DAOrigins.exe` is PE32/x86, 10,217,312 bytes, with SHA-256:

```text
2346caee611002d4dff6ecef68eb315b63a37004dd98b39c11a9c26c0b45bfb3
```

The files are ready for binary analysis. Installer scripts, registry setup,
prerequisite installers and the game itself have not been run. Extraction alone
does not establish that the game can launch on this host.

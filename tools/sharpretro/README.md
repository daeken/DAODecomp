# Paired SharpRetro IL diagnostics

This optional repository tool compares the full typed LiftIl trees emitted by
SharpRetro for attested original and retained COFF function ranges. It performs
no compilation, game execution, acceptance, source mutation or publication.
Dependencies are deliberately external; SharpRetro is not vendored.

Use the existing Python environment with Capstone installed, .NET 10, and an
unmodified SharpRetro checkout at commit
`685b7578457cad325226aa8923b45ded35098fa3`. Supply its path explicitly:

```sh
dotnet build tools/sharpretro/adapter/PairedLift.csproj -c Release -p:SharpRetroRoot=/absolute/path/to/SharpRetro
```

Create an ignored configuration file, such as `local/sharpretro-config.json`:

```json
{
  "sharp_retro_checkout": "/absolute/path/to/SharpRetro",
  "adapter_dll": "../tools/sharpretro/adapter/bin/Release/net10.0/PairedLift.dll",
  "build_manifest": "sharpretro-build-manifest.json",
  "original_binary": "/absolute/path/to/pinned/DAOrigins.exe"
}
```

Paths are absolute or relative to the configuration file. The original and VC8
compiler hashes and exact accepted flag list come from the existing source
exporter; no path or build command for the compiler VM is needed.

After the explicit build, capture and review its manifest once:

```sh
python3 tools/sharpretro/paired.py --config local/sharpretro-config.json --record-build-manifest local/sharpretro-build-manifest.json
```

The manifest records the pinned checkout, every tracked C#/project dependency
hash, package assets, adapter source/project hashes, the build command, .NET
information, DLLs and runtime configuration. Normal lifting verifies those
source/DLL/runtime bindings and refuses upstream tracked modifications. Capturing
a new manifest is an explicit trust/update operation, never an automatic repair
of a rejected binding. Retain the actual build log beside the manifest.

For one retained function:

```sh
python3 tools/sharpretro/paired.py --config local/sharpretro-config.json --summary /absolute/path/to/build/summary.json --rva 0x000ca8d0 --output local/paired-diagnostic.json
```

The summary's sibling `candidate.cpp`, `candidate.obj`, `run.json`,
`compiler.json` and `identities.json` must be intact. Source/object/compiler,
module/range, identity-derived symbols, flags and current comparator bindings
are checked. The existing complete relocation-aware comparator is freshly
replayed. Original and relocated candidate ranges are lifted at its resolved
original VA, with raw COFF hashes and relocation provenance retained.

The JSON-lines C# adapter consumes `{id,hex,pc}` and emits every instruction's
raw identity, full decoded fields and typed LiftIl data (not display strings).
Enums retain type/name/value; UInt128 bits use decimal strings. Register/flag,
memory, width/signedness, symbolic live-in reads, call/branch and opaque nodes
are retained. Capstone independently checks full range and instruction boundary
coverage and records operands, register effects and edges. Incomplete decoding
preserves the entire undecoded suffix. An attested extent can include embedded
data; linear lifting does not claim that every byte is reachable code.

States are `exact_lift_tree_agreement`, `differing_supported_il`,
`opaque_or_unsupported` and `incomplete_lift`. Unknown intrinsics/unimplemented
nodes/notes stay opaque. LOCK atomicity and repeat context without an explicit
model are conservatively marked unsupported. No address/temp normalization,
register renaming, instruction dropping, NOP removal or CFG equivalence occurs.
"Supported" only describes the pinned lifter output and decoder checks; it is
not independent verification of its semantic model. Calls retain symbolic
external behavior, not invented dependency semantics. Tree agreement/difference
never changes acceptance, proves function equivalence or proves a working game.

Run the optional actual-lifter synthetic mutation tests explicitly:

```sh
SHARPRETRO_CONFIG=local/sharpretro-config.json python3 -m unittest discover -s tests -p test_sharpretro_paired.py -v
```

Also exercise retained attestation rejection tests by setting
`SHARPRETRO_TEST_SUMMARY` to an intact single-function summary with existing
artifacts. These tests copy and mutate only temporary metadata/files. Without
those explicit configuration inputs, optional tests skip; skipped tests are not
successful lift evidence. Standard tooling validation remains
`python3 -m unittest discover -s tests -v`.

The API is `configure(config_path)`, then `paired(summary_path, rva)`, returning
the same JSON object. Raw `lift_raw` exists for machinery tests and does not attest
a game identity. Keep original inputs, reports, generated binaries and SharpRetro
checkout ignored. No SMT solver, whole decompiler or semantic acceptance engine
is included.

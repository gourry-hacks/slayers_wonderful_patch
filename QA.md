# Release verification — 2026-09-07.1

The rebuilt canonical BIN matches the tested rendering-repair candidate:
`7f446082dc9ae9543fe645cf13cb6ebb8eb59b0770f0a9fe519e18e3643c3ad4`.

The release patcher reconstructed both BIN and CUE from the original Japanese
files. Their SHA-256 hashes and complete byte comparisons match the canonical
outputs. All 41,240 sectors changed from the Japanese disc independently match
the fresh build's sector hashes. Eva's BIN/CUE downloads were refreshed to this
same build. The XOR data occupies 66,927,180 bytes across three parts.

## Rendering and safety checks

- Both menu rendering modes execute correctly in instruction replay, with
  matching 5×7 atlas ink and six-pixel advance. All 301 fixed item/spell names
  fit their 84-pixel advance budget.
- Eighteen dialogue column/stale-register cases verify the R3000 load-delay
  correction.
- All 116 battle layout records execute through the original packet emitter
  for both frames: 232 repaired cases have no out-of-bounds writes or ink
  overlap. The earlier build reproduces 28 cross-buffer cases. Those earlier
  writes remained within the observed rounded allocation; no adjacent-allocation
  overwrite is claimed.
- Battle-label capacity is 14 slots per frame, including the terminal command.
  Both buffers fit inside the unchanged 7,244-byte record with 36 bytes remaining.
- All 41 ELS overlay code/control sections and archive sizes are preserved.
  Executable edits are confined to declared hooks and text slots. The existing
  source-guarded diagnostic-string cave remains; its original diagnostic text
  is unavailable if those original error paths are reached.
- Only 274 sectors differ from the previous English candidate: EXE 12, ELS
  255, MAP font 1, battle font 2, battle layout 4. Every other raw sector,
  including FMVs and archive tables, is identical to that candidate.
- A complete rebuild validates source signatures, changed-sector contents,
  sector bounds, and EDC/ECC before promoting the disc. Injected invalid sizes,
  duplicate/out-of-range sectors, and corrupted output leave the existing disc
  intact.

## Runtime coverage and limits

An isolated PCSX-Redux instance verified clean-boot title/load menus and early
dialogue progression. Migrated field checkpoints verified equipment, items,
magic, stones, and detailed status screens. These field tests are checkpoint
migration tests, not normal memory-card load tests. Load-menu testing covered
the no-data state; no Wonderful card save was available locally.

A fresh emulator process opened the final disc. After migrating an early
story checkpoint, normal progression loaded battle resources from the disc.
All 116 relocated battle record pointers, labels, descriptor/position tables,
and capacity 14 matched the generated asset in RAM. The Special Attack list
displayed SONIC BLADE and D. SLIPPER correctly. No battle asset or battle
object was injected in this test.

Full-game progression, every save/load path, later choices and battles, ending
variants, and a complete audible subtitle timing pass remain unverified.
Old emulator save states retain old code/assets and are unsuitable for
checking an updated disc without explicit migration.

The local workspace retains the detailed report, replay programs, JSON
results, screenshots, and RAM evidence under `qa/menu_fix_20260907/`.

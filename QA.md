# Patcher input update — 2026-09-12

The patcher now verifies and patches only the input BIN. It generates the
single-track CUE from the output BIN name; `--cue` remains accepted but is
optional and ignored. Release 2026-09-12.1 disc contents are unchanged.

- Six end-to-end unit tests pass, covering absent, nonexistent, empty, renamed,
  and differently formatted CUE inputs, verification-only mode, and continued
  rejection of incorrect BIN contents and corrupted patch parts. Run them with
  `python -m unittest discover -s tests -v`.
- A complete production patch from the original Japanese BIN, with a renamed
  CUE containing a BOM, comment, and LF line endings, reproduced the release
  BIN and CUE sizes and SHA-256 hashes exactly.
- The release builder needs only source and target BINs; it checks the generated
  CUE against the pinned target and no longer packages a CUE XOR delta.

# Release verification — 2026-09-12.1

Target BIN SHA-256: `cc774a0661c3943fc6aefe389b732cb8e4264841c7018997534ef1604716e0c8`.

Fixes heap corruption when opening Lina's battle magic menu. The translated
battle-label asset used capacity 14, but its independently allocated clones
still reserved only 1,028 bytes. The header now requests 1,188 bytes, enough
for the object and both GPU packet buffers, including terminal commands.

- Reproduced the old crash in PCSX-Redux: a label's second buffer overwrote
  a neighboring digit sprite's frame pointer with GPU command `0xe1000076`.
- Loaded corrected battle resources from the rebuilt disc in a separate
  emulator process. Lina's six-spell list, cursor movement, cancellation,
  reopening, targeting, and Flare Arrow casting passed. MP fell from 300 to 290
  and control returned to the command menu. This used a migrated early-story
  checkpoint and explicit battle turn selection, not a full clean-boot run.
- Replayed every one of 116 shared spell/item/special labels through the original
  clone and packet-emission routines for both frames. The old clone size fails
  53 of 232 cases; the corrected size has no allocation overruns in 232 cases.
- Only sector 51435 differs from 2026-09-07.2: one allocation-size payload byte
  and EDC/ECC. The changed sector passes independent Redux C checksum checking.
  Executable code, save behavior, translations, and every other sector are unchanged.
- The complete production rebuild matches the emulator candidate byte for byte.
  The XOR patcher reconstructs the same complete BIN/CUE from the Japanese source.

The previous audit below checked the embedded battle-label object, not its
independent clones. Its buffer results did not establish clone heap safety;
this release corrects that missed path. Older verification is retained as
historical evidence. Full-game and real-hardware coverage remain unclaimed.

Restart the emulator with the new disc and use a memory-card save or a fresh
game; old emulator save states retain the previous assets and allocations.

## Previous release evidence

# Release verification — 2026-09-07.2

Target BIN SHA-256: `3b0a4539989139d86b2da1e55ade1cb7a590abcc558cd951031fe10f3662ab81`.

This release adds the final audited music-menu bank (37 indexed labels), the
64-byte memory-card title, two fixed title TIMs, and English ending-credit text.

The source-dependent XOR package was round-tripped from the original Japanese
BIN/CUE and checked against the complete candidate byte for byte.

## New verification

- Compared every raw sector against release 2026-09-07.1. Changes are confined to
  one EXE title sector, five ELS sectors in overlay 29, 151 title-image sectors,
  and 20,168 STAFF.STR video sectors. All other bytes are unchanged.
- Checked all 21,070 indexed strings. Exactly the intended 37 labels changed;
  all other translations, all 41 overlay code/control sections, and their
  resource names remain unchanged. No indexed Japanese messages remain.
- Replayed the native title-to-stack and title-to-save-header copies with guard
  bytes. Only the fixed title and its original terminator are copied. No card
  I/O was performed. Save identifiers, layout, icons, and executable code remain
  unchanged; existing card titles change only when the game rewrites a save.
- Replayed all 37 labels through native byte decoding and text placement with
  glyph submission intercepted. All fit the existing menu width without wrapping.
  Ordinary-play access to this optional music menu has not been demonstrated.
- Both title TIM headers, dimensions, record sizes and surrounding FIELD data
  remain unchanged. Previews were inspected after conversion to PSX pixels.
- Decoded all 2,149 replacement credit frames at 320x240 and the original
  15000/1001 cadence (143.409933 seconds). Every frame fits its original sector
  allocation. Original frame/chunk numbering and all 8,644 Form 2 sectors across
  the disc, including the ending song, are byte-identical.
- Independently regenerated EDC/ECC for all 213,770 Mode 2 Form 1 sectors with
  the Redux C implementation; every sector passes.

Fourteen credited personal names retain their Japanese spelling because their
Roman-letter readings were not verified. All role headings and company credits
are English. Song-lyric subtitles remain outside this visual-credit pass.
These checks do not establish full-game progression or real-hardware coverage.
Detailed reproducible evidence is in the local `qa/completion_20260907/` folder.

## Previous rendering repair (retained unchanged)

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

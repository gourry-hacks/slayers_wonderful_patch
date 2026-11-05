# Release verification — 2026-11-05.1

Target BIN SHA-256:
`e89c685c1fde7a80d9f2fb2ef37216e3a7398c759c702e7f44be3efcd9175b0c`.

- The earlier menu fix missed the world map's indirect string lookup. Ten
  scene-specific destination labels now use secondary font carriers. All 23
  world captions are checked, including names already using shared labels.
- Twenty Japanese-sized width values are replaced with English-derived sizes;
  two source-guarded position operands center the resulting panels. Every
  caption fits its panel and the 320-pixel screen. Event IDs, branches,
  destination order and interaction behavior are unchanged.
- Across all 41 scripts, every positioned-text call's final string producer is
  audited. Literal producers and three checked indirect table families cover
  every call in the current source. Unexpected indirect tables fail the build.
- Forty records are byte-identical to 2026-11-03.1. The world record retains its
  header, cardinalities, all other code/data and other string slots. Only three
  raw sectors change, all within that record, with valid EDC/ECC. Executable,
  controls, fonts, movies, audio, battle assets and other disc files match the
  previous release exactly.
- Forty-six R3000 replays execute the shipped positioned renderer: all 23
  labels in both font modes, including uppercase glyph UVs, punctuation,
  packet types, advancement and panel bounds.
- Fresh boots in PCSX ReARMed and Beetle PSX load synthetic original-format
  memory cards and use controller input to reach the original world-map
  captions. Old Castle, Dragon Cave, Cottage, Lake Marren–Sairaag and Mountain
  of Dead Souls are visually checked in both cores. Old-build runs reproduce
  the missing letters and overflow shown in the reports. Dragon Cave's QA
  card explicitly enables its original trigger flag; these are controlled UI
  checks, not a naturally progressed full playthrough. No shipped test jumps
  or player-card changes are used.
- Five new source/layout guard tests, six earlier menu-layout guard tests,
  six patcher tests and ten localization tests pass. The production XOR
  package applied to the original Japanese BIN reproduces this exact target.
  Localization verifies the 61 allowed code immediates and 20 data widths;
  3,319 primary entries remain across 39 overlays. An empty catalog reproduces
  this BIN exactly.

Right-stick turns and interactions while moving remain included by default.
No native-port binaries or player saves are modified. Boot the new CUE and load
an in-game memory-card save so previously loaded script data is refreshed.
This establishes focused world-caption coverage and current-source consumer
coverage; it is not a full playthrough or a test of every graphics renderer.

Older dated sections below describe previous releases.

# Release verification — 2026-11-03.1

Target BIN SHA-256:
`15d94d4dce78550fe6a100c304ebe49c409a67b2a8aaf5688c4781d3c5ce19b0`.

- Reproduced the reported broken shard labels, clipped crafting instruction and
  overlapping six-question menu with the old patch. These are patch defects.
- The repacker now distinguishes scene-specific positioned font consumers from
  ordinary dialogue. Seven shard labels use the correct secondary encoding;
  all 18 additional positioned scene literals are checked. Quantity columns
  leave a six-pixel gutter after the longest label.
- Shared choice boxes are sized and positioned for the English options in each
  overlay. All 371 recognized literal choice labels fit their panel and screen;
  26 overlays require wider boxes. One long option becomes "Use Fireball!!".
  Giles's composed three-part instruction fits its original dialogue box.
- All 41 original ELS headers, variables, record sizes, archive extents and TAG
  metadata are retained. Exactly 59 guarded immediate operands change: choice
  x/width values and seven quantity x values. All event branches and selection
  logic are unchanged. Three semantic entries change at four slots, plus seven
  font-encoding corrections. Fourteen actual R3000 renderer replays verify the
  seven labels' glyph packets in both positioned font modes.
- Only 37 raw sectors differ from 2026-10-30.2, confined to ELS.FS, with valid
  EDC/ECC. The executable, controls, fonts, movies, audio and other assets are
  byte-identical to that release.
- Cold-boot tests in both PCSX ReARMed and Beetle PSX load a synthetic original-
  format card, walk to Giles and open the actual crafting menu. Captures show
  seven correct labels, legible quantities and contained instructions. ReARMed
  also crafts Flare Blade; inventory readback verifies fire shards 13→10 and
  Flare Blade 0→1, with no other item quantities changed.
- Researcher question-menu captures are visually checked in both cores using a
  test-only jump into the original dialogue entry. All six choices fit on
  separate rows, and the first answer executes. This is controlled UI coverage
  with black background scenery, not a natural researcher quest playthrough;
  the test jump is absent from the release. Earlier shared-menu tests had
  missed these scene-specific consumers and narrow choice boxes.
- Six layout guard tests, six patcher tests and ten localization tests pass.
  The actual production XOR package reproduces this BIN from the original
  Japanese image. The updated localization adapter checks the reviewed code
  geometry, excludes positioned strings from its primary catalog and exports
  3,329 entries. An empty catalog reproduces this BIN exactly.

This is focused visual and functional coverage plus checks of recognized literal
consumer patterns across the corpus. It does not establish that every dynamic
text call, scene or emulator configuration is correct. No native-port binaries
or user saves are modified. Boot the new CUE and load an in-game memory-card
save when upgrading; old savestates can retain old scripts.

Older dated sections below describe previous releases.

# Release verification — 2026-10-30.2

Target BIN SHA-256:
`a803faceba32ced5d686150f21719eb90a3d9677a96092907353934fb7b4565f`.

- Read all 3,417 in-scope unique ELS entries in English, checked 213 candidate
  entries against Japanese and context, and revised 175 entries at 340 actual
  string slots. Reviewed all 111 production movie captions / 92 semantic cues;
  five cues in three clips remove mechanical honorifics. Fixed one key-item name
  that retained the untranslated word “Shahon.”
- Every revised actual disc string matches its approved text, respects original
  line-control counts and fits 24 cells. All other ELS strings are unchanged.
  All 41 original script headers, code and variable sections are unchanged.
  Only the 24-byte item-name slot changes in the executable; controls, renderer,
  battle fixes and font cells remain byte-identical to 2026-10-30.1.
- Relative to the previous release, 2,785 changed raw sectors are confined to ELS,
  that name slot and the three reviewed movies. All verify EDC/ECC. All 18
  captioned clips decode fully; all 40,794 production subtitle sectors match
  their patches. All 8,640 movie XA audio sectors remain byte-identical.
- New isolated PCSX ReARMed and Beetle PSX runs each complete 24,000 frames:
  cold boot, opening movies, first battle and return to field. Neither uses a
  player save or prior emulator state. Revised movie contact sheets were
  visually inspected. The guild sentence is verified in the actual string bank;
  these runs do not claim a new natural-playthrough capture of that interaction.
- Six patcher tests and ten localization tests pass. The real XOR package is
  checked against the original Japanese image, and the localization adapter is
  repinned to this base. An empty localization catalog reproduces this BIN
  exactly.

The review is a complete English editorial read with targeted Japanese
adjudication, not a fresh independent translation of every Japanese line or a
full branch-complete playthrough. Proper names, deliberate jokes, Frank's
robotic speech, original save restrictions and gameplay events are retained.
No native-port binaries or user saves are modified.

The earlier controls evidence remains applicable because the controls code is
unchanged. Boot the new CUE and load an in-game save; old emulator savestates
can retain older text and scripts.

Older dated sections below describe previous releases.

# Release verification — 2026-10-30.1

The regular patch now includes the tested right-stick camera and moving-confirm
changes, plus the complete October 29 character-voice revision. Apply it directly
to the original Japanese BIN; no earlier English patch is required.

- The full disc builder reproduces the tested combined image byte for byte:
  `b5a896d5e214c21fb5c567f4a8db7747a0a6da2a5c7bcf4b582e89ae355a4e15`.
- Applying the rebuilt production XOR package to the original Japanese BIN
  reproduces that same 523,117,728-byte image and the generated 83-byte CUE
  (`de66f8498a58a5bc5f8aff03f53b01ee48a5258fe211a4046c37cb44da445eaa`).
  Every patch-part, combined stream and final-output checksum is verified.
- All six patcher tests and ten localization tests pass. The localization
  adapter was reviewed and repinned to this release: its 3,337-entry empty
  catalog reproduces the complete new English image exactly. A synthetic
  Cyrillic sample compiles 70 glyphs; executable changes are confined to the
  allocated font cells. This is a compatibility check, not a Russian translation.
- The dialogue pass reads all 3,417 extracted unique entries and all movie
  dialogue, changing 644 entries at 1,331 occurrences plus ten movie cues.
  Original line-control counts, 24-cell English layout, all 41 VM/code/variable
  sections, archive sizes and sector starts are preserved. Every changed string
  slot was independently read back; all other string slots are unchanged.
- The earlier Beetle PSX and PCSX ReARMed checks cover cold boot, opening movies
  and battle, revised castle dialogue and field/town return. Controls checks
  cover right-stick turns, neutral dead zone and a moving pickup that awards
  one coin exactly once while completing the original event. The user also
  confirmed the combined experimental build worked before promotion. The regular
  BIN is identical to that tested image; the filename/CUE is now the normal pair.
- All 18 dialogue movies decode completely. All 40,794 subtitle sectors verify
  EDC/ECC, and all 8,640 movie XA audio sectors remain byte-identical. The prior
  battle-menu heap/clone-allocation and rendering fixes are retained.

Set port 1 to DualShock with analog mode enabled for stick input. Digital pad
input remains supported. Camera turns use the original turn behavior and scene
locks; interactions retain original scripts and movement completion. Boot the
new CUE and load an in-game memory-card save, since old emulator savestates can
retain old code and scripts. No full branch-complete playthrough or new physical
console/mobile/core-configuration coverage is claimed.

Older dated sections below describe previous releases and their original hashes.

# Localization toolkit verification — 2026-09-12

The new `localize.py` workflow is additive; the packaged English XOR parts,
release manifest and canonical disc files are unchanged.

- Exported 3,337 entries from the verified original disc, with English
  reference text reconstructed from the release patch.
- An empty catalog with English fallback reproduces the canonical English BIN
  SHA-256 exactly: `cc774a0661c3943fc6aefe389b732cb8e4264841c7018997534ef1604716e0c8`.
- A partial Cyrillic build exercises actual localized text and font generation.
  Royal 2's opening uses the compressed-scene path, with unedited records
  expanded/recompressed and pointers checked on readback.
- Complete synthetic Cyrillic catalogs exercise every supported record and
  preserve untouched resources/code/control data. Synthetic strings test the
  compiler; they are not translations or evidence of a full playthrough.
- Independent PCSX-Redux C EDC/ECC regeneration agrees on every modified or
  appended sector. The Python writer is not its own only checksum oracle.
- Russian, French, Spanish and German authoring presets compile with their
  complete reserved alphabets and representative accented text. Glyph proof
  sheets are generated for visual review; font lookup/allocation is bounded.
- Nine original-instruction replays verify the earlier two-byte-glyph wrap
  boundary. Localized Wonderful lines are limited to 22 characters.
- Focused tests cover source/ID/control changes, duplicates, fuzzy entries,
  Unicode/layout rejection, output-path containment, fixed extents and Form 2
  write rejection. Game-specific tests exercise relocation/dictionaries/font
  compression (Royal 2) or ELS offsets/carrier encoding (Wonderful).

These tests establish build/readback coverage, not emulator playability of a
finished localization. No complete target-language catalog exists yet. Newly
localized text, accents and scene layouts require emulator review before
publishing a language patch. The toolkit README lists excluded text/art domains.
Private evidence and generated catalogs are in `qa/localization_20260912/` in
the Slayers workspace; original-disc text and test disc images are not committed.

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

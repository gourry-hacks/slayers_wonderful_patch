# Slayers Wonderful English Patch

Version **2026-11-05.1**, for the Japanese PlayStation release **SLPS-01599**.

## Patch your image (Windows or Linux)

1. [Download the complete patch ZIP](https://github.com/gourry-hacks/slayers_wonderful_patch/archive/refs/tags/v2026-11-05.1.zip)
   and extract it. Install Python 3.10 or newer if needed.
2. Open a terminal in the extracted folder and run the command for your system,
   replacing the example with the path to your **original Japanese BIN**:

   Windows:
   ```powershell
   py -3 patch.py --bin "C:\Games\sw.bin"
   ```

   Linux:
   ```sh
   python3 patch.py --bin "/path/to/sw.bin"
   ```
3. Open `output/wonderful_patched.cue` in your emulator. Keep its BIN in the
   same folder. Boot the new image and load an in-game memory-card save.

This regular patch includes the revised English dialogue, **right-stick camera
turning** and **interactions while walking or running**. For analog controls,
set controller port 1 to **DualShock / analog mode**. Digital controls also work.
Camera turns retain the game's normal angles and scene locks.

**PCSX-Redux users: enable SPU IRQ.** With that setting disabled, even the
original Japanese game can wait indefinitely during voiced prologue events.
The Slayers Eva launcher enables it automatically for Wonderful.

This source-dependent XOR package patches the supported original BIN and
generates its English CUE. Python 3.10 or newer is required; no additional
Python packages are needed. Download the complete repository, including every
file in `patches/`.

```sh
python3 patch.py --bin /path/to/sw.bin
```

On Windows, use `py -3` in place of `python3`. The patcher checks the original
BIN and every BIN patch part, builds temporary outputs, verifies their SHA-256
hashes, and then installs `output/wonderful_patched.bin` and
`output/wonderful_patched.cue`. Open the resulting CUE in your emulator.
Use a separate output directory from your original disc files.

```sh
python3 patch.py --bin /path/to/sw.bin --verify-only
python3 patch.py --bin /path/to/sw.bin --output-dir /path/to/english
```

Apply this release to the original Japanese dump. It already contains the full
translation and rendering corrections; no earlier English patch is required.
Completely close and reopen the disc after replacing an older build. Start
from a fresh boot and use an ordinary memory-card save: old emulator save states
retain the previous executable and already-loaded graphics.

## New in this release

- Fixes missing initial letters and incorrect digits in world-map labels,
  including Cottage, Dragon Cave, Old Castle and the Lake Marren roads.
- All 23 destination labels use their correct font mapping, with centered
  boxes sized from the English text. Destination choices and event behavior
  are unchanged.
- Includes the earlier crafting/choice-menu fixes, revised dialogue and both
  standard controls improvements.

## November 3 menu revision (included)

- Fixes missing or incorrect letters in Giles's seven shard labels, adds room
  before their quantities, and keeps his crafting instructions inside the box.
- Sizes the shared choice boxes for their English labels. The researcher's six
  questions now occupy separate rows without wrapping over each other. The
  same correction covers 26 script overlays with longer choices.
- Includes the October 30 dialogue cleanup and all earlier controls fixes.

## October 30 dialogue revision (included)

- A fresh read of all 3,417 in-scope text entries, with 175 revisions at 340
  occurrences. Guild dialogue now identifies the guild rather than sounding
  like story-route notes. Other fixes restore clear subjects, natural grammar,
  character voices and useful directions, checked against the Japanese.
- Five movie cues remove mechanical “Ms. Lina”/“Mr. Gourry” titles. An item label
  now translates “Shahon” as “Manuscr.” to fit its menu. Movie audio is unchanged.
- Ren'Py wording is a reference, not a requirement to preserve awkward prose.
  The October 29 character review and all earlier translation fixes are included.
- Right-stick camera turns and interactions while walking or running remain
  part of the regular patch. Moving confirm completes the original event and
  waits for the current step; it does not skip dialogue or rewards.

## Translation and rendering

- 3,417 reviewed unique ELS strings at 11,514 indexed occurrences, plus all
  37 music-menu labels missed by the earlier coverage classifier.
- 250 item/equipment names, 51 spell names, and 13 standalone executable labels.
- Seven battle party names and 115 precomposed battle-list labels.
- 111 caption screens across all 18 dialogue-bearing FMV files, plus translated diagrams
  and boot credits.
- English title artwork, copyright text, memory-card title, and ending-credit
  headings with verified name romanizations. Fourteen unverified proper-name
  readings retain their Japanese credited spellings. Original song audio remains.
- Matching compact menu glyphs and six-pixel spacing in both rendering modes.
- Corrected dialogue instruction timing and battle-label frame-buffer capacity.
- Fixed battle-menu heap corruption when opening Lina’s magic list; spell, item,
  and special-attack label clones now reserve both complete drawing buffers.

Long menu names use documented display abbreviations to fit their existing
panels. The repaired disc preserves the original disc size and archive extents.
See [QA.md](QA.md) for verification and remaining coverage limits. This is not
a claim of a complete Wonderful playthrough.

## Supported files

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| Original `sw.bin` | 523117728 | `93560e9c0151baa2fa1321fe056637ef8a42962ef65b80156191b45a1b4bbfc2` |
| English `wonderful_patched.bin` | 523117728 | `e89c685c1fde7a80d9f2fb2ef37216e3a7398c759c702e7f44be3efcd9175b0c` |
| English `wonderful_patched.cue` | 83 | `de66f8498a58a5bc5f8aff03f53b01ee48a5258fe211a4046c37cb44da445eaa` |

No input CUE is required or checked. The optional `--cue` argument is accepted
for compatibility and ignored, so filenames, comments and line endings in an
existing CUE do not affect patching. The output CUE is generated for the verified
BIN's single `MODE2/2352` track and points to `wonderful_patched.bin`.
`release_manifest.json` records the complete source, target, and patch-part
sizes and hashes. Source disc images and emulator packages are not included.

## Credits

Original work: Hajime Kanzaka. Character design: Rui Araizumi.
Slayerites Ren'Py Edition localization reference: Pavel Char, Aregnaz, Gerion,
and Mafoo343. PlayStation game patch: Gourry.

## Maintainer packaging

`maintainer/build_release.py` regenerates the XOR containers from the exact
source and target BIN hashes pinned in the script. It defaults to `../sw.bin`
and `../patched/wonderful_patched.bin`, and accepts explicit paths. CUE data is
generated using the same template as the patcher; no CUE delta is packaged.
It packages an already-built translation; it does not build the translation
from the original game assets. Parts are limited to 45 MiB each.

```sh
python3 maintainer/build_release.py --patch-version 2026-11-05.1
```

## Other languages

The [localization toolkit](localization/README.md) exports Japanese dialogue
to editable PO files and builds a localized disc with custom font glyphs. It
includes Russian, French, Spanish, and German language definitions. These are
authoring presets, not completed translations.

# Slayers Wonderful English Patch

Version **2026-09-12.1**, for the Japanese PlayStation release **SLPS-01599**.

**PCSX-Redux users: enable SPU IRQ.** With that setting disabled, even the
original Japanese game can wait indefinitely during voiced prologue events.
The Slayers Eva launcher enables it automatically for Wonderful.

This source-dependent XOR package reconstructs the English BIN/CUE from the
supported original disc dump. Python 3.10 or newer is required; no additional
Python packages are needed. Download the complete repository, including every
file in `patches/`.

```sh
python3 patch.py --bin /path/to/sw.bin --cue /path/to/sw.cue
```

On Windows, use `py -3` in place of `python3`. The patcher checks the original
files and every patch part, builds temporary outputs, verifies their SHA-256
hashes, and then installs `output/wonderful_patched.bin` and
`output/wonderful_patched.cue`. Open the resulting CUE in your emulator.
Use a separate output directory from your original disc files.

```sh
python3 patch.py --bin /path/to/sw.bin --cue /path/to/sw.cue --verify-only
python3 patch.py --bin /path/to/sw.bin --cue /path/to/sw.cue --output-dir /path/to/english
```

Apply this release to the original Japanese dump. It already contains the full
translation and rendering corrections; no earlier English patch is required.
Completely close and reopen the disc after replacing an older build. Start
from a fresh boot and use an ordinary memory-card save: old emulator save states
retain the previous executable and already-loaded graphics.

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
| Original `sw.cue` | 68 | `c6f94df2bcb2b9284118943a62f420f19f11ee8fd0cb4aaf01b09d65f6cce997` |
| English `wonderful_patched.bin` | 523117728 | `cc774a0661c3943fc6aefe389b732cb8e4264841c7018997534ef1604716e0c8` |
| English `wonderful_patched.cue` | 83 | `de66f8498a58a5bc5f8aff03f53b01ee48a5258fe211a4046c37cb44da445eaa` |

CUE bytes, including line endings, must match the supported dump.
`release_manifest.json` records the complete source, target, and patch-part
sizes and hashes. Source disc images and emulator packages are not included.

## Credits

Original work: Hajime Kanzaka. Character design: Rui Araizumi.
Slayerites Ren'Py Edition localization reference: Pavel Char, Aregnaz, Gerion,
and Mafoo343. PlayStation game patch: Gourry.

## Maintainer packaging

`maintainer/build_release.py` regenerates the XOR containers from the exact
source and target hashes pinned in the script. It defaults to `../sw.bin`,
`../sw.cue`, and `../patched/wonderful_patched.*`, and accepts explicit paths.
It packages an already-built translation; it does not build the translation
from the original game assets. Parts are limited to 45 MiB each.

```sh
python3 maintainer/build_release.py --patch-version 2026-09-12.1
```

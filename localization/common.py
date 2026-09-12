"""Shared authoring validation and deterministic locale font rasterization."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
import re
import unicodedata
from PIL import Image, ImageDraw, ImageFont
from .po import PoEntry

@dataclass
class Entry:
    context: str
    source: str
    english: str
    columns: int
    lines: int
    controls: tuple[str, ...] = ()

    def po(self):
        return PoEntry(self.context, self.source, comments=(f'Limit: {self.columns} characters per line; {self.lines} lines maximum. Preserve control placeholders in order.', 'English reference: ' + json.dumps(self.english, ensure_ascii=False)))
CONTROL = re.compile('<C:[0-9A-F]{4}>')

def validate(entries, catalog, allow_incomplete):
    expected = {e.context: e for e in entries}
    actual = {e.context: e for e in catalog}
    if len(actual) != len(catalog) or set(actual) != set(expected):
        raise ValueError('catalog IDs differ from the verified source (missing, extra, or duplicate contexts)')
    translations = {}
    for key, e in expected.items():
        row = actual[key]
        if row.source != e.source:
            raise ValueError(f'{key}: Japanese msgid changed; edit only msgstr')
        text = row.translation
        if not text:
            if not allow_incomplete:
                raise ValueError(f'{key}: missing translation (use --allow-incomplete for English fallback)')
            continue
        if unicodedata.normalize('NFC', text) != text:
            raise ValueError(f'{key}: translation must use NFC Unicode')
        if tuple(CONTROL.findall(text)) != e.controls:
            raise ValueError(f'{key}: control placeholders changed or reordered')
        visible = CONTROL.sub('', text)
        if '<C:' in visible:
            raise ValueError(f'{key}: malformed control placeholder')
        if any((not ch.isprintable() and ch != '\n' for ch in visible)):
            raise ValueError(f'{key}: unsupported control character')
        if any((unicodedata.bidirectional(ch) in ('R', 'AL', 'AN') or unicodedata.combining(ch) for ch in visible)):
            raise ValueError(f'{key}: this renderer adapter does not support RTL shaping or combining marks')
        lines = visible.split('\n')
        if len(lines) > e.lines or any((len(line) > e.columns for line in lines)):
            raise ValueError(f'{key}: exceeds {e.columns} columns / {e.lines} lines')
        translations[key] = text
    return translations

def load_language(path, locale):
    value = json.loads(path.read_text(encoding='utf-8'))
    if value.get('schema') != 1 or value.get('locale') != locale:
        raise ValueError('workspace locale/schema mismatch')
    for key in ('locale', 'name', 'output_stem', 'required_characters'):
        if not isinstance(value.get(key), str):
            raise ValueError(f'invalid language field {key}')
    for key in ('locale', 'output_stem'):
        if not re.fullmatch('[A-Za-z0-9][A-Za-z0-9_-]{0,63}', value[key]):
            raise ValueError(f'unsafe {key}')
    return value

def font_path(custom=None):
    if custom:
        return Path(custom)
    paths = ['/usr/share/fonts/dejavu-sans-fonts/DejaVuSansCondensed-Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf', '/usr/share/fonts/dejavu/DejaVuSansCondensed-Bold.ttf', '/usr/share/fonts/dejavu-sans-mono-fonts/DejaVuSansMono-Bold.ttf', 'C:/Windows/Fonts/arialbd.ttf', '/System/Library/Fonts/Supplemental/Arial Bold.ttf']
    for path in paths:
        if Path(path).is_file():
            return Path(path)
    raise ValueError('no suitable font found; provide --font /path/to/font.ttf')

def raster(character, width, height, font_file):
    baseline = height - 2 if height <= 11 else height - 3
    font = None
    for size in range(max(height - 2, 6), 4, -1):
        candidate = ImageFont.truetype(str(font_file), size)
        bounds = candidate.getbbox(character, anchor='ls')
        if bounds[1] + baseline >= 0 and bounds[3] + baseline <= height:
            font = candidate
            break
    if font is None:
        raise ValueError(f'cannot fit {character!r} without clipping its accents/descenders')
    mask = font.getmask(character)
    missing = font.getmask('\u0378')
    if (mask.size, bytes(mask)) == (missing.size, bytes(missing)):
        raise ValueError(f'font has no glyph for {character!r}')
    box = font.getbbox(character, anchor='ls')
    canvas = Image.new('L', (max(width, box[2] - box[0] + 2), height))
    ImageDraw.Draw(canvas).text((1 - box[0], baseline), character, font=font, fill=255, anchor='ls')
    if not canvas.getbbox() and (not character.isspace()):
        raise ValueError(f'empty glyph for {character!r}')
    if canvas.width != width:
        canvas = canvas.resize((width, height), Image.Resampling.LANCZOS)
    return canvas.point(lambda value: 255 if value >= 96 else 0)

def proof_sheet(glyphs, path):
    if not glyphs:
        return
    width = max((m.width for _, m in glyphs))
    height = max((m.height for _, m in glyphs))
    out = Image.new('L', (16 * (width + 3), (len(glyphs) + 15) // 16 * (height + 3)))
    for i, (_, mask) in enumerate(glyphs):
        out.paste(mask, (i % 16 * (width + 3), i // 16 * (height + 3)))
    out.resize((out.width * 4, out.height * 4), Image.Resampling.NEAREST).save(path)

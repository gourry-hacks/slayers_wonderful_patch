"""Wonderful primary text-bank localization with fixed ELS/code extents."""
from __future__ import annotations
import hashlib
import struct
import string
from .disc import Disc
from .els import parse_records, parse_overlay
from .common import Entry, font_path, raster, proof_sheet
TITLE = 'Slayers Wonderful'
ELS = '/ELS/ELS.FS'
TAG = '/ELS/ELS.TAG'
EXE = '/SLPS_015.99'
ENGLISH_HASH = 'cc774a0661c3943fc6aefe389b732cb8e4264841c7018997534ef1604716e0c8'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def primary_encode(text, mapping):
    out = bytearray()
    for char in text:
        if char in mapping:
            out.extend(mapping[char].to_bytes(2, 'big'))
        elif char in '\n ' or (char.isascii() and char.isalnum()):
            out.extend(char.encode('ascii'))
        elif char in '\'"':
            out.extend({"'": '’', '"': '”'}[char].encode('cp932'))
        elif 33 <= ord(char) <= 126:
            out.extend(chr(ord(char) + 0xfee0).encode('cp932'))
        else:
            raise ValueError(f'no locale glyph allocated for {char!r}')
    return bytes(out)

def donor_offset(exe, code):
    ranges = [(0x839f, 24, 13), (0x83bf, 24, 14), (0x8440, 33, 15), (0x8470, 15, 16), (0x8480, 18, 17)]
    for start, count, index in ranges:
        if start <= code < start + count:
            table = 0x80058510 - 0x8000f800 + index * 4
            origin, base = struct.unpack_from('<HH', exe, table)
            offset = 0x800586c0 - 0x8000f800 + (code - origin + base) * 22
            if not 0x48ec0 <= offset < 0x4bbc8 - 21:
                raise ValueError('locale font lookup outside first glyph bank')
            return offset
    raise ValueError('unsupported locale carrier')

class Project:
    scope = 'Primary ELS dialogue/text strings at indices >=205; secondary menus, fixed labels, battle artwork and FMVs retain English.'

    def __init__(self, source, english, manifest):
        if manifest['target']['bin']['sha256'] != ENGLISH_HASH:
            raise ValueError('localization adapter needs review for this English base')
        self.disc = Disc(english)
        source = Disc(source)
        self.original = source.file(ELS)
        self.base = self.disc.file(ELS)
        self.exe = self.disc.file(EXE)
        if digest(self.original) != 'a929643f136ebd4a9990d06b255e897d2e0689e49ed6ca54b2dae66455a5fed6':
            raise ValueError('source ELS hash changed')
        tag = source.file(TAG)
        if tag != self.disc.file(TAG):
            raise ValueError('English ELS index changed')
        self.records = parse_records(tag, len(self.original))
        self.groups = {}
        self.parsed = {}
        self.catalog = []
        by_source = {}
        used = set()
        for r in self.records:
            start = r['fs_offset']
            end = start + r['size']
            i = r['index']
            original = parse_overlay(self.original[start:end], i)
            base = parse_overlay(self.base[start:end], i, allow_zero_tail=True)
            self.parsed[i] = base
            if self.original[start:start + original['offset_table']] != self.base[start:start + base['offset_table']]:
                raise ValueError('ELS code/control prefix changed')
            for raw in base['strings']:
                used.update((int.from_bytes(raw[n:n + 2], 'big') for n in range(len(raw) - 1)))
            for j, raw in enumerate(original['strings']):
                if j < 205:
                    continue
                try:
                    text = raw.decode('cp932')
                except UnicodeDecodeError:
                    continue
                if not any(('\u3040' <= c <= '鿿' for c in text)):
                    continue
                if any((not c.isprintable() and c != '\n' and (c != '\u3000') for c in text)):
                    continue
                current = base['strings'][j].decode('cp932')
                reference = ''.join((chr(ord(c) - 0xfee0) if '！' <= c <= '～' else c for c in current))
                if text not in by_source:
                    key = f'els/{i:02d}/{j:04d}'
                    by_source[text] = key
                    # 0x80014D00 wraps double-byte glyphs at columns-2. Leave
                    # those two cells free instead of applying the ASCII budget.
                    self.catalog.append(Entry(key, text, reference, 22, max(1, reference.count('\n') + 1)))
                key = by_source[text]
                self.groups.setdefault(key, []).append((i, j))
        self.donors = [c for start, n in [(0x839f, 24), (0x83bf, 24), (0x8440, 33), (0x8470, 15), (0x8480, 18)] for c in range(start, start + n) if c not in used]
        self.replacements = {}

    def entries(self):
        return self.catalog

    def compile(self, translations, language, font, proof_dir):
        if not translations:
            return dict(changed_overlays=0, new_glyphs=0, scope=self.scope)
        chars = sorted((set(''.join(translations.values())) | set(language['required_characters'])) - set(string.printable))
        if len(chars) > len(self.donors):
            raise ValueError(f'locale needs {len(chars)} glyphs; only {len(self.donors)} primary cells available')
        mapping = dict(zip(chars, self.donors))
        exe = bytearray(self.exe)
        proof = []
        seen = set()
        fontfile = font_path(font) if chars else None
        for char, code in mapping.items():
            offset = donor_offset(exe, code)
            if offset in seen:
                raise ValueError('locale glyphs alias each other')
            seen.add(offset)
            mask = raster(char, 11, 11, fontfile)
            proof.append((char, mask))
            for y in range(11):
                bits = sum((1 << x for x in range(11) if mask.getpixel((x, y))))
                struct.pack_into('<H', exe, offset + y * 2, bits)
        output = bytearray(self.base)
        changed = {}
        used_sizes = []
        for key, text in translations.items():
            encoded = primary_encode(text, mapping)
            for i, j in self.groups[key]:
                changed.setdefault(i, {})[j] = encoded
        for r in self.records:
            i = r['index']
            if i not in changed:
                continue
            p = self.parsed[i]
            strings = list(p['strings'])
            for j, encoded in changed[i].items():
                strings[j] = encoded
            offsets = []
            blob = bytearray()
            for raw in strings:
                offsets.append(len(blob))
                blob.extend(raw + b'\x00')
            capacity = p['string_blob_size']
            if len(blob) > capacity or max(offsets) > 0xffff:
                raise ValueError(f'ELS {i}: needs {len(blob)} string bytes, capacity {capacity}; shorten translations')
            start = r['fs_offset']
            rebuilt = bytearray(self.base[start:start + r['size']])
            struct.pack_into(f'<{len(offsets)}H', rebuilt, p['offset_table'], *offsets)
            rebuilt[p['string_blob']:] = blob.ljust(capacity, b'\x00')
            check = parse_overlay(rebuilt, i, allow_zero_tail=True)
            if check['strings'] != strings or rebuilt[:p['offset_table']] != self.base[start:start + p['offset_table']]:
                raise ValueError('ELS roundtrip/control verification failed')
            output[start:start + r['size']] = rebuilt
            used_sizes.append(dict(overlay=i, used=len(blob), capacity=capacity))
        if len(output) != len(self.base) or len(exe) != len(self.exe):
            raise ValueError('fixed extent resized')
        self.replacements = {ELS: bytes(output), EXE: bytes(exe)}
        proof_sheet(proof, proof_dir / 'locale_glyphs.png')
        return dict(changed_overlays=len(changed), translated_occurrences=sum((len(self.groups[k]) for k in translations)), new_glyphs=len(mapping), glyph_map={c: f'{code:04X}' for c, code in mapping.items()}, banks=used_sizes, scope=self.scope)

    def install(self, path):
        for name, data in self.replacements.items():
            self.disc.replace(name, data)

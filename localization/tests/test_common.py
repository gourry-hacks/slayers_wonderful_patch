"""Authoring boundaries and isolated raw-disc operations (no game data)."""
import struct
import tempfile
import unittest
from pathlib import Path
from localization.common import Entry, validate, load_language
from localization.po import PoEntry, read_po, write_po, PoError
from localization.disc import Disc, CdChecksums, DiscError

class CatalogTests(unittest.TestCase):

    def test_unicode_roundtrip_and_controls(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'dialogue.po'
            rows = [PoEntry('stable/id', '原文<C:9100>', 'Текст<C:9100>')]
            write_po(p, rows, 'ru')
            self.assertEqual(read_po(p), rows)
            entries = [Entry('stable/id', '原文<C:9100>', 'English', 36, 3, ('<C:9100>',))]
            self.assertEqual(validate(entries, rows, False), {'stable/id': 'Текст<C:9100>'})

    def test_source_and_catalog_guards(self):
        entries = [Entry('a', '原文', 'English', 5, 1)]
        for rows in ([], [PoEntry('b', '原文', 'Test')], [PoEntry('a', 'changed', 'Test')], [PoEntry('a', '原文', 'Test')] * 2):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                validate(entries, rows, False)

    def test_layout_and_unicode_guards(self):
        entries = [Entry('a', '原文', 'English', 5, 1)]
        for text in ['abcdef', 'a\nb', 'a\x00', 'é', 'a\x0c', 'العربية', '<C:9100>']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                validate(entries, [PoEntry('a', '原文', text)], False)

    def test_control_order_and_missing_translations(self):
        e = Entry('a', 'source', 'English', 36, 3, ('<C:9000>', '<C:A000>'))
        for text in ['Text', '<C:A000>Text<C:9000>', '<C:9000>Text<C:A000><C:A000>']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                validate([e], [PoEntry('a', 'source', text)], False)
        self.assertEqual(validate([e], [PoEntry('a', 'source')], True), {})
        with self.assertRaises(ValueError):
            validate([e], [PoEntry('a', 'source')], False)

    def test_po_fuzzy_and_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'dialogue.po'
            for text in ['#, fuzzy\nmsgctxt "a"\nmsgid "b"\nmsgstr "c"\n', 'msgctxt "a"\nmsgid "b"\nmsgstr "c"\n\n' * 2]:
                p.write_text(text)
                with self.assertRaises(PoError):
                    read_po(p)

    def test_locale_path_is_contained(self):
        import json
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'language.json'
            p.write_text(json.dumps(dict(schema=1, locale='ru', name='Russian', output_stem='../outside', required_characters='А')))
            with self.assertRaises(ValueError):
                load_language(p, 'ru')

class DiscTests(unittest.TestCase):

    def make_disc(self, path):
        checksum = CdChecksums()
        sectors = []
        for i in range(32):
            sector = bytearray(2352)
            sector[:12] = b'\x00' + b'\xff' * 10 + b'\x00'
            sector[15] = 2
            sector[18] = sector[22] = 8
            sectors.append(sector)
        pvd = sectors[16]
        pvd[24:31] = b'\x01CD001\x01'
        struct.pack_into('<I', pvd, 24 + 158, 20)
        struct.pack_into('<I', pvd, 24 + 166, 2048)
        directory = sectors[20]
        r = bytearray(42)
        r[0] = 42
        struct.pack_into('<I', r, 2, 21)
        struct.pack_into('<I', r, 10, 2048)
        r[32] = 8
        r[33:41] = b'TEXT.BIN'
        directory[24:66] = r
        for s in sectors:
            checksum.repair_mode2_form1(s)
        path.write_bytes(b''.join(sectors))

    def test_replace_append_and_iso_readback(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'test.bin'
            self.make_disc(p)
            before = p.read_bytes()
            disc = Disc(p)
            disc.replace('/TEXT.BIN', b'x' * 2048)
            self.assertEqual(disc.file('/TEXT.BIN'), b'x' * 2048)
            self.assertEqual(p.read_bytes()[:21 * 2352], before[:21 * 2352])
            lba = disc.append('/TEXT.BIN', b'y' * 3000)
            self.assertEqual(lba, 32)
            reopened = Disc(p)
            self.assertEqual(reopened.file('/TEXT.BIN'), b'y' * 3000)
            self.assertEqual(struct.unpack_from('<I', reopened.read(16, 2048), 80)[0], 34)
            self.assertEqual(struct.unpack_from('>I', reopened.read(16, 2048), 84)[0], 34)
            raw = p.read_bytes()
            for i in (16, 20, 21, 32, 33):
                sector = bytearray(raw[i * 2352:(i + 1) * 2352])
                expected = bytes(sector)
                CdChecksums().repair_mode2_form1(sector)
                self.assertEqual(bytes(sector), expected)

    def test_fixed_allocation_and_form2_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'test.bin'
            self.make_disc(p)
            disc = Disc(p)
            with self.assertRaises(DiscError):
                disc.replace('/TEXT.BIN', b'x' * 2049)
            data = bytearray(p.read_bytes())
            data[21 * 2352 + 18] |= 32
            p.write_bytes(data)
            with self.assertRaises(DiscError):
                disc.replace('/TEXT.BIN', b'x' * 2048)
if __name__ == '__main__':
    unittest.main()

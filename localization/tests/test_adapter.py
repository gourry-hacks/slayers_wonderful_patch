import struct
import unittest
from localization.adapter import primary_encode
from localization.els import parse_overlay

class WonderfulTests(unittest.TestCase):

    def test_cyrillic_carriers_and_literal_punctuation(self):
        self.assertEqual(primary_encode('AЯ\n;', {'Я': 33856}), b'A\x84@\n' + '；'.encode('cp932'))
        with self.assertRaises(ValueError):
            primary_encode('Я', {})

    def test_overlay_offsets_and_code_preservation(self):
        data = struct.pack('<8I', 1, 1, 2, 4, 32, 36, 40, 44) + b'CODEFLOW' + struct.pack('<2H', 0, 2) + b'a\x00b\x00'
        result = parse_overlay(data, 0)
        self.assertEqual(result['strings'], [b'a', b'b'])
        broken = bytearray(data)
        struct.pack_into('<H', broken, 42, 3)
        with self.assertRaises(ValueError):
            parse_overlay(broken, 0)
if __name__ == '__main__':
    unittest.main()

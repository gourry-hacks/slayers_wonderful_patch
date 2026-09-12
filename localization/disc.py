"""Bounded ISO-9660 file access and MODE2 Form 1 sector updates."""
from __future__ import annotations
import hashlib
import struct
from pathlib import Path

class DiscError(ValueError):
    pass
RAW_SECTOR_SIZE = 2352
USER_DATA_SIZE = 2048
USER_DATA_OFFSET = 24

class CdChecksums:
    """EDC/ECC generator for PlayStation Mode 2 Form 1 sectors."""

    def __init__(self) -> None:
        self.ecc_f = [0] * 256
        self.ecc_b = [0] * 256
        self.edc = [0] * 256
        for value in range(256):
            forward = (value << 1 ^ (285 if value & 128 else 0)) & 255
            self.ecc_f[value] = forward
            self.ecc_b[value ^ forward] = value
            crc = value
            for _ in range(8):
                crc = crc >> 1 ^ (3623976961 if crc & 1 else 0)
            self.edc[value] = crc

    def compute_edc(self, data: bytes) -> bytes:
        crc = 0
        for value in data:
            crc = crc >> 8 ^ self.edc[(crc ^ value) & 255]
        return crc.to_bytes(4, 'little')

    def compute_ecc(self, source: bytes, major_count: int, minor_count: int, major_mult: int, minor_inc: int) -> bytes:
        address = b'\x00\x00\x00\x00'
        length = major_count * minor_count
        output = bytearray(major_count * 2)
        for major in range(major_count):
            index = (major >> 1) * major_mult + (major & 1)
            ecc_a = 0
            ecc_b = 0
            for _ in range(minor_count):
                value = address[index] if index < 4 else source[index - 4]
                index = (index + minor_inc) % length
                ecc_a ^= value
                ecc_b ^= value
                ecc_a = self.ecc_f[ecc_a]
            ecc_a = self.ecc_b[self.ecc_f[ecc_a] ^ ecc_b]
            output[major] = ecc_a
            output[major + major_count] = ecc_a ^ ecc_b
        return bytes(output)

    def repair_mode2_form1(self, sector: bytearray) -> None:
        if len(sector) != RAW_SECTOR_SIZE or sector[15] != 2 or sector[18] & 32:
            raise DiscError('target sector is not MODE2/2352 Form 1')
        sector[2072:2076] = self.compute_edc(sector[16:2072])
        sector[2076:2248] = self.compute_ecc(sector[16:], 86, 24, 2, 86)
        sector[2248:2352] = self.compute_ecc(sector[16:], 52, 43, 86, 88)

class Disc:

    def __init__(self, path):
        self.path = Path(path)
        self.checksums = CdChecksums()
        self.files = {}
        pvd = self.read(16, 2048)
        if pvd[:7] != b'\x01CD001\x01':
            raise DiscError('missing ISO-9660 primary volume descriptor')
        self._walk(struct.unpack_from('<I', pvd, 158)[0], struct.unpack_from('<I', pvd, 166)[0], '', set())

    def read(self, lba, size):
        if lba < 0 or size < 0 or (lba + (size + 2047) // 2048) * 2352 > self.path.stat().st_size:
            raise DiscError('file extent outside disc')
        data = bytearray()
        with self.path.open('rb') as f:
            for i in range((size + 2047) // 2048):
                f.seek((lba + i) * 2352)
                sector = f.read(2352)
                if len(sector) != 2352 or sector[15] != 2:
                    raise DiscError('unsupported raw sector')
                data.extend(sector[24:2072])
        return bytes(data[:size])

    def _walk(self, lba, size, prefix, visited):
        if lba in visited:
            raise DiscError('cyclic directory')
        visited.add(lba)
        data = self.read(lba, size)
        offset = 0
        while offset < len(data):
            length = data[offset]
            if not length:
                offset = (offset // 2048 + 1) * 2048
                continue
            record = data[offset:offset + length]
            if len(record) != length or length < 34:
                raise DiscError('invalid directory record')
            name = record[33:33 + record[32]]
            if name not in (b'\x00', b'\x01'):
                name = prefix + '/' + name.decode('ascii').split(';')[0]
                entry = dict(lba=struct.unpack_from('<I', record, 2)[0], size=struct.unpack_from('<I', record, 10)[0], directory_lba=lba + offset // 2048, directory_offset=offset % 2048)
                if record[25] & 2:
                    self._walk(entry['lba'], entry['size'], name, visited)
                else:
                    self.files[name] = entry
            offset += length

    def file(self, name):
        e = self.files[name]
        return self.read(e['lba'], e['size'])

    def _sector_write(self, lba, payload, append=False):
        if len(payload) != 2048:
            raise DiscError('sector payload must be 2048 bytes')
        with self.path.open('r+b') as f:
            f.seek(lba * 2352)
            old = f.read(2352)
            if append:
                if old or lba * 2352 != self.path.stat().st_size:
                    raise DiscError('append would overwrite disc data')
                m, rem = divmod(lba + 150, 4500)
                s, frame = divmod(rem, 75)

                def bcd(v):
                    if not 0 <= v <= 99:
                        raise DiscError('disc address exceeds BCD range')
                    return v // 10 * 16 + v % 10
                sector = bytearray(b'\x00' + b'\xff' * 10 + b'\x00' + bytes((bcd(m), bcd(s), bcd(frame), 2)) + b'\x00\x00\x08\x00' * 2 + b'\x00' * 2328)
            else:
                if len(old) != 2352:
                    raise DiscError('short sector write')
                if old[24:2072] == payload:
                    return
                sector = bytearray(old)
            sector[24:2072] = payload
            self.checksums.repair_mode2_form1(sector)
            f.seek(lba * 2352)
            f.write(sector)

    def replace(self, name, payload):
        e = self.files[name]
        if len(payload) != e['size']:
            raise DiscError(f'{name}: replacement changes fixed extent size')
        for i in range((len(payload) + 2047) // 2048):
            block = payload[i * 2048:(i + 1) * 2048]
            if len(block) < 2048:
                block += self.read(e['lba'] + i, 2048)[len(block):]
            self._sector_write(e['lba'] + i, block)
        if self.file(name) != payload:
            raise DiscError(f'{name}: disc readback mismatch')

    def append(self, name, payload):
        if not payload or self.path.stat().st_size % 2352:
            raise DiscError('invalid appended extent')
        start = self.path.stat().st_size // 2352
        for i in range((len(payload) + 2047) // 2048):
            self._sector_write(start + i, payload[i * 2048:(i + 1) * 2048].ljust(2048, b'\x00'), True)
        e = self.files[name]
        directory = bytearray(self.read(e['directory_lba'], 2048))
        pos = e['directory_offset']
        struct.pack_into('<I', directory, pos + 2, start)
        struct.pack_into('>I', directory, pos + 6, start)
        struct.pack_into('<I', directory, pos + 10, len(payload))
        struct.pack_into('>I', directory, pos + 14, len(payload))
        self._sector_write(e['directory_lba'], directory)
        pvd = bytearray(self.read(16, 2048))
        count = self.path.stat().st_size // 2352
        struct.pack_into('<I', pvd, 80, count)
        struct.pack_into('>I', pvd, 84, count)
        self._sector_write(16, pvd)
        e.update(lba=start, size=len(payload))
        if self.file(name) != payload:
            raise DiscError('appended extent readback mismatch')
        return start

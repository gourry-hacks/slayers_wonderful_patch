"""Validated fixed-size ELS parsing from the production repacker."""
import struct
HEADER = struct.Struct("<8I")
TAG_DIRECTORY_OFFSET = 0x4100
SECTOR_SIZE = 2048

def parse_records(tag: bytes, fs_size: int) -> list[dict[str, int]]:
    directory = tag[TAG_DIRECTORY_OFFSET:]
    if not directory or len(directory) % 8:
        raise ValueError("ELS.TAG record directory is not a nonempty array of 8-byte entries")
    records: list[dict[str, int]] = []
    previous_sector = -1
    for index in range(0, len(directory), 8):
        sector, size = struct.unpack_from("<II", directory, index)
        offset = sector * SECTOR_SIZE
        if sector <= previous_sector:
            raise ValueError(f"non-increasing record sector at index {index // 8}")
        if size == 0 or offset + size > fs_size:
            raise ValueError(f"record {index // 8} lies outside ELS.FS")
        records.append(
            {
                "index": index // 8,
                "sector": sector,
                "fs_offset": offset,
                "size": size,
            }
        )
        previous_sector = sector
    return records

def parse_overlay(
    record: bytes, index: int, *, allow_zero_tail: bool = False
) -> dict[str, object]:
    if len(record) < HEADER.size:
        raise ValueError(f"record {index} is smaller than its header")
    words = HEADER.unpack_from(record)
    count32_a, count32_b, string_count, string_blob_size = words[:4]
    header_size, section_b, offset_table, string_blob = words[4:]
    if header_size != HEADER.size:
        raise ValueError(f"record {index}: header size is {header_size:#x}")
    expected_b = header_size + count32_a * 4
    expected_offsets = expected_b + count32_b * 4
    expected_strings = expected_offsets + string_count * 2
    if (section_b, offset_table, string_blob) != (
        expected_b,
        expected_offsets,
        expected_strings,
    ):
        raise ValueError(f"record {index}: inconsistent section offsets")
    if string_blob + string_blob_size != len(record):
        raise ValueError(
            f"record {index}: string blob ends at "
            f"{string_blob + string_blob_size:#x}, record ends at {len(record):#x}"
        )
    offsets = list(
        struct.unpack_from(f"<{string_count}H", record, offset_table)
    )
    if not offsets or offsets[0] != 0 or offsets != sorted(set(offsets)):
        raise ValueError(f"record {index}: invalid string offset table")
    strings: list[bytes] = []
    for position, offset in enumerate(offsets):
        end = record.find(b"\0", string_blob + offset, string_blob + string_blob_size)
        if end < 0:
            raise ValueError(f"record {index} string {position} is not NUL terminated")
        if position + 1 < len(offsets) and end + 1 != string_blob + offsets[position + 1]:
            raise ValueError(f"record {index} string table is not tightly packed")
        strings.append(record[string_blob + offset : end])
    used_end = string_blob + offsets[-1] + len(strings[-1]) + 1
    if used_end != len(record):
        tail = record[used_end:]
        if not allow_zero_tail or any(tail):
            raise ValueError(f"record {index}: final string does not end with the record")
    return {
        "words": words,
        "offset_table": offset_table,
        "string_blob": string_blob,
        "string_blob_size": string_blob_size,
        "offsets": offsets,
        "strings": strings,
    }

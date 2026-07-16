import struct
from typing import Optional


def detect_image_mime_type(data: bytes) -> Optional[str]:
    """Detect a common image MIME type from its file signature."""
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8"):
        return "image/jpeg"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if len(data) >= 12 and data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "image/webp"
    if data.startswith(b"BM"):
        return "image/bmp"
    return None


def read_image_dimensions(data: Optional[bytes]) -> Optional[tuple[int, int]]:
    """Read common image dimensions without decoding the image."""
    if not data:
        return None

    try:
        if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
            return struct.unpack(">II", data[16:24])

        if data.startswith((b"GIF87a", b"GIF89a")) and len(data) >= 10:
            return struct.unpack("<HH", data[6:10])

        if data.startswith(b"\xff\xd8"):
            return _read_jpeg_dimensions(data)

        if len(data) >= 30 and data.startswith(b"RIFF") and data[8:12] == b"WEBP":
            return _read_webp_dimensions(data)

        if data.startswith(b"BM") and len(data) >= 26:
            width, height = struct.unpack("<ii", data[18:26])
            if width > 0 and height != 0:
                return width, abs(height)
    except (IndexError, struct.error, ValueError):
        return None

    return None


def _read_jpeg_dimensions(data: bytes) -> Optional[tuple[int, int]]:
    """Read dimensions from a JPEG start-of-frame segment."""
    start_of_frame_markers = {
        0xC0,
        0xC1,
        0xC2,
        0xC3,
        0xC5,
        0xC6,
        0xC7,
        0xC9,
        0xCA,
        0xCB,
        0xCD,
        0xCE,
        0xCF,
    }
    position = 2

    while position + 8 < len(data):
        if data[position] != 0xFF:
            position += 1
            continue

        while position < len(data) and data[position] == 0xFF:
            position += 1
        if position >= len(data):
            break

        marker = data[position]
        position += 1

        if marker in {0x01, 0xD8, 0xD9} or 0xD0 <= marker <= 0xD7:
            continue
        if position + 2 > len(data):
            break

        segment_length = int.from_bytes(data[position : position + 2], "big")
        if segment_length < 2 or position + segment_length > len(data):
            break

        if marker in start_of_frame_markers and segment_length >= 7:
            height = int.from_bytes(data[position + 3 : position + 5], "big")
            width = int.from_bytes(data[position + 5 : position + 7], "big")
            if width > 0 and height > 0:
                return width, height

        position += segment_length

    return None


def _read_webp_dimensions(data: bytes) -> Optional[tuple[int, int]]:
    """Read dimensions from VP8X, VP8L, or VP8 WebP headers."""
    chunk_type = data[12:16]

    if chunk_type == b"VP8X" and len(data) >= 30:
        width = 1 + int.from_bytes(data[24:27], "little")
        height = 1 + int.from_bytes(data[27:30], "little")
        return width, height

    if chunk_type == b"VP8L" and len(data) >= 25 and data[20] == 0x2F:
        b0, b1, b2, b3 = data[21:25]
        width = 1 + b0 + ((b1 & 0x3F) << 8)
        height = 1 + (b1 >> 6) + (b2 << 2) + ((b3 & 0x0F) << 10)
        return width, height

    if chunk_type == b"VP8 " and len(data) >= 30 and data[23:26] == b"\x9d\x01\x2a":
        width = int.from_bytes(data[26:28], "little") & 0x3FFF
        height = int.from_bytes(data[28:30], "little") & 0x3FFF
        if width > 0 and height > 0:
            return width, height

    return None

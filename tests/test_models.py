import struct

from client.models import MediaInfo


def png_header(width: int, height: int) -> bytes:
    return b"\x89PNG\r\n\x1a\n" + b"\x00" * 8 + struct.pack(">II", width, height)


def jpeg_header(width: int, height: int) -> bytes:
    return (
        b"\xff\xd8"
        + b"\xff\xc0"
        + struct.pack(">H", 11)
        + b"\x08"
        + struct.pack(">HH", height, width)
        + b"\x01\x01\x11\x00"
        + b"\xff\xd9"
    )


def webp_vp8x_header(width: int, height: int) -> bytes:
    return (
        b"RIFF"
        + b"\x00\x00\x00\x00"
        + b"WEBP"
        + b"VP8X"
        + b"\x0a\x00\x00\x00"
        + b"\x00\x00\x00\x00"
        + (width - 1).to_bytes(3, "little")
        + (height - 1).to_bytes(3, "little")
    )


def test_reads_common_artwork_dimensions() -> None:
    assert MediaInfo(album_art=png_header(512, 384)).album_art_dimensions == (
        512,
        384,
    )
    assert MediaInfo(album_art=jpeg_header(100, 100)).album_art_dimensions == (
        100,
        100,
    )
    assert MediaInfo(
        album_art=b"GIF89a" + struct.pack("<HH", 96, 64)
    ).album_art_dimensions == (96, 64)
    assert MediaInfo(album_art=webp_vp8x_header(640, 360)).album_art_dimensions == (
        640,
        360,
    )


def test_artwork_fit_never_enlarges_known_pixels() -> None:
    media = MediaInfo(album_art=jpeg_header(100, 50))

    assert media.album_art_fit(176, 176) == (100, 50)
    assert media.album_art_fit(80, 80) == (80, 40)
    assert not media.album_art_is_at_least(136, 120)


def test_data_uri_uses_detected_mime_type() -> None:
    media = MediaInfo(album_art=jpeg_header(100, 100))

    assert media.album_art_mime_type == "image/jpeg"
    assert media.album_art_data_uri.startswith("data:image/jpeg;base64,")

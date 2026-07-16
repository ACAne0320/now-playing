import struct

from client.models import MediaInfo
from client.renderer.engine import Renderer


def png_header(width: int, height: int) -> bytes:
    return b"\x89PNG\r\n\x1a\n" + b"\x00" * 8 + struct.pack(">II", width, height)


def render(template: str, width: int, height: int) -> str:
    media = MediaInfo(
        title="Track",
        artist="Artist",
        album="Album",
        is_playing=True,
        album_art=png_header(width, height),
    )
    return Renderer().render_svg(media, template)


def test_music_card_uses_inset_artwork_for_small_sources() -> None:
    svg = render("music-card", 100, 100)

    assert 'class="artwork artwork-inset"' in svg
    assert '<svg width="320" height="136"' in svg
    assert 'width="88" height="88"' in svg
    assert 'class="artwork artwork-fill"' not in svg


def test_music_card_keeps_full_bleed_for_large_sources() -> None:
    svg = render("music-card", 512, 512)

    assert '<svg width="320" height="400"' in svg
    assert 'class="artwork artwork-fill"' in svg
    assert 'class="artwork artwork-inset"' not in svg


def test_rounded_uses_inset_artwork_for_small_sources() -> None:
    svg = render("rounded", 100, 100)

    assert 'class="artwork artwork-inset"' in svg
    assert 'width="88" height="88"' in svg

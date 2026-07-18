import struct
from xml.etree import ElementTree

import pytest

from client.models import MediaInfo
from client.renderer.engine import Renderer

TEMPLATES = {
    "minimalist",
    "music-card",
    "neon",
    "polaroid",
    "poster",
    "terminal",
    "ticket",
    "turntable",
}


def png_header(width: int, height: int) -> bytes:
    return b"\x89PNG\r\n\x1a\n" + b"\x00" * 8 + struct.pack(">II", width, height)


def media(artwork_size: int, is_playing: bool = True) -> MediaInfo:
    return MediaInfo(
        title="Track",
        artist="Artist",
        album="Album",
        is_playing=is_playing,
        album_art=png_header(artwork_size, artwork_size),
    )


def test_template_catalog_is_complete() -> None:
    assert set(Renderer().list_templates()) == TEMPLATES


@pytest.mark.parametrize("template", sorted(TEMPLATES))
def test_templates_render_valid_svg_in_all_artwork_states(template: str) -> None:
    states = [
        None,
        MediaInfo(title="Track", artist="Artist", is_playing=False),
        media(100),
        media(512),
    ]

    for state in states:
        svg = Renderer().render_svg(state, template)

        assert "Template error:" not in svg
        assert ElementTree.fromstring(svg).tag.endswith("svg")

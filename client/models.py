import base64
from typing import Optional

from pydantic import BaseModel

from .utils.image_metadata import detect_image_mime_type, read_image_dimensions


class MediaInfo(BaseModel):
    """Data model for media information."""

    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    is_playing: bool = False
    album_art: Optional[bytes] = None

    class Config:
        # Allow arbitrary types like bytes
        arbitrary_types_allowed = True

    @property
    def album_art_b64(self) -> Optional[str]:
        """Get base64 encoded album art for embedding in SVG."""
        if self.album_art:
            return base64.b64encode(self.album_art).decode("utf-8")
        return None

    @property
    def album_art_mime_type(self) -> Optional[str]:
        """Detect the embedded artwork MIME type from its file signature."""
        if not self.album_art:
            return None

        # Preserve the previous behavior for uncommon formats.
        return detect_image_mime_type(self.album_art) or "image/png"

    @property
    def album_art_data_uri(self) -> Optional[str]:
        """Get a correctly typed data URI for embedding artwork in SVG."""
        encoded = self.album_art_b64
        if not encoded:
            return None
        return f"data:{self.album_art_mime_type};base64,{encoded}"

    @property
    def album_art_dimensions(self) -> Optional[tuple[int, int]]:
        """Read artwork dimensions without decoding or resizing the image."""
        return read_image_dimensions(self.album_art)

    def album_art_is_at_least(self, min_width: int, min_height: int) -> bool:
        """Return whether artwork is large enough for a full-bleed layout."""
        dimensions = self.album_art_dimensions
        if not dimensions:
            return False
        width, height = dimensions
        return width >= min_width and height >= min_height

    def album_art_fit(self, max_width: int, max_height: int) -> tuple[int, int]:
        """Fit artwork inside a box without enlarging known source pixels."""
        dimensions = self.album_art_dimensions
        if not dimensions:
            return min(max_width, 96), min(max_height, 96)

        width, height = dimensions
        scale = min(max_width / width, max_height / height, 1.0)
        return max(1, round(width * scale)), max(1, round(height * scale))

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "is_playing": self.is_playing,
            "album_art_b64": self.album_art_b64,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MediaInfo":
        """Create MediaInfo from dictionary."""
        if not data:
            return None

        album_art = None
        if data.get("album_art_b64"):
            try:
                album_art = base64.b64decode(data["album_art_b64"])
            except Exception:
                pass

        return cls(
            title=data.get("title"),
            artist=data.get("artist"),
            album=data.get("album"),
            is_playing=data.get("is_playing", False),
            album_art=album_art,
        )

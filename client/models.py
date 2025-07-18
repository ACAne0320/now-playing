import base64
from typing import Optional

from pydantic import BaseModel


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

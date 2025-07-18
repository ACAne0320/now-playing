import json
import platform
import subprocess
from pathlib import Path
from typing import Optional

from ..models import MediaInfo
from .base import BasePoller

# JXA script path should be in the same directory
JXA_SCRIPT_PATH = Path(__file__).parent / "get_media_info.jxa"


class MacosMediaPoller(BasePoller):
    """
    Polls for media information on macOS by executing a JXA script.
    """

    def __init__(self):
        self.is_macos = platform.system() == "Darwin"
        self.script_available = JXA_SCRIPT_PATH.exists()

    def is_supported(self) -> bool:
        """Check if macOS JXA polling is supported."""
        return self.is_macos and self.script_available

    async def get_media_info(self) -> Optional[MediaInfo]:
        """Get current media information using JXA script."""
        if not self.is_supported():
            return None

        try:
            # Execute JXA script
            process = subprocess.run(
                ["osascript", "-l", "JavaScript", str(JXA_SCRIPT_PATH)],
                capture_output=True,
                text=True,
                check=True,
                timeout=5,  # 5 second timeout
            )

            output = process.stdout.strip()
            if not output:
                return None

            # Parse JSON output
            data = json.loads(output)

            # Handle error response
            if "error" in data:
                print(f"JXA script error: {data['error']}")
                return None

            # Return None if no media data
            if not data or data.get("title") is None:
                return None

            return MediaInfo(
                title=data.get("title", "Unknown Title"),
                artist=data.get("artist", "Unknown Artist"),
                album=data.get("album", "Unknown Album"),
                is_playing=data.get("isPlaying", False),
                album_art=None,  # JXA approach doesn't easily provide album art
            )

        except (
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
            json.JSONDecodeError,
        ) as e:
            print(f"Error getting macOS media info: {e}")
            # This is where we could implement Spotify API fallback
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

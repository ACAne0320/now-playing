import json
import platform
import subprocess
import base64
from pathlib import Path
from typing import Optional

from ..models import MediaInfo
from .base import BasePoller

# JXA script path should be in the same directory
JXA_SCRIPT_PATH = Path(__file__).parent / "get_media_info.jxa"

# MediaRemote adapter paths
MEDIAREMOTE_FRAMEWORK = Path(__file__).parent / "mediaremote-adapter" / "MediaRemoteAdapter.framework"
MEDIAREMOTE_SCRIPT = Path(__file__).parent / "mediaremote-adapter" / "bin" / "mediaremote-adapter.pl"


class MacosMediaPoller(BasePoller):
    """
    Polls for media information on macOS by executing a JXA script.
    """

    def __init__(self):
        self.is_macos = platform.system() == "Darwin"
        self.script_available = JXA_SCRIPT_PATH.exists()
        self.enhanced_mode = (
            MEDIAREMOTE_FRAMEWORK.exists() and MEDIAREMOTE_SCRIPT.exists()
        )

    def is_supported(self) -> bool:
        """Check if macOS JXA polling is supported."""
        return self.is_macos and self.script_available

    async def get_media_info(self) -> Optional[MediaInfo]:
        """Get current media information using JXA script."""
        if not self.is_supported():
            return None

        # Try enhanced mode first (with artwork)
        if self.enhanced_mode:
            media_info = await self._get_enhanced_media_info()
            if media_info:
                return media_info

        # Fallback to basic JXA mode
        return await self._get_basic_media_info()

    async def _get_enhanced_media_info(self) -> Optional[MediaInfo]:
        """Get media info with album artwork using mediaremote-adapter."""
        try:
            # Use mediaremote-adapter for complete info including artwork
            process = subprocess.run([
                "/usr/bin/perl",
                str(MEDIAREMOTE_SCRIPT),
                str(MEDIAREMOTE_FRAMEWORK),
                "get"
            ], capture_output=True, text=True, timeout=10)

            if process.returncode != 0 or not process.stdout.strip():
                return None

            data = json.loads(process.stdout.strip())
            
            # Handle null response
            if data is None:
                return None

            # Extract album artwork
            album_art_data = None
            if data.get("artworkData") and data.get("artworkMimeType"):
                try:
                    album_art_data = base64.b64decode(data["artworkData"])
                except Exception as e:
                    print(f"Error decoding artwork: {e}")

            return MediaInfo(
                title=data.get("title", "Unknown Title"),
                artist=data.get("artist", "Unknown Artist"),
                album=data.get("album", "Unknown Album"),
                is_playing=data.get("playing", False),
                album_art=album_art_data,
            )

        except Exception as e:
            print(f"Enhanced media info error: {e}")
            return None

    async def _get_basic_media_info(self) -> Optional[MediaInfo]:
        """Get basic media info using JXA script (fallback)."""
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

            # Handle None response (no media playing)
            if data is None:
                return None

            # Handle error response
            if isinstance(data, dict) and "error" in data:
                print(f"JXA script error: {data['error']}")
                return None

            # Return None if no media data
            if not data or not isinstance(data, dict) or data.get("title") is None:
                return None

            return MediaInfo(
                title=data.get("title", "Unknown Title"),
                artist=data.get("artist", "Unknown Artist"),
                album=data.get("album", "Unknown Album"),
                is_playing=data.get("isPlaying", False),
                album_art=None,  # Basic mode doesn't provide artwork
            )

        except (
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
            json.JSONDecodeError,
        ) as e:
            print(f"Error getting basic macOS media info: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in basic mode: {e}")
            return None

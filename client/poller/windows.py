import platform
from typing import Optional

# Import Windows-specific modules only on Windows
if platform.system() == "Windows":
    try:
        from winsdk.windows.media.control import (
            GlobalSystemMediaTransportControlsSessionManager as MediaManager,
        )
        from winsdk.windows.storage.streams import (
            Buffer,
            DataReader,
            InputStreamOptions,
        )

        WINDOWS_AVAILABLE = True
    except ImportError:
        WINDOWS_AVAILABLE = False
else:
    WINDOWS_AVAILABLE = False

from ..models import MediaInfo
from .base import BasePoller


class WindowsMediaPoller(BasePoller):
    """
    Polls for media information on Windows using the winsdk API.
    Uses the modern Windows SDK Python bindings for better compatibility.
    """

    def __init__(self, enable_album_art: bool = True):
        self.is_windows = platform.system() == "Windows"
        self.winsdk_available = WINDOWS_AVAILABLE
        self.enable_album_art = enable_album_art

    def is_supported(self) -> bool:
        """Check if Windows winsdk polling is supported."""
        return self.is_windows and self.winsdk_available

    async def get_media_info(self) -> Optional[MediaInfo]:
        """Get current media information using Windows winsdk API."""
        if not self.is_supported():
            return None

        try:
            sessions = await MediaManager.request_async()
            if not sessions:
                return None

            current_session = sessions.get_current_session()
            if not current_session:
                return None

            info = await current_session.try_get_media_properties_async()
            if not info:
                return None

            artist = info.artist or "Unknown Artist"
            title = info.title or "Unknown Title"
            album = info.album_title or "Unknown Album"

            playback_info = current_session.get_playback_info()
            playback_status = playback_info.playback_status
            playback_status_str = str(playback_status)

            # Windows SDK GlobalSystemMediaTransportControlsSessionPlaybackStatus Enum:
            # Closed = 0, Opened = 1, Changing = 2, Stopped = 3, Playing = 4, Paused = 5
            is_playing = False
            try:
                if hasattr(playback_status, "value"):
                    is_playing = playback_status.value == 4
                else:
                    is_playing = playback_status_str in [
                        "Playing",
                        "4",
                        "GlobalSystemMediaTransportControlsSessionPlaybackStatus.Playing",
                    ]
            except Exception:
                is_playing = "playing" in playback_status_str.lower()

            import logging

            logger = logging.getLogger(__name__)
            logger.debug(
                f"Playback status object: {playback_status}, string: '{playback_status_str}', is_playing: {is_playing}"
            )

            album_art = None
            if self.enable_album_art:
                album_art = await self._get_album_art(info.thumbnail)

            return MediaInfo(
                title=title,
                artist=artist,
                album=album,
                is_playing=is_playing,
                album_art=album_art,
            )

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error getting Windows media info: {e}", exc_info=True)
            return None

    async def _get_album_art(self, thumbnail_ref) -> Optional[bytes]:
        """Extract album art bytes from thumbnail reference."""
        if not thumbnail_ref:
            return None

        try:
            stream = await thumbnail_ref.open_read_async()
            if not stream:
                return None

            size = stream.size
            if size == 0:
                return None

            buffer = Buffer(size)
            await stream.read_async(buffer, size, InputStreamOptions.READ_AHEAD)

            if buffer.length == 0:
                return None

            try:
                reader = DataReader.from_buffer(buffer)
                byte_data = bytearray()

                for _i in range(buffer.length):
                    try:
                        byte_val = reader.read_byte()
                        byte_data.append(byte_val)
                    except Exception:
                        break

                if len(byte_data) > 0:
                    return bytes(byte_data)
                else:
                    return None

            except Exception as read_error:
                print(f"Error reading bytes from buffer: {read_error}")
                return None

        except Exception as e:
            print(f"Error extracting album art: {e}")
            return None

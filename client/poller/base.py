from abc import ABC, abstractmethod
from typing import Optional

from ..models import MediaInfo


class BasePoller(ABC):
    """Abstract base class for all media pollers."""

    @abstractmethod
    async def get_media_info(self) -> Optional[MediaInfo]:
        """
        Get current media information.

        Returns:
            MediaInfo object if media is playing, None otherwise.
        """
        pass

    def is_supported(self) -> bool:
        """
        Check if this poller is supported on the current platform.

        Returns:
            True if supported, False otherwise.
        """
        return True

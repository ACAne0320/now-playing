import platform
from typing import Optional

from .base import BasePoller
from .macos import MacosMediaPoller
from .windows import WindowsMediaPoller


def create_poller(exclude_browsers: bool = False) -> Optional[BasePoller]:
    """
    Factory function to create the appropriate poller for the current platform.

    Args:
        exclude_browsers: Whether to exclude browser media sources (default: False)

    Returns:
        A platform-specific poller instance, or None if no poller is available.
    """
    system = platform.system()

    if system == "Windows":
        poller = WindowsMediaPoller(exclude_browsers=exclude_browsers)
        if poller.is_supported():
            return poller
    elif system == "Darwin":  # macOS
        poller = MacosMediaPoller()
        if poller.is_supported():
            return poller

    # Return a dummy poller if no platform-specific one is available
    return DummyPoller()


class DummyPoller(BasePoller):
    """Dummy poller for unsupported platforms or testing."""

    async def get_media_info(self):
        """Return None to indicate no media information available."""
        return None

    def is_supported(self) -> bool:
        """Always return True for dummy poller."""
        return True

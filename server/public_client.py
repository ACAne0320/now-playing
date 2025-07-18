#!/usr/bin/env python3
"""
Public client script for Now Playing service.
This script runs on the user's local machine and sends media information
to a public server for GitHub README embedding.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import requests

# Add the now_playing package to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from client.models import MediaInfo
from client.poller.factory import create_poller
from config import get_config


class PublicClient:
    """Client for sending media information to a public server."""

    def __init__(self, server_url: str, api_key: str, poll_interval: int = 5):
        """
        Initialize the public client.

        Args:
            server_url: URL of the public server
            api_key: API key for authentication
            poll_interval: Seconds between polling attempts
        """
        self.server_url = server_url.rstrip("/")
        self.api_key = api_key
        self.poll_interval = poll_interval
        self.poller = create_poller()

        if not self.poller:
            raise RuntimeError("No supported media poller found for this platform")

    async def get_media_info(self) -> Optional[MediaInfo]:
        """Get current media information."""
        try:
            return await self.poller.get_media_info()
        except Exception as e:
            print(f"Error getting media info: {e}")
            return None

    def send_media_info(self, media_info: Optional[MediaInfo]) -> bool:
        """
        Send media information to the public server.

        Args:
            media_info: Media information to send, or None if nothing is playing

        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare data for JSON serialization
            if media_info:
                data = media_info.to_dict()
            else:
                data = None

            # Send POST request to server
            response = requests.post(
                f"{self.server_url}/api/v1/update",
                json={"media_info": data},
                params={"api_key": self.api_key},
                timeout=10,
            )
            print(response.status_code, response.text)
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "updated":
                    title = media_info.title if media_info else "No media"
                    print(
                        f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Updated: {title}"
                    )
                    return True
                else:
                    print(
                        f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Server error: {result}"
                    )
                    return False
            else:
                print(
                    f"[{datetime.now().strftime('%H:%M:%S')}] ❌ HTTP error: {response.status_code}"
                )
                return False

        except requests.RequestException as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Network error: {e}")
            return False
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Unexpected error: {e}")
            return False

    async def run(self):
        """Main client loop."""
        print("Starting Now Playing client...")
        print(f"Server: {self.server_url}")
        print(f"Poll interval: {self.poll_interval} seconds")
        print(f"Poller: {type(self.poller).__name__}")
        print("Press Ctrl+C to stop")
        print("-" * 50)

        last_media_info = None

        try:
            while True:
                # Get current media info
                current_media_info = await self.get_media_info()

                # Only send if media info changed
                if self._media_info_changed(last_media_info, current_media_info):
                    success = self.send_media_info(current_media_info)
                    if success:
                        last_media_info = current_media_info

                # Wait before next poll
                await asyncio.sleep(self.poll_interval)

        except KeyboardInterrupt:
            print("\nStopping client...")
        except Exception as e:
            print(f"Fatal error: {e}")
            sys.exit(1)

    def _media_info_changed(
        self, old: Optional[MediaInfo], new: Optional[MediaInfo]
    ) -> bool:
        """Check if media info has changed."""
        if old is None and new is None:
            return False
        if old is None or new is None:
            return True

        return (
            old.title != new.title
            or old.artist != new.artist
            or old.album != new.album
            or old.is_playing != new.is_playing
        )


def load_config() -> dict[str, Any]:
    """Load configuration from unified config system."""
    config_manager = get_config()
    return config_manager.get_client_config()


def main():
    """Main entry point."""
    try:
        config = load_config()

        # Validate configuration
        if not config.get("server_url"):
            print("Error: SERVER_URL not configured")
            sys.exit(1)

        if not config.get("api_key"):
            print("Error: API_KEY not configured")
            sys.exit(1)

        # Create and run client
        client = PublicClient(
            server_url=config["server_url"],
            api_key=config["api_key"],
            poll_interval=config["poll_interval"],
        )

        asyncio.run(client.run())

    except Exception as e:
        print(f"Failed to start client: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

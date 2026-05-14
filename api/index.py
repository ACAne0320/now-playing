"""
Vercel deployment entry point for Now Playing service.
This file is specifically designed for serverless deployment on Vercel.

The top-level `app` variable is required by Vercel's Python runtime
(@vercel/python) to locate the ASGI entrypoint.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path so that `client` and `config` are importable.
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure environment before importing the app so that config picks them up.
os.environ.setdefault("PUBLIC_MODE", "true")
os.environ.setdefault("NOW_PLAYING_POLL_INTERVAL", "30")
os.environ.setdefault("LOG_LEVEL", "INFO")

# Import the FastAPI application.  This must be a top-level statement so that
# Vercel's builder can detect the `app` variable at parse time.
from client.main import app  # noqa: E402  (module-level import after sys.path setup)

__all__ = ["app"]

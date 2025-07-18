"""
Vercel deployment entry point for Now Playing service.
This file is specifically designed for serverless deployment on Vercel.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables for Vercel deployment
os.environ.setdefault("PUBLIC_MODE", "true")
os.environ.setdefault("NOW_PLAYING_POLL_INTERVAL", "30")
os.environ.setdefault("LOG_LEVEL", "INFO")

# Import the FastAPI app
from client.main import app

# Export the app for Vercel
handler = app

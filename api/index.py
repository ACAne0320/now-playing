"""
Vercel deployment entry point for Now Playing service.
This file is specifically designed for serverless deployment on Vercel.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set environment variables for Vercel deployment
os.environ['PUBLIC_MODE'] = "true"
os.environ['NOW_PLAYING_POLL_INTERVAL'] = "30"
os.environ['LOG_LEVEL'] = "INFO"

try:
    # Import the FastAPI app
    from client.main import app
    
    # Export the app for Vercel
    handler = app
    
except Exception as e:
    print(f"Error importing app: {e}")
    import traceback
    traceback.print_exc()
    
    # Create a minimal error app
    from fastapi import FastAPI
    handler = FastAPI()
    
    @handler.get("/")
    async def error_root():
        return {"error": "Failed to import main app", "details": str(e)}
    
    @handler.get("/health")
    async def health():
        return {"status": "error", "message": "Main app failed to load"}

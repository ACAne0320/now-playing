import logging
import os
import sys
import time
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.staticfiles import StaticFiles

from .models import MediaInfo
from .poller.base import BasePoller
from .poller.factory import create_poller
from .renderer.engine import Renderer

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import get_config

config = get_config()

log_level = getattr(logging, config.get("server.log_level", "INFO").upper())
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

PUBLIC_MODE = config.get("server.public_mode", False)


class AppState:
    def __init__(self):
        self.poller: Optional[BasePoller] = None
        self.renderer: Optional[Renderer] = None
        self.media_cache: dict[str, Any] = {}
        self.start_time: float = 0
        self.debug_info: list[str] = []  # 添加调试信息存储


app_state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown events."""

    app_state.start_time = time.time()

    if not PUBLIC_MODE:
        exclude_browsers = config.get("server.exclude_browsers", False)
        app_state.poller = create_poller(exclude_browsers=exclude_browsers)

    try:
        debug_msg = f"Attempting to initialize Renderer in PUBLIC_MODE: {PUBLIC_MODE}"
        print(debug_msg)
        app_state.debug_info.append(debug_msg)
        
        app_state.renderer = Renderer()
        success_msg = "Renderer initialized successfully"
        print(success_msg)
        app_state.debug_info.append(success_msg)
    except Exception as e:
        error_msg = f"Failed to initialize renderer: {e}"
        print(error_msg)
        app_state.debug_info.append(error_msg)
        
        exc_type_msg = f"Exception type: {type(e).__name__}"
        print(exc_type_msg)
        app_state.debug_info.append(exc_type_msg)
        
        import traceback
        traceback_msg = f"Traceback: {traceback.format_exc()}"
        print(traceback_msg)
        app_state.debug_info.append(traceback_msg)
        
        # Try with absolute path
        try:
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            template_dir = os.path.join(current_dir, "renderer", "templates")
            
            current_dir_msg = f"Current directory: {current_dir}"
            print(current_dir_msg)
            app_state.debug_info.append(current_dir_msg)
            
            template_dir_msg = f"Trying template directory: {template_dir}"
            print(template_dir_msg)
            app_state.debug_info.append(template_dir_msg)
            
            exists_msg = f"Template directory exists: {os.path.exists(template_dir)}"
            print(exists_msg)
            app_state.debug_info.append(exists_msg)
            
            if os.path.exists(template_dir):
                contents_msg = f"Template directory contents: {os.listdir(template_dir)}"
                print(contents_msg)
                app_state.debug_info.append(contents_msg)
                
            app_state.renderer = Renderer(template_dir=template_dir)
            success_abs_msg = "Renderer initialized with absolute path"
            print(success_abs_msg)
            app_state.debug_info.append(success_abs_msg)
        except Exception as e2:
            error_abs_msg = f"Failed to initialize renderer with absolute path: {e2}"
            print(error_abs_msg)
            app_state.debug_info.append(error_abs_msg)
            
            exc_type_abs_msg = f"Exception type: {type(e2).__name__}"
            print(exc_type_abs_msg)
            app_state.debug_info.append(exc_type_abs_msg)
            
            traceback_abs_msg = f"Traceback: {traceback.format_exc()}"
            print(traceback_abs_msg)
            app_state.debug_info.append(traceback_abs_msg)
            
            app_state.renderer = None

    yield

    logger.info("Application shutting down")


def get_poller() -> Optional[BasePoller]:
    """Dependency to get the poller instance."""
    return app_state.poller


def get_renderer() -> Optional[Renderer]:
    """Dependency to get the renderer instance."""
    return app_state.renderer


def get_media_cache() -> dict[str, Any]:
    """Dependency to get the media cache."""
    return app_state.media_cache


app = FastAPI(
    title="Now Playing Service",
    description="A service to get currently playing music information.",
    version="1.0.0",
    lifespan=lifespan,
)

web_dir = Path(__file__).parent.parent / "web"
if web_dir.exists():
    app.mount("/web", StaticFiles(directory=str(web_dir), html=True), name="web")


@app.get("/")
async def root():
    """Root endpoint for health checks."""
    mode = "public" if PUBLIC_MODE else "local"
    return {
        "status": "ok",
        "message": "Now Playing service is running.",
        "mode": mode,
        "version": "1.0.0",
    }


@app.get("/now-playing.svg")
async def get_now_playing_svg(
    template: str = "default",
    custom_css: Optional[str] = None,
    user_id: Optional[str] = None,
    poller: Optional[BasePoller] = Depends(get_poller),
    renderer: Optional[Renderer] = Depends(get_renderer),
    media_cache: dict[str, Any] = Depends(get_media_cache),
):
    """Get the current playing media as an SVG image."""

    if PUBLIC_MODE:
        # In public mode, get data from cache
        cache_key = user_id or "default"
        cached_data = media_cache.get(cache_key)

        if cached_data:
            media_info = MediaInfo.from_dict(cached_data) if cached_data else None
        else:
            media_info = None
    else:
        # In local mode, get data from poller
        if not poller:
            return Response(
                content="<svg><text>Service not initialized</text></svg>",
                media_type="image/svg+xml",
            )

        try:
            media_info = await poller.get_media_info()
        except Exception:
            media_info = None

    if not renderer:
        error_svg = """
        <svg width="400" height="120" xmlns="http://www.w3.org/2000/svg">
            <rect width="400" height="120" fill="#ff0000" opacity="0.1"/>
            <text x="20" y="40" fill="#ff0000" font-family="Arial, sans-serif" font-size="14">
                Renderer not initialized
            </text>
            <text x="20" y="60" fill="#666" font-family="Arial, sans-serif" font-size="12">
                Template system failed to load
            </text>
        </svg>
        """
        return Response(content=error_svg, media_type="image/svg+xml")

    try:
        svg_content = renderer.render_svg(
            media_info, template_name=template, custom_css=custom_css
        )

        return Response(
            content=svg_content,
            media_type="image/svg+xml",
            headers={
                f"Cache-Control": "public, max-age=10",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        )
    except Exception as e:
        error_svg = f"""
        <svg width="400" height="120" xmlns="http://www.w3.org/2000/svg">
            <text x="10" y="50" fill="red">Error: {str(e)}</text>
        </svg>
        """
        return Response(content=error_svg, media_type="image/svg+xml")


@app.post("/api/v1/update")
async def update_media_info(
    request: dict,
    api_key: str = None,
    user_id: Optional[str] = None,
    media_cache: dict[str, Any] = Depends(get_media_cache),
):
    """Update cached media information (public mode only)."""
    if not PUBLIC_MODE:
        raise HTTPException(
            status_code=404, detail="Endpoint not available in local mode"
        )

    expected_key = config.get("server.api_key", "your-secret-key")
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    cache_key = user_id or "default"
    media_cache[cache_key] = request.get("media_info")
    media_cache[f"{cache_key}_timestamp"] = datetime.now().isoformat()

    return {"status": "updated", "user_id": cache_key}


@app.get("/api/v1/status")
async def get_status(
    poller: Optional[BasePoller] = Depends(get_poller),
    media_cache: dict[str, Any] = Depends(get_media_cache),
):
    """Get current service status and cached media info."""
    mode = "public" if PUBLIC_MODE else "local"

    if PUBLIC_MODE:
        return {
            "status": "running",
            "mode": mode,
            "cache_keys": [
                k for k in media_cache.keys() if not k.endswith("_timestamp")
            ],
            "timestamp": datetime.now().isoformat(),
        }
    else:
        current_media = None
        if poller:
            try:
                current_media = await poller.get_media_info()
                current_media = current_media.to_dict() if current_media else None
            except Exception:
                pass

        return {
            "status": "running",
            "mode": mode,
            "current_media": current_media,
            "timestamp": datetime.now().isoformat(),
        }


@app.get("/health")
async def health_check(
    poller: Optional[BasePoller] = Depends(get_poller),
    renderer: Optional[Renderer] = Depends(get_renderer),
):
    """Detailed health check endpoint."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "mode": "public" if PUBLIC_MODE else "local",
        "debug_info": app_state.debug_info,  # 添加调试信息
        "components": {
            "poller": {
                "available": poller is not None,
                "type": type(poller).__name__ if poller else None,
                "supported": poller.is_supported() if poller else False,
            },
            "renderer": {
                "available": renderer is not None,
                "templates": renderer.list_templates() if renderer else [],
            },
        },
    }

    if poller and not PUBLIC_MODE:
        try:
            test_result = await poller.get_media_info()
            health_status["components"]["poller"]["test_successful"] = True
            health_status["components"]["poller"]["has_media"] = test_result is not None
        except Exception as e:
            health_status["components"]["poller"]["test_successful"] = False
            health_status["components"]["poller"]["error"] = str(e)
            health_status["status"] = "degraded"

    return health_status


@app.get("/api/v1/templates")
async def get_templates(renderer: Optional[Renderer] = Depends(get_renderer)):
    """get available SVG templates."""
    if not renderer:
        raise HTTPException(status_code=503, detail="Renderer not available")
    
    templates = renderer.list_templates()
    return {
        "templates": templates,
        "current_template": "default",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/v1/templates/{template_name}")
async def get_template_content(
    template_name: str,
    renderer: Optional[Renderer] = Depends(get_renderer)
):
    """get content of a specific SVG template."""
    if not renderer:
        raise HTTPException(status_code=503, detail="Renderer not available")
    
    try:
        template_path = renderer.template_dir / f"{template_name}.svg"
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {
                "template_name": template_name,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail="Template not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading template: {str(e)}")


@app.post("/api/v1/preview")
async def preview_custom_svg(
    request: dict,
    renderer: Optional[Renderer] = Depends(get_renderer)
):
    """preview custom SVG content with optional mock data."""
    if not renderer:
        raise HTTPException(status_code=503, detail="Renderer not available")
    
    try:
        svg_content = request.get("svg_content", "")
        mock_data = request.get("mock_data", {})
        
        if mock_data:
            svg_content = svg_content.replace("{{title}}", mock_data.get("title", ""))
            svg_content = svg_content.replace("{{artist}}", mock_data.get("artist", ""))
            svg_content = svg_content.replace("{{album}}", mock_data.get("album", ""))
            svg_content = svg_content.replace("{{album_art}}", mock_data.get("album_art", ""))
        
        return Response(
            content=svg_content,
            media_type="image/svg+xml",
            headers={
                "Cache-Control": "no-cache",
                "Access-Control-Allow-Origin": "*",
            }
        )
        
    except Exception as e:
        error_svg = f"""
        <svg width="400" height="120" xmlns="http://www.w3.org/2000/svg">
            <rect width="400" height="120" fill="#ff4444"/>
            <text x="10" y="50" fill="white">Preview Error: {str(e)}</text>
        </svg>
        """
        return Response(content=error_svg, media_type="image/svg+xml")



if __name__ == "__main__":
    import uvicorn

    port = config.get("server.port", 8000)
    uvicorn.run(app, host="0.0.0.0", port=port)

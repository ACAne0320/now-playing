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

print(f"API entry point initialized")
print(f"PUBLIC_MODE: {os.environ.get('PUBLIC_MODE')}")
print(f"Project root: {project_root}")
print(f"Python path: {sys.path[:3]}")

try:
    # Import the FastAPI app
    print("Importing client.main...")
    from client.main import app, app_state
    print("Import successful")
    
    # Force initialization in serverless environment
    print("Checking app_state initialization...")
    print(f"App state renderer: {app_state.renderer}")
    print(f"App state debug_info: {app_state.debug_info}")
    
    # If debug_info is empty, it means lifespan wasn't called
    if not app_state.debug_info:
        print("Debug info is empty - manually triggering renderer initialization...")
        try:
            from client.renderer.engine import Renderer
            import traceback
            
            debug_msg = "Manual initialization in serverless environment"
            app_state.debug_info.append(debug_msg)
            print(debug_msg)
            
            # Try to initialize renderer manually
            app_state.renderer = Renderer()
            success_msg = "Manual renderer initialization successful"
            app_state.debug_info.append(success_msg)
            print(success_msg)
            
        except Exception as manual_e:
            error_msg = f"Manual renderer initialization failed: {manual_e}"
            app_state.debug_info.append(error_msg)
            print(error_msg)
            
            # Add traceback
            traceback_msg = f"Traceback: {traceback.format_exc()}"
            app_state.debug_info.append(traceback_msg)
            print(traceback_msg)
            
            # Try with absolute path
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_dir = os.path.dirname(current_dir)
                template_dir = os.path.join(project_dir, "client", "renderer", "templates")
                
                path_msg = f"Trying manual path: {template_dir}"
                app_state.debug_info.append(path_msg)
                print(path_msg)
                
                exists_msg = f"Template dir exists: {os.path.exists(template_dir)}"
                app_state.debug_info.append(exists_msg)
                print(exists_msg)
                
                if os.path.exists(template_dir):
                    contents_msg = f"Template contents: {os.listdir(template_dir)}"
                    app_state.debug_info.append(contents_msg)
                    print(contents_msg)
                
                app_state.renderer = Renderer(template_dir=template_dir)
                manual_abs_success = "Manual renderer with absolute path successful"
                app_state.debug_info.append(manual_abs_success)
                print(manual_abs_success)
                
            except Exception as abs_e:
                abs_error_msg = f"Manual absolute path failed: {abs_e}"
                app_state.debug_info.append(abs_error_msg)
                print(abs_error_msg)
    
except Exception as e:
    print(f"Error importing app: {e}")
    import traceback
    traceback.print_exc()
    
    # Create a minimal error app
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/")
    async def error_root():
        return {"error": "Failed to import main app", "details": str(e)}
    
    @app.get("/health")
    async def health():
        return {"status": "error", "message": "Main app failed to load"}

print("API entry point setup complete")

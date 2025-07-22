#!/bin/bash
set -e

echo "🚀 Installing Now Playing service with uv..."

if ! command -v uv &> /dev/null; then
    echo "❌ uv not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

echo "📦 Syncing dependencies..."
uv sync

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "🪟 Installing Windows dependencies..."
    uv sync --extra windows
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Installing macOS dependencies..."
    uv sync --extra macos
fi

if [[ "${INSTALL_DEV:-}" == "true" ]]; then
    echo "🛠️ Installing development dependencies..."
    uv sync --dev
fi

echo "✅ Installation complete!"
echo "🎵 To start the service: uv run uvicorn client.main:app --reload"

echo "🎵 Choose startup mode:"
echo "1) Local Client (for OBS integration)"
echo "2) Public Server (for GitHub README)"
echo "3) Public Client (send data to remote server)"
echo "4) Exit"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "🖥️ Starting Local Client..."
        
        if [[ -f "config.json" ]]; then
            PORT=$(python -c "
import json
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    print(config.get('server', {}).get('port', 8000))
except:
    print(8000)
" 2>/dev/null || echo "8000")
        else
            PORT=8000
        fi
        
        echo "📍 Service will be available at: http://localhost:${PORT}"
        echo "📦 Web interface: http://localhost:${PORT}/web"
        echo "🎨 SVG endpoint: http://localhost:${PORT}/now-playing.svg"
        echo "🛑 Press Ctrl+C to stop"
        echo ""
        
        export PUBLIC_MODE=false
        uv run uvicorn client.main:app --reload --host 0.0.0.0 --port ${PORT}
        ;;
    2)
        echo "🌐 Starting Public Server..."
        echo "⚠️  Make sure to set NOW_PLAYING_API_KEY environment variable"
        
        if [[ -z "${NOW_PLAYING_API_KEY}" ]]; then
            echo "❌ NOW_PLAYING_API_KEY not set. Please set it first:"
            echo "   export NOW_PLAYING_API_KEY='your-secure-api-key'"
            exit 1
        fi
        
        if [[ -f "config.json" ]]; then
            PORT=$(python -c "
import json
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    print(config.get('server', {}).get('port', 8000))
except:
    print(8000)
" 2>/dev/null || echo "8000")
        else
            PORT=8000
        fi
        
        echo "📍 Server will be available at: http://0.0.0.0:${PORT}"
        echo "🔑 API Key: ${NOW_PLAYING_API_KEY:0:8}..."
        echo "🛑 Press Ctrl+C to stop"
        echo ""
        
        export PUBLIC_MODE=true
        uv run uvicorn client.main:app --host 0.0.0.0 --port ${PORT}
        ;;
    3)
        echo "📤 Starting Public Client..."
        
        if [[ ! -f "config.json" ]]; then
            echo "❌ Configuration file not found: config.json"
            echo "📋 Please create it from config.example.json"
            exit 1
        fi
        
        echo "📡 Sending local media info to remote server..."
        echo "⚙️  Configuration: config.json"
        echo "🛑 Press Ctrl+C to stop"
        echo ""
        
        uv run python server/public_client.py
        ;;
    4)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac
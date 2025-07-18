# 🎵 Now Playing Service

A cross-platform music information service that displays currently playing media as beautiful SVG cards. Perfect for OBS streaming overlays, GitHub profiles, and web integrations.

[![CI/CD](https://github.com/ACAne0320/now-playing/actions/workflows/ci.yml/badge.svg)](https://github.com/ACAne0320/now-playing/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

## ✨ Features

- 🎨 **Beautiful SVG Cards**: Multiple customizable templates with album art
- 🖥️ **Cross-Platform**: Native support for Windows and macOS media APIs
- 🔄 **Real-time Updates**: Live media information with automatic refresh
- 🎮 **OBS Integration**: Perfect for streaming overlays and screen recordings
- 🌐 **GitHub Integration**: Display your music taste on your profile
- 🚀 **Modern Stack**: Built with FastAPI, uv, and platform-specific APIs
- 📱 **Responsive Design**: Adapts to different screen sizes and contexts

## 🖼️ Template Gallery

### Default

![Default Template](https://now-playing-acane.vercel.app/now-playing.svg?template=default)

### Minimalist

![Minimalist Template](https://now-playing-acane.vercel.app/now-playing.svg?template=minimalist)

### Neo

![Neo Template](https://now-playing-acane.vercel.app/now-playing.svg?template=neo)

### Rounded

![Rounded Template](https://now-playing-acane.vercel.app/now-playing.svg?template=rounded)

### Music Card

![Music Card Template](https://now-playing-acane.vercel.app/now-playing.svg?template=music-card)

### Sky 

![Sky Template](https://now-playing-acane.vercel.app/now-playing.svg?template=sky)

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

#### Option 1: Shell Script (Recommended)

```bash
# Clone the repository
git clone https://github.com/ACAne0320/now-playing.git
cd now-playing

# Copy configuration template
cp config.example.json config.json

# Edit config.json as needed (optional)

# Run the interactive launcher
./start.sh
```

#### Option 2: Manual Installation

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and navigate to the project
git clone https://github.com/ACAne0320/now-playing.git
cd now-playing

# Setup configuration
cp config.example.json config.json

# Sync dependencies
uv sync

# Platform-specific dependencies
uv sync --extra windows  # Windows
uv sync --extra macos    # macOS

# Start the service (will use config.json settings)
uv run python -m client.main
```

## 🎯 Usage Modes

### 1. 🖥️ Local Mode (OBS Integration)

Perfect for streaming and local applications:

```bash
# Configure config.json for local mode
{
  "server": {
    "public_mode": false,
    "port": 8000
  }
}

# Start local service (will use config.json settings)
uv run python -m client.main
```

**Access points:**

- Health check: `http://localhost:8000/` (or your configured port)
- Web interface: `http://localhost:8000/web`
- SVG card: `http://localhost:8000/now-playing.svg`
- Status API: `http://localhost:8000/api/v1/status`

**OBS Studio Setup:**

1. Add "Browser Source" to your scene
2. Set URL to: `http://localhost:8000/now-playing.svg` (adjust port if needed)
3. Set dimensions to 400x120 (or customize)
4. Enable "Refresh browser when scene becomes active"

### 2. 🌐 Public Mode (GitHub Integration)

Deploy to cloud for GitHub README integration:

```bash
# Configure config.json for public mode
{
  "server": {
    "public_mode": true,
    "api_key": "your-secure-api-key",
    "port": 8000
  }
}

# Or use environment variables
export PUBLIC_MODE=true
export NOW_PLAYING_API_KEY=your-secure-api-key

# Start public server
uv run python -m client.main
```

**GitHub README Integration:**

```markdown
![Now Playing](https://yours-now-playing-server/now-playing.svg)
```

### 3. 📤 Client Mode (Remote Data Push)

Send local media data to remote server:

```bash
# Configure config.json
{
  "server": {
    "public_mode": false,
    "api_key": "dev-secret-key-12345",
    "poll_interval": 5,
    "log_level": "INFO",
    "port": 8000,
    "template_dir": "",
    "enable_album_art": true
  },
  "client": {
    "server_url": "https://yours-now-playing-serverp",
    "api_key": "your-secure-api-key",
    "poll_interval": 10,
    "template": "default"
  }
}

# Start client
uv run python server/public_client.py
```

## ⚙️ Configuration

### Configuration Files

The service uses a unified configuration system with the following priority:

1. **Environment Variables** (highest priority)
2. **config.json** (main configuration file)
3. **Built-in defaults** (lowest priority)

### Setup Configuration

```bash
# Copy example configuration
cp config.example.json config.json

# Edit configuration as needed
# The config.json file contains both server and client settings
```

### Configuration Structure

```json
{
  "server": {
    "public_mode": false,           // Enable public/private mode
    "api_key": "your-secret-key",   // API authentication key
    "poll_interval": 5,             // Media polling interval (seconds)
    "log_level": "INFO",            // Logging level
    "port": 8000,                   // Server port
    "template_dir": "",             // Custom template directory
    "enable_album_art": true        // Enable album art display
  },
  "client": {
    "server_url": "http://localhost:8000",  // Remote server URL
    "api_key": "your-secret-key",           // Client API key
    "poll_interval": 10,                    // Client polling interval
    "template": "default"                   // Default template
  }
}
```

### Environment Variable Overrides

You can override any configuration setting using environment variables:

```bash
# Server configuration
export PUBLIC_MODE=true
export NOW_PLAYING_API_KEY=your-secret-key
export NOW_PLAYING_POLL_INTERVAL=5
export LOG_LEVEL=DEBUG
export PORT=8080
export TEMPLATE_DIR=./custom_templates
export ENABLE_ALBUM_ART=false

# Client configuration
export NOW_PLAYING_SERVER_URL=https://your-app.vercel.app
export NOW_PLAYING_CLIENT_API_KEY=your-client-key
export NOW_PLAYING_CLIENT_POLL_INTERVAL=15
export NOW_PLAYING_TEMPLATE=modern-card
```

## 🎨 Customization

### Templates

Available templates:

- `default`: Full-featured with album art and progress
- `modern-card`: Beautiful gradient card with modern design
- `minimalist-line`: Clean line-based design with circular album art
- `modern-dark`: Dark theme with coding aesthetic
- `glassmorphism`: Translucent glass effect with blur
- `neo`: Neumorphism design with 3D shadows
- `rounded`: Modern rounded design with clean layout
- `minimalist`: Clean and simple design
- `rounded-simple`: Simplified rounded template
- `music-card`: Spotify-like card with animated sound bars

```bash
# Use specific template
http://localhost:8000/now-playing.svg?template=music-card
```

### Custom CSS

Inject custom styles:

```bash
# Custom colors
http://localhost:8000/now-playing.svg?custom_css=.title{fill:red;}.artist{fill:blue;}

# Custom fonts
http://localhost:8000/now-playing.svg?custom_css=.title{font-family:Arial,sans-serif;}
```

## 🏗️ Architecture

### Platform Support

| Platform | API | Status | Features |
|----------|-----|--------|----------|
| Windows 10/11 | Windows SDK | ✅ Full | Media info, album art, playback status |
| macOS 10.15+ | MediaRemote.framework | ✅ Full | Media info, album art, playback status |

## 📦 Deployment

### Docker

```bash
# Build image
docker build -t now-playing .

# Run container
docker run -d -p 8000:8000 \
  -e PUBLIC_MODE=true \
  -e NOW_PLAYING_API_KEY=your-key \
  now-playing
```

### Cloud Platforms

#### Vercel (Recommended)

```bash
# coming soon
```

## 🧪 Development

### Setup Development Environment

```bash
uv sync --dev
```

### Adding New Templates

1. Create SVG template in `client/renderer/templates/`
2. Use Jinja2 templating with `media_info` context
3. Follow existing template patterns for consistency
4. Test with various media states

```jinja2
<!-- Example template structure -->
<svg width="400" height="120" xmlns="http://www.w3.org/2000/svg">
  {% if media_info %}
    <text class="title">{{ media_info.title }}</text>
    <text class="artist">{{ media_info.artist }}</text>
    {% if media_info.album_art_b64 %}
      <image href="data:image/png;base64,{{ media_info.album_art_b64 }}" />
    {% endif %}
  {% else %}
    <text>No media playing</text>
  {% endif %}
</svg>

## 🔒 Security

### API Security

- **Authentication**: API key-based authentication for public mode
- **Rate Limiting**: Built-in request throttling
- **Input Validation**: Pydantic-based data validation
- **CORS**: Configurable cross-origin resource sharing

### Best Practices

- Use strong API keys (32+ characters)
- Enable HTTPS in production
- Regularly rotate API keys
- Monitor logs for unusual activity
- Implement IP whitelisting if needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

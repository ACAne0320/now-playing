"""
Unified configuration management for Now Playing service.
Supports both server and client configurations.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Unified configuration manager."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration with optional config file path."""
        self.config_file = config_file or "config.json"
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file and environment variables."""
        config = {}
        
        # Try to load from JSON config file
        config_path = Path(self.config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except Exception as e:
                print(f"Warning: Error loading {self.config_file}: {e}")
        
        # Server configuration (with environment variable overrides)
        config.setdefault("server", {})
        config["server"].setdefault("public_mode", 
            os.getenv("PUBLIC_MODE", "false").lower() == "true")
        config["server"].setdefault("api_key", 
            os.getenv("NOW_PLAYING_API_KEY", "dev-secret-key-12345"))
        config["server"].setdefault("poll_interval", 
            int(os.getenv("NOW_PLAYING_POLL_INTERVAL", "5")))
        config["server"].setdefault("log_level", 
            os.getenv("LOG_LEVEL", "INFO"))
        config["server"].setdefault("port", 
            int(os.getenv("PORT", "8000")))
        config["server"].setdefault("template_dir", 
            os.getenv("TEMPLATE_DIR", ""))
        config["server"].setdefault("enable_album_art", 
            os.getenv("ENABLE_ALBUM_ART", "true").lower() == "true")
        
        # Client configuration (for public deployment)
        config.setdefault("client", {})
        config["client"].setdefault("server_url", 
            os.getenv("NOW_PLAYING_SERVER_URL", "http://localhost:8000"))
        config["client"].setdefault("api_key", 
            os.getenv("NOW_PLAYING_CLIENT_API_KEY", config["server"]["api_key"]))
        config["client"].setdefault("poll_interval", 
            int(os.getenv("NOW_PLAYING_CLIENT_POLL_INTERVAL", "10")))
        config["client"].setdefault("template", 
            os.getenv("NOW_PLAYING_TEMPLATE", "default"))
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'server.api_key')."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_server_config(self) -> Dict[str, Any]:
        """Get server configuration."""
        return self._config.get("server", {})
    
    def get_client_config(self) -> Dict[str, Any]:
        """Get client configuration."""
        return self._config.get("client", {})
    
    def save_config(self, config_path: Optional[str] = None) -> None:
        """Save current configuration to file."""
        path = config_path or self.config_file
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)
    
    def update(self, key: str, value: Any) -> None:
        """Update configuration value using dot notation."""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value


# Global configuration instance
_config = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def init_config(config_file: Optional[str] = None) -> Config:
    """Initialize configuration with specific file."""
    global _config
    _config = Config(config_file)
    return _config

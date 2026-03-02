"""Configuration loader for Equipment Hours Validation."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class Config:
    """Configuration manager for the application."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration loader.
        
        Args:
            config_file: Path to YAML configuration file. If None, uses default.
        """
        # Load environment variables from .env file
        load_dotenv()
        
        # Determine config file path
        if config_file is None:
            config_file = os.path.join(
                Path(__file__).parent.parent, 
                "config", 
                "settings.yaml"
            )
        
        self.config_file = config_file
        self._config = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file and environment variables."""
        # Load YAML config if file exists
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self._config = yaml.safe_load(f) or {}
        else:
            self._config = {}
        
        # Override with environment variables
        env_overrides = {
            'database_url': os.getenv('DATABASE_URL'),
            'database_path': os.getenv('DATABASE_PATH'),
            'log_level': os.getenv('LOG_LEVEL'),
            'debug': os.getenv('DEBUG'),
        }
        
        # Apply environment variable overrides
        for key, value in env_overrides.items():
            if value is not None:
                self._config[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key (supports dot notation for nested keys)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_database_path(self) -> str:
        """Get database path from configuration."""
        db_path = self.get('database_path')
        if not db_path:
            # Default to SQLite database in data directory
            db_path = os.path.join(
                Path(__file__).parent.parent,
                "data",
                "db.sqlite"
            )
        return db_path
    
    def get_log_level(self) -> str:
        """Get log level from configuration."""
        return self.get('log_level', 'INFO')
    
    def is_debug(self) -> bool:
        """Check if debug mode is enabled."""
        return self.get('debug', False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Return all configuration as dictionary."""
        return self._config.copy()


# Global configuration instance
config = Config()

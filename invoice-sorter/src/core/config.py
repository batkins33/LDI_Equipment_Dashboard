"""Configuration management for Invoice Sorter"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from .models import ProcessingConfig


class Config:
    """Configuration manager for Invoice Sorter"""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration

        Args:
            config_path: Path to configuration YAML file
        """
        # Load environment variables
        load_dotenv()

        # Default config path
        if config_path is None:
            config_path = os.getenv(
                "INVOICE_SORTER_CONFIG",
                str(Path(__file__).parent.parent.parent / "config" / "settings.yaml")
            )

        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load configuration from YAML file"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self._config = yaml.safe_load(f) or {}
        else:
            # Use defaults if config file doesn't exist
            self._config = self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "google_drive": {
                "input_folder_id": os.getenv("INPUT_FOLDER_ID", ""),
                "review_folder_id": os.getenv("REVIEW_FOLDER_ID", ""),
            },
            "google_vision": {
                "enabled": os.getenv("USE_VISION_API", "true").lower() == "true",
            },
            "llm": {
                "enabled": os.getenv("USE_LLM", "false").lower() == "true",
                "provider": os.getenv("LLM_PROVIDER", "openai"),
                "model": os.getenv("LLM_MODEL", "gpt-4"),
            },
            "logging": {
                "sheet_id": os.getenv("LOG_SHEET_ID", ""),
            },
            "vendor_mapping": {
                "source": os.getenv("VENDOR_MAPPING_SOURCE", "sheet"),
                "sheet_id": os.getenv("VENDOR_MAPPING_SHEET_ID", ""),
            },
            "filename": {
                "pattern": os.getenv("FILENAME_PATTERN", "{vendor}__{invoice_number}__{date}.pdf"),
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key

        Args:
            key: Configuration key (e.g., 'google_drive.input_folder_id')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value

    def get_processing_config(self) -> ProcessingConfig:
        """Get processing configuration as ProcessingConfig object

        Returns:
            ProcessingConfig instance
        """
        return ProcessingConfig(
            input_folder_id=self.get("google_drive.input_folder_id", ""),
            review_folder_id=self.get("google_drive.review_folder_id", ""),
            log_sheet_id=self.get("logging.sheet_id"),
            vendor_mapping_sheet_id=self.get("vendor_mapping.sheet_id"),
            use_vision_api=self.get("google_vision.enabled", True),
            use_llm=self.get("llm.enabled", False),
            filename_pattern=self.get("filename.pattern", "{vendor}__{invoice_number}__{date}.pdf"),
        )

    def save(self, config_path: Optional[str] = None) -> None:
        """Save current configuration to YAML file

        Args:
            config_path: Path to save configuration (uses default if None)
        """
        save_path = config_path or self.config_path
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, 'w') as f:
            yaml.dump(self._config, f, default_flow_style=False)

    def update(self, key: str, value: Any) -> None:
        """Update configuration value

        Args:
            key: Configuration key (dot-notation)
            value: New value
        """
        keys = key.split('.')
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value


# Global config instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get global configuration instance

    Returns:
        Config instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance

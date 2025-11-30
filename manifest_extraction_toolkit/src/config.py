"""Configuration management for manifest extraction toolkit."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class OCRConfig:
    """OCR engine configuration."""
    dpi: int = 300
    engine: str = "PyMuPDF"
    tesseract_oem: int = 3
    tesseract_psm_single_line: int = 7
    tesseract_psm_block: int = 6


@dataclass
class HandwritingConfig:
    """Handwriting processing configuration."""
    binarization_threshold: int = 180
    median_filter_size: int = 3
    bottom_band_top_percent: float = 0.82
    bottom_band_bottom_percent: float = 0.97
    bottom_band_left_percent: float = 0.05
    bottom_band_right_percent: float = 0.95


@dataclass
class ROIConfig:
    """Region of Interest positioning configuration."""
    right_of: Dict[str, int] = field(default_factory=lambda: {
        "dx": 10, "w": 220, "dy": -5, "h": 36
    })
    below_band: Dict[str, Any] = field(default_factory=lambda: {
        "top_pad": 8, "bottom": 70, "left": 0.08, "right": 0.62
    })


@dataclass
class PerformanceConfig:
    """Performance and optimization settings."""
    enable_caching: bool = True
    cache_size_mb: int = 500
    enable_parallel: bool = True
    max_workers: int = 4
    batch_size: int = 10


@dataclass
class ProcessingConfig:
    """PDF processing options."""
    max_pages_to_search: int = 3
    skip_on_error: bool = False
    validate_output: bool = True
    max_file_size_mb: int = 100


@dataclass
class OutputConfig:
    """Output formatting and storage settings."""
    default_format: str = "xlsx"
    include_timestamp: bool = True
    save_debug_images: bool = False
    debug_output_dir: str = "debug_output"


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None


@dataclass
class PathsConfig:
    """Default path configuration."""
    input_dir: Optional[str] = None
    output_dir: str = "output"
    combined_dir: Optional[str] = None


@dataclass
class Config:
    """Main configuration container."""
    ocr: OCRConfig = field(default_factory=OCRConfig)
    handwriting: HandwritingConfig = field(default_factory=HandwritingConfig)
    roi: ROIConfig = field(default_factory=ROIConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    fields: Dict[str, Any] = field(default_factory=dict)
    anchors: Dict[str, List[str]] = field(default_factory=dict)
    validation: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Config:
        """Create Config from dictionary."""
        return cls(
            ocr=OCRConfig(**data.get("ocr", {})),
            handwriting=HandwritingConfig(**data.get("handwriting", {})),
            roi=ROIConfig(**data.get("roi", {})),
            performance=PerformanceConfig(**data.get("performance", {})),
            processing=ProcessingConfig(**data.get("processing", {})),
            output=OutputConfig(**data.get("output", {})),
            logging=LoggingConfig(**data.get("logging", {})),
            paths=PathsConfig(**data.get("paths", {})),
            fields=data.get("fields", {}),
            anchors=data.get("anchors", {}),
            validation=data.get("validation", {}),
        )

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> Config:
        """Load configuration from YAML file.

        Parameters
        ----------
        config_path : Optional[Path]
            Path to config file. If None, searches for config.yaml in:
            1. Environment variable MANIFEST_EXTRACT_CONFIG
            2. Current directory
            3. Script directory
            4. Package directory

        Returns
        -------
        Config
            Loaded configuration object.
        """
        if config_path is None:
            # Try environment variable first
            env_config = os.getenv("MANIFEST_EXTRACT_CONFIG")
            if env_config:
                config_path = Path(env_config)
            else:
                # Search common locations
                search_paths = [
                    Path.cwd() / "config.yaml",
                    Path(__file__).parent.parent / "config.yaml",
                    Path(__file__).parent / "config.yaml",
                ]
                for path in search_paths:
                    if path.exists():
                        config_path = path
                        break

        if config_path and config_path.exists():
            with open(config_path, "r") as f:
                data = yaml.safe_load(f)
            return cls.from_dict(data)
        else:
            # Return default configuration
            return cls()

    def get_field_roi(self, field_name: str) -> Dict[str, Any]:
        """Get ROI configuration for a specific field.

        Returns field-specific overrides if available, otherwise defaults.
        """
        if field_name in self.fields:
            return self.fields[field_name]

        # Return appropriate defaults based on field type
        if "company" in field_name:
            return {
                **self.roi.below_band,
                "type": "below_band"
            }
        else:
            return {
                **self.roi.right_of,
                "type": "right_of"
            }

    def get_anchor_tokens(self, field_name: str) -> List[str]:
        """Get anchor tokens for a field."""
        return self.anchors.get(field_name, [])

    def validate_file_size(self, file_path: Path) -> bool:
        """Check if file size is within limits."""
        size_mb = file_path.stat().st_size / (1024 * 1024)
        return size_mb <= self.processing.max_file_size_mb


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get global configuration instance (singleton pattern)."""
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def reload_config(config_path: Optional[Path] = None) -> Config:
    """Reload configuration from file."""
    global _config
    _config = Config.load(config_path)
    return _config

"""Tests for configuration management."""

from pathlib import Path
import tempfile
import pytest
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import Config, OCRConfig, HandwritingConfig, ROIConfig


class TestConfigDefaults:
    """Test default configuration values."""

    def test_default_config_creation(self):
        config = Config()
        assert config.ocr.dpi == 300
        assert config.ocr.engine == "PyMuPDF"
        assert config.performance.enable_caching is True
        assert config.performance.max_workers == 4

    def test_ocr_config_defaults(self):
        ocr = OCRConfig()
        assert ocr.dpi == 300
        assert ocr.tesseract_oem == 3
        assert ocr.tesseract_psm_single_line == 7
        assert ocr.tesseract_psm_block == 6

    def test_handwriting_config_defaults(self):
        hw = HandwritingConfig()
        assert hw.binarization_threshold == 180
        assert hw.median_filter_size == 3
        assert 0 < hw.bottom_band_top_percent < 1
        assert 0 < hw.bottom_band_bottom_percent <= 1

    def test_roi_config_defaults(self):
        roi = ROIConfig()
        assert "dx" in roi.right_of
        assert "dy" in roi.right_of
        assert "top_pad" in roi.below_band


class TestConfigFromDict:
    """Test config creation from dictionary."""

    def test_from_dict_partial(self):
        data = {"ocr": {"dpi": 600}, "performance": {"max_workers": 8}}
        config = Config.from_dict(data)

        assert config.ocr.dpi == 600
        assert config.performance.max_workers == 8
        # Defaults should still be set
        assert config.ocr.engine == "PyMuPDF"

    def test_from_dict_empty(self):
        config = Config.from_dict({})
        # Should create with all defaults
        assert config.ocr.dpi == 300

    def test_from_dict_full(self):
        data = {
            "ocr": {"dpi": 600, "engine": "Custom", "tesseract_oem": 1, "tesseract_psm_single_line": 6, "tesseract_psm_block": 3},
            "handwriting": {"binarization_threshold": 200, "median_filter_size": 5, "bottom_band_top_percent": 0.8, "bottom_band_bottom_percent": 0.95, "bottom_band_left_percent": 0.1, "bottom_band_right_percent": 0.9},
            "performance": {"enable_caching": False, "cache_size_mb": 1000, "enable_parallel": False, "max_workers": 2, "batch_size": 5},
            "fields": {"manifest_number": {"dx": 15, "w": 250}},
            "anchors": {"manifest_number": ["test", "anchor"]},
            "validation": {"phone_length": 11},
        }
        config = Config.from_dict(data)

        assert config.ocr.dpi == 600
        assert config.handwriting.binarization_threshold == 200
        assert config.performance.max_workers == 2
        assert config.fields["manifest_number"]["dx"] == 15
        assert config.anchors["manifest_number"] == ["test", "anchor"]
        assert config.validation["phone_length"] == 11


class TestConfigLoad:
    """Test loading configuration from YAML file."""

    def test_load_from_file(self):
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("""
ocr:
  dpi: 400
  engine: TestEngine

performance:
  max_workers: 16
  enable_parallel: true

handwriting:
  binarization_threshold: 190
""")
            config_path = Path(f.name)

        try:
            config = Config.load(config_path)
            assert config.ocr.dpi == 400
            assert config.ocr.engine == "TestEngine"
            assert config.performance.max_workers == 16
            assert config.handwriting.binarization_threshold == 190
        finally:
            config_path.unlink()

    def test_load_nonexistent_file(self):
        # Should return default config
        config = Config.load(Path("/nonexistent/config.yaml"))
        assert config.ocr.dpi == 300  # Default value


class TestConfigMethods:
    """Test configuration helper methods."""

    def test_get_field_roi_manifest(self):
        config = Config()
        config.fields = {"manifest_number": {"dx": 20, "w": 300}}

        roi_config = config.get_field_roi("manifest_number")
        assert roi_config["dx"] == 20
        assert roi_config["w"] == 300

    def test_get_field_roi_company_default(self):
        config = Config()
        roi_config = config.get_field_roi("t1_company")

        # Should return below_band defaults for company fields
        assert "type" in roi_config
        assert roi_config["type"] == "below_band"

    def test_get_field_roi_other_default(self):
        config = Config()
        roi_config = config.get_field_roi("t1_phone")

        # Should return right_of defaults for non-company fields
        assert "type" in roi_config
        assert roi_config["type"] == "right_of"

    def test_get_anchor_tokens(self):
        config = Config()
        config.anchors = {"test_field": ["token1", "token2", "token3"]}

        tokens = config.get_anchor_tokens("test_field")
        assert tokens == ["token1", "token2", "token3"]

    def test_get_anchor_tokens_missing(self):
        config = Config()
        tokens = config.get_anchor_tokens("nonexistent")
        assert tokens == []

    def test_validate_file_size_valid(self):
        config = Config()
        config.processing.max_file_size_mb = 100

        # Create tiny temp file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"small file")
            temp_path = Path(f.name)

        try:
            assert config.validate_file_size(temp_path) is True
        finally:
            temp_path.unlink()

    def test_validate_file_size_too_large(self):
        config = Config()
        config.processing.max_file_size_mb = 0.000001  # Very small limit

        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"x" * 1000)  # 1KB file
            temp_path = Path(f.name)

        try:
            assert config.validate_file_size(temp_path) is False
        finally:
            temp_path.unlink()


class TestConfigIntegration:
    """Integration tests for config system."""

    def test_full_config_lifecycle(self):
        # Create config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("""
ocr:
  dpi: 450
  engine: Custom

performance:
  enable_caching: false
  max_workers: 12

handwriting:
  binarization_threshold: 175

fields:
  manifest_number:
    dx: 25
    w: 300

anchors:
  manifest_number:
    - manifest
    - doc
    - number

validation:
  phone_length: 11
""")
            config_path = Path(f.name)

        try:
            # Load config
            config = Config.load(config_path)

            # Verify all sections
            assert config.ocr.dpi == 450
            assert config.performance.enable_caching is False
            assert config.handwriting.binarization_threshold == 175

            # Test helper methods
            roi = config.get_field_roi("manifest_number")
            assert roi["dx"] == 25

            tokens = config.get_anchor_tokens("manifest_number")
            assert tokens == ["manifest", "doc", "number"]

            assert config.validation["phone_length"] == 11

        finally:
            config_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

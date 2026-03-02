"""Tests for configuration loader."""

import pytest
import os
import tempfile
import yaml
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import Config


class TestConfig:
    """Test cases for Config class."""
    
    def test_default_initialization(self):
        """Test config loads with default settings file."""
        config = Config()
        assert config is not None
        assert config.get('log_level') == 'INFO'
        assert config.get('debug') is False
    
    def test_get_with_default(self):
        """Test getting values with defaults."""
        config = Config()
        assert config.get('nonexistent_key', 'default') == 'default'
        assert config.get('nonexistent_key') is None
    
    def test_get_database_path(self):
        """Test database path resolution."""
        config = Config()
        db_path = config.get_database_path()
        assert db_path.endswith('db.sqlite')
        assert 'data' in db_path
    
    def test_get_log_level(self):
        """Test log level retrieval."""
        config = Config()
        assert config.get_log_level() == 'INFO'
    
    def test_is_debug(self):
        """Test debug mode detection."""
        config = Config()
        assert config.is_debug() is False
    
    def test_environment_override(self):
        """Test environment variable overrides."""
        # Set environment variable
        os.environ['LOG_LEVEL'] = 'DEBUG'
        os.environ['DEBUG'] = 'true'
        
        try:
            config = Config()
            assert config.get('log_level') == 'DEBUG'
            assert config.get('debug') == 'true'
        finally:
            # Clean up
            os.environ.pop('LOG_LEVEL', None)
            os.environ.pop('DEBUG', None)
    
    def test_custom_config_file(self):
        """Test loading custom configuration file."""
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            test_config = {
                'log_level': 'ERROR',
                'custom_setting': 'test_value',
                'nested': {
                    'key': 'nested_value'
                }
            }
            yaml.dump(test_config, f)
            temp_file = f.name
        
        try:
            config = Config(temp_file)
            assert config.get('log_level') == 'ERROR'
            assert config.get('custom_setting') == 'test_value'
            assert config.get('nested.key') == 'nested_value'
        finally:
            os.unlink(temp_file)
    
    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = Config()
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert 'log_level' in config_dict
    
    def test_missing_config_file(self):
        """Test behavior when config file doesn't exist."""
        config = Config('nonexistent_file.yaml')
        # Should not raise error and use defaults
        assert config.get('log_level', 'INFO') == 'INFO'


if __name__ == '__main__':
    pytest.main([__file__])

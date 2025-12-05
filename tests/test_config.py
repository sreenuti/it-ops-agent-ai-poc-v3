"""
Tests for configuration management
"""
import pytest
import os
from src.config.settings import Settings, get_settings, reload_settings


def test_settings_loads_from_env(sample_env_vars):
    """Test that settings load from environment variables"""
    settings = Settings()
    
    assert settings.openai_api_key == "test-openai-key"
    assert settings.openai_model == "gpt-4"
    assert settings.chroma_host == "localhost"
    assert settings.chroma_port == 8000
    assert settings.agent_framework == "langchain"


def test_settings_defaults():
    """Test that settings have proper defaults"""
    # Create settings with minimal required env vars
    os.environ["OPENAI_API_KEY"] = "test-key"
    
    settings = Settings()
    
    assert settings.openai_model == "gpt-4"
    assert settings.chroma_host == "localhost"
    assert settings.chroma_port == 8000
    assert settings.agent_framework == "langchain"
    assert settings.log_level == "INFO"
    assert settings.app_port == 7860
    assert settings.debug is False
    
    # Cleanup
    del os.environ["OPENAI_API_KEY"]


def test_settings_validation():
    """Test that settings validate correctly"""
    os.environ["OPENAI_API_KEY"] = "test-key"
    os.environ["AGENT_FRAMEWORK"] = "invalid"
    
    with pytest.raises(Exception):  # Should raise validation error
        Settings()
    
    # Cleanup
    del os.environ["OPENAI_API_KEY"]
    del os.environ["AGENT_FRAMEWORK"]


def test_get_settings_singleton():
    """Test that get_settings returns singleton"""
    os.environ["OPENAI_API_KEY"] = "test-key"
    
    settings1 = get_settings()
    settings2 = get_settings()
    
    assert settings1 is settings2
    
    # Cleanup
    del os.environ["OPENAI_API_KEY"]


def test_reload_settings():
    """Test that reload_settings creates new instance"""
    os.environ["OPENAI_API_KEY"] = "test-key"
    
    settings1 = get_settings()
    os.environ["LOG_LEVEL"] = "DEBUG"
    settings2 = reload_settings()
    
    assert settings1 is not settings2
    assert settings2.log_level == "DEBUG"
    
    # Cleanup
    del os.environ["OPENAI_API_KEY"]
    del os.environ["LOG_LEVEL"]


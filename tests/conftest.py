"""
Pytest configuration and shared fixtures
"""
import pytest
import os
from unittest.mock import Mock, MagicMock
from pathlib import Path


@pytest.fixture
def test_data_dir():
    """Return path to test data directory"""
    return Path(__file__).parent / "data"


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing"""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Mocked LLM response"
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_chroma_client():
    """Mock Chroma client for testing"""
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_collection.query.return_value = {
        "documents": [["Sample instruction text"]],
        "metadatas": [[{"task_type": "password_reset"}]],
        "ids": [["test-id-1"]],
        "distances": [[0.1]]
    }
    mock_collection.add.return_value = None
    mock_client.get_or_create_collection.return_value = mock_collection
    return mock_client


@pytest.fixture
def sample_env_vars(monkeypatch):
    """Set up sample environment variables for testing"""
    env_vars = {
        "OPENAI_API_KEY": "test-openai-key",
        "OPENAI_MODEL": "gpt-4",
        "CHROMA_HOST": "localhost",
        "CHROMA_PORT": "8000",
        "CHROMA_COLLECTION_NAME": "test_collection",
        "AGENT_FRAMEWORK": "langchain",
        "LOG_LEVEL": "DEBUG",
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars


@pytest.fixture
def temp_chroma_dir(tmp_path):
    """Temporary directory for Chroma database during tests"""
    chroma_dir = tmp_path / "chroma_test"
    chroma_dir.mkdir()
    return str(chroma_dir)


@pytest.fixture(autouse=True)
def reset_environment(monkeypatch):
    """Reset environment before each test"""
    # Clear any existing env vars that might interfere
    env_vars_to_clear = [
        "OPENAI_API_KEY",
        "CHROMA_HOST",
        "CHROMA_PORT",
    ]
    for var in env_vars_to_clear:
        monkeypatch.delenv(var, raising=False)


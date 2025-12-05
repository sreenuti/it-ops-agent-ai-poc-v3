"""
Configuration management using Pydantic
"""
import os
from pathlib import Path
from typing import Optional, Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv


def find_project_root() -> Path:
    """
    Find the project root directory by looking for common marker files.
    
    Returns:
        Path to project root directory
    """
    # Start from the current file's directory
    current = Path(__file__).resolve().parent
    
    # Look for project root markers
    markers = [
        "requirements.txt",
        "README.md",
        "pytest.ini",
        ".git",
        "docker",
        "k8s"
    ]
    
    # Walk up the directory tree
    for parent in [current] + list(current.parents):
        if any((parent / marker).exists() for marker in markers):
            return parent
    
    # Fallback to current file's parent's parent (assuming src/config/settings.py structure)
    return current.parent.parent


def load_env_file() -> Path:
    """
    Load .env file from project root directory.
    
    Returns:
        Path to the .env file (if found)
    """
    project_root = find_project_root()
    env_file = project_root / ".env"
    
    # Load .env file if it exists
    if env_file.exists():
        load_dotenv(dotenv_path=env_file, override=False)
        return env_file
    else:
        # Try loading from current directory as fallback
        env_file_current = Path(".env")
        if env_file_current.exists():
            load_dotenv(dotenv_path=env_file_current, override=False)
            return env_file_current
    
    return None


# Load .env file early before Settings class is instantiated
_env_file_path = load_env_file()


def _build_model_config(env_file_path: Optional[Path] = None) -> SettingsConfigDict:
    """
    Build model config dict dynamically based on env file path.
    
    Args:
        env_file_path: Optional path to .env file. If None, uses global _env_file_path.
        
    Returns:
        SettingsConfigDict instance
    """
    config_dict = {
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }
    
    # Use provided path or fall back to global
    path_to_use = env_file_path if env_file_path is not None else _env_file_path
    
    if path_to_use:
        config_dict["env_file"] = str(path_to_use)
    
    return SettingsConfigDict(**config_dict)

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Build model config with env_file if found (using function for dynamic building)
    model_config = _build_model_config()
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_model: str = Field(default="gpt-4", description="OpenAI model to use")
    
    # Chroma Database Configuration
    chroma_host: str = Field(default="localhost", description="Chroma host")
    chroma_port: int = Field(default=8000, description="Chroma port")
    chroma_collection_name: str = Field(
        default="itops_instructions",
        description="Chroma collection name"
    )
    chroma_persist_dir: str = Field(
        default="./data/chroma_db",
        description="Chroma persistence directory"
    )
    
    # Agent Framework Selection
    agent_framework: Literal["langchain", "langgraph", "crewai", "autogen"] = Field(
        default="langchain",
        description="Agent framework to use"
    )
    
    # AWS Configuration (optional)
    aws_access_key_id: Optional[str] = Field(
        default=None,
        description="AWS access key ID"
    )
    aws_secret_access_key: Optional[str] = Field(
        default=None,
        description="AWS secret access key"
    )
    aws_region: str = Field(default="us-east-1", description="AWS region")
    aws_profile: Optional[str] = Field(default=None, description="AWS profile")
    
    # System Execution Configuration
    execution_environment: Literal["windows", "linux", "both"] = Field(
        default="windows",
        description="Execution environment"
    )
    windows_domain: Optional[str] = Field(
        default=None,
        description="Windows domain"
    )
    windows_username: Optional[str] = Field(
        default=None,
        description="Windows username"
    )
    
    # Logging Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Log level"
    )
    log_file: str = Field(
        default="./logs/itops_agent.log",
        description="Log file path"
    )
    log_format: Literal["json", "text"] = Field(
        default="json",
        description="Log format"
    )
    
    # Application Configuration
    app_host: str = Field(default="0.0.0.0", description="Application host")
    app_port: int = Field(default=7860, description="Application port")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Security
    allowed_commands: Literal["all", "restricted"] = Field(
        default="all",
        description="Command execution policy"
    )


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get or create settings instance.
    
    Returns:
        Settings instance
        
    Raises:
        ValueError: If required settings are missing (like OPENAI_API_KEY)
    """
    global _settings
    if _settings is None:
        try:
            _settings = Settings()
        except Exception as e:
            # Provide helpful error message for missing required keys
            project_root = find_project_root()
            env_file = project_root / ".env"
            
            error_msg = f"Failed to load settings: {str(e)}\n\n"
            error_msg += "Please ensure:\n"
            error_msg += f"1. A .env file exists in the project root: {env_file}\n"
            error_msg += "2. The .env file contains required keys (e.g., OPENAI_API_KEY)\n"
            error_msg += "3. See .env.example for a template of required keys\n"
            
            if not env_file.exists():
                error_msg += f"\nNote: .env file not found at {env_file}\n"
            
            raise ValueError(error_msg) from e
    
    return _settings


def reload_settings() -> Settings:
    """
    Reload settings from environment and .env file.
    
    This function:
    1. Reloads the .env file (if it exists)
    2. Updates the global _env_file_path
    3. Updates the Settings class model_config to use the new env file path
    4. Creates a new Settings instance with the updated configuration
    
    Returns:
        New Settings instance
    """
    global _settings, _env_file_path
    
    # Reload .env file and update global path
    _env_file_path = load_env_file()
    
    # Update the class's model_config to reflect the new env file path
    Settings.model_config = _build_model_config(_env_file_path)
    
    # Create new instance with updated config
    _settings = Settings()
    return _settings
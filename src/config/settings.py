"""
Configuration management using Pydantic
"""
import os
from typing import Optional, Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
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
    """Get or create settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment"""
    global _settings
    _settings = Settings()
    return _settings


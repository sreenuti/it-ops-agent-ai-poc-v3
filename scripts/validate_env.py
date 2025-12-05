"""
Script to validate .env file configuration
"""
import sys
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import find_project_root, load_env_file
from src.config.settings import Settings
import os


def validate_env_file():
    """Validate .env file configuration"""
    print("IT Ops Agent - Environment Configuration Validator")
    print("=" * 60)
    print()
    
    # Find project root
    project_root = find_project_root()
    print(f"Project root: {project_root}")
    
    # Check for .env file
    env_file = project_root / ".env"
    print(f"Looking for .env file: {env_file}")
    
    if not env_file.exists():
        print("\n❌ ERROR: .env file not found!")
        print(f"   Expected location: {env_file}")
        print("\nPlease create a .env file with at minimum:")
        print("   OPENAI_API_KEY=your_openai_api_key_here")
        print("\nSee ENV_CONFIG.md for complete configuration guide.")
        return False
    
    print(f"✅ .env file found: {env_file}")
    print()
    
    # Load .env file
    loaded_path = load_env_file()
    if loaded_path:
        print(f"✅ .env file loaded from: {loaded_path}")
    else:
        print("⚠️  Warning: Could not load .env file")
    print()
    
    # Check required keys
    print("Validating configuration...")
    print("-" * 60)
    
    required_keys = {
        "OPENAI_API_KEY": "OpenAI API key (required)"
    }
    
    missing_keys = []
    for key, description in required_keys.items():
        value = os.getenv(key)
        if not value:
            print(f"❌ {key}: Missing - {description}")
            missing_keys.append(key)
        else:
            # Mask sensitive values
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print(f"✅ {key}: Set ({masked_value})")
    
    print()
    
    # Check optional keys (informational)
    optional_keys = [
        "OPENAI_MODEL",
        "CHROMA_HOST",
        "CHROMA_PORT",
        "AGENT_FRAMEWORK",
        "LOG_LEVEL",
        "APP_PORT"
    ]
    
    print("Optional configuration:")
    print("-" * 60)
    for key in optional_keys:
        value = os.getenv(key)
        if value:
            print(f"✓ {key}: {value}")
        else:
            default_value = get_default_value(key)
            print(f"○ {key}: Not set (default: {default_value})")
    
    print()
    
    # Try to load settings
    print("Testing settings loading...")
    print("-" * 60)
    
    if missing_keys:
        print("❌ Cannot load settings - missing required keys:")
        for key in missing_keys:
            print(f"   - {key}")
        print("\nPlease add the missing keys to your .env file.")
        return False
    
    try:
        settings = Settings()
        print("✅ Settings loaded successfully!")
        print()
        print("Current configuration:")
        print("-" * 60)
        print(f"OpenAI Model: {settings.openai_model}")
        print(f"Chroma Host: {settings.chroma_host}")
        print(f"Chroma Port: {settings.chroma_port}")
        print(f"Agent Framework: {settings.agent_framework}")
        print(f"Log Level: {settings.log_level}")
        print(f"App Port: {settings.app_port}")
        print()
        print("✅ All validation checks passed!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to load settings: {str(e)}")
        print("\nPlease check your .env file format and values.")
        print("See ENV_CONFIG.md for configuration guide.")
        return False


def get_default_value(key: str) -> str:
    """Get default value for a configuration key"""
    defaults = {
        "OPENAI_MODEL": "gpt-4",
        "CHROMA_HOST": "localhost",
        "CHROMA_PORT": "8000",
        "AGENT_FRAMEWORK": "langchain",
        "LOG_LEVEL": "INFO",
        "APP_PORT": "7860"
    }
    return defaults.get(key, "see documentation")


if __name__ == "__main__":
    success = validate_env_file()
    sys.exit(0 if success else 1)


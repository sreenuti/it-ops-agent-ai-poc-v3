# Environment Configuration Guide

This guide explains how to configure the IT Ops Agent System using environment variables via a `.env` file.

## Quick Start

1. Create a `.env` file in the project root directory
2. Add your configuration keys (see template below)
3. The system will automatically load the `.env` file on startup

## Required Configuration

### OPENAI_API_KEY (Required)
Your OpenAI API key. Get one from [OpenAI Platform](https://platform.openai.com/api-keys).

```env
OPENAI_API_KEY=sk-your-api-key-here
```

## Optional Configuration

### .env File Template

Copy this template to create your `.env` file:

```env
# ============================================
# REQUIRED CONFIGURATION
# ============================================

# OpenAI API Key (Required)
OPENAI_API_KEY=your_openai_api_key_here

# ============================================
# OPTIONAL CONFIGURATION
# ============================================

# OpenAI Model Configuration
OPENAI_MODEL=gpt-4

# Chroma Database Configuration
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_COLLECTION_NAME=itops_instructions
CHROMA_PERSIST_DIR=./data/chroma_db

# Agent Framework Selection
AGENT_FRAMEWORK=langchain

# AWS Configuration (optional)
# AWS_ACCESS_KEY_ID=your_aws_access_key_id
# AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=us-east-1

# System Execution Configuration
EXECUTION_ENVIRONMENT=windows

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=./logs/itops_agent.log
LOG_FORMAT=json

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=7860
DEBUG=false

# Security Configuration
ALLOWED_COMMANDS=all
```

## All Available Configuration Keys

### OpenAI Configuration

| Key | Required | Default | Description |
|-----|----------|---------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | - | Your OpenAI API key |
| `OPENAI_MODEL` | No | `gpt-4` | Model to use (e.g., gpt-4, gpt-3.5-turbo) |

### Chroma Database Configuration

| Key | Required | Default | Description |
|-----|----------|---------|-------------|
| `CHROMA_HOST` | No | `localhost` | Chroma database host |
| `CHROMA_PORT` | No | `8000` | Chroma database port |
| `CHROMA_COLLECTION_NAME` | No | `itops_instructions` | Collection name |
| `CHROMA_PERSIST_DIR` | No | `./data/chroma_db` | Local persistence directory |

### Agent Framework Configuration

| Key | Required | Default | Description |
|-----|----------|---------|-------------|
| `AGENT_FRAMEWORK` | No | `langchain` | Framework to use (langchain, langgraph, crewai, autogen) |

### AWS Configuration (Optional)

| Key | Required | Default | Description |
|-----|----------|---------|-------------|
| `AWS_ACCESS_KEY_ID` | No | - | AWS access key ID |
| `AWS_SECRET_ACCESS_KEY` | No | - | AWS secret access key |
| `AWS_REGION` | No | `us-east-1` | AWS region |
| `AWS_PROFILE` | No | - | AWS profile name |

### System Execution Configuration

| Key | Required | Default | Description |
|-----|----------|---------|-------------|
| `EXECUTION_ENVIRONMENT` | No | `windows` | Execution environment (windows, linux, both) |
| `WINDOWS_DOMAIN` | No | - | Windows domain |
| `WINDOWS_USERNAME` | No | - | Windows username |

### Logging Configuration

| Key | Required | Default | Description |
|-----|----------|---------|-------------|
| `LOG_LEVEL` | No | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FILE` | No | `./logs/itops_agent.log` | Log file path |
| `LOG_FORMAT` | No | `json` | Log format (json, text) |

### Application Configuration

| Key | Required | Default | Description |
|-----|----------|---------|-------------|
| `APP_HOST` | No | `0.0.0.0` | Application host |
| `APP_PORT` | No | `7860` | Application port |
| `DEBUG` | No | `false` | Debug mode (true, false) |

### Security Configuration

| Key | Required | Default | Description |
|-----|----------|---------|-------------|
| `ALLOWED_COMMANDS` | No | `all` | Command execution policy (all, restricted) |

## Environment Variable Naming

- Environment variables use **UPPERCASE** with **UNDERSCORES**
- The `.env` file automatically converts these to the appropriate settings
- Example: `OPENAI_API_KEY` in `.env` maps to `openai_api_key` in settings

## File Location

The `.env` file should be placed in the **project root directory**:

```
ITOps PoC v3/
├── .env              ← Your .env file goes here
├── src/
├── tests/
├── requirements.txt
└── README.md
```

## Loading Behavior

1. The system automatically finds the project root directory
2. Looks for `.env` file in the project root
3. Falls back to current directory if not found in root
4. Environment variables take precedence over `.env` file values
5. Settings are loaded when the application starts

## Security Best Practices

1. ✅ **Never commit `.env` file to version control** (already in `.gitignore`)
2. ✅ **Use environment variables in production** instead of `.env` file
3. ✅ **Rotate API keys regularly**
4. ✅ **Use secrets management** (AWS Secrets Manager, Azure Key Vault, etc.) in production
5. ✅ **Restrict file permissions** on `.env` file (e.g., `chmod 600 .env` on Linux/Mac)

## Validation

Use the validation script to check your `.env` file:

```bash
python scripts/validate_env.py
```

## Troubleshooting

### .env file not found

**Error:** `Failed to load settings: ... .env file not found at ...`

**Solution:**
1. Ensure `.env` file exists in project root
2. Check file name is exactly `.env` (not `.env.txt` or `env`)
3. Verify you're running from the project directory

### Missing required keys

**Error:** `Failed to load settings: ... OPENAI_API_KEY is required`

**Solution:**
1. Add `OPENAI_API_KEY=your_key_here` to your `.env` file
2. Ensure there are no spaces around the `=` sign
3. Don't use quotes unless the value contains spaces

### Settings not loading

**Solution:**
1. Check `.env` file syntax (no spaces around `=`)
2. Verify file encoding is UTF-8
3. Ensure no hidden characters
4. Try reloading: Call `reload_settings()` in code

## Examples

### Minimal Configuration

```env
OPENAI_API_KEY=sk-1234567890abcdef
```

### Full Configuration

```env
# Required
OPENAI_API_KEY=sk-1234567890abcdef

# OpenAI
OPENAI_MODEL=gpt-4

# Chroma
CHROMA_HOST=localhost
CHROMA_PORT=8000

# Agent
AGENT_FRAMEWORK=langchain

# Logging
LOG_LEVEL=DEBUG
LOG_FORMAT=json

# Application
APP_PORT=7860
DEBUG=true
```

### Docker Configuration

For Docker, some values are set in `docker-compose.yml`:

```env
OPENAI_API_KEY=sk-1234567890abcdef
OPENAI_MODEL=gpt-4
AGENT_FRAMEWORK=langchain
LOG_LEVEL=INFO
```

Note: In Docker Compose, `CHROMA_HOST=chroma` (service name), not `localhost`.

### Production Configuration

For production, use environment variables or secrets management:

```bash
export OPENAI_API_KEY=sk-1234567890abcdef
export OPENAI_MODEL=gpt-4
export LOG_LEVEL=INFO
```

Or use Kubernetes secrets (see `k8s/secret.yaml.template`).

## Additional Resources

- [RUN_GUIDE.md](RUN_GUIDE.md) - Detailed run instructions
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [src/config/settings.py](src/config/settings.py) - Settings source code


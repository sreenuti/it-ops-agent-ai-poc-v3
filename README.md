# IT Ops Agent System

A scalable and flexible IT operations agent system capable of handling tasks like password resets, VPN troubleshooting, and other common IT ops tasks by retrieving instructions from a vector database and executing scripts. The system is framework-agnostic, supporting multiple agent frameworks (LangChain, LangGraph, Crew AI, AutoGen) and can be deployed using Docker or Kubernetes.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
- [Development](#development)
- [Deployment](#deployment)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Framework-Agnostic**: Supports LangChain, LangGraph, Crew AI, and AutoGen through adapter pattern
- **Vector Database Integration**: Uses Chroma for semantic search of IT ops instructions
- **Multi-Platform Execution**: Supports AWS, Windows, and Linux systems
- **Dynamic Script Generation**: Generates and executes scripts based on retrieved instructions
- **Task Decomposition**: Intelligently breaks down complex tasks into subtasks
- **Conversation Management**: Maintains context across multi-turn conversations
- **Simple Chat Interface**: Gradio-based UI for easy interaction
- **Containerized**: Docker and Kubernetes deployment ready
- **Production-Ready**: Comprehensive error handling, logging, and monitoring

## Architecture

The system follows a modular, layered architecture:

```
Presentation Layer (Gradio UI)
    ↓
API Layer (Conversation & Instruction Management)
    ↓
Agent Layer (Framework Adapters + Task Decomposition)
    ↓
Vector DB (Chroma) + LLM Service (OpenAI)
    ↓
Execution Layer (AWS, Windows, Linux Executors)
```

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Prerequisites

### Required

- **Python 3.10 or higher**
- **OpenAI API key** - Get one from [OpenAI](https://platform.openai.com/api-keys)
- **Chroma DB** - Will run automatically via Docker Compose or Kubernetes

### Optional (depending on use case)

- **AWS CLI** - For AWS operations (install via [AWS CLI guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html))
- **Windows PowerShell** - For Windows system operations
- **Linux/Bash** - For Linux system operations
- **Docker & Docker Compose** - For containerized deployment
- **Kubernetes cluster** - For Kubernetes deployment (minikube/kind for local testing)

## Quick Start

> **📖 Need more details?** 
> - **Quick Setup:** See [QUICKSTART.md](QUICKSTART.md) for a 5-minute setup guide
> - **Detailed Guide:** See [RUN_GUIDE.md](RUN_GUIDE.md) for comprehensive step-by-step instructions

### 1. Clone and Setup

```bash
# Navigate to project directory (if already cloned)
cd "ITOps PoC v3"

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the project root:

```bash
# Copy and edit environment template
# Create .env file with at minimum:
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Configure Chroma (defaults work for local development)
CHROMA_HOST=localhost
CHROMA_PORT=8000

# Optional: Choose agent framework (default: langchain)
AGENT_FRAMEWORK=langchain  # Options: langchain, langgraph, crewai, autogen

# Optional: AWS configuration (if using AWS operations)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
```

**Note**: For security, never commit the `.env` file. Use environment variables or Kubernetes secrets in production.

### 3. Start Chroma DB (Local Development)

Using Docker Compose:

```bash
cd docker
docker-compose up -d chroma
```

Or start Chroma manually:

```bash
docker run -d -p 8000:8000 -v chroma_data:/chroma/chroma \
  -e IS_PERSISTENT=TRUE \
  -e PERSIST_DIRECTORY=/chroma/chroma \
  chromadb/chroma:latest
```

### 4. Load Sample Instructions

```bash
# Load sample instructions into the vector database
python scripts/load_instructions.py
```

This will load all instruction files from `data/instructions/` into Chroma.

### 5. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_config.py -v
```

### 6. Start Application

```bash
# Run Gradio interface
python -m src.api.gradio_app
```

The application will be available at `http://localhost:7860`

## Configuration

### Environment Variables

The system uses environment variables for configuration. See `src/config/settings.py` for all available settings.

#### Required Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)

#### Optional Variables

**Chroma Database:**
- `CHROMA_HOST`: Chroma host (default: `localhost`)
- `CHROMA_PORT`: Chroma port (default: `8000`)
- `CHROMA_COLLECTION_NAME`: Collection name (default: `itops_instructions`)
- `CHROMA_PERSIST_DIR`: Persistence directory (default: `./data/chroma_db`)

**Agent Framework:**
- `AGENT_FRAMEWORK`: Framework to use - `langchain`, `langgraph`, `crewai`, or `autogen` (default: `langchain`)

**OpenAI:**
- `OPENAI_MODEL`: Model to use (default: `gpt-4`)

**AWS (if using AWS operations):**
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_REGION`: AWS region (default: `us-east-1`)
- `AWS_PROFILE`: AWS profile name

**System Execution:**
- `EXECUTION_ENVIRONMENT`: `windows`, `linux`, or `both` (default: `windows`)
- `WINDOWS_DOMAIN`: Windows domain (optional)
- `WINDOWS_USERNAME`: Windows username (optional)

**Logging:**
- `LOG_LEVEL`: `DEBUG`, `INFO`, `WARNING`, or `ERROR` (default: `INFO`)
- `LOG_FILE`: Log file path (default: `./logs/itops_agent.log`)
- `LOG_FORMAT`: `json` or `text` (default: `json`)

**Application:**
- `APP_HOST`: Application host (default: `0.0.0.0`)
- `APP_PORT`: Application port (default: `7860`)
- `DEBUG`: Enable debug mode - `true` or `false` (default: `false`)

**Security:**
- `ALLOWED_COMMANDS`: `all` or `restricted` (default: `all`)

## Usage

### Using the Gradio Interface

1. Start the application (see Quick Start)
2. Open `http://localhost:7860` in your browser
3. Type your IT ops query, for example:
   - "Reset password for user john.doe in AWS IAM"
   - "Troubleshoot VPN connection issues"
   - "Unlock account for user jane.smith"
4. The agent will:
   - Retrieve relevant instructions from the vector database
   - Generate appropriate commands/scripts
   - Execute them (or show what would be executed in dry-run mode)
   - Display results

### Using Dry Run Mode

Enable "Dry Run Mode" in the Gradio interface to see what commands would be executed without actually running them. This is useful for:
- Testing the agent's understanding
- Reviewing commands before execution
- Learning what the agent would do for a task

### Programmatic Usage

```python
from src.agents.agent_factory import AgentFactory

# Create an agent instance
agent = AgentFactory.create_agent()

# Process a query
result = agent.process_query(
    "Reset password for user john.doe",
    chat_history=[],
    dry_run=True  # Set to False to actually execute
)

print(result["response"])
```

### Supported Task Types

The system supports 23+ IT ops task types:

**Access Management:**
- Password resets (AWS IAM, Active Directory, local accounts)
- Account unlock procedures
- Jira access requests
- Shared drive access

**Application Issues:**
- Outlook synchronization
- Teams authentication
- Zoom audio problems
- Application crashes
- Software installation requests

**Hardware Issues:**
- Laptop overheating
- Monitor detection
- Printer problems
- Windows audio issues

**Network Issues:**
- VPN troubleshooting
- WiFi connectivity
- Network diagnostics

**System Issues:**
- Performance optimization
- Blue screen errors
- Excel freezing
- OneDrive sync issues

**Email Issues:**
- Email delivery failures

See `data/instructions/` for available instruction files. You can add more by creating new JSON files following the same format.

## Development

### Project Structure

```
itops-agent/
├── src/
│   ├── agents/              # Agent implementations
│   │   ├── adapters/       # Framework adapters
│   │   ├── agent_factory.py
│   │   └── base_agent.py
│   ├── vector_db/          # Chroma database integration
│   ├── script_executor/    # Command execution
│   │   ├── aws_executor.py
│   │   └── system_executor.py
│   ├── task_decomposer/    # Task decomposition
│   ├── api/                # Gradio API
│   │   ├── gradio_app.py
│   │   ├── conversation_manager.py
│   │   └── instruction_manager.py
│   ├── config/             # Configuration management
│   └── utils/              # Utilities (logging, error handling)
├── tests/                  # Test suite
├── data/                   # Data and instructions
│   └── instructions/       # Instruction JSON files
├── docker/                 # Docker configuration
├── k8s/                    # Kubernetes manifests
├── scripts/                # Utility scripts
└── requirements.txt        # Python dependencies
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_config.py

# Run tests matching a pattern
pytest -k "test_config"

# Run with parallel execution
pytest -n auto
```

### Adding New Instructions

1. Create a JSON file in `data/instructions/` following this format:

```json
{
  "task_type": "your_task_type",
  "instruction_text": "Detailed step-by-step instructions...",
  "metadata": {
    "platform": "aws,windows,linux",
    "complexity": "low|medium|high",
    "category": "access_management|application_issues|..."
  }
}
```

2. Load the instruction:

```bash
python scripts/load_instructions.py
```

Or programmatically:

```python
from src.vector_db.instruction_store import InstructionStore
import json

store = InstructionStore()
with open('data/instructions/your_task.json', 'r') as f:
    instruction = json.load(f)
    store.add_instruction(
        task_type=instruction['task_type'],
        instruction_text=instruction['instruction_text'],
        metadata=instruction.get('metadata', {})
    )
```

### Adding a New Agent Framework

1. Create a new adapter in `src/agents/adapters/` that implements `BaseAgent`
2. Register it in `AgentFactory`
3. Add tests in `tests/test_adapters.py`

See existing adapters for examples.

### Code Quality

```bash
# Lint code (if configured)
pylint src/

# Format code (if using black)
black src/ tests/
```

## Deployment

### Docker Deployment

See `docker/` directory for Docker configuration.

```bash
# Build and start with Docker Compose
cd docker
docker-compose up -d

# Check logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### Kubernetes Deployment

See `k8s/README.md` for detailed Kubernetes deployment instructions.

Quick start:

```bash
# Apply all manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get all -n itops-agent

# Access via port-forward
kubectl port-forward svc/itops-agent-service 7860:80 -n itops-agent
```

For full deployment guide, see [k8s/README.md](k8s/README.md).

## Documentation

### Getting Started
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute quick start guide
- **[RUN_GUIDE.md](RUN_GUIDE.md)** - Comprehensive step-by-step run instructions
- **[TESTING.md](TESTING.md)** - Complete testing guide and procedures

### Reference Documentation
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed system architecture
- **[USER_GUIDE.md](USER_GUIDE.md)** - User guide with examples
- **[API_REFERENCE.md](API_REFERENCE.md)** - API reference documentation
- **[k8s/README.md](k8s/README.md)** - Kubernetes deployment guide
- **[data/instructions/README.md](data/instructions/README.md)** - Instruction file format and usage
- **[GITHUB_SETUP.md](GITHUB_SETUP.md)** - GitHub repository setup guide

### API Reference

The system exposes a Gradio interface with the following capabilities:

- **Chat Interface**: Interactive conversation with the agent
- **Health Check**: `/health` endpoint for container orchestration
- **Instruction Management**: Manage instructions via Gradio UI or programmatically

For detailed API documentation, see the source code docstrings or generate API docs using tools like Sphinx.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -am 'Add some feature'`)
7. Push to the branch (`git push origin feature/your-feature`)
8. Create a Pull Request

### Development Guidelines

- Write tests for all new features
- Follow existing code style
- Update documentation as needed
- Ensure backward compatibility when possible

## License

[Add your license here]

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Note**: This system executes commands on your systems. Always test in a safe environment first and use dry-run mode when unsure. The system is designed for IT operations teams with appropriate access and permissions.

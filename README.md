# IT Ops Agent System

A scalable and flexible IT operations agent system capable of handling tasks like password resets, VPN troubleshooting, and other common IT ops tasks by retrieving instructions from a vector database and executing scripts.

## Features

- **Framework-Agnostic**: Supports LangChain, LangGraph, Crew AI, and AutoGen
- **Vector Database Integration**: Uses Chroma for semantic search of IT ops instructions
- **Multi-Platform Execution**: Supports AWS, Windows, and Linux systems
- **Dynamic Script Generation**: Generates and executes scripts based on retrieved instructions
- **Simple Chat Interface**: Gradio-based UI for easy interaction

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## Prerequisites

- Python 3.10 or higher
- OpenAI API key
- AWS CLI (if using AWS executors)
- Docker and Kubernetes (for deployment)

## Quick Start

### 1. Clone and Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# At minimum, set OPENAI_API_KEY
```

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

### 4. Start Application

```bash
# Run Gradio interface
python -m src.api.gradio_app
```

## Project Structure

```
itops-agent/
├── src/
│   ├── agents/           # Agent implementations
│   ├── vector_db/        # Chroma database integration
│   ├── script_executor/  # Command execution
│   ├── task_decomposer/   # Task decomposition
│   ├── api/              # Gradio API
│   ├── config/           # Configuration management
│   └── utils/            # Utilities
├── tests/                # Test suite
├── data/                 # Data and instructions
├── docker/               # Docker configuration
├── k8s/                  # Kubernetes manifests
└── requirements.txt      # Python dependencies
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_config.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=term-missing
```

### Adding New Instructions

Instructions are stored in the Chroma vector database. You can add new instructions programmatically or through the instruction management API.

## Deployment

See deployment documentation in `k8s/` directory for Kubernetes deployment instructions.

## License

[Add your license here]

## Contributing

[Add contributing guidelines here]


# Testing Guide - IT Ops Agent System

This guide provides comprehensive testing steps for the IT Ops Agent System, covering unit tests, integration tests, end-to-end tests, and deployment validation.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start Testing](#quick-start-testing)
- [Test Categories](#test-categories)
- [Unit Tests](#unit-tests)
- [Integration Tests](#integration-tests)
- [End-to-End Tests](#end-to-end-tests)
- [Manual Testing](#manual-testing)
- [Docker Testing](#docker-testing)
- [Kubernetes Testing](#kubernetes-testing)
- [Performance Testing](#performance-testing)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before running tests, ensure you have:

### Required Software

1. **Python 3.10+** installed and accessible in PATH
2. **pip** package manager
3. **Virtual environment** (recommended)

### Optional Dependencies

- **Docker** - For containerized testing
- **Docker Compose** - For multi-container testing
- **kubectl** - For Kubernetes deployment testing
- **Kubernetes cluster** - minikube, kind, or cloud cluster

### Environment Setup

1. **Create and activate virtual environment:**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**

Create a `.env` file in the project root (or set environment variables):

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (defaults provided)
CHROMA_HOST=localhost
CHROMA_PORT=8000
AGENT_FRAMEWORK=langchain
LOG_LEVEL=INFO
```

**Note**: For testing, most tests use mocks and don't require real API keys. However, integration tests may need valid credentials.

---

## Quick Start Testing

### 1. Run All Tests

```bash
# Run entire test suite
pytest

# Run with verbose output
pytest -v

# Run with detailed output and coverage
pytest -v --cov=src --cov-report=term-missing
```

### 2. Check Test Discovery

```bash
# Verify pytest can discover all tests
pytest --collect-only

# Count tests
pytest --collect-only -q
```

**Expected**: Should discover 20+ test files with 100+ test cases

### 3. Run Tests by Category

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only end-to-end tests
pytest -m e2e

# Skip slow tests
pytest -m "not slow"
```

---

## Test Categories

The test suite is organized into the following categories:

### Unit Tests

- `test_config.py` - Configuration management
- `test_vector_db.py` - Vector database operations
- `test_executors.py` - Script executors (AWS, System)
- `test_script_generator.py` - Script generation logic
- `test_task_decomposer.py` - Task decomposition
- `test_base_agent.py` - Base agent interface
- `test_adapters.py` - Framework adapters
- `test_agent_factory.py` - Agent factory
- `test_error_handling.py` - Error handling
- `test_logging.py` - Logging system
- `test_project_setup.py` - Project structure

### Integration Tests

- `test_integration.py` - Full system integration
- `test_conversation_manager.py` - Conversation management
- `test_instruction_manager.py` - Instruction CRUD operations
- `test_framework_switching.py` - Framework switching
- `test_gradio_app.py` - Gradio UI integration

### End-to-End Tests

- `test_sample_data.py` - Sample instruction data validation
- `test_k8s_deployment.py` - Kubernetes deployment (requires cluster)
- `test_docker.py` - Docker container testing

### Manifest/Validation Tests

- `test_k8s_manifests.py` - Kubernetes manifest validation
- `test_langchain_adapter.py` - LangChain adapter specific tests
- `test_langchain_agent.py` - LangChain agent specific tests

---

## Unit Tests

### Configuration Tests

```bash
# Test configuration loading and validation
pytest tests/test_config.py -v

# Test specific configuration scenarios
pytest tests/test_config.py::test_settings_load_from_env -v
pytest tests/test_config.py::test_settings_validation -v
```

**What it tests:**
- Environment variable loading
- Configuration validation
- Default value handling
- Type checking

### Vector Database Tests

```bash
# Test Chroma integration
pytest tests/test_vector_db.py -v

# Test specific operations
pytest tests/test_vector_db.py::test_add_instruction -v
pytest tests/test_vector_db.py::test_retrieve_instructions -v
```

**What it tests:**
- Instruction storage (CRUD)
- Semantic search functionality
- Metadata handling
- Collection management

**Note**: These tests use mocked Chroma client by default.

### Executor Tests

```bash
# Test all executors
pytest tests/test_executors.py -v

# Test specific executor
pytest tests/test_executors.py -k "aws" -v
pytest tests/test_executors.py -k "system" -v
```

**What it tests:**
- AWS CLI command execution
- PowerShell/Bash command execution
- Error handling
- Output parsing
- Command validation

**Warning**: Executor tests may use dry-run mode. Real execution tests require proper credentials and permissions.

### Agent Framework Tests

```bash
# Test base agent interface
pytest tests/test_base_agent.py -v

# Test framework adapters
pytest tests/test_adapters.py -v

# Test agent factory
pytest tests/test_agent_factory.py -v

# Test LangChain adapter specifically
pytest tests/test_langchain_adapter.py -v
```

**What it tests:**
- Interface compliance
- Framework-specific implementations
- Agent creation and initialization
- Framework switching capability

### Task Decomposition Tests

```bash
# Test task decomposition
pytest tests/test_task_decomposer.py -v
```

**What it tests:**
- Complex task breakdown
- Subtask generation
- Instruction retrieval per subtask
- Execution plan generation

---

## Integration Tests

### Full System Integration

```bash
# Run all integration tests
pytest tests/test_integration.py -v

# Test specific scenarios
pytest tests/test_integration.py::test_password_reset_flow -v
pytest tests/test_integration.py::test_vpn_troubleshooting_flow -v
```

**What it tests:**
- End-to-end query processing
- Instruction retrieval → Command generation → Execution flow
- Multiple task types
- Error handling in full pipeline

**Requirements:**
- Mocked OpenAI API (uses fixtures)
- Mocked Chroma DB (uses fixtures)
- No real API calls needed

### Conversation Management

```bash
# Test conversation handling
pytest tests/test_conversation_manager.py -v
```

**What it tests:**
- Conversation history storage
- Context-aware queries
- Session management
- Multi-turn conversations

### Instruction Management

```bash
# Test instruction CRUD operations
pytest tests/test_instruction_manager.py -v
```

**What it tests:**
- Adding instructions
- Updating instructions
- Deleting instructions
- Bulk import
- Validation

### Framework Switching

```bash
# Test switching between frameworks
pytest tests/test_framework_switching.py -v
```

**What it tests:**
- Runtime framework switching
- Consistent behavior across frameworks
- Configuration-driven framework selection

---

## End-to-End Tests

### Sample Data Validation

```bash
# Validate all sample instructions
pytest tests/test_sample_data.py -v

# Test instruction loading
pytest tests/test_sample_data.py::test_load_all_instructions -v
```

**What it tests:**
- Instruction file format
- Content validation
- Loading into vector DB
- Coverage of all task types

**Requirements:**
- Sample instruction files in `data/instructions/`
- Chroma DB running (or mocked)

### Application Startup Test

```bash
# Test Gradio app initialization
pytest tests/test_gradio_app.py -v
```

**What it tests:**
- Application startup
- UI initialization
- Health check endpoints
- Error handling

---

## Manual Testing

### 1. Set Up Test Environment

```bash
# Start Chroma DB (if not using mocks)
cd docker
docker-compose up -d chroma

# Wait for Chroma to be ready
# Check logs: docker-compose logs chroma
```

### 2. Load Sample Instructions

```bash
# Load all instruction files
python scripts/load_instructions.py

# Verify loading
python -c "from src.vector_db.instruction_store import InstructionStore; store = InstructionStore(); print(f'Instructions loaded: {len(store.list_instructions())}')"
```

**Expected**: Should load 23+ instruction files

### 3. Start Application

```bash
# Start Gradio interface
python -m src.api.gradio_app
```

**Expected**: 
- Application starts without errors
- Accessible at `http://localhost:7860`
- No console errors

### 4. Test Health Endpoints

Open a new terminal and test endpoints:

```bash
# Health check
curl http://localhost:7860/health

# Expected: {"status": "healthy"}

# Metrics (Prometheus format)
curl http://localhost:7860/metrics

# Metrics (JSON format)
curl http://localhost:7860/metrics/json
```

### 5. Test Chat Interface

1. Open `http://localhost:7860` in browser
2. Test queries:

**Password Reset:**
```
Reset password for user john.doe in AWS IAM
```

**VPN Troubleshooting:**
```
Troubleshoot VPN connection issues
```

**Account Unlock:**
```
Unlock account for user jane.smith
```

3. Enable **Dry Run Mode** to see commands without execution
4. Verify:
   - Instructions are retrieved
   - Commands are generated
   - Results are displayed
   - Conversation history is maintained

### 6. Test Instruction Management

1. In Gradio UI, use instruction management features (if available)
2. Or use programmatic interface:

```python
from src.api.instruction_manager import InstructionManager

manager = InstructionManager()

# Add instruction
manager.add_instruction(
    task_type="test_task",
    instruction_text="Test instructions...",
    metadata={"category": "test"}
)

# List instructions
instructions = manager.list_instructions()
print(f"Total instructions: {len(instructions)}")

# Search instructions
results = manager.search_instructions("password reset")
print(f"Found {len(results)} matching instructions")
```

---

## Docker Testing

### 1. Build Docker Image

```bash
cd docker

# Build application image
docker build -t itops-agent:test -f Dockerfile ..

# Verify image
docker images | grep itops-agent
```

**Expected**: Image builds successfully without errors

### 2. Test Docker Compose

```bash
cd docker

# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# Check logs
docker-compose logs app
docker-compose logs chroma

# Test health endpoint
curl http://localhost:7860/health
```

**Expected**: 
- All services start successfully
- App connects to Chroma
- Health check responds

### 3. Test Container Health

```bash
# Check container health
docker-compose ps

# Test container restart
docker-compose restart app

# Test container logs
docker-compose logs -f app
```

### 4. Run Tests in Container

```bash
# Run tests inside container
docker-compose exec app pytest

# Run specific test suite
docker-compose exec app pytest tests/test_config.py -v
```

### 5. Test Volume Persistence

```bash
# Stop containers
docker-compose down

# Start again
docker-compose up -d

# Verify data persists
docker-compose exec app python -c "from src.vector_db.instruction_store import InstructionStore; store = InstructionStore(); print(len(store.list_instructions()))"
```

### 6. Clean Up

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (optional)
docker-compose down -v

# Remove images (optional)
docker rmi itops-agent:test
```

---

## Kubernetes Testing

### Prerequisites

- Kubernetes cluster (minikube, kind, or cloud)
- kubectl configured
- Access to cluster

### 1. Validate Manifests

```bash
# Test YAML syntax
pytest tests/test_k8s_manifests.py -v

# Dry-run apply (validates without applying)
kubectl apply --dry-run=client -f k8s/
```

**Expected**: All manifests are valid YAML

### 2. Create Namespace

```bash
# Apply namespace
kubectl apply -f k8s/namespace.yaml

# Verify namespace
kubectl get namespace itops-agent
```

### 3. Create Secrets

```bash
# Create secret from template
cp k8s/secret.yaml.template k8s/secret.yaml
# Edit secret.yaml with your values
kubectl apply -f k8s/secret.yaml
```

### 4. Deploy ConfigMap

```bash
# Apply ConfigMap
kubectl apply -f k8s/configmap.yaml

# Verify
kubectl get configmap -n itops-agent
```

### 5. Deploy Persistent Volume

```bash
# Apply PVC
kubectl apply -f k8s/persistentvolumeclaim.yaml

# Verify
kubectl get pvc -n itops-agent
```

### 6. Deploy Chroma DB

```bash
# Deploy Chroma
kubectl apply -f k8s/chroma-deployment.yaml
kubectl apply -f k8s/chroma-service.yaml

# Wait for deployment
kubectl wait --for=condition=available --timeout=300s deployment/chroma -n itops-agent

# Check status
kubectl get pods -n itops-agent -l app=chroma
```

### 7. Deploy Application

```bash
# Deploy app
kubectl apply -f k8s/app-deployment.yaml
kubectl apply -f k8s/app-service.yaml

# Wait for deployment
kubectl wait --for=condition=available --timeout=300s deployment/itops-agent -n itops-agent

# Check status
kubectl get pods -n itops-agent -l app=itops-agent
```

### 8. Verify Deployment

```bash
# Check all resources
kubectl get all -n itops-agent

# Check pod logs
kubectl logs -n itops-agent -l app=itops-agent --tail=100

# Check service
kubectl get svc -n itops-agent
```

### 9. Access Application

```bash
# Port forward to access locally
kubectl port-forward svc/itops-agent-service 7860:80 -n itops-agent

# In another terminal, test access
curl http://localhost:7860/health
```

### 10. Run Deployment Tests

```bash
# Run K8s deployment tests (requires cluster access)
pytest tests/test_k8s_deployment.py -v

# Check if kubectl is available
kubectl version --client
```

### 11. Test Scaling (HPA)

```bash
# Apply HPA
kubectl apply -f k8s/hpa.yaml

# Check HPA status
kubectl get hpa -n itops-agent

# Generate load to test scaling (if metrics available)
```

### 12. Clean Up

```bash
# Delete all resources
kubectl delete -f k8s/

# Or delete namespace (removes everything)
kubectl delete namespace itops-agent
```

---

## Performance Testing

### 1. Test Query Response Time

```python
import time
from src.agents.agent_factory import AgentFactory

agent = AgentFactory.create_agent()

# Time a query
start = time.time()
result = agent.process_query(
    "Reset password for user test",
    chat_history=[],
    dry_run=True
)
end = time.time()

print(f"Query time: {end - start:.2f} seconds")
```

**Expected**: < 5 seconds for typical queries

### 2. Test Concurrent Queries

```python
import concurrent.futures
import time

def test_query(query):
    agent = AgentFactory.create_agent()
    start = time.time()
    result = agent.process_query(query, chat_history=[], dry_run=True)
    return time.time() - start

queries = [
    "Reset password for user1",
    "Reset password for user2",
    "Troubleshoot VPN",
    "Unlock account for user3"
]

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    times = list(executor.map(test_query, queries))

print(f"Average time: {sum(times)/len(times):.2f} seconds")
print(f"Max time: {max(times):.2f} seconds")
```

### 3. Test Database Performance

```python
from src.vector_db.instruction_store import InstructionStore
import time

store = InstructionStore()

# Test search performance
start = time.time()
results = store.search_instructions("password reset", top_k=5)
search_time = time.time() - start

print(f"Search time: {search_time:.4f} seconds")
print(f"Results found: {len(results)}")
```

### 4. Monitor Resource Usage

```bash
# Monitor CPU and memory (if running in Docker)
docker stats

# Monitor Kubernetes pods
kubectl top pods -n itops-agent
```

---

## Test Coverage

### Generate Coverage Report

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# View report
# Open htmlcov/index.html in browser

# Generate terminal report
pytest --cov=src --cov-report=term-missing

# Check coverage percentage
pytest --cov=src --cov-report=term --cov-fail-under=80
```

**Target**: > 80% code coverage

### Coverage by Module

```bash
# Coverage for specific module
pytest --cov=src.agents --cov-report=term-missing tests/test_adapters.py

# Coverage for all executors
pytest --cov=src.script_executor --cov-report=term-missing tests/test_executors.py
```

---

## Troubleshooting

### Common Issues

#### 1. Tests Failing Due to Missing Dependencies

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Check pytest installation
pytest --version
```

#### 2. Chroma Connection Errors

```bash
# Check if Chroma is running
curl http://localhost:8000/api/v1/heartbeat

# Start Chroma if needed
cd docker && docker-compose up -d chroma
```

#### 3. OpenAI API Errors

- Most tests use mocks and don't need real API keys
- Integration tests may require valid keys
- Check `.env` file or environment variables

#### 4. Import Errors

```bash
# Ensure you're in project root
pwd  # Should show project directory

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Reinstall in development mode
pip install -e .
```

#### 5. Docker Build Failures

```bash
# Check Dockerfile syntax
docker build --no-cache -t test -f docker/Dockerfile .

# Check for syntax errors
docker-compose config
```

#### 6. Kubernetes Connection Issues

```bash
# Check kubectl configuration
kubectl config current-context
kubectl cluster-info

# Test connection
kubectl get nodes
```

### Debug Mode

```bash
# Run tests with debug output
pytest -v -s

# Run specific test with detailed output
pytest tests/test_config.py::test_specific_function -v -s

# Use Python debugger
pytest --pdb tests/test_config.py
```

### View Test Output

```bash
# Show print statements
pytest -s

# Show local variables on failure
pytest -l

# Show full traceback
pytest --tb=long
```

---

## Test Execution Checklist

Use this checklist to ensure comprehensive testing:

### Pre-Testing Setup
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Environment variables configured (`.env` file or exports)
- [ ] Chroma DB running (for integration tests)
- [ ] Test data loaded (sample instructions)

### Unit Tests
- [ ] Configuration tests pass (`test_config.py`)
- [ ] Vector DB tests pass (`test_vector_db.py`)
- [ ] Executor tests pass (`test_executors.py`)
- [ ] Agent framework tests pass (`test_adapters.py`, `test_base_agent.py`)
- [ ] Script generator tests pass (`test_script_generator.py`)
- [ ] Task decomposer tests pass (`test_task_decomposer.py`)
- [ ] Error handling tests pass (`test_error_handling.py`)
- [ ] Logging tests pass (`test_logging.py`)

### Integration Tests
- [ ] Full integration tests pass (`test_integration.py`)
- [ ] Conversation management tests pass (`test_conversation_manager.py`)
- [ ] Instruction management tests pass (`test_instruction_manager.py`)
- [ ] Framework switching tests pass (`test_framework_switching.py`)
- [ ] Gradio app tests pass (`test_gradio_app.py`)

### End-to-End Tests
- [ ] Sample data validation passes (`test_sample_data.py`)
- [ ] Application starts successfully
- [ ] Health endpoints respond correctly
- [ ] Chat interface works in browser
- [ ] Dry-run mode functions correctly

### Docker Tests
- [ ] Docker image builds successfully
- [ ] Docker Compose starts all services
- [ ] Health checks pass in containers
- [ ] Volume persistence works
- [ ] Container logs are readable

### Kubernetes Tests (if applicable)
- [ ] Manifest validation passes
- [ ] Deployment succeeds
- [ ] Services are accessible
- [ ] Pods are healthy
- [ ] Scaling works (if HPA configured)

### Coverage
- [ ] Overall coverage > 80%
- [ ] Critical modules have high coverage
- [ ] Coverage report generated and reviewed

---

## Continuous Testing

### Run Tests on Code Changes

```bash
# Watch for file changes and run tests
pytest-watch  # Requires pytest-watch package

# Or use entr (Linux/Mac)
find . -name "*.py" | entr pytest
```

### Pre-commit Hooks

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
pytest --tb=short -q
```

### CI/CD Integration

Example GitHub Actions workflow (`.github/workflows/test.yml`):

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest --cov=src --cov-report=xml
```

---

## Additional Resources

- **Test Files**: All test files are in `tests/` directory
- **Test Configuration**: See `pytest.ini` for test settings
- **Test Fixtures**: Shared fixtures in `tests/conftest.py`
- **Validation Checklist**: See `VALIDATION_CHECKLIST.md` for comprehensive validation
- **Architecture**: See `ARCHITECTURE.md` for system design
- **User Guide**: See `USER_GUIDE.md` for usage examples

---

## Summary

This testing guide covers:

1. ✅ **Unit Tests** - Individual component testing
2. ✅ **Integration Tests** - Component interaction testing
3. ✅ **End-to-End Tests** - Full system testing
4. ✅ **Manual Testing** - Interactive testing via UI
5. ✅ **Docker Testing** - Containerized deployment testing
6. ✅ **Kubernetes Testing** - K8s deployment testing
7. ✅ **Performance Testing** - Performance and load testing
8. ✅ **Coverage Analysis** - Code coverage reporting

**Quick Start Command:**
```bash
pytest -v --cov=src --cov-report=html
```

**Expected Result**: All tests pass with > 80% code coverage.

---

**Last Updated**: See project commit history
**Test Framework**: pytest
**Python Version**: 3.10+
**Target Coverage**: 80%+


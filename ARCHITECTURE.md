# IT Ops Agent System - Architecture Documentation

## Overview

The IT Ops Agent System is a scalable, framework-agnostic agent system designed to handle IT operational tasks through intelligent instruction retrieval, task decomposition, and automated execution.

## System Architecture

### Core Principles

1. **Framework Agnostic**: Supports multiple agent frameworks (LangChain, LangGraph, Crew AI, AutoGen) through adapter pattern
2. **Instruction-Driven**: Uses vector database to store and retrieve IT ops procedures
3. **Multi-Platform Execution**: Supports AWS, Windows, and Linux systems through specialized executors
4. **Test-Driven**: Comprehensive testing at each layer
5. **Modular Design**: Components are independently testable and replaceable

## Architecture Layers

### 1. Presentation Layer

**Gradio Chat Interface**
- Simple, intuitive chat interface
- Real-time status updates
- Conversation history display
- Error message presentation

**Responsibilities:**
- User interaction
- Query input and result display
- Session management

### 2. API Layer

**Components:**
- `gradio_app.py`: Main API endpoint
- `conversation_manager.py`: Manages conversation state and context
- `instruction_manager.py`: CRUD operations for instructions

**Responsibilities:**
- Request routing
- Conversation state management
- Instruction management UI/API

### 3. Agent Layer

**Core Components:**
- `base_agent.py`: Abstract interface for all agents
- `agent_factory.py`: Creates framework-specific agents
- `task_decomposer.py`: Breaks complex tasks into subtasks

**Framework Adapters:**
- `langchain_adapter.py`: LangChain implementation
- `langgraph_adapter.py`: LangGraph workflow implementation
- `crewai_adapter.py`: Crew AI crew implementation
- `autogen_adapter.py`: AutoGen agent implementation

**Responsibilities:**
- Task understanding and decomposition
- Instruction retrieval coordination
- Command generation orchestration
- Execution coordination

### 4. Vector Database Layer

**Components:**
- `chroma_client.py`: Chroma database client
- `instruction_store.py`: Instruction CRUD operations

**Responsibilities:**
- Store IT ops instructions as embeddings
- Semantic search for relevant instructions
- Instruction management (add, update, delete)

### 5. LLM Service Layer

**Integration:**
- OpenAI API (GPT-4/GPT-3.5)
- Configurable for other providers

**Responsibilities:**
- Command/script generation from instructions
- Task decomposition
- Natural language understanding

### 6. Execution Layer

**Components:**
- `executor_base.py`: Base executor interface
- `aws_executor.py`: AWS CLI command execution
- `system_executor.py`: Windows/Linux command execution
- `script_generator.py`: Script generation and validation

**Responsibilities:**
- Command validation
- Secure command execution
- Result parsing and formatting
- Error handling and retry logic

### 7. Supporting Services

**Configuration Management:**
- Environment variable management
- Settings validation (pydantic)
- Multi-environment support

**Logging System:**
- Structured logging (JSON format)
- Multiple log levels
- File and console output

**Error Handling:**
- Custom exception classes
- Retry logic for transient failures
- User-friendly error messages

## Data Flow

### Standard Task Execution Flow

1. **User Query**: User submits IT ops task via Gradio interface
2. **Agent Processing**: Agent receives query and determines task type
3. **Instruction Retrieval**: Agent queries vector database for relevant instructions
4. **Task Decomposition** (if complex): Task broken into subtasks
5. **Command Generation**: LLM generates commands/scripts based on instructions
6. **Script Validation**: Script generator validates and formats commands
7. **Execution**: Appropriate executor runs the command
8. **Result Processing**: Executor parses and structures results
9. **Response**: Results displayed to user via Gradio interface

### Complex Task Flow (with Decomposition)

```
User Query: "Reset password and unlock account for user X"
    ↓
Task Decomposer: Breaks into subtasks
    ├─ Subtask 1: Reset password
    └─ Subtask 2: Unlock account
    ↓
For each subtask:
    ├─ Retrieve relevant instructions
    ├─ Generate command
    ├─ Execute command
    └─ Collect result
    ↓
Combine results and return to user
```

## Component Interactions

### Agent → Vector DB
- **Purpose**: Retrieve relevant instructions
- **Method**: Semantic similarity search
- **Input**: Task description/query
- **Output**: Ranked list of relevant instructions

### Agent → LLM
- **Purpose**: Generate commands/scripts
- **Method**: Prompt engineering with retrieved instructions
- **Input**: Task + Instructions + Context
- **Output**: Generated command/script

### Agent → Executor
- **Purpose**: Execute generated commands
- **Method**: Direct API calls
- **Input**: Validated command
- **Output**: Structured execution results

### Executor → External Systems
- **Purpose**: Perform actual IT operations
- **Methods**: 
  - AWS CLI for cloud operations
  - PowerShell for Windows systems
  - Bash/SSH for Linux systems
- **Input**: Commands/scripts
- **Output**: Command output/results

## Deployment Architecture

### Development Environment
- Local Python environment
- Local Chroma instance
- Docker Compose for services

### Production Environment (Kubernetes)
- **Application Pod**: IT Ops Agent application
- **Chroma Pod**: Vector database with persistent storage
- **ConfigMap**: Non-sensitive configuration
- **Secrets**: API keys and credentials
- **Services**: Internal and external service definitions
- **PersistentVolumes**: Data persistence for Chroma

### Container Structure
```
Application Container:
  - Python runtime
  - Application code
  - Dependencies
  - Health check endpoint

Chroma Container:
  - Chroma server
  - Persistent volume mount
  - Network exposure
```

## Security Considerations

1. **Credential Management**: Secrets stored in Kubernetes Secrets, never in code
2. **Command Validation**: All commands validated before execution
3. **Access Control**: Executor permissions limited to required operations
4. **Network Security**: Internal service communication within cluster
5. **Audit Logging**: All operations logged for audit trail

## Scalability

### Horizontal Scaling
- Stateless agent design allows multiple pod instances
- Load balancing via Kubernetes Service
- Chroma can be scaled independently

### Performance Optimization
- Vector database caching
- LLM response caching (future enhancement)
- Async execution for long-running tasks

## Extensibility Points

1. **New Agent Frameworks**: Implement base agent interface
2. **New Executors**: Extend executor base class
3. **New Task Types**: Add instructions to vector database
4. **New LLM Providers**: Abstract LLM interface (future)
5. **New Frontends**: Replace Gradio with other UI frameworks

## Technology Stack

### Core Technologies
- **Python 3.10+**: Main development language
- **Gradio**: Frontend interface
- **Chroma**: Vector database
- **OpenAI API**: LLM service
- **Pydantic**: Configuration management

### Agent Frameworks
- **LangChain**: Primary framework (Phase 1)
- **LangGraph**: Workflow-based agent
- **Crew AI**: Multi-agent crew
- **AutoGen**: Conversational agents

### Testing
- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting
- **Mocking**: For external service testing

### Deployment
- **Docker**: Containerization
- **Kubernetes**: Orchestration
- **Docker Compose**: Local development

## Future Enhancements

1. **Multi-LLM Support**: Abstract LLM interface for multiple providers
2. **Response Caching**: Cache LLM responses for common tasks
3. **Advanced Monitoring**: Prometheus metrics, Grafana dashboards
4. **Webhook Integration**: External system notifications
5. **Role-Based Access Control**: User permissions and task restrictions
6. **Task Scheduling**: Scheduled IT ops tasks
7. **Approval Workflows**: Multi-step approval for sensitive operations


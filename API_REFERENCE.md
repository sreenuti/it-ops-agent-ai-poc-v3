# API Reference

This document provides detailed API reference for the IT Ops Agent System components.

## Table of Contents

- [Agent Factory](#agent-factory)
- [Base Agent Interface](#base-agent-interface)
- [Instruction Store](#instruction-store)
- [Executors](#executors)
- [Gradio Application](#gradio-application)
- [Configuration](#configuration)

## Agent Factory

### `AgentFactory.create_agent()`

Creates an agent instance based on the configured framework.

**Signature:**
```python
@staticmethod
def create_agent(
    framework: Optional[Literal["langchain", "langgraph", "crewai", "autogen"]] = None,
    instruction_store: Optional[InstructionStore] = None,
    aws_executor: Optional[AWSExecutor] = None,
    system_executor: Optional[SystemExecutor] = None
) -> BaseAgent
```

**Parameters:**
- `framework` (optional): Framework name. Defaults to `AGENT_FRAMEWORK` environment variable.
- `instruction_store` (optional): Instruction store instance. Creates new if not provided.
- `aws_executor` (optional): AWS executor instance. Creates new if not provided.
- `system_executor` (optional): System executor instance. Creates new if not provided.

**Returns:**
- `BaseAgent`: Agent instance implementing the base agent interface.

**Example:**
```python
from src.agents.agent_factory import AgentFactory

# Create agent with default framework
agent = AgentFactory.create_agent()

# Create agent with specific framework
agent = AgentFactory.create_agent(framework="langgraph")
```

## Base Agent Interface

All agent implementations must extend `BaseAgent` and implement the following methods:

### `process_query()`

Processes a user query and returns results.

**Signature:**
```python
def process_query(
    self,
    query: str,
    chat_history: Optional[List[Dict[str, str]]] = None,
    dry_run: bool = False
) -> Dict[str, Any]
```

**Parameters:**
- `query` (str): User's query/task request.
- `chat_history` (optional): List of previous messages in format `[{"role": "user/assistant", "content": "..."}]`.
- `dry_run` (bool): If True, show commands without executing. Defaults to False.

**Returns:**
- `Dict[str, Any]`: Result dictionary containing:
  - `success` (bool): Whether the operation succeeded.
  - `response` (str): Human-readable response.
  - `commands` (list): Commands that were/would be executed.
  - `execution_results` (list): Execution results for each command.

**Example:**
```python
result = agent.process_query(
    "Reset password for user john.doe",
    dry_run=True
)
print(result["response"])
```

### `retrieve_instructions()`

Retrieves relevant instructions from the vector database.

**Signature:**
```python
def retrieve_instructions(
    self,
    query: str,
    top_k: int = 3
) -> List[Dict[str, Any]]
```

**Parameters:**
- `query` (str): Query to search for relevant instructions.
- `top_k` (int): Number of instructions to retrieve. Defaults to 3.

**Returns:**
- `List[Dict[str, Any]]`: List of instruction dictionaries containing:
  - `task_type` (str): Type of task.
  - `instruction_text` (str): Instruction content.
  - `metadata` (dict): Instruction metadata.

### `decompose_task()`

Decomposes complex tasks into subtasks.

**Signature:**
```python
def decompose_task(
    self,
    task: str
) -> List[str]
```

**Parameters:**
- `task` (str): Complex task description.

**Returns:**
- `List[str]`: List of subtask descriptions.

## Instruction Store

### `InstructionStore`

Manages IT operations instructions in the Chroma vector database.

### `add_instruction()`

Adds a new instruction to the store.

**Signature:**
```python
def add_instruction(
    self,
    task_type: str,
    instruction_text: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str
```

**Parameters:**
- `task_type` (str): Type of task (e.g., "password_reset").
- `instruction_text` (str): Instruction content.
- `metadata` (optional): Additional metadata dictionary.

**Returns:**
- `str`: Instruction ID.

**Example:**
```python
from src.vector_db.instruction_store import InstructionStore

store = InstructionStore()
instruction_id = store.add_instruction(
    task_type="password_reset",
    instruction_text="To reset password...",
    metadata={"platform": "aws", "complexity": "medium"}
)
```

### `search_instructions()`

Searches for relevant instructions.

**Signature:**
```python
def search_instructions(
    self,
    query: str,
    n_results: int = 3
) -> List[Dict[str, Any]]
```

**Parameters:**
- `query` (str): Search query.
- `n_results` (int): Number of results to return. Defaults to 3.

**Returns:**
- `List[Dict[str, Any]]`: List of matching instructions.

### `get_instruction()`

Retrieves an instruction by ID.

**Signature:**
```python
def get_instruction(
    self,
    instruction_id: str
) -> Optional[Dict[str, Any]]
```

**Parameters:**
- `instruction_id` (str): Instruction ID.

**Returns:**
- `Optional[Dict[str, Any]]`: Instruction dictionary or None if not found.

### `update_instruction()`

Updates an existing instruction.

**Signature:**
```python
def update_instruction(
    self,
    instruction_id: str,
    instruction_text: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> bool
```

**Parameters:**
- `instruction_id` (str): Instruction ID.
- `instruction_text` (optional): New instruction text.
- `metadata` (optional): Updated metadata.

**Returns:**
- `bool`: True if updated successfully.

### `delete_instruction()`

Deletes an instruction.

**Signature:**
```python
def delete_instruction(
    self,
    instruction_id: str
) -> bool
```

**Parameters:**
- `instruction_id` (str): Instruction ID.

**Returns:**
- `bool`: True if deleted successfully.

## Executors

### `AWSExecutor`

Executes AWS CLI commands.

### `execute()`

Executes an AWS CLI command.

**Signature:**
```python
def execute(
    self,
    command: str,
    dry_run: bool = False
) -> Dict[str, Any]
```

**Parameters:**
- `command` (str): AWS CLI command to execute.
- `dry_run` (bool): If True, validate but don't execute.

**Returns:**
- `Dict[str, Any]`: Execution result containing:
  - `success` (bool): Whether execution succeeded.
  - `output` (str): Command output.
  - `error` (str): Error message if failed.

**Example:**
```python
from src.script_executor.aws_executor import AWSExecutor

executor = AWSExecutor()
result = executor.execute(
    "aws iam update-login-profile --user-name john.doe --password NewPass123!",
    dry_run=True
)
```

### `SystemExecutor`

Executes system commands (PowerShell/Bash).

### `execute()`

Executes a system command.

**Signature:**
```python
def execute(
    self,
    command: str,
    shell: Optional[str] = None,
    dry_run: bool = False
) -> Dict[str, Any]
```

**Parameters:**
- `command` (str): Command to execute.
- `shell` (optional): Shell type ("powershell", "bash", "cmd"). Auto-detected if not provided.
- `dry_run` (bool): If True, validate but don't execute.

**Returns:**
- `Dict[str, Any]`: Execution result.

**Example:**
```python
from src.script_executor.system_executor import SystemExecutor

executor = SystemExecutor()
result = executor.execute(
    "Get-Service -Name 'RasMan'",
    shell="powershell"
)
```

## Gradio Application

### `GradioApp`

Main Gradio application class for the web interface.

### `__init__()`

Initializes the Gradio application.

**Signature:**
```python
def __init__(self, agent: Optional[BaseAgent] = None)
```

**Parameters:**
- `agent` (optional): Agent instance. Creates new if not provided.

### `launch()`

Launches the Gradio interface.

**Signature:**
```python
def launch(
    self,
    share: bool = False,
    server_name: Optional[str] = None,
    server_port: Optional[int] = None
)
```

**Parameters:**
- `share` (bool): Whether to create a public link. Defaults to False.
- `server_name` (optional): Server hostname. Defaults to config.
- `server_port` (optional): Server port. Defaults to config.

### Health Check Endpoint

The application exposes a health check endpoint at `/health`.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "service": "itops-agent"
}
```

**Status Codes:**
- `200`: Service is healthy
- `503`: Service is unhealthy

## Configuration

### `Settings`

Application settings loaded from environment variables.

### Available Settings

See `src/config/settings.py` for all available settings. Key settings include:

- `openai_api_key` (str, required): OpenAI API key
- `openai_model` (str): OpenAI model to use (default: "gpt-4")
- `chroma_host` (str): Chroma host (default: "localhost")
- `chroma_port` (int): Chroma port (default: 8000)
- `agent_framework` (str): Agent framework (default: "langchain")
- `execution_environment` (str): Execution environment (default: "windows")
- `log_level` (str): Log level (default: "INFO")

### `get_settings()`

Gets the global settings instance.

**Signature:**
```python
def get_settings() -> Settings
```

**Returns:**
- `Settings`: Settings instance.

**Example:**
```python
from src.config.settings import get_settings

settings = get_settings()
print(settings.openai_model)
```

## Error Handling

### Exception Classes

The system uses custom exception classes:

- `InstructionStoreError`: Errors related to instruction store operations
- `ExecutorError`: Errors during command execution
- `AgentError`: Errors during agent processing

All exceptions inherit from base exception classes and include descriptive error messages.

## Logging

The system uses structured logging (JSON format by default). Logs include:

- Agent actions
- Instruction retrievals
- Command executions
- Errors and warnings

Logs are written to both console and file (if configured).

## Examples

### Complete Example

```python
from src.agents.agent_factory import AgentFactory
from src.config.settings import get_settings

# Get settings
settings = get_settings()

# Create agent
agent = AgentFactory.create_agent(framework="langchain")

# Process query
result = agent.process_query(
    query="Reset password for user john.doe in AWS IAM",
    chat_history=[],
    dry_run=True
)

# Print results
print(f"Success: {result['success']}")
print(f"Response: {result['response']}")
if result.get('commands'):
    print("Commands:")
    for cmd in result['commands']:
        print(f"  - {cmd}")
```

For more examples, see the test files in the `tests/` directory.


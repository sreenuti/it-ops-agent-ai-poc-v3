"""
Tests for LangChain agent
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage

from src.agents.langchain_agent import LangChainAgent
from src.vector_db.instruction_store import InstructionStore
from src.script_executor.aws_executor import AWSExecutor
from src.script_executor.system_executor import SystemExecutor
from src.vector_db.chroma_client import ChromaClient


@pytest.fixture
def mock_llm():
    """Mock LangChain LLM"""
    mock = MagicMock(spec=ChatOpenAI)
    mock.model_name = "gpt-4"
    return mock


@pytest.fixture
def mock_instruction_store():
    """Mock instruction store"""
    store = MagicMock(spec=InstructionStore)
    store.retrieve_instructions.return_value = [
        {
            "id": "test-id-1",
            "text": "To reset a password in AWS IAM, use: aws iam update-login-profile --user-name USERNAME --password NEW_PASSWORD",
            "metadata": {"task_type": "password_reset", "platform": "aws"},
            "distance": 0.1
        }
    ]
    return store


@pytest.fixture
def mock_aws_executor():
    """Mock AWS executor"""
    executor = MagicMock(spec=AWSExecutor)
    executor.execute.return_value = {
        "success": True,
        "output": "Password updated successfully",
        "error": None,
        "exit_code": 0
    }
    executor.get_executor_type.return_value = "aws"
    return executor


@pytest.fixture
def mock_system_executor():
    """Mock system executor"""
    executor = MagicMock(spec=SystemExecutor)
    executor.execute.return_value = {
        "success": True,
        "output": "Command executed successfully",
        "error": None,
        "exit_code": 0
    }
    executor.get_executor_type.return_value = "system_powershell"
    return executor


@pytest.fixture
def agent_with_mocks(mock_instruction_store, mock_aws_executor, mock_system_executor, sample_env_vars):
    """Create agent with mocked dependencies"""
    with patch('src.agents.langchain_agent.ChatOpenAI') as mock_chat:
        mock_llm_instance = MagicMock()
        mock_chat.return_value = mock_llm_instance
        
        # Mock agent executor
        with patch('src.agents.langchain_agent.AgentExecutor') as mock_executor_class:
            mock_executor = MagicMock()
            mock_executor.invoke.return_value = {
                "output": "I retrieved the instructions and executed the password reset command successfully."
            }
            mock_executor_class.return_value = mock_executor
            
            agent = LangChainAgent(
                instruction_store=mock_instruction_store,
                aws_executor=mock_aws_executor,
                system_executor=mock_system_executor
            )
            agent.agent_executor = mock_executor
            return agent


def test_agent_initialization(agent_with_mocks):
    """Test agent initialization"""
    agent = agent_with_mocks
    
    assert agent.instruction_store is not None
    assert agent.aws_executor is not None
    assert agent.system_executor is not None
    assert agent.llm is not None
    assert len(agent.tools) == 3  # retrieve_instructions, execute_aws_command, execute_system_command


def test_agent_tools_created(agent_with_mocks):
    """Test that agent tools are created correctly"""
    agent = agent_with_mocks
    
    tool_names = [tool.name for tool in agent.tools]
    assert "retrieve_instructions" in tool_names
    assert "execute_aws_command" in tool_names
    assert "execute_system_command" in tool_names


def test_retrieve_instructions_tool(agent_with_mocks):
    """Test retrieve_instructions tool"""
    agent = agent_with_mocks
    
    # Find the tool
    retrieve_tool = next(tool for tool in agent.tools if tool.name == "retrieve_instructions")
    
    # Execute tool
    result = retrieve_tool.func("password reset")
    
    # Verify instruction store was called
    agent.instruction_store.retrieve_instructions.assert_called_once_with(
        query="password reset",
        n_results=5
    )
    
    # Verify result format
    assert "Relevant Instructions" in result
    assert "password_reset" in result or "password" in result.lower()


def test_execute_aws_command_tool(agent_with_mocks):
    """Test execute_aws_command tool"""
    agent = agent_with_mocks
    
    # Find the tool
    aws_tool = next(tool for tool in agent.tools if tool.name == "execute_aws_command")
    
    # Execute tool
    result = aws_tool.func("aws iam update-login-profile --user-name testuser --password NewPass123")
    
    # Verify executor was called
    agent.aws_executor.execute.assert_called_once()
    
    # Verify result
    assert "Success" in result or "Password updated" in result


def test_execute_system_command_tool(agent_with_mocks):
    """Test execute_system_command tool"""
    agent = agent_with_mocks
    
    # Find the tool
    system_tool = next(tool for tool in agent.tools if tool.name == "execute_system_command")
    
    # Execute tool
    result = system_tool.func("Get-Service -Name 'Spooler'")
    
    # Verify executor was called
    agent.system_executor.execute.assert_called_once()
    
    # Verify result
    assert "Success" in result or "executed successfully" in result.lower()


def test_process_query_success(agent_with_mocks):
    """Test processing a query successfully"""
    agent = agent_with_mocks
    
    result = agent.process_query("Reset password for user john")
    
    # Verify agent executor was called
    agent.agent_executor.invoke.assert_called_once()
    
    # Verify result structure
    assert "response" in result
    assert "success" in result
    assert "steps" in result
    assert result["success"] is True
    assert len(result["response"]) > 0


def test_process_query_with_chat_history(agent_with_mocks):
    """Test processing query with chat history"""
    agent = agent_with_mocks
    
    chat_history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi, how can I help?"}
    ]
    
    result = agent.process_query("Reset password", chat_history=chat_history)
    
    # Verify agent executor was called with history
    call_args = agent.agent_executor.invoke.call_args
    assert call_args is not None
    assert "chat_history" in call_args[0][0] or len(call_args[0][0].get("chat_history", [])) > 0


def test_process_query_dry_run(agent_with_mocks):
    """Test processing query in dry run mode"""
    agent = agent_with_mocks
    
    result = agent.process_query("Reset password for user john", dry_run=True)
    
    # Verify agent executor was called with dry run context
    call_args = agent.agent_executor.invoke.call_args
    assert call_args is not None
    input_text = call_args[0][0].get("input", "")
    assert "DRY RUN" in input_text or "dry run" in input_text.lower()


def test_process_query_error_handling(agent_with_mocks):
    """Test error handling in process_query"""
    agent = agent_with_mocks
    
    # Make executor raise an exception
    agent.agent_executor.invoke.side_effect = Exception("Test error")
    
    result = agent.process_query("Reset password")
    
    # Verify error handling
    assert result["success"] is False
    assert "error" in result or "error" in result.get("response", "").lower()
    assert len(result["response"]) > 0


def test_execute_task(agent_with_mocks):
    """Test executing a specific task"""
    agent = agent_with_mocks
    
    task_params = {
        "username": "john",
        "new_password": "NewPass123"
    }
    
    result = agent.execute_task("password_reset", task_params)
    
    # Verify agent executor was called
    agent.agent_executor.invoke.assert_called_once()
    
    # Verify result structure
    assert "response" in result
    assert "success" in result


def test_execute_task_dry_run(agent_with_mocks):
    """Test executing task in dry run mode"""
    agent = agent_with_mocks
    
    task_params = {"username": "john"}
    result = agent.execute_task("password_reset", task_params, dry_run=True)
    
    # Verify dry run was passed through
    call_args = agent.agent_executor.invoke.call_args
    assert call_args is not None
    input_text = call_args[0][0].get("input", "")
    assert "DRY RUN" in input_text or "dry run" in input_text.lower()


def test_aws_executor_error_handling(agent_with_mocks):
    """Test AWS executor error handling in tool"""
    agent = agent_with_mocks
    
    # Make executor return error
    agent.aws_executor.execute.return_value = {
        "success": False,
        "output": "",
        "error": "Invalid command",
        "exit_code": 1
    }
    
    # Find and execute AWS tool
    aws_tool = next(tool for tool in agent.tools if tool.name == "execute_aws_command")
    result = aws_tool.func("aws invalid command")
    
    # Verify error is in result
    assert "Error" in result
    assert "Invalid command" in result


def test_system_executor_error_handling(agent_with_mocks):
    """Test system executor error handling in tool"""
    agent = agent_with_mocks
    
    # Make executor return error
    agent.system_executor.execute.return_value = {
        "success": False,
        "output": "",
        "error": "Command not found",
        "exit_code": 127
    }
    
    # Find and execute system tool
    system_tool = next(tool for tool in agent.tools if tool.name == "execute_system_command")
    result = system_tool.func("invalid-command-that-does-not-exist")
    
    # Verify error is in result
    assert "Error" in result
    assert "Command not found" in result


def test_instruction_retrieval_empty_results(agent_with_mocks):
    """Test instruction retrieval when no results found"""
    agent = agent_with_mocks
    
    # Make instruction store return empty results
    agent.instruction_store.retrieve_instructions.return_value = []
    
    # Find and execute retrieve tool
    retrieve_tool = next(tool for tool in agent.tools if tool.name == "retrieve_instructions")
    result = retrieve_tool.func("nonexistent task")
    
    # Verify appropriate message
    assert "No relevant instructions" in result or "not found" in result.lower()


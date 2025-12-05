"""
Tests for LangChain adapter
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage

from src.agents.adapters.langchain_adapter import LangChainAdapter
from src.agents.base_agent import BaseAgent
from src.vector_db.instruction_store import InstructionStore
from src.script_executor.aws_executor import AWSExecutor
from src.script_executor.system_executor import SystemExecutor


@pytest.fixture
def mock_llm():
    """Mock LangChain LLM"""
    mock = MagicMock(spec=ChatOpenAI)
    mock.model_name = "gpt-4"
    mock.invoke.return_value = AIMessage(content='[{"subtask": "test", "task_type": "general", "dependencies": [], "priority": 5}]')
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
    executor.get_executor_type.return_value = "system"
    return executor


@pytest.fixture
def langchain_adapter(mock_llm, mock_instruction_store, mock_aws_executor, mock_system_executor):
    """Create LangChain adapter instance"""
    return LangChainAdapter(
        instruction_store=mock_instruction_store,
        aws_executor=mock_aws_executor,
        system_executor=mock_system_executor,
        llm=mock_llm
    )


def test_langchain_adapter_implements_base_agent(langchain_adapter):
    """Test that LangChainAdapter implements BaseAgent interface"""
    assert isinstance(langchain_adapter, BaseAgent)


def test_langchain_adapter_get_framework_name(langchain_adapter):
    """Test get_framework_name returns correct framework"""
    assert langchain_adapter.get_framework_name() == "langchain"


def test_langchain_adapter_retrieve_instructions(langchain_adapter, mock_instruction_store):
    """Test retrieve_instructions method"""
    result = langchain_adapter.retrieve_instructions("password reset", n_results=3)
    
    assert isinstance(result, list)
    assert len(result) > 0
    mock_instruction_store.retrieve_instructions.assert_called_once_with(
        query="password reset",
        task_type=None,
        n_results=3
    )


def test_langchain_adapter_decompose_task(langchain_adapter, mock_llm):
    """Test decompose_task method"""
    task = "Reset password for user john and unlock their account"
    result = langchain_adapter.decompose_task(task)
    
    assert isinstance(result, list)
    assert len(result) > 0
    assert "subtask" in result[0]
    assert "task_type" in result[0]
    mock_llm.invoke.assert_called()


def test_langchain_adapter_execute_task(langchain_adapter):
    """Test execute_task method"""
    with patch.object(langchain_adapter, 'process_query') as mock_process:
        mock_process.return_value = {
            "response": "Task executed successfully",
            "success": True,
            "steps": [],
            "error": None
        }
        
        result = langchain_adapter.execute_task(
            task_type="password_reset",
            task_params={"username": "john", "password": "NewPass123"}
        )
        
        assert result["success"] is True
        mock_process.assert_called_once()


def test_langchain_adapter_process_query_dry_run(langchain_adapter):
    """Test process_query with dry_run=True"""
    with patch.object(langchain_adapter.agent_executor, 'invoke') as mock_invoke:
        mock_invoke.return_value = {"output": "Would execute: aws iam update-login-profile..."}
        
        result = langchain_adapter.process_query(
            query="Reset password for user john",
            dry_run=True
        )
        
        assert isinstance(result, dict)
        assert "response" in result
        assert "success" in result
        # Check that dry_run was passed to agent
        call_args = mock_invoke.call_args[0][0]
        assert "[DRY RUN MODE]" in call_args["input"]


def test_langchain_adapter_process_query_with_history(langchain_adapter):
    """Test process_query with chat history"""
    with patch.object(langchain_adapter.agent_executor, 'invoke') as mock_invoke:
        mock_invoke.return_value = {"output": "Response"}
        
        chat_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi, how can I help?"}
        ]
        
        result = langchain_adapter.process_query(
            query="Reset password",
            chat_history=chat_history
        )
        
        assert isinstance(result, dict)
        # Verify history was passed
        call_args = mock_invoke.call_args[0][0]
        assert "chat_history" in call_args


def test_langchain_adapter_error_handling(langchain_adapter):
    """Test error handling in process_query"""
    with patch.object(langchain_adapter.agent_executor, 'invoke') as mock_invoke:
        mock_invoke.side_effect = Exception("Test error")
        
        result = langchain_adapter.process_query("test query")
        
        assert result["success"] is False
        assert "error" in result
        assert "Test error" in result["error"]


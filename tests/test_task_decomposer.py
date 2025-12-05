"""
Tests for TaskDecomposer
"""
import pytest
import json
from unittest.mock import Mock, MagicMock, patch
from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage

from src.task_decomposer.decomposer import TaskDecomposer
from src.vector_db.instruction_store import InstructionStore


@pytest.fixture
def mock_llm():
    """Mock LLM for task decomposition"""
    mock = MagicMock(spec=ChatOpenAI)
    mock.invoke.return_value = AIMessage(
        content='[{"subtask": "Reset password", "task_type": "password_reset", "dependencies": [], "priority": 8}, {"subtask": "Unlock account", "task_type": "account_locked", "dependencies": ["0"], "priority": 7}]'
    )
    return mock


@pytest.fixture
def mock_instruction_store():
    """Mock instruction store"""
    store = MagicMock(spec=InstructionStore)
    store.retrieve_instructions.return_value = [
        {
            "id": "inst-1",
            "text": "Instruction text",
            "metadata": {"task_type": "password_reset"},
            "distance": 0.1
        }
    ]
    return store


@pytest.fixture
def task_decomposer(mock_llm, mock_instruction_store):
    """Create TaskDecomposer instance"""
    return TaskDecomposer(
        instruction_store=mock_instruction_store,
        llm=mock_llm
    )


def test_task_decomposer_decompose_simple_task(task_decomposer, mock_llm):
    """Test decomposing a simple task"""
    task = "Reset password for user john"
    result = task_decomposer.decompose(task)
    
    assert isinstance(result, list)
    assert len(result) > 0
    assert "subtask" in result[0]
    assert "task_type" in result[0]
    assert "dependencies" in result[0]
    assert "priority" in result[0]
    mock_llm.invoke.assert_called()


def test_task_decomposer_decompose_complex_task(task_decomposer):
    """Test decomposing a complex task"""
    task = "Reset password for user john, unlock their account, and grant Jira access"
    result = task_decomposer.decompose(task, context={"username": "john"})
    
    assert isinstance(result, list)
    # Complex task should have multiple subtasks
    assert len(result) >= 1


def test_task_decomposer_decompose_with_context(task_decomposer, mock_llm):
    """Test decomposition with context"""
    task = "Reset password"
    context = {"username": "john", "platform": "aws"}
    
    result = task_decomposer.decompose(task, context=context)
    
    assert isinstance(result, list)
    # Verify context was included in prompt
    call_args = mock_llm.invoke.call_args[0][0]
    assert "context" in call_args.lower() or "john" in call_args.lower()


def test_task_decomposer_fallback_without_llm(mock_instruction_store):
    """Test fallback behavior when LLM is not available"""
    decomposer = TaskDecomposer(
        instruction_store=mock_instruction_store,
        llm=None
    )
    
    result = decomposer.decompose("test task")
    
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["subtask"] == "test task"
    assert result[0]["task_type"] == "general"


def test_task_decomposer_get_instructions_for_subtasks(task_decomposer, mock_instruction_store):
    """Test retrieving instructions for subtasks"""
    subtasks = [
        {"id": "0", "subtask": "Reset password", "task_type": "password_reset"},
        {"id": "1", "subtask": "Unlock account", "task_type": "account_locked"}
    ]
    
    result = task_decomposer.get_instructions_for_subtasks(subtasks, n_results_per_subtask=2)
    
    assert isinstance(result, dict)
    assert "0" in result
    assert "1" in result
    assert len(result["0"]) > 0
    # Verify retrieve_instructions was called for each subtask
    assert mock_instruction_store.retrieve_instructions.call_count == 2


def test_task_decomposer_create_execution_plan(task_decomposer):
    """Test creating execution plan"""
    subtasks = [
        {"id": "0", "subtask": "Reset password", "task_type": "password_reset", "priority": 8, "dependencies": []},
        {"id": "1", "subtask": "Unlock account", "task_type": "account_locked", "priority": 7, "dependencies": ["0"]}
    ]
    
    instructions_map = {
        "0": [{"id": "inst-1", "text": "Password reset instruction"}],
        "1": [{"id": "inst-2", "text": "Account unlock instruction"}]
    }
    
    plan = task_decomposer.create_execution_plan(subtasks, instructions_map)
    
    assert isinstance(plan, list)
    assert len(plan) == 2
    assert plan[0]["step_id"] == "0"  # Higher priority first
    assert "instructions" in plan[0]
    assert "order" in plan[0]


def test_task_decomposer_handles_json_parsing_error(task_decomposer, mock_llm):
    """Test handling of JSON parsing errors"""
    # Mock LLM to return invalid JSON
    mock_llm.invoke.return_value = AIMessage(content="This is not valid JSON")
    
    result = task_decomposer.decompose("test task")
    
    # Should fallback to single subtask
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["subtask"] == "test task"


def test_task_decomposer_handles_exception(task_decomposer, mock_llm):
    """Test handling of exceptions during decomposition"""
    # Mock LLM to raise exception
    mock_llm.invoke.side_effect = Exception("LLM error")
    
    result = task_decomposer.decompose("test task")
    
    # Should fallback to single subtask
    assert isinstance(result, list)
    assert len(result) == 1


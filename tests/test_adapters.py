"""
Tests for framework adapters (LangGraph, CrewAI, AutoGen)
"""
import pytest
from unittest.mock import MagicMock

from src.agents.adapters.langgraph_adapter import LangGraphAdapter
from src.agents.adapters.crewai_adapter import CrewAIAdapter
from src.agents.adapters.autogen_adapter import AutoGenAdapter
from src.agents.base_agent import BaseAgent
from src.vector_db.instruction_store import InstructionStore
from src.script_executor.aws_executor import AWSExecutor
from src.script_executor.system_executor import SystemExecutor


@pytest.fixture
def mock_instruction_store():
    """Mock instruction store"""
    store = MagicMock(spec=InstructionStore)
    store.retrieve_instructions.return_value = []
    return store


@pytest.fixture
def mock_aws_executor():
    """Mock AWS executor"""
    executor = MagicMock(spec=AWSExecutor)
    return executor


@pytest.fixture
def mock_system_executor():
    """Mock system executor"""
    executor = MagicMock(spec=SystemExecutor)
    return executor


def test_langgraph_adapter_implements_base_agent(mock_instruction_store, mock_aws_executor, mock_system_executor):
    """Test that LangGraphAdapter implements BaseAgent"""
    adapter = LangGraphAdapter(
        instruction_store=mock_instruction_store,
        aws_executor=mock_aws_executor,
        system_executor=mock_system_executor
    )
    assert isinstance(adapter, BaseAgent)


def test_langgraph_adapter_get_framework_name(mock_instruction_store, mock_aws_executor, mock_system_executor):
    """Test LangGraphAdapter framework name"""
    adapter = LangGraphAdapter(
        instruction_store=mock_instruction_store,
        aws_executor=mock_aws_executor,
        system_executor=mock_system_executor
    )
    assert adapter.get_framework_name() == "langgraph"


def test_langgraph_adapter_retrieve_instructions(mock_instruction_store, mock_aws_executor, mock_system_executor):
    """Test LangGraphAdapter retrieve_instructions"""
    adapter = LangGraphAdapter(
        instruction_store=mock_instruction_store,
        aws_executor=mock_aws_executor,
        system_executor=mock_system_executor
    )
    result = adapter.retrieve_instructions("test query")
    assert isinstance(result, list)


def test_crewai_adapter_implements_base_agent(mock_instruction_store, mock_aws_executor, mock_system_executor):
    """Test that CrewAIAdapter implements BaseAgent"""
    adapter = CrewAIAdapter(
        instruction_store=mock_instruction_store,
        aws_executor=mock_aws_executor,
        system_executor=mock_system_executor
    )
    assert isinstance(adapter, BaseAgent)


def test_crewai_adapter_get_framework_name(mock_instruction_store, mock_aws_executor, mock_system_executor):
    """Test CrewAIAdapter framework name"""
    adapter = CrewAIAdapter(
        instruction_store=mock_instruction_store,
        aws_executor=mock_aws_executor,
        system_executor=mock_system_executor
    )
    assert adapter.get_framework_name() == "crewai"


def test_autogen_adapter_implements_base_agent(mock_instruction_store, mock_aws_executor, mock_system_executor):
    """Test that AutoGenAdapter implements BaseAgent"""
    adapter = AutoGenAdapter(
        instruction_store=mock_instruction_store,
        aws_executor=mock_aws_executor,
        system_executor=mock_system_executor
    )
    assert isinstance(adapter, BaseAgent)


def test_autogen_adapter_get_framework_name(mock_instruction_store, mock_aws_executor, mock_system_executor):
    """Test AutoGenAdapter framework name"""
    adapter = AutoGenAdapter(
        instruction_store=mock_instruction_store,
        aws_executor=mock_aws_executor,
        system_executor=mock_system_executor
    )
    assert adapter.get_framework_name() == "autogen"


def test_adapters_decompose_task(mock_instruction_store, mock_aws_executor, mock_system_executor):
    """Test that all adapters implement decompose_task"""
    adapters = [
        LangGraphAdapter(mock_instruction_store, mock_aws_executor, mock_system_executor),
        CrewAIAdapter(mock_instruction_store, mock_aws_executor, mock_system_executor),
        AutoGenAdapter(mock_instruction_store, mock_aws_executor, mock_system_executor)
    ]
    
    for adapter in adapters:
        result = adapter.decompose_task("test task")
        assert isinstance(result, list)
        assert len(result) > 0
        assert "subtask" in result[0]


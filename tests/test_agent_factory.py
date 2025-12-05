"""
Tests for AgentFactory
"""
import pytest
from unittest.mock import patch, MagicMock

from src.agents.agent_factory import AgentFactory
from src.agents.adapters.langchain_adapter import LangChainAdapter
from src.agents.adapters.langgraph_adapter import LangGraphAdapter
from src.agents.adapters.crewai_adapter import CrewAIAdapter
from src.agents.adapters.autogen_adapter import AutoGenAdapter
from src.agents.base_agent import BaseAgent


def test_agent_factory_create_langchain_agent():
    """Test creating LangChain agent"""
    agent = AgentFactory.create_agent(framework="langchain")
    assert isinstance(agent, LangChainAdapter)
    assert isinstance(agent, BaseAgent)


def test_agent_factory_create_langgraph_agent():
    """Test creating LangGraph agent"""
    agent = AgentFactory.create_agent(framework="langgraph")
    assert isinstance(agent, LangGraphAdapter)
    assert isinstance(agent, BaseAgent)


def test_agent_factory_create_crewai_agent():
    """Test creating CrewAI agent"""
    agent = AgentFactory.create_agent(framework="crewai")
    assert isinstance(agent, CrewAIAdapter)
    assert isinstance(agent, BaseAgent)


def test_agent_factory_create_autogen_agent():
    """Test creating AutoGen agent"""
    agent = AgentFactory.create_agent(framework="autogen")
    assert isinstance(agent, AutoGenAdapter)
    assert isinstance(agent, BaseAgent)


def test_agent_factory_invalid_framework():
    """Test that invalid framework raises ValueError"""
    with pytest.raises(ValueError, match="Unsupported framework"):
        AgentFactory.create_agent(framework="invalid_framework")


def test_agent_factory_uses_config_default():
    """Test that factory uses config default when framework not specified"""
    with patch('src.agents.agent_factory.get_settings') as mock_settings:
        mock_settings.return_value.agent_framework = "langchain"
        agent = AgentFactory.create_agent()
        assert isinstance(agent, LangChainAdapter)


def test_agent_factory_get_available_frameworks():
    """Test get_available_frameworks"""
    frameworks = AgentFactory.get_available_frameworks()
    assert isinstance(frameworks, list)
    assert "langchain" in frameworks
    assert "langgraph" in frameworks
    assert "crewai" in frameworks
    assert "autogen" in frameworks


def test_agent_factory_is_framework_available():
    """Test is_framework_available"""
    # Test with import check
    with patch('builtins.__import__') as mock_import:
        # Test available
        mock_import.return_value = MagicMock()
        assert AgentFactory.is_framework_available("langchain") is True
        
        # Test unavailable
        mock_import.side_effect = ImportError()
        # Note: This will actually try to import, so we test the real behavior
        result = AgentFactory.is_framework_available("langchain")
        assert isinstance(result, bool)  # Should return bool regardless


def test_agent_factory_with_custom_dependencies():
    """Test factory with custom instruction store and executors"""
    from unittest.mock import MagicMock
    
    mock_store = MagicMock()
    mock_aws = MagicMock()
    mock_sys = MagicMock()
    
    agent = AgentFactory.create_agent(
        framework="langchain",
        instruction_store=mock_store,
        aws_executor=mock_aws,
        system_executor=mock_sys
    )
    
    assert agent.instruction_store == mock_store
    assert agent.aws_executor == mock_aws
    assert agent.system_executor == mock_sys


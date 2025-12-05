"""
Integration tests for framework switching
"""
import pytest
from unittest.mock import patch, MagicMock

from src.agents.agent_factory import AgentFactory
from src.agents.base_agent import BaseAgent
from src.agents.adapters.langchain_adapter import LangChainAdapter
from src.agents.adapters.langgraph_adapter import LangGraphAdapter
from src.agents.adapters.crewai_adapter import CrewAIAdapter
from src.agents.adapters.autogen_adapter import AutoGenAdapter


def test_framework_switching_langchain_to_langgraph():
    """Test switching from LangChain to LangGraph"""
    agent1 = AgentFactory.create_agent(framework="langchain")
    agent2 = AgentFactory.create_agent(framework="langgraph")
    
    assert isinstance(agent1, LangChainAdapter)
    assert isinstance(agent2, LangGraphAdapter)
    assert agent1.get_framework_name() == "langchain"
    assert agent2.get_framework_name() == "langgraph"


def test_framework_switching_all_frameworks():
    """Test switching between all frameworks"""
    frameworks = ["langchain", "langgraph", "crewai", "autogen"]
    agents = {}
    
    for framework in frameworks:
        agents[framework] = AgentFactory.create_agent(framework=framework)
        assert isinstance(agents[framework], BaseAgent)
        assert agents[framework].get_framework_name() == framework


def test_framework_switching_consistent_interface():
    """Test that all frameworks implement consistent interface"""
    frameworks = ["langchain", "langgraph", "crewai", "autogen"]
    
    for framework in frameworks:
        agent = AgentFactory.create_agent(framework=framework)
        
        # All should have same methods
        assert hasattr(agent, 'decompose_task')
        assert hasattr(agent, 'retrieve_instructions')
        assert hasattr(agent, 'execute_task')
        assert hasattr(agent, 'process_query')
        assert hasattr(agent, 'get_framework_name')
        
        # All should return consistent types
        instructions = agent.retrieve_instructions("test query")
        assert isinstance(instructions, list)
        
        subtasks = agent.decompose_task("test task")
        assert isinstance(subtasks, list)


def test_framework_switching_with_same_dependencies():
    """Test that frameworks can share same dependencies"""
    from unittest.mock import MagicMock
    
    mock_store = MagicMock()
    mock_aws = MagicMock()
    mock_sys = MagicMock()
    
    frameworks = ["langchain", "langgraph"]
    agents = []
    
    for framework in frameworks:
        agent = AgentFactory.create_agent(
            framework=framework,
            instruction_store=mock_store,
            aws_executor=mock_aws,
            system_executor=mock_sys
        )
        agents.append(agent)
        
        # Verify same dependencies are used
        assert agent.instruction_store == mock_store
        assert agent.aws_executor == mock_aws
        assert agent.system_executor == mock_sys


def test_framework_switching_via_config():
    """Test framework switching via configuration"""
    with patch('src.agents.agent_factory.get_settings') as mock_settings:
        # Test LangChain
        mock_settings.return_value.agent_framework = "langchain"
        agent1 = AgentFactory.create_agent()
        assert isinstance(agent1, LangChainAdapter)
        
        # Test LangGraph
        mock_settings.return_value.agent_framework = "langgraph"
        agent2 = AgentFactory.create_agent()
        assert isinstance(agent2, LangGraphAdapter)
        
        # Test CrewAI
        mock_settings.return_value.agent_framework = "crewai"
        agent3 = AgentFactory.create_agent()
        assert isinstance(agent3, CrewAIAdapter)
        
        # Test AutoGen
        mock_settings.return_value.agent_framework = "autogen"
        agent4 = AgentFactory.create_agent()
        assert isinstance(agent4, AutoGenAdapter)


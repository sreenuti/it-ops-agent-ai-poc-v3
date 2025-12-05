"""
Tests for BaseAgent interface
"""
import pytest
from abc import ABC

from src.agents.base_agent import BaseAgent


def test_base_agent_is_abstract():
    """Test that BaseAgent is abstract and cannot be instantiated"""
    with pytest.raises(TypeError):
        BaseAgent()


def test_base_agent_has_required_methods():
    """Test that BaseAgent defines all required abstract methods"""
    # Check that BaseAgent has all required methods
    assert hasattr(BaseAgent, 'decompose_task')
    assert hasattr(BaseAgent, 'retrieve_instructions')
    assert hasattr(BaseAgent, 'execute_task')
    assert hasattr(BaseAgent, 'process_query')
    assert hasattr(BaseAgent, 'get_framework_name')
    
    # Check that methods are abstract
    assert getattr(BaseAgent.decompose_task, '__isabstractmethod__', False)
    assert getattr(BaseAgent.retrieve_instructions, '__isabstractmethod__', False)
    assert getattr(BaseAgent.execute_task, '__isabstractmethod__', False)
    assert getattr(BaseAgent.process_query, '__isabstractmethod__', False)
    assert getattr(BaseAgent.get_framework_name, '__isabstractmethod__', False)


def test_base_agent_interface_contract():
    """Test that BaseAgent methods have correct signatures"""
    import inspect
    
    # Check decompose_task signature
    sig = inspect.signature(BaseAgent.decompose_task)
    assert 'task' in sig.parameters
    assert 'context' in sig.parameters
    
    # Check retrieve_instructions signature
    sig = inspect.signature(BaseAgent.retrieve_instructions)
    assert 'query' in sig.parameters
    assert 'task_type' in sig.parameters
    assert 'n_results' in sig.parameters
    
    # Check execute_task signature
    sig = inspect.signature(BaseAgent.execute_task)
    assert 'task_type' in sig.parameters
    assert 'task_params' in sig.parameters
    assert 'dry_run' in sig.parameters
    
    # Check process_query signature
    sig = inspect.signature(BaseAgent.process_query)
    assert 'query' in sig.parameters
    assert 'chat_history' in sig.parameters
    assert 'dry_run' in sig.parameters
    
    # Check get_framework_name signature
    sig = inspect.signature(BaseAgent.get_framework_name)
    assert len(sig.parameters) == 0  # No parameters, just self


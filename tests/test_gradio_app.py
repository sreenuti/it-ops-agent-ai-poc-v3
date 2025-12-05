"""
Tests for Gradio application
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from src.api.gradio_app import GradioApp
from src.agents.langchain_agent import LangChainAgent


@pytest.fixture
def mock_agent():
    """Mock LangChain agent"""
    agent = MagicMock(spec=LangChainAgent)
    agent.process_query.return_value = {
        "response": "I've successfully reset the password for user john.",
        "success": True,
        "steps": [],
        "error": None
    }
    return agent


@pytest.fixture
def gradio_app(mock_agent):
    """Create Gradio app with mocked agent"""
    return GradioApp(agent=mock_agent)


def test_gradio_app_initialization(gradio_app):
    """Test Gradio app initialization"""
    assert gradio_app.agent is not None
    assert gradio_app.chat_history == []
    assert gradio_app.settings is not None


def test_gradio_app_initialization_without_agent(sample_env_vars):
    """Test Gradio app initialization without providing agent"""
    with patch('src.api.gradio_app.LangChainAgent') as mock_agent_class:
        mock_agent_instance = MagicMock()
        mock_agent_class.return_value = mock_agent_instance
        
        app = GradioApp()
        
        assert app.agent is not None
        mock_agent_class.assert_called_once()


def test_chat_interface_success(gradio_app, mock_agent):
    """Test chat interface with successful response"""
    history = []
    message = "Reset password for user john"
    
    new_history = gradio_app.chat_interface(message, history)
    
    # Verify agent was called
    mock_agent.process_query.assert_called_once()
    call_args = mock_agent.process_query.call_args
    assert call_args[0][0] == message
    
    # Verify history was updated
    assert len(new_history) == 1
    assert new_history[0][0] == message
    assert "✅" in new_history[0][1] or "successfully" in new_history[0][1].lower()


def test_chat_interface_with_history(gradio_app, mock_agent):
    """Test chat interface with existing history"""
    history = [
        ("Hello", "Hi! How can I help?"),
        ("What can you do?", "I can help with IT ops tasks.")
    ]
    message = "Reset password for user john"
    
    new_history = gradio_app.chat_interface(message, history)
    
    # Verify agent was called with history
    call_args = mock_agent.process_query.call_args
    assert call_args[0][0] == message
    assert len(call_args[1].get("chat_history", [])) == 4  # 2 previous exchanges
    
    # Verify history was updated
    assert len(new_history) == 3


def test_chat_interface_empty_message(gradio_app, mock_agent):
    """Test chat interface with empty message"""
    history = []
    message = ""
    
    new_history = gradio_app.chat_interface(message, history)
    
    # Verify agent was not called
    mock_agent.process_query.assert_not_called()
    
    # Verify history unchanged
    assert len(new_history) == 0


def test_chat_interface_whitespace_message(gradio_app, mock_agent):
    """Test chat interface with whitespace-only message"""
    history = []
    message = "   "
    
    new_history = gradio_app.chat_interface(message, history)
    
    # Verify agent was not called
    mock_agent.process_query.assert_not_called()
    
    # Verify history unchanged
    assert len(new_history) == 0


def test_chat_interface_error_handling(gradio_app, mock_agent):
    """Test chat interface error handling"""
    history = []
    message = "Reset password"
    
    # Make agent raise exception
    mock_agent.process_query.side_effect = Exception("Test error")
    
    new_history = gradio_app.chat_interface(message, history)
    
    # Verify history was updated with error
    assert len(new_history) == 1
    assert "❌" in new_history[0][1]
    assert "Error" in new_history[0][1]


def test_chat_interface_failed_response(gradio_app, mock_agent):
    """Test chat interface with failed agent response"""
    history = []
    message = "Reset password"
    
    # Make agent return failure
    mock_agent.process_query.return_value = {
        "response": "Failed to reset password: User not found",
        "success": False,
        "steps": [],
        "error": "User not found"
    }
    
    new_history = gradio_app.chat_interface(message, history)
    
    # Verify history was updated with failure indicator
    assert len(new_history) == 1
    assert "❌" in new_history[0][1] or "Failed" in new_history[0][1]


def test_create_interface(gradio_app):
    """Test interface creation"""
    interface = gradio_app.create_interface()
    
    assert interface is not None
    # Verify interface has expected components (basic check)
    assert hasattr(interface, 'launch')


@patch('gradio.Blocks.launch')
def test_launch_interface(mock_launch, gradio_app):
    """Test launching the interface"""
    gradio_app.launch(share=False)
    
    # Verify launch was called
    mock_launch.assert_called_once()


@patch('gradio.Blocks.launch')
def test_launch_interface_with_custom_params(mock_launch, gradio_app):
    """Test launching interface with custom parameters"""
    gradio_app.launch(share=True, server_name="0.0.0.0", server_port=8080)
    
    # Verify launch was called with correct parameters
    mock_launch.assert_called_once()
    call_kwargs = mock_launch.call_args[1]
    assert call_kwargs.get("server_name") == "0.0.0.0"
    assert call_kwargs.get("server_port") == 8080
    assert call_kwargs.get("share") is True


def test_chat_interface_response_formatting(gradio_app, mock_agent):
    """Test response formatting in chat interface"""
    history = []
    message = "Test message"
    
    # Test with success response
    mock_agent.process_query.return_value = {
        "response": "Task completed successfully",
        "success": True,
        "steps": [],
        "error": None
    }
    
    new_history = gradio_app.chat_interface(message, history)
    
    # Verify success indicator
    assert "✅" in new_history[0][1]
    assert "Task completed successfully" in new_history[0][1]
    
    # Test with failure response
    mock_agent.process_query.return_value = {
        "response": "Task failed",
        "success": False,
        "steps": [],
        "error": "Some error"
    }
    
    history2 = []
    new_history2 = gradio_app.chat_interface(message, history2)
    
    # Verify failure indicator
    assert "❌" in new_history2[0][1]
    assert "Task failed" in new_history2[0][1]


def test_chat_interface_history_conversion(gradio_app, mock_agent):
    """Test conversion between Gradio and agent history formats"""
    # Gradio format: list of (user, assistant) tuples
    gradio_history = [
        ("Hello", "Hi!"),
        ("What can you do?", "I help with IT ops.")
    ]
    
    message = "Reset password"
    gradio_app.chat_interface(message, gradio_history)
    
    # Verify agent received properly formatted history
    call_args = mock_agent.process_query.call_args
    agent_history = call_args[1].get("chat_history", [])
    
    # Should have 4 messages (2 user, 2 assistant)
    assert len(agent_history) == 4
    assert agent_history[0]["role"] == "user"
    assert agent_history[0]["content"] == "Hello"
    assert agent_history[1]["role"] == "assistant"
    assert agent_history[1]["content"] == "Hi!"


def test_chat_interface_empty_response(gradio_app, mock_agent):
    """Test handling of empty agent response"""
    history = []
    message = "Test message"
    
    mock_agent.process_query.return_value = {
        "response": "",
        "success": True,
        "steps": [],
        "error": None
    }
    
    new_history = gradio_app.chat_interface(message, history)
    
    # Should still have a response (fallback message)
    assert len(new_history) == 1
    assert len(new_history[0][1]) > 0


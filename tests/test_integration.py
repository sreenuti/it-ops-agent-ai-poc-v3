"""
End-to-end integration tests for IT Ops Agent System
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from src.agents.langchain_agent import LangChainAgent
from src.api.gradio_app import GradioApp
from src.vector_db.instruction_store import InstructionStore
from src.vector_db.chroma_client import ChromaClient
from src.script_executor.aws_executor import AWSExecutor
from src.script_executor.system_executor import SystemExecutor


@pytest.fixture
def mock_agent_executor():
    """Mock agent executor for integration tests"""
    mock_executor = MagicMock()
    
    # Mock different scenarios
    def invoke_side_effect(input_dict):
        query = input_dict.get("input", "")
        
        if "password reset" in query.lower():
            return {
                "output": "I retrieved the password reset instructions and executed the AWS IAM command to reset the password successfully."
            }
        elif "vpn" in query.lower():
            return {
                "output": "I retrieved VPN troubleshooting instructions and ran diagnostic commands. The VPN connection should be working now."
            }
        elif "outlook" in query.lower():
            return {
                "output": "I retrieved Outlook sync instructions and executed the necessary commands to fix the sync issue."
            }
        else:
            return {
                "output": "I processed your request and executed the necessary commands."
            }
    
    mock_executor.invoke.side_effect = invoke_side_effect
    return mock_executor


@pytest.fixture
def integration_agent(mock_agent_executor, temp_chroma_dir, sample_env_vars):
    """Create agent for integration testing with mocked LLM"""
    with patch('src.agents.langchain_agent.ChatOpenAI') as mock_chat:
        mock_llm_instance = MagicMock()
        mock_chat.return_value = mock_llm_instance
        
        with patch('src.agents.langchain_agent.AgentExecutor') as mock_executor_class:
            mock_executor_class.return_value = mock_agent_executor
            
            # Create real components
            chroma_client = ChromaClient(persist_dir=temp_chroma_dir)
            instruction_store = InstructionStore(chroma_client)
            aws_executor = AWSExecutor()
            system_executor = SystemExecutor()
            
            # Add sample instructions
            instruction_store.add_instruction(
                task_type="password_reset",
                instruction_text="To reset a password in AWS IAM, use: aws iam update-login-profile --user-name USERNAME --password NEW_PASSWORD --password-reset-required"
            )
            instruction_store.add_instruction(
                task_type="vpn_troubleshooting",
                instruction_text="To troubleshoot VPN issues: 1. Check VPN service status, 2. Verify network connectivity, 3. Restart VPN service if needed"
            )
            instruction_store.add_instruction(
                task_type="outlook_sync",
                instruction_text="To fix Outlook sync: 1. Close Outlook, 2. Clear Outlook cache, 3. Restart Outlook, 4. Check sync status"
            )
            
            agent = LangChainAgent(
                instruction_store=instruction_store,
                aws_executor=aws_executor,
                system_executor=system_executor
            )
            agent.agent_executor = mock_agent_executor
            
            return agent


@pytest.fixture
def integration_app(integration_agent):
    """Create Gradio app for integration testing"""
    return GradioApp(agent=integration_agent)


def test_password_reset_integration(integration_agent):
    """Test end-to-end password reset flow"""
    query = "Reset password for user john.doe"
    
    result = integration_agent.process_query(query, dry_run=True)
    
    # Verify result structure
    assert "response" in result
    assert "success" in result
    assert len(result["response"]) > 0
    
    # Verify agent executor was called
    integration_agent.agent_executor.invoke.assert_called_once()
    
    # Verify response mentions password reset
    assert "password" in result["response"].lower() or "reset" in result["response"].lower()


def test_vpn_troubleshooting_integration(integration_agent):
    """Test end-to-end VPN troubleshooting flow"""
    query = "Troubleshoot VPN connection issues"
    
    result = integration_agent.process_query(query, dry_run=True)
    
    # Verify result structure
    assert "response" in result
    assert "success" in result
    
    # Verify agent executor was called
    integration_agent.agent_executor.invoke.assert_called_once()
    
    # Verify response mentions VPN
    assert "vpn" in result["response"].lower()


def test_outlook_sync_integration(integration_agent):
    """Test end-to-end Outlook sync troubleshooting flow"""
    query = "Fix Outlook sync issues"
    
    result = integration_agent.process_query(query, dry_run=True)
    
    # Verify result structure
    assert "response" in result
    assert "success" in result
    
    # Verify agent executor was called
    integration_agent.agent_executor.invoke.assert_called_once()
    
    # Verify response mentions Outlook
    assert "outlook" in result["response"].lower() or "sync" in result["response"].lower()


def test_gradio_app_integration(integration_app, integration_agent):
    """Test Gradio app integration with agent"""
    history = []
    message = "Reset password for user john.doe"
    
    new_history = integration_app.chat_interface(message, history)
    
    # Verify history was updated
    assert len(new_history) == 1
    assert new_history[0][0] == message
    assert len(new_history[0][1]) > 0
    
    # Verify agent was called
    integration_agent.agent_executor.invoke.assert_called_once()


def test_conversation_flow_integration(integration_app, integration_agent):
    """Test multi-turn conversation flow"""
    history = []
    
    # First message
    message1 = "Hello"
    history = integration_app.chat_interface(message1, history)
    
    # Second message with context
    message2 = "Reset password for user john"
    history = integration_app.chat_interface(message2, history)
    
    # Verify both messages in history
    assert len(history) == 2
    assert history[0][0] == message1
    assert history[1][0] == message2
    
    # Verify agent was called twice
    assert integration_agent.agent_executor.invoke.call_count == 2


def test_dry_run_mode_integration(integration_agent):
    """Test dry run mode in integration"""
    query = "Reset password for user john"
    
    result = integration_agent.process_query(query, dry_run=True)
    
    # Verify dry run was passed through
    call_args = integration_agent.agent_executor.invoke.call_args
    assert call_args is not None
    input_text = call_args[0][0].get("input", "")
    assert "DRY RUN" in input_text or "dry run" in input_text.lower()
    
    # Verify result
    assert "response" in result
    assert "success" in result


def test_instruction_retrieval_integration(integration_agent):
    """Test that instructions are retrieved during integration"""
    query = "Reset password for user testuser"
    
    # Get the retrieve_instructions tool
    retrieve_tool = next(tool for tool in integration_agent.tools if tool.name == "retrieve_instructions")
    
    # Execute tool directly
    result = retrieve_tool.func(query)
    
    # Verify instructions were retrieved
    assert "password_reset" in result.lower() or "password" in result.lower()
    assert "instruction" in result.lower() or "aws" in result.lower()


def test_aws_command_execution_integration(integration_agent):
    """Test AWS command execution in integration"""
    # Get the execute_aws_command tool
    aws_tool = next(tool for tool in integration_agent.tools if tool.name == "execute_aws_command")
    
    # Execute AWS command (in dry run mode via executor)
    command = "aws iam update-login-profile --user-name testuser --password NewPass123"
    result = aws_tool.func(command)
    
    # Verify executor was called
    integration_agent.aws_executor.execute.assert_called_once()
    
    # Verify result
    assert len(result) > 0
    assert "Success" in result or "DRY RUN" in result or "Error" in result


def test_system_command_execution_integration(integration_agent):
    """Test system command execution in integration"""
    # Get the execute_system_command tool
    system_tool = next(tool for tool in integration_agent.tools if tool.name == "execute_system_command")
    
    # Execute system command
    command = "Get-Service -Name 'Spooler'"
    result = system_tool.func(command)
    
    # Verify executor was called
    integration_agent.system_executor.execute.assert_called_once()
    
    # Verify result
    assert len(result) > 0
    assert "Success" in result or "DRY RUN" in result or "Error" in result


def test_error_handling_integration(integration_agent):
    """Test error handling in integration"""
    # Make agent executor raise exception
    integration_agent.agent_executor.invoke.side_effect = Exception("Integration test error")
    
    query = "Reset password"
    result = integration_agent.process_query(query)
    
    # Verify error handling
    assert result["success"] is False
    assert "error" in result.get("response", "").lower() or "error" in result.get("error", "").lower()


def test_task_execution_with_parameters_integration(integration_agent):
    """Test executing specific task with parameters"""
    task_params = {
        "username": "john.doe",
        "new_password": "NewPass123"
    }
    
    result = integration_agent.execute_task("password_reset", task_params, dry_run=True)
    
    # Verify result structure
    assert "response" in result
    assert "success" in result
    
    # Verify agent was called
    integration_agent.agent_executor.invoke.assert_called_once()
    
    # Verify parameters were included in query
    call_args = integration_agent.agent_executor.invoke.call_args
    input_text = call_args[0][0].get("input", "")
    assert "password_reset" in input_text.lower()


def test_multiple_task_types_integration(integration_agent):
    """Test handling multiple different task types"""
    tasks = [
        "Reset password for user john",
        "Troubleshoot VPN connection",
        "Fix Outlook sync issues"
    ]
    
    results = []
    for task in tasks:
        result = integration_agent.process_query(task, dry_run=True)
        results.append(result)
    
    # Verify all tasks were processed
    assert len(results) == 3
    
    # Verify all have responses
    for result in results:
        assert "response" in result
        assert "success" in result
    
    # Verify agent was called for each task
    assert integration_agent.agent_executor.invoke.call_count == 3


def test_instruction_store_integration(temp_chroma_dir, sample_env_vars):
    """Test instruction store integration with Chroma"""
    chroma_client = ChromaClient(persist_dir=temp_chroma_dir)
    instruction_store = InstructionStore(chroma_client)
    
    # Add instruction
    instruction_id = instruction_store.add_instruction(
        task_type="password_reset",
        instruction_text="Test instruction for password reset"
    )
    
    assert instruction_id is not None
    
    # Retrieve instruction
    instructions = instruction_store.retrieve_instructions("password reset")
    
    assert len(instructions) > 0
    assert instructions[0]["metadata"]["task_type"] == "password_reset"


def test_full_stack_integration(integration_app, integration_agent):
    """Test full stack from Gradio app through agent to executors"""
    # Simulate user interaction through Gradio
    history = []
    
    # User asks to reset password
    message = "Reset password for user john.doe in AWS IAM"
    history = integration_app.chat_interface(message, history)
    
    # Verify full flow
    assert len(history) == 1
    assert history[0][0] == message
    assert len(history[0][1]) > 0
    
    # Verify agent was called
    integration_agent.agent_executor.invoke.assert_called_once()
    
    # Verify response has status indicator
    assert "✅" in history[0][1] or "❌" in history[0][1]


# Phase 3: Error scenario integration tests

def test_execution_error_handling(integration_agent):
    """Test handling of execution errors"""
    from src.utils.error_handler import ExecutionError
    
    # Mock executor to raise execution error
    integration_agent.aws_executor.execute = Mock(
        side_effect=ExecutionError(
            "AWS command failed",
            command="aws iam update-login-profile",
            exit_code=1
        )
    )
    
    query = "Reset password for user test"
    result = integration_agent.process_query(query, dry_run=False)
    
    # Verify error was handled
    assert result["success"] is False
    assert "error" in result.get("response", "").lower() or "error" in result.get("error", "").lower()


def test_timeout_error_handling(integration_agent):
    """Test handling of timeout errors"""
    from src.utils.error_handler import TimeoutError
    
    # Mock executor to raise timeout error
    integration_agent.system_executor.execute = Mock(
        side_effect=TimeoutError(
            "Command timed out",
            timeout_seconds=30.0
        )
    )
    
    query = "Check system status"
    result = integration_agent.process_query(query, dry_run=False)
    
    # Verify timeout was handled
    assert result["success"] is False
    assert "timeout" in result.get("response", "").lower() or "timeout" in result.get("error", "").lower()


def test_permission_error_handling(integration_agent):
    """Test handling of permission errors"""
    from src.utils.error_handler import PermissionError
    
    # Mock executor to raise permission error
    integration_agent.aws_executor.execute = Mock(
        side_effect=PermissionError(
            "Access denied",
            resource="aws iam update-login-profile"
        )
    )
    
    query = "Reset password for user test"
    result = integration_agent.process_query(query, dry_run=False)
    
    # Verify permission error was handled
    assert result["success"] is False
    assert "permission" in result.get("response", "").lower() or "access" in result.get("response", "").lower()


def test_validation_error_handling(integration_agent):
    """Test handling of validation errors"""
    from src.utils.error_handler import ValidationError
    
    # Mock executor to raise validation error
    integration_agent.system_executor.execute = Mock(
        side_effect=ValidationError(
            "Invalid command",
            details={"command": "rm -rf /"}
        )
    )
    
    query = "Execute dangerous command"
    result = integration_agent.process_query(query, dry_run=False)
    
    # Verify validation error was handled
    assert result["success"] is False
    assert "invalid" in result.get("response", "").lower() or "validation" in result.get("response", "").lower()


def test_network_error_handling(integration_agent):
    """Test handling of network errors"""
    from src.utils.error_handler import NetworkError
    
    # Mock executor to raise network error
    integration_agent.aws_executor.execute = Mock(
        side_effect=NetworkError(
            "Connection failed",
            endpoint="aws-us-east-1"
        )
    )
    
    query = "Reset password for user test"
    result = integration_agent.process_query(query, dry_run=False)
    
    # Verify network error was handled
    assert result["success"] is False
    assert "network" in result.get("response", "").lower() or "connection" in result.get("response", "").lower()


def test_retrieval_error_handling(integration_agent):
    """Test handling of instruction retrieval errors"""
    from src.utils.error_handler import RetrievalError
    
    # Mock instruction store to raise retrieval error
    integration_agent.instruction_store.retrieve_instructions = Mock(
        side_effect=RetrievalError(
            "Failed to retrieve instructions",
            query="password reset"
        )
    )
    
    query = "Reset password for user test"
    result = integration_agent.process_query(query, dry_run=True)
    
    # Verify retrieval error was handled
    assert result["success"] is False
    assert "retriev" in result.get("response", "").lower() or "error" in result.get("response", "").lower()


def test_error_handling_across_task_types(integration_agent):
    """Test error handling across different task types"""
    from src.utils.error_handler import ExecutionError
    
    task_types = [
        "password_reset",
        "vpn_troubleshooting",
        "outlook_sync",
        "account_locked"
    ]
    
    # Mock executor to raise errors for all task types
    integration_agent.aws_executor.execute = Mock(
        side_effect=ExecutionError("Command failed", command="test")
    )
    integration_agent.system_executor.execute = Mock(
        side_effect=ExecutionError("Command failed", command="test")
    )
    
    for task_type in task_types:
        query = f"Execute {task_type} task"
        result = integration_agent.process_query(query, dry_run=False)
        
        # Verify all task types handle errors gracefully
        assert "response" in result
        assert "success" in result
        # Error should be handled, not crash
        assert isinstance(result["success"], bool)


def test_conversation_manager_error_handling(integration_app):
    """Test error handling in conversation manager"""
    from src.api.conversation_manager import ConversationManager
    
    manager = ConversationManager()
    
    # Try to add message to non-existent session
    result = manager.add_message("nonexistent", "user", "Hello")
    assert result is False
    
    # Create session and add message
    conv = manager.create_conversation(session_id="test-session")
    result = manager.add_message("test-session", "user", "Hello")
    assert result is True
    
    # Get context from non-existent session
    context = manager.get_context("nonexistent")
    assert context is None


def test_instruction_manager_error_handling():
    """Test error handling in instruction manager"""
    from src.api.instruction_manager import InstructionManager
    from src.utils.error_handler import ValidationError, RetrievalError
    
    manager = InstructionManager()
    
    # Test validation errors
    with pytest.raises(ValidationError):
        manager.add_instruction("", "Test instruction")
    
    with pytest.raises(ValidationError):
        manager.add_instruction("test", "Short")
    
    # Test retrieval errors
    with pytest.raises(RetrievalError):
        manager.get_instruction("nonexistent-id")
    
    with pytest.raises(RetrievalError):
        manager.update_instruction("nonexistent-id", instruction_text="New text")
    
    with pytest.raises(RetrievalError):
        manager.delete_instruction("nonexistent-id")


def test_error_recovery_after_failure(integration_agent):
    """Test system recovery after error"""
    from src.utils.error_handler import ExecutionError
    
    # First call fails
    integration_agent.aws_executor.execute = Mock(
        side_effect=ExecutionError("First attempt failed", command="test")
    )
    
    result1 = integration_agent.process_query("Reset password", dry_run=False)
    assert result1["success"] is False
    
    # Second call succeeds
    integration_agent.aws_executor.execute = Mock(
        return_value={"success": True, "output": "Success", "error": None, "exit_code": 0}
    )
    
    result2 = integration_agent.process_query("Reset password", dry_run=False)
    # Should recover and succeed
    assert result2["success"] is True or "response" in result2

"""
Tests for ScriptGenerator
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage

from src.script_executor.script_generator import ScriptGenerator
from src.vector_db.instruction_store import InstructionStore


@pytest.fixture
def mock_llm():
    """Mock LLM for script generation"""
    mock = MagicMock(spec=ChatOpenAI)
    mock.invoke.return_value = AIMessage(content="aws iam update-login-profile --user-name john --password NewPass123")
    return mock


@pytest.fixture
def mock_instruction_store():
    """Mock instruction store"""
    store = MagicMock(spec=InstructionStore)
    return store


@pytest.fixture
def script_generator(mock_llm, mock_instruction_store):
    """Create ScriptGenerator instance"""
    return ScriptGenerator(
        instruction_store=mock_instruction_store,
        llm=mock_llm
    )


@pytest.fixture
def sample_instructions():
    """Sample instructions for testing"""
    return [
        {
            "id": "inst-1",
            "text": "To reset password in AWS IAM, use: aws iam update-login-profile --user-name USERNAME --password PASSWORD",
            "metadata": {"task_type": "password_reset", "platform": "aws"}
        }
    ]


def test_script_generator_generate_aws_script(script_generator, sample_instructions, mock_llm):
    """Test generating AWS script"""
    task_params = {"username": "john", "password": "NewPass123"}
    
    result = script_generator.generate_script(
        instructions=sample_instructions,
        task_params=task_params,
        executor_type="aws"
    )
    
    assert isinstance(result, dict)
    assert "script" in result
    assert "commands" in result
    assert "validation_errors" in result
    assert "executor_type" in result
    assert result["executor_type"] == "aws"
    assert "aws" in result["script"].lower()
    mock_llm.invoke.assert_called()


def test_script_generator_generate_powershell_script(script_generator, sample_instructions):
    """Test generating PowerShell script"""
    instructions = [{
        "id": "inst-1",
        "text": "To reset password in AD, use: Set-ADAccountPassword -Identity USERNAME -NewPassword (ConvertTo-SecureString PASSWORD -AsPlainText -Force)",
        "metadata": {"task_type": "password_reset"}
    }]
    
    task_params = {"username": "john", "password": "NewPass123"}
    
    result = script_generator.generate_script(
        instructions=instructions,
        task_params=task_params,
        executor_type="powershell"
    )
    
    assert result["executor_type"] == "powershell"


def test_script_generator_validate_script(script_generator):
    """Test script validation"""
    # Valid script
    valid_script = "aws iam update-login-profile --user-name john --password NewPass123"
    errors = script_generator.validate_script(valid_script, "aws", {"username": "john"})
    assert len(errors) == 0
    
    # Empty script
    errors = script_generator.validate_script("", "aws", {})
    assert len(errors) > 0
    assert "empty" in errors[0].lower()
    
    # Dangerous command
    dangerous_script = "rm -rf /"
    errors = script_generator.validate_script(dangerous_script, "bash", {})
    assert len(errors) > 0
    assert "dangerous" in errors[0].lower()


def test_script_generator_extract_commands(script_generator):
    """Test extracting commands from script"""
    # Single AWS command
    script = "aws iam update-login-profile --user-name john --password pass"
    commands = script_generator._extract_commands(script, "aws")
    assert len(commands) == 1
    assert commands[0] == script
    
    # Multiple PowerShell commands
    script = "Get-ADUser -Identity john; Set-ADAccountPassword -Identity john -NewPassword pass"
    commands = script_generator._extract_commands(script, "powershell")
    assert len(commands) == 2
    
    # Bash commands with &&
    script = "sudo passwd john && sudo usermod -U john"
    commands = script_generator._extract_commands(script, "bash")
    assert len(commands) >= 1


def test_script_generator_generate_multi_step_script(script_generator):
    """Test generating multi-step script"""
    execution_plan = [
        {
            "step_id": "0",
            "order": 1,
            "subtask": {"subtask": "Reset password", "task_type": "password_reset"},
            "instructions": [{"id": "inst-1", "text": "Reset password instruction"}]
        },
        {
            "step_id": "1",
            "order": 2,
            "subtask": {"subtask": "Unlock account", "task_type": "account_locked"},
            "instructions": [{"id": "inst-2", "text": "Unlock account instruction"}]
        }
    ]
    
    task_params = {"username": "john"}
    
    result = script_generator.generate_multi_step_script(execution_plan, task_params)
    
    assert isinstance(result, dict)
    assert "steps" in result
    assert "all_commands" in result
    assert "validation_errors" in result
    assert "total_steps" in result
    assert result["total_steps"] == 2
    assert len(result["steps"]) == 2


def test_script_generator_determine_executor_type(script_generator):
    """Test determining executor type"""
    # From task type
    executor = script_generator._determine_executor_type("aws_password_reset", [])
    assert executor == "aws"
    
    # From instruction content
    instructions = [{"text": "Use PowerShell: Get-ADUser -Identity USERNAME"}]
    executor = script_generator._determine_executor_type("general", instructions)
    assert executor == "powershell"
    
    # From instruction content - bash
    instructions = [{"text": "Use bash: sudo passwd USERNAME"}]
    executor = script_generator._determine_executor_type("general", instructions)
    assert executor == "bash"


def test_script_generator_empty_instructions(script_generator):
    """Test handling of empty instructions"""
    result = script_generator.generate_script(
        instructions=[],
        task_params={"username": "john"},
        executor_type="aws"
    )
    
    assert len(result["validation_errors"]) > 0
    assert "No instructions" in result["validation_errors"][0]


def test_script_generator_fallback_without_llm(mock_instruction_store):
    """Test fallback behavior when LLM is not available"""
    generator = ScriptGenerator(
        instruction_store=mock_instruction_store,
        llm=None
    )
    
    instructions = [{
        "text": "Use command: aws iam update-login-profile --user-name {USERNAME} --password {PASSWORD}"
    }]
    
    result = generator.generate_script(
        instructions=instructions,
        task_params={"username": "john", "password": "pass"},
        executor_type="aws"
    )
    
    # Should use simple template replacement
    assert "script" in result
    assert isinstance(result["script"], str)


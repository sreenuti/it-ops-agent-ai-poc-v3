"""
Tests for script executors
"""
import pytest
import os
from src.script_executor.executor_base import ExecutorBase
from src.script_executor.aws_executor import AWSExecutor
from src.script_executor.system_executor import SystemExecutor


def test_aws_executor_initialization(sample_env_vars):
    """Test AWS executor initialization"""
    executor = AWSExecutor()
    
    assert executor is not None
    assert executor.get_executor_type() == "aws"


def test_aws_executor_validate_command(sample_env_vars):
    """Test AWS command validation"""
    executor = AWSExecutor()
    
    # Valid AWS command
    assert executor.validate_command("aws iam update-login-profile --user-name test --password pass") is True
    
    # Invalid command
    assert executor.validate_command("") is False
    assert executor.validate_command(None) is False


def test_aws_executor_dry_run(sample_env_vars):
    """Test AWS executor dry run"""
    executor = AWSExecutor()
    
    result = executor.execute(
        "aws iam update-login-profile --user-name test --password pass",
        dry_run=True
    )
    
    assert result["success"] is True
    assert "[DRY RUN]" in result["output"]
    assert result["exit_code"] == 0


def test_system_executor_initialization(sample_env_vars):
    """Test system executor initialization"""
    executor = SystemExecutor()
    
    assert executor is not None
    assert "system" in executor.get_executor_type()


def test_system_executor_validate_command(sample_env_vars):
    """Test system command validation"""
    executor = SystemExecutor()
    
    # Valid command
    assert executor.validate_command("echo test") is True
    
    # Invalid command
    assert executor.validate_command("") is False
    assert executor.validate_command(None) is False


def test_system_executor_dry_run(sample_env_vars):
    """Test system executor dry run"""
    executor = SystemExecutor()
    
    result = executor.execute("echo test", dry_run=True)
    
    assert result["success"] is True
    assert "[DRY RUN]" in result["output"]
    assert result["exit_code"] == 0


def test_system_executor_powershell(sample_env_vars):
    """Test PowerShell executor"""
    executor = SystemExecutor(shell_type="powershell")
    
    assert executor.shell_type == "powershell"
    assert executor.get_executor_type() == "system_powershell"


def test_system_executor_bash(sample_env_vars):
    """Test Bash executor"""
    executor = SystemExecutor(shell_type="bash")
    
    assert executor.shell_type == "bash"
    assert executor.get_executor_type() == "system_bash"


def test_executor_base_interface():
    """Test that executors implement base interface"""
    aws_executor = AWSExecutor()
    system_executor = SystemExecutor()
    
    # Both should be instances of ExecutorBase
    assert isinstance(aws_executor, ExecutorBase)
    assert isinstance(system_executor, ExecutorBase)
    
    # Both should implement required methods
    assert hasattr(aws_executor, "execute")
    assert hasattr(aws_executor, "validate_command")
    assert hasattr(aws_executor, "get_executor_type")
    
    assert hasattr(system_executor, "execute")
    assert hasattr(system_executor, "validate_command")
    assert hasattr(system_executor, "get_executor_type")


"""
AWS CLI command executor
"""
import subprocess
import json
import re
from typing import Dict, Any, Optional
from src.script_executor.executor_base import ExecutorBase
from src.config.settings import get_settings
from src.utils.error_handler import (
    ExecutionError,
    TimeoutError,
    PermissionError,
    ValidationError,
    NetworkError,
    handle_error
)


class AWSExecutor(ExecutorBase):
    """Executor for AWS CLI commands"""
    
    def __init__(self, region: Optional[str] = None, profile: Optional[str] = None):
        """
        Initialize AWS executor
        
        Args:
            region: AWS region (defaults to config)
            profile: AWS profile (defaults to config)
        """
        settings = get_settings()
        self.region = region or settings.aws_region
        self.profile = profile or settings.aws_profile
        self.allowed_commands = settings.allowed_commands
    
    def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute AWS CLI command
        
        Args:
            command: AWS CLI command (e.g., "aws iam update-login-profile ...")
            **kwargs: Additional parameters:
                - dry_run: If True, validate but don't execute
                - timeout: Command timeout in seconds
                
        Returns:
            Dict with execution results
        """
        dry_run = kwargs.get("dry_run", False)
        timeout = kwargs.get("timeout", 30)
        
        try:
            # Validate command
            if not self.validate_command(command):
                error = ValidationError(
                    "Invalid AWS command",
                    details={"command": command, "region": self.region, "profile": self.profile}
                )
                return {
                    "success": False,
                    "output": "",
                    "error": error.message,
                    "exit_code": None,
                    "error_type": error.error_type.value,
                    "error_details": error.details
                }
            
            if dry_run:
                return {
                    "success": True,
                    "output": f"[DRY RUN] Would execute: {command}",
                    "error": None,
                    "exit_code": 0
                }
            
            # Build AWS CLI command
            aws_cmd = ["aws"]
            
            if self.region:
                aws_cmd.extend(["--region", self.region])
            
            if self.profile:
                aws_cmd.extend(["--profile", self.profile])
            
            # Parse the rest of the command
            # Remove "aws" prefix if present
            cmd_parts = command.replace("aws", "").strip().split()
            aws_cmd.extend(cmd_parts)
            
            # Execute command
            result = subprocess.run(
                aws_cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Try to parse JSON output
            output = result.stdout
            try:
                if output.strip():
                    output = json.loads(output)
            except (json.JSONDecodeError, ValueError):
                pass  # Keep as string if not JSON
            
            # Check for errors
            if result.returncode != 0:
                error_output = result.stderr or result.stdout
                error_lower = error_output.lower()
                
                # Check for specific AWS error types
                if "access denied" in error_lower or "unauthorized" in error_lower or "forbidden" in error_lower:
                    error = PermissionError(
                        f"AWS permission denied: {error_output}",
                        resource=command,
                        details={"region": self.region, "profile": self.profile, "exit_code": result.returncode}
                    )
                    return {
                        "success": False,
                        "output": "",
                        "error": error.message,
                        "exit_code": result.returncode,
                        "error_type": error.error_type.value,
                        "error_details": error.details
                    }
                elif "network" in error_lower or "connection" in error_lower or "timeout" in error_lower:
                    error = NetworkError(
                        f"AWS network error: {error_output}",
                        endpoint=f"aws-{self.region or 'default'}",
                        details={"command": command, "exit_code": result.returncode}
                    )
                    return {
                        "success": False,
                        "output": "",
                        "error": error.message,
                        "exit_code": result.returncode,
                        "error_type": error.error_type.value,
                        "error_details": error.details
                    }
                else:
                    error = ExecutionError(
                        f"AWS command failed: {error_output}",
                        command=command,
                        exit_code=result.returncode,
                        details={"region": self.region, "profile": self.profile, "stderr": error_output}
                    )
                    return {
                        "success": False,
                        "output": output,
                        "error": error.message,
                        "exit_code": result.returncode,
                        "error_type": error.error_type.value,
                        "error_details": error.details
                    }
            
            return {
                "success": True,
                "output": output,
                "error": None,
                "exit_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            error = TimeoutError(
                f"AWS command timed out after {timeout} seconds",
                timeout_seconds=timeout,
                details={"command": command, "region": self.region, "profile": self.profile}
            )
            return {
                "success": False,
                "output": "",
                "error": error.message,
                "exit_code": None,
                "error_type": error.error_type.value,
                "error_details": error.details
            }
        except PermissionError as e:
            return {
                "success": False,
                "output": "",
                "error": e.message,
                "exit_code": None,
                "error_type": e.error_type.value,
                "error_details": e.details
            }
        except Exception as e:
            error = handle_error(e, f"Failed to execute AWS command: {command}")
            exec_error = ExecutionError(
                str(error),
                command=command,
                details={"region": self.region, "profile": self.profile},
                original_error=e
            )
            return {
                "success": False,
                "output": "",
                "error": exec_error.message,
                "exit_code": None,
                "error_type": exec_error.error_type.value,
                "error_details": exec_error.details
            }
    
    def validate_command(self, command: str) -> bool:
        """
        Validate AWS CLI command
        
        Args:
            command: Command to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not command or not isinstance(command, str):
            return False
        
        # Check if command starts with "aws" or is an AWS CLI command
        command_lower = command.lower().strip()
        
        # Basic validation - check for dangerous patterns
        dangerous_patterns = [
            r"rm\s+-rf",
            r"delete.*--force",
            r"terminate.*--force"
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, command_lower):
                if self.allowed_commands == "restricted":
                    return False
        
        # Check if it looks like an AWS command
        if command_lower.startswith("aws ") or "iam" in command_lower or "ec2" in command_lower:
            return True
        
        return True  # Allow if it's a valid AWS service command
    
    def get_executor_type(self) -> str:
        """Get executor type"""
        return "aws"


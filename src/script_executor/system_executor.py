"""
System command executor for Windows and Linux
"""
import subprocess
import platform
import shlex
from typing import Dict, Any, Optional
from src.script_executor.executor_base import ExecutorBase
from src.config.settings import get_settings
from src.utils.error_handler import (
    ExecutionError,
    TimeoutError,
    PermissionError,
    ValidationError,
    handle_error
)


class SystemExecutor(ExecutorBase):
    """Executor for system commands (PowerShell on Windows, Bash on Linux)"""
    
    def __init__(self, shell_type: Optional[str] = None):
        """
        Initialize system executor
        
        Args:
            shell_type: Shell type ("powershell", "bash", or None for auto-detect)
        """
        settings = get_settings()
        self.allowed_commands = settings.allowed_commands
        
        # Determine shell type
        if shell_type:
            self.shell_type = shell_type
        else:
            system = platform.system().lower()
            if system == "windows":
                self.shell_type = "powershell"
            else:
                self.shell_type = "bash"
    
    def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute system command
        
        Args:
            command: Command to execute
            **kwargs: Additional parameters:
                - dry_run: If True, validate but don't execute
                - timeout: Command timeout in seconds
                - shell: Whether to use shell (default: True)
                
        Returns:
            Dict with execution results
        """
        try:
            dry_run = kwargs.get("dry_run", False)
            timeout = kwargs.get("timeout", 30)
            use_shell = kwargs.get("shell", True)
            
            # Validate command
            if not self.validate_command(command):
                error = ValidationError(
                    "Invalid system command",
                    details={"command": command, "shell_type": self.shell_type}
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
            
            # Build command based on shell type
            if self.shell_type == "powershell":
                cmd = ["powershell", "-Command", command]
            else:  # bash
                # Use shlex to properly split command
                cmd = shlex.split(command)
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=use_shell if self.shell_type == "powershell" else False
            )
            
            # Check for permission errors in output
            if result.returncode != 0:
                error_output = result.stderr or result.stdout
                if any(keyword in error_output.lower() for keyword in ["permission denied", "access denied", "unauthorized"]):
                    error = PermissionError(
                        f"Permission denied: {error_output}",
                        resource=command,
                        details={"shell_type": self.shell_type, "exit_code": result.returncode}
                    )
                    return {
                        "success": False,
                        "output": "",
                        "error": error.message,
                        "exit_code": result.returncode,
                        "error_type": error.error_type.value,
                        "error_details": error.details
                    }
                error = ExecutionError(
                    f"Command failed with exit code {result.returncode}: {error_output}",
                    command=command,
                    exit_code=result.returncode,
                    details={"shell_type": self.shell_type, "stderr": error_output}
                )
                return {
                    "success": False,
                    "output": result.stdout,
                    "error": error.message,
                    "exit_code": result.returncode,
                    "error_type": error.error_type.value,
                    "error_details": error.details
                }
            
            return {
                "success": True,
                "output": result.stdout,
                "error": None,
                "exit_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            error = TimeoutError(
                f"Command execution timed out after {timeout} seconds",
                timeout_seconds=timeout,
                details={"command": command, "shell_type": self.shell_type}
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
            error = handle_error(e, f"Failed to execute system command: {command}")
            exec_error = ExecutionError(
                str(error),
                command=command,
                details={"shell_type": self.shell_type},
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
        Validate system command
        
        Args:
            command: Command to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not command or not isinstance(command, str):
            return False
        
        # Check for dangerous commands in restricted mode
        if self.allowed_commands == "restricted":
            dangerous_commands = [
                "rm -rf",
                "del /f /s",
                "format",
                "fdisk",
                "mkfs",
            ]
            
            command_lower = command.lower()
            for dangerous in dangerous_commands:
                if dangerous in command_lower:
                    return False
        
        return True
    
    def get_executor_type(self) -> str:
        """Get executor type"""
        return f"system_{self.shell_type}"


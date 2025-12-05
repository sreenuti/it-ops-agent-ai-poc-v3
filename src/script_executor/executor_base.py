"""
Base executor interface
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class ExecutorBase(ABC):
    """Base class for all executors"""
    
    @abstractmethod
    def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a command
        
        Args:
            command: Command to execute
            **kwargs: Additional executor-specific parameters
            
        Returns:
            Dict with keys:
                - success: bool
                - output: str
                - error: Optional[str]
                - exit_code: Optional[int]
        """
        pass
    
    @abstractmethod
    def validate_command(self, command: str) -> bool:
        """
        Validate a command before execution
        
        Args:
            command: Command to validate
            
        Returns:
            True if command is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def get_executor_type(self) -> str:
        """
        Get the type of executor
        
        Returns:
            Executor type (e.g., "aws", "system", "powershell")
        """
        pass


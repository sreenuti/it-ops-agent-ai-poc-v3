"""
Error handling utilities and custom exceptions
"""
from typing import Optional, Dict, Any, Callable
import time
import functools
from enum import Enum


class ErrorType(Enum):
    """Error type categories"""
    VALIDATION_ERROR = "validation_error"
    EXECUTION_ERROR = "execution_error"
    NETWORK_ERROR = "network_error"
    TIMEOUT_ERROR = "timeout_error"
    PERMISSION_ERROR = "permission_error"
    CONFIGURATION_ERROR = "configuration_error"
    RETRIEVAL_ERROR = "retrieval_error"
    GENERATION_ERROR = "generation_error"
    UNKNOWN_ERROR = "unknown_error"


class ITOpsAgentError(Exception):
    """Base exception for IT Ops Agent errors"""
    
    def __init__(
        self,
        message: str,
        error_type: ErrorType = ErrorType.UNKNOWN_ERROR,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Initialize IT Ops Agent error
        
        Args:
            message: User-friendly error message
            error_type: Type of error
            details: Additional error details
            original_error: Original exception if this wraps another error
        """
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.details = details or {}
        self.original_error = original_error
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary"""
        result = {
            "error_type": self.error_type.value,
            "message": self.message,
            "details": self.details
        }
        if self.original_error:
            result["original_error"] = str(self.original_error)
        return result


class ValidationError(ITOpsAgentError):
    """Error for validation failures"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            ErrorType.VALIDATION_ERROR,
            details
        )


class ExecutionError(ITOpsAgentError):
    """Error for command execution failures"""
    
    def __init__(
        self,
        message: str,
        command: Optional[str] = None,
        exit_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        details = details or {}
        if command:
            details["command"] = command
        if exit_code is not None:
            details["exit_code"] = exit_code
        
        super().__init__(
            message,
            ErrorType.EXECUTION_ERROR,
            details,
            original_error
        )


class NetworkError(ITOpsAgentError):
    """Error for network-related failures"""
    
    def __init__(
        self,
        message: str,
        endpoint: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        details = details or {}
        if endpoint:
            details["endpoint"] = endpoint
        
        super().__init__(
            message,
            ErrorType.NETWORK_ERROR,
            details,
            original_error
        )


class TimeoutError(ITOpsAgentError):
    """Error for timeout failures"""
    
    def __init__(
        self,
        message: str,
        timeout_seconds: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if timeout_seconds:
            details["timeout_seconds"] = timeout_seconds
        
        super().__init__(
            message,
            ErrorType.TIMEOUT_ERROR,
            details
        )


class PermissionError(ITOpsAgentError):
    """Error for permission/authorization failures"""
    
    def __init__(
        self,
        message: str,
        resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if resource:
            details["resource"] = resource
        
        super().__init__(
            message,
            ErrorType.PERMISSION_ERROR,
            details
        )


class ConfigurationError(ITOpsAgentError):
    """Error for configuration issues"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            ErrorType.CONFIGURATION_ERROR,
            details
        )


class RetrievalError(ITOpsAgentError):
    """Error for instruction retrieval failures"""
    
    def __init__(
        self,
        message: str,
        query: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        details = details or {}
        if query:
            details["query"] = query
        
        super().__init__(
            message,
            ErrorType.RETRIEVAL_ERROR,
            details,
            original_error
        )


class GenerationError(ITOpsAgentError):
    """Error for command/script generation failures"""
    
    def __init__(
        self,
        message: str,
        task: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        details = details or {}
        if task:
            details["task"] = task
        
        super().__init__(
            message,
            ErrorType.GENERATION_ERROR,
            details,
            original_error
        )


def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Decorator to retry function on failure
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry on
        on_retry: Optional callback function called on each retry
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        if on_retry:
                            on_retry(attempt + 1, max_retries, e)
                        
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        # Last attempt failed
                        raise
        
        return wrapper
    return decorator


def handle_error(
    error: Exception,
    default_message: str = "An error occurred",
    error_type: ErrorType = ErrorType.UNKNOWN_ERROR
) -> ITOpsAgentError:
    """
    Convert a generic exception to an IT Ops Agent error
    
    Args:
        error: Original exception
        default_message: Default message if error has no message
        error_type: Error type to use
        
    Returns:
        ITOpsAgentError instance
    """
    if isinstance(error, ITOpsAgentError):
        return error
    
    message = str(error) if str(error) else default_message
    
    # Try to infer error type from exception
    if isinstance(error, TimeoutError) or "timeout" in message.lower():
        error_type = ErrorType.TIMEOUT_ERROR
    elif isinstance(error, PermissionError) or "permission" in message.lower() or "access denied" in message.lower():
        error_type = ErrorType.PERMISSION_ERROR
    elif isinstance(error, ConnectionError) or "connection" in message.lower() or "network" in message.lower():
        error_type = ErrorType.NETWORK_ERROR
    elif isinstance(error, ValueError) or "invalid" in message.lower() or "validation" in message.lower():
        error_type = ErrorType.VALIDATION_ERROR
    
    return ITOpsAgentError(
        message=message,
        error_type=error_type,
        original_error=error
    )


def get_user_friendly_message(error: Exception) -> str:
    """
    Get a user-friendly error message from an exception
    
    Args:
        error: Exception to convert
        
    Returns:
        User-friendly error message
    """
    if isinstance(error, ITOpsAgentError):
        return error.message
    
    error_str = str(error)
    
    # Map common error messages to user-friendly versions
    friendly_messages = {
        "timeout": "The operation took too long to complete. Please try again.",
        "permission denied": "You don't have permission to perform this operation.",
        "access denied": "Access denied. Please check your credentials.",
        "connection": "Unable to connect to the service. Please check your network connection.",
        "not found": "The requested resource was not found.",
        "invalid": "The provided input is invalid. Please check and try again.",
    }
    
    error_lower = error_str.lower()
    for key, message in friendly_messages.items():
        if key in error_lower:
            return message
    
    return f"An error occurred: {error_str}"


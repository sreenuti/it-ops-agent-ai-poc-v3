"""
Tests for error handling utilities
"""
import pytest
import time
from src.utils.error_handler import (
    ITOpsAgentError,
    ValidationError,
    ExecutionError,
    NetworkError,
    TimeoutError,
    PermissionError,
    ConfigurationError,
    RetrievalError,
    GenerationError,
    ErrorType,
    retry_on_failure,
    handle_error,
    get_user_friendly_message
)


class TestCustomExceptions:
    """Test custom exception classes"""
    
    def test_itops_agent_error_basic(self):
        """Test basic ITOpsAgentError"""
        error = ITOpsAgentError("Test error", ErrorType.VALIDATION_ERROR)
        assert str(error) == "Test error"
        assert error.error_type == ErrorType.VALIDATION_ERROR
        assert error.details == {}
        assert error.original_error is None
    
    def test_itops_agent_error_with_details(self):
        """Test ITOpsAgentError with details"""
        details = {"field": "username", "reason": "too short"}
        error = ITOpsAgentError("Test error", ErrorType.VALIDATION_ERROR, details)
        assert error.details == details
    
    def test_itops_agent_error_to_dict(self):
        """Test error to_dict conversion"""
        original = ValueError("Original error")
        error = ITOpsAgentError(
            "Test error",
            ErrorType.EXECUTION_ERROR,
            {"key": "value"},
            original
        )
        error_dict = error.to_dict()
        
        assert error_dict["error_type"] == "execution_error"
        assert error_dict["message"] == "Test error"
        assert error_dict["details"] == {"key": "value"}
        assert "Original error" in error_dict["original_error"]
    
    def test_validation_error(self):
        """Test ValidationError"""
        error = ValidationError("Invalid input", {"field": "email"})
        assert error.error_type == ErrorType.VALIDATION_ERROR
        assert error.message == "Invalid input"
        assert error.details["field"] == "email"
    
    def test_execution_error(self):
        """Test ExecutionError"""
        error = ExecutionError(
            "Command failed",
            command="ls /nonexistent",
            exit_code=1
        )
        assert error.error_type == ErrorType.EXECUTION_ERROR
        assert error.details["command"] == "ls /nonexistent"
        assert error.details["exit_code"] == 1
    
    def test_network_error(self):
        """Test NetworkError"""
        error = NetworkError("Connection failed", endpoint="https://api.example.com")
        assert error.error_type == ErrorType.NETWORK_ERROR
        assert error.details["endpoint"] == "https://api.example.com"
    
    def test_timeout_error(self):
        """Test TimeoutError"""
        error = TimeoutError("Operation timed out", timeout_seconds=30.0)
        assert error.error_type == ErrorType.TIMEOUT_ERROR
        assert error.details["timeout_seconds"] == 30.0
    
    def test_permission_error(self):
        """Test PermissionError"""
        error = PermissionError("Access denied", resource="/admin")
        assert error.error_type == ErrorType.PERMISSION_ERROR
        assert error.details["resource"] == "/admin"
    
    def test_configuration_error(self):
        """Test ConfigurationError"""
        error = ConfigurationError("Missing API key")
        assert error.error_type == ErrorType.CONFIGURATION_ERROR
    
    def test_retrieval_error(self):
        """Test RetrievalError"""
        error = RetrievalError("Failed to retrieve", query="password reset")
        assert error.error_type == ErrorType.RETRIEVAL_ERROR
        assert error.details["query"] == "password reset"
    
    def test_generation_error(self):
        """Test GenerationError"""
        error = GenerationError("Failed to generate", task="reset password")
        assert error.error_type == ErrorType.GENERATION_ERROR
        assert error.details["task"] == "reset password"


class TestRetryDecorator:
    """Test retry_on_failure decorator"""
    
    def test_retry_success_on_first_attempt(self):
        """Test that function succeeds on first attempt"""
        @retry_on_failure(max_retries=3)
        def test_func():
            return "success"
        
        assert test_func() == "success"
    
    def test_retry_succeeds_after_failures(self):
        """Test that function succeeds after retries"""
        attempts = []
        
        @retry_on_failure(max_retries=3, delay=0.1)
        def test_func():
            attempts.append(1)
            if len(attempts) < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        result = test_func()
        assert result == "success"
        assert len(attempts) == 3
    
    def test_retry_exhausts_all_attempts(self):
        """Test that function raises after all retries exhausted"""
        @retry_on_failure(max_retries=2, delay=0.1)
        def test_func():
            raise ValueError("Persistent failure")
        
        with pytest.raises(ValueError, match="Persistent failure"):
            test_func()
    
    def test_retry_with_backoff(self):
        """Test retry with exponential backoff"""
        delays = []
        start_time = time.time()
        
        @retry_on_failure(max_retries=2, delay=0.1, backoff=2.0)
        def test_func():
            delays.append(time.time() - start_time)
            raise ValueError("Failure")
        
        with pytest.raises(ValueError):
            test_func()
        
        # Should have 3 attempts (initial + 2 retries)
        assert len(delays) == 3
        # Check that delays increase (allowing for timing variance)
        assert delays[1] - delays[0] >= 0.05  # First retry delay
        assert delays[2] - delays[1] >= 0.15  # Second retry delay (0.1 * 2)
    
    def test_retry_with_specific_exceptions(self):
        """Test retry only on specific exceptions"""
        @retry_on_failure(max_retries=1, delay=0.1, exceptions=(ValueError,))
        def test_func():
            raise TypeError("Wrong exception type")
        
        # Should not retry, raise immediately
        with pytest.raises(TypeError):
            test_func()
    
    def test_retry_with_callback(self):
        """Test retry with callback function"""
        retry_calls = []
        
        def on_retry(attempt, max_retries, error):
            retry_calls.append((attempt, max_retries, error))
        
        @retry_on_failure(max_retries=2, delay=0.1, on_retry=on_retry)
        def test_func():
            raise ValueError("Failure")
        
        with pytest.raises(ValueError):
            test_func()
        
        # Should have 2 retry callbacks (for attempts 2 and 3)
        assert len(retry_calls) == 2
        assert retry_calls[0][0] == 1  # First retry
        assert retry_calls[1][0] == 2  # Second retry


class TestErrorHandling:
    """Test error handling utilities"""
    
    def test_handle_error_with_itops_error(self):
        """Test handle_error with ITOpsAgentError"""
        original = ITOpsAgentError("Test", ErrorType.VALIDATION_ERROR)
        result = handle_error(original)
        assert result is original
    
    def test_handle_error_with_timeout(self):
        """Test handle_error with TimeoutError"""
        original = TimeoutError("Operation timed out")
        result = handle_error(original)
        assert isinstance(result, ITOpsAgentError)
        assert result.error_type == ErrorType.TIMEOUT_ERROR
    
    def test_handle_error_with_permission_error(self):
        """Test handle_error with PermissionError"""
        original = PermissionError("Access denied")
        result = handle_error(original)
        assert isinstance(result, ITOpsAgentError)
        assert result.error_type == ErrorType.PERMISSION_ERROR
    
    def test_handle_error_with_connection_error(self):
        """Test handle_error with ConnectionError"""
        original = ConnectionError("Connection failed")
        result = handle_error(original)
        assert isinstance(result, ITOpsAgentError)
        assert result.error_type == ErrorType.NETWORK_ERROR
    
    def test_handle_error_with_value_error(self):
        """Test handle_error with ValueError"""
        original = ValueError("Invalid value")
        result = handle_error(original)
        assert isinstance(result, ITOpsAgentError)
        assert result.error_type == ErrorType.VALIDATION_ERROR
    
    def test_handle_error_with_generic_exception(self):
        """Test handle_error with generic exception"""
        original = Exception("Something went wrong")
        result = handle_error(original)
        assert isinstance(result, ITOpsAgentError)
        assert result.error_type == ErrorType.UNKNOWN_ERROR
    
    def test_get_user_friendly_message_from_itops_error(self):
        """Test get_user_friendly_message with ITOpsAgentError"""
        error = ITOpsAgentError("User-friendly message", ErrorType.VALIDATION_ERROR)
        message = get_user_friendly_message(error)
        assert message == "User-friendly message"
    
    def test_get_user_friendly_message_timeout(self):
        """Test get_user_friendly_message for timeout"""
        error = TimeoutError("Operation timed out")
        message = get_user_friendly_message(error)
        assert "too long" in message.lower()
    
    def test_get_user_friendly_message_permission(self):
        """Test get_user_friendly_message for permission error"""
        error = PermissionError("Permission denied")
        message = get_user_friendly_message(error)
        assert "permission" in message.lower()
    
    def test_get_user_friendly_message_connection(self):
        """Test get_user_friendly_message for connection error"""
        error = ConnectionError("Connection failed")
        message = get_user_friendly_message(error)
        assert "connect" in message.lower() or "network" in message.lower()
    
    def test_get_user_friendly_message_generic(self):
        """Test get_user_friendly_message for generic error"""
        error = Exception("Something went wrong")
        message = get_user_friendly_message(error)
        assert "error occurred" in message.lower()
        assert "Something went wrong" in message


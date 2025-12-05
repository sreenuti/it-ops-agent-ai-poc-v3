"""
Tests for logging system
"""
import pytest
import json
import tempfile
from pathlib import Path
from src.utils.logger import (
    StructuredLogger,
    LogLevel,
    get_logger
)


class TestStructuredLogger:
    """Test StructuredLogger class"""
    
    def test_logger_creation(self):
        """Test basic logger creation"""
        logger = StructuredLogger("test_logger")
        assert logger.name == "test_logger"
        assert logger.logger is not None
    
    def test_logger_with_file(self):
        """Test logger with file output"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = StructuredLogger("test_logger", log_file=log_file)
            
            logger.info("Test message")
            
            # Check file was created and contains log
            assert log_file.exists()
            with open(log_file) as f:
                content = f.read()
                assert "Test message" in content
    
    def test_log_levels(self):
        """Test different log levels"""
        logger = StructuredLogger("test_logger", log_level=LogLevel.DEBUG)
        
        # All levels should work
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
    
    def test_log_with_extra_fields(self):
        """Test logging with extra fields"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = StructuredLogger("test_logger", log_file=log_file)
            
            logger.info("Test message", extra_fields={"user": "john", "task": "password_reset"})
            
            # Check JSON log contains extra fields
            with open(log_file) as f:
                log_line = f.readline()
                log_data = json.loads(log_line)
                assert log_data["user"] == "john"
                assert log_data["task"] == "password_reset"
    
    def test_log_agent_action(self):
        """Test logging agent actions"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = StructuredLogger("test_logger", log_file=log_file)
            
            logger.log_agent_action(
                "retrieve_instructions",
                task="password_reset",
                session_id="session-123",
                details={"count": 3}
            )
            
            with open(log_file) as f:
                log_line = f.readline()
                log_data = json.loads(log_line)
                assert log_data["action"] == "retrieve_instructions"
                assert log_data["task"] == "password_reset"
                assert log_data["session_id"] == "session-123"
                assert log_data["count"] == 3
                assert log_data["component"] == "agent"
    
    def test_log_retrieval(self):
        """Test logging instruction retrieval"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = StructuredLogger("test_logger", log_file=log_file)
            
            logger.log_retrieval("password reset", 5, session_id="session-123")
            
            with open(log_file) as f:
                log_line = f.readline()
                log_data = json.loads(log_line)
                assert log_data["operation"] == "retrieval"
                assert log_data["query"] == "password reset"
                assert log_data["results_count"] == 5
                assert log_data["session_id"] == "session-123"
                assert log_data["component"] == "vector_db"
    
    def test_log_execution_success(self):
        """Test logging successful execution"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = StructuredLogger("test_logger", log_file=log_file)
            
            logger.log_execution(
                "aws iam update-login-profile",
                "aws",
                success=True,
                session_id="session-123",
                exit_code=0
            )
            
            with open(log_file) as f:
                log_line = f.readline()
                log_data = json.loads(log_line)
                assert log_data["operation"] == "execution"
                assert log_data["executor_type"] == "aws"
                assert log_data["command"] == "aws iam update-login-profile"
                assert log_data["success"] is True
                assert log_data["exit_code"] == 0
                assert log_data["component"] == "executor"
    
    def test_log_execution_failure(self):
        """Test logging failed execution"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = StructuredLogger("test_logger", log_file=log_file)
            
            logger.log_execution(
                "invalid-command",
                "system",
                success=False,
                session_id="session-123",
                exit_code=1,
                error="Command not found"
            )
            
            with open(log_file) as f:
                log_line = f.readline()
                log_data = json.loads(log_line)
                assert log_data["success"] is False
                assert log_data["exit_code"] == 1
                assert log_data["error"] == "Command not found"
    
    def test_log_error_with_exception(self):
        """Test logging error with exception"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = StructuredLogger("test_logger", log_file=log_file)
            
            try:
                raise ValueError("Test error")
            except ValueError as e:
                logger.error("An error occurred", exc_info=e)
            
            with open(log_file) as f:
                log_line = f.readline()
                log_data = json.loads(log_line)
                assert "exception" in log_data
                assert "Test error" in log_data["exception"]


class TestGetLogger:
    """Test get_logger function"""
    
    def test_get_logger(self):
        """Test getting logger instance"""
        logger = get_logger("test_logger")
        assert isinstance(logger, StructuredLogger)
        assert logger.name == "test_logger"
    
    def test_get_logger_with_options(self):
        """Test getting logger with options"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = get_logger(
                "test_logger",
                log_level=LogLevel.DEBUG,
                log_file=log_file,
                console_output=False
            )
            
            assert logger.logger.level == 10  # DEBUG level
            logger.info("Test")
            assert log_file.exists()


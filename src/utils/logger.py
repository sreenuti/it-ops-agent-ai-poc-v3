"""
Structured logging system for IT Ops Agent
"""
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from enum import Enum


class LogLevel(Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON
        
        Args:
            record: Log record
            
        Returns:
            JSON string
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data, default=str)


class StructuredLogger:
    """Structured logger for IT Ops Agent"""
    
    def __init__(
        self,
        name: str,
        log_level: LogLevel = LogLevel.INFO,
        log_file: Optional[Path] = None,
        console_output: bool = True
    ):
        """
        Initialize structured logger
        
        Args:
            name: Logger name
            log_level: Minimum log level
            log_file: Optional log file path
            console_output: Whether to output to console
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.value))
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Console handler
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, log_level.value))
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, log_level.value))
            json_formatter = JSONFormatter()
            file_handler.setFormatter(json_formatter)
            self.logger.addHandler(file_handler)
    
    def _log_with_extra(
        self,
        level: str,
        message: str,
        extra_fields: Optional[Dict[str, Any]] = None,
        exc_info: Optional[Exception] = None
    ):
        """
        Log with extra fields
        
        Args:
            level: Log level
            message: Log message
            extra_fields: Additional fields to include
            exc_info: Exception info
        """
        extra = {}
        if extra_fields:
            extra["extra_fields"] = extra_fields
        
        log_method = getattr(self.logger, level.lower())
        log_method(message, extra=extra, exc_info=exc_info)
    
    def debug(self, message: str, extra_fields: Optional[Dict[str, Any]] = None):
        """Log debug message"""
        self._log_with_extra("DEBUG", message, extra_fields)
    
    def info(self, message: str, extra_fields: Optional[Dict[str, Any]] = None):
        """Log info message"""
        self._log_with_extra("INFO", message, extra_fields)
    
    def warning(self, message: str, extra_fields: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        self._log_with_extra("WARNING", message, extra_fields)
    
    def error(
        self,
        message: str,
        extra_fields: Optional[Dict[str, Any]] = None,
        exc_info: Optional[Exception] = None
    ):
        """Log error message"""
        self._log_with_extra("ERROR", message, extra_fields, exc_info)
    
    def critical(
        self,
        message: str,
        extra_fields: Optional[Dict[str, Any]] = None,
        exc_info: Optional[Exception] = None
    ):
        """Log critical message"""
        self._log_with_extra("CRITICAL", message, extra_fields, exc_info)
    
    def log_agent_action(
        self,
        action: str,
        task: Optional[str] = None,
        session_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log agent action
        
        Args:
            action: Action name (e.g., "retrieve_instructions", "execute_command")
            task: Task type or description
            session_id: Session identifier
            details: Additional details
        """
        extra_fields = {
            "action": action,
            "component": "agent"
        }
        if task:
            extra_fields["task"] = task
        if session_id:
            extra_fields["session_id"] = session_id
        if details:
            extra_fields.update(details)
        
        self.info(f"Agent action: {action}", extra_fields=extra_fields)
    
    def log_retrieval(
        self,
        query: str,
        results_count: int,
        session_id: Optional[str] = None
    ):
        """
        Log instruction retrieval
        
        Args:
            query: Search query
            results_count: Number of results
            session_id: Session identifier
        """
        extra_fields = {
            "component": "vector_db",
            "operation": "retrieval",
            "query": query,
            "results_count": results_count
        }
        if session_id:
            extra_fields["session_id"] = session_id
        
        self.info(f"Retrieved {results_count} instructions for query: {query}", extra_fields=extra_fields)
    
    def log_execution(
        self,
        command: str,
        executor_type: str,
        success: bool,
        session_id: Optional[str] = None,
        exit_code: Optional[int] = None,
        error: Optional[str] = None
    ):
        """
        Log command execution
        
        Args:
            command: Executed command
            executor_type: Type of executor
            success: Whether execution succeeded
            session_id: Session identifier
            exit_code: Exit code
            error: Error message if failed
        """
        extra_fields = {
            "component": "executor",
            "operation": "execution",
            "executor_type": executor_type,
            "command": command,
            "success": success
        }
        if session_id:
            extra_fields["session_id"] = session_id
        if exit_code is not None:
            extra_fields["exit_code"] = exit_code
        if error:
            extra_fields["error"] = error
        
        level = "info" if success else "error"
        message = f"Command execution {'succeeded' if success else 'failed'}: {command}"
        getattr(self, level)(message, extra_fields=extra_fields)


def get_logger(
    name: str = "itops_agent",
    log_level: LogLevel = LogLevel.INFO,
    log_file: Optional[Path] = None,
    console_output: bool = True
) -> StructuredLogger:
    """
    Get or create a structured logger
    
    Args:
        name: Logger name
        log_level: Minimum log level
        log_file: Optional log file path
        console_output: Whether to output to console
        
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name, log_level, log_file, console_output)


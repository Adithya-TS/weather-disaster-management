"""
Observability: Logging, Tracing, and Metrics using ADK
Demonstrates ADK LoggingPlugin and structured logging
"""

import structlog
import logging
import os
from datetime import datetime
from pathlib import Path
from google.adk.plugins.logging_plugin import LoggingPlugin


def configure_logging(log_level: str = "INFO", log_format: str = "json", log_dir: str = "logs"):
    """
    Configure structured logging with structlog (ADK-compatible).
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_format: Format type ("json" or "console")
        log_dir: Directory to store log files
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_path / f"disaster_management_{timestamp}.log"
    
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    if log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
        
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_handler.setFormatter(logging.Formatter("%(message)s"))
    
    # Configure console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    
    # Configure root logger with both handlers
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return str(log_file)


def get_logging_plugin() -> LoggingPlugin:
    """
    Get an instance of ADK's LoggingPlugin for agent observability.
    
    Returns:
        LoggingPlugin instance configured for the application
    """
    return LoggingPlugin()


class ObservabilityManager:
    """
    Manages observability for the disaster management system using ADK.
    Wraps ADK's LoggingPlugin with additional application-specific logging.
    """
    
    def __init__(self, log_level: str = "INFO", log_dir: str = "logs"):
        """
        Initialize observability manager.
        
        Args:
            log_level: Logging level for the application
            log_dir: Directory to store log files
        """
        self.log_file = configure_logging(log_level=log_level, log_format="json", log_dir=log_dir)
        self.logger = structlog.get_logger("observability_manager")
        self.logging_plugin = get_logging_plugin()
        self.logger.info("observability_manager.initialized", log_level=log_level, log_file=self.log_file)
    
    def get_plugin(self) -> LoggingPlugin:
        """Get the ADK LoggingPlugin for use with Runner."""
        return self.logging_plugin
    
    def get_log_file(self) -> str:
        """Get the current log file path."""
        return self.log_file
    
    def log_workflow_start(self, location: str, **kwargs):
        """Log workflow start event."""
        self.logger.info("workflow.start", location=location, **kwargs)
    
    def log_workflow_complete(self, location: str, duration: float, **kwargs):
        """Log workflow completion event."""
        self.logger.info("workflow.complete", location=location, duration_seconds=duration, **kwargs)
    
    def log_workflow_error(self, location: str, error: str, **kwargs):
        """Log workflow error event."""
        self.logger.error("workflow.error", location=location, error=error, **kwargs)

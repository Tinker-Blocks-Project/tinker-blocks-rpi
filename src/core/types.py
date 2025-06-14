"""Core types and enums."""

from enum import Enum


class LogLevel(Enum):
    """Log levels for send_message function."""

    DEBUG = "debug"  # CLI only - detailed execution info
    INFO = "info"  # Both UI and CLI - general status updates
    SUCCESS = "success"  # Both UI and CLI - successful operations
    WARNING = "warning"  # Both UI and CLI - warnings and recoverable errors
    ERROR = "error"  # Both UI and CLI - critical errors
    ASSISTANT = "assistant"  # Both UI and CLI - AI assistant messages

"""
Custom exceptions for the AI Agent SDK.

This module defines the exception hierarchy used throughout the SDK
to provide clear error handling and debugging information.
"""

from typing import Any, Dict, Optional


class AgentSDKError(Exception):
    """Base exception for all Agent SDK errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": self.error_code or self.__class__.__name__,
            "message": str(self),
            "details": self.details,
        }


class ConfigurationError(AgentSDKError):
    """Raised when there's a configuration error."""
    pass


class TaskExecutionError(AgentSDKError):
    """Raised during task execution failures."""
    pass


class MCPServerError(AgentSDKError):
    """Raised when MCP server communication fails."""
    pass


class AuthenticationError(AgentSDKError):
    """Raised when authentication or authorization fails."""
    pass


class ScopeViolationError(AgentSDKError):
    """Raised when task exceeds approved scope boundaries."""
    pass


class AgentUnavailableError(AgentSDKError):
    """Raised when required agent is not available."""
    pass


class DatabaseError(AgentSDKError):
    """Raised when database operations fail."""
    pass


class CommunicationError(AgentSDKError):
    """Raised when WebSocket communication fails."""
    pass


class ValidationError(AgentSDKError):
    """Raised when data validation fails."""
    pass


class RateLimitError(AgentSDKError):
    """Raised when rate limits are exceeded."""
    pass


class TimeoutError(AgentSDKError):
    """Raised when operations timeout."""
    pass
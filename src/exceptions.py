"""
Custom exceptions for the Dynamic Stress Tests framework.
"""


class FrameworkError(Exception):
    """Base exception for all framework errors."""
    pass


class ConfigurationError(FrameworkError):
    """Raised when configuration is invalid or missing."""
    pass


class AuthenticationError(FrameworkError):
    """Raised when authentication fails."""
    pass


class OpenAPIError(FrameworkError):
    """Raised when OpenAPI specification processing fails."""
    pass


class ScenarioError(FrameworkError):
    """Raised when scenario building fails."""
    pass


class ValidationError(FrameworkError):
    """Raised when validation fails."""
    pass


class EnvironmentError(FrameworkError):
    """Raised when environment setup fails."""
    pass


class NetworkError(FrameworkError):
    """Raised when network operations fail."""
    pass


class TimeoutError(FrameworkError):
    """Raised when operations timeout."""
    pass
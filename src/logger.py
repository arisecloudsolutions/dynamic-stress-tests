"""
Logging configuration for the Dynamic Stress Tests framework.
"""

import os
import logging
import sys
from datetime import datetime
from typing import Optional

# Default log level from environment
DEFAULT_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Log format
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(
    name: str,
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    console: bool = True
) -> logging.Logger:
    """
    Set up a logger with consistent formatting.

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        console: Whether to log to console

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Clear any existing handlers
    logger.handlers.clear()

    # Set level
    log_level = getattr(logging, (level or DEFAULT_LOG_LEVEL), logging.INFO)
    logger.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        try:
            # Ensure log directory exists
            log_dir = os.path.dirname(log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)

            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            # Fallback to console logging if file logging fails
            logger.warning(f"Failed to setup file logging: {e}")

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with framework defaults.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return setup_logger(name)


# Framework logger
framework_logger = get_logger("dynamic_stress_tests")


# Helper functions for common logging patterns
def log_config_loaded(logger: logging.Logger, config_source: str):
    """Log configuration loading."""
    logger.info(f"Configuration loaded from {config_source}")


def log_api_request(logger: logging.Logger, method: str, url: str, status: Optional[int] = None):
    """Log API requests."""
    if status:
        logger.debug(f"{method} {url} -> {status}")
    else:
        logger.debug(f"{method} {url}")


def log_test_progress(logger: logging.Logger, current: int, total: int, item: str):
    """Log test progress."""
    percentage = (current / total * 100) if total > 0 else 0
    logger.info(f"Progress: {current}/{total} ({percentage:.1f}%) - {item}")


def log_auth_success(logger: logging.Logger, auth_method: str):
    """Log successful authentication."""
    logger.info(f"Authentication successful using {auth_method}")


def log_auth_failure(logger: logging.Logger, auth_method: str, error: str):
    """Log authentication failure."""
    logger.error(f"Authentication failed using {auth_method}: {error}")


def log_openapi_loaded(logger: logging.Logger, url_or_path: str, endpoint_count: int):
    """Log OpenAPI specification loading."""
    logger.info(f"OpenAPI spec loaded from {url_or_path}: {endpoint_count} endpoints found")


def log_scenario_generated(logger: logging.Logger, scenario_count: int):
    """Log scenario generation."""
    logger.info(f"Generated {scenario_count} test scenarios")


def log_docker_info(logger: logging.Logger, image: str, container: str):
    """Log Docker container information."""
    logger.info(f"Docker container '{container}' running image '{image}'")


def log_safety_check(logger: logging.Logger, check: str, passed: bool):
    """Log safety checks."""
    status = "PASSED" if passed else "FAILED"
    level = logging.INFO if passed else logging.WARNING
    logger.log(level, f"Safety check '{check}': {status}")


# Environment-specific logger setup
def setup_production_logging():
    """Setup logging for production environment."""
    # Lower verbosity, structured logging
    return setup_logger(
        "dynamic_stress_tests",
        level="WARNING",
        log_file="/var/log/dynamic_stress_tests.log",
        console=False
    )


def setup_development_logging():
    """Setup logging for development environment."""
    # Higher verbosity, console output
    return setup_logger(
        "dynamic_stress_tests",
        level="DEBUG",
        console=True
    )


def setup_ci_logging():
    """Setup logging for CI environment."""
    # Moderate verbosity, console only
    return setup_logger(
        "dynamic_stress_tests",
        level="INFO",
        console=True
    )


# Auto-configure based on environment
def auto_configure_logging():
    """Automatically configure logging based on environment."""
    env = os.getenv("ENVIRONMENT", "development").lower()

    if env == "production":
        return setup_production_logging()
    elif env in ["ci", "test", "testing"]:
        return setup_ci_logging()
    else:
        return setup_development_logging()


# Initialize logging if this module is imported
_framework_logger = auto_configure_logging()
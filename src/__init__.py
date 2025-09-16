"""
Dynamic Stress Tests - Automated Load Testing Framework

A comprehensive Locust-based load testing framework that generates tests
from OpenAPI specifications with support for various authentication methods
and production-safe defaults.
"""

__version__ = "1.0.0"
__author__ = "Load Testing Framework Team"

# Core modules
from . import auth
from . import openapi_loader
from . import scenario_builder
from . import settings
from . import utils

# Optional modules (may not be imported during CI runs)
try:
    from . import locustfile
except ImportError:
    # Locust may not be available in all environments
    pass

__all__ = [
    "auth",
    "openapi_loader",
    "scenario_builder",
    "settings",
    "utils",
]
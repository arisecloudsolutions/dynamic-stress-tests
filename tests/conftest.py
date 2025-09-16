"""
Pytest configuration and fixtures for the test suite.
"""

import os
import pytest
import tempfile
import json
from unittest.mock import Mock


@pytest.fixture
def clean_env():
    """Fixture to provide a clean environment for tests."""
    # Store original environment
    original_env = os.environ.copy()

    # Clear test-related environment variables
    test_vars = [
        "OPENAPI_URL", "OPENAPI_PATH", "BASE_URL", "AUTH_MODE", "JWT_TOKEN",
        "LOGIN_URL", "LOGIN_USER", "LOGIN_PASS", "API_KEY", "API_KEY_HEADER",
        "OAUTH_CLIENT_ID", "OAUTH_CLIENT_SECRET", "OAUTH_TOKEN_URL",
        "BASIC_USER", "BASIC_PASS", "MAX_USERS", "SPAWN_RATE",
        "REQUEST_TIMEOUT", "RETRY_COUNT", "RUN_TIME", "EXTRA_HEADERS",
        "REPORTS_DIR", "SPEC_INCLUDE_TAGS", "SPEC_EXCLUDE_TAGS"
    ]

    for var in test_vars:
        if var in os.environ:
            del os.environ[var]

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def sample_openapi_spec():
    """Fixture providing a sample OpenAPI specification."""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Test API",
            "version": "1.0.0"
        },
        "servers": [
            {"url": "https://api.example.com"}
        ],
        "paths": {
            "/users": {
                "get": {
                    "tags": ["users"],
                    "summary": "List users",
                    "responses": {
                        "200": {
                            "description": "Success"
                        }
                    }
                },
                "post": {
                    "tags": ["users"],
                    "summary": "Create user",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "email": {"type": "string", "format": "email"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Created"
                        }
                    }
                }
            },
            "/users/{id}": {
                "get": {
                    "tags": ["users"],
                    "summary": "Get user",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Success"
                        }
                    }
                },
                "delete": {
                    "tags": ["admin"],
                    "summary": "Delete user",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "responses": {
                        "204": {
                            "description": "Deleted"
                        }
                    }
                }
            }
        }
    }


@pytest.fixture
def temp_openapi_file(sample_openapi_spec):
    """Fixture providing a temporary OpenAPI file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_openapi_spec, f)
        temp_file = f.name

    yield temp_file

    # Cleanup
    os.unlink(temp_file)


@pytest.fixture
def mock_requests_response():
    """Fixture providing a mock requests response."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.elapsed.total_seconds.return_value = 0.5
    mock_response.json.return_value = {"status": "ok"}
    mock_response.raise_for_status.return_value = None
    return mock_response


@pytest.fixture
def basic_valid_config():
    """Fixture providing basic valid configuration."""
    config = {
        "OPENAPI_URL": "https://api.example.com/openapi.json",
        "BASE_URL": "https://api.example.com",
        "MAX_USERS": "10",
        "SPAWN_RATE": "2",
        "REQUEST_TIMEOUT": "10",
        "RETRY_COUNT": "1"
    }

    # Set environment variables
    for key, value in config.items():
        os.environ[key] = value

    yield config

    # Cleanup is handled by clean_env fixture


@pytest.fixture
def jwt_auth_config():
    """Fixture providing JWT authentication configuration."""
    config = {
        "AUTH_MODE": "jwt",
        "JWT_TOKEN": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature"
    }

    for key, value in config.items():
        os.environ[key] = value

    yield config


@pytest.fixture
def login_auth_config():
    """Fixture providing login authentication configuration."""
    config = {
        "AUTH_MODE": "login",
        "LOGIN_URL": "/auth/login",
        "LOGIN_USER": "testuser",
        "LOGIN_PASS": "testpass"
    }

    for key, value in config.items():
        os.environ[key] = value

    yield config


@pytest.fixture
def temp_reports_dir():
    """Fixture providing a temporary reports directory."""
    import tempfile
    import shutil

    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


class MockLocustUser:
    """Mock Locust user for testing."""

    def __init__(self):
        self.client = MockLocustClient()


class MockLocustClient:
    """Mock Locust client for testing."""

    def __init__(self):
        self.last_request = None

    def get(self, path, **kwargs):
        self.last_request = {
            "method": "GET",
            "path": path,
            "kwargs": kwargs
        }
        return MockResponse()

    def post(self, path, **kwargs):
        self.last_request = {
            "method": "POST",
            "path": path,
            "kwargs": kwargs
        }
        return MockResponse()

    def put(self, path, **kwargs):
        self.last_request = {
            "method": "PUT",
            "path": path,
            "kwargs": kwargs
        }
        return MockResponse()

    def delete(self, path, **kwargs):
        self.last_request = {
            "method": "DELETE",
            "path": path,
            "kwargs": kwargs
        }
        return MockResponse()

    def request(self, method, path, **kwargs):
        self.last_request = {
            "method": method,
            "path": path,
            "kwargs": kwargs
        }
        return MockResponse()


class MockResponse:
    """Mock response for testing."""

    def __init__(self, status_code=200):
        self.status_code = status_code

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def success(self):
        pass

    def failure(self, reason):
        pass


@pytest.fixture
def mock_locust_user():
    """Fixture providing a mock Locust user."""
    return MockLocustUser()


# Test data fixtures
@pytest.fixture
def sample_auth_headers():
    """Sample authentication headers."""
    return {
        "Authorization": "Bearer test-token",
        "X-API-Key": "test-key",
        "X-Environment": "test"
    }


@pytest.fixture
def sample_test_scenarios():
    """Sample test scenarios."""
    return [
        {
            "method": "GET",
            "path": "/users",
            "path_params": {},
            "query_params": {},
            "payload": None
        },
        {
            "method": "POST",
            "path": "/users",
            "path_params": {},
            "query_params": {},
            "payload": {
                "name": "Test User",
                "email": "test@example.com"
            }
        },
        {
            "method": "GET",
            "path": "/users/{id}",
            "path_params": {"id": 1},
            "query_params": {},
            "payload": None
        }
    ]
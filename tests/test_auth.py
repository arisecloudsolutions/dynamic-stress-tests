"""
Tests for authentication module.
"""

import os
import pytest
import json
from unittest.mock import patch, Mock

# Import from src
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from auth import AuthenticationManager
from exceptions import AuthenticationError, ConfigurationError


class TestAuthenticationManager:
    """Test cases for AuthenticationManager."""

    def setup_method(self):
        """Setup for each test."""
        # Clear environment variables
        auth_vars = [
            "AUTH_MODE", "JWT_TOKEN", "LOGIN_URL", "LOGIN_USER", "LOGIN_PASS",
            "API_KEY", "API_KEY_HEADER", "OAUTH_CLIENT_ID", "OAUTH_CLIENT_SECRET",
            "OAUTH_TOKEN_URL", "BASIC_USER", "BASIC_PASS", "EXTRA_HEADERS"
        ]
        for var in auth_vars:
            if var in os.environ:
                del os.environ[var]

    def test_no_auth_mode(self):
        """Test behavior when no auth mode is set."""
        auth_manager = AuthenticationManager()
        headers = auth_manager.get_auth_headers()
        assert headers == {}

    def test_jwt_auth_success(self):
        """Test successful JWT authentication."""
        os.environ["AUTH_MODE"] = "jwt"
        os.environ["JWT_TOKEN"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature"

        auth_manager = AuthenticationManager()
        headers = auth_manager.get_auth_headers()

        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Bearer ")

    def test_jwt_auth_missing_token(self):
        """Test JWT auth with missing token."""
        os.environ["AUTH_MODE"] = "jwt"

        auth_manager = AuthenticationManager()
        with pytest.raises(AuthenticationError):
            auth_manager.get_auth_headers()

    def test_api_key_auth(self):
        """Test API key authentication."""
        os.environ["AUTH_MODE"] = "apikey"
        os.environ["API_KEY"] = "test-api-key"

        auth_manager = AuthenticationManager()
        headers = auth_manager.get_auth_headers()

        assert "X-API-Key" in headers
        assert headers["X-API-Key"] == "test-api-key"

    def test_api_key_custom_header(self):
        """Test API key auth with custom header."""
        os.environ["AUTH_MODE"] = "apikey"
        os.environ["API_KEY"] = "test-api-key"
        os.environ["API_KEY_HEADER"] = "X-Custom-Key"

        auth_manager = AuthenticationManager()
        headers = auth_manager.get_auth_headers()

        assert "X-Custom-Key" in headers
        assert headers["X-Custom-Key"] == "test-api-key"

    def test_basic_auth(self):
        """Test HTTP Basic authentication."""
        os.environ["AUTH_MODE"] = "basic"
        os.environ["BASIC_USER"] = "testuser"
        os.environ["BASIC_PASS"] = "testpass"

        auth_manager = AuthenticationManager()
        headers = auth_manager.get_auth_headers()

        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Basic ")

    @patch('requests.post')
    def test_login_auth_success(self, mock_post):
        """Test successful login authentication."""
        os.environ["AUTH_MODE"] = "login"
        os.environ["BASE_URL"] = "https://api.example.com"
        os.environ["LOGIN_URL"] = "/auth/login"
        os.environ["LOGIN_USER"] = "testuser"
        os.environ["LOGIN_PASS"] = "testpass"

        # Mock successful login response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"access_token": "test-token"}
        mock_post.return_value = mock_response

        auth_manager = AuthenticationManager()
        headers = auth_manager.get_auth_headers()

        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test-token"

    @patch('requests.post')
    def test_oauth_auth_success(self, mock_post):
        """Test successful OAuth authentication."""
        os.environ["AUTH_MODE"] = "oauth"
        os.environ["OAUTH_CLIENT_ID"] = "client-id"
        os.environ["OAUTH_CLIENT_SECRET"] = "client-secret"
        os.environ["OAUTH_TOKEN_URL"] = "https://auth.example.com/token"

        # Mock successful OAuth response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"access_token": "oauth-token"}
        mock_post.return_value = mock_response

        auth_manager = AuthenticationManager()
        headers = auth_manager.get_auth_headers()

        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer oauth-token"

    def test_extra_headers(self):
        """Test extra headers functionality."""
        os.environ["EXTRA_HEADERS"] = json.dumps({
            "X-Environment": "test",
            "X-Version": "1.0"
        })

        auth_manager = AuthenticationManager()
        headers = auth_manager.get_auth_headers()

        assert "X-Environment" in headers
        assert "X-Version" in headers
        assert headers["X-Environment"] == "test"
        assert headers["X-Version"] == "1.0"

    def test_invalid_extra_headers_json(self):
        """Test invalid JSON in extra headers."""
        os.environ["EXTRA_HEADERS"] = "invalid-json"

        # Should not raise exception but log warning
        auth_manager = AuthenticationManager()
        headers = auth_manager.get_auth_headers()

        # Should still work with empty extra headers
        assert isinstance(headers, dict)

    def test_token_caching(self):
        """Test token caching functionality."""
        os.environ["AUTH_MODE"] = "jwt"
        os.environ["JWT_TOKEN"] = "test-token"

        auth_manager = AuthenticationManager()

        # First call should cache token
        headers1 = auth_manager.get_auth_headers()

        # Second call should use cached token
        headers2 = auth_manager.get_auth_headers()

        assert headers1 == headers2

    def test_invalid_auth_mode(self):
        """Test invalid authentication mode."""
        os.environ["AUTH_MODE"] = "invalid-mode"

        auth_manager = AuthenticationManager()
        with pytest.raises(AuthenticationError):
            auth_manager.get_auth_headers()


if __name__ == "__main__":
    pytest.main([__file__])
"""
Tests for configuration validator module.
"""

import os
import pytest
from unittest.mock import patch, Mock

# Import from src
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config_validator import ConfigValidator


class TestConfigValidator:
    """Test cases for ConfigValidator."""

    def setup_method(self):
        """Setup for each test."""
        # Clear relevant environment variables
        env_vars = [
            "OPENAPI_URL", "OPENAPI_PATH", "BASE_URL", "AUTH_MODE",
            "MAX_USERS", "SPAWN_RATE", "REQUEST_TIMEOUT", "RETRY_COUNT",
            "RUN_TIME", "EXTRA_HEADERS", "REPORTS_DIR"
        ]
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]

        self.validator = ConfigValidator()

    def test_missing_openapi_config(self):
        """Test validation with missing OpenAPI configuration."""
        is_valid, errors, warnings = self.validator.validate_all()

        assert not is_valid
        assert any("OPENAPI_URL or OPENAPI_PATH must be provided" in error for error in errors)

    def test_valid_openapi_url(self):
        """Test validation with valid OpenAPI URL."""
        os.environ["OPENAPI_URL"] = "https://api.example.com/openapi.json"
        os.environ["BASE_URL"] = "https://api.example.com"

        is_valid, errors, warnings = self.validator.validate_all()

        # Should not have OpenAPI-related errors
        openapi_errors = [e for e in errors if "OPENAPI" in e]
        assert len(openapi_errors) == 0

    def test_invalid_openapi_url(self):
        """Test validation with invalid OpenAPI URL."""
        os.environ["OPENAPI_URL"] = "not-a-valid-url"
        os.environ["BASE_URL"] = "https://api.example.com"

        is_valid, errors, warnings = self.validator.validate_all()

        assert not is_valid
        assert any("Invalid OPENAPI_URL format" in error for error in errors)

    def test_missing_base_url(self):
        """Test validation with missing BASE_URL."""
        os.environ["OPENAPI_URL"] = "https://api.example.com/openapi.json"

        is_valid, errors, warnings = self.validator.validate_all()

        assert not is_valid
        assert any("BASE_URL is required" in error for error in errors)

    def test_invalid_base_url(self):
        """Test validation with invalid BASE_URL."""
        os.environ["OPENAPI_URL"] = "https://api.example.com/openapi.json"
        os.environ["BASE_URL"] = "not-a-valid-url"

        is_valid, errors, warnings = self.validator.validate_all()

        assert not is_valid
        assert any("Invalid BASE_URL format" in error for error in errors)

    def test_auth_mode_validation(self):
        """Test authentication mode validation."""
        os.environ["OPENAPI_URL"] = "https://api.example.com/openapi.json"
        os.environ["BASE_URL"] = "https://api.example.com"
        os.environ["AUTH_MODE"] = "invalid-mode"

        is_valid, errors, warnings = self.validator.validate_all()

        assert not is_valid
        assert any("Invalid AUTH_MODE" in error for error in errors)

    def test_jwt_auth_validation(self):
        """Test JWT authentication validation."""
        os.environ["OPENAPI_URL"] = "https://api.example.com/openapi.json"
        os.environ["BASE_URL"] = "https://api.example.com"
        os.environ["AUTH_MODE"] = "jwt"

        is_valid, errors, warnings = self.validator.validate_all()

        assert not is_valid
        assert any("JWT_TOKEN is required" in error for error in errors)

    def test_login_auth_validation(self):
        """Test login authentication validation."""
        os.environ["OPENAPI_URL"] = "https://api.example.com/openapi.json"
        os.environ["BASE_URL"] = "https://api.example.com"
        os.environ["AUTH_MODE"] = "login"

        is_valid, errors, warnings = self.validator.validate_all()

        assert not is_valid
        # Should have errors for missing LOGIN_URL, LOGIN_USER, LOGIN_PASS
        login_errors = [e for e in errors if "LOGIN_" in e]
        assert len(login_errors) == 3

    def test_invalid_max_users(self):
        """Test invalid MAX_USERS validation."""
        os.environ["OPENAPI_URL"] = "https://api.example.com/openapi.json"
        os.environ["BASE_URL"] = "https://api.example.com"
        os.environ["MAX_USERS"] = "not-a-number"

        is_valid, errors, warnings = self.validator.validate_all()

        assert not is_valid
        assert any("MAX_USERS must be an integer" in error for error in errors)

    def test_zero_max_users(self):
        """Test zero MAX_USERS validation."""
        os.environ["OPENAPI_URL"] = "https://api.example.com/openapi.json"
        os.environ["BASE_URL"] = "https://api.example.com"
        os.environ["MAX_USERS"] = "0"

        is_valid, errors, warnings = self.validator.validate_all()

        assert not is_valid
        assert any("MAX_USERS must be a positive integer" in error for error in errors)

    def test_high_max_users_warning(self):
        """Test high MAX_USERS generates warning."""
        os.environ["OPENAPI_URL"] = "https://api.example.com/openapi.json"
        os.environ["BASE_URL"] = "https://api.example.com"
        os.environ["MAX_USERS"] = "15000"

        is_valid, errors, warnings = self.validator.validate_all()

        assert any("MAX_USERS is very high" in warning for warning in warnings)

    def test_invalid_spawn_rate(self):
        """Test invalid SPAWN_RATE validation."""
        os.environ["OPENAPI_URL"] = "https://api.example.com/openapi.json"
        os.environ["BASE_URL"] = "https://api.example.com"
        os.environ["SPAWN_RATE"] = "not-a-number"

        is_valid, errors, warnings = self.validator.validate_all()

        assert not is_valid
        assert any("SPAWN_RATE must be a number" in error for error in errors)

    def test_invalid_run_time_format(self):
        """Test invalid RUN_TIME format."""
        os.environ["OPENAPI_URL"] = "https://api.example.com/openapi.json"
        os.environ["BASE_URL"] = "https://api.example.com"
        os.environ["RUN_TIME"] = "invalid-format"

        is_valid, errors, warnings = self.validator.validate_all()

        assert not is_valid
        assert any("RUN_TIME format should be" in error for error in errors)

    def test_valid_run_time_formats(self):
        """Test valid RUN_TIME formats."""
        os.environ["OPENAPI_URL"] = "https://api.example.com/openapi.json"
        os.environ["BASE_URL"] = "https://api.example.com"

        valid_formats = ["10m", "30s", "1h", "300"]

        for run_time in valid_formats:
            os.environ["RUN_TIME"] = run_time
            is_valid, errors, warnings = self.validator.validate_all()

            # Should not have RUN_TIME format errors
            runtime_errors = [e for e in errors if "RUN_TIME format" in e]
            assert len(runtime_errors) == 0

    def test_production_url_warning(self):
        """Test warning for production-like URLs."""
        os.environ["OPENAPI_URL"] = "https://api.example.com/openapi.json"
        os.environ["BASE_URL"] = "https://production.example.com"
        os.environ["MAX_USERS"] = "500"

        is_valid, errors, warnings = self.validator.validate_all()

        assert any("HIGH RISK" in warning for warning in warnings)

    def test_invalid_extra_headers_json(self):
        """Test invalid JSON in EXTRA_HEADERS."""
        os.environ["OPENAPI_URL"] = "https://api.example.com/openapi.json"
        os.environ["BASE_URL"] = "https://api.example.com"
        os.environ["EXTRA_HEADERS"] = "invalid-json"

        is_valid, errors, warnings = self.validator.validate_all()

        assert not is_valid
        assert any("EXTRA_HEADERS must be valid JSON" in error for error in errors)

    def test_valid_extra_headers_json(self):
        """Test valid JSON in EXTRA_HEADERS."""
        os.environ["OPENAPI_URL"] = "https://api.example.com/openapi.json"
        os.environ["BASE_URL"] = "https://api.example.com"
        os.environ["EXTRA_HEADERS"] = '{"X-Test": "value"}'

        is_valid, errors, warnings = self.validator.validate_all()

        # Should not have JSON-related errors
        json_errors = [e for e in errors if "valid JSON" in e]
        assert len(json_errors) == 0

    @patch('requests.get')
    def test_health_check_network_success(self, mock_get):
        """Test successful network health check."""
        os.environ["BASE_URL"] = "https://api.example.com"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.5
        mock_get.return_value = mock_response

        health_results = self.validator.health_check()

        assert health_results["checks"]["network"]["status"] == "pass"
        assert health_results["checks"]["network"]["response_code"] == 200

    @patch('requests.get')
    def test_health_check_network_failure(self, mock_get):
        """Test network health check failure."""
        os.environ["BASE_URL"] = "https://api.example.com"

        mock_get.side_effect = ConnectionError("Connection failed")

        health_results = self.validator.health_check()

        assert health_results["checks"]["network"]["status"] == "fail"
        assert "Connection failed" in health_results["checks"]["network"]["error"]

    def test_health_check_no_base_url(self):
        """Test health check with no BASE_URL."""
        health_results = self.validator.health_check()

        assert health_results["checks"]["network"]["status"] == "skip"

    def test_localhost_warning(self):
        """Test warning for localhost URLs."""
        os.environ["OPENAPI_URL"] = "https://api.example.com/openapi.json"
        os.environ["BASE_URL"] = "http://localhost:8080"

        is_valid, errors, warnings = self.validator.validate_all()

        assert any("localhost" in warning for warning in warnings)

    def test_url_trailing_slash_warning(self):
        """Test warning for URLs with trailing slash."""
        os.environ["OPENAPI_URL"] = "https://api.example.com/openapi.json"
        os.environ["BASE_URL"] = "https://api.example.com/"

        is_valid, errors, warnings = self.validator.validate_all()

        assert any("should not end with '/'" in warning for warning in warnings)


if __name__ == "__main__":
    pytest.main([__file__])